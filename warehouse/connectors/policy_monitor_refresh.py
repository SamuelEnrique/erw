#!/usr/bin/env python3
"""The policy monitor's daily refresh: what is new in the open docket lists of FERC and the state commissions (session 157).

Energy Research Warehouse (ERW). A sibling of large_load_rules.py, which built the two tables once from three research
passes (session 154). This step keeps them moving. Each day, by plain request, it asks each regulator's own open list
(warehouse/config/policy_monitor_feeds.json names the list, and says which regulators are not asked and why) for

    - what is new in the dockets held: a line of the list that the list itself words as an order, a decision, a
      ruling or a rule of the regulator, dated on or after the day the regulator's lists were last read less two days;
    - new dockets on the four topics (large-load interconnection, large-load tariff, transmission cost allocation,
      interconnection reform), where a list can be searched by a plain address (Texas, Virginia, the Federal Register).

and adds rows to large_load_rules (public) or large_load_rules_internal, split by each regulator's terms class exactly
as large_load_rules.py splits them, with the same columns, merged by event_id.

What a row of this step is. The list gives a filing's title line, not the document's text, so THAT LINE IS THE
SENTENCE: sentence_kind is "docket list", sentence_from names the list, and row_flag says the row is cut from the
docket list. The line is a literal substring of the saved list's text (white space normalized), proved here before the
row is taken. No model reads anything and nothing is summarized. A field the list does not state is empty. The topic
of a row in a docket held is that docket's own; the topic of a new docket is given by the words of its title line, by
TOPIC_RULES, and the row's notes say so. status_class is by rule (an order line is "decided"; a new docket is "open"
only where the list words it open or active, else "not stated").

Scope. Federal regulators and state commissions only: a line that holds a municipal word (zoning, a city council, a
county board ...) is never a row.

Never requested. A regulator whose feed says refreshed false (Ohio: its docketing system answers a reCAPTCHA;
Illinois: its docket page says no robots); ferc.gov's own pages (a browser check: FERC is read through the Federal
Register's API); misoenergy.org and PJM's Data Miner or API; any host that is not the regulator's listed one; an
address that holds an e-mail address. A page that answers with a robot check, a CAPTCHA or HTTP 403 is recorded and
left: the regulator's remaining lists are not asked that day, and nothing is retried round it.

Ceilings, in the step itself: at most MAX_REQUESTS (120) requests a day in all (a second run the same day starts from
the first's count, kept in warehouse/raw/policy_monitor_refresh/day_<date>.json) and one request a second to a host;
the step stops BEFORE a ceiling. A redirect is followed only to the regulator's own listed host, each hop a request. The only header it sends beyond the library's own is the contact string, exactly
"ERW research project, github.com/SamuelEnrique/erw", as the User-Agent. Every response is saved raw with a manifest
under warehouse/raw/policy_monitor_refresh/<run id>/, and the text each line is proved in beside it.

The two tables are in the live set's hold lists (warehouse/supabase/live_set.yaml): this step loads nothing, and no
live page reads either table.

    python warehouse/connectors/policy_monitor_refresh.py                    # the daily step: needs the data lock
    python warehouse/connectors/policy_monitor_refresh.py --out-dir DIR --in-dir HELD   # a trial: everything under DIR
    python warehouse/connectors/policy_monitor_refresh.py --offline DIR --out-dir DIR2  # on saved list pages, no request
    python warehouse/connectors/policy_monitor_refresh.py --only txpuc,vascc           # some regulators only
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import quote, urljoin

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import large_load_rules as llr  # noqa: E402

NAME = "policy_monitor_refresh"
FEEDS_FILE = os.path.join(ROOT, "warehouse", "config", "policy_monitor_feeds.json")
CONTACT = "ERW research project, github.com/SamuelEnrique/erw"   # the owner's ruling: exactly this, nothing else
MAX_REQUESTS = 120      # a day, all regulators together (a second run the same day starts from the first's count)
HOST_GAP = 1.0          # seconds between two requests to one host
MARGIN_DAYS = 2         # a list may post a day or two late
MAX_NEW_DOCKETS = 3     # new dockets taken from one regulator in one run
MAX_BYTES = 30_000_000  # a run, all responses together: a list is small; this stops a runaway
MAX_REDIRECTS = 2       # hops followed for one list, each to the regulator's own listed host and each counted as a request
TABLES = [llr.NAME, llr.NAME_HELD]
# The one host the step may ask for each regulator: its own open list. A regulator not here is never requested.
HOSTS = {
    "ferc": ["www.federalregister.gov"],          # FERC's documents, through the Federal Register's API
    "txpuc": ["interchange.puc.texas.gov"],
    "vascc": ["www.scc.virginia.gov"],
    "iurc": ["www.in.gov"],
    "papuc": ["www.puc.pa.gov"],
    "gapsc": ["psc.ga.gov"],
    "azcc": ["efiling.azcc.gov"],
    "orpuc": ["apps.puc.state.or.us"],
    "cpuc": ["apps.cpuc.ca.gov"],
}
# Hosts that refused a plain request or that this project never asks: checked before every request, whatever HOSTS says.
NEVER = llr.REFUSED_HOSTS + ["ferc.gov", "elibrary.ferc.gov", "dis.puc.state.oh.us", "puco.ohio.gov", "icc.illinois.gov",
                             "docket.images.azcc.gov", "images.edocket.azcc.gov", "iurc.portal.in.gov",
                             "unblock.federalregister.gov"]
CHECK_WORDS = re.compile(r"captcha|just a moment\.\.\.|no robots or crawlers|verify you are (?:a )?human|are you a robot|"
                         r"access denied|cf-browser-verification|enable javascript and cookies", re.I)
FLAG_LIST = "cut from the docket list: the list's own title line, not the document's text"
SENTENCE_KIND = "docket list"
# A line the list itself words as an act of the regulator: these words at the start of its title (after "Final",
# "Interim", "Amended" and the like). A party's "Proposed Order", "Response to Order No. 3" or "Comments" does not start so.
ORDER_RE = re.compile(
    r"^(?:(?:corrected|amended|final|interim|preliminary|initial|tentative|first|second|third|supplemental|short|"
    r"commission|commission's|soah|errata to|opinion and|opinion &|finding and|finding &|entry and|memorandum opinion and)\s+)*"
    r"(?:order|orders|opinion|decision|ruling|resolution|entry|secretarial letter|proposal for publication|"
    r"notice of proposed rulemaking|notice of inquiry|notice of institution|final rule|proposed rule|policy statement)\b",
    re.I)
# Session 154: procedural orders (interventions, protective orders, schedules) are not rows.
PROCEDURAL = ["procedural", "scheduling", "protective order", "pro hac vice", "intervention", "intervene",
              "extension of time", "confidential", "prehearing", "notice of appearance", "admission of counsel"]
LARGE_LOAD_TERMS = ["large load", "large loads", "data center", "data centers", "datacenter", "datacenters", "large power",
                    "large customer", "large customers", "large electric customer", "large electric customers",
                    "high load factor", "co located load", "co located loads", "colocated load", "large computational load",
                    "large demand", "megaload"]
# The topic of a NEW docket, from the words of its title line, first match (lower case, a hyphen read as a space).
TOPIC_RULES = [
    ("large-load interconnection", lambda t: any(has(x, t) for x in LARGE_LOAD_TERMS) and re.search(r"\binterconnect", t)),
    ("large-load tariff", lambda t: any(has(x, t) for x in LARGE_LOAD_TERMS)),
    ("transmission cost allocation", lambda t: has("transmission cost", t) or has("transmission costs", t)
     or (has("cost allocation", t) and has("transmission", t))),
    ("interconnection reform", lambda t: re.search(r"\binterconnection (queue|reform|process|processes|procedures|standards)\b", t)),
]
# FERC's combined notices list every docket of the day: a line with more than this many dockets is not about one.
MAX_DOCKETS_IN_A_LINE = 3
FR_ROUTINE = re.compile(r"Combined Notice of Filings|Sunshine Act|Information Collection|Notice of Filing\b", re.I)
# Virginia: the matter number of each case held, as pass A's saved case lists give it (warehouse/raw/large_load_rules/
# A/raw/va/cases_*.json, 8 October 2026). A case found later by the caption search brings its own.
VA_MATTERS = {"PUR-2024-00144": 145480, "PUR-2025-00048": 146004, "PUR-2025-00058": 146025, "PUR-2025-00160": 146482,
              "PUR-2025-00190": 146559, "PUR-2026-00011": 146728, "PUR-2026-00056": 146917, "PUR-2026-00114": 147082,
              "PUR-2026-00131": 147127}
VA_CASES = ("https://www.scc.virginia.gov/docketsearchapi/breeze/cases_estabdate/getcasesestdate?$filter=substringof(%27{w}%27"
            "%2Ctolower(Case_Caption))%20eq%20true%20and%20substringof(%27PUR-202%27%2CCase_Number)%20eq%20true&$select="
            "MATTER_NO%2CCase_Number%2CCase_Name%2CCase_Caption%2CCase_Established_Date")
VA_DOCS = ("https://www.scc.virginia.gov/docketsearchapi/breeze/casedetails/getdocuments?$filter=MATTER_NO%20eq%20{m}"
           "&$select=Document_Name%2CDate_Filed%2CDocID%2CFileName")
TX_FILINGS = ("https://interchange.puc.texas.gov/search/filings/?UtilityType=A&ControlNumber={n}&ItemMatch=Equal"
              "&DocumentType=ALL&SortOrder=Ascending")
TX_DOCKETS = "https://interchange.puc.texas.gov/search/dockets/?UtilityType=A&Description={w}&ItemsPerPage=200"
FR_LIST = ("https://www.federalregister.gov/api/v1/documents.json?conditions%5Bagencies%5D%5B%5D=federal-energy-regulatory-"
           "commission&conditions%5Bpublication_date%5D%5Bgte%5D={since}&per_page=1000&order=newest&fields%5B%5D=title"
           "&fields%5B%5D=publication_date&fields%5B%5D=document_number&fields%5B%5D=type&fields%5B%5D=html_url"
           "&fields%5B%5D=pdf_url&fields%5B%5D=docket_ids&fields%5B%5D=action")
GA_LIST = ("https://psc.ga.gov/search/service-facts-docket/?docketId={n}&sortDirection=DESC&sortColumn=receivedDate"
           "&searchText=&pageSize=100&pageNumber=1")
IN_ORDERS = "https://www.in.gov/iurc/docketed-cases/find-a-docketed-case/weekly-orders"
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december"]


class Stop(Exception):
    """The step stops before a ceiling: nothing more is requested this run."""


class Refused(Exception):
    """A list did not answer a plain request (a check, a refusal, an error): recorded, and the regulator is left."""


def norm(s):
    return " ".join(str(s or "").split())


def low(s):
    """Lower case, a hyphen or dash read as a space: how a title line is searched for a term."""
    s = norm(s).lower()
    for d in "-" + chr(0x2010) + chr(0x2011) + chr(0x2012) + chr(0x2013) + chr(0x2014):
        s = s.replace(d, " ")
    return norm(s)


def has(term, text):
    return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", text) is not None


def is_order(title):
    """The list words the line as an act of the regulator (ORDER_RE) and not as a procedural one."""
    t = norm(title)
    if not ORDER_RE.search(t):
        return False
    return not any(w in t.lower() for w in PROCEDURAL)


def topic_of(line):
    t = low(line)
    for topic, rule in TOPIC_RULES:
        if rule(t):
            return topic
    return ""


def municipal(text):
    t = (text or "").lower()
    return [w for w in llr.MUNICIPAL if w in t]


def day_of(s):
    """A date the list writes (10/6/2026, 2026-10-06T00:00:00, October 06, 2026, 08/25/2026) as YYYY-MM-DD, else ''."""
    s = norm(s)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s)
        if m:
            mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            m = re.match(r"^([A-Za-z]+)\.? (\d{1,2}),? (\d{4})", s)
            if not m or m.group(1).lower() not in MONTHS:
                return ""
            mo, d, y = MONTHS.index(m.group(1).lower()) + 1, int(m.group(2)), int(m.group(3))
    try:
        return dt.date(y, mo, d).isoformat()
    except ValueError:
        return ""


def json_text(obj, out=None):
    """A JSON list as text: one 'key: value' line for every leaf, so that a line of the list can be proved in it."""
    out = [] if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                json_text(v, out)
            elif v is not None:
                out.append(f"{k}: {v}")
    elif isinstance(obj, list):
        for v in obj:
            json_text(v, out)
    return "\n".join(out)


def as_text(content):
    """The text of a saved list (bytes): a JSON list as its leaves, a page without its tags."""
    raw = content.decode("utf-8", "replace")
    if raw.lstrip()[:1] in "[{":
        try:
            return json_text(json.loads(raw))
        except ValueError:
            pass
    return llr.html_text(raw)


def table_rows(page):
    """Every table row of a page: ([the text of each cell], [the addresses in the row])."""
    out = []
    for tr in re.findall(r"(?is)<tr\b[^>]*>(.*?)</tr>", page):
        cells = re.findall(r"(?is)<t[dh]\b[^>]*>(.*?)</t[dh]>", tr)
        if cells:
            out.append(([norm(llr.html_text(c)) for c in cells],
                        [llr.H.unescape(h) for h in re.findall(r'(?i)href="([^"]+)"', tr)]))
    return out


# ---------------------------------------------------------------- asking, under the ceilings
class Asker:
    """Every request of a run goes through here: the host rules, the ceilings, the spacing, the saving."""

    def __init__(self, raw_dir, log, max_requests=MAX_REQUESTS, gap=HOST_GAP, offline=None, send=None,
                 clock=time.monotonic, sleep=time.sleep, used=0):
        self.raw_dir, self.log, self.max, self.gap = raw_dir, log, max_requests, gap
        self.used = used   # requests already made today by earlier runs of the step: the ceiling is a day's
        self.offline, self.send, self.clock, self.sleep = offline, send or self._send, clock, sleep
        self.n = self.bytes = 0
        self.last, self.by_key, self.asked = {}, {}, []
        self.index = {}
        if offline:
            with open(os.path.join(offline, "index.json"), encoding="utf-8") as f:
                self.index = json.load(f)
        os.makedirs(os.path.join(raw_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(raw_dir, "text"), exist_ok=True)
        self.manifest = os.path.join(raw_dir, "manifest.csv")
        with open(self.manifest, "w", encoding="utf-8", newline="") as f:
            csv.writer(f, lineterminator="\n").writerow(["n", "regulator", "url", "status", "bytes", "sha256", "retrieved_at", "file", "note"])

    @staticmethod
    def _send(url):
        import requests
        r = requests.get(url, headers={"User-Agent": CONTACT}, timeout=60, allow_redirects=False)
        return r.status_code, r.content, dict(r.headers)

    @staticmethod
    def allowed(key, url):
        """The reason an address may not be asked for this regulator, '' when it may."""
        host = llr.host_of(url)
        if not host:
            return "no http address"
        if any(host == h or host.endswith("." + h) for h in NEVER):
            return f"{host} is a host this step never requests"
        r = ip.paused(key) or ip.paused_host(host)   # session 172: a paused publisher's server is never asked, by any path
        if r:
            return f"{host} is paused since {r['paused_on']} (warehouse/metadata/paused_sources.csv): {r['reason']}"
        if host not in HOSTS.get(key, []):
            return f"{host} is not the listed host of {key}"
        if llr.EMAIL_IN_URL.search(url):
            return "the address holds an e-mail address"
        return ""

    def get(self, key, url, name):
        """(text, record) of one list. Raises Stop before a ceiling and Refused when the list does not answer plainly."""
        why = self.allowed(key, url)
        if why:
            raise Refused(f"not requested: {why}")
        host = llr.host_of(url)
        asked = url
        if self.offline:
            now = self._now()
            fn = self.index.get(url)
            if not fn:
                raise Refused("offline: this list is not among the saved pages")
            with open(os.path.join(self.offline, fn), "rb") as f:
                status, content = 200, f.read()
        else:
            for hop in range(MAX_REDIRECTS + 1):
                if self.used + self.n + 1 > self.max:
                    raise Stop(f"stopped before request {self.used + self.n + 1} of the day: the ceiling is {self.max} requests a day")
                if self.bytes >= MAX_BYTES:
                    raise Stop(f"stopped before request {self.n + 1}: {self.bytes} bytes read, the ceiling is {MAX_BYTES}")
                wait = self.gap - (self.clock() - self.last[host]) if host in self.last else 0
                if wait > 0:
                    self.sleep(wait)
                self.n += 1
                self.by_key[key] = self.by_key.get(key, 0) + 1
                self.asked.append(url)
                now = self._now()
                try:
                    status, content, headers = self.send(url)
                except Exception as exc:
                    self.last[host] = self.clock()
                    self._note(key, url, "error", b"", now, "", ip.redact(repr(exc))[:200])
                    raise Refused(f"the request failed: {ip.redact(repr(exc))[:160]}")
                self.last[host] = self.clock()
                if status not in (301, 302, 303, 307, 308):
                    break
                # a redirect is a plain answer: followed only to the regulator's own listed host, each hop a request
                to = urljoin(url, (headers or {}).get("Location") or (headers or {}).get("location") or "")
                self._note(key, url, status, content, now, "", f"redirect to {to}")
                why = self.allowed(key, to) if to else "a redirect that names no address"
                if why or hop == MAX_REDIRECTS:
                    raise Refused(f"HTTP {status} to {to or 'nowhere'}: not followed ({why or 'more than ' + str(MAX_REDIRECTS) + ' redirects'})")
                url, host = to, llr.host_of(to)
        self.bytes += len(content)
        sha = hashlib.sha256(content).hexdigest()
        fn = f"{len(os.listdir(os.path.join(self.raw_dir, 'raw'))) + 1:03d}_{key}_{re.sub(r'[^A-Za-z0-9._-]+', '_', name)[:70]}"
        with open(os.path.join(self.raw_dir, "raw", fn), "wb") as f:
            f.write(content)
        head = content[:6000].decode("utf-8", "replace")
        if status != 200:
            self._note(key, url, status, content, now, fn, "not HTTP 200: left")
            raise Refused(f"HTTP {status}")
        if CHECK_WORDS.search(head) and "<html" in head.lower():
            self._note(key, url, status, content, now, fn, "answered with a check: not passed, left")
            raise Refused("the page answered with a robot or browser check; it was not passed")
        text = as_text(content)
        tpath = os.path.join(self.raw_dir, "text", fn + ".txt")
        with open(tpath, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        self._note(key, url, status, content, now, fn, "")
        return content.decode("utf-8", "replace"), {"url": asked, "text": norm(text), "text_file": tpath, "retrieved_at": now,
                                                    "text_sha256": hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()}

    @staticmethod
    def _now():
        return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _note(self, key, url, status, content, now, fn, note):
        with open(self.manifest, "a", encoding="utf-8", newline="") as f:
            csv.writer(f, lineterminator="\n").writerow([self.n, key, url, status, len(content),
                                                         hashlib.sha256(content).hexdigest() if content else "", now, fn, note])


# ---------------------------------------------------------------- the tables held
def read_events(path):
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)


def held_tables(in_dir):
    frames = [read_events(os.path.join(in_dir, t + ".csv")) for t in TABLES if os.path.exists(os.path.join(in_dir, t + ".csv"))]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=llr.COLS)


def held_of(table, key):
    """What is held of one regulator: {docket number: {topic, title, docket_url, grids, newest}}, every address held,
    every id held, and the day its lists were last read (the newest retrieved_at of its rows)."""
    name = llr.REGULATORS[key][0]
    part = table[table["regulator"] == name]
    dockets = {}
    for r in part.sort_values("event_date").to_dict("records"):
        d = dockets.setdefault(r["docket_number"], {"topic": "", "title": "", "docket_url": "", "newest": ""})
        d["topic"] = r["topic"] or d["topic"]
        d["title"] = r["proceeding_title"] or d["title"]
        d["docket_url"] = r["docket_url"] or d["docket_url"]
        d["newest"] = max(d["newest"], r["event_date"][:10])
    read = max((r[:10] for r in part["retrieved_at"] if r), default="")
    return {"name": name, "dockets": dockets, "urls": set(part["source_url"]), "ids": set(part["event_id"]),
            "last_read": read, "blob": " ".join(part["source_url"]) + " " + " ".join(part["sentence"]) + " " + " ".join(part["notes"])}


def baseline(held, today):
    """Lines dated on or after this day are new: the day the regulator's lists were last read, less MARGIN_DAYS."""
    base = held["last_read"] or today.isoformat()
    return (dt.date.fromisoformat(base) - dt.timedelta(days=MARGIN_DAYS)).isoformat()


def docket_about_topic(d):
    """The docket's own caption holds a topic term: every order in it is on the topic. Else a line must hold one."""
    return bool(topic_of(d["title"]))


# ---------------------------------------------------------------- one regulator at a time: its lines
# A line: {docket, date, line (the title line, the sentence), doc_title, doc_url, docket_url, kind, status_worded,
#          title (the proceeding's caption), rec (the saved list it stands in), list (what the list is)}.
def lines_txpuc(ask, held, since):
    out = []
    for d, info in sorted(held["dockets"].items()):
        url = info["docket_url"] or TX_FILINGS.format(n=d)
        page, rec = ask.get("txpuc", url, f"filings_{d}.html")
        out += parse_tx_filings(page, d, rec, url)
    top = max((int(d) for d in held["dockets"] if d.isdigit()), default=0)
    fresh = {}
    for w in ("large%20load", "data%20center"):
        url = TX_DOCKETS.format(w=w)
        page, rec = ask.get("txpuc", url, f"dockets_{w.replace('%20', '_')}.html")
        for c in parse_tx_dockets(page):
            if c["docket"] not in held["dockets"] and c["docket"].isdigit() and int(c["docket"]) > top:
                fresh.setdefault(c["docket"], dict(c, rec=rec))
    for d, c in sorted(fresh.items())[:MAX_NEW_DOCKETS]:   # a control number above the highest held: opened since
        url = TX_FILINGS.format(n=d)
        page, rec2 = ask.get("txpuc", url, f"filings_{d}.html")
        first = parse_tx_filings(page, d, rec2, url, every=True)
        day = min((x["date"] for x in first if x["date"]), default="")
        out.append({"docket": d, "date": day, "line": c["caption"], "doc_title": "", "doc_url": url, "docket_url": url,
                    "kind": "proceeding", "status_worded": "", "title": c["caption"], "rec": c["rec"],
                    "list": "the Interchange docket search (case style)"})
    return out


def parse_tx_filings(page, docket, rec, url, every=False):
    out = []
    for cells, links in table_rows(page):
        if len(cells) != 5 or not cells[0].isdigit():
            continue
        link = next((x for x in links if "itemNumber=" in x), "")
        out.append({"docket": docket, "date": day_of(cells[1]), "line": cells[4], "doc_title": cells[4],
                    "doc_url": urljoin("https://interchange.puc.texas.gov/", link) if link else url, "docket_url": url,
                    "kind": "order", "status_worded": "", "title": "", "rec": rec, "item": cells[0],
                    "list": "the Interchange filing list", "order": every or is_order(cells[4])})
    return out


def parse_tx_dockets(page):
    out = []
    for cells, _ in table_rows(page):
        if len(cells) == 4 and cells[0].isdigit():
            out.append({"docket": cells[0], "caption": cells[3]})
    return out


def lines_vascc(ask, held, since):
    out = []
    matters = dict(VA_MATTERS)
    for w in ("large%20load", "large-load", "data%20center"):
        url = VA_CASES.format(w=w)
        page, rec = ask.get("vascc", url, f"cases_{w.replace('%20', '_')}.json")
        for c in json.loads(page):
            num = c.get("Case_Number", "")
            matters.setdefault(num, c.get("MATTER_NO"))
            if num and num not in held["dockets"] and day_of(c.get("Case_Established_Date")) >= since:
                out.append({"docket": num, "date": day_of(c.get("Case_Established_Date")), "line": norm(c.get("Case_Caption")),
                            "doc_title": "", "doc_url": VA_DOCS.format(m=c.get("MATTER_NO")), "docket_url": "",
                            "kind": "proceeding", "status_worded": "", "title": norm(c.get("Case_Caption")), "rec": rec,
                            "list": "the docket search's case list (caption)"})
    for d in sorted(held["dockets"]):
        if not matters.get(d):
            continue
        url = VA_DOCS.format(m=matters[d])
        page, rec = ask.get("vascc", url, f"docs_{d}.json")
        out += parse_va_docs(page, d, rec)
    return out


def parse_va_docs(page, docket, rec):
    out = []
    for x in json.loads(page):
        name = norm(x.get("Document_Name"))
        parts = [p.strip() for p in name.split(" - ")]
        out.append({"docket": docket, "date": day_of(x.get("Date_Filed")), "line": name, "doc_title": name,
                    "doc_url": "https://www.scc.virginia.gov/docketsearch/DOCS/" + quote(x.get("FileName") or "", safe="!."),
                    "docket_url": "", "kind": "order", "status_worded": "", "title": "", "rec": rec,
                    "list": "the docket search's document list of the case", "order": any(is_order(p) for p in parts[1:])})
    return out


def lines_papuc(ask, held, since):
    out = []
    for d, info in sorted(held["dockets"].items()):
        url = info["docket_url"] or "https://www.puc.pa.gov/docket/" + d
        page, rec = ask.get("papuc", url, f"docket_{d}.html")
        out += parse_pa_docket(page, d, rec, url)
    return out


def parse_pa_docket(page, docket, rec, url):
    out = []
    for cells, links in table_rows(page):
        if len(cells) != 7 or cells[0] == "Document Name":
            continue
        doc = next((x for x in links if "/pcdocs/" in x), "")
        out.append({"docket": docket, "date": day_of(cells[5]) or day_of(cells[4]) or day_of(cells[3]),
                    "line": norm(cells[0] + " " + cells[1]), "doc_title": cells[0],
                    "doc_url": urljoin("https://www.puc.pa.gov/", doc) if doc else url, "docket_url": url, "kind": "order",
                    "status_worded": "", "title": "", "rec": rec, "list": "the docket page's document list",
                    "order": is_order(cells[1])})
    return out


def lines_gapsc(ask, held, since):
    out = []
    for d, info in sorted(held["dockets"].items()):
        if not d.isdigit():
            continue
        page, rec = ask.get("gapsc", GA_LIST.format(n=d), f"docket_{d}.json")
        for x in json.loads(page).get("resultsItems", []):
            line = norm(x.get("description"))
            out.append({"docket": d, "date": day_of(x.get("filedDate")), "line": line, "doc_title": line,
                        "doc_url": f"https://psc.ga.gov/search/facts-document/?documentId={x.get('documentId')}",
                        "docket_url": info["docket_url"], "kind": "order", "status_worded": "", "title": "", "rec": rec,
                        "list": "the docket's list of filings", "order": is_order(line), "doc_id": str(x.get("documentId"))})
    return out


def lines_azcc(ask, held, since):
    out = []
    for d, info in sorted(held["dockets"].items()):
        m = re.search(r"item-detail/(\d+)", info["docket_url"])
        if not m:
            continue   # the docket's record number is not held (no release of the commission links it): not listed
        page, rec = ask.get("azcc", "https://efiling.azcc.gov/api/eDocket/docket/" + m.group(1), f"docket_{m.group(1)}.json")
        j = json.loads(page)
        for x in j.get("decisions") or []:
            line = norm(x.get("description"))
            out.append({"docket": d, "date": day_of(x.get("decisionDate")), "line": line,
                        "doc_title": f"Decision No. {x.get('decisionNumber')}",
                        "doc_url": f"https://docket.images.azcc.gov/{x.get('imageNumber')}.pdf" if x.get("imageNumber") else info["docket_url"],
                        "docket_url": info["docket_url"], "kind": "order", "status_worded": "", "title": "", "rec": rec,
                        "list": "the eDocket record's list of decisions", "order": True, "doc_id": str(x.get("decisionNumber"))})
    return out


def lines_orpuc(ask, held, since):
    out = []
    for d, info in sorted(held["dockets"].items()):
        if "DocketID=" not in info["docket_url"]:
            continue   # the docket's DocketID is not held (the eDockets search is a form): not listed
        page, rec = ask.get("orpuc", info["docket_url"], f"docket_{d.replace(' ', '')}.html")
        out += parse_or_docket(page, d, rec, info["docket_url"])
    return out


OR_ROW = re.compile(r"(?is)<b>Date:</td>\s*<td[^>]*>\s*</b>\s*([\d/]+)\s*</td>\s*<td[^>]*>\s*<b>Action:(.*?)</td>(.*?)</tr>"
                    r"\s*<tr[^>]*>.*?<b>Description</b>\s*<br>(.*?)</td>")


def parse_or_docket(page, docket, rec, url):
    out = []
    for date, action, rest, desc in OR_ROW.findall(page):
        action, line = norm(llr.html_text(action)), norm(llr.html_text(desc))
        link = re.search(r'(?i)href="([^"]+)"', rest)
        out.append({"docket": docket, "date": day_of(date), "line": line, "doc_title": line,
                    "doc_url": urljoin("https://apps.puc.state.or.us/edockets/", llr.H.unescape(link.group(1))) if link else url,
                    "docket_url": url, "kind": "order", "status_worded": "", "title": "", "rec": rec,
                    "list": "the eDockets docket summary", "order": action.upper() == "ORDER",
                    "doc_id": " ".join(re.findall(r"\b\d{2}-\d{3}\b", line))})
    return out


def lines_cpuc(ask, held, since):
    out = []
    for d, info in sorted(held["dockets"].items()):
        if "P5_PROCEEDING_SELECT" not in info["docket_url"]:
            continue   # a resolution has no proceeding page
        url = info["docket_url"].replace("f?p=401:56:", "f?p=401:59:")
        page, rec = ask.get("cpuc", url, f"decisions_{re.sub(r'[^A-Za-z0-9]', '', d)}.html")
        out += parse_ca_decisions(page, d, rec, info["docket_url"])
    return out


def parse_ca_decisions(page, docket, rec, docket_url):
    out = []
    for cells, links in table_rows(page):
        if len(cells) != 5 or cells[3] == "Document Type":
            continue
        doc = next((x for x in links if "DocID=" in x), "")
        out.append({"docket": docket, "date": day_of(cells[0]) or day_of(cells[2]) or day_of(cells[1]), "line": cells[4],
                    "doc_title": cells[4], "doc_url": doc or docket_url, "docket_url": docket_url, "kind": "order",
                    "status_worded": "", "title": "", "rec": rec, "list": "the proceeding's decisions list",
                    "order": cells[3].strip().upper() == "DECISION", "doc_id": (re.search(r"DocID=(\d+)", doc) or [None, ""])[1]})
    return out


def lines_iurc(ask, held, since):
    page, rec = ask.get("iurc", IN_ORDERS, "weekly_orders.html")
    out, seen = [], set()
    for cells, links in table_rows(page):
        doc = next((x for x in links if re.search(r"/ord_[^/]+\.pdf$", x, re.I)), "")
        if len(cells) != 2 or not doc or doc in seen:
            continue
        seen.add(doc)
        m = re.search(r"_(\d{2})(\d{2})(\d{2})\.pdf$", doc, re.I)   # the commission names an order's file by its date
        out.append({"docket": cells[0], "date": day_of(f"{m.group(1)}/{m.group(2)}/20{m.group(3)}") if m else "",
                    "line": norm(cells[0] + " " + cells[1]), "doc_title": "", "doc_url": urljoin("https://www.in.gov/", doc),
                    "docket_url": "", "kind": "order", "status_worded": "", "title": "", "rec": rec,
                    "list": "the weekly orders page", "order": True})   # every line of the weekly orders page is an order
    return out


def fr_dockets(ids):
    return [m for x in ids or [] for m in re.findall(r"\b[A-Z]{2}\d{2}-\d+(?:-\d{3})?\b", x or "")]


def lines_ferc(ask, held, since):
    page, rec = ask.get("ferc", FR_LIST.format(since=since), f"federal_register_ferc_since_{since}.json")
    out, fresh = [], 0
    bases = {llr.docket_base(d): d for d in held["dockets"]} if hasattr(llr, "docket_base") else \
        {re.sub(r"-\d{3}$", "", d): d for d in held["dockets"]}
    for x in json.loads(page).get("results", []):
        title = norm(x.get("title"))
        ids = fr_dockets(x.get("docket_ids"))
        if FR_ROUTINE.search(title) or not ids or len(ids) > MAX_DOCKETS_IN_A_LINE:
            continue
        mine = [i for i in ids if re.sub(r"-\d{3}$", "", i) in bases]
        doc = x.get("pdf_url") or x.get("html_url") or ""
        part = [p.strip() for p in title.split(";")]
        if mine:
            out.append({"docket": mine[0], "held_as": bases[re.sub(r"-\d{3}$", "", mine[0])], "date": day_of(x.get("publication_date")),
                        "line": title, "doc_title": title, "doc_url": doc, "docket_url": "", "kind": "order",
                        "status_worded": norm(x.get("action")), "title": "", "rec": rec,
                        "list": "the Federal Register's list of the Commission's documents",
                        "order": any(is_order(p) for p in part)})
        elif topic_of(title) and fresh < MAX_NEW_DOCKETS:
            fresh += 1
            out.append({"docket": ids[0], "date": day_of(x.get("publication_date")), "line": title, "doc_title": title,
                        "doc_url": doc, "docket_url": "", "kind": "proceeding", "status_worded": norm(x.get("action")),
                        "title": title, "rec": rec, "list": "the Federal Register's list of the Commission's documents"})
    return out


LINES = {"ferc": lines_ferc, "txpuc": lines_txpuc, "vascc": lines_vascc, "iurc": lines_iurc, "papuc": lines_papuc,
         "gapsc": lines_gapsc, "azcc": lines_azcc, "orpuc": lines_orpuc, "cpuc": lines_cpuc}


# ---------------------------------------------------------------- lines to rows
def already_held(c, held):
    """The line's document is a row already: its address is held, or the list's own number of it stands in an address,
    sentence or note held (a Texas item, a California DocID, a Georgia document, an Oregon order, an Arizona decision)."""
    if c["doc_url"] in held["urls"]:
        return True
    if c.get("item") and re.search(rf"/{re.escape(c['docket'])}_{re.escape(c['item'])}_\d+\.PDF", held["blob"], re.I):
        return True
    for num in (c.get("doc_id") or "").split():
        if num and re.search(r"(?<![0-9])" + re.escape(num) + r"(?![0-9])", held["blob"]):
            return True
    return False


def to_rows(key, lines, held, since, terms, today):
    """(rows, left out [(line, why)]) of one regulator's lines, by the rules in this file's head."""
    name, state, _ = llr.REGULATORS[key]
    rows, left = [], []
    for c in lines:
        d = held["dockets"].get(c.get("held_as") or c["docket"])
        if c["kind"] == "order":
            if not c.get("order") or not d:
                continue   # a party's filing, or a docket not held: never a row and not worth a line of the log
            if any(w in c["line"].lower() for w in PROCEDURAL):
                continue
            if not c["date"] or c["date"] < since:
                continue
            if already_held(c, held):
                continue
            if not (docket_about_topic(d) or topic_of(c["line"])):
                left.append((c, "an order in a docket held whose caption names no topic term, and the line names none"))
                continue
            topic, title = d["topic"], d["title"]
            cls = "decided"
            note = (f"Cut from {c['list']}: the list's own title line for a document of {c['date']}; the document itself was "
                    "not read. Status class decided by rule (the list words the line as an order). Topic: the docket's own.")
        else:
            topic, title = topic_of(c["line"]), c["title"]
            if not topic:
                continue
            cls = "open" if re.search(r"\b(open|active)\b", c["status_worded"], re.I) else "not stated"
            note = (f"Cut from {c['list']}: the title line of a docket not held before. Topic by the words of the line "
                    "(TOPIC_RULES of policy_monitor_refresh.py), the nearest of the four, not a person's reading.")
        if municipal(c["line"] + " " + title):
            left.append((c, "municipal (%s): out of scope" % ", ".join(municipal(c["line"] + " " + title))))
            continue
        sent = norm(c["line"])
        if not sent or sent not in c["rec"]["text"]:
            left.append((c, "the line is not a literal substring of the saved list's text"))
            continue
        r = {"regulator": name, "jurisdiction": "federal" if key == "ferc" else "state", "state": state, "grids": "",
             "docket_number": c.get("held_as") or c["docket"], "proceeding_title": title, "row_kind": c["kind"], "topic": topic,
             "document_title": c["doc_title"], "document_date": c["date"], "status_as_worded": c["status_worded"],
             "status_class": cls, "document_url": c["doc_url"], "docket_url": c["docket_url"], "page": "", "sentence": sent,
             "local_file": "", "retrieved_at": c["rec"]["retrieved_at"], "verified": "yes", "notes": note,
             "terms_url": (terms.get(name) or {}).get("terms_url", "") or ""}
        why = llr.row_check(r)
        if why:
            left.append((c, "; ".join(why)))
            continue
        eid = llr.event_id(key, r)
        if eid in held["ids"] or any(x["event_id"] == eid for x in rows):
            continue
        rel = os.path.relpath(c["rec"]["text_file"], os.path.dirname(ip.RAW_DIR)).replace("\\", "/")
        rows.append({
            "event_id": eid, "event_date": r["document_date"], "event_type": "regulatory_" + r["row_kind"], "parties": name,
            "entity_ids": "", "mw": "", "price": "", "currency": "", "status": cls, "source": f"{key}:dockets",
            "source_url": r["document_url"], "regulator": name, "jurisdiction": r["jurisdiction"], "state": state, "grids": "",
            "docket_number": r["docket_number"], "proceeding_title": norm(title), "row_kind": r["row_kind"], "topic": topic,
            "document_title": norm(r["document_title"]), "status_as_worded": norm(r["status_as_worded"]), "status_class": cls,
            "docket_url": r["docket_url"], "page": "", "sentence": sent, "sentence_from": c["list"].replace("the ", "", 1),
            "sentence_kind": SENTENCE_KIND, "row_flag": FLAG_LIST, "text_file": "warehouse/" + rel if not rel.startswith("..") else rel,
            "text_sha256": c["rec"]["text_sha256"], "proved_how": "the saved list's text holds the line",
            "collected_in": "daily refresh (policy_monitor_refresh.py)", "notes": note, "terms_url": r["terms_url"],
            "retrieved_at": r["retrieved_at"]})
    return rows, left


# ---------------------------------------------------------------- writing
def old_header(path):
    """The header lines a table already has, without its merge line and without an earlier line of this step."""
    out = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            t = ln[1:].strip()
            if not t.startswith("File holds ") and not t.startswith("Daily refresh (session 157)"):
                out.append(t)
    return out


def write_tables(rows, terms, run_id, log, detail):
    """New rows into the two tables, by each regulator's terms class, merged by event_id (ip.write_csv: the data lock
    where the table is warehouse/output's). A table that gains no row is not touched."""
    frame = pd.DataFrame(rows, columns=llr.COLS)
    lic, _ = llr.license_of(set(frame["regulator"]), terms)
    wrote = {}
    for name, want in ((llr.NAME, "public"), (llr.NAME_HELD, "internal")):
        part = frame[frame["regulator"].map(lic) == want].reset_index(drop=True)
        if not len(part):
            continue
        path = os.path.join(ip.OUT_DIR, name + ".csv")
        if not os.path.exists(path):
            raise RuntimeError(f"{name} is not on this machine: rows are added to a table held, never to an empty one")
        header = old_header(path)
        lic_at = next((i for i, h in enumerate(header) if h.startswith("License:")), len(header))
        header.insert(lic_at, f"Daily refresh (session 157): warehouse/connectors/policy_monitor_refresh.py adds what is new in each "
                      f"regulator's open list (warehouse/config/policy_monitor_feeds.json). Such a row's sentence is the list's own "
                      f"title line (sentence_kind '{SENTENCE_KIND}'; row_flag says so), not the document's text. Latest run {run_id} "
                      f"(UTC): {detail}. Run log: warehouse/output/logs/{NAME}_{run_id}.log. Method: docs/methods/policy_monitor.md.")
        ip.write_csv(part, name, header, log, cols=llr.COLS, key=["event_id"], time_col="event_date")
        ip.update_sources(llr.registry_entries(part, name, lic))
        wrote[name] = len(part)
    return wrote


def ensure_tables(log):
    """On a machine without the two tables (GitHub's runner), rebuild them from the ERW's own archive, as
    warehouse/scheduled.py does for its steps. True when both are there."""
    for t in TABLES:
        path = os.path.join(ip.OUT_DIR, t + ".csv")
        if os.path.exists(path):
            continue
        log(f"{t} is not on this machine; rebuilding it from the archive (erw-archive)")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "archive", "restore.py"), t, "--from-bucket",
                            "--out", path], cwd=ROOT)
        if r.returncode != 0 and os.path.exists(path):
            os.remove(path)   # a rebuild that did not finish is not an input
    return all(os.path.exists(os.path.join(ip.OUT_DIR, t + ".csv")) for t in TABLES)


def load_feeds(path=FEEDS_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def day_file(today):
    return os.path.join(ip.RAW_DIR, NAME, f"day_{today:%Y%m%d}.json")


def load_day(today):
    """What earlier runs of the step did today: {"requests": n, "left": {key: why}, "done": [keys]}. A day's ceiling is
    a day's, so a second run (warehouse/health.py tries a failed step once more) starts from the first run's count; a
    regulator that failed or refused today is not asked again today (nothing is retried round a refusal); and one
    whose lists were read today is not read twice."""
    path = day_file(today)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"requests": 0, "left": {}, "done": []}


def save_day(today, day):
    os.makedirs(os.path.dirname(day_file(today)), exist_ok=True)
    with open(day_file(today), "w", encoding="utf-8", newline="\n") as f:
        json.dump(day, f, indent=1)


def run(feeds, table, ask, log, today, only=None, since=None, day=None, again=False):
    """Every refreshed regulator in turn: ({key: result}, rows, left). A regulator's failure never stops the others;
    Stop (a ceiling) ends the asking and keeps what was found. day: what earlier runs did today (load_day)."""
    day = day if day is not None else {"requests": 0, "left": {}, "done": []}
    terms = llr.load_terms()
    results, rows, left = {}, [], []
    stopped = ""
    for f in feeds["regulators"]:
        key = f["key"]
        if only and key not in only:
            continue
        if not f["refreshed"]:
            results[key] = {"requests": 0, "new_rows": 0, "status": "not requested", "detail": f["reason"]}
            continue
        if key not in LINES or key not in HOSTS:
            results[key] = {"requests": 0, "new_rows": 0, "status": "not requested", "detail": "no reader for this regulator's list"}
            continue
        if ip.paused(key):   # session 172: a paused publisher (warehouse/metadata/paused_sources.csv) is sent nothing
            p = ip.paused(key)
            results[key] = {"requests": 0, "new_rows": 0, "status": "not requested",
                            "detail": (f"Paused since {p['paused_on']}: {p['reason']}; pending {p['until']} "
                                       "(warehouse/metadata/paused_sources.csv; the docket lists held stay as they are)")[:300]}
            log(f"  {key}: {results[key]}")
            continue
        if stopped:
            results[key] = {"requests": 0, "new_rows": 0, "status": "not requested", "detail": stopped}
            continue
        if key in day["left"]:
            results[key] = {"requests": 0, "new_rows": 0, "status": "failed",
                            "detail": f"not asked again today: {day['left'][key]}"}
            continue
        if key in day["done"] and not again:
            results[key] = {"requests": 0, "new_rows": 0, "status": "ok", "detail": "its lists were read earlier today: not read twice"}
            continue
        held = held_of(table, key)
        start = since or baseline(held, today)
        before = ask.n
        try:
            lines = LINES[key](ask, held, start)
            got, out = to_rows(key, lines, held, start, terms, today)
            rows += got
            left += [(key, c, why) for c, why in out]
            results[key] = {"requests": ask.n - before, "new_rows": len(got), "status": "ok",
                            "detail": f"{len(lines)} list lines read in {len(held['dockets'])} dockets held; new since {start}: {len(got)}"}
            day["done"].append(key)
        except Stop as exc:
            stopped = str(exc)
            results[key] = {"requests": ask.n - before, "new_rows": 0, "status": "stopped", "detail": stopped}
        except Refused as exc:
            results[key] = {"requests": ask.n - before, "new_rows": 0, "status": "failed",
                            "detail": f"{exc}; the regulator's remaining lists were not asked this run"}
            day["left"][key] = str(exc)[:200]
        except Exception as exc:   # a list whose shape changed: recorded, the others go on
            results[key] = {"requests": ask.n - before, "new_rows": 0, "status": "failed", "detail": ip.redact(repr(exc))[:240]}
            day["left"][key] = ip.redact(repr(exc))[:200]
        log(f"  {key}: {results[key]}")
    return results, rows, left


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the policy monitor's daily refresh of the regulators' open lists")
    ap.add_argument("--out-dir", help="a trial run: every output under this directory; nothing in warehouse/output")
    ap.add_argument("--in-dir", help="read the two tables held from this directory (a trial copies them into --out-dir)")
    ap.add_argument("--offline", help="a directory of saved list pages with index.json {address: file}: no request is made")
    ap.add_argument("--only", help="regulator keys, comma separated")
    ap.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    ap.add_argument("--since", help="YYYY-MM-DD: take lines dated on or after this day, in place of the day each regulator's "
                                    "lists were last read less two days (a person's catch-up after a gap)")
    ap.add_argument("--again", action="store_true", help="read again the lists already read today (never a regulator that "
                                                         "failed or refused today)")
    a = ap.parse_args(argv)
    if a.max_requests > MAX_REQUESTS:
        ap.error(f"--max-requests may lower the ceiling of {MAX_REQUESTS}, never raise it")
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    say = lambda m: (log(m), print(m))   # noqa: E731
    in_dir = os.path.abspath(a.in_dir) if a.in_dir else ip.OUT_DIR
    if a.out_dir and os.path.abspath(in_dir) != os.path.abspath(ip.OUT_DIR):
        for t in TABLES:   # a trial merges into its own copy of the tables held
            src, dst = os.path.join(in_dir, t + ".csv"), os.path.join(ip.OUT_DIR, t + ".csv")
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copyfile(src, dst)
    if ip.paused("miso"):
        log("MISO is paused (warehouse/metadata/paused_sources.csv): this step never requests misoenergy.org, paused or not")
    for key in HOSTS:   # session 172: a regulator in the pause file is sent nothing (Virginia since 10 October 2026)
        if ip.paused(key):
            log(f"{key} is paused since {ip.paused(key)['paused_on']} (warehouse/metadata/paused_sources.csv): "
                f"no request to {', '.join(HOSTS[key])} this run")
    if not a.out_dir and not ensure_tables(log):
        msg = (f"{NAME} SKIPPED: large_load_rules or large_load_rules_internal is not on this machine and could not be rebuilt "
               "from the archive, so nothing was requested and nothing was written")
        say(msg)
        log.close()
        return int(os.environ.get("ERW_SKIP_EXIT") or 0)
    table = held_tables(ip.OUT_DIR)
    feeds = load_feeds()
    raw_dir = os.path.join(ip.RAW_DIR, NAME, run_id)
    today = dt.datetime.now(dt.timezone.utc).date()
    if a.since and day_of(a.since) != a.since:
        ap.error("--since is a day, YYYY-MM-DD")
    day = {"requests": 0, "left": {}, "done": []} if a.offline else load_day(today)
    ask = Asker(raw_dir, log, max_requests=a.max_requests, offline=a.offline, used=day["requests"])
    only = [k.strip() for k in a.only.split(",")] if a.only else None
    say(f"{NAME} {run_id}: {len(table)} rows held; ceilings {a.max_requests} requests a day ({day['requests']} made earlier today), "
        "one a second to a host")
    results, rows, left = run(feeds, table, ask, log, today, only, since=a.since, day=day, again=a.again)
    if not a.offline:
        day["requests"] += ask.n
        save_day(today, day)
    by = {k: v["new_rows"] for k, v in results.items() if v["new_rows"]}
    detail = (f"{ask.n} requests of {a.max_requests}, {ask.bytes} bytes; {len(rows)} new rows ({by or 'none'}); "
              f"{sum(1 for v in results.values() if v['status'] == 'failed')} regulators failed, "
              f"{sum(1 for v in results.values() if v['status'] == 'not requested')} not requested")
    code = 0
    try:
        wrote = write_tables(rows, llr.load_terms(), run_id, lambda m: log(str(m).strip()), detail) if rows else {}
    except Exception as exc:
        wrote = {}
        code = 1
        say(f"{NAME} FAILED writing: {ip.redact(repr(exc))[:300]}")
    last = {"at_utc": run_id[:4] + "-" + run_id[4:6] + "-" + run_id[6:8] + "T" + run_id[9:11] + ":" + run_id[11:13] + ":" + run_id[13:15] + "Z",
            "requests": ask.n, "bytes": ask.bytes, "regulators": results, "tables_written": wrote}
    # the facts of the last run, for the site's refresh.json: beside the raw files always, and at a trial's root too
    for path in [os.path.join(ip.RAW_DIR, NAME, "last_run.json")] + ([os.path.join(ip.OUT_DIR, f"{NAME}_last_run.json")] if a.out_dir else []):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(last, f, indent=1)
    with open(os.path.join(raw_dir, "left_out.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["regulator", "docket", "date", "line", "why"])
        for key, c, why in left:
            w.writerow([key, c["docket"], c["date"], c["line"], why])
    for r in rows:
        say(f"  NEW {r['regulator']} | {r['docket_number']} | {r['event_date']} | {r['row_kind']} | {r['sentence'][:140]}")
    status = [dict(table=llr.NAME, market=k, status="failed" if v["status"] == "failed" else "ok",
                   detail=f"{v['status']}: {v['requests']} requests, {v['new_rows']} new rows; {v['detail']}"[:300]) for k, v in results.items()]
    ip.write_status(NAME, run_id, status + [dict(table=llr.NAME, market="all", status="ok" if code == 0 else "failed", detail=detail)])
    say(f"{NAME}: {detail}; tables written: {wrote or 'none'}")
    failed = [k for k, v in results.items() if v["status"] == "failed"]
    if failed:
        say(f"{NAME}: FAILED for {', '.join(failed)} (recorded; the others ran): " + "; ".join(f"{k}: {results[k]['detail'][:120]}" for k in failed))
    log.close()
    # a regulator that failed makes the step's exit 1, so that warehouse/health.py records it with its reason; as a soft
    # step that never stops the run, and the second try asks nothing of a regulator that failed (load_day)
    return 1 if (code or failed) else 0


if __name__ == "__main__":
    sys.exit(main())
