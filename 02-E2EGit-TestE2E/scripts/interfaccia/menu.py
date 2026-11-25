#!/usr/bin/env python3
import json
import os
import subprocess

with open("/opt/e2e/config.json") as f:
    cfg = json.load(f)

APP_DIR = "/app"
TEST_DIR = cfg.get("test_workdir") or APP_DIR
RESULTS_DIR = "/opt/e2e/results/commits"
T0_COMMIT = os.environ["T0_COMMIT"]

state = {"sha": T0_COMMIT, "date": "", "time": ""}


def run(cmd, cwd=APP_DIR, check=True):
    return subprocess.run(cmd, shell=True, cwd=cwd, check=check)


def checkout(sha, date="", time_str=""):
    run(f"git clean -fd && git checkout -f {sha}")
    if cfg.get("install_cmd"):
        run(cfg["install_cmd"])
    if cfg.get("build_cmd"):
        run(cfg["build_cmd"])
    state.update(sha=sha, date=date, time=time_str)


def run_tests(extra=""):
    out_file = f"{RESULTS_DIR}/{state['date']}_{state['time']}_{state['sha']}.json"

    cmd = f"PLAYWRIGHT_JSON_OUTPUT_NAME={out_file} {cfg['test_cmd']} {extra} --reporter=list,json"
    res = run(cmd, cwd=TEST_DIR, check=False)
    print(f"\nExit code: {res.returncode} | Report: {out_file}")


def run_range(file_path, start_n, end_n, extra=""):
    with open(file_path) as f:
        for line in f:
            parts = line.split()
            if parts and start_n <= int(parts[1]) <= end_n:
                _, num, date, time_str, sha = parts[:5]
                print(f"\n>>> Commit {num}: {sha} ({date} {time_str})")
                checkout(sha, date, time_str)
                run_tests(extra)


while True:
    print(f"\n=== {cfg.get('repo_name', 'E2E')} | commit={state['sha'][:9]} ({state['date']} {state['time']}) ===")
    print("1. Reset a t0_commit")
    print("2. Checkout commit")
    print("3. Mostra commit attuale")
    print("4. Esegui test Playwright")
    print("5. Esegui test su intervallo commit da file")
    print("0. Esci")

    choice = input("\nScelta: ").strip()
    if choice == "0":
        break
    elif choice == "1":
        checkout(T0_COMMIT)
    elif choice == "2":
        checkout(input("SHA commit: ").strip())
    elif choice == "3":
        print(f"Commit: {state['sha']}\nData:   {state['date']}\nOra:    {state['time']}")
    elif choice == "4":
        run_tests(input("Test specifico (Invio = tutti): ").strip())
    elif choice == "5":
        file_path = input("Path file commit: ").strip()
        start_n = int(input("Commit iniziale (x): ").strip())
        end_n = int(input("Commit finale (y): ").strip())
        extra = input("Test specifico (Invio = tutti): ").strip()
        run_range(file_path, start_n, end_n, extra)

