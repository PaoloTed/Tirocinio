# Tirocinio — Implementazione di un tool per l'analisi automatica di test e2e web in repository software

**Studente**: Paolo  
**Università**: Università degli Studi di Napoli Federico II  
**Docente / Tutor**: Prof. Luigi Libero Lucio Starace  
**Progetto**: Analisi empirica ed evoluzione dei test End-to-End (E2E) sul dataset **E2EGit**.

---

## 📁 Struttura del Progetto

Il codice, i dati e la documentazione del tirocinio sono organizzati all'interno della cartella [`02-E2EGit-TestE2E/`](02-E2EGit-TestE2E/):

```text
02-E2EGit-TestE2E/
├── Guida-Prog2-E2EGit.md       # Guida operativa completa e roadmap del progetto
├── data/                       # Dataset SQLite (E2EGit.db ~2.3GB), liste dipendenze e CSV
├── docs/                       # Documentazione tecnica, paper scientifici e schemi
│   ├── Metodologia_e_Concetti_Chiave.md  # Metodologia PyDriller, clone parziale e flakiness
│   ├── diagramma_metodologia.svg         # Diagramma di flusso a 4 fasi
│   ├── 02_schema.md                      # Schema delle tabelle SQLite
│   ├── 03_dizionario_csv.md              # Dizionario dei campi CSV estratti
│   ├── 04_metriche_ciclo_di_vita.md      # Formalizzazione matematica del ciclo di vita dei test
│   ├── 05_valutazione_docker_esecuzione_dinamica.md # Mining Git vs Docker (Tier 1 vs Tier 2)
│   ├── letteratura/                      # Paper originali e tradotti (MSR 2025, IST 2025, ecc.)
│   └── archivio/                         # Documentazione preliminare (confronto iniziale Prog1/Prog2)
├── docker/                     # Ambienti containerizzati per riesecuzione dinamica
│   └── angular-slickgrid/      # Dockerfile Cypress headless + script run_version_test.sh
├── src/                        # Pipeline di script Python
│   ├── 01_estrai_repository.py # Estrazione dati dal DB e generazione CSV
│   ├── 02_storia_test.py       # Analisi della storia Git e co-evoluzione dei test
│   ├── 03_filtra_node_ranking.py # Ranking progetti Node.js (JS/TS) per test e commit
│   ├── 04_analizza_ciclo_vita.py # Ricostruzione timeline ed evoluzione dei singoli test
│   ├── 05_estrai_campione_pilota.py # Estrazione empirica per i progetti pilota (Cypress & Playwright)
│   ├── 06_approfondimento_slickgrid.py # Ispezione architettura suite Cypress
│   ├── 07_analizza_versioni_test.py # Tracciamento 46 test nell'Era TypeScript (2023-2025)
│   └── 08_analizza_era_javascript.py # Tracciamento 33 test nell'Era JavaScript (2019-2023)
├── results/                    # Risultati dell'analisi ed estratti CSV
│   ├── top_node_repositories.md  # Classifica Top 20 progetti Node.js
│   ├── analisi_progetti_pilota.md # Studio del ciclo di vita su 8 test pilota
│   └── angular-slickgrid/        # Dossier approfondito sul progetto pilota Cypress
│       ├── README.md             # Studio completo (2024 vs 2026, flakiness, Docker)
│       ├── analisi_approfondita_slickgrid.md # Analisi architetturale e correlazione versioni
│       ├── analisi_pre_typescript_js.md      # Tabella Era JavaScript (2019-2023, fino a v5.4.0)
│       ├── analisi_versioni_dettagliata.md   # Tabella Era TypeScript (2023-2025, da v5.4.0 a v8.14.1)
│       ├── test_suite_33_js_era.csv # Metriche sui 33 test nell'Era JavaScript (2019-2023)
│       ├── test_suite_35_files.csv  # Metriche sui 35 file di test Cypress storici
│       └── test_suite_46_files.csv  # Dataset completo 46 file a HEAD (v8.14.1)
├── ricevimenti/                # Verbali e appunti degli incontri con il professore
│   ├── ProgTirocinio.txt                 # Traccia iniziale del docente
│   ├── PrimoRicevimentoStarace.txt       # Appunti ricevimento (titolo e obiettivi fissati)
│   ├── Domande_Primo_Ricevimento.md      # Domande discusse nel primo incontro
│   └── TODO_Ricevimento_Martedi_3.md     # Checklist e piano operativo per martedì 3
└── burocrazia_tirocinio/       # Modulistica Unina (progetto formativo, convenzioni, guide)
```

---

## 🚀 Avvio Rapido

### 1. Database E2EGit
Il database `E2EGit.db` (~2,3 GB) è memorizzato in `02-E2EGit-TestE2E/data/E2EGit.db` (escluso dal versionamento Git tramite `.gitignore`).

### 2. Estrazione Metadati
```bash
cd 02-E2EGit-TestE2E
python3 src/01_estrai_repository.py
```

### 3. Analisi della Storia Git dei Test
```bash
cd 02-E2EGit-TestE2E
python3 src/02_storia_test.py --limit 5
```
