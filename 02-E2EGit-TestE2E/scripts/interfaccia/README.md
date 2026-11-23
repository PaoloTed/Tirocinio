# Interfaccia Unica Repository (`menu.py`)

Un solo script Python per tutte le repository configurate con `docker/config.json`:

- **Modalità menu interattivo:**
  ```bash
  python3 menu.py [repo]
  ```
- **Modalità comando diretto (CLI):**
  - `python3 menu.py <repo> start [commit] [--rebuild]` — Builda immagine (se manca o con `--rebuild`), avvia container e app
  - `python3 menu.py <repo> restart` — Riavvia l'applicazione dentro il container
  - `python3 menu.py <repo> reset` — Riporta la repo a `t0_commit`
  - `python3 menu.py <repo> checkout <sha>` — Sposta `/app` su `<sha>`, installa/compila se configurato e riavvia
  - `python3 menu.py <repo> commit` — Mostra SHA, data e messaggio del commit attivo
  - `python3 menu.py <repo> test [args...]` — Esegue i test Playwright e **salva sempre** `results/<repo>_commits_tests_results.csv`, `results/commits/<sha>.txt` e `results/commits/<sha>.json`
  - `python3 menu.py <repo> results` — Estrae/salva nuovamente i risultati dall'ultimo `/tmp/pw_results.json`
  - `python3 menu.py <repo> exec <comando>` — Esegue un comando diretto in `/app` dentro il container
