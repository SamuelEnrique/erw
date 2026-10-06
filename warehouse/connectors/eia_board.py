#!/usr/bin/env python3
"""EIA series the price board adds: retail gasoline and diesel by region, crude oil by stream, and what power plants
paid for coal and gas (session 132, approved pull).

Energy Research Warehouse (ERW) connector. Three series tables from EIA's open data API (https://api.eia.gov/v2/),
each from 2019-01-01:

| table                           | route                                        | freq    | unit                              |
|---------------------------------|----------------------------------------------|---------|-----------------------------------|
| eia_regional_retail_fuel_prices | petroleum/pri/gnd (products EPMR, EPD2D)     | weekly  | USD/gal                           |
| eia_crude_stream_prices         | petroleum/pri/dfp2, land2, imc2, rac2        | monthly | USD/bbl                           |
| eia_power_plant_fuel_costs      | electricity/electric-power-operational-data  | monthly | USD/MMBtu, USD/short_ton, USD/Mcf |

    python warehouse/connectors/eia_board.py                       # every table
    python warehouse/connectors/eia_board.py --table eia_crude_stream_prices
    python warehouse/connectors/eia_board.py --out-dir DIR          # a trial: the tables under DIR

RETAIL FUEL: regular gasoline (all formulations) and No. 2 diesel, retail, every area EIA publishes by the week: the
US, the PADDs and sub-PADDs, and the states and cities EIA lists. The entity is EIA's series id; node is EIA's area
name. A weekly value sits at 00:00:00Z of EIA's date (the Monday of the survey).

CRUDE BY STREAM: EIA publishes two crude grades by the day (WTI and Brent, eia_fuel_spot_prices) and no others. By the
month it publishes first purchase prices of nine domestic streams (dfp2), landed and F.O.B. costs of the imported
streams it names (land2, imc2) and refiners' acquisition cost by region (rac2). These are averages of the month, not
spot prices. variable says which: first_purchase_price, landed_cost, fob_cost, refiner_acquisition_cost. node is the
stream or area, from EIA's description. A month EIA lists with no value (withheld, or not yet reported) is not written.

POWER PLANT FUEL COSTS: the average cost of coal and of natural gas delivered to the electric power sector (EIA's
sector 98), every location EIA lists (the US, census divisions, states), from Form EIA-923: cost_per_mmbtu (USD/MMBtu,
both fuels), and the same cost per physical unit, cost_per_short_ton (coal) and cost_per_mcf (gas). The entity is
eia:plant_fuel_cost:<location>:<fueltypeid>. EIA withholds a state's cost when few plants report, and writes a cost of
exactly 0 where a state took no deliveries that month (California's coal, for one, in every month): no row is written
for either. A negative cost is kept as EIA reports it (gas delivered in New Mexico and Arizona in 2024 to 2026).

Ceiling: 1,500,000 rows for session 132's pulls in all (the rows the API returns, the session's probes included).
The source ids of the retail and first purchase routes carry a suffix (:regional, :streams) so the registry rows of the older tables
that read the same routes (eia_retail_fuel_prices, eia_crude_first_purchase_prices) stay as they are. Values: EIA's, unchanged. Nothing is filled. EIA data are in the public domain (credit: U.S. Energy Information
Administration); its retail survey and Form EIA-923 are EIA's own collections.
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
START = {"weekly": "2019-01-01", "monthly": "2019-01"}
CEILING = 1_500_000
EXPLORED = 1_300         # session 132's probes of these routes and of the spot and futures routes
PAGE = 5000
PUBLISHER = "U.S. Energy Information Administration (EIA)"
FREQ = {"weekly": "P1W", "monthly": "P1M"}
STALE = {"weekly": 21, "monthly": 150}     # days: the newest date must be this recent, or the table is not written
STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())

TABLES = {
    "eia_regional_retail_fuel_prices": dict(
        freq="weekly", title="EIA's weekly retail prices of regular gasoline and No. 2 diesel, by region, state and city, from 2019",
        parts=[dict(source="eia:petroleum/pri/gnd:regional", route="petroleum/pri/gnd", page="https://www.eia.gov/petroleum/gasdiesel/",
                    report="Gasoline and Diesel Fuel Update (weekly retail prices)", facets=[("product", "EPMR"), ("product", "EPD2D")],
                    variable="retail_price", units={"$/GAL": "USD/gal"})],
    ),
    "eia_crude_stream_prices": dict(
        freq="monthly", title="EIA's monthly crude oil prices by stream and area: first purchase prices, landed and F.O.B. costs of imports, refiners' acquisition cost, from 2019",
        parts=[
            dict(source="eia:petroleum/pri/dfp2:streams", route="petroleum/pri/dfp2", page="https://www.eia.gov/dnav/pet/pet_pri_dfp2_k_m.htm",
                 report="Domestic Crude Oil First Purchase Prices for Selected Crude Streams", facets=[], variable="first_purchase_price", units={"$/BBL": "USD/bbl"}),
            dict(source="eia:petroleum/pri/land2", route="petroleum/pri/land2", page="https://www.eia.gov/dnav/pet/pet_pri_land2_k_m.htm",
                 report="Landed Costs of Imported Crude for Selected Crude Streams", facets=[], variable="landed_cost", units={"$/BBL": "USD/bbl"}),
            dict(source="eia:petroleum/pri/imc2", route="petroleum/pri/imc2", page="https://www.eia.gov/dnav/pet/pet_pri_imc2_k_m.htm",
                 report="F.O.B. Costs of Imported Crude Oil for Selected Crude Streams", facets=[], variable="fob_cost", units={"$/BBL": "USD/bbl"}),
            dict(source="eia:petroleum/pri/rac2", route="petroleum/pri/rac2", page="https://www.eia.gov/dnav/pet/pet_pri_rac2_dcu_nus_m.htm",
                 report="Refiner Acquisition Cost of Crude Oil", facets=[], variable="refiner_acquisition_cost", units={"$/BBL": "USD/bbl"}),
        ],
    ),
    "eia_power_plant_fuel_costs": dict(
        freq="monthly", title="EIA's monthly average cost of coal and natural gas delivered to the electric power sector, by location, from 2019 (Form EIA-923)",
        parts=[dict(source="eia:electricity/electric-power-operational-data:cost", route="electricity/electric-power-operational-data",
                    page="https://www.eia.gov/electricity/data/browser/", report="Electric power operational data: receipts and cost of fossil fuels (Form EIA-923)",
                    facets=[("sectorid", "98"), ("fueltypeid", "COW"), ("fueltypeid", "NG")], epod=True)],
    ),
}
EPOD_COLS = {"cost-per-btu": ("cost_per_mmbtu", {"dollars per million Btu": "USD/MMBtu"}),
             "cost": (None, {"dollars per short tons": ("cost_per_short_ton", "USD/short_ton"), "dollars per Mcf": ("cost_per_mcf", "USD/Mcf")})}


class Budget:
    """The rows the API has returned to this run, against the session's ceiling."""
    def __init__(self):
        self.n = EXPLORED

    def add(self, rows):
        self.n += rows
        if self.n > CEILING:
            raise RuntimeError(f"{self.n:,} rows read, over the ceiling of {CEILING:,}: stopped, nothing more is written")


def fetch(part, freq, key, log, budget):
    """Every row of one route from START, as the API returns it. Each row carries its page's address (no key) and time."""
    out, offset = [], 0
    data = ["cost-per-btu", "cost"] if part.get("epod") else ["value"]
    sort = ["period", "location", "fueltypeid"] if part.get("epod") else ["period", "series"]
    while True:
        params = [("frequency", freq)] + [(f"data[{i}]", d) for i, d in enumerate(data)] + [(f"facets[{f}][]", v) for f, v in part["facets"]]
        params += [("start", START[freq])]
        for i, c in enumerate(sort):
            params += [(f"sort[{i}][column]", c), (f"sort[{i}][direction]", "asc")]
        params += [("offset", str(offset)), ("length", str(PAGE))]
        public = requests.Request("GET", API + part["route"] + "/data/", params=params).prepare().url

        def call():
            r = requests.get(public, params=[("api_key", key)], timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"EIA {part['route']} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
            return r
        r = ip.with_retries(f"EIA {part['route']} offset {offset}", call, log)
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        ip.RAW.alias(public, r.content, r.headers)      # the answer is kept under the address without the key
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


def ts_of(period, freq):
    return (period + "-01" if freq == "monthly" else period) + "T00:00:00Z"


def number(v):
    """EIA's value as a number, or None when EIA lists the date with no value. A value that is neither stops the pull."""
    if v is None or str(v).strip() in ("", "W", "NA", "--", "null", "None"):
        return None
    return float(v)


def geo_of(code):
    """EIA's area code as the standard's geo: the US, a state, else empty (a PADD, a census division, a city)."""
    code = str(code or "")
    if code in ("NUS", "US"):
        return "US"
    if code in STATES:
        return f"US-{code}"
    if re.fullmatch(r"S[A-Z]{2}", code) and code[1:] in STATES:
        return f"US-{code[1:]}"
    return ""


def name_of(description):
    """The stream or area of a crude series, from EIA's description: the words before the measure."""
    d = re.sub(r"\s*\(Dollars per Barrel\)\s*$", "", str(description))
    d = re.sub(r"^U\.S\. (Landed|FOB) Costs of ", "", d)
    d = re.sub(r"\s+(First Purchase Price|Crude Oil)$", "", d)
    return d.strip()


def shape_series(part, rows, freq):
    """The rows of a route that has series ids, as the table's rows; dates with no value are left out and counted."""
    out, empty = [], 0
    for r in rows:
        unit = part["units"].get(r.get("units"))
        if unit is None:
            raise RuntimeError(f"{part['route']} {r.get('series')}: EIA unit {r.get('units')!r}, expected one of {sorted(part['units'])}")
        v = number(r.get("value"))
        if v is None:
            empty += 1
            continue
        node = r.get("area-name") if part["variable"] == "retail_price" else name_of(r.get("series-description"))
        out.append(dict(entity=f"eia:{r['series']}", variable=part["variable"], ts_utc=ts_of(r["period"], freq), value=v, unit=unit, freq=FREQ[freq],
                        geo=geo_of(r.get("duoarea")), market="", node=str(node or "").strip(), source=part["source"], source_url=r["_url"],
                        retrieved_at=r["_retrieved"], vintage=""))
    return out, empty


def shape_epod(part, rows, freq):
    """The cost rows of the electric power operational data: one row per location, fuel, month and measure held."""
    out, empty = [], 0
    for r in rows:
        base = dict(entity=f"eia:plant_fuel_cost:{r['location']}:{r['fueltypeid']}", ts_utc=ts_of(r["period"], freq), freq=FREQ[freq], geo=geo_of(r["location"]),
                    market="", node=str(r.get("stateDescription") or r["location"]).strip(), source=part["source"], source_url=r["_url"], retrieved_at=r["_retrieved"], vintage="")
        for col, (variable, units) in EPOD_COLS.items():
            v = number(r.get(col))
            if v is None or v == 0:     # EIA writes a cost of exactly 0 for a state and month with no deliveries: not a price
                empty += 1
                continue
            u = units.get(r.get(f"{col}-units"))
            if u is None:
                raise RuntimeError(f"{part['route']} {base['entity']}: EIA unit {r.get(col + '-units')!r} for {col}")
            var, unit = (variable, u) if variable else u
            out.append(dict(base, variable=var, value=v, unit=unit))
    return out, empty


def build(name, cfg, key, run_id, log, budget):
    freq = cfg["freq"]
    frames, empty, counts = [], 0, []
    for part in cfg["parts"]:
        rows = fetch(part, freq, key, log, budget)
        shaped, n_empty = (shape_epod if part.get("epod") else shape_series)(part, rows, freq)
        empty += n_empty
        counts.append(f"{part['route']}: {len(rows):,} rows returned, {len(shaped):,} values")
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
    n_series = table[["entity", "variable"]].drop_duplicates().shape[0]
    header = [
        f"Energy Research Warehouse (ERW): {cfg['title']} (session 132)",
        f"Shape: series (docs/datastandard.md v0). freq {FREQ[freq]}; ts_utc is EIA's date at 00:00:00Z (a weekly value's is EIA's survey Monday, a monthly value's the first day of the month). node is EIA's area or stream name. Variables: "
        + ", ".join(sorted(set(table["variable"]))) + ". Units per row.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_board.py",
        f"Run log: warehouse/output/logs/eia_board_{run_id}.log",
        "Raw files: warehouse/raw/eia_board/ (not in git; each run's manifest.csv lists each answer and its address, without the key)",
    ]
    for part in cfg["parts"]:
        header.append(f"Source: {part['source']} EIA, {part['report']}, {part['page']}")
        header.append(f"  access: {API}{part['route']}/data/ (frequency {freq}, from {START[freq]}" + ("".join(f", {f}={v}" for f, v in part["facets"])) + ")")
    header += [
        f"Series: {n_series}, newest date {newest.date()}. " + "; ".join(counts) + f". Dates or measures EIA lists with no value (withheld or not yet reported), not written: {empty}.",
        "Values are EIA's, unchanged. Nothing is filled.",
        "License: public. U.S. government publications are in the public domain (EIA, Copyrights and Reuse); these are EIA's own surveys. Credit: U.S. Energy Information Administration.",
    ]
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if os.path.exists(path):
        os.remove(path)     # the whole history from 2019 is read each run, so EIA's revisions are picked up
    ip.write_csv(table[ip.SERIES_COLS], name, header, log)
    return table, [dict(source=p["source"], publisher=PUBLISHER, report=p["report"], report_url=p["page"], document_list=API + p["route"] + "/",
                        license="public", tables=[name]) for p in cfg["parts"]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA series the price board adds (session 132)")
    ap.add_argument("--table", choices=sorted(TABLES), action="append")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia_board_{run_id}.log"))
    results, budget = [], Budget()
    try:
        key = ip.load_key("EIA_API_KEY", log)
        ip.RAW.open("eia_board", run_id)
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED before any request:\n{tb}")
        print(f"eia_board FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
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
        ip.write_status("eia_board", run_id, results)
    print(json.dumps(dict(rows_returned=budget.n, ceiling=CEILING)))
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
