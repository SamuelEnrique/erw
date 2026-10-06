#!/usr/bin/env python3
"""EIA supply and trade series for the Supply and trade page: gas storage, petroleum stocks, production, refining and
trade by the week, gas trade and basin production by the month (session 134, approved pull).

Energy Research Warehouse (ERW) connector. Four series tables from EIA's open data API (https://api.eia.gov/v2/):

| table                         | route                                              | freq    | from    | unit                 |
|-------------------------------|----------------------------------------------------|---------|---------|----------------------|
| eia_gas_storage_weekly        | natural-gas/stor/wkly                              | weekly  | 2010    | bcf                  |
| eia_petroleum_supply_weekly   | petroleum/stoc/wstk, sum/sndw, move/wkly           | weekly  | 2010    | kbbl, kbbl/d, pct    |
| eia_gas_trade_monthly         | natural-gas/move/poe1, poe2                        | monthly | 2015-01 | MMcf                 |
| eia_basin_production_monthly  | steo (Short-Term Energy Outlook)                   | monthly | 2015-01 | kbbl/d, bcf/d        |

    python warehouse/connectors/eia_supply.py                        # every table
    python warehouse/connectors/eia_supply.py --table eia_gas_storage_weekly
    python warehouse/connectors/eia_supply.py --out-dir DIR           # a trial: the tables under DIR

GAS STORAGE: working gas in underground storage, the Lower 48 and EIA's five regions (and the South Central's salt
and nonsalt), from the Weekly Natural Gas Storage Report. A weekly value sits at 00:00:00Z of EIA's date, the Friday
the report week ends.

PETROLEUM, WEEKLY, from the Weekly Petroleum Status Report: ending stocks (commercial crude, Cushing, the Strategic
Petroleum Reserve, total gasoline, distillate); field production of crude (US, Lower 48, Alaska); refinery
utilization and refiners' net input of crude, the US and the five PADDs; imports, exports and net imports of crude and
of products, and distillate and gasoline trade. Each is the series EIA names, unchanged; variable says what it is
(stocks, production, utilization, crude_input, flow).

GAS TRADE, MONTHLY: pipeline exports to Mexico and Canada, pipeline imports from Canada and Mexico, LNG exports in all
and by terminal (every terminal EIA lists with a total to all countries), LNG imports.

BASIN PRODUCTION, MONTHLY: crude oil production and marketed natural gas production by region, the series the
Short-Term Energy Outlook carries since the Drilling Productivity Report was folded into it. THE OUTLOOK'S SERIES RUN
ON INTO EIA'S FORECAST. Only history is written: months up to HISTORY_LAG months before the month of the run (the
Outlook's recent months are EIA's estimates and its later ones a forecast; the lag keeps the forecast out). The header
says which month the table ends on.

A date EIA lists with no value is not written and is counted. Nothing is filled. Each table is written only if its
newest date is recent. Ceiling: 1,200,000 rows for session 134's pulls in all (the rows the API returns, the session's
probes included). EIA data are in the public domain (credit: U.S. Energy Information Administration).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

API = "https://api.eia.gov/v2/"
CEILING = 1_200_000
EXPLORED = 6_000          # session 134's probes of these routes
PAGE = 5000
PUBLISHER = "U.S. Energy Information Administration (EIA)"
FREQ = {"weekly": "P1W", "monthly": "P1M"}
STALE = {"weekly": 21, "monthly": 150}
HISTORY_LAG = 3           # months: the Outlook's months newer than this before the run are not written
UNITS = {"BCF": "bcf", "MBBL": "kbbl", "MBBL/D": "kbbl/d", "%": "pct", "MMCF": "MMcf", "million barrels per day": "kbbl/d", "billion cubic feet per day": "bcf/d"}
SCALE = {"million barrels per day": 1000.0}      # the Outlook's crude is in million barrels a day: written as kbbl/d
WPSR = "https://www.eia.gov/petroleum/supply/weekly/"

STOCKS = {"WCESTUS1": "stocks", "W_EPC0_SAX_YCUOK_MBBL": "stocks", "WCSSTUS1": "stocks", "WGTSTUS1": "stocks", "WDISTUS1": "stocks"}
SUPPLY = {"WCRFPUS2": "production", "W_EPC0_FPF_R48_MBBLD": "production", "W_EPC0_FPF_SAK_MBBLD": "production",
          "WPULEUS3": "utilization", **{f"W_NA_YUP_R{p}0_PER": "utilization" for p in range(1, 6)},
          "WCRRIUS2": "crude_input", **{f"WCRRIP{p}2": "crude_input" for p in range(1, 6)}}
TRADE = {k: "flow" for k in ("WCRIMUS2", "WCREXUS2", "WCRNTUS2", "WRPIMUS2", "WRPEXUS2", "WRPNTUS2", "WTTNTUS2", "WDIIMUS2", "WDIEXUS2", "W_EPM0F_IM0_NUS-Z00_MBBLD")}
GAS_TRADE = ["N9132MX2", "N9132CN2", "N9133US2"]
GAS_IMPORTS = ["N9102CN2", "N9102MX2", "N9103US2"]

TABLES = {
    "eia_gas_storage_weekly": dict(
        freq="weekly", start="2010-01-01", title="EIA weekly working gas in underground storage, the Lower 48 and its regions, from 2010",
        parts=[dict(source="eia:natural-gas/stor/wkly", route="natural-gas/stor/wkly", page="https://ir.eia.gov/ngs/ngs.html", report="Weekly Natural Gas Storage Report", facets=[], variable=lambda s: "working_gas")]),
    "eia_petroleum_supply_weekly": dict(
        freq="weekly", start="2010-01-01", title="EIA weekly petroleum stocks, crude production, refinery utilization and inputs, and trade, from 2010 (Weekly Petroleum Status Report)",
        parts=[
            dict(source="eia:petroleum/stoc/wstk:supply", route="petroleum/stoc/wstk", page=WPSR, report="Weekly Petroleum Status Report: stocks", facets=[("series", s) for s in STOCKS], variable=STOCKS.get),
            dict(source="eia:petroleum/sum/sndw", route="petroleum/sum/sndw", page=WPSR, report="Weekly Petroleum Status Report: supply and disposition", facets=[("series", s) for s in SUPPLY], variable=SUPPLY.get),
            dict(source="eia:petroleum/move/wkly:supply", route="petroleum/move/wkly", page=WPSR, report="Weekly Petroleum Status Report: imports and exports", facets=[("series", s) for s in TRADE], variable=TRADE.get),
        ]),
    "eia_gas_trade_monthly": dict(
        freq="monthly", start="2015-01", title="EIA monthly natural gas trade: pipeline flows with Mexico and Canada, LNG exports in all and by terminal, LNG imports, from 2015",
        parts=[
            dict(source="eia:natural-gas/move/poe2:supply", route="natural-gas/move/poe2", page="https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_ENP_Mmcf_m.htm", report="U.S. Natural Gas Exports and Re-Exports by Point of Exit",
                 facets=[], variable=lambda s: "export_volume", keep=lambda s: s in GAS_TRADE or bool(re.fullmatch(r"NGM_EPG0_ENG_Y[A-Z]+-Z00_MMCF", s))),
            dict(source="eia:natural-gas/move/poe1:supply", route="natural-gas/move/poe1", page="https://www.eia.gov/dnav/ng/ng_move_poe1_a_EPG0_IRP_Mmcf_m.htm", report="U.S. Natural Gas Imports by Point of Entry",
                 facets=[("series", s) for s in GAS_IMPORTS], variable=lambda s: "import_volume"),
        ]),
    "eia_basin_production_monthly": dict(
        freq="monthly", start="2015-01", title="EIA monthly crude oil and marketed natural gas production by producing region, history only, from 2015 (Short-Term Energy Outlook)",
        parts=[dict(source="eia:steo:basin_production", route="steo", page="https://www.eia.gov/outlooks/steo/", report="Short-Term Energy Outlook: crude oil and natural gas production by region", steo=True, facets=[],
                    variable=lambda s: "crude_production" if s.startswith("COPR") else "gas_marketed_production")]),
}


class Budget:
    """The rows the API has returned to this run, against the session's ceiling."""
    def __init__(self):
        self.n = EXPLORED

    def add(self, rows):
        self.n += rows
        if self.n > CEILING:
            raise RuntimeError(f"{self.n:,} rows read, over the ceiling of {CEILING:,}: stopped, nothing more is written")


def steo_series(key, log):
    """The Outlook's production series by region, from its own list: COPR<region> (crude) and NGMP<region> (marketed gas)."""
    r = ip.with_retries("EIA steo series list", lambda: requests.get(API + "steo/facet/seriesId", params={"api_key": key}, timeout=120), log)
    names = {x["id"]: x.get("name") or "" for x in r.json()["response"]["facets"]}
    regions = ("AP", "BK", "EF", "HA", "PM", "AN", "NI", "R48")
    out = {s: names[s] for s in names if re.fullmatch(r"(COPR|NGMP)(" + "|".join(regions) + ")", s)}
    if len(out) < 8:
        raise RuntimeError(f"the Outlook lists {sorted(out)}: fewer regional production series than expected")
    log(f"  steo: {len(out)} regional production series: " + "; ".join(f"{k} = {v}" for k, v in sorted(out.items())))
    return out


def fetch(part, freq, start, key, log, budget, facets):
    """Every row of one route from start, as the API returns it. Each row carries its page's address (no key) and time."""
    out, offset = [], 0
    while True:
        params = [("frequency", freq), ("data[0]", "value")] + [(f"facets[{f}][]", v) for f, v in facets] + [("start", start), ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
                                                                                                               ("sort[1][column]", "seriesId" if part.get("steo") else "series"), ("sort[1][direction]", "asc"),
                                                                                                               ("offset", str(offset)), ("length", str(PAGE))]
        public = requests.Request("GET", API + part["route"] + "/data/", params=params).prepare().url

        def call():
            r = requests.get(public, params=[("api_key", key)], timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"EIA {part['route']} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
            return r
        r = ip.with_retries(f"EIA {part['route']} offset {offset}", call, log)
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        ip.RAW.alias(public, r.content, r.headers)
        resp = r.json()["response"]
        rows, total = resp.get("data", []), int(resp.get("total", 0))
        budget.add(len(rows))
        for row in rows:
            row["_url"], row["_retrieved"] = public, str(retrieved)
        out += rows
        log(f"  {part['route']} offset {offset}: {len(rows)} rows (total {total}); {budget.n:,} rows in all")
        offset += len(rows)
        if not rows or offset >= total:
            break
        time.sleep(0.4)
    if len(out) != total:
        raise RuntimeError(f"EIA {part['route']}: got {len(out)} rows, API reported {total}")
    return out


def number(v):
    if v is None or str(v).strip() in ("", "W", "NA", "--", "null", "None"):
        return None
    return float(v)


def name_of(description):
    """A series' name without its unit in brackets."""
    return re.sub(r"\s+", " ", re.sub(r"\s*\((Billion Cubic Feet|Thousand Barrels per Day|Thousand Barrels|Million Cubic Feet|MMcf|Percent)\)\s*$", "", str(description or ""))).strip()


def shape(part, rows, freq, last_month=None):
    """One route's rows as the table's rows; a date with no value is left out and counted, and so is a series not asked
    for or, for the Outlook, a month after the last month of history."""
    out, empty, forecast = [], 0, 0
    for r in rows:
        sid = r.get("seriesId") if part.get("steo") else r.get("series")
        if part.get("keep") and not part["keep"](sid):
            continue
        raw_unit = r.get("unit") if part.get("steo") else r.get("units")
        unit = UNITS.get(raw_unit)
        if unit is None:
            raise RuntimeError(f"{part['route']} {sid}: EIA unit {raw_unit!r} is not one this connector knows")
        if last_month and r["period"] > last_month:
            forecast += 1
            continue
        v = number(r.get("value"))
        if v is None:
            empty += 1
            continue
        period = r["period"]
        out.append(dict(entity=f"eia:{sid}", variable=part["variable"](sid), ts_utc=(period + "-01" if freq == "monthly" else period) + "T00:00:00Z", value=round(v * SCALE.get(raw_unit, 1.0), 6), unit=unit,
                        freq=FREQ[freq], geo="US", market="", node=name_of(r.get("seriesDescription") if part.get("steo") else r.get("series-description")), source=part["source"], source_url=r["_url"],
                        retrieved_at=r["_retrieved"], vintage=""))
    return out, empty, forecast


def build(name, cfg, key, run_id, log, budget):
    freq, frames, empty, counts, note = cfg["freq"], [], 0, [], ""
    for part in cfg["parts"]:
        facets, last_month = list(part["facets"]), None
        if part.get("steo"):
            facets = [("seriesId", s) for s in steo_series(key, log)]
            last_month = (pd.Timestamp(dt.datetime.now(dt.timezone.utc).date()).to_period("M") - HISTORY_LAG).strftime("%Y-%m")
        rows = fetch(part, freq, cfg["start"], key, log, budget, facets)
        shaped, n_empty, n_forecast = shape(part, rows, freq, last_month)
        empty += n_empty
        counts.append(f"{part['route']}: {len(rows):,} rows returned, {len(shaped):,} values")
        if part.get("steo"):
            note = f" The Outlook's months after {last_month} are EIA's newest estimates and its forecast: {n_forecast:,} such rows were not written."
        frames.append(pd.DataFrame(shaped, columns=ip.SERIES_COLS))
    table = pd.concat(frames, ignore_index=True)
    if table.empty:
        raise RuntimeError(f"{name}: EIA returned no value")
    if table.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{name}: EIA lists a series and date more than once")
    newest = pd.Timestamp(table["ts_utc"].max())
    age = (pd.Timestamp.now(tz="UTC") - newest).days
    if age > STALE[freq]:
        raise RuntimeError(f"{name}: the newest date EIA holds is {newest.date()}, {age} days old (limit {STALE[freq]})")
    header = [
        f"Energy Research Warehouse (ERW): {cfg['title']} (session 134)",
        f"Shape: series (docs/datastandard.md v0). freq {FREQ[freq]}; ts_utc is EIA's date at 00:00:00Z (a weekly value's is the date the report week ends, a monthly value's the first day of the month). node is EIA's name of the series. Variables: "
        + ", ".join(sorted(set(table["variable"]))) + ". Units per row.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_supply.py",
        f"Run log: warehouse/output/logs/eia_supply_{run_id}.log",
        "Raw files: warehouse/raw/eia_supply/ (not in git; each run's manifest.csv lists each answer and its address, without the key)",
    ]
    for part in cfg["parts"]:
        header.append(f"Source: {part['source']} EIA, {part['report']}, {part['page']}")
        header.append(f"  access: {API}{part['route']}/data/ (frequency {freq}, from {cfg['start']})")
    header += [
        f"Series: {table[['entity', 'variable']].drop_duplicates().shape[0]}, newest date {newest.date()}. " + "; ".join(counts) + f". Dates EIA lists with no value, not written: {empty}.{note}",
        "Values are EIA's (the Outlook's crude is written in thousand barrels a day, EIA's million barrels a day times 1,000). Nothing is filled.",
        "License: public. U.S. government publications are in the public domain (EIA, Copyrights and Reuse). Credit: U.S. Energy Information Administration.",
    ]
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if os.path.exists(path):
        os.remove(path)     # the whole history is read each run, so EIA's revisions are picked up
    ip.write_csv(table[ip.SERIES_COLS], name, header, log)
    return table, [dict(source=p["source"], publisher=PUBLISHER, report=p["report"], report_url=p["page"], document_list=API + p["route"] + "/", license="public", tables=[name]) for p in cfg["parts"]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA supply and trade series (session 134)")
    ap.add_argument("--table", choices=sorted(TABLES), action="append")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia_supply_{run_id}.log"))
    results, budget = [], Budget()
    try:
        key = ip.load_key("EIA_API_KEY", log)
        ip.RAW.open("eia_supply", run_id)
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED before any request:\n{tb}")
        print(f"eia_supply FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        log.close()
        return 1
    for name in args.table or list(TABLES):
        try:
            table, sources = build(name, TABLES[name], key, run_id, log, budget)
            if not args.out_dir:
                ip.update_sources(sources)
            results.append(dict(table=name, market="all", status="ok", detail=f"{len(table)} rows; {budget.n} rows returned so far"))
            print(f"{name}: {len(table):,} values, newest {table['ts_utc'].max()[:10]}; {budget.n:,} rows returned of {CEILING:,}")
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"FAILED {name}:\n{tb}")
            print(f"{name} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=name, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia_supply", run_id, results)
    print(json.dumps(dict(rows_returned=budget.n, ceiling=CEILING)))
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
