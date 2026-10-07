#!/usr/bin/env python3
"""ERCOT: hourly native load by weather zone (session 138, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ercot_zone_load_hourly.csv, from
ERCOT's "Hourly Load Data Archives", native load by weather zone, a workbook a year:

    https://www.ercot.com/gridinfo/load/load_hist                    the page that lists the yearly files
    https://www.ercot.com/files/docs/<date>/Native_Load_<YYYY>.zip   a year: one workbook, one line an hour
    Hour Ending, COAST, EAST, FWEST, NORTH, NCENT, SOUTH, SCENT, WEST, ERCOT

    python warehouse/connectors/ercot_zone_load.py [--days N] [--from YYYY-MM-DD] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row a weather zone and hour, MW over the hour, entity ercot:<zone> with ERCOT's own column
names (COAST, EAST, FWEST, NORTH, NCENT, SOUTH, SCENT, WEST), and ERCOT's own total, the column ERCOT, as the entity
ercot:system (the entity of ercot_dam_cleared_energy). The total is ERCOT's column, never a sum made here. Older
files name four columns otherwise (FAR_WEST, NORTH_C, SOUTHERN, SOUTH_C): they are the same zones, written under the
current names, and node keeps the file's own column name.

WEATHER ZONES ARE NOT LOAD ZONES. ERCOT's eight weather zones are the regions of its load forecast. Its prices are
settled at four competitive load zones (LZ_HOUSTON, LZ_NORTH, LZ_SOUTH, LZ_WEST), four non-opt-in load zones (LZ_AEN,
LZ_CPS, LZ_LCRA, LZ_RAYBN) and four trading hubs (HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST), which the ERW's price
tables hold as ercot:LZ_... and ercot:HB_.... The two maps do not coincide and ERCOT publishes no table that turns
one into the other. The nearest correspondences are approximate only: COAST is mostly the Houston load zone and hub;
NORTH, NCENT and EAST lie mostly in the North load zone; FWEST and WEST mostly in the West load zone; SOUTH and SCENT
mostly in the South load zone (with Austin's and San Antonio's non-opt-in zones inside SCENT). The weather zone NORTH
is not the load zone LZ_NORTH (most of that load zone's demand is in NCENT, around Dallas and Fort Worth), and the
same holds for SOUTH and WEST. So ercot:NORTH here does not join ercot:LZ_NORTH or ercot:HB_NORTH, and no such join
is offered; only ercot:system joins another table.

THE HOUR. ERCOT gives the hour's end in Central time; ts_utc is the hour's start. "24:00" is the hour that ends at
midnight. The hour the clock repeats in autumn is in the file twice (the files from 2017 mark the second "DST"; the
files of 2015 and 2016 hold date cells and repeat the stamp); the first is placed in daylight time, the second in
standard time. The spring day has 23 lines. The files from 2017 skip the hour ending 03:00 (01:00, 02:00, 04:00);
the files of 2015 and 2016 skip 02:00 and hold 03:00 (01:00, 03:00, 04:00): there the line is labelled by the clock
at its end, the hour that began at 01:00 standard time, and it is placed by its end (zone_load.to_utc). The repeated
hour held once only could be either of two hours and would not be written; it is counted in the log and the header.
Nothing is guessed.

REQUESTS. The page, then one file a year from the year of --from (or of --days back), newest first. A past year's
file is asked for once (its raw file is kept). The current year's file, which ERCOT extends month by month, is asked
for again when the kept copy is more than 13 days old.

HOW ROWS ARE COUNTED. A year's workbook holds one line an hour with nine loads on it. Against the ceiling it is
counted as nine rows an hour, one a series, which is what it makes in the table.

License: public (the terms session 136 quoted for ERCOT's day-ahead report; they cover the public pages of
ercot.com, where these archives are). ERCOT's terms of use, item 5 (https://www.ercot.com/help/terms, read 6 October
2026): "raw data provided in public portions of this website may be used, reproduced, and redistributed in
compilations, charts, and analyses without maintaining such notices." Also: "Use of this website in a manner that
negatively affects the performance of this website or other ERCOT systems is prohibited."
"""

import io
import os
import re
import sys
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import zone_load as zl  # noqa: E402

NAME = "ercot_zone_load_hourly"
CONNECTOR = "ercot_zone_load"
SOURCE = "ercot:load_hist"
PAGE = "https://www.ercot.com/gridinfo/load/load_hist"
LINK = re.compile(r'href="(https://www\.ercot\.com/files/docs/\d{4}/\d{2}/\d{2}/native_load_(\d{4})\.(?:zip|xlsx|xls))"', re.I)
TZ = "America/Chicago"
ZONES = ["COAST", "EAST", "FWEST", "NORTH", "NCENT", "SOUTH", "SCENT", "WEST"]
TOTAL = "ERCOT"
OLD_NAMES = {"FAR_WEST": "FWEST", "NORTH_C": "NCENT", "SOUTHERN": "SOUTH", "SOUTH_C": "SCENT"}
HOUR_COLS = {"HOUR ENDING", "HOUR_ENDING", "HOURENDING", "HOUR_END", "HOUR END"}
ROWS_A_YEAR = 8784 * (len(ZONES) + 1)
KEEP_DAYS = 13                                           # the current year's kept copy is asked for again after this
PAUSE = 3
STAMP = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4}) (\d{1,2}):(\d{2})(?::00)?$")


def links(html):
    """{year: the address of its native load file} from ERCOT's archive page."""
    return {int(y): u for u, y in LINK.findall(html)}


def hour_end(x):
    """One cell of ERCOT's hour-ending column as (the hour's end, local and naive; whether ERCOT marks it DST)."""
    if isinstance(x, str):
        s = x.strip()
        marked = s.upper().endswith("DST")
        if marked:
            s = s[:-3].strip()
        m = STAMP.match(s)
        if not m:
            raise RuntimeError(f"hour ending {x!r} is not MM/DD/YYYY HH:MM")
        mo, d, y, h, mi = (int(g) for g in m.groups())
        return pd.Timestamp(year=y, month=mo, day=d) + pd.Timedelta(hours=h, minutes=mi), marked       # 24:00 is the next midnight
    return pd.Timestamp(x).round("min"), False                                                        # a date cell: spreadsheets hold 00:59:59.997


def workbook(content):
    """The year's workbook as bytes: the file itself, or the one workbook inside ERCOT's zip."""
    if content[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(content))
        names = z.namelist()
        if "[Content_Types].xml" in names:
            return content
        books = [n for n in names if n.lower().endswith((".xlsx", ".xls"))]
        if len(books) != 1:
            raise RuntimeError(f"the zip holds {names}, expected one workbook")
        return z.read(books[0])
    return content


def parse_frame(df):
    """ERCOT's sheet (one line an hour) as (rows of entity, node, ts, value; values read; hours not placed)."""
    cols = {str(c).strip().upper().replace(" ", "_"): c for c in df.columns}
    hour = [c for k, c in cols.items() if k.replace("_", " ") in HOUR_COLS or k in HOUR_COLS]
    if len(hour) != 1:
        raise RuntimeError(f"columns {list(df.columns)}, expected one hour-ending column")
    named = {OLD_NAMES.get(k, k): c for k, c in cols.items() if c != hour[0]}
    if set(named) != set(ZONES + [TOTAL]):
        raise RuntimeError(f"columns {list(df.columns)}, expected the hour ending, {ZONES} and {TOTAL}")
    df = df[df[hour[0]].notna() & (df[hour[0]].astype(str).str.strip() != "")]
    ends = [hour_end(x) for x in df[hour[0]]]
    end = pd.Series([e for e, _ in ends])
    marked = pd.Series([m for _, m in ends])
    if (end.dt.minute != 0).any():
        raise RuntimeError(f"an hour ending is not on the hour: {end[end.dt.minute != 0].iloc[0]}")
    local = end - pd.Timedelta(hours=1)
    second = local.duplicated(keep="first")
    if (marked & ~second).any():
        raise RuntimeError(f"ERCOT marks {local[marked & ~second].iloc[0]} DST, but it is not the second of a repeated hour: the file's order is not understood")
    ts, by_end = zl.to_utc(local, TZ)
    lost = [str(t) for t in local[ts.isna().values]]
    pieces = []
    for zone in ZONES + [TOTAL]:
        c = named[zone]
        pieces.append(pd.DataFrame({"entity": "ercot:system" if zone == TOTAL else "ercot:" + zone, "node": str(c).strip(), "ts": ts.values,
                                    "value": pd.to_numeric(df[c], errors="coerce").values}))
    piece = pd.concat(pieces, ignore_index=True)
    piece["ts"] = pd.to_datetime(piece["ts"], utc=True)
    return piece[piece["ts"].notna()].reset_index(drop=True), len(df) * (len(ZONES) + 1), lost, by_end


def parse(content):
    return parse_frame(pd.read_excel(io.BytesIO(workbook(content)), sheet_name=0, header=0))


def pull(log, first, counter):
    today = pd.Timestamp.now(tz=TZ).tz_localize(None)
    html, _ = ip.fetch_raw(CONNECTOR, PAGE, log, fresh=True, headers=zl.UA, pause=PAUSE)
    files = links(html.decode("utf-8", "replace"))
    log(f"  ERCOT's page lists native load files for {min(files)} to {max(files)}" if files else "  ERCOT's page lists no native load file")
    out, notes = [], []
    for year in range(today.year, first.year - 1, -1):
        if year not in files:
            log(f"  {year}: ERCOT's page lists no native load file; the year is not written")
            notes.append(f"{year}: no native load file on ERCOT's page")
            continue
        url = files[year]
        kept = ip.raw_cached(CONNECTOR, url)
        fresh = year == today.year and (kept is None or (pd.Timestamp.now(tz="UTC") - pd.Timestamp(kept[1]["retrieved_at"])).days >= KEEP_DAYS)
        if (fresh or kept is None) and not counter.room(ROWS_A_YEAR):
            log(f"  stopping before {year}: another year's file would pass this run's ceiling ({counter.read:,} rows read)")
            notes.append(f"stopped before {year}: another year would pass the ceiling")
            break
        content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=fresh, headers=zl.UA, pause=PAUSE)
        piece, n, lost, by_end = parse(content)
        if not zl.reused(rec):
            counter.add(n, str(year))
        log(f"  {year}: {n // (len(ZONES) + 1):,} lines ({n:,} loads), {piece['ts'].nunique():,} hours placed{' (raw file reused)' if zl.reused(rec) else ''}")
        if by_end:
            log(f"  {year}: {by_end} hour of the spring clock change is labelled by its end (hour ending 03:00 after 01:00) and placed by it")
            notes.append(f"{year}: the hour after the spring clock change is labelled by its end in ERCOT's file (hour ending 03:00 follows 01:00) and is placed by its end: it began at 01:00 standard time")
        if lost:
            log(f"  {year}: {len(lost)} hours not placed in UTC and not written (local hour starts): {', '.join(lost)}")
            notes.append(f"{year}: {len(lost)} hours of ERCOT's file could not be placed in UTC and are not written (local hour starts {', '.join(lost)})")
        out.append(zl.rows(SPEC, piece, url, rec))
    return out, notes


SPEC = dict(
    iso="ercot", name=NAME, connector=CONNECTOR, source=SOURCE, geo="US-TX", days=10, ceiling=80000, stale_days=75,
    title="Hourly Load Data Archives, native load by weather zone",
    what="ERCOT, hourly native load by weather zone and ERCOT's total (Hourly Load Data Archives)",
    entry=dict(source=SOURCE, publisher="Electric Reliability Council of Texas (ERCOT)",
               report="Hourly Load Data Archives, native load by weather zone [terms: \"raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, "
                      "and analyses without maintaining such notices.\" (https://www.ercot.com/help/terms, read 6 October 2026)]",
               report_url=PAGE, document_list="https://www.ercot.com/files/docs/<date>/Native_Load_<YYYY>.zip", license="public", tables=[NAME]),
    notes=["value: ERCOT's native load for the weather zone and hour (MW over the hour). ERCOT gives the hour's end, Central; ts_utc is the hour's start. The repeated autumn hour is in the file twice, the second marked DST. "
           "ercot:system is ERCOT's own column ERCOT, never a sum made here. Older files' columns FAR_WEST, NORTH_C, SOUTHERN and SOUTH_C are FWEST, NCENT, SOUTH and SCENT; node keeps the file's name.",
           "Weather zones are not load zones: ercot:NORTH is the weather zone and does not join ercot:LZ_NORTH or ercot:HB_NORTH of the price tables. Approximately: COAST is mostly the Houston load zone; NORTH, NCENT and EAST "
           "mostly the North load zone; FWEST and WEST mostly the West; SOUTH and SCENT mostly the South. ERCOT publishes no table that turns one into the other, and none is applied here.",
           "ERCOT extends the current year's file month by month, so the newest hour can be several weeks old."],
    license="License: public. ERCOT's terms of use, item 5: \"raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, "
            "and analyses without maintaining such notices\" (https://www.ercot.com/help/terms, read 6 October 2026).",
)


if __name__ == "__main__":
    sys.exit(zl.run(SPEC, pull))
