"""01_estrai_repository.py — dall'elenco nel dataset alla lista dei repository da clonare.

E2EGit non contiene i repository: contiene metadati e i percorsi dei test.
Questo script legge E2EGit.db e produce due CSV:

    data/repos_gui.csv   una riga per repository (472 attesi), con URL GitHub
    data/tests_gui.csv   una riga per file di test, con il percorso dentro il repo

Uso:
    python src/01_estrai_repository.py
    python src/01_estrai_repository.py --check-github    # verifica che i repo esistano ancora

Nota: i nomi delle colonne NON sono documentati in modo uniforme tra paper e database
(la Figura 3 del paper mostra `name`, il codice di PT-LINTR interroga `repository_name`).
Lo script introspeziona lo schema e si adatta; se non trova la colonna giusta te lo dice.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "E2EGit.db"
OUT_DIR = ROOT / "data"

# Nomi plausibili della colonna che contiene "owner/repo", in ordine di preferenza.
REPO_COL_CANDIDATES = ("repository_name", "repo_name", "name", "repository")


def fail(msg: str) -> None:
    print(f"\n[ERRORE] {msg}\n", file=sys.stderr)
    sys.exit(1)


def columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')]


def pick(cols: list[str], candidates: tuple[str, ...]) -> str | None:
    lowered = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


def dump(conn: sqlite3.Connection, sql: str, path: Path) -> int:
    cur = conn.execute(sql)
    headers = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)
    return len(rows)


def normalize_test_path(raw: str, kind: str) -> str:
    """Dal percorso del dataset al percorso relativo dentro il repository.

    Il formato cambia tra le due tabelle (verificato sul DB il 24/10/2026):

        gui : /apache_roller/it-selenium/src/test/...   -> togli 'apache_roller'
        perf: \\apache\\roller\\testing\\load.jmx          -> togli 'apache' e 'roller'

    Gli eventuali segmenti vuoti (barre iniziali o doppie) vengono ignorati.
    """
    parts = [p for p in raw.replace("\\", "/").split("/") if p]
    drop = 1 if kind == "gui" else 2
    return "/".join(parts[drop:])


def check_github(repos: list[str]) -> dict[str, bool]:
    """HEAD su github.com/<repo>: 200 = esiste e è pubblico, 404 = sparito o privato."""
    result: dict[str, bool] = {}
    for i, repo in enumerate(repos, 1):
        url = f"https://github.com/{repo}"
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "e2egit-check"})
        try:
            with urllib.request.urlopen(req, timeout=15):
                result[repo] = True
        except urllib.error.HTTPError as exc:
            result[repo] = exc.code == 200
        except Exception:
            result[repo] = False
        if i % 25 == 0:
            print(f"  verificati {i}/{len(repos)}…")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-github", action="store_true", help="verifica l'esistenza dei repository")
    args = ap.parse_args()

    if not DB_PATH.exists():
        fail(
            f"database non trovato: {DB_PATH}\n"
            "  scaricalo con:\n"
            '    curl.exe -L -C - -o data\\E2EGit.db "https://zenodo.org/records/14234731/files/E2EGit.db?download=1"'
        )

    OUT_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

    print("=" * 70)
    print(f"Database: {DB_PATH}  ({DB_PATH.stat().st_size / 1e9:.2f} GB)")
    print("=" * 70)

    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    print("\nTabelle presenti:")
    for t in tables:
        n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"  {t:<40} {n:>10,} righe")

    # --- repository con test GUI -------------------------------------------------
    table = "gui_testing_repo_details"
    if table not in tables:
        fail(f"tabella {table} assente: il file non sembra il dataset E2EGit")

    cols = columns(conn, table)
    print(f"\n[{table}] colonne ({len(cols)}):")
    for c in cols:
        print(f"  - {c}")

    repo_col = pick(cols, REPO_COL_CANDIDATES)
    if not repo_col:
        fail(
            f"non trovo la colonna con 'owner/repo' in {table}. "
            f"Colonne disponibili: {cols}. Aggiungila a REPO_COL_CANDIDATES."
        )

    n = dump(conn, f'SELECT * FROM "{table}" ORDER BY "{repo_col}"', OUT_DIR / "repos_gui.csv")
    print(f"\n-> data/repos_gui.csv ({n} repository, colonna nome: {repo_col})")

    repos = [r[0] for r in conn.execute(f'SELECT "{repo_col}" FROM "{table}" ORDER BY 1')]

    # --- file di test per repository --------------------------------------------
    ttable = "gui_testing_test_details"
    if ttable in tables:
        tcols = columns(conn, ttable)
        print(f"\n[{ttable}] colonne ({len(tcols)}):")
        for c in tcols:
            print(f"  - {c}")
        trepo = pick(tcols, REPO_COL_CANDIDATES)
        if trepo:
            rows = conn.execute(
                f'SELECT * FROM "{ttable}" ORDER BY "{trepo}", test_path'
            ).fetchall()
            cur = conn.execute(f'SELECT * FROM "{ttable}" LIMIT 1')
            headers = [d[0] for d in cur.description]
            i_path = headers.index("test_path")
            out_rows = [list(r) + [normalize_test_path(r[i_path], "gui")] for r in rows]
            with (OUT_DIR / "tests_gui.csv").open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(headers + ["test_path_rel"])
                w.writerows(out_rows)
            print(f"\n-> data/tests_gui.csv ({len(out_rows)} file di test, con test_path_rel)")

    # --- test di performance (stessa estrazione, regola di normalizzazione diversa) ---
    ptable = "performance_testing_test_details"
    if ptable in tables:
        pcols = columns(conn, ptable)
        prepo = pick(pcols, REPO_COL_CANDIDATES)
        if prepo:
            rows = conn.execute(f'SELECT * FROM "{ptable}" ORDER BY "{prepo}", test_path').fetchall()
            cur = conn.execute(f'SELECT * FROM "{ptable}" LIMIT 1')
            headers = [d[0] for d in cur.description]
            i_path = headers.index("test_path")
            out_rows = [list(r) + [normalize_test_path(r[i_path], "perf")] for r in rows]
            with (OUT_DIR / "tests_perf.csv").open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(headers + ["test_path_rel"])
                w.writerows(out_rows)
            print(f"-> data/tests_perf.csv ({len(out_rows)} ThreadGroup/TaskSet)")

    # --- URL da clonare ----------------------------------------------------------
    with (OUT_DIR / "repos_url.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["repository", "clone_url"])
        for r in repos:
            w.writerow([r, f"https://github.com/{r}"])
    print(f"-> data/repos_url.csv ({len(repos)} URL)")

    if args.check_github:
        print("\nVerifica su GitHub (potrebbe richiedere qualche minuto)…")
        res = check_github(repos)
        vivi = sum(1 for v in res.values() if v)
        with (OUT_DIR / "repos_stato.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["repository", "esiste"])
            for r in repos:
                w.writerow([r, res.get(r, False)])
        print(f"\nRepository ancora raggiungibili: {vivi}/{len(repos)}")
        print("-> data/repos_stato.csv")

    conn.close()
    print("\nFatto. Il passo successivo è il campionamento stratificato (docs/04_selezione.md).")


if __name__ == "__main__":
    main()
