#!/usr/bin/env python3
"""analizza_versioni_test_e2e.py — Step 3 della pipeline:
Analizza i range di non aggiornamento dei test E2E direttamente sulle VERSIONI (git tag)
per le repository già clonate in `repositories/repo_nodejs/<repo>/repo`.

Confronta gli SHA-1 dei blob dei file di test E2E tra tag consecutivi tramite `git ls-tree`
(senza checkout e indipendente dalle date dei commit), calcolando:
1. Range di versioni consecutive in cui l'intera suite E2E non è cambiata.
2. Per singolo file di test E2E, il numero massimo di versioni consecutive senza modifiche
   (e gli intervalli esatti tag_inizio -> tag_fine).

Uso:
    python3 02-E2EGit-TestE2E/scripts/git_versioni/analizza_versioni_test_e2e.py --all
    python3 02-E2EGit-TestE2E/scripts/git_versioni/analizza_versioni_test_e2e.py ketcher
    python3 02-E2EGit-TestE2E/scripts/git_versioni/analizza_versioni_test_e2e.py angular-slickgrid --top 15
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT if (ROOT / "data").is_dir() else ROOT.parent
DB_PATH = DATA_ROOT / "data" / "E2EGit_e2e.db"
REPOS_NODEJS_DIR = ROOT / "repositories" / "repo_nodejs"
SUMMARY_TXT = REPOS_NODEJS_DIR / "classifica_versioni_tag.txt"
SUMMARY_CSV = REPOS_NODEJS_DIR / "classifica_versioni_tag.csv"

SEMVER_RE = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[-+].+)?$")
MONOREPO_TAG_RE = re.compile(r"^(?P<pkg>.+)@v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[-+].+)?$")

E2E_FOLDER_HINTS = ("e2e", "cypress", "playwright", "autotests", "acceptance", "integration", "puppeteer")
E2E_EXT_HINTS = (".cy.ts", ".cy.js", ".spec.ts", ".spec.js", ".test.ts", ".test.js", ".e2e.ts", ".e2e.js")


@dataclass
class TagInfo:
    name: str
    date: str
    semver: tuple[int, int, int]
    is_stable: bool
    pkg_prefix: str = ""


def run_git(repo_dir: Path, args: list[str], check: bool = True) -> str:
    res = subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        text=True,
    )
    if check and res.returncode != 0:
        raise RuntimeError(f"Errore git {' '.join(args)}: {res.stderr.strip()}")
    return res.stdout


def resolve_repo_slug(repo_dir: Path, folder_name: str) -> str:
    """Ricava owner/repo dal remote origin o dal DB."""
    remote = run_git(repo_dir, ["remote", "get-url", "origin"], check=False).strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$", remote)
    if m:
        return m.group(1)
    if DB_PATH.exists():
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT name FROM repository WHERE lower(name) LIKE ? LIMIT 1",
                (f"%/{folder_name.lower()}",),
            ).fetchone()
            if row:
                return row[0]
    return folder_name


def load_db_test_paths(repo_slug: str) -> set[str]:
    """Carica i test_path ufficiali dal dataset E2EGit (normalizzati rispetto alla root repo)."""
    if not DB_PATH.exists():
        return set()
    prefix = f"/{repo_slug.replace('/', '_')}/"
    paths: set[str] = set()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT test_path FROM gui_testing_test_details WHERE lower(repository_name) = lower(?)",
            (repo_slug,),
        ).fetchall()
    for (tp,) in rows:
        if tp.startswith(prefix):
            paths.add(tp[len(prefix) :])
        else:
            parts = tp.lstrip("/").split("/", 1)
            paths.add(parts[1] if len(parts) == 2 else tp.lstrip("/"))
    return paths


def is_e2e_test_path(rel_path: str, db_paths: set[str], db_dirs: tuple[str, ...]) -> bool:
    if rel_path in db_paths:
        return True
    low = rel_path.lower()
    if "__tests__" in low or "/unit/" in low or "/node_modules/" in low:
        return False
    if not low.endswith(E2E_EXT_HINTS):
        return False
    if db_dirs and any(low.startswith(d) for d in db_dirs):
        return True
    return any(f"/{h}/" in f"/{low}" for h in E2E_FOLDER_HINTS) or low.endswith((".cy.ts", ".cy.js", ".e2e.ts", ".e2e.js"))


def collect_release_tags(
    repo_dir: Path,
    include_prereleases: bool = False,
    tag_prefix: str | None = None,
    db_dirs: tuple[str, ...] = (),
) -> tuple[list[TagInfo], str]:
    """Raccoglie i tag di release ordinati. Supporta sia tag semver standard sia monorepo (pkg@X.Y.Z)."""
    raw = run_git(
        repo_dir,
        ["for-each-ref", "--sort=creatordate", "--format=%(creatordate:short)\t%(refname:short)", "refs/tags"],
    )
    std_tags: list[TagInfo] = []
    mono_tags: list[TagInfo] = []

    for line in raw.splitlines():
        if not line.strip():
            continue
        date_str, name = line.split("\t", 1)
        if tag_prefix and not name.startswith(tag_prefix):
            continue
        m_std = SEMVER_RE.match(name)
        if m_std:
            is_stable = m_std.group("suffix") is None
            if include_prereleases or is_stable:
                ver = (int(m_std.group("major")), int(m_std.group("minor")), int(m_std.group("patch")))
                std_tags.append(TagInfo(name=name, date=date_str, semver=ver, is_stable=is_stable))
            continue

        m_mono = MONOREPO_TAG_RE.match(name)
        if m_mono:
            is_stable = m_mono.group("suffix") is None
            if include_prereleases or is_stable:
                ver = (int(m_mono.group("major")), int(m_mono.group("minor")), int(m_mono.group("patch")))
                mono_tags.append(
                    TagInfo(name=name, date=date_str, semver=ver, is_stable=is_stable, pkg_prefix=m_mono.group("pkg"))
                )

    counts: dict[str, int] = {}
    for t in mono_tags:
        counts[t.pkg_prefix] = counts.get(t.pkg_prefix, 0) + 1
    top_mono_count = max(counts.values()) if counts else 0

    if std_tags and not (tag_prefix and mono_tags) and len(std_tags) >= top_mono_count:
        std_tags.sort(key=lambda t: (t.semver, t.date, t.name))
        return std_tags, "semver"

    if mono_tags:
        if tag_prefix:
            mono_tags.sort(key=lambda t: (t.semver, t.date, t.name))
            return mono_tags, f"monorepo:{tag_prefix}"
        # Preferisce il prefisso monorepo il cui nome compare nelle cartelle E2E del DB, altrimenti il più frequente
        db_dir_blob = " ".join(db_dirs)
        matching_pkgs = [
            pkg for pkg in counts if pkg.split("/")[-1].lower() in db_dir_blob
        ]
        if matching_pkgs:
            main_pkg = max(matching_pkgs, key=lambda k: counts[k])
        else:
            main_pkg = max(counts, key=lambda k: counts[k])
        filtered = [t for t in mono_tags if t.pkg_prefix == main_pkg]
        filtered.sort(key=lambda t: (t.semver, t.date, t.name))
        return filtered, f"monorepo:{main_pkg}"

    return [], "none"


def list_e2e_blobs_at_tag(
    repo_dir: Path, tag_name: str, db_paths: set[str], db_dirs: tuple[str, ...]
) -> dict[str, str]:
    """Restituisce {rel_path: blob_sha} dei file di test E2E al tag indicato."""
    out = run_git(repo_dir, ["ls-tree", "-r", tag_name])
    blobs: dict[str, str] = {}
    for line in out.splitlines():
        if not line:
            continue
        meta, rel_path = line.split("\t", 1)
        parts = meta.split()
        if len(parts) >= 3 and parts[1] == "blob":
            if is_e2e_test_path(rel_path, db_paths, db_dirs):
                blobs[rel_path] = parts[2]
    return blobs


def count_commits_between(repo_dir: Path, tag_a: str, tag_b: str) -> int:
    out = run_git(repo_dir, ["rev-list", "--count", f"{tag_a}..{tag_b}"], check=False).strip()
    return int(out) if out.isdigit() else 0


def analyze_repository(
    target_dir: Path,
    include_prereleases: bool = False,
    tag_prefix: str | None = None,
    top_n: int = 15,
) -> dict:
    repo_dir = target_dir / "repo" if (target_dir / "repo").is_dir() else target_dir
    results_dir = target_dir / "results" if (target_dir / "repo").is_dir() else target_dir.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    repo_slug = resolve_repo_slug(repo_dir, target_dir.name)
    db_paths = load_db_test_paths(repo_slug)
    db_dirs = tuple(sorted({str(Path(p).parent).lower() + "/" for p in db_paths if "/" in p}))

    tags, tag_mode = collect_release_tags(
        repo_dir,
        include_prereleases=include_prereleases,
        tag_prefix=tag_prefix,
        db_dirs=db_dirs,
    )
    if not tags:
        raise RuntimeError(f"Nessun tag di release trovato in {repo_dir}")

    snapshots: list[dict[str, str]] = [list_e2e_blobs_at_tag(repo_dir, t.name, db_paths, db_dirs) for t in tags]

    # 1. Range a livello di SUITE (tag consecutivi con identico insieme di blob E2E)
    suite_spans: list[dict] = []
    i = 0
    while i < len(tags):
        if not snapshots[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(tags) and snapshots[j + 1] == snapshots[i]:
            j += 1
        span_len = j - i + 1
        if span_len >= 2:
            suite_spans.append(
                {
                    "n_versioni": span_len,
                    "tag_inizio": tags[i].name,
                    "data_inizio": tags[i].date,
                    "tag_fine": tags[j].name,
                    "data_fine": tags[j].date,
                    "n_file_e2e": len(snapshots[i]),
                    "n_commit": count_commits_between(repo_dir, tags[i].name, tags[j].name),
                }
            )
        i = j + 1

    suite_spans.sort(key=lambda s: (s["n_versioni"], s["n_commit"]), reverse=True)

    # 2. Range a livello di SINGOLO FILE DI TEST
    all_test_files = sorted({p for snap in snapshots for p in snap})
    per_file_stats: list[dict] = []

    for path in all_test_files:
        present_indices = [idx for idx, snap in enumerate(snapshots) if path in snap]
        if not present_indices:
            continue

        first_idx = present_indices[0]
        last_idx = present_indices[-1]
        in_latest = last_idx == (len(tags) - 1)

        # Costruisce i run consecutivi in cui il blob SHA rimane identico
        runs: list[dict] = []
        run_start = first_idx
        prev_idx = first_idx
        prev_sha = snapshots[first_idx][path]
        n_modifiche = 0

        for idx in range(first_idx + 1, last_idx + 1):
            curr_sha = snapshots[idx].get(path)
            if curr_sha is None:
                # Il file era assente in questo tag intermedio: chiude il run precedente
                if run_start is not None:
                    runs.append(
                        {
                            "n_versioni": prev_idx - run_start + 1,
                            "tag_inizio": tags[run_start].name,
                            "data_inizio": tags[run_start].date,
                            "tag_fine": tags[prev_idx].name,
                            "data_fine": tags[prev_idx].date,
                        }
                    )
                run_start = None
                prev_sha = None
                continue

            if run_start is None:
                # Ricomparsa
                run_start = idx
                prev_idx = idx
                prev_sha = curr_sha
                n_modifiche += 1
            elif curr_sha == prev_sha:
                prev_idx = idx
            else:
                runs.append(
                    {
                        "n_versioni": prev_idx - run_start + 1,
                        "tag_inizio": tags[run_start].name,
                        "data_inizio": tags[run_start].date,
                        "tag_fine": tags[prev_idx].name,
                        "data_fine": tags[prev_idx].date,
                    }
                )
                n_modifiche += 1
                run_start = idx
                prev_idx = idx
                prev_sha = curr_sha

        if run_start is not None:
            runs.append(
                {
                    "n_versioni": prev_idx - run_start + 1,
                    "tag_inizio": tags[run_start].name,
                    "data_inizio": tags[run_start].date,
                    "tag_fine": tags[prev_idx].name,
                    "data_fine": tags[prev_idx].date,
                }
            )

        best_run = max(runs, key=lambda r: r["n_versioni"])
        n_commit_gap = count_commits_between(repo_dir, best_run["tag_inizio"], best_run["tag_fine"])
        stato = (
            "Attivo (mai modificato)"
            if in_latest and n_modifiche == 0
            else ("Attivo (modificato)" if in_latest else f"Rimosso dopo {tags[last_idx].name}")
        )

        per_file_stats.append(
            {
                "test_path": path,
                "fonte": "E2EGit_db" if path in db_paths else "PostSnapshot_pattern",
                "nascita_tag": tags[first_idx].name,
                "nascita_data": tags[first_idx].date,
                "ultimo_tag": tags[last_idx].name,
                "versioni_vita": len(present_indices),
                "n_modifiche": n_modifiche,
                "max_ver_invariate": best_run["n_versioni"],
                "max_gap_inizio": best_run["tag_inizio"],
                "max_gap_fine": best_run["tag_fine"],
                "max_gap_date": f"{best_run['data_inizio']} -> {best_run['data_fine']}",
                "max_gap_commit": n_commit_gap,
                "stato": stato,
            }
        )

    per_file_stats.sort(key=lambda x: (x["max_ver_invariate"], x["versioni_vita"], -x["n_modifiche"]), reverse=True)

    max_suite = suite_spans[0] if suite_spans else None
    max_file = per_file_stats[0] if per_file_stats else None

    report_data = {
        "repository": repo_slug,
        "folder": target_dir.name,
        "tag_mode": tag_mode,
        "n_tag_analizzati": len(tags),
        "primo_tag": f"{tags[0].name} ({tags[0].date})",
        "ultimo_tag": f"{tags[-1].name} ({tags[-1].date})",
        "n_file_e2e_distinti": len(all_test_files),
        "n_file_db": len(db_paths),
        "suite_spans_top": suite_spans[:top_n],
        "per_file_stats_top": per_file_stats[:top_n],
        "per_file_stats_all": per_file_stats,
    }

    txt_lines = [
        f"ANALISI VERSIONI (GIT TAG) TEST E2E: {repo_slug}",
        "=" * 110,
        f"Tag analizzati ({tag_mode}): {len(tags)} | Range completo: {tags[0].name} ({tags[0].date}) -> {tags[-1].name} ({tags[-1].date})",
        f"File di test E2E tracciati: {len(all_test_files)} (di cui {len(db_paths)} presenti in E2EGit_e2e.db)",
        "",
        f"--- 1. INTERA SUITE E2E FERMA TRA VERSIONI CONSECUTIVE (Top {top_n}) ---",
    ]
    if suite_spans:
        txt_lines.append(f"{'N.Ver':<6} | {'Tag Inizio':<20} | {'Tag Fine':<20} | {'Date':<24} | {'File':<5} | {'Commit'}")
        txt_lines.append("-" * 100)
        for s in suite_spans[:top_n]:
            txt_lines.append(
                f"{s['n_versioni']:<6} | {s['tag_inizio']:<20} | {s['tag_fine']:<20} | "
                f"{s['data_inizio']} -> {s['data_fine']} | {s['n_file_e2e']:<5} | {s['n_commit']}"
            )
    else:
        txt_lines.append("Nessun intervallo di >= 2 versioni consecutive con suite E2E completamente invariata.")

    txt_lines += [
        "",
        f"--- 2. SINGOLI FILE DI TEST CON PIÙ VERSIONI CONSECUTIVE INVARIATE (Top {top_n}) ---",
        f"{'MaxVer':<6} | {'Mod':<4} | {'Range Tag Invariato':<36} | {'Commit':<6} | {'Stato':<25} | {'File di Test'}",
        "-" * 130,
    ]
    for f in per_file_stats[:top_n]:
        rng = f"{f['max_gap_inizio']} -> {f['max_gap_fine']}"
        txt_lines.append(
            f"{f['max_ver_invariate']:<6} | {f['n_modifiche']:<4} | {rng:<36} | "
            f"{f['max_gap_commit']:<6} | {f['stato']:<25} | {f['test_path']}"
        )

    out_txt = results_dir / "versioni_e2e_report.txt"
    out_json = results_dir / "versioni_e2e_report.json"
    out_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    out_json.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "repository": repo_slug,
        "folder": target_dir.name,
        "tag_mode": tag_mode,
        "n_tag": len(tags),
        "n_file_e2e": len(all_test_files),
        "max_suite_ver": max_suite["n_versioni"] if max_suite else 1,
        "max_suite_range": f"{max_suite['tag_inizio']} -> {max_suite['tag_fine']}" if max_suite else "-",
        "max_suite_commit": max_suite["n_commit"] if max_suite else 0,
        "max_file_ver": max_file["max_ver_invariate"] if max_file else 0,
        "max_file_mod": max_file["n_modifiche"] if max_file else 0,
        "max_file_range": f"{max_file['max_gap_inizio']} -> {max_file['max_gap_fine']}" if max_file else "-",
        "max_file_path": max_file["test_path"] if max_file else "-",
        "out_txt": str(out_txt),
    }


def resolve_targets(args: argparse.Namespace) -> list[Path]:
    if args.all:
        return sorted(p.parent.parent for p in REPOS_NODEJS_DIR.glob("*/repo/.git") if p.is_dir())
    targets = []
    for t in args.targets:
        p = Path(t)
        if not p.exists():
            p = REPOS_NODEJS_DIR / t
        if (p / "repo" / ".git").is_dir() or (p / ".git").is_dir():
            targets.append(p.resolve())
        else:
            raise FileNotFoundError(f"Repository non trovata: {t}")
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description="Step 3: analisi range di non aggiornamento dei test E2E per versioni (git tag).")
    parser.add_argument("targets", nargs="*", help="Nome cartella o path della repository (es. ketcher, angular-slickgrid)")
    parser.add_argument("--all", action="store_true", help="Analizza tutte le repository clonate in repositories/repo_nodejs/")
    parser.add_argument("--include-prereleases", action="store_true", help="Include anche pre-release (rc, alpha, beta)")
    parser.add_argument("--tag-prefix", default=None, help="Filtra i tag per prefisso (utile per monorepo)")
    parser.add_argument("--top", type=int, default=15, help="Numero di righe top nei report (default: 15)")
    args = parser.parse_args()

    if not args.all and not args.targets:
        parser.error("Specifica almeno una repository oppure usa --all")

    targets = resolve_targets(args)
    summaries = []
    errors = []
    for t in targets:
        try:
            summary = analyze_repository(
                t,
                include_prereleases=args.include_prereleases,
                tag_prefix=args.tag_prefix,
                top_n=args.top,
            )
            summaries.append(summary)
        except Exception as exc:
            errors.append((t.name, str(exc)))
            print(f"[WARN] {t.name}: {exc}")

    if not summaries:
        raise RuntimeError("Nessuna repository analizzata con successo.")

    summaries.sort(key=lambda s: (s["max_suite_ver"], s["max_file_ver"]), reverse=True)

    header = (
        f"{'Repository':<30} | {'Tag':<5} | {'File':<5} | {'SuiteMaxVer':<11} | "
        f"{'Suite Range':<26} | {'FileMaxVer':<10} | {'File Range (test più fermo)'}"
    )
    sep = "-" * 135
    lines = [
        "RIEPILOGO STEP 3 — RANGE DI NON AGGIORNAMENTO PER VERSIONI (GIT TAG)",
        "=" * 135,
        header,
        sep,
    ]
    for s in summaries:
        lines.append(
            f"{s['repository']:<30} | {s['n_tag']:<5} | {s['n_file_e2e']:<5} | {s['max_suite_ver']:<11} | "
            f"{s['max_suite_range']:<26} | {s['max_file_ver']:<10} | {s['max_file_range']} ({Path(s['max_file_path']).name})"
        )

    out_text = "\n".join(lines)
    print(out_text)

    if len(summaries) > 1 or args.all:
        SUMMARY_TXT.write_text(out_text + "\n", encoding="utf-8")
        with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
            writer.writeheader()
            writer.writerows(summaries)
        print(f"\nRiepilogo salvato in:\n- {SUMMARY_TXT}\n- {SUMMARY_CSV}")


if __name__ == "__main__":
    main()
