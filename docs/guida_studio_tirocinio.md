# Guida di Studio per il Tirocinio — Da Zero alla Pipeline E2E (Node.js + Playwright)

> Questa guida risponde punto per punto a tutti gli argomenti dei **Blocchi A e B**, collegando ogni concetto teorico al tuo lavoro reale su `E2EGit` + `IST2025` e alle indicazioni del **Ricevimento 4** ([roadmap.md](../roadmap/roadmap.md), [ricevimenti.md](../ricevimenti/ricevimenti.md)).

---

## Indice rapido

- **Blocco A — Docker applicato al tirocinio**
  1. [`--ipc=host` e `/dev/shm` con Chromium/Playwright](#1-docker-ipchost-e-devshm-con-chromiumplaywright)
  2. [Version mismatch tra `mcr.microsoft.com/playwright` e `@playwright/test`](#2-version-mismatch-tra-immagine-playwright-e-lockfile)
  3. [Flusso Ricevimento 4: `COPY . .` vs Volume/Bind Mount e Layer Caching](#3-flusso-ricevimento-4-copy---vs-volume-e-layer-caching)
- **Blocco B — I 4 pilastri operativi e scientifici**
  4. [Git avanzato (`checkout`/`switch`, `show`, `ls-tree`, `worktree`, `bisect`)](#4-git-avanzato-e-repository-mining)
  5. [Node.js, `package.json`, Lockfile (`pnpm`/`yarn`/`npm`) e `.github/workflows/`](#5-nodejs-packagejson-lockfile-e-github-actions)
  6. [Playwright in profondità (`.spec.ts`, `playwright.config.ts`, `webServer`, `reporter`, Trace)](#6-playwright-in-profondità-test-configurazione-e-debug)
  7. [Python di automazione, Bisezione e Statistica (mediana, correlazione, $p$-value)](#7-python-di-automazione-bisezione-e-statistica)
- **Percorso pratico consigliato (Tabella di marcia)**
  8. [Come studiare e mettere subito in pratica in 4 step](#8-tabella-di-marcia-pratica-in-4-step)

---

## 1. Docker: `--ipc=host` e `/dev/shm` con Chromium/Playwright

### Spiegazione semplice
In Linux la directory speciale `/dev/shm` (*Shared Memory*) è una porzione di RAM usata dai programmi per scambiarsi dati velocemente tra più processi (**IPC**, *Inter-Process Communication*).

Un browser moderno come **Chromium** non è un programma unico: apre un processo principale, un processo per ogni scheda (*renderer*), uno per la GPU, ecc. Per passarsi frame grafici e dati delle pagine web, questi processi scrivono dentro `/dev/shm`.

* **Il problema:** di default Docker limita `/dev/shm` dentro un container a soli **64 MB**. Per un'app web reale (dashboard, editor, tabelle complesse come quelle del tuo dataset), 64 MB finiscono subito.
* **Il sintomo senza `--ipc=host`:** il test parte, poi improvvisamente esplode con errori tipo `Target page, context or browser has been closed` o tab che vanno in crash (`Aw, Snap!`). Sembra un test *flaky* o un bug dell'app, invece è semplicemente il container che ha finito la memoria condivisa.
* **La soluzione:**
  * `--ipc=host` fa condividere al container lo spazio IPC (e quindi `/dev/shm`) della macchina host, rimuovendo il tetto dei 64 MB. È il flag raccomandato ufficialmente da Playwright per Linux/Docker (lo trovi già usato in [guida_dockerfile_manuali.md](./guida_dockerfile_manuali.md#L252-L266)).
  * *Alternativa più isolata:* `--shm-size=1gb` (assegna 1 GB dedicato a `/dev/shm` senza aprire l'IPC dell'host).

### Riferimenti e verifica
* Documentazione ufficiale Playwright (sezione Docker): <https://playwright.dev/> (*Docs → Docker*).
* Nel tuo repo: [guida_dockerfile_manuali.md](./guida_dockerfile_manuali.md#L247-L266).

---

## 2. Version mismatch tra immagine Playwright e lockfile

### Cosa succede
Un'immagine ufficiale come `mcr.microsoft.com/playwright:v1.36.0-jammy` contiene già Node.js, le librerie di sistema Ubuntu (`22.04 Jammy`) e i **binari dei browser** (Chromium, Firefox, WebKit) compilati esattamente per **`playwright@1.36.0`**.

Ogni versione di Playwright si aspetta una specifica *revision* interna del browser. Se l'immagine ha dentro i browser della `1.36.0`, ma al commit $t_0$ il progetto installa `@playwright/test@1.40.0` (dal `package-lock.json` o `pnpm-lock.yaml`):
1. Playwright `1.40.0` cerca la *sua* versione di Chromium (es. `chromium-1091`), non la trova nei binari preinstallati.
2. Il comando fallisce subito prima ancora di aprire la pagina con un errore tipo *Executable doesn't exist... Please run `npx playwright install`*.

### Come si evita e come si risolve
1. **Regola principale (quella da usare sempre a $t_0$):** leggi la **versione esatta `X.Y.Z`** risolta nel lockfile (non quella con `^` in `package.json`!) usando i comandi in [guida_dockerfile_manuali.md](./guida_dockerfile_manuali.md#L63-L79), e metti **esattamente la stessa `vX.Y.Z`** nella riga `FROM`:
   ```dockerfile
   FROM mcr.microsoft.com/playwright:v1.40.0-jammy
   ```
   *(Non usare mai `:latest`, altrimenti perdi la riproducibilità nel tempo.)*
2. **Se in mezzo a una finestra $[t_0, t_{end}]$ il progetto aggiorna Playwright:**
   * o esegui `npx playwright install chromium` dentro il container quando la versione cambia;
   * **attenzione alla trappola `PLAYWRIGHT_BROWSERS_PATH`:** le immagini ufficiali tengono i browser in una cartella globale (es. `/ms-playwright`). Se monti volumi o cambi quella variabile puntando alla home locale, Playwright non vedrà più i browser dell'immagine.

### Riferimenti
* Documentazione ufficiale Playwright Docker: <https://playwright.dev/> (*Docs → Docker*).
* Guida interna: [guida_dockerfile_manuali.md](./guida_dockerfile_manuali.md#L105-L120).

---

## 3. Flusso Ricevimento 4: `COPY . .` vs Volume e Layer Caching

### Perché il vecchio flusso non basta per le finestre di commit
Nel vecchio approccio per *tag* facevi `COPY . .` + `RUN npm ci` + `docker build` da zero per ogni versione. Ma le finestre Playwright del tuo studio hanno mediana **453 commit** (media **921.3**, fino a **20.806**, vedi [intervalli_playwright_70.txt](../02-E2EGit-TestE2E/repositories/nodejs/playwright/intervalli_playwright_70.txt)): rifare `docker build` e riscaricare `node_modules` a ogni commit è impraticabile.

Con il **Ricevimento 4** passi a **1 solo `Dockerfile` al commit $t_0$** + script uniformi (`start`, `restart`, `reset_t0`, `checkout <commit_x>`, `run_tests`, `get_results`). Ecco i due concetti Docker che rendono questo flusso veloce:

### A. Layer Caching nel `Dockerfile` (a $t_0$)
Docker costruisce l'immagine a strati (*layer*) e mette in cache ogni istruzione. Se un file cambia, invalida quel layer e **tutti quelli successivi**.
* **Sbagliato:**
  ```dockerfile
  COPY . .
  RUN npm ci
  ```
  Qualsiasi modifica a un file di test o sorgente fa rieseguire `npm ci` da capo.
* **Corretto:**
  ```dockerfile
  COPY package.json package-lock.json ./
  RUN npm ci
  COPY . .
  ```
  Così `npm ci` viene rieseguito **solo** se cambiano `package.json` o il lockfile.

### B. `COPY . .` vs Bind Mount (`-v`) durante `checkout <commit_x>`
Quando devi spostarti tra decine di commit in una finestra ($t_0 \to commit\_x$):
* **Approccio 1 — Container persistente (repo clonata dentro o copiata a $t_0$):**
  Avvii il container da $t_0$, poi lo script `checkout <commit_x>` esegue `git checkout <commit_x>` **dentro il container** (con `docker exec`). In pochi millisecondi Git aggiorna solo i file modificati, mantenendo intatti i `node_modules` già presenti.
  * *Nota furba:* con `git diff --name-only <prev> <x>` controlli se `package.json` o il lockfile sono cambiati: **solo in quel caso** rilanci `npm ci`.
* **Approccio 2 — Bind Mount (`-v /percorso/repo:/app`):**
  La cartella sul tuo PC e `/app` nel container sono la stessa cartella in tempo reale: fai `git checkout <commit_x>` sull'host e il container vede subito i file nuovi.
  * **Attenzione al conflitto su `node_modules`!** Il bind mount `-v /host/repo:/app` *nasconde* tutto ciò che avevi installato in `/app` durante il `docker build` (compresi i `node_modules` Linux del container!). Per proteggere i `node_modules` del container si aggiunge un volume dedicato:
    ```bash
    docker run --rm --ipc=host -v /host/repo:/app -v /app/node_modules ...
    ```
    *(Nei monorepo con più `node_modules` nelle sottocartelle, l'Approccio 1 — lavorare con `git checkout` dentro il container/volume — evita quasi sempre grattacapi di permessi e path multipli.)*

### Video YouTube e materiali consigliati
* **Documentazione ufficiale Docker — Build Cache:** <https://docs.docker.com/build/cache/>
* **YouTube (cerca esattamente questi titoli):**
  * `"Net Ninja Docker Crash Course"` *(spiegazione visiva chiara di immagini, container e layer caching)*
  * `"TechWorld with Nana Docker Volumes Bind Mounts"` *(differenza tra volumi anonimi, nominati e bind mount con esempi Node.js)*

---

## 4. Git avanzato e Repository Mining

### Il modello mentale di Git (fondamentale per capire gli script del tirocinio)
Git non salva "la lista delle differenze" come fa un editor di testo: ogni **commit** è una **fotografia completa** (*snapshot*) di tutte le cartelle in quell'istante, collegata al commit precedente (un grafo orientato aciclico, DAG).

I 4 mattoni di Git:
1. **Blob:** il contenuto puro di un file (identificato da un hash SHA).
2. **Tree:** una cartella (mappa nomi di file $\to$ blob o altri tree).
3. **Commit:** punta a un *Tree* radice + autore/data/messaggio + hash del *commit genitore*.
4. **Riferimenti (`HEAD`, branch, tag):**
   * Un **branch** (es. `main`) è un segnalibro mobile che avanza a ogni commit.
   * Un **tag** (es. `v1.11.0`) è un segnalibro fisso su un commit preciso.
   * **`HEAD`** indica dove sei ora. Quando fai `git checkout <SHA>`, `HEAD` punta direttamente a quel commit senza nessun branch: si chiama **`detached HEAD`** ed è esattamente lo stato normale in cui lavoreranno i tuoi script di test.

### I 5 comandi che userai davvero nel tirocinio

| Comando | Cosa fa in pratica | A cosa ti serve nel tirocinio |
|---|---|---|
| `git switch --detach <SHA>` *(o `git checkout <SHA>`)* | Porta la cartella di lavoro allo stato esatto di `<SHA>` | Implementare `checkout <commit_x>` e `reset_t0` |
| `git show <SHA>:package.json` | Legge un file a un commit passato **senza fare checkout** | Ricognizione automatica a $t_0$ senza sporcare i file |
| `git ls-tree -r --name-only <SHA>` | Elenca tutti i file esistenti a `<SHA>` | Trovare `playwright.config.*`, lockfile e `.github/workflows/` |
| `git rev-list --no-merges --reverse <commit>..HEAD` | Lista cronologica dei soli **commit non-merge** | **Cruciale:** i file `*_only_gui` di `RQ3` usano indici `Commit k` basati sui commit non-merge! Ti serve per tradurre `Commit Ca -> Cb` negli SHA reali |
| `git worktree add /tmp/wt <SHA>` | Apre un secondo commit in una cartella separata condividendo lo stesso `.git` | Usato in [esegui_test_docker.py](../02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py) per isolare/testare commit in parallelo |

### `git bisect`: il padre della tua "esecuzione binaria"
Nel Ricevimento 4 il professore ha chiesto di usare una **ricerca binaria** sulle finestre lunghe. È esattamente la stessa idea di `git bisect`:
* Hai un commit sano iniziale $t_0$ (**`good`**) e un commit finale $t_{end}$ dove il test fallisce (**`bad`**).
* Invece di provare tutti i 453 commit uno alla volta, provi il commit esattamente **a metà**:
  * se passa, il guasto è nella seconda metà;
  * se fallisce, il guasto è nella prima metà.
* Risultato: su 453 commit trovi il commit che ha rotto il test in circa $\lceil \log_2(453) \rceil = 9$ esecuzioni invece di 453!

### Video YouTube e letture consigliate
* **MIT Missing Semester — Version Control (Git):**
  * Canale YouTube: <https://www.youtube.com/@MissingSemester> (lezione *Version Control (Git)*)
  * Note ed esercizi: <https://missing.csail.mit.edu/>
* **Computerphile — Inside the Hidden Git Folder:** <https://www.youtube.com/watch?v=MVw0z_ZocxM> *(spiega cosa c'è dentro `.git`)*
* **Scott Chacon — Git From the Bits Up:** <https://www.youtube.com/watch?v=lG90qAKopIg>
* **Pro Git (libro gratuito ufficiale) — Cap. 10 Git Internals:** <https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain>
* **Video mirati su YouTube (cerca questi titoli):**
  * `"GitLab Git Internals Fear Not The SHA"`
  * `"Redhwan Nacef Git Worktree Tutorial"`
  * `"GitKraken Git Tutorial #36 How to Use Git Bisect"`
  * `"Josef Bender How To Find ANY Bug with Git Bisect"` *(mostra `git bisect run`, utilissimo come ispirazione per automatizzare i test)*
* Nel tuo repo: [guida_comandi_git.md](./guida_comandi_git.md).

---

## 5. Node.js, `package.json`, Lockfile e GitHub Actions

Quando apri per la prima volta una delle repository Playwright a $t_0$, non devi leggere tutto il codice sorgente dell'applicazione: devi saper leggere **4 file chiave** in 5 minuti.

### Checklist di ispezione a $t_0$

1. **Versione di Node.js:**
   * Controlla se esistono `.nvmrc` o `.node-version` nella root (contengono un numero tipo `18` o `20.11.0`).
   * Controlla il campo `"engines": { "node": "..." }` dentro `package.json`.
   * Se nessuno dei due c'è, guarda il workflow GitHub Actions (punto 4).
2. **Package manager e lockfile:**
   * `package-lock.json` $\to$ usa **`npm ci`** *(Clean Install: cancella eventuali residui e installa le versioni esatte del lockfile, fallendo se `package.json` non combacia)*. Non usare `npm install`!
   * `yarn.lock` $\to$ usa **`yarn install --frozen-lockfile`**.
   * `pnpm-lock.yaml` $\to$ usa **`corepack enable && pnpm install --frozen-lockfile`**.
3. **Sezione `"scripts"` e `"workspaces"` di `package.json`:**
   * `"scripts"` ti dice come si compila (`"build"`) e come si avviano app e test (`"start"`, `"dev"`, `"test:e2e"`, `"pw"`).
   * Se vedi `"workspaces": ["packages/*", "apps/*"]` o un file `pnpm-workspace.yaml`, sei in un **monorepo**: le dipendenze si installano dalla root, ma i test Playwright potrebbero trovarsi in una sottocartella (es. `apps/e2e`) e lanciarsi con `pnpm --filter <pacchetto> test:e2e` o `npm --workspace=... run ...`.
4. **`.github/workflows/*.yml` — la "ricetta" già pronta della CI:**
   Un workflow YAML descrive esattamente come gli autori stessi eseguono Playwright sui server di GitHub:
   ```yaml
   jobs:
     e2e:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/setup-node@v4
           with:
             node-version: 20          # <- ti dice la versione di Node!
         - run: pnpm install --frozen-lockfile
         - run: pnpm build             # <- step preparatorio necessario!
         - run: pnpm test:e2e          # <- comando esatto dei test!
           env:
             CI: true                  # <- variabili d'ambiente richieste!
   ```
   **Cosa cercare sempre dentro il file `.yml`:**
   * Se ci sono `services:` (es. PostgreSQL, Redis, MongoDB): se i test richiedono un database esterno, dovrai saperlo prima di scrivere il `Dockerfile` singolo (oppure usare `docker-compose` / scegliere prima repo che non ne dipendono).
   * Se ci sono step di `build`, `codegen`, `seed` o un server avviato in background (`npm start &`).

### Video YouTube consigliati (cerca questi titoli)
* `"GitHub actions nodejs CI setup npm ci package-lock.json tutorial"`
* `"pnpm monorepo workspace tutorial GitHub actions CI CD"`
* `"How to Run Playwright Tests in GitHub Actions | Complete YAML Guide"`

---

## 6. Playwright in profondità: test, configurazione e debug

### Differenza fondamentale: Browser Automation vs Test Runner
Come evidenziato anche nel riassunto del paper ([E2EGit_riassunto_e_concetti.md](./letteratura/E2EGit_riassunto_e_concetti.md#L86-L94)):
* Il pacchetto `playwright` da solo è la libreria che comanda il browser.
* **`@playwright/test`** è il pacchetto completo che include sia l'automazione del browser sia il **test runner** (`test(...)`, `expect(...)`, gestione retry, reporter JSON/HTML).
* *(Nota dal tuo dataset [repository_nodejs_playwright.txt](../02-E2EGit-TestE2E/repositories/nodejs/playwright/repository_nodejs_playwright.txt#L34): su 154 repo Node+Playwright, molte usano il runner di Playwright/Jest/Mocha/Jasmine — quindi verifica sempre quale comando lancia i test.)*

### Come leggere un file `.spec.ts` / `.spec.js`
```typescript
import { test, expect } from '@playwright/test';

test('l utente riesce ad aprire il pannello', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Accedi' }).click();
  await expect(page.getByText('Dashboard')).toBeVisible();
});
```
* **`{ page }`:** è una scheda isolata del browser (niente cache/cookie condivisi tra un test e l'altro).
* **Locators** (`getByRole`, `getByTestId`, `locator('.btn')`): individuano gli elementi nella pagina. Quando l'app cambia (es. un bottone cambia testo o classe CSS) ma il test resta fermo a $t_0$, il locator non trova più l'elemento e il test va in timeout.
* **Auto-waiting:** Playwright prima di cliccare o verificare `toBeVisible()` aspetta automaticamente che l'elemento esista e sia visibile (fino al timeout configurato, di solito 30 secondi).

### I 4 blocchi di `playwright.config.ts` che contano per il tirocinio
```typescript
export default defineConfig({
  testDir: './tests/e2e',             // 1. Dove stanno i test
  retries: process.env.CI ? 2 : 0,    // 2. Quanti retry fa se un test fallisce
  webServer: {                        // 3. CRUCIALE: avvia il server da solo!
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',          // 4. Salva trace.zip per il debug
  },
  reporter: [['json', { outputFile: 'results.json' }]],
});
```
* **Attenzione al blocco `webServer`:**
  * Se **è presente** in `playwright.config.*`, lanciando `npx playwright test` Playwright avvia l'app, attende che `localhost:3000` risponda, esegue i test e chiude il server.
  * Se **non c'è** (vedi solo `baseURL`), il tuo script `start` dovrà lanciare il server dell'app in background e aspettare che la porta sia aperta prima di chiamare `run_tests`.
* **Reporter JSON (per lo script `get_results`):**
  Puoi forzarlo anche da riga di comando senza toccare il file di config:
  ```bash
  PLAYWRIGHT_JSON_OUTPUT_NAME=results.json npx playwright test --reporter=json
  ```
  Il file `results.json` prodotto contiene l'esito di ogni singolo test (`expected` = passato, `unexpected` = fallito, `flaky` = passato al retry, `skipped`), la durata e il messaggio di errore esatto.
* **Trace Viewer (per capire *perché* un test si rompe):**
  Se lanci con `--trace on`, Playwright salva un file `trace.zip`. Caricandolo su <https://trace.playwright.dev/> (o con `npx playwright show-trace trace.zip`) vedi una timeline con screenshot prima/dopo ogni click, chiamate di rete e log console.

### Video YouTube e risorse consigliate
* **Documentazione ufficiale:** <https://playwright.dev/> *(leggi in particolare: Writing tests, Test configuration, Web server, Reporters, Trace viewer)*.
* **Trace Viewer online:** <https://trace.playwright.dev/>
* **Video YouTube (cerca esattamente questi titoli):**
  * `"Software Testing with Playwright freeCodeCamp"` *(corso completo sul canale freeCodeCamp.org)*
  * `"Introduction to Playwright for End-to-End Testing with Debbie O'Brien"` *(breve e chiarissimo su config, codegen e trace viewer)*
  * `"Automation Step by Step Playwright Beginner Playlist"` *(playlist guidata passo passo)*
  * `"Playwright CI/CD: Sharding, Docker, and GitHub Actions"`

---

## 7. Python di automazione, Bisezione e Statistica

### A. I moduli Python usati negli script del tirocinio
Gli script in [02-E2EGit-TestE2E/scripts/](../02-E2EGit-TestE2E/scripts/README.md) usano quasi solo la libreria standard Python:
* **`pathlib.Path`**: percorsi puliti (`ROOT / "data" / "E2EGit_e2e.db"`).
* **`subprocess.run(..., capture_output=True, text=True, timeout=...)`**: serve per orchestrare `git`, `docker` e i tuoi 6 script uniformi. Controlli `res.returncode` (`0` = successo, diverso da zero = errore), `res.stdout`, `res.stderr`, e gestisci `subprocess.TimeoutExpired` se un test o server si blocca all'infinito.
* **`sqlite3`**: apre `E2EGit_e2e.db` ed esegue query SQL (`SELECT test_path FROM gui_testing_test_details WHERE ...`) come vedi in [calcola_intervalli_playwright.py](../02-E2EGit-TestE2E/scripts/analisi_rq3/calcola_intervalli_playwright.py#L114-L120).
* **`json` e `csv`**: in `get_results` leggi il JSON di Playwright con `json.load()` e scrivi righe tabellari nel CSV finale con `csv.DictWriter`.

**Video YouTube verificati (canale Corey Schafer):**
* **`subprocess`:** [Python Tutorial: Calling External Commands Using the Subprocess Module](https://www.youtube.com/watch?v=OFjsWhZXV6U)
* **`sqlite3`:** [Python SQLite Tutorial: Complete Overview](https://www.youtube.com/watch?v=pd-0tG9CLgQ)

### B. Progettare la ricerca binaria (bisezione) su finestre reali
In teoria la ricerca binaria su una lista ordinata di commit `[C_0, C_1, ..., C_{N-1}]` fa:
1. Verifica $C_0$ ($t_0$): **deve dare `PASS`** (altrimenti la baseline non funziona e non puoi bisecare).
2. Verifica $C_{N-1}$ ($t_{end}$): se dà `PASS`, il test ha retto da inizio a fine finestra; se dà `TEST_FAIL`, cerchi il punto di rottura.
3. Finché `low + 1 < high`: testa `mid = (low + high) // 2`. Se `PASS`, `low = mid`; se `TEST_FAIL`, `high = mid`.

**Due complicazioni pratiche che incontrerai nel tirocinio (e che fanno fare bella figura al ricevimento):**
1. **`BUILD_FAIL` a metà finestra:** nei commit intermedi (non taggati come release) può capitare che il progetto non compili. Un `BUILD_FAIL` *non* è un `TEST_FAIL`! Se `mid` non compila, l'algoritmo deve provare commit vicini (`mid + 1`, `mid - 1`, ecc.) finché trova un commit compilabile (come fa `git bisect skip`).
2. **Test *flaky*:** se a `mid` ottieni `TEST_FAIL`, rilancia quel test 2–3 volte prima di confermare il fallimento, altrimenti un errore casuale di rete/timing manda la bisezione nella metà sbagliata dell'intervallo.

*(Cerca su YouTube `"binary search algorithm explained"` se vuoi ripassare l'idea generale in 5 minuti.)*

### C. La statistica che ti serve per il report finale al professore

1. **Media vs Mediana (e IQR):**
   Guarda i numeri già usciti in [intervalli_playwright_70.txt](../02-E2EGit-TestE2E/repositories/nodejs/playwright/intervalli_playwright_70.txt#L8):
   * Intervallo `#1`: **mediana = 453 commit**, **media = 921.3 commit** (min 6, max **20.806**!).
   Perché la media è più del doppio della mediana? Perché poche repository enormi (outlier come 20.806) tirano verso l'alto la media. Nei dati di ingegneria del software (*skewed*, asimmetrici), si riportano sempre **mediana** e **IQR** (*Interquartile Range*, tra 25° e 75° percentile) accanto a min/max.
2. **Correlazione: Pearson ($r$) vs Spearman ($\rho$):**
   Al Ricevimento 4 il professore ha chiesto: *"vedere se ci sono correlazioni tra lunghezza della finestra e probabilità di fallimento di test"*.
   * **Pearson ($r$):** misura se due variabili stanno su una **retta** (relazione lineare). È molto sensibile agli outlier (un intervallo da 20.806 commit distorce il calcolo).
   * **Spearman ($\rho$):** trasforma prima i valori in **classifiche/ranghi** (1°, 2°, 3°...) e misura una relazione **monotona** ("al crescere della lunghezza della finestra, cresce tendenzialmente anche il tasso di fallimento?"). È la scelta standard nei paper empirici come `E2EGit`!
   * *Nota:* se la variabile finale è binaria per finestra (`0 = passato a t_end`, `1 = fallito a t_end`), oltre a Spearman puoi confrontare la distribuzione delle lunghezze delle finestre fallite vs passate (es. test di **Mann–Whitney U**) o usare una **regressione logistica** per stimare la *probabilità* di fallimento in funzione della lunghezza della finestra.
3. **$p$-value (in parole semplici):**
   Misura la probabilità di vedere una correlazione grande almeno quanto quella osservata *se in realtà non ci fosse alcun legame* (ipotesi nulla). Per convenzione, se $p < 0.05$ il risultato si dice "statisticamente significativo" — ricordando sempre che su poche repository (es. 10–18) il $p$-value può essere alto anche se una tendenza c'è, e che *correlazione non dimostra causalità*.

**Video YouTube verificati (canale StatQuest with Josh Starmer):**
* **Media vs Mediana:** [The mean, the median, and the mode](https://www.youtube.com/watch?v=5CcV_io0mEQ)
* **Correlazione di Pearson:** [Pearson's Correlation, Clearly Explained!!!](https://www.youtube.com/watch?v=xZyxvBBP0k4)
* **Capire i $p$-value:** [p-values: What they are and how to interpret them](https://www.youtube.com/watch?v=IZUfbRvsZ9w) e [How to calculate p-values](https://www.youtube.com/watch?v=JQc3yx0-Q9E)
* **Per Spearman:** cerca su YouTube `"Spearman's rank correlation simply explained"` *(ottimi i video brevi di **ritvikmath** o **Steven Bradburn**)*.

---

## 8. Tabella di marcia pratica in 4 step

| Fase | Cosa studi prima | Cosa fai subito nel workspace |
|---|---|---|
| **Step 1 — Capire una repo** | Sezioni **4** (Git) e **5** (Node/CI) | Scegli una repo semplice dall'elenco di [intervalli_playwright_70.txt](../02-E2EGit-TestE2E/repositories/nodejs/playwright/intervalli_playwright_70.txt), guardane `package.json`, lockfile e `.github/workflows/` al commit $t_0$ (`git show`) |
| **Step 2 — Primo container $t_0$** | Sezioni **1, 2, 3** (Docker) e **6** (Playwright) | Costruisci **1 `Dockerfile` a $t_0$**, lancialo con `--ipc=host` e verifica che i test passino producendo `--reporter=json` |
| **Step 3 — Script uniformi + bisezione** | Sezione **7A e 7B** (Python `subprocess` + bisezione) | Implementa i 6 comandi (`start`, `restart`, `reset_t0`, `checkout`, `run_tests`, `get_results`) e prova la ricerca binaria su 1 finestra |
| **Step 4 — Scala e Analisi** | Sezione **7C** (Statistica) + [E2EGit_riassunto_e_concetti.md](./letteratura/E2EGit_riassunto_e_concetti.md) | Esegui sulle altre repo pilota, raccogli i CSV e calcola statistiche descrittive e correlazione lunghezza $\leftrightarrow$ fallimento |

