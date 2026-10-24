"""02_storia_test.py — i test sono cambiati dal commit del dataset a oggi?

Risponde alle domande 1-3 di Guida §6.2, su tutti (o su N) repository con test GUI:

  1. il file di test esiste ancora al percorso indicato?
  2. quante volte è stato toccato dal commit dello snapshot a HEAD?
  3. cosa è cambiato (righe aggiunte, rimosse; diff classificato)?

NON esegue i test e NON richiede Docker: usa solo Git.
Il clone usa --filter=blob:none, così scarica la storia senza i blob: su 472 repository
è la differenza tra decine di GB e pochi GB.

Uso:
    python src/02_storia_test.py --limit 5          # prova su 5 repository
    python src/02_storia_test.py                    # tutti i 472
    python src/02_storia_test.py --workers 4        # 4 cloni in parallelo
    python src/02_storia_test.py --keep-clones      # non cancella i cloni a fine lavoro

Output:
    results/storia_test.csv          una riga per file di test
    results/storia_riepilogo.csv     una riga per repository

Dipendenze: solo Git e la libreria standard.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
CLONES = DATA / "clones"

REPO_CSV = DATA / "repos_commit.csv"
TESTS_CSV = DATA / "tests_gui.csv"

# Classificazione euristica dei diff: primo pattern che combacia vince.
DIFF_RULES = [
    ("vuoto", re.compile(r"^\s*$")),
    ("riformattazione", re.compile(r"^\s*[-+]\s*[{}();,]*\s*$")),
    ("versione_dipendenza", re.compile(r'"(version|cypress|playwright|selenium)":\s*"|version\s*=\s*"\d')),
    ("cambio_asserzioni", re.compile(r"^\s*[-+].*\b(assert|expect|should|verify)\b", re.I)),
    ("cambio_selettori", re.compile(r"^\s*[-+].*(#|\.|\[)[\w-]+\]?\s*['\"]|By\.\w+|getBy\w+|data-test", re.I)),
    ("cambio_wait", re.compile(r"^\s*[-+].*(sleep|wait|timeout|implicitly)")),
]


def _force_write(func, path, exc):
    """Su Windows Git crea file in sola lettura (oggetti, pack, hooks):
    rmtree deve fare chmod prima di riprovare, altrimenti lascia .git dietro."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:  # noqa: BLE001
        pass


def rmtree_hard(path: Path, tentativi: int = 3) -> None:
    """Cancella una cartella anche se contiene file read-only o handle aperti (Windows)."""
    if not path.exists():
        return
    for i in range(tentativi):
        try:
            shutil.rmtree(path, onexc=_force_write)
        except TypeError:  # Python < 3.12: il parametro si chiama onerror
            shutil.rmtree(path, onerror=_force_write)
        except Exception:  # noqa: BLE001
            pass
        if not path.exists():
            return
        time.sleep(0.5 * (i + 1))
    # ultima spiaggia su Windows: cmd /c rd
    if sys.platform == "win32":
        subprocess.run(["cmd", "/c", "rd", "/s", "/q", str(path)], capture_output=True)


def git(args: list[str], cwd: Path, timeout: int = 900) -> tuple[int, str]:
    try:
        p = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except Exception as exc:  # noqa: BLE001
        return 1, str(exc)


def classify_diff(diff_text: str) -> str:
    added = [l for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff_text.splitlines() if l.startswith("-") and not l.startswith("---")]
    changed = added + removed
    if not changed:
        return "nessun_cambio"
    for name, rx in DIFF_RULES:
        if all(rx.search(l) or not l.strip() for l in changed):
            return name
    if len(changed) <= 4:
        return "modifica_puntuale"
    return "riscrittura"


def count_touches(repo: Path, sha: str, path: str) -> int:
    """Quanti commit hanno toccato il file nel periodo di vita del repository.

    Nota sull'ordine degli argomenti: `--follow` e `--` devono venire PRIMA del
    percorso, altrimenti Git interpreta "rev-list --count --follow -- <path>"
    come una lista di commit e va in errore ("usage: git rev-list").
    """
    code, out = git(["rev-list", "--count", "--follow", "--", path], repo)
    if code != 0:
        return 0
    try:
        return int(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return 0


def count_since_snapshot(repo: Path, sha: str) -> int:
    """Commit totali del repository dal commit dello snapshot a HEAD."""
    code, out = git(["rev-list", "--count", f"{sha}..HEAD"], repo)
    if code != 0:
        return 0
    try:
        return int(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return 0


def last_touch(repo: Path, path: str) -> tuple[str, str, str, int]:
    """Ultimo evento che ha toccato il percorso: (sha, data, status, righe).

    `--follow` segue i rename all'indietro; `--name-status` dice se l'ultimo
    evento è stato M (modified), D (deleted), R (renamed) o A (added).
    Questo permette di distinguere un file **cancellato** da uno **spostato**.
    """
    code, out = git(["log", "--follow", "--name-status", "--numstat", "-1",
                     "--format=@%h|%ad", "--date=short", "--", path], repo)
    if code != 0 or not out.strip():
        return "", "", "", 0
    sha = date = status = ""
    nrighe = 0
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("@"):
            parts = line[1:].split("|")
            sha = parts[0] if parts else ""
            date = parts[1] if len(parts) > 1 else ""
        elif re.match(r"^[AMDRTC]\d*(\t|$)", line):
            status = line[:2] if line[1:2].isdigit() else line[:1]
        elif status and "\t" in line:
            a, d = line.split("\t")[:2]
            nrighe = (int(a) if a.isdigit() else 0) + (int(d) if d.isdigit() else 0)
            break
    return sha, date, status, nrighe


def process_repo(repo_name: str, sha: str, tests: list[dict], keep: bool) -> tuple[list[dict], dict]:
    """Elabora un repository e restituisce (righe per test, riga di riepilogo)."""
    dest = CLONES / repo_name.replace("/", "__")
    summary = {"repository_name": repo_name, "last_commit_sha": sha, "status": "ok", "note": ""}
    rows: list[dict] = []

    rmtree_hard(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    code, out = git(["clone", "--filter=blob:none", "--no-checkout", "--quiet",
                     f"https://github.com/{repo_name}", str(dest)], ROOT, timeout=1800)
    if code != 0:
        summary["status"] = "clone_fallito"
        summary["note"] = out.strip()[:200]
        return rows, summary

    # il commit dello snapshot deve esistere nel clone
    code, _ = git(["cat-file", "-e", f"{sha}^{{commit}}"], dest)
    if code != 0:
        summary["status"] = "commit_assente"
        summary["note"] = f"{sha} non raggiungibile (force-push? repo riscritto?)"
        if not keep:
            rmtree_hard(dest)
        return rows, summary

    commits_dopo = count_since_snapshot(dest, sha)

    for t in tests:
        rel = t["test_path_rel"]
        code_tree, out_tree = git(["ls-tree", "-r", "--name-only", "HEAD", "--", rel], dest)
        exists_now = code_tree == 0 and bool(out_tree.strip())

        touches = count_touches(dest, sha, rel)

        added = removed = 0
        kind = "non_valutato"
        last_sha, last_date = "", ""
        if exists_now:
            code_diff, diff_out = git(["diff", "--numstat", sha, "HEAD", "--", rel], dest)
            if code_diff == 0 and diff_out.strip():
                first = diff_out.strip().split("\t")
                added = int(first[0]) if first[0].isdigit() else 0
                removed = int(first[1]) if len(first) > 1 and first[1].isdigit() else 0
            code_full, diff_full = git(["diff", "-U0", sha, "HEAD", "--", rel], dest)
            kind = classify_diff(diff_full) if code_full == 0 else "errore_diff"
            if added or removed:
                last_sha, last_date, last_status, _ = last_touch(dest, rel)
        else:
            last_sha, last_date, last_status, _ = last_touch(dest, rel)
            if last_status.startswith("R"):
                kind = "spostato"
            elif last_status.startswith("D"):
                kind = "cancellato"
            elif last_sha:
                kind = "fuori_percorso"   # il percorso non c'è più a HEAD, ma nessun evento D
            else:
                kind = "mai_esistito"

        rows.append({
            "repository_name": repo_name,
            "test_path_rel": rel,
            "declared_tests": t["number_of_tests"],
            "esiste_oggi": int(exists_now),
            "modifiche_totali": touches,
            "commit_repo_da_snapshot": commits_dopo,
            "righe_aggiunte": added,
            "righe_rimosse": removed,
            "tipo_cambiamento": kind,
            "ultimo_evento": last_status,
            "ultimo_commit_file": last_sha,
            "ultimo_commit_data": last_date,
        })

    summary["files"] = len(tests)
    summary["files_esistenti"] = sum(r["esiste_oggi"] for r in rows)
    summary["files_modificati"] = sum(1 for r in rows if r["righe_aggiunte"] or r["righe_rimosse"])
    summary["righe_nette"] = sum(r["righe_aggiunte"] - r["righe_rimosse"] for r in rows)
    summary["commit_repo_da_snapshot"] = commits_dopo

    if not keep:
        rmtree_hard(dest)
    return rows, summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="elabora solo i primi N repository")
    ap.add_argument("--workers", type=int, default=3, help="cloni in parallelo (default 3)")
    ap.add_argument("--keep-clones", action="store_true", help="non cancellare i cloni a fine lavoro")
    args = ap.parse_args()

    if not REPO_CSV.exists() or not TESTS_CSV.exists():
        sys.exit("Mancano data/repos_commit.csv o data/tests_gui.csv: lancia prima 01_estrai_repository.py")

    repos = list(csv.DictReader(REPO_CSV.open(encoding="utf-8")))
    tests_by_repo: dict[str, list[dict]] = {}
    for t in csv.DictReader(TESTS_CSV.open(encoding="utf-8")):
        tests_by_repo.setdefault(t["repository_name"], []).append(t)

    if args.limit:
        repos = repos[: args.limit]

    RESULTS.mkdir(exist_ok=True)
    CLONES.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    summaries: list[dict] = []
    print(f"Repository da elaborare: {len(repos)}  (workers={args.workers})")

    def job(r: dict):
        return process_repo(r["repository_name"], r["last_commit_sha"],
                            tests_by_repo.get(r["repository_name"], []), args.keep_clones)

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(job, r): r["repository_name"] for r in repos}
        for i, fut in enumerate(as_completed(futures), 1):
            name = futures[fut]
            try:
                rows, summary = fut.result()
            except Exception as exc:  # noqa: BLE001
                rows, summary = [], {"repository_name": name, "status": "errore", "note": str(exc)[:200]}
            all_rows.extend(rows)
            summaries.append(summary)
            print(f"  [{i}/{len(repos)}] {name:<50} {summary.get('status')} "
                  f"({summary.get('files_esistenti', 0)}/{summary.get('files', 0)} file presenti)")

    test_cols = ["repository_name", "test_path_rel", "declared_tests", "esiste_oggi",
                 "modifiche_totali", "commit_repo_da_snapshot", "righe_aggiunte", "righe_rimosse",
                 "tipo_cambiamento", "ultimo_evento", "ultimo_commit_file", "ultimo_commit_data"]
    with (RESULTS / "storia_test.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=test_cols)
        w.writeheader()
        w.writerows(all_rows)

    sum_cols = ["repository_name", "last_commit_sha", "status", "note", "files", "files_esistenti",
                "files_modificati", "righe_nette", "commit_repo_da_snapshot"]
    with (RESULTS / "storia_riepilogo.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=sum_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(summaries)

    ok = sum(1 for s in summaries if s.get("status") == "ok")
    print(f"\nRepository ok: {ok}/{len(repos)}")
    print(f"File di test analizzati: {len(all_rows)}")
    print(f"  ancora presenti: {sum(r['esiste_oggi'] for r in all_rows)}")
    print(f"  cancellati: {sum(1 for r in all_rows if r['tipo_cambiamento'] == 'cancellato')}")
    print(f"  modificati dal commit: {sum(1 for r in all_rows if r['righe_aggiunte'] or r['righe_rimosse'])}")
    print("\n-> results/storia_test.csv")
    print("-> results/storia_riepilogo.csv")


if __name__ == "__main__":
    main()

