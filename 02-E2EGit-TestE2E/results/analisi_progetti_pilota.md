# Analisi del Ciclo di Vita — Progetti Pilota (Cypress & Playwright)

> Studio empirico condotto su 2 repository pilota selezionati dalla Top 20 di `E2EGit`:
> 1. **`ghiscoding/angular-slickgrid`** (Suite **Cypress**)
> 2. **`epam/ketcher`** (Suite **Playwright**)

---

## Repository: `ghiscoding/angular-slickgrid` (Cypress)
- **Linguaggio**: TypeScript
- **Snapshot Dataset ($t_0$, Marzo 2024)**: `5eafe04c54`
- **Commit Totali App (a HEAD)**: 4464
- **Commit App da Snapshot a Oggi**: 610

| File di Test | Esiste a HEAD? | Nascita ($t_{\text{birth}}$) | Commit Nascita | Modifiche Totali | Modifiche post-$t_0$ ($N_{\text{mod}}$) | Note / Cause Principali di Modifica |
|---|---|---|---|---|---|---|
| `example01.cy.ts` | ✅ SÌ (stesso path) | 2023-01-27 | `749aaf15` | 6 | **2** | Migrazione a TypeScript, Risoluzione Flakiness/Attese, Aggiornamento Icone/UI, Formattazione |
| `example02.cy.ts` | ✅ SÌ (stesso path) | 2023-01-27 | `749aaf15` | 5 | **2** | Migrazione a TypeScript, Risoluzione Flakiness/Attese, Aggiornamento Icone/UI, Formattazione |
| `example03.cy.ts` | ✅ SÌ (stesso path) | 2023-01-27 | `749aaf15` | 9 | **2** | Migrazione a TypeScript, Risoluzione Flakiness/Attese, Aggiornamento Icone/UI, Correzione Test Fallito (Fix), Formattazione |
| `example04.cy.ts` | ✅ SÌ (stesso path) | 2023-01-27 | `749aaf15` | 11 | **8** | Migrazione a TypeScript, Risoluzione Flakiness/Attese, Aggiornamento Icone/UI, Correzione Test Fallito (Fix), Formattazione |
| `example05.cy.ts` | ✅ SÌ (stesso path) | 2023-01-27 | `749aaf15` | 11 | **6** | Migrazione a TypeScript, Risoluzione Flakiness/Attese, Aggiornamento Icone/UI, Correzione Test Fallito (Fix), Formattazione |

## Repository: `epam/ketcher` (Playwright)
- **Linguaggio**: TypeScript
- **Snapshot Dataset ($t_0$, Marzo 2024)**: `ebe4f8d697`
- **Commit Totali App (a HEAD)**: 7706
- **Commit App da Snapshot a Oggi**: 3080

| File di Test | Esiste a HEAD? | Nascita ($t_{\text{birth}}$) | Commit Nascita | Modifiche Totali | Modifiche post-$t_0$ ($N_{\text{mod}}$) | Note / Cause Principali di Modifica |
|---|---|---|---|---|---|---|
| `api-set-get-molecule.spec.ts` | ❌ NO (cancellato) | 2023-07-06 | `aae50caf` | 22 | **10** | Correzione Test Fallito (Fix), Refactoring test |
| `is-query-structure-selected.spec.ts` | ❌ NO (cancellato) | 2023-11-30 | `1300afbb` | 1 | **1** | Manutenzione ordinaria |
| `ketcher-api.spec.ts` | ❌ NO (cancellato) | 2023-07-06 | `aae50caf` | 3 | **1** | Correzione Test Fallito (Fix) |

---

## 💡 Risultati Chiave per il Ricevimento con il Professore

### 1. Sopravvivenza dei Test (Esistono ancora a HEAD?)
- In **`angular-slickgrid` (Cypress)**: tutti i test esistono ancora oggi nello **stesso identico percorso** di 2 anni fa.
- In **`epam/ketcher` (Playwright)**: i test esistono ancora a HEAD, ma sono stati **spostati (R100)** dalla cartella `tests/API/` a `tests/specs/API/` durante una ristrutturazione della suite (commit `e8ca2948f`). Questa scoperta dimostra l'importanza fondamentale di usare `git log --follow` anziché un controllo statico del file.

### 2. Attività di Modifica post-Snapshot ($N_{\text{mod}}$)
- In **`angular-slickgrid` (Cypress)**: tutti i 5 test hanno subito tra 2 e 8 modifiche dopo marzo 2024, confermando una manutenzione attiva e regolare.
- In **`epam/ketcher` (Playwright)**: alcuni test subiscono modifiche frequenti (es. `api-set-get-molecule.spec.ts` con oltre 10 modifiche post-snapshot), mentre altri (`is-query-structure-selected.spec.ts`) sono rimasti **congelati per oltre 1 anno e mezzo** prima del refactoring globale.

### 3. Cause Principali di Modifica (Perché sono cambiati?)
L'ispezione empirica dei messaggi di commit conferma esattamente i motori di cambiamento teorizzati:
1. **Risoluzione della *Flakiness*** (es. introduzione dell'opzione di Cypress `experimentalStrategy` e gestione retry).
2. **Cambiamenti all'interfaccia UI e librerie grafiche** (es. rimozione di Font-Awesome e passaggio a icone SVG, migrazione a Vanilla Calendar).
3. **Migrazione tecnologica** (es. migrazione da Cypress JS a TypeScript).
