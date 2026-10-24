# E2EGit — riassunto ragionato e concetti non banali

**Documento di supporto** alla lettura di `docs/letteratura/E2EGit_MSR2025_C4.pdf` e della sua traduzione `docs/letteratura/E2EGit_MSR2025_C4_IT.pdf`.
**A cosa serve**: farti arrivare al ricevimento sapendo spiegare il paper, non solo avendolo letto.

---

## 1. In tre righe

Gli autori hanno preso 1,4 milioni di repository GitHub, li hanno filtrati fino a 5.563 applicazioni web "serie", e dentro queste hanno cercato i test end-to-end: **472 repository con test di interfaccia** (43.670 test) e **84 con test di performance** (271 test). Il risultato è un database SQLite pubblico che descrive quei test e lo storico dei commit che li hanno toccati.

**Perché è un contributo e non un elenco**: prima di questo lavoro non esisteva un dataset pubblico di test E2E su progetti reali. Senza un dataset condiviso, ogni studio su fragilità, manutenzione o flakiness dei test doveva costruirsi il proprio campione, e i risultati non erano confrontabili tra loro.

**Perché conta per te**: il tuo Prog2 parte da qui. Il dataset ti dà il campione e lo storico; quello che **non** ti dà è l'esecuzione dei test — ed è esattamente lo spazio in cui lavori.

---

## 2. Come leggerlo in 40 minuti

| Minuti | Cosa | Perché |
|---|---|---|
| 0–5 | Abstract + Tabella I | Ti dà tutti i numeri che ti serviranno citare |
| 5–12 | Figura 1 e §II.A | Capisci la pipeline di filtraggio: è il punto metodologicamente più delicato |
| 12–25 | §II.B e §II.C | Come hanno deciso che un file "è" un test. Qui si vince o si perde la validità |
| 25–32 | §III + Figura 3 | Lo schema del database: è ciò con cui lavorerai davvero |
| 32–40 | §V (minacce) + §VI (lavoro correlato) | Ti dice cosa puoi e non puoi concludere, e chi ha fallito prima |

Il resto (§IV usi possibili, §VII conclusioni) si legge in 5 minuti ed è utile soprattutto per la sezione "lavoro futuro" della tua relazione.

---

## 3. I numeri, uno per uno

| Numero | Cosa significa davvero |
|---|---|
| **1.401.170** | Repository restituiti da SEART nel maggio 2024, prima di qualsiasi filtro |
| **14.053** | Repository che superano i 4 criteri anti-"giocattolo" (vedi §4.2) |
| **5.563** | Repository che hanno anche almeno una dipendenza da un framework web riconosciuto |
| **472 / 84 / 13** | Repository con test GUI / con test di performance / con entrambi |
| **43.670** | Test GUI totali (non file: test) |
| **271** | Test di performance totali |
| **92,5** | Media di test GUI per repository |
| **5** | Media di test di performance per repository |
| **410** | Righe di `performance_testing_test_details`: una per **ThreadGroup/TaskSet**, non per file. Per questo è più di 271 |
| **1,5 milioni** | Repository nella tabella `repository`, con 34 campi: è lo "sfondo" statistico, non il dataset vero e proprio |

**Due trappole nei numeri.**

1. La somma della Tabella I dà **43.674**, non 43.670. Non è un errore: un repository che usa Selenium *e* Cypress compare in due righe. Il totale conta i test una volta sola.
2. **271 test ≠ 410 righe.** Un file di test performance può contenere più ThreadGroup, e ogni ThreadGroup è una riga. Se scrivi una query e conti le righe, stai contando i gruppi di carico, non i test.

**Verifiche fatte sul database** (24 ottobre 2026, `E2EGit.db` scaricato e con md5 corretto). Non sono più numeri letti dal paper: sono query eseguite.

| Verifica | Query | Risultato |
|---|---|---|
| Repository con test GUI | `COUNT(*)` su `gui_testing_repo_details` | **472** ✓ |
| Test GUI totali | `SUM(number_of_tests)` sulla stessa tabella | **43.670** ✓ (la Tabella I ne somma 43.674: sovra-conta i repo multi-framework) |
| File di test GUI | `COUNT(*)` su `gui_testing_test_details` | **8.601** — il paper non lo dice: 43.670 è il numero di *test*, non di file |
| Repository web non banali | `COUNT(*)` con `is_web_*` | **5.563** ✓ |
| Repository con entrambe le tipologie | `INTERSECT` tra le due tabelle | **13** ✓ |
| Test di performance | `COUNT(*)` su `performance_testing_test_details` | **410** righe, **84** repository distinti ✓ |
| Commit di riferimento | `repository.last_commit_sha` | presente e non nullo per tutti i 472 ✓ |
| Media test per repo | `AVG(number_of_tests)` | **92,52** ✓ (il paper dice 92,5) |

Una nota sul "1,5 milioni" della tabella sopra: la tabella `repository` contiene in realtà **1.401.170** righe, cioè esattamente il numero che il paper cita come punto di partenza. Il "1,5 milioni" nel testo del paper è un arrotondamento impreciso.

---

## 4. I concetti non banali

### 4.1 E2E, GUI e performance non sono la stessa cosa

Il paper usa "end-to-end" come **contenitore**, non come tipo di test. Dentro ci sono due attività con strumenti, problemi e fallimenti diversi:

- **GUI testing**: pilota un browser vero, simula clic e digitazioni. Rompe quando cambia il selettore, il layout, il timing del rendering.
- **Performance testing**: genera carico concorrente e misura latenza/throughput. Rompe quando cambia l'infrastruttura, il carico non è realistico, o i parametri sono sbagliati.

Questa distinzione è la ragione per cui il dataset ha **due sottocartelle di tabelle separate**. Se nel tuo lavoro le mescoli in un'unica analisi, ottieni numeri che non significano nulla.

### 4.2 "Non-trivial" è una definizione operativa, non un giudizio di qualità

I quattro criteri sono: **≥ 2000 commit**, **≥ 10 contributori**, **≥ 100 stelle**, **non fork**. Servono a escludere i progetti-esercizio, quelli abbandonati dopo tre commit e i cloni.

Ma hanno un **costo scientifico che il paper dichiara solo in parte**: una soglia di 2000 commit seleziona per definizione progetti **maturi e longevi**. Quindi il dataset non descrive "come si fa test E2E su GitHub", descrive "come si fa test E2E nei progetti abbastanza grandi da avere 2000 commit". Sono due popolazioni diverse, e la seconda sovra-rappresenta i progetti strutturati, con CI, con team. È il tipo di osservazione che un revisore ti fa e a cui devi essere pronto.

### 4.3 Framework di automazione ≠ motore di test

È la distinzione tecnica più importante del paper, e la più facile da sbagliare.

- **Framework di automazione del browser**: Selenium, Playwright, Cypress, Puppeteer. Sono le "mani": controllano il browser.
- **Motore di test**: JUnit, TestNG, Jest, Mocha, Jasmine, PyTest, unittest. È il "cervello": decide cosa è un test, lo esegue, riporta pass/fail.

Un file che importa Selenium ma non ha un motore di test è uno **script**, non un test: non ha asserzioni, non produce un esito, nessuno lo esegue in CI. Per questo la pipeline richiede **entrambi** (dipendenza + sintassi del motore, come `@Test`, `it(`, `test_`). È il passaggio che trasforma "file che sembra un test" in "test".

### 4.4 Perché JMeter è facile e Locust è difficile

- **JMeter**: i test sono file `.jmx`, cioè XML con un'estensione inconfondibile. Li trovi con un `glob`, senza analisi delle dipendenze. La validazione (esiste un ThreadGroup? esiste una richiesta?) si fa parsando l'XML.
- **Locust**: i test sono file Python normali. Non c'è nessun marcatore nel nome. Devi cercare la dipendenza in `requirements.txt`, poi cercare gli `import locust` nel codice. E la validazione finale **l'hanno fatta a mano** i primi due autori.

Questa asimmetria spiega perché nel dataset ci sono 244 test JMeter e solo 27 Locust: non è che Locust sia meno usato, è che è **più difficile da trovare in modo affidabile**. È un bias di rilevazione, non un fatto sul mondo.

### 4.5 ThreadGroup e TaskSet: l'unità di carico

In JMeter un **ThreadGroup** è un insieme di utenti virtuali che eseguono lo stesso scenario; in Locust un **TaskSet** è l'equivalente. Il numero di ThreadGroup è la granularità con cui il dataset descrive un test di performance: un file può contenerne diversi. Da qui le 410 righe.

### 4.6 I parametri `${foo}` e il problema della riproducibilità

In JMeter puoi scrivere `${utenti}` invece di un numero: il valore vero arriva da una proprietà o da una variabile d'ambiente al momento dell'esecuzione. Il dataset, che fa analisi statica, **non può saperlo**: mette la stringa `${utenti}` nel campo `number_of_users`.

Conseguenza concreta per te: i campi numerici di quella tabella sono **stringhe**, non interi. Se fai `SUM(number_of_users)` ottieni zero o un errore. E soprattutto: quel test, senza sapere il valore di `${utenti}`, **non è riproducibile**. È il primo posto dove il tuo lavoro incontrerà il muro.

### 4.7 Cos'è un "test smell" (e cosa non è)

Un *test smell* è una scelta di design nel codice di test che ne peggiora manutenibilità o efficacia: asserzioni duplicate, test che dipendono dall'ordine, setup enorme, nomi senza significato, "magic numbers". Il termine viene dal lavoro di Deursen et al. sul refactoring del codice di test ([25] nel paper).

**Non è un bug.** Un test con smell può passare per anni. Il problema è che costa, e che quando il comportamento cambia è proprio quel test a non accorgersene. Questa distinzione è la stessa che separa "test rotto" da "test inutile", ed è al centro della tua domanda di ricerca.

### 4.8 Validità interna ed esterna: cosa rispondere a un revisore

- **Interna**: il risultato dipende da come hai costruito il campione? Qui la minaccia è la scelta di 4 linguaggi, 15 framework web e 4+2 strumenti di test. La difesa degli autori è "abbiamo preso i più diffusi". È una difesa ragionevole, non una prova.
- **Esterna**: il risultato vale fuori da GitHub? No, e loro lo ammettono: i progetti industriali hanno test privati, spesso più complessi.

C'è una terza minaccia che il paper **non tratta**: la **validità di costrutto**. "Questo file contiene un test GUI" è un'inferenza da un import e una sintassi. Quanti falsi positivi? Non lo sanno, perché non hanno eseguito i test. È la lacuna che il tuo tirocinio può colmare — e va detta con rispetto, non come critica.

### 4.9 Perché un dataset è un contributo scientifico

Un dataset non è "dati messi online". È un contributo se è: **documentato** (schema, significato dei campi), **accessibile** (licenza, DOI, download stabile), **riproducibile** (sai come è stato costruito) e **utile** (altri lo usano). E2EGit ha vinto il *Distinguished Dataset Award* a MSR 2025 proprio perché copre tutti e quattro i punti — anche se la pipeline di costruzione non è rilasciata come codice, ma solo descritta.

### 4.10 Cosa NON contiene il dataset (e conta)

- ❌ **Non contiene gli esiti dei test.** Nessuno li ha eseguiti: non sai se passano.
- ❌ **Non contiene i risultati di flakiness.** Nessuna ripetizione.
- ❌ **Non contiene i repository clonati**, ma i loro metadati e i percorsi dei test.
- ❌ **Non contiene dati di esecuzione** (browser, driver, versioni): solo il percorso del file e il framework.

Tutto ciò che riguarda "il test regge o è rotto" **va prodotto da te**. Questa è la frase da dire al professore: il dataset è il punto di partenza, non il risultato.

---

## 5. Le tre domande che ti farà il professore

**1. "Perché 5.563 e non 1,4 milioni?"**
Perché ci sono due filtri in sequenza: i quattro criteri anti-giocattolo (1.401.170 → 14.053) e la presenza di una dipendenza da framework web riconosciuto (14.053 → 5.563). Ogni filtro è una scelta, non un dato.

**2. "Come sai che un file è un test?"**
Con due segnali insieme: la dipendenza dal framework di automazione e la presenza della sintassi di un motore di test. Presi singolarmente, entrambi producono falsi positivi.

**3. "Se il dataset non contiene gli esiti, cosa aggiungi tu?"**
L'esecuzione. E la classificazione dei fallimenti, e la storia dei test che non cambiano. Cioè: il dataset dice *cosa* c'è, il tuo lavoro dice *cosa succede*.

---

## 6. Dove attaccare il paper (limiti non dichiarati)

| Limite | Come usarlo nel tuo lavoro |
|---|---|
| Campione solo maturo (≥2000 commit) | Dillo nelle minacce alla validità: i tuoi 100 repo ereditano lo stesso bias |
| Nessuna esecuzione | È il tuo contributo, non un difetto da nascondere |
| Locust validato a mano | Se nel tuo campione trovi Locust, aspettati più rumore |
| Snapshot maggio 2024 | I repository possono essere spariti o archiviati: verifica prima di clonare |
| Nessuna licenza per repo | Devi controllarla tu prima di ridistribuire dati derivati |
| Pipeline non rilasciata come codice | Devi ricostruire la selezione: parti dalle tabelle, non dal paper |

---

## 7. Cosa prendere per il tuo Prog2

1. **Le cinque tabelle** come punto di partenza per la selezione dei 100 repository (in particolare `gui_testing_repo_details`).
2. **Il commit di riferimento** per ogni repository, se disponibile nei metadati: è ciò che rende confrontabili le tue esecuzioni con il dataset.
3. **La definizione di "test GUI"** (framework + motore) per non includere nei tuoi 100 repo dei falsi positivi che ti farebbero perdere giorni.
4. **La struttura delle minacce alla validità**: copiala come impianto, riempila con i tuoi numeri.
5. **Il formato del contributo**: dataset + paper breve. È il modello che il gruppo premia (vedi PT-LINTR, nato da un tirocinio).

---

## 8. Glossario minimo

| Termine | Significato |
|---|---|
| **E2E** | Test che attraversa l'intera applicazione come farebbe un utente |
| **GUI testing** | Test che pilota il browser e simula l'utente |
| **Performance testing** | Test che genera carico concorrente e misura il comportamento |
| **ThreadGroup / TaskSet** | Unità di utenti virtuali in JMeter / Locust |
| **Test engine** | Framework che definisce, esegue e referta i test (JUnit, Jest, PyTest…) |
| **Test smell** | Cattiva pratica nel codice di test che ne peggiora manutenibilità o efficacia |
| **Flakiness** | Test che passa e fallisce senza che nulla cambi |
| **Falso positivo / negativo** | Il tool segnala un test che non c'è / non vede un test che c'è |
| **Validità interna / esterna** | Il risultato dipende dal campione? / Vale fuori dal campione? |
| **Snapshot** | Fotografia del dataset a una certa data: qui maggio 2024 |

---

*Documento redatto il 24 ottobre 2026. Riferimenti verificati sul PDF originale (`E2EGit_MSR2025_C4.pdf`, 5 pagine) e sulla traduzione (`E2EGit_MSR2025_C4_IT.pdf`, 8 pagine).*
