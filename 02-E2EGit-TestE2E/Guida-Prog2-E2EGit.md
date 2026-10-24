# Prog2 — Esecuzione e manutenzione di test E2E (E2EGit, 100 repository)

### Guida operativa, piano di lavoro e calendario degli aggiornamenti al professore

**Versione** 1.0 — 23 ottobre 2026
**Documenti di partenza** `ProgTirocinio.txt`, `analisitirociniomd.md`
**Orizzonte** 20 settimane: lun 26/10/2026 → ven 12/03/2027
**Carico ipotizzato** 20–25 ore/settimana, di cui una parte rilevante è tempo macchina (batch notturni), non tempo tuo.
**Nota** questo progetto è la **continuazione di un'attività già avviata**: la prima settimana non serve a studiare, serve a **recuperare quello che esiste già** (§2). È il passaggio che, se saltato, fa perdere tre settimane.

---

## 0. In 60 secondi

- **La domanda del professore, tradotta in tre domande misurabili**: (1) i test si eseguono ancora? (2) se si eseguono, passano o sono rotti? (3) se il codice è cambiato e i test no, **perché**?
- **Il rischio numero uno** non è tecnico, è di perimetro: 100 repository × ~92 test ciascuno = oltre 9.000 test. Non li eseguirai e non li analizzerai tutti a mano. Il progetto si regge su **esecuzione automatizzata su 100 repo + analisi profonda su 10–20**.
- **Il rischio numero due**: arenarsi su un repository che non parte. Regola: **45 minuti** di setup, poi `setup_failed` e avanti. Senza eccezioni.
- **La cosa da fare lunedì 26/10**: chiedere al professore *dove sono i risultati di chi è venuto prima di te*. Non riscrivere una pipeline che esiste già.
- **Deadline esterne**: nessuna. Il che è un problema: senza scadenze intermedie il progetto slitta. Le scadenze le crei tu con i gate di §8.

---

## 1. Cosa c'è dentro questo progetto (lettura onesta)

| Voce | Valutazione |
|---|---|
| **Natura** | Ingegneria del software empirica: ambienti, esecuzione, triage, analisi |
| **Competenze che acquisisci** | Docker, Maven/Gradle/npm/pip, Selenium/Playwright/Cypress, SQL, PyDriller, analisi dei fallimenti |
| **Difficoltà tecnica** | Alta, ma di tipo "artigianale": ogni repository è un caso |
| **Difficoltà scientifica** | Media. Il disegno sperimentale è consolidato, ma la classificazione è interpretativa |
| **Soddisfazione** | Alta quando un repo parte; bassa quando passi due giorni su una dipendenza del 2019 |
| **Rischio principale** | Il tasso di eseguibilità reale è ignoto. Se è del 30%, il progetto cambia forma |
| **Segnale di buon fit** | Ti piace capire perché una build fallisce e sai resistere alla frustrazione |
| **Segnale di cattivo fit** | Vuoi costruire cose nuove e ti annoia configurare ambienti → Prog1 |

### Cosa questo progetto NON è (mettilo per iscritto nel verbale)

- ❌ Non è scrivere nuovi test per i progetti open source.
- ❌ Non è correggere i bug dei progetti che analizzi.
- ❌ Non è generare test con un LLM (al massimo è lavoro futuro, citato nelle conclusioni).
- ❌ Non è "far passare i test": il risultato può essere che il 60% dei test è rotto, ed è un risultato.

---

## 2. Prima di tutto: recuperare il lavoro già avviato

Il professore ha detto "continuo di uno già avviato". Questo significa che esiste, da qualche parte, almeno una parte di: repository clonati, una pipeline, dei risultati, una lista di repo già trattati, dei problemi noti. **Se non lo recuperi, rifai il lavoro di qualcun altro e perdi 2–3 settimane.**

### 2.1 Sei artefatti da chiedere esplicitamente

| # | Artefatto | Perché è critico | Se non esiste |
|---|---|---|---|
| 1 | Elenco dei repository **già considerati** (eseguiti, falliti, scartati) | Eviti di rieseguire gli stessi 20 repo | Lo costruisci tu e diventa il tuo contributo |
| 2 | La **pipeline** esistente (script, Dockerfile, comandi) | Riuso diretto o riscrittura consapevole | La scrivi da zero (§7) |
| 3 | I **risultati** già prodotti (log, CSV, DB) | Sono la baseline di confronto | Li produci tu |
| 4 | La **macchina** dove girava (accesso, spazio, Docker) | Eviti di scoprire a metà che non hai 200 GB | Chiedi spazio o riduci il perimetro |
| 5 | Il **protocollo di classificazione** dei fallimenti, se c'è | Se esiste, va usato per confrontabilità | Lo definisci tu (§6.4) |
| 6 | Le **persone** che ci hanno lavorato | 30 minuti con loro valgono una settimana di ricerche | — |

### 2.2 Come porre la domanda (senza sembrare che non hai letto niente)

> "Ho letto il paper E2EGit e il C4. Per non rifare lavoro già fatto: quali repository sono già stati eseguiti, esiste una pipeline che posso riusare, e su quale macchina girava? Se c'è un ex tirocinante o un dottorando che ci ha lavorato, posso parlargli 20 minuti?"

Questa formulazione funziona perché mostra che hai letto e chiede accesso, non che ti aspetti che ti venga spiegato tutto.

---

## 3. Mappa dei link: cosa contiene ognuno e cosa devi farci

Stato di verifica: ✅ consultato il 23/10/2026 · ⚠️ accesso parziale · ➖ non verificato

| # | Link | Cosa contiene (verificato) | Cosa devi fare concretamente | Entro |
|---|---|---|---|---|
| 1 | ⚠️ [Paper E2EGit — IEEE Xplore](https://ieeexplore.ieee.org/document/11025750) (DOI 10.1109/MSR66628.2025.00121) | Versione editoriale del paper MSR 2025, Data & Tool Showcase Track. L'accesso automatico non restituisce il contenuto (verifica anti-bot / paywall): serve la rete o il proxy dell'Ateneo | Usalo solo se ti serve la citazione editoriale. Per leggere, usa il C4 (link 3): è lo stesso contenuto, aperto | Sett. 1 |
| 2 | ✅ [Dataset E2EGit — Zenodo](https://zenodo.org/records/14234731) | v3, 28/11/2024, CC-BY-4.0. Quattro file, **4,2 GB** totali: `E2EGit.db` 2,4 GB (md5 `01e69c6956bb747d4142cfcd9d5eebb2`), `E2EGit.sql` 1,8 GB (md5 `73659d11ea456e5ae05bc0808fa8607f`), più 4 file di dipendenze web (Java/JS/TS/Python) | Scarica **solo** `E2EGit.db`: il `.sql` contiene gli stessi dati in forma di dump SQL, quindi è ridondante se hai il `.db`. Verifica l'md5. **Attenzione**: la pagina segnala "newer version available" → controlla `https://zenodo.org/records/14234731/latest` e **annota la versione esatta** che usi nel paper e nella relazione | Lun 26/10 (download in background) |
| 3 | ✅ [PDF del paper — C4](https://valeriapontillo.github.io/documents/conference/C4.pdf) | Paper completo E2EGit, MSR 2025, **Distinguished Dataset Award**. Contiene la Fig. 3 con lo schema del DB | Leggilo con la scheda (§4) focalizzandoti su: criteri di costruzione, definizione di "non-trivial repository", struttura delle 5 tabelle, limiti dichiarati. È la fonte per la sezione "Metodo" della tua relazione | Mar 27/10 |
| 4 | ✅ [C5 — Performance Testing in Open-Source Web Projects: Adoption, Maintenance, and a Change Taxonomy (ICSME 2025)](https://valeriapontillo.github.io/documents/conference/C5.pdf) | **Il lavoro più vicino alla tua domanda** sui test di performance: adozione, manutenzione e una **tassonomia dei cambiamenti** ai test | Leggilo per intero. Ti serve per (a) non riscoprire categorie già pubblicate, (b) usare la loro tassonomia come base per la tua. Nel paper dovrai dire in cosa il tuo lavoro la estende | Mer 28/10 |
| 5 | ✅ [J8 — Investigating the Adoption and Maintenance of Web GUI Testing (IST 2025)](https://valeriapontillo.github.io/documents/journal/J8.pdf) | Estensione journal sul versante GUI: adozione e manutenzione dei test GUI su GitHub | Leggi abstract, metodo e minacce alla validità (il resto è contesto). Ti serve per la sezione "Lavoro correlato" e per scegliere le metriche di manutenzione | Gio 29/10 |
| 6 | ✅ [C14 — Smelly Bad Practices in Performance System Tests (ICSME 2026)](https://valeriapontillo.github.io/documents/conference/C14.pdf) | **È lo stesso paper del link 9 (PT-LINTR)**, nella versione finale di settembre 2026. Non è una lettura separata: sarebbe una doppia lettura dello stesso lavoro | Leggilo una volta sola, come paper del tool (link 9). Il concetto di *lifetime* di un difetto è però esattamente il tuo "da quanto tempo il test non cambia": riusalo | Sett. 2 |
| 7 | ✅ [Pagina di Valeria Pontillo](https://valeriapontillo.github.io/) | Pubblicazioni, tool, contatti. È la co-autrice del dataset | Usala per trovare i lavori più recenti (2026) e per capire lo stato dell'arte del gruppo. Non scriverle direttamente: passa dal professore | Sett. 1 |
| 8 | ✅ [E2E-Loader — Zenodo](https://zenodo.org/records/14281199) | Tool che genera test di performance da test E2E GUI (v2, dic. 2024) | Solo se ti serve il collegamento con la linea di ricerca del gruppo. Non è necessario per il tirocinio | Sett. 4 |
| 9 | ✅ [PT-LINTR — replication package (Zenodo)](https://doi.org/10.5281/zenodo.18872673) | Il tool citato nella guida come "PT-Linter" si chiama in realtà **PT-LINTR**. Rileva 6 cattive pratiche nei test **Apache JMeter**. Non ha un repository pubblico: l'unica distribuzione è lo ZIP (87,8 MB, CC-BY-4.0, md5 `84e83260aac60645ec536914556ec0cc`) che contiene codice, `venv`, report e la storia Git del progetto. Dettagli in §3.1 | Scarica il pacchetto e **provalo su 2–3 `.jmx`**: è il modello architetturale della pipeline che ti serve (§3.1). Poi chiedi al professore l'accesso al repo live | Sett. 2 |
| 10 | ✅ [Documentazione PyDriller](https://pydriller.readthedocs.io/en/latest/) | Mining della storia Git (ultima versione 2.12) | Ti serve nella Fase 4 per la domanda "perché i test non cambiano": estrazione della storia dei file di test e del codice | Sett. 5 |

### 3.1 PT-LINTR: cos'è esattamente e perché ti riguarda

**Paper già scaricati** in `02-E2EGit-TestE2E/docs/letteratura/` (verificati il 23/10/2026):

| File | Pagine | Contenuto |
|---|---|---|
| `E2EGit_MSR2025_C4.pdf` | 5 | Paper E2EGit, MSR 2025, Distinguished Dataset Award (originale) |
| `E2EGit_MSR2025_C4_IT.pdf` | 8 | **Traduzione italiana integrale con le figure estratte** |
| `PerformanceTesting_Maintenance_ICSME2025_C5.pdf` | 12 | Manutenzione dei test di performance + tassonomia dei cambiamenti |
| `WebGUITesting_Maintenance_IST2025_J8.pdf` | 41 | Manutenzione dei test GUI (versione journal) |
| `PT-LINTR_ICSME2026_paper.pdf` | 12 | Paper PT-LINTR (= C14), versione di settembre 2026 |

Il PDF tradotto è generato da `sorgenti/E2EGit_C4_IT.html`; le figure sono in `figure/`. Il riassunto ragionato, con la spiegazione dei concetti non banali del paper, è in [`docs/letteratura/E2EGit_riassunto_e_concetti.md`](letteratura/E2EGit_riassunto_e_concetti.md): leggilo **prima** del colloquio, non dopo aver letto il paper. Lo schema del database è in [`docs/02_schema.md`](02_schema.md) e il dizionario dei CSV in [`docs/03_dizionario_csv.md`](03_dizionario_csv.md).

Non ho tenuto il preprint di giugno dello stesso paper: è la versione **anonima per la revisione** (double-blind), superata da quella di settembre. Tenerle entrambe crea solo confusione su quale citare.

**Identità.** Il nome corretto è **PT-LINTR** (non "PT-Linter"). È il tool del paper *Smelly Bad Practices in Performance System Tests: Detection, Prevalence, and Lifetime* (Di Meglio, Pontillo, Starace, Martins, Di Nucci, Palomba — ICSME 2026, SQuIDS Lab UniNA + GSSI + SeSa Lab). La cartella nel pacchetto si chiama `pt-lintr/`, il paper lo scrive `PT-LINTR`.

**Cosa fa.** Analizza test plan **Apache JMeter** (`.jmx`) e rileva 6 cattive pratiche su 10 catalogate. Le altre 4 (BP01 workload irrealistico, BP03 durata inadeguata, BP05 ambiente non rappresentativo, BP06 condizioni di rete) non sono rilevabili staticamente dal solo file di test.

| ID | Cattiva pratica | Regola nel codice | Precisione |
|---|---|---|---|
| BP02 | Ignorare i think time (nessuna pausa tra richieste) | `ThinkTimeRule` | 88,5% |
| BP04 | Ramp-up / cool-down inadeguati (0 o 1 s) | `WarmUpPhaseRule` | 100% |
| BP07 | Nomi di richiesta lasciati al default JMeter | `PoorNamingConventionsRule` | 100% |
| BP08 | Asserzioni rigide (uguaglianza esatta su tempi/dimensioni) | `RigidAssertionRule` | 100% |
| BP09 | Assenza di validazione della risposta | `NoAssertionRule` | 96,3% |
| BP10 | Troppi listener (>3) | `ExcessiveListeners` | 83,3% |

Precisione misurata su un campione manuale del 10% dei casi "smelly". Numeri di applicazione su E2EGit: 72 repository, 244 test JMeter di cui 10 corrotti → **234 analizzati**; solo **1** test senza violazioni; BP02 presente in 184 casi (78,6%), BP04 in 173 (73,9%).

**Come è fatto (ed è la parte che ti serve).** Python 3.12 + `lxml` per il parsing del JMX + `Jinja2` per i report HTML + `GitPython` per il clone + `PyDriller` per la storia + `sqlite3` per leggere `E2EGit.db`. La catena è esattamente questa:

```text
E2EGit.db → performance_testing_test_details (is_jmeter=1)
   → clone del repo su GitHub
   → PyDriller su filepath = test plan
   → per OGNI commit che tocca il file: analisi → JSON + HTML per versione
   → report di storia (una riga per versione)
```

È **lo stesso schema** che ti serve per la domanda "i test non cambiano": una versione per commit, un esito per versione, confronto tra versioni consecutive. Cambia solo l'analizzatore (lì è un linter di smell, per te saranno esito dell'esecuzione e metriche di cambiamento).

**Come provarlo (Windows, 20 minuti).**

```powershell
cd $HOME\Desktop\Universita\Tirocinio\02-E2EGit-TestE2E
curl.exe -L -o pt-lintr.zip "https://zenodo.org/records/18872673/files/ICSME26-SMELLY-PERF.zip?download=1"
Get-FileHash pt-lintr.zip -Algorithm MD5   # atteso 84E83260AAC60645EC536914556EC0CC
Expand-Archive pt-lintr.zip -DestinationPath .\pt-lintr-pkg
# il pacchetto contiene ~25.000 file (c'è dentro anche il venv): estrai solo pt-lintr/pt-lintr/
```

Tre trappole già verificate, da non scoprire a runtime:

1. **Il venv incluso è inutile**: è un ambiente macOS/Python 3.12 (ci sono i file `__MACOSX`). Creane uno tuo con `pip install lxml jinja2 gitpython pydriller requests`.
2. **Il path del DB è hardcoded** in `src/dbconnection/DatasetConnection.py`: `'/home/sergio/Scaricati/E2EGit.db'` (la macchina di uno degli autori). Va sostituito con un path relativo al tuo `data/E2EGit.db`, altrimenti su Windows cerca `C:\home\sergio\...` e fallisce.
3. **Va lanciato da `src/`** (`python Starter.py`), perché gli import sono assoluti sul package (`from rules.jmeterRules...`). L'opzione 3 del menu analizza un singolo `.jmx` locale: è la prova più veloce, non serve il dataset.

**Stato del progetto.** Ultimo commit nel pacchetto: **28/01/2026** (5 commit, 23–28 gennaio, autore Starace; prima si chiamava diversamente, il `.idea` la chiama `PerformanceTestSmellDetector`). Il remote dichiarato nel `.git` è `https://github.com/squidslab/pt-lintr` ma **oggi risponde 404**: repo privato o spostato. Il pacchetto Zenodo è quindi l'unica copia pubblica, ed è uno snapshot di gennaio 2026.

**Il dettaglio che vale più di tutti.** Il README chiude con: *"This tool was developed during the curricular internship of Vincenzo De Rosa @ SQuIDS Lab"*. Cioè: PT-LINTR è **nato da un tirocinio curriculare** ed è diventato un paper a una conferenza internazionale. È il metro con cui il professore misurerà il tuo Prog2. Non è un caso che ti abbia proposto "continuo di uno già avviato": sta replicando lo stesso modello.

**Cosa NON è.** PT-LINTR analizza test di **performance** (JMeter), non test **GUI** (Selenium/Playwright/Cypress). Non è l'oggetto del tuo tirocinio: è il tuo **modello di pipeline** e un esempio di tassonomia validata. Se lo confondi con il deliverable, sbagli perimetro.

### Cosa NON fare con questi link

- ❌ Non scaricare `E2EGit.sql`: sono 1,8 GB che duplicano il `.db`.
- ❌ Non aprire il `.db` con Excel o con un editor di testo.
- ❌ Non partire dal C5 prima del C4: prima capisci il dataset, poi cosa è già stato studiato.
- ❌ Non citare il paper IEEE con un DOI "a memoria": ricopialo dal PDF C4.

---

## 4. Scheda di lettura (template)

`docs/letteratura/schede/e2egit.md`, `c5.md`, `j8.md`: una per fonte.

```markdown
# <Titolo>
- Riferimento (DOI/URL):
- Tipo: dataset / studio empirico / tool
- Domanda:
- Dataset e periodo:
- Unità di analisi (repo? file di test? test case?):
- Definizione di "manutenzione" usata dagli autori:
- Tassonomia/categorie proposte:
- Risultati chiave (max 3, con numeri):
- Minacce alla validità dichiarate:
- Cosa posso riusare:
- Cosa il mio lavoro aggiunge:
```

La riga "**Cosa il mio lavoro aggiunge**" è quella che ti salva in sede di discussione: se non sai riempirla, il progetto non ha un contributo.

---

## 5. Setup tecnico (mezza giornata + download in background)

### 5.1 Spazio e prerequisiti

```powershell
Get-PSDrive C | Select-Object Used,Free
docker --version
git --version
java -version
node --version
python --version
```

Servono **≥250 GB liberi**: dataset 4,2 GB + 100 repository clonati (50–200 GB) + log e report. Se non li hai, il perimetro va ridotto **prima** di iniziare, non a metà.

### 5.2 Download del dataset (avvialo lunedì e dimenticatene)

```powershell
cd $HOME\Desktop\Universita\Tirocinio\02-E2EGit-TestE2E
mkdir data -Force
curl.exe -L -C - -o data\E2EGit.db "https://zenodo.org/records/14234731/files/E2EGit.db?download=1"
Get-FileHash data\E2EGit.db -Algorithm MD5
# atteso: 01E69C6956BB747D4142CFCD9D5EEBB2
```

`-C -` riprende un download interrotto: con 2,4 GB succede.

### 5.3 Esplorazione del database

```powershell
python -c "import sqlite3; c=sqlite3.connect('data/E2EGit.db'); print([r[0] for r in c.execute(\"select name from sqlite_master where type='table'\")])"
```

Poi, in un notebook o in DB Browser for SQLite:

```sql
-- 1. inventario
SELECT COUNT(*) FROM repository;                    -- atteso ~1,5 M
SELECT COUNT(*) FROM non_trivial_repository;
SELECT COUNT(*) FROM gui_testing_test_details;      -- una riga per file di test
SELECT COUNT(*) FROM gui_testing_repo_details;      -- atteso 472
SELECT COUNT(*) FROM performance_testing_test_details; -- atteso 410

-- 2. schema reale delle colonne (NON fidarti dei nomi a memoria)
PRAGMA table_info(gui_testing_repo_details);

-- 3. distribuzione (adatta i nomi delle colonne a quelli che leggi da PRAGMA)
SELECT * FROM gui_testing_repo_details LIMIT 5;
```

**Importante**: i nomi delle colonne non sono documentati in modo uniforme tra paper e DB. La prima cosa da fare è `PRAGMA table_info` su tutte e cinque le tabelle e salvare l'output in `docs/02_schema.md`. Senza quello schema scritto da te, ogni query successiva è un'indagine.

### 5.3-bis Da dove escono i repository da eseguire

Domanda che viene naturale: «ok, e i repository dove li prendo?». Risposta: **non sono nel dataset**, e non c'è niente da scaricare a parte il database.

| Cosa hai nel dataset | Cosa devi procurarti tu |
|---|---|
| Il **nome** del repository (`owner/repo`) | Il codice: `git clone https://github.com/owner/repo` |
| Il **percorso dei test** dentro il repository | Il commit giusto su cui eseguirli |
| Framework, motore di test, numero di test | Le dipendenze, il build, il browser |
| Metadati del repository (commit, stelle, lingua) | La licenza e il permesso d'uso |
| — | **L'esecuzione** (che è il tuo lavoro) |

Le due tabelle che ti servono:

- **`gui_testing_repo_details`** → una riga per repository (**472**). È la lista da cui parte la selezione dei 100.
- **`gui_testing_test_details`** → una riga per **file di test**, con `test_path`, il framework usato, il motore di test e `number_of_tests`.

**Tre trappole già viste nel codice di PT-LINTR** (che interroga le stesse tabelle):

1. La colonna del nome nella Figura 3 del paper si chiama `name`, ma nel database reale si chiama **`repository_name`**. Fidati di `PRAGMA table_info`, non della figura.
2. **`test_path` non è un percorso relativo pulito**, e la regola **cambia tra le due tabelle** (verificato sul database il 24/10/2026):
   - **`gui_testing_test_details`**: `/apache_roller/it-selenium/src/test/java/.../InitialLoginTestIT.java` — il primo segmento è `owner_repo` unito dall'underscore. Si toglie **1** segmento e resta `it-selenium/src/test/java/...`.
   - **`performance_testing_test_details`**: `\apache\roller\testing\roller-load-test.jmx` — il primo segmento è vuoto (barra iniziale), poi `owner`, poi `repo`. Si tolgono **3** segmenti e resta `testing/roller-load-test.jmx`.
   
   Applicare la regola sbagliata produce un percorso che non esiste: è il tipo di errore che ti fa perdere mezza giornata a capire se sbaglia il dataset o il tuo codice.
3. I file `.jmx` e i test Locust sono nella tabella **`performance_testing_test_details`**, non in quella GUI: sono due mondi separati, con colonne diverse.

Per estrarre la lista senza scrivere query a mano:

```powershell
cd $HOME\Desktop\Universita\Tirocinio\02-E2EGit-TestE2E
python src/01_estrai_repository.py                 # produce data/repos_gui.csv, tests_gui.csv, tests_perf.csv, repos_url.csv
python src/02_storia_test.py --limit 5             # prova la storia Git su 5 repository (scaricato in un minuto)
python src/02_storia_test.py                       # storia Git su tutti i 472 → results/storia_test.csv
```

Lo script `01` introspeziona lo schema, stampa la struttura delle tabelle e produce i CSV. **Eseguito sul database reale il 24/10/2026**: 472 repository, 8.601 file di test, 0 errori. Lo script `02` risponde alle domande 1–3 di §6.2 senza Docker: per ogni file di test dice se esiste ancora al commit di oggi, quante volte è stato toccato dalla data dello snapshot e quante righe sono cambiate.

Verifica manuale equivalente, se preferisci SQL:

```sql
-- 1. quali colonne esistono davvero
PRAGMA table_info(gui_testing_repo_details);

-- 2. la lista dei repository (adatta il nome della colonna all'output sopra)
SELECT repository_name FROM gui_testing_repo_details ORDER BY 1;

-- 3. i test di un repository specifico
SELECT test_path, number_of_tests
FROM gui_testing_test_details
WHERE repository_name = 'owner/repo';
```

**Il commit SHA c'è, ed è la colonna portante di tutto il lavoro.** La tabella `repository` contiene `last_commit` e **`last_commit_sha`**, presente per tutti e 472 i repository (verificato: 0 nulli). È già estratto in **`data/repos_commit.csv`** (11 colonne, una riga per repository):

| Colonna | Significato |
|---|---|
| `repository_name` | `owner/repo` |
| `number_of_tests`, `number_of_files` | i conteggi del repository |
| `last_commit` | data dell'ultimo commit al momento del mining (ISO, es. `2024-03-21T02:19:55`) |
| `last_commit_sha` | **l'hash da usare nel `git checkout`** |
| `default_branch` | branch di default: `main` (192), `master` (180), altro (100) |
| `licences` | licenza dichiarata — **vuota per 25 repository** |
| `main_language`, `created_at`, `pushed_at` | metadati per la stratificazione |
| `clone_url` | URL pronto per il clone |

```powershell
git clone https://github.com/<owner>/<repo>
cd <repo>; git checkout <last_commit_sha>
```

#### Perché il commit è ancora più importante per la tua tesi

La domanda del professore è "perché i test non cambiano". Per rispondere devi confrontare due momenti:

- **t₀** = il commit registrato nel dataset (dove il test è com'era quando sono stati contati 43.670 test)
- **t₁** = l'esecuzione di oggi, su quel codice

Se non ancori l'esecuzione a t₀, stai confrontando "il test di oggi" con "un metadato di un anno e mezzo fa", e ogni differenza è indistinguibile tra "il test non è cambiato" e "ho misurato due cose diverse". Il commit è ciò che rende il confronto valido — ed è la parola che in una relazione sostituisce "abbastanza preciso" con "riproducibile".

**Conseguenza operativa**: `last_commit_sha` va registrato in **ogni** record di `results/`, non solo nel testo della relazione. Un record senza SHA non è un risultato, è un'opinione.

**Tre cose che il file rivela e che non avresti notato.**

1. **Il mining è di marzo 2024, non di maggio.** Il paper dice "May 2024", ma la mediana di `last_commit` è il **27 marzo 2024** e il massimo il 29 marzo. La fotografia del codice è quindi anche più vecchia di quanto dichiarato: quasi due anni e mezzo alla data del tirocinio.
2. **Il commit è l'ultimo del repository, non l'ultimo che tocca il test.** Per sapere quando il file di test è stato modificato l'ultima volta serve PyDriller sul clone (Fase 4). Due informazioni diverse, entrambe necessarie: lo SHA dice *da dove parto*, la storia del file dice *cosa gli è successo nel frattempo*.
3. **25 repository non dichiarano licenza.** Clonarli va bene, ridistribuirne il codice no: se poi pubblichi dati derivati, quei 25 vanno esclusi o verificati a mano.


### 5.4 Immagini Docker di base

Prepara (e versiona in `docker/`) quattro immagini, non una per repository:

| Stack | Immagine base | Comando di setup tipico |
|---|---|---|
| Java / Maven | `maven:3.9-eclipse-temurin-11` (e 17) | `mvn -B dependency:resolve` |
| Java / Gradle | `gradle:8-jdk11` | `./gradlew dependencies` |
| Node | `node:20` | `npm ci` (o `yarn install --frozen-lockfile`) |
| Python | `python:3.11` | `pip install -r requirements.txt` |

**Sicurezza**: eseguire `npm install` o `mvn` su un repository sconosciuto significa eseguire codice arbitrario. Regole non negoziabili: solo container, **nessuna credenziale montata**, rete disabilitata dopo il setup (`--network none` in fase di test), nessun `sudo`, nessun push verso i repo originali.

### 5.5 Dove eseguire: PC, server o Google Colab

| Ambiente | Va bene per | Limite che ti frega |
|---|---|---|
| **PC locale + Docker** | esecuzione dei 100 repo, batch notturni | disco (250 GB) e ore accese |
| **Server di laboratorio** | la stessa cosa, meglio | da chiedere al professore |
| **Google Colab** | analisi di `results.db`, figure, PyDriller su pochi repo | **niente Docker**, sessioni max 12 h, stato non persistente |

Tre motivi per cui la pipeline **non** può girare su Colab:

1. **Niente Docker.** Le VM Colab non hanno un demone Docker utilizzabile. Il FAQ ufficiale elenca fra le tecniche vietate "containerization to circumvent anti-abuse policies": provarci ti espone alla chiusura dell'account, non solo a un errore.
2. **12 ore e poi reset.** La sessione gratuita dura al massimo 12 h e viene terminata anche per inattività. Con 100 repo da 35–70 minuti l'uno e un tasso di successo iniziale del 40–60%, ti serve un ambiente che sopravviva per giorni e riprenda da dove si era fermato.
3. **Disco e stato.** Una VM Colab ha circa 80–100 GB utilizzabili e perde tutto alla disconnessione. Clonare 100 repository (50–200 GB) a ogni sessione non è un'opzione.

Dove Colab invece **è comodo**: notebook di analisi sui risultati già raccolti, figure per la relazione, oppure PyDriller su 5–10 repository per esplorare la storia dei test. Anche qui, attenzione al mount di Drive: migliaia di file piccoli (tipo i report HTML per commit di PT-LINTR, ~25.000 file) fanno fallire `drive.mount()`; zippa prima di copiare.

**Conseguenza operativa**: chiedi al professore **accesso a una macchina con Docker** al primo incontro. È la domanda (c) del 27/10 e vale più di qualsiasi ottimizzazione del codice.

---

## 6. Il nucleo scientifico: cosa significa "test non cambiati"

Questa è la parte che distingue una tesi da un lavoro di configurazione. Va definita **prima** di eseguire, altrimenti a marzo ti trovi con 100 repo eseguiti e nessuna risposta.

### 6.1 Tre domande, tre misure

| Domanda del professore | Traduzione operativa | Fonte dati |
|---|---|---|
| "I test si eseguono ancora?" | Tasso di eseguibilità = repo con ≥1 test eseguito / repo tentati | Esecuzione (Fase 3) |
| "Reggono o si sono rotti?" | Distribuzione degli esiti: passati / falliti / skippati / non eseguiti | Report dei framework |
| "Perché non sono cambiati?" | Quadrante "test fermo + codice in movimento" (§6.3) + 5 indicatori di §6.4 | Git history (PyDriller) |

### 6.2 Prima di tutto: sono cambiati dal commit del dataset a oggi?

Il dataset descrive il codice **di un giorno preciso** (marzo 2024, vedi `data/repos_commit.csv`). Tra quel giorno e oggi passano quasi due anni e mezzo. La prima domanda da porsi non è "si eseguono?", ma **"esiste ancora ciò che il dataset descrive?"**.

La formulazione precisa però è un'altra, e la differenza è tutta:

> Non "il file di test è cambiato", ma **"il file di test è cambiato rispetto a ciò che dovrebbe verificare"**.

Un test che modifica `wait(500)` in `wait(1000)` è cambiato. Un test il cui sorgente è identico ma i cui selettori puntano a un layout che non esiste più **non è cambiato** — e quest'ultimo è il fenomeno che interessa al professore. Confondere le due cose produce numeri che sembrano risultati ma non lo sono.

#### Le quattro domande, in ordine di robustezza

| # | Domanda | Come si misura | Costo | Quanto è conclusiva |
|---|---|---|---|---|
| 1 | Il file esiste ancora al percorso indicato? | `git log --follow -- <path>` | basso | **molto**: dice se il test è sparito o è stato spostato |
| 2 | Quante volte è stato toccato da t₀ a oggi? | `git log --numstat -- <path>` | basso | media: conta anche riformattazioni e bump di versione |
| 3 | **Cosa** è cambiato? | `git diff <sha> HEAD -- <path>` | medio | alta **se leggi i diff**, non se li conti soltanto |
| 4 | L'esito è cambiato? | eseguire il test a t₀ e a HEAD | **alto** (ambienti) | **la più alta**: è il comportamento, non il testo |

La 4 è la tesi del tirocinio, ma richiede Docker e ambienti: arriva nella Fase 3. Le domande **1–3 si possono fare subito**, senza container, su tutti i 472 repository, e producono già materiale per la relazione.

#### Comandi per il singolo repository

```powershell
git clone --filter=blob:none https://github.com/10up/elasticpress
cd elasticpress
git log --oneline 9b4d1210..HEAD -- tests/cypress/integration/dashboard-sync.cy.js
git diff --stat 9b4d1210 HEAD -- tests/cypress/integration/dashboard-sync.cy.js
git diff 9b4d1210 HEAD -- tests/cypress/integration/dashboard-sync.cy.js
```

`--filter=blob:none` scarica la storia **senza il contenuto dei file**: il contenuto arriva solo quando serve. Senza quel flag, i 472 repository (50–200 GB) diventano ingestibili; con il flag, la storia pesa poche decine di MB per repository.

#### Un primo risultato già disponibile

L'8.601 file di test del dataset hanno il testo del marzo 2024. Chiedere a Git quanto è stato aggiunto, rimosso e riscritto in ciascuno, su 472 repository, produce una distribuzione che da sola dice qualcosa: alcuni progetti sono morti (`pushed_at` fermo da anni), altri iperattivi. **Quella distribuzione mostra se il codice di test E2E è "vivo" o "congelato" prima ancora di eseguire un solo test** — ed è il primo capitolo dei risultati, ottenibile senza Docker.

`src/02_storia_test.py` implementa le domande 1–3 su tutti i repository, in batch, con l'output in `results/storia_test.csv`.

##### Cosa dicono i primi 3 repository (24/10/2026)

Prova eseguita su `10up/elasticpress`, `3liz/lizmap-web-client`, `Agenta-AI/agenta` — 45 file di test:

| Esito | File | Interpretazione |
|---|---|---|
| Test ancora al percorso indicato | 16 | si possono eseguire come descritti dal dataset |
| Test **cancellati** (`last_commit` 2025-05-05 … 2025-08-06) | 29 | **due terzi spariti in 14 mesi** |
| Test modificati dal commit | 16 | tutti quelli sopravvissuti |

I test cancellati di `10up/elasticpress` non sono stati spostati: il commit `fba57ace` del 5 maggio 2025 (`"Status Report"`) li ha **sostituiti** con file `*.spec.ts` in un percorso nuovo, con un cambio di framework. `Agenta-AI/agenta` ha cancellato tutti e 10 i file Cypress in un solo commit (27/02/2025).

**Questa è già una risposta, e non è quella che ci si aspetta.** La domanda "perché i test non cambiano" presuppone test che restano: qui i due terzi dei test *non esistono più*, e nella parte che sopravvive la regola è **accumulo, non riscrittura** (le righe aggiunte superano enormemente le rimosse: `print.spec.js` +1203/−360, `edition-form.spec.js` +1367/−0). Test che crescono per addizione sono spesso test che verificano sempre più scenari senza mai ristrutturarsi — il che spiega bene l'accumulo e male la manutenzione.

Tre lezioni operative, da verificare sul campione intero:

1. **L'esecuzione non può partire dal percorso del dataset senza un controllo preliminare.** Su 3 repository, 29 file su 45 non esistono più: senza il test di esistenza, la prima ondata di esecuzione darebbe "non eseguito" per due terzi del campione, e per la ragione sbagliata.
2. **Il tasso di cancellazione è un risultato di primo livello, non un dettaglio.** Va misurato prima di tutto il resto e riportato nel paper accanto alla prevalenza dei fallimenti.
3. **"Non cambiato" va inteso in due sensi.** Il test che *non è cambiato* ha due destini: essere stato cancellato (il 64% qui) o essere cresciuto per accumulo (quelli sopravvissuti). Solo dopo questa distinzione ha senso chiedersi se regge o si è rotto.

### 6.3 La matrice 2×2 (il cuore dell'analisi)

Per ogni file di test, su una finestra di osservazione (es. gli ultimi 12 mesi di vita del repo):

|  | **Codice applicativo cambiato** | **Codice applicativo fermo** |
|---|---|---|
| **Test cambiato** | Manutenzione ordinaria | Test iper-attivo (raro, spesso flaky-fixing) |
| **Test fermo** | **TEST CONGELATO** ← il fenomeno da spiegare | Test e codice stabili (progetto maturo o morto) |

Il quadrante in basso a sinistra è il target. Un test congelato non è automaticamente un problema: **è un problema se è anche verde**, perché significa che sta "passando" senza più verificare nulla di utile. Ecco la sotto-matrice che dà il risultato più interessante:

| Test congelato + codice cambiato | Esito | Interpretazione |
|---|---|---|
| | verde | **Test di facciata**: passa perché è troppo generico o non tocca la parte cambiata |
| | rosso | **Test obsoleto**: si è rotto e nessuno lo ha aggiornato |
| | skip | **Test disabilitato**: qualcuno ha deciso di non mantenerlo |
| | non eseguito | **Test invisibile**: la CI non lo esegue più, o il file non è più nella suite |

### 6.4 Cinque indicatori da calcolare con PyDriller

| Indicatore | Definizione operativa | Cosa spiega |
|---|---|---|
| **Lag test–codice** | giorni tra ultima modifica del file di test e ultima modifica del file sorgente che il test esercita | Quanto il test è "indietro" rispetto al codice |
| **Rapporto di churn** | righe cambiate nei test / righe cambiate nel sorgente, nella finestra | Se il progetto investe nella manutenzione dei test |
| **Churn delle asserzioni** | numero di righe con `assert`/`expect` aggiunte o rimosse nel tempo | Se il test verifica ancora qualcosa o è stato svuotato |
| **Età dello skip** | giorni dall'ultimo `@Disabled`, `@Ignore`, `skip(`, `it.skip`, `xdescribe` | Quanto dura un test disabilitato prima di essere dimenticato |
| **Sopravvivenza** | tempo tra introduzione e rimozione/riscrittura del test (Kaplan-Meier) | Quanto "vivono" i test E2E |

Mappatura fra indicatori e **cause** (le 5 ipotesi da testare, non da assumere):

| Ipotesi | Come si osserva |
|---|---|
| H1 — Il test è troppo astratto/generico | poche asserzioni per test, selettori generici, nessun dato specifico |
| H2 — La CI non esegue più quel test | il test è nel repo ma non nel comando di esecuzione/configurazione CI |
| H3 — Il test è "di facciata" | copre solo il rendering iniziale, non i flussi |
| H4 — Il test è stato disabilitato e dimenticato | età dello skip alta, nessun riferimento in issue/commit |
| H5 — Il progetto è in manutenzione minima | pochi commit totali, nessuna release recente |

**Regola metodologica**: ogni caso studio va classificato con **due annotatori indipendenti** su un sotto-campione (es. 30 test), e va riportato l'accordo (Cohen's κ). Se non hai un secondo annotatore, chiedi a un collega 2 ore del suo tempo: è la differenza tra "secondo me" e "dato".

**Riusa l'impostazione di PT-LINTR.** Il tool del gruppo (§3.1) fa già, sui test JMeter, esattamente questo: per ogni commit che tocca il file, produce un'analisi e la mette in una serie storica; poi confronta versioni consecutive e classifica i commit in `introduction` / `improving` / `pejorative` / `neutral`. Tu devi fare la stessa cosa con esiti e metriche invece che con gli smell. Non riscrivere quel disegno: adottalo (e dichiaralo nel metodo, citando il paper), così i tuoi risultati sono confrontabili con i loro.

### 6.5 Protocollo di codifica (una pagina, da scrivere prima di analizzare)

`docs/05_protocollo_codifica.md` deve contenere: definizione di ogni categoria, 2 esempi reali per categoria, regola di precedenza quando un caso ricade in due categorie, cosa fare nei casi dubbi (`uncertain` è una categoria legittima, meglio di una forzatura), e la procedura di doppia codifica.

---

## 7. Pipeline e protocollo per repository

### 7.1 Architettura

```text
selezione → clone @commit → setup (Docker) → esecuzione test → parsing report
   → normalizzazione → triage automatico → DB risultati → analisi
```

### 7.2 Protocollo per singolo repository (12 passi, sempre gli stessi)

1. Leggi il record del repo da `gui_testing_repo_details` (framework, n. test, linguaggio).
2. Clona a un commit specifico; **registra l'hash** (riproducibilità).
3. Rileva lo stack (presenza di `pom.xml`, `build.gradle`, `package.json`, `requirements.txt`).
4. Scegli l'immagine Docker dello stack.
5. Setup dipendenze con **timeout 45 minuti**.
6. Se il setup fallisce → `setup_failed` + causa + passa al successivo.
7. Individua il comando di esecuzione dei test (da README, CI config, o convenzione dello stack).
8. Esegui con **timeout 20 minuti** e browser headless.
9. Cattura exit code, stdout/stderr, report XML/JSON.
10. Normalizza i risultati in un record per test.
11. Classifica con la precedenza di §7.4.
12. Salva `results/<repo_id>/meta.json`, `logs/`, `reports/`.

### 7.3 Schema del risultato (un file per repository)

```json
{
  "repo_id": 42,
  "url": "https://github.com/owner/project",
  "commit": "a1b2c3d",
  "dataset_version": "v3 / 2024-11-28",
  "stack": "java-maven",
  "framework": "selenium",
  "status": "executed",
  "setup": { "ok": true, "seconds": 1240, "log": "logs/setup.log" },
  "run": { "ok": true, "exit_code": 1, "seconds": 380, "java": "11", "browser": "chrome-119" },
  "tests": { "total": 120, "passed": 90, "failed": 20, "skipped": 10 },
  "failure_categories": { "infra": 12, "genuine_regression": 1, "obsolete": 7 },
  "notes": "richiede un DB MySQL non disponibile in CI"
}
```

### 7.4 Precedenza nella classificazione (importante per la validità)

Un repository può avere più problemi insieme. L'ordine di precedenza è:

```text
setup_failed  >  not_executed  >  timeout  >  failed  >  passed
```

Motivo: un repo con setup fallito e 0 test eseguiti **non** deve essere contato come "0% di test falliti". Se non fissi la precedenza prima, due persone (o due script) producono numeri diversi sugli stessi dati. Scrivila nel protocollo.

### 7.5 Throughput: fai i conti prima di promettere 100 repo

Stima realistica per repository: 2 min clone + 20–40 min setup + 5–20 min esecuzione + 5 min triage = **35–70 minuti**. Con 100 repository sono **60–120 ore macchina**. Con 5 container in parallelo: **12–24 ore di muro**, *se tutto va bene al primo colpo*. Il tasso di successo al primo tentativo su progetti di 2–5 anni è realisticamente **40–60%** (stima da confermare col pilota di settimana 4), quindi servono 2–3 iterazioni → **100–150 ore effettive**.

Conclusione: l'esecuzione da sola occupa **5–6 settimane** se ci lavori in parallelo all'analisi. Non è compatibile con "eseguo e poi analizzo": il piano di §8 le sovrappone.

---

## 8. Piano di lavoro — 20 settimane

Legenda: **D** = deliverable · **G** = gate.

### Fase 0 — Recupero del contesto e setup (sett. 1–2, 26/10 → 6/11)

| Sett. | Date | Obiettivo | Attività | D / G |
|---|---|---|---|---|
| 1 | 26–30/10 | Recuperare l'esistente, capire il dataset | Download `E2EGit.db` in background · lettura C4 + C5 con schede · **questionario §2.1 al professore** · `PRAGMA table_info` su 5 tabelle · stima spazio disco e accesso macchina | **D**: `docs/02_schema.md` + scheda C4 · **G0** scelta progetto |
| 2 | 2–6/11 | Avere i numeri del dataset e un modello di pipeline | Conteggi (472 repo, 410 test perf, 13 con entrambi) · distribuzione per framework/linguaggio · distribuzione dei test per repo · verifica della versione Zenodo e pin · **prova di PT-LINTR su 1 `.jmx`** (§3.1): ti fa vedere in concreto cosa significa "una versione per commit" | **D**: `docs/03_dataset.md` con numeri riprodotti · **G1** criteri di stratificazione approvati |

### Fase 1 — Selezione dei 100 repository (sett. 3–4, 9/11 → 20/11)

| Sett. | Date | Obiettivo | Attività | D / G |
|---|---|---|---|---|
| 3 | 9–13/11 | Lista candidati | Stratificazione (framework, stack, età, attività, dimensione) · 120–130 candidati con margine 20–30% · per ognuno: URL, framework, comando atteso, dipendenze, Dockerfile sì/no, n. test | **D**: `docs/04_selezione.md` + `data/candidati.csv` |
| 4 | 17–20/11 | Pilota su 10 repo | Setup + esecuzione su 10 repository eterogenei · **misura il tempo reale per repo** · stima il tasso di eseguibilità | **D**: `results/pilota.md` · **G2 = GO/NO-GO sul perimetro** |

**G2 (20/11) è il gate che salva il progetto.** Criterio: se il tasso di eseguibilità del pilota è **<50%**, non si va a 100: si scende a 50 repository (o si cambiano i criteri di selezione). Meglio 50 repo solidi di 100 fantasma. Questa decisione va scritta nel verbale.

### Fase 2 — Pipeline in due binari (sett. 5–7, 23/11 → 11/12)

La pipeline si sdoppia, perché i due binari non dipendono l'uno dall'altro e possono avanzare in parallelo.

**Binario A — storia Git (domande 1–3 di §6.2).** Non richiede Docker né ambienti: si può fare *subito*, anche prima della selezione, ed è l'unica parte che dà risultati certi e riproducibili. Se la parte di esecuzione si arenasse (tasso di eseguibilità basso), questo binario produce comunque una tesi.

**Binario B — esecuzione (domanda 4 di §6.2).** Richiede Docker, ambienti e tempo macchina. Dipende dalla selezione.

| Sett. | Date | Binario | Obiettivo | Attività | D / G |
|---|---|---|---|---|---|
| 5 | 23–27/11 | A | Storia Git su tutti i 472 | `02_storia_test.py` con `git clone --filter=blob:none` · per ogni file: esiste ancora? quante modifiche tra SHA e HEAD? diff `--stat` · risultati in CSV | **D**: `results/storia_test.csv` |
| 5–6 | 23/11–4/12 | B | Orchestrazione | Script unico `run_repo.py` con i 12 passi · gestione timeout e retry · normalizzazione report (JUnit XML, Playwright JSON, Cypress JSON) · DB risultati | **D**: pipeline che gira su 3 repo con un comando |
| 6 | 30/11–4/12 | A | Lettura dei diff | Classificazione automatica dei diff: riformattazione / bump di versione / cambio di asserzioni / cambio di selettori | **D**: `results/diff_classificati.csv` |
| 6 | 30/11–4/12 | B | Robustezza | Test su 15 repo · gestione dei casi strani (monorepo, test in sottocartelle, più framework nello stesso repo) · log leggibili | **D**: `docs/06_pipeline.md` |
| 7 | 7–11/12 | B | Batch 1 in produzione | Prime 25 repo in batch notturni · triage preliminare | **D**: `results/batch1/` · **G3** pipeline congelata |

### Fase 3 — Esecuzione e triage (sett. 8–13, 14/12 → 22/01)

| Sett. | Date | Obiettivo | Attività | D |
|---|---|---|---|---|
| 8 | 14–18/12 | Batch 2 (25 repo) | Esecuzione + triage · prime classificazioni dei fallimenti | 50/100 |
| 9–10 | 21/12 → 1/01 | Bassa intensità | Solo lanci batch e scrittura del protocollo di codifica. **Nessuna decisione di design in queste due settimane** | 65/100 |
| 11 | 4–8/01 | Batch 3 (25 repo) | Esecuzione + sostituzione con riserve | 90/100 |
| 12 | 11–15/01 | Chiusura perimetro | Ultimi 10 + riserve · **ondata 2 sui repo con fallimenti** (per separare flakiness da fallimenti deterministici) | 100/100 |
| 13 | 18–22/01 | Classificazione | Applicazione del protocollo a tutti i fallimenti · doppia codifica su un sotto-campione | **D**: DB risultati completo + κ |

**Ondata 2 (flakiness)**: non rieseguire i repo tutti verdi. Solo quelli con ≥1 fallimento o esiti sospetti, 2–3 ripetizioni. Se un test cambia esito, è `flaky` e va in una categoria separata: non è né rotto né sano.

### Fase 4 — Analisi (sett. 14–17, 25/01 → 19/02)

| Sett. | Date | Obiettivo | Attività | D |
|---|---|---|---|---|
| 14 | 25–29/01 | Analisi quantitativa | Tasso di eseguibilità · distribuzione esiti · cause di fallimento per framework/linguaggio/età · **matrice 2×2** | **D**: `results/analisi_quantitativa.md` + figure |
| 15 | 1–5/02 | "Test non cambiati" | PyDriller sui 100 repo (o su un sotto-campione): lag, churn, churn asserzioni, età skip, sopravvivenza | **D**: `results/congelati.csv` |
| 16 | 8–12/02 | Casi studio | 10–20 repository / 100–200 test · 3–5 casi narrativi con estratti di codice, commit e log | **D**: `docs/casi_studio.md` |
| 17 | 15–19/02 | Minacce alla validità | Interna, esterna, di costrutto, riproducibilità · discussione del κ | **D**: `docs/07_minacce.md` |

### Fase 5 — Documentazione e rilascio (sett. 18–20, 22/02 → 12/03)

| Sett. | Date | Obiettivo | Attività | D |
|---|---|---|---|---|
| 18 | 22–26/02 | Relazione: scheletro + risultati | Scrivi mentre i numeri sono freschi | Bozza §1–4 |
| 19 | 1–5/03 | Relazione completa | Discussione, minacce, lavoro futuro · revisione con il professore | Bozza completa |
| 20 | 8–12/03 | Consegna e rilascio | README, Dockerfile, dati aggregati anonimizzati · repo pubblico | Relazione + artefatti |

---

## 9. Calendario dei martedì (ricevimento, mattina)

**Regola operativa**: email **lunedì entro le 18:00**; 10 minuti al ricevimento; si porta un artefatto e una decisione, non un racconto.

| # | Data | Cosa porti | Decisione che chiedi | Note |
|---|---|---|---|---|
| 1 | **mar 27/10** | Scelta progetto · scheda C4 · schema del DB letto · questionario §2.1 | (a) cosa è già stato fatto e dove sono gli artefatti? (b) posso riusare la pipeline? (c) macchina con Docker e 250 GB? (d) 100 repo è un requisito o un obiettivo? (e) accesso a `squidslab/pt-lintr` (il repo è 404) | Primo incontro, porta le 10 domande di §13 |
| 2 | **mar 3/11** | Numeri del dataset + criteri di stratificazione | Approvi i criteri? Il mix 40/30/30 tra framework va bene? | |
| 3 | **mar 10/11** | Lista 120 candidati + piano del pilota | La lista va bene? Ci sono repo da escludere a priori (licenza, troppi test)? | |
| 4 | **mar 17/11** | Risultati del pilota: tasso di eseguibilità reale, tempo medio per repo | **GO/NO-GO sul perimetro**: 100 o 50? | Il gate più importante |
| 5 | **mar 24/11** | Pipeline che gira su 3 repo (demo 2 min) | Posso congelare la pipeline e passare alla produzione? | |
| 6 | **mar 1/12** | Batch 1 (25 repo) + prime cause di fallimento | La tassonomia va bene? Manca una categoria? | |
| 7 | **mar 8/12** | *Nessun ricevimento (Immacolata)* | — | Email con lo stato del batch 2 |
| 8 | **mar 15/12** | 50/100 + protocollo di codifica scritto | Approvi il protocollo? Chi può fare la seconda codifica? | Serve una persona per il κ |
| 9 | **mar 22/12** | *Sospensione natalizia (presunta)* | — | Batch in corso, email di 3 righe |
| 10 | **mar 29/12** | *Sospensione natalizia (presunta)* | — | — |
| 11 | **mar 5/01** | 65–90/100 + problemi ricorrenti | Come gestiamo i repo che richiedono servizi esterni? | |
| 12 | **mar 12/01** | 100/100 + piano dell'ondata 2 | Quante ripetizioni per la flakiness? | |
| 13 | **mar 19/01** | DB risultati completo + κ | La classificazione regge? Casi dubbi da rivedere insieme? | Porta 5 casi dubbi concreti |
| 14 | **mar 26/01** | Analisi quantitativa + matrice 2×2 | La storia che racconto è quella che interessa al gruppo? | |
| 15 | **mar 2/02** | Analisi dei "congelati" | Quali 3 casi studio scelgo? | |
| 16 | **mar 9/02** | Bozza dei casi studio | Vanno bene come narrativa? | |
| 17 | **mar 16/02** | Minacce alla validità | Manca qualcosa che i revisori attaccherebbero? | |
| 18 | **mar 23/02** | Scheletro della relazione | Struttura e lunghezza vanno bene? | |
| 19 | **mar 2/03** | Bozza avanzata | Cosa taglio? | |
| 20 | **mar 9/03** | Versione finale | Consegna e rilascio | |

**Se un martedì salta**: l'email parte lo stesso, con lo stato e il prossimo passo. Il silenzio viene letto come stallo.

---

## 10. Come si scrive l'aggiornamento (template)

### 10.1 Email del lunedì (max 120 parole)

```text
Oggetto: [Tirocinio][Prog2] Settimana 8 — <Nome>

Buongiorno Prof. <Cognome>,
aggiornamento breve prima del ricevimento di domani.

Fatto: 50 repository eseguiti su 100; pipeline stabile; protocollo di codifica scritto.
Numeri: 38 eseguibili su 50 (76%); 1.240 test eseguiti, 812 passati (65%), 297 falliti, 131 skippati.
Blocco: 12 repository usano un database MySQL esterno; senza quello non partono.
Mi serve una decisione: (a) li classifico come "setup fallito" o provo a dockerizzare il DB? (b) il tempo per dockerizzare vale il 12% del campione?

Grazie,
<Nome>
```

Un numero, un blocco, una domanda chiusa. Sempre in quest'ordine.

### 10.2 Agenda dei 10 minuti

| Min | Cosa |
|---|---|
| 0–2 | Mostra l'artefatto: tabella dei risultati, non una slide |
| 2–5 | I 3 numeri che contano |
| 5–9 | Le domande, dalla più importante. Annota le risposte mentre parla |
| 9–10 | "Quindi per martedì prossimo le porto X". Data e artefatto, non "continuo" |

### 10.3 Verbale (entro 2 ore)

`docs/verbali/2026-10-27.md`:

```markdown
# 2026-10-27 — Ricevimento
Presenti:
## Decisioni
1. Perimetro confermato a 100 repository, con riserve. Soglia di uscita: <50% di eseguibilità → 50 repo.
## Azioni
- [ ] Recuperare la pipeline del tirocinante precedente — entro 2026-11-03
- [ ] Chiedere accesso alla macchina con Docker — entro 2026-11-03
## Domande aperte
- ...
## Prossimo incontro: 2026-11-03
```

Se le decisioni cambiano il piano, manda un recap di 3 righe entro sera.

### 10.4 Quando scrivere fuori dal martedì

Solo per: (1) blocco >48 ore che impedisce il deliverable settimanale; (2) decisione con scadenza (gate sul perimetro, accesso alla macchina); (3) problemi etici o di licenza. Massimo 2–3 volte in tutto il tirocinio.

---

## 11. Deliverable e struttura della relazione

| Deliverable | Quando | Dove |
|---|---|---|
| Schema del DB documentato | sett. 1 | `docs/02_schema.md` |
| Criteri di selezione + lista 100 (+ riserve) | sett. 3 | `docs/04_selezione.md` |
| Report del pilota | sett. 4 | `results/pilota.md` |
| **Storia Git dei 8.601 file di test** (esistono? quanti tocchi? cosa è cambiato) | sett. 5 | `results/storia_test.csv` |
| Diff classificati (riformattazione / versione / asserzioni / selettori) | sett. 6 | `results/diff_classificati.csv` |
| Pipeline di esecuzione funzionante | sett. 7 | `src/` + `docker/` |
| DB dei risultati (100 repo) | sett. 13 | `results/results.db` |
| Analisi quantitativa + matrice 2×2 | sett. 14 | `results/analisi_quantitativa.md` |
| Analisi dei test congelati | sett. 15 | `results/congelati.csv` |
| Casi studio | sett. 16 | `docs/casi_studio.md` |
| Minacce alla validità | sett. 17 | `docs/07_minacce.md` |
| Relazione finale | sett. 20 | `docs/relazione/` |
| Artefatti pubblici (pipeline + dati aggregati) | sett. 20 | GitHub + Zenodo |

**Struttura della relazione** (20–30 pagine):

| Capitolo | Pagine | Contenuto |
|---|---|---|
| 1. Introduzione | 2 | Perché i test E2E invecchiano; la domanda; il contributo |
| 2. Lavoro correlato | 3 | E2EGit, C5, J8, letteratura su test maintenance e flakiness |
| 3. Dataset e selezione | 3 | E2EGit, versione usata, stratificazione, lista finale |
| 4. Metodo | 5 | Pipeline, protocollo per repo, tassonomia, protocollo di codifica, κ |
| 5. Risultati | 7 | Eseguibilità, esiti, cause, matrice 2×2, indicatori, per framework/stack |
| 6. Casi studio | 3 | 3–5 narrative |
| 7. Minacce alla validità | 2 | Interna, esterna, costrutto, riproducibilità |
| 8. Conclusioni e lavoro futuro | 1 | Risposta alla domanda + 3 estensioni |

---

## 12. Rischi e contromisure

| Rischio | Probabilità | Impatto | Contromisura |
|---|---|---|---|
| Tasso di eseguibilità basso (<50%) | Alta | Alto | Gate G2 al 20/11; piano B a 50 repo, deciso *prima* |
| Arenarsi su un repository | Alta | Medio | Time-box 45 min; `setup_failed` e avanti; nessuna eccezione |
| Spazio disco insufficiente a metà | Media | Alto | Verifica in sett. 1, non in sett. 8; clona con `--depth 1` |
| Servizi esterni (DB, API) non disponibili | Alta | Medio | Categoria `setup_failed` esplicita + conteggio a parte nel paper |
| Classificazione dei fallimenti ambigua | Alta | Alto | Protocollo scritto prima + doppia codifica + categoria `uncertain` |
| Rifare il lavoro di chi c'era prima | Media | Alto | Questionario §2.1 al primo incontro |
| Scope creep ("aggiungo anche i test di performance") | Media | Medio | Il perimetro è nel verbale; le aggiunte passano dal martedì |

---

## 13. Domande da portare al primo incontro (27/10)

1. Cosa è già stato fatto, da chi, e dove sono gli artefatti (repo, DB, log, macchina)?
2. Esiste una pipeline? La riuso o la riscrivo?
3. Quali repository sono già stati eseguiti e con quale esito?
4. Il perimetro di 100 repository è un requisito o un obiettivo? Posso scendere a 50 se l'eseguibilità è bassa?
5. Ho accesso a una macchina con Docker e ~250 GB di disco? Posso lasciarla accesa per batch notturni?
6. Posso usare i risultati del gruppo (C5, J8, PT-LINTR, E2E-Loader) come baseline? In particolare: **il repo `squidslab/pt-lintr` oggi risponde 404** — esiste una versione più recente del pacchetto Zenodo, o posso avere accesso al repo?
7. Esiste un protocollo di classificazione dei fallimenti già concordato?
8. La domanda "perché i test non cambiano" ha già una risposta parziale in C5/J8 che devo replicare o estendere?
9. Formato, lunghezza e scadenza della relazione di tirocinio?
10. Se il lavoro diventa un paper, come si gestiscono autoria e citazione?

---

## 14. Checklist master

**Settimana 1**
- [ ] `E2EGit.db` scaricato e md5 verificato
- [ ] Versione Zenodo annotata (v3? latest?)
- [ ] `PRAGMA table_info` sulle 5 tabelle → `docs/02_schema.md`
- [ ] Schede di lettura di C4 e C5
- [ ] Questionario §2.1 inviato al professore
- [ ] Spazio disco e Docker verificati
- [ ] Email del lunedì inviata + verbale scritto

**Gate G2 (20/11)**
- [ ] 10 repo del pilota eseguiti (o tentati)
- [ ] Tempo medio per repo misurato
- [ ] Tasso di eseguibilità calcolato
- [ ] Decisione 100 / 50 scritta nel verbale

**Prima dell'analisi (19/01)**
- [ ] 100 repo con `meta.json` completo
- [ ] Precedenza di classificazione applicata in modo uniforme
- [ ] Ondata 2 (flakiness) fatta sui repo con fallimenti
- [ ] Doppia codifica su ≥30 casi, κ calcolato
- [ ] Protocollo di codifica versionato

**Prima della consegna**
- [ ] Versione del dataset citata con DOI e data
- [ ] Hash dei commit usati documentati
- [ ] Versioni di browser/driver/JDK documentate
- [ ] Riproducibilità: un comando rifà la pipeline
- [ ] Dati personali assenti o anonimizzati
- [ ] Licenze dei repository rispettate

---

## 15. Registro delle decisioni

`docs/00_decisioni.md`:

| Data | Decisione | Motivazione | Chi | Impatto |
|---|---|---|---|---|
| 2026-10-23 | Preparare le guide per entrambi i progetti prima di scegliere | Confronto informato | Paolo | — |
| | | | | |

---

*Guida redatta il 23 ottobre 2026. Informazioni su dataset, paper e tool verificate alla stessa data sulle fonti ufficiali. Le date dei ricevimenti sono ipotizzate settimanali al martedì mattina e vanno confermate con il professore.*
