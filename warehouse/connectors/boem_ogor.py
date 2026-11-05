#!/usr/bin/env python3
"""BOEM's offshore oil and gas production by lease, a month, from the Oil and Gas Operations Reports Part A (OGOR-A,
well production), the Gulf of America (session 611).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/boem_ogor_lease_production_monthly.csv,
from the Bureau of Ocean Energy Management's Data Center, one delimited file a year (1996 on; the current year's to the
latest month BOEM holds):

    https://www.data.boem.gov/Production/Files/ogora<year>delimit.zip   (the current year: .../ogoradelimit.zip)

    entity    boem_lease:<lease number> (BOEM's LEASE_NUMBER), or boem_unit:<unit agreement number> for the rows BOEM
              gives under a unit agreement with no lease number
    variable  oil_production (kbbl) and gas_production (MMcf): the sum over the lease's completions and producing
              intervals of BOEM's MON_O_PROD_VOL and MON_G_PROD_VOL ("the monthly quantity of oil [gas] produced from a
              completion", in barrels and thousand cubic feet), divided by 1,000
    ts_utc    the production month's first day at 00:00:00Z; freq P1M; geo US (federal offshore, no state); node the
              lease's operators that month, as BOEM names them, joined by "; "

OGOR-A, not OGOR-B: session 611 read BOEM's record layout and code pages. OGOR-B gives a lease's dispositions under 48
codes (sales, transfers to and from facilities, injection, flaring, venting, buy-back, meter differences); BOEM's pages
name the codes but do not say which of them make the lease's production, so a sum of them would be the ERW's reading.
OGOR-A gives each completion's production as BOEM defines it, and its sum for the Federal Gulf equals EIA's Federal
Offshore Gulf of America crude oil production (January 2024: 54,389 kbbl in both).

Each completion's month is BOEM's own row; a lease, completion, month, producing interval and API number given twice
stops the run (a line repeated in every field is kept once, counted in the header); a completion's zero is kept (a reported month with no production); nothing is filled. Water and
injection volumes are not taken.

    python warehouse/connectors/boem_ogor.py [--from 2015] [--to 2026] [--offline | --fresh]

Ceiling: 21 requests a run, one a file not yet saved (3 seconds apart; a file an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (BOEM's copyright page, record 86 of license_reads.csv: works of
the U.S. government; cite "Bureau of Ocean Energy Management, OGOR-A Well Production").
"""

import argparse
import csv
import datetime as dt
import email.utils
import io
import os
import sys
import traceback
import zipfile
from urllib.parse import urlparse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "boem_ogor_lease_production_monthly"
CONNECTOR = "boem_ogor"
SOURCE = "boem:ogor_a"
PAGE = "https://www.data.boem.gov/Main/OGOR-A.aspx"
LAYOUT = "https://www.data.boem.gov/Main/HtmlPage.aspx?page=ogorA"
FILE = "https://www.data.boem.gov/Production/Files/ogora{year}delimit.zip"
# the current year's file has no year in its name (session 611: ogora2026delimit.zip answered an HTML page, HTTP 200)
CURRENT = "https://www.data.boem.gov/Production/Files/ogoradelimit.zip"
CEILING, PAUSE = 21, 3   # session 619: requests a run (a saved file is reused, no request)
FIRST = 2015
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
LICENSE = "public"
# BOEM's record layout (LAYOUT), in the delimited file's order
FIELDS = ["lease", "completion", "month", "days_on_prod", "product_code", "oil_bbl", "gas_mcf", "water_bbl", "api",
          "well_status", "area_block", "operator_num", "operator", "field", "injection", "interval", "first_prod",
          "unit_agt", "unit_aloc_suffix"]


def records(text, year):
    """BOEM's delimited file as a frame of its own fields; a wrong field count or a key given twice stops the run."""
    rows = list(csv.reader(io.StringIO(text)))
    bad = [i for i, r in enumerate(rows) if len(r) != len(FIELDS)]
    if bad:
        raise RuntimeError(f"{year}: {len(bad)} lines without {len(FIELDS)} fields (the first, line {bad[0] + 1})")
    d = pd.DataFrame(rows, columns=FIELDS).apply(lambda c: c.str.strip())
    if not d["month"].str.fullmatch(r"\d{6}").all():
        raise RuntimeError(f"{year}: a production month not read as YYYYMM")
    if (d["month"].str[:4] != str(year)).any():
        raise RuntimeError(f"{year}: a month of another year in the year's file")
    for c in ("oil_bbl", "gas_mcf"):
        if not d[c].str.fullmatch(r"-?\d+").all():
            raise RuntimeError(f"{year}: a {c} not read as a whole number")
    if ((d["lease"] == "") & (d["unit_agt"] == "")).any():
        raise RuntimeError(f"{year}: a row with neither a lease nor a unit agreement number")
    # session 619: a line repeated in every field is kept once and counted (2009 holds one, all zeros); a key given
    # twice with any field different still stops the run
    repeated = int(d.duplicated().sum())
    d = d.drop_duplicates().reset_index(drop=True)
    key = ["lease", "unit_agt", "completion", "month", "interval", "api"]
    if d.duplicated(key).any():
        raise RuntimeError(f"{year}: a completion's interval and month given twice: {d[d.duplicated(key)].iloc[0][key].to_dict()}")
    d.attrs["repeated"] = repeated
    return d


def rows(d, url, retrieved, vintage):
    """One year's completions summed by lease (or unit agreement) and month, as the ERW's series rows."""
    d = d.copy()
    d["entity"] = d["lease"].map(lambda x: f"boem_lease:{x}")
    nolease = d["lease"] == ""
    d.loc[nolease, "entity"] = "boem_unit:" + d.loc[nolease, "unit_agt"]
    d["oil"] = d["oil_bbl"].astype(int)
    d["gas"] = d["gas_mcf"].astype(int)
    g = d.groupby(["entity", "month"]).agg(oil=("oil", "sum"), gas=("gas", "sum"),
                                            node=("operator", lambda s: "; ".join(sorted(set(x for x in s if x)))))
    g = g.reset_index()
    ts = pd.to_datetime(g["month"], format="%Y%m").dt.strftime("%Y-%m-%dT00:00:00Z")
    out = []
    for var, col, unit in (("oil_production", "oil", "kbbl"), ("gas_production", "gas", "MMcf")):
        out.append(pd.DataFrame({
            "entity": g["entity"], "variable": var, "ts_utc": ts, "value": g[col] / 1000.0, "unit": unit, "freq": "P1M",
            "geo": "US", "market": "", "node": g["node"], "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
            "vintage": vintage}))
    return pd.concat(out, ignore_index=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="BOEM OGOR-A production by lease, a month")
    ap.add_argument("--from", dest="first", type=int, default=FIRST)
    ap.add_argument("--to", dest="last", type=int, default=dt.datetime.now(dt.timezone.utc).year)
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--offline", action="store_true", help="ask nothing: every file from warehouse/raw")
    g.add_argument("--fresh", action="store_true", help="fetch every file again")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(urlparse(PAGE).hostname):
            raise RuntimeError(f"{urlparse(PAGE).hostname} is paused (warehouse/metadata/paused_sources.csv)")
        years = list(range(args.first, args.last + 1))
        this_year = dt.datetime.now(dt.timezone.utc).year  # its file is CURRENT; a month of another year in it stops
        ip.RAW.open(CONNECTOR, run_id)
        parts, asked, repeated = [], 0, 0
        for year in years:
            url = CURRENT if year == this_year else FILE.format(year=year)
            # session 619: the ceiling counts requests, not files (a saved file is no request)
            if not args.offline and (args.fresh or not ip.raw_cached(CONNECTOR, url)) and asked >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached, at {year}")
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=args.fresh, pause=PAUSE, headers=UA)
            asked += 0 if rec.get("cached") else 1
            if content[:2] != b"PK":
                raise RuntimeError(f"{year}: {url} answered something not a zip file ({content[:60]!r})")
            z = zipfile.ZipFile(io.BytesIO(content))
            names = [n for n in z.namelist() if n.lower().endswith(".txt")]
            if len(names) != 1:
                raise RuntimeError(f"{year}: the zip holds {z.namelist()}, not one text file")
            d = records(z.read(names[0]).decode("latin-1"), year)
            repeated += d.attrs.get("repeated", 0)
            lm = rec.get("last_modified") or ""
            vintage = email.utils.parsedate_to_datetime(lm).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if lm else ""
            s = rows(d, url, rec["retrieved_at"], vintage)
            parts.append(s)
            log(f"  {year}: {len(d):,} completion rows, {s['entity'].nunique()} leases, {len(s):,} rows")
        s = pd.concat(parts, ignore_index=True).sort_values(["entity", "variable", "ts_utc"], kind="stable").reset_index(drop=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a lease's month given twice across the years' files")
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): BOEM, offshore oil and gas production by lease, a month, the Gulf of America, from OGOR-A well production (session 611)",
            "Shape: series (docs/datastandard.md v0). entity boem_lease:<lease number> (boem_unit:<unit agreement> where BOEM gives no lease); variable oil_production (kbbl) or gas_production (MMcf); "
            "value the sum over the lease's completions and producing intervals of BOEM's monthly oil (barrels) and gas (thousand cubic feet) produced, divided by 1,000; ts_utc the month's first day; freq P1M; node the lease's operators that month.",
            f"A completion's zero is kept; nothing is filled; water and injection are not taken; {repeated} lines BOEM repeats in every field are kept once. Months {span}; {s['entity'].nunique():,} leases; {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/boem_ogor.py; {asked} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Bureau of Ocean Energy Management, Oil and Gas Operations Reports Part A (OGOR-A), well production, {PAGE}",
            f"  access: {FILE.format(year='<year>')}, years {years[0]} to {years[-1]} (the current year {CURRENT}); record layout {LAYOUT}",
            'License: public (a work of the U.S. government; cite "Bureau of Ocean Energy Management, OGOR-A Well Production").',
        ]
        ip.write_snapshot(s[ip.SERIES_COLS], NAME, header, log, ip.SERIES_COLS)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows, {span}"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique():,} leases, {span}; {asked} requests")
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Bureau of Ocean Energy Management (BOEM)",
                                    report="Oil and Gas Operations Reports Part A (OGOR-A), well production, by year",
                                    report_url=PAGE, document_list=PAGE, license=LICENSE, tables=[NAME])])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
