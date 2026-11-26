"""ERW forecast (predict): demand further ahead, two to seven days, each horizon backtested and scored apart.

Session 10601, chain 730 (part F). Method note: docs/methods/predict.md, section "Further ahead".

A forecast made at 20:00 UTC on day D reads the demand through day D-1 (the day-ahead rule of the note). Its day
D + j is then j + 1 days after the last day read: horizon h = j + 1. The day-ahead forecast is h = 2; this script
backtests h = 3 to 7 (two to six days after tomorrow), each with the same regression refit at that horizon, and
scores each against "the same hour a week ago" (the hour of day T-7, known for every h up to 7) and against the
operator's day-ahead forecast (a day-ahead forecast, shown for scale only: the operator files nothing further
ahead). A horizon is shown on the page only where its regression's mean absolute error over the last two years is
below the week-ago hour's; otherwise its forecast is written null with the reason.

    python warehouse/predict/ahead.py [--site-dir PATH] [--places ...] [--now ...]

Writes site/data/predict/ahead.json (contract: docs/state/page_files_predict.md, the dated line of session 10601).
"""
import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import predict_data as data  # noqa: E402
import predict_demand as demand  # noqa: E402
import predict_score as score  # noqa: E402
import run  # noqa: E402

HORIZONS = [3, 4, 5, 6, 7]


def place_ahead(place, dem, op, ref, made):
    tz = data.place_tz(place, ref)
    s = dem[place]
    o = op[place] if place in op.columns else None
    frame = demand.local_frame(s, tz)
    last = demand.last_whole_day(frame, tz)
    tomorrow = pd.Timestamp(made).tz_convert(tz).tz_localize(None).normalize() + pd.Timedelta(days=1)
    out = []
    for h in HORIZONS:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            res = demand.place_forecasts(s, tz, h=h)
        hr = demand.hourly(res, o)
        meths = ("regression", "regression_recent", "week_ago", "yesterday")
        c = hr.dropna(subset=["actual"] + list(meths))
        recent = c[c["day"] > c["day"].max() - pd.Timedelta(days=score.CHOICE_DAYS)]
        mae = {m: score.metric(recent, m)[1] for m in meths}
        mape = {m: score.metric(recent, m)[2] for m in meths}
        oc = recent.dropna(subset=["operator"]) if "operator" in recent else recent.iloc[0:0]
        # the method of the horizon: the lower error of the two regressions over the last two years (the place files' rule)
        cands = [m for m in ("regression", "regression_recent") if mae[m] is not None]
        method = min(cands, key=lambda m: mae[m]) if cands else "regression"
        shown = mae[method] is not None and mae["week_ago"] is not None and mae[method] < mae["week_ago"]
        # the day this horizon forecasts from the demand held now: the last day held plus h
        target = res["M"].index.max()
        row = {"horizon_days": h, "days_after_tomorrow": int((target - tomorrow).days), "target_day": run.day_str(target), "method": method,
               "shown": bool(shown), "held": None if shown else "not shown: over the last two years this horizon's method did not beat the same hour a week ago",
               "last_2_years": {"hours": int(len(recent)), "mae": {k: run.num(v, 2) for k, v in mae.items()}, "mape": {k: run.num(v, 3) for k, v in mape.items()},
                                "operator_day_ahead_mae_same_hours": run.num(score.metric(oc, "operator")[1], 2) if len(oc) else None},
               "band_coverage_pct": score.coverage(hr, method),
               "forecast_columns": ["ts_utc", "local_hour", "erw", "lo", "hi"], "forecast": None}
        if shown:
            tm = demand.tomorrow(res, tz, target)
            row["forecast"] = [[run.iso(r["ts"]), int(r["hour"]), run.num(r[method]), run.num(r[method + "_lo"]), run.num(r[method + "_hi"])] for _, r in tm.iterrows()]
        out.append(row)
    return {"place": place, "time": tz, "last_whole_day": run.day_str(last), "horizons": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The ERW forecast further ahead (chain 730, part F)")
    ap.add_argument("--site-dir", default=run.SITE)
    ap.add_argument("--places", nargs="*")
    ap.add_argument("--now")
    a = ap.parse_args(argv)
    built = run.now_utc()
    t = pd.Timestamp(a.now or built)
    made = (t.tz_convert("UTC") if t.tzinfo else t.tz_localize("UTC")).floor("h")
    dem = data.demand_panel()
    op = data.operator_panel()
    ref, _ = data.reference()
    places = a.places or run.PLACES
    docs = []
    for place in places:
        d = place_ahead(place, dem, op, ref, made)
        docs.append(d)
        print(f"  {place}: " + ", ".join(f"h{r['horizon_days']} {'shown' if r['shown'] else 'not shown'} ({r['last_2_years']['mae']['regression']} against {r['last_2_years']['mae']['week_ago']})" for r in d["horizons"]), flush=True)
    doc = dict(run.head(built), method_notes=run.NOTES, made_utc=run.iso(made),
               what="The demand forecast two to seven days ahead: horizon h is the number of days between the last whole day of demand read and the day forecast (the day-ahead forecast is h = 2, in each place's own file). Each horizon uses the better of the two regressions of the method note (the regression and regression_recent, by mean absolute error over the last two years), refit at that horizon, scored against the same hour a week ago, and shown only where it beats it.",
               places=docs)
    run.write_json(os.path.join(a.site_dir, "ahead.json"), doc)
    print(f"{run.now_utc()} wrote ahead.json ({len(docs)} places)", flush=True)


if __name__ == "__main__":
    main()
