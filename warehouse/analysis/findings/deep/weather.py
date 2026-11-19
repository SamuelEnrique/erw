#!/usr/bin/env python3
"""The findings hunt of chain 502, family "weather": demand against temperature by region, session 8203.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Described, not modeled: no fit,
no weather adjustment (the /demand page's method is the only model the site holds, and nothing here goes beyond it).
For each of EIA's thirteen regions and each year (public rows):

    cold_mw / hot_mw         the mean demand in the year's 50 coldest (hottest) hours by the region's temperature
    cold_ratio / hot_ratio   the same as a percent of the year's mean hour of demand
    temp_top                 the mean temperature of the year's 100 highest hours of demand
    cold_hours / hot_hours   the hours of the year at or below 20 F (at or above 95 F)

Temperature: region_weather_hourly (each region's stations weighted by county population, docs/methods/region_weather.md).
Demand: the region's authorities summed by hour (hourly930.region_demand). Hours both hold, for the demand measures.

    python warehouse/analysis/findings/deep/weather.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/weather.py --load
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

FAMILY = "weather"
N_EXT = 50
N_TOP = 100
COLD_F, HOT_F = 20.0, 95.0
CTX = {}


def words(code):
    return f"{h.REG[code]} (EIA's region)"


def joined(in_dir):
    def build():
        w = h.weather(in_dir).rename(columns={"value": "temp"}).dropna(subset=["temp"])
        d = h.region_demand(in_dir)[["code", "ts_utc", "year", "demand_mw"]]
        return d.merge(w[["code", "ts_utc", "temp"]], on=["code", "ts_utc"])
    return hm._cached(("c502_weather_joined", in_dir), build)


def _cold(s):
    return s.sort_values(["temp", "ts_utc"]).head(N_EXT)


def _hot(s):
    return s.sort_values(["temp", "ts_utc"], ascending=[False, True]).head(N_EXT)


MEASURES = {"cold_mw": lambda s: _cold(s)["demand_mw"].mean(), "hot_mw": lambda s: _hot(s)["demand_mw"].mean(),
            "cold_ratio": lambda s: _cold(s)["demand_mw"].mean() / s["demand_mw"].mean() * 100,
            "hot_ratio": lambda s: _hot(s)["demand_mw"].mean() / s["demand_mw"].mean() * 100,
            "temp_top": lambda s: s.sort_values(["demand_mw", "ts_utc"], ascending=[False, True]).head(N_TOP)["temp"].mean()}


def _demand_measure(name):
    fn = MEASURES[name]

    def f(in_dir=None):
        d = joined(in_dir)
        rows, tabs = [], {}
        for code, g in d.groupby("code"):
            k = f"wx_{code.lower()}"
            for y, s in g.groupby("year"):
                rows.append(hm._row(k, words(code), y, float(fn(s)), len(s)))
            tabs[k] = ["region_weather_hourly", "eia930_ba_demand_hourly"]
        return {"rows": rows, "tables": tabs}
    return f


def _hours(cold):
    def f(in_dir=None):
        w = h.weather(in_dir).dropna(subset=["value"]).copy()
        w["year"] = w["ts_utc"].str[:4].astype(int)
        rows, tabs = [], {}
        for code, g in w.groupby("code"):
            k = f"wh_{code.lower()}"
            for y, s in g.groupby("year"):
                v = (s["value"] <= COLD_F).sum() if cold else (s["value"] >= HOT_F).sum()
                rows.append(hm._row(k, words(code), y, float(v), len(s)))
            tabs[k] = ["region_weather_hourly"]
        return {"rows": rows, "tables": tabs}
    return f


cold_mw, hot_mw, cold_ratio, hot_ratio, temp_top = (_demand_measure(n) for n in ("cold_mw", "hot_mw", "cold_ratio", "hot_ratio", "temp_top"))
cold_hours, hot_hours = _hours(True), _hours(False)
TEMP = {"winter_temp": ((1, 2, 12), "mean"), "summer_temp": ((6, 7, 8), "mean"), "min_temp": (None, "min"), "max_temp": (None, "max")}


def _temp(name):
    months, how = TEMP[name]

    def f(in_dir=None):
        w = h.weather(in_dir).dropna(subset=["value"]).copy()
        w["year"] = w["ts_utc"].str[:4].astype(int)
        if months:
            w = w[w["ts_utc"].str[5:7].astype(int).isin(months)]
        rows, tabs = [], {}
        for code, g in w.groupby("code"):
            k = f"wt_{code.lower()}"
            for y, s in g.groupby("year"):
                rows.append(hm._row(k, words(code), y, float(getattr(s["value"], how)()), len(s)))
            tabs[k] = ["region_weather_hourly"]
        return {"rows": rows, "tables": tabs}
    return f


winter_temp, summer_temp, min_temp, max_temp = (_temp(n) for n in ("winter_temp", "summer_temp", "min_temp", "max_temp"))


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_FN = {"cold_mw": f"s.sort_values(['temp', 'ts_utc']).head({N_EXT})['demand_mw'].mean()",
         "hot_mw": f"s.sort_values(['temp', 'ts_utc'], ascending=[False, True]).head({N_EXT})['demand_mw'].mean()",
         "cold_ratio": f"s.sort_values(['temp', 'ts_utc']).head({N_EXT})['demand_mw'].mean() / s['demand_mw'].mean() * 100",
         "hot_ratio": f"s.sort_values(['temp', 'ts_utc'], ascending=[False, True]).head({N_EXT})['demand_mw'].mean() / s['demand_mw'].mean() * 100",
         "temp_top": f"s.sort_values(['demand_mw', 'ts_utc'], ascending=[False, True]).head({N_TOP})['temp'].mean()"}
WHAT = {"cold_mw": f"The mean demand (MW) in the year's {N_EXT} coldest hours by the region's temperature",
        "hot_mw": f"The mean demand (MW) in the year's {N_EXT} hottest hours by the region's temperature",
        "cold_ratio": f"The mean demand in the year's {N_EXT} coldest hours as a percent of the year's mean hour of demand",
        "hot_ratio": f"The mean demand in the year's {N_EXT} hottest hours as a percent of the year's mean hour of demand",
        "temp_top": f"The mean temperature (F) of the year's {N_TOP} highest hours of demand"}


def reproduce_py(name, region):
    code = region.split("_")[1].upper()
    head = (f"w = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nw = w[(w['entity'] == 'eia930:{code}') & (w['variable'] == 'temperature_f')].copy()\n"
            "w['temp'] = pd.to_numeric(w['value'], errors='coerce')\nw = w.dropna(subset=['temp'])\n")
    if name in PY_FN:
        body = head + (f"s_all = region_demand(sys.argv[2], '{code}').merge(w[['ts_utc', 'temp']], on='ts_utc')\n"
                       f"for y, s in s_all.groupby('year'):\n    print(y, round(float({PY_FN[name]}), 6), len(s))\n")
        return (h.py_doc(name, region, ["region_weather_hourly", "eia930_ba_demand_hourly"], f"{WHAT[name]}, {h.REG[code]}; hours both tables hold; ties broken by the hour.")
                + h.PY_READ + h.PY_REGION_DEMAND + body)
    if name in TEMP:
        months, how = TEMP[name]
        body = head + "w['year'] = w['ts_utc'].str[:4].astype(int)\n"
        if months:
            body += f"w = w[w['ts_utc'].str[5:7].astype(int).isin({list(months)})]\n"
        body += f"for y, s in w.groupby('year'):\n    print(y, round(float(s['temp'].{how}()), 6), len(s))\n"
        what = {"winter_temp": "The mean temperature (F) of the year's January, February and December hours", "summer_temp": "The mean temperature (F) of the year's June to August hours",
                "min_temp": "The year's coldest hour (F)", "max_temp": "The year's hottest hour (F)"}[name]
        return h.py_doc(name, region, ["region_weather_hourly"], f"{what}, {h.REG[code]}.") + h.PY_READ + body
    cmp_ = f"<= {COLD_F}" if name == "cold_hours" else f">= {HOT_F}"
    body = head + f"w['year'] = w['ts_utc'].str[:4].astype(int)\nfor y, s in w.groupby('year'):\n    print(y, int((s['temp'] {cmp_}).sum()), len(s))\n"
    return h.py_doc(name, region, ["region_weather_hourly"], f"The hours of the year with {h.REG[code]}'s temperature {cmp_} F.") + h.PY_READ + body


def reproduce_do(name, region):
    code = region.split("_")[1].upper()
    weather_lines = ['import delimited "region_weather_hourly.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eia930:{code}" & variable == "temperature_f"',
                     "keep ts_utc value", "destring value, replace force", "rename value temp", "drop if missing(temp)"]
    if name in PY_FN:
        lines = h.do_head(name, region, ["region_weather_hourly", "eia930_ba_demand_hourly"]) + h.do_region_demand(code) + ["tempfile dem", "save `dem'"] + weather_lines
        lines += ["merge 1:1 ts_utc using `dem', keep(match) nogenerate", "bysort year: egen double ymean = mean(demand)", "bysort year: generate long n = _N"]
        if name in ("cold_mw", "cold_ratio"):
            lines += ["bysort year (temp ts_utc): generate long rank = _n", f"keep if rank <= {N_EXT}"]
        elif name in ("hot_mw", "hot_ratio"):
            lines += ["generate double negt = -temp", "bysort year (negt ts_utc): generate long rank = _n", f"keep if rank <= {N_EXT}"]
        else:
            lines += ["generate double negd = -demand", "bysort year (negd ts_utc): generate long rank = _n", f"keep if rank <= {N_TOP}"]
        if name == "temp_top":
            lines += ["collapse (mean) measure = temp (first) n = n, by(year)"]
        elif name.endswith("_mw"):
            lines += ["collapse (mean) measure = demand (first) n = n, by(year)"]
        else:
            lines += ["collapse (mean) ext = demand (first) ymean = ymean (first) n = n, by(year)", "generate double measure = 100 * ext / ymean"]
    elif name in TEMP:
        months, how = TEMP[name]
        lines = h.do_head(name, region, ["region_weather_hourly"]) + weather_lines + ["generate int year = real(substr(ts_utc, 1, 4))"]
        if months:
            lines += ["generate int month = real(substr(ts_utc, 6, 2))", "keep if " + " | ".join(f"month == {m}" for m in months)]
        lines += [f"collapse ({how}) measure = temp (count) n = temp, by(year)"]
    else:
        cond = f"temp <= {COLD_F}" if name == "cold_hours" else f"temp >= {HOT_F}"
        lines = h.do_head(name, region, ["region_weather_hourly"]) + weather_lines + ["generate int year = real(substr(ts_utc, 1, 4))", f"generate byte hit = {cond}",
                                                                                     "collapse (sum) measure = hit (count) n = temp, by(year)"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LW = ("The region's temperature is the population-weighted mean of its chosen stations (docs/methods/region_weather.md); demand is the sum of its authorities "
      "that file it; a description of the year's extreme hours, not a model, and not adjusted for anything.")
CANDIDATES = [
    C("cold_mw", FAMILY, cold_mw, "MW", 0, 8000, 300.0, "DEMAND IN THE COLDEST HOURS", f"the mean demand in the year's {N_EXT} coldest hours",
      lambda w: f"the mean demand of {w} in the year's {N_EXT} coldest hours", LW, reproduce("cold_mw"), consequence=3),
    C("hot_mw", FAMILY, hot_mw, "MW", 0, 8000, 300.0, "DEMAND IN THE HOTTEST HOURS", f"the mean demand in the year's {N_EXT} hottest hours",
      lambda w: f"the mean demand of {w} in the year's {N_EXT} hottest hours", LW, reproduce("hot_mw"), consequence=3),
    C("cold_ratio", FAMILY, cold_ratio, "percent", 1, 8000, 3.0, "THE COLDEST HOURS AGAINST THE MEAN HOUR",
      f"the mean demand in the year's {N_EXT} coldest hours as a percent of the year's mean hour",
      lambda w: f"the mean demand of {w} in the year's {N_EXT} coldest hours as a percent of its mean hour", LW, reproduce("cold_ratio"), consequence=2),
    C("hot_ratio", FAMILY, hot_ratio, "percent", 1, 8000, 3.0, "THE HOTTEST HOURS AGAINST THE MEAN HOUR",
      f"the mean demand in the year's {N_EXT} hottest hours as a percent of the year's mean hour",
      lambda w: f"the mean demand of {w} in the year's {N_EXT} hottest hours as a percent of its mean hour", LW, reproduce("hot_ratio"), consequence=2),
    C("temp_top", FAMILY, temp_top, "F", 1, 8000, 3.0, "THE TEMPERATURE OF THE PEAK HOURS", f"the mean temperature of the year's {N_TOP} highest hours of demand",
      lambda w: f"the mean temperature of the {N_TOP} highest hours of demand in {w}", LW + " A falling figure means the year's top hours came in colder weather.",
      reproduce("temp_top"), consequence=3),
    C("cold_hours", FAMILY, cold_hours, "hours", 0, 8000, 20.0, "HOURS AT OR BELOW 20 F", "the hours of the year at or below 20 F",
      lambda w: f"the hours of the year at or below 20 F in {w}", "The region's population-weighted temperature (docs/methods/region_weather.md), hours every chosen station holds.",
      reproduce("cold_hours"), consequence=2),
    C("hot_hours", FAMILY, hot_hours, "hours", 0, 8000, 20.0, "HOURS AT OR ABOVE 95 F", "the hours of the year at or above 95 F",
      lambda w: f"the hours of the year at or above 95 F in {w}", "The region's population-weighted temperature (docs/methods/region_weather.md), hours every chosen station holds.",
      reproduce("hot_hours"), consequence=2),
    C("winter_temp", FAMILY, winter_temp, "F", 1, 2000, 1.0, "THE WINTER'S MEAN TEMPERATURE", "the mean temperature of the year's January, February and December hours",
      lambda w: f"the mean temperature of January, February and December in {w}", "The region's population-weighted temperature, hours every chosen station holds; a year's winter is its own January, February and December.",
      reproduce("winter_temp"), consequence=1),
    C("summer_temp", FAMILY, summer_temp, "F", 1, 2000, 1.0, "THE SUMMER'S MEAN TEMPERATURE", "the mean temperature of the year's June to August hours",
      lambda w: f"the mean temperature of June to August in {w}", "The region's population-weighted temperature, hours every chosen station holds.",
      reproduce("summer_temp"), consequence=1),
    C("min_temp", FAMILY, min_temp, "F", 1, 8000, 3.0, "THE YEAR'S COLDEST HOUR", "the year's coldest hour",
      lambda w: f"the coldest hour of the year in {w}", "The region's population-weighted temperature, one hour; a weighted mean is milder than its coldest station.",
      reproduce("min_temp"), consequence=1),
    C("max_temp", FAMILY, max_temp, "F", 1, 8000, 3.0, "THE YEAR'S HOTTEST HOUR", "the year's hottest hour",
      lambda w: f"the hottest hour of the year in {w}", "The region's population-weighted temperature, one hour; a weighted mean is milder than its hottest station.",
      reproduce("max_temp"), consequence=1),
]
for _P in CANDIDATES:
    if _P["unit"] == "MW":
        _P["rank"] = lambda c: abs(c["change"] / c["first"]) if c["first"] else 0.0
    _P["max_per"] = 4


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, family weather")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--max-drafts", type=int, default=24)
    ap.add_argument("--replace", action="store_true")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    cands = [P for P in CANDIDATES if not a.only or P["name"] in a.only.split(",")]
    builder.run(FAMILY, cands, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
