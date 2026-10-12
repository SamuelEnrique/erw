#!/usr/bin/env python3
"""One read of a publisher's terms, license or data-use page, written down (session 205, the licensing sweep).

Energy Research Warehouse (ERW). docs/licenses.md says, for every table, what its publisher's own page allows. This
script makes the reads behind it, one page a publisher, and keeps the record a reader can check:

    python scripts/license_read.py --list runs/s205/to_read.csv --ceiling 40
    python scripts/license_read.py --list ... --dry-run          # say what would be asked; ask nothing

--list is a CSV with the columns publisher,url. For each line, in order:

- a publisher already in the record is not asked again (one page each; a failed read is a read);
- a host that warehouse/metadata/paused_sources.csv pauses is never asked (iso_prices.paused_host): the line is
  written to the record as "not asked: paused", with no request;
- at the ceiling (the count of requests in the record) nothing more is asked;
- otherwise ONE request: a GET with the ERW's own User-Agent, redirects followed, no second try whatever the answer.

The record is warehouse/metadata/license_reads.csv (in git): publisher, the address asked, the address that answered,
the time (UTC), the HTTP status, the bytes, the sha256 of the bytes and the outcome. The bytes themselves are kept
under --keep (default runs/license_reads/, not in git), each read in a folder of its own: they are a publisher's
copyrighted page and are not republished. No data file is asked for: a page of terms only.
"""

import argparse
import csv
import datetime as dt
import hashlib
import os
import re
import sys
import urllib.parse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

RECORD = os.path.join(ROOT, "warehouse", "metadata", "license_reads.csv")
COLS = ["n", "publisher", "url", "final_url", "read_at", "http_status", "bytes", "sha256", "content_type", "outcome"]
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)",
      "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8"}
TIMEOUT = 60
MAX_BYTES = 20_000_000


def record(path=None):
    path = path or RECORD
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def add(row, path=None):
    path = path or RECORD
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)


def asked(rows):
    """The requests made so far: every line of the record but those that say no request was made."""
    return sum(1 for r in rows if not r["outcome"].startswith("not asked"))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:50]


def read_one(publisher, url, ceiling, keep, path=None, get=requests.get, now=None, log=print):
    """One line of the list. Returns the record's row, or None when nothing was written (already read, or the ceiling)."""
    rows = record(path)
    if any(r["publisher"] == publisher for r in rows):
        log(f"{publisher}: already in the record; not asked again")
        return None
    n = len(rows) + 1
    stamp = (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    host = urllib.parse.urlparse(url).hostname or ""
    base = dict(n=n, publisher=publisher, url=url, final_url="", read_at=stamp, http_status="", bytes="", sha256="", content_type="")
    if ip.paused_host(host):
        row = dict(base, outcome=f"not asked: paused ({host} is in warehouse/metadata/paused_sources.csv)")
        add(row, path)
        log(f"{publisher}: {host} is paused; no request")
        return row
    if asked(rows) >= ceiling:
        log(f"{publisher}: STOPPED at the ceiling of {ceiling} reads; not asked")
        return None
    try:
        r = get(url, headers=UA, timeout=TIMEOUT, allow_redirects=True)
        body = r.content[:MAX_BYTES]
        folder = os.path.join(keep, f"{n:02d}_{slug(publisher)}")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "page.bin"), "wb") as f:
            f.write(body)
        row = dict(base, final_url=r.url, http_status=r.status_code, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                   content_type=(r.headers.get("Content-Type") or "").split(";")[0].strip(),
                   outcome="read" if r.status_code == 200 and body else f"not read: HTTP {r.status_code}")
    except requests.RequestException as e:
        row = dict(base, outcome=f"not read: {type(e).__name__}")
    add(row, path)
    log(f"{n:02d} {publisher}: {row['outcome']} ({row['http_status']}, {row['bytes']} bytes) {row['final_url'] or url}")
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description="One read of a publisher's terms page, written down (session 205)")
    ap.add_argument("--list", required=True, help="a CSV: publisher,url")
    ap.add_argument("--ceiling", type=int, required=True, help="the most requests the record may hold")
    ap.add_argument("--keep", default=os.path.join(ROOT, "runs", "license_reads"), help="where the pages' bytes are kept (not in git)")
    ap.add_argument("--record", default=RECORD)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    with open(a.list, encoding="utf-8", newline="") as f:
        todo = list(csv.DictReader(f))
    for t in todo:
        if a.dry_run:
            host = urllib.parse.urlparse(t["url"]).hostname or ""
            print(f"{t['publisher']}: would ask {t['url']}" + (" (PAUSED: would not)" if ip.paused_host(host) else ""))
            continue
        read_one(t["publisher"].strip(), t["url"].strip(), a.ceiling, a.keep, a.record)
    print(f"requests in the record: {asked(record(a.record))} of {a.ceiling}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
