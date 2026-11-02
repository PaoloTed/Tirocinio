#!/usr/bin/env python3
"""04_analizza_ciclo_vita.py — Ricostruzione e calcolo del ciclo di vita di un file di test E2E.

Implementa le metriche formali definite in docs/04_metriche_ciclo_di_vita.md:
- t_birth: commit e data di nascita del test.
- Delta commit: commit dell'applicazione tra una modifica e la successiva.
- N_mod: modifiche dal commit di snapshot (t0) a oggi (HEAD).
- Classificazione euristica del diff (selettori, asserzioni, wait, riscrittura).

Uso:
    python src/04_analizza_ciclo_vita.py --repo-dir <path_a_repo_git> --test-path <path_rel_al_test>
    python src/04_analizza_ciclo_vita.py --demo   # Esegue un'analisi dimostrativa sulla storia Git locale
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

DIFF_RULES = [
    ("vuoto", re.compile(r"^\s*$")),
    ("riformattazione", re.compile(r"^\s*[-+]\s*[{}();,]*\s*$")),
    ("versione_dipendenza", re.compile(r'"(version|cypress|playwright|selenium)":\s*"|version\s*=\s*"\d')),
    ("cambio_asserzioni", re.compile(r"^\s*[-+].*\b(assert|expect|should|verify|to\.equal|toBe)\b", re.I)),
    ("cambio_selettori", re.compile(r"^\s*[-+].*(#|\.|\[)[\w-]+\]?\s*['\"]|By\.\w+|getBy\w+|data-test", re.I)),
    ("cambio_wait", re.compile(r"^\s*[-+].*(sleep|wait|timeout|waitForSelector|waitForLoadState)", re.I)),
]


def git_cmd(args: list[str], cwd: Path) -> tuple[int, str]:
    try:
        p = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return p.returncode, p.stdout.strip()
    except Exception as e:
        return 1, str(e)


def classify_diff(diff_text: str) -> str:
    lines = diff_text.splitlines()
    added = [l for l in lines if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in lines if l.startswith("-") and not l.startswith("---")]
    changed = added + removed

    if not changed:
        return "nessun_cambio"

    for name, rx in DIFF_RULES:
        if all(rx.search(l) or not l.strip() for l in changed):
            return name
        # Se anche solo una riga contiene un selettore o asserzione, etichettiamo in modo specifico
        if any(rx.search(l) for l in changed) and name in ("cambio_selettori", "cambio_asserzioni", "cambio_wait"):
            return name

    if len(changed) <= 4:
        return "modifica_puntuale"
    return "riscrittura"


def analyze_test_lifecycle(repo_path: Path, test_path: str, snapshot_sha: str | None = None) -> dict:
    # 1. Verifica esistenza e commit che hanno toccato il file
    code, log_out = git_cmd(
        ["log", "--follow", "--format=%H|%ad|%an|%s", "--date=short", "--", test_path],
        repo_path,
    )
    if code != 0 or not log_out:
        return {"error": f"Nessuna storia trovata per il file: {test_path}"}

    commits_raw = log_out.splitlines()
    # In ordine cronologico (dal più vecchio al più recente)
    commits_raw.reverse()

    history = []
    prev_sha = None

    for idx, line in enumerate(commits_raw):
        parts = line.split("|", 3)
        sha = parts[0]
        date = parts[1]
        author = parts[2]
        msg = parts[3] if len(parts) > 3 else ""

        # Calcolo commit intermedi dell'applicazione rispetto al commit precedente
        delta_commits = 0
        diff_kind = "creazione" if idx == 0 else "modifica"
        lines_add, lines_del = 0, 0

        if prev_sha:
            code_c, count_out = git_cmd(["rev-list", "--count", f"{prev_sha}..{sha}"], repo_path)
            if code_c == 0 and count_out.isdigit():
                delta_commits = int(count_out)

            code_d, diff_text = git_cmd(["diff", "-U0", prev_sha, sha, "--", test_path], repo_path)
            if code_d == 0:
                diff_kind = classify_diff(diff_text)
                lines_add = len([l for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")])
                lines_del = len([l for l in diff_text.splitlines() if l.startswith("-") and not l.startswith("---")])

        history.append({
            "idx": idx + 1,
            "sha": sha[:8],
            "sha_full": sha,
            "date": date,
            "author": author,
            "message": msg[:60],
            "delta_app_commits": delta_commits,
            "diff_kind": diff_kind,
            "lines_added": lines_add,
            "lines_deleted": lines_del,
        })
        prev_sha = sha

    # Metriche riassuntive
    t_birth = history[0]
    delta_first_mod = history[1]["delta_app_commits"] if len(history) > 1 else None
    tot_modifications = len(history) - 1

    # N_mod rispetto a snapshot (se fornito)
    n_mod_snapshot = 0
    if snapshot_sha:
        code_s, count_s = git_cmd(
            ["rev-list", "--count", f"{snapshot_sha}..HEAD", "--", test_path],
            repo_path,
        )
        if code_s == 0 and count_s.isdigit():
            n_mod_snapshot = int(count_s)

    return {
        "test_path": test_path,
        "t_birth": t_birth,
        "delta_first_mod": delta_first_mod,
        "tot_modifications": tot_modifications,
        "n_mod_snapshot": n_mod_snapshot,
        "history": history,
    }


def print_timeline(res: dict) -> None:
    if "error" in res:
        print(f"[ERRORE] {res['error']}")
        return

    print("\n" + "=" * 90)
    print(f"📊 ANALISI CICLO DI VITA: {res['test_path']}")
    print("=" * 90)
    print(f"• t_birth (Nascita): Commit {res['t_birth']['sha']} del {res['t_birth']['date']} da {res['t_birth']['author']}")
    print(f"• Modifiche Totali nel Ciclo di Vita: {res['tot_modifications']}")
    if res['delta_first_mod'] is not None:
        print(f"• Δ_first_mod: {res['delta_first_mod']} commit dell'app prima della 1ª manutenzione")
    else:
        print("• Δ_first_mod: Mai modificato dopo la creazione (test vergine)")

    print("\nTIMELINE DEGLI EVENTI SUL TEST:")
    print("-" * 90)
    print(f"{'#':<3} | {'Data':<10} | {'Commit':<8} | {'Δ App':<7} | {'Diff Tipo':<20} | {'+/-':<8} | {'Messaggio'}")
    print("-" * 90)

    for h in res["history"]:
        delta_str = f"+{h['delta_app_commits']}" if h['delta_app_commits'] else "-"
        diff_stats = f"+{h['lines_added']}/-{h['lines_deleted']}" if h['idx'] > 1 else "INIT"
        print(
            f"{h['idx']:<3} | {h['date']:<10} | {h['sha']:<8} | {delta_str:<7} | "
            f"{h['diff_kind']:<20} | {diff_stats:<8} | {h['message']}"
        )
    print("-" * 90 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisi formale del ciclo di vita di un test E2E.")
    parser.add_argument("--repo-dir", type=Path, default=Path("."), help="Path locale del repository Git")
    parser.add_argument("--test-path", type=str, help="Path relativo del file di test da tracciare")
    parser.add_argument("--snapshot-sha", type=str, default=None, help="Commit sha dello snapshot t0")
    parser.add_argument("--demo", action="store_true", help="Esegui demo su un file del repository corrente")
    args = parser.parse_args()

    if args.demo or not args.test_path:
        # Seleziona un file del repo locale per dimostrazione
        demo_file = "02-E2EGit-TestE2E/src/01_estrai_repository.py"
        print(f"[DEMO] Esecuzione dell'analisi del ciclo di vita su: {demo_file}")
        res = analyze_test_lifecycle(Path("."), demo_file)
        print_timeline(res)
        return

    res = analyze_test_lifecycle(args.repo_dir, args.test_path, args.snapshot_sha)
    print_timeline(res)


if __name__ == "__main__":
    main()

