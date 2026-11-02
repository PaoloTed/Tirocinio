#!/usr/bin/env python3
"""03_filtra_node_ranking.py — Estrazione e ranking dei repository Node.js (JS/TS) da E2EGit.db.

Risponde all'obiettivo del 1° Ricevimento con il Prof. Starace:
- Filtra i repository con test E2E GUI nell'ecosistema Node.js (JavaScript / TypeScript).
- Ordina i repository per volume di test e attività (commit, stelle, contributor).
- Identifica i framework E2E principali (Cypress, Playwright, Puppeteer).
- Esporta la classifica in formato CSV e Markdown (in results/).

Uso:
    python src/03_filtra_node_ranking.py
    python src/03_filtra_node_ranking.py --limit 30
    python src/03_filtra_node_ranking.py --framework cypress
    python src/03_filtra_node_ranking.py --framework playwright
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DB_PATH = DATA / "E2EGit.db"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estrae e classifica i repository Node.js (JS/TS) con test E2E da E2EGit.db."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help="Percorso di E2EGit.db (default: data/E2EGit.db)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Numero di repository da mostrare/esportare (default: 20; 0 per tutti)",
    )
    parser.add_argument(
        "--framework",
        choices=["all", "cypress", "playwright", "puppeteer"],
        default="all",
        help="Filtra per framework specifico (default: all)",
    )
    parser.add_argument(
        "--min-commits",
        type=int,
        default=100,
        help="Numero minimo di commit totali (default: 100)",
    )
    parser.add_argument(
        "--min-tests",
        type=int,
        default=5,
        help="Numero minimo di test GUI (default: 5)",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=RESULTS / "top_node_repositories.csv",
        help="File di output CSV (default: results/top_node_repositories.csv)",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=RESULTS / "top_node_repositories.md",
        help="File di output Markdown (default: results/top_node_repositories.md)",
    )
    return parser.parse_args()


def determine_primary_framework(row: dict) -> str:
    counts = {
        "Cypress": row["cypress_files"],
        "Playwright": row["playwright_files"],
        "Puppeteer": row["puppeteer_files"],
        "Selenium": row["selenium_files"],
    }
    sorted_frameworks = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top_name, top_val = sorted_frameworks[0]
    if top_val == 0:
        return "Altro"
    # Se il secondo framework ha anch'esso dei test, segnaliamo la co-presenza
    sec_name, sec_val = sorted_frameworks[1]
    if sec_val > 0 and sec_val >= top_val * 0.3:
        return f"{top_name} + {sec_name}"
    return top_name


def fetch_ranked_repositories(
    conn: sqlite3.Connection,
    min_commits: int,
    min_tests: int,
    framework_filter: str,
    limit: int,
) -> list[dict]:
    query = """
    SELECT 
        g.repository_name,
        r.main_language,
        r.commits,
        r.stargazers,
        r.contributors,
        r.last_commit,
        r.last_commit_sha,
        g.number_of_tests,
        g.number_of_files,
        (g.number_files_cypress_js + g.number_files_cypress_ts) AS cypress_files,
        (g.number_files_playwright_js + g.number_files_playwright_ts) AS playwright_files,
        (g.number_files_puppeteer_js + g.number_files_puppeteer_ts) AS puppeteer_files,
        (g.number_files_selenium_js + g.number_files_selenium_ts) AS selenium_files,
        g.with_jest,
        g.with_mocha
    FROM gui_testing_repo_details g
    JOIN repository r ON g.repository_name = r.name
    WHERE r.main_language IN ('JavaScript', 'TypeScript')
      AND r.commits >= ?
      AND g.number_of_tests >= ?
      AND (
          (g.number_files_cypress_js + g.number_files_cypress_ts) > 0 OR
          (g.number_files_playwright_js + g.number_files_playwright_ts) > 0 OR
          (g.number_files_puppeteer_js + g.number_files_puppeteer_ts) > 0 OR
          (g.number_files_selenium_js + g.number_files_selenium_ts) > 0
      )
    ORDER BY g.number_of_tests DESC, r.commits DESC
    """
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(query, (min_commits, min_tests))
    raw_rows = [dict(r) for r in cursor.fetchall()]

    processed = []
    for rank, row in enumerate(raw_rows, start=1):
        framework = determine_primary_framework(row)

        if framework_filter != "all":
            if framework_filter.lower() not in framework.lower():
                continue

        # Test runner
        runners = []
        if row["with_jest"]:
            runners.append("Jest")
        if row["with_mocha"]:
            runners.append("Mocha")
        runner_str = ", ".join(runners) if runners else "Default"

        entry = {
            "rank": rank,
            "repository": row["repository_name"],
            "language": row["main_language"],
            "primary_framework": framework,
            "num_tests": row["number_of_tests"],
            "num_files": row["number_of_files"],
            "commits": row["commits"],
            "stars": row["stargazers"],
            "contributors": row["contributors"],
            "test_runner": runner_str,
            "cypress_files": row["cypress_files"],
            "playwright_files": row["playwright_files"],
            "puppeteer_files": row["puppeteer_files"],
            "last_commit_date": (row["last_commit"] or "")[:10],
            "last_commit_sha": row["last_commit_sha"],
            "url": f"https://github.com/{row['repository_name']}",
        }
        processed.append(entry)

    if limit > 0:
        return processed[:limit]
    return processed


def print_table(rows: list[dict]) -> None:
    header = (
        f"{'#':<3} | {'Repository':<38} | {'Lang':<4} | {'Framework':<18} | "
        f"{'Test':<6} | {'Files':<5} | {'Commits':<7} | {'Stars':<6}"
    )
    sep = "-" * len(header)
    print("\n" + sep)
    print(header)
    print(sep)
    for r in rows:
        lang_short = "TS" if r["language"] == "TypeScript" else "JS"
        print(
            f"{r['rank']:<3} | {r['repository']:<38} | {lang_short:<4} | {r['primary_framework']:<18} | "
            f"{r['num_tests']:<6} | {r['num_files']:<5} | {r['commits']:<7} | {r['stars']:<6}"
        )
    print(sep + "\n")


def export_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rank",
        "repository",
        "language",
        "primary_framework",
        "num_tests",
        "num_files",
        "commits",
        "stars",
        "contributors",
        "test_runner",
        "cypress_files",
        "playwright_files",
        "puppeteer_files",
        "last_commit_date",
        "last_commit_sha",
        "url",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[✓] CSV salvato in: {path}")


def export_markdown(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Classifica Progetti Node.js (JavaScript/TypeScript) con Test E2E",
        "",
        f"> Estratto da `E2EGit.db` — Top {len(rows)} repository ordinati per numero di test GUI e commit.",
        "",
        "| # | Repository | Linguaggio | Framework E2E | N. Test | N. File | Commit Totali | Stelle GitHub | Contributor | URL |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['rank']} | **`{r['repository']}`** | {r['language']} | {r['primary_framework']} | "
            f"{r['num_tests']:,} | {r['num_files']} | {r['commits']:,} | {r['stars']:,} | "
            f"{r['contributors']} | [GitHub]({r['url']}) |"
        )
    lines.append("")
    lines.append("### Note sui migliori candidati pilota:")
    lines.append("- **Cypress**: vedi `sap/spartacus`, `n8n-io/n8n`, `module-federation/...`")
    lines.append("- **Playwright**: vedi `epam/ketcher`, `tryghost/koenig`, `primer/react`, `payloadcms/payload`")
    lines.append("- **Misti (migrazione o entrambi)**: `ionic-team/ionic-framework`")
    lines.append("")

    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[✓] Markdown salvato in: {path}")


def main() -> None:
    args = parse_args()

    if not args.db.is_file():
        print(f"[ERRORE] Database non trovato in {args.db}", file=sys.stderr)
        sys.exit(1)

    with sqlite3.connect(args.db) as conn:
        ranked = fetch_ranked_repositories(
            conn=conn,
            min_commits=args.min_commits,
            min_tests=args.min_tests,
            framework_filter=args.framework,
            limit=args.limit,
        )

    if not ranked:
        print("[!] Nessun repository trovato con i filtri selezionati.")
        return

    print(f"\n[+] Trovati {len(ranked)} repository Node.js (filtro framework: '{args.framework}'):")
    print_table(ranked)
    export_csv(ranked, args.csv_out)
    export_markdown(ranked, args.md_out)


if __name__ == "__main__":
    main()

