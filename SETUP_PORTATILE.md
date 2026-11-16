# Guida Setup sul Portatile (Sincronizzazione dal PC Fisso)

Questo documento raccoglie tutto ciò che serve fare sul **portatile** per allinearlo con lo stato attuale del **PC fisso** (`PaoloTed/Tirocinio`).

---

## 1. Cosa arriva automaticamente con Git vs cosa va scaricato a parte

### ✅ Già incluso su GitHub (`git clone` / `git pull`)
* Tutta la documentazione (`02-E2EGit-TestE2E/docs/`, inclusi i paper in `docs/letteratura/`).
* Tutti gli script (`02-E2EGit-TestE2E/scripts/`) e le configurazioni Docker (`docker/`).
* Tutti i risultati testuali e i log generati finora (`repositories/repo_nodejs/*/results/` per `angular-slickgrid`, `equal-access`, `ketcher`, `koenig`).
* I verbali dei ricevimenti (`ricevimenti/ricevimento_1.txt`, `ricevimento_2.txt`, `ricevimento_3.txt`).
* Del pacchetto Zenodo IST 2025 (`02-E2EGit-TestE2E/data/IST2025_Zenodo/`):
  * `README.md`;
  * tutto il codice sorgente Python di `E2E-Miner-IST/` (escluso `venv/` e `.idea/`);
  * tutti i **`477`** file `RQ3/commit-analysis/*/*_tests_lifecycle_analysis.xlsx` (~`2,86 MB`);
  * `RQ3/commit-analysis/ghiscoding_angular-slickgrid/commits_analysisghiscoding_angular-slickgrid_only_gui.xlsx` (`241 KB`).

### ❌ Escluso da Git (file pesanti o rigenerabili)
* `02-E2EGit-TestE2E/data/E2EGit.db` (`2,28 GiB`) e `E2EGit.db.gz` (`596 MB`) — *escluso per il limite GitHub di 100 MB*.
* `02-E2EGit-TestE2E/data/E2EGit_e2e.db` (`2,7 MB`) — *escluso dalla regola `*.db` in `.gitignore`, rigenerabile in 1 secondo da `E2EGit.db`*.
* `02-E2EGit-TestE2E/data/IST2025_Zenodo/RQ3.zip` (`2,3 GiB`) e `E2E-Miner-IST.zip` (`3,5 MB`).
* Le cartelle clonate `02-E2EGit-TestE2E/repositories/repo_nodejs/*/repo/` (~`900 MB` sul fisso, di cui `835 MB` solo `equal-access`).
* Gli ambienti virtuali Python (`02-E2EGit-TestE2E/.venv/`, `E2E-Miner-IST/venv/`).
* Le immagini Docker compilate localmente (`slickgrid-e2e:*`, ~`7 GB` ciascuna).

---

## 2. Operazione preliminare sul PC Fisso (una sola volta)

Prima di passare al portatile, assicurati di aver pushato i commit locali del PC fisso su GitHub:

```bash
cd /home/paolo/Scrivania/Universita/Tirocinio
git push origin main
```

---

## 3. Setup sul Portatile — Passi da eseguire

### Passo 1 — Installare i tool di sistema
```bash
sudo apt update
sudo apt install -y git sqlite3 python3 python3-venv curl unzip
```
*(Opzionale, solo se devi eseguire i container Docker di `angular-slickgrid` sul portatile)*:
```bash
# Installa Docker Engine (o docker.io) e aggiungi il tuo utente al gruppo docker
sudo usermod -aG docker "$USER"
# Poi effettua logout/login. Nota: esegui_test_docker.sh usa anche `konsole` (KDE).
```

---

### Passo 2 — Clonare la repository GitHub
> **Nota sui percorsi**: alcuni script (`clona_repository.sh`, `esegui_test_docker.sh`) contengono il percorso assoluto `/home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E`. Se il tuo utente sul portatile si chiama `paolo`, clonando qui sotto gli script funzionano senza modifiche; altrimenti aggiorna `BASE_DIR` negli script.

```bash
mkdir -p ~/Scrivania/Universita
cd ~/Scrivania/Universita
git clone https://github.com/PaoloTed/Tirocinio.git
cd Tirocinio
```
*(Se la repo sul portatile esisteva già, usa invece `git pull origin main`.)*

---

### Passo 3 — Ricreare l'ambiente virtuale Python (`.venv`)
Serve agli script in `02-E2EGit-TestE2E/scripts/nodejs/` (`salva_versioni_txt.py`, `salva_ciclo_vita_txt.py`):

```bash
cd ~/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pydriller GitPython lizard
deactivate
```

*(Opzionale, solo se vuoi lanciare gli script di `data/IST2025_Zenodo/E2E-Miner-IST/`)*: il file `requirements.txt` originale contiene pacchetti di sistema esportati con `pip freeze`; conviene creare un `venv` dedicato dentro `E2E-Miner-IST/` installando solo le librerie realmente usate (es. `pandas`, `openpyxl`, `pydriller`, `matplotlib`) e verificare i path hardcoded in `CommitAnalyzer/commitAnalyzer.py`.

---

### Passo 4 — Scaricare i database e gli archivi pesanti

Hai **due modalità equivalenti**: scaricarli da **Zenodo** (Opzione A) oppure copiarli direttamente dal PC fisso via **chiavetta USB / `rsync`** (Opzione B, più veloce).

#### Opzione A — Download da Zenodo

1. **Database `E2EGit.db` (`2,28 GiB`, DOI `10.5281/zenodo.14234731`)**:
   * Pagina: `https://zenodo.org/records/14234731`
   * Scarica `E2EGit.db` dentro `02-E2EGit-TestE2E/data/E2EGit.db` (es. via browser oppure `curl`):
     ```bash
     cd ~/Scrivania/Universita/Tirocinio
     curl -L -o 02-E2EGit-TestE2E/data/E2EGit.db \
       "https://zenodo.org/records/14234731/files/E2EGit.db?download=1"
     md5sum 02-E2EGit-TestE2E/data/E2EGit.db
     # MD5 atteso (verificato in docs/02_schema.md): 01e69c6956bb747d4142cfcd9d5eebb2
     ```

2. **Generare il database filtrato `E2EGit_e2e.db` (`2,7 MB`, usato da `sql_trova_repo_js_ts-sh`)**:
   ```bash
   cd ~/Scrivania/Universita/Tirocinio
   sqlite3 02-E2EGit-TestE2E/data/E2EGit_e2e.db <<'SQL'
   ATTACH DATABASE '02-E2EGit-TestE2E/data/E2EGit.db' AS src;
   CREATE TABLE gui_testing_repo_details AS SELECT * FROM src.gui_testing_repo_details;
   CREATE TABLE gui_testing_test_details AS SELECT * FROM src.gui_testing_test_details;
   CREATE TABLE repository AS
     SELECT * FROM src.repository
     WHERE name IN (SELECT repository_name FROM gui_testing_repo_details);
   DETACH DATABASE src;
   SQL
   ```
   Verifica rapida (atteso `472 | 472 | 8601`):
   ```bash
   sqlite3 02-E2EGit-TestE2E/data/E2EGit_e2e.db \
     "SELECT (SELECT COUNT(*) FROM repository), (SELECT COUNT(*) FROM gui_testing_repo_details), (SELECT COUNT(*) FROM gui_testing_test_details);"
   ```

3. **Archivio `RQ3.zip` da IST 2025 Zenodo (`2,3 GiB`, DOI `10.5281/zenodo.15882798`)** — *Opzionale*:  
   I file di ciclo di vita `*_tests_lifecycle_analysis.xlsx` (477 repo) e i sorgenti di `E2E-Miner-IST` arrivano già da Git. Scarica `RQ3.zip` solo se ti servono anche gli altri Excel globali (`coevolution-metrics_IST.xlsx`, `ass_rule-metrics_*`, `dev-analysis-IST.xlsx`, `selenium_changes_*`), gli `span_analysis` o tutti gli `only_gui`:
   ```bash
   cd ~/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/data/IST2025_Zenodo
   curl -L -o RQ3.zip "https://zenodo.org/records/15882798/files/RQ3.zip?download=1"
   md5sum RQ3.zip   # MD5 atteso: 986742c4c34ebd9fb1cdddd300cd2e3b
   unzip -tq RQ3.zip
   ```
   Per estrarre tutto **l'utile (~`220 MB`) evitando i `19,38 GB` di matrici `*_only_app.*`**:
   ```bash
   unzip -q -o RQ3.zip -x "__MACOSX/*" "*/.DS_Store" "*~lock*" "*_only_app.*"
   ```

#### Opzione B — Copia diretta dal PC Fisso (USB o rete locale)
Se copi i file pesanti direttamente dal PC fisso dopo il `git clone`, ti bastano questi file negli stessi percorsi relativi sotto `~/Scrivania/Universita/Tirocinio/`:
* `02-E2EGit-TestE2E/data/E2EGit.db.gz` (`596 MB`) → poi `gunzip -k 02-E2EGit-TestE2E/data/E2EGit.db.gz` quando ti serve `E2EGit.db`
* `02-E2EGit-TestE2E/data/E2EGit_e2e.db` (`2,7 MB`)
* `02-E2EGit-TestE2E/data/IST2025_Zenodo/RQ3.zip` (`2,3 GiB`, opzionale)
* *(Opzionale)* le cartelle `02-E2EGit-TestE2E/repositories/repo_nodejs/*/repo/` se non vuoi ri-clonarle nel Passo 5.

---

### Passo 5 — Ri-clonare le repository target in `repositories/repo_nodejs/`

I file di output (`results/`) e `docker/` arrivano già da Git; mancano solo i sorgenti dentro `*/repo/` (ignorati da `.gitignore`). Puoi ri-clonarli con `--filter=blob:none` (molto più veloce e leggero):

```bash
BASE=~/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/repo_nodejs

git clone --filter=blob:none https://github.com/ghiscoding/angular-slickgrid.git "$BASE/angular-slickgrid/repo"
git clone --filter=blob:none https://github.com/ibma/equal-access.git            "$BASE/equal-access/repo"
git clone --filter=blob:none https://github.com/epam/ketcher.git                 "$BASE/ketcher/repo"
git clone --filter=blob:none https://github.com/tryghost/koenig.git              "$BASE/koenig/repo"
```

*(Nota: se in seguito usi `02-E2EGit-TestE2E/scripts/generali/clona_repository.sh <owner/repo>`, tieni presente che attualmente salva in `repositories/<repo>/repo` invece di `repositories/repo_nodejs/<repo>/repo`.)*

---

## 4. Verifica finale sul Portatile

Esegui questi controlli rapidi per verificare che tutto funzioni:

```bash
cd ~/Scrivania/Universita/Tirocinio

# 1. Verifica che lo script Python trovi .venv e PyDriller
02-E2EGit-TestE2E/.venv/bin/python -c "import pydriller; print('PyDriller OK:', pydriller.__version__)"

# 2. Verifica query sul DB ridotto
bash 02-E2EGit-TestE2E/scripts/nodejs/sql_trova_repo_js_ts-sh && head -n 10 02-E2EGit-TestE2E/repositories/repo_nodejs/repository_node_js_ts_numtest_gr10_releses_gr5.txt

# 3. Verifica che i file lifecycle siano presenti (atteso: 477)
find 02-E2EGit-TestE2E/data/IST2025_Zenodo/RQ3 -name "*_tests_lifecycle_analysis.xlsx" | wc -l
```
