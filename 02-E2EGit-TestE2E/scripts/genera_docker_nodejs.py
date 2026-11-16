#!/usr/bin/env python3
"""Analizzatore multi-versione e generatore di configurazioni Docker per repository Node.js E2E.

Funzionalità:
1. Seleziona le versioni (tag Git) nell'intervallo specificato (--from / --to).
2. Ispeziona ogni tag direttamente via `git ls-tree` e `git show` senza fare checkout.
3. Estrae Node.js, package manager, lockfile, monorepo, framework E2E e versione esatta,
   dipendenze native, dipendenze git-build, env CI e comandi di install/build/serve/test.
4. Raggruppa le versioni in cluster omogenei e genera:
   - results/docker_clusters_report.txt e .json
   - docker/Dockerfile.<cluster> (1 Dockerfile per cluster)
   - docker/esegui_test_docker.sh (per build + esecuzione test via git worktree)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


SEMVER_RE = re.compile(
    r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[-+].+)?$"
)
PARTIAL_VER_RE = re.compile(
    r"^v?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?$"
)

NATIVE_BUILD_DEPS = {
    "node-sass",
    "node-gyp",
    "canvas",
    "sqlite3",
    "better-sqlite3",
    "bcrypt",
    "sharp",
    "microtime",
    "re2",
    "utf-8-validate",
    "bufferutil",
}

GIT_BUILD_DEPS = {
    "git-revision-webpack-plugin",
    "webpack-git-hash",
}

E2E_PACKAGES = [
    ("playwright", "@playwright/test"),
    ("playwright", "playwright"),
    ("playwright", "playwright-core"),
    ("cypress", "cypress"),
    ("puppeteer", "puppeteer"),
    ("webdriverio", "@wdio/cli"),
    ("webdriverio", "webdriverio"),
    ("testcafe", "testcafe"),
    ("nightwatch", "nightwatch"),
    ("selenium", "selenium-webdriver"),
]


@dataclass
class TagInfo:
    name: str
    date: str
    semver: tuple[int, int, int] | None
    is_stable: bool


@dataclass
class VersionAnalysis:
    tag: str
    date: str
    node_version: str
    node_source: str
    pkg_manager: str
    pkg_manager_source: str
    lockfiles: list[str] = field(default_factory=list)
    workspaces: list[str] = field(default_factory=list)
    package_jsons: list[str] = field(default_factory=list)
    e2e_framework: str = "unknown"
    e2e_pkg_name: str = ""
    e2e_version: str = ""
    e2e_pkg_dir: str = "."
    e2e_config_file: str = ""
    existing_docker_base: str = ""
    native_deps: list[str] = field(default_factory=list)
    needs_git_repo: bool = False
    install_cmds: list[str] = field(default_factory=list)
    build_cmds: list[str] = field(default_factory=list)
    serve_cmd: str = ""
    serve_port: int | None = None
    test_cmd: str = ""
    ci_workflow: str = ""
    ci_env: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def cluster_signature(self) -> tuple[Any, ...]:
        """Firma canonica usata per raggruppare versioni nello stesso cluster Dockerfile."""
        e2e_ver_key = self.e2e_version
        if self.e2e_framework == "cypress" and e2e_ver_key:
            parts = e2e_ver_key.split(".")
            e2e_ver_key = ".".join(parts[:2])
        return (
            self.node_version,
            self.pkg_manager,
            self.e2e_framework,
            e2e_ver_key,
            self.e2e_pkg_dir,
            tuple(self.install_cmds),
            tuple(self.build_cmds),
            self.serve_cmd,
            self.serve_port,
            self.test_cmd,
            tuple(sorted(self.ci_env.items())),
            bool(self.native_deps),
            self.needs_git_repo,
        )


def run_git(repo_dir: Path, args: list[str], check: bool = True) -> str:
    res = subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        text=True,
    )
    if check and res.returncode != 0:
        raise RuntimeError(f"Errore git {' '.join(args)}: {res.stderr.strip()}")
    return res.stdout


def git_show(repo_dir: Path, tag: str, rel_path: str) -> str | None:
    res = subprocess.run(
        ["git", "-C", str(repo_dir), "show", f"{tag}:{rel_path}"],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return None
    return res.stdout


def parse_semver(tag_name: str) -> tuple[tuple[int, int, int] | None, bool]:
    m = SEMVER_RE.match(tag_name.strip())
    if not m:
        return None, False
    ver = (int(m.group("major")), int(m.group("minor")), int(m.group("patch")))
    is_stable = m.group("suffix") is None
    return ver, is_stable


def parse_bound(bound: str, is_upper: bool) -> tuple[int, int, int] | None:
    m = PARTIAL_VER_RE.match(bound.strip())
    if not m:
        return None
    major = int(m.group("major"))
    if m.group("minor") is None:
        return (major, 999999, 999999) if is_upper else (major, 0, 0)
    minor = int(m.group("minor"))
    if m.group("patch") is None:
        return (major, minor, 999999) if is_upper else (major, minor, 0)
    patch = int(m.group("patch"))
    return (major, minor, patch)


def collect_tags(
    repo_dir: Path,
    from_ver: str | None,
    to_ver: str | None,
    only_stable: bool,
) -> list[TagInfo]:
    raw = run_git(
        repo_dir,
        [
            "for-each-ref",
            "--sort=creatordate",
            "--format=%(creatordate:short)\t%(refname:short)",
            "refs/tags",
        ],
    )
    tags: list[TagInfo] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        date_str, name = line.split("\t", 1)
        semver, is_stable = parse_semver(name)
        if only_stable and not is_stable:
            continue
        tags.append(TagInfo(name=name, date=date_str, semver=semver, is_stable=is_stable))

    tags.sort(key=lambda t: (t.semver is None, t.semver or (0, 0, 0), t.date, t.name))

    lower_bound = parse_bound(from_ver, is_upper=False) if from_ver else None
    upper_bound = parse_bound(to_ver, is_upper=True) if to_ver else None

    if to_ver and SEMVER_RE.match(to_ver.strip()):
        v, _ = parse_semver(to_ver.strip())
        if v is not None:
            upper_bound = v
    if from_ver and SEMVER_RE.match(from_ver.strip()):
        v, _ = parse_semver(from_ver.strip())
        if v is not None:
            lower_bound = v

    filtered: list[TagInfo] = []
    for t in tags:
        if t.semver is None:
            continue
        if lower_bound and t.semver < lower_bound:
            continue
        if upper_bound and t.semver > upper_bound:
            continue
        filtered.append(t)
    return filtered


def clean_version_spec(spec: str) -> str:
    m = re.search(r"(\d+\.\d+\.\d+|\d+\.\d+|\d+)", spec or "")
    return m.group(1) if m else ""


def parse_workflow_yaml_light(content: str) -> dict[str, Any]:
    """Parser leggero senza dipendenze esterne per GitHub Actions YAML."""
    lines = content.splitlines()
    env_vars: dict[str, str] = {}
    node_versions: list[str] = []
    run_blocks: list[tuple[str, str]] = []

    in_top_env = False
    step_indent: int | None = None
    current_step_name = ""
    current_step_cmd = ""
    current_step_workdir = ""

    def flush_step() -> None:
        nonlocal current_step_name, current_step_cmd, current_step_workdir
        if current_step_cmd:
            cmd = current_step_cmd
            if (
                current_step_workdir
                and "${{" not in current_step_workdir
                and not cmd.lstrip().startswith("cd ")
            ):
                cmd = f"cd {current_step_workdir} && {cmd}"
            run_blocks.append((current_step_name, cmd))
        current_step_name = ""
        current_step_cmd = ""
        current_step_workdir = ""

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip(" "))

        if indent == 0 and stripped == "env:":
            in_top_env = True
            i += 1
            continue
        if indent == 0 and stripped != "env:":
            in_top_env = False

        if in_top_env and indent >= 2 and ":" in stripped:
            k, v = stripped.split(":", 1)
            k = k.strip()
            v = v.split("#", 1)[0].strip().strip("'\"")
            if k and v:
                env_vars[k] = v

        m_node = re.match(r"node-version:\s*(.+)$", stripped)
        if m_node:
            raw_nv = m_node.group(1).split("#", 1)[0].strip()
            if "${{" not in raw_nv:
                cleaned_nv = clean_version_spec(raw_nv)
                if cleaned_nv:
                    node_versions.append(cleaned_nv)

        if step_indent is not None and (
            indent < step_indent or (indent == step_indent and stripped.startswith("- "))
        ):
            flush_step()
            if indent < step_indent:
                step_indent = None

        if stripped.startswith("- "):
            flush_step()
            step_indent = indent

        m_name = re.match(r"^-?\s*name:\s*(.+)$", stripped)
        if m_name:
            current_step_name = m_name.group(1).strip().strip("'\"")

        m_wd = re.match(r"^-?\s*working-directory:\s*(.+)$", stripped)
        if m_wd:
            current_step_workdir = m_wd.group(1).split("#", 1)[0].strip().strip("'\"")

        m_run = re.match(r"^-?\s*run:\s*(.*)$", stripped)
        if m_run:
            rest = m_run.group(1).strip()
            run_indent = indent
            if rest in ("|", "|-", ">", ">-"):
                block_lines: list[str] = []
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    if nxt.strip() == "":
                        block_lines.append("")
                        i += 1
                        continue
                    nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                    if nxt_indent <= run_indent:
                        break
                    block_lines.append(nxt.strip())
                    i += 1
                current_step_cmd = "\n".join(line_b for line_b in block_lines if line_b)
                continue
            elif rest:
                current_step_cmd = rest

        i += 1

    flush_step()

    return {
        "env": env_vars,
        "node_versions": node_versions,
        "runs": run_blocks,
    }


def detect_node_from_date(date_str: str) -> str:
    year = int(date_str[:4])
    if year <= 2021:
        return "14"
    if year == 2022:
        return "16"
    if year in (2023, 2024):
        return "18"
    return "20"


def detect_pkg_manager(
    files: set[str],
    root_pkg: dict[str, Any],
) -> tuple[str, str, list[str]]:
    lockfiles = sorted(
        f for f in files
        if f.endswith(("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json"))
    )
    pm_field = root_pkg.get("packageManager", "")
    if isinstance(pm_field, str) and pm_field:
        if pm_field.startswith("pnpm"):
            return "pnpm", "package.json#packageManager", lockfiles
        if pm_field.startswith("yarn"):
            return "yarn", "package.json#packageManager", lockfiles
        if pm_field.startswith("npm"):
            return "npm", "package.json#packageManager", lockfiles

    if "pnpm-lock.yaml" in files or "pnpm-workspace.yaml" in files:
        return "pnpm", "pnpm-lock.yaml", lockfiles
    if "yarn.lock" in files:
        return "yarn", "yarn.lock", lockfiles
    if "package-lock.json" in files:
        return "npm", "package-lock.json", lockfiles

    return "npm", "default (nessun lockfile root)", lockfiles


def find_e2e_config_file(framework: str, pkg_dir: str, files: set[str]) -> str:
    patterns = {
        "playwright": ("playwright.config.ts", "playwright.config.js", "playwright.config.mjs"),
        "cypress": ("cypress.config.ts", "cypress.config.js", "cypress.config.mjs", "cypress.json"),
    }.get(framework, ())
    candidates = [f for f in sorted(files) if Path(f).name in patterns]
    if not candidates:
        return ""
    for c in candidates:
        if pkg_dir != "." and c.startswith(pkg_dir + "/"):
            return c
    return candidates[0]


def resolve_locked_version(
    repo_dir: Path,
    tag: str,
    dep_name: str,
    e2e_dir: str,
    files: set[str],
) -> str:
    """Legge la versione esatta risolta dal lockfile (package-lock.json) se disponibile."""
    lock_candidates = []
    if e2e_dir != "." and f"{e2e_dir}/package-lock.json" in files:
        lock_candidates.append(f"{e2e_dir}/package-lock.json")
    if "package-lock.json" in files:
        lock_candidates.append("package-lock.json")

    for lp in lock_candidates:
        raw = git_show(repo_dir, tag, lp)
        if not raw:
            continue
        try:
            ldata = json.loads(raw)
        except json.JSONDecodeError:
            continue
        packages = ldata.get("packages") or {}
        for key in (
            f"{e2e_dir}/node_modules/{dep_name}" if e2e_dir != "." else "",
            f"node_modules/{dep_name}",
        ):
            if key and key in packages and "version" in packages[key]:
                return str(packages[key]["version"])
        deps = ldata.get("dependencies") or {}
        if dep_name in deps and "version" in deps[dep_name]:
            return str(deps[dep_name]["version"])
    return ""


def detect_e2e_framework(
    repo_dir: Path,
    tag: str,
    pkg_contents: dict[str, dict[str, Any]],
    files: set[str],
) -> tuple[str, str, str, str, str]:
    """Ritorna (framework, pkg_name, version, e2e_pkg_dir, config_file)."""
    ordered_pkgs = sorted(
        pkg_contents.items(),
        key=lambda kv: (kv[0] == "package.json", "test" not in kv[0].lower(), kv[0]),
    )
    for fw_name, dep_name in E2E_PACKAGES:
        for pkg_path, data in ordered_pkgs:
            for section in ("devDependencies", "dependencies"):
                deps = data.get(section) or {}
                if dep_name in deps:
                    pkg_dir = str(Path(pkg_path).parent)
                    if pkg_dir == "":
                        pkg_dir = "."
                    locked = resolve_locked_version(repo_dir, tag, dep_name, pkg_dir, files)
                    ver = locked or clean_version_spec(str(deps[dep_name]))
                    cfg = find_e2e_config_file(fw_name, pkg_dir, files)
                    return fw_name, dep_name, ver, pkg_dir, cfg
    return "unknown", "", "", ".", ""


def pick_e2e_workflow(
    workflows: dict[str, dict[str, Any]],
) -> tuple[str, dict[str, Any]] | tuple[str, None]:
    if not workflows:
        return "", None
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for path, parsed in workflows.items():
        lname = Path(path).name.lower()
        score = 0
        if "playwright" in lname or "cypress" in lname or "e2e" in lname:
            score += 10
        if "test" in lname or "ci" in lname:
            score += 2
        if "publish" in lname or "release" in lname or "deploy" in lname:
            score -= 5
        if "macromolecules" in lname or "run-tests" in lname:
            score -= 2
        if "codeql" in lname or "lint" in lname:
            score -= 10
        joined = "\n".join(cmd for _, cmd in parsed["runs"]).lower()
        if "playwright" in joined or "cypress" in joined or "serve" in joined:
            score += 5
        scored.append((score, path, parsed))
    scored.sort(key=lambda x: (-x[0], x[1]))
    best_score, best_path, best_parsed = scored[0]
    if best_score <= 0:
        return "", None
    return best_path, best_parsed


def extract_port_from_text(text: str) -> int | None:
    m = re.search(r"(?:localhost|127\.0\.0\.1|host\.docker\.internal|0\.0\.0\.0):(\d{3,5})", text)
    if m:
        return int(m.group(1))
    m_port = re.search(r"--port[=\s]+(\d{3,5})|\bPORT=(\d{3,5})|\s-l\s+(\d{3,5})", text)
    if m_port:
        return int(m_port.group(1) or m_port.group(2) or m_port.group(3))
    return None


def is_background_serve_cmd(step_name: str, cmd: str) -> bool:
    """Riconosce avvio di un server in background evitando falsi positivi su `&&`."""
    low = cmd.lower()
    sname = step_name.lower()
    if "nohup" in low or "serve" in sname or "serve:" in low:
        return True
    # Ampersand singolo di background (&), non && né >&
    if re.search(r"(?<![&>])&(?!&)", cmd):
        return True
    return False


def normalize_ci_env_for_single_container(raw_env: dict[str, str]) -> dict[str, str]:
    """Adatta le variabili CI per esecuzione in un singolo container (localhost invece di host.docker.internal)."""
    out: dict[str, str] = {}
    for k, v in raw_env.items():
        if "host.docker.internal" in v:
            out[k] = v.replace("host.docker.internal", "localhost")
        else:
            out[k] = v
    return out


def analyze_version(repo_dir: Path, tag_info: TagInfo) -> VersionAnalysis:
    tag = tag_info.name
    tree_out = run_git(repo_dir, ["ls-tree", "-r", "--name-only", tag])
    files = set(line.strip() for line in tree_out.splitlines() if line.strip())

    pkg_paths = sorted(f for f in files if Path(f).name == "package.json")
    pkg_contents: dict[str, dict[str, Any]] = {}
    for p in pkg_paths:
        raw = git_show(repo_dir, tag, p)
        if raw:
            try:
                pkg_contents[p] = json.loads(raw)
            except json.JSONDecodeError:
                pass

    root_pkg = pkg_contents.get("package.json", {})
    workspaces = root_pkg.get("workspaces") or []
    if isinstance(workspaces, dict):
        workspaces = workspaces.get("packages") or []

    pkg_manager, pm_source, lockfiles = detect_pkg_manager(files, root_pkg)
    e2e_fw, e2e_pkg_name, e2e_ver, e2e_dir, e2e_cfg = detect_e2e_framework(
        repo_dir, tag, pkg_contents, files
    )

    wf_paths = sorted(
        f for f in files
        if f.startswith(".github/workflows/") and f.endswith((".yml", ".yaml"))
    )
    workflows: dict[str, dict[str, Any]] = {}
    for wp in wf_paths:
        raw = git_show(repo_dir, tag, wp)
        if raw:
            workflows[wp] = parse_workflow_yaml_light(raw)

    ci_wf_path, ci_wf = pick_e2e_workflow(workflows)

    # Versione Node.js
    node_ver = ""
    node_src = ""
    for dotfile in (".nvmrc", ".node-version"):
        if dotfile in files:
            raw = (git_show(repo_dir, tag, dotfile) or "").strip()
            cleaned = clean_version_spec(raw)
            if cleaned:
                node_ver, node_src = cleaned, dotfile
                break
    if not node_ver and ci_wf and ci_wf["node_versions"]:
        node_ver = ci_wf["node_versions"][0]
        node_src = ci_wf_path
    if not node_ver:
        for wp, parsed in workflows.items():
            if parsed["node_versions"]:
                node_ver = parsed["node_versions"][0]
                node_src = wp
                break
    if not node_ver:
        eng_node = (root_pkg.get("engines") or {}).get("node", "")
        if eng_node:
            node_ver = clean_version_spec(str(eng_node))
            node_src = "package.json#engines.node"
    if not node_ver:
        node_ver = detect_node_from_date(tag_info.date)
        node_src = f"fallback-anno({tag_info.date[:4]})"
    node_ver = clean_version_spec(node_ver) or node_ver

    # Eventuale Dockerfile esistente nella cartella E2E
    existing_docker_base = ""
    if e2e_dir != ".":
        df_candidate = f"{e2e_dir}/Dockerfile"
        if df_candidate in files:
            df_raw = git_show(repo_dir, tag, df_candidate) or ""
            from_lines = re.findall(r"^\s*FROM\s+(\S+)", df_raw, flags=re.MULTILINE)
            if from_lines:
                existing_docker_base = from_lines[-1]

    # Dipendenze native C/C++ e dipendenze che richiedono metadati .git
    native_found: set[str] = set()
    needs_git = False
    for pdata in pkg_contents.values():
        for sec in ("dependencies", "devDependencies"):
            deps = pdata.get(sec) or {}
            for dep in deps:
                if dep in NATIVE_BUILD_DEPS:
                    native_found.add(dep)
                if dep in GIT_BUILD_DEPS:
                    needs_git = True

    install_cmds: list[str] = []
    build_cmds: list[str] = []
    serve_cmd = ""
    serve_port: int | None = None
    test_cmd = ""
    ci_env: dict[str, str] = {}
    notes: list[str] = []

    if ci_wf:
        ci_env = normalize_ci_env_for_single_container(ci_wf["env"])
        for val in ci_env.values():
            p = extract_port_from_text(val)
            if p:
                serve_port = p

        for step_name, raw_cmd in ci_wf["runs"]:
            cmd_one_line = " && ".join(
                line.strip() for line in raw_cmd.splitlines() if line.strip()
            )
            low = cmd_one_line.lower()
            sname = step_name.lower()

            if "docker build" in low or "docker system prune" in low or "echo \"" in low:
                continue

            if any(k in low for k in ("npm ci", "npm i", "npm install", "yarn install", "pnpm install")):
                if "docker" not in low:
                    install_cmds.append(cmd_one_line)
            elif "docker:test" in low:
                e2e_pkg = pkg_contents.get(f"{e2e_dir}/package.json", root_pkg)
                e2e_scripts = e2e_pkg.get("scripts") or {}
                prefix = f"cd {e2e_dir} && " if e2e_dir != "." else ""
                if "test" in e2e_scripts:
                    test_cmd = f"{prefix}{e2e_scripts['test']}"
            elif "playwright test" in low or "cypress run" in low or "test:e2e" in low:
                test_cmd = cmd_one_line
            elif is_background_serve_cmd(step_name, cmd_one_line):
                cleaned_serve = re.sub(r"\bnohup\s+", "", cmd_one_line)
                cleaned_serve = re.sub(r"\s*&\s*$", "", cleaned_serve).strip()
                serve_cmd = cleaned_serve
            elif "build" in sname or any(
                b in low for b in ("npm run build", "yarn build", "pnpm build")
            ):
                if "docker" not in low:
                    build_cmds.append(cmd_one_line)

    # Fallback se mancano step dal workflow CI
    if not install_cmds:
        if pkg_manager == "npm":
            install_cmds.append("npm ci" if "package-lock.json" in files else "npm install")
        elif pkg_manager == "yarn":
            install_cmds.append("yarn install --frozen-lockfile")
        elif pkg_manager == "pnpm":
            install_cmds.append("pnpm install --frozen-lockfile")

        if e2e_dir != "." and f"{e2e_dir}/package.json" in pkg_contents:
            in_workspaces = any(
                e2e_dir == w.rstrip("/*") for w in workspaces if isinstance(w, str)
            )
            if not in_workspaces:
                install_cmds.append(f"cd {e2e_dir} && {install_cmds[0]}")

    install_cmds = list(dict.fromkeys(install_cmds))
    build_cmds = list(dict.fromkeys(build_cmds))

    root_scripts = root_pkg.get("scripts") or {}
    if not build_cmds and "build" in root_scripts:
        build_cmds.append(f"{pkg_manager} run build" if pkg_manager != "npm" else "npm run build")

    if not test_cmd:
        e2e_pkg = pkg_contents.get(
            f"{e2e_dir}/package.json" if e2e_dir != "." else "package.json",
            root_pkg,
        )
        e2e_scripts = e2e_pkg.get("scripts") or {}
        prefix = f"cd {e2e_dir} && " if e2e_dir != "." else ""
        if "test:e2e" in e2e_scripts:
            test_cmd = f"{prefix}{pkg_manager} run test:e2e"
        elif "e2e" in e2e_scripts:
            test_cmd = f"{prefix}{pkg_manager} run e2e"
        elif e2e_fw == "playwright":
            test_cmd = f"{prefix}{e2e_scripts.get('test', 'npx playwright test')}"
        elif e2e_fw == "cypress":
            test_cmd = f"{prefix}npx cypress run"

    # Rileva porta server
    if serve_port is None and serve_cmd:
        m_cd = re.search(r"cd\s+([^\s/&;]+)", serve_cmd)
        if m_cd:
            sub = m_cd.group(1).rstrip("/")
            sub_pkg_raw = git_show(repo_dir, tag, f"{sub}/package.json") or ""
            serve_port = extract_port_from_text(sub_pkg_raw)
    if serve_port is None and e2e_cfg:
        cfg_raw = git_show(repo_dir, tag, e2e_cfg) or ""
        serve_port = extract_port_from_text(cfg_raw)
    if serve_port is None and e2e_dir != ".":
        for candidate in sorted(files):
            if candidate.startswith(e2e_dir + "/") and (
                "constant" in candidate.lower() or candidate.endswith(".env.example")
            ):
                raw_c = git_show(repo_dir, tag, candidate) or ""
                p = extract_port_from_text(raw_c)
                if p:
                    serve_port = p
                    break

    if e2e_fw == "playwright" and existing_docker_base:
        m_img = re.search(r"playwright:v(\d+\.\d+\.\d+)", existing_docker_base)
        if m_img and e2e_ver and m_img.group(1) != e2e_ver:
            notes.append(
                f"lock/pkg ha {e2e_pkg_name}={e2e_ver}, mentre {e2e_dir}/Dockerfile usava {m_img.group(1)}"
            )

    return VersionAnalysis(
        tag=tag,
        date=tag_info.date,
        node_version=node_ver,
        node_source=node_src,
        pkg_manager=pkg_manager,
        pkg_manager_source=pm_source,
        lockfiles=lockfiles,
        workspaces=[str(w) for w in workspaces],
        package_jsons=pkg_paths,
        e2e_framework=e2e_fw,
        e2e_pkg_name=e2e_pkg_name,
        e2e_version=e2e_ver,
        e2e_pkg_dir=e2e_dir,
        e2e_config_file=e2e_cfg,
        existing_docker_base=existing_docker_base,
        native_deps=sorted(native_found),
        needs_git_repo=needs_git,
        install_cmds=install_cmds,
        build_cmds=build_cmds,
        serve_cmd=serve_cmd,
        serve_port=serve_port,
        test_cmd=test_cmd,
        ci_workflow=ci_wf_path,
        ci_env=ci_env,
        notes=notes,
    )


def cluster_analyses(analyses: list[VersionAnalysis]) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []
    sig_to_idx: dict[tuple[Any, ...], int] = {}

    for a in analyses:
        sig = a.cluster_signature()
        if sig not in sig_to_idx:
            sig_to_idx[sig] = len(clusters)
            clusters.append({"representative": a, "versions": [a]})
        else:
            clusters[sig_to_idx[sig]]["versions"].append(a)
    return clusters


CYPRESS_BASE_IMAGES = {
    "12": "cypress/browsers:node12.18.3-chrome89-ff86",
    "14": "cypress/browsers:node14.19.0-chrome100-ff99-edge",
    "16": "cypress/browsers:node-16.18.1-chrome-110.0.5481.96-1-ff-109.0-edge-110.0.1587.41-1",
    "18": "cypress/browsers:node-18.20.3-chrome-125.0.6422.141-1-ff-126.0.1-edge-125.0.2535.85-1",
    "20": "cypress/browsers:node-20.18.0-chrome-130.0.6723.69-1-ff-131.0.3-edge-130.0.2849.52-1",
    "22": "cypress/browsers:node-22.21.0-chrome-141.0.7390.107-1-ff-144.0-edge-141.0.3537.92-1",
    "24": "cypress/browsers:node-24.22.1-chrome-156.0.8078.73-1-ff-159.0-edge-156.0.4314.50-1",
}


def select_base_image(rep: VersionAnalysis) -> tuple[str, bool]:
    """Sceglie l'immagine base Docker più adatta. Ritorna (image, need_browser_install)."""
    if rep.e2e_framework == "playwright" and rep.e2e_version:
        # Playwright >= 1.22 usa immagini -jammy; <= 1.21 usa -focal
        pw_parts = [int(p) for p in rep.e2e_version.split(".")[:2] if p.isdigit()]
        distro = "focal" if tuple(pw_parts) < (1, 22) else "jammy"
        return f"mcr.microsoft.com/playwright:v{rep.e2e_version}-{distro}", True
    major = rep.node_version.split(".")[0]
    if rep.e2e_framework == "cypress":
        return CYPRESS_BASE_IMAGES.get(major, "cypress/browsers:latest"), False
    try:
        major_int = int(major)
    except ValueError:
        major_int = 20
    if major_int <= 8:
        return f"node:{major_int}-stretch", False
    if major_int <= 14:
        return f"node:{major_int}-bullseye", False
    return f"node:{major_int}-bookworm", False


def cluster_filename(cl_idx: int, versions: list[VersionAnalysis]) -> str:
    first = versions[0].tag
    last = versions[-1].tag
    if first == last:
        return f"Dockerfile.{first}"
    return f"Dockerfile.{first}-{last}"


def rewrite_subshell_cd(cmd: str) -> str:
    """Trasforma `cd dir && comando` in `(cd /app/dir && comando)` per esecuzione sicura in CMD."""
    m = re.match(r"^cd\s+([^\s&;]+)\s*&&\s*(.+)$", cmd.strip())
    if m:
        sub = m.group(1).rstrip("/")
        rest = m.group(2).strip()
        target = sub if sub.startswith("/") else f"/app/{sub}"
        return f"(cd {target} && {rest})"
    return cmd


def generate_dockerfile(
    repo_name: str,
    cl_idx: int,
    versions: list[VersionAnalysis],
    rep: VersionAnalysis,
) -> str:
    tag_range = versions[0].tag if len(versions) == 1 else f"{versions[0].tag} - {versions[-1].tag}"
    base_image, check_pw_browser = select_base_image(rep)

    lines: list[str] = [
        f"# Dockerfile auto-generato per {repo_name} (Cluster {cl_idx}: {tag_range})",
        f"# Versioni coperte: {', '.join(v.tag for v in versions)}",
        f"FROM {base_image}",
        "",
        "ARG APP_VERSION=v0.0.0",
        "ENV HUSKY=0",
    ]
    for k, v in rep.ci_env.items():
        lines.append(f"ENV {k}={v}")

    lines.extend(["", "WORKDIR /app"])

    if rep.native_deps:
        lines.extend([
            "",
            "# Dipendenze di compilazione per moduli nativi C/C++",
            "RUN apt-get update && apt-get install -y --no-install-recommends python3 make g++ && rm -rf /var/lib/apt/lists/*",
        ])

    lines.extend(["", "COPY . ."])

    if rep.needs_git_repo:
        lines.extend([
            "",
            "# Inizializza metadati git minimali per plugin di build (es. git-revision-webpack-plugin)",
            "RUN rm -rf .git && git init -q && git config user.email 'docker@local' && git config user.name 'docker' && \\",
            "    git commit --allow-empty -q -m 'docker build' && git tag -f \"$APP_VERSION\"",
        ])

    # Installazione + build
    run_steps: list[str] = []
    for cmd in rep.install_cmds:
        run_steps.append(rewrite_subshell_cd(cmd) if cmd.startswith("cd ") else cmd)

    if check_pw_browser:
        pw_prefix = f"cd /app/{rep.e2e_pkg_dir} && " if rep.e2e_pkg_dir != "." else ""
        run_steps.append(f"({pw_prefix}npx playwright install chromium)")

    for cmd in rep.build_cmds:
        run_steps.append(rewrite_subshell_cd(cmd) if cmd.startswith("cd ") else cmd)

    lines.extend(["", "# Installazione dipendenze, browser e build del progetto"])
    if len(run_steps) == 1:
        lines.append(f"RUN {run_steps[0]}")
    else:
        joined = " && \\\n    ".join(run_steps)
        lines.append(f"RUN {joined}")

    if rep.serve_port:
        lines.extend(["", f"EXPOSE {rep.serve_port}"])

    # Comando di avvio server + attesa porta + esecuzione completa dei test
    cmd_parts: list[str] = []
    if rep.serve_cmd:
        serve_exec = rewrite_subshell_cd(rep.serve_cmd)
        cmd_parts.append(f"{serve_exec} &")
        if rep.serve_port:
            wait_js = (
                f"require('http').get('http://localhost:{rep.serve_port}', "
                "()=>process.exit(0)).on('error', ()=>process.exit(1))"
            )
            cmd_parts.append(
                f"until node -e \"{wait_js}\" 2>/dev/null; do sleep 2; done"
            )
        else:
            cmd_parts.append("sleep 5")

    test_exec = rewrite_subshell_cd(rep.test_cmd)
    # Consente di passare opzionalmente TEST_ARGS a runtime, ma di default esegue tutti i test
    if test_exec.endswith(")"):
        test_exec = test_exec[:-1] + " ${TEST_ARGS:-})"
    else:
        test_exec = f"{test_exec} ${{TEST_ARGS:-}}"
    cmd_parts.append(test_exec)

    full_cmd = " && ".join(cmd_parts).replace(" & && ", " & ")
    escaped_cmd = full_cmd.replace("\\", "\\\\").replace('"', '\\"')
    lines.extend(["", "# Avvio server (se previsto) ed esecuzione di tutti i test E2E"])
    lines.append(f'CMD ["bash", "-c", "{escaped_cmd}"]')
    lines.append("")
    return "\n".join(lines)


def generate_runner_script(
    repo_name: str,
    base_dir: Path,
    clusters: list[dict[str, Any]],
) -> str:
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "-", repo_name.lower())
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f'BASE_DIR="{base_dir}"',
        'REPO_DIR="$BASE_DIR/repo"',
        'DOCKER_DIR="$BASE_DIR/docker"',
        'LOG_DIR="$BASE_DIR/results/logs"',
        'mkdir -p "$LOG_DIR"',
        "",
        "if [ \"$#\" -eq 0 ]; then",
        "    echo \"Uso: $0 <tag1> [tag2 ...]\"",
        "    echo \"Esempio: $0 " + clusters[0]["versions"][0].tag + "\"",
        "    exit 1",
        "fi",
        "",
        "declare -A TAG_TO_DOCKERFILE=(",
    ]
    for idx, cl in enumerate(clusters, 1):
        df_name = cluster_filename(idx, cl["versions"])
        for v in cl["versions"]:
            lines.append(f'    ["{v.tag}"]="{df_name}"')
    lines.extend([
        ")",
        "",
        'cd "$REPO_DIR"',
        "git worktree prune",
        "",
        'for VER in "$@"; do',
        '    DF_NAME="${TAG_TO_DOCKERFILE[$VER]:-}"',
        '    if [ -z "$DF_NAME" ]; then',
        '        echo "Errore: versione $VER non presente nella mappa dei cluster." >&2',
        "        exit 1",
        "    fi",
        '    DOCKERFILE="$DOCKER_DIR/$DF_NAME"',
        f'    WT_DIR="/tmp/{safe_name}-wt-${{VER}}"',
        '    LOG_FILE="$LOG_DIR/test_${VER}.txt"',
        "",
        '    rm -rf "$WT_DIR"',
        '    git worktree add --force "$WT_DIR" "$VER"',
        "",
        '    echo "=== BUILD + TEST PER VERSIONE: $VER ($DF_NAME) ==="',
        f'    docker build --build-arg "APP_VERSION=$VER" -t "{safe_name}-e2e:$VER" -f "$DOCKERFILE" "$WT_DIR"',
        f'    docker run --rm --ipc=host -e "TEST_ARGS=${{TEST_ARGS:-}}" "{safe_name}-e2e:$VER" | tee "$LOG_FILE"',
        '    echo "Completato $VER — Log salvato in: $LOG_FILE"',
        "",
        '    git worktree remove --force "$WT_DIR" 2>/dev/null || rm -rf "$WT_DIR"',
        "done",
        "",
    ])
    return "\n".join(lines)


def format_report(
    repo_name: str,
    analyses: list[VersionAnalysis],
    clusters: list[dict[str, Any]],
) -> str:
    lines: list[str] = []
    lines.append(f"ANALISI MULTI-VERSIONE E CLUSTERING DOCKER: {repo_name}")
    lines.append(f"Versioni analizzate: {len(analyses)} | Cluster individuati: {len(clusters)}")
    lines.append("=" * 115)
    lines.append("")

    lines.append(
        f"{'Tag':<10} | {'Data':<10} | {'Node':<8} | {'PM':<4} | {'E2E':<18} | {'Porta':<5} | {'Build'}"
    )
    lines.append("-" * 115)
    for a in analyses:
        e2e_str = f"{a.e2e_framework} {a.e2e_version}".strip()
        port_str = str(a.serve_port) if a.serve_port else "-"
        build_str = " && ".join(a.build_cmds) if a.build_cmds else "-"
        lines.append(
            f"{a.tag:<10} | {a.date:<10} | {a.node_version:<8} | {a.pkg_manager:<4} | {e2e_str:<18} | {port_str:<5} | {build_str}"
        )

    lines.append("")
    lines.append("=" * 115)
    lines.append("DETTAGLIO CLUSTER (1 Dockerfile per cluster)")
    lines.append("=" * 115)

    for idx, cl in enumerate(clusters, 1):
        rep: VersionAnalysis = cl["representative"]
        vers: list[VersionAnalysis] = cl["versions"]
        tag_list = [v.tag for v in vers]
        df_name = cluster_filename(idx, vers)
        base_img, _ = select_base_image(rep)

        lines.append(f"\n[Cluster {idx}] {df_name} ({len(vers)} versioni)")
        lines.append(f"  Versioni       : {', '.join(tag_list)}")
        lines.append(f"  Base Image     : {base_img}")
        lines.append(f"  Node.js        : {rep.node_version} (fonte: {rep.node_source})")
        lines.append(f"  Package Manager: {rep.pkg_manager} (fonte: {rep.pkg_manager_source})")
        lines.append(f"  Framework E2E  : {rep.e2e_framework} {rep.e2e_version} (dir: {rep.e2e_pkg_dir}, cfg: {rep.e2e_config_file or '-'})")
        if rep.native_deps:
            lines.append(f"  Dip. native C++: {', '.join(rep.native_deps)}")
        if rep.needs_git_repo:
            lines.append("  Git build hook : sì (richiede metadati git per build)")
        lines.append(f"  CI Workflow    : {rep.ci_workflow or '-'}")
        if rep.ci_env:
            lines.append(f"  Env CI         : {', '.join(f'{k}={v}' for k, v in rep.ci_env.items())}")
        lines.append(f"  Install        : {' && '.join(rep.install_cmds)}")
        lines.append(f"  Build          : {' && '.join(rep.build_cmds) if rep.build_cmds else '-'}")
        lines.append(f"  Serve          : {rep.serve_cmd or '-'} (porta: {rep.serve_port or '-'})")
        lines.append(f"  Test           : {rep.test_cmd or '-'}")
        all_notes = sorted({n for v in vers for n in v.notes})
        for n in all_notes:
            lines.append(f"  [!] Nota       : {n}")

    return "\n".join(lines) + "\n"


def resolve_paths(input_path: str) -> tuple[Path, Path]:
    p = Path(input_path).resolve()
    if (p / "repo" / ".git").exists():
        return p, p / "repo"
    if (p / ".git").exists():
        return p.parent, p
    raise FileNotFoundError(f"Repository Git non trovata in '{p}' né in '{p / 'repo'}'")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analizza più versioni di una repository Node.js e genera i Dockerfile per cluster."
    )
    parser.add_argument("repo_path", help="Percorso della cartella progetto (o della cartella repo/)")
    parser.add_argument("--from", dest="from_ver", required=True, help="Versione iniziale (es. 2.12 o v2.12.0)")
    parser.add_argument("--to", dest="to_ver", required=True, help="Versione finale (es. 3 o v3.0.0)")
    parser.add_argument(
        "--only-stable",
        action="store_true",
        help="Considera solo tag stabili (esclude -rc, -dev, -alpha, -beta)",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Esegue solo analisi e clustering senza scrivere i file Docker",
    )
    args = parser.parse_args()

    base_dir, repo_dir = resolve_paths(args.repo_path)
    tags = collect_tags(repo_dir, args.from_ver, args.to_ver, args.only_stable)
    if not tags:
        print("Nessun tag trovato nell'intervallo specificato.", file=sys.stderr)
        return 1

    print(f"Trovate {len(tags)} versioni nell'intervallo [{args.from_ver} .. {args.to_ver}]:")
    print(", ".join(t.name for t in tags))
    print()

    analyses: list[VersionAnalysis] = []
    for idx, t in enumerate(tags, 1):
        print(f"[{idx}/{len(tags)}] Analisi {t.name} ({t.date})...", flush=True)
        analyses.append(analyze_version(repo_dir, t))

    clusters = cluster_analyses(analyses)
    report_txt = format_report(base_dir.name, analyses, clusters)

    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    txt_path = results_dir / "docker_clusters_report.txt"
    json_path = results_dir / "docker_clusters_report.json"

    txt_path.write_text(report_txt, encoding="utf-8")
    json_payload = {
        "repository": base_dir.name,
        "from": args.from_ver,
        "to": args.to_ver,
        "only_stable": args.only_stable,
        "analyses": [asdict(a) for a in analyses],
        "clusters": [
            {
                "id": idx,
                "dockerfile": cluster_filename(idx, cl["versions"]),
                "versions": [v.tag for v in cl["versions"]],
                "representative": asdict(cl["representative"]),
            }
            for idx, cl in enumerate(clusters, 1)
        ],
    }
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    generated_files: list[Path] = []
    if not args.analyze_only:
        docker_dir = base_dir / "docker"
        docker_dir.mkdir(parents=True, exist_ok=True)

        for idx, cl in enumerate(clusters, 1):
            df_name = cluster_filename(idx, cl["versions"])
            df_path = docker_dir / df_name
            df_content = generate_dockerfile(
                base_dir.name, idx, cl["versions"], cl["representative"]
            )
            df_path.write_text(df_content, encoding="utf-8")
            generated_files.append(df_path)

            # BuildKit usa automaticamente <Dockerfile>.dockerignore accanto al Dockerfile
            di_path = docker_dir / f"{df_name}.dockerignore"
            di_path.write_text(
                ".git\nnode_modules\n**/node_modules\nresults\nplaywright-report\ntest-results\n",
                encoding="utf-8",
            )

        runner_path = docker_dir / "esegui_test_docker.sh"
        runner_path.write_text(
            generate_runner_script(base_dir.name, base_dir, clusters),
            encoding="utf-8",
        )
        os.chmod(runner_path, 0o755)
        generated_files.append(runner_path)

    print()
    print(report_txt)
    print(f"Report salvato in:\n  - {txt_path}\n  - {json_path}")
    if generated_files:
        print("File Docker generati:")
        for gf in generated_files:
            print(f"  - {gf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
