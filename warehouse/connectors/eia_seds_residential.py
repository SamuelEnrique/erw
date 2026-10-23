#!/usr/bin/env python3
"""EIA's State Energy Data System, the residential sector: what each state's households spend on energy, by source, with
their consumption, the average price they pay and the state's population, a year (session 2108, chain 069: what
households spend on energy, in place of BEA's consumption by state, whose downloads BEA's robots file disallows and whose
API needs a key the ERW does not hold).

Energy Research Warehouse (ERW) connector. One series table from the U.S. Energy Information Administration's API v2,
route seds (annual; this table from 1990):

    https://api.eia.gov/v2/seds/data/?frequency=annual&data[]=value&facets[seriesId][]=<id>...&start=1990

    eia_seds_residential_annual   entity eia_seds_res:<seriesId>:<state>; variable expenditures (USD: EIA's million
               dollars times 1,000,000), consumption (TBtu: billion Btu times 0.001), price (USD/MMBtu) or population
               (count: thousands times 1,000); ts_utc the year's 1 January; freq P1Y; geo US-<state>, or US for the
               nation; node the series' name as EIA gives it; x_series the series id; x_source the energy source

    TERCV  total energy expenditures, residential     ESRCV  electricity    NGRCV  natural gas    PARCV  all petroleum
    DFRCV  distillate fuel oil     HLRCV  hydrocarbon gas liquids (propane)     KSRCV  kerosene     WDRCV  wood
    TERCB  total energy consumed, residential (billion Btu)     TERCD  total energy average price, residential
    TPOPP  resident population (thousand)

SEDS's figures are EIA's estimates, as its technical notes describe them; a withheld or missing value has no row, and
nothing is filled. A series that returns no row, a unit not in the map or a key given twice stops the run. The table
does not repeat eia_seds_state_energy's series (ESTCV and TETCV, all sectors, are there).

    python warehouse/connectors/eia_seds_residential.py [--offline | --fresh] [--out-dir DIR]

Ceiling: 10 requests a run (pages of 5,000, 3 seconds apart; a 429 or a 5xx asked once more after 60 seconds; a saved
page reused unless --fresh). api.eia.gov has no robots file (every path answers a missing key). License: public (EIA,
record 1 of license_reads.csv; cite "U.S. Energy Information Administration, State Energy Data System").
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

TABLE = "eia_seds_residential_annual"
CONNECTOR = "eia_seds_residential"
SOURCE = "eia:seds_residential"
HOST = "api.eia.gov"
API = "https://api.eia.gov/v2/seds/"
PAGE = "https://www.eia.gov/state/seds/"
CEILING, PAUSE, RETRY_WAIT = 10, 3, 60
FIRST = "1990"
# series id: (variable, the energy source)
SERIES = {"TERCV": ("expenditures", "total"), "ESRCV": ("expenditures", "electricity"), "NGRCV": ("expenditures", "natural_gas"),
          "PARCV": ("expenditures", "petroleum"), "DFRCV": ("expenditures", "distillate_fuel_oil"), "HLRCV": ("expenditures", "hgl"),
          "KSRCV": ("expenditures", "kerosene"), "WDRCV": ("expenditures", "wood"), "TERCB": ("consumption", "total"),
          "TERCD": ("price", "total"), "TPOPP": ("population", "")}
UNITS = {"billion btu": ("TBtu", 0.001), "dollars per million btu": ("USD/MMBtu", 1.0), "million dollars": ("USD", 1e6),
         "thousand": ("count", 1000.0)}
X_COLS = ["x_series", "x_source"]


def unit_of(u):
    k = str(u).strip().lower()
    if k not in UNITS:
        raise RuntimeError(f"a unit not in the map: {u!r}")
    return UNITS[k]


def rows(data, url, retrieved):
    out = []
    for r in data:
        sid = r["seriesId"]
        if sid not in SERIES:
            raise RuntimeError(f"a series not asked for: {sid}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        unit, factor = unit_of(r.get("unit", ""))
        var, src = SERIES[sid]
        st = r["stateId"]
        out.append(dict(entity=f"eia_seds_res:{sid}:{st}", variable=var, ts_utc=f"{int(r['period'])}-01-01T00:00:00Z",
                        value=round(float(v) * factor, 6), unit=unit, freq="P1Y", geo="US" if st == "US" else f"US-{st}", market="",
                        node=r.get("seriesDescription", ""), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage="",
                        x_series=sid, x_source=src))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA State Energy Data System: the residential sector's expenditures by source and state")
    ap.add_argument("--offline", action="store_true", help="the pages from warehouse/raw only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask every page again, even one saved in warehouse/raw")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    asked = [0]

    class Saved:   # a saved page, answering as a response does
        def __init__(self, content, url):
            self.content, self.url = content, url

        def json(self):
            return json.loads(self.content)

    def get(params):
        url = requests.Request("GET", API + "data/", params=params).prepare().url
        hit = None if args.fresh else ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {ip.redact(url)}")
            return Saved(hit[0], url)
        if args.offline:
            raise RuntimeError(f"offline: {ip.redact(url)} is not in warehouse/raw/{CONNECTOR}/")
        for attempt in (1, 2):
            if asked[0] >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached")
            asked[0] += 1
            time.sleep(PAUSE)
            r = requests.get(url, timeout=120)
            if r.status_code < 500 and r.status_code != 429:
                r.raise_for_status()
                return r
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frames, offset = [], 0
        while True:
            r = get({"api_key": key, "frequency": "annual", "data[]": "value", "facets[seriesId][]": list(SERIES), "start": FIRST,
                     "sort[0][column]": "period", "sort[0][direction]": "asc", "sort[1][column]": "seriesId",
                     "sort[1][direction]": "asc", "sort[2][column]": "stateId", "sort[2][direction]": "asc",
                     "length": 5000, "offset": offset})
            resp = r.json()["response"]
            frames.append(rows(resp["data"], ip.redact(r.url.split("&offset")[0]), retrieved))
            offset += len(resp["data"])
            if offset >= int(resp["total"]) or not resp["data"]:
                break
        if offset != int(resp["total"]):
            raise RuntimeError(f"{offset} rows read, the API says {resp['total']}")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        none = sorted(set(SERIES) - set(s.x_series))
        if none:
            raise RuntimeError(f"series with no row: {none}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        header = [
            "Energy Research Warehouse (ERW): EIA State Energy Data System, the residential sector: households' energy expenditures by source, "
            "their consumption and average price, and each state's population, a year (session 2108)",
            "Shape: series (docs/datastandard.md v0). entity eia_seds_res:<seriesId>:<state>; variable expenditures (USD), consumption (TBtu), "
            "price (USD/MMBtu) or population (count); ts_utc the year's 1 January; freq P1Y; geo US-<state> or US; node the series' name; "
            f"x_series; x_source. Series: {', '.join(SERIES)}. Million dollars as USD, billion Btu as TBtu, thousands as a count.",
            f"EIA's estimates as SEDS publishes them (its technical notes); nothing is filled; a withheld value has no row. Years "
            f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}. The states and DC, and the nation. Wood's expenditures are EIA's estimate of "
            "purchased wood. Expenditures are nominal dollars.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_seds_residential.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, State Energy Data System (API v2, route seds), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&facets[seriesId][]=<id>&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, State Energy Data System").',
        ]
        ip.write_snapshot(s, TABLE, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="State Energy Data System (API v2): the residential sector's expenditures, consumption and price, and population",
                                    report_url=PAGE, document_list=API, license="public", tables=[TABLE])])
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s['entity'].nunique():,} series by state, {s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}; "
              f"{asked[0]} requests")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
