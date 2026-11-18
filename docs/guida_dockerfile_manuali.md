# Guida pratica: costruire a mano i Dockerfile per test Playwright

Questa guida spiega **dove guardare** dentro una repository Git per ricavare la configurazione Playwright di una versione (tag), **cosa fa** ciascuna istruzione del `Dockerfile` e **quali comandi eseguire** per costruire, testare a mano ed eseguire in batch i test con [esegui_test_docker.py](file:///home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py).

Struttura attesa di un progetto sotto `02-E2EGit-TestE2E/repositories/repo_nodejs/<NOME_REPO>/`:

```text
<NOME_REPO>/
├── repo/                  # Repository Git vera e propria
├── docker/                # Qui vanno i Dockerfile.<from>-<to> e .dockerignore
└── results/               # Log e report generati da esegui_test_docker.py
```

---

## Fase 1 — Dove guardare nei tag per Playwright (senza checkout)

Spostati nella cartella del progetto:

```bash
cd 02-E2EGit-TestE2E/repositories/repo_nodejs/<NOME_REPO>
```

Con i comandi `git` seguenti ispezioni qualsiasi tag direttamente da `repo/` senza fare checkout.

### 1.1 Elencare i tag in ordine cronologico (e scegliere `<TAG>`)

```bash
git -C repo for-each-ref --sort=creatordate --format='%(creatordate:short)  %(refname:short)' refs/tags
```

- **Cosa fa**: stampa data e nome dei tag per individuare l'intervallo di versioni da coprire.
- **Se parti dalle date di `classifica_b_rq3.txt`**: filtra per anno (es. `2023-` o `2024-`) per vedere solo i tag del periodo che ti interessa:
  ```bash
  git -C repo for-each-ref --sort=creatordate --format='%(creatordate:short)  %(refname:short)' refs/tags | grep -E '2023-|2024-'
  ```
- **Cosa mettere al posto di `<TAG>`**: `<TAG>` è un segnaposto — sostituiscilo **senza le parentesi `<` e `>`** con uno dei nomi stampati sopra (es. `v1.11.0`, `3.1.7`, ecc.).  
  Per comodità puoi salvarlo in una variabile di shell e riusare `"$TAG"` in tutti i comandi seguenti:
  ```bash
  TAG=v1.11.0
  ```

### 1.2 Individuare tutti i file rilevanti per Playwright in un tag

```bash
git -C repo ls-tree -r --name-only <TAG> | grep -E 'package\.json$|lock|pnpm-workspace|nvmrc|node-version|playwright\.config|\.github/workflows/'
```

*(Esempio concreto: `git -C repo ls-tree -r --name-only v1.11.0 | grep -E ...`, oppure usa `"$TAG"` se hai impostato la variabile sopra.)*

- **Cosa fa**: mostra dove si trovano `package.json` (root o sottocartelle E2E), lockfile, file `playwright.config.*` e workflow CI.

### 1.3 Controllare i 5 elementi chiave di Playwright

| Cosa ti serve sapere | Dove guardare | Comando rapido |
|---|---|---|
| **1. Versione esatta di Playwright** | `package.json` + lockfile (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) | Vedi i comandi subito sotto |
| **2. Package manager** | `packageManager` in `package.json` o quale lockfile esiste (`package-lock.json` / `yarn.lock` / `pnpm-lock.yaml`) | `git -C repo ls-tree --name-only <TAG> \| grep -E 'lock\|pnpm'` |
| **3. Dove stanno i test Playwright** | Cartella che contiene `playwright.config.ts` / `.js` / `.mjs` e il `package.json` con `@playwright/test` | `git -C repo show <TAG>:playwright.config.ts` *(o percorso trovato al punto 1.2)* |
| **4. Se Playwright avvia il server da solo** | Campo `webServer` in `playwright.config.*` oppure `start-server-and-test` negli script | `git -C repo show <TAG>:playwright.config.ts \| grep -A10 'webServer'` |
| **5. Comandi di build, serve e test** | Sezione `"scripts"` di `package.json` + step `run:` nel workflow CI in `.github/workflows/` | `git -C repo show <TAG>:package.json \| sed -n '/"scripts"/,/}/p'` |

#### Come leggere la versione esatta di Playwright dal lockfile

In `package.json` spesso trovi un range (es. `"^1.32.0"`), mentre per l'immagine Docker serve la **versione esatta `X.Y.Z`**:

- **Con `package-lock.json` (npm)**:
  ```bash
  git -C repo show <TAG>:package-lock.json | grep -A4 -E '"node_modules/(@playwright/test|playwright|playwright-core)"'
  ```
- **Con `yarn.lock` (yarn)**:
  ```bash
  git -C repo show <TAG>:yarn.lock | grep -A2 -E '^"?(@playwright/test|playwright|playwright-core)@'
  ```
- **Con `pnpm-lock.yaml` (pnpm)**:
  ```bash
  git -C repo show <TAG>:pnpm-lock.yaml | grep -E '(@playwright/test|playwright|playwright-core):' | head -n 10
  ```

#### Leggere il workflow CI Playwright (spesso ha già tutto pronto)

```bash
git -C repo show <TAG>:.github/workflows/<workflow_playwright.yml>
```

- **Cosa controllare dentro il workflow**:
  - eventuali variabili d'ambiente richieste dai test (`BASE_URL`, `CI`, ecc.);
  - eventuali comandi preparatori prima di Playwright (es. `build`, `codegen`, database seed, server in background);
  - con che comando esatto vengono lanciati i test (es. `npx playwright test`, `npm run test:e2e`, `pnpm --filter e2e test`).

### 1.4 Capire quando cambiare `Dockerfile` tra un tag e l'altro (cluster)

```bash
git -C repo diff <TAG_1> <TAG_2> -- package.json package-lock.json yarn.lock pnpm-lock.yaml playwright.config.* .github/workflows/
```

- **Cosa fa**: mostra solo le differenze che possono rompere l'ambiente Docker.
- **Quando creare un nuovo `Dockerfile`**:
  1. cambia la versione `X.Y.Z` di `@playwright/test` / `playwright` (altrimenti il browser nell'immagine base non combacia);
  2. cambia il package manager o il comando di install/build;
  3. cambia `playwright.config.*` (`webServer`, directory dei test, porta) o il comando di test.

---

## Fase 2 — Scegliere l'immagine base Playwright e capire ogni istruzione

### Regola per `FROM` (immagine ufficiale Microsoft Playwright)

Usa l'immagine con la **stessa versione `X.Y.Z`** risolta nel lockfile:

- Se Playwright `<= 1.21.x`:
  ```dockerfile
  FROM mcr.microsoft.com/playwright:v<X.Y.Z>-focal
  ```
- Se Playwright `>= 1.22.x`:
  ```dockerfile
  FROM mcr.microsoft.com/playwright:v<X.Y.Z>-jammy
  ```

> **Perché è fondamentale**: ogni immagine `mcr.microsoft.com/playwright:vX.Y.Z-...` contiene già Node.js, le librerie OS (Chromium, Firefox, WebKit) e i browser esatti attesi da `playwright@X.Y.Z`. Se la versione combacia, **non serve** eseguire `npx playwright install` in fase di build (risparmi tempo e download), a meno che il progetto non usi versioni speciali o canali come `chrome` / `msedge`.

### Cosa fa ogni istruzione del `Dockerfile`

| Istruzione | Cosa fa |
|---|---|
| `FROM mcr.microsoft.com/playwright:vX.Y.Z-jammy` | Imposta Ubuntu + Node.js + browser Playwright preinstallati per quella esatta release. |
| `ARG APP_VERSION=v0.0.0` | Riceve il nome del tag durante `docker build --build-arg APP_VERSION=...` (usato da `esegui_test_docker.py`). |
| `ENV CI=true HUSKY=0` | `CI=true` attiva il comportamento CI di Playwright (niente report HTML interattivo bloccante, retry/reporter CI); `HUSKY=0` evita errori dei git hook in installazione perché `.git` non viene copiato. |
| `WORKDIR /app` | Imposta `/app` come cartella di lavoro nel container. |
| `COPY . .` | Copia i file estratti dal tag dentro `/app` (escludendo ciò che è in `.dockerignore`). |
| `RUN ...` | Installa le dipendenze ed esegue l'eventuale `build` dell'applicazione. |
| `CMD ["bash", "-c", "..."]` | Eseguito da `docker run`: avvia l'eventuale server (se Playwright non usa `webServer`) e lancia i test passando `${TEST_ARGS:-}` per poter filtrare un singolo file `.spec.ts` da fuori. |

---

## Fase 3 — Template Playwright pronti

Salva i file in `docker/Dockerfile.<tag_inizio>-<tag_fine>` (es. `docker/Dockerfile.v1.11.0-v1.13.4`) oppure `docker/Dockerfile.<tag>`.

### Caso A — Playwright con `webServer` configurato (o app statica / già gestita dal runner)

```dockerfile
FROM mcr.microsoft.com/playwright:v1.36.0-jammy

ARG APP_VERSION=v0.0.0
ENV CI=true HUSKY=0

WORKDIR /app
COPY . .

RUN npm ci && npm run build

CMD ["bash", "-c", "npx playwright test ${TEST_ARGS:-}"]
```

*(Varianti package manager: `yarn install --frozen-lockfile && yarn build` per Yarn; `corepack enable && pnpm install --frozen-lockfile && pnpm build` per pnpm.)*

### Caso B — Playwright senza `webServer` (server dell'app da avviare in background)

Se in `playwright.config.*` vedi solo `baseURL: 'http://localhost:3000'` senza `webServer`, avvia il server in background, attendi la porta e poi lancia Playwright:

```dockerfile
FROM mcr.microsoft.com/playwright:v1.36.0-jammy

ARG APP_VERSION=v0.0.0
ENV CI=true HUSKY=0

WORKDIR /app
COPY . .

RUN npm ci && npm run build

CMD ["bash", "-c", "npm run start & until node -e \"require('http').get('http://localhost:3000', ()=>process.exit(0)).on('error', ()=>process.exit(1))\" 2>/dev/null; do sleep 2; done && npx playwright test ${TEST_ARGS:-}"]
```

### Caso C — Test Playwright in una sottocartella (es. `e2e/` o `tests/playwright/`)

Se i test hanno un proprio `package.json` in una sottocartella non inclusa nei workspace root:

```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

ARG APP_VERSION=v0.0.0
ENV CI=true HUSKY=0

WORKDIR /app
COPY . .
RUN npm ci

WORKDIR /app/e2e
RUN npm ci

CMD ["bash", "-c", "npx playwright test ${TEST_ARGS:-}"]
```

*(Se invece è un monorepo con `workspaces`, basta l'installazione nella root e poi `WORKDIR /app/<cartella_e2e>` prima del `CMD`.)*

### Caso D — Il test fallisce perché manca il binario del browser

Capita se l'immagine non coincide al 100% con il pacchetto risolto o se viene usato solo un browser specifico. In quel caso aggiungi nel `RUN`:

```dockerfile
RUN npm ci && npx playwright install chromium
```

### `.dockerignore` (accanto al `Dockerfile`)

Crea `docker/<NomeDockerfile>.dockerignore` (es. `docker/Dockerfile.v1.11.0-v1.13.4.dockerignore`):

```gitignore
.git
node_modules
**/node_modules
results
playwright-report
test-results
```

- **Cosa fa**: impedisce a `COPY . .` di copiare `node_modules` locali o la cartella `.git`, velocizzando la build ed evitando conflitti di binari nativi tra host e container.

---

## Fase 4 — Provare a mano su un singolo tag (e fare debug)

Prova sempre il `Dockerfile` su **un tag** prima di lanciare tutte le versioni.

### 4.1 Estrarre il tag in un worktree temporaneo

```bash
git -C repo worktree add --force /tmp/wt-<TAG> <TAG>
```

- **Cosa fa**: crea una copia pulita dei file di `<TAG>` in `/tmp/wt-<TAG>` senza toccare `repo/`.

### 4.2 Build dell'immagine

```bash
docker build \
  --build-arg APP_VERSION=<TAG> \
  -f docker/Dockerfile.<nome> \
  -t pw-test:<TAG> \
  /tmp/wt-<TAG>
```

- **Cosa fa**: esegue `COPY`, installazione pacchetti e build. Se fallisce qui, il problema è nei file del progetto (lockfile, Node, script `build`), non nei test.

### 4.3 Eseguire tutti i test o un singolo file `.spec.ts`

Esecuzione completa:

```bash
docker run --rm --ipc=host -e TEST_ARGS="" pw-test:<TAG>
```

Esecuzione mirata di **un solo file** (es. il file più longevo della classifica):

```bash
docker run --rm --ipc=host \
  -e TEST_ARGS="tests/percorso/mio.spec.ts" \
  pw-test:<TAG>
```

- **Cosa fa**:
  - `--rm`: rimuove il container alla fine.
  - `--ipc=host`: **obbligatorio o fortemente consigliato per Playwright/Chromium**, evita crash delle tab dovuti a `/dev/shm` limitata a 64 MB di default in Docker.
  - `-e TEST_ARGS="..."`: viene espanso dentro `CMD` dopo `npx playwright test`.

### 4.4 Debug interattivo dentro il container (se un test fallisce)

```bash
docker run --rm -it --ipc=host pw-test:<TAG> bash
```

- **Cosa fa**: apre una shell dentro `/app` (o nella `WORKDIR` impostata) così puoi verificare:
  - `npx playwright --version` (controlla che coincida con l'immagine base);
  - se l'app parte sulla porta attesa;
  - lanciare un singolo test con output dettagliato: `npx playwright test path/file.spec.ts --reporter=list`.

### 4.5 Pulizia

```bash
git -C repo worktree remove --force /tmp/wt-<TAG>
docker rmi pw-test:<TAG>   # opzionale per liberare spazio
```

---

## Fase 5 — Eseguire tutte le versioni in batch con `esegui_test_docker.py`

Lo script [esegui_test_docker.py](file:///home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py) legge automaticamente i tuoi `Dockerfile` manuali se seguono la convenzione dei nomi:

1. **Nomi file richiesti**: `docker/Dockerfile.<from>-<to>` (es. `Dockerfile.v1.11.0-v1.13.4`) o `docker/Dockerfile.<tag>`.
2. **Precedenza di `docker_clusters_report.json`**: se esiste `results/docker_clusters_report.json` da una vecchia analisi automatica, `esegui_test_docker.py` usa quello anziché leggere i file in `docker/`. Spostalo o eliminalo se stai usando `Dockerfile` creati a mano.
3. **Verificare il mapping prima di partire (`--dry-run`)** dalla cartella `02-E2EGit-TestE2E`:

```bash
python3 scripts/docker/esegui_test_docker.py <NOME_REPO> --dry-run
```

- **Cosa fa**: stampa l'elenco `tag -> Dockerfile` senza avviare build né container.

4. **Lanciare i test su tutto l'intervallo (o su un singolo file Playwright con `--test-args`)**:

```bash
python3 scripts/docker/esegui_test_docker.py <NOME_REPO> \
  --from <TAG_INIZIO> --to <TAG_FINE> \
  --test-args "percorso/al/file.spec.ts" \
  -j 2 \
  --prune-images
```

- **Cosa fa**:
  - crea e rimuove in sicurezza un `git worktree` per ogni tag;
  - esegue `docker build` + `docker run --rm --ipc=host` su `2` versioni in parallelo (`-j 2`);
  - passa `TEST_ARGS` al container (ometti `--test-args` se vuoi eseguire tutta la suite);
  - con `--prune-images` cancella ogni immagine appena finito il test per non riempire il disco.

5. **Dove vedere i risultati**:
   - Log completi per singola versione: `results/logs/test_<TAG>.txt`
   - Riepilogo finale: `results/esecuzione_test_report.txt` e `results/esecuzione_test_report.csv` (con stato `PASS`, `TEST_FAIL`, `BUILD_FAIL`, `BUILD_TIMEOUT`, `TEST_TIMEOUT` o `WORKTREE_FAIL`).
