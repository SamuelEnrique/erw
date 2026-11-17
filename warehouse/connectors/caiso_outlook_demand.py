#!/usr/bin/env python3
"""CAISO Today's Outlook: demand, every 5 minutes, on the days asked (session 7052, chain 370, done-line request 201).

Energy Research Warehouse (ERW) connector. The warehouse held Today's Outlook's supply by fuel by the hour
(`caiso_fuel_supply`, `caiso_fuel_supply_history`) and its batteries every 5 minutes (`caiso_battery_storage`), and no
5-minute demand, so the minutes after a Flex Alert (a text alert of 6 September 2022, for one) could not be read. This
connector reads CAISO's public Today's Outlook history file for each day asked,

    https://www.caiso.com/outlook/history/YYYYMMDD/demand.csv

and writes one series table, caiso_outlook_demand:

    entity    caiso:ISO
    variable  demand_mw                      CAISO's "Current demand" column
              demand_forecast_day_ahead_mw   its "Day ahead forecast" column
              demand_forecast_hour_ahead_mw  its "Hour ahead forecast" column
              demand_response_marked         1 in an interval CAISO's "Demand response" column marks (no row where it is blank)
    freq      PT5M; ts_utc is the interval start (CAISO's "Time", Pacific wall-clock time, converted)

The days: by default the 39 Flex Alert days of 2018 to 2024 that docs/methods/flex_alert_scorecard.md names (its
"The result": 39 days from 2018-07-24 to 2024-07-24; the scorecard leaves 2021-07-12 out for incomplete data, and it is
asked here all the same). --days asks other Pacific days (YYYY-MM-DD, comma separated).

    python warehouse/connectors/caiso_outlook_demand.py                    # the 39 alert days
    python warehouse/connectors/caiso_outlook_demand.py --days 2022-09-06  # named days

Completeness: a day is written only if the three MW columns hold every 5-minute interval of the Pacific day (288, or
276 and 300 on the clock-change days). The file ends with the next day's 00:00 row, which is dropped (it is the next
day's first interval). A day short of an interval is logged and skipped; nothing is filled. Each run merges into the
table (new intervals added, the same interval replaced). One request a day asked, two seconds apart. CAISO's robots
file (read 17 November 2026) disallows /resources/* only. License: public, with credit to the California ISO (its
terms of use, https://www.caiso.com/privacy-terms-of-use: materials "may be used by you provided that you keep intact
all copyright, trademark and other proprietary notices and that you credit the California ISO").
"""

import argparse
import datetime as dt
import io
import os
import sys

import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "caiso_outlook_demand"
CONNECTOR = "caiso_outlook_demand"
URL = "https://www.caiso.com/outlook/history/{day}/demand.csv"
PAGE = "https://www.caiso.com/todays-outlook"
SOURCE = "caiso:todays_outlook_demand"
TZ = "America/Los_Angeles"
COLS = {"Current demand": "demand_mw", "Day ahead forecast": "demand_forecast_day_ahead_mw", "Hour ahead forecast": "demand_forecast_hour_ahead_mw"}
FLAG = ("Demand response", "demand_response_marked")
PAUSE = 2.0
# docs/methods/flex_alert_scorecard.md, "The result": the 39 alert days of 2018 to 2024 (2021-07-12 is the one the
# scorecard leaves out for incomplete data)
ALERT_DAYS = ["2018-07-24", "2018-07-25", "2019-06-11", "2019-07-28", "2020-08-14", "2020-08-15", "2020-08-16", "2020-08-17",
              "2020-08-18", "2020-08-19", "2020-09-05", "2020-09-06", "2020-09-07", "2020-10-01", "2020-10-15", "2021-06-17",
              "2021-06-18", "2021-07-09", "2021-07-10", "2021-07-12", "2021-07-28", "2021-07-29", "2021-09-08", "2021-09-09",
              "2022-08-17", "2022-08-31", "2022-09-01", "2022-09-02", "2022-09-03", "2022-09-04", "2022-09-05", "2022-09-06",
              "2022-09-07", "2022-09-08", "2022-09-09", "2023-07-20", "2023-07-25", "2023-07-26", "2024-07-24"]


def parse(day, text, url, got):
    """One Pacific day of CAISO's demand file as rows, or (None, why)."""
    d = pd.read_csv(io.StringIO(text))
    if "Time" not in d.columns or not set(COLS) <= set(d.columns):
        return None, f"{day}: columns {list(d.columns)}"
    d = d.dropna(subset=list(COLS), how="all").reset_index(drop=True)
    times = d["Time"].astype(str).str.slice(0, 5)
    if len(d) > 1 and times.iloc[-1] == "00:00" and times.iloc[0] == "00:00":
        d = d.iloc[:-1].reset_index(drop=True)   # the next day's first interval, printed at the end of the file
        times = times.iloc[:-1]
    start = pd.Timestamp(day).tz_localize(TZ)
    end = pd.Timestamp(day + dt.timedelta(days=1)).tz_localize(TZ)
    expected = int((end - start) / pd.Timedelta(minutes=5))
    t = pd.to_datetime(times, format="%H:%M", errors="coerce")
    try:
        ts = (pd.Timestamp(day) + (t - t.dt.normalize())).dt.tz_localize(TZ, ambiguous="infer")
    except Exception as exc:
        return None, f"{day}: the clock does not convert ({type(exc).__name__})"
    d = d.assign(ts=ts).dropna(subset=list(COLS) + ["ts"])
    if len(d) != expected or d["ts"].duplicated().any():
        return None, f"{day}: {len(d)} of {expected} intervals"
    long = d.melt(id_vars=["ts"], value_vars=list(COLS), var_name="col", value_name="value")
    parts = [pd.DataFrame({"variable": long["col"].map(COLS), "ts": long["ts"], "value": long["value"].astype(float), "unit": "MW"})]
    if FLAG[0] in d.columns:
        f = d[pd.to_numeric(d[FLAG[0]], errors="coerce") == 1]
        if len(f):
            parts.append(pd.DataFrame({"variable": FLAG[1], "ts": f["ts"], "value": 1.0, "unit": "count"}))
    x = pd.concat(parts, ignore_index=True)
    out = pd.DataFrame({
        "entity": "caiso:ISO", "variable": x["variable"], "ts_utc": x["ts"].dt.tz_convert("UTC").dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": x["value"], "unit": x["unit"], "freq": "PT5M", "geo": "US-CA", "market": "", "node": "",
        "source": SOURCE, "source_url": url, "retrieved_at": got, "vintage": ""})
    return out, None


def day_rows(day, log):
    url = URL.format(day=day.strftime("%Y%m%d"))
    content, rec = ip.fetch_raw(CONNECTOR, url, log, headers={"User-Agent": "Mozilla/5.0 (ERW research)"}, pause=PAUSE)
    text = content.decode("utf-8-sig") if isinstance(content, (bytes, bytearray)) else str(content)
    return parse(day, text, url, rec["retrieved_at"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="CAISO Today's Outlook demand, 5-minute, on the days asked")
    ap.add_argument("--days", help="Pacific days, YYYY-MM-DD, comma separated (default: the 39 Flex Alert days of 2018 to 2024)")
    args = ap.parse_args(argv)
    if ip.paused("caiso"):
        print(f"caiso_outlook_demand: {ip.pause_line('caiso')}")
        return 0
    days = [dt.date.fromisoformat(x.strip()) for x in (args.days.split(",") if args.days else ALERT_DAYS) if x.strip()]
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        frames, short = [], []
        for day in days:
            try:
                rows, why = day_rows(day, log)
            except Exception as exc:
                rows, why = None, f"{day}: {ip.redact(repr(exc))[:200]}"
            if rows is None:
                short.append(why)
                log(f"  skipped {why}")
                continue
            frames.append(rows)
            log(f"  {day}: {int((rows['variable'] == 'demand_mw').sum())} intervals")
        if not frames:
            raise RuntimeError(f"no complete day among the {len(days)} asked: {short[:3]}")
        s = pd.concat(frames, ignore_index=True)
        header = [
            "Energy Research Warehouse (ERW): CAISO demand, 5-minute, on the days asked (Today's Outlook)",
            "Shape: series (docs/datastandard.md v0). freq PT5M; ts_utc is the interval start. demand_mw is CAISO's Current demand, "
            "demand_forecast_day_ahead_mw and demand_forecast_hour_ahead_mw its two forecasts (MW); demand_response_marked is 1 in an "
            "interval CAISO's Demand response column marks (count; no row where it is blank).",
            f"Window: {len(days)} Pacific days asked ({'named by hand' if args.days else 'the 39 Flex Alert days of 2018 to 2024, docs/methods/flex_alert_scorecard.md'}), "
            "merged into earlier runs; a day short of any 5-minute interval is not written"
            + (f" (this run: {'; '.join(short)})" if short else "") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/caiso_outlook_demand.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{run_id}/ (not in git)",
            f"Source: {SOURCE} California ISO, Today's Outlook, demand history files ({URL.format(day='YYYYMMDD')})",
            f"  page: {PAGE}",
            "License: public, with credit to the California ISO (CAISO's terms of use, https://www.caiso.com/privacy-terms-of-use; "
            "cite \"California ISO, Today's Outlook\").",
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="California ISO (CAISO)",
                                report="Today's Outlook: demand trend (demand.csv history)", report_url=PAGE,
                                document_list=URL.format(day="YYYYMMDD"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="demand", status="ok", detail=f"{len(frames)} days" + (f"; skipped {len(short)}" if short else "")))
        print(f"{NAME}: {len(frames)} of {len(days)} days written" + (f"; skipped: {'; '.join(short)}" if short else ""))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="demand", status="failed", detail=last[:300]))
    ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 1 if any(r["status"] != "ok" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
