# Schema reale di E2EGit.db

**Verificato il 24 ottobre 2026** aprendo il file scaricato da Zenodo, non leggendo il paper.
Se questo documento contraddice la Figura 3 del paper, ha ragione questo documento.

| Voce | Valore |
|---|---|
| File | `data/E2EGit.db` — 2,28 GiB (2,45 GB decimali) |
| Versione | v3, 28/11/2024, CC-BY-4.0 |
| DOI | 10.5281/zenodo.14234731 |
| MD5 verificato | `01E69C6956BB747D4142CFCD9D5EEBB2` ✓ |
| Tabelle | 5 |
| Righe totali | ~1.425.000 |

---

## 1. Le cinque tabelle

| Tabella | Righe | A cosa serve |
|---|---|---|
| `repository` | 1.401.170 | Metadati di tutti i repository SEART, 34 colonne |
| `non_trivial_repository` | 14.053 | Sottoinsieme che supera i filtri anti-giocattolo |
| `gui_testing_repo_details` | **472** | Una riga per repository con test GUI |
| `gui_testing_test_details` | **8.601** | Una riga per **file** di test GUI |
| `performance_testing_test_details` | **410** | Una riga per **ThreadGroup/TaskSet** |

Attenzione a due numeri che si confondono facilmente:

- **8.601** sono i *file* di test; **43.670** sono i *test* contenuti, ottenuti con `SUM(number_of_tests)`.
- **410** sono i gruppi di carico; i *file* `.jmx` distinti sono molti meno (alcuni compaiono più volte, uno per ThreadGroup).

---

## 2. `gui_testing_repo_details` (23 colonne)

```text
repository_name
number_files_selenium_java    number_files_playwright_java   number_files_puppeteer_js
number_files_selenium_js      number_files_playwright_js     number_files_puppeteer_ts
number_files_selenium_ts      number_files_playwright_ts     number_files_puppeteer_py
number_files_selenium_py      number_files_playwright_py     number_files_cypress_js
with_junit  with_testng  with_jest  with_mocha  with_jasmine  with_pytest  with_unittest
number_of_tests   number_of_files
```

Esempio reale (riga di `apache/roller`):

| repository_name | number_files_selenium_java | with_junit | number_of_tests | number_of_files |
|---|---|---|---|---|
| `apache/roller` | 1 | 1 | 1 | 1 |

---

## 3. `gui_testing_test_details` (23 colonne)

Identica struttura della precedente, ma per **file**: `repository_name`, `test_path`, le 13 colonne `is_<framework>_<lingua>`, i 7 `with_<motore>` e `number_of_tests`.

`is_selenium_java`, `is_selenium_js`, `is_selenium_ts`, `is_selenium_py`, `is_playwright_java`, `is_playwright_js`, `is_playwright_ts`, `is_playwright_py`, `is_puppeteer_js`, `is_puppeteer_ts`, `is_puppeteer_py`, `is_cypress_js`, `is_cypress_ts`.

---

## 4. `performance_testing_test_details` (11 colonne)

```text
repository_name   test_path   threadgroup_taskset_id
is_jmeter   is_locust   threadgroup_taskset_name
number_of_users   ramp_up   loop_count   duration   number_of_requests
```

Tutti i parametri numerici sono **stringhe**, non interi: possono contenere espressioni come `${utenti}`. Esempio reale
(`apache/roller`): `number_of_users='5'`, `ramp_up='300'`, `loop_count='20'`, `duration=NULL`, `number_of_requests='10'`.

> Il nome della colonna è **`loop_count`**, non `loop_cound` come stampato nella Figura 3 del paper. La figura ha il refuso, il database no.

---

## 5. `repository` (34 colonne) — contiene il commit di riferimento

```text
name  is_fork  commits  branches  releases  forks  main_language  default_branch  licences
homepage  watchers  stargazers  contributors  size  created_at  pushed_at  updated_at
total_issues  open_issues  total_pull_requests  open_pull_requests
blank_lines  code_lines  comment_lines  metrics
last_commit  last_commit_sha          <-- il commit su cui è stata eseguita la pipeline
has_wiki  is_archived  is_disabled  is_locked  languages  labels  topics
```

`last_commit_sha` è valorizzato per **tutti** i 472 repository GUI (verificato: 0 nulli). Esempio: `apache/roller` → `f6b3aa448d7703430e11b761b703b69020ea38a7`.

---

## 6. `non_trivial_repository` (6 colonne)

`name`, `is_web_java`, `is_web_python`, `is_web_javascript`, `is_web_typescript`, `web_dependencies`.

Le 14.053 righe sono i repository dopo il primo filtro; quelli con almeno un `is_web_*` a 1 sono **5.563**, cioè il campione su cui è stata cercata la presenza di test.

---

## 7. Come si legge `test_path`

Il formato **cambia tra le due tabelle**. Verificato su righe reali:

| Tabella | Valore nel DB | Regola | Percorso relativo |
|---|---|---|---|
| GUI | `/apache_roller/it-selenium/src/test/java/.../InitialLoginTestIT.java` | togli **1** segmento (`owner_repo`) | `it-selenium/src/test/java/.../InitialLoginTestIT.java` |
| Performance | `\apache\roller\testing\roller-load-test.jmx` | togli **2** segmenti (`owner`, `repo`) | `testing/roller-load-test.jmx` |

`src/01_estrai_repository.py` applica la regola giusta per tabella e produce la colonna `test_path_rel` in `data/tests_gui.csv` e `data/tests_perf.csv`.

---

## 8. Query di partenza

```sql
-- i repository da cui selezionare i 100, con il commit da usare
SELECT g.repository_name, g.number_of_tests, r.last_commit_sha
FROM gui_testing_repo_details g
JOIN repository r ON r.name = g.repository_name
ORDER BY g.number_of_tests DESC;

-- i file di test di un repository
SELECT test_path, number_of_tests
FROM gui_testing_test_details
WHERE repository_name = '10up/elasticpress';

-- chi fa sia GUI sia performance (13 repository)
SELECT repository_name FROM gui_testing_repo_details
INTERSECT
SELECT repository_name FROM performance_testing_test_details;

-- distribuzione dei test per repository
SELECT MIN(number_of_tests), AVG(number_of_tests), MAX(number_of_tests)
FROM gui_testing_repo_details;   -- 1 / 92,52 / 3352
```

---

## 9. Cosa NON c'è (e va prodotto da te)

- ❌ gli **esiti** dei test: nessuno li ha eseguiti;
- ❌ il **codice** dei test: solo il percorso, il file va preso dal repository;
- ❌ la **licenza** per repository: c'è `licences` in `repository`, ma va verificata a mano prima di ridistribuire dati derivati;
- ❌ i **Dockerfile** o le istruzioni di build;
- ❌ le **versioni** di browser, driver, JDK usate (non esistono, perché non c'è stata esecuzione).

---

*Documento generato dall'ispezione diretta del database. Se rigeneri i CSV con `src/01_estrai_repository.py`, i conteggi devono coincidere con quelli di §1.*
