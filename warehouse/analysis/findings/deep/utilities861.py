#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family other_us: what each utility sells, from EIA-861M, session 8209.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table eia861m_utility_sales_monthly
(public, EIA Form 861M, 2017 on; the largest table of the power sector no draft had read): each utility's monthly retail
sales, revenue and customers by sector, in each state it serves.

    util_commercial / util_industrial / util_total   the year's retail sales (TWh), a utility in a state, years with
                                                     all twelve months held
    util_commercial_price                            the year's commercial revenue over its commercial sales (USD per MWh)

A utility is read when it sold at least 2 TWh to commercial customers in 2017, so a small utility's percent swing does
not lead; the largest movers in TWh are kept.

    python warehouse/analysis/findings/deep/utilities861.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/utilities861.py --load
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

FAMILY = "other_us"
MIN_TWH = 2.0
# session 8209: where customers may buy power from another supplier (retail choice, community choice aggregation), a
# utility's sales count only the customers it still fully serves, so a migration reads as a fall; those states are not read
CHOICE = {"CA", "NY", "TX", "IL", "OH", "PA", "MD", "NJ", "MA", "CT", "RI", "NH", "ME", "DE", "DC", "MI"}
VARS = ["commercial_sales", "industrial_sales", "total_sales", "commercial_revenue"]
CTX = {}


def sales(in_dir):
    def build():
        d = h.read("eia861m_utility_sales_monthly", in_dir, ["entity", "variable", "ts_utc", "value", "node", "x_state"], ["value"], keep=lambda c: c["variable"].isin(VARS))
        d = d.dropna(subset=["value"])
        d["year"] = d["ts_utc"].str[:4].astype(int)
        g = d.groupby(["entity", "variable", "year"]).agg(value=("value", "sum"), n=("value", "size"), node=("node", "last"), st=("x_state", "last")).reset_index()
        big = g[(g["variable"] == "commercial_sales") & (g["year"] == 2017) & (g["n"] == 12) & (g["value"] >= MIN_TWH * 1e6)]["entity"]
        g = g[g["entity"].isin(set(big))]
        return g[~g["entity"].str.split(":").str[2].isin(CHOICE)]
    return hm._cached(("c502_861m", in_dir), build)


def words(node, st):
    return f"{node.strip()} in {st}"


def _twh(var):
    def f(in_dir=None):
        g = sales(in_dir)
        g = g[g["variable"] == var]
        rows, tabs = [], {}
        for e, x in g.groupby("entity"):
            k = "u861_" + e.split(":", 1)[1].replace(":", "_").lower()
            w = words(x["node"].iloc[-1], x["st"].iloc[-1])
            for _, r in x.iterrows():
                rows.append(hm._row(k, w, int(r["year"]), float(r["value"] / 1e6), float(r["n"])))
            tabs[k] = ["eia861m_utility_sales_monthly"]
        return {"rows": rows, "tables": tabs}
    return f


util_commercial, util_industrial, util_total = _twh("commercial_sales"), _twh("industrial_sales"), _twh("total_sales")


def util_commercial_price(in_dir=None):
    g = sales(in_dir)
    w = g[g["variable"].isin(["commercial_sales", "commercial_revenue"])].pivot_table(index=["entity", "year"], columns="variable", values=["value", "n"], aggfunc="first")
    rows, tabs = [], {}
    names = g.drop_duplicates("entity", keep="last").set_index("entity")
    for (e, y), r in w.iterrows():
        s, rev = r[("value", "commercial_sales")], r[("value", "commercial_revenue")]
        n = min(r[("n", "commercial_sales")], r[("n", "commercial_revenue")])
        if s > 0:
            k = "u861_" + e.split(":", 1)[1].replace(":", "_").lower()
            rows.append(hm._row(k, words(names.loc[e, "node"], names.loc[e, "st"]), int(y), float(rev / s), float(n)))
            tabs[k] = ["eia861m_utility_sales_monthly"]
    return {"rows": rows, "tables": tabs}


def _entity(region):
    parts = region.split("_")
    return f"eia861m:{parts[1]}:{parts[2].upper()}"


def reproduce_py(name, region):
    e = _entity(region)
    if name == "util_commercial_price":
        body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == '{e}') & d['variable'].isin(['commercial_sales', 'commercial_revenue'])].copy()\n"
                "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['value'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\n"
                "g = d.groupby(['year', 'variable'])['value'].agg(['sum', 'size']).unstack('variable')\nfor y, r in g.iterrows():\n"
                "    if r[('sum', 'commercial_sales')] > 0:\n        print(y, round(float(r[('sum', 'commercial_revenue')] / r[('sum', 'commercial_sales')]), 6), int(min(r[('size', 'commercial_sales')], r[('size', 'commercial_revenue')])))\n")
        what = f"The commercial revenue over commercial sales (USD per MWh) of {e}, by year, with the months held."
    else:
        var = {"util_commercial": "commercial_sales", "util_industrial": "industrial_sales", "util_total": "total_sales"}[name]
        body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == '{e}') & (d['variable'] == '{var}')].copy()\n"
                "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['value'])\nfor y, s in d.groupby(d['ts_utc'].str[:4]):\n"
                "    print(y, round(float(s['value'].sum() / 1e6), 6), len(s))\n")
        what = f"The {var.replace('_', ' ')} (TWh) of {e}, by year, with the months held."
    return h.py_doc(name, region, ["eia861m_utility_sales_monthly"], what) + h.PY_READ + body


def reproduce_do(name, region):
    e = _entity(region)
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table eia861m_utility_sales_monthly.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "eia861m_utility_sales_monthly.csv", varnames(1) stringcols(_all) clear']
    if name == "util_commercial_price":
        lines += [f'keep if entity == "{e}" & (variable == "commercial_sales" | variable == "commercial_revenue")', "keep ts_utc variable value", "destring value, replace force",
                  "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", "generate double s = value if variable == \"commercial_sales\"",
                  "generate double r = value if variable == \"commercial_revenue\"", "collapse (sum) s = s (sum) r = r (count) ns = s (count) nr = r, by(year)", "keep if s > 0",
                  "generate double measure = r / s", "generate n = min(ns, nr)"]
    else:
        var = {"util_commercial": "commercial_sales", "util_industrial": "industrial_sales", "util_total": "total_sales"}[name]
        lines += [f'keep if entity == "{e}" & variable == "{var}"', "keep ts_utc value", "destring value, replace force", "drop if missing(value)",
                  "generate int year = real(substr(ts_utc, 1, 4))", "collapse (sum) measure = value (count) n = value, by(year)", "replace measure = measure / 1000000"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = ("EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; "
     "the latest year's months may be preliminary.")
CANDIDATES = [
    C("util_commercial", FAMILY, util_commercial, "TWh", 2, 12, 0.5, "WHAT A UTILITY SELLS TO COMMERCIAL CUSTOMERS", "the year's retail sales to commercial customers",
      lambda w: f"the retail electricity sales to commercial customers of {w}", L, reproduce("util_commercial"), consequence=3),
    C("util_industrial", FAMILY, util_industrial, "TWh", 2, 12, 0.5, "WHAT A UTILITY SELLS TO INDUSTRY", "the year's retail sales to industrial customers",
      lambda w: f"the retail electricity sales to industrial customers of {w}", L, reproduce("util_industrial"), consequence=3),
    C("util_total", FAMILY, util_total, "TWh", 2, 12, 0.5, "WHAT A UTILITY SELLS", "the year's retail sales to all customers",
      lambda w: f"the retail electricity sales of {w}", L, reproduce("util_total"), consequence=3),
    C("util_commercial_price", FAMILY, util_commercial_price, "USD per MWh", 1, 12, 10.0, "WHAT COMMERCIAL CUSTOMERS PAY", "the year's commercial revenue over commercial sales",
      lambda w: f"the average price of electricity to commercial customers of {w} (revenue over sales, nominal)", L + " Nominal dollars.", reproduce("util_commercial_price"), consequence=2),
]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = {"util_commercial": 6, "util_industrial": 4, "util_total": 4, "util_commercial_price": 3}[_P["name"]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, utilities (EIA-861M)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=17)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("utilities861", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
