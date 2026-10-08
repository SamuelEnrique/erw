#!/usr/bin/env python3
"""The pages a Thesis Builder run cites, fetched in code and saved as text (session 147). INTERNAL.

Energy Research Warehouse (ERW), Thesis Builder. Until session 147 the web tier of the rule (tie.py) scored the
sentences the model quoted from a page, so what the model chose to quote moved the landscape (session 142: one company
entered in the third run on a sentence of a page held since the day before). From session 147 the run itself requests
every web address its rows cite, once, with no model, keeps the page's text in the niche's evidence store with its
SHA-256, the day it was retrieved, the HTTP status and the number of bytes, and the rule reads the sentences of that
saved text. This module is the request and the reading of a page. It decides nothing about a company.

THE PULL, AS THE OWNER ALLOWED IT (7 October 2026)

  * One plain GET an address. The only header set is the User-Agent, exactly UA below: no personal address, no
    cookie, no JavaScript, no login, no way round a CAPTCHA or a browser check, no archive or cache service in place
    of the page. A redirect is followed by hand, at most MAX_REDIRECTS times, each hop a counted request that passes
    every check below again; a redirect to a login is recorded and left.
  * A page that answers anything but 200 with text (HTML, plain text or a PDF) is recorded with its status and
    reason, holds no sentences, and is left. A page longer than MAX_BYTES is read to the limit, recorded as
    truncated, and holds no sentences.
  * Never misoenergy.org (paused, warehouse/metadata/paused_sources.csv): "not fetched: paused". Never a PJM Data
    Miner or API address, and never the site of a licensed database the tool reads only through the user's own
    account (pitchbook.com, crunchbase.com, harmonic.ai): "not fetched: licensed source needed". All are refused
    before any request.
  * robots.txt: each host's file is read once a day (it counts as a request) and an address it disallows for all
    agents (the group "User-agent: *"; the longest matching rule wins, Allow wins a draw) is "not fetched:
    robots.txt". A robots.txt that cannot be read (401, 403, a server error, no answer) is treated as a refusal of
    the host: its pages are not requested.
  * The ceilings, set before the first request and checked before each one: MAX_ADDRESSES_RUN addresses a run,
    MAX_ADDRESSES_SESSION a session (the count is kept in a file the runs of a session share), MAX_BYTES a page,
    TIMEOUT seconds a request, at most one request every HOST_GAP seconds to one host (longer when the host's
    robots.txt asks for a crawl delay, up to MAX_CRAWL_DELAY), MAX_REQUESTS_RUN and MAX_REQUESTS_SESSION
    requests of any kind (pages, robots.txt, redirect hops), and MAX_SECONDS_RUN seconds for a run's whole pull.
  * A page the store already holds from the run's own day is not requested again; one held from an earlier day is
    requested again, and when its text differs the store keeps both versions with their days and hashes.
  * PDFs are read with pdfplumber, a page at a time.

THE LAST GOOD TEXT IS KEPT (session 160, the owner's ruling of 8 October 2026: "keep a page's last good text when it
later refuses, with the retrieval date shown")

  * When an address the store holds a good text of (fetched whole, with text) is asked again and the attempt fails or
    is refused (any status that is not 200, a redirect that leads nowhere, no answer or a timeout, an empty or
    non-text body, a truncated body, a robots.txt that now disallows the address or cannot be read), the store keeps
    the good text as the page's text. The record's state is "kept"; "retrieved" and "retrieved_at" are the day and
    time the good text was read; "refusal" holds the failed attempt (its state, status, reason, day, time, run), and
    "refusals" every such attempt since the good read. "fetched" stays the day the address was last asked, so a page is
    still asked at most once a day. A later good read replaces the kept text as any new read does.
  * A page that never gave text holds no sentence, as before. So does a page the pull itself refuses before any
    request (OUR_REFUSALS: a paused publisher, a licensed database, not a public web address): that is this code's
    refusal by a rule of the owner's, not the page's, and nothing of such a host is read from an earlier day.
  * No age limit: the owner gave none. The age of every kept text (days from its retrieval to the attempt that
    failed) is in the record so that he can set one.
  * A store written before session 160 holds such pages with the failed attempt as the record and the good text in
    its history: restore_kept() rebuilds them (the history is left as it is).

No model call. The only network call is transport(), which a test replaces.
"""

import datetime as dt
import gzip
import hashlib
import html
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = "ERW research project, github.com/SamuelEnrique/erw"
HEADERS = {"User-Agent": UA}
MAX_ADDRESSES_RUN = 150
MAX_ADDRESSES_SESSION = 450
MAX_REQUESTS_RUN = 450            # pages, robots.txt files and redirect hops together
MAX_REQUESTS_SESSION = 1350
MAX_BYTES = 2_000_000
TIMEOUT = 20
HOST_GAP = 1.0
MAX_CRAWL_DELAY = 30.0
MAX_REDIRECTS = 3
MAX_SECONDS_RUN = 600             # a run's whole pull: the workflow's job has 40 minutes, and the pull comes after the paid calls
MAX_PDF_PAGES = 200
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PAUSED_FILE = os.path.join(ROOT, "warehouse", "metadata", "paused_sources.csv")
NEVER_HOSTS = ("misoenergy.org",)                    # the floor: refused here even if the pause file is unreadable
# The licensed databases the tool reads only through the user's own account (docs/methods/thesis_builder.md, "Bring
# your own license"): their sites are not asked for a page either. Added at the end of session 147, after four
# crunchbase.com addresses had been asked for once each that evening (each answered 403; nothing was received).
LICENSED_HOSTS = ("pitchbook.com", "crunchbase.com", "harmonic.ai")
# Session 158, the owner's ruling of 8 October 2026: the public pages of DATA VENDORS (cbinsights, dealroom, sacra and
# the like) are read as any other page, and labeled. The list is one file with the reason for each row; a page of
# one carries the vendor's name in its record ("vendor") and every sentence the rule reads from it carries it too
# (tie.py, rule 7). It is a label, never a refusal: the hosts above stay refused, and nothing else changes in the pull.
VENDOR_FILE = os.path.join(HERE, "vendor_pages.csv")
# The three licensed databases are data vendors too. Their sites are never requested (above), but the SEARCH tool of
# the research returns titles and passages of their public pages, and the rule has read those in its fetched tier
# since session 142. Such a line carries the vendor's label like any other vendor's (labeled_vendors); no page of
# theirs is fetched for it.
LICENSED_NAMES = {"pitchbook.com": "PitchBook", "crunchbase.com": "Crunchbase", "harmonic.ai": "Harmonic"}
LOGIN_WORDS = ("login", "log-in", "signin", "sign-in", "sso", "oauth", "auth", "authenticate", "subscribe", "paywall", "captcha", "register", "account", "wp-login")
LOGIN_HOSTS = ("login", "signin", "sso", "auth", "account", "accounts", "id", "idp")
TEXT_TYPES = ("text/html", "application/xhtml+xml", "text/plain")
PDF_TYPE = "application/pdf"


# ---------------------------------------------------------------------------------------------
# addresses that are never requested
# ---------------------------------------------------------------------------------------------

def paused_hosts(path=None):
    """The hosts of paused publishers: the floor above and every domain named in paused_sources.csv (outlets)."""
    hosts = set(NEVER_HOSTS)
    path = path or PAUSED_FILE
    if os.path.exists(path):
        import csv
        with open(path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                for o in (row.get("outlets") or "").split(";"):
                    o = o.strip().lower()
                    if re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", o):
                        hosts.add(o)
    return hosts


def vendor_pages(path=None):
    """{domain: the vendor's name} of the data vendors whose public pages are labeled (vendor_pages.csv, session 158)."""
    import csv
    out = {}
    path = path or VENDOR_FILE
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                d = (row.get("domain") or "").strip().lower()
                if re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", d) and (row.get("vendor") or "").strip():
                    out[d] = row["vendor"].strip()
    return out


def labeled_vendors(path=None):
    """{domain: name} of every site whose sentences carry the vendor label: the vendors of vendor_pages.csv, whose
    pages are fetched, and the three licensed databases, whose pages are not (only what the search tool returned of
    them is held)."""
    return dict(vendor_pages(path), **LICENSED_NAMES)


def vendor_of(url, vendors=None):
    """The data vendor whose page an address is, or "" (the host is a listed domain or one of its subdomains)."""
    host = host_of(url)
    host = host[4:] if host.startswith("www.") else host
    vendors = vendor_pages() if vendors is None else vendors
    for d in sorted(vendors):
        if host == d or host.endswith("." + d):
            return vendors[d]
    return ""


def to_login(url, asked):
    """True when a redirect's target looks like a login, a paywall or a browser check: a path segment that is
    one of LOGIN_WORDS (the word alone, or with an extension), or a host whose first label is one of LOGIN_HOSTS. A redirect to the same path (http to https,
    a www added) is never one."""
    try:
        u, a = urllib.parse.urlsplit(url), urllib.parse.urlsplit(asked)
    except ValueError:
        return False
    if u.path.rstrip("/").lower() == a.path.rstrip("/").lower():
        return False
    if (u.hostname or "").lower().split(".")[0] in LOGIN_HOSTS:
        return True
    for seg in u.path.lower().split("/"):
        for w in LOGIN_WORDS:
            if seg == w or seg.startswith(w + "."):
                return True
    return False


def host_of(url):
    try:
        return (urllib.parse.urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def origin_of(url):
    u = urllib.parse.urlsplit(url)
    return f"{u.scheme.lower()}://{(u.hostname or '').lower()}"


def never(url, paused=None):
    """Why an address is never requested, or "" when it may be. Checked before any request, and again at each hop."""
    try:
        u = urllib.parse.urlsplit(url)
        port = u.port
    except ValueError:
        return "not fetched: not a web address"
    host = (u.hostname or "").lower()
    if u.scheme.lower() not in ("http", "https") or not host:
        return "not fetched: not a web address"
    for h in (paused if paused is not None else paused_hosts()):
        if host == h or host.endswith("." + h):
            return "not fetched: paused"
    if any(host == h or host.endswith("." + h) for h in LICENSED_HOSTS):
        return "not fetched: licensed source needed"
    if host == "pjm.com" or host.endswith(".pjm.com"):
        first = host.split(".")[0]
        if "dataminer" in host or first.startswith("api") or "/api/" in u.path.lower() or "dataminer" in u.path.lower():
            return "not fetched: licensed source needed"
    if port not in (None, 80, 443) or u.username or re.fullmatch(r"[0-9.]+", host) or ":" in host or "." not in host \
            or host.endswith((".local", ".internal", ".localhost")) or host == "localhost":
        return "not fetched: not a public web address"
    return ""


# ---------------------------------------------------------------------------------------------
# robots.txt, for all agents
# ---------------------------------------------------------------------------------------------

def robots_rules(text):
    """(rules, crawl delay) of the groups that address all agents ("User-agent: *"). rules: [[allow, pattern]]."""
    rules, delay, agents, in_rules = [], None, [], False
    for raw in (text or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            if in_rules:
                agents, in_rules = [], False
            agents.append(v.lower())
        elif k in ("allow", "disallow"):
            in_rules = True
            if "*" in agents and v:               # an empty Disallow allows everything: no rule
                rules.append([k == "allow", v])
        elif k == "crawl-delay":
            in_rules = True
            if "*" in agents:
                try:
                    delay = float(v)
                except ValueError:
                    pass
    return rules, delay


def _robots_match(pattern, path):
    end = pattern.endswith("$")
    body = pattern[:-1] if end else pattern
    rx = ".*".join(re.escape(p) for p in body.split("*")) + ("$" if end else "")
    return re.match(rx, path) is not None


def robots_allows(rules, url):
    """True unless the longest rule that matches the address's path is a Disallow (an Allow wins a draw)."""
    u = urllib.parse.urlsplit(url)
    path = (u.path or "/") + (("?" + u.query) if u.query else "")
    best = None
    for allow, pattern in rules or []:
        if _robots_match(pattern, path):
            cand = (len(pattern), bool(allow))
            if best is None or cand > best:
                best = cand
    return True if best is None else best[1]


# ---------------------------------------------------------------------------------------------
# a page's text
# ---------------------------------------------------------------------------------------------

EXTRACTOR = 3                     # the reading of an HTML page, written in each page's record. 1 read the visible text only; 2 added
                                  # the page's description and structured data; 3 reads tags and entities inside an article body


def ld_strings(x, out):
    """The headline, description and articleBody of a page's own structured data (JSON-LD), wherever they sit."""
    if isinstance(x, dict):
        for k, v in x.items():
            if k in ("headline", "description", "articleBody") and isinstance(v, str):
                out.append(v)
            else:
                ld_strings(v, out)
    elif isinstance(x, list):
        for v in x:
            ld_strings(v, out)


class _Text(HTMLParser):
    """The text of an HTML page as it was received, one line a block: the visible text, without scripts, styles,
    navigation and footers; and what the page says of itself in its head, its description (the meta tag) and the
    headline, description and article body of its structured data (JSON-LD). Many news sites draw the article with
    JavaScript, which is never run here: on such a page the visible text is menus and headlines, and the article is
    in the head (the first run of 7 October 2026 met this on renewablesnow.com). No script is executed."""

    SKIP = {"script", "style", "noscript", "template", "svg", "iframe", "select", "textarea", "nav", "footer", "head", "canvas", "object"}
    BLOCK = {"p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr", "td", "th", "table", "section", "article", "header",
             "aside", "blockquote", "figcaption", "figure", "dd", "dt", "dl", "pre", "hr", "main", "form", "label", "button", "option", "title",
             "body", "html", "caption", "details", "summary", "address"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip, self.ld = [], {}, None

    def said_of_itself(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta" and (a.get("name", "").lower() == "description" or a.get("property", "").lower() == "og:description") and a.get("content", "").strip():
            self.parts.append("\n" + a["content"] + "\n")
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self.ld = []

    def handle_starttag(self, tag, attrs):
        self.said_of_itself(tag, attrs)
        if tag in self.SKIP:
            self.skip[tag] = self.skip.get(tag, 0) + 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        if tag == "meta":
            self.said_of_itself(tag, attrs)
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "script" and self.ld is not None:
            found = []
            try:
                ld_strings(json.loads("".join(self.ld)), found)
            except ValueError:
                pass
            for v in found:                               # an article body is often written with its own tags and entities
                self.parts.append("\n" + (html_text(v) if re.search(r"<[A-Za-z/][^>]*>", v) else html.unescape(v)) + "\n")
            self.ld = None
        if tag in self.SKIP:
            if self.skip.get(tag):
                self.skip[tag] -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.ld is not None:
            self.ld.append(data)
        elif not any(self.skip.values()):
            self.parts.append(data)


def tidy(text):
    """One line a block, spaces collapsed, empty lines dropped."""
    lines = (re.sub(r"\s+", " ", ln).strip() for ln in (text or "").replace("\r", "\n").split("\n"))
    return "\n".join(ln for ln in lines if ln)


def html_text(html):
    p = _Text()
    try:
        p.feed(html)
        p.close()
    except Exception:                                   # a page too broken to parse holds what was read so far
        pass
    return tidy("".join(p.parts))


def charset_of(content_type, body):
    m = re.search(r"charset=[\"']?([A-Za-z0-9_.:-]+)", content_type or "", re.I)
    if not m:
        m = re.search(rb"<meta[^>]+charset=[\"']?([A-Za-z0-9_.:-]+)", body[:4096], re.I)
    name = (m.group(1).decode("ascii", "replace") if m and isinstance(m.group(1), bytes) else (m.group(1) if m else "utf-8"))
    try:
        "".encode(name)
        return name
    except LookupError:
        return "utf-8"


def pdf_text(body):
    """A PDF's text, a page at a time (pdfplumber, as the CARB auction connector reads its PDF)."""
    import pdfplumber
    out = []
    with pdfplumber.open(io.BytesIO(body)) as pdf:
        for page in pdf.pages[:MAX_PDF_PAGES]:
            out.append(page.extract_text() or "")
    # a PDF's lines are layout, not blocks: a paragraph is rebuilt by joining them, and a blank line or a page ends it
    return tidy("\n".join(re.sub(r"(?<![.!?:])\n(?=\S)", " ", t) for t in out))


def text_of(content_type, body):
    """(kind, text) of a 200 answer: kind is "html", "text", "pdf", or "" when the answer is not text."""
    ct = (content_type or "").split(";")[0].strip().lower()
    if ct == PDF_TYPE or (not ct and body[:5] == b"%PDF-") or (ct == "application/octet-stream" and body[:5] == b"%PDF-"):
        return "pdf", pdf_text(body)
    if ct in TEXT_TYPES or (not ct and b"<html" in body[:2048].lower()):
        s = body.decode(charset_of(content_type, body), "replace")
        return ("text", tidy(s)) if ct == "text/plain" else ("html", html_text(s))
    return "", ""


# ---------------------------------------------------------------------------------------------
# the one network call
# ---------------------------------------------------------------------------------------------

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def request_of(url):
    """The request as it is sent: a GET with the one header."""
    return urllib.request.Request(url, headers=dict(HEADERS), method="GET")


def transport(url, headers=None, timeout=TIMEOUT, max_bytes=MAX_BYTES):
    """One plain GET. Returns (status, headers {lower name: value}, body, truncated). No cookie jar (the default
    opener has none), no redirect followed, at most max_bytes of body read, at most timeout seconds in all."""
    opener = urllib.request.build_opener(_NoRedirect)
    opener.addheaders = []
    req = urllib.request.Request(url, headers=dict(headers or HEADERS), method="GET")
    t0 = time.monotonic()
    try:
        resp = opener.open(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        resp = exc
    status = getattr(resp, "status", None) or getattr(resp, "code", None)
    head = {k.lower(): v for k, v in (resp.headers.items() if resp.headers else [])}
    body, truncated = b"", False
    unzip = None
    if "gzip" in head.get("content-encoding", "").lower():        # not asked for, but some servers send it anyway
        import zlib
        unzip = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        while True:
            if time.monotonic() - t0 > timeout:
                raise TimeoutError(f"no complete answer in {timeout} seconds")
            chunk = resp.read(65536)
            if not chunk:
                break
            body += unzip.decompress(chunk, max_bytes + 1 - len(body)) if unzip else chunk
            if len(body) > max_bytes:
                body, truncated = body[:max_bytes], True
                break
    finally:
        try:
            resp.close()
        except Exception:
            pass
    return status, head, body, truncated


# ---------------------------------------------------------------------------------------------
# the count a session's runs share
# ---------------------------------------------------------------------------------------------

class Count:
    """Addresses, requests and bytes of a session, kept in a file so that several runs stay under one ceiling."""

    def __init__(self, path=None):
        self.path = path
        self.n = {"addresses": 0, "requests": 0, "bytes": 0}
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.n.update(json.load(f))

    def add(self, **k):
        for name, v in k.items():
            self.n[name] = self.n.get(name, 0) + v
        if self.path:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.n, f)
            os.replace(tmp, self.path)


# ---------------------------------------------------------------------------------------------
# session 160: a page's last good text is kept when the page later refuses
# ---------------------------------------------------------------------------------------------

KEPT = "kept"
# The pull's own refusals, made before any request by a rule of the owner's: they keep no earlier text.
OUR_REFUSALS = ("not fetched: paused", "not fetched: licensed source needed", "not fetched: not a web address", "not fetched: not a public web address")
_HISTORY_KEYS = ("fetched", "fetched_at", "state", "status", "reason", "bytes", "sha256", "text_sha256", "text", "last_run")
_KEPT_KEYS = ("retrieved", "retrieved_at", "retrieved_run", "refusal")


def holds_good(p):
    """True when a page record (or an entry of a page's history) holds a good text: fetched whole with text, or kept."""
    if not p or not p.get("text"):
        return False
    return p.get("state") == KEPT or (p.get("state") == "fetched" and not p.get("truncated"))


def days_between(a, b):
    """Whole days from day a to day b (YYYY-MM-DD), or None when either is not a day."""
    try:
        return (dt.date.fromisoformat(str(b)[:10]) - dt.date.fromisoformat(str(a)[:10])).days
    except ValueError:
        return None


def kept_record(good, rec):
    """The record of an address after an attempt. good: what the store held of it before (a record, an entry of a
    history, or None). rec: the record of the attempt just made. When the attempt gave a good text, or nothing good
    was held, or the refusal is this code's own (OUR_REFUSALS), rec is returned as it is. Otherwise the good text
    stays the page's text and the failed attempt is recorded beside it."""
    if holds_good(rec) or not holds_good(good) or (rec.get("reason") or "") in OUR_REFUSALS:
        return rec
    retrieved = good.get("retrieved") or good.get("fetched") or ""
    refusal = {"state": rec.get("state"), "status": rec.get("status"), "reason": rec.get("reason"), "day": rec.get("fetched"), "at": rec.get("fetched_at"),
               "run": rec.get("last_run"), "bytes": rec.get("bytes"), "truncated": bool(rec.get("truncated"))}
    out = dict(rec)
    out.update(state=KEPT, text=good["text"], text_sha256=good.get("text_sha256") or hashlib.sha256(good["text"].encode("utf-8")).hexdigest(), truncated=False,
               retrieved=retrieved, retrieved_at=good.get("retrieved_at") or good.get("fetched_at") or "", retrieved_run=good.get("retrieved_run") or good.get("last_run") or "",
               refusal=refusal, refusals=list(good.get("refusals") or []) + [refusal], age_days=days_between(retrieved, rec.get("fetched")))
    for k in ("kind", "extractor"):
        if good.get(k) is not None:
            out[k] = good[k]
    return out


def restore_kept(store):
    """A store written before session 160: a page whose record is a failed attempt and whose history holds an earlier
    good text becomes a kept page (the latest good text of its history). The history is left as it is. Returns the
    addresses restored, a to z. A store already in the new form is unchanged."""
    done = []
    for url in sorted(store.get("pages") or {}):
        p = store["pages"][url]
        if holds_good(p) or (p.get("reason") or "") in OUR_REFUSALS:
            continue
        good = next((h for h in reversed(p.get("history") or []) if holds_good(h)), None)
        if good is None:
            continue
        store["pages"][url] = kept_record(good, p)
        done.append(url)
    return done


def _face(p):
    """What a change of a page is measured by: its text and whether it holds one. A good text that is kept is the same page."""
    return (p.get("text_sha256"), "fetched" if p.get("state") == KEPT else p.get("state"))


def _past(old):
    """A record as an entry of its page's history."""
    return {k: old.get(k) for k in _HISTORY_KEYS + tuple(k for k in _KEPT_KEYS if k in old)}


# ---------------------------------------------------------------------------------------------
# one run's pull
# ---------------------------------------------------------------------------------------------

def held_today(store, url, day):
    p = (store.get("pages") or {}).get(url)
    return p is not None and str(p.get("fetched") or "") >= day


def fetch_run(store, addresses, run_id, day, log=lambda s: None, count=None, get=None, sleep=time.sleep, clock=time.monotonic,
              raw_dir=None, paused=None, max_run=MAX_ADDRESSES_RUN, max_session=MAX_ADDRESSES_SESSION,
              max_requests_run=MAX_REQUESTS_RUN, max_requests_session=MAX_REQUESTS_SESSION, max_bytes=MAX_BYTES, shelf=None,
              max_seconds=MAX_SECONDS_RUN, vendors=None):
    """Request every address of the list the store does not hold from this day, in the order given, under the
    ceilings; save each page (or why it was not fetched) in store["pages"] and each robots.txt in store["robots"].
    Returns the run's tally. Never raises for an address: a failure is that address's record.

    shelf: another store of the same niche ({"pages", "robots"}), or None. An address this run asks for that the shelf
    holds from this day is copied from it, record and all, and not requested again (tally "copied"). It serves the
    replays of a session, which apply the code again to saved answers through a store of their own: a page the
    session already holds is not asked of its publisher a second time. A run started by the page has no shelf."""
    get = get or transport
    count = count or Count()
    paused = paused if paused is not None else paused_hosts()
    vendors = vendor_pages() if vendors is None else vendors          # session 158: a data vendor's page is fetched as before, and labeled
    pages, robots = store.setdefault("pages", {}), store.setdefault("robots", {})
    tally = {"run_id": run_id, "day": day, "user_agent": UA, "cited": 0, "held": 0, "copied": 0, "requested": 0, "fetched": 0, "refused": {}, "failed": 0, "not_text": 0,
             "truncated": 0, "empty": 0, "kept": {}, "robots_disallowed": 0, "robots_unreadable": 0, "paused": 0, "licensed": 0, "not_web": 0, "login": 0,
             "ceiling": 0, "requests": 0, "robots_requests": 0, "hop_requests": 0, "bytes": 0, "changed": [], "addresses": {},
             "ceilings": {"addresses_run": max_run, "addresses_session": max_session, "requests_run": max_requests_run,
                          "requests_session": max_requests_session, "bytes_page": max_bytes, "seconds": TIMEOUT, "host_gap_seconds": HOST_GAP,
                          "seconds_run": max_seconds}}
    last = {}                                           # host: when it was last asked
    began = clock()

    class Ceiling(Exception):
        pass

    def ask(url, kind):
        """One counted request, after the ceilings and the host's gap. Returns (status, headers, body, truncated, error)."""
        if tally["requests"] >= max_requests_run or count.n["requests"] >= max_requests_session:
            raise Ceiling(f"the ceiling of requests is reached (run {tally['requests']} of {max_requests_run}, session {count.n['requests']} of {max_requests_session})")
        if clock() - began > max_seconds:
            raise Ceiling(f"the ceiling of time is reached ({max_seconds} seconds for a run's pull)")
        host = host_of(url)
        gap = max(HOST_GAP, min(float((robots.get(origin_of(url)) or {}).get("crawl_delay") or 0), MAX_CRAWL_DELAY))
        wait = gap - (clock() - last[host]) if host in last else 0
        if wait > 0:
            sleep(wait)
        tally["requests"] += 1
        if kind != "page":
            tally[kind] += 1
        count.add(requests=1)
        try:
            status, head, body, truncated = get(url, dict(HEADERS), TIMEOUT, max_bytes)
            err = ""
        except Exception as exc:                        # no answer, a refused connection, a certificate that fails: recorded
            status, head, body, truncated, err = None, {}, b"", False, f"{type(exc).__name__}: {str(exc)[:160]}"
        last[host] = clock()
        tally["bytes"] += len(body)
        count.add(bytes=len(body))
        return status, head, body, truncated, err

    def rules_for(url):
        """The host's rules for all agents, read once a day. Returns (rules or None when unreadable, note)."""
        org = origin_of(url)
        held = robots.get(org)
        on_shelf = ((shelf or {}).get("robots") or {}).get(org)
        if (held is None or str(held.get("fetched") or "") < day) and on_shelf is not None and str(on_shelf.get("fetched") or "") >= day:
            held = robots[org] = json.loads(json.dumps(on_shelf))
        if held is None or str(held.get("fetched") or "") < day:
            target, status, body, err = org + "/robots.txt", None, b"", ""
            for hop in range(MAX_REDIRECTS + 1):
                why = never(target, paused)
                if why:
                    status, err = None, why
                    break
                status, head, body, truncated, err = ask(target, "robots_requests")
                if status in (301, 302, 303, 307, 308) and head.get("location") and hop < MAX_REDIRECTS:
                    target = urllib.parse.urljoin(target, head["location"])
                    continue
                break
            if status == 200:
                text = body.decode("utf-8", "replace")
                rules, delay = robots_rules(text)
                held = {"fetched": day, "status": 200, "rules": rules, "crawl_delay": delay, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "readable": True}
            elif status is not None and 400 <= status < 500 and status not in (401, 403, 429):
                held = {"fetched": day, "status": status, "rules": [], "crawl_delay": None, "bytes": len(body), "sha256": "", "readable": True}      # no robots.txt: nothing is disallowed
            else:
                held = {"fetched": day, "status": status, "rules": [], "crawl_delay": None, "bytes": len(body), "sha256": "", "readable": False,
                        "reason": err or f"robots.txt answered {status}"}
            robots[org] = held
        if not held.get("readable"):
            return None, held.get("reason") or f"robots.txt answered {held.get('status')}"
        return held.get("rules") or [], ""

    def record(url, rec):
        old = pages.get(url)
        rec = dict(rec, address=url, fetched=day, fetched_at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), last_run=run_id)
        rec["first_run"] = (old or {}).get("first_run") or run_id
        rec["first_fetched"] = (old or {}).get("first_fetched") or day
        rec = kept_record(old, rec)                       # session 160: a failed attempt after a good read keeps the good text
        if old is not None and old.get("refusals") and "refusals" not in rec:
            rec["refusals"] = list(old["refusals"])       # a good read after refusals: the refusals stay on record
        hist = list((old or {}).get("history") or [])
        if old is not None and _face(old) != _face(rec):
            hist.append(_past(old))
            tally["changed"].append(url)
        rec["history"] = hist
        if vendor_of(url, vendors):
            rec["vendor"] = vendor_of(url, vendors)
        pages[url] = rec
        if rec["state"] == KEPT:
            tally["kept"][url] = {"retrieved": rec["retrieved"], "reason": rec["reason"], "status": rec.get("status"), "age_days": rec.get("age_days")}
        tally["addresses"][url] = rec["reason"] if rec["state"] != "fetched" else "fetched"

    def one(url):
        why = never(url, paused)
        if why:
            key = {"not fetched: paused": "paused", "not fetched: licensed source needed": "licensed"}.get(why, "not_web")
            tally[key] += 1
            return record(url, {"state": "not fetched", "status": None, "reason": why, "bytes": 0, "sha256": "", "text_sha256": "", "text": "", "truncated": False})
        if tally["requested"] >= max_run or count.n["addresses"] >= max_session:
            raise Ceiling(f"the ceiling of addresses is reached (run {tally['requested']} of {max_run}, session {count.n['addresses']} of {max_session})")
        target, hops, counted = url, 0, False
        while True:
            rules, note = rules_for(target)
            if rules is None:
                tally["robots_unreadable"] += 1
                return record(url, {"state": "not fetched", "status": None, "reason": f"not fetched: robots.txt could not be read ({note})", "bytes": 0, "sha256": "", "text_sha256": "", "text": "", "truncated": False})
            if not robots_allows(rules, target):
                tally["robots_disallowed"] += 1
                return record(url, {"state": "not fetched", "status": None, "reason": "not fetched: robots.txt", "bytes": 0, "sha256": "", "text_sha256": "", "text": "", "truncated": False})
            if not counted:
                counted = True
                tally["requested"] += 1
                count.add(addresses=1)
            status, head, body, truncated, err = ask(target, "page" if hops == 0 else "hop_requests")
            base = {"status": status, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest() if body else "", "text_sha256": "", "text": "",
                    "truncated": truncated, "final": target, "content_type": head.get("content-type", "")}
            if raw_dir and body:
                os.makedirs(raw_dir, exist_ok=True)
                with open(os.path.join(raw_dir, base["sha256"] + ".bin"), "wb") as f:
                    f.write(body)
            if err:
                tally["failed"] += 1
                return record(url, dict(base, state="refused", reason=f"no answer: {err}"))
            if status in (301, 302, 303, 307, 308) and head.get("location"):
                nxt = urllib.parse.urljoin(target, head["location"])
                if to_login(nxt, url):
                    tally["login"] += 1
                    return record(url, dict(base, state="refused", reason=f"redirects to a login ({status})"))
                why = never(nxt, paused)
                if why:
                    tally["refused"][str(status)] = tally["refused"].get(str(status), 0) + 1
                    return record(url, dict(base, state="refused", reason=f"redirects ({status}) to an address that is {why}"))
                if hops >= MAX_REDIRECTS:
                    tally["refused"][str(status)] = tally["refused"].get(str(status), 0) + 1
                    return record(url, dict(base, state="refused", reason=f"more than {MAX_REDIRECTS} redirects"))
                target, hops = nxt, hops + 1
                continue
            if status != 200:
                tally["refused"][str(status)] = tally["refused"].get(str(status), 0) + 1
                return record(url, dict(base, state="refused", reason=f"answered {status}"))
            if truncated:
                tally["truncated"] += 1
                return record(url, dict(base, state="truncated", reason=f"truncated at {max_bytes} bytes"))
            try:
                kind, text = text_of(head.get("content-type", ""), body)
            except Exception as exc:
                kind, text = "unreadable", ""
                base["reason_detail"] = f"{type(exc).__name__}: {str(exc)[:120]}"
            if kind in ("", "unreadable"):
                tally["not_text"] += 1
                return record(url, dict(base, state="refused", reason="answered 200 without text" + (f" ({base['content_type'].split(';')[0]})" if base["content_type"] else "")))
            if not text.strip():
                tally["empty"] += 1
                return record(url, dict(base, state="refused", reason=f"answered 200 with no text in the {kind}"))
            tally["fetched"] += 1
            return record(url, dict(base, state="fetched", reason="", kind=kind, extractor=EXTRACTOR, text=text, text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest()))

    todo = list(dict.fromkeys(a for a in addresses if a and not str(a).startswith("erw:")))
    tally["cited"] = len(todo)
    tally["vendor_pages"] = {u: vendor_of(u, vendors) for u in todo if vendor_of(u, vendors)}      # session 158: every cited address of a data vendor, by name
    stopped = ""
    for n, url in enumerate(todo):
        if held_today(store, url, day):
            tally["held"] += 1
            continue
        if shelf is not None and held_today(shelf, url, day):
            rec = json.loads(json.dumps(shelf["pages"][url]))
            rec.update(history=list((pages.get(url) or {}).get("history") or []), first_run=run_id, last_run=run_id, copied_from_run=shelf["pages"][url].get("last_run"))
            old = pages.get(url)
            rec = kept_record(old, rec)                   # session 160: the copy of a failed attempt keeps the good text this store holds
            if holds_good(old) and _face(old) != _face(rec):
                rec["history"] = rec["history"] + [_past(old)]      # a text this store held is never dropped by a copy
            pages[url] = rec
            if rec["state"] == KEPT:
                tally["kept"][url] = {"retrieved": rec["retrieved"], "reason": rec["reason"], "status": rec.get("status"), "age_days": rec.get("age_days")}
            org = origin_of(rec.get("final") or url)
            for o in {origin_of(url), org}:
                if o in (shelf.get("robots") or {}) and o not in robots:
                    robots[o] = json.loads(json.dumps(shelf["robots"][o]))
            tally["copied"] += 1
            tally["addresses"][url] = "copied: " + (rec["reason"] if rec["state"] != "fetched" else "fetched")
            continue
        if stopped:
            tally["ceiling"] += 1
            continue
        try:
            one(url)
        except Ceiling as exc:
            stopped = str(exc)
            tally["ceiling"] += 1
            log(f"  pages: {stopped}; {len(todo) - n} addresses are left unrequested")
        except Exception as exc:                        # this address's failure, never the run's
            tally["failed"] += 1
            record(url, {"state": "refused", "status": None, "reason": f"not read: {type(exc).__name__}: {str(exc)[:160]}", "bytes": 0, "sha256": "", "text_sha256": "", "text": "", "truncated": False})
    tally["stopped"] = stopped
    tally["vendor_pages_held"] = sum(1 for u in tally["vendor_pages"] if holds_good(pages.get(u)))
    tally["session"] = dict(count.n)
    log(f"  pages: cited {tally['cited']}; held from today {tally['held']}; copied from the session's shelf {tally['copied']}; requested {tally['requested']}; fetched with text {tally['fetched']}; refused by status {tally['refused'] or 'none'}; "
        f"no answer {tally['failed']}; not text {tally['not_text']}; empty {tally['empty']}; truncated {tally['truncated']}; redirects to a login {tally['login']}; kept with the last good text {len(tally['kept'])}; "
        f"robots.txt disallows {tally['robots_disallowed']}; robots.txt unreadable {tally['robots_unreadable']}; paused {tally['paused']}; licensed {tally['licensed']}; "
        f"left by the ceiling {tally['ceiling']}; requests {tally['requests']} ({tally['robots_requests']} robots.txt, {tally['hop_requests']} redirect hops); bytes {tally['bytes']:,}; "
        f"session so far: {count.n['addresses']} addresses, {count.n['requests']} requests")
    log(f"  pages of data vendors (read and labeled, session 158): cited {len(tally['vendor_pages'])}; holding text {tally['vendor_pages_held']}"
        + ("" if not tally["vendor_pages"] else ": " + "; ".join(f"{u} ({v})" for u, v in sorted(tally["vendor_pages"].items()))))
    return tally
