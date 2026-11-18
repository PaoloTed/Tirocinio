#!/usr/bin/env python3
"""esegui_test_docker.py — Step 5 della pipeline:
Esegue in parallelo build Docker e test E2E su un intervallo di versioni
(o su tutte le versioni mappate in `results/docker_clusters_report.json`).

Caratteristiche principali:
- Risolve automaticamente le versioni nell'intervallo `--from .. --to` oppure `--tags`.
- Esegue `docker build` + `docker run` in parallelo fino a `--jobs` worker contemporanei.
- Apre un terminale separato per ciascuna versione in esecuzione per seguire
  l'output di build e test in tempo reale (disattivabile con `--no-terminals`).
- Protegge le operazioni `git worktree` con lock per evitare race condition.
- Non si ferma se una versione fallisce: distingue `PASS`, `TEST_FAIL` e `BUILD_FAIL`.
- Salva i log individuali in `results/logs/test_<ver>.txt` e un riepilogo finale in
  `results/esecuzione_test_report.txt` e `.csv`.

Uso:
    python3 02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py equal-access --from 3.1.7 --to 3.1.15 -j 2
    python3 02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py equal-access --prune-images -j 2
    python3 02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py equal-access --no-terminals
    python3 02-E2EGit-TestE2E/scripts/docker/esegui_test_docker.py equal-access --dry-run
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import TextIO

ROOT = Path(__file__).resolve().parents[2]
REPOS_NODEJS_DIR = ROOT / "repositories" / "repo_nodejs"

SEMVER_RE = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[-+].+)?$")
PARTIAL_VER_RE = re.compile(r"^v?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?$")

GIT_WORKTREE_LOCK = threading.Lock()


def resolve_repo_dir(repo_arg: str) -> tuple[Path, Path]:
    p = Path(repo_arg)
    if not p.exists():
        p = REPOS_NODEJS_DIR / repo_arg
    p = p.resolve()
    if (p / "repo" / ".git").is_dir():
        return p, p / "repo"
    if (p / ".git").is_dir():
        return p.parent, p
    raise FileNotFoundError(f"Repository non trovata: {repo_arg}")


def parse_semver_tuple(ver: str) -> tuple[int, int, int] | None:
    m = SEMVER_RE.match(ver.strip())
    if not m:
        return None
    return int(m.group("major")), int(m.group("minor")), int(m.group("patch"))


def parse_bound(bound: str, is_upper: bool) -> tuple[int, int, int] | None:
    m_exact = SEMVER_RE.match(bound.strip())
    if m_exact:
        return (
            int(m_exact.group("major")),
            int(m_exact.group("minor")),
            int(m_exact.group("patch")),
        )
    m = PARTIAL_VER_RE.match(bound.strip())
    if not m:
        return None
    major = int(m.group("major"))
    if m.group("minor") is None:
        return (major, 999999, 999999) if is_upper else (major, 0, 0)
    minor = int(m.group("minor"))
    if m.group("patch") is None:
        return (major, minor, 999999) if is_upper else (major, minor, 0)
    return major, minor, int(m.group("patch"))


def load_plan_from_dockerfiles(base_dir: Path, repo_dir: Path) -> list[tuple[str, str]]:
    """Fallback quando manca docker_clusters_report.json (es. angular-slickgrid):
    mappa i tag git sui Dockerfile.<from>-<to> presenti in docker/.
    """
    docker_dir = base_dir / "docker"
    ranges: list[tuple[tuple[int, int, int], tuple[int, int, int], str]] = []
    for df in sorted(docker_dir.glob("Dockerfile.*")):
        if df.name.endswith(".dockerignore"):
            continue
        suffix = df.name[len("Dockerfile.") :]
        if "-" in suffix:
            left, right = suffix.split("-", 1)
            lb = parse_bound(left, is_upper=False)
            ub = parse_bound(right, is_upper=True)
        else:
            lb = parse_bound(suffix, is_upper=False)
            ub = parse_bound(suffix, is_upper=True)
        if lb and ub:
            ranges.append((lb, ub, df.name))

    if not ranges:
        raise FileNotFoundError(
            f"Né {base_dir / 'results' / 'docker_clusters_report.json'} né Dockerfile.<range> validi trovati in {docker_dir}"
        )

    raw = subprocess.run(
        ["git", "-C", str(repo_dir), "for-each-ref", "--sort=creatordate", "--format=%(refname:short)", "refs/tags"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    matched: list[tuple[tuple[int, int, int], str, str]] = []
    for name in raw.splitlines():
        name = name.strip()
        m = SEMVER_RE.match(name)
        if not m or m.group("suffix") is not None:
            continue
        sv = (int(m.group("major")), int(m.group("minor")), int(m.group("patch")))
        for lb, ub, df_name in ranges:
            if lb <= sv <= ub:
                matched.append((sv, name, df_name))
                break

    matched.sort(key=lambda x: x[0])
    return [(name, df_name) for _, name, df_name in matched]


def load_version_plan(base_dir: Path, repo_dir: Path) -> list[tuple[str, str]]:
    """Restituisce lista ordinata [(tag, dockerfile_name), ...] da docker_clusters_report.json o fallback docker/."""
    report_json = base_dir / "results" / "docker_clusters_report.json"
    if not report_json.is_file():
        return load_plan_from_dockerfiles(base_dir, repo_dir)
    data = json.loads(report_json.read_text(encoding="utf-8"))

    tag_to_df: dict[str, str] = {}
    ordered_tags: list[str] = []
    for cl in data.get("clusters", []):
        df_name = cl["dockerfile"]
        for ver in cl.get("versions", []):
            tag_to_df[ver] = df_name
            ordered_tags.append(ver)

    # Mantiene l'ordine di `analyses` se disponibile
    analyses_order = [a["tag"] for a in data.get("analyses", []) if a.get("tag") in tag_to_df]
    if analyses_order:
        return [(t, tag_to_df[t]) for t in analyses_order]
    return [(t, tag_to_df[t]) for t in ordered_tags]


def filter_plan(
    plan: list[tuple[str, str]],
    from_ver: str | None,
    to_ver: str | None,
    explicit_tags: list[str] | None,
) -> list[tuple[str, str]]:
    if explicit_tags:
        tag_map = dict(plan)
        selected = []
        for t in explicit_tags:
            if t not in tag_map:
                raise ValueError(f"Tag '{t}' non presente in docker_clusters_report.json")
            selected.append((t, tag_map[t]))
        return selected

    if not from_ver and not to_ver:
        return plan

    lower = parse_bound(from_ver, is_upper=False) if from_ver else None
    upper = parse_bound(to_ver, is_upper=True) if to_ver else None

    # Se entrambi i bound non sono semver, usa indice testuale nel piano
    if (from_ver and lower is None) or (to_ver and upper is None):
        names = [t for t, _ in plan]
        start_idx = names.index(from_ver) if from_ver else 0
        end_idx = names.index(to_ver) if to_ver else len(plan) - 1
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx
        return plan[start_idx : end_idx + 1]

    selected = []
    for tag, df_name in plan:
        sv = parse_semver_tuple(tag)
        if sv is None:
            continue
        if lower and sv < lower:
            continue
        if upper and sv > upper:
            continue
        selected.append((tag, df_name))
    return selected


def _has_gui_display() -> bool:
    """Restituisce True se è disponibile una sessione grafica X11 o Wayland."""
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def resolve_terminal(preferred: str | None = None) -> str | None:
    """Individua l'eseguibile del terminale da usare per le finestre separate."""
    if preferred:
        if preferred.lower() == "none":
            return None
        resolved = shutil.which(preferred)
        if not resolved:
            raise FileNotFoundError(f"Terminale non trovato nel PATH: {preferred}")
        return resolved

    if not _has_gui_display():
        return None

    is_kde = "KDE" in os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
    candidates = (
        ["konsole", "alacritty", "kitty", "gnome-terminal", "xfce4-terminal", "terminator", "xterm", "x-terminal-emulator"]
        if is_kde
        else ["x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal", "alacritty", "kitty", "terminator", "xterm"]
    )
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    return None


def build_terminal_command(terminal_bin: str, title: str, cmd: list[str]) -> list[str]:
    """Costruisce la riga di comando specifica per aprire una nuova finestra di terminale."""
    name = Path(terminal_bin).name
    if name == "konsole":
        return [terminal_bin, "--separate", "--qwindowtitle", title, "-p", f"tabtitle={title}", "-e", *cmd]
    if name == "alacritty":
        return [terminal_bin, "--title", title, "-e", *cmd]
    if name == "kitty":
        return [terminal_bin, "--title", title, *cmd]
    if name == "gnome-terminal":
        return [terminal_bin, "--title", title, "--", *cmd]
    if name in ("xfce4-terminal", "terminator"):
        return [terminal_bin, "--title", title, "-e", shlex.join(cmd)]
    if name == "xterm":
        return [terminal_bin, "-T", title, "-e", *cmd]
    return [terminal_bin, "-e", *cmd]


def launch_terminal_tailer(
    terminal_bin: str,
    title: str,
    log_file: Path,
    done_file: Path,
    auto_close: bool,
) -> None:
    """Avvia un terminale separato che mostra in tempo reale l'output scritto in `log_file`."""
    tail_cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--_tail-log",
        str(log_file),
        "--_done-file",
        str(done_file),
        "--_parent-pid",
        str(os.getpid()),
        "--_title",
        title,
    ]
    if auto_close:
        tail_cmd.append("--_auto-close")

    term_cmd = build_terminal_command(terminal_bin, title, tail_cmd)
    try:
        subprocess.Popen(
            term_cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        print(f"[WARN] Impossibile aprire il terminale separato ({terminal_bin}): {exc}", flush=True)


def _is_pid_alive(pid: int) -> bool:
    if pid <= 0:
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def run_log_tailer(
    log_file: Path,
    done_file: Path,
    parent_pid: int,
    title: str,
    auto_close: bool,
) -> int:
    """Modalità interna eseguita dentro il terminale separato per mostrare il log live."""
    sys.stdout.write(f"\033]0;{title}\007")
    sys.stdout.flush()

    deadline = time.monotonic() + 10.0
    while not log_file.exists():
        if done_file.exists() or not _is_pid_alive(parent_pid) or time.monotonic() > deadline:
            break
        time.sleep(0.05)

    parent_died = False
    if log_file.exists():
        with log_file.open("r", encoding="utf-8", errors="replace") as fh:
            while True:
                chunk = fh.read()
                if chunk:
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                    continue

                if done_file.exists():
                    # Drena eventuali byte scritti contestualmente al marker di fine
                    tail_chunk = fh.read()
                    if tail_chunk:
                        sys.stdout.write(tail_chunk)
                        sys.stdout.flush()
                    break

                if not _is_pid_alive(parent_pid):
                    tail_chunk = fh.read()
                    if tail_chunk:
                        sys.stdout.write(tail_chunk)
                        sys.stdout.flush()
                    parent_died = True
                    break

                time.sleep(0.1)

    esito = "TERMINATO"
    if done_file.exists():
        try:
            meta = json.loads(done_file.read_text(encoding="utf-8"))
            esito = str(meta.get("esito", esito))
        except (OSError, json.JSONDecodeError):
            pass
        done_file.unlink(missing_ok=True)
    elif parent_died:
        esito = "INTERROTTO"
        print("\n[INFO] Processo principale terminato.")

    if auto_close:
        print(f"\n--- Fine esecuzione ({esito}). Chiusura automatica... ---", flush=True)
        time.sleep(1.5)
        return 0

    print(f"\n--- Fine esecuzione ({esito}). Premi INVIO per chiudere questo terminale ---", flush=True)
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    return 0


def _write_log(log_fh: TextIO, text: str) -> None:
    if not text:
        return
    log_fh.write(text)
    if not text.endswith("\n"):
        log_fh.write("\n")
    log_fh.flush()


def _run_streamed_command(cmd: list[str], log_fh: TextIO, timeout_sec: int) -> int:
    """Esegue un comando scrivendo stdout+stderr in tempo reale in `log_fh`."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    def _drain() -> None:
        assert proc.stdout is not None
        for line in iter(proc.stdout.readline, ""):
            log_fh.write(line)
            log_fh.flush()

    reader = threading.Thread(target=_drain, daemon=True)
    reader.start()

    try:
        rc = proc.wait(timeout=timeout_sec if timeout_sec > 0 else None)
    except subprocess.TimeoutExpired:
        proc.kill()
        reader.join(timeout=2.0)
        raise

    reader.join()
    return rc


def _build_result(
    ver: str,
    df_name: str,
    esito: str,
    build_rc: int | str,
    test_rc: int | str,
    start_ts: float,
    log_file: Path,
) -> dict:
    return {
        "versione": ver,
        "dockerfile": df_name,
        "esito": esito,
        "build_rc": build_rc,
        "test_rc": test_rc,
        "durata_sec": round(time.monotonic() - start_ts, 1),
        "log_file": str(log_file),
    }


def run_single_version(
    repo_name: str,
    base_dir: Path,
    repo_dir: Path,
    ver: str,
    df_name: str,
    test_args: str,
    timeout_sec: int,
    prune_images: bool,
    terminal_bin: str | None = None,
    auto_close_terminal: bool = False,
) -> dict:
    docker_dir = base_dir / "docker"
    log_dir = base_dir / "results" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    dockerfile = docker_dir / df_name
    safe_repo = re.sub(r"[^a-z0-9_.-]", "-", repo_name.lower())
    safe_ver = re.sub(r"[^a-zA-Z0-9_.-]", "-", ver)
    image_tag = f"{safe_repo}-e2e:{safe_ver}"
    container_name = f"{safe_repo}-run-{safe_ver}-{os.getpid()}"
    wt_dir = Path(f"/tmp/{safe_repo}-wt-{safe_ver}")
    log_file = log_dir / f"test_{safe_ver}.txt"
    done_file = Path(f"/tmp/{safe_repo}-done-{safe_ver}-{os.getpid()}.json")
    done_file.unlink(missing_ok=True)

    start_ts = time.monotonic()
    build_rc: int | str = "-"
    test_rc: int | str = "-"
    esito = "BUILD_FAIL"

    log_fh = log_file.open("w", encoding="utf-8", buffering=1)
    try:
        _write_log(
            log_fh,
            f"=== REPO: {repo_name} | VERSIONE: {ver} | DOCKERFILE: {df_name} ===\n"
            f"Start: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        )

        if terminal_bin:
            title = f"[{repo_name}] {ver} ({df_name})"
            launch_terminal_tailer(
                terminal_bin=terminal_bin,
                title=title,
                log_file=log_file,
                done_file=done_file,
                auto_close=auto_close_terminal,
            )

        with GIT_WORKTREE_LOCK:
            if wt_dir.exists():
                shutil.rmtree(wt_dir, ignore_errors=True)
            subprocess.run(
                ["git", "-C", str(repo_dir), "worktree", "prune"],
                capture_output=True,
                text=True,
            )
            wt_res = subprocess.run(
                ["git", "-C", str(repo_dir), "worktree", "add", "--force", str(wt_dir), ver],
                capture_output=True,
                text=True,
            )
        if wt_res.returncode != 0:
            _write_log(log_fh, "[ERROR] git worktree add fallito:")
            _write_log(log_fh, wt_res.stdout)
            _write_log(log_fh, wt_res.stderr)
            esito = "WORKTREE_FAIL"
            return _build_result(ver, df_name, esito, build_rc, test_rc, start_ts, log_file)

        # 1. Docker build
        build_cmd = [
            "docker",
            "build",
            "--build-arg",
            f"APP_VERSION={ver}",
            "-t",
            image_tag,
            "-f",
            str(dockerfile),
            str(wt_dir),
        ]
        _write_log(log_fh, f"--- DOCKER BUILD: {' '.join(build_cmd)} ---")
        try:
            build_rc = _run_streamed_command(build_cmd, log_fh, timeout_sec)
        except subprocess.TimeoutExpired:
            build_rc = "TIMEOUT"
            esito = "BUILD_TIMEOUT"
            _write_log(log_fh, f"\n[TIMEOUT] Build interrotta dopo {timeout_sec}s")
            return _build_result(ver, df_name, esito, build_rc, test_rc, start_ts, log_file)

        if build_rc != 0:
            esito = "BUILD_FAIL"
            return _build_result(ver, df_name, esito, build_rc, test_rc, start_ts, log_file)

        # 2. Docker run
        run_cmd = [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "--ipc=host",
            "-e",
            f"TEST_ARGS={test_args}",
            image_tag,
        ]
        _write_log(log_fh, f"\n--- DOCKER RUN: {' '.join(run_cmd)} ---")
        try:
            test_rc = _run_streamed_command(run_cmd, log_fh, timeout_sec)
            esito = "PASS" if test_rc == 0 else "TEST_FAIL"
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
            test_rc = "TIMEOUT"
            esito = "TEST_TIMEOUT"
            _write_log(log_fh, f"\n[TIMEOUT] Test interrotto dopo {timeout_sec}s")

        return _build_result(ver, df_name, esito, build_rc, test_rc, start_ts, log_file)
    finally:
        durata = round(time.monotonic() - start_ts, 1)
        _write_log(log_fh, f"\n=== ESITO FINALE: {esito} (durata: {durata}s) ===")
        log_fh.close()

        with GIT_WORKTREE_LOCK:
            subprocess.run(
                ["git", "-C", str(repo_dir), "worktree", "remove", "--force", str(wt_dir)],
                capture_output=True,
            )
            if wt_dir.exists():
                shutil.rmtree(wt_dir, ignore_errors=True)

        if prune_images:
            subprocess.run(["docker", "rmi", "-f", image_tag], capture_output=True)

        if terminal_bin:
            done_file.write_text(json.dumps({"esito": esito, "durata_sec": durata}), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Step 5: build Docker ed esecuzione test E2E in parallelo su un intervallo di versioni."
    )
    parser.add_argument("repo", nargs="?", help="Nome cartella in repositories/repo_nodejs/ o path completo")
    parser.add_argument("--from", dest="from_ver", default=None, help="Versione iniziale (es. 3.1.7)")
    parser.add_argument("--to", dest="to_ver", default=None, help="Versione finale (es. 3.1.15)")
    parser.add_argument("--tags", nargs="+", default=None, help="Lista esplicita di tag da eseguire")
    parser.add_argument("-j", "--jobs", type=int, default=2, help="Numero di versioni in parallelo (default: 2)")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in secondi per build/run (default: 1800, 0=illimitato)")
    parser.add_argument("--test-args", default="", help="Argomenti extra passati a TEST_ARGS nel container")
    parser.add_argument("--prune-images", action="store_true", help="Rimuove l'immagine Docker subito dopo il test per risparmiare disco")
    parser.add_argument("--dry-run", action="store_true", help="Mostra le versioni selezionate e i Dockerfile senza eseguire Docker")
    parser.add_argument("--no-terminals", action="store_true", help="Non apre un terminale separato per ogni versione")
    parser.add_argument("--close-terminals", action="store_true", help="Chiude automaticamente i terminali separati al termine del test")
    parser.add_argument("--terminal", default=None, help="Terminale da usare (es. konsole, alacritty, gnome-terminal, xterm)")

    # Flag interni usati dal processo tailer dentro ciascun terminale separato
    parser.add_argument("--_tail-log", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--_done-file", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--_parent-pid", type=int, default=0, help=argparse.SUPPRESS)
    parser.add_argument("--_title", default="Docker E2E Test", help=argparse.SUPPRESS)
    parser.add_argument("--_auto-close", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args._tail_log:
        if not args._done_file:
            parser.error("--_done-file richiesto con --_tail-log")
        return run_log_tailer(
            log_file=Path(args._tail_log),
            done_file=Path(args._done_file),
            parent_pid=args._parent_pid,
            title=args._title,
            auto_close=args._auto_close,
        )

    if not args.repo:
        parser.error("Specificare il parametro 'repo'.")

    base_dir, repo_dir = resolve_repo_dir(args.repo)
    plan = load_version_plan(base_dir, repo_dir)
    selected = filter_plan(plan, args.from_ver, args.to_ver, args.tags)

    if not selected:
        print("Nessuna versione trovata nell'intervallo specificato.")
        return 1

    terminal_bin = None if (args.no_terminals or args.dry_run) else resolve_terminal(args.terminal)
    if not args.no_terminals and not args.dry_run and terminal_bin is None:
        print("[WARN] Nessun terminale grafico rilevato (DISPLAY/WAYLAND non impostati o emulatore assente): esecuzione solo su file di log.")

    print(
        f"Repository: {base_dir.name} | Versioni selezionate: {len(selected)} | "
        f"Worker paralleli: {args.jobs} | Terminale separato: {Path(terminal_bin).name if terminal_bin else 'disattivo'}"
    )
    if args.dry_run:
        print("\n[DRY-RUN] Piano di esecuzione:")
        for ver, df_name in selected:
            print(f"  - {ver:<16} -> {df_name}")
        return 0

    results_by_ver: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        future_map = {
            ex.submit(
                run_single_version,
                base_dir.name,
                base_dir,
                repo_dir,
                ver,
                df_name,
                args.test_args,
                args.timeout,
                args.prune_images,
                terminal_bin,
                args.close_terminals,
            ): ver
            for ver, df_name in selected
        }
        for idx, fut in enumerate(concurrent.futures.as_completed(future_map), 1):
            r = fut.result()
            results_by_ver[r["versione"]] = r
            print(
                f"[{idx}/{len(selected)}] {r['versione']:<16} -> {r['esito']:<13} "
                f"(build={r['build_rc']}, test={r['test_rc']}, {r['durata_sec']}s)",
                flush=True,
            )

    ordered_results = [results_by_ver[ver] for ver, _ in selected]

    lines = [
        f"REPORT ESECUZIONE TEST DOCKER: {base_dir.name}",
        "=" * 105,
        f"{'Versione':<16} | {'Esito':<13} | {'BuildRC':<7} | {'TestRC':<7} | {'Durata(s)':<9} | {'Dockerfile'}",
        "-" * 105,
    ]
    for r in ordered_results:
        lines.append(
            f"{r['versione']:<16} | {r['esito']:<13} | {str(r['build_rc']):<7} | "
            f"{str(r['test_rc']):<7} | {str(r['durata_sec']):<9} | {r['dockerfile']}"
        )

    counts = {
        "PASS": sum(1 for r in ordered_results if r["esito"] == "PASS"),
        "TEST_FAIL": sum(1 for r in ordered_results if r["esito"] == "TEST_FAIL"),
        "BUILD_FAIL": sum(1 for r in ordered_results if r["esito"] not in ("PASS", "TEST_FAIL")),
    }
    lines += [
        "",
        f"Riepilogo: PASS={counts['PASS']} | TEST_FAIL={counts['TEST_FAIL']} | ALTRO/BUILD_FAIL={counts['BUILD_FAIL']}",
    ]

    report_txt = base_dir / "results" / "esecuzione_test_report.txt"
    report_csv = base_dir / "results" / "esecuzione_test_report.csv"
    report_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with report_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ordered_results[0].keys()))
        writer.writeheader()
        writer.writerows(ordered_results)

    print()
    print("\n".join(lines))
    print(f"\nReport salvato in:\n- {report_txt}\n- {report_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

