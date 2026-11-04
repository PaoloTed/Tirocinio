#!/usr/bin/env python3
"""salva_versioni_txt.py — Salva tutte le versioni (tag Git) di una repository Node.js
in versioni_repository.txt, tracciando il numero e i percorsi dei package.json.

Uso:
    python3 salva_versioni_txt.py <path_repository>
Esempio:
    python3 scripts/nodejs/salva_versioni_txt.py /home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/angular-slickgrid
"""

import sys
from collections import defaultdict
from glob import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend(glob(str(ROOT / ".venv/lib/python*/site-packages")))

from pydriller import Git

# 1. Parsing dell'argomento: path completo della repository
if len(sys.argv) < 2:
    print("Uso: python3 salva_versioni_txt.py <path_repository>")
    print("Esempio: python3 salva_versioni_txt.py /home/paolo/.../repositories/angular-slickgrid")
    sys.exit(1)

target_path = Path(sys.argv[1]).resolve()
if not target_path.exists() and (ROOT / "repositories" / sys.argv[1]).exists():
    target_path = ROOT / "repositories" / sys.argv[1]

# Se target_path contiene la sottocartella "repo", usa quella per Git e "results" per l'output
repo_dir = target_path / "repo" if (target_path / "repo").exists() else target_path
results_dir = target_path / "results" if (target_path / "repo").exists() else target_path.parent / "results"
nome_repo = target_path.name if (target_path / "repo").exists() else repo_dir.name

out_file = results_dir / "versioni_repository.txt"
results_dir.mkdir(parents=True, exist_ok=True)

# 2. Estrae tutti i tag e trova i package.json presenti per ciascun commit
gr = Git(str(repo_dir))
cache_pkg = {}
versioni = []

for t in gr.repo.tags:
    sha = t.commit.hexsha
    if sha not in cache_pkg:
        cache_pkg[sha] = [
            item.path for item in t.commit.tree.traverse()
            if item.type == "blob" and Path(item.path).name == "package.json"
        ]
    data = t.commit.committed_datetime.strftime("%Y-%m-%d")
    versioni.append((data, t.name, cache_pkg[sha]))

versioni.sort(key=lambda x: x[0])

per_anno = defaultdict(list)
for data, nome_tag, _ in versioni:
    per_anno[data[:4]].append(nome_tag)

# 3. Costruisce e salva il file di testo
righe = [
    f"ELENCO VERSIONI REPOSITORY (Node.js): {nome_repo} (Totale: {len(versioni)})",
    "=" * 100,
    "",
    f"{'Anno':<8} | {'N. Versioni':<12} | {'Prima Versione':<20} | {'Ultima Versione':<20}",
    "-" * 65,
]
for anno, lista in sorted(per_anno.items()):
    righe.append(f"{anno:<8} | {len(lista):<12} | {lista[0]:<20} | {lista[-1]:<20}")

righe += [
    "",
    f"{'#':<5} | {'Versione':<28} | {'Data Rilascio':<15} | {'Anno':<6} | {'N. Pkg':<8} | {'Percorsi package.json'}",
    "-" * 100,
]
for i, (data, nome_tag, pkgs) in enumerate(versioni, 1):
    str_pkgs = ", ".join(pkgs) if pkgs else "Nessuno"
    righe.append(f"{i:<5} | {nome_tag:<28} | {data:<15} | {data[:4]:<6} | {len(pkgs):<8} | {str_pkgs}")

out_file.write_text("\n".join(righe) + "\n", encoding="utf-8")
print(f"Salvato: {out_file} ({len(versioni)} versioni analizzate)")

