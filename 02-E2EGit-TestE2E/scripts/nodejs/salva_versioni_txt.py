#!/usr/bin/env python3
import sys
from collections import defaultdict
from glob import glob
from pathlib import Path

# Usa l'ambiente virtuale del progetto
ROOT = Path(__file__).resolve().parents[2]
sys.path.extend(glob(str(ROOT / ".venv/lib/python*/site-packages")))

from pydriller import Git

# 1. Percorsi della repository
base_dir = Path(sys.argv[1]).resolve()
repo_dir = base_dir / "repo"
out_file = base_dir / "results" / "versioni_repository.txt"
out_file.parent.mkdir(parents=True, exist_ok=True)

# 2. Estrazione di tutti i tag (versioni) e dei package.json
gr = Git(str(repo_dir))
versioni = []

for tag in gr.repo.tags:
    data = tag.commit.committed_datetime.strftime("%Y-%m-%d")
    pkgs = [
        item.path for item in tag.commit.tree.traverse()
        if getattr(item, "name", "") == "package.json"
    ]
    versioni.append((data, tag.name, pkgs))

versioni.sort()

# Raggruppa le versioni per anno
per_anno = defaultdict(list)
for data, nome_tag, _ in versioni:
    anno = data[:4]
    per_anno[anno].append(nome_tag)

# 3. Scrittura del file di testo
with open(out_file, "w", encoding="utf-8") as f:
    f.write(f"ELENCO VERSIONI REPOSITORY: {base_dir.name} (Totale: {len(versioni)})\n")
    f.write("=" * 100 + "\n\n")

    # Tabella 1: Riepilogo per anno
    f.write(f"{'Anno':<8} | {'N. Versioni':<12} | {'Prima Versione':<20} | {'Ultima Versione':<20}\n")
    f.write("-" * 65 + "\n")
    for anno, lista in sorted(per_anno.items()):
        f.write(f"{anno:<8} | {len(lista):<12} | {lista[0]:<20} | {lista[-1]:<20}\n")

    # Tabella 2: Elenco completo delle versioni
    f.write("\n")
    f.write(f"{'#':<5} | {'Versione':<28} | {'Data Rilascio':<15} | {'Anno':<6} | {'N. Pkg':<8} | {'Percorsi package.json'}\n")
    f.write("-" * 100 + "\n")
    for i, (data, nome_tag, pkgs) in enumerate(versioni, 1):
        percorsi = ", ".join(pkgs) if pkgs else "Nessuno"
        f.write(f"{i:<5} | {nome_tag:<28} | {data:<15} | {data[:4]:<6} | {len(pkgs):<8} | {percorsi}\n")

print(f"Salvato: {out_file} ({len(versioni)} versioni)")
