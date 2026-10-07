#!/usr/bin/env python3
"""CAISO: hourly actual load by TAC area (session 138, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/caiso_area_load_hourly.csv, from
CAISO's OASIS report SLD_FCST, "CAISO Demand Forecast", its actual run (the hourly integrated load, not a forecast):

    https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=<areas>
        &startdatetime=<YYYYMMDD>T00:00-0000&enddatetime=<YYYYMMDD>T00:00-0000&version=1&resultformat=6
    a zip of one CSV: INTERVALSTARTTIME_GMT, INTERVALENDTIME_GMT, ..., TAC_AREA_NAME, LABEL, XML_DATA_ITEM, POS, MW

    python warehouse/connectors/caiso_area_load.py [--days N] [--from YYYY-MM-DD] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row an area and hour: the data item SYS_FCST_ACT_MW ("Total Actual Hourly Integrated Load"),
MW over the hour, for the ISO's transmission access charge (TAC) areas, entity caiso:<TAC_AREA_NAME> with CAISO's own
names: PGE-TAC, SCE-TAC, SDGE-TAC, VEA-TAC, MWD-TAC. CAISO's own total, the area it names "CA ISO-TAC", is the
entity caiso:system (node "CA ISO-TAC"), the entity of caiso_dam_cleared_energy. Nothing is summed here. A TAC area
is not a pricing hub: the ERW's CAISO price tables hold the trading hubs NP15, SP15 and ZP26, which do not correspond
to TAC areas one for one (PGE-TAC lies in NP15 and ZP26, SCE-TAC and SDGE-TAC in SP15), so no join on entity is
offered between them.

THE REQUEST NAMES THE AREAS. Without tac_area_name the report answers 37 areas (6 October 2026), most of them the
balancing areas of the Western Energy Imbalance Market; those are not asked for, so no row is read that is not kept.

THE HOUR. CAISO gives each interval's start and end in GMT, so the 23-hour and the 25-hour day need no inference.
An interval that is not one hour is refused.

REQUESTS. OASIS refuses a request of 31 days (session 136). The connector asks in windows of 30 days counted from
1 January 2019 (UTC), newest first, so a window's address never changes and its raw file is kept: the windows that
end in the last 35 days are asked for each run, an earlier one once. Six seconds between requests, as the ERW's other
OASIS connectors wait.

License: public, with credit (the terms session 136 quoted for OASIS's day-ahead schedules; the same terms of use
cover this OASIS report). CAISO's terms of use (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026): its
materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices
and that you credit the California ISO when using such materials and/or information." Of its API: "Users are
prohibited from using the CAISO API in a manner that adversely impacts the performance of CAISO's systems".
"""

import io
import os
import sys
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import zone_load as zl  # noqa: E402

NAME = "caiso_area_load_hourly"
CONNECTOR = "caiso_area_load"
SOURCE = "caiso:SLD_FCST"
TOTAL = "CA ISO-TAC"
AREAS = [TOTAL, "PGE-TAC", "SCE-TAC", "SDGE-TAC", "VEA-TAC", "MWD-TAC"]
URL = ("https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=" + ",".join(a.replace(" ", "%20") for a in AREAS)
       + "&startdatetime={}T00:00-0000&enddatetime={}T00:00-0000&version=1&resultformat=6")
PAGE = "https://oasis.caiso.com/mrioasis/logon.do"
ITEM = "SYS_FCST_ACT_MW"
ANCHOR = pd.Timestamp("2019-01-01", tz="UTC")
SPAN = 30                                                # days a request: OASIS refuses 31
ROWS_A_WINDOW = SPAN * 24 * len(AREAS)
PAUSE = 6
NEED = ["INTERVALSTARTTIME_GMT", "INTERVALENDTIME_GMT", "MARKET_RUN_ID", "TAC_AREA_NAME", "XML_DATA_ITEM", "MW"]


def entity(area):
    return "caiso:system" if area == TOTAL else "caiso:" + area


def parse(content):
    """One window's zip as (rows of entity, node, ts, value; lines read). A zip that holds OASIS's error XML for "no
    data" gives no hour; any other error is raised."""
    z = zipfile.ZipFile(io.BytesIO(content))
    names = z.namelist()
    csvs = [n for n in names if n.lower().endswith(".csv")]
    if not csvs:
        text = z.read(names[0]).decode("utf-8", "replace") if names else ""
        if "<m:ERR_CODE>1000</m:ERR_CODE>" in text or "No data returned" in text:
            return pd.DataFrame(columns=zl.PIECE), 0
        raise RuntimeError(f"OASIS answered no CSV: {text[:300]}")
    df = pd.read_csv(io.BytesIO(z.read(csvs[0])), dtype=str, keep_default_na=False)
    if not set(NEED) <= set(df.columns):
        raise RuntimeError(f"columns {list(df.columns)}, expected {NEED}")
    x = df[(df["XML_DATA_ITEM"] == ITEM) & (df["MARKET_RUN_ID"] == "ACTUAL") & df["TAC_AREA_NAME"].isin(AREAS)]
    start, end = pd.to_datetime(x["INTERVALSTARTTIME_GMT"], utc=True), pd.to_datetime(x["INTERVALENDTIME_GMT"], utc=True)
    if not ((end - start) == pd.Timedelta(hours=1)).all():
        raise RuntimeError("an interval of the actual load is not one hour")
    v = pd.to_numeric(x["MW"], errors="coerce")
    piece = pd.DataFrame({"entity": x["TAC_AREA_NAME"].map(entity).values, "node": x["TAC_AREA_NAME"].values, "ts": start.values, "value": v.values})
    piece["ts"] = pd.to_datetime(piece["ts"], utc=True)
    return piece[piece["value"].notna()].sort_values(["entity", "ts"]).reset_index(drop=True), len(df)


def windows(first, now):
    """The 30-day windows, counted from the anchor, that reach from `first` to `now` (UTC days), newest first."""
    k0 = max(0, (first - ANCHOR).days // SPAN)
    k1 = (now - ANCHOR).days // SPAN
    return [(ANCHOR + pd.Timedelta(days=SPAN * k), ANCHOR + pd.Timedelta(days=SPAN * (k + 1))) for k in range(k1, k0 - 1, -1)]


def pull(log, first, counter):
    today = pd.Timestamp.now(tz="UTC").normalize()
    out, notes, differ = [], [], 0
    for a, b in windows(first.tz_localize("UTC"), today):
        if not counter.room(ROWS_A_WINDOW):
            log(f"  stopping before {a:%Y-%m-%d}: another window would pass this run's ceiling ({counter.read:,} rows read)")
            notes.append(f"stopped before the window of {a:%Y-%m-%d}: another window would pass the ceiling")
            break
        end = min(b, today + pd.Timedelta(days=1))
        url = URL.format(a.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
        fresh = b > today - pd.Timedelta(days=35)                      # the newest windows: asked again each run
        content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=fresh, headers=zl.UA, pause=PAUSE)
        piece, n = parse(content)
        if not zl.reused(rec):
            counter.add(n, a.strftime("%Y-%m-%d"))
        piece, d = zl.once(piece, log, f"{a:%Y-%m-%d}")
        differ += d
        log(f"  {a:%Y-%m-%d} to {end:%Y-%m-%d}: {n:,} lines, {len(piece):,} area hours{' (raw file reused)' if zl.reused(rec) else ''}")
        out.append(zl.rows(SPEC, piece, url, rec))
    if differ:
        notes.append(f"{differ:,} area hours CAISO gives twice with different loads are not written")
    return out, notes


SPEC = dict(
    iso="caiso", name=NAME, connector=CONNECTOR, source=SOURCE, geo="US-CA", days=10, ceiling=12000, stale_days=5,
    title="OASIS SLD_FCST, CAISO Demand Forecast, the actual run (Total Actual Hourly Integrated Load), by TAC area",
    what="CAISO, hourly actual load by TAC area and the ISO's total (OASIS SLD_FCST, the actual run, data item SYS_FCST_ACT_MW)",
    entry=dict(source=SOURCE, publisher="California ISO (CAISO)",
               report="OASIS SLD_FCST, CAISO Demand Forecast, the actual run (Total Actual Hourly Integrated Load), by TAC area [terms: materials \"may be used by you provided that you keep intact all copyright, "
                      "trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information.\" (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026)]",
               report_url=PAGE, document_list=URL.format("<YYYYMMDD>", "<YYYYMMDD>"), license="public", tables=[NAME]),
    notes=["value: CAISO's SYS_FCST_ACT_MW, Total Actual Hourly Integrated Load, for the area and hour (MW over the hour); the interval's start and end are CAISO's, in GMT. "
           "Entities are CAISO's TAC areas under its own names; caiso:system is the area CAISO names CA ISO-TAC, its own total. A TAC area is not a trading hub (NP15, SP15, ZP26): no join with the price tables is offered. "
           "The request names the six areas; the report's other areas (Western Energy Imbalance Market balancing areas) are not asked for."],
    license="License: public, with credit to the California ISO. Its terms: materials \"may be used by you provided that you keep intact all copyright, trademark and other proprietary notices "
            "and that you credit the California ISO\" (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026).",
)


if __name__ == "__main__":
    sys.exit(zl.run(SPEC, pull))
