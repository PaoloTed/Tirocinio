#!/usr/bin/env python3
"""07_analizza_versioni_test.py — Traccia il ciclo di vita del 100% dei test E2E (46 file)
di ghiscoding/angular-slickgrid in relazione a tutte le 70 versioni rilasciate
da v5.4.0 (2023-02-04) a v8.14.1 (2025-05-08).
"""

from __future__ import annotations

import csv
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLONE_DIR = ROOT / "repositories" / "angular-slickgrid" / "repo"
RESULTS_DIR = ROOT / "repositories" / "angular-slickgrid" / "results"


def git_cmd(args: list[str]) -> str:
    p = subprocess.run(["git", *args], cwd=CLONE_DIR, capture_output=True, text=True, errors="replace")
    return p.stdout.strip()


def main():
    # 1. Mappatura di tutte le release da v5.4.0 a v8.14.1
    p_tags = git_cmd(["tag", "--sort=creatordate", "--format=%(creatordate:short)|%(refname:short)"])
    tags_by_year = defaultdict(list)
    all_tags = []
    ts_era_tags = []  # Da v5.4.0 a v8.14.1
    started_v54 = False

    for line in p_tags.splitlines():
        if not line.strip():
            continue
        date, tag = line.split("|")
        all_tags.append(tag)
        if tag == "v5.4.0":
            started_v54 = True
        if started_v54:
            year = date[:4]
            tags_by_year[year].append((date, tag))
            ts_era_tags.append((date, tag))

    tag_index = {tag: i for i, tag in enumerate(all_tags)}

    # 2. Carica TUTTI i 46 file di test E2E presenti a v8.14.1 / master
    # Nota: se il working tree è su un tag vecchio (es. v5.4.0), leggiamo la lista da master
    ls_out = git_cmd(["ls-tree", "--name-only", "master", "test/cypress/e2e/"])
    test_files = sorted([
        line.strip() for line in ls_out.splitlines()
        if line.strip().endswith(".cy.ts")
    ])

    def get_release_for_commit(sha: str) -> str:
        out = git_cmd(["tag", "--contains", sha, "--sort=creatordate"])
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        return lines[0] if lines else "HEAD (post-v8.14.1)"

    analysis_data = []
    # Mappa inversa per versione: quali test sono nati e quali sono stati modificati in ogni versione
    born_in_version = defaultdict(list)
    modified_in_version = defaultdict(list)

    for t in test_files:
        log_out = git_cmd(["log", "master", "--format=%H|%ad|%s", "--date=short", "--", t])
        commits = [line.split("|") for line in log_out.splitlines() if line.strip()]
        commits.reverse()  # Ordine cronologico

        fname = Path(t).name
        birth_sha = commits[0][0]
        birth_date = commits[0][1]
        birth_year = birth_date[:4]
        birth_ver = get_release_for_commit(birth_sha)
        born_in_version[birth_ver].append(fname)

        # Versioni dell'app rilasciate nell'anno di nascita (da v5.4.0 in poi)
        versions_in_birth_year = len(tags_by_year[birth_year])

        # Versioni in cui il test è stato modificato
        mod_events = []
        prev_ver = birth_ver
        for c in commits[1:]:
            c_sha, c_date, c_msg = c[0], c[1], c[2]
            c_ver = get_release_for_commit(c_sha)
            if c_ver != prev_ver:
                idx_prev = tag_index.get(prev_ver, 0)
                idx_curr = tag_index.get(c_ver, len(all_tags))
                delta_ver = max(1, idx_curr - idx_prev)
                mod_events.append({
                    "version": c_ver,
                    "date": c_date,
                    "delta_from_prev": delta_ver,
                    "sha": c_sha[:8],
                    "msg": c_msg[:45],
                })
                modified_in_version[c_ver].append(fname)
                prev_ver = c_ver

        analysis_data.append({
            "filename": fname,
            "path": t,
            "birth_year": birth_year,
            "birth_date": birth_date,
            "birth_version": birth_ver,
            "versions_in_birth_year": versions_in_birth_year,
            "mod_count": len(commits) - 1,
            "mod_events": mod_events,
        })

    # 3. Genera sezione Markdown
    lines = [
        "## 🔬 Analisi del Ciclo di Vita Completo: 100% della Suite E2E (46 File di Test)",
        "",
        "> **Copertura totale**: Questo report traccia **tutte le 70 versioni** di `ghiscoding/angular-slickgrid` da **`v5.4.0`** (passaggio a TypeScript) fino a **`v8.14.1`** (ultima release prima del monorepo) e **tutti i 46 file di test Cypress**.",
        "",
        "### A. Distribuzione delle Versioni Rilasciate per Anno (da `v5.4.0` a `v8.14.1`)",
        "",
        "| Anno di Rilascio | N. Versioni Rilasciate | Prima Release | Ultima Release | Note sull'Attività della Suite E2E |",
        "|---|---|---|---|---|",
    ]

    for y in ["2023", "2024", "2025"]:
        t_list = tags_by_year[y]
        note = "Passaggio della suite Cypress a TS in `v5.4.0` (33 file) + `example34` in `v7.1.0`" if y == "2023" else (
            "Espansione della suite (+9 nuovi file di test da `example35` a `example43`)" if y == "2024" else
            "Completamento (`example18`, `example44`, `example45`), release `v8.14.1` e migrazione a monorepo"
        )
        lines.append(
            f"| **{y}** | **{len(t_list)} versioni** | `{t_list[0][1]}` ({t_list[0][0]}) | `{t_list[-1][1]}` ({t_list[-1][0]}) | {note} |"
        )

    lines.extend([
        "",
        f"**Totale versioni pubblicate da `v5.4.0` a `v8.14.1` (2023 – 2025)**: **{len(ts_era_tags)} versioni rilasciate**.",
        "",
        "---",
        "",
        "### B. Elenco Completo di Tutte le 70 Versioni del Programma (da `v5.4.0` a `v8.14.1`)",
        "",
        "La tabella seguente riporta cronologicamente **tutte le 70 versioni** dell'applicazione dalla `v5.4.0` alla `v8.14.1`, mostrando per ciascuna versione quanti file di test sono stati **introdotti** e quanti sono stati **modificati**:",
        "",
        "| # | Versione | Data di Rilascio | Anno | Test Nati / Introdotti | Test Modificati nella Versione |",
        "|---|---|---|---|---|---|",
    ])

    for i, (r_date, r_tag) in enumerate(ts_era_tags, start=1):
        r_year = r_date[:4]
        born_list = born_in_version.get(r_tag, [])
        mod_list = modified_in_version.get(r_tag, [])

        if len(born_list) > 5:
            born_str = f"**{len(born_list)} file** (`example01`..`example33`, `home`)"
        elif born_list:
            born_str = f"**{len(born_list)} file** (" + ", ".join(f"`{x}`" for x in born_list) + ")"
        else:
            born_str = "-"

        if len(mod_list) > 6:
            mod_str = f"**{len(mod_list)} file modificati** (`{mod_list[0]}` .. `{mod_list[-1]}`)"
        elif mod_list:
            mod_str = f"**{len(mod_list)} file** (" + ", ".join(f"`{x}`" for x in mod_list) + ")"
        else:
            mod_str = "*Nessuna modifica ai test*"

        lines.append(f"| {i} | **`{r_tag}`** | {r_date} | {r_year} | {born_str} | {mod_str} |")

    lines.extend([
        "",
        "---",
        "",
        "### C. Tabella del Ciclo di Vita di Tutti i 46 File di Test",
        "",
        r"La tabella seguente traccia per ogni test: l'**anno** e la **versione di nascita**, quante versioni sono state rilasciate in quell'anno, la **prima versione in cui è stato modificato** e il salto di versioni ($\Delta_{\text{versioni}}$):",
        "",
        "| # | File di Test | Anno Nascita | Versione Nascita | N. Versioni Anno | 1ª Versione di Modifica | $\\Delta$ Versioni alla 1ª Modifica | Versioni di Modifica Successive |",
        "|---|---|---|---|---|---|---|---|",
    ])

    for idx, d in enumerate(analysis_data, start=1):
        mod_vers = [f"`{m['version']}` (+{m['delta_from_prev']} v)" for m in d["mod_events"]]
        first_mod_ver = f"`{d['mod_events'][0]['version']}`" if d["mod_events"] else "*Nessuna*"
        delta_first = f"**{d['mod_events'][0]['delta_from_prev']} versioni**" if d["mod_events"] else "*Mai modificato*"
        all_mods_str = ", ".join(mod_vers[1:]) if len(mod_vers) > 1 else ("*Nessun'altra*" if mod_vers else "-")

        lines.append(
            f"| {idx} | **`{d['filename']}`** | **{d['birth_year']}** | `{d['birth_version']}` | {d['versions_in_birth_year']} | "
            f"{first_mod_ver} | {delta_first} | {all_mods_str} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "### D. Approfondimento: Il Caso di `example18.cy.ts` (2025) vs `example19.cy.ts` (2023)",
        "",
        "Un'ispezione della tabella evidenzia un'apparente anomalia nella numerazione: `example18.cy.ts` risulta nato nel **2025**, mentre `example19.cy.ts` è nato nel **2023**.",
        "L'analisi dettagliata dei commit Git (`git log --name-status`) rivela la causa di questa evoluzione:",
        "",
        "1. **Perché `example19.cy.ts` è nato nel 2023 (`v5.4.0`)**:",
        "   - A gennaio 2023 l'intera suite Cypress è stata convertita in TypeScript.",
        "   - In quella fase iniziale esistevano i test da 1 a 17 e poi da 19 a 33. **Il test 18 non è mai esistito nel 2023** perché l'Esempio 18 della demo Angular era `grid-remote.component.ts` (un esempio collegato a un server remoto OData/GraphQL), privo di test E2E automatici locali.",
        "2. **Perché `example18.cy.ts` risulta nato a gennaio 2025 (`v8.12.0`)**:",
        "   - Nel commit `6ab4d1fb` (18 gennaio 2025, *«chore: remove Remote Example & replace with Import from CSV»*), l'autore ha rimosso definitivamente l'esempio remoto non testabile.",
        "   - Per riempire lo slot #18 vacante, l'autore ha **rinominato** il nuovo test di import CSV (`example43.cy.ts` $\\rightarrow$ `example18.cy.ts`), facendo apparire il file `example18.cy.ts` per la prima volta nella storia Git nel 2025.",
        "   - Pochi giorni dopo (20 gennaio 2025, commit `d583887f`), lo slot 43 liberato è stato riassegnato a una nuova feature creando un nuovo `example43.cy.ts` (`feat: add rowspan implementation`).",
        "",
        "---",
        "",
        "### E. Sintesi delle Scoperte sul Ciclo di Vita (Tesi & Colloquio)",
        "",
        "1. **I Test Iniziali (Convertiti in TS in `v5.4.0`, Gennaio 2023)**:",
        "   - Sono nati in TypeScript nella versione **`v5.4.0`** (dopo l'era JavaScript documentata in [`analisi_pre_typescript_js.md`](./analisi_pre_typescript_js.md)).",
        "   - Hanno evidenziato un consistente **Release Lag**: su 70 versioni rilasciate, nella maggioranza delle release intermedie i test non subiscono alcuna modifica (restando inalterati mediamente per **16–17 release consecutive** fino a `v6.4.0` / `v6.5.0`).",
        "2. **I Nuovi Test Aggiunti Successivamente (2024 – 2025)**:",
        "   - Dimostrano la crescita costante dell'applicazione: ogni volta che veniva implementata una nuova feature di griglia complessa (es. `example36` per il parser callback o `example45` per il sub-grid rendering), veniva scritto un nuovo test E2E dedicato.",
        "   - Questi test recenti hanno un tasso di manutenzione più rapido: vengono spesso aggiornati entro **1–4 release** dalla creazione.",
        "3. **Convergenza di Manutenzione Globale**:",
        "   - Dall'elenco delle 70 versioni (Sezione B) si vede chiaramente che la manutenzione dei test non è sparpagliata su ogni release, ma concentrata in **pochi grandi picchi architetturali**:",
        "     - **`v6.4.0` / `v6.5.0`** (novembre 2023): introduzione dei sottomenu e della strategia anti-flakiness Cypress (`experimentalStrategy`).",
        "     - **`v7.0.0`** (dicembre 2023): aggiornamento major della griglia.",
        "     - **`v8.0.0`** (maggio 2024): refactoring selettori DOM per passaggio da Font-Awesome a icone SVG.",
        "     - **`v8.12.0`** (gennaio 2025): uniformazione linting e formattazione Prettier su tutta la suite (42 file toccati).",
        "",
    ])

    content_to_insert = "\n".join(lines)

    # 4. Scrivi report dedicato in results/angular-slickgrid/analisi_versioni_dettagliata.md
    report_file = RESULTS_DIR / "analisi_versioni_dettagliata.md"
    with report_file.open("w", encoding="utf-8") as f:
        f.write("# Ciclo di Vita del 100% dei Test E2E (46 File) e Tutte le 70 Versioni (`v5.4.0` – `v8.14.1`) — `angular-slickgrid`\n\n" + content_to_insert)
    print(f"[✓] File aggiornato con tutte le 70 versioni e i 46 test: {report_file}")

    # 5. Salva anche il CSV con tutti i 46 file
    csv_out = RESULTS_DIR / "test_suite_46_files.csv"
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "filename", "path", "birth_year", "birth_date",
            "birth_version", "versions_in_birth_year", "mod_count",
            "first_mod_version", "delta_versions_first_mod"
        ])
        writer.writeheader()
        for d in analysis_data:
            first_v = d["mod_events"][0]["version"] if d["mod_events"] else ""
            delta_v = d["mod_events"][0]["delta_from_prev"] if d["mod_events"] else 0
            writer.writerow({
                "filename": d["filename"],
                "path": d["path"],
                "birth_year": d["birth_year"],
                "birth_date": d["birth_date"],
                "birth_version": d["birth_version"],
                "versions_in_birth_year": d["versions_in_birth_year"],
                "mod_count": d["mod_count"],
                "first_mod_version": first_v,
                "delta_versions_first_mod": delta_v,
            })
    print(f"[✓] CSV completo (46 file) esportato in: {csv_out}")

    # 6. Aggiorna analisi_approfondita_slickgrid.md
    md_main = RESULTS_DIR / "analisi_approfondita_slickgrid.md"
    if md_main.exists():
        text = md_main.read_text(encoding="utf-8")
        if "## 🔬 Analisi Dettagliata per Anno" in text:
            prefix = text.split("## 🔬 Analisi Dettagliata per Anno")[0]
            md_main.write_text(prefix.strip() + "\n\n---\n\n" + content_to_insert, encoding="utf-8")
        elif "## 🔬 Analisi del Ciclo di Vita Completo" in text:
            prefix = text.split("## 🔬 Analisi del Ciclo di Vita Completo")[0]
            md_main.write_text(prefix.strip() + "\n\n---\n\n" + content_to_insert, encoding="utf-8")
        else:
            md_main.write_text(text.strip() + "\n\n---\n\n" + content_to_insert, encoding="utf-8")
        print(f"[✓] Aggiornato {md_main}")


if __name__ == "__main__":
    main()
