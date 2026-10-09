#!/usr/bin/env python3
"""The filings' own PDFs for the Ohio and Illinois rows of the large-load rules (session 164): the fetcher.

Energy Research Warehouse (ERW). Session 154 could cut Ohio's rows only from the commission's docket cards and
Illinois's from its minutes, agendas and a list. This script asks, by one plain request each, for the public PDF of
a filing those dockets name, and saves it as pass D beside the other passes (warehouse/raw/large_load_rules/D, not
in git): the file as downloaded, its text by page (pdftotext -layout, pages split by a form feed), and one line in
requests.csv with the address, the status, the bytes, the hash and the time.

What it will not do, by its own code:
    - ask a host for anything before that host's robots.txt is saved (the one request it may make first), or for an
      address the saved robots.txt disallows for this script's name or for every robot;
    - ask for an address on misoenergy.org, on PJM's Data Miner or API, or one that holds an e-mail address;
    - ask for more than 400 documents, 600 requests or 1 GB in all (the stop is before the request);
    - ask a host more often than once in two seconds;
    - get past anything: an answer that is a CAPTCHA, a robot check or a login is saved as it came, marked, and
      never read as a document. A PDF is taken only when the answer's first bytes are a PDF's.
The User-Agent is exactly the ruled contact string. No address of a person is sent.

    python warehouse/connectors/large_load_filings.py --raw-root RAW get FOLDER NAME URL [--doc]
    python warehouse/connectors/large_load_filings.py --raw-root RAW tally
"""

import argparse
import csv
import datetime as dt
import hashlib
import html as H
import os
import re
import subprocess
import sys
import time
import urllib.robotparser

UA = "ERW research project, github.com/SamuelEnrique/erw"
PASS = "D"
MAX_DOCS = 400
MAX_REQ = 600
MAX_BYTES = 1_000_000_000
PACE = 2.1   # seconds after every request, whatever the host: never more than one request in two seconds a host
# Who asks. This script's requests are made by an AI agent built on Anthropic's Claude, and what it fetches is read by
# a Claude model. A host whose robots.txt disallows Anthropic's agents by name is therefore not asked, whatever name
# the request itself carries: a rule that names the asker is not got round by a different label (session 164, the
# agent's decision, handed to the owner: Ohio's docketing system names all three and disallows every path). Only the
# owner empties this list.
ASKED_BY = ("anthropic-ai", "ClaudeBot", "Claude-Web")
REQ_COLS = ["url", "status", "bytes", "at", "sha256", "kind", "doc", "saved", "note"]
REFUSED_HOSTS = ["misoenergy.org", "dataminer2.pjm.com", "dataminer.pjm.com", "api.pjm.com"]
EMAIL_IN_URL = re.compile(r"[\w.+-]+(?:%40|@)[\w-]+(?:\.[\w-]+)+", re.I)
CHECK_WORDS = [b"recaptcha", b"captcha", b"no robots or crawlers", b"are you a robot", b"verify you are human",
               b"just a moment", b"i'm not a robot"]


def host_of(url):
    m = re.match(r"^https?://([^/:]+)", url or "", flags=re.I)
    return m.group(1).lower() if m else ""


def refused(url):
    """Why an address is never asked for; '' when it may be."""
    host = host_of(url)
    if not host:
        return "no http address"
    if any(host == h or host.endswith("." + h) for h in REFUSED_HOSTS):
        return "an address this project never requests (MISO is paused; no PJM Data Miner or API)"
    if EMAIL_IN_URL.search(url):
        return "the address holds an e-mail address: not requested"
    return ""


def robots_path(base, host):
    return os.path.join(base, PASS, "raw", "robots", host + ".txt")


def robots_says(base, url):
    """(may ask, the words). A host's robots.txt must be saved first; a saved file that is not a robots file (the
    host answered 404 or a page) forbids nothing."""
    host = host_of(url)
    if re.match(r"^https?://[^/]+/robots\.txt$", url, flags=re.I):
        return True, "the robots.txt itself"
    p = robots_path(base, host)
    if not os.path.exists(p):
        return False, f"robots.txt of {host} is not saved yet: ask for it first"
    with open(p, encoding="utf-8", errors="replace") as f:
        text = f.read()
    if not re.search(r"(?im)^\s*(user-agent|disallow|allow)\s*:", text):
        return True, "the saved answer is not a robots file (nothing is disallowed)"
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(text.lstrip("﻿").splitlines())
    for agent in (UA, "ERW", "*") + ASKED_BY:
        if not rp.can_fetch(agent, url):
            return False, f"robots.txt of {host} disallows this address for '{agent}'"
    return True, "robots.txt allows it"


def read_requests(base):
    p = os.path.join(base, PASS, "requests.csv")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def tally(base):
    rows = read_requests(base)
    n = len(rows)
    b = sum(int(r["bytes"]) for r in rows if (r.get("bytes") or "").isdigit())
    docs = sum(1 for r in rows if r.get("doc") == "1")
    return n, b, docs


def log_request(base, row):
    p = os.path.join(base, PASS, "requests.csv")
    new = not os.path.exists(p)
    with open(p, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REQ_COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)


def html_text(raw):
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        s = raw.decode("cp1252", errors="replace")
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>|</h[1-6]>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = H.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s)


def get(base, folder, name, url, doc=False, out=print):
    """One plain request. Returns the request's row, or None when it was not asked."""
    import requests
    why = refused(url)
    if why:
        out(f"NOT REQUESTED {url}: {why}")
        return None
    ok, words = robots_says(base, url)
    if not ok:
        out(f"NOT REQUESTED {url}: {words}")
        return None
    n, b, docs = tally(base)
    if n >= MAX_REQ or b >= MAX_BYTES - 60_000_000 or (doc and docs >= MAX_DOCS):
        out(f"CEILING: {n} requests, {b} bytes, {docs} documents so far. Not requested: {url}")
        return None
    is_robots = url.lower().endswith("/robots.txt")
    d = os.path.join(base, PASS, "raw", "robots" if is_robots else folder)
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(base, PASS, "text"), exist_ok=True)
    path = robots_path(base, host_of(url)) if is_robots else os.path.join(d, name)
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = {"url": url, "status": "", "bytes": 0, "at": at, "sha256": "", "kind": "", "doc": "1" if doc else "0",
           "saved": "", "note": ""}
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept": "*/*"}, timeout=120, allow_redirects=True)
        body = r.content
    except Exception as exc:   # the exact error is the record
        row.update(status=f"error: {type(exc).__name__}", note=str(exc)[:300])
        log_request(base, row)
        out(f"ERROR {url}: {str(exc)[:200]}")
        time.sleep(PACE)
        return row
    kind = "pdf" if body[:1024].lstrip().startswith(b"%PDF") else "other"
    note = "" if r.url == url else f"redirected to {r.url}"
    low = body[:300000].lower()
    if kind != "pdf" and any(w in low for w in CHECK_WORDS):
        note = (note + "; " if note else "") + "the answer speaks of a CAPTCHA or robot check: saved as it came, not read, not got past"
        kind = "check"
    with open(path, "wb") as f:
        f.write(body)
    row.update(status=str(r.status_code), bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), kind=kind,
               saved=os.path.relpath(path, os.path.join(base, PASS)).replace("\\", "/"), note=note)
    log_request(base, row)
    if r.status_code == 200 and not is_robots:
        txt = os.path.join(base, PASS, "text", f"{folder}__{name}.txt")
        if kind == "pdf":
            subprocess.run(["pdftotext", "-q", "-enc", "UTF-8", "-layout", path, txt], check=False)
        else:
            with open(txt, "w", encoding="utf-8") as f:
                f.write(html_text(body))
    out(f"{folder} {name} http={row['status']} bytes={row['bytes']} {kind} at={at} {note}")
    time.sleep(PACE)
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: one plain request for a filing's public PDF, counted against the ceilings")
    ap.add_argument("--raw-root", required=True, help="the directory that holds the passes' folders (warehouse/raw/large_load_rules)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get")
    g.add_argument("triples", nargs="+", help="folder, file name, address; in threes")
    g.add_argument("--doc", action="store_true", help="the addresses are documents (counted against the ceiling of 400)")
    sub.add_parser("tally")
    a = ap.parse_args(argv)
    base = os.path.abspath(a.raw_root)
    if a.cmd == "tally":
        n, b, docs = tally(base)
        print(f"pass {PASS}: {n} requests of {MAX_REQ}, {b} bytes of {MAX_BYTES}, {docs} documents of {MAX_DOCS}")
        return 0
    if len(a.triples) % 3:
        print("arguments come in threes: folder, file name, address")
        return 2
    for i in range(0, len(a.triples), 3):
        get(base, a.triples[i], a.triples[i + 1], a.triples[i + 2], doc=a.doc)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
