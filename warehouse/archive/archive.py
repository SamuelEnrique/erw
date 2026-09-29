#!/usr/bin/env python3
"""The ERW's append-only durable store (session 28; Ben Domingue's review, item 1).

Energy Research Warehouse (ERW). The tables in warehouse/output are a working store: the
daily run rewrites them, and the rolling-window tables keep their history only by merging.
This script keeps every version of every row where no rewrite can reach it.

    python warehouse/archive/archive.py write               # the daily step: archive what changed
    python warehouse/archive/archive.py write --no-bucket   # local files only (tests, DRY_STORES=1)
    python warehouse/archive/archive.py write --tables '^ercot_'
    python warehouse/archive/archive.py sync                # upload local parts the bucket lacks
    python warehouse/archive/archive.py pull                # append the bucket's parts this machine lacks
    python warehouse/archive/archive.py status              # months, parts and bytes, locally and in the bucket
    python warehouse/archive/archive.py reindex             # rebuild every index from the month files
    python warehouse/archive/archive.py seed-consolidated   # session 29, once per consolidated table

What a run writes, for each table in warehouse/output whose data changed since its last archive
(warehouse/metadata/archive_manifest.csv):
- warehouse/archive/<table>/<YYYY-MM>.csv, the month of the run (UTC). Append only: a run adds
  lines at the end and never rewrites a byte already there. Each line is one row that is new or
  changed since the table was last archived (_op upsert), or, for a table that can lose rows, one
  key that has disappeared (_op delete, with only its _key_sha). Columns: _run_id, _archived_at,
  _op, _key_sha, the table's columns as of the month file's first line, and _extra (JSON of any
  column added since).
- The same lines as one immutable object in the private Supabase storage bucket erw-archive:
  <table>/<YYYY-MM>/<run_id>.csv.gz, a standalone CSV with its column row. Written once and never
  overwritten (the upload refuses an existing name), so the bucket is append-only too.
- warehouse/archive/_runs/<YYYY-MM>.csv (and _runs/<YYYY-MM>/<run_id>.csv.gz in the bucket): one
  line per table and run: rows added, keys deleted, the table's row count and data SHA-256, its
  columns, and its own provenance header in full, so every archived number traces to its source.

"New or changed" is decided by a per-table index of 64-bit hashes (warehouse/archive/_state/,
and _state/<table>.npz in the bucket, the one object that is overwritten: it is an index, not the
archive, and warehouse/archive/restore.py --state rebuilds it from the parts). A row is archived
when its hash has never been archived, or when its key is not in the table as last archived (a
row that comes back). Values are compared as the ERW writes them after a Redivis restore (numbers
as floats, true and false in lower case), so a restored table is not archived again for its
formatting alone. The rolling-window tables (restore_before_run in warehouse/redivis/config.yaml)
only merge, so their keys are never deleted: a key missing from a stale local copy is not a
deletion.

The bucket is the shared copy: GitHub runs and local runs both write to it, and a local machine
brings in the runs it did not make with `pull`. warehouse/archive/restore.py rebuilds any table,
as of any run, from the month files or from the bucket. Credentials: SUPABASE_URL and
SUPABASE_SERVICE_KEY (.env or the environment), never printed. Exit 1 if any table fails.
"""

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import sys

import numpy as np
import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
ARCH = HERE
MANIFEST = os.path.join(ROOT, "warehouse", "metadata", "archive_manifest.csv")
MANIFEST_COLS = ["table", "data_sha256", "rows", "run_id", "archived_at"]
BUCKET = "erw-archive"
FIXED = ["_run_id", "_archived_at", "_op", "_key_sha"]
EXTRA = "_extra"
RUN_COLS = ["run_id", "archived_at", "runner", "table", "month", "added", "deleted", "table_rows",
            "data_sha256", "columns", "header"]
KEYS = {"series": ["entity", "variable", "ts_utc"], "events": ["event_id"], "entities": ["entity_id"]}
ROLLING = yaml.safe_load(open(os.path.join(ROOT, "warehouse", "redivis", "config.yaml"),
                              encoding="utf-8"))["restore_before_run"]
PAGE = 1000


def log(msg):
    print(msg, flush=True)


def secret(name):
    v = os.environ.get(name)
    if not v:
        from dotenv import dotenv_values
        v = (dotenv_values(os.path.join(ROOT, ".env")).get(name) or "").strip()
    if not v:
        raise SystemExit(f"{name} is not set (.env or environment); nothing archived to the bucket")
    return v.strip()


def rolling(name):
    return any(re.match(p, name) for p in ROLLING)


# ---------------------------------------------------------------- tables and hashes

def read_table(path):
    """(provenance header lines, data text, frame of strings) of one ERW CSV."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    n = 0
    while n < len(lines) and lines[n].startswith("#"):
        n += 1
    data = "\n".join(lines[n:])
    df = pd.read_csv(io.StringIO(data), dtype=str, keep_default_na=False, na_values=[])
    return [ln[1:].strip() for ln in lines[:n]], data, df


def shape_of(cols):
    cols = list(cols)
    if cols[:2] == ["entity_id", "entity_type"]:
        return "entities"
    if cols[:1] == ["event_id"]:
        return "events"
    return "series"


def normalized(s):
    """A column as it compares: numbers as Python floats (Redivis returns 12 as 12.0), true and
    false in lower case, everything else as written. Each distinct value is normalized once."""
    codes, uniq = pd.factorize(s.fillna("").astype(str), sort=False)
    u = pd.Series(uniq, dtype=object)
    num = pd.to_numeric(u.where(u.str.strip() != ""), errors="coerce")
    out = u.where(num.isna(), num.astype(float).astype(str))
    low = out.str.lower()
    out = out.where(~low.isin(["true", "false"]), low)
    return out.to_numpy(dtype=object)[codes] if len(codes) else np.array([], dtype=object)


def h64(texts):
    return np.fromiter((int.from_bytes(hashlib.blake2b(t.encode("utf-8"), digest_size=8).digest(), "little")
                        for t in texts), dtype=np.uint64, count=len(texts))


def joined(df, cols, prefix=""):
    """One text per row: the normalized values of cols joined by , after prefix."""
    parts = [normalized(df[c]) if c in df.columns else np.full(len(df), "", dtype=object) for c in cols]
    return [prefix + "".join(t) for t in zip(*parts)] if parts else [prefix] * len(df)


# Session 28, after the first daily run: a column that says only when a run read the row. A full-history
# table rewrites it on every row every run, so comparing it re-archived 0.9 million unchanged rows in a day.
# It is left out of the comparison: a row is archived when anything else in it is new, and keeps the
# retrieved_at of that run; every run's own retrieval time is in its _runs line (the table's header).
VOLATILE = ("retrieved_at",)
HASH_VERSION = "2"  # 1: every column (the first two runs); 2: VOLATILE left out


def row_hashes(df):
    """One hash per row over every column but VOLATILE, named, so a renamed or added column changes it."""
    cols = sorted(c for c in df.columns if c not in VOLATILE)
    return h64(joined(df, cols, "".join(cols) + ""))


def key_hashes(df, shape):
    return h64(joined(df, KEYS[shape]))


def hexes(a):
    return [format(int(x), "016x") for x in a]


# ---------------------------------------------------------------- the bucket

class Bucket:
    """The private Supabase storage bucket erw-archive, or nothing (enabled=False)."""

    def __init__(self, enabled):
        self.enabled = enabled
        if not enabled:
            return
        import urllib.parse
        from supabase import create_client
        u = urllib.parse.urlparse(secret("SUPABASE_URL"))
        self.client = create_client(f"{u.scheme}://{u.netloc}", secret("SUPABASE_SERVICE_KEY"))
        buckets = {b.name: b for b in self.client.storage.list_buckets()}
        if BUCKET not in buckets:
            self.client.storage.create_bucket(BUCKET, options={"public": False})
            log(f"created the private storage bucket {BUCKET}")
        elif getattr(buckets[BUCKET], "public", False):
            raise SystemExit(f"storage bucket {BUCKET} is public; it must be private. Nothing archived")
        self.b = self.client.storage.from_(BUCKET)

    def get(self, path):
        """The object's bytes, or None when it does not exist. Any other error propagates."""
        from storage3.exceptions import StorageApiError
        try:
            return self.b.download(path)
        except StorageApiError as exc:
            if str(getattr(exc, "status", "")) in ("400", "404") and "not found" in str(exc).lower():
                return None
            raise

    def put(self, path, data, overwrite=False):
        """Upload; without overwrite an existing object is an error (the archive is immutable)."""
        self.b.upload(path, data, {"content-type": "application/octet-stream",
                                   "upsert": "true" if overwrite else "false"})

    def ls(self, prefix):
        """Names directly under prefix (folders and files), every page."""
        out, off = [], 0
        while True:
            got = self.b.list(prefix, {"limit": PAGE, "offset": off, "sortBy": {"column": "name", "order": "asc"}})
            out += got
            if len(got) < PAGE:
                return out
            off += PAGE


def gz(text):
    return gzip.compress(text.encode("utf-8"), mtime=0)


# ---------------------------------------------------------------- state

def state_path(name):
    return os.path.join(ARCH, "_state", name + ".npz")


def pack_state(seen, keys, run_id):
    buf = io.BytesIO()
    np.savez(buf, seen=seen, keys=keys, run_id=np.array(run_id), version=np.array(HASH_VERSION))
    return buf.getvalue()


def unpack_state(data):
    """(seen, keys, run_id), or None for an index built with another hash version (rebuilt from the archive)."""
    z = np.load(io.BytesIO(data), allow_pickle=False)
    if "version" not in z.files or str(z["version"]) != HASH_VERSION:
        return None
    return z["seen"], z["keys"], str(z["run_id"])


def load_state(name, bucket, man):
    """(seen row hashes, keys as last archived, run id) or None for a table never archived.
    The bucket's index is the shared one; a local index is used only without the bucket."""
    data = None
    if bucket.enabled:
        data = bucket.get(f"_state/{name}.npz")
    elif os.path.exists(state_path(name)):
        with open(state_path(name), "rb") as f:
            data = f.read()
    st = unpack_state(data) if data is not None else None
    if st is not None:
        return st
    if name in man.index:
        # archived before, but its index is gone: rebuild it from the parts rather than archive everything again
        import restore
        log(f"  {name}: no index in the {'bucket' if bucket.enabled else 'local archive'}; rebuilding it from the archive")
        return restore.state_from_archive(name, from_bucket=bucket.enabled, bucket=bucket)
    return None


def save_state(name, seen, keys, run_id, bucket):
    data = pack_state(seen, keys, run_id)
    os.makedirs(os.path.dirname(state_path(name)), exist_ok=True)
    with open(state_path(name), "wb") as f:
        f.write(data)
    if bucket.enabled:
        bucket.put(f"_state/{name}.npz", data, overwrite=True)


# ---------------------------------------------------------------- month files

def month_columns(path):
    """The column row of an existing month file (the first line that is not a # comment)."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                return list(pd.read_csv(io.StringIO(line), dtype=str, nrows=0).columns)
    return None


def to_month_columns(rows, cols):
    """rows (FIXED + the table's columns) laid out in a month file's columns: a column the file
    does not have goes into _extra as JSON; a column the rows do not have is blank."""
    table_cols = [c for c in cols if c not in FIXED and c != EXTRA]
    extra = [c for c in rows.columns if c not in cols]
    out = pd.DataFrame(index=rows.index)
    for c in FIXED + table_cols:
        out[c] = rows[c] if c in rows.columns else ""
    if extra:
        out[EXTRA] = [json.dumps(dict(zip(extra, vals)), ensure_ascii=False, sort_keys=True)
                      for vals in rows[extra].itertuples(index=False, name=None)]
    else:
        out[EXTRA] = ""
    return out[FIXED + table_cols + [EXTRA]]


def month_header(name, month, header):
    return [f"# ERW archive: table {name}, the rows archived in {month} (UTC). Append only, never rewritten.",
            "# Each line is a row that was new or changed when a run archived it (_op upsert), or a key that had "
            "disappeared (_op delete, only _key_sha).",
            "# Written by warehouse/archive/archive.py (session 28); rebuild the table with warehouse/archive/restore.py. "
            f"Copy in the private Supabase storage bucket {BUCKET}: {name}/{month}/<run_id>.csv.gz, one object per run.",
            "# Provenance: each run's own header of the table is in warehouse/archive/_runs/<YYYY-MM>.csv. "
            "The table's header when this month's file was started:"] + [f"# | {h}" for h in header]


def append_lines(path, df, header_lines=None):
    """Append df's rows to path; a new file gets the header lines and the column row first."""
    new = not os.path.exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as f:
        if new:
            for ln in header_lines or []:
                f.write(ln + "\n")
        df.to_csv(f, index=False, header=new, lineterminator="\n")


def count_comments(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n


# ---------------------------------------------------------------- manifest

def read_manifest():
    if os.path.exists(MANIFEST):
        return pd.read_csv(MANIFEST, dtype=str, keep_default_na=False).set_index("table")
    return pd.DataFrame(columns=MANIFEST_COLS).set_index("table")


def write_manifest(man):
    m = man.reset_index().rename(columns={"index": "table"}).sort_values("table")[MANIFEST_COLS]
    m.to_csv(MANIFEST, index=False, lineterminator="\n")


# ---------------------------------------------------------------- write

def data_sha256(path):
    """SHA-256 of a table's data (the column row onwards), as read_table computes it, streamed (session 29:
    the ERCOT history is 0.65 GB; an unchanged table is skipped without being parsed)."""
    h = hashlib.sha256()
    with open(path, encoding="utf-8", newline="") as f:
        first = True
        for line in f:
            if first and line.startswith("#"):
                continue
            first = False
            h.update(line.encode("utf-8"))
    return h.hexdigest()


def archive_table(name, run_id, now, bucket, man, runner):
    """Archive one table's new or changed rows. Returns the _runs line, or None when unchanged."""
    if name in man.index and man.loc[name, "data_sha256"] == data_sha256(os.path.join(OUT, name + ".csv")):
        return None
    header, data, df = read_table(os.path.join(OUT, name + ".csv"))
    data_sha = hashlib.sha256(data.encode("utf-8")).hexdigest()
    shape = shape_of(df.columns)
    rh, kh = row_hashes(df), key_hashes(df, shape)
    st = load_state(name, bucket, man)
    seen, keys = (st[0], st[1]) if st else (np.array([], dtype=np.uint64), np.array([], dtype=np.uint64))
    new = ~np.isin(rh, seen) | ~np.isin(kh, keys)
    gone = np.array([], dtype=np.uint64) if rolling(name) else np.setdiff1d(keys, kh)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    month = now.strftime("%Y-%m")
    if new.any() or len(gone):
        up = df[new].copy()
        up.insert(0, "_key_sha", hexes(kh[new]))
        up.insert(0, "_op", "upsert")
        up.insert(0, "_archived_at", stamp)
        up.insert(0, "_run_id", run_id)
        dl = pd.DataFrame({"_run_id": run_id, "_archived_at": stamp, "_op": "delete", "_key_sha": hexes(gone)})
        rows = pd.concat([up, dl], ignore_index=True).fillna("")
        path = os.path.join(ARCH, name, month + ".csv")
        cols = month_columns(path) if os.path.exists(path) else FIXED + list(df.columns) + [EXTRA]
        lines = to_month_columns(rows, cols)
        # the bucket first: if the upload fails, nothing local claims this run was archived
        if bucket.enabled:
            bucket.put(f"{name}/{month}/{run_id}.csv.gz", gz(lines.to_csv(index=False, lineterminator="\n")))
        append_lines(path, lines, month_header(name, month, header))
    seen = np.union1d(seen, rh[new]) if new.any() else seen
    keys = np.union1d(keys, kh) if rolling(name) else np.unique(kh)
    save_state(name, seen, keys, run_id, bucket)
    man.loc[name, ["data_sha256", "rows", "run_id", "archived_at"]] = [data_sha, str(len(df)), run_id, stamp]
    return dict(run_id=run_id, archived_at=stamp, runner=runner, table=name, month=month,
                added=int(new.sum()), deleted=int(len(gone)), table_rows=len(df), data_sha256=data_sha,
                columns=json.dumps(list(df.columns)), header="\n".join(header))


def write(tables_re, use_bucket, now=None):
    now = now or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    runner = "github" if os.environ.get("GITHUB_ACTIONS") == "true" else "local"
    run_id = now.strftime("%Y%m%dT%H%M%SZ") + "-" + runner
    bucket = Bucket(use_bucket)
    man = read_manifest()
    names = sorted(os.path.splitext(f)[0] for f in os.listdir(OUT) if f.endswith(".csv"))
    if tables_re:
        names = [n for n in names if any(re.search(p, n) for p in tables_re)]
    runs, failed, unchanged = [], [], 0
    for name in names:
        try:
            r = archive_table(name, run_id, now, bucket, man, runner)
            if r is None:
                unchanged += 1
                continue
            runs.append(r)
            log(f"archived {name}: {r['added']:,} rows new or changed, {r['deleted']:,} keys deleted "
                f"(table {r['table_rows']:,} rows)")
        except Exception as exc:
            failed.append(name)
            log(f"FAIL archive {name}: {type(exc).__name__}: {exc}")
    if runs:
        month = now.strftime("%Y-%m")
        rl = pd.DataFrame(runs, columns=RUN_COLS)
        try:
            if bucket.enabled:
                bucket.put(f"_runs/{month}/{run_id}.csv.gz", gz(rl.to_csv(index=False, lineterminator="\n")))
            append_lines(os.path.join(ARCH, "_runs", month + ".csv"), rl,
                         [f"# ERW archive run log, {month} (UTC): one line per table archived by a run. Append only, "
                          "never rewritten. Written by warehouse/archive/archive.py (session 28)."])
        except Exception as exc:
            failed.append("_runs")
            log(f"FAIL archive run log: {type(exc).__name__}: {exc}")
    write_manifest(man)
    added = sum(r["added"] for r in runs)
    log(f"archive run {run_id}: {len(runs)} tables archived ({added:,} rows), {unchanged} unchanged, "
        f"{len(failed)} failed{': ' + ', '.join(failed) if failed else ''}; "
        f"{'bucket ' + BUCKET + ' and ' if bucket.enabled else ''}warehouse/archive")
    return 1 if failed else 0


# ---------------------------------------------------------------- sync, pull, status

def local_months():
    for name in sorted(os.listdir(ARCH)):
        d = os.path.join(ARCH, name)
        if not os.path.isdir(d) or name == "__pycache__" or (name.startswith("_") and name != "_runs"):
            continue
        for f in sorted(os.listdir(d)):
            if re.match(r"^\d{4}-\d{2}\.csv$", f):
                yield name, f[:-4], os.path.join(d, f)


def read_month(path):
    return pd.read_csv(path, skiprows=count_comments(path), dtype=str, keep_default_na=False, na_values=[])


def sync():
    """Upload every run's lines that are in a local month file but not in the bucket."""
    bucket = Bucket(True)
    n = 0
    for name, month, path in local_months():
        have = {o["name"][:-7] for o in bucket.ls(f"{name}/{month}") if o["name"].endswith(".csv.gz")}
        df = read_month(path)
        idcol = "run_id" if name == "_runs" else "_run_id"
        for rid, part in df.groupby(idcol, sort=False):
            if rid not in have:
                bucket.put(f"{name}/{month}/{rid}.csv.gz", gz(part.to_csv(index=False, lineterminator="\n")))
                n += 1
                log(f"uploaded {name}/{month}/{rid}.csv.gz ({len(part):,} lines)")
    log(f"sync: {n} parts uploaded")
    return 0


def pull():
    """Append to the local month files every run in the bucket they do not have (append only)."""
    bucket = Bucket(True)
    n = 0
    for top in bucket.ls(""):
        name = top["name"]
        if name == "_state" or top.get("id") is not None:
            continue
        for mo in bucket.ls(name):
            month = mo["name"]
            path = os.path.join(ARCH, name, month + ".csv")
            idcol = "run_id" if name == "_runs" else "_run_id"
            local = set(read_month(path)[idcol]) if os.path.exists(path) else set()
            for o in bucket.ls(f"{name}/{month}"):
                rid = o["name"][:-7]
                if not o["name"].endswith(".csv.gz") or rid in local:
                    continue
                part = pd.read_csv(io.BytesIO(gzip.decompress(bucket.get(f"{name}/{month}/{rid}.csv.gz"))),
                                   dtype=str, keep_default_na=False, na_values=[])
                if name == "_runs":
                    hdr = [f"# ERW archive run log, {month} (UTC): one line per table archived by a run. Append "
                           "only, never rewritten. Written by warehouse/archive/archive.py (session 28)."]
                    append_lines(path, part[RUN_COLS], hdr)
                else:
                    cols = month_columns(path) if os.path.exists(path) else list(part.columns)
                    if EXTRA in part.columns and part[EXTRA].ne("").any():  # unpack before re-laying out
                        ext = pd.DataFrame([json.loads(x) if x else {} for x in part[EXTRA]], index=part.index)
                        part = pd.concat([part.drop(columns=[EXTRA]), ext], axis=1).fillna("")
                    append_lines(path, to_month_columns(part.drop(columns=[EXTRA], errors="ignore"), cols),
                                 [f"# ERW archive: table {name}, {month} (UTC); started by archive.py pull from "
                                  f"the bucket {BUCKET}. Append only, never rewritten. See warehouse/archive/README.md."])
                n += 1
                log(f"pulled {name}/{month}/{rid} ({len(part):,} lines)")
    log(f"pull: {n} parts appended")
    return 0


def status(use_bucket):
    tot = 0
    for name, month, path in local_months():
        tot += os.path.getsize(path)
    log(f"local: {sum(1 for _ in local_months())} month files, {tot / 1e6:,.1f} MB in warehouse/archive")
    if use_bucket:
        bucket = Bucket(True)
        parts, size = 0, 0
        for top in bucket.ls(""):
            if top.get("id") is not None:
                continue
            for mo in bucket.ls(top["name"]):
                if mo.get("id") is not None:  # _state/<table>.npz
                    size += int((mo.get("metadata") or {}).get("size") or 0)
                    continue
                for o in bucket.ls(f"{top['name']}/{mo['name']}"):
                    parts += 1
                    size += int((o.get("metadata") or {}).get("size") or 0)
        log(f"bucket {BUCKET}: {parts} run parts, {size / 1e6:,.1f} MB with the indexes")
    return 0


def reindex(tables_re, use_bucket):
    """Rebuild every table's index from the local month files with the current hash version, and store it
    locally and in the bucket (session 28: after VOLATILE was introduced)."""
    import restore
    bucket = Bucket(use_bucket)
    names = sorted(d for d in os.listdir(ARCH) if os.path.isdir(os.path.join(ARCH, d)) and not d.startswith("_")
                   and d != "__pycache__")
    names = sorted(set(names) | set(n for n in read_manifest().index if restore.members_of(n)))  # session 29
    if tables_re:
        names = [n for n in names if any(re.search(p, n) for p in tables_re)]
    bad = 0
    for name in names:
        try:
            seen, keys, run_id = restore.state_from_archive(name)
            save_state(name, seen, keys, run_id, bucket)
            log(f"reindexed {name}: {len(seen):,} row hashes, {len(keys):,} keys (as of {run_id})")
        except Exception as exc:
            bad += 1
            log(f"FAIL reindex {name}: {type(exc).__name__}: {exc}")
    log(f"reindex: {len(names) - bad} of {len(names)} tables (hash version {HASH_VERSION})")
    return 1 if bad else 0


def seed_consolidated(tables_re, use_bucket, now=None):
    """Session 29: a consolidated table's history is archived under its members' old names, which are never
    rewritten or renamed; restore.py reaches it through warehouse/metadata/table_migrations.csv. So that the
    first run under the new name archives only what is new (and not three million rows again), its index is
    built here FROM THE ARCHIVE through the map (restore.state_from_archive), and checked against the table in
    warehouse/output: every one of its rows must already be in the archive. Then the table's manifest line and
    one _runs line (added 0, runner "migration", its header) are appended. A table already archived under its
    new name is left alone."""
    import restore
    now = now or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    run_id = now.strftime("%Y%m%dT%H%M%SZ") + "-migration"
    stamp, month = now.strftime("%Y-%m-%dT%H:%M:%SZ"), now.strftime("%Y-%m")
    bucket = Bucket(use_bucket)
    man = read_manifest()
    names = sorted(pd.read_csv(restore.MIGRATIONS, dtype=str)["new_table"].unique())
    if tables_re:
        names = [n for n in names if any(re.search(p, n) for p in tables_re)]
    runs, bad = [], 0
    for name in names:
        path = os.path.join(OUT, name + ".csv")
        try:
            if name in man.index:
                log(f"{name}: already in {os.path.relpath(MANIFEST, ROOT)}; not seeded again")
                continue
            if not os.path.exists(path):
                raise RuntimeError("not in warehouse/output")
            seen, keys, _ = restore.state_from_archive(name, from_bucket=False)
            nhead = count_comments(path)
            rows, missing = 0, 0
            for chunk in pd.read_csv(path, skiprows=nhead, dtype=str, keep_default_na=False, na_values=[],
                                     chunksize=250_000):
                rows += len(chunk)
                missing += int((~np.isin(row_hashes(chunk), seen)).sum())
                cols = list(chunk.columns)
            if missing:
                raise RuntimeError(f"{missing:,} of its {rows:,} rows are not in the archive through the map; not seeded")
            with open(path, encoding="utf-8") as f:
                header = [ln.rstrip("\r\n")[1:].strip() for ln in f if ln.startswith("#")]
            save_state(name, seen, keys, run_id, bucket)
            sha = data_sha256(path)
            man.loc[name, ["data_sha256", "rows", "run_id", "archived_at"]] = [sha, str(rows), run_id, stamp]
            runs.append(dict(run_id=run_id, archived_at=stamp, runner="migration", table=name, month=month,
                             added=0, deleted=0, table_rows=rows, data_sha256=sha, columns=json.dumps(cols),
                             header="\n".join(header)))
            log(f"seeded {name}: {rows:,} rows, all in the archive through the map; index {len(seen):,} row hashes, "
                f"{len(keys):,} keys")
        except Exception as exc:
            bad += 1
            log(f"FAIL seed {name}: {type(exc).__name__}: {exc}")
    if runs:
        rl = pd.DataFrame(runs, columns=RUN_COLS)
        if bucket.enabled:
            bucket.put(f"_runs/{month}/{run_id}.csv.gz", gz(rl.to_csv(index=False, lineterminator="\n")))
        append_lines(os.path.join(ARCH, "_runs", month + ".csv"), rl,
                     [f"# ERW archive run log, {month} (UTC): one line per table archived by a run. Append only, "
                      "never rewritten. Written by warehouse/archive/archive.py (session 28)."])
    write_manifest(man)
    log(f"seed-consolidated: {len(runs)} seeded, {bad} failed")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW append-only archive (session 28)")
    ap.add_argument("command", choices=["write", "sync", "pull", "status", "reindex", "seed-consolidated"])
    ap.add_argument("--tables", action="append", metavar="REGEX", help="write: only tables matching")
    ap.add_argument("--no-bucket", action="store_true", help="local files only (tests, DRY_STORES=1)")
    args = ap.parse_args(argv)
    if args.command == "write":
        return write(args.tables, not args.no_bucket)
    if args.command == "reindex":
        return reindex(args.tables, not args.no_bucket)
    if args.command == "seed-consolidated":
        return seed_consolidated(args.tables, not args.no_bucket)
    if args.command == "sync":
        return sync()
    if args.command == "pull":
        return pull()
    return status(not args.no_bucket)


if __name__ == "__main__":
    sys.exit(main())
