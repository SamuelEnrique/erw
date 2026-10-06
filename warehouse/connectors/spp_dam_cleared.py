#!/usr/bin/env python3
"""SPP: demand cleared in the day-ahead market, by hour (session 136, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/spp_dam_cleared_energy.csv, from SPP's
Marketplace portal, the public file browser's "Market Clearing" folder, the day-ahead file of each day:

    https://portal.spp.org/file-browser-api/download/market-clearing?path=/<YYYY>/<MM>/DA-MC-<YYYYMMDD>0100.csv
    Interval (Central, hour ending), GMTIntervalEnd, BAA, ..., Cleared Demand Bid, Cleared Fixed Demand Bid,
    Cleared Virtual Bid, ..., Total Demand, ...

    python warehouse/connectors/spp_dam_cleared.py [--days N] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row an hour for each balancing authority area the file names (spp:SPP, and from 1 April 2026
spp:SWPW, the western area): the column "Total Demand", the demand the day-ahead market cleared. MW over the hour.
A file from before 1 April 2026 names no area and its one row an hour is written as spp:SPP. An empty cell is not a
quantity and gives no row. The file's other columns are read and not written.

REQUESTS. One small file a day (24 or 48 rows). The ERW already downloads these same files for its reserve
quantities (spp_as_quantities.py): a day whose raw file that connector or this one kept is read from the machine and
asks SPP for nothing. Two seconds between requests. A day SPP has not posted (HTTP 404) is not written.

License: public, with citation. SPP's terms (https://www.spp.org/terms-conditions/, read 6 October 2026):
"Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part
(with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial
publication ... Any commercial use of these materials requires prior, express written authorization".
"""

import io
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dam_cleared as dc  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "spp_dam_cleared_energy"
CONNECTOR = "spp_dam_cleared"
SOURCE = "spp:DA-MC:cleared"
FILE = "https://portal.spp.org/file-browser-api/download/market-clearing?path=/{}"
PAGE = "https://portal.spp.org/pages/market-clearing"
COLUMN = "Total Demand"
OTHER = "spp_as_quantities"          # the connector that already keeps these files
PAUSE = 2


def parse(content):
    """One day's file as ({(area, hour start UTC): MW}, rows read)."""
    df = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    if "GMTIntervalEnd" not in df.columns or COLUMN not in df.columns:
        raise RuntimeError(f"columns {list(df.columns)[:12]}, expected GMTIntervalEnd and {COLUMN!r}")
    end = pd.to_datetime(df["GMTIntervalEnd"].str.strip(), format="%m/%d/%Y %H:%M:%S", utc=True)
    area = df["BAA"].str.strip() if "BAA" in df.columns else pd.Series(["SPP"] * len(df), index=df.index)
    v = pd.to_numeric(df[COLUMN].str.strip(), errors="coerce")
    out = {}
    for a, e, m in zip(area, end, v):
        if pd.notna(m) and a:
            out[(a, e - pd.Timedelta(hours=1))] = float(m)
    return out, len(df)


def pull(log, days, counter):
    today = pd.Timestamp.now(tz="America/Chicago").normalize().tz_localize(None)
    out = []
    for day in reversed(pd.date_range(today - pd.Timedelta(days=days), today + pd.Timedelta(days=1), freq="D")):
        url = FILE.format(f"{day:%Y}/{day:%m}/DA-MC-{day:%Y%m%d}0100.csv")
        url = requests.Request("GET", url).prepare().url          # as iso_prices.fetch_raw records it, so a kept file is found
        hit = ip.raw_cached(OTHER, url)
        try:
            content, rec = hit if hit else ip.fetch_raw(CONNECTOR, url, log, headers=dc.UA, pause=PAUSE)
        except ip.SourceGap:
            log(f"  {day:%Y-%m-%d}: SPP has not posted the file (HTTP 404); the day is not written")
            continue
        hours, n = parse(content)
        if not dc.reused(rec):
            counter.add(n, f"{day:%Y-%m-%d}")
        out += [dc.row(SPEC, f"spp:{a}", ts, v, COLUMN, url, rec["retrieved_at"]) for (a, ts), v in sorted(hours.items(), key=lambda kv: (kv[0][1], kv[0][0]))]
    log(f"  {len(out):,} hours of {len({r['entity'] for r in out})} areas; {counter.read:,} rows read from SPP in this run (the rest from raw files already on this machine)")
    return out


SPEC = dict(
    iso="spp", name=NAME, connector=CONNECTOR, source=SOURCE, unit="MW",
    geo="US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY", days=14, ceiling=5000, stale_days=5,
    what="SPP, demand cleared in the day-ahead market by hour and balancing authority area (Marketplace portal, Market Clearing, DA-MC files, Total Demand)",
    entry=dict(source=SOURCE, publisher="Southwest Power Pool (SPP)", report="Marketplace portal, Market Clearing, day-ahead files (DA-MC), cleared demand", report_url=PAGE,
               document_list=FILE.format("<YYYY>/<MM>/DA-MC-<YYYYMMDD>0100.csv"), license="public", tables=[NAME]),
    notes=["value: SPP's column Total Demand for the hour and the balancing authority area (MW over the hour). From 1 April 2026 the file names two areas, SPP and SWPW; before it, one row an hour, written as spp:SPP."],
    license="License: public, with citation. SPP's terms: \"Permission is implicitly granted to copy and distribute ... in whole or in part (with appropriate citation) EXCEPT when such materials "
            "will be used, in whole or in part, within a commercial publication\" (https://www.spp.org/terms-conditions/, read 6 October 2026).",
)


if __name__ == "__main__":
    sys.exit(dc.run(SPEC, pull))
