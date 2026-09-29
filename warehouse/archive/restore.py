#!/usr/bin/env python3
"""Rebuild an ERW table from the append-only archive (session 28).

Energy Research Warehouse (ERW). Replays a table's archive (warehouse/archive/<table>/<YYYY-MM>.csv,
or its parts in the private Supabase storage bucket erw-archive) in the order the runs archived it:
an upsert line sets its key's row, a delete line removes the key. The result is the table as it
stood after any chosen run.

    python warehouse/archive/restore.py ercot_dam_hub_prices                  # as of the latest run
    python warehouse/archive/restore.py ercot_dam_hub_prices --as-of 2026-09-28T23:00:00Z
    python warehouse/archive/restore.py ercot_dam_hub_prices --from-bucket    # from the bucket, not local files
    python warehouse/archive/restore.py --all --check                         # rebuild every table, compare with warehouse/output
    python warehouse/archive/restore.py ercot_dam_hub_prices --out warehouse/output/ercot_dam_hub_prices.csv

It writes to runs/archive_restore/<table>.csv unless --out names a path, and never replaces a file in
warehouse/output unless --out names it. The file's header is the table's own provenance header as the
chosen run recorded it (warehouse/archive/_runs), after a line saying it was rebuilt from the archive.
--check compares the rebuilt rows with the table in warehouse/output (values as the archive compares
them) and with the row count the run recorded. Exit 1 on a mismatch or a failure.
"""

import argparse
import gzip
import io
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archive as A  # noqa: E402


def month_frames(name, from_bucket=False, bucket=None):
    """Every archived line of a table, as frames in archive order, with _extra unpacked."""
    frames = []
    if from_bucket:
        bucket = bucket or A.Bucket(True)
        for mo in bucket.ls(name):
            for o in bucket.ls(f"{name}/{mo['name']}"):
                if o["name"].endswith(".csv.gz"):
                    frames.append(pd.read_csv(io.BytesIO(gzip.decompress(bucket.get(f"{name}/{mo['name']}/{o['name']}"))),
                                              dtype=str, keep_default_na=False, na_values=[]))
    else:
        d = os.path.join(A.ARCH, name)
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if f.endswith(".csv"):
                frames.append(A.read_month(os.path.join(d, f)))
    out = []
    for f in frames:
        if A.EXTRA in f.columns and f[A.EXTRA].ne("").any():
            ext = pd.DataFrame([json.loads(x) if x else {} for x in f[A.EXTRA]], index=f.index)
            f = pd.concat([f.drop(columns=[A.EXTRA]), ext], axis=1)
        out.append(f.drop(columns=[A.EXTRA], errors="ignore"))
    return out


def run_log(name, from_bucket=False, bucket=None):
    """The _runs lines of one table, oldest first."""
    frames = []
    if from_bucket:
        bucket = bucket or A.Bucket(True)
        for mo in bucket.ls("_runs"):
            for o in bucket.ls(f"_runs/{mo['name']}"):
                frames.append(pd.read_csv(io.BytesIO(gzip.decompress(bucket.get(f"_runs/{mo['name']}/{o['name']}"))),
                                          dtype=str, keep_default_na=False, na_values=[]))
    else:
        d = os.path.join(A.ARCH, "_runs")
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if f.endswith(".csv"):
                frames.append(A.read_month(os.path.join(d, f)))
    if not frames:
        return pd.DataFrame(columns=A.RUN_COLS)
    rl = pd.concat(frames, ignore_index=True)
    rl = rl[rl["table"] == name].drop_duplicates("run_id")
    return rl.sort_values(["archived_at", "run_id"], kind="stable")


def replay(name, as_of=None, from_bucket=False, bucket=None):
    """(rows of the table as of the run, the lines replayed). Rows keep every column seen."""
    frames = month_frames(name, from_bucket, bucket)
    if not frames:
        raise SystemExit(f"{name}: nothing archived {'in the bucket' if from_bucket else 'in warehouse/archive'}")
    lines = pd.concat(frames, ignore_index=True).fillna("")
    lines["_order"] = np.arange(len(lines))
    lines = lines.sort_values(["_archived_at", "_run_id", "_order"], kind="stable")
    if as_of:
        lines = lines[lines["_archived_at"] <= as_of]
    last = lines.drop_duplicates("_key_sha", keep="last")
    rows = last[last["_op"] == "upsert"]
    return rows, lines


def rebuild(name, as_of=None, from_bucket=False, bucket=None):
    """(header lines, frame) of the table as of the last run at or before as_of."""
    rows, lines = replay(name, as_of, from_bucket, bucket)
    rl = run_log(name, from_bucket, bucket)
    if as_of:
        rl = rl[rl["archived_at"] <= as_of]
    if len(rl):
        run = rl.iloc[-1]
        cols = json.loads(run["columns"])
        header = [f"Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run {run['run_id']} "
                  f"({run['archived_at']}); that run's own header of the table follows"] + run["header"].split("\n")
        expected = int(run["table_rows"])
    else:  # no run log: the columns the lines carry, in their order
        cols = [c for c in rows.columns if c not in A.FIXED and c != "_order"]
        header = ["Rebuilt from the ERW archive by warehouse/archive/restore.py; no run log was found"]
        expected = None
    df = rows.reindex(columns=cols).fillna("").reset_index(drop=True)
    if "_order" in df.columns:
        df = df.drop(columns=["_order"])
    return header, df, expected


def state_from_archive(name, from_bucket=False, bucket=None):
    """The index archive.py keeps (every row hash archived, the keys as last archived), from the archive."""
    rows, lines = replay(name, None, from_bucket, bucket)
    ups = lines[lines["_op"] == "upsert"]
    cols = [c for c in ups.columns if c not in A.FIXED and c != "_order"]
    # a row's hash is over the columns it had when archived: the non-blank ones of its run
    rl = run_log(name, from_bucket, bucket)
    by_run = {r["run_id"]: json.loads(r["columns"]) for _, r in rl.iterrows()}
    seen = []
    for rid, part in ups.groupby("_run_id", sort=False):
        c = by_run.get(rid, cols)
        seen.append(A.row_hashes(part.reindex(columns=c).fillna("")))
    seen = np.unique(np.concatenate(seen)) if seen else np.array([], dtype=np.uint64)
    keys = np.unique(np.array([int(k, 16) for k in rows["_key_sha"]], dtype=np.uint64))
    run_id = str(lines["_run_id"].iloc[-1]) if len(lines) else ""
    return seen, keys, run_id


def check(name, df, expected):
    """Rebuilt rows against warehouse/output (as the archive compares values, retrieved_at left out: the
    archive keeps a row's retrieved_at from the run that first archived its values) and the recorded count."""
    path = os.path.join(A.OUT, name + ".csv")
    msgs = []
    if expected is not None and len(df) != expected:
        msgs.append(f"{len(df):,} rows, the run recorded {expected:,}")
    if os.path.exists(path):
        _, _, cur = A.read_table(path)
        if list(cur.columns) != list(df.columns):
            msgs.append("columns differ from warehouse/output")
        else:
            a, b = np.sort(A.row_hashes(df)), np.sort(A.row_hashes(cur))
            if len(a) != len(b) or not np.array_equal(a, b):
                msgs.append(f"rows differ from warehouse/output ({len(df):,} rebuilt, {len(cur):,} there, "
                            f"{len(np.setdiff1d(b, a)):,} of theirs missing)")
    return msgs


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rebuild an ERW table from the archive (session 28)")
    ap.add_argument("tables", nargs="*")
    ap.add_argument("--all", action="store_true", help="every table in the archive")
    ap.add_argument("--as-of", help="UTC timestamp: the table as of the last run at or before it")
    ap.add_argument("--from-bucket", action="store_true", help="read the bucket's parts, not the local month files")
    ap.add_argument("--out", help="where to write (one table only); default runs/archive_restore/<table>.csv")
    ap.add_argument("--check", action="store_true", help="compare with warehouse/output and the recorded row count")
    ap.add_argument("--no-write", action="store_true", help="with --check: compare only, write nothing")
    args = ap.parse_args(argv)
    bucket = A.Bucket(True) if args.from_bucket else None
    names = list(args.tables)
    if args.all:
        if args.from_bucket:
            names = sorted(o["name"] for o in bucket.ls("") if o.get("id") is None and not o["name"].startswith("_"))
        else:
            names = sorted(d for d in os.listdir(A.ARCH) if os.path.isdir(os.path.join(A.ARCH, d))
                           and not d.startswith("_"))
    if not names or (args.out and len(names) > 1):
        ap.error("name one table with --out, or tables, or --all")
    bad = 0
    for name in names:
        try:
            header, df, expected = rebuild(name, args.as_of, args.from_bucket, bucket)
            if not args.no_write:
                out = args.out or os.path.join(A.ROOT, "runs", "archive_restore", name + ".csv")
                os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
                with open(out, "w", encoding="utf-8", newline="") as f:
                    for h in header:
                        f.write(f"# {h}\n")
                    df.to_csv(f, index=False, lineterminator="\n")
            msgs = check(name, df, expected) if args.check else []
            bad += bool(msgs)
            print(f"{'MISMATCH' if msgs else 'ok      '} {name}: {len(df):,} rows"
                  + (f"; {'; '.join(msgs)}" if msgs else "")
                  + ("" if args.no_write else f" -> {os.path.relpath(out, A.ROOT)}"), flush=True)
        except Exception as exc:
            bad += 1
            print(f"FAIL     {name}: {type(exc).__name__}: {exc}", flush=True)
    print(f"rebuilt {len(names) - bad} of {len(names)} tables" + (" (checked)" if args.check else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
