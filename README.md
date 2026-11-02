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
│   ├── letteratura/                      # Paper originali e tradotti (MSR 2025, IST 2025, ecc.)
│   └── archivio/                         # Documentazione preliminare (confronto iniziale Prog1/Prog2)
├── src/                        # Pipeline di script Python
│   ├── 01_estrai_repository.py # Estrazione dati dal DB e generazione CSV
│   └── 02_storia_test.py       # Analisi della storia Git e co-evoluzione dei test
├── results/                    # Risultati dell'analisi ed estratti CSV
├── ricevimenti/                # Verbali e appunti degli incontri con il professore
│   ├── ProgTirocinio.txt                 # Traccia iniziale del docente
│   ├── PrimoRicevimentoStarace.txt       # Appunti ricevimento (titolo e obiettivi fissati)
│   └── Domande_Primo_Ricevimento.md      # Domande discusse nel primo incontro
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
