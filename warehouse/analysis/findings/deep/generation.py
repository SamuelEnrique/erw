#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "generation_pipeline", first part: the mix (session 3005).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Two public sources:

    eia_state_generation_monthly     EIA's net generation by state and energy source, every sector, from 2001 (MWh). A
                                     share is the source's MWh over the state's ALL (which leaves out estimated
                                     small-scale solar, DPV); DPV is set against ALL as a ratio of its own
    generation_mix_hourly_profile    the ERW's mean MW by grid, local hour and source, a month at a time, from EIA-930
                                     (2019 on; docs/methods/generation_mix_hourly.md). A year's share in some hours is
                                     the mean over its months of the source's MW in those hours over all sources' MW

The weekly hunt already asks wind's night share, curtailment, the evening ramp and battery discharge in the evening;
here the questions are the shares that crossed a line: solar's, wind's, coal's and gas's share of each state's
generation, small-scale solar against it, solar's midday share and gas's evening share by grid. Regions of MISO, SPP,
NYISO and ISO-NE are never drafted.

    python warehouse/analysis/findings/deep/generation.py --dry-run
    python warehouse/analysis/findings/deep/generation.py --load
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
import hunt_measures as hm  # noqa: E402

FAMILY = "generation_pipeline"
STATES = dict(fuels_carbon.STATES, US="the United States")
SOURCES = {"SUN": "utility-scale solar", "WND": "wind", "COW": "coal", "NG": "natural gas", "DPV": "small-scale solar", "NUC": "nuclear", "HYC": "conventional hydro"}
GRIDS = {"iso:ercot": ("ercot_mix", "ERCOT"), "iso:caiso": ("caiso_mix", "CAISO"), "iso:pjm": ("pjm_mix", "PJM")}
MIX = ("natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other")
MIDDAY, EVENING = (11, 15), (17, 21)


def state_gen(in_dir):
    def build():
        d = hm.series("eia_state_generation_monthly", in_dir, variables=["net_generation"], extra=("geo",))
        d["state"], d["src"] = d["entity"].str.split(":").str[2], d["entity"].str.split(":").str[3]
        d = d[d["state"].isin(STATES) & d["src"].isin(list(SOURCES) + ["ALL"])]
        w = d.pivot_table(index=["state", "ts"], columns="src", values="value").reset_index()
        w["year"] = w["ts"].dt.year
        return w
    return hm._cached(("deep_state_gen", in_dir), build)


def _share(in_dir, src):
    rows, tables = [], {}
    w = state_gen(in_dir)
    w = w.dropna(subset=["ALL"])
    w = w[w["ALL"] > 0]
    for st, g in w.groupby("state"):
        region, words = f"state_{src.lower()}_{st}", STATES[st]
        g = g.assign(v=g[src].fillna(0.0)) if src in g else g.assign(v=0.0)
        for y, s in g.groupby("year"):
            rows.append(hm._row(region, words, y, float(100 * s["v"].sum() / s["ALL"].sum()), len(s)))
        tables[region] = ["eia_state_generation_monthly"]
    return {"rows": rows, "tables": tables}


def solar_share(in_dir=None):
    """Utility-scale solar's share of the state's net generation over the year (percent)."""
    return _share(in_dir, "SUN")


def wind_share(in_dir=None):
    """Wind's share of the state's net generation over the year (percent)."""
    return _share(in_dir, "WND")


def coal_share(in_dir=None):
    """Coal's share of the state's net generation over the year (percent)."""
    return _share(in_dir, "COW")


def gas_share(in_dir=None):
    """Natural gas's share of the state's net generation over the year (percent)."""
    return _share(in_dir, "NG")


def small_solar_ratio(in_dir=None):
    """EIA's estimate of small-scale solar generation as a percent of the state's net generation (which leaves it out)."""
    rows, tables = [], {}
    w = state_gen(in_dir).dropna(subset=["ALL", "DPV"])
    w = w[(w["ALL"] > 0) & (w["state"] != "DC")]      # DC generates almost nothing itself: its ratio passes 100 percent
    for st, g in w.groupby("state"):
        region, words = f"state_dpv_{st}", STATES[st]
        for y, s in g.groupby("year"):
            rows.append(hm._row(region, words, y, float(100 * s["DPV"].sum() / s["ALL"].sum()), len(s)))
        tables[region] = ["eia_state_generation_monthly"]
    return {"rows": rows, "tables": tables}


def mix(in_dir):
    def build():
        names = [f"avg_{s}_mw_h{h:02d}" for s in MIX for h in range(24)]
        d = hm.series("generation_mix_hourly_profile", in_dir, variables=names, entities=list(GRIDS))
        d["src"] = d["variable"].str[4:].str.rsplit("_mw_h", n=1).str[0]
        d["hour"] = d["variable"].str[-2:].astype(int)
        d["year"] = d["ts"].dt.year
        return d
    return hm._cached(("deep_mix", in_dir), build)


def _hour_share(in_dir, src, hours):
    rows, tables = [], {}
    d = mix(in_dir)
    d = d[d["hour"].between(*hours)]
    for ent, g in d.groupby("entity"):
        region, words = GRIDS[ent]
        g = g.assign(value=g["value"].clip(lower=0))         # each hour's MW at or above zero: storage counts when it discharges
        m = g.groupby(["ts", "src"])["value"].sum().unstack("src")
        m = m.dropna(subset=[src])
        gen = m.sum(axis=1)
        share = 100 * m[src] / gen
        for y, s in share.groupby(share.index.year):
            rows.append(hm._row(region, words, y, float(s.mean()), len(s)))
        tables[region] = ["generation_mix_hourly_profile"]
    return {"rows": rows, "tables": tables}


def solar_midday_share(in_dir=None):
    """Solar's share of the grid's generation from 11 AM to 4 PM local: the mean over the year's months."""
    return _hour_share(in_dir, "solar", MIDDAY)


def gas_evening_share(in_dir=None):
    """Natural gas's share of the grid's generation from 5 PM to 10 PM local: the mean over the year's months."""
    return _hour_share(in_dir, "natural_gas", EVENING)


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_STATE = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <eia_state_generation_monthly.csv>

{label}, by calendar year, for {words}. Series eia:generation:{st}:{src} over eia:generation:{st}:ALL (net generation,
MWh, every sector); a month without the source's row counts as zero for it{dpv_note}.
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
d = d[d["entity"].isin(["eia:generation:{st}:ALL", "eia:generation:{st}:{src}"]) & (d["variable"] == "net_generation")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["src"] = d["entity"].str.split(":").str[3]
w = d.pivot_table(index="ts_utc", columns="src", values="value")
w = w.dropna(subset=["ALL"{dpv_drop}])
w = w[w["ALL"] > 0]
w["v"] = w["{src}"].fillna(0.0) if "{src}" in w else 0.0
w["year"] = w.index.str[:4].astype(int)
for y, s in w.groupby("year"):
    print(y, round(float(100 * s["v"].sum() / s["ALL"].sum()), 6), len(s))
'''

PY_MIX = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <generation_mix_hourly_profile.csv>

{label}, by calendar year, for {words} (entity {ent}). A month's share: the source's mean MW in local hours {h0} to {h1}
over the sum of every source's mean MW in those hours (storage counted when it discharges, not when it charges).
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
d = d[(d["entity"] == "{ent}") & d["variable"].str.match(r"^avg_[a-z_]+_mw_h[0-9][0-9]$")].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["src"] = d["variable"].str[4:].str.rsplit("_mw_h", n=1).str[0]
d["hour"] = d["variable"].str[-2:].astype(int)
d = d[d["src"].isin({mix!r}) & d["hour"].between({h0}, {h1})]
d["value"] = d["value"].clip(lower=0)
m = d.groupby(["ts_utc", "src"])["value"].sum().unstack("src").dropna(subset=["{src}"])
gen = m.sum(axis=1)
share = 100 * m["{src}"] / gen
for y, s in share.groupby(share.index.str[:4].astype(int)):
    print(y, round(float(s.mean()), 6), len(s))
'''


def _state_src(name, region):
    return region.rsplit("_", 1)[1], {"solar_share": "SUN", "wind_share": "WND", "coal_share": "COW", "gas_share": "NG", "small_solar_ratio": "DPV",
                                      "nuclear_share": "NUC", "hydro_share": "HYC"}[name]   # the last two: nuclear_fleet.py, session 3006


def reproduce_py(name, region):
    P = next((p for p in CANDIDATES if p["name"] == name), None)
    label = (P["label"][0].upper() + P["label"][1:]) if P else f"{SOURCES[_state_src(name, region)[1]][0].upper()}{SOURCES[_state_src(name, region)[1]][1:]}'s share of the state's net generation over the year"
    if name in ("solar_midday_share", "gas_evening_share"):
        ent = next(k for k, v in GRIDS.items() if v[0] == region)
        src, (h0, h1) = ("solar", MIDDAY) if name == "solar_midday_share" else ("natural_gas", EVENING)
        return PY_MIX.format(name=name, region=region, label=label, words=GRIDS[ent][1], ent=ent, h0=h0, h1=h1, src=src, mix=list(MIX))
    st, src = _state_src(name, region)
    dpv = name == "small_solar_ratio"
    return PY_STATE.format(name=name, region=region, label=label, words=STATES[st], st=st, src=src,
                           dpv_note="; for small-scale solar, a month without its row is left out" if dpv else "",
                           dpv_drop=', "DPV"' if dpv else "")


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
            "clear all"]
    if name in ("solar_midday_share", "gas_evening_share"):
        ent = next(k for k, v in GRIDS.items() if v[0] == region)
        src, (h0, h1) = ("solar", MIDDAY) if name == "solar_midday_share" else ("natural_gas", EVENING)
        lines = head + ['import delimited "generation_mix_hourly_profile.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "{ent}" & regexm(variable, "^avg_[a-z_]+_mw_h[0-9][0-9]$")', "destring value, replace force", "drop if missing(value)",
                        "generate int hour = real(substr(variable, -2, 2))", 'generate str20 src = regexs(1) if regexm(variable, "^avg_([a-z_]+)_mw_h[0-9][0-9]$")',
                        f"keep if inrange(hour, {h0}, {h1})", "keep if " + " | ".join(f'src == "{s}"' for s in MIX),
                        'replace value = max(value, 0)', "collapse (sum) value, by(ts_utc src)",
                        "bysort ts_utc: egen double gen = total(value)", f'keep if src == "{src}"', "generate double share = 100 * value / gen",
                        "generate int year = real(substr(ts_utc, 1, 4))", "collapse (mean) measure = share (count) n = share, by(year)"]
    else:
        st, src = _state_src(name, region)
        dpv = name == "small_solar_ratio"
        lines = head + ['import delimited "eia_state_generation_monthly.csv", varnames(1) stringcols(_all) clear',
                        f'keep if (entity == "eia:generation:{st}:ALL" | entity == "eia:generation:{st}:{src}") & variable == "net_generation"',
                        "destring value, replace force", "drop if missing(value)", 'generate str4 src = cond(entity == "eia:generation:' + st + ':ALL", "ALL", "SRC")',
                        "keep ts_utc src value", "reshape wide value, i(ts_utc) j(src) string", "drop if missing(valueALL) | valueALL <= 0"]
        lines += (["drop if missing(valueSRC)"] if dpv else ["capture confirm variable valueSRC", "if _rc generate double valueSRC = 0", "replace valueSRC = 0 if missing(valueSRC)"])
        lines += ["generate int year = real(substr(ts_utc, 1, 4))", "collapse (sum) src = valueSRC (sum) all = valueALL (count) n = valueALL, by(year)",
                  "generate double measure = 100 * src / all"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_STATE = ("EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, "
               "not what is used in it, and EIA withholds some plants' months.")
CANDIDATES = [
    C("solar_share", FAMILY, solar_share, "percent of net generation", 1, 11, 2.0, "SOLAR'S SHARE",
      "utility-scale solar's share of the state's net generation over the year", lambda w: f"utility-scale solar's share of net generation in {w}",
      LIMIT_STATE, reproduce("solar_share"), consequence=3),
    C("wind_share", FAMILY, wind_share, "percent of net generation", 1, 11, 2.0, "WIND'S SHARE",
      "wind's share of the state's net generation over the year", lambda w: f"wind's share of net generation in {w}",
      LIMIT_STATE, reproduce("wind_share"), consequence=3),
    C("coal_share", FAMILY, coal_share, "percent of net generation", 1, 11, 2.0, "COAL'S SHARE",
      "coal's share of the state's net generation over the year", lambda w: f"coal's share of net generation in {w}",
      LIMIT_STATE, reproduce("coal_share"), consequence=3),
    C("gas_share", FAMILY, gas_share, "percent of net generation", 1, 11, 2.0, "GAS'S SHARE",
      "natural gas's share of the state's net generation over the year", lambda w: f"natural gas's share of net generation in {w}",
      LIMIT_STATE, reproduce("gas_share"), consequence=3),
    C("small_solar_ratio", FAMILY, small_solar_ratio, "percent of net generation", 1, 11, 1.0, "SMALL-SCALE SOLAR",
      "EIA's estimate of small-scale solar generation as a percent of the state's net generation, which leaves it out",
      lambda w: f"EIA's estimate of small-scale solar generation in {w}, as a percent of the state's net generation,",
      "An estimate EIA models from capacity, not a metered figure, and set against a total that does not include it.",
      reproduce("small_solar_ratio"), consequence=2),
    C("solar_midday_share", FAMILY, solar_midday_share, "percent of generation", 1, 11, 2.0, "SOLAR AT MIDDAY",
      "solar's share of the grid's generation from 11 AM to 4 PM local, the mean over the year's months",
      lambda w: f"solar's share of {w}'s generation from 11 AM to 4 PM",
      "EIA-930 hourly generation as the ERW's monthly profile holds it; a month is the mean of its complete days, and behind-the-meter solar is not in it.",
      reproduce("solar_midday_share"), consequence=3),
    C("gas_evening_share", FAMILY, gas_evening_share, "percent of generation", 1, 11, 2.0, "GAS IN THE EVENING",
      "natural gas's share of the grid's generation from 5 PM to 10 PM local, the mean over the year's months",
      lambda w: f"natural gas's share of {w}'s generation from 5 PM to 10 PM",
      "EIA-930 hourly generation as the ERW's monthly profile holds it; imports are not in the denominator, so a grid that imports more in the evening shows a share of what it generates, not of what it uses.",
      reproduce("gas_evening_share"), consequence=3),
]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])        # the largest move in share points first


def _us_first(region):
    return 1e9 if region.endswith("_US") else 0.0


RANK_REGION = _us_first                          # session 3005: the United States before any state, then the largest move
for _P in CANDIDATES:
    if _P["name"] not in ("solar_midday_share", "gas_evening_share"):
        _P["rank_region"] = _us_first


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family generation, the mix (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place (session 3019)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_mix", cands, a.in_dir, dry_run=not a.load, max_drafts=13, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
