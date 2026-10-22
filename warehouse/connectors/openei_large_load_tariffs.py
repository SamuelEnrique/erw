#!/usr/bin/env python3
"""OpenEI's Utility Rate Database: the large-load tariffs of the seven grids' utilities (session 670, chain 043).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/utility_large_load_tariffs.csv, from the
Utility Rate Database (URDB) API of OpenEI (https://openei.org/wiki/Utility_Rate_Database), version 7:

    https://api.openei.org/utility_rates?version=7&format=json&detail=full&approved=true&sector=<Industrial|Commercial>
                                        &limit=500&offset=<n>&api_key=<OPENEI_API_KEY>

NOT YET RUN AGAINST THE API. Session 670 found no OPENEI_API_KEY on the data machine and pulled nothing; the parser is
tested on rates built in tests/test_session670.py in the API's documented form. The first run with a key is a trial
(--out-dir), read against three utilities' own rate pages before a write.

Which rates: sector Industrial or Commercial, approved, whose minimum demand (peakkwcapacitymin) is 1,000 kW or more,
of a utility (URDB's eiaid) that utility_service_territories lists in the seven grids' states. Paged by sector, so the
requests do not grow with the utilities (about 60 pages); a page is never asked twice (saved in warehouse/raw/).

    entity    openei_urdb:<rate label>; node the rate's name; geo US-<state of the utility's first territory row>
    ts_utc    the rate's start date (startdate), 00:00:00Z; freq blank (a tariff in force from that day)
    variables energy_charge (USD/MWh), the hour-weighted mean over URDB's 12 x 24 weekday and weekend schedules of each
              period's first tier (rate plus adjustment, per kWh times 1,000); demand_charge (USD/kW-month), the flat
              demand structure's first tier plus, for a time-of-use demand structure, the mean over months of the sum of
              the first-tier rates of the periods that month's schedule holds (a flat load sets its demand in every
              period); fixed_charge (USD, a month, fixedchargefirstmeter where its unit is $/month); min_demand_mw
              (MW, peakkwcapacitymin / 1,000); all_in_300mw (USD/MWh) = energy_charge + demand_charge * 1000 / 730 + fixed_charge /
              (300 * 730), a flat 300 MW load for a 730-hour month
    x_*       the utility's EIA id and name, the sector, the rate's URDB page (uri), the end date if any

License: public. OpenEI: "Content is available under Creative Commons Zero unless otherwise noted" (record 88 of
license_reads.csv, session 666). OpenEI's robots file refuses the bulk file /apps/USURDB/download/usurdb.csv, so it is
never asked; the API needs a key from the NREL (now NLR) developer network.
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "utility_large_load_tariffs"
CONNECTOR = "openei_urdb"
SOURCE = "openei:urdb"
API = "https://api.openei.org/utility_rates"
PAGE = "https://openei.org/wiki/Utility_Rate_Database"
SECTORS = ("Industrial", "Commercial")
MIN_KW = 1000.0
LOAD_MW, MONTH_HOURS = 300.0, 730.0
CEILING = 400
LIMIT = 500
GRID_STATES = None  # read from utility_service_territories and grid_peak_vs_capacity's x_states at run time
X_COLS = ["x_eia_id", "x_utility", "x_sector", "x_uri", "x_end_date"]


def first_tier(period):
    """A period's first tier: rate plus adjustment (URDB's per-unit figures), or None when it holds no rate."""
    if not period:
        return None
    t = period[0]
    if "rate" not in t:
        return None
    return float(t["rate"]) + float(t.get("adj") or 0.0)


def energy_charge(rate):
    """USD/MWh: the hour-weighted mean of the first-tier energy rates over the weekday and weekend 12 x 24 schedules
    (weekdays 5/7, weekends 2/7), for a load drawn the same every hour. None when the rate has no energy structure or a
    tier's unit is not kWh."""
    s, wd, we = rate.get("energyratestructure"), rate.get("energyweekdayschedule"), rate.get("energyweekendschedule")
    if not s or not wd:
        return None
    if any((p and p[0].get("unit", "kWh") != "kWh") for p in s):
        return None
    we = we or wd
    vals = [first_tier(p) for p in s]
    total, hours = 0.0, 0.0
    for sched, w in ((wd, 5.0), (we, 2.0)):
        for month in sched:
            for period in month:
                v = vals[period] if period < len(vals) else None
                if v is None:
                    return None
                total += v * w
                hours += w
    return round(total / hours * 1000.0, 4)


def demand_charge(rate):
    """USD/kW-month for a flat load: the flat demand structure's first tier (the month's own, by flatdemandmonths, as a
    mean over the months), plus a time-of-use structure's first-tier rates summed over the periods each month's weekday
    schedule holds, as a mean over the months. 0 when the rate has neither."""
    out = 0.0
    flat, months = rate.get("flatdemandstructure"), rate.get("flatdemandmonths")
    if flat:
        vals = [first_tier(p) or 0.0 for p in flat]
        idx = months if months and len(months) == 12 else [0] * 12
        out += sum(vals[i] if i < len(vals) else 0.0 for i in idx) / 12.0
    tou, sched = rate.get("demandratestructure"), rate.get("demandweekdayschedule")
    if tou and sched:
        vals = [first_tier(p) or 0.0 for p in tou]
        out += sum(sum(vals[p] for p in sorted(set(month)) if p < len(vals)) for month in sched) / len(sched)
    return round(out, 4)


def fixed_charge(rate):
    if rate.get("fixedchargeunits", "$/month") != "$/month":
        return None
    v = rate.get("fixedchargefirstmeter")
    return None if v is None else float(v)


def rows_of(rate, eia_utilities, url, retrieved):
    """One rate's rows, or [] when it is not a large-load rate of a utility the territories table lists."""
    if rate.get("sector") not in SECTORS or not rate.get("approved", True):
        return []
    kw = rate.get("peakkwcapacitymin")
    if kw is None or float(kw) < MIN_KW:
        return []
    eia = str(rate.get("eiaid") or "")
    if eia not in eia_utilities:
        return []
    start = rate.get("startdate")
    if start is None:
        return []
    day = dt.datetime.fromtimestamp(int(start), dt.timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    end = rate.get("enddate")
    end = dt.datetime.fromtimestamp(int(end), dt.timezone.utc).strftime("%Y-%m-%d") if end else ""
    e, d, f = energy_charge(rate), demand_charge(rate), fixed_charge(rate)
    base = dict(entity=f"openei_urdb:{rate['label']}", ts_utc=day, freq="", geo=f"US-{eia_utilities[eia]}", market="",
                node=rate.get("name", ""), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                x_eia_id=eia, x_utility=rate.get("utility", ""), x_sector=rate["sector"], x_uri=rate.get("uri", ""),
                x_end_date=end)
    out = [dict(base, variable="min_demand_mw", value=float(kw) / 1000.0, unit="MW"),
           dict(base, variable="demand_charge", value=d, unit="USD/kW-month")]
    if e is not None:
        out.append(dict(base, variable="energy_charge", value=e, unit="USD/MWh"))
    if f is not None:
        out.append(dict(base, variable="fixed_charge", value=f, unit="USD"))
    if e is not None:
        allin = e + d * 1000.0 / MONTH_HOURS + (f or 0.0) / (LOAD_MW * MONTH_HOURS)
        out.append(dict(base, variable="all_in_300mw", value=round(allin, 4), unit="USD/MWh"))
    return out


def territories(out_dir, states):
    """{EIA utility id: its first state} for the utilities utility_service_territories lists in these states."""
    p = os.path.join(out_dir, "utility_service_territories.csv")
    n = sum(1 for ln in open(p, encoding="utf-8") if ln.startswith("#"))
    t = pd.read_csv(p, skiprows=n, dtype=str, keep_default_na=False)
    t = t[t["x_state"].isin(states)].sort_values(["x_utility_number", "x_state"])
    return dict(zip(t["x_utility_number"], t["x_state"]))


def grid_states(out_dir):
    p = os.path.join(out_dir, "grid_peak_vs_capacity.csv")
    n = sum(1 for ln in open(p, encoding="utf-8") if ln.startswith("#"))
    t = pd.read_csv(p, skiprows=n, dtype=str, keep_default_na=False)
    return sorted({s for v in t["x_states"] for s in v.split(";") if s})


def main(argv=None):
    ap = argparse.ArgumentParser(description="OpenEI URDB large-load tariffs of the seven grids' utilities")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--offline", action="store_true", help="the saved pages only")
    args = ap.parse_args(argv)
    key = os.environ.get("OPENEI_API_KEY")
    if not key:
        from dotenv import dotenv_values
        key = (dotenv_values(os.path.join(ip.ROOT, ".env")).get("OPENEI_API_KEY") or "").strip()
    if not key and not args.offline:
        print("OPENEI_API_KEY is not set (.env or environment): nothing asked, nothing written", file=sys.stderr)
        return 1
    held = ip.OUT_DIR
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results, asked = [], 0
    try:
        utilities = territories(held, grid_states(held))
        rows = []
        for sector in SECTORS:
            offset = 0
            while True:
                if asked >= CEILING:
                    raise RuntimeError(f"the ceiling of {CEILING} requests was reached at {sector} offset {offset}")
                url = (f"{API}?version=7&format=json&detail=full&approved=true&sector={sector}&limit={LIMIT}"
                       f"&offset={offset}&api_key={key}")
                content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline)
                asked += 1
                items = json.loads(content).get("items", [])
                for r in items:
                    rows += rows_of(r, utilities, ip.redact(url), rec["retrieved_at"])
                if len(items) < LIMIT:
                    break
                offset += LIMIT
        s = pd.DataFrame(rows, columns=ip.SERIES_COLS + X_COLS)
        if s.empty:
            raise RuntimeError("no large-load rate of a listed utility")
        s = s.drop_duplicates(["entity", "variable", "ts_utc"], keep="last")
        header = [
            "Energy Research Warehouse (ERW): OpenEI Utility Rate Database, the large-load tariffs (minimum demand 1 MW or more) of the seven grids' utilities (session 670)",
            "Shape: series (docs/datastandard.md v0). entity openei_urdb:<label>; ts_utc the rate's start date; variables energy_charge (USD/MWh), demand_charge (USD/kW-month), fixed_charge (USD a month), min_demand_mw (MW), all_in_300mw (USD/MWh).",
            f"all_in_300mw = energy_charge + demand_charge * 1000 / {MONTH_HOURS:.0f} + fixed_charge / ({LOAD_MW:.0f} * {MONTH_HOURS:.0f}): a flat {LOAD_MW:.0f} MW load for a {MONTH_HOURS:.0f}-hour month. Energy: the hour-weighted mean of the first tiers over URDB's weekday and weekend schedules; demand: the flat structure's first tier plus each month's time-of-use periods' first tiers.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/openei_large_load_tariffs.py; {asked} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} OpenEI, Utility Rate Database, {PAGE}",
            "License: public (OpenEI: \"Content is available under Creative Commons Zero unless otherwise noted\").",
        ]
        ip.write_csv(s, NAME, header, log, cols=ip.SERIES_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="OpenEI", report="Utility Rate Database (URDB)", report_url=PAGE,
                                    document_list=API, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{s['entity'].nunique():,} rates, {asked} requests"))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
