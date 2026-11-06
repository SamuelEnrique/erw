#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164): findings that need two families (session 3016).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Each measure is one family's
figure over another's, for the same place and year, from public tables already hunted by family:

    battery_per_peak     the battery fleet at the year's end (storage_buildout_monthly, generation) as a percent of
                         the grid's peak days (the mean of its ten highest days of demand as average GW, eia930_daily_demand)
    built_per_asked      the MW of a type that entered service in the year and still operate (eia860m_operating_generators)
                         as a percent of the MW of the type requested in the year (lbnl_interconnection_queue)
    storage_per_solar    the battery fleet's MWh per MW of solar at the year's end (storage_buildout_monthly)

Not drafted, and why (the chain file's other pairs): nuclear outages against the hub prices of their weeks (both
follow the seasons, and a pair without a seasonal control would read as a cause); the spark spread against the gas
balance and datacenter MW against sub-region peaks (the yearly series are too short or the facilities table is a
partial inventory begun in 2025).

    python warehouse/analysis/findings/deep/cross.py --dry-run
    python warehouse/analysis/findings/deep/cross.py --load
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
import hunt_measures as hm  # noqa: E402

FAMILY = "cross_family"
SB, DD, OP, LQ = "storage_buildout_monthly", "eia930_daily_demand", "eia860m_operating_generators", "lbnl_interconnection_queue"
GRIDS = {"ercot": ("iso:ercot", "eia930:ERCO", "ERCOT"), "caiso": ("iso:caiso", "eia930:CISO", "CAISO"), "pjm": ("iso:pjm", "eia930:PJM", "PJM"),
         "us": ("us:total", "eia930:US48", "the United States")}
TYPES = {"solar": ("Solar Photovoltaic", "Solar"), "battery": ("Batteries", "Battery")}
FIRST, LAST = 2010, 2024


def _december(in_dir, var, ents):
    d = hm.series(SB, in_dir, variables=[var], entities=ents)
    d = d[d["ts_utc"].str[5:7] == "12"]
    return {(e, int(t[:4])): v for e, t, v in zip(d["entity"], d["ts_utc"], d["value"])}


def battery_per_peak(in_dir=None):
    """The battery fleet at the year's end as a percent of the grid's peak days: the mean of its ten highest days of
    demand, as average GW (GWh over 24). Days of reporting faults are dropped (a third, or three times, the year's median)."""
    fleet = _december(in_dir, "battery_operating_mw", [g[0] for g in GRIDS.values()])
    d = hm.series(DD, in_dir, variables=["demand_mwh"], entities=[g[1] for g in GRIDS.values()])
    d = d[d["value"] > 0].drop_duplicates(["entity", "ts_utc"]).assign(year=lambda x: x["ts_utc"].str[:4].astype(int))
    med = d.groupby(["entity", "year"])["value"].transform("median")
    d = d[(d["value"] >= med / 3) & (d["value"] <= med * 3)]
    rows, tables = [], {}
    for key, (sb, ba, words) in GRIDS.items():
        g = d[d["entity"] == ba]
        for y, s in g.groupby("year"):
            if (sb, y) in fleet:
                peak_mw = s["value"].nlargest(10).mean() / 24.0
                rows.append(hm._row(f"{key}_bat_peak", words, y, float(100 * fleet[(sb, y)] / peak_mw), len(s)))
        tables[f"{key}_bat_peak"] = [SB, DD]
    return {"rows": rows, "tables": tables}


def built_per_asked(in_dir=None):
    """The US MW of a type that entered service in the year (and still operate) as a percent of the MW of the type
    requested in the year (Berkeley Lab's queue year)."""
    op = common.read_table(OP, in_dir, usecols=["technology", "nameplate_mw", "operating_year"])
    op = op.assign(mw=pd.to_numeric(op["nameplate_mw"], errors="coerce"), year=pd.to_numeric(op["operating_year"], errors="coerce")).dropna(subset=["mw", "year"])
    lq = common.read_table(LQ, in_dir, usecols=["type_clean", "mw_1", "q_year"])
    lq = lq.assign(mw=pd.to_numeric(lq["mw_1"], errors="coerce"), year=pd.to_numeric(lq["q_year"], errors="coerce")).dropna(subset=["mw", "year"])
    rows, tables = [], {}
    for key, (tech, typ) in TYPES.items():
        built = op[op["technology"] == tech].groupby("year")["mw"].sum()
        asked = lq[lq["type_clean"] == typ].groupby("year")["mw"].sum()
        for y in range(FIRST, LAST + 1):
            if asked.get(y, 0) > 0:
                rows.append(hm._row(f"us_{key}_built_asked", f"US {key}", y, float(100 * built.get(y, 0.0) / asked[y]), 1))
        tables[f"us_{key}_built_asked"] = [OP, LQ]
    return {"rows": rows, "tables": tables}


def storage_per_solar(in_dir=None):
    """The battery fleet's MWh per MW of solar in operation at the year's end."""
    v = _december(in_dir, "battery_mwh_per_solar_mw", [g[0] for g in GRIDS.values()])
    rows, tables = [], {}
    for key, (sb, ba, words) in GRIDS.items():
        for (e, y), val in sorted(v.items()):
            if e == sb:
                rows.append(hm._row(f"{key}_bat_solar", words, y, float(val), 1))
        tables[f"{key}_bat_solar"] = [SB]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_READ = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables.

    python {{this file}} {args}

{label}.
"""
import sys

import pandas as pd


def read(path, cols):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    return pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str)


'''


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    if name == "battery_per_peak":
        sb, ba, words = GRIDS[region.split("_")[0]]
        return (PY_READ.format(name=name, region=region, args=f"<{SB}.csv> <{DD}.csv>", label=label + f", {words}")
                + "f = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\n"
                + f"f = f[(f['entity'] == {sb!r}) & (f['variable'] == 'battery_operating_mw') & (f['ts_utc'].str[5:7] == '12')]\n"
                + "fleet = {int(t[:4]): float(v) for t, v in zip(f['ts_utc'], f['value'])}\n"
                + "d = read(sys.argv[2], ['entity', 'variable', 'ts_utc', 'value'])\n"
                + f"d = d[(d['entity'] == {ba!r}) & (d['variable'] == 'demand_mwh')].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                + "d = d[d['value'] > 0].drop_duplicates(['entity', 'ts_utc'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\n"
                + "med = d.groupby('year')['value'].transform('median')\nd = d[(d['value'] >= med / 3) & (d['value'] <= med * 3)]\n"
                + "for y, s in d.groupby('year'):\n    if y in fleet:\n        print(y, round(100 * fleet[y] / (s['value'].nlargest(10).mean() / 24.0), 6), len(s))\n")
    if name == "built_per_asked":
        key = region.split("_")[1]
        tech, typ = TYPES[key]
        return (PY_READ.format(name=name, region=region, args=f"<{OP}.csv> <{LQ}.csv>", label=label + f", {key}")
                + f"op = read(sys.argv[1], ['technology', 'nameplate_mw', 'operating_year'])\nop = op[op['technology'] == {tech!r}]\n"
                + "op = op.assign(mw=pd.to_numeric(op['nameplate_mw'], errors='coerce'), year=pd.to_numeric(op['operating_year'], errors='coerce')).dropna(subset=['mw', 'year'])\n"
                + f"lq = read(sys.argv[2], ['type_clean', 'mw_1', 'q_year'])\nlq = lq[lq['type_clean'] == {typ!r}]\n"
                + "lq = lq.assign(mw=pd.to_numeric(lq['mw_1'], errors='coerce'), year=pd.to_numeric(lq['q_year'], errors='coerce')).dropna(subset=['mw', 'year'])\n"
                + "built, asked = op.groupby('year')['mw'].sum(), lq.groupby('year')['mw'].sum()\n"
                + f"for y in range({FIRST}, {LAST + 1}):\n    if asked.get(y, 0) > 0:\n        print(y, round(float(100 * built.get(y, 0.0) / asked[y]), 6), 1)\n")
    sb, ba, words = GRIDS[region.split("_")[0]]
    return (PY_READ.format(name=name, region=region, args=f"<{SB}.csv>", label=label + f", {words}")
            + "f = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\n"
            + f"f = f[(f['entity'] == {sb!r}) & (f['variable'] == 'battery_mwh_per_solar_mw') & (f['ts_utc'].str[5:7] == '12')]\n"
            + "for t, v in sorted(zip(f['ts_utc'], f['value'])):\n    print(int(t[:4]), round(float(v), 6), 1)\n")


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.",
            "clear all"]
    if name == "battery_per_peak":
        sb, ba, words = GRIDS[region.split("_")[0]]
        lines = head + [f'import delimited "{SB}.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{sb}" & variable == "battery_operating_mw" & substr(ts_utc, 6, 2) == "12"',
                        "destring value, replace force", "generate int year = real(substr(ts_utc, 1, 4))", "keep year value", "rename value fleet", "save fleet_years, replace",
                        f'import delimited "{DD}.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{ba}" & variable == "demand_mwh"',
                        "destring value, replace force", "keep if value > 0 & !missing(value)", "duplicates drop entity ts_utc, force", "generate int year = real(substr(ts_utc, 1, 4))",
                        "bysort year: egen double med = median(value)", "keep if value >= med / 3 & value <= med * 3", "gsort year -value", "by year: generate long rank = _n",
                        "by year: generate long n = _N", "by year: egen double top = mean(cond(rank <= 10, value, .))", "by year: keep if _n == 1",
                        "merge 1:1 year using fleet_years, keep(match) nogenerate", "generate double measure = 100 * fleet / (top / 24)"]
    elif name == "built_per_asked":
        key = region.split("_")[1]
        tech, typ = TYPES[key]
        lines = head + [f'import delimited "{OP}.csv", varnames(1) stringcols(_all) clear', f'keep if technology == "{tech}"', "destring nameplate_mw operating_year, replace force",
                        "drop if missing(nameplate_mw) | missing(operating_year)", "collapse (sum) built = nameplate_mw, by(operating_year)", "rename operating_year year",
                        "save built_years, replace", f'import delimited "{LQ}.csv", varnames(1) stringcols(_all) clear', f'keep if type_clean == "{typ}"',
                        "destring mw_1 q_year, replace force", "drop if missing(mw_1) | missing(q_year)", "collapse (sum) asked = mw_1, by(q_year)", "rename q_year year",
                        "merge 1:1 year using built_years, keep(master match) nogenerate", "replace built = 0 if missing(built)",
                        f"keep if inrange(year, {FIRST}, {LAST}) & asked > 0", "generate double measure = 100 * built / asked", "generate byte n = 1"]
    else:
        sb, ba, words = GRIDS[region.split("_")[0]]
        lines = head + [f'import delimited "{SB}.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "{sb}" & variable == "battery_mwh_per_solar_mw" & substr(ts_utc, 6, 2) == "12"', "destring value, replace force",
                        "generate int year = real(substr(ts_utc, 1, 4))", "rename value measure", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
CANDIDATES = [
    C("battery_per_peak", FAMILY, battery_per_peak, "percent of peak-day demand", 1, 330, 1.0, "BATTERIES AGAINST THE PEAK",
      "the battery fleet at the year's end as a percent of the grid's peak days (the mean of its ten highest days of demand, as average GW)",
      lambda w: f"the battery fleet of {w} at the year's end, against the average GW of its ten highest days of demand,",
      "Two families in one figure: EIA-860M's operating batteries (the ERW's monthly fleet) over EIA-930's daily demand; a battery's MW is its discharge rate, not its energy, and a peak day's average GW is below its peak hour.",
      reproduce("battery_per_peak"), first_words="the first year both tables hold", consequence=3),
    C("built_per_asked", FAMILY, built_per_asked, "percent of MW requested", 1, 1, 5.0, "BUILT AGAINST ASKED FOR",
      "the US MW of a type that entered service in the year (and still operate) as a percent of the MW of the type requested in the year",
      lambda w: f"the MW of {w} entering service in the year against the MW of {w} requested in the year",
      "Two families in one figure: a year's requests and a year's completions are different projects (a completion's request is years older), so the figure compares two flows, not a success rate.",
      reproduce("built_per_asked"), first_words="the first year this measure counts", consequence=2),
    C("storage_per_solar", FAMILY, storage_per_solar, "MWh per MW of solar", 2, 1, 0.1, "STORAGE BESIDE SOLAR",
      "the battery fleet's MWh per MW of solar in operation at the year's end",
      lambda w: f"the battery energy capacity in {w} per MW of solar in operation at the year's end",
      "EIA-860M's operating batteries and solar as the ERW counts them each month; batteries that report no MWh are left out.",
      reproduce("storage_per_solar"), first_words="the first year the ERW's fleet table holds", consequence=3),
]
for _P in CANDIDATES:
    _P["rank_region"] = lambda r: 1e9 if r.startswith("us_") else 0.0
    if _P["name"] in ("battery_per_peak", "storage_per_solar"):
        _P["max_per"] = 3                         # the US, ERCOT and CAISO: three grids, three stories


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, findings across families (chain 164)")
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
