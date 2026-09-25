#!/usr/bin/env python3
"""Hourly demand and generation for the seven ISOs and the US Lower 48 (EIA-930).

Energy Research Warehouse (ERW) connector. Reads Form EIA-930 (Hourly
Electric Grid Monitor) through the EIA API v2 and writes, per balancing
authority (BA), two `series` tables:

    warehouse/output/eia930_<ba>_demand.csv      demand_mw, demand_forecast_mw
    warehouse/output/eia930_<ba>_generation.csv  net_generation_mw,
                                                 net_generation_<fuel>_mw

    python warehouse/connectors/eia930.py --days 30
    python warehouse/connectors/eia930.py --days 3 --ba ciso

Routes and parameters (the exact request is each row's source_url, with the
API key removed):
  electricity/rto/region-data     frequency=hourly, facets type D, DF, NG
  electricity/rto/fuel-type-data  frequency=hourly, every fuel type reported

Time: EIA's hourly `period` is the END of the hour in UTC (checked in session
5: EIA NYIS demand matches NYISO's own load integrated over the hour before
`period`, mean difference 57.5 MW, against 405.7 MW for the hour after; the
EIA-930 bulk files name the column "UTC time at end of hour", and gridstatus
reads it the same way). ts_utc is therefore period minus one hour, the
interval start, as docs/datastandard.md requires.

Window: the last N complete UTC days before today. EIA-930 is published in UTC
hours, so UTC days are used rather than each BA's local operating day.

Completeness (the ERW rule): a table is written only if every variable it
holds has a value for every hour of the window. A fuel type the BA does not
report at all is not a variable of that table; one reported for some hours
and not others makes the table incomplete, and nothing is written for it.
Values are MW as EIA publishes them (net generation of storage can be
negative). The key comes from EIA_API_KEY (environment or .env).
"""

import argparse
import datetime as dt
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402  shared: raw capture, merge-writer, logs, redaction

API = "https://api.eia.gov/v2/"
PAGE = 5000
BAS = {
    # table code: (EIA respondent, geo)
    "ciso": ("CISO", "US-CA"),
    "erco": ("ERCO", "US-TX"),
    "isne": ("ISNE", "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT"),
    "miso": ("MISO", "US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,"
             "US-ND,US-SD,US-TX,US-WI"),
    "nyis": ("NYIS", "US-NY"),
    "pjm": ("PJM", "US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,"
            "US-TN,US-VA,US-WV"),
    "swpp": ("SWPP", "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,"
             "US-SD,US-TX,US-WY"),
    "us48": ("US48", "US"),
}
REGION_TYPES = {"D": "demand_mw", "DF": "demand_forecast_mw", "NG": "net_generation_mw"}
FUELS = {
    "COL": "coal", "NG": "natural_gas", "NUC": "nuclear", "OIL": "oil", "WAT": "hydro",
    "SUN": "solar", "WND": "wind", "GEO": "geothermal", "OTH": "other", "UNK": "unknown",
    "BAT": "battery", "PS": "pumped_storage", "SNB": "solar_with_battery",
    "WNB": "wind_with_battery", "OES": "other_storage", "UES": "unknown_storage",
}
REPORT_PAGE = "https://www.eia.gov/electricity/gridmonitor/"
REPORTS = {
    "eia:electricity/rto/region-data": (
        "Form EIA-930, Hourly Electric Grid Monitor: hourly demand, day-ahead demand forecast, "
        "net generation and interchange by balancing authority", REPORT_PAGE,
        API + "electricity/rto/region-data/"),
    "eia:electricity/rto/fuel-type-data": (
        "Form EIA-930, Hourly Electric Grid Monitor: hourly net generation by energy source",
        REPORT_PAGE, API + "electricity/rto/fuel-type-data/"),
}


def fetch_route(route, key, facets, start, end, log):
    """All rows of an EIA v2 route for [start, end] hours, paged; each row keeps its page URL."""
    out, offset, total = [], 0, None
    while True:
        params = [("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
                  ("start", start), ("end", end), ("sort[0][column]", "period"),
                  ("sort[0][direction]", "asc"), ("sort[1][column]", "respondent"),
                  ("sort[1][direction]", "asc"), ("offset", str(offset)), ("length", str(PAGE))]
        for name, values in facets.items():
            params += [(f"facets[{name}][]", v) for v in values]

        def call():
            r = requests.get(API + route + "/data/", params=params, timeout=120)
            if r.status_code != 200:
                raise RuntimeError(f"EIA {route} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
            return r
        r = ip.with_retries(f"EIA {route} offset {offset}", call, log)
        body = r.json()["response"]
        rows = body.get("data", [])
        total = int(body.get("total", 0))
        url = ip.redact(r.url)
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for row in rows:
            row["_url"], row["_retrieved"] = url, retrieved
        out += rows
        log(f"  {route} offset {offset}: {len(rows)} rows (total {total}) {url}")
        offset += len(rows)
        if not rows or offset >= total:
            break
        time.sleep(0.5)
    if total is not None and len(out) != total:
        raise RuntimeError(f"EIA {route}: got {len(out)} rows, API reported {total}")
    return pd.DataFrame(out)


def to_rows(df, route, variable_of, code_col):
    """EIA rows to interval-start rows with provenance; unknown codes raise."""
    unknown = sorted(set(df[code_col]) - set(variable_of))
    if unknown:
        raise RuntimeError(f"{route}: unmapped {code_col} codes {unknown}; add them to the "
                           "connector before writing (never drop data silently)")
    value = pd.to_numeric(df["value"], errors="coerce")
    end = pd.to_datetime(df["period"], format="%Y-%m-%dT%H", utc=True)
    out = pd.DataFrame({
        "respondent": df["respondent"].values,
        "variable": df[code_col].map(variable_of).values,
        "interval_start": (end - pd.Timedelta(hours=1)).values,
        "value": value.values,
        "source": f"eia:{route}",
        "source_url": df["_url"].values,
        "retrieved_at": df["_retrieved"].values,
    })
    out["interval_start"] = pd.to_datetime(out["interval_start"], utc=True)  # .values drops tz
    return out


def check_complete(rows, start, end, log, what):
    expected = pd.date_range(start, end, freq="1h", inclusive="left")
    problems = []
    for var, g in rows.groupby("variable"):
        have = pd.DatetimeIndex(g.loc[g["value"].notna(), "interval_start"])
        missing = expected.difference(have)
        nulls = int(g["value"].isna().sum())
        if len(missing) or have.has_duplicates:
            problems.append(f"{var}: {len(have)} of {len(expected)} hours "
                            f"({len(missing)} missing, {nulls} published as null; first missing "
                            f"{[ip.utc_iso(t) for t in missing[:3]]})")
    if problems:
        for p in problems:
            log(f"  INCOMPLETE {what} {p}")
        raise RuntimeError(f"incomplete data, no file written for {what}: " + "; ".join(problems[:4]))
    log(f"  complete: {what}: {rows['variable'].nunique()} variables x {len(expected)} hours")


def build_table(rows, code, start, end, log, name, title, run_id, days):
    respondent, geo = BAS[code]
    rows = rows[(rows["interval_start"] >= start) & (rows["interval_start"] < end)]
    dup = rows.duplicated(["variable", "interval_start"], keep=False)
    if dup.any():
        raise RuntimeError(f"{name}: {int(dup.sum())} rows repeat a (variable, hour) key")
    check_complete(rows, start, end, log, name)
    s = pd.DataFrame({
        "entity": f"eia930:{respondent}",
        "variable": rows["variable"].values,
        "ts_utc": pd.to_datetime(rows["interval_start"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ").values,
        "value": rows["value"].values,
        "unit": "MW",
        "freq": "PT1H",
        "geo": geo,
        "market": "",
        "node": "",
        "source": rows["source"].values,
        "source_url": rows["source_url"].values,
        "retrieved_at": rows["retrieved_at"].values,
        "vintage": "",
    })
    s = s.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
    header = [
        f"Energy Research Warehouse (ERW): {title}",
        "Shape: series (docs/datastandard.md v0). Units: MW. ts_utc is interval start, UTC "
        "(EIA's hourly period is the hour END; one hour is subtracted).",
        f"Window: {days} complete UTC days, [{ip.utc_iso(start)}, {ip.utc_iso(end)})",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia930.py via the EIA API v2",
        f"Run log: warehouse/output/logs/eia930_{run_id}.log (every API request, key removed)",
        f"Raw files: warehouse/raw/eia930/{run_id}/ (not in git; manifest.csv lists each file and URL)",
    ]
    for src in sorted(set(s["source"])):
        report, page, route_url = REPORTS[src]
        header.append(f"Source: {src} {report}, {page}")
        header.append(f"  document list: {route_url}")
    header.append(f"Respondent {respondent}. Variables: {', '.join(sorted(set(s['variable'])))}. "
                  "vintage is empty: EIA does not publish a release time per value, and EIA-930 "
                  "values are revised; the latest retrieval replaces earlier ones.")
    return ip.write_csv(s, name, header, log)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA-930 demand and generation connector")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--ba", action="append", choices=sorted(BAS),
                    help="one balancing authority (repeatable); default all")
    ap.add_argument("--out-dir", help="write CSVs, logs and raw files here (trial runs)")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia930_{run_id}.log"))
    ip.RAW.open("eia930", run_id)
    results = []
    key = ip.load_key("EIA_API_KEY", log)
    codes = args.ba or sorted(BAS)
    end = pd.Timestamp.now(tz="UTC").normalize()
    start = end - pd.Timedelta(days=args.days)
    log(f"ERW eia930 run {run_id}; window [{ip.utc_iso(start)}, {ip.utc_iso(end)}); BAs {codes}")
    if key is None:
        log("FAILED: EIA_API_KEY is empty; nothing pulled")
        print("eia930 FAILED: EIA_API_KEY is empty", file=sys.stderr)
        results = [dict(table=f"eia930_{c}_{fam}", market=fam, status="failed",
                        detail="EIA_API_KEY empty") for c in codes for fam in ("demand", "generation")]
        ip.write_status("eia930", run_id, results)
        log.close()
        return 1
    respondents = [BAS[c][0] for c in codes]
    # EIA periods are hour-ending, so the window's first hour ends at start + 1h
    q_start = (start + pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H")
    q_end = end.strftime("%Y-%m-%dT%H")
    fetched = {}
    try:
        reg = fetch_route("electricity/rto/region-data", key,
                          {"respondent": respondents, "type": list(REGION_TYPES)}, q_start, q_end, log)
        fetched["region"] = to_rows(reg, "electricity/rto/region-data", REGION_TYPES, "type")
        fuel = fetch_route("electricity/rto/fuel-type-data", key,
                           {"respondent": respondents}, q_start, q_end, log)
        fuel_vars = {k: f"net_generation_{v}_mw" for k, v in FUELS.items()}
        fetched["fuel"] = to_rows(fuel, "electricity/rto/fuel-type-data", fuel_vars, "fueltype")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED fetching from EIA, nothing written:\n{tb}")
        print(f"eia930 FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results = [dict(table=f"eia930_{c}_{fam}", market=fam, status="failed",
                        detail=tb.strip().splitlines()[-1][:300])
                   for c in codes for fam in ("demand", "generation")]
        ip.write_status("eia930", run_id, results)
        log.close()
        return 1
    reg, fuel = fetched["region"], fetched["fuel"]
    for code in codes:
        respondent = BAS[code][0]
        for fam, rows, title in (
            ("demand", reg[(reg["respondent"] == respondent)
                           & reg["variable"].isin(["demand_mw", "demand_forecast_mw"])],
             f"EIA-930 hourly demand and day-ahead demand forecast, {respondent}"),
            ("generation", pd.concat([
                reg[(reg["respondent"] == respondent) & (reg["variable"] == "net_generation_mw")],
                fuel[fuel["respondent"] == respondent]], ignore_index=True),
             f"EIA-930 hourly net generation, total and by energy source, {respondent}"),
        ):
            name = f"eia930_{code}_{fam}"
            log(f"{name}:")
            try:
                if rows.empty:
                    raise ip.SourceGap(f"EIA returned no {fam} rows for {respondent}")
                build_table(rows, code, start, end, log, name, title, run_id, args.days)
                results.append(dict(table=name, market=fam, status="ok", detail=""))
            except Exception:
                tb = ip.redact(traceback.format_exc())
                last = tb.strip().splitlines()[-1]
                log(f"{name} FAILED, no output file written:\n{tb}")
                print(f"eia930 {name} FAILED, no output file written: {last}", file=sys.stderr)
                results.append(dict(table=name, market=fam, status="failed", detail=last[:300]))
    ip.update_sources([dict(source=s, publisher="U.S. Energy Information Administration (EIA)",
                            report=r[0], report_url=r[1], document_list=r[2],
                            tables=[x["table"] for x in results if x["status"] == "ok"])
                       for s, r in REPORTS.items()])
    ip.write_status("eia930", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"eia930 run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
