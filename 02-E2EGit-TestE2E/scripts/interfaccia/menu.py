#!/usr/bin/env python3
"""Interfaccia unica (menu interattivo e CLI) per gestire container, commit e test Playwright."""

import csv
import json
import os
import re
import shlex
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
CSV_FIELDS = [
    "commit",
    "commit_date",
    "status",
    "total",
    "passed",
    "failed",
    "flaky",
    "skipped",
    "duration_ms",
]


def load_config(repo_dir):
    """Carica docker/config.json della repository e prepara la cartella results/."""
    repo = os.path.abspath(repo_dir)
    config_path = os.path.join(repo, "docker", "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["repo_dir"] = repo
    os.makedirs(os.path.join(repo, "results"), exist_ok=True)
    return cfg


def run_host(cmd, check=True, capture=False):
    """Esegue un comando sull'host."""
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def in_container(cfg, script, check=True, capture=False):
    """Esegue un comando bash nel container configurato."""
    cmd = ["docker", "exec", cfg["container"], "bash", "-lc", script]
    return run_host(cmd, check=check, capture=capture)


def stop_app(cfg):
    """Riavvia il container per fermare l'eventuale app in background."""
    if cfg.get("app_start_cmd", ""):
        run_host(["docker", "restart", "-t", "1", cfg["container"]], capture=True)


def start_app(cfg):
    """Avvia l'app nel container e attende che app_url risponda."""
    app_cmd = cfg.get("app_start_cmd", "")
    if not app_cmd:
        return

    cmd_avvio = f"cd /app && exec {app_cmd} >/tmp/app.log 2>&1"
    run_host(["docker", "exec", "-d", cfg["container"], "bash", "-lc", cmd_avvio])

    url = cfg.get("app_url", "")
    if not url:
        return

    check_js = f"require('http').get('{url}', () => process.exit(0)).on('error', () => process.exit(1))"
    while True:
        res = run_host(["docker", "exec", cfg["container"], "node", "-e", check_js], check=False)
        if res.returncode == 0:
            break
        time.sleep(2)


def _image_name(repo_dir, repo_git, commit):
    repo_name = re.sub(r"[^a-z0-9._-]", "-", os.path.basename(repo_dir).lower()).strip(".-") or "repo"
    res = subprocess.run(["git", "-C", repo_git, "rev-parse", "--verify", commit], text=True, capture_output=True)
    sha = res.stdout.strip() if res.returncode == 0 else commit
    tag = re.sub(r"[^a-zA-Z0-9_.-]", "-", sha)
    return f"{repo_name}:{tag}", sha


def start(cfg, commit=None, rebuild=False):
    """Costruisce l'immagine se manca (o con rebuild), avvia container e app."""
    repo = cfg["repo_dir"]
    dockerfile = os.path.join(repo, "docker", "Dockerfile")
    repo_git = os.path.join(repo, "repo")
    image_name, resolved_commit = _image_name(repo, repo_git, commit or cfg["t0_commit"])

    exists = run_host(["docker", "image", "inspect", image_name], check=False, capture=True).returncode == 0
    if rebuild or not exists:
        print(f"Immagine: {image_name} (build...)")
        run_host([
            "docker", "build",
            "--build-arg", f"T0_COMMIT={resolved_commit}",
            "-f", dockerfile,
            "-t", image_name,
            repo_git,
        ])
    else:
        print(f"Immagine: {image_name} (già presente, salto build)")

    run_host(["docker", "rm", "-f", cfg["container"]], check=False, capture=True)
    run_host(["docker", "run", "-d", "--name", cfg["container"], "--ipc=host", image_name], capture=True)
    start_app(cfg)


def restart(cfg):
    """Riavvia l'app dentro il container."""
    stop_app(cfg)
    start_app(cfg)


def checkout_commit(cfg, sha):
    """Sposta /app nello SHA indicato, reinstalla/ricompila se configurato e riavvia."""
    stop_app(cfg)
    in_container(cfg, f"cd /app && git clean -fd >/dev/null && git checkout -f {shlex.quote(sha)}")
    for key in ("install_cmd", "build_cmd"):
        cmd = cfg.get(key, "")
        if cmd:
            in_container(cfg, f"cd /app && {cmd}")
    start_app(cfg)


def get_commit(cfg):
    """Mostra SHA, data e messaggio del commit HEAD attivo in /app."""
    try:
        res = in_container(cfg, "cd /app && git log -1 --format='%H%n%h%n%ci%n%s'", capture=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"Errore: impossibile leggere il commit dal container '{cfg['container']}' (assicurati che sia avviato)."
        ) from exc

    lines = res.stdout.strip().splitlines()
    sha, short_sha, date, subject = (lines + ["", "", "", ""])[:4]
    t0_label = " [t0_commit]" if sha == cfg.get("t0_commit") else ""
    print(f"Container: {cfg['container']}")
    print(f"Commit:    {sha}{t0_label}")
    print(f"Short:     {short_sha}")
    print(f"Data:      {date}")
    print(f"Messaggio: {subject}")
    return sha


def _clean(text):
    return ANSI_RE.sub("", text).strip()


def _parse_commit_date(date_str):
    """Converte la data git in datetime UTC-aware per l'ordinamento cronologico."""
    value = (date_str or "").strip()
    if not value:
        return (1, datetime.max.replace(tzinfo=timezone.utc))
    for parser in (datetime.fromisoformat, lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M:%S %z")):
        try:
            dt = parser(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return (0, dt.astimezone(timezone.utc))
        except ValueError:
            continue
    return (1, datetime.max.replace(tzinfo=timezone.utc))


def _get_commit_date(cfg, sha, cache):
    """Recupera la data di un commit dalla repo locale o dal container (con cache)."""
    if not sha:
        return ""
    if sha in cache:
        return cache[sha]

    date = ""
    repo_git = os.path.join(cfg["repo_dir"], "repo")
    if os.path.isdir(repo_git):
        res = subprocess.run(["git", "-C", repo_git, "show", "-s", "--format=%ci", sha], text=True, capture_output=True)
        if res.returncode == 0:
            date = res.stdout.strip()

    if not date:
        res = in_container(cfg, f"cd /app && git show -s --format=%ci {shlex.quote(sha)}", check=False, capture=True)
        if res.returncode == 0:
            date = res.stdout.strip()

    cache[sha] = date
    return date


def _update_history_csv(cfg, out_csv, new_row, date_cache):
    """Aggiorna/aggiunge la riga del commit senza duplicati e ordina per commit_date."""
    by_commit = {}
    if os.path.exists(out_csv):
        with open(out_csv, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sha = row.get("commit", "")
                if not row.get("commit_date"):
                    row["commit_date"] = _get_commit_date(cfg, sha, date_cache)
                by_commit[sha] = row

    by_commit[new_row.get("commit", "")] = new_row
    rows = list(by_commit.values())
    rows.sort(key=lambda r: _parse_commit_date(r.get("commit_date", "")))

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def save_results(cfg):
    """Legge /tmp/pw_results.json dal container, stampa riepilogo e salva JSON, TXT e CSV."""
    raw_res = in_container(cfg, "cat /tmp/pw_results.json", check=False, capture=True)
    raw_json = raw_res.stdout
    if raw_res.returncode != 0 or not raw_json.strip():
        print("Avviso: /tmp/pw_results.json non trovato o vuoto, risultati non salvati.")
        return False

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        print(f"Avviso: /tmp/pw_results.json non valido ({exc}), risultati non salvati.")
        return False

    results_dir = os.path.join(cfg["repo_dir"], "results")
    commits_dir = os.path.join(results_dir, "commits")
    os.makedirs(commits_dir, exist_ok=True)
    repo_name = os.path.basename(cfg["repo_dir"])
    out_csv = os.path.join(results_dir, f"{repo_name}_commits_tests_results.csv")

    commit_lines = in_container(cfg, "cd /app && git log -1 --format='%H%n%ci'", capture=True).stdout.strip().splitlines()
    commit = commit_lines[0].strip()
    commit_date = commit_lines[1].strip() if len(commit_lines) > 1 else ""

    counts = Counter()
    duration = 0
    failed_lines = []
    stack = list(data.get("suites", []))
    while stack:
        suite = stack.pop()
        stack.extend(suite.get("suites", []))
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                status = test.get("status", "")
                counts[status] += 1
                results = test.get("results", [])
                duration += sum(r.get("duration", 0) for r in results)
                if status == "unexpected":
                    err_text = ""
                    for r in results:
                        err = r.get("error") or {}
                        stack_msg = _clean(err.get("stack") or err.get("message") or "")
                        snippet = _clean(err.get("snippet") or "")
                        if stack_msg or snippet:
                            err_text = "\n\n".join(p for p in (stack_msg, snippet) if p)
                            break
                    loc = f"{spec.get('file', '')}:{spec.get('line', '')}"
                    failed_lines.append(f"[{test.get('projectName', '')}] {loc} - {spec.get('title', '')}\n{err_text}\n")

    passed = counts["expected"]
    failed = counts["unexpected"]
    flaky = counts["flaky"]
    skipped = counts["skipped"]
    total = passed + failed + flaky + skipped
    errors = [_clean(e.get("message", str(e))) for e in data.get("errors", [])]
    final_status = "PASS" if failed == 0 and not errors and total > 0 else "TEST_FAIL"
    duration_ms = round(duration)

    out_json = os.path.join(commits_dir, f"{commit}.json")
    with open(out_json, "w", encoding="utf-8") as f:
        f.write(raw_json)

    out_txt = os.path.join(commits_dir, f"{commit}.txt")
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(f"COMMIT: {commit}\nDATA: {commit_date}\nSTATUS: {final_status}\n")
        f.write(f"TEST: total={total} passed={passed} failed={failed} flaky={flaky} skipped={skipped}\n\n")
        if errors:
            f.write("=== ERRORI GLOBALI ===\n" + "\n\n".join(errors) + "\n\n")
        if failed_lines:
            f.write("=== TEST FALLITI ===\n" + "\n".join(failed_lines))
        elif not errors:
            f.write("Nessun test fallito.\n")

    print(f"COMMIT : {commit}")
    print(f"DATA   : {commit_date}")
    print(f"STATUS : {final_status}")
    print(f"TEST   : total={total} passed={passed} failed={failed} flaky={flaky} skipped={skipped}")
    print(f"DURATA : {duration_ms} ms")
    print(f"ERRORI : {out_txt}")
    print(f"JSON   : {out_json}")
    print(f"CSV    : {out_csv}")

    new_row = {
        "commit": commit,
        "commit_date": commit_date,
        "status": final_status,
        "total": total,
        "passed": passed,
        "failed": failed,
        "flaky": flaky,
        "skipped": skipped,
        "duration_ms": duration_ms,
    }
    _update_history_csv(cfg, out_csv, new_row, {commit: commit_date})
    return True


def run_tests(cfg, extra_args=None):
    """Esegue i test Playwright nel container e salva sempre i risultati."""
    args = " ".join(extra_args) if extra_args else ""
    workdir = cfg.get("test_workdir", "/app")
    cmd = f"cd '{workdir}' && PLAYWRIGHT_JSON_OUTPUT_NAME=/tmp/pw_results.json {cfg['test_cmd']} {args} --reporter=json,list"
    res = in_container(cfg, cmd, check=False)
    save_results(cfg)
    return res.returncode


def _resolve_repo(raw_path):
    path = os.path.abspath(os.path.expanduser(raw_path))
    if os.path.basename(path) == "repo" and os.path.isfile(os.path.join(os.path.dirname(path), "docker", "config.json")):
        path = os.path.dirname(path)
    config_path = os.path.join(path, "docker", "config.json")
    if os.path.isfile(config_path):
        return load_config(path)
    return None


def _ask_repo(initial_path=None):
    while True:
        raw = initial_path if initial_path is not None else input("Inserisci il path della repository: ").strip()
        initial_path = None
        if not raw:
            continue
        cfg = _resolve_repo(raw)
        if cfg is not None:
            return cfg
        print(f"Errore: docker/config.json non trovato in {os.path.abspath(os.path.expanduser(raw))}")


def _print_menu(cfg):
    print("\n" + "=" * 50)
    print(f"Repository : {cfg['repo_dir']}")
    print(f"Container  : {cfg['container']} (t0={cfg['t0_commit'][:9]})")
    print("=" * 50)
    print("1. Start (build se manca + avvia container)")
    print("2. Start con rebuild (--rebuild)")
    print("3. Restart app nel container")
    print("4. Reset a t0_commit")
    print("5. Checkout commit specifico")
    print("6. Mostra commit attuale")
    print("7. Esegui test Playwright (salva sempre risultati)")
    print("8. Esegui comando nel container")
    print("9. Cambia repository")
    print("0. Esci")


def _run_cli(args):
    cfg = _resolve_repo(args[0])
    if cfg is None:
        raise SystemExit(f"Errore: docker/config.json non trovato in {args[0]}")

    action = args[1]
    rest = args[2:]
    if action == "start":
        rebuild = "--rebuild" in rest
        commits = [a for a in rest if a != "--rebuild"]
        start(cfg, commits[0] if commits else None, rebuild=rebuild)
    elif action == "restart":
        restart(cfg)
    elif action == "reset":
        checkout_commit(cfg, cfg["t0_commit"])
    elif action == "checkout":
        if not rest:
            raise SystemExit("Uso: python3 menu.py <repo> checkout <sha>")
        checkout_commit(cfg, rest[0])
    elif action == "commit":
        get_commit(cfg)
    elif action == "test":
        raise SystemExit(run_tests(cfg, rest or None))
    elif action == "results":
        save_results(cfg)
    elif action == "exec":
        if not rest:
            raise SystemExit("Uso: python3 menu.py <repo> exec <comando>")
        res = in_container(cfg, f"cd /app && {' '.join(rest)}", check=False)
        raise SystemExit(res.returncode)
    else:
        raise SystemExit(
            f"Azione non valida: {action}\n"
            "Azioni: start [sha] [--rebuild] | restart | reset | checkout <sha> | commit | test [args...] | results | exec <cmd>"
        )


def main():
    if len(sys.argv) > 2:
        _run_cli(sys.argv[1:])
        return

    cfg = _ask_repo(sys.argv[1] if len(sys.argv) > 1 else None)
    while True:
        _print_menu(cfg)
        try:
            choice = input("\nScelta: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice in ("0", "q", "exit"):
            break

        try:
            if choice in ("1", "2"):
                sha = input("Commit iniziale [Invio per t0_commit]: ").strip() or None
                start(cfg, sha, rebuild=(choice == "2"))
            elif choice == "3":
                restart(cfg)
            elif choice == "4":
                checkout_commit(cfg, cfg["t0_commit"])
            elif choice == "5":
                sha = input("Inserisci lo SHA del commit: ").strip()
                if sha:
                    checkout_commit(cfg, sha)
                else:
                    print("SHA vuoto, operazione annullata.")
            elif choice == "6":
                get_commit(cfg)
            elif choice == "7":
                raw_args = input("Argomenti extra Playwright [Invio per tutti i test]: ").strip()
                extra = shlex.split(raw_args) if raw_args else None
                code = run_tests(cfg, extra)
                print(f"Test terminati con exit code {code}")
            elif choice == "8":
                cmd = input("Comando nel container (in /app): ").strip()
                if cmd:
                    res = in_container(cfg, f"cd /app && {cmd}", check=False)
                    print(f"Comando terminato con exit code {res.returncode}")
                else:
                    print("Comando vuoto, operazione annullata.")
            elif choice == "9":
                cfg = _ask_repo()
            else:
                print("Scelta non valida.")
        except SystemExit as exc:
            if exc.code not in (None, 0):
                print(exc.code)
        except subprocess.CalledProcessError as exc:
            print(f"Comando fallito (exit code {exc.returncode}).")
        except Exception as exc:
            print(f"Errore: {exc}")


if __name__ == "__main__":
    main()
