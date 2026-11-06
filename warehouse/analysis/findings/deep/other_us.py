#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 166, session 3179): the rest of the US tables.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Public tables:

    eia_primary_energy_monthly          US primary energy production by source (TBtu): renewables (REPRBUS) over all (TEPRBUS)
    eia_seds_residential_annual         SEDS's residential sector: electricity expenditures (ESRCV) over all energy
                                        expenditures (TERCV), by state and the US, 1990 to 2024
    afdc_vehicle_registrations_annual   light-duty vehicle registrations by fuel and state (AFDC), 2016 on
    afdc_ev_charging_state_annual       public EV charging ports by state (AFDC), 2014 on

    python warehouse/analysis/findings/deep/other_us.py --dry-run
    python warehouse/analysis/findings/deep/other_us.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import generation  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "other_us"
PE, SEDS, REG, EV = "eia_primary_energy_monthly", "eia_seds_residential_annual", "afdc_vehicle_registrations_annual", "afdc_ev_charging_state_annual"
STATES = generation.STATES


def renewable_share(in_dir=None):
    """Renewables' share of US primary energy production over the year (percent), the months that hold both."""
    d = hm.series(PE, in_dir, entities=["eia:REPRBUS", "eia:TEPRBUS"]).drop_duplicates(["entity", "ts_utc"])
    w = d.pivot_table(index="ts_utc", columns="entity", values="value").dropna()
    w["year"] = w.index.str[:4].astype(int)
    rows = [hm._row("us_renewable_share", "the United States", y, float(100 * s["eia:REPRBUS"].sum() / s["eia:TEPRBUS"].sum()), len(s)) for y, s in w.groupby("year")]
    return {"rows": rows, "tables": {"us_renewable_share": [PE]}}


def home_electric_spend(in_dir=None):
    """Electricity's share of the residential sector's energy expenditures, by state and the US (percent)."""
    d = hm.series(SEDS, in_dir, variables=["expenditures"])
    p = d["entity"].str.split(":", expand=True)
    d = d.assign(series=p[1], st=p[2], year=d["ts_utc"].str[:4].astype(int))
    d = d[d["series"].isin(["ESRCV", "TERCV"])]
    w = d.pivot_table(index=["st", "year"], columns="series", values="value").dropna().reset_index()
    w = w[w["TERCV"] > 0]
    rows = [hm._row(f"home_elec_{st}", STATES.get(st, st), y, float(100 * e / t), 1) for st, y, e, t in zip(w["st"], w["year"], w["ESRCV"], w["TERCV"]) if st in STATES]
    return {"rows": rows, "tables": {r["region"]: [SEDS] for r in rows}}


def ev_share(in_dir=None):
    """Battery electric vehicles' share of the light-duty vehicles registered, by state and the US (percent)."""
    d = hm.series(REG, in_dir)
    d = d[d["variable"].str.startswith("registrations_")].assign(st=lambda x: x["entity"].str.split(":").str[1], year=lambda x: x["ts_utc"].str[:4].astype(int))
    tot = d.groupby(["st", "year"])["value"].sum()
    ev = d[d["variable"] == "registrations_ev"].groupby(["st", "year"])["value"].sum()
    rows = [hm._row(f"ev_{st}", STATES.get(st, st), y, float(100 * ev.get((st, y), 0.0) / t), 1) for (st, y), t in tot.items() if t > 0 and st in STATES]
    return {"rows": rows, "tables": {r["region"]: [REG] for r in rows}}


def dcfast_ports(in_dir=None):
    """Public DC fast charging ports at the year's end, the US (the states' sum) and each state."""
    d = hm.series(EV, in_dir, variables=["ev_dcfast_ports"])
    d = d.assign(st=d["entity"].str.split(":").str[1].str.upper(), year=d["ts_utc"].str[:4].astype(int))
    rows = []
    for st, g in [("US", d[d["st"].isin(STATES)])] + list(d.groupby("st")):   # the US is the states and DC
        if st not in STATES:
            continue
        for y, s in g.groupby("year"):
            rows.append(hm._row(f"dcfast_{st}", STATES[st], y, float(s["value"].sum()), 1))
    return {"rows": rows, "tables": {r["region"]: [EV] for r in rows}}


PY_HEAD = '''"""ERW findings hunt (chain 166): reproduce candidate {name} for {region} from the ERW's public table.

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
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
'''
TABLE = {"renewable_share": PE, "home_electric_spend": SEDS, "ev_share": REG, "dcfast_ports": EV}


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    head = PY_HEAD.format(name=name, region=region, table=TABLE[name], label=P["label"][0].upper() + P["label"][1:])
    st = region.split("_")[-1]
    if name == "renewable_share":
        return head + ("d = d[d['entity'].isin(['eia:REPRBUS', 'eia:TEPRBUS'])].drop_duplicates(['entity', 'ts_utc'])\n"
                       "w = d.pivot_table(index='ts_utc', columns='entity', values='value').dropna()\n"
                       "for y, s in w.groupby(w.index.str[:4].astype(int)):\n    print(y, round(float(100 * s['eia:REPRBUS'].sum() / s['eia:TEPRBUS'].sum()), 6), len(s))\n")
    if name == "home_electric_spend":
        return head + (f"d = d[d['entity'].isin(['eia_seds_res:ESRCV:{st}', 'eia_seds_res:TERCV:{st}']) & (d['variable'] == 'expenditures')]\n"
                       "w = d.pivot_table(index='year', columns='entity', values='value').dropna()\n"
                       f"for y, r in w.iterrows():\n    if r['eia_seds_res:TERCV:{st}'] > 0:\n"
                       f"        print(y, round(float(100 * r['eia_seds_res:ESRCV:{st}'] / r['eia_seds_res:TERCV:{st}']), 6), 1)\n")
    if name == "ev_share":
        return head + (f"d = d[(d['entity'] == 'afdc_reg:{st}') & d['variable'].str.startswith('registrations_')]\n"
                       "for y, s in d.groupby('year'):\n    t = s['value'].sum()\n    if t > 0:\n"
                       "        print(y, round(float(100 * s.loc[s['variable'] == 'registrations_ev', 'value'].sum() / t), 6), 1)\n")
    filt = "" if st == "US" else f"d = d[d['entity'].str.split(':').str[1].str.upper() == {st!r}]\n"
    return head + ("d = d[d['variable'] == 'ev_dcfast_ports']\n" + filt
                   + f"d = d[d['entity'].str.split(':').str[1].str.upper().isin({sorted(STATES)!r})]\n"
                   + "for y, s in d.groupby('year'):\n    print(y, round(float(s['value'].sum()), 6), 1)\n")


def reproduce_do(name, region):
    st = region.split("_")[-1]
    lines = [f"* ERW findings hunt (chain 166): reproduce candidate {name} for {region} from the ERW's public table.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
             "clear all", f'import delimited "{TABLE[name]}.csv", varnames(1) stringcols(_all) clear', "destring value, replace force", "drop if missing(value)",
             "generate int year = real(substr(ts_utc, 1, 4))"]
    if name == "renewable_share":
        lines += ['keep if entity == "eia:REPRBUS" | entity == "eia:TEPRBUS"', "duplicates drop entity ts_utc, force",
                  'generate str3 side = cond(entity == "eia:REPRBUS", "ren", "all")', "keep year ts_utc side value", "reshape wide value, i(ts_utc) j(side) string",
                  "drop if missing(valueren) | missing(valueall)", "collapse (sum) ren = valueren (sum) all = valueall (count) n = valueren, by(year)",
                  "generate double measure = 100 * ren / all"]
    elif name == "home_electric_spend":
        lines += [f'keep if (entity == "eia_seds_res:ESRCV:{st}" | entity == "eia_seds_res:TERCV:{st}") & variable == "expenditures"',
                  'generate str3 side = cond(strpos(entity, ":ESRCV:") > 0, "ele", "all")', "keep year side value", "reshape wide value, i(year) j(side) string",
                  "drop if missing(valueele) | missing(valueall) | valueall <= 0", "generate double measure = 100 * valueele / valueall", "generate byte n = 1"]
    elif name == "ev_share":
        lines += [f'keep if entity == "afdc_reg:{st}" & substr(variable, 1, 14) == "registrations_"', 'generate double ev = value if variable == "registrations_ev"',
                  "collapse (sum) ev (sum) all = value, by(year)", "keep if all > 0", "generate double measure = 100 * ev / all", "generate byte n = 1"]
    else:
        names = " ".join(sorted(s for s in STATES if s != "US"))
        lines += ['keep if variable == "ev_dcfast_ports"', 'generate str2 st = upper(word(subinstr(entity, ":", " ", .), 2))',
                  f'keep if strpos(" {names} ", " " + st + " ") > 0']
        if st != "US":
            lines += [f'keep if st == "{st}"']
        lines += ["collapse (sum) measure = value, by(year)", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
CANDIDATES = [
    C("renewable_share", FAMILY, renewable_share, "percent of primary energy production", 1, 11, 1.0, "RENEWABLES IN US ENERGY PRODUCTION",
      "renewables' share of US primary energy production", lambda w: "renewables' share of US primary energy production",
      "EIA's Monthly Energy Review, primary energy in Btu; renewables count hydro, wind, solar, wood, waste, geothermal and biofuels together.",
      reproduce("renewable_share"), consequence=3),
    C("home_electric_spend", FAMILY, home_electric_spend, "percent of home energy spending", 1, 1, 2.0, "ELECTRICITY IN WHAT HOMES SPEND ON ENERGY",
      "electricity's share of the residential sector's energy expenditures", lambda w: f"electricity's share of what households in {w} spend on energy",
      "EIA's State Energy Data System, nominal dollars; a share of spending moves with prices as much as with use.", reproduce("home_electric_spend"),
      first_words="the first year the ERW's table holds", consequence=2),
    C("ev_share", FAMILY, ev_share, "percent of registered light-duty vehicles", 2, 1, 0.5, "ELECTRIC CARS ON THE ROAD",
      "battery electric vehicles' share of the light-duty vehicles registered", lambda w: f"battery electric vehicles' share of the light-duty vehicles registered in {w}",
      "The Alternative Fuels Data Center's registrations (Experian), a stock not sales; plug-in hybrids are counted apart.", reproduce("ev_share"),
      first_words="the first year the ERW's table holds", consequence=2),
    C("dcfast_ports", FAMILY, dcfast_ports, "ports", 0, 1, 2000.0, "FAST CHARGERS",
      "public DC fast charging ports at the year's end", lambda w: f"the public DC fast charging ports in {w}",
      "The Alternative Fuels Data Center's historical station counts, public ports only, counted near each year's end.", reproduce("dcfast_ports"),
      first_words="the first year the ERW's table holds", consequence=2),
]
for _P in CANDIDATES:
    if _P["name"] != "renewable_share":
        _P["rank_region"] = generation._us_first
        _P["rank"] = lambda c: abs(c["change"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, the rest of the US tables (chain 166)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY, cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
