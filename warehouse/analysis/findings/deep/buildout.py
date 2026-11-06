#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "generation_pipeline", third part: the build-out (session 3007).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. The pipeline table of the chain
file (generator_pipeline_by_grid) holds two months (August and September 2026) and cannot be tested by year; what was
built and retired, year by year, can. Public sources:

    eia860m_operating_generators     EIA-860M's operating generators with their first year of operation: the MW that
                                     entered service each year and still operate, and batteries' MWh per MW
    eia860m_retired_generators_all   EIA-860M's retired generators with their retirement month: the MW retired each year
    uswtdb_wind_turbines             the US Wind Turbine Database: each turbine's rated capacity and rotor by project year
    lbnl_tracking_the_sun            Berkeley Lab's Tracking the Sun: the median installed price of systems by state,
                                     customer segment and year (USD per kW DC, unscreened)
    storage_buildout_monthly         the ERW's battery fleet by grid at each month's end (EIA-860M)

An annual total (MW entering service, MW retired, a fleet at December) is one observation of its year, as EIA-923's
are (session 3006): its count of units is no test of the year being whole.

    python warehouse/analysis/findings/deep/buildout.py --dry-run
    python warehouse/analysis/findings/deep/buildout.py --load
"""

import argparse
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import generation  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "generation_pipeline"
FIRST = 2010                       # the build-out years counted: operating units that entered service from 2010
LAST = 2025
TURBINE_FIRST = 2005               # the turbine years counted from: earlier years hold few projects
MIN_BATTERY_MW = 100.0             # session 3007: a year of batteries entering service is counted from 100 MW (2011 rested on two units)
MIN_PRICED = 500                   # a state's residential year is counted when at least 500 of its systems carry a price
# session 3007: a year of an inventory (turbines installed, systems priced) is one observation; its count grows over the
# years and is no test of the year being whole (session 3006's fault again, found on the dry run)
TECH = {"Batteries": ("battery", "batteries"), "Solar Photovoltaic": ("solar", "solar photovoltaic"), "Onshore Wind Turbine": ("wind", "onshore wind"),
        "Natural Gas Fired Combined Cycle": ("gascc", "natural gas combined cycle"), "Natural Gas Fired Combustion Turbine": ("gasct", "natural gas combustion turbines")}
GRIDS = {"iso:ercot": ("ercot_fleet", "ERCOT"), "iso:caiso": ("caiso_fleet", "CAISO"), "iso:pjm": ("pjm_fleet", "PJM"), "us:total": ("us_fleet", "the United States")}


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def operating(in_dir):
    def build():
        d = common.read_table("eia860m_operating_generators", in_dir, usecols=["entity_id", "state", "technology", "nameplate_mw", "operating_year", "energy_capacity_mwh"])
        d["mw"], d["mwh"], d["year"] = _num(d["nameplate_mw"]), _num(d["energy_capacity_mwh"]), _num(d["operating_year"])
        return d.dropna(subset=["mw", "year"])
    return hm._cached(("deep_860m_op", in_dir), build)


def added_mw(in_dir=None):
    """By technology, the US and each state: the nameplate MW of today's operating generators that entered service in the year."""
    d = operating(in_dir)
    d = d[d["technology"].isin(TECH) & d["year"].between(FIRST, LAST)]
    rows, tables = [], {}
    for tech, g in d.groupby("technology"):
        key, words = TECH[tech]
        for st, h in [("US", g)] + list(g[g["state"].isin(generation.STATES)].groupby("state")):
            region = f"add_{key}_{st}"
            by = h.groupby("year")["mw"].sum()
            for y in range(FIRST, LAST + 1):
                rows.append(hm._row(region, f"{words}, {generation.STATES.get(st, st)}", y, float(by.get(y, 0.0)), 1))
            tables[region] = ["eia860m_operating_generators"]
    return {"rows": rows, "tables": tables}


def battery_hours(in_dir=None):
    """The MWh per MW of the batteries that entered service in the year and still operate (their summed MWh over their summed MW), US."""
    d = operating(in_dir)
    d = d[(d["technology"] == "Batteries") & d["year"].between(FIRST, LAST)].dropna(subset=["mwh"])
    t = d.groupby("year")[["mwh", "mw"]].sum()
    rows = [hm._row("us_battery_hours", "US batteries", y, float(r["mwh"] / r["mw"]), 1) for y, r in t.iterrows() if r["mw"] >= MIN_BATTERY_MW]
    return {"rows": rows, "tables": {"us_battery_hours": ["eia860m_operating_generators"]}}


def coal_retired(in_dir=None):
    """The nameplate MW of coal-fired generators (EIA's conventional steam coal) retired in the year, US."""
    d = common.read_table("eia860m_retired_generators_all", in_dir, usecols=["entity_id", "technology", "nameplate_mw", "retirement_date"])
    d = d[d["technology"] == "Conventional Steam Coal"]
    d["mw"], d["year"] = _num(d["nameplate_mw"]), _num(d["retirement_date"].astype(str).str[:4])
    by = d.dropna(subset=["mw", "year"]).groupby("year")["mw"].sum()
    rows = [hm._row("us_coal_retired", "US coal-fired generators", y, float(by.get(y, 0.0)), 1) for y in range(2002, LAST + 1)]
    return {"rows": rows, "tables": {"us_coal_retired": ["eia860m_retired_generators_all"]}}


def turbines(in_dir):
    def build():
        d = common.read_table("uswtdb_wind_turbines", in_dir, usecols=["entity_id", "project_year", "turbine_capacity_kw", "rotor_diameter_m", "offshore", "retrofit"])
        d["year"], d["kw"], d["rotor"] = _num(d["project_year"]), _num(d["turbine_capacity_kw"]), _num(d["rotor_diameter_m"])
        d = d[d["offshore"].astype(str).isin(["0", "0.0", "False", "false"])]
        return d.dropna(subset=["year"])
    return hm._cached(("deep_uswtdb", in_dir), build)


def turbine_kw(in_dir=None):
    """The mean rated capacity of the onshore turbines of the year's projects (kW), turbines with a rating."""
    d = turbines(in_dir).dropna(subset=["kw"])
    rows = [hm._row("us_turbine_kw", "US onshore wind turbines", y, float(s["kw"].mean()), 1) for y, s in d.groupby("year") if TURBINE_FIRST <= y <= LAST]
    return {"rows": rows, "tables": {"us_turbine_kw": ["uswtdb_wind_turbines"]}}


def turbine_rotor(in_dir=None):
    """The mean rotor diameter of the onshore turbines of the year's projects (m), turbines with a diameter."""
    d = turbines(in_dir).dropna(subset=["rotor"])
    rows = [hm._row("us_turbine_rotor", "US onshore wind turbines", y, float(s["rotor"].mean()), 1) for y, s in d.groupby("year") if TURBINE_FIRST <= y <= LAST]
    return {"rows": rows, "tables": {"us_turbine_rotor": ["uswtdb_wind_turbines"]}}


def res_pv_price(in_dir=None):
    """By state: the median installed price of the year's residential systems (USD per kW DC), Tracking the Sun as the ERW holds it."""
    d = hm.series("lbnl_tracking_the_sun", in_dir, variables=["price_median", "systems_priced"])
    d = d[d["entity"].str.endswith("_res")]
    w = d.pivot_table(index=["entity", "ts"], columns="variable", values="value").dropna().reset_index()
    rows, tables = [], {}
    for ent, g in w.groupby("entity"):
        st = ent.split(":")[1].split("_")[0].upper()
        region = f"tts_res_{st}"
        for _, r in g[g["systems_priced"] >= MIN_PRICED].iterrows():
            rows.append(hm._row(region, f"residential systems in {generation.STATES.get(st, st)}", r["ts"].year, float(r["price_median"]), 1))
        tables[region] = ["lbnl_tracking_the_sun"]
    return {"rows": rows, "tables": tables}


def _fleet(in_dir, var):
    d = hm.series("storage_buildout_monthly", in_dir, variables=[var], entities=list(GRIDS))
    d = d[d["ts"].dt.month == 12]
    rows, tables = [], {}
    for ent, g in d.groupby("entity"):
        region, words = GRIDS[ent]
        for _, r in g.iterrows():
            rows.append(hm._row(f"{region}_{var}", words, r["ts"].year, float(r["value"]), 1))
        tables[f"{region}_{var}"] = ["storage_buildout_monthly"]
    return {"rows": rows, "tables": tables}


def battery_fleet_mw(in_dir=None):
    """The battery fleet in operation at the year's end (MW), by grid and the US."""
    return _fleet(in_dir, "battery_operating_mw")


def fleet_hours(in_dir=None):
    """The battery fleet's MWh per MW at the year's end, by grid and the US."""
    return _fleet(in_dir, "battery_operating_mwh_per_mw")


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_HEAD = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <{table}.csv>

{label}.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, dtype=str)
'''


def _added(region):
    _, key, st = region.split("_", 2)
    tech = next(k for k, v in TECH.items() if v[0] == key)
    return tech, st


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    if name == "added_mw":
        tech, st = _added(region)
        sf = "" if st == "US" else f"d = d[d['state'] == {st!r}]\n"
        body = (f"d = d[d['technology'] == {tech!r}]\n{sf}d['mw'], d['year'] = pd.to_numeric(d['nameplate_mw'], errors='coerce'), pd.to_numeric(d['operating_year'], errors='coerce')\n"
                f"by = d.dropna(subset=['mw', 'year']).groupby('year')['mw'].sum()\nfor y in range({FIRST}, {LAST + 1}):\n    print(y, round(float(by.get(y, 0.0)), 6), 1)\n")
        return PY_HEAD.format(name=name, region=region, table="eia860m_operating_generators", label=label) + body
    if name == "battery_hours":
        body = ("d = d[d['technology'] == 'Batteries']\nfor c in ('nameplate_mw', 'energy_capacity_mwh', 'operating_year'):\n    d[c] = pd.to_numeric(d[c], errors='coerce')\n"
                f"d = d.dropna(subset=['nameplate_mw', 'energy_capacity_mwh', 'operating_year'])\nd = d[d['operating_year'].between({FIRST}, {LAST})]\n"
                "t = d.groupby('operating_year')[['energy_capacity_mwh', 'nameplate_mw']].sum()\nfor y, r in t.iterrows():\n"
                "    if r['nameplate_mw'] >= 100:\n        print(int(y), round(float(r['energy_capacity_mwh'] / r['nameplate_mw']), 6), 1)\n")
        return PY_HEAD.format(name=name, region=region, table="eia860m_operating_generators", label=label) + body
    if name == "coal_retired":
        body = ("d = d[d['technology'] == 'Conventional Steam Coal']\nd['mw'], d['year'] = pd.to_numeric(d['nameplate_mw'], errors='coerce'), pd.to_numeric(d['retirement_date'].str[:4], errors='coerce')\n"
                f"by = d.dropna(subset=['mw', 'year']).groupby('year')['mw'].sum()\nfor y in range(2002, {LAST + 1}):\n    print(y, round(float(by.get(y, 0.0)), 6), 1)\n")
        return PY_HEAD.format(name=name, region=region, table="eia860m_retired_generators_all", label=label) + body
    if name in ("turbine_kw", "turbine_rotor"):
        col = "turbine_capacity_kw" if name == "turbine_kw" else "rotor_diameter_m"
        body = (f"d = d[d['offshore'].isin(['0', '0.0', 'False', 'false'])]\nd['year'], d['v'] = pd.to_numeric(d['project_year'], errors='coerce'), pd.to_numeric(d[{col!r}], errors='coerce')\n"
                f"d = d.dropna(subset=['year', 'v'])\nfor y, s in d.groupby('year'):\n    if {TURBINE_FIRST} <= y <= {LAST}:\n        print(int(y), round(float(s['v'].mean()), 6), 1)\n")
        return PY_HEAD.format(name=name, region=region, table="uswtdb_wind_turbines", label=label) + body
    if name == "res_pv_price":
        st = region.split("_")[-1]
        body = (f"d = d[(d['entity'] == 'tts:{st.lower()}_res') & d['variable'].isin(['price_median', 'systems_priced'])]\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                f"w = d.pivot_table(index='ts_utc', columns='variable', values='value').dropna()\nw = w[w['systems_priced'] >= {MIN_PRICED}]\nfor ts, r in w.iterrows():\n"
                "    print(int(ts[:4]), round(float(r['price_median']), 6), 1)\n")
        return PY_HEAD.format(name=name, region=region, table="lbnl_tracking_the_sun", label=label) + body
    var = "battery_operating_mw" if name == "battery_fleet_mw" else "battery_operating_mwh_per_mw"
    ent = next(k for k, v in GRIDS.items() if region == f"{v[0]}_{var}")
    body = (f"d = d[(d['entity'] == {ent!r}) & (d['variable'] == {var!r}) & (d['ts_utc'].str[5:7] == '12')]\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
            "for _, r in d.dropna(subset=['value']).iterrows():\n    print(int(r['ts_utc'][:4]), round(float(r['value']), 6), 1)\n")
    return PY_HEAD.format(name=name, region=region, table="storage_buildout_monthly", label=label) + body


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
            "clear all"]
    if name == "added_mw":
        tech, st = _added(region)
        lines = head + ['import delimited "eia860m_operating_generators.csv", varnames(1) stringcols(_all) clear', f'keep if technology == "{tech}"']
        lines += ([] if st == "US" else [f'keep if state == "{st}"'])
        lines += ["destring nameplate_mw operating_year, replace force", "drop if missing(nameplate_mw) | missing(operating_year)",
                  f"keep if inrange(operating_year, {FIRST}, {LAST})", "collapse (sum) measure = nameplate_mw, by(operating_year)", "rename operating_year year",
                  "generate byte n = 1", "* A year with no unit is a year of zero MW, as the Python prints it."]
    elif name == "battery_hours":
        lines = head + ['import delimited "eia860m_operating_generators.csv", varnames(1) stringcols(_all) clear', 'keep if technology == "Batteries"',
                        "destring nameplate_mw energy_capacity_mwh operating_year, replace force", "drop if missing(nameplate_mw) | missing(energy_capacity_mwh) | missing(operating_year)",
                        f"keep if inrange(operating_year, {FIRST}, {LAST})", "collapse (sum) mwh = energy_capacity_mwh (sum) mw = nameplate_mw, by(operating_year)",
                        "keep if mw >= 100", "generate double measure = mwh / mw", "rename operating_year year", "generate byte n = 1"]
    elif name == "coal_retired":
        lines = head + ['import delimited "eia860m_retired_generators_all.csv", varnames(1) stringcols(_all) clear', 'keep if technology == "Conventional Steam Coal"',
                        "destring nameplate_mw, replace force", "generate int year = real(substr(retirement_date, 1, 4))", "drop if missing(nameplate_mw) | missing(year)",
                        f"keep if inrange(year, 2002, {LAST})", "collapse (sum) measure = nameplate_mw, by(year)", "generate byte n = 1",
                        "* A year with no unit is a year of zero MW, as the Python prints it."]
    elif name in ("turbine_kw", "turbine_rotor"):
        col = "turbine_capacity_kw" if name == "turbine_kw" else "rotor_diameter_m"
        lines = head + ['import delimited "uswtdb_wind_turbines.csv", varnames(1) stringcols(_all) clear',
                        'keep if offshore == "0" | offshore == "0.0" | offshore == "False" | offshore == "false"',
                        f"destring project_year {col}, replace force", f"drop if missing(project_year) | missing({col})", f"keep if inrange(project_year, {TURBINE_FIRST}, {LAST})",
                        f"collapse (mean) measure = {col}, by(project_year)", "rename project_year year", "generate byte n = 1"]
    elif name == "res_pv_price":
        st = region.split("_")[-1]
        lines = head + ['import delimited "lbnl_tracking_the_sun.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "tts:{st.lower()}_res" & (variable == "price_median" | variable == "systems_priced")', "destring value, replace force",
                        "keep ts_utc variable value", "reshape wide value, i(ts_utc) j(variable) string", "drop if missing(valueprice_median) | missing(valuesystems_priced)", f"keep if valuesystems_priced >= {MIN_PRICED}",
                        "generate int year = real(substr(ts_utc, 1, 4))", "rename valueprice_median measure", "generate byte n = 1"]
    else:
        var = "battery_operating_mw" if name == "battery_fleet_mw" else "battery_operating_mwh_per_mw"
        ent = next(k for k, v in GRIDS.items() if region == f"{v[0]}_{var}")
        lines = head + ['import delimited "storage_buildout_monthly.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "{ent}" & variable == "{var}" & substr(ts_utc, 6, 2) == "12"', "destring value, replace force", "drop if missing(value)",
                        "generate int year = real(substr(ts_utc, 1, 4))", "rename value measure", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_860M = ("EIA-860M's generators that operate today, by the year they entered service: a unit built and since retired is not counted, "
              "and the latest months are preliminary.")
CANDIDATES = [
    C("added_mw", FAMILY, added_mw, "MW", 0, 1, 500.0, "WHAT ENTERED SERVICE",
      "the nameplate MW of today's operating generators that entered service in the year",
      lambda w: f"the nameplate capacity of {w} that entered service in the year and operates today",
      LIMIT_860M, reproduce("added_mw"), first_words="the first year this measure counts", consequence=3),
    C("battery_hours", FAMILY, battery_hours, "MWh per MW", 2, 1, 0.2, "HOW LONG NEW BATTERIES RUN",
      "the MWh per MW of the batteries that entered service in the year (their summed MWh over their summed MW)",
      lambda w: "the energy capacity per MW of the US batteries that entered service in the year",
      LIMIT_860M + " A battery's MWh is its reported energy capacity, not what it delivers in a cycle; a year with less than 100 MW entering service is left out.",
      reproduce("battery_hours"), first_words="the first year this measure counts", consequence=3),
    C("coal_retired", FAMILY, coal_retired, "MW", 0, 1, 1000.0, "COAL RETIRED",
      "the nameplate MW of coal-fired generators retired in the year",
      lambda w: "the nameplate capacity of US coal-fired generators retired in the year",
      "EIA-860M's retired generators by retirement month, nameplate MW; a unit converted to gas is retired as coal only if EIA lists it so.",
      reproduce("coal_retired"), consequence=3),
    C("turbine_kw", FAMILY, turbine_kw, "kW", 0, 1, 100.0, "THE SIZE OF A WIND TURBINE",
      "the mean rated capacity of the onshore turbines of the year's projects",
      lambda w: "the mean rated capacity of the US onshore wind turbines of the year's projects",
      "The US Wind Turbine Database's project year and turbine rating; turbines without a rating are left out, and repowered turbines keep their project's year.",
      reproduce("turbine_kw"), first_words="the first year this measure counts", consequence=2),
    C("turbine_rotor", FAMILY, turbine_rotor, "m", 1, 1, 5.0, "THE ROTOR OF A WIND TURBINE",
      "the mean rotor diameter of the onshore turbines of the year's projects",
      lambda w: "the mean rotor diameter of the US onshore wind turbines of the year's projects",
      "The US Wind Turbine Database's project year and rotor diameter; turbines without a diameter are left out.",
      reproduce("turbine_rotor"), first_words="the first year this measure counts", consequence=2),
    C("res_pv_price", FAMILY, res_pv_price, "USD per kW DC", 0, 1, 200.0, "WHAT A HOME SOLAR SYSTEM COSTS",
      "the median installed price of the year's residential systems over their DC size",
      lambda w: f"the median installed price of {w}",
      "Nominal dollars; the ERW's unscreened median over the systems Berkeley Lab lists with a price, not Berkeley Lab's reported figure; a year with fewer than 500 priced systems is left out.",
      reproduce("res_pv_price"), first_words="the first year this measure counts", consequence=2),
    C("battery_fleet_mw", FAMILY, battery_fleet_mw, "MW", 0, 1, 500.0, "THE BATTERY FLEET",
      "the battery fleet in operation at the year's end",
      lambda w: f"the battery fleet in operation in {w} at the year's end",
      "EIA-860M's operating batteries as the ERW counts them each month; a battery that reports late joins its month when EIA lists it.",
      reproduce("battery_fleet_mw"), consequence=3),
    C("fleet_hours", FAMILY, fleet_hours, "MWh per MW", 2, 1, 0.2, "THE BATTERY FLEET'S HOURS",
      "the battery fleet's MWh per MW at the year's end",
      lambda w: f"the energy capacity per MW of the battery fleet in {w} at the year's end",
      "EIA-860M's reported energy capacity; batteries that report no MWh are left out of the ratio.",
      reproduce("fleet_hours"), consequence=2),
]
for _P in CANDIDATES:
    if _P["name"] in ("added_mw", "battery_fleet_mw", "fleet_hours"):
        _P["rank_region"] = lambda r: 1e9 if r.endswith("_US") or r.startswith("us_") else 0.0
        _P["rank"] = lambda c: abs(c["change"])


def area(region):
    """A candidate's place: for the MW entering service, the technology (two states of one technology tell two stories, so
    the technology is not folded; the region itself is the area)."""
    return region


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family generation, the build-out (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="session 3009: correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_buildout", cands, a.in_dir, dry_run=not a.load, max_drafts=13, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
