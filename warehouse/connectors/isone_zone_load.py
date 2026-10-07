#!/usr/bin/env python3
"""ISO-NE: hourly real-time demand by load zone (session 138, approved pull). INTERNAL.

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/isone_zone_load_hourly.csv, from ISO
New England's "Zonal Information" page, the yearly workbook "SMD Hourly Data":

    https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/zone-info                      the page
    https://www.iso-ne.com/isoexpress/web/reports/download/docWidgetGetMore?start=<N>&treenode=zone-info   its file list (JSON)
    https://www.iso-ne.com/static-assets/documents/<folder>/<YYYY>_smd_hourly.xlsx                      a year
    a sheet for the system (ISO NE CA) and one a load zone (ME, NH, VT, CT, RI, SEMA, WCMA, NEMA):
    Date, Hr_End, DA_Demand, RT_Demand, DA_LMP, ..., Dry_Bulb, Dew_Point

    python warehouse/connectors/isone_zone_load.py [--days N] [--from YYYY-MM-DD] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row a load zone and hour: the column RT_Demand, ISO-NE's real-time demand for the hour (MWh for
the hour, which is MW over the hour). Entities carry the names the ERW's ISO-NE price tables use for the same eight
load zones, so load and price join on entity; node keeps the sheet's name:

    ME .Z.MAINE, NH .Z.NEWHAMPSHIRE, VT .Z.VERMONT, CT .Z.CONNECTICUT, RI .Z.RHODEISLAND, SEMA .Z.SEMASS,
    WCMA .Z.WCMASS, NEMA .Z.NEMASSBOST, and the sheet ISO NE CA (the control area, ISO-NE's own total) isone:system

The total is ISO-NE's own sheet, never a sum made here. The workbook's other columns (day-ahead demand, prices,
temperatures) are read and not written.

THE HOUR. Hr_End is the hour ending, 1 to 24, Eastern; ts_utc is the hour's start. "02X" is the second 01:00 to
02:00 hour of the autumn clock change (25 lines that day). The spring day has 23 lines, labelled by the clock at the
hour's end: 01, then 03 (the hour that began at 01:00 standard time and ended at 03:00 daylight time), so that line
is placed by its end (zone_load.to_utc). The repeated hour held once only could be either of two hours and would not
be written; it is counted in the log and the header. Nothing is guessed.

HOW OPEN IT IS. Session 136 found ISO Express's CSV addresses (/transform/csv/...) answer HTTP 403 to a plain
request. These yearly workbooks are different: on 6 October 2026 the page, its file list and each workbook answered
a plain request (HTTP 200), with no cookie, no account and no CAPTCHA. The page does put a CAPTCHA on its own
"Download Selected Files" form, which packs several files into one zip: that form is not used and no CAPTCHA is
answered or avoided; each workbook is asked for at the address the page's own list gives. So the files are openly
reachable, and the terms are still what they were: see the license. For that reason the history asked for here is
modest (the pull of session 138: 2025 and 2026), and the table is internal.

REQUESTS. The file list, then one workbook a year, newest first. A year's workbook is asked for again only when the
list's publish date for it is later than the kept copy.

License: INTERNAL (the ERW's standing reading for ISO-NE, sessions 65, 85 and 136). ISO-NE's legal notice
(https://www.iso-ne.com/legal-privacy, read 6 October 2026 by session 136): "You are also hereby put on notice that
the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use
may violate copyright, trademark, and other laws." The table is not published; it is in no public dataset and no
download.
"""

import io
import json
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import zone_load as zl  # noqa: E402

NAME = "isone_zone_load_hourly"
CONNECTOR = "isone_zone_load"
SOURCE = "isone:smd_hourly"
PAGE = "https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/zone-info"
LIST = "https://www.iso-ne.com/isoexpress/web/reports/download/docWidgetGetMore?start={}&treenode=zone-info"
HOST = "https://www.iso-ne.com"
FILE = re.compile(r"^/static-assets/documents/[A-Za-z0-9_/]+/(\d{4})_smd_hourly\.xlsx$")
TZ = "America/New_York"
SHEETS = {"ISO NE CA": "isone:system", "ME": "isone:.Z.MAINE", "NH": "isone:.Z.NEWHAMPSHIRE", "VT": "isone:.Z.VERMONT", "CT": "isone:.Z.CONNECTICUT",
          "RI": "isone:.Z.RHODEISLAND", "SEMA": "isone:.Z.SEMASS", "WCMA": "isone:.Z.WCMASS", "NEMA": "isone:.Z.NEMASSBOST"}
COLUMN = "RT_Demand"
ROWS_A_YEAR = 8784 * len(SHEETS)
LIST_STEP, LIST_PAGES = 40, 3
PAUSE = 3


def listed(texts):
    """{year: (the workbook's address, the list's publish date as UTC)} from the pages of ISO-NE's file list."""
    out = {}
    for text in texts:
        for d in json.loads(text).get("data", []):
            m = FILE.match(str(d.get("path", "")))
            if m:
                stamp = re.sub(r"\s+E[SD]T$", "", str(d.get("publishDate", "")).strip())
                when = pd.to_datetime(stamp, format="%m/%d/%Y %I:%M %p", errors="coerce")
                when = when.tz_localize(TZ, ambiguous=True, nonexistent="shift_forward").tz_convert("UTC") if pd.notna(when) else None
                out[int(m.group(1))] = (HOST + d["path"], when)
    return out


def parse_sheet(df, sheet):
    """One zone's sheet as (rows of entity, node, ts, value; lines read; hours not placed)."""
    df = df.rename(columns={c: str(c).strip() for c in df.columns})
    need = ["Date", "Hr_End", COLUMN]
    if not set(need) <= set(df.columns):
        raise RuntimeError(f"sheet {sheet!r} has columns {list(df.columns)[:8]}, expected {need}")
    df = df[df["Date"].notna()]
    he = df["Hr_End"].astype(str).str.strip().str.upper().str.replace(r"\.0$", "", regex=True)
    second = he.str.endswith("X").values
    hour = pd.to_numeric(he.str.rstrip("X"), errors="coerce")
    if hour.isna().any() or not hour.between(1, 24).all():
        raise RuntimeError(f"sheet {sheet!r}: hour ending {sorted(set(he[hour.isna() | ~hour.between(1, 24)]))[:5]} is not 1 to 24")
    local = pd.to_datetime(df["Date"]).dt.normalize() + pd.to_timedelta(hour.astype(int) - 1, unit="h")
    ts, _ = zl.to_utc(local, TZ, second=second)
    lost = [str(t) for t in local[ts.isna().values]]
    piece = pd.DataFrame({"entity": SHEETS[sheet], "node": sheet, "ts": ts.values, "value": pd.to_numeric(df[COLUMN], errors="coerce").values})
    piece["ts"] = pd.to_datetime(piece["ts"], utc=True)
    return piece[piece["ts"].notna()].reset_index(drop=True), len(df), lost


def parse(content):
    """A year's workbook as (rows; lines read in the nine sheets; hours not placed, by sheet)."""
    book = pd.read_excel(io.BytesIO(content), sheet_name=None, header=0)
    names = {str(k).strip().upper(): k for k in book}
    missing = [s for s in SHEETS if s not in names]
    if missing:
        raise RuntimeError(f"the workbook's sheets are {list(book)}, expected {list(SHEETS)}")
    pieces, n, lost = [], 0, {}
    for sheet in SHEETS:
        p, k, gone = parse_sheet(book[names[sheet]], sheet)
        pieces.append(p)
        n += k
        if gone:
            lost[sheet] = gone
    return pd.concat(pieces, ignore_index=True), n, lost


def pull(log, first, counter):
    today = pd.Timestamp.now(tz=TZ).tz_localize(None)
    texts = []
    for i in range(LIST_PAGES):
        content, _ = ip.fetch_raw(CONNECTOR, LIST.format(i * LIST_STEP), log, fresh=True, headers=zl.UA, pause=PAUSE)
        texts.append(content.decode("utf-8", "replace"))
        if len(json.loads(texts[-1]).get("data", [])) < LIST_STEP:
            break
    files = listed(texts)
    log(f"  ISO-NE's list holds SMD hourly workbooks for {sorted(files)}")
    out, notes = [], []
    for year in range(today.year, first.year - 1, -1):
        if year not in files:
            log(f"  {year}: ISO-NE's list holds no SMD hourly workbook; the year is not written")
            notes.append(f"{year}: no SMD hourly workbook on ISO-NE's list")
            continue
        url, published = files[year]
        kept = ip.raw_cached(CONNECTOR, url)
        fresh = kept is not None and published is not None and published > pd.Timestamp(kept[1]["retrieved_at"])
        if (fresh or kept is None) and not counter.room(ROWS_A_YEAR):
            log(f"  stopping before {year}: another year's workbook would pass this run's ceiling ({counter.read:,} rows read)")
            notes.append(f"stopped before {year}: another year would pass the ceiling")
            break
        content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=fresh, headers=zl.UA, pause=PAUSE)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} did not answer a workbook (first bytes {content[:40]!r})")
        piece, n, lost = parse(content)
        if not zl.reused(rec):
            counter.add(n, str(year))
        log(f"  {year}: {n:,} lines in {len(SHEETS)} sheets, {len(piece):,} zone hours placed; published {published}{' (raw file reused)' if zl.reused(rec) else ''}")
        for sheet, gone in lost.items():
            log(f"  {year}, sheet {sheet}: {len(gone)} hours not placed in UTC and not written (local hour starts): {', '.join(gone)}")
        if lost:
            every = sorted({g for gone in lost.values() for g in gone})
            notes.append(f"{year}: {sum(len(g) for g in lost.values())} zone hours of ISO-NE's workbook could not be placed in UTC and are not written (local hour starts {', '.join(every)})")
        out.append(zl.rows(SPEC, piece, url, rec))
    return out, notes


SPEC = dict(
    iso="isone", name=NAME, connector=CONNECTOR, source=SOURCE, geo="US-CT,US-MA,US-ME,US-NH,US-RI,US-VT", days=10, ceiling=80000, stale_days=100,
    title="Zonal Information, SMD Hourly Data (yearly workbook), real-time demand by load zone",
    what="ISO-NE, hourly real-time demand by load zone and the control area's total (Zonal Information, SMD Hourly Data, column RT_Demand). INTERNAL",
    entry=dict(source=SOURCE, publisher="ISO New England (ISO-NE)",
               report="Zonal Information, SMD Hourly Data (yearly workbook), real-time demand by load zone [terms: \"Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws.\" "
                      "(https://www.iso-ne.com/legal-privacy, read 6 October 2026); held internal]",
               report_url=PAGE, document_list=HOST + "/static-assets/documents/<folder>/<YYYY>_smd_hourly.xlsx", license="internal", tables=[NAME]),
    notes=["value: ISO-NE's RT_Demand, real-time demand for the load zone and hour (MWh for the hour, which is MW over the hour). Hr_End is the hour ending, Eastern; ts_utc is the hour's start; 02X is the repeated autumn hour; the spring day's 23 lines go 01, 03 (the hour is labelled by its end) and that line is placed by its end. "
           "Entities carry the names of isone_dam_zone_prices and isone_rtm_zone_prices (.Z.MAINE and so on); node keeps the sheet's name (ME and so on). isone:system is ISO-NE's own sheet ISO NE CA, never a sum made here.",
           "The workbooks answer a plain request (no cookie, no account); the page's own CAPTCHA guards its several-files download form, which is not used. ISO-NE extends the current year's workbook about once a month, "
           "so the newest hour can be many weeks old."],
    license="License: internal. ISO-NE's legal notice: \"Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws\" "
            "(https://www.iso-ne.com/legal-privacy, read 6 October 2026). Not published, in no public dataset and no download.",
)


if __name__ == "__main__":
    sys.exit(zl.run(SPEC, pull))
