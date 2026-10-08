#!/usr/bin/env python3
"""Session 154: draw the audit sample of policy_actions by a stated seed, and save it before any row is checked.

Energy Research Warehouse (ERW). The sample is random.Random(SEED).sample(sorted(event_id), N): the same list on any
machine that holds the same table. Nothing is swapped: a source that cannot be fetched is a result, not a redraw.

    python warehouse/policy/audit/audit_sample.py --in-dir C:/Users/lossa/Documents/erw/warehouse/output \
        --out C:/Users/lossa/Documents/erw/runs/session154/audit/sample.csv
"""

import argparse
import datetime as dt
import hashlib
import os
import random
import sys

import pandas as pd

SEED, N = 154, 50


def read_events(path):
    with open(path, encoding="utf-8") as f:
        head = [ln for ln in f if ln.startswith("#")]
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False)


def draw(ids, seed=SEED, n=N):
    return random.Random(seed).sample(sorted(ids), n)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy audit sample")
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if os.path.exists(args.out):
        print(f"{args.out} exists: the sample is drawn once and not redrawn", file=sys.stderr)
        return 1
    path = os.path.join(args.in_dir, "policy_actions.csv")
    acts = read_events(path)
    ids = draw(acts["event_id"])
    reads = read_events(os.path.join(args.in_dir, "policy_reads.csv"))
    has_read = set(reads["action_event_id"])
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    s = acts.set_index("event_id").loc[ids].reset_index()
    s.insert(0, "draw", range(1, len(s) + 1))
    s["has_read"] = s["event_id"].isin(has_read).map({True: "yes", False: "no"})
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        f.write(f"# Session 154 audit sample: random.Random({SEED}).sample(sorted(event_id), {N}) over {len(acts)} rows "
                f"of policy_actions.csv (sha256 {sha})\n# Drawn {now} (UTC), before any source was fetched.\n")
        s[["draw", "event_id", "source", "agency", "action_type", "event_date", "has_read", "source_url"]].to_csv(
            f, index=False, lineterminator="\n")
    print(f"{len(s)} of {len(acts)} drawn with seed {SEED}; {int((s['has_read'] == 'yes').sum())} have an impact read")
    print(s.groupby(["source", "action_type"]).size().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
