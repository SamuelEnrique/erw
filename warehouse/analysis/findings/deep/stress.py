#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 166, session 3177): the grids' stress, from the ERW's own table.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. grid_stress_yearly (the ERW's
derived table, warehouse/derived/mix_stress.py, docs/methods/grid_stress.md; EIA-930 and EIA's inventory) holds each
grid's year from 2019: what each source gave in the year's tightest hours as a share of its capacity, wind and solar's
mean output and capacity, and the calm hours. Session 252's lesson holds: no measure here is one interval of a year
(the year's single lowest net load and largest ramp are left out); the tightest hours are a set of hours.

ERCOT, CAISO and PJM; MISO, SPP, NYISO and ISO-NE are never drafted. Other operating tables are too short for the
hunt's tests: node_basis_daily from October 2025, scarcity_hours_by_grid from November 2023.

    python warehouse/analysis/findings/deep/stress.py --dry-run
    python warehouse/analysis/findings/deep/stress.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "markets_operations"
T = "grid_stress_yearly"
GRIDS = {"iso:ercot": ("ercot", "ERCOT"), "iso:caiso": ("caiso", "CAISO"), "iso:pjm": ("pjm", "PJM"), "iso:miso": ("miso", "MISO"), "iso:spp": ("spp", "SPP"),
         "iso:nyiso": ("nyiso", "NYISO"), "iso:isone": ("isone", "ISO-NE")}
# name: (numerator variable, denominator variable or None, scale)
SPEC = {"tight_solar": ("tight_solar_share_of_capacity_pct", None, 1.0), "tight_wind": ("tight_wind_share_of_capacity_pct", None, 1.0),
        "tight_gas": ("tight_natural_gas_share_of_capacity_pct", None, 1.0), "wind_solar_cf": ("wind_solar_mean_mw", "wind_solar_capacity_mw", 100.0),
        "calm_hours": ("calm_hours", None, 1.0)}


def _fn(name):
    num, den, scale = SPEC[name]

    def fn(in_dir=None):
        d = hm.series(T, in_dir, variables=[num] + ([den] if den else []), entities=list(GRIDS)).drop_duplicates(["entity", "variable", "ts_utc"])
        d = d.assign(year=d["ts_utc"].str[:4].astype(int))
        rows, tables = [], {}
        for ent, g in d.groupby("entity"):
            key, words = GRIDS[ent]
            w = g.pivot_table(index="year", columns="variable", values="value")
            for y, r in w.iterrows():
                if den:
                    if r.get(den, 0) and r.get(num) == r.get(num):
                        rows.append(hm._row(f"{key}_{name}", words, y, float(r[num] * scale / r[den]), 1))
                elif r.get(num) == r.get(num):
                    rows.append(hm._row(f"{key}_{name}", words, y, float(r[num] * scale), 1))
            tables[f"{key}_{name}"] = [T]
        return {"rows": rows, "tables": tables}
    fn.__name__ = name
    return fn


PY = '''"""ERW findings hunt (chain 166): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <grid_stress_yearly.csv>

{label}, {words}.
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
d = d[d["entity"] == {ent!r}].copy()
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"]).drop_duplicates(["entity", "variable", "ts_utc"])
d["year"] = d["ts_utc"].str[:4].astype(int)
w = d.pivot_table(index="year", columns="variable", values="value")
for y, r in w.iterrows():
{body}
'''


def _ent(region):
    key = region.split("_", 1)[0]
    return next(e for e, v in GRIDS.items() if v[0] == key)


def reproduce_py(name, region):
    num, den, scale = SPEC[name]
    P = next(p for p in CANDIDATES if p["name"] == name)
    ent = _ent(region)
    if den:
        body = f"    if r.get({den!r}, 0) and r.get({num!r}) == r.get({num!r}):\n        print(y, round(float(r[{num!r}] * {scale!r} / r[{den!r}]), 6), 1)"
    else:
        body = f"    if r.get({num!r}) == r.get({num!r}):\n        print(y, round(float(r[{num!r}] * {scale!r}), 6), 1)"
    return PY.format(name=name, region=region, label=P["label"][0].upper() + P["label"][1:], words=GRIDS[ent][1], ent=ent, body=body)


def reproduce_do(name, region):
    num, den, scale = SPEC[name]
    ent = _ent(region)
    lines = [f"* ERW findings hunt (chain 166): reproduce candidate {name} for {region} from the ERW's public table.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
             "clear all", f'import delimited "{T}.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{ent}" & (variable == "{num}"' + (f' | variable == "{den}")' if den else ")"),
             "destring value, replace force", "drop if missing(value)", "duplicates drop entity variable ts_utc, force", "generate int year = real(substr(ts_utc, 1, 4))",
             "keep year variable value", "reshape wide value, i(year) j(variable) string"]
    if den:
        lines += [f"drop if missing(value{num}) | missing(value{den}) | value{den} == 0", f"generate double measure = value{num} * {scale!r} / value{den}"]
    else:
        lines += [f"drop if missing(value{num})", f"generate double measure = value{num} * {scale!r}"]
    lines += ["generate byte n = 1", "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT = ("The ERW's derived grid_stress_yearly (EIA-930 hourly by source, EIA's generator inventory); the tightest hours are the year's hours of highest net load, "
         "and a grid whose capacity grew late in a year shows a share of a capacity it held only in part. ")
FW = "the first year the ERW's table holds"
CANDIDATES = [
    C("tight_solar", FAMILY, _fn("tight_solar"), "percent of solar capacity", 1, 1, 3.0, "SOLAR IN THE TIGHTEST HOURS",
      "solar's output in the year's tightest hours as a percent of its capacity", lambda w: f"solar's output in {w}'s tightest hours, as a share of its solar capacity,",
      LIMIT, reproduce("tight_solar"), first_words=FW, consequence=3),
    C("tight_wind", FAMILY, _fn("tight_wind"), "percent of wind capacity", 1, 1, 3.0, "WIND IN THE TIGHTEST HOURS",
      "wind's output in the year's tightest hours as a percent of its capacity", lambda w: f"wind's output in {w}'s tightest hours, as a share of its wind capacity,",
      LIMIT, reproduce("tight_wind"), first_words=FW, consequence=3),
    C("tight_gas", FAMILY, _fn("tight_gas"), "percent of gas capacity", 1, 1, 3.0, "GAS IN THE TIGHTEST HOURS",
      "natural gas's output in the year's tightest hours as a percent of its capacity", lambda w: f"gas-fired output in {w}'s tightest hours, as a share of its gas capacity,",
      LIMIT, reproduce("tight_gas"), first_words=FW, consequence=3),
    C("wind_solar_cf", FAMILY, _fn("wind_solar_cf"), "percent of capacity", 1, 1, 2.0, "WIND AND SOLAR'S CAPACITY FACTOR",
      "wind and solar's mean output over the year as a percent of their capacity", lambda w: f"wind and solar's mean output in {w} as a share of their capacity",
      LIMIT, reproduce("wind_solar_cf"), first_words=FW, consequence=2),
    C("calm_hours", FAMILY, _fn("calm_hours"), "hours", 0, 1, 50.0, "CALM HOURS",
      "the year's calm hours (wind and solar together far below their usual output, as docs/methods/grid_stress.md defines them)",
      lambda w: f"the number of calm hours (wind and solar far below usual) in {w}", LIMIT + "Weather moves the count from year to year.",
      reproduce("calm_hours"), first_words=FW, consequence=2),
]
for _P in CANDIDATES:
    _P["max_per"] = 3


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, the grids' stress (chain 166)")
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
