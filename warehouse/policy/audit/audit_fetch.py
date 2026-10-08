#!/usr/bin/env python3
"""Session 154: fetch the source document of each sampled policy action, by a plain request, and save it raw.

Energy Research Warehouse (ERW). A check of sources already held, not a new pull: no row enters any table from it.

For a Federal Register row: the public API record of the same document number (every field the Register holds for
it) and then the Register's plain text of the document (the record's raw_text_url). For a news release: the row's own
source_url. One request a second to a host; every response is saved under <out>/raw/ and listed in
<out>/manifest.csv with its status, bytes, sha256 and retrieval time. The run stops BEFORE a ceiling, not after.
A response that is not HTTP 200 is a result ("source not reachable"), recorded with its status and never retried
round a refusal.

The User-Agent is the connector's own (warehouse/connectors/policy_sources.py UA): it names the project and its
repository, and holds no person's address (asserted below).

    python warehouse/policy/audit/audit_fetch.py --sample <audit>/sample.csv --out <audit>
    python warehouse/policy/audit/audit_fetch.py --out <audit> --url KEY=https://...      # one more named document
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from urllib.parse import urlparse

import requests

UA = {"User-Agent": "Mozilla/5.0 (ERW energy research warehouse; https://github.com/SamuelEnrique/erw)"}
assert "@" not in UA["User-Agent"], "no person's address in a request header"
MAX_REQUESTS, MAX_BYTES = 200, 200 * 1024 * 1024
FORBIDDEN = ("misoenergy.org", "dataminer", "api.pjm.com")
FR_API = "https://www.federalregister.gov/api/v1/documents/{}.json"
MAN_COLS = ["n", "key", "kind", "url", "status", "bytes", "sha256", "content_type", "retrieved_at", "file", "error"]
# Session 157: the manifest status of a printed text copied from the connector's own store (it was requested once,
# by the connector), for which this tool makes no request. It counts toward neither ceiling's request count.
HELD = "held"


class Store:
    def __init__(self, out):
        self.out, self.raw = out, os.path.join(out, "raw")
        os.makedirs(self.raw, exist_ok=True)
        self.man = os.path.join(out, "manifest.csv")
        self.rows = []
        if os.path.exists(self.man):
            with open(self.man, encoding="utf-8") as f:
                self.rows = list(csv.DictReader(f))
        self.last = {}

    @property
    def requests(self):
        return sum(1 for r in self.rows if r["status"] != HELD)   # a text taken from the store is no request

    @property
    def bytes(self):
        return sum(int(r["bytes"] or 0) for r in self.rows if r["status"] != HELD)

    def have(self, key, kind):
        return next((r for r in self.rows if r["key"] == key and r["kind"] == kind and r["status"] in ("200", HELD)),
                    None)

    def save(self):
        with open(self.man, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=MAN_COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(self.rows)

    def take_held(self, key, kind, url, path, ext):
        """Session 157: the connector already holds this printed text (its store, by document number). The file is
        copied here and listed with status 'held' and its sha256, and no request is made."""
        with open(path, "rb") as f:
            content = f.read()
        name = re.sub(r"[^A-Za-z0-9_.-]+", "_", key) + f".{kind}.{ext}"
        with open(os.path.join(self.raw, name), "wb") as f:
            f.write(content)
        when = dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        row = dict(n=str(len(self.rows) + 1), key=key, kind=kind, url=url, status=HELD, bytes=str(len(content)),
                   sha256=hashlib.sha256(content).hexdigest(), content_type="", retrieved_at=when, file="raw/" + name,
                   error="held (the connector's store): " + path.replace(os.sep, "/") + "; no request made here")
        self.rows.append(row)
        self.save()
        print(f"  {row['n']:>3} {key} {kind}: held in the connector's store, {row['bytes']} bytes, no request")
        return row

    def tried(self, key, kind):
        return any(r["key"] == key and r["kind"] == kind for r in self.rows)

    def get(self, key, kind, url, ext):
        host = urlparse(url).netloc.lower()
        if any(f in url.lower() for f in FORBIDDEN):
            raise RuntimeError(f"forbidden host: {url}")
        if "@" in url or "%40" in url:
            raise RuntimeError(f"address holds an e-mail address: not requested: {url}")
        if self.requests + 1 > MAX_REQUESTS or self.bytes > MAX_BYTES - 20 * 1024 * 1024:
            raise RuntimeError(f"ceiling: {self.requests} requests, {self.bytes} bytes; stopping before the next")
        wait = 1.1 - (time.time() - self.last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        row = dict(n=str(len(self.rows) + 1), key=key, kind=kind, url=url, status="", bytes="0", sha256="",
                   content_type="", retrieved_at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   file="", error="")
        try:
            r = requests.get(url, headers=UA, timeout=90)
            self.last[host] = time.time()
            row.update(status=str(r.status_code), bytes=str(len(r.content)),
                       sha256=hashlib.sha256(r.content).hexdigest(), content_type=r.headers.get("content-type", ""))
            if r.url != url:
                row["error"] = f"redirected to {r.url}"
            name = re.sub(r"[^A-Za-z0-9_.-]+", "_", key) + f".{kind}.{ext}"
            if r.status_code != 200:
                name += f".http{r.status_code}"
            with open(os.path.join(self.raw, name), "wb") as f:
                f.write(r.content)
            row["file"] = "raw/" + name
        except Exception as exc:  # recorded, not retried
            self.last[host] = time.time()
            row.update(status="error", error=repr(exc)[:300])
        self.rows.append(row)
        self.save()
        print(f"  {row['n']:>3} {key} {kind}: {row['status']} {row['bytes']} bytes {row['error']}")
        return row


def ext_of(url):
    return "pdf" if url.lower().endswith(".pdf") else "html"


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy audit: fetch the sampled sources")
    ap.add_argument("--sample")
    ap.add_argument("--out", required=True)
    ap.add_argument("--url", action="append", default=[], help="KEY=URL: one more named document (kind 'extra')")
    ap.add_argument("--store", help="session 157: the connector's store of printed Federal Register texts, one file "
                                    "a document number (<number>.txt); a text held there is copied, not requested")
    args = ap.parse_args(argv)
    st = Store(args.out)
    if args.sample:
        with open(args.sample, encoding="utf-8") as f:
            sample = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
        for s in sample:
            key = s["event_id"]
            if key.startswith("federalregister:"):
                num = key.split(":", 1)[1]
                if not st.tried(key, "api"):
                    st.get(key, "api", FR_API.format(num), "json")
                rec = st.have(key, "api")
                if rec and not st.tried(key, "text"):
                    meta = json.load(open(os.path.join(args.out, rec["file"]), encoding="utf-8"))
                    held = os.path.join(args.store, num + ".txt") if args.store else ""
                    if meta.get("raw_text_url") and held and os.path.isfile(held) and os.path.getsize(held) > 0:
                        st.take_held(key, "text", meta["raw_text_url"], held, "txt")
                    elif meta.get("raw_text_url"):
                        st.get(key, "text", meta["raw_text_url"], "txt")
            elif not st.tried(key, "page"):
                st.get(key, "page", s["source_url"], ext_of(s["source_url"]))
    for item in args.url:
        key, url = item.split("=", 1)
        if not st.tried(key, "extra"):
            st.get(key, "extra", url, ext_of(url))
    ok = sum(1 for r in st.rows if r["status"] == "200")
    held = sum(1 for r in st.rows if r["status"] == HELD)
    print(f"{st.requests} requests of {MAX_REQUESTS}, {st.bytes} bytes of {MAX_BYTES}; {ok} answered 200"
          + (f"; {held} printed texts taken from the connector's store, no request" if held else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
