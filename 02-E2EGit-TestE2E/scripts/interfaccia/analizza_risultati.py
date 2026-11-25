#!/usr/bin/env python3
import glob
import json
import os
import sys


def analyze(path):
    with open(path) as f:
        data = json.load(f)

    passed = failed = flaky = skipped = 0
    failed_names = []

    def walk(suites, parents=()):
        nonlocal passed, failed, flaky, skipped
        for s in suites:
            title = s.get("title", "")
            path_titles = parents + ((title,) if title else ())
            for spec in s.get("specs", []):
                full_name = " > ".join(path_titles + (spec.get("title", ""),))
                for t in spec.get("tests", []):
                    st = t.get("status")
                    if st == "expected":
                        passed += 1
                    elif st == "unexpected":
                        failed += 1
                        failed_names.append(f"[{t.get('projectName', '')}] {full_name}")
                    elif st == "flaky":
                        flaky += 1
                    elif st == "skipped":
                        skipped += 1
            walk(s.get("suites", []), path_titles)

    walk(data.get("suites", []))
    total = passed + failed + flaky + skipped

    lines = [
        f"File: {os.path.basename(path)}",
        f"Totale: {total} | OK: {passed} | Falliti: {failed} | Flaky: {flaky} | Skippati: {skipped}",
    ]
    if failed_names:
        lines.append("Test falliti:")
        for name in failed_names:
            lines.append(f"  - {name}")

    out_path = os.path.splitext(path)[0] + ".txt"
    with open(out_path, "w") as out:
        out.write("\n".join(lines) + "\n")
    print(f"Creato: {out_path}")


target = sys.argv[1]
files = sorted(glob.glob(f"{target}/*.json")) if os.path.isdir(target) else [target]
for p in files:
    analyze(p)

