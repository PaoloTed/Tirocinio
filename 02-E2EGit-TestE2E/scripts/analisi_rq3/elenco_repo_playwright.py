#!/usr/bin/env python3
"""elenco_repo_playwright.py — Estrae l'elenco dei repository Node.js (JS/TS)
con test > 10 e release > 5 che utilizzano esclusivamente Playwright.

Uso:
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/elenco_repo_playwright.py
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/elenco_repo_playwright.py --min-tests 10 --min-releases 5
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classifica_repo_rq3 import DB_PATH, ROOT, RQ3_COMMIT_DIR, format_table  # noqa: E402

OUT_TXT = ROOT / "repositories" / "repo_nodejs" / "repository_nodejs_playwright.txt"
OUT_CSV = ROOT / "repositories" / "repo_nodejs" / "repository_nodejs_playwright.csv"

QUERY_PURE_PLAYWRIGHT = """
SELECT
    r.name AS repository,
    r.main_language AS language,
    r.stargazers AS stars,
    r.releases AS releases,
    g.number_of_files AS test_files,
    g.number_of_tests AS total_tests,
    r.commits AS total_commits,
    g.number_files_playwright_js AS pw_js,
    g.number_files_playwright_ts AS pw_ts
FROM repository r
JOIN gui_testing_repo_details g ON r.name = g.repository_name
WHERE r.main_language IN ('JavaScript', 'TypeScript')
  AND g.number_of_tests > ?
  AND r.releases > ?
  AND (g.number_files_playwright_js + g.number_files_playwright_ts) > 0
  AND (
      g.number_files_selenium_java + g.number_files_selenium_js
      + g.number_files_selenium_ts + g.number_files_selenium_py
      + g.number_files_playwright_java + g.number_files_playwright_py
      + g.number_files_puppeteer_js + g.number_files_puppeteer_ts
      + g.number_files_puppeteer_py + g.number_files_cypress_js
      + g.number_files_cypress_ts
  ) = 0
ORDER BY r.stargazers DESC;
"""


def fetch_pure_playwright_repos(min_tests: int, min_releases: int) -> list[dict]:
    """Interroga E2EGit_e2e.db e verifica la presenza in RQ3/commit-analysis."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = [
            dict(r)
            for r in conn.execute(QUERY_PURE_PLAYWRIGHT, (min_tests, min_releases)).fetchall()
        ]

    for idx, row in enumerate(rows, start=1):
        row["pos"] = idx
        rq3_dir = RQ3_COMMIT_DIR / row["repository"].replace("/", "_")
        row["in_rq3"] = "si" if rq3_dir.is_dir() and any(rq3_dir.iterdir()) else "no"
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Elenca i repository Node.js (JS/TS) esclusivamente Playwright."
    )
    parser.add_argument("--min-tests", type=int, default=10, help="Numero minimo di test GUI (default: 10)")
    parser.add_argument("--min-releases", type=int, default=5, help="Numero minimo di release (default: 5)")
    args = parser.parse_args()

    repos = fetch_pure_playwright_repos(args.min_tests, args.min_releases)
    in_rq3_count = sum(1 for r in repos if r["in_rq3"] == "si")

    repo_w = max(len("Repository"), max((len(r["repository"]) for r in repos), default=0))
    cols = [
        ("pos", "Pos", 3),
        ("repository", "Repository", repo_w),
        ("language", "Linguaggio", 10),
        ("stars", "Stelle", 6),
        ("releases", "Versioni", 8),
        ("test_files", "FileTest", 8),
        ("total_tests", "TotTest", 7),
        ("total_commits", "Commits", 7),
        ("pw_js", "PW_JS", 5),
        ("pw_ts", "PW_TS", 5),
        ("in_rq3", "InRQ3", 5),
    ]

    header = (
        f"Repository Node.js (JS/TS, test > {args.min_tests}, releases > {args.min_releases}, "
        f"SOLO Playwright): {len(repos)} trovati ({in_rq3_count} presenti e non vuoti in RQ3)"
    )
    report = "\n".join([header, "", format_table(repos, cols)])

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text(report + "\n", encoding="utf-8")

    fieldnames = [
        "pos",
        "repository",
        "language",
        "stars",
        "releases",
        "test_files",
        "total_tests",
        "total_commits",
        "pw_js",
        "pw_ts",
        "in_rq3",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repos)

    print(report)
    print(f"\nElenco salvato in:\n- {OUT_TXT}\n- {OUT_CSV}")


if __name__ == "__main__":
    main()

