#!/usr/bin/env python3
"""The second pass over the findings hunt's drafts (chain 164, sessions 3017 to 3019).

Energy Research Warehouse (ERW). Every draft of docs/findings/<family>/ is recomputed from its own reproduce.py, copied
alone into an empty folder (so it reads nothing of the repository), run on the tables its usage line names, and
compared with the expected figures at its top: the first and the last full year, within the stated tolerance (0.5
percent of the change). The draft's own numbers are never read. A draft whose figure does not reproduce is named, with
what the script printed; the session corrects or removes it.

    python warehouse/analysis/findings/deep/check.py --tables C:/Users/Shared/Documents/erw/warehouse/output [--family prices]

Exit 0 every draft reproduces; 1 one or more do not; 2 bad input.
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = os.path.join(ROOT, "docs", "findings")
EXPECTED = re.compile(r"^# Expected: (\d{4}) (-?[\d.e+-]+), (\d{4}) (-?[\d.e+-]+), change (-?[\d.e+-]+) \(")
USAGE = re.compile(r"python \{this file\} (.+)$")


def args_of(text):
    """The table files a script's usage line names, in order ("<a.csv> ... <b.csv>" spans the years between)."""
    for line in text.split("\n"):
        m = USAGE.search(line.strip())
        if not m:
            continue
        names = re.findall(r"<([^>]+\.csv)>", m.group(1))
        if "..." in m.group(1) and len(names) == 2:
            a, b = names
            ya, yb = re.search(r"(\d{4})\.csv$", a), re.search(r"(\d{4})\.csv$", b)
            stem = a[: ya.start()]
            names = [f"{stem}{y}.csv" for y in range(int(ya.group(1)), int(yb.group(1)) + 1)]
        return names
    return None


def expected_of(text):
    for line in text.split("\n")[:3]:
        m = EXPECTED.match(line)
        if m:
            return {"first_year": int(m.group(1)), "first": float(m.group(2)), "last_year": int(m.group(3)), "last": float(m.group(4)), "change": float(m.group(5))}
    return None


def check_one(path, tables, python=sys.executable, timeout=900):
    text = open(path, encoding="utf-8").read()
    exp, names = expected_of(text), args_of(text)
    out = {"draft": os.path.relpath(path, DOCS).replace("\\", "/"), "ok": False}
    if exp is None or not names:
        out["why"] = "no expected line or no usage line"
        return out
    files = [os.path.join(tables, n) for n in names]
    missing = [n for n in names if not os.path.exists(os.path.join(tables, n))]
    if missing:
        out["why"] = f"tables not on this machine: {', '.join(missing)}"
        return out
    with tempfile.TemporaryDirectory() as d:
        script = os.path.join(d, "reproduce.py")
        shutil.copy(path, script)
        r = subprocess.run([python, "-I", script] + files, capture_output=True, text=True, cwd=d, timeout=timeout)
    if r.returncode != 0:
        out["why"] = f"exit {r.returncode}: {r.stderr.strip()[-300:]}"
        return out
    got = {}
    for line in r.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2 and re.fullmatch(r"\d{4}", parts[0]):
            got[int(parts[0])] = float(parts[1])
    tol = max(abs(exp["change"]) * 0.005, 1e-9)
    a, b = got.get(exp["first_year"]), got.get(exp["last_year"])
    out.update(printed_first=a, printed_last=b, expected=exp, tolerance=tol)
    if a is None or b is None:
        out["why"] = "the script printed no figure for the claim's years"
    elif abs(a - exp["first"]) > tol or abs(b - exp["last"]) > tol:
        out["why"] = f"printed {a} and {b}, expected {exp['first']} and {exp['last']} (tolerance {tol:.6g})"
    else:
        out["ok"] = True
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The second pass: every draft recomputed from its reproduce.py (chain 164)")
    ap.add_argument("--tables", required=True, help="the folder holding the tables' CSVs")
    ap.add_argument("--family", default=None)
    ap.add_argument("--out", default=None, help="write the results as JSON here")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.tables):
        print(f"no folder {a.tables}", file=sys.stderr)
        return 2
    paths = sorted(glob.glob(os.path.join(DOCS, a.family or "*", "*.reproduce.py")))
    results = []
    for p in paths:
        res = check_one(p, a.tables)
        results.append(res)
        print(("ok   " if res["ok"] else "FAIL ") + res["draft"] + ("" if res["ok"] else f": {res['why']}"), flush=True)
    bad = [r for r in results if not r["ok"]]
    print(f"{len(results) - len(bad)} of {len(results)} drafts reproduce from their own scripts")
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(results, f, indent=1)
            f.write("\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
