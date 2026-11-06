#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "oil_products_world", second part (session 3014).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Public EIA tables, monthly:

    eia_world_oil_monthly              EIA's international statistics: production by country and in all (WORL); the US
                                       share of world total liquids (code 53) and of world NGPL (code 58)
    eia_refinery_utilization_monthly   US operable crude distillation capacity (MOCLEUS2, thousand b/d)
    eia_crude_quality_monthly          the API gravity (MCRAPUS2) and sulfur content (MCRS1US2) of the crude US refineries ran
    eia_product_supplied_monthly       US product supplied by product (thousand b/d): finished motor gasoline (MGFUPUS2),
                                       distillate (MDIUPUS2), jet fuel (MKJUPUS2), propane (MPRUPUS2), residual (MREUPUS2)

Two rules: MEAN, the year's mean of a series' months; SHARE, one series' months summed over another's, the months
that hold both. A year's months are its observations. The reproduction scripts follow the same two rules.

    python warehouse/analysis/findings/deep/oil_world.py --dry-run
    python warehouse/analysis/findings/deep/oil_world.py --load
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

FAMILY = "oil_products_world"
WORLD, REF, QUAL, SUP = "eia_world_oil_monthly", "eia_refinery_utilization_monthly", "eia_crude_quality_monthly", "eia_product_supplied_monthly"
PRODUCTS = {"gasoline": ("eia_product_supplied:MGFUPUS2", "finished motor gasoline"), "distillate": ("eia_product_supplied:MDIUPUS2", "distillate fuel oil"),
            "jet": ("eia_product_supplied:MKJUPUS2", "kerosene-type jet fuel"), "propane": ("eia_product_supplied:MPRUPUS2", "propane and propylene"),
            "residual": ("eia_product_supplied:MREUPUS2", "residual fuel oil")}
# name: (table, kind, numerator (entity, variable), denominator or None, scale)
SPEC = {
    "us_liquids_share": (WORLD, "share", ("eia_intl:USA:53", "production"), ("eia_intl:WORL:53", "production"), 100.0),
    "us_ngpl_share": (WORLD, "share", ("eia_intl:USA:58", "production"), ("eia_intl:WORL:58", "production"), 100.0),
    "refining_capacity": (REF, "mean", ("eia_refinery_utilization:MOCLEUS2", "operable_capacity"), None, 1.0),
    "api_gravity": (QUAL, "mean", ("eia_crude_quality:MCRAPUS2", "api_gravity"), None, 1.0),
    "sulfur_content": (QUAL, "mean", ("eia_crude_quality:MCRS1US2", "sulfur_content"), None, 1.0),
}
for _k, (_e, _w) in PRODUCTS.items():
    SPEC[f"supplied_{_k}"] = (SUP, "mean", (_e, "product_supplied_per_day"), None, 1.0)


def compute(d, kind, num, den, scale):
    """{year: (value, months)} by the module's two rules; d holds entity, variable, ts_utc and a numeric value."""
    d = d.drop_duplicates(["entity", "variable", "ts_utc"]).assign(year=d["ts_utc"].str[:4].astype(int))
    a = d[(d["entity"] == num[0]) & (d["variable"] == num[1])]
    if kind == "mean":
        return {int(y): (float(s["value"].mean() * scale), len(s)) for y, s in a.groupby("year")}
    b = d[(d["entity"] == den[0]) & (d["variable"] == den[1])]
    m = a.merge(b[["ts_utc", "value"]], on="ts_utc", suffixes=("", "_den"))
    out = {}
    for y, s in m.groupby("year"):
        if s["value_den"].sum() != 0:
            out[int(y)] = (float(s["value"].sum() * scale / s["value_den"].sum()), len(s))
    return out


def _fn(name, region, words):
    table, kind, num, den, scale = SPEC[name]

    def fn(in_dir=None):
        ents = [num[0]] + ([den[0]] if den else [])
        d = hm.series(table, in_dir, entities=ents)[["entity", "variable", "ts_utc", "value"]]
        rows = [hm._row(region, words, y, v, n) for y, (v, n) in compute(d, kind, num, den, scale).items()]
        return {"rows": rows, "tables": {region: [table]}}
    fn.__name__ = name
    return fn


PY = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <{table}.csv>

{label}. Rule {kind}: {rule}
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
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"]).drop_duplicates(["entity", "variable", "ts_utc"])
d["year"] = d["ts_utc"].str[:4].astype(int)
a = d[(d["entity"] == {num_e!r}) & (d["variable"] == {num_v!r})]
'''
PY_MEAN = "for y, s in a.groupby('year'):\n    print(y, round(float(s['value'].mean() * {scale!r}), 6), len(s))\n"
PY_SHARE = ("b = d[(d['entity'] == {den_e!r}) & (d['variable'] == {den_v!r})]\nm = a.merge(b[['ts_utc', 'value']], on='ts_utc', suffixes=('', '_den'))\n"
            "for y, s in m.groupby('year'):\n    if s['value_den'].sum() != 0:\n        print(y, round(float(s['value'].sum() * {scale!r} / s['value_den'].sum()), 6), len(s))\n")


def reproduce_py(name, region):
    table, kind, num, den, scale = SPEC[name]
    P = next(p for p in CANDIDATES if p["name"] == name)
    rule = "the year's mean of the series' months." if kind == "mean" else "the series' months summed over the other's, the months that hold both."
    text = PY.format(name=name, region=region, table=table, label=P["label"][0].upper() + P["label"][1:], kind=kind, rule=rule, num_e=num[0], num_v=num[1])
    return text + (PY_MEAN.format(scale=scale) if kind == "mean" else PY_SHARE.format(den_e=den[0], den_v=den[1], scale=scale))


def reproduce_do(name, region):
    table, kind, num, den, scale = SPEC[name]
    lines = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
             "clear all", f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear', "destring value, replace force", "drop if missing(value)",
             "duplicates drop entity variable ts_utc, force", "generate int year = real(substr(ts_utc, 1, 4))"]
    if kind == "mean":
        lines += [f'keep if entity == "{num[0]}" & variable == "{num[1]}"', "collapse (mean) measure = value (count) n = value, by(year)",
                  f"replace measure = measure * {scale!r}"]
    else:
        lines += [f'keep if (entity == "{num[0]}" & variable == "{num[1]}") | (entity == "{den[0]}" & variable == "{den[1]}")',
                  f'generate str3 side = cond(entity == "{num[0]}", "num", "den")', "keep year ts_utc side value", "reshape wide value, i(ts_utc) j(side) string",
                  "drop if missing(valuenum) | missing(valueden)", "collapse (sum) num = valuenum (sum) den = valueden (count) n = valuenum, by(year)",
                  "keep if den != 0", f"generate double measure = num * {scale!r} / den"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT = "EIA's monthly figures as published, the latest months preliminary."
CANDIDATES = [
    C("us_liquids_share", FAMILY, _fn("us_liquids_share", "us_world_liquids", "the United States"), "percent of world production", 1, 11, 1.0,
      "THE US SHARE OF WORLD OIL", "US total petroleum and other liquids production as a percent of the world's, the months that hold both",
      lambda w: "the US share of world petroleum and other liquids production", LIMIT + " Liquids hold crude, NGPL, refinery gain and biofuels together.",
      reproduce("us_liquids_share"), consequence=3),
    C("us_ngpl_share", FAMILY, _fn("us_ngpl_share", "us_world_ngpl", "the United States"), "percent of world NGPL", 1, 11, 2.0,
      "THE US SHARE OF WORLD NGPL", "US natural gas plant liquids production as a percent of the world's, the months that hold both",
      lambda w: "the US share of world natural gas plant liquids production", LIMIT, reproduce("us_ngpl_share"), consequence=2),
    C("refining_capacity", FAMILY, _fn("refining_capacity", "us_refining_capacity", "the United States"), "thousand barrels a day", 0, 11, 200.0,
      "US REFINING CAPACITY", "US operable crude distillation capacity, the year's mean of its months",
      lambda w: "US operable crude oil distillation capacity", LIMIT + " Operable capacity counts idle units that could run within 30 days.",
      reproduce("refining_capacity"), consequence=2),
    C("api_gravity", FAMILY, _fn("api_gravity", "us_api_gravity", "the United States"), "degrees API", 2, 11, 0.3,
      "HOW LIGHT US REFINERIES' CRUDE IS", "the weighted average API gravity of the crude oil US refineries ran, the year's mean of its months",
      lambda w: "the average API gravity of the crude oil run in US refineries", LIMIT + " A higher API gravity is a lighter crude.",
      reproduce("api_gravity"), consequence=2),
    C("sulfur_content", FAMILY, _fn("sulfur_content", "us_sulfur", "the United States"), "percent sulfur by weight", 3, 11, 0.05,
      "HOW SOUR US REFINERIES' CRUDE IS", "the weighted average sulfur content of the crude oil US refineries ran, the year's mean of its months",
      lambda w: "the average sulfur content of the crude oil run in US refineries", LIMIT, reproduce("sulfur_content"), consequence=2),
]
for _k, (_e, _w) in PRODUCTS.items():
    CANDIDATES.append(C(f"supplied_{_k}", FAMILY, _fn(f"supplied_{_k}", f"us_supplied_{_k}", f"US {_w}"), "thousand barrels a day", 0, 11, 100.0,
                        "WHAT THE US USES", f"US product supplied of {_w}, the year's mean of its months", lambda w: f"US product supplied of {w[3:]}",
                        LIMIT + " Product supplied is EIA's measure of demand: what leaves primary supply, not what is burned that month.",
                        reproduce(f"supplied_{_k}"), consequence=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family oil and the world (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_world", cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
