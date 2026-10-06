#!/usr/bin/env python3
"""CAISO: demand cleared in the day-ahead market, by hour (session 136, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/caiso_dam_cleared_energy.csv, from
CAISO's OASIS report ENE_SLRS, "Market Schedules", for the day-ahead market and the ISO's totals:

    https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals
        &schedule=ALL&startdatetime=<YYYYMMDD>T00:00-0000&enddatetime=<YYYYMMDD>T00:00-0000&version=1&resultformat=6
    a zip of one CSV: INTERVALSTARTTIME_GMT, ..., SCHEDULE (Load, Generation, Import, Export), XML_DATA_ITEM, MW

    python warehouse/connectors/caiso_dam_cleared.py [--days N] [--ceiling ROWS] [--out-dir DIR]

WHAT IS WRITTEN. One row an hour for the entity caiso:system: the data item ISO_TOT_LOAD_MW, which CAISO's interface
specification describes as the ISO's total MW cleared as demand in the day-ahead market. The schedule request answers
generation, imports and exports too (four rows an hour); only the load row is kept. MW over an hour.

REQUESTS. OASIS refuses a request of 31 days ("Data can be requested for period of 31 days only": a whole August,
asked on 6 October 2026, was refused). The connector asks by half month (UTC: the 1st to the 16th, the 16th to the
next 1st), newest first: the halves of this month and the last from CAISO each run, an earlier half once (its raw
file is kept). Six seconds between requests, as the ERW's other OASIS connectors wait.

License: public, with credit. CAISO's terms of use (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026):
its materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices
and that you credit the California ISO when using such materials and/or information." Of its API: "Users are
prohibited from using the CAISO API in a manner that adversely impacts the performance of CAISO's systems".
"""

import io
import os
import sys
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dam_cleared as dc  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "caiso_dam_cleared_energy"
CONNECTOR = "caiso_dam_cleared"
SOURCE = "caiso:ENE_SLRS"
URL = ("https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals&schedule=ALL"
       "&startdatetime={}T00:00-0000&enddatetime={}T00:00-0000&version=1&resultformat=6")
PAGE = "https://oasis.caiso.com/mrioasis/logon.do"
ITEM = "ISO_TOT_LOAD_MW"
PAUSE = 6


def parse(content):
    """One month's zip as ({hour start UTC: MW of the load schedule}, rows read). A zip that holds OASIS's error XML
    for "no data" gives no hour; any other error is raised."""
    z = zipfile.ZipFile(io.BytesIO(content))
    names = z.namelist()
    csvs = [n for n in names if n.lower().endswith(".csv")]
    if not csvs:
        text = z.read(names[0]).decode("utf-8", "replace") if names else ""
        if "<m:ERR_CODE>1000</m:ERR_CODE>" in text or "No data returned" in text:
            return {}, 0
        raise RuntimeError(f"OASIS answered no CSV: {text[:300]}")
    df = pd.read_csv(io.BytesIO(z.read(csvs[0])), dtype=str, keep_default_na=False)
    need = {"INTERVALSTARTTIME_GMT", "INTERVALENDTIME_GMT", "MARKET_RUN_ID", "TAC_ZONE_NAME", "XML_DATA_ITEM", "MW"}
    if not need <= set(df.columns):
        raise RuntimeError(f"columns {list(df.columns)}, expected {sorted(need)}")
    x = df[(df["XML_DATA_ITEM"] == ITEM) & (df["MARKET_RUN_ID"] == "DAM") & (df["TAC_ZONE_NAME"] == "Caiso_Totals")]
    start, end = pd.to_datetime(x["INTERVALSTARTTIME_GMT"], utc=True), pd.to_datetime(x["INTERVALENDTIME_GMT"], utc=True)
    if not ((end - start) == pd.Timedelta(hours=1)).all():
        raise RuntimeError("an interval of the day-ahead schedule is not one hour")
    v = pd.to_numeric(x["MW"], errors="coerce")
    return {t: float(m) for t, m in zip(start, v) if pd.notna(m)}, len(df)


def pull(log, days, counter):
    today = pd.Timestamp.now(tz="UTC").normalize()
    first = (today - pd.Timedelta(days=days)).replace(day=1)
    halves = [h for m in pd.date_range(first, today, freq="MS") for h in ((m, m + pd.Timedelta(days=15)), (m + pd.Timedelta(days=15), m + pd.offsets.MonthBegin(1)))]
    out = []
    for m, stop in reversed(halves):
        if m > today + pd.Timedelta(days=1):
            continue
        end = min(stop, today + pd.Timedelta(days=2))                                 # the day-ahead market has run for tomorrow
        url = URL.format(m.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
        fresh = m >= (today.replace(day=1) - pd.offsets.MonthBegin(1))                # this month and the last: asked again each run
        content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=fresh, headers=dc.UA, pause=PAUSE)
        hours, n = parse(content)
        if not dc.reused(rec):
            counter.add(n, m.strftime("%Y-%m-%d"))
        log(f"  {m:%Y-%m-%d} to {end:%Y-%m-%d}: {n:,} rows, {len(hours)} hours of {ITEM}{' (raw file reused)' if dc.reused(rec) else ''}")
        out += [dc.row(SPEC, "caiso:system", ts, v, ITEM, url, rec["retrieved_at"]) for ts, v in sorted(hours.items())]
    seen, rows = set(), []
    for r in out:                                                                    # a month's end and the next month's start never overlap, but an hour is written once whatever CAISO answers
        if r["ts_utc"] not in seen:
            seen.add(r["ts_utc"]); rows.append(r)
    return rows


SPEC = dict(
    iso="caiso", name=NAME, connector=CONNECTOR, source=SOURCE, unit="MW", geo="US-CA", days=14, ceiling=20000, stale_days=5,
    what="CAISO, demand cleared in the day-ahead market by hour, the ISO's total (OASIS ENE_SLRS, Market Schedules, data item ISO_TOT_LOAD_MW)",
    entry=dict(source=SOURCE, publisher="California ISO (CAISO)", report="OASIS ENE_SLRS, Market Schedules, day-ahead market, ISO totals", report_url=PAGE,
               document_list=URL.format("<YYYYMMDD>", "<YYYYMMDD>"), license="public", tables=[NAME]),
    notes=["value: CAISO's ISO_TOT_LOAD_MW, the ISO's total MW cleared as demand in the day-ahead market, for the hour (MW over the hour). The request also answers generation, imports and exports; they are read and not written."],
    license="License: public, with credit to the California ISO. Its terms: materials \"may be used by you provided that you keep intact all copyright, trademark and other proprietary notices "
            "and that you credit the California ISO\" (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026).",
)


if __name__ == "__main__":
    sys.exit(dc.run(SPEC, pull))
