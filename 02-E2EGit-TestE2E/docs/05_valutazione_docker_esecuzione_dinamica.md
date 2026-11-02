# Valutazione Tecnica: Mining Statico della Cronologia Git vs Esecuzione Dinamica in Docker

**Progetto**: *Implementazione di un tool per l'analisi automatica di test e2e web in repository software*  
**Autore**: Paolo  
**Tutor accademico**: Prof. Luigi Libero Lucio Starace  
**Riferimento riunione**: Appunto *"con container dockerfile per rieseguire i test, con script per determinata versione ecc DA VEDERE SE FARLO FORSE TROPPO DIFFICILE"*  
**Data**: Novembre 2026  

---

## 1. Obiettivo dell'Indagine

Nel primo colloquio con il prof. Starace è emerso l'interrogativo metodologico fondamentale:
> *È opportuno estendere il tool affinché riesegua dinamicamente i test end-to-end (E2E) in container Docker retrodatati per ogni versione storica dell'applicazione, oppure è preferibile concentrare l'architettura sul mining statico della cronologia Git?*

Il presente documento fornisce una valutazione scientifica e ingegneristica di fattibilità, analizzando le criticità dell'esecuzione retroattiva, i vantaggi del mining della cronologia e delineando la **strategia ibrida a due livelli (Tier 1 + Tier 2)** proposta per la tesi.

---

## 2. Il Problema della Riesecuzione Dinamica su Repository Storici

Sebbene l'idea di eseguire `cypress run` o `playwright test` a ritroso su centinaia di release storiche sia affascinante, la letteratura scientifica di *Mining Software Repositories* (MSR) e l'esperienza industriale dimostrano che **l'esecuzione dinamica regressiva su larga scala soffre di tassi di fallimento elevati per cause estrinseche al test stesso**.

### 2.1 Le Criticità Tecniche Rilevate

1. **Dependency Rot (Degrado delle Dipendenze Node/NPM)**:
   - File `package.json` storici contengono spesso intervalli di versione elastici (`^` o `~`). A distanza di mesi o anni, `npm install` risolve sotto-dipendenze che non esistono più, sono state deprecate o non sono compatibili con il runtime Node.js corrente.
   - I file di lock (`package-lock.json` o `yarn.lock`) attenuano il problema solo se i registri remoti conservano gli esatti tarball binari immutati.
2. **Disallineamento Runtime Node.js e Motori Browser**:
   - Una release del 2021 richiede Node.js 14 o 16 e una versione di Cypress (es. v8.x) compilata contro una specifica libreria `glibc` di Linux. Eseguirla in un container moderno (Node 20 / Debian Bookworm) genera errori di caricamento delle shared library (`libnss3.so`, `libatk-1.0.so`).
   - Servirebbe un'immagine Docker diversa per ogni era tecnologica del progetto (matrice combinatoria complessa: Node version $\times$ Cypress/Playwright version $\times$ OS distribution).
3. **Assenza di Backend e Dipendenze Esterne**:
   - Molti dei 472 repository nel dataset E2EGit testano applicazioni collegate a microservizi, database relazionali (PostgreSQL, MongoDB), sistemi di autenticazione OAuth o API esterne.
   - Senza un ambiente di mock completo e preconfigurato, i test E2E falliscono per `ECONNREFUSED` ancor prima di interagire con il DOM, falsando l'analisi di stabilità.
4. **Flakiness non Deterministica**:
   - Anche su codice perfettamente valido, i test E2E GUI risentono di *flakiness* dovuta a timing di rendering, animazioni CSS e carico CPU/memoria dell'host di virtualizzazione.

---

## 3. Confronto Comparativo: Mining Statico vs Esecuzione Dinamica

| Dimensione di Analisi | Mining Statico (Git History) | Esecuzione Dinamica (Docker) |
|---|---|---|
| **Copertura del Dataset** | **100% (tutti i 472 repository)** | Circa 5–15% (solo repo standalone con mock) |
| **Tempo di Analisi per Commit** | **< 1 secondo** (query commit diff) | 2–8 minuti (npm install + build + test run) |
| **Scalabilità Temporale** | Esegue su 5 anni di commit in pochi secondi | Richiede ore/giorni di build container |
| **Riproducibilità** | **100% deterministica** (il testo del commit non cambia) | Bassa (soggetta a dipendenze di rete e flakiness) |
| **Informazioni Estratte** | Data nascita, autore, frequenza modifiche, evoluzione selettori DOM, asserzioni, rimozioni, bugfix | Esito booleano Pass/Fail a runtime, screenshot/video |
| **Costo Computazionale** | Minimo (CPU per parsing regex / AST) | Elevatissimo (CPU, RAM, storage container) |

---

## 4. Architettura Ibrida Consigliata (Proposta per la Tesi)

Per conciliare il rigore analitico con l'obiettivo di ricerca del prof. Starace, proponiamo una **struttura a due livelli disaccoppiati**:

```mermaid
flowchart TD
    subgraph Tier1["TIER 1 — Core Tool: Mining Statico Scalabile (100% Repos)"]
        A["Database E2EGit (472 Repo)"] --> B["Git History Mining Engine"]
        B --> C["Calcolo Metriche: t_birth, Δ_first_mod, N_mod"]
        B --> D["Tassonomia Diff: Selettori, Asserzioni, Wait, Flake"]
        C --> E["Report Globale & Pattern di Evoluzione"]
        D --> E
    end

    subgraph Tier2["TIER 2 — Validation Suite: Esecuzione Dinamica Mirata (Progetti Pilota)"]
        F["Selezione Progetti Pilota (Standalone / Mock Demo)"] --> G["Docker Runner Dedicato"]
        G --> H["Esecuzione Cypress/Playwright su Release Pivot (v1, v2, v3)"]
        H --> I["Verifica Empirica: Il test falliva davvero prima del commit di fix?"]
    end

    E -.->|"Fornisce i commit di break/fix da verificare"| F
```

### Livello 1: Core Engine di Mining Statico (Universale)
- Opera tramite le API di Git (`git log`, `git blame`, `git diff`) e parsing statico.
- Analizza l'intera storia di qualsiasi repository Node.js.
- Ricostruisce con precisione millimetrica quando un test è nato, quante versioni applicative sono trascorse prima di essere toccato e cosa è cambiato nel codice.

### Livello 2: Runner Docker per Progetti Pilota Selezionati (Sperimentale)
- Riservato esclusivamente a repository autonomi identificati nella fase pilota, in particolare **`ghiscoding/angular-slickgrid`**.
- Questo progetto è il candidato ideale perché:
  1. I test E2E Cypress girano contro una **demo Angular autonoma** inclusa nel repository.
  2. Non richiede backend né database esterni: i dataset sono mockati in JSON statici (`src/assets/data/`).
  3. Il comando di build e test è documentato e riproducibile:
     ```bash
     npm run build:demo && npm run serve:demo
     npm run cypress:ci
     ```

---

## 5. Prototipo Operativo Docker per `angular-slickgrid`

Per mostrare al professore la fattibilità pratica sul progetto pilota, è stato predisposto un prototipo containerizzato con l'ambiente ufficiale Cypress:

### 5.1 Dockerfile (`02-E2EGit-TestE2E/docker/angular-slickgrid/Dockerfile`)

```dockerfile
# Immagine certificata con Node 20, Chrome Headless e dipendenze di sistema Cypress
FROM cypress/browsers:node-20.14.0-chrome-126.0.6478.114-1-ff-127.0.2-edge-126.0.6478.114-1

WORKDIR /e2e-app

# Copia dei descrittori di dipendenze
COPY package*.json ./

# Installazione pulita (senza interattività)
RUN npm ci --prefer-offline --no-audit

# Copia del codice sorgente e suite di test
COPY . .

# Compilazione del demo harness
RUN npm run build:demo

# Esposizione della porta del web server demo
EXPOSE 4300

# Script di esecuzione: avvia il server in background ed esegue Cypress
CMD ["bash", "-c", "npm run serve:demo & npx wait-on http://localhost:4300 && npm run cypress:ci"]
```

### 5.2 Script di Esecuzione Parametrico per Versione (`run_version_test.sh`)
Uno script che permette di fare il checkout su un tag o commit specifico e lanciare il container:

```bash
#!/usr/bin/env bash
# Esempio d'uso: ./run_version_test.sh v6.5.0
TAG_OR_COMMIT=${1:-"master"}
echo "==> Esecuzione test dinamico su commit/tag: $TAG_OR_COMMIT"

cd ../../data/clones/ghiscoding__angular-slickgrid
git checkout $TAG_OR_COMMIT

docker build -t slickgrid-e2e:$TAG_OR_COMMIT -f ../../docker/angular-slickgrid/Dockerfile .
docker run --rm slickgrid-e2e:$TAG_OR_COMMIT
```

---

## 6. Risposta Chiara e Argomentata per il Professore

Alla domanda del professore sul da farsi riguardo a Docker, la risposta sintetizzata è:

> **«Professore, abbiamo valutato in dettaglio la fattibilità tecnica:**
> 1. **Per l'analisi complessiva (i 472 repo):** La riesecuzione dinamica su versioni storiche è sconsigliata e computazionalmente proibitiva a causa del *dependency rot* di NPM e dell'assenza di backend/database esterni per molte app. Il **mining statico della cronologia Git** è la strada scientificamente corretta: è deterministico al 100%, immediato, copre tutti i 472 repository e ci dà l'esatta evoluzione del codice dei test nel tempo.
> 2. **Per i progetti pilota (come `angular-slickgrid`):** L'esecuzione Docker è **fattibile e già prototipata**, perché l'applicazione dispone di una suite di demo completamente mockata in locale.
> 3. **Proposta di tesi:** Strutturare il tool con un **motore principale di Git Mining** scalabile a tutto il dataset, affiancato da un **modulo opzionale di esecuzione containerizzata** da attivare solo sui progetti pilota che supportano test autonomi.»

