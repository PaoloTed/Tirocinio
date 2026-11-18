# Roadmap di Progetto — Analisi Test E2E (Node.js + Playwright)

> Basata sull'analisi dello stato attuale del workspace e sulle indicazioni del **Ricevimento 4** ([ricevimento 4 ](../ricevimenti/ricevimento%204%20), [ricevimenti.md](../ricevimenti/ricevimenti.md)).

---

## 1. Stato attuale — Cosa è già stato fatto

### A. Selezione e filtraggio del dataset (Node.js + Playwright)
- **Censimento completo Playwright**: generato [repository_nodejs_playwright.txt](../02-E2EGit-TestE2E/repositories/repo_nodejs/playwright/repository_nodejs_playwright.txt) tramite [elenco_repo_playwright.py](../02-E2EGit-TestE2E/scripts/analisi_rq3/elenco_repo_playwright.py):
  - **154 repository Node.js** con Playwright (130 TypeScript, 24 JavaScript), di cui **140 esclusivamente Playwright** (138 JS/TS + 2 PW_PY) e **82 mature** (`TotTest > 10` e `Versioni > 5`, solo Playwright JS/TS).
- **Classifiche preliminari RQ3**: implementati [classifica_repo_rq3.py](../02-E2EGit-TestE2E/scripts/analisi_rq3/classifica_repo_rq3.py), [classifica_b_rq3.py](../02-E2EGit-TestE2E/scripts/analisi_rq3/classifica_b_rq3.py) e [storia_test_only_gui.py](../02-E2EGit-TestE2E/scripts/analisi_rq3/storia_test_only_gui.py) per ispezionare i file `*_only_gui.xlsx/.csv` di `RQ3` senza clonare le repository.

### B. Analisi delle finestre di commit Playwright
- **Calcolo intervalli disgiunti di stabilità ($\ge 70\%$ test invariati)**: lo script [calcola_intervalli_playwright.py](../02-E2EGit-TestE2E/scripts/analisi_rq3/calcola_intervalli_playwright.py) ha già elaborato tutte le 140 repository solo Playwright, producendo [intervalli_playwright_70.txt](../02-E2EGit-TestE2E/repositories/repo_nodejs/playwright/intervalli_playwright_70.txt) e [intervalli_playwright_70.csv](../02-E2EGit-TestE2E/repositories/repo_nodejs/playwright/intervalli_playwright_70.csv):
  - **137 repository valide**, **482 intervalli disgiunti** individuati (massimo 5 per repository).
  - **Lunghezza dell'intervallo principale (`#1`)**: mediana = **453 commit**, media = **921.3 commit** (min 6, max 20.806).
  - Questi numeri confermano l'utilità dell'**esecuzione binaria (bisezione)** richiesta al Ricevimento 4 per evitare di testare linearmente centinaia o migliaia di commit.

### C. Predisposizione delle repository campione
- In [02-E2EGit-TestE2E/repositories/repo_nodejs/playwright/](../02-E2EGit-TestE2E/repositories/repo_nodejs/playwright/) sono già presenti le **18 cartelle** delle repository selezionate (`css`, `fluentui`, `ketcher`, `koenig`, `lizmap-web-client`, `monokle`, `nocodb`, `novu`, `oneuptime`, `openmct`, `pc-nrfconnect-launcher`, `rocket.chat`, `sanity`, `sefaria-project`, `tldraw`, `trezor-suite`, `umbrel`, `xterm.js`), svuotate dai vecchi artefatti per ripartire con il nuovo flusso a singolo Dockerfile su finestre di commit.
- L'infrastruttura precedente basata sui tag (`analizza_versioni_test_e2e.py`, `genera_docker_nodejs.py`, `esegui_test_docker.py`) ha prodotto un solo report di esecuzione su Cypress (`angular-slickgrid`, `v5.5.0`: `PASS`), mentre per Playwright non ci sono ancora esecuzioni reali.

---

## 2. Problemi tecnici da sistemare subito

- **Path rotti negli script Python dopo lo spostamento di `data/` e `docs/`**:
  - Le cartelle `data/` e `docs/` si trovano ora nella root `/home/paolo/Scrivania/Universita/Tirocinio/`, fuori da `02-E2EGit-TestE2E/`.
  - Gli script in [02-E2EGit-TestE2E/scripts/](../02-E2EGit-TestE2E/scripts/) definiscono ancora `ROOT = Path(__file__).resolve().parents[1]` (che punta a `02-E2EGit-TestE2E/`) e cercano `data/E2EGit_e2e.db` lì dentro. Occorre aggiornare i percorsi puntando alla root superiore per `data/` (mantenendo `repositories/` sotto `02-E2EGit-TestE2E/`).

---

## 3. Cambio di paradigma (Ricevimento 4) e Cosa Manca

| Aspetto | Approccio precedente negli script | Nuovo approccio richiesto (Ricevimento 4) | Stato |
|---|---|---|---|
| **Unità di analisi** | Tag di release (`v1.0`, `v1.1`, ...) | **Finestra di commit** $[t_0, t_{end}]$ | Da adeguare |
| **Strategia Docker** | 1 `Dockerfile` per cluster + `docker build` da zero per ogni tag | **1 singolo `Dockerfile` per repository**, configurato e funzionante al commit iniziale $t_0$ | **Manca** |
| **Ricognizione repo** | Ispezione di `package.json` e lockfile | Verifica sistematica se la repo contiene già `Dockerfile`, `docker-compose`, workflow CI o istruzioni di test | Parziale |
| **Esecuzione test** | Container usa-e-getta (`docker build` + `docker run` per tag) | **Script di interfaccia uniformi** per tutte le repo (`start`, `restart`, `reset_t0`, `checkout`, `run_tests`, `get_results`) | **Manca** |
| **Strategia sulla finestra** | Esecuzione lineare di tutti i tag | **Esecuzione binaria (bisezione)** sulla finestra quando troppo lunga | **Manca** |
| **Analisi e correlazioni** | Report intervalli $\ge 70\%$ ([intervalli_playwright_70.csv](../02-E2EGit-TestE2E/repositories/repo_nodejs/playwright/intervalli_playwright_70.csv)) | Report statistico lunghezza finestre + **correlazione lunghezza finestra $\leftrightarrow$ probabilità di fallimento test** | **Manca** |

### Moduli e attività mancanti — Prossimi passi

1. **Fix path negli script e ripulitura/ripristino flusso di clonazione**:
   - Correggere i riferimenti a `data/` negli script Python (`classifica_repo_rq3.py`, `analizza_versioni_test_e2e.py`, ecc.).
2. **Mappatura `Commit k (RQ3)` $\rightarrow$ `SHA Git reale`**:
   - Tradurre gli indici dei commit non-merge presenti nei file `*_only_gui.xlsx/.csv` (`Commit Ca -> Commit Cb`) negli SHA Git reali della repository clonata, così da ottenere la lista esatta dei commit da $t_0$ a $t_{end}$.
3. **Analizzatore risorse Docker e istruzioni di test esistenti**:
   - Script di ricognizione al commit $t_0$ per verificare automaticamente la presenza di `Dockerfile`, `docker-compose*`, `.devcontainer`, script `package.json`, workflow `.github/workflows/*` e documentazione test, riducendo l'effort manuale di configurazione del singolo `Dockerfile`.
4. **Costruzione del primo `Dockerfile` a $t_0$ (repository pilota)**:
   - Scegliere una repository Playwright semplice tra le 18 selezionate e investire l'effort iniziale per far partire la prima versione del container al commit $t_0$ verificando che i test passino (baseline).
5. **Implementazione degli script di interfaccia uniformi**:
   - Definire un contratto standard uguale per tutte le repository (configurabile per singola repo, uniforme nei comandi esterni):
     1. `start` — far partire il repository / applicazione (e servizi necessari)
     2. `restart` — riavviare l'applicazione dopo un cambio di stato
     3. `reset_t0` — riportare il codice e l'ambiente al commit iniziale $t_0$
     4. `checkout <commit_x>` — spostarsi al commit $x$ (con eventuale rebuild)
     5. `run_tests` — eseguire i test Playwright con output strutturato (es. JSON reporter)
     6. `get_results` — estrarre e normalizzare i risultati (pass/fail per test, errori, durata)
6. **Orchestratore con esecuzione binaria (bisezione)**:
   - Verificare la baseline a $t_0$, testare l'estremo finale $t_{end}$ (o campionamenti) e, in caso di fallimento, applicare la ricerca binaria sull'intervallo $[t_0, t_{end}]$ ($\approx \log_2 N$ esecuzioni invece di $N$) per individuare il commit di rottura.
7. **Report sulle finestre e analisi di correlazione**:
   - Analizzare la distribuzione delle lunghezze delle finestre di commit (in numero di commit e in giorni).
   - Calcolare le correlazioni tra lunghezza della finestra (e altre metriche raccolte) e probabilità di fallimento dei test dopo aver eseguito i test sulle repository campione.

---

## 4. Cose da stabilire — Domande aperte

1. **Semantica di `checkout commit x` rispetto ai file di test**:
   - **(A)** Eseguire l'intero repository così com'è al commit $x$ (limitandosi ai file di test rimasti invariati tra $t_0$ e $x$)?
   - **(B)** Oppure eseguire `git checkout x` sull'applicazione ma **mantenere forzatamente i file di test alla versione $t_0$** (`git checkout t0 -- <test_files>`) per verificare se i vecchi test reggono sulle nuove versioni dell'app?
2. **Direzione della finestra ($t_0$ all'inizio o alla fine)**:
   - Partire sempre dal primo commit dell'intervallo ($t_0 = C_a \rightarrow C_b$) o considerare anche il verso inverso ($C_b \rightarrow C_a$)?
3. **Gestione build e dipendenze durante `checkout x`**:
   - Assumere che le dipendenze installate a $t_0$ restino valide lungo la finestra (facendo solo il rebuild applicativo se necessario), oppure rieseguire `npm/yarn/pnpm install` quando `package.json`/lockfile cambiano?
4. **Scelta della prima repository pilota**:
   - Quale delle 18 repository Playwright usare per prima per validare il `Dockerfile` singolo a $t_0$, gli script di interfaccia e la ricerca binaria (es. `xterm.js`, `openmct`, `css` o `ketcher`)?
