#!/usr/bin/env python3
"""
Estrae le 472 repository da E2EGit_e2e.db, le classifica per linguaggio
(raggruppando JavaScript + TypeScript in nodejs) e per framework di test E2E,
le ordina per framework, stelle, commit e numero di test, e salva un file CSV
per ogni linguaggio oltre a un CSV complessivo.
"""

import csv
import sqlite3
from collections import defaultdict
from pathlib import Path

DB_PATH = Path("/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/data/E2EGit_e2e.db")
RQ3_COMMIT_ANALYSIS = Path("/home/paolo/Scrivania/Universita/Tirocinio/data/IST2025_Zenodo/RQ3/commit-analysis")
OUT_DIR = Path("/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/results/classificazione_repo")

LANGUAGE_GROUP_MAP = {
    "JavaScript": "nodejs",
    "TypeScript": "nodejs",
    "C++": "cpp",
    "C#": "csharp",
}

QUERY = """
SELECT
    r.name AS repo,
    r.main_language AS linguaggio,
    r.stargazers AS stelle,
    r.commits AS commits,
    g.number_of_tests AS num_test,
    g.number_of_files AS num_file_test,
    (g.number_files_playwright_java + g.number_files_playwright_js + g.number_files_playwright_ts + g.number_files_playwright_py) AS f_playwright,
    (g.number_files_cypress_js + g.number_files_cypress_ts) AS f_cypress,
    (g.number_files_selenium_java + g.number_files_selenium_js + g.number_files_selenium_ts + g.number_files_selenium_py) AS f_selenium,
    (g.number_files_puppeteer_js + g.number_files_puppeteer_ts + g.number_files_puppeteer_py) AS f_puppeteer,
    (g.number_files_selenium_java + g.number_files_playwright_java) AS t_java,
    (g.number_files_selenium_js + g.number_files_playwright_js + g.number_files_puppeteer_js + g.number_files_cypress_js) AS t_js,
    (g.number_files_selenium_ts + g.number_files_playwright_ts + g.number_files_puppeteer_ts + g.number_files_cypress_ts) AS t_ts,
    (g.number_files_selenium_py + g.number_files_playwright_py + g.number_files_puppeteer_py) AS t_py
FROM repository r
JOIN gui_testing_repo_details g ON r.name = g.repository_name
"""

FIELDNAMES = [
    "repo",
    "gruppo_linguaggio",
    "linguaggio",
    "framework",
    "linguaggio_test",
    "stelle",
    "commits",
    "num_test",
    "num_file_test",
    "in_rq3",
    "url",
]


def language_slug(lang: str) -> str:
    if not lang:
        return "altro"
    if lang in LANGUAGE_GROUP_MAP:
        return LANGUAGE_GROUP_MAP[lang]
    return lang.lower().replace(" ", "_")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rq3_dirs = {p.name for p in RQ3_COMMIT_ANALYSIS.iterdir() if p.is_dir()} if RQ3_COMMIT_ANALYSIS.exists() else set()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(QUERY).fetchall()
    conn.close()

    by_group: dict[str, list[dict]] = defaultdict(list)
    all_records: list[dict] = []

    for row in rows:
        frameworks = []
        if row["f_playwright"] > 0:
            frameworks.append("Playwright")
        if row["f_cypress"] > 0:
            frameworks.append("Cypress")
        if row["f_selenium"] > 0:
            frameworks.append("Selenium")
        if row["f_puppeteer"] > 0:
            frameworks.append("Puppeteer")

        test_langs = []
        if row["t_ts"] > 0:
            test_langs.append("TS")
        if row["t_js"] > 0:
            test_langs.append("JS")
        if row["t_java"] > 0:
            test_langs.append("Java")
        if row["t_py"] > 0:
            test_langs.append("Python")

        group = language_slug(row["linguaggio"])
        repo_folder = row["repo"].replace("/", "_")

        record = {
            "repo": row["repo"],
            "gruppo_linguaggio": group,
            "linguaggio": row["linguaggio"] or "",
            "framework": "+".join(frameworks) if frameworks else "Sconosciuto",
            "linguaggio_test": "+".join(test_langs),
            "stelle": row["stelle"] or 0,
            "commits": row["commits"] or 0,
            "num_test": row["num_test"] or 0,
            "num_file_test": row["num_file_test"] or 0,
            "in_rq3": "si" if repo_folder in rq3_dirs else "no",
            "url": f"https://github.com/{row['repo']}",
        }
        by_group[group].append(record)
        all_records.append(record)

    sort_key = lambda r: (r["framework"], -r["stelle"], -r["commits"], -r["num_test"], r["repo"].lower())

    for group, records in sorted(by_group.items()):
        records.sort(key=sort_key)
        csv_path = OUT_DIR / f"{group}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(records)

    all_records.sort(key=lambda r: (r["gruppo_linguaggio"], r["framework"], -r["stelle"], -r["commits"], -r["num_test"], r["repo"].lower()))
    master_path = OUT_DIR / "tutte_le_repo.csv"
    with master_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_records)

    print(f"Generati {len(by_group)} CSV per linguaggio + tutte_le_repo.csv in {OUT_DIR}")
    for group, records in sorted(by_group.items(), key=lambda kv: -len(kv[1])):
        fw_counts: dict[str, int] = defaultdict(int)
        for r in records:
            fw_counts[r["framework"]] += 1
        fw_summary = ", ".join(f"{k}: {v}" for k, v in sorted(fw_counts.items(), key=lambda kv: -kv[1]))
        print(f"  - {group}.csv: {len(records)} repo ({fw_summary})")


if __name__ == "__main__":
    main()

