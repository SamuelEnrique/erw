#!/usr/bin/env python3
"""Duplicate deals in energy_deals: the register a person or a session writes, checked, and the site's copy of it.

Energy Research Warehouse (ERW), session 113. The extraction (warehouse/deals/extract.py) asks the model to mark a deal
that is one it has already extracted, and some slip through: two outlets on the same day, or one deal reported at two
stages. warehouse/deals/duplicates.csv names each pair found, one row a pair:

    duplicate_event_id   the row that repeats another
    kept_event_id        the row that stays, with its own fields as extracted
    ruling               fold (clearly one transaction) or doubtful (listed, not folded)
    reason               what the stories say, in a sentence
    found                the session and the day

This script calls no model and makes no request. It checks the register against the table and writes
site/data/deal_duplicates.json, which /deals/v2 reads: a folded pair is shown as one deal, the kept row, with the story
links of both. Nothing is rewritten in energy_deals: the table is as the extraction left it, and the register says
which of its rows repeat another.

    python warehouse/deals/duplicates.py            # check, and write site/data/deal_duplicates.json
    python warehouse/deals/duplicates.py --check    # check only; exit 1 when the site's copy is not the register's
"""

import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REGISTER = os.path.join(HERE, "duplicates.csv")
DEALS = os.path.join(ROOT, "warehouse", "output", "energy_deals.csv")
SNAPSHOT = os.path.join(ROOT, "site", "data", "deal_duplicates.json")
COLS = ["duplicate_event_id", "kept_event_id", "ruling", "reason", "found"]
RULINGS = ("fold", "doubtful")


def register():
    r = pd.read_csv(REGISTER, dtype=str, keep_default_na=False)
    if list(r.columns) != COLS:
        raise RuntimeError(f"duplicates.csv columns {list(r.columns)}, expected {COLS}")
    return r


def check(reg, deals):
    """Every problem with the register, as sentences; an empty list when it is sound."""
    ids = set(deals["event_id"])
    bad = []
    for r in reg.to_dict("records"):
        pair = f"{r['duplicate_event_id']} -> {r['kept_event_id']}"
        if r["ruling"] not in RULINGS:
            bad.append(f"{pair}: ruling {r['ruling']!r} is not one of {RULINGS}")
        if not r["reason"].strip() or not r["found"].strip():
            bad.append(f"{pair}: no reason or no session")
        for k in ("duplicate_event_id", "kept_event_id"):
            if r[k] not in ids:
                bad.append(f"{pair}: {r[k]} is not in energy_deals")
        if r["duplicate_event_id"] == r["kept_event_id"]:
            bad.append(f"{pair}: a row cannot repeat itself")
    folds = reg[reg["ruling"] == "fold"]
    if folds["duplicate_event_id"].duplicated().any():
        bad.append("a row is folded into two others")
    if set(folds["duplicate_event_id"]) & set(folds["kept_event_id"]):
        bad.append("a kept row is itself folded into another: name the last one as kept")
    return bad


def snapshot(reg):
    return {"register": "warehouse/deals/duplicates.csv", "table": "energy_deals",
            "pairs": [{"duplicate": r["duplicate_event_id"], "kept": r["kept_event_id"], "ruling": r["ruling"],
                       "reason": r["reason"], "found": r["found"]} for r in reg.to_dict("records")]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the register of duplicate deals, checked, and the site's copy")
    ap.add_argument("--check", action="store_true", help="check only; write nothing")
    a = ap.parse_args(argv)
    reg = register()
    deals = pd.read_csv(DEALS, comment="#", dtype=str, keep_default_na=False)
    bad = check(reg, deals)
    for b in bad:
        print(f"duplicates.csv: {b}", file=sys.stderr)
    if bad:
        return 1
    snap = snapshot(reg)
    held = None
    if os.path.exists(SNAPSHOT):
        with open(SNAPSHOT, encoding="utf-8") as f:
            held = json.load(f)
    same = held is not None and {k: held.get(k) for k in snap} == snap
    n = int((reg["ruling"] == "fold").sum())
    print(f"duplicates.csv: {len(reg)} pairs, {n} folded, {len(reg) - n} doubtful; energy_deals holds {len(deals)} rows, "
          f"{len(deals) - n} deals once the folded pairs are one")
    if a.check:
        if not same:
            print("site/data/deal_duplicates.json is not the register's: run warehouse/deals/duplicates.py", file=sys.stderr)
        return 0 if same else 1
    if not same:
        snap["built"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(SNAPSHOT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(snap, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print(f"wrote {os.path.relpath(SNAPSHOT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
