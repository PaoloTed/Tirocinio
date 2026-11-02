# Documento Riassuntivo Completo: Analisi dei Progetti di Tirocinio

## Università degli Studi di Napoli Federico II — Proposta di Tirocinio Interno

---

## Indice

1. [Premessa e Contesto](#1-premessa-e-contesto)
2. [Parte I — Analisi Comparativa dei Due Progetti](#2-parte-i--analisi-comparativa-dei-due-progetti)
   - 2.1 [Prog1: Tool di Analisi per Agent Skills (GitSkills / MSR 2027)](#21-prog1-tool-di-analisi-per-agent-skills-gitskills--msr-2027)
   - 2.2 [Prog2: Esecuzione e Manutenzione di Test E2E (E2EGit)](#22-prog2-esecuzione-e-manutenzione-di-test-e2e-e2egit)
   - 2.3 [Tabella di Confronto Sintetico](#23-tabella-di-confronto-sintetico)
3. [Parte II — Guida Operativa Dettagliata: Prog1](#3-parte-ii--guida-operativa-dettagliata-prog1)
4. [Parte III — Guida Operativa Dettagliata: Prog2 (con perimetro a 100 repository)](#4-parte-iii--guida-operativa-dettagliata-prog2-con-perimetro-a-100-repository)
5. [Parte IV — Rilevanza per la Carriera e Possibilità Lavorative](#5-parte-iv--rilevanza-per-la-carriera-e-possibilità-lavorative)
6. [Conclusioni e Raccomandazioni Finali](#6-conclusioni-e-raccomandazioni-finali)
7. [Riferimenti e Link Utili](#7-riferimenti-e-link-utili)

---

## 1. Premessa e Contesto

Il presente documento consolidato riassume l'analisi completa di due progetti di tirocinio interno proposti da un professore dell'Università degli Studi di Napoli Federico II. I due progetti afferiscono a due sotto-campi distinti ma complementari dell'Ingegneria del Software:

- **Prog1 (NUOVO)**: Mining di repository e costruzione di un tool di analisi per *Agent Skills* (`SKILL.md`), con parallelo sulla MSR 2027 Mining Challenge e sul dataset GitSkills.
- **Prog2 (CONTINUO DI UNO GIÀ AVVIATO)**: Esecuzione e manutenzione di test end-to-end (E2E) sul dataset E2EGit, con un perimetro concordato di **100 repository**.

La scelta tra i due dipende dalla propensione personale: il Prog1 è più orientato alla **costruzione di tool e all'analisi dati su un fenomeno emergente** (AI agent skills); il Prog2 è più orientato all'**ingegneria del software concreta, al debugging e all'analisi empirica** su progetti reali.

---

## 2. Parte I — Analisi Comparativa dei Due Progetti

### 2.1 Prog1: Tool di Analisi per Agent Skills (GitSkills / MSR 2027)

#### 2.1.1 Descrizione sintetica

Il progetto prevede la realizzazione di un **tool di analisi statica e mineraria** per repository che ospitano *Agent Skills*, ovvero artefatti software di nuova generazione pensati per gli agenti basati su modelli linguistici (LLM). L'obiettivo è "vedere l'andamento del progetto: commit, commenti alle commit, errori, code smells, ecc.", con un **parallelo** sul dataset della **MSR 2027 Mining Challenge**. In sostanza, si vuole costruire una pipeline che, a partire dai repository GitHub contenenti file `SKILL.md`, estragga metriche di processo e di prodotto, per poi applicarle su larga scala al dataset GitSkills.

#### 2.1.2 Analisi dei link e dei concetti chiave

**a) PyDriller (framework di mining)**

PyDriller è un framework Python per il mining di repository Git. Permette di aprire un repository e iterare sui commit, ottenendo informazioni dettagliate su ciascuna modifica. È altamente configurabile e può calcolare metriche strutturali sui file modificati appoggiandosi a **Lizard**, un analizzatore di codice sorgente multi-linguaggio. Nel contesto del progetto, PyDriller sarebbe il motore naturale per l'estrazione dei dati di processo (commit, commenti, autori, timestamp, file toccati). **Limite**: PyDriller e Lizard sono progettati per codice sorgente tradizionale, non per artefatti principalmente in linguaggio naturale come i file `SKILL.md`. Questo impone un adattamento delle metriche e delle euristiche di "code smell".

**b) GitSkills e MSR 2027 Mining Challenge**

GitSkills è il primo dataset su larga scala di *agent skills*: contiene **3.797.117 occorrenze di file `SKILL.md`** provenienti da **282.200 repository pubblici** di GitHub, riconducibili a **195.841 account**, raccolte nel luglio 2026. Il dataset include anche **7.264.865 file accessori** e **458.548 storie di commit** campionate con autori anonimizzati. La MSR 2027 Mining Challenge invita la comunità a esplorare questi artefatti, chiedendosi come vengono scritti, riutilizzati e mantenuti. Il bando è aperto sia a GitSkills sia a **SpecMine** (un corpus di artefatti di *Spec-Driven Development*).

La sfida scientifica è duplice: le *skill* sono scritte in linguaggio naturale, la loro selezione a runtime è **probabilistica**, non esiste un compilatore o un type checker, e non c'è un registry centrale; la diffusione avviene per **copia diretta tra repository**. La **mancanza di metriche consolidate** rende il progetto intrinsecamente esplorativo: definire cosa sia un "code smell" in una `SKILL.md` è parte stessa della ricerca.

#### 2.1.3 Tematiche affrontate

- Mining di repository software (Git, commit history, autori, commenti).
- Analisi della qualità di artefatti non tradizionali: skill per agenti LLM.
- Definizione e adattamento di metriche: dai classici code smell a smell specifici per il dominio delle skill.
- Visualizzazione e monitoraggio dell'evoluzione di un progetto.
- Riproducibilità e scalabilità su dataset da milioni di file.

#### 2.1.4 Complessità

**Medio-alta**, distribuita su più dimensioni:

1. **Tecnica**: costruire un tool modulare che integri PyDriller, un layer di parsing delle `SKILL.md`, un motore di regole per gli smell e una dashboard.
2. **Scientifica**: non esiste letteratura consolidata sugli "smell" delle agent skill. Bisogna giustificare le metriche e validarle.
3. **Di scala**: il dataset è dell'ordine di milioni di file; servono efficienza, database (SQLite/Parquet), caching e campionamento ragionato.
4. **Di validazione**: confrontare i risultati con un'analisi manuale su un campione o correlare gli indicatori con esiti osservabili.

#### 2.1.5 Tempo richiesto

Stima realistica per un tirocinio curriculare (3–6 mesi a tempo parziale, o 2–4 mesi full-time):

- **Settimane 1–3**: studio del dominio e definizione delle metriche.
- **Settimane 4–8**: sviluppo della pipeline di estrazione e primo prototipo.
- **Settimane 9–12**: implementazione delle euristiche di smell e visualizzazioni.
- **Settimane 13–16**: applicazione al dataset, analisi dei risultati, stesura della relazione.
- **Coda**: iterazioni e documentazione.

#### 2.1.6 Aspetto innovativo

**Molto alto** per tre motivi: GitSkills è un dataset nuovissimo (2026) e la MSR 2027 Mining Challenge è un'occasione competitiva; il progetto costruisce un tool nuovo per un tipo di artefatto mai analizzato sistematicamente; il tema delle agent skills è strategico (Anthropic ha introdotto il formato `SKILL.md` nell'ottobre 2025 e in pochi mesi sono comparsi milioni di file).

#### 2.1.7 Stimolazione intellettuale

Molto stimolante per chi è interessato a **AI engineering**, **software analytics** e **ricerca empirica**. Consente di lavorare su un tema di frontiera, acquisire competenze su PyDriller, Git, database e pipeline dati, e ottenere potenzialmente un contributo pubblicabile. Il rovescio della medaglia è che l'assenza di metriche consolidate può generare frustrazione.

---

### 2.2 Prog2: Esecuzione e Manutenzione di Test E2E (E2EGit)

#### 2.2.1 Descrizione sintetica

Il progetto è la **continuazione di un'attività già avviata** e si concentra sull'**esecuzione end-to-end** di test appartenenti al dataset **E2EGit**. L'obiettivo operativo è: "eseguire i test e verificare perché non sono cambiati, se reggono o si sono rotti". Si tratta di rieseguire suite di test E2E (GUI e performance) su progetti open source, confrontare i risultati con lo stato atteso, classificare i fallimenti e analizzare le cause per cui un test "non cambia" pur in presenza di evoluzione del codice. Il progetto si colloca nell'intersezione tra **test maintenance**, **regression testing** e **empirical software engineering**.

#### 2.2.2 Analisi dei link e dei concetti chiave

**a) IEEE Xplore — E2EGit: A Dataset of End-to-End Web Tests in Open Source Projects**

Il documento IEEE (DOI 10.1109/MSR66628.2025.00121) presenta **E2EGit**, un dataset di progetti web open source non banali che adottano test E2E. Il dataset è stato costruito analizzando **oltre 5.000 repository web** in Java, JavaScript, TypeScript e Python, identificando **472 repository** con **43.670 test GUI automatizzati** (Selenium, Playwright, Cypress, Puppeteer) e **84 repository** con **271 test di performance** (JMeter, Locust); **13 repository** implementano entrambe le tipologie.

**b) Zenodo — Record 14234731 (E2EGit dataset)**

Il record Zenodo fornisce il dataset vero e proprio, in versione v3 (28 novembre 2024). Il dataset è distribuito come **database SQLite** (e file SQL) con **cinque tabelle**: `repository`, `non_trivial_repository`, `gui_testing_test_details`, `gui_testing_repo_details`, `performance_testing_test_details`. La tabella `repository` contiene informazioni su **1,5 milioni di repository**; la tabella `non_trivial_repository` elenca i repository che hanno superato i filtri; le tabelle `gui_testing_test_details` e `gui_testing_repo_details` contengono, rispettivamente, una riga per file di test e un riepilogo per repository; la tabella `performance_testing_test_details` contiene **410 righe**. Il dataset ha una dimensione complessiva di **4,2 GB**.

**c) PDF "C4" — Valeria Pontillo (E2EGit paper)**

Il PDF ospitato sul sito di Valeria Pontillo è il paper completo di E2EGit, presentato alla MSR 2025. Gli autori includono Sergio Di Meglio, Luigi Libero Lucio Starace, Valeria Pontillo, Ruben Opdebeeck, Coen De Roover e Sergio Di Martino, con affiliazioni all'Università di Napoli Federico II e al SOFT Lab della Vrije Universiteit Brussel. Il paper chiarisce la distinzione tra **GUI testing** e **performance testing** e sottolinea che, nonostante l'importanza riconosciuta, l'adozione e la manutenzione dei test E2E sono spesso trascurate e la ricerca empirica su di esse è limitata.

**d) Valeria Pontillo — contesto di ricerca**

La pagina personale di Valeria Pontillo conferma che la sua ricerca si concentra su **Software Testing, Software Quality e Software Maintenance and Evolution**. Il progetto E2EGit ha già generato lavori derivati, come **PT-Linter** per il rilevamento di "bad practice" nei test di performance e **E2E-Loader** per il caricamento e l'analisi dei test. Questo è un segnale importante: il progetto fa parte di un **ecosistema di ricerca attivo** con prospettive di continuazione.

#### 2.2.3 Tematiche affrontate

- Test end-to-end (E2E): test GUI e test di performance su applicazioni web reali.
- Esecuzione e riproducibilità dei test: gestione di ambienti, dipendenze, browser, driver, configurazioni.
- Manutenzione dei test: perché i test "non cambiano", quando diventano obsoleti.
- Regression testing e classificazione dei fallimenti.
- Flakiness e fragilità dei test E2E.
- Empirical Software Engineering: misurazione, campionamento, validazione.

#### 2.2.4 Complessità

**Alta**, per i seguenti motivi:

1. **Infrastrutturale**: eseguire test E2E reali significa allestire ambienti per progetti diversi, con stack eterogenei, dipendenze non più disponibili, versioni di browser e driver obsolete.
2. **Di classificazione**: stabilire "perché un test non è cambiato" e "se regge o si è rotto" richiede un protocollo di analisi e competenza tecnica e di dominio.
3. **Di scala e costo computazionale**: eseguire migliaia di test GUI e di performance è oneroso in termini di tempo e risorse.
4. **Di riproducibilità**: documentare le condizioni di esecuzione, le versioni e le configurazioni è essenziale ma richiede rigore.

#### 2.2.5 Tempo richiesto

Poiché il progetto è la continuazione di un'attività già avviata, una parte del lavoro preliminare potrebbe essere già stata fatta. Tuttavia, la fase di esecuzione e analisi è intrinsecamente lunga. Con il perimetro a **100 repository** (si veda la Parte III), la stima è di circa **20 settimane** (5 mesi) a tempo pieno, o 6–8 mesi a tempo parziale.

#### 2.2.6 Aspetto innovativo

**Alto ma di natura diversa** rispetto al Prog1. E2EGit è un dataset già pubblicato e riconosciuto (MSR 2025), quindi il progetto non costruisce il dataset, ma ne sfrutta il potenziale per uno studio empirico originale. L'aspetto innovativo risiede nel focus sulla **manutenzione e sull'evoluzione dei test E2E**, un'area in cui la letteratura è ancora scarsa. Mentre la maggior parte degli studi si concentra sulla generazione o sull'efficacia dei test, questo progetto si chiede **cosa succede ai test nel tempo**.

#### 2.2.7 Stimolazione intellettuale

Molto stimolante per chi ha una **propensione pratica all'ingegneria del software**, ama il debugging, la configurazione di ambienti e l'analisi delle cause profonde. Offre contatto diretto con progetti reali, sviluppo di competenze su framework di test E2E, comprensione concreta dei problemi di flakiness e regressione. Le sfide possono essere frustranti (ambienti che non funzionano, dipendenze mancanti), ma il progetto è altamente formativo.

---

### 2.3 Tabella di Confronto Sintetico

| Dimensione | Prog1 (Agent Skills Tool) | Prog2 (E2EGit Maintenance) |
|---|---|---|
| **Natura** | Costruzione di tool + mining su dataset nuovo | Esecuzione empirica su dataset consolidato |
| **Oggetto** | Artefatti in linguaggio naturale (`SKILL.md`) | Test E2E (GUI e performance) |
| **Competenze tecniche** | Python, PyDriller, parsing, database, visualizzazione | Ambienti di test, framework E2E, debugging, SQLite |
| **Complessità** | Medio-alta (scientifica e di design) | Alta (infrastrutturale e interpretativa) |
| **Tempo** | 4–6 mesi (con perimetro circoscritto) | ~5 mesi full-time (100 repository) |
| **Innovazione** | Molto alta (frontiera AI agent skills, MSR 2027) | Alta (manutenzione E2E, area poco esplorata) |
| **Stimolazione** | Intellettuale, esplorativa, "pionieristica" | Pratica, ingegneristica, "da trincea" |
| **Rischio principale** | Euristiche non validate, risultati inconcludenti | Fallimenti infrastrutturali, tempi imprevedibili |
| **Potenziale pubblicazione** | Sì (MSR 2027 Mining Challenge) | Sì (contributo empirico, continuazione di linea attiva) |

---

## 3. Parte II — Guida Operativa Dettagliata: Prog1

### Fase 0 — Setup e comprensione del dominio (Settimane 1–2)

**Obiettivo**: capire cosa sono le agent skill, come è fatto il dataset e quali domande di ricerca hanno senso.

1. **Leggi il preprint di GitSkills** (arXiv:2608.10906). Punti chiave:
   - Una skill è una cartella con un file `SKILL.md` e, opzionalmente, script e file di riferimento.
   - Il formato è stato introdotto da Anthropic nell'ottobre 2025 come specifica aperta.
   - Le skill sono scritte principalmente in **linguaggio naturale**, vengono selezionate **probabilisticamente** a runtime e **non hanno un compilatore o un type checker**.
   - Non esiste un registry centrale: la diffusione avviene per **copia diretta tra repository**.
   - Il dataset contiene **3.797.117 occorrenze di file `SKILL.md`** raggruppate in **1.877.981 contenuti distinti**, provenienti da **282.200 repository** e **195.841 account**, raccolti nel luglio 2026. Include anche **7.264.865 file accessori** e **458.548 storie di commit** campionate.

2. **Leggi la pagina della MSR 2027 Mining Challenge** per allineare il progetto alle aspettative della competizione.

3. **Studia la documentazione di PyDriller** (versione 1.12 o superiore). Si crea un oggetto `RepositoryMining` (o `Repository`) passando il percorso del repository, e si itera sui commit con `traverse_commits()`.

4. **Scarica il dataset GitSkills**:
   - Il dataset completo è un singolo file **SQLite** su Zenodo (DOI: 10.5281/zenodo.21875637).
   - Esiste un **mirror Parquet** su Hugging Face e un **campione** su GitHub, utili per iniziare senza scaricare l'intero dataset.

**Output della fase**: un documento di 2–3 pagine con (a) sintesi del dominio, (b) schema del dataset, (c) 3–5 domande di ricerca candidate, (d) elenco delle metriche grezze estraibili con PyDriller.

---

### Fase 1 — Definizione delle metriche e delle euristiche di "smell" (Settimane 3–4)

Questa è la fase **più delicata e innovativa**. Poiché non esistono metriche consolidate per le `SKILL.md`, devi costruire il tuo set di indicatori e giustificarlo.

**Metriche di processo (estraibili con PyDriller o da Git)**:
- Numero di commit che toccano il file `SKILL.md` (frequenza di manutenzione).
- Distribuzione temporale dei commit (attività recente vs. abbandono).
- Numero di autori distinti che hanno modificato la skill.
- Messaggi di commit: lunghezza, presenza di riferimenti a issue, parole chiave ricorrenti.

**Metriche di prodotto (sul contenuto della `SKILL.md`)**:
- Dimensione del file (numero di righe, numero di parole).
- Presenza e correttezza del **front-matter** (YAML/JSON iniziale).
- Numero di sezioni e struttura (heading, liste, esempi).
- Presenza di **script o file di riferimento** nella cartella della skill.
- **Ridondanza**: similarità con altre skill (hash del contenuto, similarità testuale).
- **Ambiguità potenziale**: uso di termini vaghi, istruzioni non verificabili, assenza di esempi concreti.
- **Accoppiamento implicito**: riferimenti a percorsi assoluti, URL esterni, credenziali, dipendenze non dichiarate.

**Euristiche di "code smell" adattate** (da validare su un campione manuale):
- *Skill orfana*: skill senza commit recenti e senza file accessori.
- *Skill monolitica*: skill troppo lunga e con molte responsabilità non separate.
- *Skill copiata*: contenuto identico o quasi identico ad altre skill nel dataset.
- *Skill non testabile*: assenza di esempi, di criteri di successo o di riferimenti a script eseguibili.

**Output della fase**: un documento di specifica delle metriche, con per ciascuna metrica (a) definizione operativa, (b) modalità di calcolo, (c) motivazione scientifica, (d) potenziale rumore o falsi positivi.

---

### Fase 2 — Sviluppo della pipeline di estrazione e del prototipo di tool (Settimane 5–8)

1. **Modulo di estrazione Git**: usa PyDriller per estrarre commit, autori, date, messaggi e file modificati per un sottoinsieme di repository. Attenzione: PyDriller è pensato per codice sorgente; per i file `SKILL.md` dovrai gestire il contenuto come testo.

2. **Modulo di parsing delle skill**: leggi il front-matter e il corpo della `SKILL.md`. Usa un parser YAML per il front-matter e tecniche di NLP leggero (regex, conteggio di sezioni, similarità con `difflib` o embedding) per le metriche testuali.

3. **Layer di memorizzazione**: salva i risultati in un database locale (SQLite va benissimo) con tabelle separate per repository, skill, commit e metriche.

4. **Primo prototipo di analisi**: implementa un sottoinsieme delle metriche e applicalo a un **campione di 50–100 repository** del dataset. Non partire dall'intero dataset: rischi di sprecare tempo in ottimizzazioni premature.

**Output della fase**: un repository Git con codice funzionante, un database popolato sul campione e un notebook (Jupyter) che mostra le prime statistiche descrittive.

---

### Fase 3 — Applicazione al dataset e analisi (Settimane 9–12)

1. **Estendi il campione**: passa da 50–100 repository a un campione più ampio e rappresentativo (ad esempio, 500–1.000 repository, stratificati per età, popolarità e framework). Usa il campione su GitHub per test rapidi e poi passa al dataset SQLite completo per le query aggregabili senza mining pesante.

2. **Esegui la pipeline** e popola il database con le metriche per l'intero campione.

3. **Analisi esplorativa**: distribuzioni, correlazioni, cluster. Domande guida:
   - Le skill "popolari" hanno più commit o sono più stabili?
   - Esiste una relazione tra dimensione della skill e frequenza di manutenzione?
   - Le skill con script allegati sono più o meno mantenute di quelle puramente testuali?
   - Quante skill sono "copiate" e quante sono originali?

4. **Validazione qualitativa**: seleziona manualmente 20–30 skill e verifica se le euristiche di smell etichettano correttamente i casi. Calcola precisione e richiamo e documenta i falsi positivi.

**Output della fase**: un report di analisi con grafici e tabelle, e una prima risposta (provvisoria) alle domande di ricerca.

---

### Fase 4 — Consolidamento, visualizzazione e scrittura (Settimane 13–16)

1. **Dashboard o report interattivo**: costruisci una visualizzazione semplice (Streamlit, Plotly, o notebook ben formattati) che mostri l'"andamento" di un repository: timeline dei commit, metriche per skill, indicatori di smell.

2. **Documentazione del tool**: README con istruzioni di installazione, esempi di utilizzo e limitazioni note.

3. **Scrittura della relazione di tirocinio** e, se i risultati sono solidi, preparazione di un **paper breve per la MSR 2027 Mining Challenge**.

4. **Rilascio dell'artefatto**: pubblica il tool su GitHub con licenza aperta e, se possibile, un piccolo dataset di metriche aggregate per favorire la riproducibilità.

---

## 4. Parte III — Guida Operativa Dettagliata: Prog2 (con perimetro a 100 repository)

### Premessa: cosa cambia con "100 repository"

Il dataset E2EGit contiene **472 repository** con test GUI e **84 repository** con test di performance (13 con entrambe le tipologie). Selezionare **100 repository** significa coprire circa il **21% dei repository GUI** del dataset. Con una media di **92,5 test GUI per repository**, 100 repository corrispondono potenzialmente a **oltre 9.000 test**, un numero che rende impraticabile l'esecuzione e l'analisi manuale di ogni singolo test. La strategia deve quindi essere **a due livelli**:

- **Livello 1 — Esecuzione e triage su larga scala**: eseguire (o tentare di eseguire) i test su tutti i 100 repository, raccogliendo esiti aggregati e classificazioni automatiche/semi-automatiche.
- **Livello 2 — Analisi approfondita su un sotto-campione**: selezionare 10–20 repository (o 100–200 test) per l'analisi qualitativa delle cause, dei test "non cambiati" e dei casi studio.

Questo approccio ibrido è l'unico sostenibile entro un tirocinio curriculare e consente di coniugare **ampiezza** (100 repository) e **profondità** (casi studio).

---

### Fase 0 — Ripresa del contesto e setup (Settimane 1–2)

**Obiettivo**: padroneggiare il dataset e preparare l'infrastruttura di lavoro.

1. **Rileggi il paper E2EGit** (MSR 2025, DOI 10.1109/MSR66628.2025.00121) e il PDF sul sito di Valeria Pontillo. Focalizzati su:
   - La distinzione tra **GUI testing** (Selenium, Playwright, Cypress, Puppeteer) e **performance testing** (JMeter, Locust).
   - I criteri di costruzione del dataset: 5.000+ repository analizzati, 472 con test GUI, 84 con test di performance.
   - La struttura del database SQLite su Zenodo (DOI 10.5281/zenodo.14234731) con le cinque tabelle: `repository`, `non_trivial_repository`, `gui_testing_test_details`, `gui_testing_repo_details`, `performance_testing_test_details`.

2. **Scarica il dataset** (4,2 GB: file `.db` da 2,4 GB e `.sql` da 1,8 GB) e aprilo con DB Browser for SQLite, DBeaver o Python (`sqlite3` + `pandas`). Esplora:
   - Quanti repository hanno test GUI e quanti test per repository (distribuzione).
   - Quali framework sono usati e con quale frequenza.
   - Quali linguaggi (Java, JavaScript, TypeScript, Python) e stack tecnologici.
   - La presenza di metadati utili.

3. **Recupera lo stato dell'arte interno**: chiedi al professore o a chi ti ha preceduto (a) quali repository sono già stati considerati, (b) se esiste una pipeline di esecuzione, (c) quali problemi infrastrutturali sono già emersi.

4. **Prepara l'infrastruttura**:
   - **Spazio disco**: 100 repository clonati possono occupare 50–200 GB.
   - **Docker**: installa Docker e prepara immagini base per i principali stack (Java/Maven, Java/Gradle, Node.js, Python).
   - **Orchestrazione**: predisponi un ambiente Python con `pandas`, `sqlite3`, `subprocess`, `jinja2`, e valuta `GNU parallel` o `concurrent.futures` per l'esecuzione parallela.
   - **Storage dei risultati**: definisci una struttura di cartelle (es. `results/<repo_id>/logs/`, `results/<repo_id>/reports/`) e un database SQLite per aggregare gli esiti.

**Output della fase**: dataset esplorato, infrastruttura pronta, lista preliminare di criteri per la selezione dei 100 repository.

---

### Fase 1 — Selezione dei 100 repository (Settimane 3–4)

Questa è la fase **decisionale più importante**. Un campione ben stratificato rende i risultati generalizzabili; un campione casuale o mal calibrato può produrre conclusioni deboli o un progetto arenato su repository impossibili da configurare.

#### 1.1 Criteri di stratificazione

Seleziona i 100 repository in modo **stratificato** rispetto a:

- **Framework di test**: almeno 3 framework rappresentati (es. Selenium, Playwright, Cypress), con proporzioni ragionevoli (es. 40% Selenium, 30% Playwright, 30% Cypress/Puppeteer).
- **Linguaggio/stack**: Java (Maven/Gradle), JavaScript/TypeScript (npm/yarn), Python (pip/poetry). Evita di sovra-rappresentare un solo stack.
- **Longevità del progetto**: repository giovani (< 2 anni), maturi (2–5 anni), storici (> 5 anni).
- **Attività recente**: repository attivi (commit negli ultimi 6 mesi) e inattivi (nessun commit recente).
- **Dimensione**: repository piccoli (< 20 test), medi (20–100 test), grandi (> 100 test).
- **Complessità infrastrutturale**: privilegia repository con dipendenze gestibili, ma includi anche alcuni casi complessi, per non distorcere il campione.

#### 1.2 Procedura operativa

1. Interroga la tabella `gui_testing_repo_details` per ottenere l'elenco dei repository con test GUI e i loro metadati.
2. Applica i criteri di stratificazione e costruisci una **lista di 120–130 repository candidati**, con un margine del 20–30% per sostituire quelli che si riveleranno ineseguibili.
3. Per ciascun candidato, annota: URL, framework, linguaggio, comando di esecuzione atteso, dipendenze principali, presenza di Dockerfile o istruzioni di setup, numero di test.
4. **Pilota su 10 repository**: prima di impegnarti sui 100, prova a configurare ed eseguire i test su 10 repository campione. Questo ti darà una stima realistica del tasso di successo e del tempo medio per repository. Se il tasso di successo è troppo basso (es. < 50%), rivedi i criteri di selezione.

#### 1.3 Documentazione della selezione

Produci una tabella con i 100 repository selezionati e le motivazioni della scelta (stratificazione), più una lista di riserva. Questo documento sarà parte della relazione finale e ti proteggerà da critiche sulla rappresentatività del campione.

**Output della fase**: lista definitiva di 100 repository (più riserve), con metadati e note infrastrutturali.

---

### Fase 2 — Pipeline di orchestrazione (Settimane 5–7)

Con 100 repository, l'esecuzione manuale è impensabile. Devi costruire una **pipeline automatizzata** che, per ciascun repository, esegua una sequenza di passi: clone → setup dipendenze → esecuzione test → raccolta risultati → triage iniziale.

#### 2.1 Architettura della pipeline

1. **Modulo di clone e checkout**: clona il repository a un commit specifico (idealmente quello usato nel dataset E2EGit, per riproducibilità) e registra l'hash. Usa `git clone --depth 1` se non ti serve la storia completa, oppure clona l'intera storia se vuoi analizzare l'evoluzione dei test.

2. **Modulo di setup**: per ciascuno stack, esegui i comandi di installazione delle dipendenze in un container Docker dedicato:
   - Java/Maven: `mvn dependency:resolve` o `mvn test-compile`.
   - Java/Gradle: `./gradlew dependencies`.
   - Node.js: `npm install` o `yarn install`.
   - Python: `pip install -r requirements.txt` o `poetry install`.
   - Cattura i log e registra se il setup è andato a buon fine.

3. **Modulo di esecuzione**: esegui il comando di test specifico per il framework:
   - Selenium/JUnit: `mvn test -Dtest=...` o `./gradlew test`.
   - Playwright: `npx playwright test`.
   - Cypress: `npx cypress run`.
   - Puppeteer: `npm test` (a seconda della configurazione).
   - Cattura exit code, stdout/stderr, e i report (XML JUnit, JSON di Playwright/Cypress).

4. **Modulo di raccolta risultati**: normalizza i risultati in un formato comune (es. un record JSON per test con: repository, file di test, nome del test, esito, durata, messaggio di errore). Salva i log completi su disco e i record aggregati in SQLite.

5. **Modulo di triage automatico**: classifica automaticamente i fallimenti in macro-categorie:
   - **Setup fallito**: il repository non si clona, le dipendenze non si installano, il build fallisce.
   - **Test non eseguito**: il framework non parte, non trova i test, o li salta tutti.
   - **Test fallito**: il test è stato eseguito ma è fallito (da approfondire in Fase 3).
   - **Test passato**: il test è passato.
   - **Timeout**: l'esecuzione supera una soglia (es. 10 minuti per repository).

#### 2.2 Gestione della parallelizzazione

- Esegui i repository in **batch paralleli** (es. 4–8 alla volta) su una macchina con sufficienti CPU e RAM. Attenzione: i test GUI sono pesanti (browser headless), quindi non esagerare con il parallelismo.
- Usa Docker per isolare le esecuzioni e evitare conflitti di dipendenze.
- Prevedi un **meccanismo di retry** per i fallimenti infrastrutturali transitori (es. timeout di rete durante `npm install`).

#### 2.3 Gestione dei casi problematici

- **Regola del time-box**: se un repository richiede più di 30–60 minuti di setup senza successo, marcalo come "setup fallito" e passa al successivo. Con 100 repository, non puoi permetterti di perdere giorni su un singolo caso.
- **Documenta i fallimenti**: per ogni repository che non parte, registra la causa (dipendenza mancante, versione incompatibile, servizio esterno non disponibile). Questi dati sono preziosi per l'analisi e per la relazione.

**Output della fase**: pipeline funzionante, testata su 10–20 repository, con risultati normalizzati e triage automatico.

---

### Fase 3 — Esecuzione e triage sui 100 repository (Settimane 8–13)

Questa è la fase **più lunga e onerosa**, ma anche quella che produce il dataset di risultati.

#### 3.1 Esecuzione in ondate

1. **Ondata 1 — Setup e prima esecuzione**: esegui la pipeline su tutti i 100 repository. Raccogli i risultati della prima esecuzione. Questa ondata può richiedere 2–4 settimane, a seconda del parallelismo e dei tempi di setup.
2. **Ondata 2 — Ripetizione per flakiness**: riesegui i test sui repository che hanno avuto almeno un fallimento o esiti sospetti, per distinguere fallimenti deterministici da flakiness. Non è necessario rieseguire i repository con tutti i test verdi.
3. **Ondata 3 (opzionale) — Verifica di casi dubbi**: per i test che cambiano esito tra le ondate, esegui ulteriori ripetizioni mirate.

#### 3.2 Classificazione dei fallimenti

Per ciascun repository e ciascun test fallito, assegna una categoria (manualmente o semi-automaticamente, con regole euritiche):

- **Regressione genuina**: il codice dell'applicazione è cambiato e il test ha correttamente rilevato un problema.
- **Test obsoleto**: l'interfaccia o il flusso applicativo è cambiato, ma il test non è stato aggiornato.
- **Problema infrastrutturale**: dipendenze mancanti, browser/driver non disponibili, URL non raggiungibile, database non inizializzato.
- **Flakiness**: esito non deterministico tra esecuzioni.
- **Test skipped/disabilitato**: il test è marcato come skip o ignorato; la domanda è da quanto tempo e perché.

#### 3.3 Focus sui "test non cambiati"

Il cuore della richiesta del professore è capire **perché i test non cambiano** pur in presenza di evoluzione del codice. Con 100 repository, puoi automatizzare questa analisi:

- Per ciascun repository, usa **PyDriller** (riuso intelligente dello strumento del Prog1) per estrarre la storia dei commit che toccano i file di test e i file del codice applicativo.
- Calcola, per ciascun file di test, l'intervallo tra l'ultima modifica del test e l'ultima modifica del codice applicativo corrispondente.
- Identifica i casi in cui il codice è cambiato ripetutamente mentre il test è rimasto fermo. Questi sono i **candidati "test non cambiati"** da analizzare in profondità nella Fase 4.

**Output della fase**: database dei risultati con esiti, classificazioni e metriche di evoluzione per tutti i 100 repository; elenco dei casi "non cambiati" da approfondire.

---

### Fase 4 — Analisi approfondita e casi studio (Settimane 14–17)

Con i dati aggregati dei 100 repository, puoi condurre un'analisi **quantitativa** e selezionare un sotto-campione per l'analisi **qualitativa**.

#### 4.1 Analisi quantitativa

- **Tasso di eseguibilità**: quanti dei 100 repository sono riusciti a eseguire i test? Quali categorie di fallimento infrastrutturale sono più frequenti?
- **Tasso di successo dei test**: sui repository eseguibili, qual è la proporzione di test passati, falliti, skippati?
- **Distribuzione delle cause di fallimento**: regressioni genuine vs. test obsoleti vs. flakiness vs. problemi infrastrutturali. Questa è la risposta principale alla domanda del professore.
- **Analisi per framework/linguaggio**: i pattern cambiano tra Selenium, Playwright, Cypress? Tra Java e JavaScript?
- **Analisi di sopravvivenza dei test**: quanto "vivono" i test prima di essere rimossi o riscritti? Puoi usare tecniche di survival analysis (Kaplan-Meier) sui dati di commit.
- **Correlazione tra attività del repository e manutenzione dei test**: i repository più attivi mantengono meglio i test?

#### 4.2 Analisi qualitativa e casi studio

Seleziona **10–20 repository** (o 100–200 test) per l'analisi approfondita:

- Scegli i casi più rappresentativi di ciascuna categoria di fallimento.
- Per i "test non cambiati", ricostruisci la storia: quando è stato introdotto il test, cosa è cambiato nell'app, perché il test non è stato aggiornato (test troppo generico, assenza di CI, mancanza di manutenzione, test "di facciata").
- Documenta 3–5 casi studio narrativi, con estratti di codice, commit e log.

#### 4.3 Minacce alla validità

Documenta esplicitamente:
- **Validità interna**: i fallimenti infrastrutturali potrebbero mascherare regressioni genuine.
- **Validità esterna**: i 100 repository sono rappresentativi dei 472? E dei repository E2E in generale?
- **Validità di costrutto**: le categorie di classificazione sono affidabili? Hai verificato l'accordo tra annotatori (se possibile, chiedi a un collega di classificare un sotto-campione e calcola la Cohen's kappa).
- **Riproducibilità**: le versioni dei browser, dei driver e delle dipendenze sono documentate?

**Output della fase**: analisi statistica completa, casi studio, discussione delle minacce alla validità.

---

### Fase 5 — Documentazione, rilascio e prospettive (Settimane 18–20)

1. **Relazione finale** con: protocollo di selezione, pipeline, risultati quantitativi, casi studio, minacce alla validità, lavoro futuro.
2. **Rilascio degli artefatti**: pubblica su GitHub la pipeline di orchestrazione (con Dockerfile e script), i dati aggregati anonimizzati e, se possibile, un piccolo dataset di risultati per la riproducibilità.
3. **Prospettive**: discuti come il lavoro si collega a PT-Linter (bad practice nei test di performance) e E2E-Loader (generazione di carichi da test GUI), e proponi estensioni (es. automazione della classificazione con LLM, studio longitudinale su più versioni).
4. **Eventuale contributo scientifico**: se i risultati sono solidi, valuta un paper per una conferenza di empirical software engineering (MSR, ICSME, SANER) o un workshop.

---

### Stima temporale rivista e gestione del rischio (Prog2)

| Fase | Durata stimata | Rischio principale | Mitigazione |
|---|---|---|---|
| 0. Setup | 2 settimane | Dataset poco familiare | Studio guidato del paper e del DB |
| 1. Selezione 100 repo | 2 settimane | Campione mal stratificato | Pilota su 10 repo, lista di riserva |
| 2. Pipeline | 3 settimane | Complessità di orchestrazione | Docker, time-box, parallelismo controllato |
| 3. Esecuzione e triage | 6 settimane | Repo ineseguibili, tempi lunghi | Regola del time-box, sostituzione con riserve |
| 4. Analisi | 4 settimane | Dati rumorosi, classificazione ambigua | Doppia codifica, casi studio, minacce alla validità |
| 5. Documentazione | 3 settimane | Tempo insufficiente | Iniziare a scrivere durante la Fase 4 |

**Totale**: circa **20 settimane** (5 mesi) a tempo pieno, o 6–8 mesi a tempo parziale.

**Piano B**: se dopo la Fase 3 il tasso di eseguibilità è troppo basso (es. < 40%), riduci il campione a 50 repository ben analizzati e giustifica la scelta nella relazione. Meglio 50 repository con dati solidi che 100 con dati inaffidabili.

---

## 5. Parte IV — Rilevanza per la Carriera e Possibilità Lavorative

La scelta tra i due progetti dipende in larga misura da quale tipo di carriera immagini per te. **Il Prog1 (Agent Skills) ha un potenziale di mercato e di ricerca a breve termine molto più alto e "di frontiera", mentre il Prog2 (Manutenzione Test E2E) offre una base ingegneristica solida e una domanda di lavoro immediata e concreta, ma in un settore che sta cambiando rapidamente proprio a causa dell'AI.**

### 5.1 Prog1 (Agent Skills): L'onda del presente (e del futuro)

Lavorare su `SKILL.md` e sull'ecosistema degli agenti AI ti colloca esattamente dove il mercato sta investendo di più.

- **Domanda di mercato esplosiva**: La creazione di "Skill" per agenti è diventata una competenza richiesta esplicitamente in annunci di lavoro per ruoli come **AI Engineer, Agent Engineer e Applied AI Engineer**. Aziende come ServiceNow cercano figure in grado di "scrivere skill Claude (basate su SKILL.md) che sfruttano i dati aziendali tramite connettori MCP". La domanda di competenze su workflow agentici e MCP è cresciuta drasticamente, passando dal 22,4% al 38,6% delle offerte di lavoro analizzate in un solo anno.
- **Ecosistema in iper-crescita**: A metà 2026, il **40% delle aziende Fortune 500** stava già distribuendo skill AI interne. Il numero di skill pubbliche è passato da circa 50 a **oltre 85.000** nel giro di un anno, e il mercato degli agenti AI è valutato decine di miliardi di dollari, con previsioni di crescita esplosiva.
- **Competenze tecniche e di ricerca all'avanguardia**: Il progetto ti darebbe competenze pratiche su **Python, mining di repository (PyDriller) e pipeline dati**, ma soprattutto ti calerebbe in un problema di ricerca aperto e competitivo (la MSR 2027 Mining Challenge) su un dataset nuovissimo. Questo è un biglietto da visita formidabile per un dottorato di ricerca o per un ruolo di ricerca industriale in AI.

### 5.2 Prog2 (Manutenzione Test E2E): La solidità dell'ingegneria, con uno sguardo al futuro

Questo progetto ti dà una competenza ingegneristica "da trincea" molto richiesta, ma il settore del testing sta vivendo una profonda trasformazione.

- **Domanda immediata e concreta**: La capacità di scrivere ed eseguire test di automazione è quasi un requisito di base: **circa l'80% degli annunci per ruoli QA** enfatizza competenze di automazione. Conoscere framework moderni come **Playwright e Cypress** è oggi un requisito di assunzione predefinito, avendo di fatto soppiantato la sola conoscenza di Selenium.
- **La "trappola" della manutenzione**: Il progetto si concentra sulla manutenzione e sui test che "non cambiano". Questa è una competenza preziosa, ma il mercato del lavoro tradizionale per i "manutentori di test" sta evolvendo. La spinta è verso ruoli che **usano l'AI per generare, mantenere e analizzare i test**, non solo per eseguirli manualmente. La competenza puramente esecutiva rischia di essere commoditizzata.
- **Ricerca solida ma consolidata**: Lavoreresti su un dataset riconosciuto (E2EGit, MSR 2025), il che è un vantaggio per la riproducibilità. Tuttavia, l'aspetto innovativo è meno "pionieristico" rispetto al Prog1; si tratta di uno studio empirico su un fenomeno noto (la fragilità dei test E2E) piuttosto che dell'esplorazione di un ecosistema nascente.

### 5.3 Confronto Diretto per la Carriera

| Dimensione per la Carriera | Prog1 (Agent Skills) | Prog2 (Manutenzione Test E2E) |
| :--- | :--- | :--- |
| **Ruoli target** | AI Engineer, Agent Engineer, LLM Engineer, Ricercatore in AI Engineering | QA Automation Engineer, SDET, Test Automation Architect, Ricercatore in SE Empirico |
| **Competenze chiave** | Python, LLM, RAG, **MCP**, Prompt/Context Engineering, Pipeline Dati | Playwright/Cypress, CI/CD, Docker, **Debugging**, Analisi di Log |
| **Domanda di mercato** | **Altissima e in crescita esplosiva**. Competenza "calda" | **Alta ma in trasformazione**. La sola automazione non basta più; serve la componente AI |
| **Stabilità nel tempo** | Molto alta, ma legata all'evoluzione (rapida) delle piattaforme AI | Molto alta, ma le competenze puramente esecutive rischiano l'obsolescenza |
| **Potenziale di Ricerca** | **Molto alto** (dataset nuovo, competizione internazionale, tema di frontiera) | **Alto** (dataset consolidato, opportunità di pubblicazione in venue empiriche) |
| **Rischio principale** | L'ecosistema è giovane e "rumoroso"; i risultati della ricerca potrebbero essere inconcludenti | Il progetto può diventare un esercizio infrastrutturale frustrante se i repository sono "impossibili" |

### 5.4 In Sintesi: Quale Scegliere?

La scelta si riduce a una domanda fondamentale: **vuoi costruire il futuro o vuoi rendere solido il presente?**

- **Scegli il Prog1 se**: vuoi un biglietto da visita diretto per il mercato dell'**AI Engineering**, che oggi è tra i più vivaci e remunerativi. Ami l'idea di lavorare su un tema di ricerca **esplorativo e competitivo** e non ti spaventa l'idea di costruire metriche e strumenti da zero in un campo in rapida definizione. Questo progetto massimizza il tuo **potenziale a breve termine** e la tua visibilità nella comunità di ricerca AI.

- **Scegli il Prog2 se**: preferisci acquisire una **competenza ingegneristica fondamentale e trasversale** come il testing, che è alla base di qualsiasi prodotto software serio. Ti piace il lavoro "sul campo", il debugging e la comprensione di sistemi complessi e reali. Sebbene il progetto di per sé non sia "AI", ti dà una base perfetta per poi specializzarti in ruoli emergenti come **"AI Quality Engineer"**, dove la tua conoscenza dei test E2E e della loro manutenzione sarà fondamentale per validare sistemi software sempre più complessi e autonomi.

In definitiva, **il Prog1 è più orientato al futuro e al mercato dell'AI, mentre il Prog2 è più orientato alla solidità dell'ingegneria del software tradizionale**, anche se con un occhio di riguardo alle sue evoluzioni. Se il tuo obiettivo è entrare nel mondo dell'AI nel modo più diretto possibile, il Prog1 è la scelta con il potenziale di carriera più immediato e "dirompente".

---

## 6. Conclusioni e Raccomandazioni Finali

### 6.1 Sintesi delle due roadmap

| Fase | Prog1 (Agent Skills Tool) | Prog2 (E2EGit, 100 repository) |
|---|---|---|
| **0. Setup** | Preprint GitSkills, MSR 2027, PyDriller docs, download dataset | Paper E2EGit, download dataset SQLite, ripresa stato interno |
| **1. Definizione** | Metriche di processo e prodotto, euristiche di smell | Selezione campione di ~100 repository stratificati |
| **2. Sviluppo/Esecuzione** | Pipeline di estrazione, parsing, prototipo su 50–100 repo | Pipeline di orchestrazione, setup Docker, esecuzione incrementale |
| **3. Analisi** | Applicazione a campione ampio, analisi esplorativa, validazione | Esecuzione in ondate, classificazione fallimenti, focus sui test "non cambiati" |
| **4. Chiusura** | Dashboard, documentazione, paper MSR 2027 | Analisi quantitativa e qualitativa, casi studio, documentazione, rilascio |

### 6.2 Raccomandazioni trasversali

- **Prog1**: il rischio principale è **perdersi nell'esplorazione**. Fissa un limite: entro la settimana 8 devi avere un prototipo funzionante su un campione, anche se le metriche non sono perfette. Le euristiche si raffinano *dopo*, con i dati alla mano.
- **Prog2**: il rischio principale è **arenarsi su un repository che non parte**. Regola d'oro: se un repository richiede più di 2–3 giorni di setup senza successo, scartalo e passane a un altro. Con 100 repository, hai margine per sostituire i casi problematici. Il limite dei 100 repository è un obiettivo, non un vincolo assoluto: meglio 50 repository con dati solidi che 100 con dati inaffidabili.

### 6.3 Come sfruttare il legame tra i due progetti

Anche se scegli uno dei due, puoi **ibridare** le competenze. Se fai il Prog2, puoi usare PyDriller per analizzare la storia dei file di test: è un modo per applicare il mining alla manutenzione dei test. Se fai il Prog1, puoi ispirarti al concetto di "smell" del Prog2 per definire gli indicatori di qualità delle skill. Questo rende il tirocinio più ricco e ti dà un profilo più versatile.

### 6.4 Considerazione finale

Entrambi i progetti sono di **elevata qualità** e ben radicati nella letteratura recente. Il Prog1 rappresenta un'opportunità per lavorare su un tema **di frontiera** (agent skills) con un dataset nuovo e una competizione internazionale. Il Prog2 rappresenta un'opportunità per **approfondire la manutenzione dei test E2E** su un dataset solido, con un approccio empirico e un impatto pratico immediato. La scelta dovrebbe essere guidata dalla **propensione personale** e dagli **obiettivi di carriera**: se ami l'esplorazione, l'AI e la costruzione di strumenti, scegli il Prog1; se ami l'analisi dei sistemi reali, il debugging e la soluzione di problemi concreti di testing, scegli il Prog2. In entrambi i casi, il tirocinio offre l'occasione di acquisire competenze avanzate e di entrare in contatto con un gruppo di ricerca attivo e produttivo.

---

## 7. Riferimenti e Link Utili

### Prog1 — Agent Skills / GitSkills / MSR 2027

- **GitSkills preprint**: arXiv:2608.10906
- **Dataset GitSkills su Zenodo**: DOI 10.5281/zenodo.21875637
- **MSR 2027 Mining Challenge**: https://2027.msrconf.org/track/msr-2027-mining-challenge
- **PyDriller**: documentazione ufficiale (versione 1.12+)
- **Lizard**: analizzatore di codice sorgente multi-linguaggio

### Prog2 — E2EGit / Test E2E

- **Paper E2EGit (IEEE Xplore)**: DOI 10.1109/MSR66628.2025.00121 — https://ieeexplore.ieee.org/document/11025750
- **Dataset E2EGit (Zenodo)**: DOI 10.5281/zenodo.14234731 — https://zenodo.org/records/14234731
- **PDF del paper E2EGit**: https://valeriapontillo.github.io/documents/conference/C4.pdf
- **Pagina personale di Valeria Pontillo**: https://valeriapontillo.github.io/
- **PT-Linter**: strumento per il rilevamento di bad practice nei test di performance
- **E2E-Loader**: strumento per il caricamento e l'analisi dei test

### Strumenti e tecnologie citati

- **Python**, **PyDriller**, **SQLite**, **pandas**, **Jupyter**, **difflib**, **sentence-transformers**, **Streamlit**
- **Docker**, **DB Browser for SQLite**, **DBeaver**
- **Selenium**, **Playwright**, **Cypress**, **Puppeteer**, **JMeter**, **Locust**
- **JUnit**, **Jest**, **PyTest**, **Maven**, **Gradle**, **npm/yarn**, **pip/poetry**

---

*Documento redatto il 21 ottobre 2026. Le informazioni sui dataset, sulle conferenze e sulle tecnologie sono aggiornate alla data di redazione. Per eventuali aggiornamenti, consultare i link ufficiali indicati nella Sezione 7.*