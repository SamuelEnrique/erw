#!/usr/bin/env python3
"""Hand the raw source files of one machine to another through the archive bucket (session 187).

Energy Research Warehouse (ERW). The raw files (warehouse/raw, not in git) lived only on the machine that downloaded
them. When the data role moves to a machine that cannot reach the old one, this script carries them through the one
store both can reach: the private Supabase storage bucket erw-archive, under the prefix _handover/<session>/.

    python scripts/raw_handover.py plan                  # walk warehouse/raw, cut it into parts (no network)
    python scripts/raw_handover.py upload --minutes 80   # pack and upload the parts not yet uploaded (resumes)
    python scripts/raw_handover.py handover              # write runs/session187/handover.json from the plan and the state
    python scripts/raw_handover.py fetch                 # on the receiving machine: download, check, unpack
    python scripts/raw_handover.py fetch --folders ercot_zone_prices,zone_price_history
    python scripts/raw_handover.py verify                # every file of the manifest against the files on this machine

What is stored. Each top folder of warehouse/raw is cut into parts of at most 40 MiB before compression, because the
bucket refuses an object over 50 MB (archive.py, session 34). A part is one of two kinds:
- tar: whole files, as a tar archive (PAX), gzip-compressed when its files compress (csv, txt, html, json and the like),
  stored as it is when they are compressed already (zip, gz, pdf, xlsx). Object <folder>/<folder>.<NNNN>.tar.gz or .tar.
- chunk: a slice of one file too large for a part, in order. Object <folder>/<folder>.<NNNN>.chunk.gz or .chunk.
Every object is written once (x-upsert false): an object already there with the same size is taken as uploaded, one
with another size is an error. Nothing on the sending machine is deleted, moved or changed.

Names. The archive's own scripts list the bucket: pull and status walk every top-level name except _state, restore
--all skips names that begin with an underscore, and all of them read only objects that end in .csv.gz at the third
level. Nothing here ends in .csv.gz, and the parts sit at the fourth level and below, so those scripts see three
folder names and read nothing.

The manifest. One line per file: path under warehouse/raw, bytes, SHA-256, modification time (UTC) and the objects
that hold it. It is uploaded beside the parts (a .csv.gzip object) and named, with its own SHA-256, in handover.json,
which also lists every part: object, bytes, SHA-256 and what it holds. handover.json is the index the receiving
machine reads; it is in git (runs/session187/handover.json, added with -f).

The receiving machine. fetch downloads each part, checks its SHA-256, and writes each file under warehouse/raw. A
file already there with the same bytes is left; one there with other bytes is never overwritten: it is listed in
runs/session187/fetch_conflicts.csv and the fetched copy is not written. fetch resumes. Neither side takes the data
lock: warehouse/raw is not a warehouse table, and no object of the archive proper is touched.

Credentials: SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment), never printed.
"""

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import sys
import tarfile
import threading
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RAW = os.path.join(ROOT, "warehouse", "raw")
SESSION = "187"
WORK = os.path.join(ROOT, "runs", f"session{SESSION}")
BUCKET = "erw-archive"
PREFIX = f"_handover/{SESSION}"
CAP = 40 * 1024 * 1024            # a part's bytes before compression
OBJECT_MAX = 48 * 1024 * 1024     # the bucket refuses an object over 50 MB
FIRST = ["ercot_zone_prices", "zone_price_history"]   # the session's order: these two, then the smallest folder first
# Not handed over: a test's made-up folder (tests/test_session85.py writes it; rule 1, real data only) and Python's caches.
EXCLUDE_FOLDERS = {"madeup_as_prices": "written by tests/test_session85.py with made-up documents; not a source"}
EXCLUDE_DIRS = {"__pycache__": "Python's cache of compiled scripts; rebuilt on its own"}
PACKED = {".zip", ".gz", ".pdf", ".xlsx", ".xls", ".png", ".jpg", ".jpeg", ".7z", ".docx", ".pptx", ".npz", ".parquet",
          ".bz2", ".xz", ".tgz", ".kmz", ".gif", ".webp"}
MANIFEST_COLS = ["path", "bytes", "sha256", "mtime_utc", "folder", "objects"]


def log(msg):
    print(msg, flush=True)


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def stamp(t=None):
    return (t or now_utc()).strftime("%Y%m%dT%H%M%SZ")


def lp(path):
    """A path Windows opens whatever its length."""
    path = os.path.abspath(path)
    if os.name == "nt" and not path.startswith("\\\\"):
        return "\\\\?\\" + path
    return path


def sha256_of(data):
    return hashlib.sha256(data).hexdigest()


def tar_cost(rel, size):
    """The bytes a file takes in a PAX tar: its header, its data padded to 512, and a long name's extra header."""
    extra = 1536 if len(rel.encode("utf-8")) > 100 or not rel.isascii() else 0
    return 512 + extra + -(-size // 512) * 512


# ---------------------------------------------------------------- the store

class Bucket:
    """The private bucket, by the storage API. put never replaces an object."""

    def __init__(self, bucket=BUCKET, session=None):
        import requests
        env = {}
        try:
            from dotenv import dotenv_values
            env = dotenv_values(os.path.join(ROOT, ".env"))
        except ImportError:
            pass

        def secret(name):
            v = (os.environ.get(name) or env.get(name) or "").strip()
            if not v:
                raise SystemExit(f"{name} is not set (.env or environment); nothing sent")
            return v

        u = urllib.parse.urlparse(secret("SUPABASE_URL"))        # may end in /rest/v1/
        self.base = f"{u.scheme}://{u.netloc}/storage/v1"
        key = secret("SUPABASE_SERVICE_KEY")
        self.h = {"Authorization": f"Bearer {key}", "apikey": key}
        self.bucket = bucket
        self._session, self._local = session, threading.local()
        self.where = f"supabase storage (private): {bucket}"

    @property
    def s(self):
        """One connection pool per thread."""
        if self._session is not None:
            return self._session
        if not hasattr(self._local, "s"):
            import requests
            self._local.s = requests.Session()
        return self._local.s

    def check_private(self):
        r = self.s.get(f"{self.base}/bucket/{self.bucket}", headers=self.h, timeout=60)
        if r.status_code != 200:
            raise SystemExit(f"storage bucket {self.bucket}: the storage API answered {r.status_code}; nothing sent")
        if r.json().get("public"):
            raise SystemExit(f"storage bucket {self.bucket} is public; it must be private. Nothing sent")

    def size(self, obj):
        """The object's bytes, or None when it is not there."""
        folder, name = obj.rsplit("/", 1)
        r = self.s.post(f"{self.base}/object/list/{self.bucket}", headers=self.h, timeout=60,
                        json={"prefix": folder, "limit": 100, "offset": 0, "search": name})
        r.raise_for_status()
        for o in r.json():
            if o.get("name") == name and o.get("id") is not None:
                return int((o.get("metadata") or {}).get("size") or 0)
        return None

    def put(self, obj, data):
        """'created', or 'exists' when an object of the same size is already there. Anything else raises."""
        import requests
        last = None
        for attempt in range(6):
            try:
                r = self.s.post(f"{self.base}/object/{self.bucket}/{obj}", data=data, timeout=600,
                                headers=dict(self.h, **{"x-upsert": "false", "Content-Type": "application/octet-stream"}))
            except requests.RequestException as exc:
                last = f"{type(exc).__name__}"
                time.sleep(min(60, 5 * 2 ** attempt))
                # the request may have landed before the connection dropped
                try:
                    if self.size(obj) == len(data):
                        return "exists"
                except requests.RequestException:
                    pass
                continue
            if r.status_code in (200, 201):
                return "created"
            body = r.text[:300]
            if r.status_code in (400, 409) and ("exist" in body.lower() or "duplicate" in body.lower()):
                held = self.size(obj)
                if held == len(data):
                    return "exists"
                raise RuntimeError(f"{obj}: an object of {held} bytes is already there, this one is {len(data)}; "
                                   "nothing replaced")
            if r.status_code in (408, 425, 429) or r.status_code >= 500:
                last = f"HTTP {r.status_code} {body}"
                time.sleep(min(60, 5 * 2 ** attempt))
                continue
            raise RuntimeError(f"{obj}: the storage API answered {r.status_code} {body}")
        raise RuntimeError(f"{obj}: not uploaded after 6 tries ({last})")

    def get(self, obj):
        import requests
        last = None
        for attempt in range(6):
            try:
                r = self.s.get(f"{self.base}/object/{self.bucket}/{obj}", headers=self.h, timeout=600)
            except requests.RequestException as exc:
                last = type(exc).__name__
                time.sleep(min(60, 5 * 2 ** attempt))
                continue
            if r.status_code == 200:
                return r.content
            if r.status_code in (408, 425, 429) or r.status_code >= 500:
                last = f"HTTP {r.status_code}"
                time.sleep(min(60, 5 * 2 ** attempt))
                continue
            raise RuntimeError(f"{obj}: the storage API answered {r.status_code} {r.text[:200]}")
        raise RuntimeError(f"{obj}: not downloaded after 6 tries ({last})")


class DictStore:
    """A store in memory, for the tests: the same three calls."""

    def __init__(self):
        self.objects = {}
        self.where = "memory"

    def check_private(self):
        pass

    def size(self, obj):
        return len(self.objects[obj]) if obj in self.objects else None

    def put(self, obj, data):
        if obj in self.objects:
            if len(self.objects[obj]) == len(data):
                return "exists"
            raise RuntimeError(f"{obj}: an object of another size is already there; nothing replaced")
        self.objects[obj] = bytes(data)
        return "created"

    def get(self, obj):
        return self.objects[obj]


# ---------------------------------------------------------------- the plan

def walk(raw):
    """{top folder: [(path under raw with forward slashes, bytes)]}, files in name order, and what was left out."""
    folders, left_out = {}, []
    for top in sorted(os.listdir(raw)):
        full = os.path.join(raw, top)
        if top in EXCLUDE_FOLDERS:
            n = sum(len(fs) for _, _, fs in os.walk(lp(full)))
            left_out.append({"path": top, "files": n, "why": EXCLUDE_FOLDERS[top]})
            continue
        if os.path.isfile(full):
            folders.setdefault("_root", []).append((top, os.path.getsize(full)))
            continue
        files = []
        for d, dirs, fs in os.walk(lp(full)):
            for x in [x for x in dirs if x in EXCLUDE_DIRS]:
                rel = os.path.relpath(os.path.join(d, x), lp(raw)).replace(os.sep, "/")
                left_out.append({"path": rel, "files": sum(len(f) for _, _, f in os.walk(os.path.join(d, x))),
                                 "why": EXCLUDE_DIRS[x]})
                dirs.remove(x)
            for f in fs:
                p = os.path.join(d, f)
                files.append((os.path.relpath(p, lp(raw)).replace(os.sep, "/"), os.path.getsize(p)))
        folders[top] = sorted(files)
    return folders, left_out


def packed_share(files):
    tot = sum(s for _, s in files) or 1
    return sum(s for p, s in files if os.path.splitext(p)[1].lower() in PACKED) / tot


def cut(folder, files, cap=CAP):
    """The parts of one folder: tar parts of whole files, and chunk parts for a file larger than a part."""
    parts, cur, cur_cost = [], [], 0

    def close():
        nonlocal cur, cur_cost
        if cur:
            parts.append({"kind": "tar", "files": cur, "gz": packed_share(cur) < 0.5})
            cur, cur_cost = [], 0

    for rel, size in files:
        cost = tar_cost(rel, size)
        if cost + 1024 > cap:
            close()
            n = -(-size // cap)
            gz = os.path.splitext(rel)[1].lower() not in PACKED
            for i in range(n):
                parts.append({"kind": "chunk", "path": rel, "file_bytes": size, "index": i + 1, "of": n,
                              "offset": i * cap, "length": min(cap, size - i * cap), "gz": gz})
            continue
        if cur_cost + cost + 1024 > cap:
            close()
        cur.append([rel, size])
        cur_cost += cost
    close()
    for i, p in enumerate(parts, 1):
        ext = {"tar": ".tar", "chunk": ".chunk"}[p["kind"]] + (".gz" if p["gz"] else "")
        p["folder"] = folder
        p["id"] = f"{folder}/{i:04d}"
        p["object"] = f"{PREFIX}/raw/{folder}/{folder}.{i:04d}{ext}"
    return parts


def make_plan(raw=RAW, cap=CAP):
    folders, left_out = walk(raw)
    size = {k: sum(s for _, s in v) for k, v in folders.items()}
    order = [f for f in FIRST if f in folders] + sorted((f for f in folders if f not in FIRST), key=lambda f: (size[f], f))
    plan = {"made_at": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"), "raw": "warehouse/raw", "cap": cap, "prefix": PREFIX,
            "left_out": left_out, "folders": [], "parts": []}
    for f in order:
        parts = cut(f, folders[f], cap)
        plan["folders"].append({"folder": f, "files": len(folders[f]), "bytes": size[f], "parts": len(parts)})
        plan["parts"] += parts
    return plan


# ---------------------------------------------------------------- packing

def pack(part, raw=RAW):
    """(the object's bytes, the record of what it holds). Reads the files; changes nothing."""
    if part["kind"] == "chunk":
        with open(lp(os.path.join(raw, part["path"])), "rb") as f:
            f.seek(part["offset"])
            data = f.read(part["length"])
        if len(data) != part["length"]:
            raise RuntimeError(f"{part['path']}: {len(data)} bytes read at {part['offset']}, {part['length']} planned; "
                               "the file changed since the plan")
        rec = {"path": part["path"], "index": part["index"], "of": part["of"], "offset": part["offset"],
               "length": part["length"], "chunk_sha256": sha256_of(data)}
        if part["index"] == part["of"]:      # the whole file's hash and time travel with its last chunk
            h = hashlib.sha256()
            with open(lp(os.path.join(raw, part["path"])), "rb") as f:
                for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
                    h.update(block)
            st = os.stat(lp(os.path.join(raw, part["path"])))
            rec.update(file_sha256=h.hexdigest(), file_bytes=st.st_size, mtime=int(st.st_mtime))
        body = gzip.compress(data, compresslevel=6, mtime=0) if part["gz"] else data
        return body, rec
    buf, files = io.BytesIO(), []
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for rel, size in part["files"]:
            p = lp(os.path.join(raw, rel))
            with open(p, "rb") as f:
                data = f.read()
            ti = tarfile.TarInfo(rel)
            ti.size, ti.mtime, ti.mode = len(data), int(os.stat(p).st_mtime), 0o644
            tar.addfile(ti, io.BytesIO(data))
            files.append([rel, len(data), sha256_of(data), ti.mtime])
    body = buf.getvalue()
    if part["gz"]:
        body = gzip.compress(body, compresslevel=6, mtime=0)
    return body, {"files": files}


def read_state(path):
    done = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    done[r["id"]] = r
    return done


def upload(store, plan, state_path, raw=RAW, minutes=None, workers=4, only=None):
    """Pack and upload, in the plan's order, every part the state does not hold. Returns (uploaded, failed, left)."""
    done = read_state(state_path)
    todo = [p for p in plan["parts"] if p["id"] not in done and (not only or p["folder"] in only)]
    log(f"upload: {len(plan['parts']):,} parts planned, {len(done):,} done, {len(todo):,} to do, to {store.where}")
    t0, sent, n_ok, failed = time.time(), 0, 0, []

    def one(part):
        body, rec = pack(part, raw)
        if len(body) > OBJECT_MAX:
            raise RuntimeError(f"{part['object']}: {len(body):,} bytes, over the bucket's limit")
        how = store.put(part["object"], body)
        return dict(rec, id=part["id"], folder=part["folder"], kind=part["kind"], gz=part["gz"], object=part["object"],
                    bytes=len(body), sha256=sha256_of(body), put=how, at=now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"))

    it = iter(todo)
    with cf.ThreadPoolExecutor(max_workers=workers) as pool, open(state_path, "a", encoding="utf-8") as out:
        live = {}
        while True:
            while len(live) < workers * 2 and (minutes is None or time.time() - t0 < minutes * 60) and len(failed) < 10:
                part = next(it, None)
                if part is None:
                    break
                live[pool.submit(one, part)] = part
            if not live:
                break
            for fut in cf.wait(live, return_when=cf.FIRST_COMPLETED)[0]:
                part = live.pop(fut)
                try:
                    r = fut.result()
                except Exception as exc:  # one part's failure is recorded; the others go on
                    failed.append(part["id"])
                    log(f"FAILED {part['id']}: {type(exc).__name__}: {str(exc)[:300]}")
                    continue
                out.write(json.dumps(r) + "\n")
                out.flush()
                n_ok += 1
                sent += r["bytes"]
                if n_ok % 20 == 0:
                    el = time.time() - t0
                    log(f"  {n_ok:,} parts, {sent / 1e6:,.0f} MB sent in {el / 60:.1f} min ({sent * 8 / 1e6 / el:.1f} Mbit/s); "
                        f"at {part['id']}")
    left = len(todo) - n_ok - len(failed)
    log(f"upload: {n_ok:,} parts uploaded ({sent / 1e6:,.0f} MB), {len(failed)} failed, {left:,} not started, "
        f"{(time.time() - t0) / 60:.1f} min")
    return n_ok, failed, left


# ---------------------------------------------------------------- the manifest and handover.json

def manifest_rows(plan, done):
    """One row per file whose every part is uploaded: path, bytes, sha256, mtime_utc, folder, objects."""
    rows, chunks = [], {}
    for p in plan["parts"]:
        r = done.get(p["id"])
        if p["kind"] == "chunk":
            chunks.setdefault(p["path"], []).append((p, r))
            continue
        if r:
            for rel, size, sha, mtime in r["files"]:
                rows.append([rel, size, sha, iso(mtime), p["folder"], r["object"]])
    for path, got in chunks.items():
        if all(r for _, r in got):
            last = got[-1][1]
            rows.append([path, last["file_bytes"], last["file_sha256"], iso(last["mtime"]), got[0][0]["folder"],
                         ";".join(r["object"] for _, r in got)])
    return sorted(rows)


def iso(mtime):
    return dt.datetime.fromtimestamp(mtime, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def manifest_bytes(rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(MANIFEST_COLS)
    w.writerows(rows)
    return gzip.compress(buf.getvalue().encode("utf-8"), mtime=0)


def write_handover(store, plan, state_path, out_path, archive_note=None, machine=None):
    """Upload the manifest of the files uploaded so far and write handover.json, the index of every part."""
    done = read_state(state_path)
    rows = manifest_rows(plan, done)
    body = manifest_bytes(rows)
    obj = f"{PREFIX}/manifest/raw_files_{stamp()}.csv.gzip"
    store.put(obj, body)
    folders = []
    for f in plan["folders"]:
        parts = [p for p in plan["parts"] if p["folder"] == f["folder"]]
        up = [done[p["id"]] for p in parts if p["id"] in done]
        folders.append({
            "folder": f["folder"], "files": f["files"], "bytes": f["bytes"], "parts_planned": len(parts),
            "parts_uploaded": len(up), "bytes_uploaded": sum(r["bytes"] for r in up), "complete": len(up) == len(parts),
            "parts": [dict({"object": r["object"], "bytes": r["bytes"], "sha256": r["sha256"], "kind": r["kind"], "gz": r["gz"]},
                           **({"files": len(r["files"])} if r["kind"] == "tar" else
                              {k: r[k] for k in ("path", "index", "of", "length", "file_sha256", "file_bytes", "mtime")
                               if k in r}))
                      for r in up]})
    complete = all(f["complete"] for f in folders)
    h = {
        "session": int(SESSION),
        "written_at": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "from_machine": machine or machine_name(),
        "what": "the raw source files of warehouse/raw, handed to the data machine through the archive bucket",
        "store": {"kind": "Supabase storage, private bucket (the archive's)", "bucket": BUCKET, "prefix": PREFIX,
                  "read_with": "SUPABASE_URL and SUPABASE_SERVICE_KEY from .env",
                  "object_url": "<SUPABASE_URL host>/storage/v1/object/" + BUCKET + "/<object>"},
        "complete": complete,
        "raw": {
            "root": "warehouse/raw",
            "plan_made_at": plan["made_at"],
            "files_planned": sum(f["files"] for f in plan["folders"]),
            "bytes_planned": sum(f["bytes"] for f in plan["folders"]),
            "files_uploaded": len(rows),
            "bytes_uploaded_files": sum(r[1] for r in rows),
            "parts_planned": len(plan["parts"]),
            "parts_uploaded": len(done),
            "object_bytes_uploaded": sum(r["bytes"] for r in done.values()),
            "part_format": {"tar": "a PAX tar of whole files, names relative to warehouse/raw; .tar.gz is gzip of it",
                            "chunk": "a slice of one file, in index order; .chunk.gz is gzip of the slice"},
            "manifest": {"object": obj, "bytes": len(body), "sha256": sha256_of(body), "format": "gzip of a CSV",
                         "columns": MANIFEST_COLS, "rows": len(rows)},
            "left_out": plan["left_out"],
            "folders": folders,
        },
        "archive": archive_note or {},
        "on_the_data_machine": [
            "git fetch origin && git checkout wip/187-raw-handover   (or main, once it is merged)",
            "python scripts/raw_handover.py fetch --folders ercot_zone_prices     # first, about 220 MB",
            "python scripts/raw_handover.py fetch                                 # everything uploaded; resumes",
            "python scripts/raw_handover.py verify                                # every file against the manifest",
        ],
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(h, f, indent=1)
        f.write("\n")
    log(f"handover: {len(done):,} of {len(plan['parts']):,} parts, {len(rows):,} files in the manifest ({obj}); "
        f"complete: {complete}; written {os.path.relpath(out_path, ROOT)}")
    return h


def machine_name():
    try:
        return json.load(open(os.path.join(ROOT, ".erw", "machine.json"), encoding="utf-8")).get("name") or "unknown"
    except (OSError, ValueError):
        return "unknown"


# ---------------------------------------------------------------- the receiving machine

def safe_target(dest, rel):
    if rel.startswith("/") or ":" in rel.split("/")[0] or ".." in rel.split("/"):
        raise RuntimeError(f"refused a path that leaves the folder: {rel}")
    return lp(os.path.join(dest, *rel.split("/")))


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def place(target, data, mtime, conflicts, rel):
    """Write a fetched file unless one is already there: the same bytes are left, other bytes are a conflict."""
    if os.path.exists(target):
        if os.path.getsize(target) == len(data) and file_sha256(target) == sha256_of(data):
            return "same"
        conflicts.append([rel, os.path.getsize(target), len(data)])
        return "conflict"
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = target + ".handover-tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    if mtime:
        os.utime(tmp, (mtime, mtime))
    os.replace(tmp, target)
    return "written"


def fetch(store, handover, dest=RAW, state_path=None, folders=None, conflicts_path=None):
    """Download every part handover.json lists, check it, and write its files under dest. Returns counts."""
    state_path = state_path or os.path.join(WORK, "fetch_state.jsonl")
    conflicts_path = conflicts_path or os.path.join(WORK, "fetch_conflicts.csv")
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    got = set()
    if os.path.exists(state_path):
        got = {json.loads(x)["object"] for x in open(state_path, encoding="utf-8") if x.strip()}
    n = {"parts": 0, "written": 0, "same": 0, "conflict": 0, "skipped_parts": 0, "bad_parts": 0}
    conflicts = []
    with open(state_path, "a", encoding="utf-8") as out:
        for f in handover["raw"]["folders"]:
            if folders and f["folder"] not in folders:
                continue
            chunk_objects = {(q["path"], q["index"]): q["object"] for q in f["parts"] if q["kind"] == "chunk"}
            for p in f["parts"]:
                if p["object"] in got:
                    n["skipped_parts"] += 1
                    continue
                if p["kind"] == "chunk":   # a slice fetched by an earlier, interrupted run is kept
                    piece = safe_target(dest, p["path"]) + f".handover-part{p['index']:04d}"
                    if os.path.exists(piece) and os.path.getsize(piece) == p["length"] and p["index"] != p["of"]:
                        n["skipped_parts"] += 1
                        continue
                body = store.get(p["object"])
                if sha256_of(body) != p["sha256"]:
                    n["bad_parts"] += 1
                    log(f"BAD {p['object']}: its SHA-256 is not the one in handover.json; nothing written from it")
                    continue
                data = gzip.decompress(body) if p["gz"] else body
                if p["kind"] == "tar":
                    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as tar:
                        for ti in tar:
                            if not ti.isfile():
                                continue
                            how = place(safe_target(dest, ti.name), tar.extractfile(ti).read(), ti.mtime, conflicts, ti.name)
                            n[how] += 1
                    out.write(json.dumps({"object": p["object"]}) + "\n")
                else:
                    part_file = safe_target(dest, p["path"]) + f".handover-part{p['index']:04d}"
                    os.makedirs(os.path.dirname(part_file), exist_ok=True)
                    with open(part_file, "wb") as w:
                        w.write(data)
                    have = {i: safe_target(dest, p["path"]) + f".handover-part{i:04d}" for i in range(1, p["of"] + 1)}
                    if all(os.path.exists(x) for x in have.values()):
                        target = safe_target(dest, p["path"])
                        h = hashlib.sha256()
                        for i in sorted(have):
                            with open(have[i], "rb") as r:
                                h.update(r.read())
                        whole = h.hexdigest()
                        if p.get("file_sha256") and whole != p["file_sha256"]:
                            n["bad_parts"] += 1
                            log(f"BAD {p['path']}: its slices do not add up to the file's SHA-256; nothing written")
                            for x in have.values():
                                os.remove(x)    # fetched again by the next run
                            continue
                        if os.path.exists(target):
                            if file_sha256(target) == whole:
                                n["same"] += 1
                            else:
                                conflicts.append([p["path"], os.path.getsize(target), sum(os.path.getsize(x) for x in have.values())])
                                n["conflict"] += 1
                        else:
                            with open(target + ".handover-tmp", "wb") as w:
                                for i in sorted(have):
                                    with open(have[i], "rb") as r:
                                        w.write(r.read())
                            if p.get("mtime"):
                                os.utime(target + ".handover-tmp", (p["mtime"], p["mtime"]))
                            os.replace(target + ".handover-tmp", target)
                            n["written"] += 1
                        for x in have.values():
                            os.remove(x)        # the fetch's own pieces, never a source file
                        for i in range(1, p["of"] + 1):
                            out.write(json.dumps({"object": chunk_objects[(p["path"], i)]}) + "\n")
                out.flush()
                n["parts"] += 1
                if n["parts"] % 20 == 0:
                    log(f"  {n['parts']:,} parts fetched; at {p['object']}")
    if conflicts:
        new = not os.path.exists(conflicts_path)
        with open(conflicts_path, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            if new:
                w.writerow(["path", "bytes_here", "bytes_fetched"])
            w.writerows(conflicts)
    log(f"fetch: {n['parts']:,} parts read ({n['skipped_parts']:,} already done, {n['bad_parts']} bad); files written "
        f"{n['written']:,}, already here and the same {n['same']:,}, already here and different (kept, not overwritten) "
        f"{n['conflict']:,}")
    return n


def verify(store, handover, dest=RAW, folders=None):
    """Every file of the manifest against dest: (same, missing, different)."""
    m = handover["raw"]["manifest"]
    body = store.get(m["object"])
    if sha256_of(body) != m["sha256"]:
        raise SystemExit(f"{m['object']}: its SHA-256 is not the one in handover.json")
    same, missing, different = 0, [], []
    for row in csv.DictReader(io.StringIO(gzip.decompress(body).decode("utf-8"))):
        if folders and row["folder"] not in folders:
            continue
        t = safe_target(dest, row["path"])
        if not os.path.exists(t):
            missing.append(row["path"])
        elif os.path.getsize(t) != int(row["bytes"]) or file_sha256(t) != row["sha256"]:
            different.append(row["path"])
        else:
            same += 1
    log(f"verify: {same:,} files the same as the manifest, {len(missing):,} missing, {len(different):,} different")
    for p in (missing + different)[:20]:
        log(f"   {'missing' if p in missing else 'different'}: {p}")
    return same, missing, different


# ---------------------------------------------------------------- command line

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["plan", "upload", "handover", "fetch", "verify"])
    ap.add_argument("--minutes", type=float, help="upload: start no new part after this many minutes")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--folders", help="comma-separated top folders (upload, fetch, verify)")
    ap.add_argument("--dest", default=RAW, help="fetch, verify: where the files go (default warehouse/raw)")
    ap.add_argument("--archive-note", help="handover: a JSON file whose content goes under 'archive'")
    ap.add_argument("--handover", help="fetch, verify: the handover.json to read (default runs/session187/handover.json)")
    ap.add_argument("--state", help="fetch: where the fetch keeps its place (default runs/session187/fetch_state.jsonl)")
    args = ap.parse_args(argv)
    only = set(args.folders.split(",")) if args.folders else None
    plan_path = os.path.join(WORK, "plan.json")
    state_path = os.path.join(WORK, "upload_state.jsonl")
    hand_path = os.path.join(WORK, "handover.json")
    os.makedirs(WORK, exist_ok=True)

    if args.command == "plan":
        if os.path.exists(plan_path):
            log(f"{os.path.relpath(plan_path, ROOT)} exists; kept (the uploaded parts follow it)")
            plan = json.load(open(plan_path, encoding="utf-8"))
        else:
            plan = make_plan()
            json.dump(plan, open(plan_path, "w", encoding="utf-8"))
        tot = sum(f["bytes"] for f in plan["folders"])
        log(f"plan: {len(plan['folders'])} folders, {sum(f['files'] for f in plan['folders']):,} files, {tot / 1e9:.2f} GB, "
            f"{len(plan['parts']):,} parts; left out: {[(x['path'], x['files']) for x in plan['left_out']]}")
        return 0
    if args.command in ("upload", "handover"):
        plan = json.load(open(plan_path, encoding="utf-8"))
        store = Bucket()
        store.check_private()
        if args.command == "upload":
            ok, failed, left = upload(store, plan, state_path, minutes=args.minutes, workers=args.workers, only=only)
            return 1 if failed else 0
        note = json.load(open(args.archive_note, encoding="utf-8")) if args.archive_note else None
        write_handover(store, plan, state_path, hand_path, archive_note=note)
        return 0
    handover = json.load(open(args.handover or hand_path, encoding="utf-8"))
    store = Bucket()
    store.check_private()
    if args.command == "fetch":
        n = fetch(store, handover, dest=args.dest, folders=only, state_path=args.state,
                  conflicts_path=(os.path.splitext(args.state)[0] + "_conflicts.csv") if args.state else None)
        return 1 if n["bad_parts"] else 0
    same, missing, different = verify(store, handover, dest=args.dest, folders=only)
    return 1 if missing or different else 0


if __name__ == "__main__":
    sys.exit(main())
