#!/usr/bin/env python3
"""The findings hunt of chain 502, family "forecasts": what the planning areas forecast in their FERC Form 714, session 8207.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table ferc714_planning_area_forecasts
(public; FERC Form 714 Part 3 Schedule 2 through PUDL, docs/methods/ferc714_forecast_growth.md): each planning area's own
forecast, in each year's filing, of its summer peak, winter peak and net energy for the next ten years. The figure a
filing gives here is the growth it forecasts, a year, from its first forecast year to its tenth (nine steps):

    summer_growth / winter_growth / energy_growth    ((the tenth year's figure / the first's) ** (1/9) - 1) * 100

The year of a claim is the filing's report year, so a claim compares the newest filing with the first the ERW holds
(2006). A filing whose tenth year is more than three times or less than half its first is left out (a figure in the
wrong unit, as the method note warns). Planning areas whose first forecast year's summer peak is under 3,000 MW in the
newest filing are not read. Areas overlap (an ISO's forecast holds its members' load): nothing is added across areas.

    python warehouse/analysis/findings/deep/ferc714.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/ferc714.py --load
"""

import argparse
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import hourly930 as h  # noqa: E402  (sets builder.CHAIN to 502)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "forecasts"
MIN_MW = 3000.0
NEWEST = 2024                  # an area whose newest usable filing is older than this is not read
VAR = {"summer_growth": ("summer_peak_forecast_mw", "summer peak"), "winter_growth": ("winter_peak_forecast_mw", "winter peak"),
       "energy_growth": ("net_energy_forecast_mwh", "net energy")}
CTX = {}


def names(in_dir):
    r = h.read("ferc714_respondents", in_dir, ["entity_id", "name"], [])
    return dict(zip(r["entity_id"], r["name"]))


def forecasts(in_dir):
    def build():
        d = h.read("ferc714_planning_area_forecasts", in_dir, ["entity", "variable", "ts_utc", "value", "x_report_year"], ["value"])
        d["fy"], d["ry"] = d["ts_utc"].str[:4].astype(int), pd.to_numeric(d["x_report_year"], errors="coerce")
        d = d.dropna(subset=["value", "ry"]).drop_duplicates(["entity", "variable", "fy", "ry"])
        d["ry"] = d["ry"].astype(int)
        return d
    return hm._cached(("c502_ferc714", in_dir), build)


def growth_rows(in_dir, var):
    d = forecasts(in_dir)
    d = d[d["variable"] == var]
    out = []
    for (e, ry), g in d.groupby(["entity", "ry"]):
        v = dict(zip(g["fy"], g["value"]))
        a, b = v.get(ry + 1), v.get(ry + 10)
        if a is None or b is None or a <= 0 or not (0.5 <= b / a <= 3.0):
            continue
        out.append((e, ry, ((b / a) ** (1 / 9) - 1) * 100, a))
    return pd.DataFrame(out, columns=["entity", "ry", "growth", "first"])


def _measure(name):
    var, words_ = VAR[name]

    def f(in_dir=None):
        g = growth_rows(in_dir, var)
        s = forecasts(in_dir)
        s = s[s["variable"] == "summer_peak_forecast_mw"]
        newest = s[s["ry"] == s.groupby("entity")["ry"].transform("max")]
        big = set(newest[newest["fy"] == newest["ry"] + 1].query("value >= @MIN_MW")["entity"])
        recent = set(g.groupby("entity")["ry"].max().loc[lambda x: x >= NEWEST].index)     # session 8207: a claim ends at a recent filing
        big &= recent
        nm = names(in_dir)
        rows, tabs = [], {}
        for e, x in g[g["entity"].isin(big)].groupby("entity"):
            k = f"pa_{e.split(':')[1]}"
            w = f"{nm.get(e, e)} (FERC 714 planning area {e.split(':')[1]})"
            for _, r in x.iterrows():
                rows.append(hm._row(k, w, int(r["ry"]), float(r["growth"]), 1))
            tabs[k] = ["ferc714_planning_area_forecasts"]
        return {"rows": rows, "tables": tabs}
    return f


summer_growth, winter_growth, energy_growth = (_measure(n) for n in VAR)


def reproduce_py(name, region):
    var = VAR[name][0]
    e = "ferc714:" + region.split("_", 1)[1]
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value', 'x_report_year'])\nd = d[(d['entity'] == '{e}') & (d['variable'] == '{var}')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nd['ry'] = pd.to_numeric(d['x_report_year'], errors='coerce')\nd = d.dropna(subset=['value', 'ry'])\n"
            "d['fy'], d['ry'] = d['ts_utc'].str[:4].astype(int), d['ry'].astype(int)\nd = d.drop_duplicates(['fy', 'ry'])\nfor ry, g in d.groupby('ry'):\n"
            "    v = dict(zip(g['fy'], g['value']))\n    a, b = v.get(ry + 1), v.get(ry + 10)\n    if a is None or b is None or a <= 0 or not (0.5 <= b / a <= 3.0):\n        continue\n"
            "    print(ry, round(((b / a) ** (1 / 9) - 1) * 100, 6), 1)\n")
    return h.py_doc(name, region, ["ferc714_planning_area_forecasts"],
                    f"For each filing (report year): the yearly growth it forecasts for the {VAR[name][1]} of {e}, from its first forecast year to its tenth, in percent.") + h.PY_READ + body


def reproduce_do(name, region):
    var = VAR[name][0]
    e = "ferc714:" + region.split("_", 1)[1]
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table ferc714_planning_area_forecasts.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "ferc714_planning_area_forecasts.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{e}" & variable == "{var}"',
             "keep ts_utc value x_report_year", "destring value x_report_year, replace force", "drop if missing(value) | missing(x_report_year)",
             "generate int fy = real(substr(ts_utc, 1, 4))", "rename x_report_year year", "duplicates drop fy year, force",
             "generate double first = value if fy == year + 1", "generate double tenth = value if fy == year + 10",
             "collapse (max) first = first (max) tenth = tenth, by(year)", "drop if missing(first) | missing(tenth) | first <= 0",
             "keep if tenth / first >= 0.5 & tenth / first <= 3", "generate double measure = ((tenth / first) ^ (1 / 9) - 1) * 100", "generate byte n = 1",
             "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LF = ("The planning area's own forecast as filed in FERC Form 714 (through PUDL), not an outcome; a filing's ten years start the year after its report "
      "year; areas overlap, so nothing is added across them; a filing whose tenth year is over three times or under half its first is left out.")
CANDIDATES = [
    C(n, FAMILY, fn, "percent a year", 2, 1, 0.3, f"WHAT A UTILITY FORECASTS: {VAR[n][1].upper()} GROWTH",
      f"the yearly growth a filing forecasts for the area's {VAR[n][1]}, from its first forecast year to its tenth",
      (lambda wd: (lambda w: f"the yearly growth of its {wd} that {w} forecast, from the first year of its filing to the tenth,"))(VAR[n][1]),
      LF, reproduce(n), consequence=3, first_words="the first filing the ERW holds")
    for n, fn in (("summer_growth", summer_growth), ("winter_growth", winter_growth), ("energy_growth", energy_growth))
]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = 6


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, family forecasts (FERC 714)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=18)
    ap.add_argument("--replace", action="store_true")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run(FAMILY, CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
