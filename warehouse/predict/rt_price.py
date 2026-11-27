"""ERW forecast (predict): the daily run of the real-time price forecast at the three public hubs (chain 730, part F).
Writes site/data/predict/rt_price.json and appends to site/data/predict/ledger_rt_price.csv (never overwritten).
Method note: docs/methods/predict_price.md, section 7. Reads only warehouse tables; writes no table.

Usage: python warehouse/predict/rt_price.py [--now <UTC hour>] [--no-ledger] [--site-dir <dir>]
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import predict_data as data  # noqa: E402
import predict_demand as demand  # noqa: E402
import predict_rt as rtm  # noqa: E402
import predict_score as score  # noqa: E402

SITE = os.path.join(data.ROOT, "site", "data", "predict")
CONTRACT = "docs/state/page_files_predict.md"
NOTE = "docs/methods/predict_price.md"
MAPE_FLOOR = 5.0
SPIKE_Q = 0.99
HISTORY_DAYS = 35
SCORED = ["erw", "day_ahead", "yesterday", "regression"]
LONG_FIRST = pd.Timestamp("2016-01-01")   # the longer backtest (session 10603; method note predict_price.md section 8)
LONG_WHAT = ("the same walk-forward backtest from 1 January 2016, as far back as each hub's prices allow (ERCOT's are held from "
             "2015, SPP's and CAISO's from July 2018, so their first scored day is as in the backtest): each year scored on the "
             "hours every method and the day-ahead price hold; the method chosen now (last two years) is the ERW's in every year, "
             "so the earlier years test the rule, they do not choose; the backtest and its cuts above are unchanged")
LEDGER_COLS = ["hub", "target_day", "ts_utc", "local_hour", "made_utc", "inputs_through_utc", "horizon_days", "method", "erw", "lo", "hi", "day_ahead"]
WORDS = {"erw": "the ERW method the rule chose for the hub (the lowest mean absolute error of yesterday and the regression over the last two years, on the hours the day-ahead price also holds)",
         "day_ahead": "the hub's day-ahead price for the hour: the market's own forecast of the real-time price, published before the forecast is made; the comparator, never an ERW method",
         "yesterday": "the real-time price of the same local hour two days before the target day (the latest whole day read)",
         "regression": "least squares by local hour on the day-ahead price for the hour, the real-time less day-ahead price at the hour two days before, and its mean over the seven days to then; refit every day on the 730 days before it"}


def iso(t):
    return pd.Timestamp(t).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def num(x, nd=2):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return round(x, nd) if np.isfinite(x) else None


def long_backtest(res, choice, first=LONG_FIRST):
    """The longer backtest (section 8): the whole span from `first`, and each calendar year of the target day."""
    hl = demand.hourly(res, None, first=first)
    for suf in ("", "_lo", "_hi"):
        hl["erw" + suf] = hl[choice + suf]
    c = score.common(hl, SCORED)
    years = []
    for y in sorted(c["day"].dt.year.unique()):
        s = score.summary(hl[hl["day"].dt.year == y], SCORED, mape_floor=MAPE_FLOOR)
        years.append(dict(year=int(y), **s))
    return {"what": LONG_WHAT, "first_target": first.strftime("%Y-%m-%d"), "method": choice,
            "all": score.summary(hl, SCORED, mape_floor=MAPE_FLOOR), "band_coverage_pct": score.coverage(hl, "erw", days=100000),
            "by_year": years}


def one(grid, rt, da, made):
    tz = rtm.HUB_TZ[grid]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = rtm.place_forecasts(rt[grid].dropna(), da[grid].dropna(), tz)
    hr = demand.hourly(res, None, first=rtm.FIRST_TARGET)
    choice, maes = score.choose(hr, rtm.METHODS, extra=["day_ahead"])
    for suf in ("", "_lo", "_hi"):
        hr["erw" + suf] = hr[choice + suf]
    rows = score.rows(f"hub-{grid}", "rt_price", hr, SCORED, {}, mape_floor=MAPE_FLOOR, spike_q=SPIKE_Q)
    frame = res["frame"]
    last = demand.last_whole_day(frame, tz)
    target = pd.Timestamp(made).tz_convert(tz).tz_localize(None).normalize() + pd.Timedelta(days=1)
    h = int((target - last).days)
    tomorrow, held = None, None
    if h == rtm.H:
        tm = demand.tomorrow(res, tz, target)
        if np.isfinite(tm["day_ahead"]).all():
            tomorrow = [[iso(t), int(k), num(v), num(lo), num(hi), num(d)] for t, k, v, lo, hi, d in
                        zip(tm["ts"], tm["hour"], tm[choice], tm[choice + "_lo"], tm[choice + "_hi"], tm["day_ahead"])]
        else:
            held = "no forecast yet: the day-ahead price for the target day is not held when the forecast is made"
    else:
        held = f"no forecast: the last whole day of real-time prices held ({last.date()}) is {h} days before the target day; this forecast reads exactly two"
    c = score.common(hr, SCORED)
    hist = c[c["day"] > c["day"].max() - pd.Timedelta(days=HISTORY_DAYS)]
    block = {"hub": data.HUBS[grid], "grid": grid, "time": tz, "status": "shown", "method": choice,
             "method_mae_last_2_years": {m: num(v) for m, v in maes.items()}, "made_utc": iso(made),
             "inputs_through_utc": iso(frame.loc[frame["day"] <= last, "ts"].max()), "target_day": target.strftime("%Y-%m-%d"), "horizon_days": h,
             "band": "the 10th and 90th percentile of the chosen method's own past errors (actual less forecast, USD/MWh) at the same local hour over 365 days",
             "band_coverage_pct": score.coverage(hr, "erw"),
             "band_coverage": score.coverage_detail(hr, "erw"),
             "long_backtest": long_backtest(res, choice),
             "tomorrow_columns": ["ts_utc", "local_hour", "erw", "lo", "hi", "day_ahead"], "tomorrow": tomorrow, "tomorrow_held": held,
             "summary": {"last_2_years": score.summary(hr, SCORED, days=score.CHOICE_DAYS, mape_floor=MAPE_FLOOR),
                         "backtest": score.summary(hr, SCORED, mape_floor=MAPE_FLOOR)},
             "history_columns": ["ts_utc", "local_day", "local_hour", "erw", "lo", "hi", "day_ahead", "actual", "yesterday"],
             "history": [[iso(r.ts), r.day.strftime("%Y-%m-%d"), int(r.hour), num(r.erw), num(r.erw_lo), num(r.erw_hi), num(r.day_ahead), num(r.actual), num(r.yesterday)]
                         for r in hist.itertuples()]}
    ledger = []
    if tomorrow:
        for t, k, v, lo, hi, d in tomorrow:
            ledger.append({"hub": data.HUBS[grid], "target_day": block["target_day"], "ts_utc": t, "local_hour": k, "made_utc": iso(made),
                           "inputs_through_utc": block["inputs_through_utc"], "horizon_days": h, "method": choice, "erw": v, "lo": lo, "hi": hi, "day_ahead": d})
    return block, rows, ledger


def append_ledger(site, rows):
    p = os.path.join(site, "ledger_rt_price.csv")
    have = pd.read_csv(p, skiprows=data.ip.header_rows(p), dtype={"target_day": str}) if os.path.exists(p) else pd.DataFrame(columns=LEDGER_COLS)
    held = set(zip(have["hub"], have["target_day"].astype(str)))
    new = [r for r in rows if (r["hub"], r["target_day"]) not in held]
    if not new:
        return 0
    first = not os.path.exists(p)
    os.makedirs(site, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        if first:
            f.write("# Energy Research Warehouse (ERW): the ERW forecast of the real-time hub price, every forecast as made on its day, never overwritten (tier derived; a model's output, not a published figure)\n")
            f.write(f"# Written by warehouse/predict/rt_price.py; contract {CONTRACT}; method {NOTE}, section 7. One row a hub and UTC hour of the target day, USD/MWh; made_utc the hour the forecast was made; day_ahead the hub's day-ahead price for the hour, read when the forecast was made.\n")
            f.write("# Source: erw:predict, from the hubs' real-time and day-ahead prices (ERCOT, SPP, CAISO; public)\n")
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS, lineterminator="\n")
        if first:
            w.writeheader()
        for r in new:
            w.writerow(r)
    return len(new)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The ERW forecast of the real-time hub price (chain 730, part F)")
    ap.add_argument("--site-dir", default=SITE)
    ap.add_argument("--now")
    ap.add_argument("--no-ledger", action="store_true")
    a = ap.parse_args(argv)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    t = pd.Timestamp(a.now or built)
    made = (t.tz_convert("UTC") if t.tzinfo else t.tz_localize("UTC")).floor("h")
    rt = rtm.rt_panel()
    da = data.price_panel()
    hubs, rows, ledger = [], [], []
    for grid in ("ercot", "spp", "caiso"):
        block, r, lg = one(grid, rt, da, made)
        hubs.append(block)
        rows += r
        ledger += lg
        print(f"  {grid}: method {block['method']} {block['method_mae_last_2_years']}; last two years MAE {block['summary']['last_2_years']['mae']}", flush=True)
    added = 0 if a.no_ledger else append_ledger(a.site_dir, ledger)
    doc = {"contract": CONTRACT, "built": built, "tier": "derived", "label": "ERW forecast", "method_note": NOTE + ", section 7",
           "made_rule": f"made at {rtm.MADE_HOUR}:00 UTC the day before the target local day, after the three day-ahead markets publish on their ordinary timelines, from real-time prices through two days before",
           "units": "USD/MWh; mape over the hours whose actual price is at least 5 USD/MWh in size", "methods": [{"id": m, "words": w} for m, w in WORDS.items()],
           "hubs": hubs, "rows_columns": score.COLUMNS, "rows": rows}
    os.makedirs(a.site_dir, exist_ok=True)
    with open(os.path.join(a.site_dir, "rt_price.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), allow_nan=False)
    print(f"{built} wrote rt_price.json ({len(hubs)} hubs, {len(rows)} score rows); ledger: {added} rows added", flush=True)


if __name__ == "__main__":
    main()
