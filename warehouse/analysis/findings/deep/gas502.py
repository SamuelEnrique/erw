#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family gas: pipeline capacity between states and gas customers, session 8217.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Two public EIA tables no draft had
read (runs/c502/unread.py):

    eia_state_to_state_capacity (EIA's State-to-State Capacity, 1990 to 2025: each pipeline's capacity at each state border
    it crosses, a year)
        s2s_in     the summed capacity of the crossings into a state (bcf a day), from other states, Canada and Mexico
        s2s_out    the summed capacity of the crossings out of a state (bcf a day)
    eia_gas_consumers_state_annual (1986 on)
        gas_res_customers   the state's residential natural gas customers (thousands)

A crossing EIA lists twice is counted twice, as the table keeps it.

    python warehouse/analysis/findings/deep/gas502.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/gas502.py --load
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
import partd  # noqa: E402

FAMILY = "gas"
NAMES = {v: v for v in partd.STATES.values() if not v.startswith("the ")}     # the table names states in full, title case
CTX = {}


def s2s(in_dir):
    def build():
        d = h.read("eia_state_to_state_capacity", in_dir, ["entity", "ts_utc", "value", "x_state_from", "x_state_to"], ["value"])
        d["year"] = d["ts_utc"].str[:4].astype(int)
        return d.dropna(subset=["value"])
    return hm._cached(("c502_s2s", in_dir), build)


def _cap(col, prefix, word):
    def f(in_dir=None):
        d = s2s(in_dir)
        rows, tabs = [], {}
        for st, g in d.groupby(col):
            if st not in NAMES:
                continue
            k = f"{prefix}_{st.lower().replace(' ', '_')}"
            by = g.groupby("year")["value"].sum()
            for y, v in by.items():
                rows.append(hm._row(k, NAMES[st], int(y), float(v), 1))
            tabs[k] = ["eia_state_to_state_capacity"]
        return {"rows": rows, "tables": tabs}
    return f


s2s_in, s2s_out = _cap("x_state_to", "s2in", "into"), _cap("x_state_from", "s2out", "out of")


def gas_res_customers(in_dir=None):
    d = h.read("eia_gas_consumers_state_annual", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"], keep=lambda c: c["variable"] == "residential_consumers")
    d = d.dropna(subset=["value"])
    rows, tabs = [], {}
    for e, g in d.groupby("entity"):
        code = e.split(":")[1]
        if not (code.startswith("S") and code[1:] in partd.STATES):
            continue
        k = f"gc_{code[1:].lower()}"
        for _, r in g.iterrows():
            rows.append(hm._row(k, partd.STATES[code[1:]], int(r["ts_utc"][:4]), float(r["value"] / 1000), 1))
        tabs[k] = ["eia_gas_consumers_state_annual"]
    return {"rows": rows, "tables": tabs}


def reproduce_py(name, region):
    if name in ("s2s_in", "s2s_out"):
        col = "x_state_to" if name == "s2s_in" else "x_state_from"
        st = next(v for v in NAMES if v.lower().replace(' ', '_') == region.split('_', 1)[1])
        body = (f"d = read(sys.argv[1], ['ts_utc', 'value', '{col}'])\nd = d[d['{col}'] == '{st}'].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                "for y, s in d.dropna(subset=['value']).groupby(d['ts_utc'].str[:4]):\n    print(y, round(float(s['value'].sum()), 6), 1)\n")
        return h.py_doc(name, region, ["eia_state_to_state_capacity"], f"The summed capacity (bcf a day) of the pipeline crossings {'into' if name == 's2s_in' else 'out of'} {NAMES[st]}, by year.") + h.PY_READ + body
    st = region.split("_")[1].upper()
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == 'eia_gas_consumers:S{st}') & (d['variable'] == 'residential_consumers')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nfor _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():\n    print(int(r['ts_utc'][:4]), round(float(r['value'] / 1000), 6), 1)\n")
    return h.py_doc(name, region, ["eia_gas_consumers_state_annual"], f"The residential natural gas customers (thousands) of {partd.STATES[st]}, by year.") + h.PY_READ + body


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
            "clear all"]
    if name in ("s2s_in", "s2s_out"):
        col = "x_state_to" if name == "s2s_in" else "x_state_from"
        st = next(v for v in NAMES if v.lower().replace(' ', '_') == region.split('_', 1)[1])
        lines = head + ['import delimited "eia_state_to_state_capacity.csv", varnames(1) stringcols(_all) clear', f'keep if {col} == "{st}"', "keep ts_utc value",
                        "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", "collapse (sum) measure = value, by(year)",
                        "generate byte n = 1"]
    else:
        st = region.split("_")[1].upper()
        lines = head + ['import delimited "eia_gas_consumers_state_annual.csv", varnames(1) stringcols(_all) clear',
                        f'keep if entity == "eia_gas_consumers:S{st}" & variable == "residential_consumers"', "keep ts_utc value", "destring value, replace force",
                        "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", "generate double measure = value / 1000", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LS = "EIA's State-to-State Capacity as its January 2026 issue lists it: each pipeline's capacity at a border crossing, a year; capacity is what a pipeline can carry, not what it carried."
CANDIDATES_ALL = [
    C("s2s_in", FAMILY, s2s_in, "bcf a day", 2, 1, 0.5, "PIPELINE CAPACITY INTO A STATE", "the summed capacity of the pipeline crossings into the state",
      lambda w: f"the summed capacity of the natural gas pipeline crossings into {w}", LS, reproduce("s2s_in"), consequence=3),
    C("s2s_out", FAMILY, s2s_out, "bcf a day", 2, 1, 0.5, "PIPELINE CAPACITY OUT OF A STATE", "the summed capacity of the pipeline crossings out of the state",
      lambda w: f"the summed capacity of the natural gas pipeline crossings out of {w}", LS, reproduce("s2s_out"), consequence=3),
    C("gas_res_customers", FAMILY, gas_res_customers, "thousand customers", 0, 1, 50.0, "HOMES ON NATURAL GAS", "the state's residential natural gas customers",
      lambda w: f"the residential natural gas customers of {w}", "EIA's count of residential customers as reported by the state's distributors.", reproduce("gas_res_customers"), consequence=2),
]
# session 8217: the customer counts mix units across years (Arizona: 1 thousand in 1986, 1,396 thousand in 2024), so they are not drafted
CANDIDATES = [P for P in CANDIDATES_ALL if P["name"] != "gas_res_customers"]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = 5


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, gas")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=13)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("gas502", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
