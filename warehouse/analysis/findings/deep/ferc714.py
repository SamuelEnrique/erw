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
AHEAD = 5                      # session 8219: the revision of the forecast of the year five ahead


def _revision(name):
    var = VAR[name.replace("_revision", "_growth")][0]

    def f(in_dir=None):
        d = forecasts(in_dir)
        d = d[d["variable"] == var]
        v = d.set_index(["entity", "ry", "fy"])["value"]
        s = forecasts(in_dir)
        s = s[s["variable"] == "summer_peak_forecast_mw"]
        newest = s[s["ry"] == s.groupby("entity")["ry"].transform("max")]
        big = set(newest[newest["fy"] == newest["ry"] + 1].query("value >= @MIN_MW")["entity"])
        big &= set(s.groupby("entity")["ry"].max().loc[lambda x: x >= NEWEST].index)
        nm = names(in_dir)
        rows, tabs = [], {}
        for (e, ry, fy), val in v.items():
            if e not in big or fy != ry + AHEAD:
                continue
            prev = v.get((e, ry - 1, fy))
            if prev is None or prev <= 0 or not (0.5 <= val / prev <= 2.0):
                continue
            k = f"pa_{e.split(':')[1]}"
            rows.append(hm._row(k, f"{nm.get(e, e)} (FERC 714 planning area {e.split(':')[1]})", int(ry), float((val / prev - 1) * 100), 1))
            tabs[k] = ["ferc714_planning_area_forecasts"]
        return {"rows": rows, "tables": tabs}
    return f


summer_revision, energy_revision = _revision("summer_revision"), _revision("energy_revision")


def reproduce_py(name, region):
    if name.endswith("_revision"):
        var = VAR[name.replace("_revision", "_growth")][0]
        e = "ferc714:" + region.split("_", 1)[1]
        body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value', 'x_report_year'])\nd = d[(d['entity'] == '{e}') & (d['variable'] == '{var}')].copy()\n"
                "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nd['ry'] = pd.to_numeric(d['x_report_year'], errors='coerce')\nd = d.dropna(subset=['value', 'ry'])\n"
                "d['fy'], d['ry'] = d['ts_utc'].str[:4].astype(int), d['ry'].astype(int)\nd = d.drop_duplicates(['fy', 'ry'])\nv = d.set_index(['ry', 'fy'])['value']\n"
                f"for ry in sorted(d['ry'].unique()):\n    a, b = v.get((ry, ry + {AHEAD})), v.get((ry - 1, ry + {AHEAD}))\n"
                "    if a is None or b is None or b <= 0 or not (0.5 <= a / b <= 2.0):\n        continue\n    print(ry, round(float((a / b - 1) * 100), 6), 1)\n")
        return h.py_doc(name, region, ["ferc714_planning_area_forecasts"],
                        f"For each filing (report year R): its forecast of the {VAR[name.replace('_revision', '_growth')][1]} of year R+{AHEAD} against the filing of R-1's forecast of the same year, percent.") + h.PY_READ + body
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
    if name.endswith("_revision"):
        var = VAR[name.replace("_revision", "_growth")][0]
        e = "ferc714:" + region.split("_", 1)[1]
        lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table ferc714_planning_area_forecasts.",
                 "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
                 "clear all", 'import delimited "ferc714_planning_area_forecasts.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{e}" & variable == "{var}"',
                 "keep ts_utc value x_report_year", "destring value x_report_year, replace force", "drop if missing(value) | missing(x_report_year)",
                 "generate int fy = real(substr(ts_utc, 1, 4))", "rename x_report_year ry", "duplicates drop fy ry, force", "preserve", "rename value prev", "replace ry = ry + 1",
                 "tempfile p", "save `p'", "restore", "merge 1:1 ry fy using `p', keep(match) nogenerate", f"keep if fy == ry + {AHEAD}",
                 "keep if prev > 0 & value / prev >= 0.5 & value / prev <= 2", "generate double measure = (value / prev - 1) * 100", "rename ry year", "generate byte n = 1",
                 "sort year", "list year measure n, noobs"]
        return common.do_file(lines)
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
LR = ("The planning area's own forecast as filed in FERC Form 714 (through PUDL): each filing against the one a year before, for the same year "
      f"{AHEAD} years after the filing; a revision of more than double or less than half is left out (a figure in the wrong unit).")
REVISIONS = [
    C(n, FAMILY, fn, "percent", 1, 1, 2.0, f"HOW A UTILITY REVISES ITS FORECAST: {VAR[n.replace('_revision', '_growth')][1].upper()}",
      f"how much a filing changed its forecast of the year {AHEAD} ahead against the filing a year before",
      (lambda wd: (lambda w: f"the revision {w} made to its forecast of its {wd} {AHEAD} years ahead, against its filing of the year before,"))(VAR[n.replace("_revision", "_growth")][1]),
      LR, reproduce(n), consequence=3, first_words="the first filing that can be compared")
    for n, fn in (("summer_revision", summer_revision), ("energy_revision", energy_revision))
]
for _P in CANDIDATES + REVISIONS:
    _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = 6


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, family forecasts (FERC 714)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=18)
    ap.add_argument("--replace", action="store_true")
    ap.add_argument("--revisions", action="store_true", help="session 8219: only the revisions")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run(FAMILY + ("_revisions" if a.revisions else ""), REVISIONS if a.revisions else CANDIDATES, CTX["in_dir"], dry_run=not a.load,
                max_drafts=a.max_drafts, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
