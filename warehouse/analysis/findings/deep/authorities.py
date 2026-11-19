#!/usr/bin/env python3
"""The findings hunt of chain 502, family "authorities": the balancing authorities one by one, session 8205.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Every EIA-930 balancing
authority with a mean demand of at least 500 MW over 2019 to 2025 (public rows):

    ba_mean_mw         the year's mean hour of demand (eia930_ba_demand_hourly)
    ba_peak_mw         the year's highest hour of demand
    ba_gen_ratio       the authority's net generation as a percent of its demand (eia930_ba_supply_hourly over demand)
    ba_co2_intensity   the CO2 its generators emitted per MWh they generated (eia930_all_emissions over net generation)
    ba_coal_co2_share  coal's share of the CO2 its generators emitted (eia930_all_emissions)

The hourly tables hold no fuel before August 2026; EIA-930's CO2 by fuel, which EIA computes from each authority's
generation by fuel, is the mix this family can read since 2018. Faults: an hour of demand or net generation at or below
zero or above three times its year's median is dropped; an hour of CO2 below zero is dropped.

    python warehouse/analysis/findings/deep/authorities.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/authorities.py --load
"""

import argparse
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import hourly930 as h  # noqa: E402  (sets builder.CHAIN to 502)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "authorities"
MIN_MW = 500.0
FULL = list(range(2019, 2026))
CTX = {}


def words(code):
    return f"{h.ba_words(code)} ({code}, EIA-930 balancing authority)"


def _clean(d, col, by):
    d = d[d[col] > 0]
    return d[d[col] <= 3 * d.groupby(by)[col].transform("median")]


def demand(in_dir):
    def build():
        d = h.read("eia930_ba_demand_hourly", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"], keep=lambda c: c["variable"] == "demand_mw")
        d["ba"] = d.pop("entity").str.split(":").str[1]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        d = _clean(d.dropna(subset=["value"]), "value", ["ba", "year"])
        big = d[d["year"].isin(FULL)].groupby("ba")["value"].mean()
        return d[d["ba"].isin(big[big >= MIN_MW].index)].rename(columns={"value": "demand"})
    return hm._cached(("c502_ba_demand", in_dir), build)


def gen(in_dir):
    def build():
        d = h.read("eia930_ba_supply_hourly", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"], keep=lambda c: c["variable"] == "net_generation_mw")
        d["ba"] = d.pop("entity").str.split(":").str[1]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        return _clean(d.dropna(subset=["value"]), "value", ["ba", "year"]).rename(columns={"value": "gen"})
    return hm._cached(("c502_ba_gen", in_dir), build)


def co2(in_dir):
    def build():
        v = ["co2_emissions_generated", "co2_emissions_coal"]
        d = h.read("eia930_all_emissions", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"], keep=lambda c: c["variable"].isin(v))
        d["ba"] = d.pop("entity").str.split(":").str[1]
        d = d.dropna(subset=["value"])
        d = d[d["value"] >= 0]
        w = d.pivot_table(index=["ba", "ts_utc"], columns="variable", values="value", aggfunc="first").reset_index()
        w["year"] = w["ts_utc"].str[:4].astype(int)
        return w
    return hm._cached(("c502_ba_co2", in_dir), build)


def _rows(d, key_fn, tables):
    rows, tabs = [], {}
    for ba, g in d.groupby("ba"):
        k = f"ba_{ba.lower()}"
        for y, s in g.groupby("year"):
            v = key_fn(s)
            if v is not None:
                rows.append(hm._row(k, words(ba), y, float(v), len(s)))
        tabs[k] = list(tables)
    return {"rows": rows, "tables": tabs}


def ba_mean_mw(in_dir=None):
    return _rows(demand(in_dir), lambda s: s["demand"].mean(), ["eia930_ba_demand_hourly"])


SPIKE = 1.10                   # an hour more than 10 percent above both its neighbouring hours is a lone spike


def despike(d, col, by="ba"):
    """Drop a lone spike: an hour more than SPIKE times the larger of the hour before and the hour after (whichever are
    held). Hours are counted as days times 24 plus the hour, so a missing neighbour is not taken for one."""
    d = d.copy()
    d["t"] = (pd.to_datetime(d["ts_utc"].str[:10]).values.astype("datetime64[D]").astype("int64") * 24 + d["ts_utc"].str[11:13].astype(int))
    d = d.sort_values([by, "t"]) if by else d.sort_values("t")
    g = d.groupby(by) if by else d
    prev = g[col].shift(1).where(g["t"].shift(1) == d["t"] - 1)
    nxt = g[col].shift(-1).where(g["t"].shift(-1) == d["t"] + 1)
    near = pd.concat([prev, nxt], axis=1).max(axis=1)
    return d[~(d[col] > SPIKE * near)]


def ba_peak_mw(in_dir=None):
    return _rows(despike(demand(in_dir), "demand"), lambda s: s["demand"].max(), ["eia930_ba_demand_hourly"])


def ba_gen_ratio(in_dir=None):
    d = demand(in_dir).merge(gen(in_dir)[["ba", "ts_utc", "gen"]], on=["ba", "ts_utc"])
    return _rows(d, lambda s: s["gen"].sum() / s["demand"].sum() * 100, ["eia930_ba_supply_hourly", "eia930_ba_demand_hourly"])


def _co2_frame(in_dir):
    keep = set(demand(in_dir)["ba"].unique())
    c = co2(in_dir)
    return c[c["ba"].isin(keep)]


def ba_co2_intensity(in_dir=None):
    d = _co2_frame(in_dir).dropna(subset=["co2_emissions_generated"]).merge(gen(in_dir)[["ba", "ts_utc", "gen"]], on=["ba", "ts_utc"])
    return _rows(d, lambda s: s["co2_emissions_generated"].sum() / s["gen"].sum() * 1000, ["eia930_all_emissions", "eia930_ba_supply_hourly"])


def ba_coal_co2_share(in_dir=None):
    d = _co2_frame(in_dir).dropna(subset=["co2_emissions_generated", "co2_emissions_coal"])
    return _rows(d, lambda s: s["co2_emissions_coal"].sum() / s["co2_emissions_generated"].sum() * 100 if s["co2_emissions_generated"].sum() > 0 else None,
                 ["eia930_all_emissions"])


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_CLEAN = '''def clean(d, col):
    d = d[d[col] > 0]
    return d[d[col] <= 3 * d.groupby('year')[col].transform('median')]


def one(path, entity, variable, col):
    d = read(path, ['entity', 'variable', 'ts_utc', 'value'])
    d = d[(d['entity'] == entity) & (d['variable'] == variable)].copy()
    d[col] = pd.to_numeric(d['value'], errors='coerce')
    d = d.dropna(subset=[col])
    d['year'] = d['ts_utc'].str[:4].astype(int)
    return d[['ts_utc', 'year', col]]

'''


def reproduce_py(name, region):
    ba = region.split("_", 1)[1].upper()
    e = f"eia930:{ba}"
    if name in ("ba_mean_mw", "ba_peak_mw"):
        m = "mean" if name == "ba_mean_mw" else "max"
        body = f"d = clean(one(sys.argv[1], '{e}', 'demand_mw', 'demand'), 'demand')\n"
        if m == "max":
            body += ("d['t'] = pd.to_datetime(d['ts_utc'].str[:10]).values.astype('datetime64[D]').astype('int64') * 24 + d['ts_utc'].str[11:13].astype(int)\n"
                     "d = d.sort_values('t')\nprev = d['demand'].shift(1).where(d['t'].shift(1) == d['t'] - 1)\nnxt = d['demand'].shift(-1).where(d['t'].shift(-1) == d['t'] + 1)\n"
                     f"near = pd.concat([prev, nxt], axis=1).max(axis=1)\nd = d[~(d['demand'] > {SPIKE} * near)]\n")
        body += f"for y, s in d.groupby('year'):\n    print(y, round(float(s['demand'].{m}()), 6), len(s))\n"
        what = f"The year's {'mean' if m == 'mean' else 'highest'} hour of demand (MW) of {ba}" + ("." if m == "mean" else
                                                                                                 ", after dropping a lone spike (an hour more than 10 percent above both its neighbouring hours).")
        return h.py_doc(name, region, ["eia930_ba_demand_hourly"], what) + h.PY_READ + PY_CLEAN + body
    if name == "ba_gen_ratio":
        body = (f"g = clean(one(sys.argv[1], '{e}', 'net_generation_mw', 'gen'), 'gen')\nd = clean(one(sys.argv[2], '{e}', 'demand_mw', 'demand'), 'demand')\n"
                "w = d.merge(g[['ts_utc', 'gen']], on='ts_utc')\nfor y, s in w.groupby('year'):\n    print(y, round(float(s['gen'].sum() / s['demand'].sum() * 100), 6), len(s))\n")
        return h.py_doc(name, region, ["eia930_ba_supply_hourly", "eia930_ba_demand_hourly"], f"{ba}'s net generation as a percent of its demand, hours both are held.") + h.PY_READ + PY_CLEAN + body
    if name == "ba_co2_intensity":
        body = (f"c = one(sys.argv[1], '{e}', 'co2_emissions_generated', 'co2')\nc = c[c['co2'] >= 0]\ng = clean(one(sys.argv[2], '{e}', 'net_generation_mw', 'gen'), 'gen')\n"
                "w = c.merge(g[['ts_utc', 'gen']], on='ts_utc')\nfor y, s in w.groupby('year'):\n    print(y, round(float(s['co2'].sum() / s['gen'].sum() * 1000), 6), len(s))\n")
        return h.py_doc(name, region, ["eia930_all_emissions", "eia930_ba_supply_hourly"], f"The CO2 {ba}'s generators emitted per MWh they generated (kg per MWh), hours both are held.") + h.PY_READ + PY_CLEAN + body
    body = (f"t = one(sys.argv[1], '{e}', 'co2_emissions_generated', 'co2')\nk = one(sys.argv[1], '{e}', 'co2_emissions_coal', 'coal')\nt, k = t[t['co2'] >= 0], k[k['coal'] >= 0]\n"
            "w = t.merge(k[['ts_utc', 'coal']], on='ts_utc')\nfor y, s in w.groupby('year'):\n    if s['co2'].sum() > 0:\n        print(y, round(float(s['coal'].sum() / s['co2'].sum() * 100), 6), len(s))\n")
    return h.py_doc(name, region, ["eia930_all_emissions"], f"Coal's share (percent) of the CO2 {ba}'s generators emitted, hours both are held.") + h.PY_READ + PY_CLEAN + body


def _do_one(table, ba, variable, col, clean=True):
    out = [f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia930:{ba}" & variable == "{variable}"', "keep ts_utc value",
           "destring value, replace force", f"rename value {col}", f"drop if missing({col})", "generate int year = real(substr(ts_utc, 1, 4))"]
    if clean:
        out += [f"drop if {col} <= 0", f"bysort year: egen double med = median({col})", f"drop if {col} > 3 * med", "drop med"]
    else:
        out += [f"drop if {col} < 0"]
    return out


def reproduce_do(name, region):
    ba = region.split("_", 1)[1].upper()
    if name in ("ba_mean_mw", "ba_peak_mw"):
        st = "mean" if name == "ba_mean_mw" else "max"
        lines = h.do_head(name, region, ["eia930_ba_demand_hourly"]) + _do_one("eia930_ba_demand_hourly", ba, "demand_mw", "demand")
        if st == "max":
            lines += ["generate double t = date(substr(ts_utc, 1, 10), \"YMD\") * 24 + real(substr(ts_utc, 12, 2))", "sort t",
                      "generate double prev = demand[_n-1] if t[_n-1] == t - 1", "generate double nxt = demand[_n+1] if t[_n+1] == t + 1",
                      "generate double near = max(prev, nxt)", f"drop if demand > {SPIKE} * near & !missing(near)"]
        lines += [f"collapse ({st}) measure = demand (count) n = demand, by(year)"]
    elif name == "ba_gen_ratio":
        lines = (h.do_head(name, region, ["eia930_ba_supply_hourly", "eia930_ba_demand_hourly"]) + _do_one("eia930_ba_demand_hourly", ba, "demand_mw", "demand")
                 + ["drop year", "tempfile dem", "save `dem'"] + _do_one("eia930_ba_supply_hourly", ba, "net_generation_mw", "gen")
                 + ["merge 1:1 ts_utc using `dem', keep(match) nogenerate", "collapse (sum) gen = gen (sum) demand = demand (count) n = gen, by(year)", "generate double measure = 100 * gen / demand"])
    elif name == "ba_co2_intensity":
        lines = (h.do_head(name, region, ["eia930_all_emissions", "eia930_ba_supply_hourly"]) + _do_one("eia930_ba_supply_hourly", ba, "net_generation_mw", "gen")
                 + ["drop year", "tempfile g", "save `g'"] + _do_one("eia930_all_emissions", ba, "co2_emissions_generated", "co2", clean=False)
                 + ["merge 1:1 ts_utc using `g', keep(match) nogenerate", "collapse (sum) co2 = co2 (sum) gen = gen (count) n = co2, by(year)", "generate double measure = 1000 * co2 / gen"])
    else:
        lines = (h.do_head(name, region, ["eia930_all_emissions"]) + _do_one("eia930_all_emissions", ba, "co2_emissions_coal", "coal", clean=False)
                 + ["drop year", "tempfile k", "save `k'"] + _do_one("eia930_all_emissions", ba, "co2_emissions_generated", "co2", clean=False)
                 + ["merge 1:1 ts_utc using `k', keep(match) nogenerate", "collapse (sum) co2 = co2 (sum) coal = coal (count) n = co2, by(year)", "keep if co2 > 0",
                    "generate double measure = 100 * coal / co2"])
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LB = "EIA-930 as the authority filed it; an authority whose footprint changed (one that absorbed another) changes its figures with it; not adjusted for weather."
LE = ("EIA-930's CO2, which EIA estimates from the authority's hourly generation by fuel and standard emission rates, not a measured stack figure; "
      "CO2 from generation inside the authority, whatever is imported or exported.")
CANDIDATES = [
    C("ba_mean_mw", FAMILY, ba_mean_mw, "MW", 0, 8000, 100.0, "AN AUTHORITY'S MEAN HOUR", "the year's mean hour of demand",
      lambda w: f"the mean hour of demand of {w}", LB, reproduce("ba_mean_mw"), consequence=3),
    C("ba_peak_mw", FAMILY, ba_peak_mw, "MW", 0, 8000, 200.0, "AN AUTHORITY'S PEAK HOUR", "the year's highest hour of demand",
      lambda w: f"the highest hour of demand of {w}", LB, reproduce("ba_peak_mw"), consequence=3),
    C("ba_gen_ratio", FAMILY, ba_gen_ratio, "percent", 1, 8000, 3.0, "WHAT AN AUTHORITY GENERATES AGAINST WHAT IT USES",
      "the authority's net generation as a percent of its demand", lambda w: f"the net generation of {w} as a percent of its demand",
      LB + " Hours both are held.", reproduce("ba_gen_ratio"), consequence=3),
    C("ba_co2_intensity", FAMILY, ba_co2_intensity, "kg CO2 per MWh", 0, 8000, 25.0, "CO2 PER MWH GENERATED", "the CO2 its generators emitted per MWh they generated",
      lambda w: f"the CO2 emitted per MWh generated by the generators of {w}", LE, reproduce("ba_co2_intensity"), consequence=3),
    C("ba_coal_co2_share", FAMILY, ba_coal_co2_share, "percent", 1, 8000, 5.0, "COAL'S SHARE OF AN AUTHORITY'S CO2", "coal's share of the CO2 its generators emitted",
      lambda w: f"coal's share of the CO2 emitted by the generators of {w}", LE, reproduce("ba_coal_co2_share"), consequence=2),
]
# session 8205: one story once. ERCOT's mean demand is chain 164's draft (mean-day-ercot-ba); an authority that is a whole
# region (SOCO the Southeast, TVA Tennessee, FPL is not) repeats its region's draft of family 2 or 3 and is left to it.
# WAPA's Rocky Mountain region (WACM) stepped up about 700 MW of mean demand from 2022 to 2023 while Public Service of
# Colorado (PSCO) fell about 440 MW: a change of footprint cannot be ruled out from these rows, so its demand and its
# generation against demand are not drafted (runs/c502/ba_check.py).
SKIP = {("ba_mean_mw", "ba_erco"), ("ba_mean_mw", "ba_tva"), ("ba_peak_mw", "ba_tva"), ("ba_gen_ratio", "ba_tva"), ("ba_gen_ratio", "ba_soco"),
        ("ba_mean_mw", "ba_wacm"), ("ba_peak_mw", "ba_wacm"), ("ba_gen_ratio", "ba_wacm"), ("ba_mean_mw", "ba_psco"), ("ba_peak_mw", "ba_psco"), ("ba_gen_ratio", "ba_psco")}
for _P in CANDIDATES:
    if _P["unit"] == "MW":
        _P["rank"] = lambda c: abs(c["change"] / c["first"]) if c["first"] else 0.0
    else:
        _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = 5

    def _wrap(fn, name):
        def f(in_dir=None):
            got = fn(in_dir)
            got["rows"] = [r for r in got["rows"] if (name, r["region"]) not in SKIP]
            return got
        return f
    _P["_fn"] = _wrap(_P["_fn"], _P["name"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, family authorities")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--max-drafts", type=int, default=25)
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
