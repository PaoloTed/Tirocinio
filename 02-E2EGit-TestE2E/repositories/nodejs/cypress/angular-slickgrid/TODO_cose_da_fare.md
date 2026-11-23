# Checklist Operativa: Cosa Fare per Analizzare una Repository E2E

Questa checklist definisce tutti i passaggi standard (analisi statica Git + esecuzione dinamica Docker) da applicare a ogni repository selezionata dal dataset `E2EGit`.

---

## Fase 1 — Preparazione e Struttura Cartelle
- [x] **1.1 Creazione struttura unificata** in `repositories/<nome-repo>/`:
  - `repo/` (clone Git del progetto)
  - `docker/` (Dockerfile per epoca + script di esecuzione parallela)
  - `results/` (report Markdown, tabelle CSV e sottocartella `logs/`)
- [x] **1.2 Clonazione completa di tag e storia Git**:
  - Verificare che tutti i tag di versione siano presenti (`git tag --sort=creatordate`).

---

## Fase 2 — Storico delle Versioni della Repository (`results/01_versioni_repository.md`)
- [x] **2.1 Individuazione dei punti di svolta architetturali**:
  - Trovare il primo commit/versione assoluta in cui sono stati introdotti i test E2E.
  - Identificare eventuali transizioni di linguaggio o struttura (es. passaggio da JavaScript `.js` a TypeScript `.ts`, cambio versione major di Cypress/Playwright, passaggio a monorepo).
- [x] **2.2 Tabella di riepilogo annuale delle release**:
  - Raggruppare le versioni per anno solare con numero di release, prima/ultima release dell'anno e numero di nuovi test introdotti.
- [x] **2.3 Elenco cronologico completo di tutte le versioni**:
  - Per ogni versione rilasciata (sia era JS che era TS), indicare data, anno, file di test nati e file di test modificati.

---

## Fase 3 — Ciclo di Vita dei Singoli Test (`results/02_ciclo_vita_test.md` + `.csv`)
- [x] **3.1 Tracciamento delle ridenominazioni storiche**:
  - Seguire ogni file di test attraverso i cambi di cartella o estensione (es. `cypress/integration/*.spec.js` $\rightarrow$ `test/cypress/e2e/*.cy.js` $\rightarrow$ `*.cy.ts`).
- [x] **3.2 Calcolo metriche del ciclo di vita per ogni file di test**:
  - Anno, data e versione esatta di nascita.
  - Numero di versioni dell'applicazione rilasciate nell'anno di nascita.
  - Prima versione in cui il test è stato modificato e calcolo del **Release Lag** ($\Delta_{\text{versioni}}$ tra nascita e 1ª modifica).
  - Elenco di tutte le versioni successive in cui il test è stato aggiornato.
- [x] **3.3 Analisi delle anomalie sulla numerazione o sui file**:
  - Verificare eventuali buchi nella numerazione o sostituzioni di test (es. il caso `example18.cy.ts` nato nel 2025 da ridenominazione di `example43.cy.ts`).
- [x] **3.4 Esportazione dei dataset CSV**:
  - `ciclo_vita_test_javascript.csv` e `ciclo_vita_test_typescript.csv`.

---

## Fase 4 — Manutenzione, Diff e Flakiness (`results/03_manutenzione_e_flakiness.md`)
- [x] **4.1 Confronto Snapshot Dataset ($t_0$) vs Stato Attuale (`HEAD`)**:
  - Calcolare il tasso di sopravvivenza dei test presenti nel dataset, il numero di nuovi file di test aggiunti e il totale dei blocchi `it(...)` / `test(...)`.
- [x] **4.2 Analisi dei Diff e delle cause di modifica**:
  - Contare righe aggiunte/rimosse (`+`/`-`) e classificare il tipo di modifica (`cambio_asserzioni`, `cambio_selettori`, `cambio_wait`).
  - Ispezionare i commit principali per capire il motivo reale delle modifiche ai test (es. cambio librerie icone/calendari, refactoring UI, regole di linting/Prettier).
- [x] **4.3 Analisi della configurazione di Flakiness e isolamento**:
  - Controllare `cypress.config.*` o `playwright.config.*` per vedere se gli sviluppatori usano `retries` automatici, `experimentalStrategy` anti-flake o `testIsolation: false`.

---

## Fase 5 — Containerizzazione Docker Ottimizzata (`docker/`)
- [x] **5.1 Scelta delle immagini base per epoca**:
  - Verificare versione di Node.js e architettura dei `package.json` nelle diverse versioni storiche (es. `Dockerfile.v5.4-v6.4` con Node 16 e doppio `package.json` vs `Dockerfile.v6.5-v8.14` con Node 20 e `package.json` unificato).
- [x] **5.2 Ottimizzazioni di Build e Runtime**:
  - Normalizzare `"version": "0.0.0"` in `package.json` e creare `.dockerignore` per massimizzare la cache Docker.
  - Usare l'**Immagine Base Calda (`BASE_IMAGE`)** e il controllo `cmp -s` sui lockfile per evitare di reinstallare `node_modules` da zero quando le dipendenze non cambiano.
  - Saltare step inutili in fase di build (es. `ng lint`) ed escludere meta-runner duplicati (es. `000-run-all-specs.cy.ts`).
  - Disattivare video e screenshot (`--config screenshotOnRunFailure=false,video=false`) per velocizzare i test ed evitare che il salvataggio di file su disco inneschi il *live-reload* del dev-server.
- [x] **5.3 Script orchestratore multi-versione (`esegui_test_docker.sh`)**:
  - Estrazione automatica con `git worktree` in `/tmp/`, avvio parallelo nei terminali e salvataggio automatico dei log con `tee`.

---

## Fase 6 — Esecuzione Dinamica e Analisi dei Log (`results/logs/`)
- [x] **6.1 Esecuzione su sequenza di versioni storiche (es. `v5.4.0` $\rightarrow$ `v6.2.0`)**:
  - Salvataggio dei log completi in `results/logs/test_<versione>.txt`.
- [ ] **6.2 Estensione dell'esecuzione alle versioni successive (`v6.3.0` $\rightarrow$ `v8.14.1`)**:
  - Eseguire i blocchi di versioni rimanenti di interesse per completare il quadro sperimentale.
- [ ] **6.3 Tabella riassuntiva dei risultati di esecuzione (`04_risultati_esecuzione_docker.md`)**:
  - Riassumere per ogni versione testata: numero di spec totali, test passati, test falliti, durata di esecuzione e correlazione tra i fallimenti osservati e le versioni in cui i test sono stati (o non sono stati) modificati.
