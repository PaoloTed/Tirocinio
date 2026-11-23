# Guida ai comandi Git per il Tirocinio

Elenco pratico dei comandi Git utili per il lavoro quotidiano sul tirocinio (sincronizzazione tra PC fisso e portatile tramite `PaoloTed/Tirocinio`, gestione delle repository target in `repositories/nodejs/*/repo`, ispezione di tag/release e risoluzione dei problemi più comuni).

---

## 1. Flusso quotidiano e sincronizzazione (PC fisso ↔ GitHub ↔ Portatile)

* **`git status`** — Controlla i file modificati, aggiunti (`staged`) o non tracciati (`untracked`) prima di fare qualsiasi operazione.
* **`git pull origin main`** — Scarica e integra gli ultimi commit da GitHub (da eseguire sempre quando si cambia PC prima di iniziare a lavorare).
  ```bash
  # Variante più pulita se hai commit locali non ancora pushati:
  git pull --rebase origin main
  ```
* **`git add <file>`** oppure **`git add .`** — Prepara i file per il commit.
  ```bash
  # Aggiunge interattivamente solo singole modifiche (hunk), utile per evitare debug temporanei:
  git add -p
  ```
* **`git commit -m "messaggio"`** — Salva le modifiche nella cronologia locale.
* **`git commit --amend -m "nuovo messaggio"`** — Modifica l'ultimo commit (messaggio o file appena aggiunti con `git add`), *solo prima di fare `push`*.
* **`git push origin main`** — Invia i commit locali su GitHub.

---

## 2. Clonazione delle repository target (`nodejs/*/repo`)

* **`git clone <url> <percorso>`** — Clona una repository completa.
* **`git clone --filter=blob:none <url> <percorso>`** — **Partial clone leggero**: scarica tutta la storia e i tag senza scaricare subito tutti i file storici pesanti (li scarica solo al bisogno). Ideale per `angular-slickgrid`, `equal-access`, `care_fe`, `gsender`, ecc.
  ```bash
  git clone --filter=blob:none https://github.com/ghiscoding/angular-slickgrid.git repo
  ```
* **`git clone --depth=1 --branch <tag> <url> <percorso>`** — Scarica solo lo snapshot di un tag/branch specifico senza cronologia (molto veloce per build o test isolati).
* **`git fetch --tags`** — Aggiorna l'elenco di tutti i tag/release dal remoto senza modificare la cartella di lavoro.

---

## 3. Ispezione di tag, release, commit e file (utile per Dockerfile e analisi RQ3)

> **Cos'è un `<tag>` in Git?**  
> Un **tag** è un'"etichetta fissa" (un segnalibro immutabile) applicata a uno specifico **commit** nella storia del repository per identificarne una **versione / release** precisa (ad esempio `v5.5.0` in `angular-slickgrid`, `v1.4.0` in `gsender` o `1.20.0`).  
> A differenza di un **branch** (come `main`, che avanza a ogni nuovo commit), un tag resta sempre fermo su quel punto esatto della storia: nei tuoi script e Dockerfile ti permette di analizzare, scaricare o testare il codice esatto di una specifica release.
>
> * *(Opzionale, se vuoi creare tag nella tua repo)*:
>   * **`git tag -a v1.0 -m "Consegna milestone"`** — Crea un **tag annotato** (con autore, data e messaggio) sul commit corrente.
>   * **`git push origin v1.0`** *(oppure `git push origin --tags`)* — Invia i tag creati localmente su GitHub.
>   * **`git tag -d v1.0`** — Elimina un tag locale.

* **`git tag -l --sort=-v:refname`** — Elenca tutti i tag/release dalla versione più recente alla più vecchia.
* **`git show <tag>:<percorso/file>`** — Legge il contenuto di un file (es. `package.json`, `.nvmrc`, `Dockerfile`, file di test) a una determinata versione **senza cambiare branch o fare checkout**.
  ```bash
  git show v5.5.0:package.json
  ```
* **`git switch --detach <tag>`** *(oppure `git checkout <tag>`)* — Porta i file nella cartella di lavoro esattamente allo stato di una specifica release.
  ```bash
  # Per tornare al branch principale:
  git switch main
  # oppure tornare al branch/commit precedente:
  git switch -
  ```
* **`git log --oneline -n 20`** — Mostra gli ultimi 20 commit in formato compatto.
* **`git log --oneline -- <percorso/file>`** — Mostra solo i commit che hanno modificato un file o una cartella specifica (es. la cartella dei test E2E).
* **`git log -S "<testo>" --oneline`** — Cerca nella storia quando una certa stringa (es. un test o una dipendenza) è stata aggiunta o rimossa.
* **`git diff`** — Mostra le modifiche locali non ancora aggiunte allo staging.
* **`git diff --staged`** — Mostra le modifiche già aggiunte con `git add`.
* **`git diff <tag1> <tag2> -- <file>`** — Confronta come è cambiato un file (es. `package.json`) tra due versioni diverse.
* **`git describe --tags --always`** — Mostra il tag o l'hash del commit corrente.

---

## 4. Annullare errori, mettere da parte modifiche e pulire

* **`git restore <file>`** — Annulla le modifiche locali non ancora aggiunte con `git add` *(attenzione: non recuperabile)*.
* **`git restore --staged <file>`** — Toglie un file dallo staging (annulla `git add`) senza perdere le modifiche su disco.
* **`git stash push -m "descrizione"`** — Salva temporaneamente le modifiche locali non committate e ripulisce la directory (utile prima di un `git pull`).
  ```bash
  git stash list   # Elenca gli stash salvati
  git stash pop    # Ripristina l'ultimo stash e lo rimuove dalla lista
  ```
* **`git reset --soft HEAD~1`** — Annulla l'ultimo commit locale mantenendo tutte le modifiche pronte per un nuovo commit.
* **`git clean -nd`** — Anteprima (dry-run) dei file non tracciati che verrebbero eliminati.
  ```bash
  # Elimina fisicamente file e cartelle non tracciate (controllare sempre prima con -nd):
  git clean -fd
  ```

---

## 5. Gestione branch (per esperimenti senza sporcare `main`)

* **`git branch`** — Mostra i branch locali e quello attivo.
* **`git switch -c <nome-branch>`** — Crea un nuovo branch e ci si sposta subito.
* **`git switch main`** — Torna sul branch `main`.
* **`git merge <nome-branch>`** — Unisce in `main` il lavoro fatto sul branch secondario.
* **`git branch -d <nome-branch>`** — Elimina un branch locale dopo il merge (`-D` forza l'eliminazione).

---

## 6. Controllo `.gitignore`, file pesanti (>100 MB) e configurazione

* **`git check-ignore -v <file>`** — Verifica se un file (es. `.db`, `.venv`, `repo/`) è coperto da `.gitignore` e da quale regola.
* **`git status --ignored`** — Mostra anche i file ignorati presenti nella directory.
* **`git rm --cached <file>`** — Rimuove un file dal tracking di Git (es. un file pesante committato per sbaglio) **senza cancellarlo dal disco**.
* **`git remote -v`** — Verifica gli URL remoti configurati (`origin`).
* **`git count-objects -vH`** — Mostra quanto spazio occupa la cartella `.git` locale.
* **`git config --list`** — Controlla nome, email e impostazioni Git correnti.

---

## 7. Risoluzione conflitti dopo `git pull`

Se due PC hanno modificato le stesse righe dello stesso file:
1. Esegui `git status` per vedere i file in conflitto (`both modified`).
2. Apri il file e risolvi i marcatori `<<<<<<<`, `=======`, `>>>>>>>`.
3. Segna il file come risolto e completa l'operazione:
   ```bash
   git add <file>
   git commit              # se hai usato git pull (merge)
   # oppure:
   git rebase --continue   # se hai usato git pull --rebase
   ```
   *(Per annullare tutto e tornare prima del pull: `git merge --abort` oppure `git rebase --abort`.)*

---

## Checklist rapida anti-problemi

1. **Prima di iniziare su un PC**: `git pull origin main`
2. **Prima di `git add .`**: esegui sempre `git status` per assicurarti di non includere per sbaglio file pesanti (`*.db`, `RQ3.zip`, `repo/`) che bloccherebbero il `push` su GitHub (>100 MB).
3. **Quando finisci / cambi PC**: `git add ...` → `git commit -m "..."` → `git push origin main`

