#!/usr/bin/env python3
"""The findings hunt of chain 502, family "regions": the six regions the site has never shown, session 8202.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. EIA's Southeast, Florida, the
Carolinas, Tennessee, the Northwest and the Southwest (public EIA rows):

    demand (hourly930.region_demand: the region's authorities' demand summed by hour, eia930_ba_demand_hourly):
        peak_mw          the year's highest hour of demand
        mean_mw          the year's mean hour of demand
        winter_summer    the winter peak (January, February, December) as a percent of the summer peak (June to August)
        top_winter       the share of the year's 100 highest hours that fell in January, February or December
        load_factor      the mean hour as a percent of the peak hour
    net generation against demand (eia930_region_hourly's net generation over the summed demand, hours both held):
        gen_ratio        the region's net generation as a percent of its demand
    what they burn (eia_state_generation_monthly, the states at each region's core, 2001 on; the hourly tables hold
    no fuel and EIA-930's fuel mix in the ERW starts in August 2026):
        coal_share, gas_share, solar_share, nuclear_share   a fuel's share of the states' net generation

    python warehouse/analysis/findings/deep/regions.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/regions.py --load
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import hourly930 as h  # noqa: E402  (sets builder.CHAIN to 502)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "regions"
SIX = ["SE", "FLA", "CAR", "TEN", "NW", "SW"]
WINTER, SUMMER = (1, 2, 12), (6, 7, 8)
TOP = 100
STATES = {"SE": (["GA", "AL"], "Georgia and Alabama (the core of EIA's Southeast region)"),
          "FLA": (["FL"], "Florida (the state)"),
          "CAR": (["NC", "SC"], "North and South Carolina (EIA's Carolinas region)"),
          "TEN": (["TN"], "Tennessee (the state, the core of the Tennessee Valley Authority)"),
          "NW": (["WA", "OR", "ID", "MT", "UT", "WY", "CO", "NV"], "the eight states of EIA's Northwest region (WA, OR, ID, MT, UT, WY, CO, NV)"),
          "SW": (["AZ", "NM"], "Arizona and New Mexico (the core of EIA's Southwest region)")}
FUEL = {"coal_share": ("COW", "coal"), "gas_share": ("NG", "natural gas"), "solar_share": ("SUN", "utility-scale solar"), "nuclear_share": ("NUC", "nuclear")}
CTX = {}


def _in():
    return CTX.get("in_dir") or common.DEFAULT_IN_DIR


def words(code):
    return f"{h.REG[code]} (EIA's region)"


def demand(in_dir):
    d = h.region_demand(in_dir)
    return d[d["code"].isin(SIX)]


def _by_year(fn, tables):
    def f(in_dir=None):
        d = demand(in_dir)
        rows, tabs = [], {}
        for code, g in d.groupby("code"):
            k = f"rd_{code.lower()}"
            for y, s in g.groupby("year"):
                v = fn(s)
                if v is not None:
                    rows.append(hm._row(k, words(code), y, float(v), len(s)))
            tabs[k] = list(tables)
        return {"rows": rows, "tables": tabs}
    return f


def _peak(s):
    return s["demand_mw"].max()


def _winter_summer(s):
    w, m = s[s["month"].isin(WINTER)]["demand_mw"], s[s["month"].isin(SUMMER)]["demand_mw"]
    return None if not len(w) or not len(m) else w.max() / m.max() * 100


def _top_winter(s):
    t = s.nlargest(TOP, "demand_mw")
    return t["month"].isin(WINTER).mean() * 100


peak_mw = _by_year(_peak, ["eia930_ba_demand_hourly"])
mean_mw = _by_year(lambda s: s["demand_mw"].mean(), ["eia930_ba_demand_hourly"])
winter_summer = _by_year(_winter_summer, ["eia930_ba_demand_hourly"])
top_winter = _by_year(_top_winter, ["eia930_ba_demand_hourly"])
load_factor = _by_year(lambda s: s["demand_mw"].mean() / s["demand_mw"].max() * 100, ["eia930_ba_demand_hourly"])


def gen_ratio(in_dir=None):
    g = h.region(in_dir, variables=("net_generation_mw",))
    g = g[g["code"].isin(SIX)].dropna(subset=["net_generation_mw"])
    g = g[g["net_generation_mw"] > 0]
    g = g[g["net_generation_mw"] <= 3 * g.groupby(["code", "year"])["net_generation_mw"].transform("median")]
    d = demand(in_dir)[["code", "ts_utc", "demand_mw"]].merge(g[["code", "ts_utc", "year", "net_generation_mw"]], on=["code", "ts_utc"])
    rows, tabs = [], {}
    for code, x in d.groupby("code"):
        k = f"rg_{code.lower()}"
        for y, s in x.groupby("year"):
            rows.append(hm._row(k, words(code), y, float(s["net_generation_mw"].sum() / s["demand_mw"].sum() * 100), len(s)))
        tabs[k] = ["eia930_region_hourly", "eia930_ba_demand_hourly"]
    return {"rows": rows, "tables": tabs}


def state_gen(in_dir):
    def build():
        sts = sorted({s for v in STATES.values() for s in v[0]})
        ents = [f"eia:generation:{s}:{f}" for s in sts for f in ["ALL"] + [v[0] for v in FUEL.values()]]
        d = hm.series("eia_state_generation_monthly", in_dir, variables=["net_generation"], entities=ents)
        d["state"], d["fuel"] = d["entity"].str.split(":").str[2], d["entity"].str.split(":").str[3]
        d["year"] = d["ts"].dt.year
        return d
    return hm._cached(("c502_state_gen", in_dir), build)


def _share(name):
    code_f = FUEL[name][0]

    def f(in_dir=None):
        d = state_gen(in_dir)
        rows, tabs = [], {}
        for code, (sts, w) in STATES.items():
            x = d[d["state"].isin(sts)]
            k = f"st_{code.lower()}_{code_f.lower()}"
            for y, s in x.groupby("year"):
                months = s[s["fuel"] == "ALL"].groupby("state")["ts"].nunique()
                if len(months) < len(sts) or months.min() < 12:
                    continue
                tot = s[s["fuel"] == "ALL"]["value"].sum()
                fu = s[s["fuel"] == code_f]["value"].sum()
                rows.append(hm._row(k, w, y, float(fu / tot * 100), 12))
            tabs[k] = ["eia_state_generation_monthly"]
        return {"rows": rows, "tables": tabs}
    return f


coal_share, gas_share, solar_share, nuclear_share = (_share(n) for n in ("coal_share", "gas_share", "solar_share", "nuclear_share"))


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_MEASURE = {"peak_mw": "s['demand_mw'].max()", "mean_mw": "s['demand_mw'].mean()",
              "load_factor": "s['demand_mw'].mean() / s['demand_mw'].max() * 100",
              "winter_summer": "s[s['month'].isin([1, 2, 12])]['demand_mw'].max() / s[s['month'].isin([6, 7, 8])]['demand_mw'].max() * 100",
              "top_winter": f"s.nlargest({TOP}, 'demand_mw')['month'].isin([1, 2, 12]).mean() * 100"}
WHAT = {"peak_mw": "The year's highest hour of demand (MW)", "mean_mw": "The year's mean hour of demand (MW)",
        "load_factor": "The year's mean hour of demand as a percent of its highest hour",
        "winter_summer": "The year's winter peak (January, February, December) as a percent of its summer peak (June to August)",
        "top_winter": f"The share (percent) of the year's {TOP} highest hours of demand that fell in January, February or December"}


def reproduce_py(name, region):
    code = region.split("_")[1].upper()
    if name in PY_MEASURE:
        body = (f"d = region_demand(sys.argv[1], '{code}')\nd['month'] = d['ts_utc'].str[5:7].astype(int)\n"
                f"for y, s in d.groupby('year'):\n    print(y, round(float({PY_MEASURE[name]}), 6), len(s))\n")
        return (h.py_doc(name, region, ["eia930_ba_demand_hourly"], f"{WHAT[name]}, {h.REG[code]}: the demand of the region's authorities summed by hour.")
                + h.PY_READ + h.PY_REGION_DEMAND + body)
    if name == "gen_ratio":
        body = (f"g = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\ng = g[(g['entity'] == 'eia930:{code}') & (g['variable'] == 'net_generation_mw')].copy()\n"
                "g['gen'] = pd.to_numeric(g['value'], errors='coerce')\ng = g.dropna(subset=['gen'])\ng = g[g['gen'] > 0]\ng['year'] = g['ts_utc'].str[:4].astype(int)\n"
                "g = g[g['gen'] <= 3 * g.groupby('year')['gen'].transform('median')]\n"
                f"w = region_demand(sys.argv[2], '{code}').merge(g[['ts_utc', 'gen']], on='ts_utc')\n"
                "for y, s in w.groupby('year'):\n    print(y, round(float(s['gen'].sum() / s['demand_mw'].sum() * 100), 6), len(s))\n")
        return (h.py_doc(name, region, ["eia930_region_hourly", "eia930_ba_demand_hourly"],
                         f"{h.REG[code]}'s net generation as a percent of its demand (the region table's net generation over its authorities' demand summed by hour), hours both are held.")
                + h.PY_READ + h.PY_REGION_DEMAND + body)
    rc, fc = region.split("_")[1].upper(), region.split("_")[2].upper()
    sts = STATES[rc][0]
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nsts = {sts!r}\n"
            f"d = d[(d['variable'] == 'net_generation') & d['entity'].isin([f'eia:generation:{{s}}:{{f}}' for s in sts for f in ('ALL', '{fc}')])].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['value'])\nd['state'], d['fuel'] = d['entity'].str.split(':').str[2], d['entity'].str.split(':').str[3]\n"
            "d['year'] = d['ts_utc'].str[:4].astype(int)\nfor y, s in d.groupby('year'):\n    a = s[s['fuel'] == 'ALL']\n    months = a.groupby('state')['ts_utc'].nunique()\n"
            "    if len(months) < len(sts) or months.min() < 12:\n        continue\n"
            f"    print(y, round(float(s[s['fuel'] == '{fc}']['value'].sum() / a['value'].sum() * 100), 6), 12)\n")
    return h.py_doc(name, region, ["eia_state_generation_monthly"], f"{FUEL[name][1].capitalize()}'s share (percent) of the net generation of {', '.join(sts)}, years with all twelve months of every state.") + h.PY_READ + body


DO_MEASURE = {"peak_mw": ["collapse (max) measure = demand (count) n = demand, by(year)"],
              "mean_mw": ["collapse (mean) measure = demand (count) n = demand, by(year)"],
              "load_factor": ["collapse (mean) avg = demand (max) peak = demand (count) n = demand, by(year)", "generate double measure = 100 * avg / peak"],
              "winter_summer": ["generate int month = real(substr(ts_utc, 6, 2))", "generate double wdem = demand if month == 1 | month == 2 | month == 12",
                                "generate double sdem = demand if month >= 6 & month <= 8", "collapse (max) wpeak = wdem (max) speak = sdem (count) n = demand, by(year)",
                                "generate double measure = 100 * wpeak / speak"],
              "top_winter": ["generate int month = real(substr(ts_utc, 6, 2))", "generate double negdem = -demand", "bysort year (negdem ts_utc): generate long rank = _n",
                             "bysort year: generate long n = _N", f"keep if rank <= {TOP}", "generate double winter = 100 * (month == 1 | month == 2 | month == 12)",
                             "collapse (mean) measure = winter (first) n = n, by(year)"]}


def reproduce_do(name, region):
    code = region.split("_")[1].upper()
    if name in DO_MEASURE:
        lines = h.do_head(name, region, ["eia930_ba_demand_hourly"]) + h.do_region_demand(code) + DO_MEASURE[name]
    elif name == "gen_ratio":
        lines = (h.do_head(name, region, ["eia930_region_hourly", "eia930_ba_demand_hourly"]) + h.do_region_demand(code) + ["drop year", "tempfile dem", "save `dem'",
                 'import delimited "eia930_region_hourly.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia930:{code}" & variable == "net_generation_mw"',
                 "keep ts_utc value", "destring value, replace force", "rename value gen", "drop if missing(gen) | gen <= 0", "generate int year = real(substr(ts_utc, 1, 4))",
                 "bysort year: egen double med = median(gen)", "drop if gen > 3 * med", "merge 1:1 ts_utc using `dem', keep(match) nogenerate",
                 "collapse (sum) gen = gen (sum) demand = demand (count) n = gen, by(year)", "generate double measure = 100 * gen / demand"])
    else:
        rc, fc = region.split("_")[1].upper(), region.split("_")[2].upper()
        sts = STATES[rc][0]
        cond = " | ".join(f'entity == "eia:generation:{s}:ALL" | entity == "eia:generation:{s}:{fc}"' for s in sts)
        lines = h.do_head(name, region, ["eia_state_generation_monthly"]) + ['import delimited "eia_state_generation_monthly.csv", varnames(1) stringcols(_all) clear',
                                                                            'keep if variable == "net_generation"', f"keep if {cond}", "keep entity ts_utc value", "destring value, replace force",
                                                                            "drop if missing(value)", "generate str2 state = substr(entity, 16, 2)", "generate str4 fuel = substr(entity, 19, .)",
                                                                            "generate int year = real(substr(ts_utc, 1, 4))", "generate double allgen = value if fuel == \"ALL\"",
                                                                            f"generate double fuelgen = value if fuel == \"{fc}\"", "generate byte allrow = fuel == \"ALL\"",
                                                                            "bysort year state allrow: generate long nmonths = _N if allrow", "bysort year: egen long minmonths = min(nmonths)",
                                                                            "bysort year state: generate byte firststate = _n == 1", "bysort year: egen long nstates = total(firststate)",
                                                                            f"keep if minmonths >= 12 & nstates == {len(sts)}",
                                                                            "collapse (sum) allgen = allgen (sum) fuelgen = fuelgen, by(year)", "generate double measure = 100 * fuelgen / allgen", "generate byte n = 12"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LD = "EIA-930 as the balancing authorities report it; a region's demand is the sum of its authorities that file demand, an hour held only when all of them do; not adjusted for weather."
LS = "EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary."
CANDIDATES = [
    C("peak_mw", FAMILY, peak_mw, "MW", 0, 8000, 300.0, "THE YEAR'S PEAK HOUR", "the year's highest hour of demand",
      lambda w: f"the highest hour of demand in {w}", LD, reproduce("peak_mw"), consequence=3),
    C("mean_mw", FAMILY, mean_mw, "MW", 0, 8000, 200.0, "THE YEAR'S MEAN HOUR", "the year's mean hour of demand",
      lambda w: f"the mean hour of demand in {w}", LD, reproduce("mean_mw"), consequence=3),
    C("winter_summer", FAMILY, winter_summer, "percent", 1, 8000, 3.0, "WINTER'S PEAK AGAINST SUMMER'S",
      "the winter peak (January, February, December) as a percent of the summer peak (June to August)",
      lambda w: f"the winter peak hour of {w} as a percent of its summer peak hour", LD + " A year's winter is its own January, February and December.",
      reproduce("winter_summer"), consequence=3),
    C("top_winter", FAMILY, top_winter, "percent of the top hours", 1, 8000, 10.0, "WHEN THE PEAK HOURS FALL",
      f"the share of the year's {TOP} highest hours of demand that fell in January, February or December",
      lambda w: f"the share of the year's {TOP} highest hours of demand in {w} that fell in January, February or December", LD + " Months are UTC months.",
      reproduce("top_winter"), consequence=2),
    C("load_factor", FAMILY, load_factor, "percent", 1, 8000, 2.0, "THE LOAD FACTOR", "the year's mean hour of demand as a percent of its highest hour",
      lambda w: f"the load factor of {w} (its mean hour of demand as a percent of its highest)", LD, reproduce("load_factor"), consequence=2),
    C("gen_ratio", FAMILY, gen_ratio, "percent", 1, 8000, 2.0, "WHAT A REGION GENERATES AGAINST WHAT IT USES",
      "the region's net generation as a percent of its demand",
      lambda w: f"the net generation of {w} as a percent of its demand",
      "EIA-930 as the authorities report it; net generation includes the authorities that file no demand, and demand is summed from those that do, hours both are held.",
      reproduce("gen_ratio"), consequence=3),
    C("coal_share", FAMILY, coal_share, "percent", 1, 12, 3.0, "WHAT A REGION BURNS: COAL", "coal's share of the states' net generation",
      lambda w: f"coal's share of the net generation of {w}", LS, reproduce("coal_share"), consequence=3),
    C("gas_share", FAMILY, gas_share, "percent", 1, 12, 3.0, "WHAT A REGION BURNS: NATURAL GAS", "natural gas's share of the states' net generation",
      lambda w: f"natural gas's share of the net generation of {w}", LS, reproduce("gas_share"), consequence=3),
    C("solar_share", FAMILY, solar_share, "percent", 1, 12, 1.0, "WHAT A REGION GENERATES: SOLAR", "utility-scale solar's share of the states' net generation",
      lambda w: f"utility-scale solar's share of the net generation of {w}", LS + " Small rooftop systems are not in this figure.", reproduce("solar_share"), consequence=2),
    C("nuclear_share", FAMILY, nuclear_share, "percent", 1, 12, 2.0, "WHAT A REGION GENERATES: NUCLEAR", "nuclear's share of the states' net generation",
      lambda w: f"nuclear's share of the net generation of {w}", LS, reproduce("nuclear_share"), consequence=2),
]
# session 8202: one story once. Tennessee's net generation against demand is the trade family's draft of its net imports
# (rn_ten); the Southeast's and Tennessee's share of winter in the top hours is their winter peak against summer's.
# session 8205: the Southeast's and Tennessee's winter peak against summer's are chain 164's drafts of Southern Company and
# TVA (docs/findings/demand/winter-vs-summer-ba-soco.md, -tva.md); loaded before this was seen, they wait for Samuel's ruling
SKIP = {("gen_ratio", "rg_ten"), ("top_winter", "rd_se"), ("top_winter", "rd_ten"), ("winter_summer", "rd_se"), ("winter_summer", "rd_ten")}
for _P in CANDIDATES:
    if _P["unit"] == "MW":
        _P["rank"] = lambda c: abs(c["change"] / c["first"]) if c["first"] else 0.0
    elif _P["name"].endswith("_share"):
        _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = 3 if _P["name"] == "solar_share" else 4

    def _wrap(fn, name):
        def f(in_dir=None):
            got = fn(in_dir)
            got["rows"] = [r for r in got["rows"] if (name, r["region"]) not in SKIP]
            return got
        return f
    _P["_fn"] = _wrap(_P["_fn"], _P["name"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, family regions")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--max-drafts", type=int, default=24)
    ap.add_argument("--replace", action="store_true")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    cands = [P for P in CANDIDATES if not a.only or P["name"] in a.only.split(",")]
    builder.run(FAMILY, cands, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
