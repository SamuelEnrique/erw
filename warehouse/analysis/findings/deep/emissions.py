#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 166, session 3176): emissions and climate.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Public tables:

    eia_co2_state_annual            EIA's energy-related CO2 by state, sector (EC electric power, TC transport, TT all) and
                                    fuel (CO coal, TO all), 1970 to 2022 (tCO2)
    eia_state_generation_monthly    net generation by state (eia:generation:<st>:ALL), for the power sector's CO2 per MWh
    noaa_climdiv_state_monthly      NCEI's monthly temperature by state and the contiguous US (110), with each calendar
                                    month's 1901 to 2000 mean (x_mean_1901_2000)

The claims are counted from 2001 (2000 for the temperature): the tables reach back to 1970, and a claim from 1970 would
set this century against a different economy. NOAA's degree days (noaa_cpc_degree_days_daily) begin in 2024 and are
not hunted.

    python warehouse/analysis/findings/deep/emissions.py --dry-run
    python warehouse/analysis/findings/deep/emissions.py --load
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

FAMILY = "emissions_climate"
CO2, GEN, CLIM = "eia_co2_state_annual", "eia_state_generation_monthly", "noaa_climdiv_state_monthly"
FROM = 2001
STATES = generation.STATES


def _co2(in_dir):
    def build():
        d = hm.series(CO2, in_dir, variables=["co2"])
        p = d["entity"].str.split(":", expand=True)
        return d.assign(st=p[1], sec=p[2], fuel=p[3], year=d["ts_utc"].str[:4].astype(int))
    return hm._cached(("deep_co2", in_dir), build)


def _us(in_dir, sec, fuel):
    d = _co2(in_dir)
    s = d[(d["st"] == "US") & (d["sec"] == sec) & (d["fuel"] == fuel) & (d["year"] >= FROM)]
    return s.groupby("year")["value"].sum()


def power_co2(in_dir=None):
    """The US electric power sector's energy-related CO2 over the year (million tCO2)."""
    s = _us(in_dir, "EC", "TO")
    return {"rows": [hm._row("us_power_co2", "the United States", y, float(v / 1e6), 1) for y, v in s.items()], "tables": {"us_power_co2": [CO2]}}


def _share(in_dir, sec, fuel, region):
    a, b = _us(in_dir, sec, fuel), _us(in_dir, "TT", "TO")
    rows = [hm._row(region, "the United States", y, float(100 * a[y] / b[y]), 1) for y in a.index if b.get(y, 0) > 0]
    return {"rows": rows, "tables": {region: [CO2]}}


def power_co2_share(in_dir=None):
    """The electric power sector's share of US energy-related CO2 (percent)."""
    return _share(in_dir, "EC", "TO", "us_power_co2_share")


def transport_co2_share(in_dir=None):
    """Transport's share of US energy-related CO2 (percent)."""
    return _share(in_dir, "TC", "TO", "us_transport_co2_share")


def coal_co2_share(in_dir=None):
    """Coal's share of US energy-related CO2, every sector (percent)."""
    return _share(in_dir, "TT", "CO", "us_coal_co2_share")


def power_co2_per_mwh(in_dir=None):
    """By state and the US: the electric power sector's CO2 over the state's net generation (kg CO2 per MWh)."""
    d = _co2(in_dir)
    co2 = d[(d["sec"] == "EC") & (d["fuel"] == "TO") & (d["year"] >= FROM)].groupby(["st", "year"])["value"].sum()
    g = generation.state_gen(in_dir).dropna(subset=["ALL"])
    gen = g.groupby(["state", "year"]).agg(mwh=("ALL", "sum"), months=("ALL", "size"))
    rows, tables = [], {}
    for (st, y), v in co2.items():
        if (st, y) in gen.index and gen.loc[(st, y), "months"] == 12 and gen.loc[(st, y), "mwh"] > 0 and st in STATES and st != "DC":   # DC generates almost nothing
            rows.append(hm._row(f"co2mwh_{st}", STATES[st], y, float(1000 * v / gen.loc[(st, y), "mwh"]), 1))
            tables[f"co2mwh_{st}"] = [CO2, GEN]
    return {"rows": rows, "tables": tables}


def conus_temperature(in_dir=None):
    """The contiguous US's mean monthly temperature over the year less the mean of its months' 1901 to 2000 means (degrees F)."""
    d = hm.series(CLIM, in_dir, variables=["temp_avg"], entities=["noaa_climdiv:110"], extra=("x_mean_1901_2000",))
    d = d.assign(norm=pd.to_numeric(d["x_mean_1901_2000"], errors="coerce"), year=d["ts_utc"].str[:4].astype(int)).dropna(subset=["norm"])
    d = d[d["year"] >= 2000]
    rows = [hm._row("conus_temp", "the contiguous United States", y, float((s["value"] - s["norm"]).mean()), len(s)) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"conus_temp": [CLIM]}}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_READ = '''"""ERW findings hunt (chain 166): reproduce candidate {name} for {region} from the ERW's public tables.

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
    d = pd.read_csv(path, skiprows=skip, usecols=cols, dtype=str)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"])


'''
SHARE = {"power_co2_share": ("EC", "TO"), "transport_co2_share": ("TC", "TO"), "coal_co2_share": ("TT", "CO")}


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    co2_head = ("d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[d['variable'] == 'co2']\n"
                "p = d['entity'].str.split(':', expand=True)\nd['st'], d['sec'], d['fuel'], d['year'] = p[1], p[2], p[3], d['ts_utc'].str[:4].astype(int)\n"
                f"d = d[d['year'] >= {FROM}]\n")
    if name == "power_co2":
        return (PY_READ.format(name=name, region=region, args=f"<{CO2}.csv>", label=label) + co2_head
                + "s = d[(d['st'] == 'US') & (d['sec'] == 'EC') & (d['fuel'] == 'TO')].groupby('year')['value'].sum()\n"
                + "for y, v in s.items():\n    print(y, round(float(v / 1e6), 6), 1)\n")
    if name in SHARE:
        sec, fuel = SHARE[name]
        return (PY_READ.format(name=name, region=region, args=f"<{CO2}.csv>", label=label) + co2_head
                + f"a = d[(d['st'] == 'US') & (d['sec'] == {sec!r}) & (d['fuel'] == {fuel!r})].groupby('year')['value'].sum()\n"
                + "b = d[(d['st'] == 'US') & (d['sec'] == 'TT') & (d['fuel'] == 'TO')].groupby('year')['value'].sum()\n"
                + "for y in a.index:\n    if b.get(y, 0) > 0:\n        print(y, round(float(100 * a[y] / b[y]), 6), 1)\n")
    if name == "power_co2_per_mwh":
        st = region.split("_")[1]
        return (PY_READ.format(name=name, region=region, args=f"<{CO2}.csv> <{GEN}.csv>", label=label + f", {STATES[st]}") + co2_head
                + f"co2 = d[(d['st'] == {st!r}) & (d['sec'] == 'EC') & (d['fuel'] == 'TO')].groupby('year')['value'].sum()\n"
                + f"g = read(sys.argv[2], ['entity', 'variable', 'ts_utc', 'value'])\ng = g[(g['entity'] == 'eia:generation:{st}:ALL') & (g['variable'] == 'net_generation')]\n"
                + "g['year'] = g['ts_utc'].str[:4].astype(int)\ngen = g.groupby('year').agg(mwh=('value', 'sum'), months=('value', 'size'))\n"
                + "for y, v in co2.items():\n    if y in gen.index and gen.loc[y, 'months'] == 12 and gen.loc[y, 'mwh'] > 0:\n"
                + "        print(y, round(float(1000 * v / gen.loc[y, 'mwh']), 6), 1)\n")
    return (PY_READ.format(name=name, region=region, args=f"<{CLIM}.csv>", label=label)
            + "d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value', 'x_mean_1901_2000'])\n"
            + "d = d[(d['entity'] == 'noaa_climdiv:110') & (d['variable'] == 'temp_avg')].copy()\n"
            + "d['norm'] = pd.to_numeric(d['x_mean_1901_2000'], errors='coerce')\nd = d.dropna(subset=['norm'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\n"
            + "d = d[d['year'] >= 2000]\nfor y, s in d.groupby('year'):\n    print(y, round(float((s['value'] - s['norm']).mean()), 6), len(s))\n")


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 166): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.",
            "clear all"]
    co2 = [f'import delimited "{CO2}.csv", varnames(1) stringcols(_all) clear', 'keep if variable == "co2"', "destring value, replace force", "drop if missing(value)",
           'generate str4 st = word(subinstr(entity, ":", " ", .), 2)', 'generate str4 sec = word(subinstr(entity, ":", " ", .), 3)',
           'generate str4 fuel = word(subinstr(entity, ":", " ", .), 4)', "generate int year = real(substr(ts_utc, 1, 4))", f"keep if year >= {FROM}"]
    if name == "power_co2":
        lines = head + co2 + ['keep if st == "US" & sec == "EC" & fuel == "TO"', "collapse (sum) measure = value, by(year)", "replace measure = measure / 1000000"]
    elif name in SHARE:
        sec, fuel = SHARE[name]
        lines = head + co2 + ['keep if st == "US"', f'generate double part = value if sec == "{sec}" & fuel == "{fuel}"',
                              'generate double all = value if sec == "TT" & fuel == "TO"', "collapse (sum) part (sum) all, by(year)", "keep if all > 0",
                              "generate double measure = 100 * part / all"]
    elif name == "power_co2_per_mwh":
        st = region.split("_")[1]
        lines = head + [f'import delimited "{GEN}.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia:generation:{st}:ALL" & variable == "net_generation"',
                        "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
                        "collapse (sum) mwh = value (count) months = value, by(year)", "keep if months == 12 & mwh > 0", "save gen_years, replace"] + co2 + [
                        f'keep if st == "{st}" & sec == "EC" & fuel == "TO"', "collapse (sum) co2 = value, by(year)",
                        "merge 1:1 year using gen_years, keep(match) nogenerate", "generate double measure = 1000 * co2 / mwh"]
    else:
        lines = head + [f'import delimited "{CLIM}.csv", varnames(1) stringcols(_all) clear', 'keep if entity == "noaa_climdiv:110" & variable == "temp_avg"',
                        "destring value x_mean_1901_2000, replace force", "drop if missing(value) | missing(x_mean_1901_2000)",
                        "generate int year = real(substr(ts_utc, 1, 4))", "keep if year >= 2000", "generate double anomaly = value - x_mean_1901_2000",
                        "collapse (mean) measure = anomaly (count) n = anomaly, by(year)"]
    if name != "conus_temperature":
        lines += ["generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_CO2 = "EIA's energy-related CO2 by state, which ends in 2022 in the ERW's table; it counts fuel burned, not the electricity a state imports."
FW = "the first year this measure counts"
CANDIDATES = [
    C("power_co2", FAMILY, power_co2, "million tCO2", 1, 1, 30.0, "THE POWER SECTOR'S CO2",
      "the US electric power sector's energy-related CO2 over the year", lambda w: "the CO2 the US electric power sector emitted", LIMIT_CO2,
      reproduce("power_co2"), first_words=FW, consequence=3),
    C("power_co2_share", FAMILY, power_co2_share, "percent of US energy CO2", 1, 1, 1.0, "POWER'S SHARE OF US CO2",
      "the electric power sector's share of US energy-related CO2", lambda w: "the electric power sector's share of US energy-related CO2", LIMIT_CO2,
      reproduce("power_co2_share"), first_words=FW, consequence=3),
    C("transport_co2_share", FAMILY, transport_co2_share, "percent of US energy CO2", 1, 1, 1.0, "TRANSPORT'S SHARE OF US CO2",
      "transport's share of US energy-related CO2", lambda w: "transport's share of US energy-related CO2", LIMIT_CO2,
      reproduce("transport_co2_share"), first_words=FW, consequence=3),
    C("coal_co2_share", FAMILY, coal_co2_share, "percent of US energy CO2", 1, 1, 1.0, "COAL'S SHARE OF US CO2",
      "coal's share of US energy-related CO2, every sector", lambda w: "coal's share of US energy-related CO2", LIMIT_CO2,
      reproduce("coal_co2_share"), first_words=FW, consequence=3),
    C("power_co2_per_mwh", FAMILY, power_co2_per_mwh, "kg CO2 per MWh", 0, 1, 20.0, "THE POWER SECTOR'S CO2 PER MWH",
      "the electric power sector's CO2 over the state's net generation", lambda w: f"the power sector's CO2 per MWh generated in {w}",
      LIMIT_CO2 + " Two families in one figure: EIA's CO2 by state over its net generation; combined heat and power plants' heat is in the CO2 and not in the MWh.",
      reproduce("power_co2_per_mwh"), first_words=FW, consequence=3),
    C("conus_temperature", FAMILY, conus_temperature, "degrees F above the 1901 to 2000 mean", 2, 11, 0.5, "THE CONTIGUOUS US's TEMPERATURE",
      "the contiguous US's mean monthly temperature over the year less its months' 1901 to 2000 means",
      lambda w: "the contiguous US's average temperature",
      "NCEI's climate divisional data, a mean of the months against each month's own century mean; a year's weather, not a trend's cause.",
      reproduce("conus_temperature"), first_words="the first year this measure counts", consequence=2),
]
for _P in CANDIDATES:
    if _P["name"] == "power_co2_per_mwh":
        _P["rank_region"] = generation._us_first
        _P["rank"] = lambda c: abs(c["change"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, emissions and climate (chain 166)")
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
