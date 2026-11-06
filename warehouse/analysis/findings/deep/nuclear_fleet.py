#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "generation_pipeline", second part: the fleets (session 3006).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Public sources:

    eia_nuclear_outages_daily             EIA's US nuclear capacity and outage by day, 2007 on (MW, and the outage share)
    eia_nuclear_outages_generator_daily   the same by reactor (EIA's plant and reactor ids)
    eia923_plant_fuel_annual              EIA-923 by plant, fuel and year, 2001 to 2024: net generation (MWh) and fuel
                                          consumed (TBtu); a fleet's heat rate is its fuel over its generation

EIA's capacity factors by technology (eia_capacity_factors_monthly) hold 2023 to 2025 only and are not hunted (the
window test needs four full years). A reactor's uprate is a step: its typical yearly move is zero and the hunt's
strength cannot be computed, so uprates are not a candidate; the US fleet's capacity is.

    python warehouse/analysis/findings/deep/nuclear_fleet.py --dry-run
    python warehouse/analysis/findings/deep/nuclear_fleet.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import fuels_carbon  # noqa: E402
import generation  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "generation_pipeline"
OUT_LINE = 0.5                     # a reactor's day counts as an outage day when at least half its capacity is out
COAL = ("BIT", "SUB", "LIG", "RC", "WC", "ANT", "SC")
HR_RANGE = (6.0, 15.0)            # MMBtu per MWh: a fleet's heat rate outside it is not a fleet's
STATES = generation.STATES


def us_outage_share(in_dir=None):
    """The year's mean of EIA's daily outage share of the US nuclear fleet (percent of capacity)."""
    d = hm.series("eia_nuclear_outages_daily", in_dir, variables=["outage_share"], entities=["eia_nuclear_outages:US"])
    rows = [hm._row("us_nuclear", "the US nuclear fleet", y, float(100 * s["value"].mean()), len(s)) for y, s in d.groupby(d["ts"].dt.year)]
    return {"rows": rows, "tables": {"us_nuclear": ["eia_nuclear_outages_daily"]}}


def us_nuclear_capacity(in_dir=None):
    """The year's mean of EIA's daily US nuclear capacity (MW)."""
    d = hm.series("eia_nuclear_outages_daily", in_dir, variables=["capacity"], entities=["eia_nuclear_outages:US"])
    rows = [hm._row("us_nuclear_cap", "the US nuclear fleet", y, float(s["value"].mean()), len(s)) for y, s in d.groupby(d["ts"].dt.year)]
    return {"rows": rows, "tables": {"us_nuclear_cap": ["eia_nuclear_outages_daily"]}}


def reactor_outage_days(in_dir=None):
    """By reactor: the days of the year with at least half its capacity out."""
    d = hm.series("eia_nuclear_outages_generator_daily", in_dir, variables=["capacity", "outage"], extra=("node",))
    names = d.dropna(subset=["node"]).drop_duplicates("entity").set_index("entity")["node"].to_dict()
    w = d.pivot_table(index=["entity", "ts"], columns="variable", values="value").reset_index().dropna(subset=["capacity"])
    w = w[w["capacity"] > 0]
    w["out"] = w["outage"].fillna(0.0) >= OUT_LINE * w["capacity"]
    # session 3006: only the reactors that report a whole 2007 and a whole 2025; a retired reactor's last years and a new
    # one's start-up are not a trend of its outages
    days = w.groupby(["entity", w["ts"].dt.year]).size().unstack()
    keep = days.index[(days.get(2007, 0) >= 330) & (days.get(2025, 0) >= 330)]
    w = w[w["entity"].isin(keep)]
    rows, tables = [], {}
    for ent, g in w.groupby("entity"):
        fac, gen_ = ent.split(":")[1], ent.split(":")[2]
        region, words = f"nuc_{fac}_{gen_}", str(names.get(ent, ent))
        for y, s in g.groupby(g["ts"].dt.year):
            rows.append(hm._row(region, words, y, float(s["out"].sum()), len(s)))
        tables[region] = ["eia_nuclear_outages_generator_daily"]
    return {"rows": rows, "tables": tables}


def fleet(in_dir):
    def build():
        d = hm.series("eia923_plant_fuel_annual", in_dir, variables=["net_generation", "fuel_consumed"], extra=("geo",))
        p = d["entity"].str.split(":", expand=True)
        d["f2002"], d["ft"], d["year"] = p[2], p[3], d["ts"].dt.year
        return d[d["f2002"] != "ALL"]
    return hm._cached(("deep_eia923", in_dir), build)


def _heat_rate(in_dir, codes, prefix):
    d = fleet(in_dir)
    d = d[d["f2002"].isin(codes)]
    d = d.assign(state=d["geo"].astype(str).str[3:])
    rows, tables = [], {}
    for st, g in [("US", d)] + list(d[d["state"].isin(fuels_carbon.STATES)].groupby("state")):
        region, words = f"{prefix}_{st}", STATES.get(st, st)
        t = g.pivot_table(index="year", columns="variable", values="value", aggfunc="sum")
        for y, r in t.iterrows():
            if r.get("net_generation", 0) > 0 and r.get("fuel_consumed", 0) > 0:
                # session 3006: an EIA-923 year is a whole year as EIA publishes it; its count of plant rows grows over the
                # years and is no test of a year being whole, so each year counts as one observation
                rows.append(hm._row(region, words, y, float(r["fuel_consumed"] * 1e6 / r["net_generation"]), 1))
        tables[region] = ["eia923_plant_fuel_annual"]
    # session 3006: a state whose fleet shows any year outside 6 to 15 MMBtu per MWh is left out: there combined heat and
    # power plants' fuel for heat, or a few megawatt-hours, carry the ratio (Montana's gas 70.6 in 2001, Idaho's coal 73.1)
    bad = {r["region"] for r in rows if r["value"] is not None and not (HR_RANGE[0] <= r["value"] <= HR_RANGE[1])}
    rows = [r for r in rows if r["region"] not in bad]
    return {"rows": rows, "tables": {k: v for k, v in tables.items() if k not in bad}}


def nuclear_share(in_dir=None):
    """Nuclear's share of the state's net generation over the year (percent)."""
    return generation._share(in_dir, "NUC")


def hydro_share(in_dir=None):
    """Conventional hydro's share of the state's net generation over the year (percent)."""
    return generation._share(in_dir, "HYC")


def gas_heat_rate(in_dir=None):
    """The gas-fired fleet's fuel over its net generation (MMBtu per MWh), every plant row whose 2002 fuel code is NG."""
    return _heat_rate(in_dir, ("NG",), "hr_gas")


def coal_heat_rate(in_dir=None):
    """The coal-fired fleet's fuel over its net generation (MMBtu per MWh), the coal fuel codes of EIA-923."""
    return _heat_rate(in_dir, COAL, "hr_coal")


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_HEAD = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <{table}.csv>

{label}, by calendar year{extra}.
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, usecols={cols!r}, dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["year"] = d["ts_utc"].str[:4].astype(int)
'''

PY_BODY = {
    "us_outage_share": ("d = d[(d['entity'] == 'eia_nuclear_outages:US') & (d['variable'] == 'outage_share')]\n"
                        "for y, s in d.groupby('year'):\n    print(y, round(float(100 * s['value'].mean()), 6), len(s))\n"),
    "us_nuclear_capacity": ("d = d[(d['entity'] == 'eia_nuclear_outages:US') & (d['variable'] == 'capacity')]\n"
                            "for y, s in d.groupby('year'):\n    print(y, round(float(s['value'].mean()), 6), len(s))\n"),
    "reactor_outage_days": ("d = d[(d['entity'] == {ent!r}) & d['variable'].isin(['capacity', 'outage'])]\n"
                            "w = d.pivot_table(index=['ts_utc', 'year'], columns='variable', values='value').reset_index().dropna(subset=['capacity'])\n"
                            "w = w[w['capacity'] > 0]\nw['out'] = w['outage'].fillna(0.0) >= 0.5 * w['capacity']\n"
                            "for y, s in w.groupby('year'):\n    print(y, int(s['out'].sum()), len(s))\n"),
    "heat_rate": ("p = d['entity'].str.split(':', expand=True)\nd = d[p[2].isin({codes!r}) & (p[2] != 'ALL')]\n{state_filter}"
                  "t = d.pivot_table(index='year', columns='variable', values='value', aggfunc='sum')\n"
                  "for y, r in t.iterrows():\n    if r.get('net_generation', 0) > 0 and r.get('fuel_consumed', 0) > 0:\n"
                  "        print(y, round(float(r['fuel_consumed'] * 1e6 / r['net_generation']), 6), 1)\n"),
}


def _hr(region):
    prefix, st = region.rsplit("_", 1)
    return (("NG",) if prefix == "hr_gas" else COAL), st


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    if name in ("us_outage_share", "us_nuclear_capacity"):
        return PY_HEAD.format(name=name, region=region, table="eia_nuclear_outages_daily", label=label, extra="",
                              cols=["entity", "variable", "ts_utc", "value"]) + PY_BODY[name]
    if name == "reactor_outage_days":
        ent = "eia_nuclear_outages_gen:" + ":".join(region.split("_")[1:3])
        return PY_HEAD.format(name=name, region=region, table="eia_nuclear_outages_generator_daily", label=label, extra=f" (entity {ent})",
                              cols=["entity", "variable", "ts_utc", "value"]) + PY_BODY[name].format(ent=ent)
    codes, st = _hr(region)
    sf = "" if st == "US" else f"d = d[d['geo'] == 'US-{st}']\n"
    return PY_HEAD.format(name=name, region=region, table="eia923_plant_fuel_annual", label=label,
                          extra=", " + ("the United States" if st == "US" else STATES[st]) + "; MMBtu = TBtu times 1,000,000",
                          cols=["entity", "variable", "ts_utc", "value", "geo"]) + PY_BODY["heat_rate"].format(codes=list(codes), state_filter=sf)


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
            "clear all"]
    if name in ("us_outage_share", "us_nuclear_capacity"):
        var = "outage_share" if name == "us_outage_share" else "capacity"
        lines = head + ['import delimited "eia_nuclear_outages_daily.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "eia_nuclear_outages:US" & variable == "{var}"', "destring value, replace force", "drop if missing(value)",
                        "generate int year = real(substr(ts_utc, 1, 4))", "collapse (mean) measure = value (count) n = value, by(year)"]
        if name == "us_outage_share":
            lines += ["replace measure = 100 * measure"]
    elif name == "reactor_outage_days":
        ent = "eia_nuclear_outages_gen:" + ":".join(region.split("_")[1:3])
        lines = head + ['import delimited "eia_nuclear_outages_generator_daily.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "{ent}" & (variable == "capacity" | variable == "outage")', "destring value, replace force", "drop if missing(value)",
                        "keep ts_utc variable value", "reshape wide value, i(ts_utc) j(variable) string", "drop if missing(valuecapacity) | valuecapacity <= 0",
                        "replace valueoutage = 0 if missing(valueoutage)", "generate byte out = valueoutage >= 0.5 * valuecapacity",
                        "generate int year = real(substr(ts_utc, 1, 4))", "collapse (sum) measure = out (count) n = out, by(year)"]
    else:
        codes, st = _hr(region)
        lines = head + ['import delimited "eia923_plant_fuel_annual.csv", varnames(1) stringcols(_all) clear',
                        'generate str8 f2002 = word(subinstr(entity, ":", " ", .), 3)', "keep if " + " | ".join(f'f2002 == "{c}"' for c in codes)]
        if st != "US":
            lines += [f'keep if geo == "US-{st}"']
        lines += ["destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
                  'generate double gen = value if variable == "net_generation"', 'generate double fuel = value if variable == "fuel_consumed"',
                  "collapse (sum) gen (sum) fuel, by(year)", "keep if gen > 0 & fuel > 0", "generate double measure = fuel * 1000000 / gen", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
CANDIDATES = [
    C("us_outage_share", FAMILY, us_outage_share, "percent of capacity", 2, 330, 0.5, "THE NUCLEAR FLEET'S OUTAGES",
      "the year's mean of EIA's daily outage share of the US nuclear fleet",
      lambda w: "the mean share of the US nuclear fleet's capacity out of service on a day",
      "EIA's daily outage estimate from the NRC's reactor status reports, planned refuelling and forced outages together.",
      reproduce("us_outage_share"), consequence=3),
    C("us_nuclear_capacity", FAMILY, us_nuclear_capacity, "MW", 0, 330, 200.0, "THE NUCLEAR FLEET'S CAPACITY",
      "the year's mean of EIA's daily US nuclear capacity",
      lambda w: "the mean daily capacity of the US nuclear fleet",
      "EIA's capacity as used for its outage estimate; it moves with retirements, new reactors and uprates together, and the measure does not separate them.",
      reproduce("us_nuclear_capacity"), consequence=3),
    C("reactor_outage_days", FAMILY, reactor_outage_days, "days", 0, 330, 5.0, "A REACTOR'S OUTAGE DAYS",
      "the days of the year on which at least half the reactor's capacity was out",
      lambda w: f"the number of days on which at least half of {w}'s capacity was out",
      "EIA's daily estimate; refuelling outages fall every 18 or 24 months, so a reactor's years alternate, and the measure counts planned and forced days alike; only reactors that report all of 2007 and 2025 are counted.",
      reproduce("reactor_outage_days"), consequence=1),
    C("nuclear_share", FAMILY, nuclear_share, "percent of net generation", 1, 11, 2.0, "NUCLEAR'S SHARE",
      "nuclear's share of the state's net generation over the year", lambda w: f"nuclear's share of net generation in {w}",
      generation.LIMIT_STATE, lambda region: {"py": generation.reproduce_py("nuclear_share", region), "do": generation.reproduce_do("nuclear_share", region)}, consequence=3),
    C("hydro_share", FAMILY, hydro_share, "percent of net generation", 1, 11, 2.0, "HYDRO'S SHARE",
      "conventional hydro's share of the state's net generation over the year", lambda w: f"conventional hydro's share of net generation in {w}",
      generation.LIMIT_STATE + " Hydro follows the year's water, so a dry last year moves the figure.",
      lambda region: {"py": generation.reproduce_py("hydro_share", region), "do": generation.reproduce_do("hydro_share", region)}, consequence=2),
    C("gas_heat_rate", FAMILY, gas_heat_rate, "MMBtu per MWh", 2, 1, 0.1, "THE GAS FLEET'S HEAT RATE",
      "the gas-fired fleet's fuel consumed over its net generation, EIA-923",
      lambda w: f"the gas-fired fleet's fuel per MWh in {w}",
      "EIA-923's total fuel consumed, which at combined heat and power plants includes fuel for their useful heat, so a fleet with more such plants shows a higher figure.",
      reproduce("gas_heat_rate"), consequence=3),
    C("coal_heat_rate", FAMILY, coal_heat_rate, "MMBtu per MWh", 2, 1, 0.1, "THE COAL FLEET'S HEAT RATE",
      "the coal-fired fleet's fuel consumed over its net generation, EIA-923",
      lambda w: f"the coal-fired fleet's fuel per MWh in {w}",
      "EIA-923's total fuel consumed, combined heat and power plants' useful heat included; a fleet that runs less often runs at less efficient loads.",
      reproduce("coal_heat_rate"), consequence=2),
]
for _P in CANDIDATES:
    if _P["name"] in ("gas_heat_rate", "coal_heat_rate", "nuclear_share", "hydro_share"):
        _P["rank_region"] = generation._us_first
    if _P["name"] in ("nuclear_share", "hydro_share"):
        _P["rank"] = lambda c: abs(c["change"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family generation, the fleets (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place (session 3019)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_fleets", cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
