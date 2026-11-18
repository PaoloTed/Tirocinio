#!/usr/bin/env python3
"""calcola_intervalli_playwright.py — Calcola per tutte le repository in
`repositories/repo_nodejs/playwright/repository_nodejs_playwright.txt`
l'intervallo (e gli eventuali ulteriori intervalli disgiunti) in cui almeno
una soglia (default 70%) dei file di test Playwright attivi non viene modificata.

Pulizia applicata ai file `*_only_gui.xlsx/.csv` di RQ3:
- Esclusione della riga spuria `df.iloc[0:1]` introdotta da `commitAnalyzer.py`
  quando non corrisponde a un file di test reale presente in `E2EGit_e2e.db`.
- Per le repository multi-framework (Playwright + Cypress/Puppeteer), filtro sui
  soli file Playwright censiti in `gui_testing_test_details`.
- Fusione cronologica delle righe duplicate sullo stesso filepath (es. `badge.spec.ts`
  in `microsoft/fluentui`, eliminato nel 2021 e ricreato nel 2024).

Uso:
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/calcola_intervalli_playwright.py
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/calcola_intervalli_playwright.py --threshold 0.70 --max-intervals 5
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/calcola_intervalli_playwright.py --repo microsoft/fluentui
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sqlite3
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classifica_b_rq3 import _load_only_gui_csv, _load_only_gui_xlsx  # noqa: E402
from classifica_repo_rq3 import DB_PATH, ROOT, RQ3_COMMIT_DIR  # noqa: E402

PLAYWRIGHT_DIR = ROOT / "repositories" / "repo_nodejs" / "playwright"
INPUT_LIST_TXT = PLAYWRIGHT_DIR / "repository_nodejs_playwright.txt"
OUT_TXT = PLAYWRIGHT_DIR / "intervalli_playwright_70.txt"
OUT_CSV = PLAYWRIGHT_DIR / "intervalli_playwright_70.csv"

REPO_LINE_RE = re.compile(
    r"^\s*(\d+)\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\s+"
    r"(TypeScript|JavaScript)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+"
)
DATETIME_RE = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
TEST_EXT_HINTS = (
    ".spec.ts",
    ".spec.js",
    ".test.ts",
    ".test.js",
    ".e2e.ts",
    ".e2e.js",
    ".e2e-spec.ts",
    ".e2e-spec.js",
)


@dataclass
class RepoEntry:
    group: str
    pos: int
    slug: str
    language: str
    stars: int
    releases: int
    db_commits: int
    db_files: int
    db_tests: int


def parse_playwright_list(path: Path) -> list[RepoEntry]:
    """Estrae le repository ordinate da `repository_nodejs_playwright.txt`."""
    entries: list[RepoEntry] = []
    current_group = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("--- Framework:"):
            current_group = line.split(":", 1)[1].split("(", 1)[0].strip()
            continue
        m = REPO_LINE_RE.match(line)
        if m:
            entries.append(
                RepoEntry(
                    group=current_group,
                    pos=int(m.group(1)),
                    slug=m.group(2),
                    language=m.group(3),
                    stars=int(m.group(4)),
                    releases=int(m.group(5)),
                    db_commits=int(m.group(6)),
                    db_files=int(m.group(7)),
                    db_tests=int(m.group(8)),
                )
            )
    return entries


def parse_commit_dt(hdr_str: str) -> datetime | None:
    m = DATETIME_RE.search(hdr_str)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")


def format_date(hdr_str: str) -> str:
    dt = parse_commit_dt(hdr_str)
    return dt.strftime("%Y-%m-%d") if dt else "-"


def load_db_paths(conn: sqlite3.Connection, slug: str) -> tuple[set[str], set[str]]:
    """Restituisce (tutti_path_gui, path_playwright) normalizzati dal DB E2EGit."""
    prefix = f"/{slug.replace('/', '_')}/"
    all_db: set[str] = set()
    pw_db: set[str] = set()
    rows = conn.execute(
        """SELECT test_path, is_playwright_js, is_playwright_ts, is_playwright_py
           FROM gui_testing_test_details
           WHERE lower(repository_name) = lower(?)""",
        (slug,),
    ).fetchall()
    for tp, pw_js, pw_ts, pw_py in rows:
        rel = tp[len(prefix) :] if tp.startswith(prefix) else tp.lstrip("/").split("/", 1)[-1]
        all_db.add(rel)
        if pw_js or pw_ts or pw_py:
            pw_db.add(rel)
    return all_db, pw_db


def load_clean_playwright_history(
    conn: sqlite3.Connection,
    entry: RepoEntry,
) -> tuple[dict[int, str], int, dict[str, list[tuple[int, str]]], int, str]:
    """Carica e pulisce la storia commit dai file `*_only_gui` di RQ3."""
    all_db, pw_db = load_db_paths(conn, entry.slug)
    rq3_dir = RQ3_COMMIT_DIR / entry.slug.replace("/", "_")
    if not rq3_dir.is_dir():
        return {}, 0, {}, len(pw_db), "cartella RQ3 assente"

    files = sorted(rq3_dir.glob("*_only_gui.xlsx")) or sorted(rq3_dir.glob("*_only_gui.csv"))
    if not files:
        return {}, 0, {}, len(pw_db), "file *_only_gui assente in RQ3"

    src = files[0]
    hdr, rows = _load_only_gui_csv(src) if src.suffix == ".csv" else _load_only_gui_xlsx(src)
    commit_cols = sorted(k for k in hdr if k >= 1)
    if not commit_cols:
        return hdr, 0, {}, len(pw_db), "nessuna colonna commit in *_only_gui"
    max_c = commit_cols[-1]

    if not rows:
        return hdr, max_c, {}, len(pw_db), "0 righe in *_only_gui RQ3"

    is_multi = entry.group != "Playwright"
    by_path: dict[str, list[tuple[int, str]]] = {}
    dropped_row0 = False

    for idx, row in enumerate(rows):
        path = row.get(0, "").strip()
        if not path:
            continue
        if is_multi:
            if path not in pw_db:
                continue
        else:
            # commitAnalyzer.py copia sempre df.iloc[0:1] come prima riga: la scartiamo
            # se non e' nel DB (a meno che non sia l'unica riga e sembri un file di test).
            if idx == 0 and path not in all_db:
                looks_test = path.lower().endswith(TEST_EXT_HINTS)
                if len(rows) > 1 or not looks_test:
                    dropped_row0 = True
                    continue

        events = [(c, row[c]) for c in sorted(row) if isinstance(c, int) and c >= 1]
        if events:
            by_path.setdefault(path, []).extend(events)

    for path in by_path:
        by_path[path].sort(key=lambda x: x[0])

    notes: list[str] = []
    if not by_path:
        notes.append("nessun file di test valido in *_only_gui RQ3")
    else:
        if is_multi:
            notes.append(f"filtrati soli {len(by_path)}/{len(pw_db)} file Playwright DB")
        elif len(by_path) < len(pw_db):
            notes.append(f"tracciati {len(by_path)}/{len(pw_db)} file Playwright in RQ3")
        if dropped_row0 and len(rows) == 1:
            notes.append("unica riga spuria scartata")

    return hdr, max_c, by_path, len(pw_db), "; ".join(notes)


def build_active_spans(events: list[tuple[int, str]]) -> list[tuple[int, int | None]]:
    """Ricostruisce gli intervalli [start, end_delete) di esistenza attiva di un file."""
    spans: list[tuple[int, int | None]] = []
    cur_start: int | None = None
    for c, val in events:
        if val == "D":
            if cur_start is None:
                cur_start = 1
            spans.append((cur_start, c))
            cur_start = None
        else:
            if cur_start is None:
                cur_start = c if val == "A" else (1 if c == 1 else c)
    if cur_start is not None:
        spans.append((cur_start, None))
    return spans


def compute_disjoint_intervals(
    hdr: dict[int, str],
    max_c: int,
    tests: dict[str, list[tuple[int, str]]],
    threshold: float,
    min_suite_frac: float,
    min_secondary_commits: int,
    max_intervals: int,
) -> tuple[list[dict], int]:
    """Trova gli intervalli disgiunti più lunghi con >= `threshold` test non modificati."""
    if not tests or max_c < 2:
        return [], 0

    active_spans: dict[str, list[tuple[int, int | None]]] = {}
    test_event_commits: dict[str, set[int]] = {}
    all_event_commits: set[int] = set()

    for path, events in tests.items():
        cs = {c for c, _ in events}
        test_event_commits[path] = cs
        all_event_commits.update(cs)
        active_spans[path] = build_active_spans(events)

    def active_at(commit_idx: int) -> list[str]:
        return [
            p
            for p, spans in active_spans.items()
            if any(s <= commit_idx and (e is None or commit_idx < e) for s, e in spans)
        ]

    candidate_starts = sorted(all_event_commits | {1, max_c})
    peak_n = max((len(active_at(c)) for c in candidate_starts), default=0)
    min_active = max(1, math.ceil(min_suite_frac * peak_n))

    events_sorted = sorted(all_event_commits)
    maximal: list[dict] = []

    for a in candidate_starts:
        if a >= max_c:
            continue
        act = active_at(a)
        n_act = len(act)
        if n_act < min_active:
            continue

        touched: set[str] = set()
        break_c: int | None = None
        for e in events_sorted:
            if e <= a:
                continue
            newly = [p for p in act if e in test_event_commits[p]]
            if newly:
                cand_touched = touched | set(newly)
                if (n_act - len(cand_touched)) / n_act < threshold - 1e-12:
                    break_c = e
                    break
                touched = cand_touched

        b = (break_c - 1) if break_c is not None else max_c
        if b <= a:
            continue

        stable_cnt = n_act - len(touched)
        pct = (stable_cnt / n_act) * 100.0
        dt_a = parse_commit_dt(hdr.get(a, ""))
        dt_b = parse_commit_dt(hdr.get(b, ""))
        days = max(0, (dt_b - dt_a).days) if dt_a and dt_b else 0

        maximal.append(
            {
                "commit_a": a,
                "date_a": format_date(hdr.get(a, "")),
                "commit_b": b,
                "date_b": format_date(hdr.get(b, "")),
                "durata_commit": b - a,
                "durata_giorni": days,
                "test_stabili": stable_cnt,
                "test_attivi": n_act,
                "picco_test_pw": peak_n,
                "pct_stabili": round(pct, 1),
                "fine_motivo": f"rottura_soglia@C{break_c}" if break_c is not None else "fine_storia_rq3",
            }
        )

    # Selezione greedy di intervalli strettamente disgiunti, ordinati per lunghezza
    maximal.sort(
        key=lambda x: (x["durata_commit"], x["pct_stabili"], x["test_attivi"], x["commit_b"]),
        reverse=True,
    )
    chosen: list[dict] = []
    for cand in maximal:
        if any(not (cand["commit_b"] < ch["commit_a"] or cand["commit_a"] > ch["commit_b"]) for ch in chosen):
            continue
        if chosen and cand["durata_commit"] < min_secondary_commits:
            continue
        chosen.append(cand)
        if len(chosen) >= max_intervals:
            break

    return chosen, peak_n


def build_reports(
    entries: list[RepoEntry],
    threshold: float,
    min_suite_frac: float,
    min_secondary_commits: int,
    max_intervals: int,
) -> tuple[str, list[dict]]:
    """Elabora tutte le repository e costruisce report testuale + righe CSV."""
    records: list[dict] = []
    with sqlite3.connect(DB_PATH) as conn:
        for entry in entries:
            hdr, max_c, tests, pw_db_cnt, note = load_clean_playwright_history(conn, entry)
            intervals, peak_n = compute_disjoint_intervals(
                hdr=hdr,
                max_c=max_c,
                tests=tests,
                threshold=threshold,
                min_suite_frac=min_suite_frac,
                min_secondary_commits=min_secondary_commits,
                max_intervals=max_intervals,
            )
            records.append(
                {
                    "entry": entry,
                    "max_c": max_c,
                    "n_files": len(tests),
                    "pw_db_cnt": pw_db_cnt,
                    "peak_n": peak_n,
                    "intervals": intervals,
                    "note": note,
                }
            )

    valid_recs = [r for r in records if r["intervals"]]
    top1_lens = [r["intervals"][0]["durata_commit"] for r in valid_recs]
    total_ivs = sum(len(r["intervals"]) for r in records)
    pct_label = int(round(threshold * 100))
    suite_pct_label = int(round(min_suite_frac * 100))

    lines: list[str] = [
        "=" * 110,
        f"INTERVALLI CON >= {pct_label}% DEI TEST PLAYWRIGHT NON MODIFICATI (Dataset E2EGit / RQ3 IST2025)",
        "=" * 110,
        f"Fonte elenco           : {INPUT_LIST_TXT.relative_to(ROOT)}",
        f"Fonte storia commit    : {RQ3_COMMIT_DIR.relative_to(ROOT if RQ3_COMMIT_DIR.is_relative_to(ROOT) else ROOT.parent)}/*_only_gui.{{xlsx,csv}}",
        f"Repository totali      : {len(records)} (valide con >=1 intervallo: {len(valid_recs)}, senza dati validi: {len(records) - len(valid_recs)})",
        f"Intervalli individuati : {total_ivs} (massimo {max_intervals} intervalli disgiunti per repo; soglia secondari >= {min_secondary_commits} commit)",
    ]
    if top1_lens:
        lines.append(
            f"Durata intervallo #1   : mediana = {int(statistics.median(top1_lens))} commit | "
            f"media = {statistics.mean(top1_lens):.1f} commit | "
            f"min = {min(top1_lens)} | max = {max(top1_lens)}"
        )
    lines.extend(
        [
            "",
            "Metodologia e pulizia applicata:",
            f"- Per ogni intervallo [Ca, Cb], all'inizio Ca devono essere attivi almeno il {suite_pct_label}% del picco attivo di file Playwright della repo.",
            f"- Da Ca+1 a Cb almeno il {pct_label}% di quei file attivi non subisce alcuna modifica/rename/cancellazione.",
            "- Pulizia automatica RQ3: rimossa la riga spuria `df.iloc[0:1]` di commitAnalyzer.py se non e' un test reale;",
            "  in eventuali repo multi-framework sono mantenuti solo i file Playwright censiti in E2EGit_e2e.db;",
            "  i file cancellati e ricreati con lo stesso path (es. `badge.spec.ts` in `fluentui`) sono fusi cronologicamente.",
            "- Nota sugli indici: `Commit <n>` / `C<n>` sono gli indici dei commit non-merge nell'archivio RQ3 (colonne di `*_only_gui`), non gli SHA Git.",
            "",
            "Legenda dei campi:",
            "- Intestazione repo:",
            "  * [<Framework> #<Pos>] : gruppo framework (es. `Playwright`) e posizione per stelle in `repository_nodejs_playwright.txt`.",
            "  * Stelle               : numero di stelle GitHub nello snapshot E2EGit.",
            "  * Commit RQ3           : numero totale di commit non-merge analizzati nei dati RQ3 per la repository.",
            "  * File PW tracciati    : file di test Playwright distinti presenti nei dati puliti di RQ3 lungo l'intera storia.",
            "  * DB                   : file di test Playwright censiti nello snapshot finale del database E2EGit (`gui_testing_test_details`).",
            "  * picco attivo         : numero massimo di file Playwright vivi contemporaneamente in uno stesso commit (creati e non cancellati).",
            "  * Nota                 : eventuali differenze rispetto al DB (es. repo multi-framework o copertura parziale in RQ3).",
            "- Righe intervallo:",
            "  * Intervallo #<k>      : rango dell'intervallo disgiunto ordinato per durata in commit (`#1` e' il piu' lungo).",
            "  * Commit Ca -> Cb      : commit iniziale (`t_0`) e finale dell'intervallo con le rispettive date (YYYY-MM-DD).",
            "  * durata               : ampiezza dell'intervallo in commit (`Cb - Ca`) e in giorni di calendario.",
            f"  * stabili: X/Y (Z%)    : su Y file Playwright attivi a Ca, X file ({pct_label}%+) non sono mai stati toccati tra Ca+1 e Cb (non e' l'esito pass/fail).",
            "  * fine                 : `rottura_soglia@C<k>` se al commit C<k> i file non toccati scendono sotto soglia; `fine_storia_rq3` se arriva a fine dataset.",
            "",
        ]
    )

    lines.extend(["=" * 110, "DETTAGLIO COMPLETO INTERVALLI DISGIUNTI PER SINGOLA REPOSITORY", "=" * 110])
    csv_rows: list[dict] = []

    for rec in records:
        e = rec["entry"]
        header_line = (
            f"\n[{e.group} #{e.pos}] {e.slug} | Stelle: {e.stars} | Commit RQ3: {rec['max_c']} | "
            f"File PW tracciati: {rec['n_files']} (DB: {rec['pw_db_cnt']}, picco attivo: {rec['peak_n']})"
        )
        if rec["note"]:
            header_line += f" | Nota: {rec['note']}"
        lines.append(header_line)

        if not rec["intervals"]:
            lines.append("  -> Nessun intervallo calcolabile dai dati *_only_gui disponibili.")
            csv_rows.append(
                {
                    "framework_group": e.group,
                    "pos": e.pos,
                    "repository": e.slug,
                    "stars": e.stars,
                    "rank_interval": 0,
                    "commit_inizio": "",
                    "data_inizio": "",
                    "commit_fine": "",
                    "data_fine": "",
                    "durata_commit": "",
                    "durata_giorni": "",
                    "test_stabili": "",
                    "test_attivi": "",
                    "picco_test_pw": rec["peak_n"],
                    "pct_stabili": "",
                    "fine_motivo": "",
                    "tot_commit_rq3": rec["max_c"],
                    "file_pw_tracciati": rec["n_files"],
                    "file_pw_db": rec["pw_db_cnt"],
                    "note": rec["note"],
                }
            )
            continue

        for rk, iv in enumerate(rec["intervals"], start=1):
            lines.append(
                f"  - Intervallo #{rk}: Commit {iv['commit_a']} ({iv['date_a']}) -> Commit {iv['commit_b']} ({iv['date_b']}) | "
                f"durata: {iv['durata_commit']} commit ({iv['durata_giorni']} giorni) | "
                f"stabili: {iv['test_stabili']}/{iv['test_attivi']} ({iv['pct_stabili']:.1f}%) | "
                f"fine: {iv['fine_motivo']}"
            )
            csv_rows.append(
                {
                    "framework_group": e.group,
                    "pos": e.pos,
                    "repository": e.slug,
                    "stars": e.stars,
                    "rank_interval": rk,
                    "commit_inizio": iv["commit_a"],
                    "data_inizio": iv["date_a"],
                    "commit_fine": iv["commit_b"],
                    "data_fine": iv["date_b"],
                    "durata_commit": iv["durata_commit"],
                    "durata_giorni": iv["durata_giorni"],
                    "test_stabili": iv["test_stabili"],
                    "test_attivi": iv["test_attivi"],
                    "picco_test_pw": iv["picco_test_pw"],
                    "pct_stabili": iv["pct_stabili"],
                    "fine_motivo": iv["fine_motivo"],
                    "tot_commit_rq3": rec["max_c"],
                    "file_pw_tracciati": rec["n_files"],
                    "file_pw_db": rec["pw_db_cnt"],
                    "note": rec["note"],
                }
            )

    return "\n".join(lines) + "\n", csv_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calcola gli intervalli di commit con >= 70% di test Playwright non modificati."
    )
    parser.add_argument("--threshold", type=float, default=0.70, help="Soglia minima di test invariati (default: 0.70)")
    parser.add_argument(
        "--min-suite-frac",
        type=float,
        default=0.50,
        help="Quota minima di suite Playwright già attiva a inizio intervallo rispetto al picco (default: 0.50)",
    )
    parser.add_argument(
        "--min-commits",
        type=int,
        default=15,
        help="Lunghezza minima in commit per includere intervalli disgiunti secondari (#2+) (default: 15)",
    )
    parser.add_argument("--max-intervals", type=int, default=5, help="Numero massimo di intervalli disgiunti per repo (default: 5)")
    parser.add_argument("--repo", help="Esegue e stampa solo per una repository specifica (es. microsoft/fluentui)")
    args = parser.parse_args()

    entries = parse_playwright_list(INPUT_LIST_TXT)
    if args.repo:
        entries = [e for e in entries if e.slug.lower() == args.repo.lower()]
        if not entries:
            raise SystemExit(f"Repository '{args.repo}' non trovata in {INPUT_LIST_TXT}")

    report_txt, csv_rows = build_reports(
        entries=entries,
        threshold=args.threshold,
        min_suite_frac=args.min_suite_frac,
        min_secondary_commits=args.min_commits,
        max_intervals=args.max_intervals,
    )

    if args.repo:
        print(report_txt)
        return

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text(report_txt, encoding="utf-8")

    fieldnames = list(csv_rows[0].keys()) if csv_rows else []
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Elaborate {len(entries)} repository.")
    print(f"Report salvati in:\n- {OUT_TXT}\n- {OUT_CSV}")


if __name__ == "__main__":
    main()
