# Analisi Manutenzione, Diff e Flakiness — `ghiscoding/angular-slickgrid`

> Studio empirico delle modifiche post-snapshot E2EGit ($t_0$ = Marzo 2024, `5eafe04c54`), delle cause di manutenzione dei test e della gestione della *flakiness*.

---

## 1. Confronto Temporale: Snapshot Dataset ($t_0$) vs Stato Attuale (HEAD)

| Dimensione | Snapshot Dataset ($t_0$, Marzo 2024) | Stato Attuale su GitHub (HEAD) | Delta / Crescita |
|---|---|---|---|
| **Commit SHA** | `5eafe04c5494c52eb46e3174883625c0d1f41a4d` | `c82fdbae` (HEAD) | **+610 commit** |
| **Commit Totali Applicazione** | 3.854 | 4.464 | **+15.8%** |
| **File di Test E2E Cypress** | **35 file** (`example01` $\rightarrow$ `example35`) | **46 file** (`example01` $\rightarrow$ `example45`) | **+11 nuovi file** (+31.4%) |
| **Test Case Singoli (`it(...)`)** | **658 test** | **858 test** | **+200 test case** (+30.4%) |
| **Tasso di Sopravvivenza** | - | **100%** (46/46 file presenti) | Nessun test rimosso |

### Distribuzione delle Modifiche Post-Snapshot ($t_0 \rightarrow$ HEAD sui 35 file originali)
| Natura del Cambiamento | Numero File Coinvolti | Percentuale |
|---|---|---|
| **`cambio_asserzioni`** | 33 | 94.3% |
| **`cambio_selettori`** | 2 | 5.7% |

---

## 2. Tabella dei Diff Post-Snapshot ($t_0 \rightarrow$ HEAD) sui 35 File del Dataset

| # | File di Test | Data Nascita TS | Commit Nascita TS | Mod. Totali | Mod. post-$t_0$ ($N_{\text{mod}}$) | Diff post-$t_0$ | Righe +/- |
|---|---|---|---|---|---|---|---|
| 1 | **`example01.cy.ts`** | 2023-01-27 | `749aaf15` | 6 | **2** | `cambio_asserzioni` | +47/-111 |
| 2 | **`example02.cy.ts`** | 2023-01-27 | `749aaf15` | 5 | **2** | `cambio_asserzioni` | +40/-5 |
| 3 | **`example03.cy.ts`** | 2023-01-27 | `749aaf15` | 9 | **2** | `cambio_asserzioni` | +81/-63 |
| 4 | **`example04.cy.ts`** | 2023-01-27 | `749aaf15` | 11 | **8** | `cambio_asserzioni` | +97/-46 |
| 5 | **`example05.cy.ts`** | 2023-01-27 | `749aaf15` | 11 | **6** | `cambio_asserzioni` | +316/-445 |
| 6 | **`example06.cy.ts`** | 2023-01-27 | `749aaf15` | 17 | **10** | `cambio_asserzioni` | +370/-268 |
| 7 | **`example07.cy.ts`** | 2023-01-27 | `749aaf15` | 6 | **3** | `cambio_asserzioni` | +127/-157 |
| 8 | **`example08.cy.ts`** | 2023-01-27 | `749aaf15` | 5 | **2** | `cambio_asserzioni` | +14/-31 |
| 9 | **`example09.cy.ts`** | 2023-01-27 | `749aaf15` | 4 | **1** | `cambio_asserzioni` | +34/-118 |
| 10 | **`example10.cy.ts`** | 2023-01-27 | `749aaf15` | 6 | **2** | `cambio_asserzioni` | +214/-445 |
| 11 | **`example11.cy.ts`** | 2023-01-27 | `749aaf15` | 5 | **1** | `cambio_asserzioni` | +10/-27 |
| 12 | **`example12.cy.ts`** | 2023-01-27 | `749aaf15` | 8 | **2** | `cambio_asserzioni` | +50/-106 |
| 13 | **`example13.cy.ts`** | 2023-01-27 | `749aaf15` | 4 | **2** | `cambio_asserzioni` | +19/-26 |
| 14 | **`example14.cy.ts`** | 2023-01-27 | `749aaf15` | 7 | **4** | `cambio_asserzioni` | +175/-21 |
| 15 | **`example15.cy.ts`** | 2023-01-27 | `749aaf15` | 4 | **1** | `cambio_selettori` | +4/-9 |
| 16 | **`example16.cy.ts`** | 2023-01-27 | `749aaf15` | 9 | **3** | `cambio_asserzioni` | +148/-108 |
| 17 | **`example17.cy.ts`** | 2023-01-27 | `749aaf15` | 8 | **2** | `cambio_asserzioni` | +68/-70 |
| 18 | **`example19.cy.ts`** | 2023-01-27 | `749aaf15` | 7 | **4** | `cambio_asserzioni` | +284/-57 |
| 19 | **`example20.cy.ts`** | 2023-01-27 | `749aaf15` | 5 | **1** | `cambio_asserzioni` | +85/-42 |
| 20 | **`example21.cy.ts`** | 2023-01-27 | `749aaf15` | 12 | **6** | `cambio_asserzioni` | +81/-160 |
| 21 | **`example22.cy.ts`** | 2023-01-27 | `749aaf15` | 5 | **1** | `cambio_asserzioni` | +26/-31 |
| 22 | **`example23.cy.ts`** | 2023-01-27 | `749aaf15` | 4 | **1** | `cambio_selettori` | +11/-24 |
| 23 | **`example24.cy.ts`** | 2023-01-27 | `749aaf15` | 5 | **1** | `cambio_asserzioni` | +25/-8 |
| 24 | **`example25.cy.ts`** | 2023-01-27 | `749aaf15` | 12 | **6** | `cambio_asserzioni` | +42/-43 |
| 25 | **`example26.cy.ts`** | 2023-01-27 | `749aaf15` | 6 | **2** | `cambio_asserzioni` | +182/-377 |
| 26 | **`example27.cy.ts`** | 2023-01-27 | `749aaf15` | 4 | **1** | `cambio_asserzioni` | +40/-57 |
| 27 | **`example28.cy.ts`** | 2023-01-27 | `749aaf15` | 5 | **1** | `cambio_asserzioni` | +68/-129 |
| 28 | **`example29.cy.ts`** | 2023-01-27 | `749aaf15` | 6 | **1** | `cambio_asserzioni` | +464/-224 |
| 29 | **`example30.cy.ts`** | 2023-01-27 | `749aaf15` | 13 | **6** | `cambio_asserzioni` | +270/-114 |
| 30 | **`example31.cy.ts`** | 2023-01-27 | `749aaf15` | 9 | **4** | `cambio_asserzioni` | +221/-136 |
| 31 | **`example32.cy.ts`** | 2023-01-27 | `749aaf15` | 11 | **7** | `cambio_asserzioni` | +64/-39 |
| 32 | **`example33.cy.ts`** | 2023-01-27 | `749aaf15` | 6 | **2** | `cambio_asserzioni` | +29/-14 |
| 33 | **`example34.cy.ts`** | 2023-12-19 | `5aa8bb16` | 1 | **1** | `cambio_asserzioni` | +3/-5 |
| 34 | **`example35.cy.ts`** | 2024-01-20 | `1f768a57` | 3 | **3** | `cambio_asserzioni` | +52/-36 |
| 35 | **`home.cy.ts`** | 2023-01-27 | `749aaf15` | 3 | **2** | `cambio_asserzioni` | +1/-6 |

---

## 3. Tassonomia delle Cause di Modifica del Codice di Test

1. **Sostituzione Icone e Selettori DOM (`v8.0.0`)**:
   - Commit `d73cc9c9`: *«feat!: remove Font-Awesome and use new SVG icons»*.
   - L'eliminazione dei tag `<i>` con classi Font-Awesome a favore di tag `<svg>` in linea ha reso obsoleti i selettori CSS precedenti, costringendo lo sviluppatore ad aggiornare i test.
2. **Sostituzione Componenti UI di Terze Parti**:
   - Passaggio da `Flatpickr` a `Vanilla-Calendar` (commit `109f155e`) e da `Moment.js` a `Tempo` (commit `a27b6e9c`), che ha comportato modifiche alle interazioni con i widget calendario nei test `example04.cy.ts`.
3. **Migrazione a TypeScript (`v5.4.0`)**:
   - Commit `749aaf15`: *«chore: migrate all Cypress tests to TypeScript»*.
4. **Uniformazione Linting e Formattazione (`v8.12.0`)**:
   - Introduzione di regole Prettier/ESLint uniformi su tutta la suite (42 file toccati contemporaneamente).

---

## 4. Gestione della *Flakiness* in `cypress.config.ts`

1. **Versioni `v5.4.0` – `v6.4.0`**:
   ```typescript
   retries: {
     runMode: 2,
     openMode: 0,
   }
   ```
2. **Versioni `v6.5.0+` (Strategia sperimentale di Cypress)**:
   ```typescript
   retries: {
     experimentalStrategy: 'detect-flake-and-pass-on-threshold',
     experimentalOptions: {
       maxRetries: 2,
       passesRequired: 1,
     },
     openMode: false,
     runMode: true,
   }
   ```
   - Inoltre, i test utilizzano `testIsolation: false` (ogni blocco `it()` prosegue sullo stato DOM lasciato dal test precedente). Durante l'esecuzione dinamica in Docker su Angular 16 (`v6.0.0+`), questo ha evidenziato come il salvataggio di uno screenshot su disco al 1° tentativo fallito possa innescare il *file-watcher* di `ng serve` (`Reloading client(s)...`), azzerando lo stato della pagina e causando fallimenti a catena se non si disabilitano gli screenshot (`--config screenshotOnRunFailure=false`).

