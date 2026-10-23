#!/usr/bin/env python3
"""EIA's Wholesale Electricity and Natural Gas Market Data: the Intercontinental Exchange's (ICE) day-ahead on-peak
electricity indices at the hubs EIA republishes with ICE's permission, a delivery day (session 2014, chain 057: the
hubs outside the ISOs' own price tables, Mid-Columbia and Palo Verde, beside those the ISO tables also price; EIA's page
names eight hubs, and its 2026 file holds seven: ERCOT North has no row in it).

Energy Research Warehouse (ERW) connector. One series table from EIA's current-year workbook:

    https://www.eia.gov/electricity/wholesale/xls/ice_electric-<YEAR>.xlsx

    eia_ice_electricity_daily   entity ice:<product> (ICE's product name, slugged: ice:mid_c_peak, ice:palo_verde_peak, ...);
                                variables price_high, price_low, price_wavg (USD/MWh), volume (MWh), trades and
                                counterparties (count), and price_change (USD/MWh, the change in the weighted average from
                                the product's previous trade date, as the file gives it); ts_utc the delivery start date
                                (00:00 UTC of the calendar day); freq P1D; geo US-<state> of the hub where one state holds it,
                                empty otherwise; market ICE's region (EIA's table); node ICE's price hub as written;
                                x_trade_date and x_delivery_end the file's dates

Each sheet's header must hold the columns read below, in any order; a hub the map does not hold, a date that does not
read, a price that is not a number, a delivery end before its start, or an (entity, variable, ts_utc) given twice stops
the run. A trade covering more than one delivery day (a weekend or holiday package) is one row at its start date, with
its end in x_delivery_end; nothing is spread over the days. An empty cell has no row; nothing is filled.

    python warehouse/connectors/eia_ice_electricity.py [--offline] [--out-dir DIR] [--years 2026]

Ceiling: one request a year. EIA's robots file (read 23 October 2026, session 2014) disallows "/*archive/", which holds
every earlier year's final file (xls/archive/ice_electric-<YEAR>final.xlsx) and the history zip: only the current year's
file is asked, and the table holds that year. The file is fetched again on each run (EIA updates it every two weeks).
License: held internal. EIA's page: "The market data provided here are republished, with permission, from data
collected by the Intercontinental Exchange (ICE)"; EIA's public domain statement covers EIA's own work, and these are
ICE's data (session 2014's decision; Samuel's ruling).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "eia_ice_electricity"
SOURCE = "eia:ice_wholesale_electricity"
PAGE = "https://www.eia.gov/electricity/wholesale/"
BASE = "https://www.eia.gov/electricity/wholesale/xls/"
TABLE = "eia_ice_electricity_daily"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = [dt.datetime.now(dt.timezone.utc).year]
X_COLS = ["x_trade_date", "x_delivery_end"]

# the price hub as the file names it, lowered, with its spaces and dashes gone -> (region as EIA's table names it, geo)
HUBS = {
    "nepoolmhdalmppeak": ("New England", "US-MA"),
    "pjmwhrealtimepeak": ("PJM", ""),
    "indianahubrtpeak": ("Midwest", "US-IN"),
    "ercotnorth345kvpeak": ("Texas", "US-TX"),
    "midcpeak": ("Northwest", ""),
    "np15ezgendalmppeak": ("Northern California", "US-CA"),
    "palovrdepeak": ("Southwest", "US-AZ"),
    "paloverdepeak": ("Southwest", "US-AZ"),
    "sp15ezgendalmppeak": ("Southern California", "US-CA"),
    "sp15gendalmppeak": ("Southern California", "US-CA"),
}
# a column of the file, matched on its name lowered and stripped of everything but letters -> our name
COLS = {
    "pricehub": "hub",
    "tradedate": "trade_date",
    "deliverystartdate": "start",
    "deliveryenddate": "end",
    "highpricemwh": "price_high",
    "lowpricemwh": "price_low",
    "wtdavgpricemwh": "price_wavg",
    "change": "price_change",
    "dailyvolumemwh": "volume",
    "numberoftrades": "trades",
    "numberofcounterparties": "counterparties",
}
UNITS = {"price_high": "USD/MWh", "price_low": "USD/MWh", "price_wavg": "USD/MWh", "price_change": "USD/MWh",
         "volume": "MWh", "trades": "count", "counterparties": "count"}
NEED = ["hub", "trade_date", "start", "end", "price_high", "price_low", "price_wavg", "volume", "trades"]


def key(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def day(v, what):
    t = pd.to_datetime(v, errors="coerce")
    if pd.isna(t):
        raise RuntimeError(f"{what}: a date that does not read: {v!r}")
    return t.normalize()


def parse(content, base):
    """The rows of one workbook: every sheet whose header holds the columns needed."""
    sheets = pd.read_excel(io.BytesIO(content), sheet_name=None, header=None, keep_default_na=False)  # only an empty cell is empty: "n/a" stops the run
    out, read = [], []
    for name, raw in sheets.items():
        hdr = None
        for i in range(min(len(raw), 10)):
            names = {key(c): j for j, c in enumerate(raw.iloc[i].tolist())}
            if "pricehub" in names and "tradedate" in names:
                hdr = (i, names)
                break
        if hdr is None:
            continue
        i, names = hdr
        cols = {ours: names[k] for k, ours in COLS.items() if k in names}
        missing = [c for c in NEED if c not in cols]
        if missing:
            raise RuntimeError(f"sheet {name!r}: no column for {missing}; the header reads {raw.iloc[i].tolist()}")
        read.append(name)
        for r in raw.iloc[i + 1:].itertuples(index=False):
            r = list(r)
            hub = r[cols["hub"]]
            if pd.isna(hub) or str(hub).strip() == "":
                continue
            hub = str(hub).strip()
            if key(hub) not in HUBS:
                raise RuntimeError(f"sheet {name!r}: a hub not in the map: {hub!r}")
            region, geo = HUBS[key(hub)]
            trade, start, end = day(r[cols["trade_date"]], hub), day(r[cols["start"]], hub), day(r[cols["end"]], hub)
            if end < start:
                raise RuntimeError(f"{hub}: delivery end {end.date()} before its start {start.date()}")
            for var in UNITS:
                if var not in cols:
                    continue
                v = r[cols[var]]
                if pd.isna(v) or (isinstance(v, str) and v.strip() == ""):
                    continue
                try:
                    v = float(v)
                except (TypeError, ValueError):
                    raise RuntimeError(f"{hub} {start.date()} {var}: not a number: {v!r}")
                out.append(dict(base, entity=f"ice:{slug(hub)}", variable=var, ts_utc=start.strftime("%Y-%m-%dT00:00:00Z"), value=v,
                                unit=UNITS[var], freq="P1D", geo=geo, market=region, node=hub,
                                x_trade_date=trade.strftime("%Y-%m-%d"), x_delivery_end=end.strftime("%Y-%m-%d")))
    if not read:
        raise RuntimeError(f"no sheet has a 'Price hub' and 'Trade date' header: sheets {list(sheets)}")
    if not out:
        raise RuntimeError("no row")
    return out, read


def main(argv=None):
    ap = argparse.ArgumentParser(description="ICE's day-ahead on-peak electricity indices at the hubs EIA republishes")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--years", type=int, nargs="+", default=YEARS)
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        rows, urls, latest, sheets = [], [], "", []
        for y in sorted(args.years):
            url = f"{BASE}ice_electric-{y}.xlsx"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got, read = parse(content, base)
            rows += got
            sheets += read
            urls.append(url)
            latest = max(latest, base["retrieved_at"])
            log(f"  {url}: {len(got)} rows from sheets {read}")
        s = pd.DataFrame(rows)
        dup = s.duplicated(["entity", "variable", "ts_utc"], keep=False)
        if dup.any():
            raise RuntimeError(f"an (entity, variable, ts_utc) given twice: {s[dup][['entity', 'ts_utc', 'x_trade_date']].head(6).values.tolist()}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        multi = int((s.drop_duplicates(["entity", "ts_utc"]).pipe(lambda d: d.x_delivery_end > d.ts_utc.str[:10])).sum())
        head = [
            "Energy Research Warehouse (ERW): EIA, Wholesale Electricity and Natural Gas Market Data: the Intercontinental Exchange's (ICE) day-ahead "
            f"on-peak electricity indices at {s.entity.nunique()} hubs, a delivery day, republished by EIA with ICE's permission (session 2014)",
            "Shape: series (docs/datastandard.md v0). entity ice:<ICE product, slugged>; variables price_high, price_low, price_wavg, price_change "
            "(USD/MWh), volume (MWh), trades and counterparties (count); freq P1D; ts_utc the delivery start date; geo US-<state> where one state holds "
            "the hub, else empty; market ICE's region as EIA's page names it; node ICE's price hub; x_trade_date the trade date; x_delivery_end the "
            "delivery end date.",
            f"{s.entity.nunique()} hubs; delivery {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}; years {', '.join(str(y) for y in sorted(args.years))}. "
            f"A trade for more than one delivery day (a weekend or holiday package, {multi} hub-days) is one row at its start date. An empty cell has "
            "no row. Nothing is filled. Earlier years' files are under EIA's /archive/ paths, which its robots file disallows: not asked.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_ice_electricity.py; the latest file retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Wholesale Electricity and Natural Gas Market Data, {PAGE}",
            f"  access: {BASE}ice_electric-<YEAR>.xlsx ({len(urls)} file, sheets {', '.join(sheets)})",
            'License: internal. EIA: "The market data provided here are republished, with permission, from data collected by the Intercontinental '
            'Exchange (ICE)"; the data are ICE\'s, not EIA\'s own work, and are held from publication pending a ruling.',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} hubs, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA), republishing the Intercontinental Exchange (ICE)",
                                    report="Wholesale Electricity and Natural Gas Market Data: ICE day-ahead on-peak electricity indices", report_url=PAGE,
                                    document_list=PAGE, license="internal", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
