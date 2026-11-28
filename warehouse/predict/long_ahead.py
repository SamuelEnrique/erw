"""ERW forecast (predict): the longer backtest of the forecast two to seven days ahead (session 10603, chain 730,
Samuel's order of 28 November 2026, "then longer backtests and more places"). Method note: docs/methods/predict.md,
section 30. Contract: docs/state/page_files_predict.md.

ahead.py backtests each horizon h = 3 to 7 from 1 July 2019, on the hourly EIA-930 demand that began on 1 July 2018.
Since landing 20 (data request 9) eia930_all_history holds every authority's demand from July 2015, so this run walks
the same horizons from 1 July 2016, on predict_data.demand_panel_long, with the same methods and fits (the regression
and regression_recent refit at the horizon on the 730 days before each target day, at least 300), and scores each
horizon by the calendar year of the target day against the same hour a week ago (known at every horizon to 7).

The method of a horizon is chosen as ahead.py chooses it: the lower mean absolute error of the two regressions over
the last two years, on the hours the actual and the four candidates (the two regressions, the week-ago hour,
yesterday's hour) all hold. It is the method in every year (the earlier years test the rule, they do not choose).
"beats" in a year is that method's mean absolute error below the week-ago hour's on that year's common hours.
Nothing in ahead.json or ahead_more.json changes: their backtests stay as ahead.py writes them.

Writes site/data/predict/long_ahead.json. Reads only warehouse tables; writes no table.

Usage: python warehouse/predict/long_ahead.py [--places ...] [--out <file>]
       python warehouse/predict/long_ahead.py --merge <part.json> <part.json> ... [--site-dir <dir>]
"""
import argparse
import json
import os
import sys
import warnings

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import predict_data as data  # noqa: E402
import predict_demand as demand  # noqa: E402
import predict_score as score  # noqa: E402
import run  # noqa: E402

FIRST = pd.Timestamp("2016-07-01")
HORIZONS = [3, 4, 5, 6, 7]
CANDS = ("regression", "regression_recent", "week_ago", "yesterday")
SCORED = ["erw", "regression", "regression_recent", "week_ago", "yesterday"]
WHAT = ("the forecast two to seven days ahead walked from 1 July 2016, on the authorities' demand of EIA's six-month files "
        "before July 2018 (eia930_all_history) and the hourly table after: each horizon h (days between the last whole day "
        "read and the day forecast) with the same two regressions refit at that horizon, its method chosen now as ahead.py "
        "chooses it (the lower mean absolute error of the two over the last two years), scored by the calendar year of the "
        "target day on the hours every candidate holds, against the same hour a week ago; beats: the method's mean "
        "absolute error below the week-ago hour's that year. ahead.json and ahead_more.json are unchanged")


def horizon_long(s, tz, h):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = demand.place_forecasts(s, tz, h=h)
    hr = demand.hourly(res, None, first=FIRST)
    c = hr.dropna(subset=["actual"] + list(CANDS))
    recent = c[c["day"] > c["day"].max() - pd.Timedelta(days=score.CHOICE_DAYS)]
    mae = {m: score.metric(recent, m)[1] for m in CANDS}
    cands = [m for m in ("regression", "regression_recent") if mae[m] is not None]
    method = min(cands, key=lambda m: mae[m]) if cands else "regression"
    for suf in ("", "_lo", "_hi"):
        hr["erw" + suf] = hr[method + suf]
    years = []
    for y in sorted(hr["day"].dt.year.unique()):
        sm = score.summary(hr[hr["day"].dt.year == y], SCORED)
        if not sm["hours"]:
            continue
        sm = dict(year=int(y), **sm)
        sm["beats_week_ago"] = bool(sm["mae"]["erw"] < sm["mae"]["week_ago"])
        years.append(sm)
    first = score.common(hr, SCORED)["day"].min()
    return {"horizon_days": h, "method": method, "method_mae_last_2_years": {m: run.num(v, 2) for m, v in mae.items()},
            "first_scored_day": run.day_str(first) if pd.notna(first) else None,
            "all": score.summary(hr, SCORED), "years_beating_week_ago": sum(y["beats_week_ago"] for y in years), "years": len(years),
            "band_coverage_pct": score.coverage(hr, "erw", days=100000), "by_year": years}


def place_long(place, dem, ref):
    tz = data.place_tz(place, ref)
    s = dem[place].dropna()
    return {"place": place, "time": tz, "first_target": FIRST.strftime("%Y-%m-%d"),
            "horizons": [horizon_long(s, tz, h) for h in HORIZONS]}


def write_doc(site_dir, places, built):
    doc = dict(run.head(built), what=WHAT, method_note="docs/methods/predict.md, section 30",
               tables=["eia930_all_history", "eia930_ba_demand_hourly"], places=places)
    return run.write_json(os.path.join(site_dir, "long_ahead.json"), doc)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The longer backtest of the forecast two to seven days ahead (session 10603)")
    ap.add_argument("--site-dir", default=run.SITE)
    ap.add_argument("--places", nargs="*")
    ap.add_argument("--out", help="write the places to this part file instead of the site file (merge the parts with --merge)")
    ap.add_argument("--merge", nargs="*", help="part files to merge, in the order of run.PLACES, into the site file")
    a = ap.parse_args(argv)
    built = run.now_utc()
    if a.merge:
        got = {}
        for p in a.merge:
            with open(p, encoding="utf-8") as f:
                for x in json.load(f)["places"]:
                    got[x["place"]] = x
        out = [got[p] for p in run.PLACES if p in got]
        size = write_doc(a.site_dir, out, built)
        print(f"{run.now_utc()} wrote long_ahead.json ({len(out)} places, {size:,} bytes)", flush=True)
        return
    dem = data.demand_panel_long()
    ref, _ = data.reference()
    out = []
    for place in a.places or run.PLACES:
        if place not in dem.columns:
            continue
        p = place_long(place, dem, ref)
        out.append(p)
        print(f"  {place}: " + ", ".join(f"h{x['horizon_days']} {x['method']} beats {x['years_beating_week_ago']}/{x['years']}" for x in p["horizons"]), flush=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"places": out}, f, separators=(",", ":"), allow_nan=False)
        print(f"{run.now_utc()} wrote {a.out} ({len(out)} places)", flush=True)
    else:
        size = write_doc(a.site_dir, out, built)
        print(f"{run.now_utc()} wrote long_ahead.json ({len(out)} places, {size:,} bytes)", flush=True)


if __name__ == "__main__":
    main()
