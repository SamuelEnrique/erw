#!/usr/bin/env python3
"""CAISO day-ahead ancillary service clearing prices, hourly, the system regions, from 2024-09-01.

Energy Research Warehouse (ERW) connector, session 65 (docs/methods/capacity_and_ancillary.md). Writes one series
table, warehouse/output/caiso_as_prices.csv:

    entity    caiso:<region as OASIS names it>    caiso:AS_CAISO (the CAISO system), caiso:AS_CAISO_EXP (expanded:
                                                  the system with the interties)
    variable  as_price_dam_ru, as_price_dam_rd, as_price_dam_sr, as_price_dam_nr
              (Regulation Up, Regulation Down, Spinning Reserve, Non-Spinning Reserve; OASIS types RU, RD, SR, NR)
    unit      USD/MW-hour   (US dollars per MW of capacity held for one hour)
    freq      PT1H; ts_utc is the start of the trading hour, UTC (OASIS INTERVALSTARTTIME_GMT)
    market    caiso_dam
    node      the region

    python warehouse/connectors/caiso_as_prices.py                      # 2024-09-01 to today (Pacific)
    python warehouse/connectors/caiso_as_prices.py --out-dir C:/scratch # a trial run: nothing in warehouse/output
    python warehouse/connectors/caiso_as_prices.py --offline            # from the raw files only, no request

Source: CAISO OASIS report PRC_AS (AS Clearing Prices), market run DAM, version 12, through the SingleZip API. OASIS
answers one operating day per request whatever range is asked (checked in session 65), so the pull is one request
per Pacific operating day, 6 seconds apart, in one process. It resumes by itself: each day's zip is kept in
warehouse/raw/caiso_as_prices/ and a day already there is not requested again (iso_prices.fetch_raw), so a run that
is throttled or interrupted is simply started again.

Kept: the two system regions only, not the sub-regions (AS_NP26, AS_SP26 and their expanded forms), by the session 65
ruling. Left out: the regulation mileage prices (RMU, RMD), which are per MW of movement, not of capacity, and the
hour-ahead (HASP) and real-time runs.

Never fill. gridstatus's reader of this report fills missing cells with zero, so it is not used. A (region,
service, Pacific day) is written only when every hour of that day is there (24, or 23 and 25 at the clock changes);
a day short of that is left out, logged, and reported as a gap in the run's status. A day OASIS answers with "no
data" is a gap too.

Ceiling: 500,000 rows (session 65 ruling). If the two regions would pass it, only the expanded system region is
kept; if that would still pass it, nothing is written.

License: public. CAISO's terms of use (https://www.caiso.com/privacy-terms-of-use): materials and information on
the website "may be used by you provided that you keep intact all copyright, trademark and other proprietary
notices and that you credit the California ISO".
"""

import argparse
import datetime as dt
import io
import os
import sys
import time
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "caiso_as_prices"
CONNECTOR = "caiso_as_prices"
START = "2024-09-01"
CEILING = 500_000
TZ = "America/Los_Angeles"
REGIONS = ["AS_CAISO", "AS_CAISO_EXP"]
TYPES = {"RU": "as_price_dam_ru", "RD": "as_price_dam_rd", "SR": "as_price_dam_sr", "NR": "as_price_dam_nr"}
MILEAGE = {"RMU", "RMD"}
SOURCE = "caiso:PRC_AS"
REPORT = "OASIS AS Clearing Prices (PRC_AS), day-ahead market (DAM)"
PAGE = "https://oasis.caiso.com/mrioasis/logon.do"
API = ("https://oasis.caiso.com/oasisapi/SingleZip?queryname=PRC_AS&market_run_id=DAM&anc_type=ALL&anc_region=ALL"
       "&startdatetime={}&enddatetime={}&version=12&resultformat=6")
PAUSE = 6  # seconds between requests; OASIS throttles
COLS = ["INTERVALSTARTTIME_GMT", "OPR_DT", "ANC_TYPE", "ANC_REGION", "MARKET_RUN_ID", "XML_DATA_ITEM", "MW"]


class NoData(ip.SourceGap):
    """OASIS answered that it holds nothing for the day."""


class Throttled(RuntimeError):
    """OASIS answered an error that is not 'no data' (a throttle, a timeout): try again later."""


def url_for(day):
    """The request for one Pacific operating day (a date)."""
    a = pd.Timestamp(day).tz_localize(TZ)
    b = (a + pd.DateOffset(days=1))
    f = lambda t: t.tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000")  # noqa: E731
    return API.format(f(a), f(b))


def hours_in(day):
    a = pd.Timestamp(day).tz_localize(TZ)
    return int(((a + pd.DateOffset(days=1)) - a) / pd.Timedelta(hours=1))


def parse(raw, day):
    """One day's zip: rows (region, type, ts, value) for the system regions and the four capacity services.
    Raises NoData or Throttled when the zip holds OASIS's error document instead of the report."""
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise Throttled(f"{day}: the answer is not a zip ({raw[:80]!r})")
    names = z.namelist()
    csvs = [n for n in names if n.lower().endswith(".csv")]
    if len(csvs) != 1:
        text = z.read(names[0]).decode("utf-8", "replace") if names else ""
        if "No data returned" in text:
            raise NoData(f"{day}: OASIS: no data returned")
        raise Throttled(f"{day}: OASIS answered {names}: {' '.join(text.split())[:200]}")
    x = pd.read_csv(z.open(csvs[0]), dtype=str, keep_default_na=False)
    missing = [c for c in COLS if c not in x.columns]
    if missing:
        raise RuntimeError(f"{day}: PRC_AS file lacks {missing}: layout changed")
    if set(x["MARKET_RUN_ID"]) != {"DAM"}:
        raise RuntimeError(f"{day}: market runs {set(x['MARKET_RUN_ID'])}, expected DAM only")
    unknown = set(x["ANC_TYPE"]) - set(TYPES) - MILEAGE
    if unknown:
        raise RuntimeError(f"{day}: unknown service types {sorted(unknown)}")
    x = x[x["ANC_REGION"].isin(REGIONS) & x["ANC_TYPE"].isin(TYPES)]
    if not x["XML_DATA_ITEM"].str.endswith("_CLR_PRC").all():
        raise RuntimeError(f"{day}: data items {set(x['XML_DATA_ITEM'])} are not all clearing prices")
    if set(x["OPR_DT"]) - {str(pd.Timestamp(day).date())}:
        raise RuntimeError(f"{day}: the file holds operating days {sorted(set(x['OPR_DT']))}")
    v = x["MW"].str.strip()
    x = x[v != ""]  # an empty cell is not a price: no row
    x = x.reset_index(drop=True)
    return pd.DataFrame({"region": x["ANC_REGION"], "type": x["ANC_TYPE"],
                         "ts": pd.to_datetime(x["INTERVALSTARTTIME_GMT"], utc=True),
                         "value": pd.to_numeric(x["MW"], errors="raise"), "day": str(pd.Timestamp(day).date())})


def complete(rows, day, log):
    """Keep the (region, service) series of the day that hold every hour exactly once; name the others."""
    want = hours_in(day)
    keep, gaps = [], []
    if rows.duplicated(["region", "type", "ts"]).any():
        raise RuntimeError(f"{day}: rows repeat a (region, service, hour)")
    for r in REGIONS:
        for t in TYPES:
            g = rows[(rows["region"] == r) & (rows["type"] == t)]
            if len(g) == want:
                keep.append(g)
            else:
                gaps.append(f"{r} {t} {pd.Timestamp(day).date()}: {len(g)} of {want} hours")
    for g in gaps:
        log(f"  gap, left out: {g}")
    return (pd.concat(keep, ignore_index=True) if keep else rows.iloc[0:0]), gaps


def fetch_day(day, log, offline):
    """One day's rows with provenance. A cached answer that turns out to be an error document is fetched again."""
    url = url_for(day)
    last = None
    for attempt in range(5):
        try:
            raw, rec = ip.fetch_raw(CONNECTOR, url, log, offline=offline, fresh=attempt > 0, pause=0)
        except ip.SourceGap:
            raise
        except RuntimeError as exc:  # HTTP 429 or a timeout, after fetch_raw's own retries
            if offline:
                raise
            last = exc
            wait = 60 * (attempt + 1)
            log(f"    {exc}; waiting {wait} s")
            time.sleep(wait)
            continue
        try:
            rows = parse(raw, day)
        except Throttled as exc:
            last = exc
            if offline:
                raise
            wait = 30 * (attempt + 1)
            log(f"    {exc}; waiting {wait} s")
            time.sleep(wait)
            continue
        finally:
            if not rec["cached"]:
                time.sleep(PAUSE)
        rows["source_url"], rows["retrieved_at"] = rec["url"], rec["retrieved_at"]
        return rows
    raise RuntimeError(f"{day}: OASIS did not answer the report after 5 tries: {last}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: CAISO day-ahead ancillary service clearing prices")
    ap.add_argument("--out-dir", help="write the table, log, registry and status under this directory instead of "
                    "the repository (raw files stay in warehouse/raw)")
    ap.add_argument("--offline", action="store_true", help="read the raw files only; make no request")
    ap.add_argument("--start", default=START)
    ap.add_argument("--until", help="first day not pulled (default: tomorrow, Pacific)")
    a = ap.parse_args(argv)
    raw_dir = ip.RAW_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
        ip.RAW_DIR = raw_dir  # source documents are kept once, in warehouse/raw, whatever the output directory
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        until = pd.Timestamp(a.until) if a.until else pd.Timestamp.now(tz=TZ).tz_localize(None).normalize() + pd.Timedelta(days=1)
        days = pd.date_range(a.start, until - pd.Timedelta(days=1), freq="D")
        log(f"ERW {CONNECTOR} run {run_id}: {len(days)} operating days, {days[0].date()} to {days[-1].date()}")
        frames, gaps = [], []
        for i, day in enumerate(days):
            try:
                rows = fetch_day(day, log, a.offline)
            except NoData as exc:
                gaps.append(f"{day.date()}: no data at the source")
                log(f"  gap: {exc}")
                continue
            rows, g = complete(rows, day, log)
            gaps += g
            frames.append(rows)
            if i % 50 == 0:
                print(f"{CONNECTOR}: {day.date()} ({i + 1} of {len(days)})", flush=True)
        rows = pd.concat(frames, ignore_index=True)
        regions = list(REGIONS)
        if len(rows) > CEILING:
            log(f"{len(rows)} rows would pass the ceiling of {CEILING}: keeping the expanded system region only")
            regions = ["AS_CAISO_EXP"]
            rows = rows[rows["region"].isin(regions)]
        if len(rows) > CEILING:
            raise RuntimeError(f"{len(rows)} rows would pass the ceiling of {CEILING}; nothing written")
        s = pd.DataFrame({
            "entity": "caiso:" + rows["region"], "variable": rows["type"].map(TYPES),
            "ts_utc": rows["ts"].map(ip.utc_iso),
            "value": rows["value"], "unit": "USD/MW-hour", "freq": "PT1H", "geo": "US-CA", "market": "caiso_dam",
            "node": rows["region"], "source": SOURCE, "source_url": rows["source_url"],
            "retrieved_at": rows["retrieved_at"], "vintage": "",
        }).sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)[ip.SERIES_COLS]
        header = [
            "Energy Research Warehouse (ERW): CAISO day-ahead ancillary service clearing prices, hourly, the "
            "system regions",
            "Shape: series (docs/datastandard.md v0). Unit USD/MW-hour: US dollars per MW of capacity held for one "
            "hour. ts_utc is the start of the trading hour, UTC.",
            f"Regions: {', '.join(regions)} (AS_CAISO the CAISO system, AS_CAISO_EXP the system with the "
            "interties); the sub-regions are not pulled. Variables: as_price_dam_ru Regulation Up, as_price_dam_rd "
            "Regulation Down, as_price_dam_sr Spinning Reserve, as_price_dam_nr Non-Spinning Reserve. Mileage "
            "prices (RMU, RMD) are left out.",
            f"Window: Pacific operating days {days[0].date()} to {days[-1].date()}. Never filled: a (region, "
            f"service, day) is written only when every hour of the day is there; {len(gaps)} are left out of this "
            "run" + (": " + "; ".join(gaps[:20]) if gaps else "") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/caiso_as_prices.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; each run's manifest.csv lists each file and URL)",
            f"Source: {SOURCE} CAISO, {REPORT}, {PAGE}",
            "License: public. CAISO terms of use: materials may be used provided the notices are kept intact and "
            "the California ISO is credited.",
            "Method: docs/methods/capacity_and_ancillary.md",
        ]
        ip.write_csv(s, NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher=ip.ISO_PUBLISHERS["caiso"], report=REPORT,
                                report_url=PAGE, document_list="https://oasis.caiso.com/oasisapi/SingleZip",
                                tables=[NAME])])
        results.append(dict(table=NAME, market="DAM", status="ok", detail=f"{len(s)} rows of {CEILING}"))
        for g in gaps:
            results.append(dict(table=NAME, market="DAM", status="gap", detail=g))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="DAM", status="failed", detail=last[:300]))
    ip.write_status(CONNECTOR, run_id, results)
    failures = sum(r["status"] == "failed" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"{CONNECTOR} run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
