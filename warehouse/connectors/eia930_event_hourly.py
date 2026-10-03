#!/usr/bin/env python3
"""Hourly interchange of every pair and hourly demand of every balancing authority, EIA-930, for two event windows
(session 68, approved pull, ceiling 400,000 rows).

Energy Research Warehouse (ERW) connector. Writes one series table, history (not in the Supabase live set):

    warehouse/output/eia930_event_hourly_interchange.csv    interchange_mw (entity eia930:<FROM>-<TO>) and demand_mw
                                                            (entity eia930:<BA>), partition columns ba and event

for the two historical stories of /network, and for nothing else:

    uri_2021         Winter Storm Uri, 2021-02-07 to 2021-02-24, Central days
    east_heat_2025   the June 2025 heat, 2025-06-20 to 2025-06-28, Eastern days

from the EIA API v2 routes electricity/rto/interchange-data (every directed pair EIA reports) and
electricity/rto/region-data, type D (demand), hourly. The warehouse's own hourly interchange table
(eia930_all_interchange) is a rolling window of recent weeks and holds neither window.

    python warehouse/connectors/eia930_event_hourly.py

Time: EIA's hourly period is the END of the hour in UTC (eia930.py), so ts_utc = period minus one hour. Sign, as EIA
publishes it and as eia930_all_interchange: the reporting balancing authority's net flow with the neighbour, positive
when it exports. Both directions of a pair are kept as published. Demand is kept for the respondents that are
balancing authorities (those that report an interchange in the window), not for EIA's regional sums.
Never filled: an hour EIA does not report is absent, a row without a number is not written and is counted, and
nothing is carried from one hour to the next. The stories say what is missing.
Ceiling: before any page is asked for, the rows the API reports for both routes over both windows are counted, and
the pull stops without writing if they pass 400,000.
Resume: each window and route is one checkpoint (warehouse/raw/eia930_event_hourly/checkpoints/), every page is saved
under warehouse/raw/eia930_event_hourly/<run_id>/. The key comes from EIA_API_KEY and is removed from every URL, log
line and row. Method: docs/methods/grid_network.md, "The stories".
"""

import datetime as dt
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eia930  # noqa: E402
import eia930_interchange as hourly  # noqa: E402  (fetch and count_rows of the hourly interchange route)
import iso_prices as ip  # noqa: E402

NAME = "eia930_event_hourly_interchange"
CONNECTOR = "eia930_event_hourly"
SOURCE_X = f"eia:{hourly.ROUTE}"
DEMAND_ROUTE = "electricity/rto/region-data"
SOURCE_D = f"eia:{DEMAND_ROUTE}"
CEILING = 400_000
COLS = ip.SERIES_COLS + ["ba", "x_to_ba", "event"]
# event id, the window's first and last local day (inclusive), the time zone of those days
EVENTS = [
    dict(event="uri_2021", label="Winter Storm Uri", start="2021-02-07", end="2021-02-24", tz="America/Chicago"),
    dict(event="east_heat_2025", label="the June 2025 heat", start="2025-06-20", end="2025-06-28", tz="America/New_York"),
]


def window(e):
    """The window's UTC hour starts [a, b) and EIA's inclusive period range (the hour's end)."""
    a = pd.Timestamp(e["start"]).tz_localize(e["tz"]).tz_convert("UTC")
    b = (pd.Timestamp(e["end"]) + pd.Timedelta(days=1)).tz_localize(e["tz"]).tz_convert("UTC")
    return a, b, (a + pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H"), b.strftime("%Y-%m-%dT%H")


def count_demand(key, start, end, log):
    import requests
    params = [("api_key", key), ("frequency", "hourly"), ("data[0]", "value"), ("facets[type][]", "D"), ("start", start), ("end", end),
              ("offset", "0"), ("length", "0")]

    def call():
        r = requests.get(eia930.API + DEMAND_ROUTE + "/data/", params=params, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"EIA {DEMAND_ROUTE} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
        return r
    total = int(ip.with_retries(f"EIA {DEMAND_ROUTE} count", call, log).json()["response"].get("total", 0))
    log(f"  {DEMAND_ROUTE} type D [{start}, {end}]: the API reports {total} rows")
    return total


def checkpointed(name, pull, log):
    cp = os.path.join(ip.RAW_DIR, CONNECTOR, "checkpoints", name + ".csv")
    if os.path.exists(cp):
        log(f"  {name}: from checkpoint {os.path.relpath(cp, ip.ROOT)}")
        return pd.read_csv(cp, dtype=str, keep_default_na=False)
    df = pull()
    df = df.astype(str) if len(df) else df
    if len(df):
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        df.to_csv(cp, index=False)
    return df


def to_rows(x, d, e, a, b):
    """The table's rows of one event from the two routes' rows; (rows, counts)."""
    out, n = [], {}
    x = x.copy()
    x["ts"] = pd.to_datetime(x["period"], format="%Y-%m-%dT%H", utc=True) - pd.Timedelta(hours=1)
    x["v"] = pd.to_numeric(x["value"], errors="coerce")
    n["interchange_api"] = len(x)
    n["interchange_no_value"] = int(x["v"].isna().sum())
    x = x[x["v"].notna() & (x["ts"] >= a) & (x["ts"] < b)]
    if x.duplicated(["period", "fromba", "toba"]).any():
        raise RuntimeError(f"{e['event']}: a pair-hour appears twice")
    out.append(pd.DataFrame({
        "entity": "eia930:" + x["fromba"] + "-" + x["toba"], "variable": "interchange_mw", "ts_utc": x["ts"].map(ip.utc_iso),
        "value": x["v"].astype(float), "unit": "MW", "freq": "PT1H", "geo": "", "market": "", "node": "", "source": SOURCE_X,
        "source_url": x["_url"], "retrieved_at": x["_retrieved"], "vintage": "", "ba": x["fromba"].str.lower(),
        "x_to_ba": x["toba"].str.lower(), "event": e["event"]}))
    bas = set(x["fromba"]) | set(x["toba"])
    d = d.copy()
    n["demand_api"] = len(d)
    d = d[d["respondent"].isin(bas)]
    d["ts"] = pd.to_datetime(d["period"], format="%Y-%m-%dT%H", utc=True) - pd.Timedelta(hours=1)
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    n["demand_no_value"] = int(d["v"].isna().sum())
    d = d[d["v"].notna() & (d["ts"] >= a) & (d["ts"] < b)]
    if d.duplicated(["period", "respondent"]).any():
        raise RuntimeError(f"{e['event']}: a balancing authority's hour of demand appears twice")
    out.append(pd.DataFrame({
        "entity": "eia930:" + d["respondent"], "variable": "demand_mw", "ts_utc": d["ts"].map(ip.utc_iso),
        "value": d["v"].astype(float), "unit": "MW", "freq": "PT1H", "geo": "", "market": "", "node": "", "source": SOURCE_D,
        "source_url": d["_url"], "retrieved_at": d["_retrieved"], "vintage": "", "ba": d["respondent"].str.lower(),
        "x_to_ba": "", "event": e["event"]}))
    n["pairs"], n["bas_with_demand"], n["hours"] = x.groupby(["fromba", "toba"]).ngroups, d["respondent"].nunique(), int((b - a) / pd.Timedelta(hours=1))
    n["interchange_rows"], n["demand_rows"] = len(x), len(d)
    return pd.concat(out, ignore_index=True), n


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    try:
        key = ip.load_key("EIA_API_KEY", log)
        ip.RAW.open(CONNECTOR, run_id)
        total = 0
        for e in EVENTS:
            _, _, p0, p1 = window(e)
            total += hourly.count_rows(key, p0, p1, log) + count_demand(key, p0, p1, log)
        log(f"EIA reports {total:,} rows for the two windows and the two routes; ceiling {CEILING:,}")
        if total > CEILING:
            raise RuntimeError(f"{total:,} rows would pass the {CEILING:,} ceiling: nothing pulled")
        frames, notes = [], []
        for e in EVENTS:
            a, b, p0, p1 = window(e)
            x = checkpointed(f"{e['event']}_interchange", lambda: hourly.fetch(key, p0, p1, log), log)
            d = checkpointed(f"{e['event']}_demand", lambda: eia930.fetch_route(DEMAND_ROUTE, key, {"type": ["D"]}, p0, p1, log), log)
            rows, n = to_rows(x, d, e, a, b)
            frames.append(rows)
            notes.append(f"{e['event']} ({e['label']}, {e['start']} to {e['end']}, {e['tz']} days, {n['hours']} hours): "
                         f"{n['interchange_rows']:,} interchange rows of {n['pairs']} directed pairs, {n['demand_rows']:,} demand rows of "
                         f"{n['bas_with_demand']} balancing authorities; rows without a number, not written: interchange "
                         f"{n['interchange_no_value']:,}, demand {n['demand_no_value']:,}")
            log("  " + notes[-1])
        s = pd.concat(frames, ignore_index=True)
        if len(s) > CEILING:
            raise RuntimeError(f"{len(s):,} rows would pass the {CEILING:,} ceiling: nothing written")
        if s.duplicated(["entity", "variable", "ts_utc", "event"]).any():
            raise RuntimeError("two rows share a key")
        header = [
            "Energy Research Warehouse (ERW): hourly interchange of every pair and hourly demand of every balancing authority, "
            "EIA-930, for the two historical stories of /network (session 68)",
            "Shape: series (docs/datastandard.md v0), partition columns ba and event (the key holds event, Decision 32). "
            "interchange_mw: entity eia930:<FROM>-<TO>, the reporting balancing authority's net flow with the neighbour (x_to_ba), MW, "
            "positive when it exports; both directions as EIA publishes them. demand_mw: entity eia930:<BA>, MW. ts_utc is the start "
            "of the hour, UTC (EIA's period is its end). Nothing filled: an hour EIA does not report is absent.",
            "Windows: " + " | ".join(notes),
            f"Rows: {len(s):,} of the {CEILING:,}-row ceiling ({total:,} reported by the API before paging, EIA's regional sums of demand included).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930_event_hourly.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (pages per run, one checkpoint per window and route; not in git)",
            f"Source: {SOURCE_X} U.S. Energy Information Administration, Form EIA-930, hourly interchange between balancing authorities, {eia930.REPORT_PAGE}",
            f"Source: {SOURCE_D} U.S. Energy Information Administration, Form EIA-930, hourly demand by balancing authority (type D), {eia930.REPORT_PAGE}",
            "License: public domain (U.S. Government data, EIA).",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)  # rebuilt whole from the checkpoints
        ip.write_csv(s[COLS], NAME, header, log, cols=COLS, key=["entity", "variable", "ts_utc", "event"])
        ip.update_sources([
            dict(source=SOURCE_X, publisher="U.S. Energy Information Administration", report=hourly.REPORT[0], report_url=hourly.REPORT[1],
                 document_list=hourly.REPORT[2], license="public", tables=[NAME]),
            dict(source=SOURCE_D, publisher="U.S. Energy Information Administration",
                 report="Form EIA-930, Hourly Electric Grid Monitor: hourly demand by balancing authority", report_url=eia930.REPORT_PAGE,
                 document_list=eia930.API + DEMAND_ROUTE + "/", license="public", tables=[NAME])])
        msg = f"{len(s):,} rows of the {CEILING:,} ceiling; " + "; ".join(notes)
        print(f"{NAME}: {msg}")
        results.append(dict(table=NAME, market="all", status="ok", detail=msg[:300]))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{CONNECTOR} {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
