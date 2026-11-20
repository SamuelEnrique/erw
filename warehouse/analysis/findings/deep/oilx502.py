#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family oil_products_world: what the United States exports, session 8218.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table
eia_petroleum_exports_by_destination (public, EIA, monthly from 2015; no draft had read it): US exports by product and
destination, thousand barrels a month.

    exp_crude_dest   US crude oil exports (product EPC0) to a destination, thousand barrels a day
    exp_product      US exports of a product to the world (destination Z00), thousand barrels a day

A year's figure is its months' barrels over its days, years with all twelve months.

    python warehouse/analysis/findings/deep/oilx502.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/oilx502.py --load
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

FAMILY = "oil_products_world"
COUNTRY = {"CAN": "Canada", "CHN": "China", "KOR": "South Korea", "NLD": "the Netherlands", "GBR": "the United Kingdom", "IND": "India", "JPN": "Japan", "ITA": "Italy",
           "FRA": "France", "DEU": "Germany", "ESP": "Spain", "TWN": "Taiwan", "SGP": "Singapore", "MEX": "Mexico", "BRA": "Brazil", "THA": "Thailand", "AUS": "Australia",
           "PRT": "Portugal", "GRC": "Greece", "POL": "Poland", "ISR": "Israel", "TUR": "Turkey", "PER": "Peru", "CHL": "Chile", "COL": "Colombia", "PAN": "Panama",
           "DOM": "the Dominican Republic", "VNM": "Vietnam", "MYS": "Malaysia", "IDN": "Indonesia", "SWE": "Sweden", "NOR": "Norway", "DNK": "Denmark", "BEL": "Belgium"}
PRODUCT = {"EPC0": "crude oil", "EPP0": "all petroleum products", "EPLLEA": "ethane", "EPLLPA": "propane", "EPD0": "distillate fuel oil", "EPM0F": "finished motor gasoline",
           "EPJK": "kerosene-type jet fuel", "EPPC": "petroleum coke", "EPPR": "residual fuel oil"}
CTX = {}


def exports(in_dir):
    def build():
        d = h.read("eia_petroleum_exports_by_destination", in_dir, ["entity", "variable", "ts_utc", "value", "node"], ["value"], keep=lambda c: c["variable"] == "exports")
        d = d.dropna(subset=["value"])
        p = d["entity"].str.split(":")
        d["dest"], d["prod"] = p.str[1].str.split("-").str[1], p.str[2]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        d["iso3"] = d["node"].str.split(",").str[0].str.strip()
        return d
    return hm._cached(("c502_oilx", in_dir), build)


def _days(y):
    return 366 if y % 4 == 0 else 365


def _rows(g, k, w):
    out = []
    for y, s in g.groupby("year"):
        out.append(hm._row(k, w, int(y), float(s["value"].sum() / _days(int(y))), len(s)))
    return out


def exp_crude_dest(in_dir=None):
    d = exports(in_dir)
    d = d[(d["prod"] == "EPC0") & (d["dest"] != "Z00")]
    rows, tabs = [], {}
    for dest, g in d.groupby("dest"):
        iso = g["iso3"].iloc[-1]
        k = f"xc_{dest.lower()}"
        rows += _rows(g, k, f"{COUNTRY.get(iso, iso)}")
        tabs[k] = ["eia_petroleum_exports_by_destination"]
    return {"rows": rows, "tables": tabs}


def exp_product(in_dir=None):
    d = exports(in_dir)
    d = d[(d["dest"] == "Z00") & d["prod"].isin(PRODUCT)]
    rows, tabs = [], {}
    for prod, g in d.groupby("prod"):
        k = f"xp_{prod.lower()}"
        rows += _rows(g, k, PRODUCT[prod])
        tabs[k] = ["eia_petroleum_exports_by_destination"]
    return {"rows": rows, "tables": tabs}


def _entity(name, region):
    code = region.split("_", 1)[1].upper()
    return f"eia_petroleum_exports:NUS-{code}:EPC0" if name == "exp_crude_dest" else f"eia_petroleum_exports:NUS-Z00:{code}"


def reproduce_py(name, region):
    e = _entity(name, region)
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == '{e}') & (d['variable'] == 'exports')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['value'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\n"
            "for y, s in d.groupby('year'):\n    print(y, round(float(s['value'].sum() / (366 if y % 4 == 0 else 365)), 6), len(s))\n")
    return h.py_doc(name, region, ["eia_petroleum_exports_by_destination"], f"The exports of {e} (thousand barrels a day: the year's barrels over its days), with the months held.") + h.PY_READ + body


def reproduce_do(name, region):
    e = _entity(name, region)
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table eia_petroleum_exports_by_destination.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "eia_petroleum_exports_by_destination.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{e}" & variable == "exports"',
             "keep ts_utc value", "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
             "collapse (sum) kbbl = value (count) n = value, by(year)", "generate double measure = kbbl / cond(mod(year, 4) == 0, 366, 365)", "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = "EIA's exports by destination as published, the latest months preliminary; a destination is the first one shipped to, not always where the oil is used."
CANDIDATES = [
    C("exp_crude_dest", FAMILY, exp_crude_dest, "thousand barrels a day", 0, 12, 30.0, "WHERE US CRUDE GOES", "US crude oil exports to the destination",
      lambda w: f"US crude oil exports to {w}", L + " A month with no row is not taken for zero: a year counts only with all twelve months listed.",
      reproduce("exp_crude_dest"), consequence=3, first_words="the first year with all twelve months listed"),
    C("exp_product", FAMILY, exp_product, "thousand barrels a day", 0, 12, 30.0, "WHAT THE US EXPORTS", "US exports of the product to the world",
      lambda w: f"US exports of {w}", L, reproduce("exp_product"), consequence=3),
]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = 6


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, US petroleum exports")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=12)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("oilx502", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
