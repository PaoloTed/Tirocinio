#!/usr/bin/env python3
"""Dato il nome di una repo (o --all per tutte quelle in repositories/repo_nodejs/),
prende il file *_only_gui.xlsx/.csv da RQ3, lo copia nella cartella della repo
e genera storia_test_<nome_repo>.txt con creazione e modifiche (%) di ogni test.

Uso:
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/storia_test_only_gui.py lizmap-web-client
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/storia_test_only_gui.py altinn/altinn-studio
    python3 02-E2EGit-TestE2E/scripts/analisi_rq3/storia_test_only_gui.py --all
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from classifica_b_rq3 import ROOT, _load_only_gui_csv, _load_only_gui_xlsx
from classifica_repo_rq3 import RQ3_COMMIT_DIR

REPOS_NODEJS_DIR = ROOT / "repositories" / "repo_nodejs"


def slug_da_git_remote(repo_dir: Path) -> str | None:
    """Se esiste repo/.git, ricava 'owner_repo' dal remote origin."""
    git_dir = repo_dir / "repo"
    if not (git_dir / ".git").exists():
        return None
    res = subprocess.run(
        ["git", "-C", str(git_dir), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return None
    parts = res.stdout.strip().rstrip("/").removesuffix(".git").split("/")
    return f"{parts[-2]}_{parts[-1]}" if len(parts) >= 2 else None


def trova_sorgente_e_destinazione(target: str) -> tuple[str, Path, Path]:
    """Restituisce (nome_cartella_locale, file_only_gui_in_rq3, cartella_destinazione)."""
    p = Path(target)
    if p.is_file():
        nome_locale = p.parent.name.split("_", 1)[-1]
        return nome_locale, p, REPOS_NODEJS_DIR / nome_locale

    nome_pulito = p.name if p.exists() else target.strip()
    if "/" in nome_pulito:
        slug = nome_pulito.replace("/", "_")
        nome_locale = nome_pulito.split("/", 1)[1]
    elif (REPOS_NODEJS_DIR / nome_pulito).is_dir():
        nome_locale = nome_pulito
        slug = slug_da_git_remote(REPOS_NODEJS_DIR / nome_locale) or nome_pulito
    elif (RQ3_COMMIT_DIR / nome_pulito).is_dir():
        slug = nome_pulito
        nome_locale = nome_pulito.split("_", 1)[-1]
    else:
        nome_locale = nome_pulito
        slug = nome_pulito

    rq3_dir = RQ3_COMMIT_DIR / slug
    if not rq3_dir.is_dir():
        candidati = sorted(d for d in RQ3_COMMIT_DIR.iterdir() if d.is_dir() and d.name.lower().endswith(f"_{nome_locale.lower()}"))
        if len(candidati) == 1:
            rq3_dir = candidati[0]
        elif len(candidati) > 1:
            raise ValueError(f"Più repo in RQ3 corrispondono a '{target}': {[c.name for c in candidati]}. Usa 'owner/repo'.")
        else:
            raise FileNotFoundError(f"Cartella RQ3 non trovata per '{target}'.")

    files = sorted(rq3_dir.glob("*_only_gui.xlsx")) or sorted(rq3_dir.glob("*_only_gui.csv"))
    if not files:
        raise FileNotFoundError(f"Nessun file *_only_gui.xlsx/.csv in {rq3_dir}")

    return nome_locale, files[0], REPOS_NODEJS_DIR / nome_locale


def dividi_commit_data(intestazione: str) -> tuple[str, str]:
    """Da 'Commit 98 (2024-01-31 15:32:09)' restituisce ('Commit 98', '2024-01-31 15:32:09')."""
    if " (" in intestazione:
        commit, data = intestazione.split(" (", 1)
        return commit.strip(), data.rstrip(") ").strip()
    return intestazione.strip(), "-"


def descrivi_test(indice: int, percorso: str, eventi: list[tuple[int, str, str]], ultimo_col: int, ultima_intestazione: str) -> list[str]:
    """Crea le righe di testo per un singolo test."""
    col_inizio, hdr_inizio, val_inizio = eventi[0]
    commit_inizio, data_inizio = dividi_commit_data(hdr_inizio)

    if val_inizio == "A":
        righe = [f"Test {indice}: {percorso} | creato a {commit_inizio} ({data_inizio})"]
    else:
        righe = [f"Test {indice}: {percorso} | primo evento [{val_inizio}] a {commit_inizio} ({data_inizio})"]

    col_prec = col_inizio
    num_mod = 0
    eliminato = False

    for col, hdr, val in eventi[1:]:
        dopo = col - col_prec
        commit, data = dividi_commit_data(hdr)

        if val.startswith("M("):
            num_mod += 1
            righe.append(f"- Mod {num_mod} dopo {dopo} commit ({commit}) in percentuale {val[2:-1]}% | {data}")
        elif val.startswith("R("):
            righe.append(f"- Rename (da {val[2:-1]}) dopo {dopo} commit ({commit}) | {data}")
        elif val == "D":
            eliminato = True
            righe.append(f"- Eliminato dopo {dopo} commit ({commit}) | {data}")
        else:
            righe.append(f"- Evento [{val}] dopo {dopo} commit ({commit}) | {data}")
            eliminato = False

        col_prec = col

    if not eliminato and ultimo_col > col_prec:
        commit_fine, data_fine = dividi_commit_data(ultima_intestazione)
        righe.append(f"- Nessun'altra modifica per {ultimo_col - col_prec} commit fino a fine storia ({commit_fine}, {data_fine})")

    return righe


def elabora_repo(target: str) -> None:
    """Copia *_only_gui nella cartella della repo e genera storia_test_<nome_repo>.txt."""
    nome_locale, file_gui, dest_dir = trova_sorgente_e_destinazione(target)
    dest_dir.mkdir(parents=True, exist_ok=True)

    file_copiato = dest_dir / file_gui.name
    if file_gui.resolve() != file_copiato.resolve():
        shutil.copy2(file_gui, file_copiato)

    hdr, righe = _load_only_gui_csv(file_copiato) if file_copiato.suffix == ".csv" else _load_only_gui_xlsx(file_copiato)
    colonne_commit = sorted(k for k in hdr if k >= 1)
    ultimo_col = colonne_commit[-1]
    c1, d1 = dividi_commit_data(hdr[colonne_commit[0]])
    c2, d2 = dividi_commit_data(hdr[ultimo_col])

    output = [
        f"Repository: {nome_locale}",
        f"Commit analizzati: {len(colonne_commit)} ({c1} {d1} -> {c2} {d2})",
        f"File di test trovati: {len(righe)}",
        "",
    ]

    for i, celle in enumerate(righe, start=1):
        percorso = celle.get(0, "").strip()
        if not percorso:
            continue
        eventi = [(c, hdr[c], celle[c]) for c in sorted(celle) if c >= 1 and c in hdr]
        if eventi:
            output.extend(descrivi_test(i, percorso, eventi, ultimo_col, hdr[ultimo_col]))
            output.append("")

    out_txt = dest_dir / f"storia_test_{nome_locale}.txt"
    out_txt.write_text("\n".join(output), encoding="utf-8")
    print(f"[OK] {nome_locale}: copiato {file_copiato.name} e creato {out_txt.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Copia *_only_gui da RQ3 nella repo e genera storia_test_<repo>.txt.")
    parser.add_argument("repo", nargs="?", help="Nome repo (es. lizmap-web-client o altinn/altinn-studio)")
    parser.add_argument("--all", action="store_true", help="Elabora tutte le repo in repositories/repo_nodejs/")
    args = parser.parse_args()

    if args.all:
        for d in sorted(REPOS_NODEJS_DIR.iterdir()):
            if d.is_dir():
                elabora_repo(d.name)
    elif args.repo:
        elabora_repo(args.repo)
    else:
        parser.error("Specifica il nome della repo oppure --all")


if __name__ == "__main__":
    main()
