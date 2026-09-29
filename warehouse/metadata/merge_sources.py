#!/usr/bin/env python3
"""Merge two copies of the ERW source registry into one (session 29).

Energy Research Warehouse (ERW). warehouse/metadata/sources.csv only grows (docs/datastandard.md,
decision 13): a run updates a report's description and last_seen and adds tables, and never removes
an entry, so erw.cite() can always name a report an earlier run used. The daily workflow used to
keep its own copy of a file that main also changed while it ran, and on 2026-09-28 that dropped the
source a session had added (archive/sessions/SESSION_28_REPORT.md). The session 29 ruling: the
workflow regenerates sources.csv after its pull, never before, from both copies:

    python warehouse/metadata/merge_sources.py MAIN_COPY RUN_COPY --out warehouse/metadata/sources.csv

- every source in either copy is kept;
- a source in both: the run's description, license and URLs (the newer read), the union of the
  tables, the earlier first_seen and the later last_seen.
Exit 1 if either copy lacks the registry's columns.
"""

import argparse
import os
import sys

import pandas as pd

COLS = ["source", "publisher", "report", "report_url", "document_list", "license",
        "tables", "first_seen", "last_seen"]


def read(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [c for c in COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"{path}: not a source registry, missing {missing}")
    return {r["source"]: dict(r) for r in df[COLS].to_dict("records")}


def merge(main, run):
    out = dict(main)
    for sid, r in run.items():
        m = main.get(sid)
        if m is None:
            out[sid] = r
            continue
        tables = sorted(set(t for t in (m["tables"] + ";" + r["tables"]).split(";") if t))
        firsts = [d for d in (m["first_seen"], r["first_seen"]) if d]
        lasts = [d for d in (m["last_seen"], r["last_seen"]) if d]
        out[sid] = {**m, **{k: v for k, v in r.items() if v != ""}, "tables": ";".join(tables),
                    "first_seen": min(firsts) if firsts else "", "last_seen": max(lasts) if lasts else ""}
    return pd.DataFrame([out[k] for k in sorted(out)], columns=COLS)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Merge two copies of warehouse/metadata/sources.csv")
    ap.add_argument("main_copy", help="the registry on main after the pull")
    ap.add_argument("run_copy", help="the registry this run wrote")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    main_reg, run_reg = read(args.main_copy), read(args.run_copy)
    reg = merge(main_reg, run_reg)
    tmp = args.out + ".tmp"
    reg.to_csv(tmp, index=False, lineterminator="\n")
    os.replace(tmp, args.out)
    only_main = sorted(set(main_reg) - set(run_reg))
    only_run = sorted(set(run_reg) - set(main_reg))
    print(f"sources: {len(reg)} ({len(only_main)} only on main, {len(only_run)} only in this run)"
          + (f"; kept from main: {only_main[:5]}" if only_main else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
