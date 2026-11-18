#!/usr/bin/env python3
"""classifica_repo_rq3.py — Incrocia E2EGit_e2e.db con i dati RQ3 (IST 2025)
per individuare le repository Node.js (JS/TS) con i range di non aggiornamento
dei test E2E GUI più lunghi.

Uso:
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/classifica_repo_rq3.py
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/classifica_repo_rq3.py --top 25
"""

import argparse
import csv
import re
import sqlite3
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT if (ROOT / "data").is_dir() else ROOT.parent
DB_PATH = DATA_ROOT / "data" / "E2EGit_e2e.db"
RQ3_COMMIT_DIR = DATA_ROOT / "data" / "IST2025_Zenodo" / "RQ3" / "commit-analysis"
OUT_TXT = ROOT / "repositories" / "repo_nodejs" / "classifica_rq3_non_aggiornamento.txt"
OUT_CSV = ROOT / "repositories" / "repo_nodejs" / "classifica_rq3_non_aggiornamento.csv"

NS_MAIN = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def col_ref_to_idx(ref: str) -> int:
    letters = "".join(ch for ch in ref if ch.isalpha())
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return idx - 1


def read_xlsx_rows(path: Path) -> list[dict[str, str]]:
    """Legge il primo foglio di un file .xlsx usando solo stdlib e restituisce lista di dict."""
    with zipfile.ZipFile(path) as z:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            s_root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings = ["".join(si.itertext()) for si in s_root]

        sheets = sorted(n for n in z.namelist() if n.startswith("xl/worksheets/sheet"))
        if not sheets:
            return []
        root = ET.fromstring(z.read(sheets[0]))

        raw_rows: list[list[str]] = []
        for row_el in root.findall(".//m:row", NS_MAIN):
            cells: dict[int, str] = {}
            max_idx = -1
            for c in row_el.findall("m:c", NS_MAIN):
                ref = c.attrib.get("r", "")
                idx = col_ref_to_idx(ref) if ref else max_idx + 1
                max_idx = max(max_idx, idx)
                ctype = c.attrib.get("t")
                v = c.find("m:v", NS_MAIN)
                if ctype == "s" and v is not None and v.text is not None:
                    val = strings[int(v.text)]
                elif ctype == "inlineStr":
                    val = "".join(c.itertext())
                elif v is not None and v.text is not None:
                    val = v.text
                else:
                    val = "".join(c.itertext())
                cells[idx] = val.strip()
            if max_idx >= 0:
                raw_rows.append([cells.get(i, "") for i in range(max_idx + 1)])

    if len(raw_rows) < 2:
        return []
    headers = raw_rows[0]
    out: list[dict[str, str]] = []
    for row in raw_rows[1:]:
        if not any(row):
            continue
        out.append({headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers)) if headers[i]})
    return out


def to_int(val: str, default: int = 0) -> int:
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def extract_date_range(span_text: str) -> str:
    dates = DATE_RE.findall(span_text)
    if not dates:
        return "-"
    if len(dates) == 1:
        return dates[0]
    return f"{dates[0]} -> {dates[-1]}"


def fetch_nodejs_repos(min_tests: int, min_releases: int) -> list[dict]:
    query = """
    SELECT
        CASE
            WHEN (g.number_files_cypress_js + g.number_files_cypress_ts) > 0
             AND (g.number_files_playwright_js + g.number_files_playwright_ts) > 0 THEN 'Multi (Cypress+Playwright)'
            WHEN (g.number_files_cypress_js + g.number_files_cypress_ts) > 0 THEN 'Cypress'
            WHEN (g.number_files_playwright_js + g.number_files_playwright_ts) > 0 THEN 'Playwright'
            WHEN (g.number_files_puppeteer_js + g.number_files_puppeteer_ts) > 0 THEN 'Puppeteer'
            WHEN (g.number_files_selenium_js + g.number_files_selenium_ts) > 0 THEN 'Selenium'
            ELSE 'Altro'
        END AS framework,
        r.name AS repository,
        r.main_language AS language,
        r.stargazers AS stars,
        r.releases AS releases,
        g.number_of_files AS test_files,
        g.number_of_tests AS total_tests,
        r.commits AS total_commits
    FROM repository r
    JOIN gui_testing_repo_details g ON r.name = g.repository_name
    WHERE r.main_language IN ('JavaScript', 'TypeScript')
      AND g.number_of_tests > ?
      AND r.releases > ?
    ORDER BY r.stargazers DESC;
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(query, (min_tests, min_releases)).fetchall()]


def analyze_repo(repo_info: dict) -> dict | None:
    folder_name = repo_info["repository"].replace("/", "_")
    repo_dir = RQ3_COMMIT_DIR / folder_name
    if not repo_dir.is_dir():
        return None

    app_span_files = list(repo_dir.glob("*_app_span_analysis.xlsx"))
    lifecycle_files = list(repo_dir.glob("*_tests_lifecycle_analysis.xlsx"))

    max_span_commits = 0
    max_span_days = 0
    best_span_range = "-"
    n_app_spans = 0

    if app_span_files:
        rows = read_xlsx_rows(app_span_files[0])
        n_app_spans = len(rows)
        for row in rows:
            c = to_int(row.get("commit", "0"))
            d = to_int(row.get("days", "0"))
            if c > max_span_commits or (c == max_span_commits and d > max_span_days):
                max_span_commits = c
                max_span_days = d
                best_span_range = extract_date_range(row.get("span", ""))

    max_svac_unmod = 0
    max_svday_unmod = 0
    max_svac_per_mod = 0.0
    max_svac_any = 0
    max_svday_any = 0
    total_blobs = 0
    unmod_blobs = 0

    if lifecycle_files:
        rows = read_xlsx_rows(lifecycle_files[0])
        total_blobs = len(rows)
        for row in rows:
            svday = to_int(row.get("svday", "0"))
            svmod = to_int(row.get("svmod", "0"))
            svac = to_int(row.get("svac", "0"))
            max_svac_any = max(max_svac_any, svac)
            max_svday_any = max(max_svday_any, svday)
            if svmod > 0:
                max_svac_per_mod = max(max_svac_per_mod, svac / svmod)
            if svmod == 1:
                unmod_blobs += 1
                if svac > max_svac_unmod or (svac == max_svac_unmod and svday > max_svday_unmod):
                    max_svac_unmod = svac
                    max_svday_unmod = svday

    return {
        **repo_info,
        "n_app_spans": n_app_spans,
        "max_span_commits": max_span_commits,
        "max_span_days": max_span_days,
        "best_span_range": best_span_range,
        "total_blobs": total_blobs,
        "unmod_blobs": unmod_blobs,
        "max_svac_unmod": max_svac_unmod,
        "max_svday_unmod": max_svday_unmod,
        "max_svac_per_mod": round(max_svac_per_mod, 1),
        "max_svac_any": max_svac_any,
        "max_svday_any": max_svday_any,
    }


def format_table(rows: list[dict], columns: list[tuple[str, str, int]]) -> str:
    header = "  ".join(label.ljust(w) for _, label, w in columns)
    sep = "  ".join("-" * w for _, _, w in columns)
    lines = [header, sep]
    for r in rows:
        vals = []
        for key, _, w in columns:
            s = str(r.get(key, ""))
            if len(s) > w:
                s = s[: w - 1] + "…"
            vals.append(s.ljust(w))
        lines.append("  ".join(vals))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classifica repository Node.js in base ai range di non aggiornamento RQ3.")
    parser.add_argument("--min-tests", type=int, default=10, help="Numero minimo di test GUI (default: 10)")
    parser.add_argument("--min-releases", type=int, default=5, help="Numero minimo di release (default: 5)")
    parser.add_argument("--top", type=int, default=20, help="Numero di righe da mostrare per classifica (default: 20)")
    args = parser.parse_args()

    repos = fetch_nodejs_repos(args.min_tests, args.min_releases)
    results = []
    missing = []
    for r in repos:
        analyzed = analyze_repo(r)
        if analyzed is None:
            missing.append(r["repository"])
        else:
            results.append(analyzed)

    by_app_span = sorted(results, key=lambda x: (x["max_span_commits"], x["max_span_days"]), reverse=True)
    by_unmod_test = sorted(results, key=lambda x: (x["max_svac_unmod"], x["max_svac_per_mod"], x["max_svday_unmod"]), reverse=True)

    cols_span = [
        ("framework", "Framework", 12),
        ("repository", "Repository", 36),
        ("releases", "Rel", 5),
        ("total_tests", "Test", 5),
        ("max_span_commits", "MaxAppSpanC", 11),
        ("max_span_days", "MaxAppSpanD", 11),
        ("best_span_range", "Range Date Span Max", 24),
    ]
    cols_test = [
        ("framework", "Framework", 12),
        ("repository", "Repository", 36),
        ("unmod_blobs", "Blob1", 5),
        ("total_blobs", "BlobTot", 7),
        ("max_svac_unmod", "MaxSvac(m=1)", 12),
        ("max_svday_unmod", "MaxDay(m=1)", 11),
        ("max_svac_per_mod", "MaxSvac/Mod", 11),
        ("max_span_commits", "MaxAppSpanC", 11),
    ]

    report_parts = [
        f"Repository Node.js (JS/TS, test > {args.min_tests}, releases > {args.min_releases}): {len(repos)} trovate in DB, {len(results)} presenti in RQ3 ({len(missing)} assenti)",
        "",
        f"=== CLASSIFICA A: Range più lungo senza modifiche ai test GUI (da *_app_span_analysis.xlsx) [Top {args.top}] ===",
        format_table(by_app_span[: args.top], cols_span),
        "",
        f"=== CLASSIFICA B: Singoli file di test più longevi senza modifiche (da *_tests_lifecycle_analysis.xlsx) [Top {args.top}] ===",
        format_table(by_unmod_test[: args.top], cols_test),
    ]
    report = "\n".join(report_parts)
    print(report)

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text(report + "\n", encoding="utf-8")

    if results:
        fieldnames = list(results[0].keys())
        with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(by_app_span)

    print(f"\nReport salvato in:\n- {OUT_TXT}\n- {OUT_CSV}")


if __name__ == "__main__":
    main()

