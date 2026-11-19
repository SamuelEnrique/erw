#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family cross_family: the actual year against the forecast made years before, session 8210.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Two families of this chain read
together: what the seven ISO planning areas forecast in FERC Form 714 (ferc714_planning_area_forecasts, family
forecasts) and what EIA-930 then recorded for their balancing authorities (eia930_ba_demand_hourly, family authorities).
The map is the method note's (docs/methods/ferc714_forecast_growth.md, "Cross-check"): CISO 24, ERCO 58, ISNE 76,
NYIS 100, PJM 119, SWPP 146, MISO 203.

    peak_vs_<k>y     the year's actual peak hour (EIA-930, a lone spike dropped as in family authorities) against the
                     higher of the summer and winter peak the area's filing of k years before forecast for that year,
                     in percent above (+) or below (-) the forecast
    energy_vs_<k>y   the year's actual demand (the sum of its hours, MWh, years with 98 percent of their hours) against
                     the net energy the filing of k years before forecast, in percent

k is 3 and 5. EIA-930's demand and FERC 714's net energy for load are not defined alike (losses, the area's footprint), so
a level gap is expected; the claim is how the gap moved.

    python warehouse/analysis/findings/deep/cross502.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/cross502.py --load
"""

import argparse
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import authorities  # noqa: E402
import ferc714  # noqa: E402
import hourly930 as h  # noqa: E402  (sets builder.CHAIN to 502)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "cross_family"
MAP = {"CISO": "24", "ERCO": "58", "ISNE": "76", "NYIS": "100", "PJM": "119", "SWPP": "146", "MISO": "203"}
WORDS = {"CISO": "CAISO", "ERCO": "ERCOT", "ISNE": "ISO New England", "NYIS": "the New York ISO", "PJM": "PJM", "SWPP": "the Southwest Power Pool", "MISO": "MISO"}
CTX = {}


def actual(in_dir):
    def build():
        d = authorities.demand(in_dir)
        d = d[d["ba"].isin(MAP)]
        pk = authorities.despike(d, "demand").groupby(["ba", "year"])["demand"].max()
        en = d.groupby(["ba", "year"])["demand"].agg(["sum", "size"])
        return pk, en
    return hm._cached(("c502_actual", in_dir), build)


def forecast(in_dir, var, k):
    f = ferc714.forecasts(in_dir)
    f = f[f["entity"].isin([f"ferc714:{v}" for v in MAP.values()]) & (f["fy"] - f["ry"] == k)]
    if var == "peak":
        f = f[f["variable"].isin(["summer_peak_forecast_mw", "winter_peak_forecast_mw"])].groupby(["entity", "fy"])["value"].max()
    else:
        f = f[f["variable"] == "net_energy_forecast_mwh"].groupby(["entity", "fy"])["value"].first()
    return f


def _measure(var, k):
    def fn(in_dir=None):
        pk, en = actual(in_dir)
        fc = forecast(in_dir, var, k)
        rows, tabs = [], {}
        for ba, pa in MAP.items():
            key = f"x{var[0]}{k}_{ba.lower()}"
            for y in range(2019, 2026):
                fv = fc.get((f"ferc714:{pa}", y))
                if fv is None or fv <= 0:
                    continue
                if var == "peak":
                    av = pk.get((ba, y))
                else:
                    s = en.loc[(ba, y)] if (ba, y) in en.index else None
                    av = s["sum"] if s is not None and s["size"] >= 0.98 * (8784 if y % 4 == 0 else 8760) else None
                if av is None:
                    continue
                if not (0.5 <= av / fv <= 2.0):          # a filing in the wrong unit (the method note warns of them)
                    continue
                rows.append(hm._row(key, f"{WORDS[ba]} ({ba}; FERC 714 planning area {pa})", y, float((av / fv - 1) * 100), 1))
            tabs[key] = ["eia930_ba_demand_hourly", "ferc714_planning_area_forecasts"]
        return {"rows": rows, "tables": tabs}
    return fn


def reproduce_py(name, region):
    var, k = ("peak" if name.startswith("peak") else "energy"), int(name.split("_")[-1][:-1])
    ba = region.split("_")[1].upper()
    pa = MAP[ba]
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == 'eia930:{ba}') & (d['variable'] == 'demand_mw')].copy()\n"
            "d['demand'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['demand'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\nd = d[d['demand'] > 0]\n"
            "d = d[d['demand'] <= 3 * d.groupby('year')['demand'].transform('median')]\n")
    if var == "peak":
        body += ("d['t'] = pd.to_datetime(d['ts_utc'].str[:10]).values.astype('datetime64[D]').astype('int64') * 24 + d['ts_utc'].str[11:13].astype(int)\n"
                 "d = d.sort_values('t')\nprev = d['demand'].shift(1).where(d['t'].shift(1) == d['t'] - 1)\nnxt = d['demand'].shift(-1).where(d['t'].shift(-1) == d['t'] + 1)\n"
                 "d = d[~(d['demand'] > 1.1 * pd.concat([prev, nxt], axis=1).max(axis=1))]\nact = d.groupby('year')['demand'].max()\n")
        fvar = "['summer_peak_forecast_mw', 'winter_peak_forecast_mw']"
        agg = "max"
    else:
        body += "g = d.groupby('year')['demand'].agg(['sum', 'size'])\nact = g[g['size'] >= 0.98 * g.index.map(lambda y: 8784 if y % 4 == 0 else 8760)]['sum']\n"
        fvar = "['net_energy_forecast_mwh']"
        agg = "first"
    body += (f"f = read(sys.argv[2], ['entity', 'variable', 'ts_utc', 'value', 'x_report_year'])\nf = f[(f['entity'] == 'ferc714:{pa}') & f['variable'].isin({fvar})].copy()\n"
             "f['value'] = pd.to_numeric(f['value'], errors='coerce')\nf['ry'] = pd.to_numeric(f['x_report_year'], errors='coerce')\nf = f.dropna(subset=['value', 'ry'])\n"
             "f['fy'] = f['ts_utc'].str[:4].astype(int)\nf = f.drop_duplicates(['variable', 'fy', 'ry'])\n"
             f"fc = f[f['fy'] - f['ry'] == {k}].groupby('fy')['value'].{agg}()\n"
             "for y in range(2019, 2026):\n    if y in act.index and y in fc.index and fc[y] > 0 and 0.5 <= act[y] / fc[y] <= 2.0:\n        print(y, round(float((act[y] / fc[y] - 1) * 100), 6), 1)\n")
    what = (f"For each year 2019 to 2025: {ba}'s actual {'peak hour (a lone spike dropped)' if var == 'peak' else 'demand (the sum of its hours)'} against the "
            f"{'higher of the summer and winter peak' if var == 'peak' else 'net energy'} that planning area {pa}'s filing of {k} years before forecast for it, percent.")
    return h.py_doc(name, region, ["eia930_ba_demand_hourly", "ferc714_planning_area_forecasts"], what) + h.PY_READ + body


def reproduce_do(name, region):
    var, k = ("peak" if name.startswith("peak") else "energy"), int(name.split("_")[-1][:-1])
    ba = region.split("_")[1].upper()
    pa = MAP[ba]
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public tables (eia930_ba_demand_hourly, ferc714_planning_area_forecasts).",
             "* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.",
             "clear all", 'import delimited "ferc714_planning_area_forecasts.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "ferc714:{pa}"']
    if var == "peak":
        lines += ['keep if variable == "summer_peak_forecast_mw" | variable == "winter_peak_forecast_mw"']
    else:
        lines += ['keep if variable == "net_energy_forecast_mwh"']
    lines += ["destring value x_report_year, replace force", "drop if missing(value) | missing(x_report_year)", "generate int year = real(substr(ts_utc, 1, 4))",
              "duplicates drop variable year x_report_year, force", f"keep if year - x_report_year == {k}",
              f"collapse ({'max' if var == 'peak' else 'first'}) fc = value, by(year)", "tempfile fc", "save `fc'",
              'import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia930:{ba}" & variable == "demand_mw"',
              "keep ts_utc value", "destring value, replace force", "rename value demand", "drop if missing(demand) | demand <= 0", "generate int year = real(substr(ts_utc, 1, 4))",
              "bysort year: egen double med = median(demand)", "drop if demand > 3 * med"]
    if var == "peak":
        lines += ["generate double t = date(substr(ts_utc, 1, 10), \"YMD\") * 24 + real(substr(ts_utc, 12, 2))", "sort t",
                  "generate double prev = demand[_n-1] if t[_n-1] == t - 1", "generate double nxt = demand[_n+1] if t[_n+1] == t + 1",
                  "generate double near = max(prev, nxt)", "drop if demand > 1.1 * near & !missing(near)", "collapse (max) act = demand, by(year)"]
    else:
        lines += ["collapse (sum) act = demand (count) hrs = demand, by(year)", "keep if hrs >= 0.98 * cond(mod(year, 4) == 0, 8784, 8760)", "drop hrs"]
    lines += ["merge 1:1 year using `fc', keep(match) nogenerate", "keep if year >= 2019 & year <= 2025 & fc > 0 & act / fc >= 0.5 & act / fc <= 2", "generate double measure = (act / fc - 1) * 100",
              "generate byte n = 1", "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LX = ("FERC 714's forecast as the area filed it and EIA-930's demand as its balancing authority reported it; the two are not defined alike (losses, footprint), "
      "so the level of the gap means less than its move; a lone spike is dropped from the actual peak.")
CANDIDATES = []
for var in ("peak", "energy"):
    for k in (5, 3):
        nm = f"{var}_vs_{k}y"
        CANDIDATES.append(C(nm, FAMILY, _measure(var, k), "percent", 1, 1, 2.0,
                            f"THE ACTUAL YEAR AGAINST THE FORECAST OF {k} YEARS BEFORE: {'PEAK' if var == 'peak' else 'DEMAND'}",
                            f"the year's actual {'peak hour' if var == 'peak' else 'demand'} against what the area's filing of {k} years before forecast, percent",
                            (lambda vv, kk: (lambda w: f"how far the actual {'peak hour' if vv == 'peak' else 'yearly demand'} of {w} ran above (+) or below (-) its own forecast "
                                                       f"for that year, filed {kk} years before,"))(var, k),
                            LX, reproduce(nm), consequence=3, first_words="the first year this measure counts"))
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = 3


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, cross_family")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=12)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("cross502", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
