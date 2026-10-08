#!/usr/bin/env python3
"""Session 154: compare a trial policy_actions.csv with the table held, field by field. Reads two files, writes none.

Energy Research Warehouse (ERW). For the hand-over: after `policy_sources.py --out-dir <trial>`, this says how many
rows the fixed extraction changes in each field, how many rows are only in one file, and prints up to --show
examples a field. Columns a trial run cannot fill are left out by default (news_story_ids and news_story_urls need
news_stories.csv in the trial folder; retrieved_at is the run's own time).

    python warehouse/policy/audit/audit_compare.py --held C:/Users/lossa/Documents/erw/warehouse/output \
        --trial C:/Users/lossa/Documents/erw/runs/session154/audit/trial
"""

import argparse
import os
import sys

import pandas as pd

SKIP = ["news_story_ids", "news_story_urls", "retrieved_at"]


def read_events(path):
    with open(path, encoding="utf-8") as f:
        head = [ln for ln in f if ln.startswith("#")]
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False)


def compare(held, trial, skip=SKIP):
    """({field: [event_id, ...]}, ids only held, ids only in the trial)."""
    h, t = held.set_index("event_id"), trial.set_index("event_id")
    both = h.index.intersection(t.index)
    out = {}
    for c in h.columns:
        if c in skip or c not in t.columns:
            continue
        diff = both[(h.loc[both, c] != t.loc[both, c]).to_numpy()]
        if len(diff):
            out[c] = list(diff)
    return out, sorted(set(h.index) - set(t.index)), sorted(set(t.index) - set(h.index))


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy audit: a trial table against the table held")
    ap.add_argument("--held", required=True)
    ap.add_argument("--trial", required=True)
    ap.add_argument("--show", type=int, default=3)
    ap.add_argument("--all-columns", action="store_true")
    args = ap.parse_args(argv)
    held = read_events(os.path.join(args.held, "policy_actions.csv"))
    trial = read_events(os.path.join(args.trial, "policy_actions.csv"))
    diff, gone, new = compare(held, trial, [] if args.all_columns else SKIP)
    rows = sorted({e for ids in diff.values() for e in ids})
    print(f"held {len(held)} rows, trial {len(trial)} rows; {len(rows)} rows differ in at least one field; "
          f"{len(gone)} only in the held table, {len(new)} only in the trial")
    h, t = held.set_index("event_id"), trial.set_index("event_id")
    for c, ids in sorted(diff.items(), key=lambda kv: -len(kv[1])):
        print(f"  {c}: {len(ids)} rows")
        for e in ids[:args.show]:
            print(f"    {e}: {h.at[e, c][:90]!r} -> {t.at[e, c][:90]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
