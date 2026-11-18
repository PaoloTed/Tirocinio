#!/usr/bin/env python3
"""classifica_b_rq3.py — Genera la sola Classifica B completa (singoli file di test
più longevi senza modifiche in RQ3) per tutte le repository Node.js filtrate.

Uso:
    python3 02-E2EGit-TestE2E/scripts/classifica_b_rq3.py
    python3 02-E2EGit-TestE2E/scripts/classifica_b_rq3.py --sort-by days
    python3 02-E2EGit-TestE2E/scripts/classifica_b_rq3.py --sort-by ratio --top 30
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classifica_repo_rq3 import (  # noqa: E402
    NS_MAIN,
    ROOT,
    RQ3_COMMIT_DIR,
    analyze_repo,
    col_ref_to_idx,
    fetch_nodejs_repos,
    format_table,
    read_xlsx_rows,
    to_int,
)

OUT_TXT = ROOT / "repositories" / "repo_nodejs" / "classifica_b_rq3.txt"
OUT_CSV = ROOT / "repositories" / "repo_nodejs" / "classifica_b_rq3.csv"

DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2})?")

NS_URI = NS_MAIN["m"]
TAG_ROW = f"{{{NS_URI}}}row"
TAG_SI = f"{{{NS_URI}}}si"
TAG_V = f"{{{NS_URI}}}v"

SORT_MODES = {
    "svac": (
        "MaxSvac(m=1)",
        lambda x: (x["max_svac_unmod"], x["max_svac_per_mod"], x["max_svday_unmod"]),
    ),
    "days": (
        "MaxDay(m=1)",
        lambda x: (x["max_svday_unmod"], x["max_svac_unmod"], x["max_svac_per_mod"]),
    ),
    "ratio": (
        "MaxSvac/Mod",
        lambda x: (x["max_svac_per_mod"], x["max_svac_unmod"], x["max_svday_unmod"]),
    ),
}

CSV_FIELDS = [
    "pos",
    "framework",
    "repository",
    "language",
    "stars",
    "releases",
    "test_files",
    "total_tests",
    "total_commits",
    "unmod_blobs",
    "total_blobs",
    "max_svac_unmod",
    "max_svday_unmod",
    "max_svac_per_mod",
    "max_svac_any",
    "max_svday_any",
    "max_span_commits",
    "max_span_days",
    "best_span_range",
    "best_unmod_test",
    "best_unmod_date_range",
    "best_ratio_test",
    "best_ratio_date_range",
]


def _cell_text(cell: ET.Element, strings: list[str]) -> str:
    ctype = cell.attrib.get("t")
    if ctype == "s":
        v = cell.find(TAG_V)
        return strings[int(v.text)].strip() if v is not None and v.text is not None else ""
    if ctype == "inlineStr":
        return "".join(cell.itertext()).strip()
    v = cell.find(TAG_V)
    if v is not None and v.text is not None:
        return v.text.strip()
    return "".join(cell.itertext()).strip()


def _load_only_gui_xlsx(path: Path) -> tuple[dict[int, str], list[dict[int, str]]]:
    """Legge velocemente *_only_gui.xlsx saltando le celle vuote."""
    with zipfile.ZipFile(path) as z:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            with z.open("xl/sharedStrings.xml") as sf:
                strings = [
                    "".join(si.itertext())
                    for _, si in ET.iterparse(sf, events=("end",))
                    if si.tag == TAG_SI
                ]
        sheets = sorted(n for n in z.namelist() if n.startswith("xl/worksheets/sheet"))
        if not sheets:
            return {}, []

        hdr: dict[int, str] | None = None
        rows: list[dict[int, str]] = []
        with z.open(sheets[0]) as xf:
            for _, elem in ET.iterparse(xf, events=("end",)):
                if elem.tag != TAG_ROW:
                    continue
                cells: dict[int, str] = {}
                max_idx = -1
                for cell in elem:
                    ref = cell.attrib.get("r", "")
                    if ref:
                        if not len(cell):
                            continue
                        idx = col_ref_to_idx(ref)
                    else:
                        idx = max_idx + 1
                    if idx > max_idx:
                        max_idx = idx
                    if not len(cell):
                        continue
                    val = _cell_text(cell, strings)
                    if val:
                        cells[idx] = val
                elem.clear()
                if hdr is None:
                    hdr = cells
                elif cells:
                    rows.append(cells)
    return (hdr or {}), rows


def _load_only_gui_csv(path: Path) -> tuple[dict[int, str], list[dict[int, str]]]:
    """Legge *_only_gui.csv nello stesso formato sparso usato per gli .xlsx."""
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        hdr_row = next(reader, [])
        if not hdr_row:
            return {}, []
        hdr = {i: v.strip() for i, v in enumerate(hdr_row) if v.strip()}
        rows = [{i: v.strip() for i, v in enumerate(row) if v.strip()} for row in reader if row]
    return hdr, rows


def _format_datetime_range(start_col: str, end_col: str) -> str:
    start_m = DATETIME_RE.search(start_col)
    end_m = DATETIME_RE.search(end_col)
    if not start_m and not end_m:
        return "-"
    if start_m and end_m:
        return f"{start_m.group(0)} -> {end_m.group(0)}"
    return (start_m or end_m).group(0)


def _extract_only_gui_blobs(repo_dir: Path) -> list[tuple[str, int, str]]:
    """Ricostruisce (testpath_blob, svmod, datetime_range) replicando la logica di CommitAnalyzer."""
    xlsx_files = list(repo_dir.glob("*_only_gui.xlsx"))
    csv_files = list(repo_dir.glob("*_only_gui.csv"))
    if xlsx_files:
        hdr, rows = _load_only_gui_xlsx(xlsx_files[0])
    elif csv_files:
        hdr, rows = _load_only_gui_csv(csv_files[0])
    else:
        return []

    commit_cols = [i for i in hdr if i >= 1]
    if not commit_cols:
        return []
    last_commit_col = hdr[max(commit_cols)]

    blobs: list[tuple[str, int, str]] = []

    def append_blob(filepath: str, blob_idx: int, mod: int, commits: list[str]) -> None:
        blobs.append((f"{filepath}_({blob_idx})", mod, _format_datetime_range(commits[0], commits[-1])))

    for cells in rows:
        filepath = cells.get(0, "")
        if not filepath:
            continue
        blob_idx = 0
        cur_commits: list[str] = []
        for col_idx in sorted(k for k in cells if k >= 1):
            val = cells[col_idx]
            col_str = hdr.get(col_idx, "")
            if val == "A" or val.startswith("R"):
                cur_commits.append(col_str)
            elif val == "D":
                mod = len(cur_commits)
                cur_commits.append(col_str)
                append_blob(filepath, blob_idx, mod, cur_commits)
                cur_commits = []
                blob_idx += 1
            elif val.startswith("M"):
                num = int(val[val.index("(") + 1 : val.index(")")])
                if num < 44:
                    cur_commits.append(col_str)
                else:
                    mod = len(cur_commits)
                    cur_commits.append(col_str)
                    append_blob(filepath, blob_idx, mod, cur_commits)
                    cur_commits = [col_str]
                    blob_idx += 1
        if cur_commits:
            mod = len(cur_commits)
            cur_commits.append(last_commit_col)
            append_blob(filepath, blob_idx, mod, cur_commits)
    return blobs


def _find_blob_date_range(
    og_blobs: list[tuple[str, int, str]], idx: int, testpath: str, svmod: int
) -> str:
    if 0 <= idx < len(og_blobs) and og_blobs[idx][0] == testpath and og_blobs[idx][1] == svmod:
        return og_blobs[idx][2]
    for b_name, b_mod, date_range in og_blobs:
        if b_name == testpath and b_mod == svmod:
            return date_range
    return "-"


def extract_best_lifecycle_details(repository: str) -> dict[str, str]:
    """Estrae file vincente e range date commit per m=1 e MaxSvac/Mod dai file RQ3."""
    repo_dir = RQ3_COMMIT_DIR / repository.replace("/", "_")
    lifecycle_files = list(repo_dir.glob("*_tests_lifecycle_analysis.xlsx"))
    if not lifecycle_files:
        return {
            "best_unmod_test": "-",
            "best_unmod_date_range": "-",
            "best_ratio_test": "-",
            "best_ratio_date_range": "-",
        }

    best_unmod: tuple[tuple[int, int], int, str, int] | None = None
    best_ratio: tuple[tuple[float, int, int], int, str, int] | None = None

    for idx, row in enumerate(read_xlsx_rows(lifecycle_files[0])):
        testpath = row.get("testpath(blob)", "") or "-"
        svday = to_int(row.get("svday", "0"))
        svmod = to_int(row.get("svmod", "0"))
        svac = to_int(row.get("svac", "0"))
        if svmod > 0:
            ratio_key = (svac / svmod, svac, svday)
            if best_ratio is None or ratio_key > best_ratio[0]:
                best_ratio = (ratio_key, idx, testpath, svmod)
        if svmod == 1:
            unmod_key = (svac, svday)
            if best_unmod is None or unmod_key > best_unmod[0]:
                best_unmod = (unmod_key, idx, testpath, svmod)

    og_blobs = _extract_only_gui_blobs(repo_dir)
    return {
        "best_unmod_test": best_unmod[2] if best_unmod is not None else "-",
        "best_unmod_date_range": (
            _find_blob_date_range(og_blobs, best_unmod[1], best_unmod[2], best_unmod[3])
            if best_unmod is not None
            else "-"
        ),
        "best_ratio_test": best_ratio[2] if best_ratio is not None else "-",
        "best_ratio_date_range": (
            _find_blob_date_range(og_blobs, best_ratio[1], best_ratio[2], best_ratio[3])
            if best_ratio is not None
            else "-"
        ),
    }


def build_classifica_b(min_tests: int, min_releases: int, sort_by: str) -> tuple[list[dict], int, int]:
    """Estrae le repository filtrate e restituisce la classifica B ordinata e numerata."""
    repos = fetch_nodejs_repos(min_tests, min_releases)
    results = []
    for r in repos:
        analyzed = analyze_repo(r)
        if analyzed is None:
            continue
        analyzed.update(extract_best_lifecycle_details(r["repository"]))
        results.append(analyzed)
    _, key_fn = SORT_MODES[sort_by]
    ranked = sorted(results, key=key_fn, reverse=True)
    for idx, row in enumerate(ranked, start=1):
        row["pos"] = idx
    return ranked, len(repos), len(repos) - len(results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera la sola Classifica B completa per tutte le repository Node.js (RQ3)."
    )
    parser.add_argument("--min-tests", type=int, default=10, help="Numero minimo di test GUI (default: 10)")
    parser.add_argument("--min-releases", type=int, default=5, help="Numero minimo di release (default: 5)")
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Numero di righe da mostrare/salvare (0 = tutte, default: 0)",
    )
    parser.add_argument(
        "--sort-by",
        choices=tuple(SORT_MODES),
        default="svac",
        help="Criterio principale di ordinamento (default: svac)",
    )
    args = parser.parse_args()

    ranked, total_db, missing_count = build_classifica_b(args.min_tests, args.min_releases, args.sort_by)
    displayed = ranked[: args.top] if args.top > 0 else ranked

    if args.sort_by == "ratio":
        date_key, date_label = "best_ratio_date_range", "RangeDataOra(Ratio)"
        file_key, file_label = "best_ratio_test", "FileTest(MaxSvac/Mod)"
    else:
        date_key, date_label = "best_unmod_date_range", "RangeDataOra(m=1)"
        file_key, file_label = "best_unmod_test", "FileTest(m=1)"

    def col_w(key: str, label: str) -> int:
        return max(len(label), max((len(str(r[key])) for r in displayed), default=0))

    cols = [
        ("pos", "Pos", 3),
        ("framework", "Framework", col_w("framework", "Framework")),
        ("repository", "Repository", col_w("repository", "Repository")),
        ("unmod_blobs", "Blob1", 5),
        ("total_blobs", "BlobTot", 7),
        ("max_svac_unmod", "MaxSvac(m=1)", 12),
        ("max_svday_unmod", "MaxDay(m=1)", 11),
        ("max_svac_per_mod", "MaxSvac/Mod", 11),
        ("max_span_commits", "MaxAppSpanC", 11),
        (date_key, date_label, col_w(date_key, date_label)),
        (file_key, file_label, col_w(file_key, file_label)),
    ]

    sort_label, _ = SORT_MODES[args.sort_by]
    scope_label = f"Top {len(displayed)}" if args.top > 0 else f"Tutte ({len(displayed)})"
    header = (
        f"Repository Node.js (JS/TS, test > {args.min_tests}, releases > {args.min_releases}): "
        f"{total_db} trovate in DB, {len(ranked)} presenti in RQ3 ({missing_count} assenti)"
    )
    title = (
        f"=== CLASSIFICA B: Singoli file di test più longevi senza modifiche "
        f"(ordinata per {sort_label}) [{scope_label}] ==="
    )
    report = "\n".join([header, "", title, format_table(displayed, cols)])

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text(report + "\n", encoding="utf-8")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(displayed)

    print(report)
    print(f"\nReport salvato in:\n- {OUT_TXT}\n- {OUT_CSV}")


if __name__ == "__main__":
    main()
