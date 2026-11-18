# Guida agli Script

Gli script in questa cartella sono organizzati in **3 sottocartelle** in base al loro utilizzo:

| Sottocartella | Utilizzo | Script inclusi |
|---|---|---|
| **`analisi_rq3/`** | Selezione repository, classifiche e analisi offline dei dati `E2EGit_e2e.db` + `RQ3` (senza clonare) | `elenco_repo_playwright.py`, `classifica_repo_rq3.py`, `classifica_b_rq3.py`, `storia_test_only_gui.py`, `calcola_intervalli_playwright.py` |
| **`git_versioni/`** | Clonazione leggera delle repository GitHub e analisi delle versioni (`git tag`) | `clona_repository.sh`, `analizza_versioni_test_e2e.py` |
| **`docker/`** | Generazione dei `Dockerfile` per cluster ed esecuzione parallela dei test E2E in Docker | `genera_docker_nodejs.py`, `esegui_test_docker.py` |

---

## 1. `analisi_rq3/` — Analisi dataset E2EGit e RQ3 (senza clonare)

- **`elenco_repo_playwright.py`**: interroga `data/E2EGit_e2e.db` ed estrae l'elenco dei repository Node.js (JS/TS) con test > 10 e release > 5 che utilizzano esclusivamente Playwright, salvando `repositories/repo_nodejs/repository_nodejs_playwright.{txt,csv}`.
  ```bash
  python3 02-E2EGit-TestE2E/scripts/analisi_rq3/elenco_repo_playwright.py
  python3 02-E2EGit-TestE2E/scripts/analisi_rq3/elenco_repo_playwright.py --min-tests 10 --min-releases 5
  ```

- **`classifica_repo_rq3.py`**: incrocia `data/E2EGit_e2e.db` con `data/IST2025_Zenodo/RQ3/commit-analysis` per individuare le repository Node.js con i range più lunghi senza aggiornamenti ai test E2E GUI. Salva `repositories/repo_nodejs/classifica_rq3_non_aggiornamento.{txt,csv}`.
  ```bash
  python3 02-E2EGit-TestE2E/scripts/analisi_rq3/classifica_repo_rq3.py --top 25
  ```

- **`classifica_b_rq3.py`**: genera la Classifica B completa (singoli file di test più longevi senza modifiche in RQ3) ordinabile per `svac`, `days` o `ratio`. Salva `repositories/repo_nodejs/classifica_b_rq3.{txt,csv}`.
  ```bash
  python3 02-E2EGit-TestE2E/scripts/analisi_rq3/classifica_b_rq3.py --sort-by days
  ```

- **`storia_test_only_gui.py`**: copia il file `*_only_gui.xlsx/.csv` da RQ3 nella cartella della repository e genera `storia_test_<nome_repo>.txt` con creazione e modifiche di ogni test.
  ```bash
  python3 02-E2EGit-TestE2E/scripts/analisi_rq3/storia_test_only_gui.py lizmap-web-client
  python3 02-E2EGit-TestE2E/scripts/analisi_rq3/storia_test_only_gui.py --all
  ```

- **`calcola_intervalli_playwright.py`**: calcola per le repository in `repositories/repo_nodejs/playwright/repository_nodejs_playwright.txt` gli intervalli disgiunti di commit in cui almeno una soglia (default 70%) dei file di test Playwright attivi non viene modificata, salvando `intervalli_playwright_70.{txt,csv}`.
  ```bash
  python3 02-E2EGit-TestE2E/scripts/analisi_rq3/calcola_intervalli_playwright.py
  python3 02-E2EGit-TestE2E/scripts/analisi_rq3/calcola_intervalli_playwright.py --repo microsoft/fluentui
  ```

---

## 2. `git_versioni/` — Clonazione e analisi versioni (`git tag`)

- **`clona_repository.sh`**: clona una repository GitHub dentro `02-E2EGit-TestE2E/repositories/<sottocartella>/<nome_repo>/repo` usando `--filter=blob:none` (e opzionalmente `--no-checkout`).
  ```bash
  bash 02-E2EGit-TestE2E/scripts/git_versioni/clona_repository.sh owner/repo
  bash 02-E2EGit-TestE2E/scripts/git_versioni/clona_repository.sh --no-checkout owner/repo
  ```

- **`analizza_versioni_test_e2e.py`**: legge tutti i `git tag` delle repository clonate e verifica tra quali versioni consecutive l'intera suite E2E (o i singoli file di test) è rimasta invariata, generando `results/versioni_e2e_report.{txt,json}` e `repositories/repo_nodejs/classifica_versioni_tag.{txt,csv}`.
  ```bash
  python3 02-E2EGit-TestE2E/scripts/git_versioni/analizza_versioni_test_e2e.py --all
  python3 02-E2EGit-TestE2E/scripts/git_versioni/analizza_versioni_test_e2e.py equal-access
  ```

---

## 3. `docker/` — Generazione Dockerfile ed esecuzione test

- **`genera_docker_nodejs.py`**: analizza le versioni comprese tra `--from` e `--to`, le raggruppa in cluster omogenei e genera i `Dockerfile.<cluster>` + `results/docker_clusters_report.{txt,json}`.
  ```bash
  python3 02-E2EGit-TestE2E/scripts/docker/genera_docker_nodejs.py 02-E2EGit-TestE2E/repositories/repo_nodejs/<nome_repo> --from <tag_inizio> --to <tag_fine> --only-stable
  ```

- **`esegui_test_docker.py`**: legge `results/docker_clusters_report.json` (o i `Dockerfile.<range>` in `docker/`), crea i `git worktree` temporanei per le versioni richieste, esegue `docker build` + `docker run` in parallelo (`-j`) e salva log e report (`PASS` / `TEST_FAIL` / `BUILD_FAIL`).
  ```bash
  python3 02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py equal-access --from 3.1.7 --to 3.1.15 --dry-run
  python3 02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py equal-access --from 3.1.7 --to 3.1.15 -j 2 --prune-images
  python3 02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py equal-access -j 2 --prune-images
  ```
