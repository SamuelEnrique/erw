#!/usr/bin/env python3
"""The forecast tool's parameters as a warehouse table (session 3938, chain 267; request 4 of
docs/state/data_requests_forecast.md).

Energy Research Warehouse (ERW). Writes warehouse/output/forecast_tool_parameters.csv (series shape) from the three files the
forecast tool (/impact) reads, each written by chain 239 (lab-desktop window 4) with every number's source:

    site/data/forecast/eia_capex.json     EIA's overnight capital cost by technology, state and city (2023 dollars), each
                                          case's construction months, operating life, size and heat rate: the capital
                                          cost study for AEO2025 (Sargent & Lundy), Appendix A
    site/data/forecast/jedi_taxable.json  the share of construction spending that bears sales and use tax, by technology:
                                          JEDI's own taxable base (NLR's JEDI models)
    site/data/forecast/gas.json           the gas plant's fuel: the heat rate (the same study), JEDI's default capacity
                                          factor, the 2025 Henry Hub mean (eia_steo_forecasts) and EIA's heat content

Nothing is read again and no request is made: the files are the record. A value a file does not give (geothermal's
taxable share; geothermal's cost in the states the study does not list) is not written. Entities forecast:<file>:<
technology>:<place>; place us (the case), a state's two-letter code (the study's state figure) or <state>_<city>.

    python warehouse/derived/forecast_tool_parameters.py              # the table (data lock)
    python warehouse/derived/forecast_tool_parameters.py --out-dir D  # a trial
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "forecast_tool_parameters"   # three parts (the validator's file name pattern)
FOLDER = os.path.join(ROOT, "site", "data", "forecast")
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/forecast.md"
SOURCES = {
    "capex": ("eia:capital_cost_aeo2025", "U.S. Energy Information Administration (EIA)",
              "Capital Cost and Performance Characteristic Estimates for Utility Scale Electric Power Generating Technologies (AEO2025), Appendix A"),
    "jedi": ("nlr:jedi_models", "National Laboratory of the Rockies (NLR, formerly NREL)", "JEDI models (Jobs and Economic Development Impact)"),
    "gas": ("erw:forecast_gas", "Energy Research Warehouse (ERW)", "The forecast tool's gas fuel defaults (site/data/forecast/gas.json)"),
}
X_COLS = ["x_technology", "x_place", "x_dollar_year", "x_detail"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def row(entity, variable, value, unit, src, url, retrieved, tech, place, dollar_year="", detail=""):
    return dict(entity=entity, variable=variable, ts_utc=f"{dollar_year or 2026}-01-01T00:00:00Z", value=float(value), unit=unit, freq="",
                geo="US", market="", node="", source=src, source_url=url, retrieved_at=retrieved, vintage="",
                x_technology=tech, x_place=place, x_dollar_year=str(dollar_year), x_detail=detail)


def build(folder=FOLDER):
    capex = json.load(open(os.path.join(folder, "eia_capex.json"), encoding="utf-8"))
    taxable = json.load(open(os.path.join(folder, "jedi_taxable.json"), encoding="utf-8"))
    gas = json.load(open(os.path.join(folder, "gas.json"), encoding="utf-8"))
    out = []
    src, url = SOURCES["capex"][0], capex["source_url"]
    when = str(capex.get("written_at", ""))
    for tech, t in capex["technologies"].items():
        dy = t.get("dollar_year", "")
        base = f"forecast:eia_capex:{tech}"
        detail = f"{t.get('table', '')}; case {t.get('case', '')}; basis {t.get('basis', '')}"
        out.append(row(f"{base}:us", "overnight_cost", t["base_usd_per_kw"], "USD/kW", src, url, when, tech, "us", dy, detail))
        out.append(row(f"{base}:us", "construction_months", t["construction_months"], "month", src, url, when, tech, "us", "", detail))
        out.append(row(f"{base}:us", "case_mw", t["case_mw"], "MW", src, url, when, tech, "us", "", detail))
        out.append(row(f"{base}:us", "operating_life", t["operating_life_years"], "year", src, url, when, tech, "us", "", detail))
        if t.get("heat_rate_btu_per_kwh_hhv") not in (None, ""):
            out.append(row(f"{base}:us", "heat_rate", float(t["heat_rate_btu_per_kwh_hhv"]) / 1000.0, "MMBtu/MWh", src, url, when, tech, "us", "",
                           detail + f"; {t['heat_rate_btu_per_kwh_hhv']} Btu/kWh (HHV) as printed"))
        for st, s in t.get("states", {}).items():
            if s.get("usd_per_kw") not in (None, ""):
                out.append(row(f"{base}:{st}", "overnight_cost", s["usd_per_kw"], "USD/kW", src, url, when, tech, st, dy, f"{s.get('state', '')}: the study's state figure"))
            for c in s.get("cities", []):
                place = f"{st}_{slug(c['city'])}"
                out.append(row(f"{base}:{place}", "overnight_cost", c["usd_per_kw"], "USD/kW", src, url, when, tech, place, dy, f"{c['city']}, {s.get('state', '')}"))
                out.append(row(f"{base}:{place}", "location_variation", c["location_variation"], "ratio", src, url, when, tech, place, "", f"{c['city']}, {s.get('state', '')}"))
    src = SOURCES["jedi"][0]
    for tech, t in taxable["technologies"].items():
        if t.get("taxable_share") in (None, ""):
            continue
        out.append(row(f"forecast:jedi_taxable:{tech}:us", "taxable_share", t["taxable_share"], "ratio", src, "https://www.nlr.gov/analysis/jedi/models", "",
                       tech, "us", "", f"{t.get('file', '')}: {t.get('arithmetic', '')}"))
    src = SOURCES["gas"][0]
    gwhen = str(gas.get("written_at", ""))
    out.append(row("forecast:gas:natural_gas:us", "heat_rate", float(gas["heat_rate_btu_per_kwh"]) / 1000.0, "MMBtu/MWh", src, METHOD_URL, gwhen, "natural_gas", "us", "",
                   f"{gas['heat_rate_btu_per_kwh']} Btu/kWh: {gas['heat_rate_source']}"))
    out.append(row("forecast:gas:natural_gas:us", "capacity_factor", gas["capacity_factor"], "ratio", src, METHOD_URL, gwhen, "natural_gas", "us", "",
                   json.dumps(gas["capacity_factor_source"], ensure_ascii=False)))
    out.append(row("forecast:gas:natural_gas:us", "fuel_price", gas["price_usd_per_mmbtu"], "USD/MMBtu", src, METHOD_URL, gwhen, "natural_gas", "us", "2025",
                   gas["price_source"]))
    out.append(row("forecast:gas:natural_gas:us", "heat_content", gas["btu_per_cf"], "Btu/ft3", src, METHOD_URL, gwhen, "natural_gas", "us", "",
                   json.dumps(gas["btu_per_cf_source"], ensure_ascii=False) if isinstance(gas["btu_per_cf_source"], (dict, list)) else str(gas["btu_per_cf_source"])))
    d = pd.DataFrame(out)
    d["retrieved_at"] = d["retrieved_at"].where(d["retrieved_at"] != "", gwhen)
    if d.duplicated(["entity", "variable"]).any():
        raise RuntimeError(f"an (entity, variable) twice: {d[d.duplicated(['entity', 'variable'])].head(2).to_dict('records')}")
    return d, capex, taxable, gas


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the forecast tool's parameters as a table (session 3938)")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    d, capex, taxable, gas = build()
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        cols = ip.SERIES_COLS + X_COLS
        header = [
            "Energy Research Warehouse (ERW): the forecast tool's parameters (EIA's capital cost by technology, state and city; JEDI's taxable share; the gas plant's fuel defaults) (session 3938)",
            "Shape: series (docs/datastandard.md v0). entity forecast:<file>:<technology>:<place> (place us, a state code, or <state>_<city>); "
            "variables overnight_cost (USD/kW, x_dollar_year), construction_months, case_mw, operating_life (year), heat_rate (MMBtu/MWh), location_variation and "
            "taxable_share and capacity_factor (ratio), fuel_price (USD/MMBtu, the 2025 mean), heat_content (Btu/ft3); ts_utc the dollar year's "
            "first day where the value has one, else 2026-01-01; no freq (a parameter, not a time series).",
            f"Rows: {len(d)}. Read from site/data/forecast/eia_capex.json, jedi_taxable.json and gas.json (chain 239, lab-desktop window 4, "
            f"13 November 2026); nothing read again, no request. Geothermal's taxable share (JEDI's model has no sales tax line) and its cost in "
            f"the {len(capex['technologies'].get('geothermal', {}).get('not_given', []))} states the study does not list are not written.",
            f"Source: {SOURCES['capex'][0]} {SOURCES['capex'][1]}, {SOURCES['capex'][2]}, {capex['source_url']}; {SOURCES['jedi'][0]} "
            f"{SOURCES['jedi'][1]}, {SOURCES['jedi'][2]}, https://www.nlr.gov/analysis/jedi/models; {SOURCES['gas'][0]}: the study's heat rate, "
            "JEDI's default capacity factor, eia_steo_forecasts' NGHHUUS and EIA's heat content",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/{NAME}.py; retrieved_at is when each file was written",
            f"Method: {METHOD_URL}",
            "License: public. EIA's study is a work of the U.S. government; NLR's data terms grant use and copying with its notice kept "
            "(jedi_taxable.json's notice); the gas defaults are the ERW's arithmetic over them.",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)   # written whole from the files each run
        ip.write_csv(d[cols], NAME, header, log, cols=cols, key=["entity", "variable", "ts_utc"])
        if not a.out_dir:
            ip.update_sources([dict(source=s, publisher=p, report=r, report_url=METHOD_URL, document_list="", license="public", tables=[NAME])
                               for s, p, r in SOURCES.values()])
        print(f"{NAME}: {len(d)} rows")
    except Exception as exc:
        print(f"{NAME} FAILED: {type(exc).__name__}: {exc}")
        log(traceback.format_exc())
        return 1
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
