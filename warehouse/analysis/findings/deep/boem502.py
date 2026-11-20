#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family oil_products_world: offshore production in the Gulf of America, session 8224.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table boem_ogor_lease_production_monthly
(public, BOEM's OGOR-A, every lease's monthly oil and gas, 1996 on; no draft had read it; 1.1 million rows):

    gulf_oil      the Gulf's federal offshore oil production, thousand barrels a day (the year's barrels over its days)
    gulf_gas      its gas production, million cubic feet a day
    gulf_leases   the leases (or units) that produced any oil or gas in the year

    python warehouse/analysis/findings/deep/boem502.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/boem502.py --load
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
CTX = {}


def boem(in_dir):
    def build():
        d = h.read("boem_ogor_lease_production_monthly", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"])
        d = d.dropna(subset=["value"])
        d["year"] = d["ts_utc"].str[:4].astype(int)
        d["month"] = d["ts_utc"].str[:7]
        return d
    return hm._cached(("c502_boem", in_dir), build)


def _days(y):
    return 366 if y % 4 == 0 else 365


def _volume(var):
    def f(in_dir=None):
        d = boem(in_dir)
        d = d[d["variable"] == var]
        rows = []
        for y, s in d.groupby("year"):
            rows.append(hm._row("gulf", "the Gulf of America's federal offshore leases", int(y), float(s["value"].sum() / _days(int(y))), s["month"].nunique()))
        return {"rows": rows, "tables": {"gulf": ["boem_ogor_lease_production_monthly"]}}
    return f


gulf_oil, gulf_gas = _volume("oil_production"), _volume("gas_production")


def gulf_leases(in_dir=None):
    d = boem(in_dir)
    d = d[d["value"] > 0]
    rows = [hm._row("gulf", "the Gulf of America's federal offshore leases", int(y), float(s["entity"].nunique()), s["month"].nunique()) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"gulf": ["boem_ogor_lease_production_monthly"]}}


def reproduce_py(name, region):
    if name == "gulf_leases":
        body = ("d = read(sys.argv[1], ['entity', 'ts_utc', 'value'])\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d[d['value'] > 0]\n"
                "for y, s in d.groupby(d['ts_utc'].str[:4]):\n    print(y, s['entity'].nunique(), s['ts_utc'].str[:7].nunique())\n")
        what = "The leases (or units) that produced any oil or gas, by year; the third figure is the months held."
    else:
        var = "oil_production" if name == "gulf_oil" else "gas_production"
        body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[d['variable'] == '{var}'].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                "d = d.dropna(subset=['value'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\nfor y, s in d.groupby('year'):\n"
                "    print(y, round(float(s['value'].sum() / (366 if y % 4 == 0 else 365)), 6), s['ts_utc'].str[:7].nunique())\n")
        what = f"The Gulf's {'oil (thousand barrels a day)' if name == 'gulf_oil' else 'gas (million cubic feet a day)'}: the year's volume over its days; the third figure is the months held."
    return h.py_doc(name, region, ["boem_ogor_lease_production_monthly"], what) + h.PY_READ + body


def reproduce_do(name, region):
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table boem_ogor_lease_production_monthly.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "boem_ogor_lease_production_monthly.csv", varnames(1) stringcols(_all) clear']
    if name == "gulf_leases":
        lines += ["destring value, replace force", "keep if value > 0 & !missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", "generate str7 ym = substr(ts_utc, 1, 7)",
                  "bysort year entity: generate byte firstl = _n == 1", "bysort year ym: generate byte firstm = _n == 1",
                  "collapse (sum) measure = firstl (sum) n = firstm, by(year)"]
    else:
        var = "oil_production" if name == "gulf_oil" else "gas_production"
        lines += [f'keep if variable == "{var}"', "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
                  "generate str7 ym = substr(ts_utc, 1, 7)", "bysort year ym: generate byte firstm = _n == 1", "collapse (sum) vol = value (sum) n = firstm, by(year)",
                  "generate double measure = vol / cond(mod(year, 4) == 0, 366, 365)"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = "BOEM's OGOR-A well production as the ERW sums it by lease, the Gulf of America's federal waters only; the latest months are revised as operators report."
CANDIDATES = [
    C("gulf_oil", FAMILY, gulf_oil, "thousand barrels a day", 0, 12, 50.0, "OIL FROM THE GULF'S FEDERAL WATERS", "the Gulf's federal offshore oil production",
      lambda w: f"the oil production of {w}", L, reproduce("gulf_oil"), consequence=3, first_words="the first full year the ERW holds"),
    C("gulf_gas", FAMILY, gulf_gas, "million cubic feet a day", 0, 12, 300.0, "GAS FROM THE GULF'S FEDERAL WATERS", "the Gulf's federal offshore gas production",
      lambda w: f"the gas production of {w}", L, reproduce("gulf_gas"), consequence=3),
    C("gulf_leases", FAMILY, gulf_leases, "leases", 0, 12, 50.0, "PRODUCING LEASES IN THE GULF", "the leases that produced any oil or gas in the year",
      lambda w: f"the count of {w} that produced any oil or gas", L, reproduce("gulf_leases"), consequence=2),
]


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, Gulf offshore production")
    ap.add_argument("--in-dir", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("boem502", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=3)
    return 0


if __name__ == "__main__":
    sys.exit(main())
