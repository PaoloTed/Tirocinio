# Verbale e To-Do List — Ricevimento Martedì 3 Novembre 2026

**Progetto**: *Implementazione di un tool per l'analisi automatica di test e2e web in repository software*  
**Docente / Tutor**: Prof. Luigi Libero Lucio Starace  
**Studente**: Paolo  
**Data Ricevimento**: Martedì 3 Novembre 2026  
**Documento di riferimento**: [`PrimoRicevimentoStarace.txt`](./PrimoRicevimentoStarace.txt)

---

## 📌 Sintesi degli Orientamenti del Professore

1. **Focus tecnologico**: Progetti in ecosistema **Node.js / JavaScript / TypeScript** con test E2E GUI (Cypress, Playwright, Puppeteer, Selenium).
2. **Ciclo di vita del test (Test Lifecycle)**:
   - Capire quando nasce un test (commit di introduzione).
   - Misurare quante versioni/commit dell'applicazione intercorrono tra la creazione e la prima modifica, e tra le modifiche successive.
   - Analizzare la stabilità: se e da quale versione dell'applicazione un test smette di funzionare, e se viene corretto nella versione successiva.
3. **Approccio pilota**:
   - Stilare una classifica iniziale sui 472 repository del dataset E2EGit.
   - Partire con l'analisi approfondita di **2–3 progetti campione**.
4. **Nota metodologica su Docker**:
   - Valutare con cautela l'esecuzione automatica in container Dockerfile per versioni storiche (*«DA VEDERE SE FARLO FORSE TROPPO DIFFICILE»*): privilegiare il mining statico della storia Git rispetto a setup di ambienti troppo fragili o bloccanti.

---

## 📋 Checklist Operativa (Cosa preparare per il colloquio)

### 1. Filtraggio e Ranking dei Repository E2EGit (Priorità 1) — ✅ COMPLETATO
- [x] **Query sul database `E2EGit.db`**:
  - Filtrati i repository Node.js / JS / TS con test GUI tramite [`src/03_filtra_node_ranking.py`](../src/03_filtra_node_ranking.py).
- [x] **Ordinamento secondo i criteri discussi**:
  - Progetti con il **maggior numero di test E2E**.
  - Progetti con **alta attività** (elevato numero di commit e contributor).
- [x] **Generazione della lista candidati (Top 20)**:
  - Generata la tabella in [`results/top_node_repositories.md`](../results/top_node_repositories.md) e [`results/top_node_repositories.csv`](../results/top_node_repositories.csv).

---

### 2. Formalizzazione delle Metriche sul Ciclo di Vita dei Test (Priorità 2) — ✅ COMPLETATO
- [x] **Definire la timeline di evoluzione del test**:
  - Formalizzato il modello matematico e operativo in [`docs/04_metriche_ciclo_di_vita.md`](../docs/04_metriche_ciclo_di_vita.md).
  - **$t_{\text{birth}}$**: Commit e data di introduzione del file di test.
  - **$\Delta_{\text{first\_mod}}$**: Numero di commit dell'applicazione prima della 1ª manutenzione.
  - **$N_{\text{mod}}$**: Modifiche subite da $t_0$ (marzo 2024) a HEAD (oggi).
- [x] **Classificare la natura delle modifiche**:
  - Implementata la tassonomia con Regex per *cambio_selettori*, *cambio_asserzioni*, *cambio_wait*, *riformattazione*.
  - Sviluppato lo script di estrazione cronologica: [`src/04_analizza_ciclo_vita.py`](../src/04_analizza_ciclo_vita.py).

---

### 3. Selezione di 2–3 Progetti Pilota (Priorità 3) — ✅ COMPLETATO
- [x] **Individuati i 2 repository pilota**:
  - **`ghiscoding/angular-slickgrid`** per **Cypress** (TypeScript, 35 file, 658 test, 4.464 commit).
  - **`epam/ketcher`** per **Playwright** (TypeScript, 169 file, 2.154 test, 7.706 commit).
- [x] **Estratta la storia Git di un campione di test**:
  - Tracciati 5 file di test Cypress e 3 file Playwright con [`src/05_estrai_campione_pilota.py`](../src/05_estrai_campione_pilota.py).
  - Generato il report empirico completo in [`results/analisi_progetti_pilota.md`](../results/analisi_progetti_pilota.md) e [`results/analisi_progetti_pilota.csv`](../results/analisi_progetti_pilota.csv).
  - Dimostrato che i test sopravvivono a HEAD (anche tramite rename/migrazione `R100`) e che i cambi sono guidati da *flakiness*, aggiornamenti UI e TypeScript.

---

### 4. Valutazione Tecnica su Docker ed Esecuzione Dinamica (Priorità 4) — ✅ COMPLETATO
- [x] **Ispezione tecnica dei progetti pilota**:
  - Verificato che i repository storici soffrono di *dependency rot* su NPM e richiedono configurazioni esterne complesse, tranne casi particolari con demo standalone come `angular-slickgrid`.
- [x] **Valutazione metodologica formalizzata**:
  - Redatto il documento di analisi scientifica e fattibilità in [`docs/05_valutazione_docker_esecuzione_dinamica.md`](../docs/05_valutazione_docker_esecuzione_dinamica.md).
  - Dimostrata la superiorità del **Git Mining Statico** come motore universale (100% di copertura deterministica sui 472 repository).
  - Proposta al professore un'**architettura ibrida (Tier 1 Git Mining + Tier 2 Docker Runner sperimentale)**.
- [x] **Prototipo Docker funzionante**:
  - Creati [`docker/angular-slickgrid/Dockerfile`](../docker/angular-slickgrid/Dockerfile) e lo script di esecuzione parametrico per versione [`docker/angular-slickgrid/run_version_test.sh`](../docker/angular-slickgrid/run_version_test.sh).

---

## 💼 Materiale da Portare al Ricevimento
1. **Classifica Top 20 Repository Node.js** estratta con SQL da `E2EGit.db`: [`results/top_node_repositories.md`](../results/top_node_repositories.md).
2. **Formalizzazione Matematica delle Metriche di Ciclo di Vita**: [`docs/04_metriche_ciclo_di_vita.md`](../docs/04_metriche_ciclo_di_vita.md).
3. **Analisi Comparativa dei 2 Progetti Pilota** (Cypress vs Playwright): [`results/analisi_progetti_pilota.md`](../results/analisi_progetti_pilota.md).
4. **Dossier di Dettaglio sul 100% dei Test di `angular-slickgrid`** (46 test su 71 versioni): [`results/angular-slickgrid/analisi_versioni_dettagliata.md`](../results/angular-slickgrid/analisi_versioni_dettagliata.md).
5. **Dossier di Valutazione Docker e Architettura del Tool**: [`docs/05_valutazione_docker_esecuzione_dinamica.md`](../docs/05_valutazione_docker_esecuzione_dinamica.md).

