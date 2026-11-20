#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family coal_uranium_metals: coal by country, session 8214.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table eia_world_coal_annual (public,
EIA's international data, 1980 on; no draft had read it): each country's coal, product code 7 (all coal, short tons).

    wc_consumption / wc_production / wc_exports   million short tons a year, the world (WORL) and the countries that
                                                  consumed or produced at least 50 million short tons in 2023

    python warehouse/analysis/findings/deep/worldcoal.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/worldcoal.py --load
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

FAMILY = "coal_uranium_metals"
MIN_MST = 50.0
CTX = {}


def coal(in_dir):
    def build():
        d = h.read("eia_world_coal_annual", in_dir, ["entity", "variable", "ts_utc", "value", "node", "x_area"], ["value"], keep=lambda c: c["entity"].str.endswith(":7"))
        d = d.dropna(subset=["value"])
        d["iso"] = d["entity"].str.split(":").str[1]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        d["name"] = d["node"].str.split(",").str[0].str.strip()
        return d
    return hm._cached(("c502_wcoal", in_dir), build)


def _measure(var):
    def f(in_dir=None):
        d = coal(in_dir)
        big = d[(d["year"] == 2023) & d["variable"].isin(["consumption", "production"]) & (d["value"] >= MIN_MST * 1e6)]["iso"]
        keep = set(big[d.loc[big.index, "x_area"] == "country"]) | {"WORL"}
        x = d[(d["variable"] == var) & d["iso"].isin(keep)]
        rows, tabs = [], {}
        for iso, g in x.groupby("iso"):
            k = f"wc_{iso.lower()}"
            nm = g["name"].iloc[-1]
            w = "the world" if iso == "WORL" else ("the " + nm if nm.startswith("United") else nm)
            for _, r in g.iterrows():
                rows.append(hm._row(k, w, int(r["year"]), float(r["value"] / 1e6), 1))
            tabs[k] = ["eia_world_coal_annual"]
        return {"rows": rows, "tables": tabs}
    return f


wc_consumption, wc_production, wc_exports = _measure("consumption"), _measure("production"), _measure("exports")


def reproduce_py(name, region):
    var, iso = name.split("_")[1], region.split("_")[1].upper()
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == 'eia_intl:{iso}:7') & (d['variable'] == '{var}')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nfor _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():\n    print(int(r['ts_utc'][:4]), round(float(r['value'] / 1e6), 6), 1)\n")
    return h.py_doc(name, region, ["eia_world_coal_annual"], f"The coal {var} (all coal, product code 7; million short tons) of {iso}, by year.") + h.PY_READ + body


def reproduce_do(name, region):
    var, iso = name.split("_")[1], region.split("_")[1].upper()
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table eia_world_coal_annual.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "eia_world_coal_annual.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia_intl:{iso}:7" & variable == "{var}"',
             "keep ts_utc value", "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
             "generate double measure = value / 1000000", "generate byte n = 1", "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = "EIA's international energy data as the latest bulk file holds them; short tons of all coal, not its heat; a country's recent years are often EIA's estimates."
CANDIDATES = [C(n, FAMILY, fn, "million short tons", 1, 1, 20.0, f"COAL BY COUNTRY: {n.split('_')[1].upper()}", f"the country's coal {n.split('_')[1]}",
                (lambda v: (lambda w: f"the coal {v} of {w}"))(n.split("_")[1]), L, reproduce(n), consequence=3)
              for n, fn in (("wc_consumption", wc_consumption), ("wc_production", wc_production), ("wc_exports", wc_exports))]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["rank_region"] = lambda r: {"wc_worl": 1e9, "wc_usa": 5e8}.get(r, 0.0)        # the world, then the US, then the largest moves
    _P["max_per"] = 4


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, world coal")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=12)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("worldcoal", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
