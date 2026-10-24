# Dizionario dei CSV

Cinque file, tutti generati leggendo `data/E2EGit.db` (i primi quattro da `src/01_estrai_repository.py`, `repos_commit.csv` da una query dedicata).
Sono derivati: se li cancelli, li rigeneri in una trentina di secondi. Il database è la fonte, i CSV sono la vista comoda.

| File | Righe | Cosa contiene |
|---|---|---|
| `repos_gui.csv` | 472 | un repository per riga, con i conteggi aggregati |
| `tests_gui.csv` | 8.601 | un **file di test** per riga |
| `tests_perf.csv` | 410 | un **ThreadGroup/TaskSet** per riga |
| `repos_url.csv` | 472 | solo nome e URL da clonare |
| `repos_commit.csv` | 472 | il **commit di riferimento** e i metadati per la stratificazione |

---

## 0. A cosa servono, in pratica

Non sono quattro copie dello stesso dato: sono **tre livelli di zoom** più una rubrica.

```text
repos_gui.csv        IL CATALOGO        472 righe
                     "quali repository esistono e quanto sono grandi"
                          │
                          ├── tests_gui.csv     L'INVENTARIO        8.601 righe
                          │                     "dentro quel repo, quali file di test"
                          │
                          └── tests_perf.csv    L'INVENTARIO DEI TEST DI CARICO   410 righe
                                                "quanti utenti simulati, quante iterazioni"

repos_url.csv        LA RUBRICA         472 righe
                     "questo nome → questo URL da clonare"
```

Il catalogo ti serve per **scegliere**. Gli inventari per **eseguire**. La rubrica per **non sbagliare l'URL**.

### A cosa serve ognuno, nel momento in cui ti servirà

| Quando | Apri | La domanda a cui risponde |
|---|---|---|
| **Scelta dei 100 repository** | `repos_gui.csv` | Quali hanno abbastanza test? Quali usano Selenium e non solo Cypress? Quali sono troppo grandi per il tempo che ho? |
| **Prima di clonare** | `repos_url.csv` | Qual è l'URL esatto di questo repository? |
| **Durante l'esecuzione** | `tests_gui.csv` | Quali file devo lanciare, con quale framework, e quanti test devo aspettarmi? Se ne passano 3 su 6, è un dato. |
| **Test di carico** | `tests_perf.csv` | Questo `.jmx` dichiara 5 utenti e 20 iterazioni, oppure `${utenti}`, che non posso risolvere? |
| **Analisi della storia** | `tests_gui.csv` | Su quale file faccio girare PyDriller per sapere se è cambiato mentre il codice cambiava? |

### Esempio completo: dal catalogo all'esito

Repository reale, valori reali presi dai CSV (`10up/elasticpress`).

**Passo 1 — Catalogo.** Una riga di `repos_gui.csv`:

| repository_name | number_files_cypress_js | number_of_files | number_of_tests |
|---|---|---|---|
| `10up/elasticpress` | 18 | 18 | 116 |

Traduzione: 18 file di test, tutti Cypress e tutti JavaScript, 116 test dichiarati. Nessun `with_junit`, `with_jest` o altro motore: normale per Cypress, che è insieme framework e runner.

**Passo 2 — Rubrica.** Una riga di `repos_url.csv`:

```text
10up/elasticpress, https://github.com/10up/elasticpress
```

**Passo 3 — Inventario.** Filtro `tests_gui.csv` per `repository_name = "10up/elasticpress"` e ottengo 18 righe. Una:

| test_path_rel | is_cypress_js | number_of_tests |
|---|---|---|
| `tests/cypress/integration/dashboard-sync.cy.js` | 1 | 6 |

**Passo 4 — Clone ed esecuzione.** L'URL del passo 2, il commit da `repository.last_commit_sha` (vedi `docs/02_schema.md`), il file del passo 3:

```powershell
git clone https://github.com/10up/elasticpress
cd elasticpress
git checkout <last_commit_sha>
npx cypress run --spec tests/cypress/integration/dashboard-sync.cy.js
```

**Passo 5 — Registro l'esito.** Quello che scrivi tu, perché nel dataset non c'è:

```json
{
  "repository": "10up/elasticpress",
  "test_path": "tests/cypress/integration/dashboard-sync.cy.js",
  "commit": "<last_commit_sha>",
  "framework": "cypress",
  "declared_tests": 6,
  "executed": { "total": 6, "passed": 4, "failed": 1, "skipped": 1 },
  "status": "executed",
  "seconds": 42
}
```

Tutto il flusso sta in quei cinque passi. Il dataset copre i passi 1–3; i passi 4–5 sono il tuo tirocinio.

> **Attenzione a un numero che sembra uguale e non lo è.** `number_of_tests` (116, 6) è quello che il mining ha *contato nel file*, non quello che il framework *eseguirà*. Un test può essere parametrizzato e generare più casi, oppure essere filtrato dalla configurazione. `declared_tests` e `executed.total` vanno tenuti separati: la differenza tra i due è già un risultato.

### Perché quattro file e non uno

Perché la riga ha un significato diverso in ognuno: un repository contiene molti file, un file può contenere più gruppi di carico. In un unico CSV le righe avrebbero lunghezza diversa e colonne vuote — il modo più rapido per sbagliare i conteggi (e per sommare due volte lo stesso test).

### Cosa non contengono

- ❌ il **codice** dei test: solo il percorso, il file va preso dal repository;
- ❌ gli **esiti**: nessuno ha eseguito niente;
- ❌ le **versioni** di browser, driver o JDK;
- ❌ il **commit**: sta in `repository.last_commit_sha`, non nei CSV.

Contengono **dove** andare a prendere tutto questo.

---

## 1. `repos_gui.csv` — 23 colonne

Una riga per repository con almeno un test GUI. È la tabella da cui parte la selezione dei 100.

| Colonna | Tipo | Significato |
|---|---|---|
| `repository_name` | testo | `owner/repo`, es. `10up/elasticpress`. **Chiave** |
| `number_files_selenium_java` | intero | quanti **file** di test usano Selenium in Java |
| `number_files_selenium_js` | intero | … in JavaScript |
| `number_files_selenium_ts` | intero | … in TypeScript |
| `number_files_selenium_py` | intero | … in Python |
| `number_files_playwright_java/js/ts/py` | intero | idem, con Playwright (4 colonne) |
| `number_files_puppeteer_js/ts/py` | intero | idem, con Puppeteer (3 colonne — non esiste Java) |
| `number_files_cypress_js/ts` | intero | idem, con Cypress (2 colonne) |
| `with_junit` | 0/1 | il repository usa JUnit come motore di test |
| `with_testng` | 0/1 | … TestNG |
| `with_jest` | 0/1 | … Jest |
| `with_mocha` | 0/1 | … Mocha |
| `with_jasmine` | 0/1 | … Jasmine |
| `with_pytest` | 0/1 | … PyTest |
| `with_unittest` | 0/1 | … unittest |
| `number_of_tests` | intero | **somma dei test** contenuti in tutti i file del repository |
| `number_of_files` | intero | quanti file di test ha in totale |

Esempio: `10up/elasticpress` → 18 file Cypress/JS, 116 test, nessun motore separato.

**Le 13 colonne `number_files_*` sono conteggi, non flag**: un repository può usare due framework, e in quel caso compare in due gruppi. La somma delle colonne può quindi superare `number_of_files`.

---

## 2. `tests_gui.csv` — 24 colonne

Una riga per **file** di test. È la granularità giusta per il mining della storia Git, perché `test_path` identifica un file che puoi seguire nei commit.

| Colonna | Tipo | Significato |
|---|---|---|
| `repository_name` | testo | `owner/repo` |
| `test_path` | testo | percorso **come lo ha scritto il mining**, non relativo al repo (vedi §5) |
| `is_selenium_java` | 0/1 | questo file usa Selenium in Java |
| `is_selenium_js/ts/py` | 0/1 | idem per gli altri linguaggi (13 colonne in totale, stesso schema di `repos_gui`) |
| `with_junit` … `with_unittest` | 0/1 | motore di test usato **da questo file** |
| `number_of_tests` | intero | quanti test contiene questo file |
| `test_path_rel` | testo | percorso relativo alla radice del repository, **calcolato da noi** |

La somma di `number_of_tests` su tutte le 8.601 righe dà **43.670**, il totale del dataset.
Solo **2** file dichiarano più di un framework; nessuno zero.

---

## 3. `tests_perf.csv` — 12 colonne

Una riga per **ThreadGroup** (JMeter) o **TaskSet** (Locust), non per file: un `.jmx` con 10 gruppi produce 10 righe.

| Colonna | Tipo | Significato |
|---|---|---|
| `repository_name` | testo | `owner/repo` |
| `test_path` | testo | percorso nel formato `\owner\repo\...` |
| `threadgroup_taskset_id` | intero | identificativo del gruppo dentro il file |
| `is_jmeter` | 0/1 | il gruppo è JMeter |
| `is_locust` | 0/1 | il gruppo è Locust |
| `threadgroup_taskset_name` | testo | nome dato dall'autore, es. `KVP - Request Scenario A` |
| `number_of_users` | **testo** | utenti virtuali: può essere `5` o `${utenti}` |
| `ramp_up` | **testo** | secondi di salita |
| `loop_count` | **testo** | iterazioni (attenzione: la Figura 3 del paper lo scrive `loop_cound`) |
| `duration` | **testo** | durata; **vuoto in 336 righe su 410** (Locust la passa da riga di comando) |
| `number_of_requests` | **testo** | richieste per iterazione |
| `test_path_rel` | testo | percorso relativo, calcolato da noi |

**Tutti i parametri numerici sono testo, non interi.** Non fare `SUM(number_of_users)`: sommeresti stringhe. Prima vanno puliti e convertiti, e i valori `${...}` vanno esclusi o trattati a parte.

---

## 4. `repos_url.csv` — 2 colonne

| Colonna | Significato |
|---|---|
| `repository` | `owner/repo` |
| `clone_url` | `https://github.com/owner/repo`, pronto per `git clone` |

Serve solo a evitare di costruire l'URL a mano 472 volte. Non contiene il commit: quello sta in `repos_commit.csv`.

---

## 4-bis. `repos_commit.csv` — 11 colonne

Il file che **ancora ogni esecuzione a un punto preciso nel tempo**. Senza, "il test è cambiato" e "ho guardato il momento sbagliato" diventano indistinguibili.

| Colonna | Tipo | Significato |
|---|---|---|
| `repository_name` | testo | `owner/repo` — chiave di join con gli altri CSV |
| `number_of_tests` | intero | test dichiarati nel repository |
| `number_of_files` | intero | file di test |
| `last_commit` | data ISO | **quando** è stato preso lo snapshot, es. `2024-03-21T02:19:55` |
| `last_commit_sha` | testo | **l'hash da passare a `git checkout`** |
| `default_branch` | testo | branch di default: `main` 192, `master` 180, altro 100 |
| `licences` | testo | licenza dichiarata — **vuota in 25 righe** |
| `main_language` | testo | linguaggio principale (TypeScript 207, Java 89, JavaScript 75, PHP 30, Python 30…) |
| `created_at` | data | nascita del repository: serve per la stratificazione per età |
| `pushed_at` | data | ultimo push registrato: serve per l'attività recente |
| `clone_url` | testo | URL pronto per `git clone` |

Esempio reale:

```text
repository_name : 10up/elasticpress
number_of_tests : 116
last_commit     : 2024-03-21T02:19:55
last_commit_sha : 9b4d1210fe5b3c30e0781b72149cf4b773bd0196
default_branch  : develop
licences        : GNU General Public License v2.0
```

### Perché nella tesi è il file più importante

La domanda del professore è "perché i test non cambiano". Per rispondere devi confrontare due momenti:

- **t₀** = il commit registrato nel dataset (dove il test è com'era quando sono stati contati 43.670 test)
- **t₁** = l'esecuzione di oggi, su quel codice

Se non ancori l'esecuzione a t₀, stai confrontando "il test di oggi" con "un metadato di un anno e mezzo fa", e ogni differenza è indistinguibile tra "il test non è cambiato" e "ho misurato due cose diverse". Il commit è ciò che rende il confronto valido — ed è la parola che in una relazione sostituisce "abbastanza preciso" con "riproducibile".

**In pratica**: `last_commit_sha` va copiato in ogni record di `results/`, accanto all'esito. Un record senza SHA non è un risultato.

**Tre cose che questo file rivela.**

1. **Lo snapshot è di marzo 2024, non di maggio.** Il paper dichiara "May 2024", ma la mediana di `last_commit` è il **27 marzo 2024** (massimo il 29). Il codice che analizzi è quindi più vecchio di quanto il paper lasci intendere.
2. **`last_commit_sha` è l'ultimo commit del repository, non del file di test.** Per sapere quando il test è stato modificato l'ultima volta serve PyDriller sul clone: due informazioni diverse, entrambe necessarie.
3. **25 repository non dichiarano licenza.** Clonarli è lecito, ridistribuirne il codice no: se pubblichi dati derivati, vanno esclusi o verificati a mano.

---

## 5. Le quattro trappole

**a) `test_path` non è relativo al repository.** Contiene un prefisso aggiunto dal mining, diverso tra le due tabelle:

| Tabella | Nel CSV | `test_path_rel` |
|---|---|---|
| GUI | `/10up_elasticpress/tests/cypress/integration/x.cy.js` | `tests/cypress/integration/x.cy.js` |
| Performance | `\52north\sos\core\test\src\...\testplan.jmx` | `core/test/src/test/resources/testplan.jmx` |

Usa sempre `test_path_rel` per aprire il file dentro il clone.

**b) `with_*` tutti a zero non significa "nessun motore".** 175 repository su 472 hanno tutti i sette flag a zero, e in **tutti e 175** i test sono Cypress. Cypress è insieme framework e runner: non compare fra i motori elencati (JUnit, TestNG, Jest, Mocha, Jasmine, PyTest, unittest) e quindi non alza nessun flag. Se filtri per `with_junit=1` per "avere test veri", stai buttando via 175 repository validi.

**c) Conteggi e flag si somigliano ma non sono la stessa cosa.** `number_files_cypress_js = 18` dice quanti file; `is_cypress_js = 1` dice se *quel* file usa Cypress. Nel primo CSV sono conteggi, nel secondo flag.

**d) Stringa vuota e NULL.** Nei CSV i NULL di SQLite diventano celle vuote (es. `duration`). Se leggi con pandas ottieni `NaN`; con `csv` ottieni `""`. Non sono la stessa cosa quando conti.

---

## 6. Query di controllo

Se rigeneri i CSV, questi numeri devono tornare:

```sql
SELECT COUNT(*) FROM gui_testing_repo_details;                 -- 472
SELECT COUNT(*) FROM gui_testing_test_details;                 -- 8601
SELECT SUM(number_of_tests) FROM gui_testing_test_details;     -- 43670
SELECT COUNT(*) FROM performance_testing_test_details;         -- 410
SELECT COUNT(DISTINCT repository_name) FROM performance_testing_test_details;  -- 84
```

---

*Documento redatto il 24 ottobre 2026 sui CSV generati dal database v3 di E2EGit.*
