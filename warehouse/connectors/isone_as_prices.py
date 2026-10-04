#!/usr/bin/env python3
"""ISO-NE day-ahead ancillary service clearing prices, hourly, the system, from 2025-03-01. Internal.

Energy Research Warehouse (ERW) connector, session 85 (docs/methods/capacity_and_ancillary.md). Writes one series
table, warehouse/output/isone_as_prices.csv:

    entity    isone:7000    the report's one Location ID: day-ahead ancillary services clear for New England as a
                            whole
    variable  as_price_dam_tmsr    "Ten Minute Spinning Reserve Clearing Price"
              as_price_dam_tmr10   "Ten Minute Reserve Clearing Price" (total ten-minute reserve)
              as_price_dam_tmr30   "Total Thirty Reserve Clearing Price" (total thirty-minute reserve)
              as_price_dam_fer     "FER Price" (the forecast energy requirement)
    unit      USD/MW-hour   (the file's unit row reads "$"; the price is per MW for the hour)
    freq      PT1H; ts_utc is the start of the hour, UTC (the file's Local Date and Hour Ending, Eastern)
    market    isone_dam
    node      7000

    python warehouse/connectors/isone_as_prices.py                      # 2025-03-01 to today (Eastern)
    python warehouse/connectors/isone_as_prices.py --out-dir C:/scratch # a trial run: nothing in warehouse/output
    python warehouse/connectors/isone_as_prices.py --offline            # from the raw files only, no request

Source: ISO Express, "Day-Ahead Hourly Reserve Requirements Prices Designations and Forecast"
(https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/ancillary-daas-hourly-rr), the csv at
https://www.iso-ne.com/transform/csv/daasreservedata?start=<YYYYMMDD>&end=<YYYYMMDD>. One request per month. ISO-NE
answers the csv only to a session that has opened one of its report pages first (as gridstatus does), so the
connector opens one page and then asks. The month in progress is fetched again on every run.

The window starts 2025-03-01, not 2024-09-01: ISO-NE's day-ahead ancillary services market began on 1 March 2025,
and the report answers no row for an earlier day (2025-02-01 asked in session 85: a header and no data). Before it
New England bought forward reserves in a seasonal auction, which has no hourly day-ahead price.

Kept: the four prices. Left out: the requirements, the forecast and the designated MW in the same file (they are
quantities, not prices), and the strike prices (another report).

The repeated hour. The file names an hour by its ending, 01 to 24, in order; the day the clocks go back holds 02
twice, the day they go forward has no 03. A day is read only when its hours are exactly the ones that day has, in
order; any other day is left out and named.

Never fill. An empty cell is not a price and gives no row; a (product, day) short of an hour is left out.

Ceiling: 500,000 rows (session 85). Past it nothing is written.

License: internal. ISO-NE's terms (https://www.iso-ne.com/legal-privacy, read 2026-10-04): "You are also hereby put
on notice that the Content is protected by copyright under United States laws. Any duplication of the Content or
non-personal use may violate copyright, trademark, and other laws." The same reading as session 65's for ISO-NE's
capacity prices: the terms do not allow republishing, so the table is internal until a person rules otherwise.
"""

import csv
import io
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_as_common as common  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "isone_as_prices"
TZ = "America/New_York"
FIRST = "2025-03-01"
SOURCE = "isone:daasreservedata"
REPORT = "Day-Ahead Hourly Reserve Requirements Prices Designations and Forecast"
PAGE = "https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/ancillary-daas-hourly-rr"
URL = "https://www.iso-ne.com/transform/csv/daasreservedata?start={}&end={}"
COOKIE_PAGE = "https://www.iso-ne.com/isoexpress/web/reports/operations/-/tree/gen-fuel-mix"
LOCATION = "7000"
PRICES = {"Ten Minute Spinning Reserve Clearing Price": "as_price_dam_tmsr",
          "Ten Minute Reserve Clearing Price": "as_price_dam_tmr10",
          "Total Thirty Reserve Clearing Price": "as_price_dam_tmr30",
          "FER Price": "as_price_dam_fer"}
COLS = ["H", "Local Date", "Hour Ending", "Location ID", "Ten Minute Spinning Reserve Requirement",
        "Total Ten Minute Reserve Requirement", "Total Thirty Minute Reserve Requirement",
        "Forecasted MW Requirement", "Ten Minute Spinning Reserve Clearing Price",
        "Ten Minute Reserve Clearing Price", "Total Thirty Reserve Clearing Price", "FER Price",
        "TMSR Designated MW", "TMNSR Designated MW", "TMOR Designated MW", "EIR Designated MW"]
WANTED = {LOCATION: list(PRICES.values())}
_session = {}


def documents(start, until, log, offline):
    today = pd.Timestamp.now(tz=TZ).tz_localize(None).normalize()
    last = until - pd.Timedelta(days=1)
    docs = []
    for m in pd.period_range(start, last, freq="M"):
        a, b = max(m.start_time.normalize(), start), min(m.end_time.normalize(), last)
        docs.append(dict(url=URL.format(a.strftime("%Y%m%d"), b.strftime("%Y%m%d")), label=str(m),
                         settled=b + pd.Timedelta(days=2) < today))
    return docs


def fetch(doc, log, offline):
    url = requests.Request("GET", doc["url"]).prepare().url
    if offline or doc["settled"]:
        hit = ip.raw_cached(NAME, url)
        if hit:
            log(f"  raw file reused: {url} ({os.path.relpath(hit[1]['file'], ip.ROOT)})")
            return hit
        if offline:
            raise RuntimeError(f"offline: {url} is not in warehouse/raw/{NAME}/")
    if "s" not in _session:
        s = requests.Session()
        s.headers["User-Agent"] = "Mozilla/5.0 (Energy Research Warehouse)"
        s.get(COOKIE_PAGE, timeout=120)  # sets the cookies ISO-NE requires, as gridstatus does
        _session["s"] = s

    def call():
        r = _session["s"].get(url, timeout=180)
        if r.status_code != 200 or "csv" not in r.headers.get("Content-Type", ""):
            raise RuntimeError(f"HTTP {r.status_code}, {r.headers.get('Content-Type')} for {url}")
        return r
    r = ip.with_retries(url, call, log)
    log(f"  GET {url}: {len(r.content)} bytes")
    return r.content, {"url": url, "retrieved_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")),
                       "last_modified": r.headers.get("Last-Modified") or "", "file": "", "cached": False}


def labels(day):
    """The hour-ending labels the day has, in order, with the UTC start of each hour."""
    return [(f"{h.tz_convert(TZ).hour + 1:02d}", h) for h in common.day_hours(day, TZ)]


def parse(raw, doc, log):
    lines = list(csv.reader(io.StringIO(raw.decode("utf-8"))))
    heads = [l for l in lines if l and l[0] == "H"]
    if not heads or heads[0] != COLS:
        raise RuntimeError(f"{doc['label']}: columns {heads[0] if heads else None}: layout changed")
    data = [l for l in lines if l and l[0] == "D"]
    total = [l for l in lines if l and l[0] == "T"]
    if not total or total[0][1] != f"{len(data)} lines":
        raise RuntimeError(f"{doc['label']}: the file says {total[0][1] if total else 'nothing'}, {len(data)} read")
    x = pd.DataFrame(data, columns=COLS)
    if set(x["Location ID"]) - {LOCATION}:
        raise RuntimeError(f"{doc['label']}: locations {sorted(set(x['Location ID']))}, expected {LOCATION} only")
    out = []
    for date, g in x.groupby("Local Date", sort=False):
        day = pd.to_datetime(date, format="%m/%d/%Y").strftime("%Y-%m-%d")
        want = labels(day)
        got = [h.strip() for h in g["Hour Ending"]]
        if got == [w[0] for w in want]:
            ts = [w[1] for w in want]
        else:  # not the day's hours in order: keep only the hours named once, so the day is reported short
            once = {k: t for k, t in want if [w[0] for w in want].count(k) == 1}
            keep = [k in once and got.count(k) == 1 for k in got]
            log(f"  {day}: hours {got} are not the day's {len(want)} hours in order")
            g, ts = g[keep], [once[k] for k, ok in zip(got, keep) if ok]
        for col, var in PRICES.items():
            v = g[col].str.strip()
            ok = (v != "").values  # an empty cell is not a price: no row
            out.append(pd.DataFrame({"region": LOCATION, "variable": var, "ts": [t for t, o in zip(ts, ok) if o],
                                     "value": pd.to_numeric(v[ok].values, errors="raise"), "day": day}))
    if not out:
        return pd.DataFrame(columns=["region", "variable", "ts", "value", "day"])
    return pd.concat(out, ignore_index=True)


def header(regions, days, gaps):
    return [
        "Energy Research Warehouse (ERW): ISO-NE day-ahead ancillary service clearing prices, hourly, the system",
        "Shape: series (docs/datastandard.md v0). Unit USD/MW-hour: US dollars per MW for one hour (the file's "
        "unit row reads \"$\"). ts_utc is the start of the hour, UTC.",
        "Region: 7000, the report's one Location ID (New England as a whole). Variables: as_price_dam_tmsr Ten "
        "Minute Spinning Reserve Clearing Price, as_price_dam_tmr10 Ten Minute Reserve Clearing Price, "
        "as_price_dam_tmr30 Total Thirty Reserve Clearing Price, as_price_dam_fer FER Price (the forecast energy "
        "requirement). The requirements and designated MW in the same file are not kept.",
        "The market began on 2025-03-01; the report holds no earlier day.",
    ]


SPEC = dict(
    name=NAME, connector=NAME, label="ISO-NE", namespace="isone", tz=TZ, first=FIRST, geo="US-CT,US-MA,US-ME,US-NH,US-RI,US-VT",
    market="isone_dam", source=SOURCE, report=REPORT, page=PAGE, document_list=PAGE,
    publisher=ip.ISO_PUBLISHERS["isone"], license="internal", documents=documents, fetch=fetch, parse=parse,
    wanted=WANTED, header=header, pause=2,
    license_line="License: internal. ISO-NE's terms (https://www.iso-ne.com/legal-privacy): \"Any duplication of "
                 "the Content or non-personal use may violate copyright, trademark, and other laws.\"",
)


if __name__ == "__main__":
    sys.exit(common.run(SPEC))
