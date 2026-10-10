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
       Census  NOT REQUESTED: api.census.gov answered "Missing Key" to a request without one (9 October 2026) and the
               .env holds none. Recorded and left (LEFT); _cbp() stays for the day a key is held.
       FRED    NOT REQUESTED: its API needs a key and the .env holds none (the owner: "a source that needs a key the
               .env lacks is recorded and left"). FRED series already in the warehouse are in tier 1.
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
]
BY_ID = {e["id"]: e for e in OUTSIDE}
# The publishers named by the owner that a run does not request, and why (session 169). _bls() stays for the day BLS's
# robots.txt allows the API path.
LEFT = {"FRED": "its API needs a key and the root .env holds none; FRED series the warehouse already holds are drawn from the warehouse",
        "Census": "api.census.gov answered Missing Key to a request without one, and the root .env holds no Census key",
        "BLS": "api.bls.gov's robots.txt disallows every path to every agent, and www.bls.gov refused the request for its terms (HTTP 403)"}
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
