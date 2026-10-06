#!/usr/bin/env python3
"""ERCOT: energy bought in the day-ahead market, by hour (session 136, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ercot_dam_cleared_energy.csv, from
ERCOT's public report NP4-192-CD, "DAM Total Energy Purchased" (report type 12333): the energy bought in the
day-ahead market at each settlement point, by hour. The file published on a day covers the next delivery day.

    list   https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12333
    file   https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>      (a zip of one CSV)
    cols   DeliveryDate, HourEnding, Settlement_Point, Total_DAM_Energy_Bought, RepeatedHourFlag (Central time)

    python warehouse/connectors/ercot_dam_cleared.py [--days N] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row an hour for the entity ercot:system: the sum of Total_DAM_Energy_Bought over every
settlement point of the file, which is the day-ahead market's energy purchased system-wide. The sum is this
connector's one computation; an hour is written only when every one of its rows holds a number. ERCOT's file does not
name its unit. Its product page calls the figure an "amount of energy" for an hour, which is read here as MWh.

SIZE. A day's file holds about 24,000 rows (about 1,000 settlement points for 24 hours), all of which are read to
make 24. ERCOT lists the last 31 days only, so the history starts where the first pull did and grows by merging.
A run reads --days days (default 8: a week and a day) and stops before a file that would pass --ceiling.

License: public. ERCOT's terms of use (https://www.ercot.com/help/terms, read 6 October 2026), item 5:
"Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and
redistributed in compilations, charts, and analyses without maintaining such notices." Item 6: "Use of this website
in a manner that negatively affects the performance of this website or other ERCOT systems is prohibited": one
request every three seconds, and a file once.
"""

import io
import json
import os
import sys
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dam_cleared as dc  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "ercot_dam_cleared_energy"
CONNECTOR = "ercot_dam_cleared"
SOURCE = "ercot:NP4-192-CD"
TYPE_ID = 12333
DOC_LIST = f"https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={TYPE_ID}"
DOWNLOAD = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={}"
PAGE = "https://www.ercot.com/mp/data-products/data-product-details?id=NP4-192-CD"
TZ = "America/Chicago"
COLS = ["DeliveryDate", "HourEnding", "Settlement_Point", "Total_DAM_Energy_Bought", "RepeatedHourFlag"]
ROWS_A_DAY = 26000          # what a day's file is taken to hold before it is opened (about 24,000 on 6 October 2026)
PAUSE = 3


def to_utc(dates, hour_ending, repeated):
    """ERCOT's delivery date and hour ending (01:00 to 24:00, Central) as the hour's start in UTC; the repeated-hour
    flag Y marks the second 01:00 to 02:00 hour of the autumn clock change (as ercot_as_prices.py reads it)."""
    he = hour_ending.str.strip().str.extract(r"^(\d{1,2}):00$")[0]
    if he.isna().any():
        raise RuntimeError(f"hour ending not HH:00: {hour_ending[he.isna()].unique()[:5]}")
    he = he.astype(int)
    local = pd.to_datetime(dates.str.strip(), format="%m/%d/%Y") + pd.to_timedelta(he - 1, unit="h")
    flag = repeated.str.strip().str.upper()
    return local.dt.tz_localize(TZ, ambiguous=(flag == "N").values, nonexistent="raise").dt.tz_convert("UTC")


def parse(content):
    """A day's zip as (hours: Series of the system sum indexed by the hour's UTC start, rows read)."""
    z = zipfile.ZipFile(io.BytesIO(content))
    names = [n for n in z.namelist() if n.lower().endswith(".csv")]
    if len(names) != 1:
        raise RuntimeError(f"the zip holds {z.namelist()}, expected one CSV")
    df = pd.read_csv(io.BytesIO(z.read(names[0])), dtype=str, keep_default_na=False)
    if list(df.columns) != COLS:
        raise RuntimeError(f"columns {list(df.columns)}, expected {COLS}")
    v = pd.to_numeric(df["Total_DAM_Energy_Bought"], errors="coerce")
    ts = to_utc(df["DeliveryDate"], df["HourEnding"], df["RepeatedHourFlag"])
    g = pd.DataFrame({"ts": ts, "v": v}).groupby("ts")["v"]
    whole = g.apply(lambda c: bool(c.notna().all()))          # an hour with a blank row is not summed
    return g.sum()[whole], len(df)


def pull(log, days, counter):
    content, rec = ip.fetch_raw(CONNECTOR, DOC_LIST, log, fresh=True, headers=dc.UA, pause=PAUSE)
    docs = [d["Document"] for d in json.loads(content)["ListDocsByRptTypeRes"]["DocumentList"]]
    docs = sorted((d for d in docs if str(d.get("ConstructedName", "")).endswith("_csv.zip")), key=lambda d: d["PublishDate"], reverse=True)
    log(f"  ERCOT lists {len(docs)} days of {SOURCE}; asking for the newest {days}")
    out = []
    for d in docs[:days]:
        if not counter.room(ROWS_A_DAY):
            log(f"  stopping before {d['ConstructedName']}: another day's file would pass this run's ceiling ({counter.read:,} rows read)")
            break
        url = DOWNLOAD.format(d["DocID"])
        content, rec = ip.fetch_raw(CONNECTOR, url, log, headers=dc.UA, pause=PAUSE)
        hours, n = parse(content)
        if not dc.reused(rec):
            counter.add(n, d["ConstructedName"])           # a file kept from an earlier run crosses no wire again
        log(f"  {d['ConstructedName']}: {n:,} rows, {len(hours)} whole hours{' (raw file reused)' if dc.reused(rec) else ''}")
        out += [dc.row(SPEC, "ercot:system", ts, v, "Total_DAM_Energy_Bought, summed over settlement points", url, rec["retrieved_at"]) for ts, v in hours.items()]
    return out


SPEC = dict(
    iso="ercot", name=NAME, connector=CONNECTOR, source=SOURCE, unit="MWh", geo="US-TX", days=8, ceiling=250000, stale_days=5,
    what="ERCOT, energy bought in the day-ahead market by hour, system-wide (NP4-192-CD, DAM Total Energy Purchased)",
    entry=dict(source=SOURCE, publisher="Electric Reliability Council of Texas (ERCOT)", report="NP4-192-CD, DAM Total Energy Purchased", report_url=PAGE,
               document_list=DOC_LIST, license="public", tables=[NAME]),
    notes=["value: the sum of Total_DAM_Energy_Bought over every settlement point of ERCOT's file for the hour (the one computation made here); an hour with a blank row is not written. "
           "ERCOT's file names no unit; its product page calls the figure an amount of energy for the hour, read here as MWh.",
           "ERCOT lists the last 31 days of this report only: the history starts with the first pull (6 October 2026) and grows by merging."],
    license="License: public. ERCOT's terms of use, item 5: \"raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, "
            "and analyses without maintaining such notices\" (https://www.ercot.com/help/terms, read 6 October 2026).",
)


if __name__ == "__main__":
    sys.exit(dc.run(SPEC, pull))
