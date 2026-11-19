#!/usr/bin/env python3
"""Energy use by industry: the page file site/data/industry.json (session 8003, chain 501 step D2).

Energy Research Warehouse (ERW). Writes one new page file; no table, no request. The second window (chain 502) builds the
page. The file's shape: docs/state/page_files_regions.md, section 9. Method: docs/methods/industry_page.md.

    python warehouse/derived/industry_page.py                 # site/data/industry.json
    python warehouse/derived/industry_page.py --site-dir DIR  # a trial

Inputs (warehouse/output), each as its publisher printed it, nothing filled:
    eia_mecs_manufacturing                 the 2022 Manufacturing Energy Consumption Survey: fuel by industry (NAICS) and census region, TBtu
    eia_sector_energy_consumption_monthly  the Monthly Energy Review: the industrial sector's consumption by source, monthly since 1973, TBtu
    eia_seds_industrial_annual             the State Energy Data System: the industrial sector's consumption by source, expenditures and price, by state, a year
    eia_seds_state_energy                  the same system's industrial natural gas (NGICB) and electricity (ESICB) by state
    eia_retail_sales_monthly               Form EIA-861M: electricity sold to industrial customers by state, monthly, MWh
    eia_aeo_industrial                     the Annual Energy Outlook's industrial sub-sector tables, energy use by fuel, every case (projections)
"""

import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SITE_FILE = os.path.join(ROOT, "site", "data", "industry.json")
MER = {"TEICBUS": "total", "TNICBUS": "end_use_total", "CLICBUS": "coal", "NNICBUS": "natural_gas", "PAICBUS": "petroleum",
       "REICBUS": "renewables", "ESICBUS": "electricity_retail_sales", "LOICBUS": "electrical_system_losses"}
MER_LABEL = {"total": "total energy consumed by the industrial sector", "end_use_total": "end-use energy consumed (without electrical system losses)",
             "coal": "coal", "natural_gas": "natural gas (without supplemental gaseous fuels)", "petroleum": "petroleum",
             "renewables": "renewable energy", "electricity_retail_sales": "electricity sold to industrial customers",
             "electrical_system_losses": "the industrial sector's share of electrical system energy losses"}
MECS_FUELS = ["fuel_total", "fuel_net_electricity", "fuel_natural_gas", "fuel_coal", "fuel_coke_and_breeze", "fuel_residual_fuel_oil",
              "fuel_distillate_fuel_oil", "fuel_hgl", "fuel_hydrogen", "fuel_other"]
SEDS_FUELS = {"TEICB": "total", "TNICB": "end_use_total", "CLICB": "coal", "PAICB": "petroleum", "REICB": "renewables",
              "WWICB": "wood_and_waste", "HLICB": "hgl", "DFICB": "distillate_fuel_oil", "RFICB": "residual_fuel_oil",
              "PCICB": "petroleum_coke", "LOICB": "electrical_system_losses"}
SEDS_HELD = {"NGICB": "natural_gas", "ESICB": "electricity"}
SEDS_MONEY = {"TEICV": "total", "CLICV": "coal", "PAICV": "petroleum", "NGICV": "natural_gas", "ESICV": "electricity"}


def read(name, cols=None):
    p = os.path.join(OUT, name + ".csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, usecols=cols, dtype=str, keep_default_na=False, engine="pyarrow")
    fh.close()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d


def num(v, nd=3):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), nd)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Energy use by industry, the page file")
    ap.add_argument("--site-dir")
    a = ap.parse_args(argv)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # the Monthly Energy Review: the sector, monthly
    mer = read("eia_sector_energy_consumption_monthly", ["entity", "ts_utc", "value"])
    mer["code"] = mer["entity"].str.split(":").str[1]
    mer = mer[mer["code"].isin(MER)]
    months = sorted(mer["ts_utc"].str.slice(0, 7).unique())
    monthly = {"unit": "TBtu", "months": months, "labels": MER_LABEL, "by_source": {}}
    for code, key in MER.items():
        s = mer[mer["code"] == code].set_index(mer.loc[mer["code"] == code, "ts_utc"].str.slice(0, 7))["value"]
        monthly["by_source"][key] = [num(s.get(m)) for m in months]
    # MECS 2022: industries
    m = read("eia_mecs_manufacturing", ["entity", "variable", "ts_utc", "value", "node", "x_naics", "x_region"])
    m["region"] = m["entity"].str.split(":").str[1].str.split("_").str[0]
    fu = m[m["variable"].isin(MECS_FUELS)]
    inds = {}
    for (naics, node), g in fu.groupby(["x_naics", "node"]):
        r = {"naics": naics, "name": node, "by_region": {}}
        for reg, gg in g.groupby("region"):
            r["by_region"][reg] = {v[len("fuel_"):]: num(x) for v, x in zip(gg["variable"], gg["value"])}
        inds[naics] = r
    us_total = {k: v["by_region"].get("us", {}).get("total") for k, v in inds.items()}
    level3 = sorted([k for k in inds if len(k) == 3 and k.isdigit() and us_total.get(k) is not None], key=lambda k: -us_total[k])
    for i, k in enumerate(level3, 1):
        inds[k]["rank_us_total"] = i
    elec = m[m["variable"].str.startswith("elec_") | m["variable"].str.startswith("gen_")]
    for (naics, reg), g in elec.groupby(["x_naics", "region"]):
        if naics in inds:
            inds[naics].setdefault("electricity_mwh", {})[reg] = {v: num(x, 1) for v, x in zip(g["variable"], g["value"])}
    mecs = {"survey_year": 2022, "unit": "TBtu (fuel), MWh (electricity components)",
            "regions": ["us", "northeast", "midwest", "south", "west"],
            "fuels": [f[len("fuel_"):] for f in MECS_FUELS], "ranked_3_digit": level3,
            "industries": dict(sorted(inds.items())),
            "note": "EIA withholds or does not estimate some cells (codes *, D, NA, Q); such a cell has no figure here. Fuel consumption counts some byproduct fuels twice, as EIA's note to Table 3.2 says."}
    # SEDS by state
    sd = read("eia_seds_industrial_annual", ["entity", "variable", "ts_utc", "value", "unit"])
    sd["sid"], sd["st"] = sd["entity"].str.split(":").str[1], sd["entity"].str.split(":").str[2]
    held = read("eia_seds_state_energy", ["entity", "ts_utc", "value"])
    held["sid"], held["st"] = held["entity"].str.split(":").str[1], held["entity"].str.split(":").str[2]
    held = held[held["sid"].isin(SEDS_HELD)]
    years = sorted(set(sd["ts_utc"].str.slice(0, 4)) | set(held["ts_utc"].str.slice(0, 4)))
    states = {}
    for frame, mapping, kind in ((sd, SEDS_FUELS, "consumption_tbtu"), (held, SEDS_HELD, "consumption_tbtu"), (sd, SEDS_MONEY, "expenditures_usd")):
        f = frame[frame["sid"].isin(mapping)]
        for (sid, st), g in f.groupby(["sid", "st"]):
            vals = dict(zip(g["ts_utc"].str.slice(0, 4), g["value"]))
            states.setdefault(st, {}).setdefault(kind, {})[mapping[sid]] = [num(vals.get(y)) for y in years]   # both tables print TBtu
    price = sd[sd["sid"] == "TEICD"]
    for st, g in price.groupby("st"):
        vals = dict(zip(g["ts_utc"].str.slice(0, 4), g["value"]))
        states.setdefault(st, {})["price_usd_per_mmbtu"] = [num(vals.get(y)) for y in years]
    seds = {"unit": "TBtu; USD; USD/MMBtu", "years": years, "states": dict(sorted(states.items()))}
    # retail sales to industry, monthly by state
    rs = read("eia_retail_sales_monthly", ["entity", "variable", "ts_utc", "value"])
    rs = rs[(rs["variable"] == "retail_sales") & rs["entity"].str.endswith(":IND")]
    rs["st"] = rs["entity"].str.split(":").str[2]
    rmonths = sorted(rs["ts_utc"].str.slice(0, 7).unique())
    sales = {"unit": "MWh", "months": rmonths, "states": {}}
    for st, g in rs.groupby("st"):
        vals = dict(zip(g["ts_utc"].str.slice(0, 7), g["value"]))
        sales["states"][st] = [num(vals.get(mo), 1) for mo in rmonths]
    # the outlook
    ao = read("eia_aeo_industrial", ["entity", "ts_utc", "value", "node", "x_series_id", "x_industry", "x_scenario", "x_scenario_name", "x_history"])
    ayears = sorted(ao["ts_utc"].str.slice(0, 4).unique())
    outlook = {"unit": "TBtu", "projections": True, "release": ao["entity"].iloc[0].split(":")[0].replace("eia_aeo_", "") if len(ao) else None,
               "years": ayears, "cases": dict(sorted(set(zip(ao["x_scenario"], ao["x_scenario_name"])))), "history_years": sorted(ao.loc[ao["x_history"] == "HISTORY", "ts_utc"].str.slice(0, 4).unique()),
               "industries": {}}
    for (ind, node, case), g in ao.groupby(["x_industry", "node", "x_scenario"]):
        vals = dict(zip(g["ts_utc"].str.slice(0, 4), g["value"]))
        outlook["industries"].setdefault(ind, {}).setdefault(node, {})[case] = [num(vals.get(y), 1) for y in ayears]
    doc = {"built": built, "method": "docs/methods/industry_page.md", "license": "public",
           "tables": ["eia_mecs_manufacturing", "eia_sector_energy_consumption_monthly", "eia_seds_industrial_annual", "eia_seds_state_energy",
                      "eia_retail_sales_monthly", "eia_aeo_industrial"],
           "sources": {"monthly": "U.S. Energy Information Administration, Monthly Energy Review (Table 2.4)",
                       "industries": "U.S. Energy Information Administration, 2022 Manufacturing Energy Consumption Survey (Tables 3.2, 11.1, 11.3)",
                       "states": "U.S. Energy Information Administration, State Energy Data System",
                       "electricity_sales": "U.S. Energy Information Administration, Form EIA-861M",
                       "outlook": "U.S. Energy Information Administration, Annual Energy Outlook (industrial sub-sector tables)"},
           "monthly": monthly, "industries": mecs, "states_annual": seds, "electricity_sales_monthly": sales, "outlook": outlook}
    path = os.path.join(a.site_dir, "industry.json") if a.site_dir else SITE_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), allow_nan=False)
    print(f"{os.path.relpath(path, ROOT)}: {os.path.getsize(path):,} bytes; {len(months)} months of the sector, {len(inds)} MECS industries, "
          f"{len(states)} states over {years[0]} to {years[-1]}, {len(rmonths)} months of sales, outlook {len(outlook['industries'])} industries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
