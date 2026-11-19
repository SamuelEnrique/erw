#!/usr/bin/env python3
"""The findings hunt of chain 502, family "trade": who sends power to whom, session 8201.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Descriptive only (the chain
file's rule: the donor grids paper is Samuel's own work): who sends to whom, how much, when, and how that changed. No
regression on weather, no share of a shock covered by imports, no ledger of donors and takers.

Candidates, each a figure a year for each pair, region or tie (hourly EIA-930 rows, public):
    pair_flow             the mean hourly flow between two of EIA's regions, read in its standing direction
    pair_against          the share of the year's hours the pair's flow ran against its standing direction
    pair_against_summer   the same, June to August
    pair_against_winter   the same, January, February and December
    pair_side_gap         the mean absolute difference between the two regions' reports of the hour's flow
    region_net            a region's net exports (or net imports) as a percent of its demand
    region_against        the share of the year's hours a standing exporter imported, or a standing importer exported
    tie_flow              the mean hourly flow on a tie between two balancing authorities, in its standing direction
    tie_side_gap          the mean absolute difference between the two balancing authorities' reports on their tie

The standing direction of a pair or tie is the sign of its mean flow over the full years 2019 to 2025. A pair or tie is
drafted from one side's figures only when the other side, where it reports at least 90 percent of the hours of both
end years, moved the same way by between half and twice as much (else the two sides' gap is the finding, not the flow).

    python warehouse/analysis/findings/deep/trade.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/trade.py --load
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hourly930 as h  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "trade"
FULL = list(range(2019, 2026))
END = (2019, 2025)
MIN_TIE_MW = 300.0             # a tie is read when its mean absolute flow over the full years is at least this
SUMMER, WINTER = (6, 7, 8), (1, 2, 12)
EXCLUDED = []                  # (what, key, why): printed by main()


def _sgn(x):
    return 1.0 if x >= 0 else -1.0


def _side_ok(c_main, c_other):
    if c_other is None:
        return True
    if c_main == 0 or c_other == 0 or np.sign(c_main) != np.sign(c_other):
        return False
    r = abs(c_main) / abs(c_other)
    return 0.5 <= r <= 2.0


# ---------------------------------------------------------------------------------------------------------------------
# region pairs
# ---------------------------------------------------------------------------------------------------------------------
def pair_frame(in_dir):
    """Each pair's hours after the fault rule on value, with its standing sign and its key and words; pairs whose sides
    disagree on the change are left out (EXCLUDED)."""
    def build():
        d = h.pairs(in_dir)
        v = h.drop_flow_faults(d[["pair", "year", "month", "ts_utc", "value"]].copy(), "value", ["pair", "year"])
        out = []
        for pair, g in v.groupby("pair"):
            a, b = pair.split("-")
            s = _sgn(g[g["year"].isin(FULL)]["value"].mean())
            sides = {}
            for col in ("x_first_report", "x_second_report"):
                x = d[d["pair"] == pair][["year", col]].dropna()
                x = h.drop_flow_faults(x, col, ["year"])
                n = x.groupby("year")[col].size()
                m = x.groupby("year")[col].mean()
                full = all(n.get(y, 0) >= 0.9 * 8760 for y in END)
                sides[col] = (m.get(END[1], np.nan) - m.get(END[0], np.nan)) if full else None
            main = g.groupby("year")["value"].mean()
            c_main = main.get(END[1], np.nan) - main.get(END[0], np.nan)
            held = [c for c in sides.values() if c is not None]
            if len(held) == 2 and not _side_ok(held[0], held[1]):
                EXCLUDED.append(("pair", pair, f"the two sides moved apart from {END[0]} to {END[1]}: {held[0]:.0f} and {held[1]:.0f} MW"))
                continue
            if np.isnan(c_main):
                continue
            exp, imp = (a, b) if s > 0 else (b, a)
            g = g.copy()
            g["v"] = g["value"] * s
            g["key"] = f"rp_{exp.lower()}_{imp.lower()}"
            g["words"] = f"{h.REG[exp]} to {h.REG[imp]}"
            g["sign"] = s
            out.append(g)
        return pd.concat(out, ignore_index=True)
    return hm._cached(("c502_pair_frame", in_dir), build)


def _yearly(d, fn, key="key"):
    rows, tables = [], {}
    for k, g in d.groupby(key):
        words = g["words"].iloc[0]
        for y, s in g.groupby("year"):
            rows.append(hm._row(k, words, y, float(fn(s)), len(s)))
        tables[k] = ["eia930_region_pair_hourly"]
    return {"rows": rows, "tables": tables}


def pair_flow(in_dir=None):
    return _yearly(pair_frame(in_dir), lambda s: s["v"].mean())


def pair_against(in_dir=None):
    return _yearly(pair_frame(in_dir), lambda s: (s["v"] < 0).mean() * 100)


def pair_against_summer(in_dir=None):
    d = pair_frame(in_dir)
    return _yearly(d[d["month"].isin(SUMMER)], lambda s: (s["v"] < 0).mean() * 100)


def pair_against_winter(in_dir=None):
    d = pair_frame(in_dir)
    return _yearly(d[d["month"].isin(WINTER)], lambda s: (s["v"] < 0).mean() * 100)


def pair_side_gap(in_dir=None):
    d = h.pairs(in_dir)
    rows, tables = [], {}
    for pair, g in d.groupby("pair"):
        f = h.drop_flow_faults(g[["ts_utc", "year", "x_first_report"]].dropna(), "x_first_report", ["year"])
        s = h.drop_flow_faults(g[["ts_utc", "year", "x_second_report"]].dropna(), "x_second_report", ["year"])
        w = f.merge(s[["ts_utc", "x_second_report"]], on="ts_utc")
        if not len(w):
            continue
        w["gap"] = (w["x_first_report"] - w["x_second_report"]).abs()
        a, b = pair.split("-")
        k = f"rg_{a.lower()}_{b.lower()}"
        for y, x in w.groupby("year"):
            rows.append(hm._row(k, f"{h.REG[a]} and {h.REG[b]}", y, float(x["gap"].mean()), len(x)))
        tables[k] = ["eia930_region_pair_hourly"]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# regions
# ---------------------------------------------------------------------------------------------------------------------
MANY = 3                       # a region of more than this many authorities is cross-checked against its pairs


def pair_net(in_dir):
    """{region: {year: MW}}: a region's net flow out across its borders as the region pair table holds it, the sum of
    each pair's yearly mean (fault rule applied), None for a region with a pair whose sides moved apart."""
    d = h.drop_flow_faults(h.pairs(in_dir)[["pair", "year", "value"]].copy(), "value", ["pair", "year"])
    m = d.groupby(["pair", "year"])["value"].mean()
    bad = {e[1] for e in EXCLUDED if e[0] == "pair"}
    out = {}
    for code in h.REGIONS:
        mine = [p for p in m.index.get_level_values(0).unique() if code in p.split("-")]
        if any(p in bad for p in mine):
            out[code] = None
            continue
        tot = {}
        for p in mine:
            sg = 1.0 if p.split("-")[0] == code else -1.0
            for y, v in m[p].items():
                tot[y] = tot.get(y, 0.0) + sg * v
        out[code] = tot
    return out


def region_frame(in_dir):
    """Each region's hours with its total interchange (fault rule), its standing sign, key and words. A region of more
    than MANY authorities (its internal flows cancel only as far as both sides report them alike) is kept only when its
    net flow across its borders by the region pair table moved the same way from 2019 to 2025, by half to twice as much."""
    def build():
        pair_frame(in_dir)                                 # fills EXCLUDED's pairs first
        w = h.region(in_dir).copy()
        w = w.dropna(subset=["total_interchange_mw"])
        w = h.drop_flow_faults(w, "total_interchange_mw", ["code", "year"])
        bas = h.read("eia930_region_hourly", in_dir, ["entity", "variable", "x_bas"], ["x_bas"], keep=lambda c: c["variable"] == "total_interchange_mw")
        bas = bas.groupby(bas["entity"].str.split(":").str[1])["x_bas"].median()
        pn = pair_net(in_dir)
        out = []
        for code, g in w.groupby("code"):
            if bas.get(code, 1) > MANY:
                ti = g.groupby("year")["total_interchange_mw"].mean()
                c_ti = ti.get(END[1], np.nan) - ti.get(END[0], np.nan)
                p = pn.get(code)
                if p is None or np.isnan(c_ti) or END[0] not in p or END[1] not in p or not _side_ok(c_ti, p[END[1]] - p[END[0]]):
                    EXCLUDED.append(("region", code, f"{int(bas.get(code))} authorities; total interchange moved {c_ti:.0f} MW from {END[0]} to {END[1]}, "
                                     f"the border flows by the pair table {'cannot be summed (a pair whose sides moved apart)' if p is None else f'{p.get(END[1], np.nan) - p.get(END[0], np.nan):.0f} MW'}"))
                    continue
            s = _sgn(g[g["year"].isin(FULL)]["total_interchange_mw"].mean())
            g = g.copy()
            g["v"] = g["total_interchange_mw"] * s
            g["sign"] = s
            g["key"] = f"rn_{code.lower()}"
            g["words"] = f"{h.REG[code]} (EIA's region), a net {'exporter' if s > 0 else 'importer'} over 2019 to 2025"
            out.append(g)
        return pd.concat(out, ignore_index=True)
    return hm._cached(("c502_region_frame", in_dir), build)


def region_net(in_dir=None):
    """Net exports (or imports) over demand: total interchange from the region table, demand summed from the
    authorities' table (hourly930.region_demand), hours both are held."""
    dem = h.region_demand(in_dir)[["code", "ts_utc", "demand_mw"]]
    d = region_frame(in_dir).drop(columns=["demand_mw"], errors="ignore").merge(dem, on=["code", "ts_utc"])
    rows, tables = [], {}
    for k, g in d.groupby("key"):
        for y, s in g.groupby("year"):
            rows.append(hm._row(k, g["words"].iloc[0], y, float(s["v"].sum() / s["demand_mw"].sum() * 100), len(s)))
        tables[k] = ["eia930_region_hourly", "eia930_ba_demand_hourly"]
    return {"rows": rows, "tables": tables}


def region_against(in_dir=None):
    d = region_frame(in_dir)
    rows, tables = [], {}
    for k, g in d.groupby("key"):
        for y, s in g.groupby("year"):
            rows.append(hm._row(k, g["words"].iloc[0], y, float((s["v"] < 0).mean() * 100), len(s)))
        tables[k] = ["eia930_region_hourly"]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# ties between balancing authorities
# ---------------------------------------------------------------------------------------------------------------------
def tie_frame(in_dir):
    """Per tie: the side read (the one with more hours over the full years), its standing sign, its yearly figures."""
    def build():
        t = h.ties(in_dir)
        out = []
        for (a, b), g in t.groupby(["a", "b"]):
            full = g[g["year"].isin(FULL)]
            if not len(full):
                continue
            n_side = full.groupby("side")["n"].sum()
            side = n_side.idxmax()
            gs = g[g["side"] == side].set_index("year")
            fs = gs.loc[gs.index.isin(FULL)]
            mean_all = (fs["mean"] * fs["n"]).sum() / fs["n"].sum()
            if abs(mean_all) < MIN_TIE_MW:
                continue
            s = _sgn(mean_all)
            other = g[g["side"] != side].set_index("year")
            c_main = gs["mean"].get(END[1], np.nan) - gs["mean"].get(END[0], np.nan)
            c_other = None
            if len(other) and all(other["n"].get(y, 0) >= 0.9 * 8760 for y in END):
                c_other = other["mean"].get(END[1]) - other["mean"].get(END[0])
            if np.isnan(c_main):
                continue
            if not _side_ok(c_main, c_other):
                EXCLUDED.append(("tie", f"{a}-{b}", f"the two sides moved apart from {END[0]} to {END[1]}: {c_main:.0f} and {c_other:.0f} MW"))
                continue
            exp, imp = (a, b) if s > 0 else (b, a)
            rep, nbr = (a, b) if side == "lo" else (b, a)
            for y, r in gs.iterrows():
                v = r["mean"] * s
                against = (r["neg"] if s > 0 else r["pos"]) / r["n"] * 100
                out.append({"key": f"bt_{exp.lower()}_{imp.lower()}", "words": f"{h.ba_words(exp)} ({exp}) to {h.ba_words(imp)} ({imp})",
                            "year": int(y), "v": v, "against": against, "n": r["n"], "rep": rep, "nbr": nbr, "exp": exp})
        return pd.DataFrame(out)
    return hm._cached(("c502_tie_frame", in_dir), build)


def tie_flow(in_dir=None):
    d = tie_frame(in_dir)
    rows = [hm._row(r["key"], r["words"], r["year"], float(r["v"]), r["n"]) for _, r in d.iterrows()]
    return {"rows": rows, "tables": {k: [f"eia930_ba_interchange_hourly_{y}" for y in h.YEARS] for k in d["key"].unique()}}


def tie_side_gap(in_dir=None):
    t = h.ties(in_dir)
    t = t[t["side"] == "lo"].dropna(subset=["gap"])
    flows = h.ties(in_dir)
    big = flows[flows["year"].isin(FULL)].groupby(["a", "b"]).apply(lambda g: (g["mean"].abs() * g["n"]).sum() / g["n"].sum())
    rows, tables = [], {}
    for _, r in t.iterrows():
        if big.get((r["a"], r["b"]), 0) < MIN_TIE_MW:
            continue
        k = f"bg_{r['a'].lower()}_{r['b'].lower()}"
        rows.append(hm._row(k, f"{h.ba_words(r['a'])} ({r['a']}) and {h.ba_words(r['b'])} ({r['b']})", r["year"], float(r["gap"]), r["n_both"]))
        tables[k] = [f"eia930_ba_interchange_hourly_{y}" for y in h.YEARS]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
def _pair_of(region):
    _, x, y = region.split("_")
    x, y = x.upper(), y.upper()
    first, second = sorted([x, y], key=lambda c: c)  # EIA's order is alphabetical by code in this table
    return first, second, (1 if x == first else -1)


def _tie_of(region, in_dir=None):
    _, exp, imp = region.split("_")
    d = tie_frame(in_dir)
    r = d[d["key"] == region].iloc[0]
    return r["rep"], r["nbr"], (1 if r["rep"] == r["exp"] else -1)


MEASURE_PY = {"mean": "s['v'].mean()", "against": "(s['v'] < 0).mean() * 100"}


def reproduce_py(name, region):
    if name.startswith("pair_") and name != "pair_side_gap":
        first, second, sg = _pair_of(region)
        months = {"pair_against_summer": SUMMER, "pair_against_winter": WINTER}.get(name)
        m = MEASURE_PY["mean" if name == "pair_flow" else "against"]
        body = (f"d = read(sys.argv[1], ['entity', 'ts_utc', 'value'])\nd = d[d['entity'] == 'eia930:{first}-{second}'].copy()\n"
                f"d['v'] = pd.to_numeric(d['value'], errors='coerce') * {sg}\nd = d.dropna(subset=['v'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\n"
                "d = drop_flow_faults(d, 'v', ['year'])\n")
        if months:
            body += f"d = d[d['ts_utc'].str[5:7].astype(int).isin({list(months)})]\n"
        body += f"for y, s in d.groupby('year'):\n    print(y, round(float({m}), 6), len(s))\n"
        what = {"pair_flow": "The year's mean hourly flow", "pair_against": "The share of the year's hours (percent) with the flow"}.get(name, "The share of the season's hours (percent) with the flow")
        what += f" from {h.REG[first] if sg > 0 else h.REG[second]} to {h.REG[second] if sg > 0 else h.REG[first]}" + (" below zero (against its standing direction)." if name != "pair_flow" else " (MW).")
        return h.py_doc(name, region, ["eia930_region_pair_hourly"], what) + h.PY_READ + body
    if name == "pair_side_gap":
        _, a, b = region.split("_")
        body = (f"d = read(sys.argv[1], ['entity', 'ts_utc', 'x_first_report', 'x_second_report'])\nd = d[d['entity'] == 'eia930:{a.upper()}-{b.upper()}'].copy()\n"
                "d['year'] = d['ts_utc'].str[:4].astype(int)\nsides = []\nfor col in ('x_first_report', 'x_second_report'):\n"
                "    x = d[['ts_utc', 'year', col]].copy()\n    x[col] = pd.to_numeric(x[col], errors='coerce')\n    x = drop_flow_faults(x.dropna(subset=[col]), col, ['year'])\n"
                "    sides.append(x)\nw = sides[0].merge(sides[1][['ts_utc', 'x_second_report']], on='ts_utc')\nw['gap'] = (w['x_first_report'] - w['x_second_report']).abs()\n"
                "for y, s in w.groupby('year'):\n    print(y, round(float(s['gap'].mean()), 6), len(s))\n")
        return h.py_doc(name, region, ["eia930_region_pair_hourly"], "The year's mean absolute difference (MW) between the two regions' reports of the hour's flow, hours both sides hold.") + h.PY_READ + body
    if name in ("region_net", "region_against"):
        code = region.split("_")[1].upper()
        sg = int(region_frame(_in()).query("key == @region")["sign"].iloc[0])
        body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == 'eia930:{code}') & (d['variable'] == 'total_interchange_mw')].copy()\n"
                "d['ti'] = pd.to_numeric(d['value'], errors='coerce')\nw = d.dropna(subset=['ti'])[['ts_utc', 'ti']].copy()\n"
                "w['year'] = w['ts_utc'].str[:4].astype(int)\nw = drop_flow_faults(w, 'ti', ['year'])\n"
                f"w['v'] = w['ti'] * {sg}\n")
        if name == "region_net":
            body += (f"w = w.merge(region_demand(sys.argv[2], '{code}')[['ts_utc', 'demand_mw']], on='ts_utc')\n"
                     "for y, s in w.groupby('year'):\n    print(y, round(float(s['v'].sum() / s['demand_mw'].sum() * 100), 6), len(s))\n")
            what = (f"The year's net {'exports' if sg > 0 else 'imports'} of {h.REG[code]} as a percent of its demand: total interchange from the region table over the "
                    "demand of the region's authorities summed by hour, hours both are held.")
            return h.py_doc(name, region, ["eia930_region_hourly", "eia930_ba_demand_hourly"], what) + h.PY_READ + h.PY_REGION_DEMAND + body
        body += "for y, s in w.groupby('year'):\n    print(y, round(float((s['v'] < 0).mean() * 100), 6), len(s))\n"
        what = f"The share of the year's hours (percent) in which {h.REG[code]}, a net {'exporter' if sg > 0 else 'importer'} over 2019 to 2025, {'imported' if sg > 0 else 'exported'}."
        return h.py_doc(name, region, ["eia930_region_hourly"], what) + h.PY_READ + body
    tables = [f"eia930_ba_interchange_hourly_{y}" for y in h.YEARS]
    if name == "tie_flow":
        rep, nbr, sg = _tie_of(region, _in())
        body = (f"d = pd.concat([read(p, ['entity', 'ts_utc', 'value']) for p in sys.argv[1:]], ignore_index=True)\nd = d[d['entity'] == 'eia930:{rep}-{nbr}'].copy()\n"
                f"d['v'] = pd.to_numeric(d['value'], errors='coerce') * {sg}\nd = d.dropna(subset=['v'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\n"
                "d = drop_flow_faults(d, 'v', ['year'])\nfor y, s in d.groupby('year'):\n    print(y, round(float(s['v'].mean()), 6), len(s))\n")
        return h.py_doc(name, region, tables, f"The year's mean hourly flow on the tie (MW), as {rep} filed it, read from {'its' if sg > 0 else 'the neighbour'} side to the other.") + h.PY_READ + body
    _, a, b = region.split("_")
    a, b = a.upper(), b.upper()
    body = (f"d = pd.concat([read(p, ['entity', 'ts_utc', 'value']) for p in sys.argv[1:]], ignore_index=True)\n"
            f"d = d[d['entity'].isin(['eia930:{a}-{b}', 'eia930:{b}-{a}'])].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
            f"d['v'] = np.where(d['entity'] == 'eia930:{a}-{b}', d['value'], -d['value'])\nd['side'] = d['entity']\nd = d.dropna(subset=['v'])\n"
            "d['year'] = d['ts_utc'].str[:4].astype(int)\nd = drop_flow_faults(d, 'v', ['side', 'year'])\n"
            "w = d.pivot_table(index=['ts_utc', 'year'], columns='side', values='v', aggfunc='first').dropna().reset_index()\n"
            f"w['gap'] = (w['eia930:{a}-{b}'] - w['eia930:{b}-{a}']).abs()\nfor y, s in w.groupby('year'):\n    print(y, round(float(s['gap'].mean()), 6), len(s))\n")
    return h.py_doc(name, region, tables, f"The year's mean absolute difference (MW) between {a}'s and {b}'s reports on their tie, hours both hold, each read as power from {a} to {b}.") + h.PY_READ + body


def reproduce_do(name, region):
    if name.startswith("pair_") and name != "pair_side_gap":
        first, second, sg = _pair_of(region)
        lines = h.do_head(name, region, ["eia930_region_pair_hourly"]) + ['import delimited "eia930_region_pair_hourly.csv", varnames(1) stringcols(_all) clear',
                                                                          f'keep if entity == "eia930:{first}-{second}"', "keep ts_utc value", "destring value, replace force",
                                                                          "drop if missing(value)", f"generate double v = value * {sg}", "generate int year = real(substr(ts_utc, 1, 4))"]
        lines += h.do_flow_faults("v")
        if name == "pair_against_summer":
            lines += ["generate int month = real(substr(ts_utc, 6, 2))", "keep if month == 6 | month == 7 | month == 8"]
        if name == "pair_against_winter":
            lines += ["generate int month = real(substr(ts_utc, 6, 2))", "keep if month == 1 | month == 2 | month == 12"]
        if name == "pair_flow":
            lines += ["collapse (mean) measure = v (count) n = v, by(year)"]
        else:
            lines += ["generate double against = 100 * (v < 0)", "collapse (mean) measure = against (count) n = v, by(year)"]
    elif name == "pair_side_gap":
        _, a, b = region.split("_")
        lines = h.do_head(name, region, ["eia930_region_pair_hourly"]) + ['import delimited "eia930_region_pair_hourly.csv", varnames(1) stringcols(_all) clear',
                                                                          f'keep if entity == "eia930:{a.upper()}-{b.upper()}"', "keep ts_utc x_first_report x_second_report",
                                                                          "destring x_first_report x_second_report, replace force", "generate int year = real(substr(ts_utc, 1, 4))",
                                                                          "generate double absfirst = abs(x_first_report)", "bysort year: egen double p99first = pctile(absfirst), p(99)",
                                                                          "replace x_first_report = . if absfirst > 3 * p99first", "generate double abssecond = abs(x_second_report)",
                                                                          "bysort year: egen double p99second = pctile(abssecond), p(99)", "replace x_second_report = . if abssecond > 3 * p99second",
                                                                          "drop if missing(x_first_report) | missing(x_second_report)", "generate double gap = abs(x_first_report - x_second_report)",
                                                                          "collapse (mean) measure = gap (count) n = gap, by(year)"]
    elif name in ("region_net", "region_against"):
        code = region.split("_")[1].upper()
        sg = int(region_frame(_in()).query("key == @region")["sign"].iloc[0])
        tabs = ["eia930_region_hourly", "eia930_ba_demand_hourly"] if name == "region_net" else ["eia930_region_hourly"]
        lines = h.do_head(name, region, tabs)
        if name == "region_net":
            lines += h.do_region_demand(code) + ["drop year", "tempfile dem", "save `dem'"]
        lines += ['import delimited "eia930_region_hourly.csv", varnames(1) stringcols(_all) clear',
                  f'keep if entity == "eia930:{code}" & variable == "total_interchange_mw"', "keep ts_utc value", "destring value, replace force", "rename value ti",
                  "drop if missing(ti)", "generate int year = real(substr(ts_utc, 1, 4))"]
        lines += h.do_flow_faults("ti") + [f"generate double v = ti * {sg}"]
        if name == "region_net":
            lines += ["merge 1:1 ts_utc using `dem', keep(match) nogenerate",
                      "collapse (sum) v = v (sum) demand = demand (count) n = v, by(year)", "generate double measure = 100 * v / demand"]
        else:
            lines += ["generate double against = 100 * (v < 0)", "collapse (mean) measure = against (count) n = v, by(year)"]
    else:
        tables = [f"eia930_ba_interchange_hourly_{y}" for y in h.YEARS]
        if name == "tie_flow":
            rep, nbr, sg = _tie_of(region, _in())
            keep = f'keep if entity == "eia930:{rep}-{nbr}"'
        else:
            _, a, b = region.split("_")
            a, b = a.upper(), b.upper()
            keep = f'keep if entity == "eia930:{a}-{b}" | entity == "eia930:{b}-{a}"'
        lines = h.do_head(name, region, tables) + ["tempfile all", "save `all', emptyok",
                                                   [f"foreach y of numlist {h.YEARS[0]}/{h.YEARS[-1]} {{", 'import delimited "eia930_ba_interchange_hourly_`y\'.csv", varnames(1) stringcols(_all) clear',
                                                    keep, "keep entity ts_utc value", "append using `all'", "save `all', replace", "}"],
                                                   "use `all', clear", "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))"]
        if name == "tie_flow":
            lines += [f"generate double v = value * {sg}"] + h.do_flow_faults("v") + ["collapse (mean) measure = v (count) n = v, by(year)"]
        else:
            lines += [f'generate double v = cond(entity == "eia930:{a}-{b}", value, -value)', f'generate str1 side = cond(entity == "eia930:{a}-{b}", "a", "b")']
            lines += h.do_flow_faults("v", by="side year") + ["keep ts_utc year side v", "reshape wide v, i(ts_utc year) j(side) string", "drop if missing(va) | missing(vb)",
                                                              "generate double gap = abs(va - vb)", "collapse (mean) measure = gap (count) n = gap, by(year)"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


CTX = {}


def _in():
    return CTX.get("in_dir") or common.DEFAULT_IN_DIR


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L930 = "EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years"
CANDIDATES = [
    C("pair_flow", FAMILY, pair_flow, "MW", 0, 8000, 100.0, "WHO SENDS POWER TO WHOM",
      "the mean hourly flow between two of EIA's regions, in its standing direction over 2019 to 2025",
      lambda w: f"the mean hourly flow of power from {w} (EIA's regions)",
      L930 + "; a mean of the hours held, not a metered annual total.", reproduce("pair_flow"), consequence=3),
    C("region_net", FAMILY, region_net, "percent", 1, 8000, 1.0, "NET EXPORTS AND IMPORTS BY REGION",
      "a region's net exports (or net imports, for a net importer) as a percent of its demand",
      lambda w: f"the year's net {'exports' if 'exporter' in w else 'imports'} of {w.split(' (')[0]} (EIA's region) as a share of its demand",
      L930 + "; flows between two authorities of one region cancel only as far as both report them alike; a negative figure is a year the region traded the other way on net; "
      "demand is summed from the region's authorities that file it.", reproduce("region_net"), consequence=3),
    C("tie_flow", FAMILY, tie_flow, "MW", 0, 8000, 100.0, "THE LARGEST TIES BETWEEN BALANCING AUTHORITIES",
      "the mean hourly flow on a tie between two balancing authorities, in its standing direction over 2019 to 2025",
      lambda w: f"the mean hourly flow of power from {w}",
      "EIA-930 as one of the two authorities filed it; a tie is read when its mean flow is at least 300 MW, and its other side moved the same way.",
      reproduce("tie_flow"), consequence=3),
    C("pair_against", FAMILY, pair_against, "percent of hours", 1, 8000, 3.0, "HOURS A FLOW RUNS THE OTHER WAY",
      "the share of the year's hours a pair's flow ran against its standing direction",
      lambda w: f"the share of the year's hours in which power flowed the other way to its usual direction, from {w}",
      L930 + "; an hour at exactly zero counts as neither way.", reproduce("pair_against"), consequence=2),
    C("pair_against_summer", FAMILY, pair_against_summer, "percent of hours", 1, 2000, 3.0, "SUMMER HOURS A FLOW RUNS THE OTHER WAY",
      "the share of June to August hours a pair's flow ran against its standing direction",
      lambda w: f"the share of June to August hours in which power flowed the other way to its usual direction, from {w}",
      L930 + "; months are UTC months.", reproduce("pair_against_summer"), consequence=2),
    C("pair_against_winter", FAMILY, pair_against_winter, "percent of hours", 1, 2000, 3.0, "WINTER HOURS A FLOW RUNS THE OTHER WAY",
      "the share of January, February and December hours a pair's flow ran against its standing direction",
      lambda w: f"the share of January, February and December hours in which power flowed the other way to its usual direction, from {w}",
      L930 + "; months are UTC months, and a year's winter is its own January, February and December.", reproduce("pair_against_winter"), consequence=2),
    C("region_against", FAMILY, region_against, "percent of hours", 1, 8000, 3.0, "HOURS A REGION TRADES THE OTHER WAY",
      "the share of the year's hours a standing exporter imported, or a standing importer exported",
      lambda w: f"the share of the year's hours in which {w.split(' (')[0]}, {w.split('), ')[1]}, {'imported' if 'exporter' in w else 'exported'} on net",
      L930 + ".", reproduce("region_against"), consequence=2),
    C("pair_side_gap", FAMILY, pair_side_gap, "MW", 0, 8000, 50.0, "WHERE THE TWO SIDES' REPORTS DISAGREE",
      "the mean absolute difference between the two regions' reports of the hour's flow",
      lambda w: f"the mean absolute difference between the reports of {w} on the hour's flow between them",
      "Each side summed from its balancing authorities' reports on the ties between the two regions, hours both sides hold; which side is right is not known from these rows.",
      reproduce("pair_side_gap"), consequence=2),
    C("tie_side_gap", FAMILY, tie_side_gap, "MW", 0, 8000, 50.0, "WHERE TWO AUTHORITIES' REPORTS ON A TIE DISAGREE",
      "the mean absolute difference between the two balancing authorities' reports on their tie",
      lambda w: f"the mean absolute difference between the reports of {w} on their tie",
      "EIA-930 as each authority filed it, hours both hold, ties with a mean flow of at least 300 MW; which side is right is not known from these rows.",
      reproduce("tie_side_gap"), consequence=2),
]
# session 8201: one story is drafted once. A pair keeps its flow and at most one measure of the hours it runs the other
# way (the season where the change is largest); a tie whose region pair tells the same story is folded into the pair's
# draft (Hydro-Quebec to ISO New England is most of Canada to New England); a draft whose change is a reporting fix of a
# few MW is left out.
SKIP = {("pair_against", "rp_can_midw"), ("pair_against_summer", "rp_can_midw"), ("pair_against", "rp_can_ny"), ("pair_against_winter", "rp_can_ny"),
        ("pair_against_summer", "rp_can_ne"), ("pair_against_winter", "rp_can_ne"), ("pair_against_summer", "rp_cent_nw"), ("pair_against_winter", "rp_cent_nw"),
        ("pair_against", "rp_se_car"), ("pair_against_winter", "rp_se_car"), ("pair_against_winter", "rp_midw_ten"), ("pair_against", "rp_midw_ten"),
        ("pair_against_summer", "rp_cent_midw"), ("pair_against_winter", "rp_cent_midw"), ("pair_against_summer", "rp_cent_sw"), ("pair_against", "rp_cent_sw"),
        ("pair_against_winter", "rp_ten_car"), ("tie_flow", "bt_hqt_isne"), ("pair_side_gap", "rg_cal_nw"), ("pair_side_gap", "rg_car_se"),
        ("tie_side_gap", "bg_psco_wacm")}
NEG = " A negative mean is a year power flowed the other way on balance."
for _P in CANDIDATES:
    if _P["unit"] == "MW" or _P["name"] == "region_net":
        _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = {"pair_flow": 8, "region_net": 6, "tie_flow": 8}.get(_P["name"], 4)
    if _P["name"] in ("pair_flow", "tie_flow"):
        _P["limits"] = _P["limits"] + NEG

    def _wrap(fn, name):
        def f(in_dir=None):
            got = fn(in_dir)
            got["rows"] = [r for r in got["rows"] if (name, r["region"]) not in SKIP]
            return got
        return f
    _P["_fn"] = _wrap(_P["_fn"], _P["name"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, family trade")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--max-drafts", type=int, default=24)
    ap.add_argument("--replace", action="store_true", help="correct this family's open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    cands = [P for P in CANDIDATES if not a.only or P["name"] in a.only.split(",")]
    builder.run(FAMILY, cands, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts, replace=a.replace)
    for e in EXCLUDED:
        print("left out:", *e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
