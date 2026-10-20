#!/usr/bin/env python3
"""The archive proven: every table of coverage rebuilt from the bucket and set beside this machine's copy (session 362).

Energy Research Warehouse (ERW). For each table of warehouse/metadata/coverage.csv: the table rebuilt from the
erw-archive bucket as of its latest archived run (warehouse/archive/restore.py: rebuild, or rebuild_consolidated
through the session 29 map) into a scratch folder, never into warehouse/output; then the rebuilt file and
warehouse/output/<table>.csv are compared by

    rows       the count of data rows
    newest     the newest ts_utc (series), event_date (events), or none (entities)
    hash       SHA-256 of the sorted 64-bit row hashes (archive.row_hashes: every column but retrieved_at, values as the
               archive normalizes them), so two files with the same rows in any order hash the same

and every mismatch is given a cause:

    equal                  the same rows
    not on this machine    coverage carries the table, this machine holds no copy (the runner's or another machine's)
    not in the archive     nothing archived under the name (a table not yet archived: it cannot be rebuilt at all)
    this machine behind    the archive holds rows this copy lacks and none the other way: a newer run archived them
    archive behind         this copy holds rows the archive lacks and none the other way: the archive cannot rebuild it
                           whole; its missing rows are written to the archive from this copy (--write, data lock)
    both differ            each holds rows the other lacks (a revision on one side, or two machines' runs)

    python warehouse/archive/prove.py                       # every table, the results in runs/archive_prove/prove.jsonl
    python warehouse/archive/prove.py --only '^eia_'        # some tables
    python warehouse/archive/prove.py --write               # then archive the "archive behind" tables (data lock)

A table already in prove.jsonl is not done again (the run can be stopped and resumed); --fresh starts over.
"""

import argparse
import gc
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archive as A  # noqa: E402
import restore as R  # noqa: E402

ROOT = A.ROOT
OUT_DIR = os.path.join(ROOT, "runs", "archive_prove")
SCRATCH = os.path.join(OUT_DIR, "rebuilt")
RESULTS = os.path.join(OUT_DIR, "prove.jsonl")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
CHUNK = 250_000


def stats(path):
    """(rows, newest, sorted row hashes) of one ERW CSV, read in chunks."""
    nhead = A.count_comments(path)
    n, newest, hs = 0, None, []
    for ch in pd.read_csv(path, skiprows=nhead, dtype=str, keep_default_na=False, na_values=[], chunksize=CHUNK):
        n += len(ch)
        col = "ts_utc" if "ts_utc" in ch.columns else ("event_date" if "event_date" in ch.columns else None)
        if col is not None and len(ch):
            m = ch[col].max()
            newest = m if newest is None or m > newest else newest
        if len(ch):
            hs.append(A.row_hashes(ch))
    h = np.sort(np.concatenate(hs)) if hs else np.array([], dtype=np.uint64)
    return n, newest, h


def sha(h):
    return hashlib.sha256(h.tobytes()).hexdigest()


def last_run(name, bucket):
    rl = R.run_log(name, True, bucket)
    if not len(rl):
        return None
    r = rl.iloc[-1]
    return {"run_id": r["run_id"], "archived_at": r["archived_at"], "runner": r.get("runner", ""), "table_rows": int(r["table_rows"])}


def rebuild_to(name, out, bucket):
    """Write the table rebuilt from the bucket to out. Returns the rows its latest run recorded, or None."""
    if R.members_of(name):
        _, expected = R.rebuild_consolidated(name, out, None, True, bucket)
        return expected
    header, df, expected = R.rebuild(name, None, True, bucket)
    with open(out, "w", encoding="utf-8", newline="") as f:
        for h in header:
            f.write(f"# {h}\n")
        df.to_csv(f, index=False, lineterminator="\n")
    return expected


def prove(name, bucket, log=print):
    rec = {"table": name}
    local = os.path.join(A.OUT, name + ".csv")
    out = os.path.join(SCRATCH, name + ".csv")
    t0 = time.time()
    try:
        expected = rebuild_to(name, out, bucket)
    except SystemExit as e:  # restore.replay: nothing archived
        rec.update(status="not in the archive", cause=str(e))
        if os.path.exists(local):
            n, newest, _ = stats(local)
            rec.update(local_rows=n, local_newest=newest)
        return rec
    run = last_run(name, bucket)
    an, anew, ah = stats(out)
    rec.update(archive_rows=an, archive_newest=anew, archive_sha=sha(ah), archive_run=run, archive_expected_rows=expected)
    if not os.path.exists(local):
        rec.update(status="not on this machine", cause="coverage carries the table; this machine holds no copy, so only the archive's side is shown")
        return rec
    ln, lnew, lh = stats(local)
    only_local = int(len(np.setdiff1d(lh, ah, assume_unique=False)))
    only_arch = int(len(np.setdiff1d(ah, lh, assume_unique=False)))
    rec.update(local_rows=ln, local_newest=lnew, local_sha=sha(lh), only_local=only_local, only_archive=only_arch)
    who = f"run {run['run_id']} ({run['archived_at']})" if run else "its last run"
    if only_local == 0 and only_arch == 0 and an == ln:
        rec.update(status="equal", cause="")
    elif only_local == 0:
        rec.update(status="this machine behind", cause=f"the archive holds {only_arch:,} rows this copy lacks; {who} archived them after this copy was written")
    elif only_arch == 0:
        rec.update(status="archive behind", cause=f"this copy holds {only_local:,} rows the archive lacks: the archive cannot rebuild it whole")
    else:
        rec.update(status="both differ", cause=f"this copy holds {only_local:,} rows the archive lacks and the archive {only_arch:,} this copy lacks "
                                               f"(the archive's newest {anew}, this copy's {lnew}; {who})")
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def key_stats(path):
    """{key hash: row hash} of one ERW CSV, read in chunks (the key as archive.key_hashes takes it)."""
    nhead = A.count_comments(path)
    ks, hs = [], []
    for ch in pd.read_csv(path, skiprows=nhead, dtype=str, keep_default_na=False, na_values=[], chunksize=CHUNK):
        if len(ch):
            ks.append(A.key_hashes(ch, A.shape_of(ch.columns)))
            hs.append(A.row_hashes(ch))
    k = np.concatenate(ks) if ks else np.array([], dtype=np.uint64)
    h = np.concatenate(hs) if hs else np.array([], dtype=np.uint64)
    return pd.Series(h, index=k)


def refine(name, bucket):
    """For a table whose rows differ both ways: how many keys only this copy holds, only the archive holds, and both hold
    with other values (a revision), and the cause in words."""
    out = os.path.join(SCRATCH, name + ".csv")
    rebuild_to(name, out, bucket)
    a, l = key_stats(out), key_stats(os.path.join(A.OUT, name + ".csv"))
    os.remove(out)
    a, l = a[~a.index.duplicated(keep="last")], l[~l.index.duplicated(keep="last")]
    both = a.index.intersection(l.index)
    revised = int((a.loc[both].to_numpy() != l.loc[both].to_numpy()).sum())
    only_l, only_a = int(len(l.index.difference(a.index))), int(len(a.index.difference(l.index)))
    rolling = A.rolling(name)
    if only_l == 0:
        cause = (f"no key is this copy's alone: the archive's later runs revised {revised:,} rows' values and added {only_a:,} keys; "
                 "this machine is behind, the archive rebuilds the table whole")
    elif rolling:
        cause = (f"{only_l:,} keys are this copy's alone (a rolling-window table: the archive never deletes a key, so they were never archived), "
                 f"{only_a:,} the archive's alone, {revised:,} revised: the archive cannot rebuild this copy whole")
    else:
        cause = (f"{only_l:,} keys are this copy's alone, {only_a:,} the archive's alone, {revised:,} revised; the table can lose rows, so a key "
                 "only here may be one the publisher withdrew and a later run deleted")
    return {"keys_only_local": only_l, "keys_only_archive": only_a, "keys_revised": revised, "rolling": bool(rolling), "refined_cause": cause}


def fill(names, log=print):
    """Session 362: archive only the rows this machine alone holds, for a table whose archive lacks them while it holds
    newer rows or values this copy lacks (so archiving this copy whole would put its older values back over them). The
    archive's own table as of its latest run, plus this copy's rows of the keys the archive never held, goes through
    archive.archive_table from a scratch folder: its index sees every archived row already, so exactly the missing rows
    are written, as one run. Needs the data lock (archive.py's writers)."""
    import datetime as dt
    import tempfile
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    run_id = now.strftime("%Y%m%dT%H%M%SZ") + "-local"
    bucket, man = A.Bucket(True), A.read_manifest()
    runs, out_dir = [], tempfile.mkdtemp(prefix="erw_fill_")
    for name in names:
        reb = os.path.join(out_dir, name + ".rebuilt.csv")
        rebuild_to(name, reb, bucket)
        hdr, _, a = A.read_table(reb)
        _, _, l = A.read_table(os.path.join(A.OUT, name + ".csv"))
        sh = A.shape_of(l.columns)
        miss = l[~np.isin(A.key_hashes(l, sh), A.key_hashes(a, sh))].reindex(columns=a.columns).fillna("")
        merged = pd.concat([a, miss], ignore_index=True)
        run = last_run(name, bucket)
        with open(os.path.join(out_dir, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# Session 362 (warehouse/archive/prove.py fill): the archive's own rows as of run {run['run_id'] if run else 'none'}, with the "
                    f"{len(miss):,} rows of keys only lab-desktop's copy held, so that the archive rebuilds them\n")
            for h in hdr[1:]:
                f.write(f"# {h}\n")
            merged.to_csv(f, index=False, lineterminator="\n")
        os.remove(reb)
        was = A.OUT
        A.OUT = out_dir
        try:
            r = A.archive_table(name, run_id, now, bucket, man, "local")
        finally:
            A.OUT = was
        if r:
            runs.append(r)
            log(f"filled {name}: {r['added']:,} rows archived, {r['deleted']:,} deleted (the table as archived: {r['table_rows']:,} rows)")
    if runs:
        month = now.strftime("%Y-%m")
        rl = pd.DataFrame(runs, columns=A.RUN_COLS)
        bucket.put(f"_runs/{month}/{run_id}.csv.gz", A.gz(rl.to_csv(index=False, lineterminator="\n")))
        A.append_lines(os.path.join(A.ARCH, "_runs", month + ".csv"), rl,
                       [f"# ERW archive run log, {month} (UTC): one line per table archived by a run. Append only, never rewritten. "
                        "Written by warehouse/archive/archive.py (session 28)."])
    A.write_manifest(man)
    return runs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="a regular expression: these tables")
    ap.add_argument("--fresh", action="store_true", help="start over: the results so far are set aside")
    ap.add_argument("--write", action="store_true", help="archive the tables found 'archive behind' (data lock), after the comparison")
    ap.add_argument("--keep", action="store_true", help="keep the rebuilt files (default: each is removed once compared)")
    ap.add_argument("--refine", action="store_true", help="the tables found 'both differ': keys only here, only in the archive, revised")
    ap.add_argument("--fill", nargs="+", metavar="TABLE", help="archive only the rows of keys this copy alone holds (data lock)")
    a = ap.parse_args(argv)
    if a.fill:
        import importlib.util
        spec = importlib.util.spec_from_file_location("erw_lock", os.path.join(ROOT, "warehouse", "lock.py"))
        lock = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lock)
        lock.require(os.path.join(A.OUT, "x.csv"), "the archive fill")
        return 0 if fill(a.fill) else 1
    if a.refine:
        recs = [json.loads(line) for line in open(RESULTS, encoding="utf-8") if line.strip()]
        bucket = A.Bucket(True)
        out = []
        for r in recs:
            if r["status"] == "both differ" and "refined_cause" not in r and (not a.only or re.search(a.only, r["table"])):
                try:
                    r.update(refine(r["table"], bucket))
                except MemoryError:
                    r["refined_cause"] = "not refined: the machine ran out of memory"
                except Exception as e:
                    r["refined_cause"] = f"not refined: {type(e).__name__}: {str(e)[:200]}"
                print(f"{r['table']}: {r['refined_cause'][:160]}", flush=True)
                gc.collect()
            out.append(r)
        with open(RESULTS + ".tmp", "w", encoding="utf-8") as f:
            for r in out:
                f.write(json.dumps(r, default=str) + "\n")
        os.replace(RESULTS + ".tmp", RESULTS)
        return 0
    os.makedirs(SCRATCH, exist_ok=True)
    if a.fresh and os.path.exists(RESULTS):
        os.replace(RESULTS, RESULTS + f".{int(time.time())}")
    done = set()
    if os.path.exists(RESULTS):
        with open(RESULTS, encoding="utf-8") as f:
            done = {json.loads(line)["table"] for line in f if line.strip()}
    cov = pd.read_csv(COVERAGE, dtype=str, keep_default_na=False)
    cov["n"] = pd.to_numeric(cov["n_rows"], errors="coerce").fillna(0)
    tables = [t for t in cov.sort_values("n")["table"] if (not a.only or re.search(a.only, t)) and t not in done]
    bucket = A.Bucket(True)
    print(f"{len(tables)} tables to prove ({len(done)} done before)", flush=True)
    for name in tables:
        try:
            rec = prove(name, bucket)
        except MemoryError:
            rec = {"table": name, "status": "not compared", "cause": "the machine ran out of memory rebuilding it"}
        except Exception as e:
            rec = {"table": name, "status": "failed", "cause": f"{type(e).__name__}: {str(e)[:300]}", "trace": traceback.format_exc()[-1500:]}
        if not a.keep:
            p = os.path.join(SCRATCH, name + ".csv")
            if os.path.exists(p):
                os.remove(p)
        with open(RESULTS, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")
        print(f"{name}: {rec['status']}{' (' + rec['cause'][:140] + ')' if rec.get('cause') else ''}", flush=True)
        gc.collect()
    if a.write:
        with open(RESULTS, encoding="utf-8") as f:
            behind = [json.loads(line)["table"] for line in f if line.strip() and json.loads(line)["status"] in ("archive behind", "not in the archive")]
        behind = [t for t in behind if os.path.exists(os.path.join(A.OUT, t + ".csv"))]
        if behind:
            pat = "^(" + "|".join(re.escape(t) for t in behind) + ")$"
            print(f"archiving {len(behind)} tables from this machine's copy: {', '.join(behind)}", flush=True)
            r = subprocess.run([sys.executable, os.path.join(HERE, "archive.py"), "write", "--tables", pat], cwd=ROOT)
            return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
