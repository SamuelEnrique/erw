#!/usr/bin/env python3
"""The findings hunt of chain 502, part D: oil and gas by country, from EIA's international data, session 8226.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table eia_world_oil_gas_annual (public,
EIA's international data; no draft had read it):

    wog_crude        crude oil with lease condensate produced (EIA's code 57), thousand barrels a day   family oil_products_world
    wog_oil_use      petroleum and other liquids consumed (code 5), thousand barrels a day              family oil_products_world
    wog_gas          dry natural gas produced (code 26), billion cubic feet a year                      family gas
    wog_gas_exports  dry natural gas exported (code 26), billion cubic feet a year                      family gas

From 1980 (before it, EIA's international series hold the United States alone); the world (WORL), then the United States,
then the largest moves among the countries that produced or consumed at least 1,000 thousand barrels a day of oil, or
produced at least 1,000 billion cubic feet of gas, in 2023.

    python warehouse/analysis/findings/deep/worldoil.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/worldoil.py --load
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

FIRST = 1980
SPEC = {"wog_crude": ("57", "production", "crude oil production", "thousand barrels a day", "oil_products_world"),
        "wog_oil_use": ("5", "consumption", "petroleum and other liquids consumption", "thousand barrels a day", "oil_products_world"),
        "wog_gas": ("26", "production", "dry natural gas production", "billion cubic feet", "gas"),
        "wog_gas_exports": ("26", "exports", "dry natural gas exports", "billion cubic feet", "gas")}
CTX = {}


def data(in_dir):
    def build():
        codes = {":" + v[0] for v in SPEC.values()}
        d = h.read("eia_world_oil_gas_annual", in_dir, ["entity", "variable", "ts_utc", "value", "node", "x_area"], ["value"],
                   keep=lambda c: c["entity"].str.contains("|".join(x + "$" for x in codes)))
        d = d.dropna(subset=["value"])
        d["iso"], d["code"] = d["entity"].str.split(":").str[1], d["entity"].str.split(":").str[2]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        d = d[d["year"] >= FIRST]
        d["name"] = d["node"].str.split(",").str[0].str.strip()
        return d
    return hm._cached(("c502_wog", in_dir), build)


def _big(d):
    oil = d[(d["code"].isin(["57", "5"])) & (d["year"] == 2023) & (d["value"] >= 1000)]
    gas = d[(d["code"] == "26") & (d["variable"] == "production") & (d["year"] == 2023) & (d["value"] >= 1000)]
    x = d.loc[oil.index.union(gas.index)]
    return set(x[x["x_area"] == "country"]["iso"]) | {"WORL"}


def _measure(name):
    code, var = SPEC[name][0], SPEC[name][1]

    def f(in_dir=None):
        d = data(in_dir)
        keep = _big(d)
        x = d[(d["code"] == code) & (d["variable"] == var) & d["iso"].isin(keep)]
        rows, tabs = [], {}
        for iso, g in x.groupby("iso"):
            k = f"wog_{iso.lower()}"
            nm = g["name"].iloc[-1]
            w = "the world" if iso == "WORL" else ("the " + nm if nm.startswith("United") else nm)
            for _, r in g.iterrows():
                rows.append(hm._row(k, w, int(r["year"]), float(r["value"]), 1))
            tabs[k] = ["eia_world_oil_gas_annual"]
        return {"rows": rows, "tables": tabs}
    return f


FN = {n: _measure(n) for n in SPEC}


def reproduce_py(name, region):
    code, var = SPEC[name][0], SPEC[name][1]
    iso = region.split("_", 1)[1].upper()
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == 'eia_intl:{iso}:{code}') & (d['variable'] == '{var}')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nfor _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():\n"
            f"    if int(r['ts_utc'][:4]) >= {FIRST}:\n        print(int(r['ts_utc'][:4]), round(float(r['value']), 6), 1)\n")
    return h.py_doc(name, region, ["eia_world_oil_gas_annual"], f"{SPEC[name][2].capitalize()} (EIA's code {code}, {SPEC[name][3]}) of {iso}, by year from {FIRST}.") + h.PY_READ + body


def reproduce_do(name, region):
    code, var = SPEC[name][0], SPEC[name][1]
    iso = region.split("_", 1)[1].upper()
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table eia_world_oil_gas_annual.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "eia_world_oil_gas_annual.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia_intl:{iso}:{code}" & variable == "{var}"',
             "keep ts_utc value", "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", f"keep if year >= {FIRST}",
             "rename value measure", "generate byte n = 1", "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = "EIA's international energy data as the latest bulk file holds them; a country's recent years are often EIA's estimates; from 1980, when the series begin for every country."
CANDIDATES = [C(n, SPEC[n][4], FN[n], SPEC[n][3], 0, 1, 100.0 if SPEC[n][3].startswith("thousand") else 200.0, f"BY COUNTRY: {SPEC[n][2].upper()}", f"the country's {SPEC[n][2]}",
                (lambda wd: (lambda w: f"the {wd} of {w}"))(SPEC[n][2]), L, reproduce(n), consequence=3) for n in SPEC]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["rank_region"] = lambda r: {"wog_worl": 1e9, "wog_usa": 5e8}.get(r, 0.0)
    _P["max_per"] = 4


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, oil and gas by country")
    ap.add_argument("--in-dir", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("worldoil", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=16)
    return 0


if __name__ == "__main__":
    sys.exit(main())
