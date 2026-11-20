#!/usr/bin/env python3
"""ERW: every state on one page, the page files site/data/states/<st>.json and states/index.json (session 8014, chain 581 part B).

Energy Research Warehouse (ERW). Writes new page files only; no table, no request. Contract:
docs/state/page_files_states.md. Method: docs/methods/states_page.md. For each of the fifty states, the District of
Columbia and the United States as a whole: what it generates by source month by month since 2001; what its homes,
businesses and industry buy and what EIA says they pay; its plants, its capacity by source and what is planned to come
and go; carbon dioxide from power; natural gas used and produced; total energy by source and sector; which balancing
authorities and which of the seven grids serve its people; its large-load law and its severance tax where the ERW
holds one. Every part names its ERW table, its vintage and its source. A part a source does not cover for a state is
present with a null and the reason, never a zero. The only arithmetic is sums, shares, twelve-month windows and one
product the method names (revenue as EIA's sales times EIA's average price).

    python warehouse/derived/states_page.py                    # site/data/states/
    python warehouse/derived/states_page.py --site-dir DIR     # a trial
    python warehouse/derived/states_page.py --only CA TX       # a trial of some states (index.json not written)
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SITE = os.path.join(ROOT, "site", "data", "states")
METHOD = "docs/methods/states_page.md"
STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}
PLACES = dict(STATES, US="United States")
GEN_SOURCES = ["coal", "natural_gas", "nuclear", "hydro", "wind", "solar", "other_renewables", "oil_and_other", "not_itemized"]
SECTORS = {"RES": "residential", "COM": "commercial", "IND": "industrial", "TRA": "transportation", "ALL": "all"}
CO2_FUELS = {"ALL": "all", "COL": "coal", "NG": "natural_gas", "PET": "petroleum", "OTH": "other"}
GAS_USE = ["consumption_residential", "consumption_commercial", "consumption_industrial", "consumption_electric_power"]
SEDS_SOURCES = {"TETCB": "total", "CLTCB": "coal", "NGTCB": "natural_gas", "PATCB": "petroleum", "NUETB": "nuclear",
                "RETCB": "renewables", "ESTCB": "electricity_retail_sales"}
SEDS_SECTORS = {"TERCB": "residential", "TEICB": "industrial"}
DISPOSITION = ["total_net_generation", "full_service_providers", "energy_only_providers", "estimated_losses",
               "net_interstate_trade", "total_international_imports", "total_international_exports"]
GRIDS = {"CISO": "CAISO", "ERCO": "ERCOT", "ISNE": "ISO-NE", "MISO": "MISO", "NYIS": "NYISO", "PJM": "PJM", "SWPP": "SPP"}
SRC = {
    "generation": "U.S. Energy Information Administration, Electric Power Monthly (Form EIA-923), net generation by state and source, grouped by the ERW (docs/methods/generation_mix.md)",
    "retail": "U.S. Energy Information Administration, Form EIA-861M, retail sales and average price by state and sector",
    "plants": "U.S. Energy Information Administration, Preliminary Monthly Electric Generator Inventory (Form EIA-860M)",
    "co2": "U.S. Energy Information Administration, State Electricity Profiles, emissions by state by fuel",
    "gas": "U.S. Energy Information Administration, Natural Gas Monthly, consumption by end use and production by state",
    "seds": "U.S. Energy Information Administration, State Energy Data System",
    "disposition": "U.S. Energy Information Administration, State Electricity Profiles, source and disposition",
    "serving": "U.S. Census Bureau county population estimates, and Form EIA-861's utilities and balancing authorities by county, as the ERW's table eia_county_region joins them",
    "laws": "The ERW's large-load research files, each law read at its legislature's or regulator's own page",
    "severance": "The ERW's severance tool's rules file (site/data/severance_rules.json), each rate cited to its state's page",
}


def read(name, cols=None):
    p = os.path.join(OUT, name + ".csv")
    if not os.path.exists(p):
        raise SystemExit(f"states_page: no table {name} at {p}")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, usecols=cols, dtype=str, keep_default_na=False, engine="pyarrow")
    fh.close()
    if "value" in d.columns:
        d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d


def num(v, nd=1):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(f) else round(f, nd)


def month_range(first, last):
    out, y, m = [], int(first[:4]), int(first[5:7])
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def series_by(frame, keycol, months, nd=1):
    """{key: [value or None for each month]} from a frame of key, month, value."""
    out = {}
    for k, g in frame.groupby(keycol):
        vals = dict(zip(g["month"], g["value"]))
        out[k] = [num(vals.get(mo), nd) for mo in months]
    return out


def whole_years(months, arrays):
    """The years whose twelve months all carry a figure in every array that has any figure that year; sums by year."""
    years = sorted({m[:4] for m in months})
    out = {}
    for k, arr in arrays.items():
        out[k] = []
        for y in years:
            idx = [i for i, m in enumerate(months) if m[:4] == y]
            vals = [arr[i] for i in idx]
            out[k].append(round(sum(v for v in vals if v is not None), 1) if len(idx) == 12 and all(v is not None for v in vals) else None)
    return years, out


def build_generation(gen, st):
    g = gen[gen["st"] == st]
    if g.empty:
        return {"table": "state_generation_mix_monthly", "months": None, "reason": f"EIA prints no net generation for {PLACES[st]} in the table"}
    months = month_range(g["month"].min(), g["month"].max())
    by = series_by(g, "src", months, 1)
    by = {k: by.get(k, [None] * len(months)) for k in GEN_SOURCES}
    total = [round(sum(v for v in col if v is not None), 1) if any(v is not None for v in col) else None for col in zip(*by.values())]
    last = months[-12:]
    # a source with no figure in any of the twelve months is a null (EIA prints nothing for it there), never a zero
    sums = {k: (sum(v for v in by[k][-12:] if v is not None) if any(v is not None for v in by[k][-12:]) else None) for k in GEN_SOURCES}
    tot12 = sum(v for v in sums.values() if v is not None)
    years, annual = whole_years(months, {**by, "total": total})
    return {
        "table": "state_generation_mix_monthly", "vintage": months[-1], "source": SRC["generation"], "unit": "MWh",
        "months": months, "by_source": by, "total": total,
        "years": years, "annual": annual,
        "last12": {"from": last[0], "to": last[-1], "total_mwh": round(tot12, 1),
                   "mwh": {k: (round(v, 1) if v is not None else None) for k, v in sums.items()},
                   "share_pct": {k: (round(100 * v / tot12, 2) if tot12 and v is not None else None) for k, v in sums.items()}},
        "hourly": None,
        "hourly_reason": "No public source gives a state's generation by the hour; the hourly picture is by balancing authority, in the Grid tool.",
    }


def build_retail(sales, price, cust, st):
    s, p = sales[sales["st"] == st], price[price["st"] == st]
    if s.empty:
        return {"table": "eia_retail_sales_monthly", "months": None, "reason": f"EIA prints no retail sales for {PLACES[st]} in the table"}
    months = month_range(min(s["month"].min(), p["month"].min() if len(p) else s["month"].min()), max(s["month"].max(), p["month"].max() if len(p) else s["month"].max()))
    sl = series_by(s, "sector", months, 1)
    pr = series_by(p, "sector", months, 2)
    sl = {SECTORS[k]: sl.get(k, [None] * len(months)) for k in SECTORS}
    pr = {SECTORS[k]: pr.get(k, [None] * len(months)) for k in SECTORS}
    rev = {k: [round(a * b, 0) if a is not None and b is not None else None for a, b in zip(sl[k], pr[k])] for k in sl}
    last12 = {}
    for k in sl:
        a = [x for x in sl[k][-12:]]
        r = [x for x in rev[k][-12:]]
        ok = all(x is not None for x in a) and all(x is not None for x in r)
        last12[k] = {"sales_mwh": round(sum(a), 1) if ok else None, "revenue_usd": round(sum(r), 0) if ok else None,
                     "price_usd_per_mwh": round(sum(r) / sum(a), 2) if ok and sum(a) else None}
    c = cust[cust["st"] == st]
    lastc = c["month"].max() if len(c) else None
    customers = {SECTORS[k]: num(c[(c["month"] == lastc) & (c["sector"] == k)]["value"].sum(), 0) if lastc and len(c[(c["month"] == lastc) & (c["sector"] == k)]) else None for k in SECTORS}
    years, annual_sales = whole_years(months, sl)
    _, annual_rev = whole_years(months, rev)
    return {
        "table": "eia_retail_sales_monthly", "price_table": "eia_retail_electricity_prices", "vintage": months[-1], "source": SRC["retail"],
        "months": months, "sales_mwh": sl, "price_usd_per_mwh": pr, "revenue_usd": rev,
        "revenue_note": "Revenue is EIA's sales times EIA's average price for the same month and sector. EIA computes its average price as revenue over sales, so the product gives EIA's revenue to within the price's rounding (one tenth of a dollar a MWh).",
        "years": years, "annual_sales_mwh": annual_sales, "annual_revenue_usd": annual_rev,
        "last12": {"from": months[-12], "to": months[-1], "by_sector": last12},
        "customers": {"month": lastc, "by_sector": customers},
    }


def build_plants(op, planned, retired, st):
    o = op[op["state"] == st] if st != "US" else op
    if o.empty:
        return {"table": "eia860m_operating_generators", "largest": None, "reason": f"EIA-860M lists no operating generator in {PLACES[st]}"}
    vintage = o["vintage"].iloc[0]
    by_tech = {}
    for t, g in o.groupby("technology_group"):
        by_tech[t] = {"nameplate_mw": num(g["nameplate_mw"].sum(), 1), "net_summer_mw": num(g["net_summer_mw"].sum(), 1), "generators": int(len(g))}
        if t == "storage":
            by_tech[t]["energy_mwh"] = num(g["energy_capacity_mwh"].sum(), 1)
    plants = []
    for pid, g in o.groupby("plant_id"):
        mw = g["nameplate_mw"].sum()
        top = g.groupby("technology_group")["nameplate_mw"].sum().sort_values(ascending=False)
        plants.append({"plant_id": pid, "name": g["name"].iloc[0], "state": g["state"].iloc[0], "county": g["county"].iloc[0],
                       "operator": g["operator"].mode().iloc[0], "balancing_authority": g["balancing_authority"].mode().iloc[0] or None,
                       "nameplate_mw": num(mw, 1), "net_summer_mw": num(g["net_summer_mw"].sum(), 1),
                       "technology_group": top.index[0], "technologies": {k: num(v, 1) for k, v in top.items()},
                       "lat": num(g["lat"].iloc[0], 4), "lon": num(g["lon"].iloc[0], 4), "generators": int(len(g))})
    plants.sort(key=lambda r: -(r["nameplate_mw"] or 0))
    pl = planned[planned["state"] == st] if st != "US" else planned
    coming = {}
    for (y, t), g in pl.assign(year=pl["planned_operation_date"].str.slice(0, 4)).groupby(["year", "technology_group"]):
        coming.setdefault(y or "no date", {})[t] = {"nameplate_mw": num(g["nameplate_mw"].sum(), 1), "generators": int(len(g)),
                                                    "under_construction_mw": num(g.loc[g["status"] == "under_construction", "nameplate_mw"].sum(), 1)}
    going = {}
    pr = o[o["planned_retirement_date"].astype(str).str.len() >= 4]
    for (y, t), g in pr.assign(year=pr["planned_retirement_date"].astype(str).str.slice(0, 4)).groupby(["year", "technology_group"]):
        going.setdefault(y, {})[t] = {"nameplate_mw": num(g["nameplate_mw"].sum(), 1), "generators": int(len(g))}
    rt = retired[retired["state"] == st] if st != "US" else retired
    gone = {}
    for (y, t), g in rt.assign(year=rt["retirement_date"].astype(str).str.slice(0, 4)).groupby(["year", "technology_group"]):
        gone.setdefault(y, {})[t] = {"nameplate_mw": num(g["nameplate_mw"].sum(), 1), "generators": int(len(g))}
    return {
        "table": "eia860m_operating_generators", "planned_table": "eia860m_planned_generators", "retired_table": "eia860m_retired_generators",
        "vintage": vintage, "source": SRC["plants"], "unit": "MW (nameplate and net summer); MWh (storage energy)",
        "capacity_by_technology": dict(sorted(by_tech.items(), key=lambda kv: -(kv[1]["nameplate_mw"] or 0))),
        "capacity_total_mw": num(o["nameplate_mw"].sum(), 1), "plants": int(o["plant_id"].nunique()),
        "largest": plants[:10],
        "coming_by_year": dict(sorted(coming.items())), "retiring_by_year": dict(sorted(going.items())),
        "retired_by_year": dict(sorted(gone.items())),
        "retired_note": "EIA-860M's retired sheet as the ERW's table holds it: the generators retired in its window, not every retirement since 2001.",
    }


def build_co2(co2, st):
    c = co2[co2["st"] == st]
    if c.empty:
        return {"table": "eia_power_co2_state_annual", "years": None, "reason": f"EIA prints no emissions for {PLACES[st]} in the table"}
    years = sorted(c["year"].unique())
    tons = c[c["variable"] == "co2"]
    by = {}
    for f, g in tons.groupby("fuel"):
        vals = dict(zip(g["year"], g["value"]))
        by[CO2_FUELS.get(f, f)] = [num(vals.get(y), 0) for y in years]
    rate = c[(c["variable"] == "co2_rate") & (c["fuel"] == "ALL")]
    rv = dict(zip(rate["year"], rate["value"]))
    return {"table": "eia_power_co2_state_annual", "vintage": years[-1], "source": SRC["co2"], "unit": "metric tons of CO2; kg of CO2 per MWh",
            "years": years, "tons_by_fuel": by, "rate_kg_per_mwh": [num(rv.get(y), 1) for y in years]}


def build_gas(use, prod, st):
    u, p = use[use["st"] == st], prod[prod["st"] == st]
    if u.empty and p.empty:
        return {"table": "eia_gas_consumption_state_monthly", "months": None, "reason": f"EIA prints no natural gas figures for {PLACES[st]} in the tables"}
    lo = min(x for x in [u["month"].min() if len(u) else None, p["month"].min() if len(p) else None] if x)
    hi = max(x for x in [u["month"].max() if len(u) else None, p["month"].max() if len(p) else None] if x)
    months = month_range(lo, hi)
    used = series_by(u, "variable", months, 0)
    used = {k.replace("consumption_", ""): used.get(k) for k in GAS_USE}
    out = {"table": "eia_gas_consumption_state_monthly", "production_table": "eia_gas_production_state_monthly", "vintage": months[-1],
           "source": SRC["gas"], "unit": "MMcf", "months": months, "consumption": {}, "consumption_reason": {}}
    for k, v in used.items():
        if v is None or all(x is None for x in v):
            out["consumption"][k] = None
            out["consumption_reason"][k] = f"EIA prints no {k.replace('_', ' ')} consumption for {PLACES[st]} in the table"
        else:
            out["consumption"][k] = v
    mp = p[p["variable"] == "marketed_production"]
    if mp.empty:
        out["marketed_production"] = None
        out["production_reason"] = f"EIA prints no marketed production for {PLACES[st]}: it is not a producing state in the Natural Gas Monthly"
    else:
        out["marketed_production"] = series_by(mp, "variable", months, 0)["marketed_production"]
    return out


def build_seds(seds, res, ind, st):
    frames = []
    for f, mp in ((seds, SEDS_SOURCES), (res, SEDS_SECTORS), (ind, SEDS_SECTORS)):
        g = f[(f["st"] == st) & f["sid"].isin(mp)]
        frames.append(g.assign(key=g["sid"].map(mp)))
    g = pd.concat(frames)
    if g.empty:
        return {"table": "eia_seds_state_energy", "years": None, "reason": f"EIA's State Energy Data System has no figures for {PLACES[st]} in the tables"}
    years = sorted(g["year"].unique())
    def arr(k):
        h = g[g["key"] == k]
        vals = dict(zip(h["year"], h["value"]))
        return [num(vals.get(y), 1) for y in years] if len(h) else None
    return {"table": "eia_seds_state_energy", "sector_tables": ["eia_seds_residential_annual", "eia_seds_industrial_annual"],
            "vintage": years[-1], "source": SRC["seds"], "unit": "trillion Btu", "years": years,
            "by_source": {v: arr(v) for v in SEDS_SOURCES.values()},
            "by_sector": {"residential": arr("residential"), "industrial": arr("industrial"), "commercial": None, "transportation": None},
            "by_sector_reason": {"commercial": "the warehouse's SEDS tables hold the commercial sector's electricity and natural gas, not its total energy",
                                 "transportation": "the warehouse's SEDS tables hold the transportation sector's electricity and natural gas, not its total energy"}}


def build_disposition(disp, st):
    d = disp[disp["st"] == st]
    if d.empty:
        return {"table": "eia_state_source_disposition_annual", "years": None, "reason": f"EIA's state profile has no source and disposition for {PLACES[st]} in the table"}
    years = sorted(d["year"].unique())
    out = {}
    for v in DISPOSITION:
        h = d[d["variable"] == v]
        vals = dict(zip(h["year"], h["value"]))
        out[v] = [num(vals.get(y), 0) for y in years] if len(h) else None
    return {"table": "eia_state_source_disposition_annual", "vintage": years[-1], "source": SRC["disposition"], "unit": "MWh", "years": years, "values": out,
            "note": "Net interstate trade is EIA's figure: positive where the state took in more electricity from other states than it sent out."}


def build_serving(county, pop, ba_meta, st):
    if st == "US":
        return {"table": "eia_county_region", "by_authority": None, "reason": "the nation is served by every authority; see the Grid tool's map"}
    c = county[county["x_state"] == st]
    if c.empty:
        return {"table": "eia_county_region", "by_authority": None, "reason": f"the ERW's county table does not place {PLACES[st]}'s counties in a balancing authority"}
    c = c.merge(pop, on="x_fips", how="left")
    year = pop["year"].iloc[0]
    unmatched = sorted(c.loc[c["population"].isna(), "x_fips"])
    if len(unmatched) == len(c):
        raise SystemExit(f"states_page: no county of {st} has a population in census_county_population; the join is broken")
    total = c["population"].sum()
    by = []
    for ba, g in c.groupby("x_ba_primary"):
        meta = ba_meta.get(ba, {})
        by.append({"code": ba or None, "name": meta.get("name") if ba else None, "region": meta.get("region") if ba else None,
                   "grid": GRIDS.get(ba) if ba else None, "counties": int(len(g)), "population": int(g["population"].sum()),
                   "share_pct": round(100 * g["population"].sum() / total, 2) if total else None,
                   "shared_counties": int((g["x_shared"] == "Y").sum()),
                   "reason": None if ba else "; ".join(sorted(set(g["x_basis"])))})
    by.sort(key=lambda r: -r["population"])
    mismatch = None
    if unmatched and c.loc[c["population"].isna(), "x_ba_primary"].astype(bool).any():
        # counties EIA-861 places in an authority have no population, so a share by people would be wrong: no share at all
        mismatch = (f"{PLACES[st]}'s counties in EIA-861 and in the Census Bureau's newest estimates do not match (Connecticut's eight old "
                    "counties became nine planning regions in 2022), so no share by population is computed; the counties are counted as EIA-861 lists them")
        for r in by:
            r["share_pct"] = None
            r["population"] = None
            r["reason"] = mismatch if r["code"] else r["reason"]
        by = [r for r in by if r["code"]] + [r for r in by if not r["code"]]
    grids = {}
    for r in by:
        k = r["grid"] or "none of the seven"
        grids[k] = None if mismatch else round(grids.get(k, 0) + (r["share_pct"] or 0), 2)
    return {"table": "eia_county_region", "population_table": "census_county_population", "vintage": f"EIA-861 2025; population {year}",
            "source": SRC["serving"], "population_year": year, "population": int(total), "by_authority": by, "by_grid_pct": grids,
            "shares_reason": mismatch,
            "counties_without_population": unmatched,
            "counties_without_population_reason": ("counties of EIA-861 with no figure in the Census Bureau's newest county estimates (Connecticut's eight old counties became nine planning regions in 2022); they count for no one" if unmatched else None),
            "basis": "Each county counts once, whole, for its primary authority: the one whose utilities serve most of the county's customers in EIA-861. A county two authorities share is counted for its primary one."}


RESEARCH = os.path.join(ROOT, "docs", "research", "large_load", "legislation")


def research_status(st):
    """Session 9000 (data request 563): what the large-load research says of a state with no law in the table, from its
    own files (docs/research/large_load/legislation/*.json): withheld (a law found but its text not read on an allowed
    host), not read (the legislature's site could not be read), none found (searched, nothing found), or not yet read
    (the research did not cover the state). Returns (status, words)."""
    import glob
    for path in sorted(glob.glob(os.path.join(RESEARCH, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        for w in d.get("withheld", []):
            if w.get("state") == st:
                return "withheld", (f"{w.get('bill', 'a law')} was found but is withheld: its text was not read on a host "
                                    f"that allows this reader ({w.get('reason', '')})")
        for n in d.get("none_found", []):
            if n.get("state") == st:
                s = n.get("searched", "")
                if s.startswith("not read"):
                    return "not read", f"the research could not read the legislature's site: {s[len('not read'):].lstrip(': ')}"
                return "none found", f"the research searched and found no large-load law: {s}"
    return "not yet read", f"the ERW's large-load research has not yet read {PLACES[st]}'s laws"


def build_laws(laws, st):
    rows = laws[laws["x_state"] == st]
    if rows.empty:
        status, words = research_status(st)
        return {"table": "state_large_load_laws", "laws": [], "research_status": status, "reason": words}
    out = []
    for _, r in rows.sort_values("event_date").iterrows():
        out.append({"law_id": r["x_law_id"], "bill": r["x_bill"], "session": r["x_session"], "title": r["x_title"], "status": r["status"],
                    "date": r["event_date"], "date_kind": r["x_date_kind"], "effective": r["x_effective_date"] or None,
                    "threshold": r["x_threshold_mw"] or None, "requirements": r["x_requirements"] or None, "url": r["source_url"],
                    "read": r["x_date_read"] or None})
    return {"table": "state_large_load_laws", "source": SRC["laws"], "laws": out}


def build_severance(sev, st):
    if st in sev.get("states", {}):
        s = sev["states"][st]
        return {"file": "site/data/severance_rules.json", "source": SRC["severance"], "in_tool": True, "address": f"/severance?state={st}",
                "products": sorted(s.get("products", {}).keys())}
    return {"file": "site/data/severance_rules.json", "in_tool": False,
            "reason": "the severance tool holds " + ", ".join(PLACES[k] for k in sev.get("states", {})) + " only"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: every state on one page, the page files")
    ap.add_argument("--site-dir")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    site = a.site_dir or SITE
    os.makedirs(site, exist_ok=True)

    gen = read("state_generation_mix_monthly", ["entity", "variable", "ts_utc", "value"])
    gen["st"] = gen["entity"].str.split(":").str[1]
    gen["src"] = gen["variable"].str.replace("net_generation_", "", regex=False).str.replace("_mwh", "", regex=False)
    gen["month"] = gen["ts_utc"].str.slice(0, 7)
    rs = read("eia_retail_sales_monthly", ["entity", "variable", "ts_utc", "value"])
    parts = rs["entity"].str.split(":")
    rs["st"], rs["sector"], rs["month"] = parts.str[2], parts.str[3], rs["ts_utc"].str.slice(0, 7)
    sales = rs[(rs["variable"] == "retail_sales") & rs["sector"].isin(SECTORS)]
    cust = rs[(rs["variable"] == "customers") & rs["sector"].isin(SECTORS)]
    pr = read("eia_retail_electricity_prices", ["entity", "ts_utc", "value"])
    parts = pr["entity"].str.split(":")
    pr["st"], pr["sector"], pr["month"] = parts.str[2], parts.str[3], pr["ts_utc"].str.slice(0, 7)
    pr = pr[pr["sector"].isin(SECTORS)]
    gcols = ["plant_id", "name", "state", "county", "operator", "balancing_authority", "technology_group", "nameplate_mw", "net_summer_mw", "lat", "lon", "vintage"]
    op = read("eia860m_operating_generators", gcols + ["planned_retirement_date", "energy_capacity_mwh"])
    planned = read("eia860m_planned_generators", gcols + ["planned_operation_date", "status"])
    retired = read("eia860m_retired_generators", gcols + ["retirement_date"])
    for f in (op, planned, retired):
        for col in ("nameplate_mw", "net_summer_mw", "energy_capacity_mwh"):
            if col in f.columns:
                f[col] = pd.to_numeric(f[col], errors="coerce")
    co2 = read("eia_power_co2_state_annual", ["entity", "variable", "ts_utc", "value"])
    parts = co2["entity"].str.split(":")
    co2["st"], co2["fuel"], co2["year"] = parts.str[1], parts.str[2], co2["ts_utc"].str.slice(0, 4)
    use = read("eia_gas_consumption_state_monthly", ["entity", "variable", "ts_utc", "value", "geo"])
    use = use[use["variable"].isin(GAS_USE)]
    use["st"] = use["entity"].str.split(":").str[2].str.slice(1)
    use.loc[use["entity"].str.split(":").str[2] == "NUS", "st"] = "US"
    use["month"] = use["ts_utc"].str.slice(0, 7)
    prod = read("eia_gas_production_state_monthly", ["entity", "variable", "ts_utc", "value"])
    prod["st"] = prod["entity"].str.split(":").str[1].str.slice(1)
    prod.loc[prod["entity"].str.split(":").str[1] == "NUS", "st"] = "US"
    prod["month"] = prod["ts_utc"].str.slice(0, 7)
    seds = read("eia_seds_state_energy", ["entity", "ts_utc", "value"])
    res = read("eia_seds_residential_annual", ["entity", "ts_utc", "value"])
    ind = read("eia_seds_industrial_annual", ["entity", "ts_utc", "value"])
    for f in (seds, res, ind):
        parts = f["entity"].str.split(":")
        f["sid"], f["st"], f["year"] = parts.str[1], parts.str[2], f["ts_utc"].str.slice(0, 4)
    disp = read("eia_state_source_disposition_annual", ["entity", "variable", "ts_utc", "value"])
    disp["st"], disp["year"] = disp["entity"].str.split(":").str[1], disp["ts_utc"].str.slice(0, 4)
    county = read("eia_county_region", ["x_state", "x_fips", "x_ba_primary", "x_shared", "x_basis"])
    county["x_fips"] = county["x_fips"].astype(str).str.zfill(5)   # the reader's engine reads 01001 as a number; a county code is five digits
    pop = read("census_county_population", ["entity", "variable", "ts_utc", "value"])
    pop = pop[pop["variable"] == "population_estimate"]
    newest = pop["ts_utc"].max()
    pop = pop[pop["ts_utc"] == newest]
    pop = pd.DataFrame({"x_fips": pop["entity"].str.split(":").str[2], "population": pop["value"], "year": newest[:4]})
    with open(os.path.join(ROOT, "site", "data", "regions", "index.json"), encoding="utf-8") as fh:
        ba_meta = {b["code"]: b for b in json.load(fh)["bas"]}
    laws = read("state_large_load_laws")
    with open(os.path.join(ROOT, "site", "data", "severance_rules.json"), encoding="utf-8") as fh:
        sev = json.load(fh)

    tables = ["state_generation_mix_monthly", "eia_retail_sales_monthly", "eia_retail_electricity_prices", "eia860m_operating_generators",
              "eia860m_planned_generators", "eia860m_retired_generators", "eia_power_co2_state_annual", "eia_gas_consumption_state_monthly",
              "eia_gas_production_state_monthly", "eia_seds_state_energy", "eia_seds_residential_annual", "eia_seds_industrial_annual",
              "eia_state_source_disposition_annual", "eia_county_region", "census_county_population", "state_large_load_laws"]
    places = a.only or list(PLACES)
    index = []
    for st in places:
        if st not in PLACES:
            raise SystemExit(f"states_page: {st} is not a state code of the page")
        doc = {"built": built, "state": st, "name": PLACES[st], "method": METHOD, "license": "public", "tables": tables,
               "generation": build_generation(gen, st), "retail": build_retail(sales, pr, cust, st),
               "plants": build_plants(op, planned, retired, st), "co2": build_co2(co2, st), "gas": build_gas(use, prod, st),
               "energy": build_seds(seds, res, ind, st), "disposition": build_disposition(disp, st),
               "serving": build_serving(county, pop, ba_meta, st), "large_load_laws": build_laws(laws, st),
               "severance": build_severance(sev, st)}
        path = os.path.join(site, f"{st.lower()}.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, separators=(",", ":"), allow_nan=False)
        g, r = doc["generation"], doc["retail"]
        l12 = g.get("last12") or {}
        top = max(l12.get("share_pct", {}).items(), key=lambda kv: kv[1] or -1)[0] if l12 else None
        index.append({"state": st, "name": PLACES[st], "file": f"{st.lower()}.json", "bytes": os.path.getsize(path),
                      "generation_last12_mwh": l12.get("total_mwh"), "largest_source_last12": top,
                      "largest_source_share_pct": l12.get("share_pct", {}).get(top) if top else None,
                      "price_all_last12_usd_per_mwh": (r.get("last12") or {}).get("by_sector", {}).get("all", {}).get("price_usd_per_mwh"),
                      "capacity_mw": doc["plants"].get("capacity_total_mw"),
                      "grids": sorted(doc["serving"].get("by_grid_pct", {}).keys()) if doc["serving"].get("by_grid_pct") else None,
                      "laws": len(doc["large_load_laws"]["laws"])})
    if not a.only:
        first_month, last_month = gen["month"].min(), gen["month"].max()
        idx = {"built": built, "method": METHOD, "license": "public", "tables": tables, "contract": "docs/state/page_files_states.md",
               "generation_months": [first_month, last_month],
               "states": index}
        with open(os.path.join(site, "index.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(idx, f, separators=(",", ":"), allow_nan=False)
    total = sum(r["bytes"] for r in index)
    print(f"states_page: {len(index)} files, {total:,} bytes, largest {max(r['bytes'] for r in index):,}; index {'written' if not a.only else 'not written (--only)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
