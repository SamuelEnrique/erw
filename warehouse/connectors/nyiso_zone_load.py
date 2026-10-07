#!/usr/bin/env python3
"""NYISO: hourly load by zone, the integrated real-time actual load (session 138, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nyiso_zone_load_hourly.csv, from
NYISO's public report P-58C, "Integrated Real-Time Actual Load" (palIntegrated):

    http://mis.nyiso.com/public/csv/palIntegrated/<YYYYMM>01palIntegrated_csv.zip      a month: one CSV a day
    "Time Stamp","Time Zone","Name","PTID","Integrated Load"      one line a zone and hour

    python warehouse/connectors/nyiso_zone_load.py [--days N] [--from YYYY-MM-DD] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row a zone and hour for NYISO's eleven load zones, entity nyiso:<Name> with NYISO's own names
(CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST): the same names the ERW's NYISO
price tables use (nyiso_dam_zone_prices, nyiso_rtm_zone_prices), so load and price join on entity. Value: Integrated
Load, MW over the hour. The file gives no total for the state and none is written: nothing is summed here.

THE HOUR. Time Stamp is the hour's start in Eastern time and Time Zone says which (EDT or EST) on every line, so the
23-hour and the 25-hour day need no inference: EDT is UTC less 4 hours, EST UTC less 5. A line that is not on the
hour, or whose zone is not one of the eleven, is read and not written (the log counts them).

REQUESTS. One zip a calendar month, newest first. This month's is asked for each run, last month's too in a month's
first seven days; an earlier month once (its raw file is kept).

License: public, with a caution (the ruling of session 65 for NYISO's capacity prices, kept by sessions 85 and 136;
the same notice covers this report, on the same public server). NYISO's legal notice
(https://www.nyiso.com/legal-notice, read 6 October 2026) grants no license and does not forbid republishing its
market data: "Access to this Web site does not confer any license or ownership interest in either the form or content
of the Web site ... Downloading, republishing, retransmitting, reproducing, or other use of any image or video on
this website as a stand-alone file is strictly prohibited". The prohibition names images and video, not data. A
person can rule otherwise.
"""

import io
import os
import sys
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import zone_load as zl  # noqa: E402

NAME = "nyiso_zone_load_hourly"
CONNECTOR = "nyiso_zone_load"
SOURCE = "nyiso:palIntegrated"
URL = "http://mis.nyiso.com/public/csv/palIntegrated/{}01palIntegrated_csv.zip"
PAGE = "http://mis.nyiso.com/public/P-58Clist.htm"
TZ = "America/New_York"
ZONES = ip.NYISO_ZONES                                   # the names the price tables use
COLS = ["Time Stamp", "Time Zone", "Name", "PTID", "Integrated Load"]
OFFSET = {"EDT": 4, "EST": 5}                             # hours to add to the local stamp for UTC
ROWS_A_MONTH = 31 * 25 * len(ZONES)                       # what a month's file is taken to hold before it is asked for
PAUSE = 2


def parse_day(text):
    """One day's CSV as (rows of entity, node, ts, value; lines read; lines not written and why)."""
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    if list(df.columns) != COLS:
        raise RuntimeError(f"columns {list(df.columns)}, expected {COLS}")
    n = len(df)
    zone = df["Name"].str.strip()
    off = df["Time Zone"].str.strip().map(OFFSET)
    if off.isna().any():
        raise RuntimeError(f"time zone {sorted(set(df['Time Zone'][off.isna()]))}, expected EDT or EST")
    local = pd.to_datetime(df["Time Stamp"].str.strip(), format="%m/%d/%Y %H:%M:%S")
    ts = (local + pd.to_timedelta(off, unit="h")).dt.tz_localize("UTC")
    v = pd.to_numeric(df["Integrated Load"], errors="coerce")
    on_hour = (local.dt.minute == 0) & (local.dt.second == 0)
    known = zone.isin(ZONES)
    keep = on_hour & known & v.notna()
    skipped = {"not on the hour": int((~on_hour).sum()), "another zone name": int((on_hour & ~known).sum()), "blank load": int((on_hour & known & v.isna()).sum())}
    piece = pd.DataFrame({"entity": "nyiso:" + zone[keep], "node": zone[keep], "ts": ts[keep], "value": v[keep]})
    return piece, n, skipped


def pull(log, first, counter):
    today = pd.Timestamp.now(tz=TZ).normalize().tz_localize(None)
    this = today.replace(day=1)
    out, notes, skipped, differ = [], [], {}, 0
    for m in reversed(pd.date_range(first.replace(day=1), today, freq="MS")):
        if not counter.room(ROWS_A_MONTH):
            log(f"  stopping before {m:%Y-%m}: another month's file would pass this run's ceiling ({counter.read:,} rows read)")
            notes.append(f"stopped before {m:%Y-%m}: another month would pass the ceiling")
            break
        url = URL.format(m.strftime("%Y%m"))
        fresh = m == this or (m == this - pd.offsets.MonthBegin(1) and today.day <= 7)
        try:
            content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=fresh, headers=zl.UA, pause=PAUSE)
        except ip.SourceGap:
            log(f"  {m:%Y-%m}: NYISO has no monthly file (HTTP 404); the month is not written")
            notes.append(f"{m:%Y-%m}: no monthly file at NYISO (HTTP 404)")
            continue
        z = zipfile.ZipFile(io.BytesIO(content))
        pieces, n = [], 0
        for name in sorted(z.namelist()):
            if name.lower().endswith(".csv"):
                p, k, sk = parse_day(z.read(name).decode("utf-8", "replace"))
                pieces.append(p)
                n += k
                for why, c in sk.items():
                    skipped[why] = skipped.get(why, 0) + c
        if not zl.reused(rec):
            counter.add(n, m.strftime("%Y-%m"))
        month, d = zl.once(pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame(columns=zl.PIECE), log, m.strftime("%Y-%m"))
        differ += d
        log(f"  {m:%Y-%m}: {n:,} lines, {len(month):,} zone hours{' (raw file reused)' if zl.reused(rec) else ''}")
        out.append(zl.rows(SPEC, month, url, rec))
    for why, c in skipped.items():
        if c:
            notes.append(f"{c:,} lines read and not written: {why}")
    if differ:
        notes.append(f"{differ:,} zone hours NYISO gives twice with different loads are not written")
    return out, notes


SPEC = dict(
    iso="nyiso", name=NAME, connector=CONNECTOR, source=SOURCE, geo="US-NY", days=10, ceiling=20000, stale_days=5,
    title="P-58C, Integrated Real-Time Actual Load (palIntegrated)",
    what="NYISO, hourly load by zone, the integrated real-time actual load of its eleven load zones (P-58C, palIntegrated)",
    entry=dict(source=SOURCE, publisher="New York ISO (NYISO)",
               report="P-58C, Integrated Real-Time Actual Load (palIntegrated), by zone [terms: \"Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site\"; "
                      "the notice forbids republishing \"any image or video on this website as a stand-alone file\", not data (https://www.nyiso.com/legal-notice, read 6 October 2026)]",
               report_url=PAGE, document_list=URL.format("<YYYYMM>"), license="public", tables=[NAME]),
    notes=["value: NYISO's Integrated Load for the zone and hour (MW over the hour). Time Stamp is the hour's start, Eastern; the file's Time Zone column (EDT, EST) places every hour, the repeated autumn hour included. "
           "Entities carry NYISO's zone names, the same as nyiso_dam_zone_prices and nyiso_rtm_zone_prices. NYISO's file gives no state total and none is written."],
    license="License: public, with a caution (sessions 65, 85 and 136). NYISO's legal notice grants no license and forbids republishing \"any image or video on this website as a stand-alone file\", "
            "which names images and video, not data (https://www.nyiso.com/legal-notice, read 6 October 2026). A person can rule otherwise.",
)


if __name__ == "__main__":
    sys.exit(zl.run(SPEC, pull))
