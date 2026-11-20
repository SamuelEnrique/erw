#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family world_power: France's grid, half-hour by half-hour, session 8225.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table rte_eco2mix_france_halfhourly
(public, RTE's eCO2mix national data, 2020 on, 1.4 million rows; no draft had read it):

    fr_mean_<source>   the year's mean output (MW) of nuclear, wind, solar and gas, and the mean consumption
    fr_nuclear_share   nuclear's share of the year's production (the sum of nuclear, coal, gas, oil, hydro, wind, solar
                       and bioenergy), percent

RTE's physical exchanges are not read: the table does not say which sign is an import.

    python warehouse/analysis/findings/deep/rte502.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/rte502.py --load
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

FAMILY = "world_power"
SOURCES = {"nuclear": "nuclear power", "wind": "wind power", "solar": "solar power", "gas": "gas-fired power", "consumption": "consumption"}
PRODUCTION = ["nuclear", "coal", "gas", "oil", "hydro", "wind", "solar", "bioenergy"]
CTX = {}


def rte(in_dir):
    def build():
        d = h.read("rte_eco2mix_france_halfhourly", in_dir, ["variable", "ts_utc", "value"], ["value"], keep=lambda c: c["variable"].isin(set(SOURCES) | set(PRODUCTION)))
        d = d.dropna(subset=["value"])
        d["year"] = d["ts_utc"].str[:4].astype(int)
        return d
    return hm._cached(("c502_rte", in_dir), build)


def _mean(src):
    def f(in_dir=None):
        d = rte(in_dir)
        d = d[d["variable"] == src]
        rows = [hm._row("fr", "France", int(y), float(s["value"].mean()), len(s)) for y, s in d.groupby("year")]
        return {"rows": rows, "tables": {"fr": ["rte_eco2mix_france_halfhourly"]}}
    return f


def fr_nuclear_share(in_dir=None):
    d = rte(in_dir)
    d = d[d["variable"].isin(PRODUCTION)]
    w = d.pivot_table(index=["ts_utc", "year"], columns="variable", values="value", aggfunc="first").dropna().reset_index()
    rows = [hm._row("fr", "France", int(y), float(s["nuclear"].sum() / s[PRODUCTION].sum().sum() * 100), len(s)) for y, s in w.groupby("year")]
    return {"rows": rows, "tables": {"fr": ["rte_eco2mix_france_halfhourly"]}}


MEANS = {f"fr_mean_{s}": _mean(s) for s in SOURCES}


def reproduce_py(name, region):
    if name == "fr_nuclear_share":
        body = (f"d = read(sys.argv[1], ['variable', 'ts_utc', 'value'])\nprod = {PRODUCTION!r}\nd = d[d['variable'].isin(prod)].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                "w = d.pivot_table(index='ts_utc', columns='variable', values='value', aggfunc='first').dropna().reset_index()\n"
                "for y, s in w.groupby(w['ts_utc'].str[:4]):\n    print(y, round(float(s['nuclear'].sum() / s[prod].sum().sum() * 100), 6), len(s))\n")
        what = "Nuclear's share (percent) of France's production (nuclear, coal, gas, oil, hydro, wind, solar, bioenergy summed), half-hours every source holds."
    else:
        src = name.split("_", 2)[2]
        body = (f"d = read(sys.argv[1], ['variable', 'ts_utc', 'value'])\nd = d[d['variable'] == '{src}'].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                "d = d.dropna(subset=['value'])\nfor y, s in d.groupby(d['ts_utc'].str[:4]):\n    print(y, round(float(s['value'].mean()), 6), len(s))\n")
        what = f"The year's mean {SOURCES[src]} (MW) in France, RTE's half-hours."
    return h.py_doc(name, region, ["rte_eco2mix_france_halfhourly"], what) + h.PY_READ + body


def reproduce_do(name, region):
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table rte_eco2mix_france_halfhourly.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "rte_eco2mix_france_halfhourly.csv", varnames(1) stringcols(_all) clear']
    if name == "fr_nuclear_share":
        cond = " | ".join(f'variable == "{p}"' for p in PRODUCTION)
        lines += [f"keep if {cond}", "keep variable ts_utc value", "destring value, replace force", "reshape wide value, i(ts_utc) j(variable) string",
                  "egen byte nmiss = rowmiss(value*)", "keep if nmiss == 0", "egen double prod = rowtotal(value*)", "generate int year = real(substr(ts_utc, 1, 4))",
                  "collapse (sum) nuc = valuenuclear (sum) prod = prod (count) n = prod, by(year)", "generate double measure = 100 * nuc / prod"]
    else:
        src = name.split("_", 2)[2]
        lines += [f'keep if variable == "{src}"', "keep ts_utc value", "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
                  "collapse (mean) measure = value (count) n = value, by(year)"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = "RTE's eCO2mix national data, final for past years and consolidated or real-time for the latest; mainland France; a mean over the half-hours held."
CANDIDATES = [C(n, FAMILY, fn, "MW", 0, 15000, 300.0, f"FRANCE'S GRID: {SOURCES[n.split('_', 2)[2]].upper()}", f"the year's mean {SOURCES[n.split('_', 2)[2]]}",
                (lambda wd: (lambda w: f"the mean {wd} in {w} over the year"))(SOURCES[n.split("_", 2)[2]]), L, reproduce(n), consequence=2) for n, fn in MEANS.items()]
CANDIDATES.append(C("fr_nuclear_share", FAMILY, fr_nuclear_share, "percent", 1, 15000, 2.0, "FRANCE'S GRID: NUCLEAR'S SHARE", "nuclear's share of France's production",
                    lambda w: f"nuclear's share of the electricity produced in {w}", L + " Production is the eight sources RTE lists, pumping not netted.", reproduce("fr_nuclear_share"), consequence=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, France's grid")
    ap.add_argument("--in-dir", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("rte502", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=6)
    return 0


if __name__ == "__main__":
    sys.exit(main())
