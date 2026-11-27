"""ERW forecast (predict): the demand forecast's longer backtest (session 10603, chain 730, Samuel's order of 27 November
2026, "longer backtests"). Method note: docs/methods/predict.md, section 25. Contract: docs/state/page_files_predict.md.

The backtest of run.py starts on 1 July 2019 because the warehouse's hourly EIA-930 demand began on 1 July 2018. Since
landing 20 (data request 9) eia930_all_history holds every authority's demand from July 2015 to June 2018, so the same
walk can start on 1 July 2016. This run walks it, with the same methods, the same fits (730 days before each target day,
at least 300) and the same horizon (two days), on the demand of predict_data.demand_panel_long, and scores it by the
calendar year of the target day. Nothing in the place files changes: the backtest there, its cuts and the choice stay
as run.py writes them (the longer window changes the fits of 2019 and 2020, which is why this is a file of its own).
The ERW's method in every year is the one chosen now on the last two years, which the longer walk leaves unchanged.

The operator's forecast is scored only where the screened table holds it (eia930_forecast_error_hourly, from July 2018):
the history table's filed forecasts before then are not screened for filing errors, and are not used.

Writes site/data/predict/long_backtest.json. Reads only warehouse tables; writes no table.

Usage: python warehouse/predict/long_backtest.py [--site-dir <dir>] [--places region-tex ...]
"""
import argparse
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
METHODS = ["erw", "yesterday", "week_ago", "regression", "regression_recent"]
WHAT = ("the demand forecast's walk-forward backtest from 1 July 2016, on the authorities' demand of EIA's six-month files "
        "before July 2018 (eia930_all_history) and the hourly table after: the same methods, fits and horizon as the place "
        "files, scored by the calendar year of the target day on the hours every ERW method holds; erw is the method chosen "
        "now in every year (the earlier years test the choice, they do not make it); the operator beside it on the hours "
        "its screened filing holds (from July 2018). The place files' backtest is unchanged")


def place_long(place, dem, op, ref):
    tz = data.place_tz(place, ref)
    o = op[place] if place in op.columns else None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = demand.place_forecasts(dem[place].dropna(), tz, h=2)
    hr = demand.hourly(res, o, first=FIRST)
    choice, maes = score.choose(hr, demand.METHODS, extra=["operator"] if o is not None else [])
    for suf in ("", "_lo", "_hi"):
        hr["erw" + suf] = hr[choice + suf]
    years = []
    for y in sorted(hr["day"].dt.year.unique()):
        g = hr[hr["day"].dt.year == y]
        sm = score.summary(g, METHODS)
        if not sm["hours"]:
            continue
        og = score.summary(g, ["erw", "operator"]) if o is not None else None
        years.append(dict(year=int(y), **sm, operator_same_hours=og if og and og["hours"] else None))
    first = score.common(hr, METHODS)["day"].min()
    return {"place": place, "time": tz, "method": choice, "method_mae_last_2_years": {m: run.num(v, 2) for m, v in maes.items()},
            "first_target": FIRST.strftime("%Y-%m-%d"), "first_scored_day": run.day_str(first) if pd.notna(first) else None,
            "all": score.summary(hr, METHODS), "band_coverage_pct": score.coverage(hr, "erw", days=100000), "by_year": years}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The demand forecast's longer backtest (session 10603)")
    ap.add_argument("--site-dir", default=run.SITE)
    ap.add_argument("--places", nargs="*")
    a = ap.parse_args(argv)
    built = run.now_utc()
    dem = data.demand_panel_long()
    op = data.operator_panel()
    ref, _ = data.reference()
    out = []
    for place in a.places or run.PLACES:
        if place not in dem.columns:
            continue
        p = place_long(place, dem, op, ref)
        out.append(p)
        print(f"  {place}: method {p['method']}, first scored day {p['first_scored_day']}; all {p['all']['hours']} hours, MAPE {p['all']['mape']}", flush=True)
    doc = dict(run.head(built), what=WHAT, method_note="docs/methods/predict.md, section 25",
               tables=["eia930_all_history", "eia930_ba_demand_hourly", "eia930_forecast_error_hourly"], places=out)
    size = run.write_json(os.path.join(a.site_dir, "long_backtest.json"), doc)
    print(f"{run.now_utc()} wrote long_backtest.json ({len(out)} places, {size:,} bytes)", flush=True)


if __name__ == "__main__":
    main()
