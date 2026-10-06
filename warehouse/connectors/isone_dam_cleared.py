#!/usr/bin/env python3
"""ISO-NE: demand cleared in the day-ahead market, by hour (session 136, approved pull). INTERNAL.

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/isone_dam_cleared_energy.csv, from
ISO New England's ISO Express report "Day-Ahead Hourly Cleared Demand":

    https://www.iso-ne.com/transform/csv/hourlydayaheaddemand?start=<YYYYMMDD>&end=<YYYYMMDD>
    lines: "C" comments; "H","Date","Hour Ending","Day-Ahead Cleared Demand"; "H","Date","HE","MWh"; "D" data rows

    python warehouse/connectors/isone_dam_cleared.py [--days N] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row an hour for the entity isone:system: ISO-NE's Day-Ahead Cleared Demand, MWh, system-wide.
Hour ending 01 to 24, Eastern; "02X" is the second 01:00 to 02:00 hour of the autumn clock change.

HOW OPEN IT IS: ONLY PARTLY. The address answers HTTP 403 to a plain request. It answers a session that has first
opened one of ISO Express's report pages, which sets an anonymous cookie: no account, no key. That is the route the
ERW's ISO-NE reserve prices already use (isone_as_prices.py, session 85). ISO Express's own page puts a CAPTCHA on
its search for past dates and offers one to fifteen days at a time. So this connector asks for little: --days days
(default 14), fifteen days a request, and it never walks back through the years. The history grows by merging.

License: INTERNAL (the ERW's standing reading for ISO-NE, sessions 65 and 85). ISO-NE's legal notice
(https://www.iso-ne.com/legal-privacy, read 6 October 2026): "You are also hereby put on notice that the Content is
protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate
copyright, trademark, and other laws." The table is not published; it is in no public dataset and no download.
"""

import csv
import io
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dam_cleared as dc  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "isone_dam_cleared_energy"
CONNECTOR = "isone_dam_cleared"
SOURCE = "isone:hourlydayaheaddemand"
URL = "https://www.iso-ne.com/transform/csv/hourlydayaheaddemand?start={}&end={}"
COOKIE_PAGE = "https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/dmnd-da-hourly-cleared"
TZ = "America/New_York"
HEAD = ["H", "Date", "Hour Ending", "Day-Ahead Cleared Demand"]
SPAN = 15           # days a request, the most ISO Express's own page offers
PAUSE = 3
_session = {}


def fetch(url, log):
    """The CSV, in a session that has opened a report page first (the cookie ISO-NE requires; isone_as_prices.py)."""
    if "s" not in _session:
        s = requests.Session()
        s.headers["User-Agent"] = dc.UA["User-Agent"]
        s.get(COOKIE_PAGE, timeout=120)
        _session["s"] = s

    def call():
        r = _session["s"].get(url, timeout=180)
        if r.status_code != 200 or "csv" not in r.headers.get("Content-Type", ""):
            raise RuntimeError(f"HTTP {r.status_code}, {r.headers.get('Content-Type')} for {url}")
        return r
    r = ip.with_retries(url, call, log)
    log(f"  GET {url}: {len(r.content)} bytes")
    return r.content, ip.utc_iso(pd.Timestamp.now(tz="UTC"))


def parse(content):
    """({hour start UTC: MWh}, data rows read)."""
    lines = list(csv.reader(io.StringIO(content.decode("utf-8", "replace"))))
    heads = [l for l in lines if l and l[0] == "H"]
    if not heads or [c.strip() for c in heads[0]] != HEAD:
        raise RuntimeError(f"header {heads[:1]}, expected {HEAD}")
    if len(heads) > 1 and heads[1][-1].strip() != "MWh":
        raise RuntimeError(f"unit line {heads[1]}, expected MWh")
    out, n = {}, 0
    for l in lines:
        if not l or l[0] != "D":
            continue
        n += 1
        he, second = l[2].strip(), False
        if he.upper().endswith("X"):
            he, second = he[:-1], True
        if l[3].strip() == "":
            continue                                         # an hour ISO-NE leaves blank is not a quantity
        local = pd.Timestamp(pd.to_datetime(l[1].strip(), format="%m/%d/%Y")) + pd.Timedelta(hours=int(he) - 1)
        ts = local.tz_localize(TZ, ambiguous=not second, nonexistent="raise").tz_convert("UTC")
        out[ts] = float(l[3])
    return out, n


def pull(log, days, counter):
    import time
    today = pd.Timestamp.now(tz=TZ).normalize().tz_localize(None)
    start, end = today - pd.Timedelta(days=days), today + pd.Timedelta(days=1)          # tomorrow's market has cleared by early afternoon
    out, a = [], start
    while a <= end:
        b = min(a + pd.Timedelta(days=SPAN - 1), end)
        url = URL.format(a.strftime("%Y%m%d"), b.strftime("%Y%m%d"))
        content, retrieved = fetch(url, log)
        hours, n = parse(content)
        counter.add(n, f"{a:%Y-%m-%d} to {b:%Y-%m-%d}")
        log(f"  {a:%Y-%m-%d} to {b:%Y-%m-%d}: {n:,} rows, {len(hours)} hours")
        out += [dc.row(SPEC, "isone:system", ts, v, "Day-Ahead Cleared Demand", url, retrieved) for ts, v in sorted(hours.items())]
        a = b + pd.Timedelta(days=1)
        time.sleep(PAUSE)
    return out


SPEC = dict(
    iso="isone", name=NAME, connector=CONNECTOR, source=SOURCE, unit="MWh", geo="US-CT,US-MA,US-ME,US-NH,US-RI,US-VT", days=14, ceiling=2000, stale_days=5,
    what="ISO-NE, demand cleared in the day-ahead market by hour, system-wide (ISO Express, Day-Ahead Hourly Cleared Demand). INTERNAL",
    entry=dict(source=SOURCE, publisher="ISO New England (ISO-NE)", report="ISO Express, Day-Ahead Hourly Cleared Demand", report_url=COOKIE_PAGE,
               document_list=URL.format("<YYYYMMDD>", "<YYYYMMDD>"), license="internal", tables=[NAME]),
    notes=["value: ISO-NE's Day-Ahead Cleared Demand for the hour, MWh. The address answers only a session that has opened an ISO Express report page (an anonymous cookie; no account): "
           "few days are asked for, fifteen a request, and past years are never walked."],
    license="License: internal. ISO-NE's legal notice: \"Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws\" "
            "(https://www.iso-ne.com/legal-privacy, read 6 October 2026). Not published, in no public dataset and no download.",
)


if __name__ == "__main__":
    sys.exit(dc.run(SPEC, pull))
