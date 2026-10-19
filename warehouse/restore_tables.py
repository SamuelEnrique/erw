#!/usr/bin/env python3
"""Where a scheduled job's tables come from (session 305): the archive first, Redivis last.

Energy Research Warehouse (ERW). Redivis is the citable release, never a scheduled job's working store. Until session
305 the daily run restored its rolling-window tables from the Redivis draft every morning (upload.py --restore, about
2.5 GB of downloads a run, eia930_all_emissions alone 1.1 GB); with the reruns, the Roundup and the data machine's sync
that passed Redivis's limit of 100 GB of exports in 30 days, and from 15 October 2026 every export was refused
("Cannot export more than 100GB within a 30 day period"), so the daily run stopped at its first step three days running.

    python warehouse/restore_tables.py --rolling                         # every rolling-window table missing here
    python warehouse/restore_tables.py --rolling --cache runs/cache/output   # the daily run: GitHub's cache first
    python warehouse/restore_tables.py t1 t2                             # these tables, when missing here
    python warehouse/restore_tables.py --rolling --check                 # where each would come from; nothing written
    python warehouse/restore_tables.py --rolling --stash runs/cache/output   # after a run: the copies for the cache
    python warehouse/restore_tables.py t1 --seed-bucket                  # a person: an exact copy into the bucket

A table already in warehouse/output is never replaced. Each missing table is taken from the first of these that has it:

1. the cache (--cache DIR): DIR/<table>.csv, the copy an earlier run stashed for GitHub's cache (actions/cache), taken
   only when its data SHA-256 is the one the archive's run log records for the table's latest run: an exact copy;
2. a copy in the archive bucket (_copies/<table>/<data sha256>.csv.gz), taken on the same test: for a table whose
   history the archive alone cannot rebuild row for row (a rolling-window table that drops keys, such as
   policy_reads_evidence, whose deletions the archive does not record). archive.py write puts the copy there each time
   it archives such a table; --seed-bucket puts one there by hand;
3. the archive (warehouse/archive/restore.py, from the private bucket erw-archive): the table rebuilt from its parts,
   taken only when it has the row count the latest run recorded, or more for a table its builder rewrites whole as a
   moving window (judge_by_newest in warehouse/redivis/config.yaml: price_board_spreads). A large table is replayed in
   sixteen slices by key (eia930_all_emissions held whole needs more memory than the machines have);
4. Redivis (warehouse/redivis/upload.py --restore for that table), only under the daily export ceiling of
   warehouse/redivis/config.yaml (export_ceiling_gb_per_day, all machines together): before asking, the ledger of the
   day's exports in the bucket (_exports/<YYYY-MM-DD>/) is read, and an export that would pass the ceiling is not
   asked for. An export made is written to the ledger.

A table none of them gives fails, and the exit is 1: the run stops before a short window could be merged and uploaded
over the full one (the rule of session 28). --no-redivis leaves out the last. Credentials: SUPABASE_URL and
SUPABASE_SERVICE_KEY (the bucket), REDIVIS_API_TOKEN and REDIVIS_OWNER (only when Redivis is asked).
"""

import argparse
import datetime as dt
import gzip
import io
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import time

import numpy as np
import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "archive"))
import archive as A  # noqa: E402
import restore as R  # noqa: E402

CONFIG = yaml.safe_load(open(os.path.join(ROOT, "warehouse", "redivis", "config.yaml"), encoding="utf-8"))
REDIVIS_MANIFEST = os.path.join(ROOT, CONFIG["manifest"])
MIGRATIONS = os.path.join(ROOT, "warehouse", "metadata", "table_migrations.csv")
SLICES = 16  # the replay's slices by the first hex digit of a row's key hash
CAP_MESSAGE = "Cannot export more than"  # Redivis's answer when the 30-day export limit is reached


def log(msg):
    print(msg, flush=True)


def ceiling_bytes():
    return int(float(CONFIG.get("export_ceiling_gb_per_day", 2)) * 1e9)


def rolling_tables():
    """The rolling-window tables the Redivis record lists (restore_before_run), less those consolidated into another:
    the set upload.py --restore checked (session 28)."""
    man = pd.read_csv(REDIVIS_MANIFEST, dtype=str, keep_default_na=False) if os.path.exists(REDIVIS_MANIFEST) \
        else pd.DataFrame(columns=["table", "migrated_to"])
    moved = set(man.loc[man.get("migrated_to", pd.Series(dtype=str)).fillna("") != "", "table"])
    if os.path.exists(MIGRATIONS):
        moved |= set(pd.read_csv(MIGRATIONS, dtype=str)["old_table"])
    return sorted(n for n in man["table"] if A.rolling(n) and n not in moved)


def write_atomic(path, writer):
    """Write through a temporary file beside the target, so an interrupted restore leaves no half-written table."""
    tmp = path + ".restore"
    try:
        writer(tmp)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


class Sources:
    """The four sources of a table, in order; the bucket and its run log opened once, when first needed."""

    def __init__(self, cache=None, redivis=True, bucket=None, log=log):
        self.cache, self.redivis, self.log = cache, redivis, log
        self._bucket, self._runs = bucket, None

    @property
    def bucket(self):
        if self._bucket is None:
            self._bucket = A.Bucket(True)
        return self._bucket

    def latest(self, name):
        """The run log's latest line for a table (a dict), or None when the archive has no run of it."""
        if self._runs is None:
            R.run_log("", True, self.bucket)  # reads the bucket's _runs parts once; restore.py keeps them for its rebuilds
            got = R._BUCKET_RUNS.get(id(self.bucket))
            runs = pd.concat(got, ignore_index=True) if got else pd.DataFrame(columns=A.RUN_COLS)
            self._runs = runs.drop_duplicates(["table", "run_id"]).sort_values(["archived_at", "run_id"], kind="stable")
        rl = self._runs[self._runs["table"] == name]
        return rl.iloc[-1].to_dict() if len(rl) else None

    # ---- 1. the cache
    def from_cache(self, name, path, run):
        if not self.cache or run is None:
            return None
        src = os.path.join(self.cache, name + ".csv")
        if not os.path.exists(src):
            return None
        if A.data_sha256(src) != run["data_sha256"]:
            self.log(f"  {name}: the cached copy is not the latest run's ({run['run_id']}); not taken")
            return None
        write_atomic(path, lambda tmp: shutil.copyfile(src, tmp))
        return int(run["table_rows"])

    # ---- 2. a copy in the bucket
    def from_copy(self, name, path, run):
        if run is None:
            return None
        data = self.bucket.get(f"_copies/{name}/{run['data_sha256']}.csv.gz")
        if data is None:
            return None
        raw = gzip.decompress(data)

        def put(tmp):
            with open(tmp, "wb") as f:
                f.write(raw)
        write_atomic(path, put)
        if A.data_sha256(path) != run["data_sha256"]:
            os.remove(path)
            raise RuntimeError("the bucket's copy does not have the SHA-256 its name says")
        return int(run["table_rows"])

    # ---- 3. the archive
    def parts(self, name):
        """Every archived part of a table, in the bucket's order (months, then run ids), one frame at a time."""
        for mo in self.bucket.ls(name):
            if mo.get("id") is not None:
                continue
            for o in self.bucket.ls(f"{name}/{mo['name']}"):
                if o["name"].endswith(".csv.gz"):
                    f = pd.read_csv(io.BytesIO(gzip.decompress(self.bucket.get(f"{name}/{mo['name']}/{o['name']}"))),
                                    dtype=str, keep_default_na=False, na_values=[])
                    if A.EXTRA in f.columns and f[A.EXTRA].ne("").any():
                        ext = pd.DataFrame([json.loads(x) if x else {} for x in f[A.EXTRA]], index=f.index)
                        f = pd.concat([f.drop(columns=[A.EXTRA]), ext], axis=1)
                    yield f.drop(columns=[A.EXTRA], errors="ignore")

    def replay_sliced(self, name, run, out):
        """restore.replay's rule (the latest line of each key, in archive order; upserts kept), one slice of keys at a
        time, so a table never has to be held whole. Writes the table to out; returns its rows."""
        cols = json.loads(run["columns"])
        work = tempfile.mkdtemp(prefix="erw-replay-")
        try:
            order, n_parts = 0, 0
            for i, f in enumerate(self.parts(name)):
                f = f.fillna("")
                f["_order"] = np.arange(order, order + len(f))
                order += len(f)
                n_parts += 1
                for k, g in f.groupby(f["_key_sha"].str[:1]):
                    g.to_pickle(os.path.join(work, f"{k}_{i:06d}.pkl"))
            if not n_parts:
                raise RuntimeError("nothing archived in the bucket")
            header = [f"Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run "
                      f"{run['run_id']} ({run['archived_at']}); that run's own header of the table follows"] + \
                run["header"].split("\n")
            n = 0
            with open(out, "w", encoding="utf-8", newline="") as fh:
                for h in header:
                    fh.write(f"# {h}\n")
                fh.write(pd.DataFrame(columns=cols).to_csv(index=False, lineterminator="\n"))
                for k in sorted({p.split("_")[0] for p in os.listdir(work)}):
                    lines = pd.concat([pd.read_pickle(os.path.join(work, p)) for p in sorted(os.listdir(work))
                                       if p.split("_")[0] == k], ignore_index=True).fillna("")
                    lines = lines.sort_values(["_archived_at", "_run_id", "_order"], kind="stable")
                    last = lines.drop_duplicates("_key_sha", keep="last")
                    rows = last[last["_op"] == "upsert"].reindex(columns=cols).fillna("")
                    rows.to_csv(fh, index=False, header=False, lineterminator="\n")
                    n += len(rows)
                    del lines, last, rows
            return n
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def from_archive(self, name, path, run):
        if run is None:
            raise RuntimeError("the archive has no run of this table")
        expected = int(run["table_rows"])

        def build(tmp):
            if R.members_of(name):  # session 29: a consolidated table, through the map, streamed member by member
                n, _ = R.rebuild_consolidated(name, tmp, None, True, self.bucket)
            else:
                n = self.replay_sliced(name, run, tmp)
            got[0] = n
            if n == expected:
                return
            if n > expected and any(re.match(p, name) for p in CONFIG.get("judge_by_newest") or []):
                # a table its builder rewrites whole as a moving window (price_board_spreads, session 206): the
                # rebuild also holds days that have left the window. The builder writes the table again from its
                # inputs and takes from the table held only ERCOT's rows (price_board.carry_history)
                self.log(f"  {name}: {n - expected:,} rows more than the latest run's {expected:,}: days that left "
                         "its moving window (judge_by_newest); its builder rebuilds the table from its inputs")
                return
            raise RuntimeError(f"rebuilt {n:,} rows, the latest run ({run['run_id']}) recorded {expected:,}")
        got = [None]
        write_atomic(path, build)
        return got[0]

    # ---- 4. Redivis, under the ceiling
    def exported_today(self):
        day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        total = 0
        for o in self.bucket.ls(f"_exports/{day}"):
            m = re.search(r"_(\d+)\.json$", o["name"])
            total += int(m.group(1)) if m else 0
        return day, total

    def record_export(self, name, nbytes):
        now = dt.datetime.now(dt.timezone.utc)
        host = re.sub(r"[^A-Za-z0-9-]", "-", "github" if os.environ.get("GITHUB_ACTIONS") == "true" else socket.gethostname())
        body = json.dumps({"table": name, "bytes": nbytes, "machine": host, "at": now.strftime("%Y-%m-%dT%H:%M:%SZ")})
        self.bucket.put(f"_exports/{now:%Y-%m-%d}/{now:%H%M%S}_{host}_{name}_{nbytes}.json", body.encode("utf-8"))

    def from_redivis(self, name, path):
        if not self.redivis:
            raise RuntimeError("Redivis is left out (--no-redivis)")
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
        import upload as up
        lic = up.licenses()
        ds = up.Drafts()(up.dataset_for(lic.get(name, "")))
        meta = up.table_meta(ds, name)
        if meta is None:
            raise RuntimeError("not in the Redivis draft either")
        nbytes = int(meta.get("numBytes") or 0) or int(1e9)  # a size Redivis does not give is counted as 1 GB
        day, done = self.exported_today()
        if done + nbytes > ceiling_bytes():
            raise RuntimeError(f"not asked of Redivis: {nbytes / 1e9:.2f} GB would bring {day}'s exports to "
                               f"{(done + nbytes) / 1e9:.2f} GB, over the ceiling of {ceiling_bytes() / 1e9:.1f} GB "
                               "(export_ceiling_gb_per_day, warehouse/redivis/config.yaml)")
        out_dir = tempfile.mkdtemp(prefix="erw-redivis-restore-")
        try:
            rc = up.restore(out_dir, only=[name])
            self.record_export(name, nbytes)
            got = os.path.join(out_dir, name + ".csv")
            if rc != 0 or not os.path.exists(got):
                raise RuntimeError("upload.py --restore failed for it (its lines above)")
            write_atomic(path, lambda tmp: shutil.copyfile(got, tmp))
        finally:
            shutil.rmtree(out_dir, ignore_errors=True)
        return None

    def restore(self, name, path=None):
        """(rows or None, source, None) when restored, or (None, None, every source's reason) when not."""
        path = path or os.path.join(OUT, name + ".csv")
        why = []
        try:
            run = self.latest(name)
        except Exception as exc:
            run = None
            why.append(f"the archive's run log could not be read: {type(exc).__name__}: {str(exc)[:160]}")
        for source, fn in (("GitHub's cache", lambda: self.from_cache(name, path, run)),
                           ("a copy in the archive bucket", lambda: self.from_copy(name, path, run)),
                           ("the archive", lambda: self.from_archive(name, path, run)),
                           ("Redivis", lambda: self.from_redivis(name, path))):
            if source == "GitHub's cache" and not self.cache:
                continue
            t0 = time.time()
            try:
                n = fn()
                if n is None and source in ("GitHub's cache", "a copy in the archive bucket"):
                    continue  # nothing there; not a failure of this source
                return n, source, f"{time.time() - t0:.0f} s"
            except Exception as exc:
                why.append(f"{source}: {type(exc).__name__}: {str(exc)[:300]}")
        return None, None, "; ".join(why)


def stash(names, into, log=log):
    """Copy each table whose data is the one this machine last archived (archive_manifest.csv) into the cache folder;
    remove any other copy there (it would not be taken)."""
    os.makedirs(into, exist_ok=True)
    man = A.read_manifest()
    kept = 0
    for name in names:
        src, dst = os.path.join(OUT, name + ".csv"), os.path.join(into, name + ".csv")
        if os.path.exists(src) and name in man.index and A.data_sha256(src) == man.loc[name, "data_sha256"]:
            shutil.copyfile(src, dst)
            kept += 1
        elif os.path.exists(dst):
            os.remove(dst)
            log(f"  {name}: not as last archived here; no copy kept for the cache")
    log(f"stash: {kept} of {len(names)} tables copied to {os.path.relpath(into, ROOT)} for GitHub's cache")
    return 0


def seed(names, src_dir=OUT, log=log):
    """An exact copy of each table into the bucket, named by its data SHA-256, when that is the latest run's (a person
    runs this, for a table the archive cannot rebuild row for row)."""
    s = Sources(redivis=False)
    bad = 0
    for name in names:
        src = os.path.join(src_dir, name + ".csv")
        run = s.latest(name)
        if not os.path.exists(src) or run is None:
            log(f"FAIL {name}: no local file or no archived run")
            bad += 1
            continue
        sha = A.data_sha256(src)
        if sha != run["data_sha256"]:
            log(f"FAIL {name}: this copy is not the latest run's ({run['run_id']}); nothing written")
            bad += 1
            continue
        key = f"_copies/{name}/{sha}.csv.gz"
        if s.bucket.get(key) is None:
            with open(src, "rb") as f:
                s.bucket.put(key, gzip.compress(f.read()))
        log(f"ok   {name}: {key} (run {run['run_id']}, {int(run['table_rows']):,} rows)")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Restore missing tables: the cache, the archive, Redivis last (session 305)")
    ap.add_argument("tables", nargs="*")
    ap.add_argument("--rolling", action="store_true", help="every rolling-window table (restore_before_run)")
    ap.add_argument("--cache", help="a folder of copies stashed by an earlier run (GitHub's cache)")
    ap.add_argument("--no-redivis", action="store_true", help="never ask Redivis")
    ap.add_argument("--check", action="store_true", help="say what is missing; write nothing")
    ap.add_argument("--stash", help="copy the tables as last archived here into this folder; restore nothing")
    ap.add_argument("--seed-bucket", action="store_true", help="put exact copies of the named tables into the bucket")
    ap.add_argument("--out-dir", help="restore into this folder, not warehouse/output (a trial)")
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out_dir) if a.out_dir else OUT
    names = sorted(set(a.tables) | (set(rolling_tables()) if a.rolling else set()))
    if not names:
        ap.error("name tables, or --rolling")
    if a.stash:
        return stash(names, os.path.abspath(a.stash))
    if a.seed_bucket:
        return seed(names)
    todo = [n for n in names if not os.path.exists(os.path.join(out, n + ".csv"))]
    log(f"restore: {len(names)} tables checked, {len(todo)} missing here"
        + (f": {', '.join(todo)}" if a.check and todo else ""))
    if a.check or not todo:
        return 0
    os.makedirs(out, exist_ok=True)
    src = Sources(cache=a.cache, redivis=not a.no_redivis)
    failed, by = [], {}
    for name in todo:
        n, source, note = src.restore(name, os.path.join(out, name + ".csv"))
        if source is None:
            failed.append(name)
            log(f"FAIL restore {name}: {note}")
            continue
        by[source] = by.get(source, 0) + 1
        log(f"restored {name}" + (f": {n:,} rows" if n is not None else "") + f", from {source} ({note})")
    log(f"restored {len(todo) - len(failed)} of {len(todo)} tables ("
        + ", ".join(f"{k}: {v}" for k, v in by.items()) + f"); {len(failed)} failed"
        + (f": {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
