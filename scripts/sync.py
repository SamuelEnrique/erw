#!/usr/bin/env python3
"""Sync this machine from the cloud, the ERW's source of truth (session 59). Every session starts with it.

Energy Research Warehouse (ERW). docs/machines.md.

    python scripts/sync.py              # pull main; restore every warehouse table missing here from Redivis; verify counts
    python scripts/sync.py --check      # report only: what is missing or differs, nothing written
    python scripts/sync.py --tables '^eia930_'   # only tables matching
    python scripts/sync.py --refresh    # also replace a local table whose row count differs from coverage with Redivis's
    python scripts/sync.py --no-git     # skip the pull

Where the warehouse lives in the cloud (docs/machines.md, "Cloud copies"):
- the code, the metadata (coverage.csv lists every table and its rows) and the news tables: GitHub, main
- every table, as last uploaded by a data run: Redivis, the public dataset and the internal one (licenses as in
  coverage.csv); the daily job already restores its rolling-window tables from there each morning
- every row ever written, by month: the append-only archive (warehouse/archive/, and the private Supabase Storage bucket
  erw-archive), which warehouse/archive/restore.py rebuilds a table from; Redivis is the first choice, the archive the
  fallback for what Redivis lacks
- raw source files (warehouse/raw/, several GB): the data machine only, by design (too large for the free tiers)

The pull: on main with no uncommitted tracked changes, a fast-forward to origin/main (a merge if local commits exist; never
a force or a rebase). On another branch, it fetches and reports.

The tables: for every table in coverage.csv, the local CSV's data rows against coverage's n_rows. Missing here: restored
from its Redivis dataset, with its provenance header from Redivis's erw_headers table, and the rows downloaded checked
against Redivis's own count and against coverage. Present but different: reported (a data machine may hold newer rows
than the last upload); replaced only with --refresh. The restore writes local working files only, so it needs no data
lock. Exit 1 if any restore fails.
"""

import argparse
import os
import re
import subprocess
import sys
import time

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def pull():
    git("fetch", "-q", "origin")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != "main":
        ahead = git("rev-list", "--count", f"origin/main..{branch}")
        return f"on branch {branch} ({ahead} commits not on main): fetched, not merged"
    dirty = [ln for ln in git("status", "--porcelain").splitlines() if not ln.startswith("??")]
    if dirty:
        return f"main has {len(dirty)} uncommitted tracked changes: fetched, not merged (commit or stash them, then sync)"
    before = git("rev-parse", "HEAD")
    r = subprocess.run(["git", "merge", "--ff-only", "-q", "origin/main"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        git("merge", "--no-edit", "-q", "origin/main")
    after = git("rev-parse", "HEAD")
    n = git("rev-list", "--count", f"{before}..{after}")
    return f"main: {n} new commits merged ({before[:7]} to {after[:7]})"


def local_rows(path):
    """Data rows of a CSV: the lines after the '#' header lines and the column row."""
    n = -1
    with open(path, "rb") as f:
        for ln in f:
            if not ln.startswith(b"#"):
                n += 1
    return max(n, 0)


def restore(names, lic, log):
    """Each table from its Redivis dataset into warehouse/output, header lines first. Returns {name: (rows, error)}."""
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
    import upload as up
    drafts = up.Drafts()
    headers, out = {}, {}
    for name in names:
        try:
            dataset = up.dataset_for(lic.get(name, ""))
            ds = drafts(dataset)
            meta = up.table_meta(ds, name)
            if meta is None:
                raise RuntimeError(f"not in the Redivis dataset {dataset}; rebuild it from the archive: python warehouse/archive/restore.py {name}")
            have = meta.get("numRows")
            t0 = time.time()
            df = up.as_erw_text(ds.table(name).to_pandas_dataframe(progress=False, dtype_backend="numpy"))
            if have is not None and len(df) != int(have):
                raise RuntimeError(f"downloaded {len(df):,} rows, Redivis's count is {int(have):,}")
            if dataset not in headers:
                try:
                    h = ds.table(up.HEADERS_TABLE).to_pandas_dataframe(progress=False, dtype_backend="numpy")
                    headers[dataset] = {t: [str(x) for x in g.sort_values("line_no")["line"]] for t, g in h.groupby("table")}
                except Exception as exc:
                    headers[dataset] = {}
                    log(f"  WARNING: no header lines from {up.HEADERS_TABLE} ({dataset}): {type(exc).__name__}")
            lines = [x for x in headers[dataset].get(name, []) if not x.startswith("Restored from the Redivis draft")]
            path = os.path.join(OUT, name + ".csv")
            tmp = path + ".sync"
            with open(tmp, "w", encoding="utf-8", newline="") as f:
                for x in lines:
                    f.write(f"# {x}\n")
                f.write(f"# Restored from the Redivis draft ({dataset}) by scripts/sync.py; the connector rewrites this header when it merges\n")
                df.to_csv(f, index=False, lineterminator="\n")
            os.replace(tmp, path)  # never half-written: a sync interrupted here leaves the old file or none
            out[name] = (len(df), None)
            log(f"  restored {name}: {len(df):,} rows in {time.time() - t0:.0f} s ({dataset})")
        except Exception as exc:
            out[name] = (0, f"{type(exc).__name__}: {str(exc)[:200]}")
            log(f"  FAILED {name}: {out[name][1]}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW sync: pull main, restore the warehouse from the cloud (session 59)")
    ap.add_argument("--check", action="store_true", help="report only")
    ap.add_argument("--tables", help="only tables matching this regex")
    ap.add_argument("--refresh", action="store_true", help="also replace tables whose row count differs from coverage")
    ap.add_argument("--no-git", action="store_true")
    a = ap.parse_args(argv)
    log = lambda m: print(m, flush=True)  # noqa: E731
    if not a.no_git:
        log("git: " + pull())
    cov = pd.read_csv(COVERAGE, dtype=str, keep_default_na=False)
    if a.tables:
        cov = cov[cov["table"].str.contains(a.tables, regex=True)]
    lic = dict(zip(cov["table"], cov["license"]))
    os.makedirs(OUT, exist_ok=True)
    ok, missing, differs = [], [], []
    for r in cov.itertuples():
        path = os.path.join(OUT, r.table + ".csv")
        want = int(r.n_rows) if str(r.n_rows).isdigit() else None
        if not os.path.exists(path):
            missing.append(r.table)
            continue
        have = local_rows(path)
        (ok if want is None or have == want else differs).append((r.table, have, want))
    log(f"tables in coverage: {len(cov)}; here and matching coverage: {len(ok)}; missing here: {len(missing)}; "
        f"present with another row count: {len(differs)}")
    for t, have, want in differs:
        log(f"  differs: {t}: {have:,} rows here, {want:,} in coverage")
    todo = missing + ([t for t, _, _ in differs] if a.refresh else [])
    if a.check or not todo:
        return 0
    log(f"restoring {len(todo)} tables from Redivis")
    got = restore(todo, lic, log)
    want = dict(zip(cov["table"], cov["n_rows"]))
    failed = [t for t, (_, e) in got.items() if e]
    off = [(t, n, want.get(t)) for t, (n, e) in got.items() if not e and str(want.get(t, "")).isdigit() and n != int(want[t])]
    for t, n, w in off:
        log(f"  note: {t} restored with {n:,} rows; coverage says {int(w):,} (coverage is the last data build; Redivis the last upload)")
    log(f"sync: {len(got) - len(failed)} restored, {len(failed)} failed, {len(off)} differing from coverage")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
