#!/usr/bin/env python3
"""A page file is never committed with less history than main holds (session 3714, chain 208).

Energy Research Warehouse (ERW). docs/state/main_red_2026-11-06.md: the daily run of 6 November 2026 (the runner's
catch-up, the first run of November, so the monthly builders ran) rewrote page files from tables shorter than their
history. CAISO's energy mix lost its months of California's hydro gap (90 months to 80), because
warehouse/scheduled.py did not name caiso_fuel_supply_history among mix_profile's inputs, so the runner's restore step
never fetched it and the builder wrote CAISO without those months; the board's hourly files and the curtailment profile
were rebuilt from shorter windows the same way. Main then failed five tests. This runs in the runner's commit step,
after the files are staged and before the commit:

    python scripts/never_thinner.py --staged            every staged file it knows how to measure, against HEAD
    python scripts/never_thinner.py --staged --dry-run  say which would be put back; change nothing
    python scripts/never_thinner.py --check NEW OLD     measure two copies of one file (a test, a person)

A file is measured by the history it says it holds: its "months" (a page file built by month: the energy mix, how
clean, the curtailment profile), its "first" period, and for an hourly series of the price board (t0, n) its first
hour. A staged file whose first period is later than HEAD's, or that drops a month HEAD holds other than its newest,
is put back as HEAD has it (in the index and on disk) and named; the commit goes ahead with the rest. A file this
cannot measure is left as it is. Exit 0 (whatever was put back; each is named), 2 bad input. Standard library only.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
# the folders whose files carry a history this can measure
PREFIXES = ("site/data/mix/", "site/data/clean/", "site/data/stress/", "site/data/mixplus/", "site/data/curtailment_profile.json",
            "site/public/board/h/", "site/public/board/s/")


def git(args, cwd=ROOT, text=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=text, stdin=subprocess.DEVNULL)


def thinner(new, old):
    """Why the new copy holds less history than the old one, or None. Both are a page file's parsed JSON."""
    if not isinstance(new, dict) or not isinstance(old, dict):
        return None
    if isinstance(new.get("t0"), int) and isinstance(old.get("t0"), int) and new["t0"] > old["t0"]:
        return f"its first hour moved later ({old['t0']} to {new['t0']}): {new['t0'] - old['t0']} hours of history lost"
    for key in ("first", "first_day"):
        a, b = new.get(key), old.get(key)
        if isinstance(a, str) and isinstance(b, str) and a > b:
            return f"its {key} moved later ({b} to {a})"
    nm, om = new.get("months"), old.get("months")
    if isinstance(nm, dict) and isinstance(om, dict) and om:
        newest = max(om)
        lost = sorted(m for m in om if m not in nm and m != newest)
        if lost:
            return f"{len(lost)} months HEAD holds are gone ({lost[0]} to {lost[-1]}): {len(om)} months to {len(nm)}"
    return None


def staged_files():
    p = git(["diff", "--cached", "--name-only", "--diff-filter=M"])
    return [f for f in p.stdout.splitlines() if f.startswith(PREFIXES) and f.endswith(".json")]


def head_copy(path):
    p = git(["show", f"HEAD:{path}"], text=False)
    return None if p.returncode != 0 else json.loads(p.stdout.decode("utf-8"))


def staged_copy(path):
    p = git(["show", f":{path}"], text=False)
    return None if p.returncode != 0 else json.loads(p.stdout.decode("utf-8"))


def put_back(path):
    git(["reset", "--quiet", "HEAD", "--", path])
    git(["checkout", "HEAD", "--", path])


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", nargs=2, metavar=("NEW", "OLD"))
    a = ap.parse_args(argv)
    if a.check:
        try:
            with open(a.check[0], encoding="utf-8") as f:
                new = json.load(f)
            with open(a.check[1], encoding="utf-8") as f:
                old = json.load(f)
        except (OSError, ValueError) as exc:
            print(f"never_thinner: cannot read: {exc}")
            return 2
        why = thinner(new, old)
        print(f"thinner: {why}" if why else "not thinner")
        return 1 if why else 0
    if not a.staged:
        ap.error("--staged or --check")
    back = []
    for path in staged_files():
        try:
            new, old = staged_copy(path), head_copy(path)
        except ValueError:
            continue
        why = thinner(new, old) if new is not None and old is not None else None
        if why:
            back.append((path, why))
            if not a.dry_run:
                put_back(path)
    for path, why in back:
        print(f"::warning title=page file kept as main has it::{path}: {why}{' (dry run: not put back)' if a.dry_run else ''}")
    print(f"never_thinner: {len(back)} page files {'would be ' if a.dry_run else ''}put back as main has them")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
