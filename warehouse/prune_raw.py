#!/usr/bin/env python3
"""Prune raw source files older than 14 days, keeping every manifest.csv.

Energy Research Warehouse (ERW), session 5 ruling: raw files stay local
(warehouse/raw is gitignored) and runs older than 14 days are pruned, but
each run's manifest.csv is kept, so what was downloaded, when, from where and
with which SHA-256 stays on record after the bytes are gone.

    python warehouse/prune_raw.py              # prune runs older than 14 days
    python warehouse/prune_raw.py --dry-run    # list what would be removed
    python warehouse/prune_raw.py --days 30

A run's age comes from its directory name (the run id, YYYYMMDDTHHMMSSZ), not
from file times, which copying can change. Directories whose name is not a
run id are left alone and reported. Only files inside
warehouse/raw/<source>/<run_id>/ are ever removed.
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "warehouse", "raw")
KEEP = "manifest.csv"


def prune(raw_dir=RAW, days=14, dry_run=False, now=None):
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    removed_files = removed_bytes = 0
    pruned_runs, skipped = [], []
    if not os.path.isdir(raw_dir):
        return {"runs": [], "files": 0, "bytes": 0, "skipped": []}
    for source in sorted(os.listdir(raw_dir)):
        sdir = os.path.join(raw_dir, source)
        if not os.path.isdir(sdir):
            continue
        for run_id in sorted(os.listdir(sdir)):
            rdir = os.path.join(sdir, run_id)
            if not os.path.isdir(rdir):
                continue
            try:
                started = datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                skipped.append(os.path.relpath(rdir, raw_dir))
                continue
            if started >= cutoff:
                continue
            n = 0
            for name in os.listdir(rdir):
                path = os.path.join(rdir, name)
                if name == KEEP or not os.path.isfile(path):
                    continue
                removed_bytes += os.path.getsize(path)
                n += 1
                if not dry_run:
                    os.remove(path)
            if n:
                pruned_runs.append(f"{source}/{run_id}")
                removed_files += n
    return {"runs": pruned_runs, "files": removed_files, "bytes": removed_bytes, "skipped": skipped}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Prune ERW raw files older than N days")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--raw-dir", default=RAW)
    args = ap.parse_args(argv)
    r = prune(args.raw_dir, args.days, args.dry_run)
    verb = "would remove" if args.dry_run else "removed"
    print(f"prune_raw: {verb} {r['files']} files ({r['bytes'] / 1e6:.1f} MB) from "
          f"{len(r['runs'])} runs older than {args.days} days; every manifest.csv kept")
    for s in r["skipped"]:
        print(f"  not a run id, left alone: {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
