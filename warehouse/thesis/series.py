#!/usr/bin/env python3
"""The real series behind a Thesis Builder trend (session 169). INTERNAL.

Energy Research Warehouse (ERW), Thesis Builder. The owner's ruling of 8 October 2026: "five trends, each a title, a
one-sentence "Fact:" with its number, one interactive chart of a real series (the warehouse first; otherwise FRED,
Census, BLS or EIA), and a source line. Every number traces to a source. Nothing is invented. A trend with no real
series says so and is not drawn."

This module holds the series a trend may be drawn with and pulls the one chosen. It decides nothing about which: the
run's classification call (warehouse/thesis/run.py, on the small model) picks one id per trend from catalog() or
"none". A series is drawn as its publisher gives it: every value as published, at its own frequency, never filled,
smoothed, averaged across a gap or rescaled. A pull that fails is recorded with its error and the trend says so.

THE CATALOG, IN ORDER
  1. The warehouse's own tables (warehouse_catalog): every entity and variable of a public series table of the
     coverage file whose interval is monthly, weekly or annual and that holds at least MIN_POINTS values, read from
     the tables on the machine (--in-dir). Nothing is requested for these.
  2. Outside, the publishers the owner named, through their APIs only:
       EIA     api.eia.gov, API v2, with EIA_API_KEY from the root .env (the key is never written anywhere)
       BLS     NOT REQUESTED: api.bls.gov's robots.txt reads "User-agent: *" and "Disallow: /" (read 9 October 2026),
               and www.bls.gov refused the request for its robots.txt and terms (HTTP 403). Recorded and left (LEFT).
       Census  NOT REQUESTED: a key is required. On 10 October 2026 (session 175) api.census.gov answered a request
               for its robots.txt with "Request Rejected" (HTML, HTTP 200) and a keyless County Business Patterns
               request with HTTP 302 to https://api.census.gov/data/missing_key.html; the .env holds no Census key
               (a free one is given at https://api.census.gov/data/key_signup.html). Recorded and left (LEFT); _cbp()
               stays for the day a key is held.
       FRED    through its public CSV endpoint, https://fred.stlouisfed.org/graph/fredgraph.csv?id=<series> (session
               175, the owner's approval of 9 October 2026), not its API (which needs a key). Read 10 October 2026:
               fred.stlouisfed.org/robots.txt allows every agent every path but six (graph-landing.php, image.php,
               fredgraph.png, searchresults, the widget, seriesBeta; Crawl-delay 1), so fredgraph.csv is allowed; the
               FRED Services Terms of Use (fred.stlouisfed.org/legal/) permit "non-commercial, educational, and
               personal uses", to "Conduct research", to "View, download, and print FRED content" and to "Create
               individual visualizations of FRED data", and forbid scripts or bots used "in any manner that is
               excessive, disruptive, or adversely impacts the stability, performance, or availability of the FRED
               Services" (the summary's "Don't do any data mining, scraping or extraction of FRED data" is that
               clause, which the full terms qualify). A run asks for at most five small CSVs, one a second, and cites
               each as FRED's "Cite" tab does. The CSV carries no title: the title is the catalog's, written from
               FRED's own listing, and the CSV's header must name the series asked for or the pull is refused.
     The outside catalog is a fixed list (OUTSIDE below), each entry checked by hand against its publisher's own
     description when it was added; the title shown is the one the publisher's answer gives wherever the answer gives
     one, and a pull whose answer names another series than the one asked for is refused.

THE PULL
  * One plain GET a request, the only header the User-Agent below (the owner's contact string, nothing else).
  * Each host's robots.txt is read before its first request of a day (it counts as a request); a host whose file
    cannot be read, or that disallows the path for all agents, is not requested.
  * The ceiling: Count (a file the runs of a session share) holds every request; a request that would pass the
    ceiling is not made. MAX_REQUESTS_RUN holds one run inside its own ceiling on production.
"""

import datetime as dt
import json
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.robotparser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
UA = "ERW research project, github.com/SamuelEnrique/erw"
TIMEOUT = 30
MAX_REQUESTS_RUN = 20           # one run: 3 robots files and at most 5 series, Census at most 4 requests each
MIN_POINTS = 8
MAX_POINTS = 240                # a long series is drawn from its latest MAX_POINTS values; the cut is stated
MAX_YEARS = 30                  # an annual series is drawn from its latest MAX_YEARS values (session 169's run 2 drew 89 years from 1936)
HOST_GAP = 1.0


class Ceiling(RuntimeError):
    pass


class Count:
    """The requests of a session, by host, kept in a file the runs share; the ceiling is checked before a request."""

    def __init__(self, path=None, ceiling=MAX_REQUESTS_RUN):
        self.path, self.ceiling = path, ceiling
        self.n = {"requests": 0, "by_host": {}, "log": []}
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.n.update(json.load(f))

    def take(self, url):
        if self.n["requests"] + 1 > self.ceiling:
            raise Ceiling(f"the ceiling of {self.ceiling} requests is reached; {url.split('?')[0]} not requested")
        host = urllib.parse.urlsplit(url).hostname or ""
        self.n["requests"] += 1
        self.n["by_host"][host] = self.n["by_host"].get(host, 0) + 1
        self.n["log"].append({"at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "url": redact(url)})
        if self.path:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path + ".tmp", "w", encoding="utf-8") as f:
                json.dump(self.n, f, indent=1)
            os.replace(self.path + ".tmp", self.path)


def redact(url):
    """An address as it may be written down: a key in it is replaced."""
    return re.sub(r"(api_key|registrationkey|key)=[^&]+", r"\1=<key>", url, flags=re.I)


_last = {}
_robots = {}


def get(url, count, log=None, raw_dir=None):
    """One counted GET. Returns (status, bytes). Raises Ceiling before a request the ceiling does not allow."""
    host = urllib.parse.urlsplit(url).hostname or ""
    wait = HOST_GAP - (time.time() - _last.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    count.take(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    _last[host] = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body, status = resp.read(), resp.status
    except urllib.error.HTTPError as e:
        body, status = e.read() or b"", e.code
    if log:
        log(f"    GET {redact(url)[:160]}: HTTP {status}, {len(body)} bytes")
    if raw_dir:
        import hashlib
        os.makedirs(raw_dir, exist_ok=True)
        with open(os.path.join(raw_dir, hashlib.sha256(body).hexdigest() + ".bin"), "wb") as f:
            f.write(body)
    return status, body


def robots_ok(url, count, log=None):
    """Is the path allowed to every agent by its host's robots.txt? Read once a process; unreadable is a refusal."""
    parts = urllib.parse.urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in _robots:
        status, body = get(base + "/robots.txt", count, log)
        if status == 404 or (status in (401, 403) and body.lstrip()[:1] == b"{" and b"API_KEY_MISSING" in body):
            # no file: nothing is disallowed. api.eia.gov has none: every path, /robots.txt too, answers with the API's own
            # JSON error for a request without its key (read 9 October 2026), which is not a robots refusal
            _robots[base] = None
        elif status != 200:
            _robots[base] = False
        else:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(body.decode("utf-8", "replace").splitlines())
            _robots[base] = rp
    rp = _robots[base]
    if rp is False:
        return False
    return True if rp is None else rp.can_fetch("*", url)


# ---------------------------------------------------------------------------------------------
# the outside catalog: each entry is one series of one publisher, its API route and what it is
# ---------------------------------------------------------------------------------------------

EIA_OPS = "https://api.eia.gov/v2/electricity/electric-power-operational-data/data/"
EIA_GAS = "https://api.eia.gov/v2/natural-gas/prod/sum/data/"
EIA_CRUDE = "https://api.eia.gov/v2/petroleum/crd/crpdn/data/"
EIA_RETAIL = "https://api.eia.gov/v2/electricity/retail-sales/data/"
EIA_TOTAL = "https://api.eia.gov/v2/total-energy/data/"


def _eia_msn(msn, title, unit):
    """A series of the Monthly Energy Review (total-energy), annual, by its MSN code; the title shown is EIA's own."""
    return {"id": f"eia:mer:{msn}", "source": "EIA", "title": title, "unit": unit, "freq": "annual", "route": EIA_TOTAL,
            "params": {"frequency": "annual", "data[0]": "value", "facets[msn][]": msn}, "field": "value", "check": {"msn": msn}, "title_from": "description"}


def _eia_gen(fuel, label):
    return {"id": f"eia:generation:{fuel}", "source": "EIA", "title": f"US net generation, {label}, all sectors", "unit": "thousand MWh", "freq": "annual",
            "route": EIA_OPS, "params": {"frequency": "annual", "data[0]": "generation", "facets[location][]": "US", "facets[sectorid][]": "99", "facets[fueltypeid][]": fuel},
            "field": "generation", "check": {"fueltypeid": fuel, "location": "US"}, "title_from": "fuelTypeDescription"}


def _eia_series(route, sid, title, unit):
    return {"id": f"eia:{sid}", "source": "EIA", "title": title, "unit": unit, "freq": "annual", "route": route,
            "params": {"frequency": "annual", "data[0]": "value", "facets[series][]": sid}, "field": "value", "check": {"series": sid}, "title_from": "series-description"}


def _bls(sid, title, unit):
    return {"id": f"bls:{sid}", "source": "BLS", "title": title, "unit": unit, "freq": "monthly", "series": sid}


def _fred(sid, title, unit, freq="monthly"):
    """A FRED series by its id, read from fredgraph.csv. The title is FRED's own, as the catalog records it."""
    return {"id": f"fred:{sid}", "source": "FRED", "title": title, "unit": unit, "freq": freq, "series": sid}


def _cbp(naics, title):
    return {"id": f"census:cbp:{naics}", "source": "Census", "title": f"US establishments, NAICS {naics} ({title})", "unit": "establishments", "freq": "annual", "naics": naics}


OUTSIDE = [
    _eia_gen("GEO", "geothermal"), _eia_gen("SUN", "solar"), _eia_gen("WND", "wind"), _eia_gen("NUC", "nuclear"), _eia_gen("NG", "natural gas"),
    _eia_gen("COL", "coal"), _eia_gen("HYC", "conventional hydroelectric"), _eia_gen("ALL", "all fuels"),
    _eia_series(EIA_GAS, "N9010US2", "US natural gas gross withdrawals", "million cubic feet"),
    _eia_series(EIA_GAS, "N9040US2", "US natural gas vented and flared", "million cubic feet"),
    _eia_series(EIA_GAS, "N9050US2", "US natural gas marketed production", "million cubic feet"),
    _eia_series(EIA_CRUDE, "MCRFPUS2", "US field production of crude oil", "thousand barrels per day"),
    _eia_series("https://api.eia.gov/v2/natural-gas/cons/sum/data/", "N9140US2", "US natural gas total consumption", "million cubic feet"),
    _eia_msn("GETCBUS", "Geothermal energy consumption, US", "trillion Btu"), _eia_msn("SOTCBUS", "Solar energy consumption, US", "trillion Btu"),
    _eia_msn("WYTCBUS", "Wind energy consumption, US", "trillion Btu"), _eia_msn("REPRBUS", "Total renewable energy production, US", "trillion Btu"),
    _eia_msn("TETCBUS", "Total primary energy consumption, US", "trillion Btu"),
    {"id": "eia:retail-price:IND", "source": "EIA", "title": "US average retail price of electricity, industrial", "unit": "cents per kWh", "freq": "annual", "route": EIA_RETAIL,
     "params": {"frequency": "annual", "data[0]": "price", "facets[stateid][]": "US", "facets[sectorid][]": "IND"}, "field": "price", "check": {"stateid": "US", "sectorid": "IND"}, "title_from": None},
    {"id": "eia:retail-sales:COM", "source": "EIA", "title": "US retail sales of electricity, commercial sector", "unit": "million kWh", "freq": "annual", "route": EIA_RETAIL,
     "params": {"frequency": "annual", "data[0]": "sales", "facets[stateid][]": "US", "facets[sectorid][]": "COM"}, "field": "sales", "check": {"stateid": "US", "sectorid": "COM"}, "title_from": None},
    # FRED (session 175): monthly series of the Federal Reserve Bank of St. Louis's database, each by its id, the title
    # as FRED lists it (fredgraph.csv carries none)
    _fred("MCOILWTICO", "Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma", "dollars per barrel"),
    _fred("MHHNGSP", "Henry Hub Natural Gas Spot Price", "dollars per million BTU"),
    _fred("GASREGM", "US Regular All Formulations Gas Price", "dollars per gallon"),
    _fred("PNRGINDEXM", "Global Price of Energy Index", "index 2016=100"),
    _fred("IPG211S", "Industrial Production: Mining: Oil and Gas Extraction (NAICS = 211)", "index 2017=100"),
    _fred("CAPUTLG211S", "Capacity Utilization: Mining: Oil and Gas Extraction (NAICS = 211)", "percent of capacity"),
    _fred("IPUTIL", "Industrial Production: Utilities (NAICS = 2211,2)", "index 2017=100"),
    _fred("IPG2211S", "Industrial Production: Utilities: Electric Power Generation, Transmission, and Distribution (NAICS = 2211)", "index 2017=100"),
    _fred("CES1021100001", "All Employees, Oil and Gas Extraction", "thousands of persons"),
    _fred("CES4422000001", "All Employees, Utilities", "thousands of persons"),
    _fred("CES2023700001", "All Employees, Heavy and Civil Engineering Construction", "thousands of persons"),
    _fred("PCU211211", "Producer Price Index by Industry: Oil and Gas Extraction", "index Dec 1985=100"),
    _fred("PCU22112211", "Producer Price Index by Industry: Electric Power Generation, Transmission and Distribution", "index Dec 1990=100"),
    _fred("PCU333611333611", "Producer Price Index by Industry: Turbine and Turbine Generator Set Units Manufacturing", "index Dec 1984=100"),
    _fred("TLPWRCONS", "Total Construction Spending: Power in the United States", "millions of dollars, seasonally adjusted annual rate"),
    _fred("CUSR0000SEHF01", "Consumer Price Index for All Urban Consumers: Electricity in U.S. City Average", "index 1982-1984=100"),
    _fred("CUSR0000SEHF02", "Consumer Price Index for All Urban Consumers: Utility (Piped) Gas Service in U.S. City Average", "index 1982-1984=100"),
    _fred("GS10", "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity, Quoted on an Investment Basis", "percent"),
]
BY_ID = {e["id"]: e for e in OUTSIDE}
# The publishers named by the owner that a run does not request, and why (session 169). _bls() stays for the day BLS's
# robots.txt allows the API path.
LEFT = {"Census": "a Census API key is required: api.census.gov answers a keyless request with HTTP 302 to its missing_key.html page "
                  "(10 October 2026), and the root .env holds no Census key (a free one is given at api.census.gov/data/key_signup.html)",
        "BLS": "api.bls.gov's robots.txt disallows every path to every agent, and www.bls.gov refused the request for its terms (HTTP 403)"}
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
FRED_TERMS = ("FRED Services Terms of Use, fred.stlouisfed.org/legal/, read 10 October 2026: non-commercial, educational and personal use; "
              "research, downloading and individual visualizations allowed; scripts or bots forbidden only when excessive or disruptive")
# Census's terms: "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."
CENSUS_NOTICE = "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."
CBP_YEARS = (2019, 2020, 2021, 2022)


# ---------------------------------------------------------------------------------------------
# the warehouse's catalog (no request)
# ---------------------------------------------------------------------------------------------

def _read(path):
    import pandas as pd
    with open(path, encoding="utf-8") as f:
        head = []
        for ln in f:
            if not ln.startswith("#"):
                break
            head.append(ln)
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False), "".join(head)


def warehouse_catalog(table_dir, log=None):
    """[entry] for each entity and variable of the warehouse's public series tables of a monthly, weekly or annual
    interval held on this machine. An entry's id is erw:<table>|<entity>|<variable>."""
    import pandas as pd
    cov_path = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
    if not table_dir or not os.path.exists(cov_path):
        return []
    cov = pd.read_csv(cov_path, dtype=str, keep_default_na=False)
    # the source tables only: a derived table's rows are the ERW's own computations, read on their own pages
    keep = cov[(cov["license"] == "public") & cov["interval"].isin(["P1M", "P1Y", "P1W"]) & (cov["derived"] == "no")
               & (pd.to_numeric(cov["n_nodes"], errors="coerce").fillna(999) <= 40)]
    out = []
    for _, c in keep.iterrows():
        path = os.path.join(table_dir, c["table"] + ".csv")
        if not os.path.exists(path):
            continue
        try:
            df, _ = _read(path)
        except Exception as exc:
            if log:
                log(f"    warehouse catalog: {c['table']} could not be read ({type(exc).__name__})")
            continue
        if not {"entity", "variable", "ts_utc", "value"} <= set(df.columns):
            continue
        unit = "unit" in df.columns
        g = df.groupby(["entity", "variable"] + (["unit"] if unit else []))
        for key, part in g:
            if len(part) < MIN_POINTS:
                continue
            ent, var = key[0], key[1]
            out.append({"id": f"erw:{c['table']}|{ent}|{var}", "source": "ERW", "table": c["table"], "entity": ent, "variable": var,
                        "unit": key[2] if unit else "", "freq": c["interval"], "title": f"{var.replace('_', ' ')}, {ent}",
                        "span": f"{part['ts_utc'].min()[:10]} to {part['ts_utc'].max()[:10]}", "n": int(len(part))})
    if log:
        log(f"    warehouse catalog: {len(out)} series in {len(keep)} tables of the coverage file")
    return out


def catalog(table_dir, log=None):
    return warehouse_catalog(table_dir, log) + [dict(e) for e in OUTSIDE]


def lines(cat):
    """The catalog as the classification call reads it: one line an entry."""
    out = []
    for e in cat:
        span = f"; {e['span']}" if e.get("span") else ""
        out.append(f"{e['id']} | {e['source']} | {e['title']} | {e['unit'] or 'unit not stated'} | {e['freq']}{span}")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# the pull of one series
# ---------------------------------------------------------------------------------------------

def _num(v):
    try:
        x = float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return x if x == x and abs(x) != float("inf") else None


def pull(entry, count, table_dir=None, log=None, raw_dir=None):
    """{id, source, title, unit, freq, url, retrieved, points: [[period, value]], cut, note}. Raises on a failure."""
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    src = entry["source"]
    if src == "ERW":
        df, head = _read(os.path.join(table_dir, entry["table"] + ".csv"))
        part = df[(df["entity"] == entry["entity"]) & (df["variable"] == entry["variable"])]
        if entry.get("unit") and "unit" in df.columns:
            part = part[part["unit"] == entry["unit"]]
        pts = sorted((r["ts_utc"][:10], _num(r["value"])) for _, r in part.iterrows())
        retrieved = (re.search(r"[Rr]etrieved[^0-9]*(\d{4}-\d{2}-\d{2})", head) or [None, ""])[1]
        url, note = f"erw:{entry['table']}", f"ERW table {entry['table']}"
    elif src == "EIA":
        key = os.environ.get("EIA_API_KEY") or _env_key("EIA_API_KEY")
        if not key:
            raise RuntimeError("EIA_API_KEY is not set")
        params = dict(entry["params"], **{"sort[0][column]": "period", "sort[0][direction]": "asc", "length": "5000"})
        url = entry["route"] + "?" + urllib.parse.urlencode(params)
        if not robots_ok(url, count, log):
            raise RuntimeError("robots.txt of api.eia.gov does not allow it")
        status, body = get(url + "&api_key=" + urllib.parse.quote(key), count, log, raw_dir)
        if status != 200:
            raise RuntimeError(f"EIA answered HTTP {status}: {body[:200]!r}")
        rows = json.loads(body)["response"]["data"]
        for r in rows:
            for k, v in entry["check"].items():
                if str(r.get(k)) != v:
                    raise RuntimeError(f"EIA's answer names {k}={r.get(k)!r}, not the {v!r} asked for")
        if entry.get("title_from") and rows and rows[0].get(entry["title_from"]):
            entry = dict(entry, title=rows[0][entry["title_from"]] + (f" ({entry['title']})" if entry["title_from"] == "fuelTypeDescription" else ""))
        units = {r.get(entry["field"] + "-units") or r.get("unit") for r in rows if r.get(entry["field"] + "-units") or r.get("unit")}
        if len(units) == 1:
            entry = dict(entry, unit=units.pop())
        pts = [(str(r["period"]), _num(r.get(entry["field"]))) for r in rows]
        retrieved, note = now, "EIA API v2"
    elif src == "BLS":
        url = f"https://api.bls.gov/publicAPI/v1/timeseries/data/{entry['series']}"
        if not robots_ok(url, count, log):
            raise RuntimeError("robots.txt of api.bls.gov does not allow it")
        status, body = get(url, count, log, raw_dir)
        j = json.loads(body) if status == 200 else {}
        if j.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(f"BLS answered HTTP {status}, {j.get('status')}: {' '.join(j.get('message') or [])[:200]}")
        s = j["Results"]["series"][0]
        if s.get("seriesID") != entry["series"]:
            raise RuntimeError(f"BLS's answer is series {s.get('seriesID')}, not {entry['series']}")
        pts = sorted((f"{d['year']}-{d['period'][1:]}", _num(d["value"])) for d in s["data"] if re.fullmatch(r"M(0[1-9]|1[0-2])", d["period"]))
        retrieved, note = now, "BLS public data API v1"
    elif src == "FRED":
        url = FRED_CSV + urllib.parse.quote(entry["series"])
        if not robots_ok(url, count, log):
            raise RuntimeError("robots.txt of fred.stlouisfed.org does not allow it")
        status, body = get(url, count, log, raw_dir)
        if status != 200:
            raise RuntimeError(f"FRED answered HTTP {status}: {body[:200]!r}")
        pts = parse_fredgraph(body, entry["series"])
        retrieved, note = now, "FRED, Federal Reserve Bank of St. Louis (fredgraph.csv)"
    elif src == "Census":
        pts, url = [], ""
        for year in CBP_YEARS:
            u = f"https://api.census.gov/data/{year}/cbp?" + urllib.parse.urlencode({"get": "ESTAB,NAICS2017_LABEL", "for": "us:*", "NAICS2017": entry["naics"]})
            if not robots_ok(u, count, log):
                raise RuntimeError("robots.txt of api.census.gov does not allow it")
            status, body = get(u, count, log, raw_dir)
            if status != 200:
                if log:
                    log(f"    Census CBP {year}: HTTP {status}; the year is left out")
                continue
            t = json.loads(body)
            row = dict(zip(t[0], t[1]))
            pts.append((str(year), _num(row.get("ESTAB"))))
            entry = dict(entry, title=f"US establishments, NAICS {entry['naics']} ({row.get('NAICS2017_LABEL', '').strip()})")
            url = u
        retrieved, note = now, "Census County Business Patterns API"
    else:
        raise RuntimeError(f"no puller for {src}")
    pts = [[p, v] for p, v in pts if v is not None]
    if len(pts) < 3:
        raise RuntimeError(f"{len(pts)} values: too few to draw")
    keep = MAX_YEARS if entry.get("freq") in ("annual", "P1Y") else MAX_POINTS
    cut = len(pts) > keep
    pts = pts[-keep:]
    return {"id": entry["id"], "source": src, "title": entry["title"], "unit": entry.get("unit") or "", "freq": entry["freq"], "url": redact(url),
            "retrieved": retrieved, "points": pts, "cut": cut, "note": note}


def parse_fredgraph(body, sid):
    """The points of a fredgraph.csv answer: its header must be observation_date and the series asked for (an answer
    naming another series is refused); a "." is a missing value and is left out; every other value as published."""
    text = body.decode("utf-8", "replace").lstrip("\ufeff")
    lines_ = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines_ or lines_[0].split(",") != ["observation_date", sid]:
        raise RuntimeError(f"FRED's answer is headed {lines_[0][:80] if lines_ else 'nothing'!r}, not observation_date,{sid}")
    pts = []
    for ln in lines_[1:]:
        parts = ln.split(",")
        if len(parts) != 2 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", parts[0]):
            raise RuntimeError(f"FRED's answer holds a line that is not a date and a value: {ln[:60]!r}")
        if parts[1] == ".":
            continue
        pts.append((parts[0], _num(parts[1])))
    return pts


def _env_key(name):
    try:
        from dotenv import dotenv_values
        return dotenv_values(os.path.join(ROOT, ".env")).get(name)
    except ImportError:
        return None


def describe(s):
    """The series' numbers as text, for the literal-number check of the sentence written about it: every value with
    its period, then the first and the latest value and the change between them, as the sentence may state them."""
    pts = s["points"]
    first, last = pts[0], pts[-1]
    plain = lambda v: str(int(v)) if float(v).is_integer() else f"{v:.6f}".rstrip("0").rstrip(".")      # noqa: E731  never in exponent form
    lines_ = [f"{p}: {plain(v)}" for p, v in pts]
    extra = []
    if first[1]:
        ch = (last[1] - first[1]) / abs(first[1]) * 100
        extra = [f"change from {first[0]} to {last[0]}: {ch:.0f}% ({ch:.1f}%)", f"ratio {last[1] / first[1]:.1f}"]
    return f"{s['title']} ({s['unit']}), {s['source']}: " + "; ".join(lines_ + extra) + f"; {len(pts)} values"
