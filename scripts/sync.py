#!/usr/bin/env python3
"""Sync this machine from the cloud, the ERW's source of truth (session 59). Every session starts with it.

Energy Research Warehouse (ERW). docs/machines.md.

    python scripts/sync.py              # pull main; compare every table with Redivis; restore the missing and the behind
    python scripts/sync.py --check      # report only: what is missing, behind or ahead, nothing written
    python scripts/sync.py --tables '^eia930_'   # only tables matching
    python scripts/sync.py --refresh    # also replace a table that has diverged from Redivis (neither ahead nor behind)
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

The tables (session 72): coverage.csv only lists them (and their licenses). Each local table is compared with Redivis's
own copy, the draft of its dataset (or the last released version when no draft is open), by row count and by its newest
timestamp (ts_utc, else event_date or date). Until session 72 the comparison was with coverage.csv's n_rows, which the
same machine may have rebuilt from its own files, so a stale machine looked current (session 67: this laptop's
eia930_all_interchange and news_scores_shadow). Each table is then:

- missing here: restored from Redivis;
- behind: Redivis holds a newer timestamp, or the same newest timestamp and more rows: restored from Redivis;
- ahead: this machine holds a newer timestamp, or the same and more rows (a data run not yet uploaded): never
  overwritten, and said so on its own line;
- diverged: newer here by one measure and older by the other: reported; replaced only with --refresh;
- current: the same newest timestamp and the same rows.

Restored rows are checked against Redivis's own count. The restore writes local working files only, so it needs no data
lock. Exit 1 if any restore fails or Redivis cannot be read for a table.
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
    """Data rows of a CSV: the records after the '#' header lines and the column row. Session 60: records, not lines;
    a quoted field may hold a line break (the queue tables' notes), and counting lines made three tables look different
    from coverage when they were not."""
    import csv
    with open(path, encoding="utf-8", newline="") as f:
        lines = (ln for ln in f if not ln.startswith("#"))
        n = sum(1 for _ in csv.reader(lines)) - 1
    return max(n, 0)


TIME_COLUMNS = ("ts_utc", "event_date", "date")


def norm_ts(v):
    """A timestamp as 'YYYY-MM-DD HH:MM:SS' (or a shorter date), so a CSV's text and Redivis's value compare as text."""
    if v is None:
        return None
    t = str(v).strip()
    if not t or t.lower() in ("nan", "nat", "none"):
        return None
    t = t.replace("T", " ").replace("Z", "")
    t = re.sub(r"[+-]00:?00$", "", t)
    return t[:19]


def local_state(path):
    """(data rows, time column, newest timestamp) of a local CSV, in one pass over its records."""
    import csv
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(ln for ln in f if not ln.startswith("#"))
        head = next(reader, [])
        col = next((c for c in TIME_COLUMNS if c in head), None)
        k = head.index(col) if col else None
        n, newest = 0, None
        for rec in reader:
            n += 1
            if k is not None and k < len(rec):
                v = norm_ts(rec[k])
                if v and (newest is None or v > newest):
                    newest = v
    return n, col, newest


def classify(local, cloud):
    """'missing', 'current', 'behind', 'ahead' or 'diverged': this machine's (rows, newest) against Redivis's.
    local None: missing here. A newest of None (a table with no time column) compares by rows alone."""
    if local is None:
        return "missing"
    (ln, lt), (cn, ct) = local, cloud
    t = 0 if lt == ct or lt is None or ct is None else (1 if lt > ct else -1)
    r = (ln > cn) - (ln < cn)
    if t == 0 and r == 0:
        return "current"
    if t >= 0 and r >= 0:
        return "ahead"
    if t <= 0 and r <= 0:
        return "behind"
    return "diverged"


def open_read(acct, dataset):
    """A dataset's draft when one is open, else its last released version. Read only: never creates a draft."""
    d = acct.dataset(dataset, version="next")
    try:
        if d.exists():
            return d
    except Exception:
        pass
    return acct.dataset(dataset)


def cloud_state(names, lic, cols, log):
    """{name: (rows, newest) or None when Redivis does not hold it}; a table whose question goes unanswered is left out
    and reported, never read as absent."""
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
    import redivis
    import upload as up
    acct, opened, out = up.account(), {}, {}
    for name in names:
        dataset = up.dataset_for(lic.get(name, ""))
        try:
            if dataset not in opened:
                opened[dataset] = open_read(acct, dataset)
            meta = up.table_meta(opened[dataset], name)
            if meta is None:
                out[name] = None
                continue
            ref = meta["qualifiedReference"]
            col = cols.get(name)
            sql = f"select count(*) as n{f', max(`{col}`) as newest' if col else ''} from `{ref}`"
            row = redivis.query(sql).to_arrow_table(progress=False).to_pylist()[0]
            out[name] = (int(row["n"]), norm_ts(row.get("newest")))
        except Exception as exc:
            log(f"  could not read {name} on Redivis ({dataset}): {type(exc).__name__}: {str(exc)[:160]}")
    return out


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


def main(argv=None, cloud_reader=None, restorer=None):
    ap = argparse.ArgumentParser(description="ERW sync: pull main, compare every table with Redivis, restore (session 59, 72)")
    ap.add_argument("--check", action="store_true", help="report only")
    ap.add_argument("--tables", help="only tables matching this regex")
    ap.add_argument("--refresh", action="store_true", help="also replace tables that have diverged from Redivis")
    ap.add_argument("--no-git", action="store_true")
    a = ap.parse_args(argv)
    log = lambda m: print(m, flush=True)  # noqa: E731
    cloud_reader, restorer = cloud_reader or cloud_state, restorer or restore
    if not a.no_git:
        log("git: " + pull())
    cov = pd.read_csv(COVERAGE, dtype=str, keep_default_na=False)
    if a.tables:
        cov = cov[cov["table"].str.contains(a.tables, regex=True)]
    lic = dict(zip(cov["table"], cov["license"]))
    os.makedirs(OUT, exist_ok=True)
    local, cols = {}, {}
    for t in cov["table"]:
        path = os.path.join(OUT, t + ".csv")
        if os.path.exists(path):
            n, col, newest = local_state(path)
            local[t], cols[t] = (n, newest), col
    cloud = cloud_reader(list(cov["table"]), lic, cols, log)
    unread = [t for t in cov["table"] if t not in cloud]
    groups = {k: [] for k in ("current", "missing", "behind", "ahead", "diverged", "not on Redivis")}
    for t in cov["table"]:
        if t in unread:
            continue
        if cloud[t] is None:
            groups["not on Redivis"].append(t)
            continue
        groups[classify(local.get(t), cloud[t])].append(t)
    log(f"tables in coverage: {len(cov)}; " + "; ".join(f"{k}: {len(v)}" for k, v in groups.items()) + f"; unread: {len(unread)}")
    fmt = lambda x: "none" if x is None else f"{x[0]:,} rows to {x[1] or 'no timestamp'}"  # noqa: E731
    for k in ("behind", "diverged"):
        for t in groups[k]:
            log(f"  {k}: {t}: here {fmt(local.get(t))}; Redivis {fmt(cloud[t])}")
    for t in groups["ahead"]:
        log(f"  AHEAD, not overwritten: {t}: here {fmt(local.get(t))}; Redivis {fmt(cloud[t])} (upload it, or it is lost with this machine)")
    for t in groups["not on Redivis"]:
        log(f"  not on Redivis: {t}" + ("" if t in local else ": and not here; rebuild it from the archive: python warehouse/archive/restore.py " + t))
    todo = groups["missing"] + groups["behind"] + (groups["diverged"] if a.refresh else [])
    if a.check or not todo:
        return 1 if unread else 0
    log(f"restoring {len(todo)} tables from Redivis")
    got = restorer(todo, lic, log)
    failed = [t for t, (_, e) in got.items() if e]
    off = [(t, n) for t, (n, e) in got.items() if not e and n != cloud[t][0]]
    for t, n in off:
        log(f"  FAILED {t}: restored {n:,} rows, Redivis counted {cloud[t][0]:,}")
    log(f"sync: {len(got) - len(failed) - len(off)} restored, {len(failed) + len(off)} failed")
    return 1 if failed or off or unread else 0


if __name__ == "__main__":
    sys.exit(main())
