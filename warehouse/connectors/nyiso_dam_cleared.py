#!/usr/bin/env python3
"""NYISO: load scheduled in the day-ahead market, by hour (session 136, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nyiso_dam_cleared_energy.csv, from
NYISO's public report P-30, "Day-Ahead Market Daily Energy Report":

    http://mis.nyiso.com/public/csv/damenergy/<YYYYMM>01DAM_energy_rep_csv.zip      a month: one CSV a day
    Date Hour (Eastern, the hour's start), ..., Total Load Scheduled, ..., and a last line "Total"

    python warehouse/connectors/nyiso_dam_cleared.py [--days N] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row an hour for the entity nyiso:system: the column "Total Load Scheduled", the load the
day-ahead market scheduled system-wide (bid load, bilateral load and price-capped load together, as NYISO totals
them). MW over the hour. The file's "Total" line is the day's sum and is not a row. The report's other columns
(offers, generation, imports, exports, virtual bids) are read and not written.

REQUESTS. One zip a calendar month, newest first: this month and the last from NYISO each run, an earlier month once.

License: public, with a caution (the ruling of session 65 for NYISO's capacity prices, kept by session 85). NYISO's
legal notice (https://www.nyiso.com/legal-notice, read 6 October 2026) grants no license and does not forbid
republishing its market data: "Access to this Web site does not confer any license or ownership interest in either
the form or content of the Web site ... Downloading, republishing, retransmitting, reproducing, or other use of any
image or video on this website as a stand-alone file is strictly prohibited". The prohibition names images and
video, not data. A person can rule otherwise.
"""

import io
import os
import sys
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dam_cleared as dc  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "nyiso_dam_cleared_energy"
CONNECTOR = "nyiso_dam_cleared"
SOURCE = "nyiso:damenergy"
URL = "http://mis.nyiso.com/public/csv/damenergy/{}01DAM_energy_rep_csv.zip"
PAGE = "http://mis.nyiso.com/public/P-30list.htm"
TZ = "America/New_York"
COLUMN = "Total Load Scheduled"
PAUSE = 2


def parse_day(text):
    """One day's CSV as ({hour start UTC: MW}, rows read). The "Total" line is not an hour."""
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    if "Date Hour" not in df.columns or COLUMN not in df.columns:
        raise RuntimeError(f"columns {list(df.columns)[:12]}, expected 'Date Hour' and {COLUMN!r}")
    n = len(df)
    df = df[df["Date Hour"].str.strip().str.lower() != "total"]
    local = pd.to_datetime(df["Date Hour"].str.strip(), format="%m/%d/%Y %H:%M")
    ts = local.dt.tz_localize(TZ, ambiguous="infer", nonexistent="raise").dt.tz_convert("UTC")
    v = pd.to_numeric(df[COLUMN], errors="coerce")
    return {t: float(m) for t, m in zip(ts, v) if pd.notna(m)}, n


def pull(log, days, counter):
    today = pd.Timestamp.now(tz=TZ).normalize().tz_localize(None)
    first = (today - pd.Timedelta(days=days)).replace(day=1)
    out = []
    for m in reversed(pd.date_range(first, today, freq="MS")):
        url = URL.format(m.strftime("%Y%m"))
        fresh = m >= (today.replace(day=1) - pd.offsets.MonthBegin(1))
        try:
            content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=fresh, headers=dc.UA, pause=PAUSE)
        except ip.SourceGap:
            log(f"  {m:%Y-%m}: NYISO has no monthly file (HTTP 404); the month is not written")
            continue
        z = zipfile.ZipFile(io.BytesIO(content))
        hours, n = {}, 0
        for name in sorted(z.namelist()):
            if name.lower().endswith(".csv"):
                h, k = parse_day(z.read(name).decode("utf-8", "replace"))
                hours.update(h)
                n += k
        if not dc.reused(rec):
            counter.add(n, m.strftime("%Y-%m"))
        log(f"  {m:%Y-%m}: {n:,} rows, {len(hours)} hours{' (raw file reused)' if dc.reused(rec) else ''}")
        out += [dc.row(SPEC, "nyiso:system", ts, v, COLUMN, url, rec["retrieved_at"]) for ts, v in sorted(hours.items())]
    return out


SPEC = dict(
    iso="nyiso", name=NAME, connector=CONNECTOR, source=SOURCE, unit="MW", geo="US-NY", days=14, ceiling=5000, stale_days=5,
    what="NYISO, load scheduled in the day-ahead market by hour, system-wide (P-30, Day-Ahead Market Daily Energy Report, Total Load Scheduled)",
    entry=dict(source=SOURCE, publisher="New York ISO (NYISO)", report="P-30, Day-Ahead Market Daily Energy Report", report_url=PAGE,
               document_list=URL.format("<YYYYMM>"), license="public", tables=[NAME]),
    notes=["value: NYISO's column Total Load Scheduled for the hour (MW over the hour). The file's Total line is the day's sum and is not written; the report's other columns are read and not written."],
    license="License: public, with a caution (sessions 65 and 85). NYISO's legal notice grants no license and forbids republishing \"any image or video on this website as a stand-alone file\", "
            "which names images and video, not data (https://www.nyiso.com/legal-notice, read 6 October 2026). A person can rule otherwise.",
)


if __name__ == "__main__":
    sys.exit(dc.run(SPEC, pull))
