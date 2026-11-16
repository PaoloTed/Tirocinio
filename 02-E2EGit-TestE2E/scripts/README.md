# Guida Semplice agli Script

In questa cartella ci sono **4 script**, da usare in questo ordine:

---

## Ordine di esecuzione (in breve)

1. **`classifica_repo_rq3.py`** → Sceglie quali repository Node.js vale la pena studiare (usando i dati già pronti di E2EGit + RQ3, senza clonare nulla).
2. **`clona_repository.sh`** → Scarica (in modo leggero) le repository scelte.
3. **`analizza_versioni_test_e2e.py`** → Controlla i `git tag` reali delle repository scaricate e trova le **versioni** in cui i test E2E non sono cambiati.
4. **`genera_docker_nodejs.py`** → Prende una repository e l'intervallo di tag trovato al passo 3 (`--from` / `--to`) e genera i `Dockerfile` per eseguire i test.

---

## 1. `classifica_repo_rq3.py` (Pre-selezione senza clonare)
- **Cosa fa**: incrocia il database `data/E2EGit_e2e.db` (repository JS/TS significative con test E2E) con i file di `RQ3` per vedere quali hanno lunghi periodi senza aggiornamenti ai test.
- **Output**: `repositories/repo_nodejs/classifica_rq3_non_aggiornamento.txt` e `.csv`.
- **Come si esegue**:
  ```bash
  python3 02-E2EGit-TestE2E/scripts/classifica_repo_rq3.py --top 25
  ```

---

## 2. `clona_repository.sh` (Download leggero della repository)
- **Cosa fa**: clona una repository GitHub dentro `repositories/repo_nodejs/<nome_repo>/repo` usando `--filter=blob:none`. Con `--no-checkout` scarica solo cronologia e tag (occupa molto meno spazio).
- **Come si esegue**:
  ```bash
  bash 02-E2EGit-TestE2E/scripts/clona_repository.sh owner/repo
  # oppure ancora più leggero (solo tag e storia, senza file estratti):
  bash 02-E2EGit-TestE2E/scripts/clona_repository.sh --no-checkout owner/repo
  ```

---

## 3. `analizza_versioni_test_e2e.py` (Range reali sulle versioni / `git tag`)
- **Cosa fa**: legge tutti i `git tag` delle repository clonate e controlla tra quali versioni consecutive l'intera suite E2E (o i singoli file di test) è rimasta identica.
- **Output**:
  - Per ogni repository: `results/versioni_e2e_report.txt` e `.json`.
  - Riepilogo generale: `repositories/repo_nodejs/classifica_versioni_tag.txt` e `.csv`.
- **Come si esegue**:
  ```bash
  # Su tutte le repository già clonate:
  python3 02-E2EGit-TestE2E/scripts/analizza_versioni_test_e2e.py --all

  # Oppure su una repository specifica:
  python3 02-E2EGit-TestE2E/scripts/analizza_versioni_test_e2e.py equal-access
  ```

---

## 4. `genera_docker_nodejs.py` (Creazione Dockerfile ed esecuzione test)
- **Cosa fa**: analizza le versioni comprese tra `--from` e `--to` (trovate al passo 3), le raggruppa in cluster e crea i `Dockerfile` + `docker/esegui_test_docker.sh` per eseguire i test in container isolati.
- **Come si esegue**:
  ```bash
  python3 02-E2EGit-TestE2E/scripts/genera_docker_nodejs.py 02-E2EGit-TestE2E/repositories/repo_nodejs/<nome_repo> --from <tag_inizio> --to <tag_fine> --only-stable
  ```

