#!/usr/bin/env python3
"""salva_ciclo_vita_txt.py — Salva il ciclo di vita dei test E2E di progetti Node.js in ciclo_vita_test.txt
usando PyDriller e le versioni salvate in versioni_repository.txt.

Uso:
    python3 salva_ciclo_vita_txt.py <path_repository>
Esempio:
    python3 scripts/nodejs/salva_ciclo_vita_txt.py /home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/angular-slickgrid
"""

import subprocess
import sys
from collections import defaultdict
from glob import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend(glob(str(ROOT / ".venv/lib/python*/site-packages")))

from pydriller import Git, Repository

# Filtri specifici per l'ecosistema Node.js (JavaScript / TypeScript)
CARTELLE_E2E = ("e2e", "cypress", "playwright", "autotests", "acceptance", "integration")
ESTENSIONI_E2E = (".cy.ts", ".cy.js", ".spec.ts", ".spec.js", ".test.ts", ".test.js", ".e2e.ts", ".e2e.js")

# 1. Parsing dell'argomento: path completo della repository
if len(sys.argv) < 2:
    print("Uso: python3 salva_ciclo_vita_txt.py <path_repository>")
    print("Esempio: python3 salva_ciclo_vita_txt.py /home/paolo/.../repositories/angular-slickgrid")
    sys.exit(1)

target_path = Path(sys.argv[1]).resolve()
if not target_path.exists() and (ROOT / "repositories" / sys.argv[1]).exists():
    target_path = ROOT / "repositories" / sys.argv[1]

repo_dir = target_path / "repo" if (target_path / "repo").exists() else target_path
results_dir = target_path / "results" if (target_path / "repo").exists() else target_path.parent / "results"
nome_repo = target_path.name if (target_path / "repo").exists() else repo_dir.name

file_versioni = results_dir / "versioni_repository.txt"
out_file = results_dir / "ciclo_vita_test.txt"

# 2. Se non esiste ancora versioni_repository.txt, richiama salva_versioni_txt.py
if not file_versioni.exists():
    script_versioni = Path(__file__).resolve().parent / "salva_versioni_txt.py"
    subprocess.run([sys.executable, str(script_versioni), str(target_path)], check=True)

# 3. Legge le versioni da versioni_repository.txt
versioni = []
versioni_per_anno = defaultdict(int)
for riga in file_versioni.read_text(encoding="utf-8").splitlines():
    parti = [p.strip() for p in riga.split("|")]
    if len(parti) >= 4 and parti[0].isdigit() and parti[3].isdigit():
        _, tag, data, anno = parti[:4]
        versioni.append((data, tag))
        versioni_per_anno[anno] += 1

indice_ver = {tag: i for i, (_, tag) in enumerate(versioni)}

# 4. Estrae i file E2E toccati in ogni commit e scorre la storia con PyDriller
gr = Git(str(repo_dir))
branch = "master" if "master" in [h.name for h in gr.repo.heads] else "HEAD"

file_nel_commit = defaultdict(list)
sha = ""
for riga in gr.repo.git.log(branch, "--no-renames", "--format=COMMIT|%H", "--name-only").splitlines():
    if riga.startswith("COMMIT|"):
        sha = riga.split("|")[1]
    elif riga.lower().endswith(ESTENSIONI_E2E) and "__tests__" not in riga.lower():
        if any(c in riga.lower() for c in CARTELLE_E2E) or riga.lower().endswith((".cy.ts", ".cy.js")):
            file_nel_commit[sha].append(Path(riga).name)

storia_test = defaultdict(list)
for commit in Repository(str(repo_dir), only_in_branch=branch).traverse_commits():
    if commit.hash not in file_nel_commit:
        continue
    data_c = commit.committer_date.strftime("%Y-%m-%d")
    ver_c = next((tag for data_t, tag in versioni if data_t >= data_c), "HEAD")
    for nome_file in file_nel_commit[commit.hash]:
        storia_test[nome_file].append((data_c, ver_c))

# 5. Scrive la tabella finale in ciclo_vita_test.txt
righe = [
    f"CICLO DI VITA DEI TEST E2E (Node.js): {nome_repo} (Totale: {len(storia_test)} file)",
    "=" * 115,
    f"{'File di Test':<32} | {'Nascita (Ver / Data)':<24} | {'Ver. Anno':<9} | {'1ª Modifica (Δ Ver)':<22} | {'Modifiche Successive'}",
    "-" * 115,
]

for nome_file in sorted(storia_test):
    eventi = storia_test[nome_file]
    data_nascita, ver_nascita = eventi[0]
    n_ver_anno = versioni_per_anno[data_nascita[:4]]

    ver_modifiche = []
    ver_prec = ver_nascita
    for _, ver_corr in eventi[1:]:
        if ver_corr != ver_prec:
            delta = max(1, indice_ver.get(ver_corr, len(versioni)) - indice_ver.get(ver_prec, 0))
            ver_modifiche.append((ver_corr, delta))
            ver_prec = ver_corr

    if ver_modifiche:
        prima_ver, primo_delta = ver_modifiche[0]
        prima_mod = f"{prima_ver} (+{primo_delta} ver)"
        altre_mod = ", ".join(v for v, _ in ver_modifiche[1:]) or "Nessuna"
    else:
        prima_mod, altre_mod = "Mai modificato", "-"

    righe.append(f"{nome_file:<32} | {f'{ver_nascita} ({data_nascita})':<24} | {n_ver_anno:<9} | {prima_mod:<22} | {altre_mod}")

out_file.write_text("\n".join(righe) + "\n", encoding="utf-8")
print(f"Salvato: {out_file} ({len(storia_test)} test E2E)")

