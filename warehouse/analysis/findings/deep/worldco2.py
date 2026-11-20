#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family emissions_climate: CO2 from energy by country, session 8215.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table eia_world_energy_co2_annual
(public, EIA's international data; no draft had read it): each country's CO2 from energy, million t CO2 a year.

    co2_total   all energy (EIA's code 4008)      co2_coal   coal and coke (4002)      co2_gas   natural gas (4010)

The world (WORL), then the United States, then the largest moves among countries that emitted at least 200 million t
CO2 from energy in 2023.

    python warehouse/analysis/findings/deep/worldco2.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/worldco2.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import hourly930 as h  # noqa: E402  (sets builder.CHAIN to 502)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "emissions_climate"
MIN_MT = 200.0
FIRST = 1980                   # EIA's international series begin here for every country but the US
CODES = {"co2_total": ("4008", "CO2 from all energy"), "co2_coal": ("4002", "CO2 from coal and coke"), "co2_gas": ("4010", "CO2 from natural gas")}
CTX = {}


def co2(in_dir):
    def build():
        codes = {":" + v[0] for v in CODES.values()}
        d = h.read("eia_world_energy_co2_annual", in_dir, ["entity", "variable", "ts_utc", "value", "node", "x_area"], ["value"],
                   keep=lambda c: (c["variable"] == "emissions") & c["entity"].str.contains("|".join(x + "$" for x in codes)))
        d = d.dropna(subset=["value"])
        d["iso"], d["code"] = d["entity"].str.split(":").str[1], d["entity"].str.split(":").str[2]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        d = d[d["year"] >= FIRST]                # session 8215: before 1980 the series hold the US alone, and WORL equals it
        d["name"] = d["node"].str.split(",").str[0].str.strip()
        return d
    return hm._cached(("c502_wco2", in_dir), build)


def _measure(name):
    code = CODES[name][0]

    def f(in_dir=None):
        d = co2(in_dir)
        tot = d[(d["code"] == "4008") & (d["year"] == 2023) & (d["x_area"] == "country") & (d["value"] >= MIN_MT * 1e6)]
        keep = set(tot["iso"]) | {"WORL"}
        x = d[(d["code"] == code) & d["iso"].isin(keep)]
        rows, tabs = [], {}
        for iso, g in x.groupby("iso"):
            k = f"co2_{iso.lower()}"
            nm = g["name"].iloc[-1]
            w = "the world" if iso == "WORL" else ("the " + nm if nm.startswith("United") else nm)
            for _, r in g.iterrows():
                rows.append(hm._row(k, w, int(r["year"]), float(r["value"] / 1e6), 1))
            tabs[k] = ["eia_world_energy_co2_annual"]
        return {"rows": rows, "tables": tabs}
    return f


co2_total, co2_coal, co2_gas = (_measure(n) for n in CODES)


def reproduce_py(name, region):
    code, iso = CODES[name][0], region.split("_")[1].upper()
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == 'eia_intl:{iso}:{code}') & (d['variable'] == 'emissions')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nfor _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():\n"
            f"    if int(r['ts_utc'][:4]) >= {FIRST}:\n        print(int(r['ts_utc'][:4]), round(float(r['value'] / 1e6), 6), 1)\n")
    return h.py_doc(name, region, ["eia_world_energy_co2_annual"], f"{CODES[name][1]} (EIA's code {code}; million t CO2) of {iso}, by year.") + h.PY_READ + body


def reproduce_do(name, region):
    code, iso = CODES[name][0], region.split("_")[1].upper()
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table eia_world_energy_co2_annual.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "eia_world_energy_co2_annual.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia_intl:{iso}:{code}" & variable == "emissions"',
             "keep ts_utc value", "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", f"keep if year >= {FIRST}",
             "generate double measure = value / 1000000", "generate byte n = 1", "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = "EIA's international energy data as the latest bulk file holds them: CO2 from the energy a country consumes, not its land use or industrial processes; recent years are often EIA's estimates."
CANDIDATES = [C(n, FAMILY, fn, "million t CO2", 1, 1, 20.0, f"CO2 BY COUNTRY: {CODES[n][1].upper()}", f"the country's {CODES[n][1]}",
                (lambda wd: (lambda w: f"the {wd} of {w}"))(CODES[n][1]), L, reproduce(n), consequence=3)
              for n, fn in (("co2_total", co2_total), ("co2_coal", co2_coal), ("co2_gas", co2_gas))]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["rank_region"] = lambda r: {"co2_worl": 1e9, "co2_usa": 5e8}.get(r, 0.0)
    _P["max_per"] = 4


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, CO2 by country")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=12)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("worldco2", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
