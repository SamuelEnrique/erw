"""ERW forecast (predict): the day-ahead price forecast's longer backtest (session 10603, chain 730, Samuel's order of 27
November 2026, "longer backtests"). Method note: docs/methods/predict_price.md, section 11. Contract:
docs/state/page_files_predict.md.

The day-ahead price forecast (predict_price.md sections 1 to 4, 10) reads the place's demand forecast, so its backtest
began where the warehouse's hourly demand began (July 2018; the regression's first fits in March 2020). With the
authorities' demand of EIA's six-month files held from July 2015 (eia930_all_history, data request 9), the same walk
can start earlier wherever the hub's prices are held earlier: ERCOT's from January 2015. This run walks it from
1 July 2016 on predict_data.demand_panel_long, for the six places of the place files and the four hubs of
price_hubs.json, with the same methods, fits, hour of making and horizons, and scores it by calendar year. SPP's and
CAISO's prices begin in 2018 and 2023, so their places start where they did. Nothing in the place files or in
price_hubs.json changes; the method in every year is the one chosen now on the last two years.

Writes site/data/predict/long_price.json. Reads only warehouse tables; writes no table.

Usage: python warehouse/predict/long_price.py [--site-dir <dir>]
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
import predict_price as price  # noqa: E402
import predict_rt as rtm  # noqa: E402
import predict_score as score  # noqa: E402
import price_hubs  # noqa: E402
import run  # noqa: E402

FIRST = pd.Timestamp("2016-07-01")
METHODS = ["erw", "yesterday", "week_ago", "regression"]
WHAT = ("the day-ahead price forecast's walk-forward backtest from 1 July 2016, on the demand of EIA's six-month files "
        "before July 2018 (eia930_all_history) and the hourly table after: the same methods, fits, hour of making and "
        "horizons as the place files and price_hubs.json, scored by the calendar year of the target day on the hours "
        "every method holds (MAPE over hours of at least 5 USD/MWh); erw is the method chosen now in every year. Where a "
        "hub's prices begin after 2016 (SPP 2018, CAISO 2023) the span starts where its prices allow. The place files' and "
        "price_hubs.json's backtests are unchanged")


def one(place, hub_col, demand_place, pp, dem, ref, gas):
    tz = data.place_tz(demand_place, ref)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = price.place_forecasts(pp[hub_col], tz, dem[demand_place].dropna(), tz, gas, hp=1, hd=3)
    hr = demand.hourly(res, first=FIRST)
    choice, maes = score.choose(hr, price.METHODS)
    for suf in ("", "_lo", "_hi"):
        hr["erw" + suf] = hr[choice + suf]
    years = []
    for y in sorted(hr["day"].dt.year.unique()):
        sm = score.summary(hr[hr["day"].dt.year == y], METHODS, mape_floor=price.MAPE_FLOOR)
        if sm["hours"]:
            years.append(dict(year=int(y), **sm))
    first = score.common(hr, METHODS)["day"].min()
    return {"place": place, "hub": rtm.RT_HUBS[hub_col], "demand_place": demand_place, "time": tz, "method": choice,
            "method_mae_last_2_years": {m: run.num(v, 2) for m, v in maes.items()}, "first_target": FIRST.strftime("%Y-%m-%d"),
            "first_scored_day": run.day_str(first) if pd.notna(first) else None,
            "all": score.summary(hr, METHODS, mape_floor=price.MAPE_FLOOR), "band_coverage_pct": score.coverage(hr, "erw", days=100000),
            "by_year": years}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The day-ahead price forecast's longer backtest (session 10603)")
    ap.add_argument("--site-dir", default=run.SITE)
    a = ap.parse_args(argv)
    built = run.now_utc()
    dem = data.demand_panel_long()
    ref, _ = data.reference()
    gas = data.gas_series()
    pp = data.price_panel(rtm.RT_HUBS)
    jobs = [(p, g, p) for p, g in run.PRICE_GRID.items()] + [(f"hub-{h}", h, d) for h, d in price_hubs.HUB_DEMAND.items()]
    out = []
    for place, hub_col, dp in jobs:
        p = one(place, hub_col, dp, pp, dem, ref, gas)
        out.append(p)
        print(f"  {place} ({p['hub']}): method {p['method']}, first scored day {p['first_scored_day']}; all MAE {p['all']['mae']}", flush=True)
    doc = dict(run.head(built), what=WHAT, method_note="docs/methods/predict_price.md, section 11",
               tables=["eia930_all_history", "eia930_ba_demand_hourly", "eia_fuel_spot_prices"] + data.PRICE_TABLES, places=out)
    size = run.write_json(os.path.join(a.site_dir, "long_price.json"), doc)
    print(f"{run.now_utc()} wrote long_price.json ({len(out)} places, {size:,} bytes)", flush=True)


if __name__ == "__main__":
    main()
