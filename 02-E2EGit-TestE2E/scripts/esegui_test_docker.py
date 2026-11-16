#!/usr/bin/env python3
"""esegui_test_docker.py — Step 5 della pipeline:
Esegue in parallelo build Docker e test E2E su un intervallo di versioni
(o su tutte le versioni mappate in `results/docker_clusters_report.json`).

Caratteristiche principali:
- Risolve automaticamente le versioni nell'intervallo `--from .. --to` oppure `--tags`.
- Esegue `docker build` + `docker run` in parallelo fino a `--jobs` worker contemporanei.
- Protegge le operazioni `git worktree` con lock per evitare race condition.
- Non si ferma se una versione fallisce: distingue `PASS`, `TEST_FAIL` e `BUILD_FAIL`.
- Salva i log individuali in `results/logs/test_<ver>.txt` e un riepilogo finale in
  `results/esecuzione_test_report.txt` e `.csv`.

Uso:
    python3 02-E2EGit-TestE2E/scripts/esegui_test_docker.py equal-access --from 3.1.7 --to 3.1.15 -j 2
    python3 02-E2EGit-TestE2E/scripts/esegui_test_docker.py equal-access --prune-images -j 2
    python3 02-E2EGit-TestE2E/scripts/esegui_test_docker.py equal-access --dry-run
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOS_NODEJS_DIR = ROOT / "repositories" / "repo_nodejs"

SEMVER_RE = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[-+].+)?$")
PARTIAL_VER_RE = re.compile(r"^v?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?$")

GIT_WORKTREE_LOCK = threading.Lock()


def resolve_repo_dir(repo_arg: str) -> tuple[Path, Path]:
    p = Path(repo_arg)
    if not p.exists():
        p = REPOS_NODEJS_DIR / repo_arg
    p = p.resolve()
    if (p / "repo" / ".git").is_dir():
        return p, p / "repo"
    if (p / ".git").is_dir():
        return p.parent, p
    raise FileNotFoundError(f"Repository non trovata: {repo_arg}")


def parse_semver_tuple(ver: str) -> tuple[int, int, int] | None:
    m = SEMVER_RE.match(ver.strip())
    if not m:
        return None
    return int(m.group("major")), int(m.group("minor")), int(m.group("patch"))


def parse_bound(bound: str, is_upper: bool) -> tuple[int, int, int] | None:
    m_exact = SEMVER_RE.match(bound.strip())
    if m_exact:
        return (
            int(m_exact.group("major")),
            int(m_exact.group("minor")),
            int(m_exact.group("patch")),
        )
    m = PARTIAL_VER_RE.match(bound.strip())
    if not m:
        return None
    major = int(m.group("major"))
    if m.group("minor") is None:
        return (major, 999999, 999999) if is_upper else (major, 0, 0)
    minor = int(m.group("minor"))
    if m.group("patch") is None:
        return (major, minor, 999999) if is_upper else (major, minor, 0)
    return major, minor, int(m.group("patch"))


def load_plan_from_dockerfiles(base_dir: Path, repo_dir: Path) -> list[tuple[str, str]]:
    """Fallback quando manca docker_clusters_report.json (es. angular-slickgrid):
    mappa i tag git sui Dockerfile.<from>-<to> presenti in docker/.
    """
    docker_dir = base_dir / "docker"
    ranges: list[tuple[tuple[int, int, int], tuple[int, int, int], str]] = []
    for df in sorted(docker_dir.glob("Dockerfile.*")):
        if df.name.endswith(".dockerignore"):
            continue
        suffix = df.name[len("Dockerfile.") :]
        if "-" in suffix:
            left, right = suffix.split("-", 1)
            lb = parse_bound(left, is_upper=False)
            ub = parse_bound(right, is_upper=True)
        else:
            lb = parse_bound(suffix, is_upper=False)
            ub = parse_bound(suffix, is_upper=True)
        if lb and ub:
            ranges.append((lb, ub, df.name))

    if not ranges:
        raise FileNotFoundError(
            f"Né {base_dir / 'results' / 'docker_clusters_report.json'} né Dockerfile.<range> validi trovati in {docker_dir}"
        )

    raw = subprocess.run(
        ["git", "-C", str(repo_dir), "for-each-ref", "--sort=creatordate", "--format=%(refname:short)", "refs/tags"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    matched: list[tuple[tuple[int, int, int], str, str]] = []
    for name in raw.splitlines():
        name = name.strip()
        m = SEMVER_RE.match(name)
        if not m or m.group("suffix") is not None:
            continue
        sv = (int(m.group("major")), int(m.group("minor")), int(m.group("patch")))
        for lb, ub, df_name in ranges:
            if lb <= sv <= ub:
                matched.append((sv, name, df_name))
                break

    matched.sort(key=lambda x: x[0])
    return [(name, df_name) for _, name, df_name in matched]


def load_version_plan(base_dir: Path, repo_dir: Path) -> list[tuple[str, str]]:
    """Restituisce lista ordinata [(tag, dockerfile_name), ...] da docker_clusters_report.json o fallback docker/."""
    report_json = base_dir / "results" / "docker_clusters_report.json"
    if not report_json.is_file():
        return load_plan_from_dockerfiles(base_dir, repo_dir)
    data = json.loads(report_json.read_text(encoding="utf-8"))

    tag_to_df: dict[str, str] = {}
    ordered_tags: list[str] = []
    for cl in data.get("clusters", []):
        df_name = cl["dockerfile"]
        for ver in cl.get("versions", []):
            tag_to_df[ver] = df_name
            ordered_tags.append(ver)

    # Mantiene l'ordine di `analyses` se disponibile
    analyses_order = [a["tag"] for a in data.get("analyses", []) if a.get("tag") in tag_to_df]
    if analyses_order:
        return [(t, tag_to_df[t]) for t in analyses_order]
    return [(t, tag_to_df[t]) for t in ordered_tags]


def filter_plan(
    plan: list[tuple[str, str]],
    from_ver: str | None,
    to_ver: str | None,
    explicit_tags: list[str] | None,
) -> list[tuple[str, str]]:
    if explicit_tags:
        tag_map = dict(plan)
        selected = []
        for t in explicit_tags:
            if t not in tag_map:
                raise ValueError(f"Tag '{t}' non presente in docker_clusters_report.json")
            selected.append((t, tag_map[t]))
        return selected

    if not from_ver and not to_ver:
        return plan

    lower = parse_bound(from_ver, is_upper=False) if from_ver else None
    upper = parse_bound(to_ver, is_upper=True) if to_ver else None

    # Se entrambi i bound non sono semver, usa indice testuale nel piano
    if (from_ver and lower is None) or (to_ver and upper is None):
        names = [t for t, _ in plan]
        start_idx = names.index(from_ver) if from_ver else 0
        end_idx = names.index(to_ver) if to_ver else len(plan) - 1
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx
        return plan[start_idx : end_idx + 1]

    selected = []
    for tag, df_name in plan:
        sv = parse_semver_tuple(tag)
        if sv is None:
            continue
        if lower and sv < lower:
            continue
        if upper and sv > upper:
            continue
        selected.append((tag, df_name))
    return selected


def run_single_version(
    repo_name: str,
    base_dir: Path,
    repo_dir: Path,
    ver: str,
    df_name: str,
    test_args: str,
    timeout_sec: int,
    prune_images: bool,
) -> dict:
    docker_dir = base_dir / "docker"
    log_dir = base_dir / "results" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    dockerfile = docker_dir / df_name
    safe_repo = re.sub(r"[^a-z0-9_.-]", "-", repo_name.lower())
    safe_ver = re.sub(r"[^a-zA-Z0-9_.-]", "-", ver)
    image_tag = f"{safe_repo}-e2e:{safe_ver}"
    container_name = f"{safe_repo}-run-{safe_ver}-{os.getpid()}"
    wt_dir = Path(f"/tmp/{safe_repo}-wt-{safe_ver}")
    log_file = log_dir / f"test_{safe_ver}.txt"

    start_ts = time.monotonic()
    build_rc: int | str = "-"
    test_rc: int | str = "-"
    esito = "BUILD_FAIL"
    log_chunks: list[str] = [
        f"=== REPO: {repo_name} | VERSIONE: {ver} | DOCKERFILE: {df_name} ===",
        f"Start: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    try:
        with GIT_WORKTREE_LOCK:
            if wt_dir.exists():
                shutil.rmtree(wt_dir, ignore_errors=True)
            subprocess.run(
                ["git", "-C", str(repo_dir), "worktree", "prune"],
                capture_output=True,
                text=True,
            )
            wt_res = subprocess.run(
                ["git", "-C", str(repo_dir), "worktree", "add", "--force", str(wt_dir), ver],
                capture_output=True,
                text=True,
            )
        if wt_res.returncode != 0:
            log_chunks.append("[ERROR] git worktree add fallito:")
            log_chunks.append(wt_res.stdout)
            log_chunks.append(wt_res.stderr)
            esito = "WORKTREE_FAIL"
            return {
                "versione": ver,
                "dockerfile": df_name,
                "esito": esito,
                "build_rc": build_rc,
                "test_rc": test_rc,
                "durata_sec": round(time.monotonic() - start_ts, 1),
                "log_file": str(log_file),
            }

        # 1. Docker build
        build_cmd = [
            "docker",
            "build",
            "--build-arg",
            f"APP_VERSION={ver}",
            "-t",
            image_tag,
            "-f",
            str(dockerfile),
            str(wt_dir),
        ]
        log_chunks.append(f"--- DOCKER BUILD: {' '.join(build_cmd)} ---")
        try:
            b_res = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec if timeout_sec > 0 else None,
            )
            build_rc = b_res.returncode
            log_chunks.append(b_res.stdout)
            if b_res.stderr:
                log_chunks.append(b_res.stderr)
        except subprocess.TimeoutExpired as exc:
            build_rc = "TIMEOUT"
            esito = "BUILD_TIMEOUT"
            log_chunks.append((exc.stdout or "") if isinstance(exc.stdout, str) else "")
            log_chunks.append(f"\n[TIMEOUT] Build interrotta dopo {timeout_sec}s")
            return {
                "versione": ver,
                "dockerfile": df_name,
                "esito": esito,
                "build_rc": build_rc,
                "test_rc": test_rc,
                "durata_sec": round(time.monotonic() - start_ts, 1),
                "log_file": str(log_file),
            }

        if build_rc != 0:
            esito = "BUILD_FAIL"
            return {
                "versione": ver,
                "dockerfile": df_name,
                "esito": esito,
                "build_rc": build_rc,
                "test_rc": test_rc,
                "durata_sec": round(time.monotonic() - start_ts, 1),
                "log_file": str(log_file),
            }

        # 2. Docker run
        run_cmd = [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "--ipc=host",
            "-e",
            f"TEST_ARGS={test_args}",
            image_tag,
        ]
        log_chunks.append(f"\n--- DOCKER RUN: {' '.join(run_cmd)} ---")
        try:
            t_res = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec if timeout_sec > 0 else None,
            )
            test_rc = t_res.returncode
            log_chunks.append(t_res.stdout)
            if t_res.stderr:
                log_chunks.append(t_res.stderr)
            esito = "PASS" if test_rc == 0 else "TEST_FAIL"
        except subprocess.TimeoutExpired as exc:
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
            test_rc = "TIMEOUT"
            esito = "TEST_TIMEOUT"
            log_chunks.append((exc.stdout or "") if isinstance(exc.stdout, str) else "")
            log_chunks.append(f"\n[TIMEOUT] Test interrotto dopo {timeout_sec}s")

        return {
            "versione": ver,
            "dockerfile": df_name,
            "esito": esito,
            "build_rc": build_rc,
            "test_rc": test_rc,
            "durata_sec": round(time.monotonic() - start_ts, 1),
            "log_file": str(log_file),
        }
    finally:
        log_chunks.append(f"\n=== ESITO FINALE: {esito} (durata: {round(time.monotonic() - start_ts, 1)}s) ===")
        log_file.write_text("\n".join(log_chunks) + "\n", encoding="utf-8")

        with GIT_WORKTREE_LOCK:
            subprocess.run(
                ["git", "-C", str(repo_dir), "worktree", "remove", "--force", str(wt_dir)],
                capture_output=True,
            )
            if wt_dir.exists():
                shutil.rmtree(wt_dir, ignore_errors=True)

        if prune_images:
            subprocess.run(["docker", "rmi", "-f", image_tag], capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Step 5: build Docker ed esecuzione test E2E in parallelo su un intervallo di versioni."
    )
    parser.add_argument("repo", help="Nome cartella in repositories/repo_nodejs/ o path completo")
    parser.add_argument("--from", dest="from_ver", default=None, help="Versione iniziale (es. 3.1.7)")
    parser.add_argument("--to", dest="to_ver", default=None, help="Versione finale (es. 3.1.15)")
    parser.add_argument("--tags", nargs="+", default=None, help="Lista esplicita di tag da eseguire")
    parser.add_argument("-j", "--jobs", type=int, default=2, help="Numero di versioni in parallelo (default: 2)")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in secondi per build/run (default: 1800, 0=illimitato)")
    parser.add_argument("--test-args", default="", help="Argomenti extra passati a TEST_ARGS nel container")
    parser.add_argument("--prune-images", action="store_true", help="Rimuove l'immagine Docker subito dopo il test per risparmiare disco")
    parser.add_argument("--dry-run", action="store_true", help="Mostra le versioni selezionate e i Dockerfile senza eseguire Docker")
    args = parser.parse_args()

    base_dir, repo_dir = resolve_repo_dir(args.repo)
    plan = load_version_plan(base_dir, repo_dir)
    selected = filter_plan(plan, args.from_ver, args.to_ver, args.tags)

    if not selected:
        print("Nessuna versione trovata nell'intervallo specificato.")
        return 1

    print(f"Repository: {base_dir.name} | Versioni selezionate: {len(selected)} | Worker paralleli: {args.jobs}")
    if args.dry_run:
        print("\n[DRY-RUN] Piano di esecuzione:")
        for ver, df_name in selected:
            print(f"  - {ver:<16} -> {df_name}")
        return 0

    results_by_ver: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        future_map = {
            ex.submit(
                run_single_version,
                base_dir.name,
                base_dir,
                repo_dir,
                ver,
                df_name,
                args.test_args,
                args.timeout,
                args.prune_images,
            ): ver
            for ver, df_name in selected
        }
        for idx, fut in enumerate(concurrent.futures.as_completed(future_map), 1):
            r = fut.result()
            results_by_ver[r["versione"]] = r
            print(
                f"[{idx}/{len(selected)}] {r['versione']:<16} -> {r['esito']:<13} "
                f"(build={r['build_rc']}, test={r['test_rc']}, {r['durata_sec']}s)",
                flush=True,
            )

    ordered_results = [results_by_ver[ver] for ver, _ in selected]

    lines = [
        f"REPORT ESECUZIONE TEST DOCKER: {base_dir.name}",
        "=" * 105,
        f"{'Versione':<16} | {'Esito':<13} | {'BuildRC':<7} | {'TestRC':<7} | {'Durata(s)':<9} | {'Dockerfile'}",
        "-" * 105,
    ]
    for r in ordered_results:
        lines.append(
            f"{r['versione']:<16} | {r['esito']:<13} | {str(r['build_rc']):<7} | "
            f"{str(r['test_rc']):<7} | {str(r['durata_sec']):<9} | {r['dockerfile']}"
        )

    counts = {
        "PASS": sum(1 for r in ordered_results if r["esito"] == "PASS"),
        "TEST_FAIL": sum(1 for r in ordered_results if r["esito"] == "TEST_FAIL"),
        "BUILD_FAIL": sum(1 for r in ordered_results if r["esito"] not in ("PASS", "TEST_FAIL")),
    }
    lines += [
        "",
        f"Riepilogo: PASS={counts['PASS']} | TEST_FAIL={counts['TEST_FAIL']} | ALTRO/BUILD_FAIL={counts['BUILD_FAIL']}",
    ]

    report_txt = base_dir / "results" / "esecuzione_test_report.txt"
    report_csv = base_dir / "results" / "esecuzione_test_report.csv"
    report_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with report_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ordered_results[0].keys()))
        writer.writeheader()
        writer.writerows(ordered_results)

    print()
    print("\n".join(lines))
    print(f"\nReport salvato in:\n- {report_txt}\n- {report_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

