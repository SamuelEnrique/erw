#!/usr/bin/env python3
"""How long large loads waited, measured from successive dated copies of public queues (session 155, approved pull).

Energy Research Warehouse (ERW) connector. Writes warehouse/output/large_load_waits.csv (events shape, one row a
request and stage interval). INTERNAL: nothing here is published, on the site, in a public Redivis dataset or in the
live set.

    python -I warehouse/connectors/large_load_waits.py --list                # the Internet Archive's listings of each address (CDX), saved
    python -I warehouse/connectors/large_load_waits.py --pull                # each distinct capture once, and the current copies
    python -I warehouse/connectors/large_load_waits.py --terms               # the Archive's and each publisher's terms, saved with their hashes
    python -I warehouse/connectors/large_load_waits.py --write               # the table (needs the data lock); no request
    python -I warehouse/connectors/large_load_waits.py --write --out-dir DIR # a trial: the table, its log and the summary's counts under DIR
    python -I warehouse/connectors/large_load_waits.py --count               # read the saved copies and count their rows against the ceiling; no request
    python -I warehouse/connectors/large_load_waits.py --summary DIR         # the summary's lines of numbers, from DIR/large_load_waits_counts.json
    [--raw-root DIR]   the directory that holds large_load_waits/ and large_load_statements/ (default: this copy's warehouse/raw)

(-I: a file fetched from an archive is untrusted. Python is started isolated and every workbook is opened read-only.)

WHY. No utility, operator or regulator among the eighty read in session 151 publishes how long its large loads waited
from request to energization. A list of requests that is published again and again says it without being asked: the
day a request first stands in a dated copy, the day its status changes, the day it first reads in service. The
Internet Archive keeps dated copies of such lists.

THE PULL (the owner's words, 8 October 2026: "every dated copy the Internet Archive holds of NYISO's interconnection
queue workbook (its load-project sheets), of Grant County PUD's public large-load queue, and of ERCOT's large-load
interconnection status reports, plus the current copies"). Ceilings: 3,000,000 rows, 1,500 requests, 3 GB, counted
in warehouse/raw/large_load_waits/requests.csv across every run; a request that would pass one is refused BEFORE it
is made (Budget). The Archive is asked at most once every two seconds; a 429 or a 503 is waited out once, recorded,
and that address is left. Every request carries the User-Agent "ERW research project, github.com/SamuelEnrique/erw"
and nothing else that names anyone. MISO and PJM are never requested. A login, a form, a CAPTCHA or a browser check
is recorded and left.

A COPY IS DATED BY ITS PUBLISHER, never by the day the Archive captured it (an old address can answer with a newer
file): NYISO's workbook by the day it was last saved (its own properties), or the publisher's Last-Modified for the
.xls workbooks of 2014 to 2019; Grant County PUD's PDF by the day printed at its top. One file captured many times
is one copy (its sha256).

FOLLOWING A REQUEST. A request is followed by the publisher's own identifier: NYISO's queue position (leading zeros
aside); Grant County PUD's queue position with its queue date, the description being the same in every copy. A
request seen in one copy only is not followed; neither is one whose identifier stands on two differing rows of one
copy, or whose printed queue date differs between copies. Each is counted with its reason (follow()). Megawatts are
kept as written in each copy, and a change is recorded, not corrected.

A DURATION IS A RANGE BETWEEN COPIES, NEVER A MIDPOINT. An event (a change of stage, in service, withdrawal) came
between the last copy that does not show it and the first that does: both are on the row. The queue date the copies
print is used as printed. At least: the later bound of the start to the earlier bound of the end. At most: the
earlier bound of the start to the later bound of the end. Labels (measure()): `measured` (the end lies between two
copies that hold the request, and the start is printed or bounded); `lower bound` (the end has not come, or a side
is not bounded); `two copies only` (the request is seen in two copies: a lower bound, labeled so); `upper bound`
(the end had already come in the first copy that holds the request). A stage is counted only where a copy shows it
in the publisher's words. Nothing is interpolated; no average is taken over lower bounds; a figure on fewer than
five requests is its values, not a median (figure()).

ERCOT's status reports give megawatts by stage for the whole system and list no request: they are read and dated
(read_ercot()), and no wait is made from them.

License: internal. NYISO's legal notice confers no license (session 149): its requests, names and megawatts are in
no tracked file. The Archive's terms, Grant County PUD's and ERCOT's are quoted in docs/accelerator/large_load_waits.md.
"""

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

NAME = "large_load_waits"
CONNECTOR = "large_load_waits"
SOURCE = "erw:large_load_waits"
CONTACT = "ERW research project, github.com/SamuelEnrique/erw"   # the owner's ruling: this string and nothing else
UA = {"User-Agent": CONTACT}
RAW_DEFAULT = os.path.join(ROOT, "warehouse", "raw")

CEILING_ROWS = 2_000_000             # session 160: the owner's ceiling for this pull (session 155's was 3,000,000); counted across both
CEILING_REQUESTS = 1_500
CEILING_BYTES = 3 * 1024 ** 3
CEILING_LISTINGS_OTHER = 60          # CDX listings of queues that could be followed next (nothing of theirs is fetched)
ROWS_RESERVE = 5_000                 # the most rows one copy is taken to hold, set aside before it is fetched
BYTES_RESERVE = 60 * 1024 ** 2       # the most bytes one answer may be: a fetch stops reading at what is left of this
ARCHIVE_PAUSE = 2.5                  # seconds between two requests to the Archive (the rule: one every two seconds at most)
PUBLISHER_PAUSE = 2.0
BACKOFF = 60                         # seconds waited once after a 429 or a 503, before that address is left
NEVER = ("misoenergy.org", "pjm.com")   # no request for any reason (dataminer and api are hosts of pjm.com)

CDX = "https://web.archive.org/cdx/search/cdx"
WAYBACK = "https://web.archive.org/web/{ts}id_/{url}"
REQUEST_COLS = ["at", "kind", "host", "url", "status", "bytes", "note"]
CAPTURE_COLS = ["publisher", "original", "capture", "archive_url", "digest", "bytes", "sha256", "retrieved_at", "status",
                "file", "rows", "last_modified", "note"]

# the addresses listed with the Archive: (publisher, the url given to the CDX, its match type, a filter on the
# original address or "", what it is)
LISTINGS = [
    ("nyiso", "nyiso.com/documents/20142/1407078/", "prefix", "",
     "the folder of NYISO's interconnection queue workbook since its 2018 site (the address nyiso_load_queue.py reads)"),
    ("nyiso", "nyiso.com/public/webdocs/markets_operations/services/planning/Documents_and_Resources/Interconnection_Studies/NYISO_Interconnection_Queue/", "prefix", "",
     "the folder of the workbook on NYISO's site before 2018"),
    ("grantpud", "grantpud.org", "domain", "(?i).*queue.*",
     "every address of Grant County PUD's site that names a queue"),
    ("ercot", "ercot.com/files/docs/", "prefix", "(?i).*(large[-_ .%20]*load|LLI[-_ .]|LFL[-_ .]|TAC[-_ .]*Report).*",
     "the meeting documents of ERCOT whose name says large load, LLI, LFL or TAC Report"),
    # session 160: the first listing's filter missed a name written with %20 after LLI or LFL ("LLI%20Queue%20Status%20Update")
    # and the status reports named for the queue alone. One listing a year since the interim process began (March 2022).
] + [
    ("ercot", f"ercot.com/files/docs/{y}/", "prefix", "(?i).*(LLI|LFL|large.{0,3}load|queue.{0,3}status|interconnection.{0,3}status|LLWG).*",
     f"session 160: ERCOT's meeting documents of {y} whose name says LLI, LFL, large load, queue status, interconnection status or LLWG")
    for y in range(2022, 2027)
] + [
    ("grantpud", "grantpud.org/", "prefix", "(?i).*(large.{0,3}(load|power)|load.{0,3}(interconnect|queue|request)|wait.{0,3}list).*",
     "session 160: every address of Grant County PUD's site that names a large load, a large power request or a waiting list"),
]


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def stamp(t=None):
    return (t or now_utc()).strftime("%Y-%m-%dT%H:%M:%SZ")


def host_of(url):
    m = re.match(r"^https?://([^/:]+)", url or "")
    return m.group(1).lower() if m else ""


class Refused(RuntimeError):
    """A request that was not made: it would pass a ceiling, or its host is never requested."""


class Budget:
    """The pull's ceilings, counted across every run in requests.csv. ask() is called BEFORE a request and raises
    Refused when the request would pass a ceiling: one more request, the bytes set aside for one answer, the rows set
    aside for one copy. spend() records what the request then cost. Nothing here makes a request."""

    def __init__(self, raw, rows=CEILING_ROWS, requests=CEILING_REQUESTS, nbytes=CEILING_BYTES):
        self.raw = raw
        self.path = os.path.join(raw, "requests.csv")
        self.ceiling = {"rows": rows, "requests": requests, "bytes": nbytes}
        self.requests = 0
        self.bytes = 0
        self.rows = 0
        self.other_listings = 0
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    self.requests += 1
                    self.bytes += int(r["bytes"] or 0)
                    self.other_listings += r["kind"] == "listing of another queue"
        # rows: a request's row in a copy. Counted in copies.csv once a copy has been read; a copy fetched and not yet
        # read is taken at the most one copy may hold (ROWS_RESERVE), so the count never runs behind the pull
        counted = {}
        cop = os.path.join(raw, "copies.csv")
        if os.path.exists(cop):
            with open(cop, encoding="utf-8", newline="") as f:
                counted = {r["sha256"]: int(r["rows"] or 0) for r in csv.DictReader(f)}
        cap = os.path.join(raw, "captures.csv")
        if os.path.exists(cap):
            with open(cap, encoding="utf-8", newline="") as f:
                shas = {r["sha256"] for r in csv.DictReader(f) if r["sha256"] and r["file"] and r["publisher"] in WANTED
                        and WANTED[r["publisher"]].search(r["original"]) and not NOT_WANTED.search(r["original"])}
            self.rows = sum(counted.get(s, ROWS_RESERVE) for s in shas)

    def left(self):
        return {"requests": self.ceiling["requests"] - self.requests, "bytes": self.ceiling["bytes"] - self.bytes,
                "rows": self.ceiling["rows"] - self.rows}

    def ask(self, url, kind="", rows_reserve=0, bytes_reserve=BYTES_RESERVE):
        host = host_of(url)
        if any(n in url.lower() for n in NEVER):   # the publisher's own servers, and the Archive's copies of them too
            raise Refused(f"never requested: an address of {[n for n in NEVER if n in url.lower()][0]}")
        if self.requests + 1 > self.ceiling["requests"]:
            raise Refused(f"the request would be number {self.requests + 1}, past the ceiling of {self.ceiling['requests']:,} requests")
        if self.bytes + bytes_reserve > self.ceiling["bytes"]:
            raise Refused(f"{self.bytes:,} bytes read; one more answer of up to {bytes_reserve:,} would pass the ceiling of {self.ceiling['bytes']:,} bytes")
        if self.rows + rows_reserve > self.ceiling["rows"]:
            raise Refused(f"{self.rows:,} rows counted; one more copy of up to {rows_reserve:,} would pass the ceiling of {self.ceiling['rows']:,} rows")
        if kind == "listing of another queue" and self.other_listings + 1 > CEILING_LISTINGS_OTHER:
            raise Refused(f"the listing would be number {self.other_listings + 1} of the queues to follow next, past the ceiling of {CEILING_LISTINGS_OTHER}")
        return min(bytes_reserve, self.ceiling["bytes"] - self.bytes)

    def spend(self, url, kind, status, nbytes, note=""):
        self.requests += 1
        self.bytes += nbytes
        self.other_listings += kind == "listing of another queue"
        os.makedirs(self.raw, exist_ok=True)
        new = not os.path.exists(self.path)
        with open(self.path, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=REQUEST_COLS, lineterminator="\n")
            if new:
                w.writeheader()
            w.writerow(dict(at=stamp(), kind=kind, host=host_of(url), url=url, status=status, bytes=nbytes, note=note[:300]))

    def add_rows(self, n):
        self.rows += n


class Net:
    """Plain requests, counted. One at a time; the Archive at most once every ARCHIVE_PAUSE seconds. An answer of 429
    or 503 is waited out once (BACKOFF seconds), recorded, and the address is then in self.left_alone: it is not asked
    again in this run."""

    def __init__(self, budget, log, sleep=time.sleep):
        self.budget = budget
        self.log = log
        self.sleep = sleep
        self.last = {}
        self.left_alone = {}
        self.session = None

    def get(self, url, kind, rows_reserve=0, timeout=120):
        """(status, content, headers). Raises Refused before the request when it would pass a ceiling."""
        import requests
        if url in self.left_alone:
            raise Refused(f"left alone after {self.left_alone[url]}")
        room = self.budget.ask(url, kind, rows_reserve)
        host = host_of(url)
        pause = ARCHIVE_PAUSE if host.endswith("archive.org") else PUBLISHER_PAUSE
        wait = self.last.get(host, 0) + pause - time.time()
        if wait > 0:
            self.sleep(wait)
        if self.session is None:
            self.session = requests.Session()
        status, content, headers, note = "", b"", {}, ""
        try:
            with self.session.get(url, headers=UA, timeout=timeout, stream=True, allow_redirects=True) as r:
                status, headers = str(r.status_code), dict(r.headers)
                got = []
                size = 0
                for chunk in r.iter_content(1 << 16):
                    size += len(chunk)
                    if size > room:
                        note = f"stopped reading at {room:,} bytes: the answer would pass what is left under the ceiling"
                        break
                    got.append(chunk)
                content = b"".join(got)
                if r.url != url:
                    note = (note + " " if note else "") + f"answered at {r.url}"
        except Exception as e:  # a failed request is recorded with its exact error and left
            status, note = "error", f"{type(e).__name__}: {e}"
        self.last[host] = time.time()
        self.budget.spend(url, kind, status, len(content), note)
        self.log(f"  GET {url} -> {status}, {len(content):,} bytes{'; ' + note if note else ''}")
        if status in ("429", "503"):
            self.left_alone[url] = f"HTTP {status}"
            self.log(f"  HTTP {status}: waiting {BACKOFF} seconds, then this address is left")
            self.sleep(BACKOFF)
            self.last[host] = time.time()
        return status, content, headers


# ---------------------------------------------------------------------------
# The listings and the captures
# ---------------------------------------------------------------------------

def cdx_url(url, match, flt="", extra=""):
    from urllib.parse import quote
    q = f"{CDX}?url={quote(url, safe='/:.')}&matchType={match}&output=json&fl=timestamp,original,mimetype,statuscode,digest,length&filter=statuscode:200"
    if flt:
        q += "&filter=original:" + quote(flt, safe="")
    return q + extra


def read_listing(content):
    """A CDX answer (JSON, a header row then one row a capture) as a list of dicts; [] for an empty answer."""
    text = content.decode("utf-8", "replace").strip()
    if not text:
        return []
    rows = json.loads(text)
    if not rows:
        return []
    head = rows[0]
    return [dict(zip(head, r)) for r in rows[1:]]


def listing_file(raw, publisher, url, match):
    key = hashlib.sha1(f"{url}|{match}".encode("utf-8")).hexdigest()[:10]
    return os.path.join(raw, "listings", f"{publisher}_{key}.json")


def do_list(raw, net, log, listings=LISTINGS, kind="listing"):
    """One CDX request an address of LISTINGS; each answer is saved whole under listings/."""
    os.makedirs(os.path.join(raw, "listings"), exist_ok=True)
    out = []
    for publisher, url, match, flt, what in listings:
        path = listing_file(raw, publisher, url, match)
        if os.path.exists(path):
            log(f"list {publisher}: {url} ({match}) already listed, {path}")
            continue
        try:
            status, content, _ = net.get(cdx_url(url, match, flt), kind)
        except Refused as e:
            log(f"list {publisher}: REFUSED before the request: {e}")
            out.append((publisher, url, "refused", str(e)))
            continue
        if status != "200":
            log(f"list {publisher}: {url} answered {status}; recorded and left")
            out.append((publisher, url, status, ""))
            continue
        try:
            rows = read_listing(content)
        except ValueError as e:
            log(f"list {publisher}: {url}: the answer is not a listing ({e}); recorded and left")
            out.append((publisher, url, "not a listing", ""))
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"publisher": publisher, "url": url, "match": match, "filter": flt, "what": what, "listed_at": stamp(), "captures": rows}, f, indent=0)
        log(f"list {publisher}: {url} ({match}): {len(rows)} captures, {len({r['digest'] for r in rows})} distinct by digest, "
            f"{len({r['original'] for r in rows})} addresses")
        out.append((publisher, url, "200", f"{len(rows)} captures"))
    return out


def saved_listings(raw):
    out = []
    d = os.path.join(raw, "listings")
    if not os.path.isdir(d):
        return out
    for n in sorted(os.listdir(d)):
        if n.endswith(".json"):
            with open(os.path.join(d, n), encoding="utf-8") as f:
                out.append(json.load(f))
    return out


def read_captures(raw):
    path = os.path.join(raw, "captures.csv")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def append_capture(raw, row):
    path = os.path.join(raw, "captures.csv")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAPTURE_COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in CAPTURE_COLS})


def safe_name(original):
    n = original.split("?")[0].rstrip("/").split("/")[-1] or "page"
    from urllib.parse import unquote
    n = re.sub(r"[^A-Za-z0-9._-]+", "-", unquote(n))
    return n[:80]


class Log:
    def __init__(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.f = open(path, "a", encoding="utf-8", newline="\n")

    def __call__(self, msg):
        self.f.write(f"{stamp()} {msg}\n")
        self.f.flush()

    def close(self):
        self.f.close()


# ---------------------------------------------------------------------------
# The pull: which captures are a copy of a queue, and each fetched once
# ---------------------------------------------------------------------------

MONTH_NAMES = "january|february|march|april|may|june|july|august|september|october|november|december"
WANTED = {
    # NYISO: every workbook in the two folders (the load-project sheets are looked for in each)
    "nyiso": re.compile(r"(?i)interconnection[-_ %20]*queue[^/]*\.xlsx?(/|\?|$)"),
    # Grant County PUD: the queue's own PDF, by its name (the drafts of tariffs in the folder Transmission-Queue are not the queue)
    "grantpud": re.compile(r"(?i)/[^/]*queue[^/]*\.pdf(\?|$)"),
    # ERCOT: a document whose name says it is a status update of the large load queue, or the monthly report to TAC
    # (session 160: also the working group's monthly report, as a file or as the meeting's zip, which holds the status update since April 2026)
    "ercot": re.compile(r"(?i)/[^/]*(queue[-_ ]*status|lli[-_ ]*status|status[-_ %20]*update|interconnection(%20|[-_ ])*status|aggregate[-_ ]*data|"
                        r"(?:" + MONTH_NAMES + r")[-_ ]*tac[-_ ]*report|large[-_ ]*load[-_ ]*update|llwg[-_ ]*report)[^/]*\.(pdf|pptx|docx|zip)(\?|$)"),
}
# not a copy of a queue: Grant County PUD's staging host and the tariff drafts beside its queue; ERCOT's documents of before 2020
# (TAC's reports to the board) and its regional planning group's project updates
# (session 160: a "status update" of a study or of a regional planning project is not the queue's status report)
NOT_WANTED = re.compile(r"(?i)staging\.grantpud\.org|(OATT|LGIA|SGIA|LGIP|SGIP|Rate%20Schedule|PUBLIC%20NOTICE)|ercot\.com/files/docs/(19|200|201)\d/|_RPG\.|"
                        r"Voltage-Ride|Transmission-Upgrades|/EIR[-_]|RPG[-_]")


def wanted_captures(raw):
    """From the saved listings: the captures that are a copy of a queue by their address, as (publisher, capture)
    in the order of capture; and those listed and not wanted, counted by publisher."""
    want, rest = [], {}
    for lst in saved_listings(raw):
        pub = lst["publisher"]
        if pub not in WANTED:
            continue
        for c in lst["captures"]:
            if WANTED[pub].search(c["original"]) and not NOT_WANTED.search(c["original"]):
                want.append((pub, c))
            else:
                rest[pub] = rest.get(pub, 0) + 1
    want.sort(key=lambda pc: (pc[0], pc[1]["timestamp"], pc[1]["original"]))
    return want, rest


def save_answer(raw, publisher, capture_ts, original, content):
    d = os.path.join(raw, publisher)
    os.makedirs(d, exist_ok=True)
    fname = f"{capture_ts}_{safe_name(original)}"
    path = os.path.join(d, fname)
    n = 1
    while os.path.exists(path):   # never written over: a second answer for the same name gets a number
        with open(path, "rb") as f:
            if f.read() == content:
                return f"{publisher}/{os.path.basename(path)}"
        n += 1
        path = os.path.join(d, f"{capture_ts}_{n}_{safe_name(original)}")
    with open(path, "wb") as f:
        f.write(content)
    return f"{publisher}/{os.path.basename(path)}"


def do_pull_archive(raw, net, log, only=()):
    """Each distinct capture (by the Archive's digest) once, in its raw form. A capture already in captures.csv is not
    asked for again. Returns counts by publisher. only: the publishers this run may ask for (empty: all)."""
    want, rest = wanted_captures(raw)
    want = [(pub, c) for pub, c in want if not only or pub in only]
    have = {(r["publisher"], r["digest"]) for r in read_captures(raw) if r["digest"]}
    asked = {(r["publisher"], r["original"], r["capture"]) for r in read_captures(raw)}
    counts = {}
    for pub, c in want:
        k = counts.setdefault(pub, {"listed": 0, "distinct": set(), "fetched": 0, "refused": 0, "failed": 0, "already": 0})
        k["listed"] += 1
        k["distinct"].add(c["digest"])
    for pub, c in want:
        k = counts[pub]
        if (pub, c["digest"]) in have or (pub, c["original"], c["timestamp"]) in asked:
            continue
        url = WAYBACK.format(ts=c["timestamp"], url=c["original"])
        try:
            status, content, headers = net.get(url, "capture", rows_reserve=ROWS_RESERVE)
        except Refused as e:
            k["refused"] += 1
            log(f"pull {pub}: REFUSED before the request: {e} ({url})")
            if "ceiling" in str(e):
                break
            continue
        row = dict(publisher=pub, original=c["original"], capture=c["timestamp"], archive_url=url, digest=c["digest"], bytes=len(content),
                   sha256=hashlib.sha256(content).hexdigest() if content else "", retrieved_at=stamp(), status=status,
                   last_modified=headers.get("x-archive-orig-last-modified", "") or headers.get("X-Archive-Orig-Last-Modified", ""), rows="")
        if status == "200" and content:
            row["file"] = save_answer(raw, pub, c["timestamp"], c["original"], content)
            have.add((pub, c["digest"]))
            k["fetched"] += 1
        else:
            row["note"] = "not fetched: recorded and left"
            k["failed"] += 1
        append_capture(raw, row)
    for pub, k in counts.items():
        k["distinct"] = len(k["distinct"])
        log(f"pull {pub}: {k['listed']} captures wanted, {k['distinct']} distinct by digest; this run fetched {k['fetched']}, failed {k['failed']}, refused {k['refused']}; "
            f"listed and not a copy of the queue by its address: {rest.get(pub, 0)}")
    return counts


def do_fetch_current(raw, net, log, publisher, url, kind="current copy", rows_reserve=ROWS_RESERVE):
    """One plain request to a publisher for a current copy or a page; saved and written to captures.csv with the
    capture stamp of the moment it was read. Returns (status, content, the file's name or "")."""
    ts = now_utc().strftime("%Y%m%d%H%M%S")
    status, content, headers = net.get(url, kind, rows_reserve=rows_reserve)
    row = dict(publisher=publisher, original=url, capture=ts, archive_url="", digest="", bytes=len(content),
               sha256=hashlib.sha256(content).hexdigest() if content else "", retrieved_at=stamp(), status=status,
               last_modified=headers.get("Last-Modified", ""), rows="", note=kind + ", from the publisher")
    fname = ""
    if status == "200" and content:
        fname = row["file"] = save_answer(raw, publisher, ts, url, content)
    append_capture(raw, row)
    return status, content, fname


# ---------------------------------------------------------------------------
# Reading a copy: the load requests it lists
# ---------------------------------------------------------------------------

ENTITIES = {
    "nyiso": dict(entity="New York ISO", group="New York ISO", source="nyiso:interconnection_queue_dated_copies",
                  publisher="New York Independent System Operator (NYISO)", id_name="Queue Pos. (Queue Number)"),
    "grantpud": dict(entity="Grant County Public Utility District", group="Grant County Public Utility District",
                     source="grantpud:interconnection_queue_dated_copies", publisher="Public Utility District No. 2 of Grant County, Washington (Grant PUD)",
                     id_name="Queue Position with its Queue Date"),
}
# the five stages of large_load_statements (stage_vocabulary.csv), and the class each publisher's status words are placed on.
# The words are always kept beside the class. NYISO: the classes stage_vocabulary.csv gives its words (Project Scoping 1; SIS Pending,
# in Progress and Approved, Facilities Study Pending and in Progress 2; Under Construction 5); the words it does not hold are placed
# by the same reading (the collecting agent's, not a person's review).
STAGES = ["1 request or inquiry", "2 study or engineering", "3 financial commitment", "4 signed service agreement", "5 under construction or energized"]
NONE = "none"
CLASS_RULES = [
    (r"withdrawn|removed from queue|no longer applicable", NONE, "the publisher says the request left the list"),
    (r"in.service", STAGES[4], "in service"),
    (r"under construction", STAGES[4], "stage_vocabulary.csv: Under Construction, class 5"),
    (r"construction agreement signed", STAGES[3], "the nearest of Grant County PUD's stage words in stage_vocabulary.csv is 'facilities agreement signed', class 4"),
    (r"interconnection agreement signed|ia completed", STAGES[3], "an agreement to interconnect is signed (the nearest class: 4)"),
    (r"accepted cost allocation", STAGES[2], "cost allocation accepted, the agreement not yet complete: money committed short of an agreement"),
    (r"scoping", STAGES[0], "stage_vocabulary.csv: Project Scoping, class 1"),
    (r"\bfes\b|sris|\bsis\b|\bfs\b|study|cost allocation|cluster|phase", STAGES[1], "a study pending, in progress or done (stage_vocabulary.csv places SIS and Facilities Study words on class 2)"),
]
IN_SERVICE = re.compile(r"(?i)in.service")
LEFT = re.compile(r"(?i)withdrawn|removed from queue|no longer applicable")
SIZE_CLASSES = [("under 20 MW", 0, 20), ("20 to under 100 MW", 20, 100), ("100 to under 300 MW", 100, 300), ("300 MW and over", 300, float("inf"))]


def stage_class(words):
    w = (words or "").lower()
    for pattern, cls, why in CLASS_RULES:
        if re.search(pattern, w):
            return cls, why
    return "not classed", ""


def size_class(mw):
    try:
        v = float(mw)
    except (TypeError, ValueError):
        return "megawatts not a number"
    for name, lo, hi in SIZE_CLASSES:
        if lo <= v < hi:
            return name
    return "megawatts not a number"


def squeeze(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def num_text(v):
    """A number as a sheet prints it in a General cell: 40, 50.2. Text is returned squeezed."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(int(v)) if v == int(v) else repr(v)
    return squeeze(v)


def request_id(printed):
    """The identifier a request is followed by: NYISO's queue position as printed, with leading zeros removed (the
    same position is printed as 123, 0123 and 123.0 in the workbooks of different years). Nothing else is changed."""
    t = num_text(printed).upper()
    return t.lstrip("0") or t


def iso_day(v):
    """YYYY-MM-DD where the cell holds a full date (a date cell, or text M/D/YYYY or M/D/YY); else ""."""
    if isinstance(v, (dt.datetime, dt.date)):
        return v.strftime("%Y-%m-%d")
    t = squeeze(v) if v is not None else ""
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})", t)
    if m:
        y = int(m.group(3))
        y += 2000 if y < 70 else 1900 if y < 100 else 0
        try:
            return dt.date(y, int(m.group(1)), int(m.group(2))).strftime("%Y-%m-%d")
        except ValueError:
            return ""
    return ""


def workbook_grids(path):
    """Every sheet of a workbook as (name, rows of cell values), opened read-only. An .xls date cell is given as a
    datetime (the cell's own type says it is a date)."""
    with open(path, "rb") as f:
        head = f.read(8)
    if head[:2] == b"PK":
        import openpyxl
        with open(path, "rb") as f:
            wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
            for name in wb.sheetnames:
                yield name, [list(r) for r in wb[name].iter_rows(values_only=True)]
            wb.close()
    elif head[:4] == b"\xd0\xcf\x11\xe0":
        import xlrd
        wb = xlrd.open_workbook(path, on_demand=True)
        for name in wb.sheet_names():
            sh = wb.sheet_by_name(name)
            rows = []
            for i in range(sh.nrows):
                row = []
                for c in sh.row(i):
                    if c.ctype == xlrd.XL_CELL_DATE:
                        try:
                            row.append(xlrd.xldate_as_datetime(c.value, wb.datemode))
                        except Exception:
                            row.append(c.value)
                    elif c.ctype == xlrd.XL_CELL_EMPTY:
                        row.append(None)
                    else:
                        row.append(c.value)
                rows.append(row)
            yield name, rows
    else:
        raise ValueError(f"not a workbook (first bytes {head!r})")


NYISO_SKIP = ("nyiso zonal map", "load project tracking")
KEY_MARK = re.compile(r"(?:^|(?<=[\s,:]))([0-9]{1,2}[A-Z]?|P)\s*=")


def nyiso_status_key(grids):
    """The workbook's own key of its status column, code -> words ("1=Scoping Meeting Pending, ..."), from the notes
    under its sheets. The Load Projects sheet's key where it has one, else the first key found."""
    found = {}
    bullets = (chr(0x25CF), chr(0x2022))   # the marks NYISO's notes begin with
    for name, rows in grids:
        lines = []   # the notes under a sheet: rows that hold text in one cell only
        for row in rows:
            cells = [squeeze(v) for v in row if v is not None and squeeze(v) != ""]
            if len(cells) == 1 and isinstance(next(v for v in row if v is not None and squeeze(v) != ""), str):
                lines.append(cells[0])
        start = next((i for i, n in enumerate(lines) if re.search(r"1\s*=\s*Scoping", n)), None)
        if start is None:
            continue
        text = lines[start]
        for n in lines[start + 1:]:   # the key runs on to the next note
            if n[:1] in bullets or not KEY_MARK.search(n):
                break
            text += " " + n
        text = text.split("Key", 1)[1] if "Key" in text else text
        marks = list(KEY_MARK.finditer(text))
        key = {}
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            key.setdefault(m.group(1), squeeze(text[m.end():end]).strip(" ,.:"))
        found.setdefault(name.strip(), key)
    if not found:
        return {}
    return found.get("Load Projects") or next(iter(found.values()))


def nyiso_header(rows):
    """(index of the first data row, {field: column}) of a sheet of the workbook, or None. The header is one row, or
    two (the older sheets print "Queue" over "Pos.")."""
    for i, row in enumerate(rows[:4]):
        vals = ["" if v is None else squeeze(v) for v in row]
        if not any(v.startswith("Queue") for v in vals):
            continue
        nxt = ["" if v is None else squeeze(v) for v in rows[i + 1]] if i + 1 < len(rows) else []
        two = bool(nxt) and nxt[0] in ("Pos.", "") and any(x in ("Pos.", "Original", "Current", "COD", "Fuel") for x in nxt)
        heads = [squeeze(vals[j] + " " + (nxt[j] if two and j < len(nxt) else "")).lower() for j in range(len(vals))]
        col = {}
        for j, h in enumerate(heads):
            bare = h.replace(" ", "")
            if h.startswith("queue") and "id" not in col:
                col["id"] = j
            elif ("developer" in h or "owner" in h or "customer" in h) and "developer" not in col:
                col["developer"] = j
            elif "project name" in h and "name" not in col:
                col["name"] = j
            elif h in ("date of ir", "ir submission date") and "queue_date" not in col:
                col["queue_date"] = j
            elif h in ("sp (mw)", "peak mw load") and "mw" not in col:
                col["mw"] = j
            elif bare == "type/fuel" and "type" not in col:
                col["type"] = j
            elif h in ("s", "project status #", "nyiso status") and "status" not in col:
                col["status"] = j
            elif h.startswith("last update") and "last_update" not in col:
                col["last_update"] = j
        return i + (2 if two else 1), col
    return None


def read_nyiso(path):
    """The load requests of one copy of NYISO's workbook: the rows of the sheet "Load Projects" where the workbook
    has it, and in every other sheet the rows whose Type/Fuel is L (NYISO's own mark for a load). Returns
    (rows, notes). A row: id, id_printed, name, developer, mw, queue_date_printed, queue_date, status_code,
    status_words, sheet."""
    grids = [(n, r) for n, r in workbook_grids(path) if n.strip().lower() not in NYISO_SKIP]
    key = nyiso_status_key(grids)
    out, notes = [], []
    if not key:
        notes.append("no status key in the workbook: the status codes are kept without words")
    for name, rows in grids:
        sheet = name.strip()
        got = nyiso_header(rows)
        if got is None:
            continue
        first, col = got
        if "id" not in col or ("type" not in col and sheet != "Load Projects"):
            continue
        for row in rows[first:]:
            def cell(k):
                j = col.get(k)
                return row[j] if j is not None and j < len(row) else None
            if sheet != "Load Projects" and squeeze(cell("type") or "").upper() != "L":
                continue
            idp = num_text(cell("id"))
            filled = sum(1 for v in row if v is not None and squeeze(v) != "")
            if not idp or filled < 3:
                continue   # a line of the key or of the notes, not a request
            code = num_text(cell("status")).upper()
            qd = cell("queue_date")
            low = sheet.lower()
            words = key.get(code, "")
            if not words and "withdrawn" in low:
                words = "Withdrawn"
            if not words and "in service" in low:
                words = "In Service"
            out.append(dict(id=request_id(idp), id_printed=idp, name=squeeze(cell("name") or ""), developer=squeeze(cell("developer") or ""),
                            mw=num_text(cell("mw")), queue_date_printed=qd.strftime("%Y-%m-%d") if isinstance(qd, (dt.datetime, dt.date)) else num_text(qd),
                            queue_date=iso_day(qd), status_code=code, status_words=words, sheet=sheet))
    return out, notes


GRANT_DATE = re.compile(r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(" + MONTH_NAMES + r")\s+(\d{1,2}),\s+(\d{4})", re.I)


def read_grantpud(path):
    """The load requests of one copy of Grant County PUD's Interconnection Queue (a one-page PDF): the rows of its
    first table whose Type is Load. Returns (rows, notes, the day printed at the top of the copy or ""). A PDF that is
    a picture of the page holds no text and gives no rows: a number is never read off a picture."""
    import pdfplumber
    out, notes, day = [], [], ""
    with open(path, "rb") as f:
        if f.read(4) != b"%PDF":
            return out, ["not a PDF: the address answered with a web page"], day
    with pdfplumber.open(path) as pdf:
        words = sum(len(p.extract_words()) for p in pdf.pages)
        if not words:
            return out, [f"a picture of the page ({sum(len(p.images) for p in pdf.pages)} image, no text): not read"], day
        text = " ".join((p.extract_text() or "") for p in pdf.pages)
        m = GRANT_DATE.search(text)
        if m:
            months = MONTH_NAMES.split("|")
            day = dt.date(int(m.group(3)), months.index(m.group(1).lower()) + 1, int(m.group(2))).strftime("%Y-%m-%d")
        for page in pdf.pages:
            for table in page.extract_tables():
                if not table or not table[0]:
                    continue
                head = [squeeze(h or "").lower() for h in table[0]]
                if "type" not in head or "queue date" not in head:
                    continue   # the Transmission Service Queue has no Type column: it lists wheeling requests, not loads
                at = {h: i for i, h in enumerate(head)}
                for r in table[1:]:
                    cells = [squeeze(c or "") for c in r]
                    qd, typ = cells[at["queue date"]], cells[at["type"]]
                    glued = re.fullmatch(r"(\d{1,2}/\d{1,2}/\d{4})\s*([A-Za-z]+)", qd)   # the two cells run together in one copy's text
                    if glued and not typ:
                        qd, typ = glued.group(1), glued.group(2)
                    if typ.lower() != "load":
                        continue
                    pos = cells[at["queue position"]]
                    mw = re.sub(r"(?<=\d) (?=\d)", "", cells[at["mw"]])   # the PDF's text sets a space inside a number ("2 2"): the digits are joined, nothing else
                    out.append(dict(id=f"{pos} ({qd})", id_printed=pos, name=cells[at["description"]], developer="", mw=mw, queue_date_printed=qd,
                                    queue_date=iso_day(qd), status_code="", status_words=cells[at["status"]], sheet="Interconnection Queue",
                                    active=cells[at["active project"]] if "active project" in at else ""))
    return out, notes, day


def http_day(text):
    """A Last-Modified header as (YYYY-MM-DD, YYYY-MM-DDTHH:MM:SSZ), or ("", "")."""
    from email.utils import parsedate_to_datetime
    try:
        t = parsedate_to_datetime(text).astimezone(dt.timezone.utc)
    except (TypeError, ValueError):
        return "", ""
    return t.strftime("%Y-%m-%d"), t.strftime("%Y-%m-%dT%H:%M:%SZ")


def workbook_saved(path):
    """The moment an .xlsx workbook was last saved, from its own properties, as (YYYY-MM-DD, YYYY-MM-DDTHH:MM:SSZ);
    ("", "") for a file that has none (an .xls workbook)."""
    try:
        with zipfile.ZipFile(path) as z:
            core = z.read("docProps/core.xml").decode("utf-8", "replace")
    except (zipfile.BadZipFile, KeyError, OSError):
        return "", ""
    m = re.search(r"<dcterms:modified[^>]*>(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})Z?<", core)
    return (m.group(1), f"{m.group(1)}T{m.group(2)}Z") if m else ("", "")


def read_copies(raw, log):
    """Every saved copy of a queue, read: one entry a distinct file (by its sha256), dated by the publisher's own
    stamp and never by the day the Archive happened to capture it (an old address can answer with a newer file, and
    NYISO's server gave two old workbooks the Last-Modified of the day it moved them). NYISO: the day the workbook
    was last saved, by its own properties (the list is as it stood then); for the .xls workbooks of 2014 to 2019,
    the Last-Modified the publisher gave the file. Grant County PUD: the day printed at the top of the copy. Returns
    (copies, unread): a copy is dict(publisher, date, stamp, date_basis, url, file, sha256, rows, notes, captures)."""
    by_sha, unread = {}, []
    for c in read_captures(raw):
        pub = c["publisher"]
        if pub not in ENTITIES or not c["file"] or c["status"] != "200":
            continue
        if not WANTED[pub].search(c["original"]) or NOT_WANTED.search(c["original"]):
            continue   # a page that lists the copies, or a document beside the queue: not a copy of the queue
        e = by_sha.setdefault((pub, c["sha256"]), dict(publisher=pub, sha256=c["sha256"], file=c["file"], captures=[], last_modified=c["last_modified"]))
        e["captures"].append(c)
    copies = []
    for (pub, sha), e in by_sha.items():
        path = os.path.join(raw, e["file"])
        first = sorted(e["captures"], key=lambda c: (c["archive_url"] == "", c["capture"]))[0]   # the Archive's address where it holds the copy
        e["url"] = first["archive_url"] or first["original"]
        e["held_by"] = "the Internet Archive" if first["archive_url"] else "the publisher (read today)"
        try:
            if pub == "nyiso":
                rows, notes = read_nyiso(path)
                day, full = workbook_saved(path)
                basis = "the day the workbook was last saved, by its own properties (docProps/core.xml)"
                if not day:   # an .xls workbook: its properties are not read here
                    day, full = http_day(e["last_modified"])
                    basis = "the Last-Modified the publisher gave the file" + (", as the Archive kept it" if first["archive_url"] else "")
            else:
                rows, notes, day = read_grantpud(path)
                full, basis = day, "the day printed at the top of the copy"
        except Exception as ex:   # a copy that cannot be read is listed with its exact error and left
            unread.append(dict(e, why=f"{type(ex).__name__}: {ex}"))
            log(f"  {pub} {e['file']}: cannot be read: {type(ex).__name__}: {ex}")
            continue
        if not day:
            unread.append(dict(e, why="; ".join(notes) or "the copy carries no date of its own"))
            log(f"  {pub} {e['file']}: not used: {'; '.join(notes) or 'the copy carries no date of its own'}")
            continue
        copies.append(dict(e, date=day, stamp=full, date_basis=basis, rows=rows, notes=notes))
    copies.sort(key=lambda c: (c["publisher"], c["stamp"], c["file"]))
    return copies, unread


ERCOT_STAGES = ["No Studies Submitted", "Under ERCOT Review", "Planning Studies Approved", "Approved to Energize", "Observed Energized"]
# session 160. The one sentence each report writes out in words: megawatts approved to energize and megawatts observed
# consuming, for the whole system. Kept as ERCOT wrote it; it is a total, not a request's wait, and no wait is made from it.
ERCOT_A2E = re.compile(r"Of the ([\d,]+) ?MW that have received Approval to Energize, ERCOT has observed a non-\s*simultaneous (monthly )?peak consumption of ([\d,]+) ?MW", re.I)
# the words a list of requests would carry as a column head: a report that prints one is read by a person before anything is followed
ERCOT_LISTS = re.compile(r"(?i)\b(project name|project id|project number|customer name|queue position|queue number|request id|request number)\b")


def document_pages(name, content):
    """The text of a PDF or a PowerPoint file, a string a page or slide; [] for anything else."""
    if content[:4] == b"%PDF":
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return [" ".join((p.extract_text() or "").split()) for p in pdf.pages]
    if content[:2] == b"PK":
        try:
            z = zipfile.ZipFile(io.BytesIO(content))
        except zipfile.BadZipFile:
            return []
        slides = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)), key=lambda n: int(re.findall(r"\d+", n)[-1]))
        out = []
        for n in slides:
            xml = z.read(n).decode("utf-8", "replace")
            paras = ["".join(re.findall(r"<a:t>([^<]*)</a:t>", para)) for para in re.findall(r"<a:p>[\s\S]*?</a:p>|<a:p [\s\S]*?</a:p>", xml)]
            out.append(" ".join(" ".join(paras).split()))
        return out
    return []


def read_ercot(raw, log):
    """ERCOT's large load status reports among the saved documents (this pull's, and those ercot_large_load_status.py
    saved on this machine): for each, the day on its first page and which of ERCOT's five stage names it prints. The
    reports give megawatts by stage for the whole system and name no request, so nothing in them can be followed:
    a stage's megawatts over time is not a request's wait, and no wait is made from them. One entry a report day."""
    files = []
    for c in read_captures(raw):
        if c["publisher"] == "ercot" and c["file"] and c["status"] == "200":
            files.append((os.path.join(raw, c["file"]), c["archive_url"] or c["original"], "the Internet Archive" if c["archive_url"] else "ERCOT (read today)"))
    old = os.path.join(os.path.dirname(raw), "ercot_large_load_status")
    if os.path.isdir(old):
        for run in sorted(os.listdir(old)):
            d = os.path.join(old, run)
            if os.path.isdir(d):
                files += [(os.path.join(d, n), f"warehouse/raw/ercot_large_load_status/{run}/{n}", "ERCOT (saved by ercot_large_load_status.py)") for n in sorted(os.listdir(d))]
    months = MONTH_NAMES.split("|")
    out = {}
    for path, where, held in files:
        try:
            with open(path, "rb") as f:
                content = f.read()
            docs = [(os.path.basename(path), content)]
            if content[:2] == b"PK" and not path.lower().endswith((".pptx", ".docx", ".xlsx")):
                try:
                    z = zipfile.ZipFile(io.BytesIO(content))
                    if not any(n.startswith("ppt/") for n in z.namelist()):
                        docs = [(n, z.read(n)) for n in z.namelist() if n.lower().endswith((".pdf", ".pptx"))]
                except zipfile.BadZipFile:
                    docs = []
            for name, body in docs:
                pages = document_pages(name, body)
                first = pages[0] if pages else ""
                if not (re.search(r"Large\s+Load\s+Interconnection", first, re.I) and re.search(r"Status|Requests", first, re.I)):
                    continue
                # session 160: a month written whole or by its first three letters, a day with or without "st", "nd", "rd", "th"
                m = re.search(r"(" + MONTH_NAMES + r"|jan|feb|mar|apr|jun|jul|aug|sept?|oct|nov|dec)\.?\s+(\d{1,2})(?:st|nd|rd|th)?\s*,\s*(\d{4})", first, re.I)
                if not m:
                    continue
                day = dt.date(int(m.group(3)), [x[:3] for x in months].index(m.group(1).lower()[:3]) + 1, int(m.group(2))).strftime("%Y-%m-%d")
                text = " ".join(pages)
                m2 = ERCOT_A2E.search(text)
                out.setdefault(day, dict(day=day, document=name.split("/")[-1], where=where, held_by=held, pages=len(pages),
                                         stages_named=[x for x in ERCOT_STAGES if x.lower() in text.lower()],
                                         sha256=hashlib.sha256(body).hexdigest(),
                                         names_a_request=bool(ERCOT_LISTS.search(text)),
                                         approved_to_energize_mw=m2.group(1).replace(",", "") if m2 else "",
                                         observed_consuming_mw=m2.group(3).replace(",", "") if m2 else "",
                                         observed_basis=("the month's non-simultaneous peak" if m2.group(2) else "the all-time non-simultaneous peak") if m2 else "",
                                         sentence=" ".join(m2.group(0).split()) if m2 else ""))
        except Exception as ex:   # a document that cannot be read is recorded and left
            log(f"  ercot {os.path.basename(path)}: cannot be read: {type(ex).__name__}: {ex}")
    return [out[k] for k in sorted(out)]


# ---------------------------------------------------------------------------
# Following a request across copies
# ---------------------------------------------------------------------------

def follow(copies):
    """The requests that can be followed, by publisher, and those that cannot with the reason.

    A request is followed by its own identifier (request_id). It is NOT followed when: it is seen in one copy only
    (nothing to follow across); its identifier stands on two rows of one copy that differ in status or megawatts;
    the queue date printed for it differs between copies (the identifier may have been used twice). Where a list
    prints a description and megawatts beside a position (Grant County PUD), a change of the description is also a
    reason, since the position alone is not an identifier there. Returns (followed, not_followed): followed is
    {(publisher, id): [observation, ...]} in the order of the copies' dates; an observation is the request's row
    with its copy's date and address."""
    seen, bad = {}, {}
    for c in copies:
        by = {}
        for r in c["rows"]:
            by.setdefault(r["id"], []).append(r)
        for rid, rows in by.items():
            key = (c["publisher"], rid)
            if len({(r["status_code"], r["status_words"], r["mw"]) for r in rows}) > 1:
                bad[key] = "the same identifier is on two rows of one copy that differ in status or megawatts"
            seen.setdefault(key, []).append(dict(rows[0], date=c["date"], stamp=c["stamp"], url=c["url"], file=c["file"]))
    followed, not_followed = {}, []
    for key, obs in seen.items():
        why = bad.get(key, "")
        if not why and len(obs) < 2:
            why = "seen in one copy only"
        if not why and len({o["queue_date"] or o["queue_date_printed"] for o in obs if o["queue_date_printed"]}) > 1:   # the day, however the cell is formatted
            why = "the queue date printed for it differs between copies"
        if not why and key[0] == "grantpud" and len({o["name"].lower() for o in obs}) > 1:
            why = "its description changes between copies, and the position alone is not an identifier"
        if why:
            not_followed.append(dict(publisher=key[0], id=key[1], copies_seen=len(obs), first_copy=obs[0]["date"], last_copy=obs[-1]["date"], why=why))
        else:
            followed[key] = obs
    return followed, not_followed


def bound(o, kind="copy"):
    return {"date": o["date"], "url": o.get("url", ""), "kind": kind}


def days(a, b):
    return (dt.date.fromisoformat(b["date"] if isinstance(b, dict) else b) - dt.date.fromisoformat(a["date"] if isinstance(a, dict) else a)).days


def measure(S, E, last, copies_seen):
    """The range of one duration, in days, and its label. S and E are (the earlier bound, the later bound) of the
    start and of the end; a bound is a copy (its date and address) or a date the publisher prints, or None where
    nothing bounds that side. E is None where the end has not come by the last copy that holds the request (last).

    at least: the later bound of the start to the earlier bound of the end. at most: the earlier bound of the start
    to the later bound of the end. Never a midpoint. Labels:
      measured         the end lies between two copies that hold the request, and the start is a printed date or lies
                       between two bounds (two copies, or the printed queue date and the first copy that holds it)
      lower bound      the end has not come, or one side of the start or of the end is not bounded: only "at least"
      upper bound      the end had already come in the first copy that holds the request: only "at most"
      two copies only  the request is seen in exactly two copies: whatever they show, only "at least" is given
    Returns (at_least or None, at_most or None, label), or None where neither side can be given."""
    s_before, s_first = S
    at_least = at_most = None
    if E is None:
        if s_first is not None:
            at_least = max(0, days(s_first, last))
        label = "lower bound"
    else:
        e_before, e_first = E
        if s_first is not None and e_before is not None:
            at_least = max(0, days(s_first, e_before))
        if s_before is not None and e_first is not None:
            at_most = days(s_before, e_first)
        end_between_copies = e_before is not None and e_first is not None and e_before["kind"] == "copy" and e_first["kind"] == "copy"
        if None not in (s_before, s_first) and end_between_copies:
            label = "measured"
        elif not end_between_copies and at_most is not None:
            label, at_least = "upper bound", None
        else:
            label, at_most = "lower bound", None
    if copies_seen == 2:
        label, at_most = "two copies only", None
    if at_least is None and at_most is None:
        return None
    return at_least, at_most, label


def rank(o):
    """The stage class of an observation as a number 1 to 5; 0 for a request that has left, or words on no stage."""
    cls = stage_class(o["status_words"])[0]
    return int(cls[0]) if cls in STAGES else 0


def reach(obs, pred):
    """The first observation for which pred holds, as (the copy before it, that copy): the event came between the
    two. The copy before is None when pred already holds in the first copy that holds the request. None where pred
    never holds."""
    for i, o in enumerate(obs):
        if pred(o):
            return (bound(obs[i - 1]) if i else None, bound(o)), o
    return None, None


SIS_OPEN = re.compile(r"(?i)sris/sis (pending|in progress)|sris commenced")
INTERVALS = ["request to study", "request to agreement", "request to construction", "request to energized", "study to agreement",
             "agreement to energized", "request to withdrawal", "system impact study, pending or in progress to approved", "in stage",
             "in stage, then withdrawn"]


def durations(pub, rid, obs, latest_date):
    """Every stage interval of one followed request, as rows of the table without the provenance columns.

    Stage intervals, by the publisher's own status words placed on the five stages (the words kept). A stage is
    reached only where a copy shows it in the publisher's words; none is read into a request that skips it.
      request to study         the printed queue date, to the first copy that shows a study status (class 2)
      request to agreement     the printed queue date, to the first copy that shows a signed agreement (class 4)
      request to construction  the printed queue date, to the first copy that shows it under construction
      request to energized     the printed queue date, to the first copy that shows it in service
      study to agreement       the first copy that shows class 2, to the first that shows class 4
      agreement to energized   the first copy that shows class 4, to the first that shows it in service
      request to withdrawal    the printed queue date, to the first copy in which the publisher shows it withdrawn
      system impact study, pending or in progress to approved   (NYISO's words) the first copy that shows SRIS/SIS
                               Pending or in Progress, to the first that shows a later status
      in stage                 one row for each run of copies that show the same status words: from the copy before
                               the run and its first copy, to its last copy and the first copy after it
      in stage, then withdrawn the same, where the status after the run is the publisher's word for leaving the list
    A stage a request had already reached in the first copy that holds it has no bounded start. A request that has
    left the list (withdrawn) gives no lower bound for a stage it never reached."""
    e = ENTITIES[pub]
    n = len(obs)
    last = obs[-1]
    qd = last["queue_date"] if last["queue_date"] and len({o["queue_date"] for o in obs if o["queue_date"]}) == 1 else ""
    P = {"date": qd, "url": last["url"], "kind": "printed"} if qd else None
    start_request = (P, P) if P else (None, bound(obs[0]))
    left = bool(LEFT.search(last["status_words"]))
    gone = (not left) and last["date"] < latest_date      # no longer in the publisher's newest copy, and no word why
    mws = []
    for o in obs:
        if o["mw"] and (not mws or mws[-1][1] != o["mw"]):
            mws.append((o["date"], o["mw"]))
    mw_last = next((m for _, m in reversed(mws) if re.fullmatch(r"-?\d+(\.\d+)?", m)), "")
    names = []
    for o in obs:
        if o["name"] and o["name"] not in names:
            names.append(o["name"])
    base = dict(publisher=pub, entity=e["entity"], entity_group=e["group"], request_id=rid, request_id_as_printed=last["id_printed"], followed_by=e["id_name"],
                request_name=last["name"], request_names_seen=len(names), mw=mw_last, mw_first=mws[0][1] if mws else "", mw_last=mws[-1][1] if mws else "",
                mw_as_written_changes="; ".join(f"{d}: {m}" for d, m in mws) if len(mws) > 1 else "", size_class=size_class(mw_last),
                queue_date_printed=last["queue_date_printed"], copies_seen=n, first_copy_date=obs[0]["date"], last_copy_date=last["date"],
                status_in_last_copy=last["status_words"], source=e["source"])
    rows = []

    def add(interval, S, E, stage_words="", stage_code="", end_words="", note=""):
        got = measure(S, E, bound(last), n)
        if got is None:
            return
        at_least, at_most, label = got
        cls, why = stage_class(stage_words) if stage_words else ("", "")
        e_pair = E if E else (None, None)
        end = e_pair[1] or bound(last)
        row = dict(base, interval=interval, stage_as_worded=stage_words, stage_code=stage_code, stage_class=cls, stage_class_basis=why, end_as_worded=end_words,
                   days_at_least="" if at_least is None else at_least, days_at_most="" if at_most is None else at_most, label=label,
                   event_date=end["date"], source_url=end["url"], notes=note)
        for side, pair in (("start", S), ("end", e_pair)):
            for which, b in zip(("earlier", "later"), pair):
                row[f"{side}_{which}_date"] = b["date"] if b else ""
                row[f"{side}_{which}_basis"] = ("a copy" if b["kind"] == "copy" else "the queue date the copies print") if b else ""
                row[f"{side}_{which}_url"] = b["url"] if b else ""
        rows.append(row)

    def started(m):
        """A stage reached, as the start of an interval: where the request had already reached it in the first
        copy that holds it, the earlier bound is the printed queue date (a stage cannot begin before the request)."""
        return (m[0] or P, m[1])

    # A stage is reached only where a copy SHOWS it in the publisher's words: a request that goes from a study status
    # straight to in service never shows an agreement, and no agreement is read into it.
    in_service = lambda o: bool(IN_SERVICE.search(o["status_words"]))   # noqa: E731
    building = lambda o: rank(o) == 5 and not in_service(o)             # noqa: E731
    m_study, o_study = reach(obs, lambda o: rank(o) == 2)
    m_agree, o_agree = reach(obs, lambda o: rank(o) == 4)
    m_build, o_build = reach(obs, building)
    m_live, o_live = reach(obs, in_service)
    m_left, o_left = reach(obs, lambda o: bool(LEFT.search(o["status_words"])))
    top = max(rank(o) for o in obs)
    waiting = not left
    gone_note = "no longer in the publisher's newest copy; the copy prints no reason" if gone else ""

    def close(name, S, m, o_end, still_before):
        """One interval: to the milestone where a copy shows it; a lower bound where the request is still waiting
        and has shown nothing later than the stages before the milestone (still_before); otherwise no row."""
        if m:
            add(name, S, m, end_words=o_end["status_words"])
        elif waiting and still_before:
            add(name, S, None, note=gone_note)

    close("request to study", start_request, m_study, o_study, top < 2)
    close("request to agreement", start_request, m_agree, o_agree, top < 4)
    close("request to construction", start_request, m_build, o_build, top < 5)
    close("request to energized", start_request, m_live, o_live, True)
    if m_study:
        close("study to agreement", started(m_study), m_agree, o_agree, top < 4)
    if m_agree:
        close("agreement to energized", started(m_agree), m_live, o_live, True)
    if m_left:
        add("request to withdrawal", start_request, m_left, end_words=o_left["status_words"])
    m_sis, _ = reach(obs, lambda o: bool(SIS_OPEN.search(o["status_words"])))
    if m_sis:
        after = [o for o in obs if o["date"] >= m_sis[1]["date"]]
        m_done, o_done = reach(after, lambda o: not SIS_OPEN.search(o["status_words"]) and not LEFT.search(o["status_words"]) and rank(o) >= 2)
        if m_done:
            add("system impact study, pending or in progress to approved", started(m_sis), m_done, end_words=o_done["status_words"])
        elif waiting:
            add("system impact study, pending or in progress to approved", started(m_sis), None, note=gone_note)
    # one row for each run of copies that show the same status words
    runs = []
    for o in obs:
        if runs and (runs[-1][0]["status_code"], runs[-1][0]["status_words"]) == (o["status_code"], o["status_words"]):
            runs[-1].append(o)
        else:
            runs.append([o])
    for k, run in enumerate(runs):
        words = run[0]["status_words"]
        if LEFT.search(words) or IN_SERVICE.search(words) or not words:
            continue   # the end of a wait, not a stage of it
        if k:
            S = (bound(runs[k - 1][-1]), bound(run[0]))
        elif P and stage_class(words)[0] == STAGES[0]:
            S = (P, P)   # the request stage begins with the request: its printed queue date
        else:
            S = (P, bound(run[0]))   # already in this stage in the first copy that holds it: it began after the printed queue date
        if k + 1 < len(runs):
            E, end_words = (bound(run[-1]), bound(runs[k + 1][0])), runs[k + 1][0]["status_words"]
        else:
            E, end_words = None, ""
        add("in stage, then withdrawn" if LEFT.search(end_words) else "in stage", S, E, stage_words=words, stage_code=run[0]["status_code"], end_words=end_words,
            note=gone_note if E is None else "")
    return rows


def median(values):
    v = sorted(values)
    m = len(v) // 2
    return v[m] if len(v) % 2 else (v[m - 1] + v[m]) / 2


MIN_FOR_MEDIAN = 5


def figure(rows):
    """One figure from the rows of one group: the count behind it, and what may be said of it. Measured durations
    are ranges (at least, at most): with MIN_FOR_MEDIAN or more the median of the at-least values, the median of the
    at-most values and the whole range are given; with fewer, the individual ranges and no median. Lower bounds
    (and requests seen in two copies only) are counted apart, with the range of their at-least values: they are
    never averaged, and never mixed with the measured ones."""
    meas = [(r["days_at_least"], r["days_at_most"]) for r in rows if r["label"] == "measured"]
    low = sorted(r["days_at_least"] for r in rows if r["label"] == "lower bound" and r["days_at_least"] != "")
    two = sorted(r["days_at_least"] for r in rows if r["label"] == "two copies only" and r["days_at_least"] != "")
    up = sorted(r["days_at_most"] for r in rows if r["label"] == "upper bound" and r["days_at_most"] != "")
    out = dict(measured_n=len(meas), measured_median_at_least="", measured_median_at_most="", measured_range="", measured_values="",
               lower_bound_n=len(low), lower_bound_range=f"{low[0]} to {low[-1]}" if low else "",
               two_copies_only_n=len(two), two_copies_only_range=f"{two[0]} to {two[-1]}" if two else "",
               upper_bound_n=len(up), upper_bound_range=f"{up[0]} to {up[-1]}" if up else "")
    if meas:
        out["measured_range"] = f"{min(a for a, _ in meas)} to {max(b for _, b in meas)}"
        if len(meas) >= MIN_FOR_MEDIAN:
            out["measured_median_at_least"] = median([a for a, _ in meas])
            out["measured_median_at_most"] = median([b for _, b in meas])
        else:
            out["measured_values"] = "; ".join(f"{a} to {b}" for a, b in sorted(meas))
    return out


def figures(rows):
    """The figures by entity, interval (and stage words, for the rows in a stage) and size class, and for all sizes."""
    groups = {}
    for r in rows:
        for size in ("all sizes", r["size_class"]):
            groups.setdefault((r["entity"], r["interval"], r["stage_as_worded"], r["stage_class"], size), []).append(r)
    out = []
    for (entity, interval, words, cls, size), rs in groups.items():
        out.append(dict(dict(entity=entity, interval=interval, stage_as_worded=words, stage_class=cls, size_class=size, requests=len(rs)), **figure(rs)))
    order = {n: i for i, n in enumerate(INTERVALS)}
    sizes = ["all sizes"] + [s[0] for s in SIZE_CLASSES] + ["megawatts not a number"]
    out.sort(key=lambda f: (f["entity"], order.get(f["interval"], 99), f["stage_class"], f["stage_as_worded"], sizes.index(f["size_class"])))
    return out


# what the same entity said to expect (large_load_statements, wait_figures.csv), beside the interval measured here that
# covers the same step: (entity group, the duration as written, its days, how the days were got, the interval, what differs)
# (entity group, the duration as written, its days, how the days were got, [(interval, stage words or "")], what differs)
SIS_WHOLE = ("system impact study, pending or in progress to approved", "")
SIS_RUNNING = ("in stage", "SRIS/SIS in Progress")
EXPECTED = [
    ("New York ISO", "nine months", 274, "nine calendar months at 365.25 / 12 days a month, rounded", [SIS_WHOLE, SIS_RUNNING],
     "the statement runs from the customer's study selection to the study's completion; no copy shows the day of the selection, so two measures stand "
     "beside it: from the first copy that shows SRIS/SIS Pending or in Progress to the first that shows a later status, and the time shown as SRIS/SIS in Progress alone"),
    ("New York ISO", "90-day", 90, "as written", [SIS_WHOLE, SIS_RUNNING],
     "the statement is a step of a procedure NYISO has proposed, not the one these requests went through"),
    ("New York ISO", "2 weeks", 14, "two weeks of seven days", [],
     "no comparison: the statement runs from NYISO finding a request complete to its scheduling a scoping call, and no copy shows either day"),
]


def compare(rows, wait_figures):
    """Each stated expectation of an entity measured here, beside the measured interval for the same step. A
    measured duration is a range: it is above the stated figure when even its at-least is longer, below when even
    its at-most is shorter, and otherwise the stated figure lies inside the range and the two cannot be told
    apart. Lower bounds are counted apart: how many are already longer than the stated figure. No ranking across
    entities. Returns (comparisons, entities measured with no stated expectation)."""
    stated = {}
    for f in wait_figures:
        if f.get("wait_basis") == "expected" and f.get("wait_counted") == "yes" and not f.get("load_scope", "").startswith("all distribution"):
            stated.setdefault(f["wait_figure"].split(" | ")[0], []).append(f)
    out = []
    measured_groups = sorted({r["entity_group"] for r in rows})
    for group in measured_groups:
        for f in stated.get(group, []):
            spec = next((x for x in EXPECTED if x[0] == group and x[1].lower() == squeeze(f["quantity_as_written"]).lower()), None)
            base = dict(entity_group=group, stated_as_written=f["quantity_as_written"], stated_stage=f.get("status", ""), stated_stage_class=f.get("stage_class", ""),
                        stated_date=f.get("event_date", ""), stated_source_url=f.get("source_url", ""), stated_days="", stated_days_how="", measured_interval="",
                        measured_stage_as_worded="", measured_n="", above="", below="", inside="", lower_bounds_n="", lower_bounds_already_longer="", comparison="")
            if spec is None:
                out.append(dict(base, comparison="no comparison: no interval measured here covers this step"))
                continue
            base.update(stated_days=spec[2], stated_days_how=spec[3], comparison=spec[5])
            if not spec[4]:
                out.append(base)
            for interval, words in spec[4]:
                mine = [r for r in rows if r["entity_group"] == group and r["interval"] == interval and (not words or r["stage_as_worded"] == words)]
                meas = [r for r in mine if r["label"] == "measured"]
                low = [r for r in mine if r["label"] in ("lower bound", "two copies only") and r["days_at_least"] != ""]
                row = dict(base, measured_interval=interval, measured_stage_as_worded=words, measured_n=len(meas),
                           above=sum(1 for r in meas if r["days_at_least"] > spec[2]), below=sum(1 for r in meas if r["days_at_most"] < spec[2]),
                           lower_bounds_n=len(low), lower_bounds_already_longer=sum(1 for r in low if r["days_at_least"] > spec[2]))
                row["inside"] = row["measured_n"] - row["above"] - row["below"]
                out.append(row)
    return out, [g for g in measured_groups if not stated.get(g)]


# ---------------------------------------------------------------------------
# The current copies and the terms pages
# ---------------------------------------------------------------------------

CURRENT = {
    "nyiso": "https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx",
    "grantpud_page": "https://www.grantpud.org/transmission-information",
    # session 160: the task force that held the status updates from 2022 to 2024 (ERCOT lists it as inactive), and the service page
    "ercot_pages": ["https://www.ercot.com/committees/tac/llwg", "https://www.ercot.com/committees/tac",
                    "https://www.ercot.com/committees/inactive/lfltf", "https://www.ercot.com/services/rq/large-load-integration"],
}
ERCOT_MEETING = re.compile(r'(?:https://www\.ercot\.com)?(/calendar/(\d{2})(\d{2})(\d{4})-(?:Special-)?(?:LLWG|TAC|LFLTF)-Meeting[^"\s]*)"')
# a committee page's own earlier years (session 160): /committees/tac/llwg/2025, /committees/inactive/lfltf/2022
ERCOT_YEAR = re.compile(r'href="(?:https://www\.ercot\.com)?(/committees/(?:tac/llwg|tac|inactive/lfltf)/(20\d\d))"')
FIRST_YEAR = 2022   # the interim large load interconnection process began in March 2022
# the terms pages, and the sentences quoted from each: a quoted sentence must stand in the saved page word for word
TERMS = {
    "internet_archive": dict(
        who="Internet Archive", url="https://archive.org/about/terms.php", ask="https://web.archive.org/web/20240601000000id_/https://archive.org/about/terms.php",
        note="the Archive's page is drawn by a script today and a plain request returns no text: the text read is the Archive's own capture of its page "
             "(1 June 2024), which prints: Terms of Use, 31 Dec 2014",
        quotes=[
            "Access to the Archive\u2019s Collections is provided at no cost to you and is granted for scholarship and research purposes only.",
            "You agree to abide by all applicable laws and regulations, including intellectual property laws, in connection with your use of the Archive.",
            "In particular, you certify that your use of any part of the Archive's Collections will be limited to noninfringing or fair use under copyright law.",
            "In addition, we request that, according to standard academic practice, if you use the Archive's Collections for any research that results in an "
            "article, a book, or other publication, you list the Archive as a resource in your bibliography.",
        ]),
    "nyiso": dict(
        who="NYISO", url="https://www.nyiso.com/legal-notice", ask="", saved_in="nyiso_load_queue",
        note="saved and read by session 149 (nyiso_load_queue.py --terms); no new request",
        quotes=[
            "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential "
            "or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety.",
            "Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as a stand-alone file is strictly prohibited",
        ]),
    "grantpud": dict(
        who="Grant County PUD", url="https://www.grantpud.org/statement-of-privacy", ask="https://www.grantpud.org/statement-of-privacy",
        note="the one legal page the site's footer links; it is a privacy statement, and the site states no terms of use for its documents",
        quotes=[
            "All information collected at this Web site or through this Service becomes a public record that may be subject to inspection by the public unless "
            "an exemption in law exists.",
            "\u00a9 Public Utility District No. 2 of Grant County, WA, All Rights Reserved",
        ]),
    "ercot": dict(
        who="ERCOT", url="https://www.ercot.com/help/terms", ask="https://www.ercot.com/help/terms", note="the sentences session 144 quoted, checked in the page as it reads today",
        quotes=[
            "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that "
            "you maintain all copyright and other notices contained in the contents, including this Agreement.",
            "Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, "
            "charts, and analyses without maintaining such notices.",
        ]),
}


def page_text(content):
    """A web page's visible text, white space collapsed (scripts, styles and tags dropped)."""
    import html
    t = content.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", t)
    t = html.unescape(re.sub(r"(?s)<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


def do_pull_current(raw, net, log, ip=None, only=()):
    """The current copies, by plain request to each publisher: NYISO's workbook; the queue that Grant County PUD's
    transmission page links (the PDF whose name says it is the queue, nothing else in its folder); ERCOT's status
    updates on the pages of the meetings its committee pages list (session 160: each committee page's earlier years
    too, back to 2022, and the task force ERCOT lists as inactive). A publisher that is paused is not asked; only:
    the publishers this run may ask (empty: all). An address already saved with a 200 is not asked for again."""
    def paused(scope):
        return ip is not None and ip.paused(scope)

    def on(pub):
        return not only or pub in only
    held = {r["original"] for r in read_captures(raw) if r["status"] == "200" and r["file"] and not r["archive_url"]
            and re.search(r"(?i)\.(pdf|pptx|docx|zip|xlsx?)(\?|$)", r["original"])}
    try:
        if on("nyiso"):
            if paused("nyiso"):
                log("current nyiso: " + ip.pause_line("nyiso"))
            else:
                st, content, fname = do_fetch_current(raw, net, log, "nyiso", CURRENT["nyiso"])
                log(f"current nyiso: {st}, {len(content):,} bytes, {fname}")
        if on("grantpud"):
            st, content, _ = do_fetch_current(raw, net, log, "grantpud", CURRENT["grantpud_page"], kind="page that links the current copy", rows_reserve=0)
            n = 0
            for href in sorted(set(re.findall(r'href="([^"]+)"', content.decode("utf-8", "replace")))):
                url = (href if href.startswith("http") else "https://www.grantpud.org" + href).replace(" ", "%20")
                if WANTED["grantpud"].search(url) and not NOT_WANTED.search(url):
                    n += 1
                    if url in held:
                        log(f"current grantpud: {url} is already saved from the publisher; not asked for again")
                        continue
                    st, body, fname = do_fetch_current(raw, net, log, "grantpud", url)
                    log(f"current grantpud: {url} -> {st}, {len(body):,} bytes, {fname}")
            if not n:
                log(f"current grantpud: the page answered {st} with {len(content):,} bytes and links no queue file: {page_text(content)[:160]!r}")
        if not on("ercot"):
            return
        if paused("ercot"):
            log("current ercot: " + ip.pause_line("ercot"))
            return
        seen = set()
        today = now_utc().strftime("%Y%m%d")
        for index in CURRENT["ercot_pages"]:
            st, content, _ = do_fetch_current(raw, net, log, "ercot", index, kind="page that lists the meetings", rows_reserve=0)
            pages = [content]
            own = index.replace("https://www.ercot.com", "")
            for path, year in sorted(set(ERCOT_YEAR.findall(content.decode("utf-8", "replace")))):
                if path.rsplit("/", 1)[0] != own or int(year) < FIRST_YEAR or path in seen:
                    continue
                if own == "/committees/tac" and int(year) < 2025:
                    continue   # the status update reached TAC's meetings with the working group in 2025; before, it was the task force's
                seen.add(path)
                st, more, _ = do_fetch_current(raw, net, log, "ercot", "https://www.ercot.com" + path, kind="page that lists the meetings of an earlier year", rows_reserve=0)
                pages.append(more)
            docs = set()
            for page in pages:
                text = page.decode("utf-8", "replace")
                docs |= set(re.findall(r'href="([^"]+\.(?:pdf|pptx|docx|zip))"', text, re.I))   # a status report the committee page links itself
                for path, mm, dd, yyyy in sorted(set(ERCOT_MEETING.findall(text))):
                    if path in seen or f"{yyyy}{mm}{dd}" > today or int(yyyy) < FIRST_YEAR:
                        continue
                    seen.add(path)
                    st, meeting, _ = do_fetch_current(raw, net, log, "ercot", "https://www.ercot.com" + path, kind="meeting page", rows_reserve=0)
                    docs |= set(re.findall(r'href="([^"]+\.(?:pdf|pptx|docx|zip))"', meeting.decode("utf-8", "replace"), re.I))
            for href in sorted(docs):
                url = (href if href.startswith("http") else "https://www.ercot.com" + href).replace(" ", "%20")
                if "ercot.com/" not in url or not WANTED["ercot"].search(url) or NOT_WANTED.search(url) or url in seen:
                    continue
                seen.add(url)
                if url in held:
                    log(f"current ercot: {url} is already saved from the publisher; not asked for again")
                    continue
                do_fetch_current(raw, net, log, "ercot", url)
    except Refused as e:
        log(f"current copies: REFUSED before the request: {e}")


def do_terms(raw, net, log):
    """One request a terms page; each saved under terms/ with its hash in captures.csv; each quoted sentence must
    stand in the saved page word for word, or the stage says which does not."""
    missing = []
    for name, t in TERMS.items():
        if not t["ask"]:
            continue   # saved by an earlier session: read from its raw folder, not asked for again
        try:
            status, content, headers = net.get(t["ask"], "terms page")
        except Refused as e:
            log(f"terms {name}: REFUSED before the request: {e}")
            continue
        ts = now_utc().strftime("%Y%m%d%H%M%S")
        fname = save_answer(raw, "terms", ts, name + ".html", content) if status == "200" and content else ""
        append_capture(raw, dict(publisher="terms", original=t["url"], capture=ts, archive_url=t["ask"] if "web.archive.org" in t["ask"] else "", bytes=len(content),
                                 sha256=hashlib.sha256(content).hexdigest() if content else "", retrieved_at=stamp(), status=status, file=fname,
                                 note=("terms page. " + t["note"] + " " + headers.get("Memento-Datetime", headers.get("memento-datetime", ""))).strip()))
        text = page_text(content)
        for q in t["quotes"]:
            ok = q in text
            log(f"terms {name}: {'found' if ok else 'NOT FOUND'} word for word: \"{q}\"")
            if not ok:
                missing.append((name, q))
    if missing:
        raise RuntimeError(f"{len(missing)} quoted sentence(s) are not in the terms page as saved: {missing[0][0]}: {missing[0][1][:80]!r}")


def terms_saved(raw):
    """No request. The saved copy of each terms page that holds its quoted sentences, with its sha256, retrieval
    time and whether each quoted sentence stands in it word for word: a list of dicts (name, who, url, file, sha256,
    retrieved_at, note, quotes [(sentence, found)])."""
    out = []
    caps = [c for c in read_captures(raw) if c["publisher"] == "terms" and c["file"] and c["status"] == "200"]
    for name, t in TERMS.items():
        cands = []
        if t.get("saved_in"):   # another connector's raw folder, beside this one
            d = os.path.join(os.path.dirname(raw), t["saved_in"])
            m = os.path.join(d, "manifest.csv")
            if os.path.exists(m):
                with open(m, encoding="utf-8", newline="") as f:
                    cands = [(os.path.join(d, r["file"]), f"{t['saved_in']}/{r['file']}", r["sha256"], r["retrieved_at"]) for r in csv.DictReader(f)
                             if r["url"] == t["url"] and r["status"] == "200"]
        else:
            cands = [(os.path.join(raw, c["file"]), c["file"], c["sha256"], c["retrieved_at"]) for c in caps if c["original"] == t["url"]]
        best = None
        for path, fname, sha, got in cands:
            if not os.path.exists(path):
                continue
            with open(path, "rb") as f:
                text = page_text(f.read())
            found = [(q, q in text) for q in t["quotes"]]
            if best is None or all(ok for _, ok in found):
                best = dict(name=name, who=t["who"], url=t["url"], file=fname, sha256=sha, retrieved_at=got, note=t["note"], quotes=found)
        out.append(best or dict(name=name, who=t["who"], url=t["url"], file="", sha256="", retrieved_at="", note="no saved page on this machine", quotes=[(q, False) for q in t["quotes"]]))
    return out


# ---------------------------------------------------------------------------
# The table
# ---------------------------------------------------------------------------

EVENTS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
EXTRA = ["entity", "entity_group", "request_id", "request_id_as_printed", "followed_by", "request_name", "request_names_seen", "mw_first", "mw_last",
         "mw_as_written_changes", "size_class", "queue_date_printed", "interval", "stage_as_worded", "stage_code", "stage_class", "stage_class_basis",
         "end_as_worded", "start_earlier_date", "start_earlier_basis", "start_earlier_url", "start_later_date", "start_later_basis", "start_later_url",
         "end_earlier_date", "end_earlier_basis", "end_earlier_url", "end_later_date", "end_later_basis", "end_later_url", "days_at_least", "days_at_most",
         "label", "copies_seen", "first_copy_date", "last_copy_date", "status_in_last_copy", "retrieved_at", "notes"]
COLS = EVENTS + EXTRA
LABELS = ["measured", "lower bound", "two copies only", "upper bound"]


def build(raw, log):
    """Everything the table is made of, with nothing written and no request made: the copies read, the requests
    followed and not, the rows."""
    copies, unread = read_copies(raw, log)
    followed, not_followed = follow(copies)
    latest = {}
    for c in copies:
        latest[c["publisher"]] = max(latest.get(c["publisher"], ""), c["date"])
    # session 160: a row's retrieved_at is the last retrieval of a copy of ITS publisher's queue. Before, it was the last
    # retrieval of anything in the store, so reading ERCOT's reports again would have marked every New York row as changed.
    got = {}
    for c in copies:
        for cap in c["captures"]:
            got[c["publisher"]] = max(got.get(c["publisher"], ""), cap["retrieved_at"])
    rows = []
    for (pub, rid), obs in sorted(followed.items()):
        for r in durations(pub, rid, obs, latest[pub]):
            key = "|".join([pub, rid, r["interval"], r["stage_as_worded"], r["start_later_date"]])
            r.update(event_id="llwait:" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:16], event_type="large_load_wait", parties=r["entity"], entity_ids="",
                     price="", currency="", status=r["stage_as_worded"] or r["status_in_last_copy"], retrieved_at=got.get(pub) or stamp(),
                     mw=float(r["mw"]) if r["mw"] else "")
            rows.append(r)
    ids = [r["event_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("two rows share an id; nothing is written")
    seen = {}
    for c in copies:
        for r in c["rows"]:
            seen.setdefault(c["publisher"], set()).add(r["id"])
    return dict(copies=copies, unread=unread, followed=followed, not_followed=not_followed, rows=rows, seen=seen, latest=latest)


def counts_of(b, comparison, no_expectation):
    """The counts the summary gives, from the table's rows alone (and the copies read): no request is named."""
    rows = b["rows"]
    out = {"copies": {}, "requests": {}, "rows": len(rows), "rows_by_label": {k: sum(1 for r in rows if r["label"] == k) for k in LABELS},
           "rows_by_entity": {}, "figures": [f for f in figures(rows) if f["size_class"] == "all sizes"], "comparison": comparison,
           "entities_with_no_stated_expectation": no_expectation}
    for pub, e in ENTITIES.items():
        mine = [c for c in b["copies"] if c["publisher"] == pub]
        out["copies"][e["entity"]] = {"read": len(mine), "not_read": sum(1 for u in b["unread"] if u["publisher"] == pub),
                                      "first": mine[0]["date"] if mine else "", "last": mine[-1]["date"] if mine else "",
                                      "request_rows": sum(len(c["rows"]) for c in mine)}
        nf = {}
        for n in b["not_followed"]:
            if n["publisher"] == pub:
                nf[n["why"]] = nf.get(n["why"], 0) + 1
        fol = [k for k in b["followed"] if k[0] == pub]
        last = {k: b["followed"][k][-1] for k in fol}
        out["requests"][e["entity"]] = {
            "seen": len(b["seen"].get(pub, ())), "followed": len(fol), "not_followed": nf,
            "in_service_in_last_copy": sum(1 for o in last.values() if IN_SERVICE.search(o["status_words"])),
            "withdrawn_in_last_copy": sum(1 for o in last.values() if LEFT.search(o["status_words"])),
            "megawatts_changed": sum(1 for k in fol if len({o["mw"] for o in b["followed"][k] if o["mw"]}) > 1),
            "seen_in_two_copies_only": sum(1 for k in fol if len(b["followed"][k]) == 2)}
        out["rows_by_entity"][e["entity"]] = sum(1 for r in rows if r["publisher"] == pub)
    return out


def write_beside(d, b, figs, comparison, counts):
    """The working files beside the table (not in git): every copy, every request's row in every copy, the requests
    not followed, the figures, the comparison and the summary's counts."""
    os.makedirs(d, exist_ok=True)

    def dump(name, cols, rows):
        with open(os.path.join(d, name), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    dump(f"{NAME}_copies.csv", ["publisher", "date", "stamp", "date_basis", "url", "held_by", "file", "sha256", "rows", "captures", "notes"],
         [dict(c, rows=len(c["rows"]), captures=len(c["captures"]), notes="; ".join(c["notes"])) for c in b["copies"]] +
         [dict(u, date="", stamp="", date_basis="", url="", rows=0, captures=len(u["captures"]), notes="not read: " + u["why"]) for u in b["unread"]])
    obs = [dict(o, publisher=c["publisher"], copy_date=c["date"], copy_url=c["url"]) for c in b["copies"] for o in c["rows"]]
    dump(f"{NAME}_observations.csv", ["publisher", "copy_date", "copy_url", "sheet", "id", "id_printed", "name", "developer", "mw", "queue_date_printed",
                                      "queue_date", "status_code", "status_words"], obs)
    dump(f"{NAME}_not_followed.csv", ["publisher", "id", "copies_seen", "first_copy", "last_copy", "why"], b["not_followed"])
    dump(f"{NAME}_figures.csv", list(figs[0]) if figs else ["entity"], figs)
    dump(f"{NAME}_comparison.csv", list(comparison[0]) if comparison else ["entity_group"], comparison)
    # session 160: ERCOT's status reports, one a report day, with what each holds (system totals; no request)
    dump(f"{NAME}_ercot_reports.csv", ["day", "document", "held_by", "where", "sha256", "pages", "names_a_request", "approved_to_energize_mw",
                                       "observed_consuming_mw", "observed_basis", "sentence", "stages_named"],
         [dict(r, stages_named="; ".join(r["stages_named"])) for r in counts.get("ercot", {}).get("reports", [])])
    with open(os.path.join(d, f"{NAME}_counts.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(counts, f, indent=1)


def count_rows(raw, log):
    """copies.csv in the raw store: the rows of each distinct copy, so that the ceiling counts what was read."""
    copies, unread = read_copies(raw, log)
    with open(os.path.join(raw, "copies.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["publisher", "sha256", "file", "date", "rows", "note"], lineterminator="\n")
        w.writeheader()
        for c in copies:
            w.writerow(dict(publisher=c["publisher"], sha256=c["sha256"], file=c["file"], date=c["date"], rows=len(c["rows"]), note="; ".join(c["notes"])))
        for u in unread:
            w.writerow(dict(publisher=u["publisher"], sha256=u["sha256"], file=u["file"], date="", rows=0, note="not read: " + u["why"]))
        done = set()
        for c in read_captures(raw):   # ERCOT's reports list no request: each counts no row
            if c["publisher"] == "ercot" and c["file"] and c["sha256"] not in done and WANTED["ercot"].search(c["original"]) and not NOT_WANTED.search(c["original"]):
                done.add(c["sha256"])
                w.writerow(dict(publisher="ercot", sha256=c["sha256"], file=c["file"], date="", rows=0, note="system totals by stage: no request is listed"))
    total = sum(len(c["rows"]) for c in copies)
    log(f"count: {len(copies)} copies read, {len(unread)} not read; {total:,} rows of requests against a ceiling of {CEILING_ROWS:,}")
    return total


def header_lines(run_id, b, counts):
    c = counts
    per = "; ".join(f"{e}: {v['read']} copies read ({v['first']} to {v['last']}), {c['requests'][e]['seen']} requests seen, {c['requests'][e]['followed']} followed"
                    for e, v in c["copies"].items())
    return [
        "Energy Research Warehouse (ERW): how long large loads waited, measured from successive dated copies of public queues (session 155)",
        "Shape: events (docs/datastandard.md v0), event_type large_load_wait. One row a request and stage interval: the entity, the request's identifier, "
        "megawatts as written in the last copy that holds it, the stage in the publisher's words (status, stage_as_worded) and its class beside them, the two "
        "bounds of the start and the two of the end (a copy's date and address, or the queue date the copies print), and the duration's range in days.",
        "A DURATION IS A RANGE, NEVER A MIDPOINT. days_at_least: the later bound of the start to the earlier bound of the end. days_at_most: the earlier bound of "
        "the start to the later bound of the end. label: measured (the end lies between two copies that hold the request and the start is printed or bounded); "
        "lower bound (the end has not come, or a side is not bounded: days_at_least only); two copies only (the request is seen in two copies: days_at_least "
        "only); upper bound (the end had come before the first copy that holds the request: days_at_most only). Nothing is interpolated. Do not average lower bounds.",
        "event_date: the later bound of the interval's end, or the last copy that holds the request where the end has not come. A copy's date is the publisher's own "
        "(NYISO: the day the workbook was last saved, or its Last-Modified for the .xls workbooks; Grant County PUD: the day printed on the copy), never the day "
        "the Internet Archive captured it.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/large_load_waits.py from the copies saved under warehouse/raw/large_load_waits (not in git): "
        "captures.csv lists each with its address at the Internet Archive, digest, bytes, sha256 and retrieval time",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        "Source: the Internet Archive's Wayback Machine (web.archive.org) and the publishers' own sites for the current copies. "
        "nyiso:interconnection_queue_dated_copies: NYISO Interconnection Queue workbook, the sheet Load Projects and the rows of type L of the other sheets. "
        "grantpud:interconnection_queue_dated_copies: Grant PUD Interconnection Queue (PDF), the rows of type Load. ERCOT's large load status reports list no "
        "request (system totals by stage): no row comes from them.",
        f"This run: {per}. {len(b['rows'])} rows: " + ", ".join(f"{k} {v}" for k, v in c["rows_by_label"].items()) + "."
        + (f" ERCOT (session 160): {c['ercot']['status_reports']} status reports read ({c['ercot']['first']} to {c['ercot']['last']}), "
           f"{c['ercot'].get('reports_naming_a_request', 0)} name a request, no row." if c.get("ercot") else ""),
        "License: internal. NYISO's legal notice confers no license in the content of its site and reserves all rights (session 149); Grant County PUD's site "
        "states no terms of use for its documents. Not on the site, not in a public Redivis dataset, not in the live set. A person can rule otherwise.",
    ]


# the queues that could be followed next: (the listing's name under listings/, the publisher, a pattern for the queue's own
# file among the addresses listed, what is known of it without opening a copy)
OTHER_QUEUES = [
    ("other-bpa2", "Bonneville Power Administration", r"(?i)InterconnectionQueueOutput\.xlsx?$",
     "its interconnection queue workbook (generation, and line and load interconnections). Not opened: whether each load request carries its own number is to be confirmed on the first copy"),
    ("other-bpa3", "Bonneville Power Administration (its earlier transmission site)", r"(?i)InterconnectionQueueOutput\.xlsx?$",
     "the same workbook at its address of 2011 to 2013"),
    ("other-aeso", "Alberta Electric System Operator (Canada, not the United States)", r"(?i)Project-List\.xlsx?$",
     "its monthly connection project list (loads and generators), one file a month, each with its month in its name. Not opened"),
]


def other_queues(raw):
    """From the saved listings of other publishers (listings only: no copy of theirs was fetched): the dated copies
    the Internet Archive lists for each queue file, with the first and the last capture."""
    by = {x["publisher"]: x for x in saved_listings(raw)}
    out = []
    for name, who, pattern, what in OTHER_QUEUES:
        lst = by.get(name)
        if not lst:
            continue
        caps = [c for c in lst["captures"] if re.search(pattern, c["original"].split("?")[0])]
        if not caps:
            continue
        out.append(dict(publisher=who, listed=lst["url"], addresses=len({c["original"].split("?")[0].lower() for c in caps}), captures=len(caps),
                        distinct=len({c["digest"] for c in caps}), first=min(c["timestamp"] for c in caps)[:8], last=max(c["timestamp"] for c in caps)[:8], what=what))
    empty = sorted(x["url"] for x in saved_listings(raw) if x["publisher"].startswith("other-") and not x["captures"])
    return out, empty


def day_range(f, n_key, range_key):
    return f"{f[n_key]} ({f[range_key]})" if f[n_key] else "0"


def summary_lines(counts):
    """The lines of numbers the one-page summary carries, made from the table's counts and nothing else, so that a
    test can hold the page to the table. No request is named and no megawatt is given."""
    c = counts
    lines = []
    for e, v in c["copies"].items():
        r = c["requests"][e]
        nf = "; ".join(f"{k}: {n}" for k, n in r["not_followed"].items()) or "none"
        lines.append(f"- **{e}**: {v['read']} dated copies read, {v['first']} to {v['last']}" + (f" ({v['not_read']} more could not be read)" if v["not_read"] else "")
                     + f"; load requests: {r['seen']} seen, **{r['followed']} followed**, {r['seen'] - r['followed']} not ({nf}); "
                     f"{r['in_service_in_last_copy']} in service and {r['withdrawn_in_last_copy']} withdrawn in the last copy.")
    lines.append(f"- **The table**: {c['rows']} rows, one a request and stage interval: " + ", ".join(f"{k} {n}" for k, n in c["rows_by_label"].items()) + ".")
    lines.append("")
    lines.append("| Entity | Interval, or the stage as worded | Requests | Measured | Measured, days | Lower bounds, days at least | Two copies only | Upper bounds, days at most |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for f in c["figures"]:
        what = f["interval"] if not f["stage_as_worded"] else f"{f['interval']}: {f['stage_as_worded']}"
        if f["measured_n"] >= MIN_FOR_MEDIAN:
            meas = f"median at least {f['measured_median_at_least']:g}, at most {f['measured_median_at_most']:g}; all within {f['measured_range']}"
        else:
            meas = f["measured_values"] or ""
        lines.append(f"| {f['entity']} | {what} | {f['requests']} | {f['measured_n']} | {meas} | {day_range(f, 'lower_bound_n', 'lower_bound_range')} | "
                     f"{day_range(f, 'two_copies_only_n', 'two_copies_only_range')} | {day_range(f, 'upper_bound_n', 'upper_bound_range')} |")
    return lines


TEXAS_GROUPS = ("ERCOT", "Oncor Electric Delivery")


def texas_stated(stated):
    """The wait figures large_load_statements holds for ERCOT and for Oncor (wait_figures.csv), as written: what the
    measurement is set beside. Nothing is converted and nothing is ranked."""
    out = []
    for f in stated:
        if f.get("entity_group") in TEXAS_GROUPS and f.get("wait_counted") == "yes":
            out.append(dict(entity_group=f["entity_group"], as_written=f["quantity_as_written"], basis=f["wait_basis"], what=f["status"],
                            stage_class=f["stage_class"], date=f["event_date"], source_url=f["source_url"], page=f.get("page", "")))
    out.sort(key=lambda x: (x["entity_group"] != "Oncor Electric Delivery", x["basis"] != "measured", x["date"], x["as_written"]))
    return out


def texas_lines(counts):
    """The Texas lines of the one-page summary (session 160), made from the counts and nothing else."""
    e = counts["ercot"]
    lines = [f"- **ERCOT**: {e['status_reports']} large load status reports read, {e['first']} to {e['last']} "
             f"({e.get('held_by_archive', 0)} held by the Internet Archive, {e.get('held_by_publisher', 0)} read from ERCOT); "
             f"reports that name a request: {e.get('reports_naming_a_request', 0)}; requests followed: {e['requests_listed']}; measured waits: none."]
    with_totals = [r for r in e["reports"] if r.get("approved_to_energize_mw")]
    if with_totals:
        a, z = with_totals[0], with_totals[-1]
        lines.append(f"- What the reports do print, for the whole system ({len(with_totals)} of the {e['status_reports']} write the sentence out): on {a['day']}, "
                     f"{int(a['approved_to_energize_mw']):,} MW approved to energize and {int(a['observed_consuming_mw']):,} MW observed consuming ({a['observed_basis']}); "
                     f"on {z['day']}, {int(z['approved_to_energize_mw']):,} MW and {int(z['observed_consuming_mw']):,} MW ({z['observed_basis']}). "
                     "A total over time is not a request's wait: no wait is made from it.")
    for x in counts.get("texas_stated", []):
        lines.append(f"- **{x['entity_group']}** wrote \"{x['as_written']}\" ({x['basis']}; {x['what']}; {x['date']}).")
    return lines


def comparison_lines(counts):
    lines = []
    for x in counts["comparison"]:
        head = f"- **{x['entity_group']}** said \"{x['stated_as_written']}\" ({x['stated_stage']}, {x['stated_date']})"
        if x["measured_interval"]:
            what = x["measured_interval"] + (f": {x['measured_stage_as_worded']}" if x["measured_stage_as_worded"] else "")
            lines.append(f"{head}, taken as {x['stated_days']} days. Measured, {what}: {x['measured_n']} durations, {x['above']} above, {x['below']} below, "
                         f"{x['inside']} with the stated figure inside the measured range; {x['lower_bounds_n']} lower bounds, {x['lower_bounds_already_longer']} already longer.")
        else:
            lines.append(f"{head}: {x['comparison']}.")
    for g in counts["entities_with_no_stated_expectation"]:
        lines.append(f"- **{g}** states no expectation of a wait in the table: no comparison.")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true", help="the Internet Archive's listings of each address (one request an address)")
    ap.add_argument("--pull", action="store_true", help="each distinct capture once, and the current copies from the publishers")
    ap.add_argument("--terms", action="store_true", help="the Archive's and the publishers' terms pages, saved with their hashes, the quoted sentences checked")
    ap.add_argument("--count", action="store_true", help="read the saved copies and write copies.csv in the raw store; no request")
    ap.add_argument("--write", action="store_true", help="build the table from the saved copies; no request")
    ap.add_argument("--summary", metavar="DIR", help="print the summary's lines of numbers from DIR/large_load_waits_counts.json; no request, nothing written")
    ap.add_argument("--out-dir", help="a trial: the table, its log and the working files under this directory")
    ap.add_argument("--publishers", default="", help="session 160: only these publishers are listed and pulled, comma separated (nyiso, grantpud, ercot); default all")
    ap.add_argument("--raw-root", default=RAW_DEFAULT, help="the directory that holds large_load_waits/ and large_load_statements/")
    a = ap.parse_args(argv)
    if a.summary:
        with open(os.path.join(a.summary, f"{NAME}_counts.json"), encoding="utf-8") as f:
            counts = json.load(f)
        print("\n".join(summary_lines(counts) + [""] + comparison_lines(counts) + [""] + texas_lines(counts)))
        return 0
    if not (a.list or a.pull or a.terms or a.count or a.write):
        ap.error("name a stage: --list, --pull, --terms, --count or --write")
    import iso_prices as ip
    raw = os.path.join(a.raw_root, CONNECTOR)
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = now_utc().strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))

    def say(m):
        log(m)
        print(m)

    status = dict(table=NAME, market="large_load", status="ok", detail="")
    try:
        if a.list or a.pull or a.terms:
            os.makedirs(raw, exist_ok=True)
            budget = Budget(raw)
            net = Net(budget, say)
            only = {p.strip() for p in a.publishers.split(",") if p.strip()}
            if only - set(WANTED):
                raise RuntimeError(f"--publishers names {sorted(only - set(WANTED))}; the publishers are {sorted(WANTED)}")
            if a.list:
                do_list(raw, net, say, [l for l in LISTINGS if not only or l[0] in only])
            if a.pull:
                do_pull_archive(raw, net, say, only)
                do_pull_current(raw, net, say, ip, only)
                count_rows(raw, say)
            if a.terms:
                do_terms(raw, net, say)
            say(f"requests {budget.requests:,} of {CEILING_REQUESTS:,}; bytes {budget.bytes:,} of {CEILING_BYTES:,}; rows {Budget(raw).rows:,} of {CEILING_ROWS:,}")
        if a.count:
            count_rows(raw, say)
        if a.write:
            b = build(raw, say)
            if not b["rows"]:
                raise RuntimeError("no request could be followed across the saved copies; nothing is written")
            n_rows = sum(len(c["rows"]) for c in b["copies"])
            if n_rows > CEILING_ROWS:
                raise RuntimeError(f"{n_rows:,} rows of requests would pass the ceiling of {CEILING_ROWS:,}; nothing is written")
            wf = os.path.join(a.raw_root, "large_load_statements", "wait_figures.csv")
            stated = []
            if os.path.exists(wf):
                with open(wf, encoding="utf-8", newline="") as f:
                    stated = list(csv.DictReader(f))
            else:
                say(f"  {wf} is not on this machine: the stated expectations are not compared in this run")
            comparison, no_expectation = compare(b["rows"], stated)
            counts = counts_of(b, comparison, no_expectation)
            ercot = read_ercot(raw, say)
            counts["ercot"] = {"status_reports": len(ercot), "first": ercot[0]["day"] if ercot else "", "last": ercot[-1]["day"] if ercot else "",
                               "requests_listed": 0, "reports": ercot,
                               "held_by_archive": sum(1 for r in ercot if r["held_by"] == "the Internet Archive"),
                               "held_by_publisher": sum(1 for r in ercot if r["held_by"] != "the Internet Archive"),
                               "reports_naming_a_request": sum(1 for r in ercot if r["names_a_request"])}
            counts["texas_stated"] = texas_stated(stated)
            naming = [r["document"] for r in ercot if r["names_a_request"]]
            if naming:
                say(f"  ERCOT: {len(naming)} report(s) print a column head of a list of requests and must be read by a person before anything is said of them: {naming}")
            say(f"  ERCOT: {len(ercot)} status reports read ({counts['ercot']['first']} to {counts['ercot']['last']}); they give megawatts by stage for the "
                "system and list no request: nothing is followed and no wait is made from them")
            counts["other_queues"], counts["other_listings_with_no_capture"] = other_queues(raw)
            counts["terms"] = [dict(t, quotes=[dict(sentence=q, found=ok) for q, ok in t["quotes"]]) for t in terms_saved(raw)]
            for t in counts["terms"]:
                bad = [q["sentence"] for q in t["quotes"] if not q["found"]]
                say(f"  terms {t['who']}: {len(t['quotes']) - len(bad)} of {len(t['quotes'])} quoted sentences stand word for word in {t['file'] or 'no saved page'}"
                    f" (sha256 {t['sha256'][:16]}, retrieved {t['retrieved_at']})")
                if bad and t["file"]:
                    raise RuntimeError(f"a quoted sentence of {t['who']}'s terms is not in the saved page {t['file']}: {bad[0][:80]!r}")
            counts["request_rows_read"] = n_rows
            counts["stated_figures_read"] = len(stated)
            counts["stated_expectations_of_large_loads"] = sum(1 for f in stated if f.get("wait_basis") == "expected" and f.get("wait_counted") == "yes"
                                                               and not f.get("load_scope", "").startswith("all distribution"))
            figs = figures(b["rows"])
            import pandas as pd
            df = pd.DataFrame(b["rows"], columns=COLS).sort_values(["entity", "request_id", "interval", "start_later_date", "event_id"]).reset_index(drop=True)
            ip.write_snapshot(df, NAME, header_lines(run_id, b, counts), say, COLS)
            ip.update_sources([dict(source=e["source"], publisher=e["publisher"],
                                    report=("NYISO Interconnection Queue workbook, its load requests in each dated copy the Internet Archive holds and the current copy "
                                            "(session 155: followed across copies for large_load_waits) [terms: \"Access to this Web site does not confer any license or "
                                            "ownership interest in either the form or content of the Web site\" (https://www.nyiso.com/legal-notice); held internal]"
                                            if pub == "nyiso" else
                                            "Grant PUD Interconnection Queue (PDF), its load requests in each dated copy the Internet Archive holds and the current copy "
                                            "(session 155: followed across copies for large_load_waits) [the publisher's site states no terms of use for its documents; "
                                            "held internal until a person rules]"),
                                    report_url="https://www.nyiso.com/interconnections" if pub == "nyiso" else "https://www.grantpud.org/transmission-information",
                                    document_list="https://web.archive.org/", license="internal", tables=[NAME]) for pub, e in ENTITIES.items()])
            write_beside(a.out_dir or raw, b, figs, comparison, counts)
            for e, v in counts["requests"].items():
                say(f"  {e}: requests seen {v['seen']}, followed {v['followed']}, not followed {v['not_followed']}")
            say(f"  rows {len(df)}: {counts['rows_by_label']}")
            status["detail"] = f"{len(df)} rows; {n_rows:,} rows of requests read of a ceiling of {CEILING_ROWS:,}"
    except Exception:
        import traceback
        tb = traceback.format_exc()
        last = tb.strip().splitlines()[-1]
        log(f"FAILED:\n{tb}")
        print(f"{CONNECTOR} FAILED: {last}", file=sys.stderr)
        status.update(status="failed", detail=last[:300])
    if a.write:
        ip.write_status(CONNECTOR, run_id, [status])
    log.close()
    print(f"{CONNECTOR}: {status['status']}: {status['detail']}; run log {log.path}")
    return 1 if status["status"] == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
