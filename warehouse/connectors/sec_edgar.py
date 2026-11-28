#!/usr/bin/env python3
"""SEC EDGAR: the exchange-listed energy companies (equity_universe) and their filed statements
(equity_fundamentals_quarterly).

Energy Research Warehouse (ERW), session 10000 (chain 701, part D), after the owner's ruling of 26 November 2026 that
gave the SEC a contact address. Read first (runs/c701/sec/requests.csv on lab-desktop): www.sec.gov's robots file allows
/files/ and /Archives/edgar/ (it disallows /cgi-bin, which this never asks); data.sec.gov has no robots file (HTTP 404).
The SEC's "Accessing EDGAR Data" page: "Current max request rate: 10 requests/second", a user agent naming a company and
a contact ("Sample Company Name AdminContact@<sample company domain>.com"), "Download only what you need". This connector
waits a quarter of a second between two requests (four a second at most) and sends the contact string from the
environment (SEC_USER_AGENT, kept in .env, never in the repository); without it, it refuses before any request. The
SEC's privacy and security policy: "Information presented on sec.gov is considered public information and may be
copied or further distributed by users of the web site without the SEC's permission. Please consider appropriate
citation to the SEC as the source." License: public, the SEC cited on every row.

    python warehouse/connectors/sec_edgar.py universe                    # equity_universe, under the data lock
    python warehouse/connectors/sec_edgar.py fundamentals                # equity_fundamentals_quarterly, under the lock
    python warehouse/connectors/sec_edgar.py universe --out-dir DIR      # a trial: the table under DIR
    python warehouse/connectors/sec_edgar.py fundamentals --limit 5      # a trial of the first five companies

The universe (method: docs/methods/equities.md, "The universe"): every company in the SEC's list of tickers
(www.sec.gov/files/company_tickers_exchange.json) listed on an exchange (NYSE, Nasdaq, Cboe, TXSE; over-the-counter
names are not listed) whose SEC industry code (SIC) is one of SIC_SEGMENTS; its segments are that code's. The SIC of each
listed company comes from its submissions file (data.sec.gov/submissions/CIK##########.json): read once from the SEC's
nightly bulk file of all of them (Archives/edgar/daily-index/bulkdata/submissions.zip, 1.6 GB, when it is in
warehouse/raw/sec_edgar/), and kept in warehouse/raw/sec_edgar/sic_cache.csv; afterwards only a listed company not in
the cache is asked for, one request each. A company is matched to company_directory by exact legal name only (the
directory holds no SEC number), case and spaces aside.

The statements: each universe company's XBRL facts (data.sec.gov/api/xbrl/companyfacts/CIK##########.json), as filed,
every filing kept (vintage the filing date). Five lines: revenue, net income, capital spending (durations: 3, 6, 9 or 12
months as the filing reports them, in the variable's name), long-term debt and shares outstanding (instants at the
period's end). For each line, each period and each filing, the first concept of CONCEPTS that the filing holds is read,
and named in x_concept. Only us-gaap facts of forms 10-Q and 10-K (and their amendments) are read; a foreign filer's
20-F or 40-F (often IFRS) is not, and its rows are absent (the page says so). After the first pull, a company's facts are
asked again only when EDGAR's daily form index shows it filed a 10-Q, 10-K or an amendment since the last run, or when
its cached copy is missing.
"""
import argparse
import csv
import datetime as dt
import gzip
import io
import json
import os
import re
import sys
import time
import traceback
import zipfile
from collections import defaultdict

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "sec_edgar"
SOURCE = "sec:edgar"
PUBLISHER = "U.S. Securities and Exchange Commission (SEC), EDGAR"
TICKERS_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
INDEX_URL = "https://www.sec.gov/Archives/edgar/daily-index/{y}/QTR{q}/form.{d}.idx"
FILING_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{accn}-index.htm"
PAGE = "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"
WAIT = 0.25  # seconds between two requests: four a second, under the SEC's ten
LISTED = {"NYSE", "Nasdaq", "CBOE", "TXSE"}
FORMS = {"10-Q", "10-K", "10-Q/A", "10-K/A"}
UNIVERSE = "equity_universe"
FUNDAMENTALS = "equity_fundamentals_quarterly"
CEILING = 3_000_000  # rows of the statements table; past it nothing is written

# The written rule (docs/methods/equities.md, "The universe"): an SEC industry code and its segments. A code that names
# two segments puts its companies in both, and segments_note says why. No company is placed by judgment.
SIC_SEGMENTS = {
    "1311": ["exploration_production"],                       # crude petroleum and natural gas
    "1381": ["oilfield_services"], "1382": ["oilfield_services"], "1389": ["oilfield_services"],
    "3533": ["oilfield_services"],                            # oil and gas field machinery and equipment
    "2911": ["integrated_oil_gas", "refining"],               # petroleum refining: the code does not separate the two
    "4610": ["midstream_pipelines"], "4922": ["midstream_pipelines"],
    "4923": ["midstream_pipelines", "regulated_utilities"],   # gas transmission and distribution
    "4924": ["midstream_pipelines", "regulated_utilities"],  # natural gas distribution: local distributors and LNG exporters
    "1220": ["coal"], "1221": ["coal"], "1222": ["coal"],
    "4911": ["regulated_utilities", "independent_power"],     # electric services: the code does not separate the two
    "4931": ["regulated_utilities"], "4932": ["regulated_utilities"], "4939": ["regulated_utilities"],
    "4991": ["independent_power"],                            # cogeneration and small power producers
    "3612": ["grid_equipment"], "3613": ["grid_equipment"],   # transformers; switchgear
}
TWO_NOTE = {
    "2911": "SIC 2911 (petroleum refining) does not separate integrated companies from refiners: in both",
    "4911": "SIC 4911 (electric services) does not separate regulated utilities from independent producers: in both",
    "4923": "SIC 4923 (gas transmission and distribution) is pipelines and local distribution together: in both",
    "4924": ("SIC 4924 (natural gas distribution) holds local gas distributors and the LNG exporters alike; the code does not "
             "separate them: in both"),
}
# segments no SEC industry code holds alone, so the written rule places no company in them (docs/methods/equities.md)
NO_CODE = {
    "lng": "no SIC code is LNG alone: the exporters file under 4924 with the local gas distributors",
    "nuclear_uranium": "no SIC code is nuclear or uranium alone: uranium miners file under 1090 or 1400 with other ores, "
                       "reactor owners under 4911",
    "solar": "no SIC code is solar alone: makers of cells and inverters file under 3674 with all semiconductors",
    "wind": "no SIC code is wind alone: turbine makers file under 3510, 3511 or 3600 with all engines and electrical equipment",
    "storage": "no SIC code is storage alone: 3690 holds batteries with consumer batteries and unrelated equipment",
    "hydrogen_fuel_cells": "no SIC code is hydrogen or fuel cells alone: 2810 holds the industrial gases with pigments, "
                           "3620 fuel cells with all electrical apparatus",
}
CONCEPTS = {  # the line, its unit, duration (True) or instant, and the us-gaap concepts in the order they are read
    # a utility's total operating revenue (RegulatedAndUnregulatedOperatingRevenue) before revenue from contracts with
    # customers, which for a utility is a part of it (the cross-check of 27 November: NextEra 6,100 and Duke 8,995 were
    # that part, not the income statement's total)
    "revenue_usd": ("USD", True, ["Revenues", "RegulatedAndUnregulatedOperatingRevenue",
                                  "RevenueFromContractWithCustomerExcludingAssessedTax",
                                  "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet",
                                  "ElectricUtilityRevenue", "SalesRevenueGoodsNet"]),
    "net_income_usd": ("USD", True, ["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"]),
    "capex_usd": ("USD", True, ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
                                "PaymentsToAcquireOilAndGasPropertyAndEquipment", "PaymentsToAcquireOilAndGasProperty"]),
    "long_term_debt_usd": ("USD", False, ["LongTermDebt", "LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations",
                                          "LongTermDebtAndFinanceLeaseObligations"]),
    "shares_outstanding": ("shares", False, ["CommonStockSharesOutstanding"]),  # XBRL unit shares; written as count
    # session 10000 (chain 701, part F, a reader's case): 72 of 243 companies file no balance-sheet count (Southern among
    # them) but every 10-Q and 10-K gives one on its cover, at the cover's own date (after the period's end): a line of its own
    "shares_outstanding_cover": ("shares", False, ["dei:EntityCommonStockSharesOutstanding"]),
}
UNIVERSE_COLS = ["entity_id", "entity_type", "name", "geo", "source", "source_url", "retrieved_at", "vintage", "cik",
                 "ticker", "tickers", "exchange", "sic", "sic_label", "segments", "segments_note", "directory_id",
                 "state_of_incorporation", "fiscal_year_end", "filer_category"]
FUND_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "source_url", "retrieved_at", "vintage",
             "x_period_start", "x_months", "x_fy", "x_fp", "x_form", "x_accession", "x_concept", "x_ticker"]
RAW = os.path.join(ip.RAW_DIR, "sec_edgar")


def agent():
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if not ua:
        env = os.path.join(ip.ROOT, ".env")
        if os.path.exists(env):
            for ln in open(env, encoding="utf-8"):
                if ln.startswith("SEC_USER_AGENT="):
                    ua = ln.split("=", 1)[1].strip()
    if not ua or "@" not in ua:
        raise RuntimeError("no SEC_USER_AGENT (a name and a contact address, the SEC's form) in the environment or .env; "
                           "nothing was requested")
    return ua


class Client:
    """Every request of a run: the contact string, a quarter of a second apart, the host's pause checked first."""

    def __init__(self, log):
        self.ua, self.log, self.last, self.n = agent(), log, 0.0, 0

    def get(self, url):
        host = url.split("/")[2]
        if ip.paused_host(host):
            raise RuntimeError(f"{host} is paused (warehouse/metadata/paused_sources.csv); not asked")
        wait = WAIT - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(4):
            r = requests.get(url, headers={"User-Agent": self.ua, "Accept-Encoding": "gzip, deflate"}, timeout=120)
            self.last = time.time()
            self.n += 1
            if r.status_code in (429, 503):  # the SEC limits a fast reader for ten minutes: wait, never press
                self.log(f"  HTTP {r.status_code} for {url}; waiting 60 s ({attempt + 1} of 4)")
                time.sleep(60)
                continue
            return r
        return r


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cik10(c):
    return str(int(c)).zfill(10)


def listed(tickers):
    """{cik10: (name, [tickers], exchange)} of the exchange-listed rows of the SEC's tickers file, in its order."""
    f = tickers["fields"]
    out = {}
    for row in tickers["data"]:
        r = dict(zip(f, row))
        if r.get("exchange") not in LISTED:
            continue
        k = cik10(r["cik"])
        if k in out:
            out[k][1].append(r["ticker"])
        else:
            out[k] = (r["name"], [r["ticker"]], r["exchange"])
    return out


# Five-tools data request 69 (session 11200): where a company's submissions file gives its SIC code a description that
# the SEC's own SIC code list does not (the four coal miners filed under 1220 carry "Silver Ores"), the list's name is
# used. Read on www.sec.gov/search-filings/standard-industrial-classification-sic-code-list on 28 November 2026.
SIC_LIST_NAME = {"1220": "Bituminous Coal & Lignite Mining"}


def sic_label(sic, label):
    return SIC_LIST_NAME.get(str(sic), label)


def sub_fields(d):
    a = (d.get("addresses") or {}).get("business") or {}
    st = (a.get("stateOrCountry") or "").strip()
    return {"sic": str(d.get("sic") or "").strip(), "sic_label": (d.get("sicDescription") or "").strip(),
            "name": (d.get("name") or "").strip(), "state_of_incorporation": (d.get("stateOfIncorporation") or "").strip(),
            "fiscal_year_end": (d.get("fiscalYearEnd") or "").strip(), "filer_category": (d.get("category") or "").strip(),
            "business_state": st if len(st) == 2 and st.isalpha() else ""}


CACHE_COLS = ["cik", "sic", "sic_label", "name", "state_of_incorporation", "fiscal_year_end", "filer_category",
              "business_state", "read_from", "read_at"]


def read_cache():
    p = os.path.join(RAW, "sic_cache.csv")
    if not os.path.exists(p):
        return {}
    return {r["cik"]: r for r in csv.DictReader(open(p, encoding="utf-8", newline=""))}


def write_cache(cache):
    os.makedirs(RAW, exist_ok=True)
    p = os.path.join(RAW, "sic_cache.csv")
    with open(p + ".tmp", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CACHE_COLS)
        w.writeheader()
        for k in sorted(cache):
            w.writerow({c: cache[k].get(c, "") for c in CACHE_COLS})
    os.replace(p + ".tmp", p)


def fill_from_bulk(cache, ciks, log):
    """The listed companies not in the cache, from the newest bulk file in the raw folder (no request)."""
    zips = sorted(f for f in os.listdir(RAW) if f.startswith("submissions_") and f.endswith(".zip")) if os.path.isdir(RAW) else []
    if not zips:
        return 0
    z = zipfile.ZipFile(os.path.join(RAW, zips[-1]))
    names = set(z.namelist())
    n = 0
    for k in ciks:
        if k in cache or f"CIK{k}.json" not in names:
            continue
        cache[k] = {"cik": k, **sub_fields(json.loads(z.read(f"CIK{k}.json"))), "read_from": zips[-1], "read_at": now_iso()}
        n += 1
    log(f"  {n} companies read from {zips[-1]}")
    return n


def segments_of(sic):
    segs = SIC_SEGMENTS.get(sic, [])
    return segs, (TWO_NOTE.get(sic) if len(segs) > 1 else None)


def norm_name(s):
    """A legal name for the exact match: case, commas, periods and runs of spaces aside, nothing else."""
    return " ".join(str(s).upper().replace(",", " ").replace(".", " ").split())


ABBREVIATIONS = {"COMPANY": "CO", "CORPORATION": "CORP", "INCORPORATED": "INC", "LIMITED": "LTD"}


def same_entity(a, b):
    """Two names the SEC gives one entity in two companyfacts files: equal but for case, commas, periods and the
    standard legal abbreviations (Company and Co, Corporation and Corp, Incorporated and Inc, Limited and Ltd)."""
    def n(s):
        return " ".join(ABBREVIATIONS.get(w, w) for w in norm_name(s).split())
    return bool(a) and n(a) == n(b)


def directory_ids():
    p = os.path.join(ip.OUT_DIR, "company_directory.csv")
    if not os.path.exists(p):
        return {}
    d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, usecols=["entity_id", "name"])
    out = {}
    for e, n in zip(d["entity_id"], d["name"]):
        out.setdefault(norm_name(n), []).append(e)
    return {k: v[0] for k, v in out.items() if len(v) == 1}  # a name held twice in the directory matches neither


def build_universe(lst, cache, retrieved, vintage):
    dirs = directory_ids()
    rows = []
    for k, (tname, tks, exch) in lst.items():
        c = cache.get(k)
        if not c:
            continue
        segs, note = segments_of(c["sic"])
        if not segs:
            continue
        name = c["name"] or tname
        rows.append({"entity_id": f"sec:{k}", "entity_type": "company", "name": name,
                     "geo": f"US-{c['business_state']}" if c.get("business_state") else "", "source": SOURCE,
                     "source_url": SUBMISSIONS_URL.format(cik=k), "retrieved_at": retrieved, "vintage": vintage, "cik": k,
                     "ticker": tks[0], "tickers": ";".join(tks), "exchange": exch, "sic": c["sic"],
                     "sic_label": sic_label(c["sic"], c["sic_label"]),
                     "segments": ";".join(segs), "segments_note": note or "", "directory_id": dirs.get(norm_name(name), ""),
                     "state_of_incorporation": c.get("state_of_incorporation", ""), "fiscal_year_end": c.get("fiscal_year_end", ""),
                     "filer_category": c.get("filer_category", "")})
    return pd.DataFrame(rows, columns=UNIVERSE_COLS).sort_values("entity_id").reset_index(drop=True)


def months_between(start, end):
    d = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
    m = round(d / 30.44)
    return m if m in (3, 6, 9, 12) and abs(d - m * 30.44) <= 12 else None


def fundamentals_rows(cik, ticker, facts, retrieved, only_accns=None):
    """The table's rows of one company's companyfacts: per line, period and filing, the first concept held."""
    picked = {}
    for var, (unit, duration, concepts) in CONCEPTS.items():
        for concept in concepts:
            ns, name = concept.split(":", 1) if ":" in concept else ("us-gaap", concept)
            g = (facts.get("facts") or {}).get(ns) or {}
            for f in ((g.get(name) or {}).get("units") or {}).get(unit, []):
                if f.get("form") not in FORMS or f.get("val") is None or not f.get("end") or not f.get("filed"):
                    continue
                if only_accns is not None and f.get("accn") not in only_accns:   # a co-registrant's file: this company's filings only
                    continue
                if f["end"] > f["filed"]:  # a period that ends after its filing cannot be as filed: a tagging error, left out
                    continue
                if duration:
                    if not f.get("start"):
                        continue
                    m = months_between(f["start"], f["end"])
                    if m is None:
                        continue
                    v = f"{var.replace('_usd', '')}_{m}m_usd" if var.endswith("_usd") else f"{var}_{m}m"
                else:
                    if f.get("start"):
                        continue
                    m, v = None, var
                key = (v, f["end"], f["accn"])
                if key in picked:
                    continue
                picked[key] = (v, f, concept, m, unit)
    rows = []
    for (v, end, accn), (_, f, concept, m, unit) in picked.items():
        acc = accn.replace("-", "")
        val = f["val"]
        val = str(int(val)) if float(val).is_integer() else repr(float(val))
        rows.append({"entity": f"sec:{cik}", "variable": v, "ts_utc": f"{end}T00:00:00Z", "value": val,
                     "unit": "count" if unit == "shares" else unit,
                     "freq": f"P{m}M" if m else "", "source": SOURCE,
                     "source_url": FILING_URL.format(cik=int(cik), acc=acc, accn=accn), "retrieved_at": retrieved,
                     "vintage": f"{f['filed']}T00:00:00Z", "x_period_start": f.get("start", ""), "x_months": m or "",
                     "x_fy": f.get("fy") or "", "x_fp": f.get("fp") or "", "x_form": f["form"], "x_accession": accn,
                     "x_concept": concept if ":" in concept else f"us-gaap:{concept}", "x_ticker": ticker})
    df = pd.DataFrame(rows, columns=FUND_COLS)
    # two filings of one day for one period (a filing and its amendment): the later accession is kept
    return df.sort_values(["entity", "variable", "ts_utc", "vintage", "x_accession"]).drop_duplicates(
        ["entity", "variable", "ts_utc", "vintage"], keep="last")


def filers_since(client, since, today, log):
    """(CIKs that filed a 10-Q, 10-K or an amendment on EDGAR's daily form indexes after `since` up to `today`, the last
    day read). A day's index is published in its evening, and a holiday has none: the last day read is the last day whose
    index answered, so a day not yet published is asked again by the next run, and a holiday before an answered day is
    passed."""
    out, day, last_read = set(), since + dt.timedelta(days=1), since
    by_accn = defaultdict(set)   # a joint filing is listed once under each of its filers
    while day <= today:
        if day.weekday() < 5:
            url = INDEX_URL.format(y=day.year, q=(day.month - 1) // 3 + 1, d=day.strftime("%Y%m%d"))
            r = client.get(url)
            if r.status_code == 200:
                last_read = day
                for ln in r.text.splitlines():
                    form = ln[:12].strip()
                    m = re.search(r"edgar/data/(\d+)/([\d-]+)\.txt", ln)   # the file name holds the CIK and the accession
                    if form in FORMS and m:
                        out.add(cik10(m.group(1)))
                        by_accn[m.group(2)].add(cik10(m.group(1)))
            elif r.status_code != 404 and r.status_code != 403:
                raise RuntimeError(f"EDGAR's form index for {day}: HTTP {r.status_code}")
        day += dt.timedelta(days=1)
    log(f"  daily form indexes after {since}: {len(out)} filers of a 10-Q or 10-K; read through {last_read}")
    return out, last_read, by_accn


def header_universe(t, run_id, tickers_rec):
    return [
        "Energy Research Warehouse (ERW): the exchange-listed US energy companies, by the SEC's industry code (session 10000, "
        "chain 701, part D)",
        "Shape: entities (docs/datastandard.md v0). entity_id sec:<the SEC's ten-digit CIK>; one row a company; segments by "
        "the written rule of docs/methods/equities.md (a code that names two segments puts its companies in both, "
        "segments_note says why); directory_id the company_directory row of the same exact legal name, else blank.",
        f"Companies: {len(t)} of the SEC's list of tickers, listed on NYSE, Nasdaq, Cboe or TXSE, with an energy SIC.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/sec_edgar.py; the tickers file {tickers_rec}",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        "Raw files: warehouse/raw/sec_edgar/ (not in git)",
        f"Source: {SOURCE} {PUBLISHER}: company_tickers_exchange.json and each company's submissions file, {PAGE}",
        "License: public (the SEC's privacy and security policy: information on sec.gov is public information and may be "
        "copied or further distributed without the SEC's permission; cite the SEC as the source).",
        "Method: docs/methods/equities.md",
    ]


def header_fundamentals(t, run_id, n_co):
    return [
        "Energy Research Warehouse (ERW): the universe's filed statements from SEC EDGAR's XBRL facts: revenue, net income, "
        "capital spending, long-term debt and shares outstanding, as filed (session 10000, chain 701, part D)",
        "Shape: series (docs/datastandard.md v0). entity sec:<CIK>; ts_utc the period's end; durations named by their "
        "months (revenue_3m_usd, net_income_12m_usd, capex_9m_usd: a 10-Q's cash flow is year to date), instants at the "
        "period's end (long_term_debt_usd, shares_outstanding in unit count: shares); shares_outstanding_cover the count on "
        "the filing's cover (dei:EntityCommonStockSharesOutstanding), ts_utc the cover's own date; x_concept the concept read; source_url the filing.",
        "Revisions: kept, one row per vintage. Key: entity, variable, ts_utc, vintage. vintage is the filing date: every "
        "filing that reported a period is a row (a later 10-K repeats a year's quarters); a fact whose period ends after its "
        "filing date is left out (a tagging error).",
        f"Companies: {n_co}; periods {t['ts_utc'].min()[:10] if len(t) else ''} to {t['ts_utc'].max()[:10] if len(t) else ''}; "
        f"{len(t)} rows. Forms 10-Q and 10-K and their amendments, us-gaap only (a 20-F or 40-F is not read).",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/sec_edgar.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        "Raw files: warehouse/raw/sec_edgar/facts/ (not in git)",
        f"Source: {SOURCE} {PUBLISHER}: data.sec.gov/api/xbrl/companyfacts, {PAGE}",
        "License: public (the SEC's privacy and security policy: information on sec.gov is public information and may be "
        "copied or further distributed without the SEC's permission; cite the SEC as the source).",
        "Method: docs/methods/equities.md",
    ]


def run_universe(client, log, run_id, retrieved):
    r = client.get(TICKERS_URL)
    if r.status_code != 200:
        raise RuntimeError(f"{TICKERS_URL}: HTTP {r.status_code}")
    os.makedirs(RAW, exist_ok=True)
    open(os.path.join(RAW, f"company_tickers_exchange_{run_id[:8]}.json"), "wb").write(r.content)
    lst = listed(r.json())
    cache = read_cache()
    fill_from_bulk(cache, list(lst), log)
    missing = [k for k in lst if k not in cache]
    for k in missing:  # a listed company new since the cache: its submissions file, one request
        s = client.get(SUBMISSIONS_URL.format(cik=k))
        if s.status_code == 200:
            cache[k] = {"cik": k, **sub_fields(s.json()), "read_from": SUBMISSIONS_URL.format(cik=k), "read_at": now_iso()}
        else:
            log(f"  {k}: submissions HTTP {s.status_code}; left out this run")
    write_cache(cache)
    t = build_universe(lst, cache, retrieved, run_id[:8])
    log(f"  listed companies {len(lst)}; asked one by one {len(missing)}; in the universe {len(t)}")
    rec = f"{TICKERS_URL} ({len(r.content):,} bytes)"
    ip.write_snapshot(t, UNIVERSE, header_universe(t, run_id, rec), log, cols=UNIVERSE_COLS)
    return t


HEADER_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{accn}-index-headers.html"


def own_filings(cik, zf):
    """{accession: report date} of the company's 10-Q and 10-K filings marked XBRL, from its submissions in the SEC's
    bulk file (no request); empty when the bulk file or the company is not there."""
    if zf is None or f"CIK{cik}.json" not in zf.namelist():
        return {}
    r = json.loads(zf.read(f"CIK{cik}.json")).get("filings", {}).get("recent", {})
    out = {}
    for i, form in enumerate(r.get("form", [])):
        if form in FORMS and (r.get("isXBRL") or [0] * (i + 1))[i]:
            out[r["accessionNumber"][i]] = r.get("reportDate", [""] * (i + 1))[i]
    return out


def coregistrants(client, cik, accn, by_accn, log):
    """The other filers of a joint filing: from the day's form index when it listed the filing, else from the filing's
    EDGAR header (CENTRAL INDEX KEY lines; read once, kept in warehouse/raw/sec_edgar/headers/)."""
    if accn in by_accn:
        return sorted(by_accn[accn] - {cik})
    hdir = os.path.join(RAW, "headers")
    os.makedirs(hdir, exist_ok=True)
    hp = os.path.join(hdir, f"{accn}.txt")
    if not os.path.exists(hp):
        r = client.get(HEADER_URL.format(cik=int(cik), acc=accn.replace("-", ""), accn=accn))
        if r.status_code != 200:
            log(f"  {cik} {accn}: header HTTP {r.status_code}; its co-registrants not read")
            if r.status_code == 404:   # kept, so the next run does not ask again
                open(hp, "w", encoding="utf-8").write(f"HTTP 404 {now_iso()}")
            return []
        open(hp, "w", encoding="utf-8").write(r.text)
    keys = re.findall(r"CENTRAL INDEX KEY:\s*(\d+)", open(hp, encoding="utf-8").read())
    return sorted({cik10(k) for k in keys} - {cik})


def facts_of(client, cik, fdir, fresh, log):
    """A company's companyfacts from the raw folder, asked again when `fresh` or not held; None when it has none."""
    cp = os.path.join(fdir, f"CIK{cik}.json.gz")
    none = os.path.join(fdir, f"CIK{cik}.none")   # the SEC answered 404: asked again only when fresh
    if os.path.exists(none) and not fresh:
        return None
    if not os.path.exists(cp) or fresh:
        r = client.get(FACTS_URL.format(cik=cik))
        if r.status_code == 404:  # no XBRL facts (a filer of 20-F or 40-F only, or none yet)
            open(none, "w", encoding="utf-8").write(now_iso())
            return None
        if r.status_code != 200:
            raise RuntimeError(f"{cik} HTTP {r.status_code}")
        with gzip.open(cp + ".tmp", "wb") as f:
            f.write(r.content)
        os.replace(cp + ".tmp", cp)
    with gzip.open(cp, "rb") as f:
        return json.load(io.TextIOWrapper(f, encoding="utf-8"))


def accns_and_newest(facts):
    """The accessions a companyfacts file holds us-gaap facts of, and the newest period end among them."""
    acc, newest = set(), ""
    for c in ((facts or {}).get("facts") or {}).get("us-gaap", {}).values():
        for u in c.get("units", {}).values():
            for f in u:
                acc.add(f.get("accn"))
                newest = max(newest, f.get("end") or "")
    return acc, newest


def run_fundamentals(client, log, run_id, retrieved, limit=None):
    p = os.path.join(ip.OUT_DIR, UNIVERSE + ".csv")
    if not os.path.exists(p):
        raise RuntimeError(f"{UNIVERSE} is not on this machine: run the universe first")
    u = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
    if limit:
        u = u.head(limit)
    fdir = os.path.join(RAW, "facts")
    os.makedirs(fdir, exist_ok=True)
    state_p = os.path.join(fdir, "last_index_day.txt")
    today = dt.datetime.now(dt.timezone.utc).date()
    refresh, read_through, by_accn = set(), None, {}
    if os.path.exists(state_p):
        since = dt.date.fromisoformat(open(state_p, encoding="utf-8").read().strip())
        refresh, read_through, by_accn = filers_since(client, since, today, log)
    zips = sorted(f for f in os.listdir(RAW) if f.startswith("submissions_") and f.endswith(".zip")) if os.path.isdir(RAW) else []
    zf = zipfile.ZipFile(os.path.join(RAW, zips[-1])) if zips else None
    frames, asked, failed, joined = [], 0, [], []
    co_fresh = set()   # co-registrants' files asked again this run (once each)
    for cik, ticker in zip(u["cik"], u["ticker"]):
        try:
            n0 = client.n
            facts = facts_of(client, cik, fdir, cik in refresh, log)
            asked += client.n - n0
        except RuntimeError as e:
            failed.append(str(e))
            continue
        if facts is None:
            continue
        frames.append(fundamentals_rows(cik, ticker, facts, retrieved))
        # docs/methods/equities.md, "Joint filings" (done-line request 579): a 10-Q or 10-K of the company's own, for a
        # period after the newest its own facts hold, that its facts lack, is read from the co-registrant's file where the
        # SEC keeps it (NextEra's June and September 2026 10-Qs sit in Florida Power & Light's), that filing's facts only
        have, newest = accns_and_newest(facts)
        own = own_filings(cik, zf)
        own.update({a: "" for a, ciks in by_accn.items() if cik in ciks})
        missing = sorted(a for a, rep in own.items() if a not in have and (rep == "" or rep > newest))
        for accn in missing:
            for other in coregistrants(client, cik, accn, by_accn, log):
                try:
                    n0 = client.n
                    of = facts_of(client, other, fdir, other in refresh and other not in co_fresh, log)
                    co_fresh.add(other)
                    asked += client.n - n0
                except RuntimeError as e:
                    log(f"  {cik} {accn}: co-registrant {other}: {e}")
                    continue
                if of is None or accn not in accns_and_newest(of)[0]:
                    continue
                # the co-registrant's file must name this company as its entity (Florida Power & Light's file is named
                # NEXTERA ENERGY, INC.): a parent's file holds the parent's consolidated figures, never a subsidiary's
                if not same_entity(of.get("entityName", ""), facts.get("entityName", "")):
                    continue
                rows = fundamentals_rows(cik, ticker, of, retrieved, only_accns={accn})
                if len(rows):
                    frames.append(rows)
                    joined.append(f"{ticker} {accn} from {other}")
                    break
    if joined:
        log(f"  joint filings read from a co-registrant's file: {len(joined)} ({'; '.join(joined[:8])})")
    if failed:
        raise RuntimeError(f"{len(failed)} companies' facts could not be read ({'; '.join(failed[:5])}); nothing written")
    frames = [f for f in frames if len(f)]
    t = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=FUND_COLS)
    t = t.drop_duplicates(["entity", "variable", "ts_utc", "vintage"], keep="first")   # a company's own row before a joined one
    if len(t) > CEILING:
        raise RuntimeError(f"{len(t)} rows would pass the ceiling of {CEILING}; nothing written")
    log(f"  companies {len(u)}; facts asked {asked}; with facts {t['entity'].nunique()}; rows {len(t)}")
    if not limit:
        ip.write_snapshot(t, FUNDAMENTALS, header_fundamentals(t, run_id, t["entity"].nunique()), log, cols=FUND_COLS)
        open(state_p, "w", encoding="utf-8").write((read_through or today - dt.timedelta(days=1)).isoformat())
    else:
        print(f"a trial of {limit} companies: {len(t)} rows, not written")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="SEC EDGAR: the listed energy companies and their filed statements")
    ap.add_argument("what", choices=["universe", "fundamentals"])
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--limit", type=int, help="fundamentals: a trial of the first N companies, nothing written")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = now_iso()
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    table = UNIVERSE if args.what == "universe" else FUNDAMENTALS
    client = None
    try:
        client = Client(log)
        t = run_universe(client, log, run_id, retrieved) if args.what == "universe" else \
            run_fundamentals(client, log, run_id, retrieved, args.limit)
        results.append(dict(table=table, market="all", status="ok", detail=f"{len(t)} rows, {client.n} requests"))
        print(f"{table}: {len(t)} rows; {client.n} requests to the SEC")
        if not args.out_dir and not args.limit:
            ip.update_sources([dict(source=SOURCE, publisher=PUBLISHER,
                                    report="EDGAR: the list of tickers, each company's submissions and XBRL company facts",
                                    report_url=PAGE, document_list=TICKERS_URL, license="public", tables=[table])])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=table, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir and not args.limit:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
