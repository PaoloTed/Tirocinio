# Guida Pratica: Come Controllare e Configurare una Repository Node.js + Playwright

> Questa guida raccoglie **tutto ciò che devi controllare** (in ordine esatto, quali file aprire, quali comandi lanciare e quali guide `.md` consultare) prima di configurare il `Dockerfile` singolo a $t_0$ e far girare i 6 script su una nuova repository.

---

## Indice dei file `.md` di riferimento nel progetto

| File | A cosa ti serve |
|---|---|
| [repository_nodejs_playwright.txt](./playwright/repository_nodejs_playwright.txt) | Elenco delle 154 repo Node+Playwright con framework, motore di test, file e stelle |
| [intervalli_playwright_70.txt](./playwright/intervalli_playwright_70.txt) | Intervalli di commit $[C_a, C_b]$ dove $\ge 70\%$ dei test non cambia (e [CSV](./playwright/intervalli_playwright_70.csv)) |
| [scripts/interfaccia/README.md](../../scripts/interfaccia/README.md) | Uso dei 6 script Python (`start.py`, `restart.py`, `reset_t0.py`, `checkout.py`, `run_tests.py`, `get_results.py`) |
| [docs/guida_dockerfile_manuali.md](../../../docs/guida_dockerfile_manuali.md) | Istruzioni Playwright nei `Dockerfile`, immagini `mcr.microsoft.com/playwright` e debug container |
| [docs/guida_comandi_git.md](../../../docs/guida_comandi_git.md) | Comandi Git per ispezionare commit, tag, branch e fare pulizia |
| [docs/guida_studio_tirocinio.md](../../../docs/guida_studio_tirocinio.md) | Spiegazione approfondita di Docker, Git, Node/CI, Playwright, Python e statistica |
| [roadmap/roadmap.md](../../../roadmap/roadmap.md) | Stato generale del progetto e indicazioni del Ricevimento 4 |

---

## Passo 0 — Scegliere la repository dai file del dataset

1. Apri [repository_nodejs_playwright.txt](./playwright/repository_nodejs_playwright.txt):
   * **Preferisci** le repository nella sezione **`Framework: Playwright`** (solo Playwright, non multi-framework come `Playwright + Cypress` o `Puppeteer`).
   * Controlla la colonna **`MotoreTest`**: le repo con `@playwright/test` nativo sono le più lineari; se usano Jest/Mocha bisognerà adattare `test_cmd` e il parser risultati.
   * All'inizio evita i giganti enormi (es. `vscode`, `fluentui`, `rocket.chat`) perché compilano troppo lentamente: parti da repo medie con **5–50 file di test**.
2. Apri [intervalli_playwright_70.txt](./playwright/intervalli_playwright_70.txt) e cerca la repo scelta:
   * Annota **`Commit Ca`** ($t_0$) e **`Commit Cb`** ($t_{end}$) dell'`Intervallo #1` (con le **date** esatte).
   * Controlla la durata in commit: intervalli tra **50 e 600 commit** sono ottimi per provare prima lineare su pochi commit e poi la ricerca binaria.

---

## Passo 1 — Clonare e ricavare gli SHA reali di $t_0$ e $t_{end}$

1. **Clonazione in `02-E2EGit-TestE2E/repositories/nodejs/playwright/<nome_repo>/repo`:**
   * Se vuoi solo ispezionare i file velocemente usa [clona_repository.sh](../../scripts/git_versioni/clona_repository.sh) (`--filter=blob:none --no-checkout`).
   * Però per usare i 6 script dentro Docker **senza dipendere dalla rete ad ogni `checkout`**, conviene un clone completo (`git clone <url_github> repo`) oppure scaricare tutti i file mancanti se avevi già fatto un partial clone:
     ```bash
     git -C 02-E2EGit-TestE2E/repositories/nodejs/playwright/<nome_repo>/repo fetch --refetch
     ```
2. **Tradurre `Commit Ca` e `Commit Cb` in SHA Git reali:**
   * I numeri `Commit 2251` di `intervalli_playwright_70.txt` sono gli indici delle colonne del file `data/IST2025_Zenodo/RQ3/commit-analysis/<owner_repo>/*_only_gui.xlsx` (basati sui commit **non-merge**).
   * Usa [trova_intervallo_sha_commit.sh](../../scripts/git_versioni/trova_intervallo_sha_commit.sh) oppure cerca per data e ora esatta:
     ```bash
     # 1. Leggi data e ora esatte di Commit Ca / Cb dal file *_only_gui.xlsx
     # 2. Trova lo SHA corrispondente in Git
     git -C repo log --all --no-merges --format="%H  %ai  %ci  %s" | grep "YYYY-MM-DD"
     ```
   * Verifica che lo SHA scelto corrisponda all'ora riportata nella colonna del file `.xlsx`.

---

## Passo 2 — Ispezione completa al commit $t_0$ (senza modificare file)

Puoi ispezionare la repository al commit `<SHA_T0>` in due modi equivalenti:
* **Dal browser su GitHub:** sostituisci `main` nell'URL con lo SHA di $t_0$, ad esempio `https://github.com/<owner>/<repo>/tree/<SHA_T0>`.
* **Dal terminale (senza fare checkout):** lancia questo comando per vedere tutti i file di configurazione esistenti esattamente al commit `<SHA_T0>`:

```bash
git -C repo ls-tree -r --name-only <SHA_T0> | grep -E 'playwright\.config|package\.json$|lock|pnpm-workspace|\.nvmrc|\.node-version|\.github/workflows|Dockerfile|docker-compose|\.env'
```

Poi apri e controlla **tutti e 7 questi punti** usando `git -C repo show <SHA_T0>:<percorso_file>`:

### 1. `.github/workflows/*.yml` *(Il file più importante)*
Cerca il workflow che esegue i test E2E / Playwright e controlla:
* **`actions/checkout`:** verifica se clona **un altro repository esterno** (`repository: ...` diverso dal repo attuale) $\rightarrow$ se sì, è un forte segnale per **scartare** la repo (vedi `podkrepi-frontend`).
* **`actions/setup-node`:** annota `node-version` (es. `16`, `18`, `20`).
* **`services:` o `docker compose`:** controlla se richiede database/servizi esterni pesanti (PostgreSQL, Redis, Elasticsearch, Stripe webhook).
* **Pacchetti di sistema (`apt-get`):** controlla se installa librerie o font extra (es. `msttcorefonts`).
* **Variabili `env:` e `secrets.`:** se servono chiavi segrete reali (`API_KEY`, OAuth) senza fallback mock, i test falliranno.
* **Comandi `run:`:** annota la sequenza esatta usata dagli autori per **install**, **build** e **lancio test**.

### 2. `Dockerfile` / `docker-compose.yml` già presenti nella repo
* Controlla se la repo ha già un `Dockerfile` per i test/CI o un `docker-compose` di sviluppo/test.
* *Attenzione:* spesso il `Dockerfile` nella root serve solo a deployare l'app in produzione (senza browser Playwright), quindi non basta così com'è ma ti svela comunque build, porte e variabili d'ambiente.

### 3. `package.json` (root e sottocartelle tipo `e2e/` o `packages/*/`)
* **`"workspaces"`** (o `pnpm-workspace.yaml`): ti dice se è un **monorepo** (come `tryghost/koenig`).
* **`"scripts"`:** cerca `setup`, `build`, `start`, `dev`, `pretest`, `test`, `test:e2e`.
* **`"dependencies"` / `"devDependencies"`:** capisci **in quale cartella** si trova `@playwright/test` (root o sottocartella come `e2e/` o `packages/koenig-lexical/`). Quella cartella sarà `test_workdir` in `config.json`.
* **`"engines"`, `.nvmrc`, `.node-version`:** confermano la versione di Node attesa.
* **`"packageManager"` e `"prepare"`:** se in `"prepare"` c'è `husky install`, imposta `ENV HUSKY=0` nel `Dockerfile` per evitare errori di hook.

### 4. Lockfile (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`)
* **Quale package manager usare** (sempre in modalità bloccata per riproducibilità!):
  * `package-lock.json` $\rightarrow$ `npm ci`
  * `yarn.lock` (Yarn 1) $\rightarrow$ `yarn install --frozen-lockfile`
  * `yarn.lock` + `.yarnrc.yml` (Yarn 2/3/4) $\rightarrow$ `yarn install --immutable`
  * `pnpm-lock.yaml` $\rightarrow$ `corepack enable && pnpm install --frozen-lockfile`
* **Versione esatta `X.Y.Z` di Playwright** (ti serve per scegliere `FROM mcr.microsoft.com/playwright:vX.Y.Z-jammy`, o `-focal` se $\le$ `1.21.x`):
  ```bash
  # npm (package-lock.json)
  git -C repo show <SHA_T0>:package-lock.json | grep -A4 -E '"node_modules/(@playwright/test|playwright)"'

  # yarn (yarn.lock)
  git -C repo show <SHA_T0>:yarn.lock | grep -A3 -E '^"?(@playwright/test|playwright)@'

  # pnpm (pnpm-lock.yaml)
  git -C repo show <SHA_T0>:pnpm-lock.yaml | grep -E '(@playwright/test|playwright):' | head -n 10
  ```

### 5. `playwright.config.ts` / `.js` / `.mjs`
Controlla questi 5 campi nel file di configurazione:
* **`testDir`:** cartella dei test (per verificare che corrisponda ai file censiti in `RQ3`).
* **`baseURL`:** deve puntare a **`http://localhost:<porta>`** (se punta a un dominio pubblico esterno come `https://dev.miosito.org`, non stai testando il commit locale!).
* **`webServer`:**
  * Se **c'è** `webServer: { command: ..., url: ... }`: Playwright avvia e ferma l'app da solo $\rightarrow$ in `config.json` lasci `"app_start_cmd": ""` e `"app_url": ""`.
  * Se **non c'è**: devi compilare e avviare tu il server prima dei test $\rightarrow$ imposti `"app_start_cmd"` e `"app_url"` in `config.json`.
* **`projects`:** guarda se lancia solo `chromium` o anche `firefox` / `webkit` / `chrome` (se chiede `channel: 'chrome'` o `msedge`, potrebbe servire installarli a parte).
* **`reporter`:** controlla se ha impostazioni strane che confliggono con `--reporter=json,list` passato da [run_tests.py](../../scripts/interfaccia/run_tests.py).

### 6. File `.env*` e `README.md` (o `e2e/README.md`)
* Se vedi `.env.example` / `.env.local.example`, controlla se `predev` o il workflow CI fanno `cp .env.local.example .env.local`.
* Dai un'occhiata veloce al `README.md` (soprattutto alla sezione *Testing / Contributing*) per eventuali prerequisiti tipo `yarn setup` o `lerna run build`.

### 7. Campione di 1–2 file di test (`.spec.ts` / `.test.js`)
Apri un paio di file dalla lista dei test E2E:
```bash
git -C repo show <SHA_T0>:<percorso/esempio.spec.ts>
```
Verifica che navighino sull'app locale e non dipendano da siti esterni o credenziali reali.

---

## Passo 3 — Verdetto Semaforo (tenere o scartare?)

| Stato | Criteri | Cosa fare |
|---|---|---|
| 🟢 **OK — Procedi** | Autocontenuta nella stessa repo; usa `@playwright/test` standard; `baseURL` su `localhost`; niente repo esterni né DB pesanti; build ragionevole (es. `tryghost/koenig`) | Passa al **Passo 4** |
| 🟡 **Forse — Da valutare** | Usa `playwright` con Jest/Mocha invece di `@playwright/test`, oppure ha build lenta (Next.js/monorepo grande), oppure ha un solo servizio leggero già incluso | Valuta se tenerla per dopo o adattare `test_cmd` / parser JSON |
| 🔴 **Scarta** | Clona un secondo repository per il backend (es. `podkrepi-bg/frontend`); richiede stack multi-container pesante; testa un sito esterno invece di `localhost`; richiede segreti privati; ha 0/1 test reali | Documenta il motivo e passa alla repo successiva |

---

## Passo 4 — Dove mettere le cose trovate (`Dockerfile`, `.dockerignore`, `config.json`)

Questa tabella ti mostra esattamente **dove finisce** ogni informazione scoperta al Passo 2 e **quale script la usa**:

| Cosa hai trovato al Passo 2 | File da compilare | Campo / Riga | Chi lo usa |
|---|---|---|---|
| **Versione `X.Y.Z`** di `@playwright/test` nel lockfile | `Dockerfile` | `FROM mcr.microsoft.com/playwright:v<X.Y.Z>-jammy` | `start.py` (`docker build`) |
| **SHA di $t_0$** (`Commit Ca` in `intervalli_playwright_70.txt`) | `Dockerfile` + `config.json` | `ARG T0_COMMIT=...` e `"t0_commit"` | `start.py`, `reset_t0.py` |
| **Hook `husky`** in `package.json` (`"prepare"`) | `Dockerfile` | `ENV CI=true HUSKY=0` | `start.py` (`docker build`) |
| **Package manager + lockfile** (`npm` / `yarn` / `pnpm`) | `Dockerfile` + `config.json` | `RUN <install>` e `"install_cmd"` | `start.py`, `checkout.py` |
| **Build / `lerna` / `.env`** (da CI workflow e `README.md`) | `Dockerfile` + `config.json` | `RUN <build>` e `"build_cmd"` *(vuoto `""` se non serve)* | `start.py`, `checkout.py` |
| **Presenza di `webServer`** in `playwright.config.*` | `config.json` | Se c'è: `"app_start_cmd": ""`, `"app_url": ""`. Se manca: comando server + `baseURL` | `start.py`, `restart.py`, `checkout.py` |
| **Cartella** che contiene `playwright.config.*` | `config.json` | `"test_workdir": "/app/<sottocartella>"` (o `"/app"`) | `run_tests.py` |
| **Script E2E** (da `package.json` o CI, incluse eventuali `ENV`) | `config.json` | `"test_cmd"` (deve finire con `playwright test` così `run_tests.py` può aggiungere `--reporter=json,list`) | `run_tests.py` |
| **Cartelle pesanti / generate** (`node_modules`, `dist`, `.next`, report) | `Dockerfile.dockerignore` | Un pattern per riga (**mai** mettere `.git`!) | `start.py` (`docker build`) |

---

### Esempio reale completo: `tryghost/koenig`

Qui sotto vedi **una alla volta** tutte le 8 cose reali trovate dentro `tryghost/koenig` al commit `25bc8a51` (`Commit 2251`), con **il pezzo esatto trovato nel file** e **dove va messo**, e subito dopo i 3 file completi assemblati.

#### Parte A — Ogni singola cosa trovata → dove l'ho trovata → dove va messa

1. **Commit iniziale $t_0$ (`25bc8a51...`)**
   * **Dove l'ho trovato:** in [intervalli_playwright_70.txt](./playwright/intervalli_playwright_70.txt) (`Intervallo #1: Commit 2251 (2023-10-04)`), poi verificato con data/ora esatta (`2023-10-04 11:06:53`) in `commits_analysistryghost_koenig_only_gui.xlsx` e `git log`:
     ```text
     25bc8a514eb8b080a4ed23959ac4229f18cb3cff  2023-10-04 11:06:53 +0100  🐛 Fixed drag-to-select...
     ```
   * **Dove va:**
     * in `Dockerfile` $\rightarrow$ `ARG T0_COMMIT=25bc8a514eb8b080a4ed23959ac4229f18cb3cff`
     * in `config.json` $\rightarrow$ `"t0_commit": "25bc8a514eb8b080a4ed23959ac4229f18cb3cff"`

2. **Versione esatta di Playwright (`1.38.1`)**
   * **Dove l'ho trovata:** nel file **`yarn.lock`** nella root del repository:
     ```yaml
     "@playwright/test@^1.33.0":
       version "1.38.1"
     ```
   * **Dove va:**
     * in `Dockerfile` $\rightarrow$ `FROM mcr.microsoft.com/playwright:v1.38.1-jammy`

3. **Package manager e comando di installazione (`yarn` v1)**
   * **Dove l'ho trovato:** nella root c'è **`yarn.lock`** senza `.yarnrc.yml` (quindi Yarn 1) e **`.github/workflows/test.yml`** lancia `run: yarn`.
   * **Dove va:**
     * in `Dockerfile` $\rightarrow$ `RUN ... yarn install --frozen-lockfile`
     * in `config.json` $\rightarrow$ `"install_cmd": "yarn install --frozen-lockfile"`

4. **Git hook `husky` da disattivare in Docker**
   * **Dove l'ho trovato:** nel file **`package.json`** nella root:
     ```json
     "prepare": "husky install .github/hooks"
     ```
   * **Dove va:**
     * in `Dockerfile` $\rightarrow$ `ENV CI=true HUSKY=0`

5. **Struttura monorepo e comando di build (`lerna`)**
   * **Dove l'ho trovato:** in **`README.md`** (*"run `yarn setup` from the top-level"*) e nel file **`package.json`** nella root:
     ```json
     "workspaces": ["packages/*"],
     "scripts": {
       "setup": "yarn && lerna run build"
     }
     ```
   * **Dove va:**
     * in `Dockerfile` $\rightarrow$ `RUN ... yarn lerna run build`
     * in `config.json` $\rightarrow$ `"build_cmd": "yarn lerna run build"`
     * in `Dockerfile.dockerignore` $\rightarrow$ `**/node_modules` e `**/dist` *(così ignora le cartelle generate dentro ogni sottocartella di `packages/`)*

6. **Cartella dove eseguire Playwright (`test_workdir`)**
   * **Dove l'ho trovata:** elencando i file con `git ls-tree` (o navigando su GitHub dentro `packages/`):
     ```text
     packages/koenig-lexical/playwright.config.js
     packages/koenig-lexical/test/e2e/cards/code-block-card.test.js
     ```
   * **Dove va:**
     * in `config.json` $\rightarrow$ `"test_workdir": "/app/packages/koenig-lexical"`

7. **Server dell'app (`webServer` già gestito da Playwright, niente backend esterno)**
   * **Dove l'ho trovato:** in **`.github/workflows/test.yml`** non ci sono altri repository né `services:` DB, e in **`packages/koenig-lexical/playwright.config.js`** c'è già:
     ```js
     webServer: {
         command: `yarn dev:test`,
         url: `http://localhost:${E2E_PORT}`,
         reuseExistingServer: !process.env.CI,
         timeout: 10000
     }
     ```
   * **Dove va:**
     * in `config.json` $\rightarrow$ `"app_start_cmd": ""` e `"app_url": ""` *(vuoti perché Playwright accende Vite da solo)*.
     * *(Confronto — caso senza `webServer`: in [podkrepi-frontend/docker/config.json](./podkrepi-frontend/docker/config.json) invece `playwright.config.ts` ha solo `baseURL: 'http://localhost:3040'` senza `webServer`, quindi lì vanno compilati `"app_start_cmd": "yarn start"` e `"app_url": "http://localhost:3040"`.)*

8. **Comando esatto dei test (`test_cmd`)**
   * **Dove l'ho trovato:** nel file **`packages/koenig-lexical/package.json`** dentro `"scripts"`:
     ```json
     "test:e2e": "NODE_ENV=test NODE_OPTIONS='--experimental-specifier-resolution=node --no-warnings' VITE_TEST=true playwright test"
     ```
   * **Dove va:**
     * in `config.json` $\rightarrow$ `"test_cmd": "NODE_ENV=test NODE_OPTIONS='--experimental-specifier-resolution=node --no-warnings' VITE_TEST=true npx playwright test"`

---

#### Parte B — I 3 file finali assemblati dentro `koenig/docker/`

1. **[koenig/docker/Dockerfile](./playwright/koenig/docker/Dockerfile)**
```dockerfile
FROM mcr.microsoft.com/playwright:v1.38.1-jammy

ENV CI=true HUSKY=0
ARG T0_COMMIT=25bc8a514eb8b080a4ed23959ac4229f18cb3cff

WORKDIR /app
COPY . .

RUN git config --global --add safe.directory /app && \
    git checkout -f "$T0_COMMIT" && \
    yarn install --frozen-lockfile && \
    yarn lerna run build

CMD ["sleep", "infinity"]
```

2. **[koenig/docker/Dockerfile.dockerignore](./playwright/koenig/docker/Dockerfile.dockerignore)**
```gitignore
# NON ignorare .git perché checkout.py e reset_t0.py lo usano dentro il container
node_modules
**/node_modules
dist
**/dist
playwright-report
test-results
results
```

3. **[koenig/docker/config.json](./playwright/koenig/docker/config.json)**
```json
{
  "image": "e2e-koenig:t0",
  "container": "e2e-koenig",
  "t0_commit": "25bc8a514eb8b080a4ed23959ac4229f18cb3cff",
  "install_cmd": "yarn install --frozen-lockfile",
  "build_cmd": "yarn lerna run build",
  "app_start_cmd": "",
  "app_url": "",
  "test_workdir": "/app/packages/koenig-lexical",
  "test_cmd": "NODE_ENV=test NODE_OPTIONS='--experimental-specifier-resolution=node --no-warnings' VITE_TEST=true npx playwright test"
}
```

---

## Passo 5 — Verificare la baseline a $t_0$ con i 6 script

Prima di testare altri commit dell'intervallo, verifica sempre che al commit $t_0$ i test partano e passino:

```bash
DIR="02-E2EGit-TestE2E/scripts/interfaccia"
REPO="02-E2EGit-TestE2E/repositories/nodejs/playwright/<nome_repo>"

# 1. Costruisce l'immagine a t0 e avvia il container (e l'app se serve)
python3 "$DIR/start.py" "$REPO"

# 2. Prova prima su un singolo file .spec / .test per verificare che funzioni
python3 "$DIR/run_tests.py" "$REPO" <percorso_un_file_test>
python3 "$DIR/get_results.py" "$REPO"

# 3. Se ok, prova tutta la suite (o i file stabili) su t0
python3 "$DIR/run_tests.py" "$REPO"
python3 "$DIR/get_results.py" "$REPO"

# 4. Prova un checkout su un secondo commit (es. t_end) e poi reset_t0
python3 "$DIR/checkout.py" "$REPO" <SHA_TEND>
python3 "$DIR/run_tests.py" "$REPO"
python3 "$DIR/get_results.py" "$REPO"
python3 "$DIR/reset_t0.py" "$REPO"
```

* Se a $t_0$ ottieni `PASS` e anche `checkout.py` + `reset_t0.py` funzionano puliti, la repository è **pronta per la bisezione e l'analisi finale**!

