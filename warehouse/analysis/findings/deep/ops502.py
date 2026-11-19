#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family markets_operations: nuclear outages and coal stocks, session 8211.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Two public EIA tables no draft
had read (runs/c502/unread.py):

    eia_nuclear_outages_facility_daily (2007 on): each facility's capacity and the MW on outage, every day
        nuc_out_mean      the year's mean of the US nuclear capacity on outage (MW), days with every facility's row
        nuc_out_peak      the year's highest day of US nuclear capacity on outage (MW)
        nuc_out_share     a facility's mean share of its capacity on outage over the year (percent)
    eia_power_fuel_stocks_monthly (2008 on): the coal held at power plants (electric power sector, code 98)
        coal_stocks_dec   the stock at the end of December (million short tons), the US and each state

    python warehouse/analysis/findings/deep/ops502.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/ops502.py --load
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

FAMILY = "markets_operations"
CTX = {}


def outages(in_dir):
    def build():
        d = h.read("eia_nuclear_outages_facility_daily", in_dir, ["entity", "variable", "ts_utc", "value", "node"], ["value"], keep=lambda c: c["variable"].isin(["capacity", "outage"]))
        w = d.pivot_table(index=["entity", "ts_utc"], columns="variable", values="value", aggfunc="first").dropna().reset_index()
        w["year"] = w["ts_utc"].str[:4].astype(int)
        names = d.drop_duplicates("entity", keep="last").set_index("entity")["node"]
        w["node"] = w["entity"].map(names)
        return w
    return hm._cached(("c502_nuc", in_dir), build)


def _us_daily(in_dir):
    w = outages(in_dir)
    return w.groupby(["ts_utc", "year"])["outage"].sum().reset_index()


def nuc_out_mean(in_dir=None):
    d = _us_daily(in_dir)
    rows = [hm._row("nuc_us", "the US nuclear fleet", y, float(s["outage"].mean()), len(s)) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"nuc_us": ["eia_nuclear_outages_facility_daily"]}}


def nuc_out_peak(in_dir=None):
    d = _us_daily(in_dir)
    rows = [hm._row("nuc_us", "the US nuclear fleet", y, float(s["outage"].max()), len(s)) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"nuc_us": ["eia_nuclear_outages_facility_daily"]}}


def nuc_out_share(in_dir=None):
    w = outages(in_dir)
    w = w[w["capacity"] > 0]
    rows, tabs = [], {}
    for e, g in w.groupby("entity"):
        k = "nucf_" + e.split(":")[1]
        for y, s in g.groupby("year"):
            rows.append(hm._row(k, f"the {g['node'].iloc[-1]} nuclear plant", y, float((s["outage"] / s["capacity"]).mean() * 100), len(s)))
        tabs[k] = ["eia_nuclear_outages_facility_daily"]
    return {"rows": rows, "tables": tabs}


def coal_stocks_dec(in_dir=None):
    d = h.read("eia_power_fuel_stocks_monthly", in_dir, ["entity", "ts_utc", "value"], ["value"], keep=lambda c: c["entity"].str.endswith(":98:COL"))
    d = d.dropna(subset=["value"])
    d = d[d["ts_utc"].str[5:7] == "12"]
    rows, tabs = [], {}
    for e, g in d.groupby("entity"):
        st = e.split(":")[1]
        if st != "US" and st not in partd.STATES:
            continue
        k = f"cst_{st.lower()}"
        w = "US power plants" if st == "US" else f"the power plants of {partd.STATES[st]}"
        for _, r in g.iterrows():
            rows.append(hm._row(k, w, int(r["ts_utc"][:4]), float(r["value"] / 1e6), 1))
        tabs[k] = ["eia_power_fuel_stocks_monthly"]
    return {"rows": rows, "tables": tabs}


def reproduce_py(name, region):
    if name.startswith("nuc_out_") and name != "nuc_out_share":
        stat = "mean" if name == "nuc_out_mean" else "max"
        body = ("d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[d['variable'].isin(['capacity', 'outage'])].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                "w = d.pivot_table(index=['entity', 'ts_utc'], columns='variable', values='value', aggfunc='first').dropna().reset_index()\n"
                "us = w.groupby('ts_utc')['outage'].sum().reset_index()\nfor y, s in us.groupby(us['ts_utc'].str[:4]):\n"
                f"    print(y, round(float(s['outage'].{stat}()), 6), len(s))\n")
        return h.py_doc(name, region, ["eia_nuclear_outages_facility_daily"], f"The year's {stat} of the US nuclear capacity on outage (MW, the facilities summed by day).") + h.PY_READ + body
    if name == "nuc_out_share":
        e = "eia_nuclear_outages:" + region.split("_")[1]
        body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == '{e}') & d['variable'].isin(['capacity', 'outage'])].copy()\n"
                "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nw = d.pivot_table(index='ts_utc', columns='variable', values='value', aggfunc='first').dropna().reset_index()\n"
                "w = w[w['capacity'] > 0]\nfor y, s in w.groupby(w['ts_utc'].str[:4]):\n    print(y, round(float((s['outage'] / s['capacity']).mean() * 100), 6), len(s))\n")
        return h.py_doc(name, region, ["eia_nuclear_outages_facility_daily"], f"The year's mean share (percent) of {e}'s capacity on outage.") + h.PY_READ + body
    st = region.split("_")[1].upper()
    body = (f"d = read(sys.argv[1], ['entity', 'ts_utc', 'value'])\nd = d[(d['entity'] == 'eia_power_stocks:{st}:98:COL') & (d['ts_utc'].str[5:7] == '12')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nfor _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():\n    print(int(r['ts_utc'][:4]), round(float(r['value'] / 1e6), 6), 1)\n")
    return h.py_doc(name, region, ["eia_power_fuel_stocks_monthly"], f"The coal stocks (million short tons) of {st}'s electric power sector at the end of each December.") + h.PY_READ + body


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
            "clear all"]
    if name.startswith("nuc_out_"):
        lines = head + ['import delimited "eia_nuclear_outages_facility_daily.csv", varnames(1) stringcols(_all) clear']
        if name == "nuc_out_share":
            lines += [f'keep if entity == "eia_nuclear_outages:{region.split("_")[1]}"']
        lines += ['keep if variable == "capacity" | variable == "outage"', "keep entity ts_utc variable value", "destring value, replace force",
                  "reshape wide value, i(entity ts_utc) j(variable) string", "drop if missing(valuecapacity) | missing(valueoutage)"]
        if name == "nuc_out_share":
            lines += ["keep if valuecapacity > 0", "generate double share = 100 * valueoutage / valuecapacity", "generate int year = real(substr(ts_utc, 1, 4))",
                      "collapse (mean) measure = share (count) n = share, by(year)"]
        else:
            st = "mean" if name == "nuc_out_mean" else "max"
            lines += ["collapse (sum) outage = valueoutage, by(ts_utc)", "generate int year = real(substr(ts_utc, 1, 4))", f"collapse ({st}) measure = outage (count) n = outage, by(year)"]
    else:
        st = region.split("_")[1].upper()
        lines = head + ['import delimited "eia_power_fuel_stocks_monthly.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia_power_stocks:{st}:98:COL" & substr(ts_utc, 6, 2) == "12"',
                        "keep ts_utc value", "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
                        "generate double measure = value / 1000000", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LN = "EIA's daily nuclear outages by facility, as EIA compiles them from the NRC's daily status; a facility's capacity is as EIA lists it that day; a year's days are those every facility row holds."
LS = "EIA's stocks at power plants of the electric power sector (code 98), coal excluding waste coal, at the end of December."
CANDIDATES = [
    C("nuc_out_mean", FAMILY, nuc_out_mean, "MW", 0, 330, 300.0, "NUCLEAR CAPACITY ON OUTAGE", "the year's mean of the US nuclear capacity on outage",
      lambda w: f"the mean nuclear capacity on outage across {w} over the year", LN, reproduce("nuc_out_mean"), consequence=3),
    C("nuc_out_peak", FAMILY, nuc_out_peak, "MW", 0, 330, 1000.0, "THE YEAR'S WORST DAY OF NUCLEAR OUTAGES", "the year's highest day of US nuclear capacity on outage",
      lambda w: f"the highest day of nuclear capacity on outage across {w}", LN, reproduce("nuc_out_peak"), consequence=2),
    C("nuc_out_share", FAMILY, nuc_out_share, "percent", 1, 330, 3.0, "A NUCLEAR PLANT'S TIME OUT", "a facility's mean share of its capacity on outage over the year",
      lambda w: f"the mean share of the capacity of {w} on outage over the year", LN, reproduce("nuc_out_share"), consequence=2),
    C("coal_stocks_dec", FAMILY, coal_stocks_dec, "million short tons", 1, 1, 5.0, "COAL PILED AT POWER PLANTS", "the coal stocks of the electric power sector at the end of December",
      lambda w: f"the coal held by {w} at the end of December", LS, reproduce("coal_stocks_dec"), consequence=3),
]
NEWEST = 2024                  # session 8211: a facility or state whose newest year is older (a retired plant) is not read


# Sequoyah (6152) and McGuire (6038) are chain 164's drafts of reactor outage days (reactor-outage-days-nuc-6152-2, -6038-1)
SKIP = {"nucf_6152", "nucf_6038"}


def _recent(fn):
    def f(in_dir=None):
        got = fn(in_dir)
        got["rows"] = [r for r in got["rows"] if r["region"] not in SKIP]
        last = {}
        for r in got["rows"]:
            last[r["region"]] = max(last.get(r["region"], 0), r["year"])
        got["rows"] = [r for r in got["rows"] if last[r["region"]] >= NEWEST]
        return got
    return f


for _P in CANDIDATES:
    _P["_fn"] = _recent(_P["_fn"])
    _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = {"nuc_out_mean": 1, "nuc_out_peak": 1, "nuc_out_share": 4, "coal_stocks_dec": 5}[_P["name"]]
    if _P["name"] == "coal_stocks_dec":
        _P["rank_region"] = lambda r: 1e9 if r == "cst_us" else 0.0


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, markets_operations")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=11)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("ops502", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
