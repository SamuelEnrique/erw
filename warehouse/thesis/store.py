#!/usr/bin/env python3
"""Where a niche's evidence store is kept (session 147). INTERNAL.

Energy Research Warehouse (ERW), Thesis Builder. The evidence store of a niche (tie.py, rule 6) was one JSON file on
the machine that ran the tool. The page's runs happen on a GitHub runner, whose files are discarded with it, so the
store did not outlive a run there. From session 147 the store is one object of a PRIVATE Supabase storage bucket:

    bucket   erw-thesis                                  (private; created once with the service key)
    object   evidence/<niche>__<geography>__<stage>.json.gz   the store, written whole and read whole (gzip of JSON)
    object   evidence/history/<niche>__<geography>__<stage>/<YYYYMMDDTHHMMSSZ>.json.gz
                                                         the object as it was, copied here before it is replaced

It is a bucket of its own, not a prefix of erw-archive: the archive is append-only and its scripts list and restore
everything under it. Credentials: SUPABASE_URL and SUPABASE_SERVICE_KEY from the environment or the repository's .env,
never printed. With no key (a test, a machine without it) the store is the local file, as before, and every run's
record says which store it used (the handle's "where").

The one network call is transport(), which a test replaces. Nothing here is public: the bucket is private and is
read only with the service key; the site's public key cannot read it.
"""

import datetime as dt
import gzip
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BUCKET = "erw-thesis"
PREFIX = "evidence"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "any").lower()).strip("-")[:50] or "any"


def head_of(niche):
    return re.split(r"[,:;(]", niche or "", maxsplit=1)[0].strip()


def store_name(niche, stage, geography):
    """The store's name: one a niche, geography and stage (the key the local file always had)."""
    return f"{slug(head_of(niche))}__{slug(geography)}__{slug(stage)}"


def empty(niche="", stage="", geography=""):
    return {"version": 2, "niche": niche, "stage": stage, "geography": geography, "runs": [], "sources": {}, "quotes": [],
            "rows": [], "pages": {}, "robots": {}, "last": None}


def upgrade(store):
    """A store written before session 147 held no pages: it gains the two empty parts and keeps everything else."""
    store.setdefault("pages", {})
    store.setdefault("robots", {})
    return store


def secret(name, env=None):
    """A credential from the environment, else from the repository's .env. Never printed."""
    env = os.environ if env is None else env
    v = (env.get(name) or "").strip()
    if v or env is not os.environ:
        return v
    try:
        from dotenv import dotenv_values
        return (dotenv_values(os.path.join(ROOT, ".env")).get(name) or "").strip()
    except ImportError:
        return ""


def transport(method, url, headers, body=None, timeout=60):
    """One call of the storage API. Returns (status, body bytes); an HTTP error status is returned, not raised."""
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


class FileStore:
    """The store as one local JSON file: the fallback when no key is set, and what the tests use."""

    kind = "file"

    def __init__(self, path):
        self.path = path
        self.where = path

    def load(self, niche="", stage="", geography=""):
        if self.path and os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as f:
                return upgrade(json.load(f))
        return empty(niche, stage, geography)

    def save(self, store):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=1, sort_keys=True, default=str)
        os.replace(tmp, self.path)
        return self.where


class BucketStore:
    """The store as one object of the private bucket. A save that the bucket refuses is written to the fallback file
    and said so: a run's evidence is never lost with the runner."""

    kind = "bucket"

    def __init__(self, base, key, name, bucket=BUCKET, send=None, fallback=None, log=None, now=None, sleep=time.sleep):
        u = urllib.parse.urlparse(base)
        self.base = f"{u.scheme}://{u.netloc}/storage/v1"          # SUPABASE_URL may end in /rest/v1/
        self.key, self.name, self.bucket = key, name, bucket
        self.send = send or transport
        self.fallback = fallback
        self.log = log or (lambda s: None)
        self.now = now or (lambda: dt.datetime.now(dt.timezone.utc))
        self.sleep = sleep
        self.reads = 0
        self.object = f"{PREFIX}/{name}.json.gz"
        self.where = f"supabase storage (private): {bucket}/{self.object}"
        self.calls = []                                             # (method, path, status): the record of every call, no key in it
        self.loaded = None                                          # the object's bytes as read, kept for the dated copy

    def _call(self, method, path, body=None, extra=None):
        headers = {"Authorization": f"Bearer {self.key}", "apikey": self.key}
        headers.update(extra or {})
        status, data = self.send(method, f"{self.base}/{path}", headers, body)
        self.calls.append((method, path, status))
        return status, data

    @staticmethod
    def _missing(status, data):
        return status == 404 or (status == 400 and b"not found" in (data or b"").lower()) or (status == 400 and b"not_found" in (data or b"").lower())

    def ensure_bucket(self):
        """The bucket exists and is private; created with one call when it is not there. Returns what was done."""
        status, data = self._call("GET", f"bucket/{self.bucket}")
        if status == 200:
            if json.loads(data.decode("utf-8")).get("public"):
                raise RuntimeError(f"storage bucket {self.bucket} is public; it must be private. Nothing is written")
            return "exists"
        if not self._missing(status, data):
            raise RuntimeError(f"storage bucket {self.bucket}: the storage API answered {status}")
        status, data = self._call("POST", "bucket", json.dumps({"id": self.bucket, "name": self.bucket, "public": False}).encode("utf-8"),
                                  {"Content-Type": "application/json"})
        if status not in (200, 201):
            raise RuntimeError(f"storage bucket {self.bucket} could not be created: the storage API answered {status}")
        self.log(f"  created the private storage bucket {self.bucket}")
        return "created"

    def _read(self):
        """The object as it is now. A read just after a write was answered with the version before it for a few
        seconds (probed on 7 October 2026: runs/session147/bucket_probe.out); a read with a query of its own was not,
        so every read carries one."""
        self.reads += 1
        return self._call("GET", f"object/{self.bucket}/{self.object}?v={self.now().strftime('%Y%m%dT%H%M%S%f')}-{self.reads}")

    def load(self, niche="", stage="", geography=""):
        status, data = self._read()
        if status == 200:
            self.loaded = data
            return upgrade(json.loads(gzip.decompress(data).decode("utf-8")))
        if self._missing(status, data):
            self.loaded = None
            return empty(niche, stage, geography)
        raise RuntimeError(f"evidence store {self.where}: the storage API answered {status} on read")

    def save(self, store):
        body = gzip.compress(json.dumps(store, sort_keys=True, default=str).encode("utf-8"), mtime=0)
        try:
            status, data = self._read()
            before = data if status == 200 else None
            if status != 200 and not self._missing(status, data):
                raise RuntimeError(f"the storage API answered {status} on read before the write")
            if before is not None and before != body:                # the object as it was, under a dated name, before it is replaced
                stamp = self.now().strftime("%Y%m%dT%H%M%SZ")
                kept = f"{PREFIX}/history/{self.name}/{stamp}.json.gz"
                status, data = self._call("POST", f"object/{self.bucket}/{kept}", before, {"Content-Type": "application/gzip", "x-upsert": "false"})
                if status not in (200, 201):
                    raise RuntimeError(f"the storage API answered {status} on the dated copy; the object is not replaced")
            status, data = self._call("POST", f"object/{self.bucket}/{self.object}", body, {"Content-Type": "application/gzip", "x-upsert": "true"})
            if status not in (200, 201):
                raise RuntimeError(f"the storage API answered {status} on write")
            for attempt in range(5):                                 # written whole, then read whole: the write is believed when it reads back
                status, data = self._read()
                if status == 200 and data == body:
                    return self.where
                self.sleep(2)
            raise RuntimeError(f"the object did not read back as written (last answer {status})")
        except Exception as exc:
            if not self.fallback:
                raise
            where = FileStore(self.fallback).save(store)
            self.log(f"  EVIDENCE STORE NOT WRITTEN TO THE BUCKET ({type(exc).__name__}: {str(exc)[:200]}); kept in the local file {where}")
            self.where = f"local file (the bucket refused the write): {where}"
            self.kind = "file"
            return self.where


def open_store(evidence_dir, niche, stage, geography, mode="auto", log=None, env=None, send=None):
    """The handle of a niche's store. mode: "bucket", "file", or "auto" (the bucket when both credentials are set, else
    the file). The file's path is also the bucket handle's fallback."""
    name = store_name(niche, stage, geography)
    path = os.path.join(evidence_dir, name + ".json") if evidence_dir else None
    if mode == "file":
        return FileStore(path)
    base, key = secret("SUPABASE_URL", env), secret("SUPABASE_SERVICE_KEY", env)
    if base and key:
        return BucketStore(base, key, name, send=send, fallback=path, log=log)
    if mode == "bucket":
        raise RuntimeError("the evidence store was asked to be the bucket, and SUPABASE_URL or SUPABASE_SERVICE_KEY is not set")
    return FileStore(path)


def handle_of(x):
    """A handle from what a caller passes: None (no store), a path (the local file), or a handle."""
    if x is None or hasattr(x, "load"):
        return x
    return FileStore(x)
