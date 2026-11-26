"""ERW forecast (predict): the daily run. Tomorrow's forecast for every place, the backtest, the scores and the page files.

Session 10600, chain 730 (part D4 and D5). Contract of the files: docs/state/page_files_predict.md. Method notes:
docs/methods/predict.md (demand) and docs/methods/predict_price.md (price).

    python warehouse/predict/run.py [--site-dir PATH] [--out-dir PATH] [--places region-tex ba-ciso] [--now 2026-11-26T20:00:00Z]

What it does, in order:
 1. reads the warehouse's tables (warehouse/predict/data.py; ERW_DATA_ROOT names the folder that holds them);
 2. for each place, the walk-forward backtest of every method (warehouse/predict/demand.py), the choice of the method
    by the rule, and the scores (warehouse/predict/score.py);
 3. tomorrow's forecast: the place's next local day after the hour the run is made, from the demand held then; it is
    appended to the ledger (site/data/predict/ledger_demand.csv) only if the ledger holds no forecast for that place
    and day: a forecast once written is never overwritten;
 4. the page files: index.json, one file a place, scores.json (site/data/predict/);
 5. the tables asked of window A (docs/state/data_requests_predict.md), written as files to --out-dir (by default
    runs/predict_out, not in git): this script writes no warehouse table.

Tier: derived. Every file says "ERW forecast", a model's output, never a published or official figure.
"""
import argparse
import csv
import datetime as dt
import glob
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
import predict_price as price  # noqa: E402
import predict_score as score  # noqa: E402

ROOT = data.ROOT
SITE = os.path.join(ROOT, "site", "data", "predict")
OUT = os.path.join(ROOT, "runs", "predict_out")
CONTRACT = "docs/state/page_files_predict.md"
NOTES = {"demand": "docs/methods/predict.md", "price": "docs/methods/predict_price.md"}
LABEL = "ERW forecast"
TIER = "derived"
HISTORY_DAYS = 35
DEMAND_MADE_HOUR = 20      # UTC, on day T-1 (the ground, section 3)
LARGE_BAS = ["BPAT", "CISO", "CPLE", "DUK", "ERCO", "FPC", "FPL", "ISNE", "MISO", "NYIS", "PACE", "PJM", "PSCO", "SOCO", "SWPP", "TVA"]
PLACES = [f"region-{r.lower()}" for r in data.REGIONS] + [f"ba-{b.lower()}" for b in LARGE_BAS]
SCORED = ["erw", "operator", "yesterday", "week_ago", "regression", "regression_recent"]
METHOD_WORDS = {
    "erw": "the method chosen for the place by the rule of the method note (the lowest mean absolute error of the ERW's methods over the last two years of the backtest)",
    "operator": "the operator's own day-ahead demand forecast, as filed on Form EIA-930 (eia930_forecast_error_hourly, the screened hours left out); for the price none is published, and its rows are held",
    "yesterday": "the same local hour of the latest whole day held when the forecast is made (two days before the target day, for the day-ahead forecast)",
    "week_ago": "the same local hour seven days before the target day",
    "regression": "the least-squares regression of the method note, one a local hour, refit for every day on the 730 days before it",
    "regression_recent": "the same regression with three more recent regressors (the last hour of the latest day read, the same hour the day before it, the same hour two weeks before the target day); added in session 10601",
}
# price status by place until part E: the grid's hub, or why none (the ground, section 2)
PRICE_GRID = {"region-tex": "ercot", "ba-erco": "ercot", "region-cent": "spp", "ba-swpp": "spp", "region-cal": "caiso",
              "ba-ciso": "caiso"}
PRICE_HELD = {"region-midw": ("paused", "paused: MISO's terms forbid automated access (warehouse/metadata/paused_sources.csv); no price since 4 October 2026"),
              "ba-miso": ("paused", "paused: MISO's terms forbid automated access (warehouse/metadata/paused_sources.csv); no price since 4 October 2026"),
              "region-mida": ("license needed", "license needed: PJM's prices need a paid data license (docs/licenses.md); none is held"),
              "ba-pjm": ("license needed", "license needed: PJM's prices need a paid data license (docs/licenses.md); none is held"),
              "region-ne": ("license needed", "license needed: ISO-NE's terms ask for written permission, which the ERW has not recorded (warehouse/metadata/license_verdicts.csv; iso_hub_prices_history license needed since 2026-10-21)"),
              "ba-isne": ("license needed", "license needed: ISO-NE's terms ask for written permission, which the ERW has not recorded (warehouse/metadata/license_verdicts.csv; iso_hub_prices_history license needed since 2026-10-21)"),
              "region-ny": ("license needed", "license needed: NYISO's terms ask for written permission, which the ERW has not recorded (warehouse/metadata/license_verdicts.csv; iso_hub_prices_history license needed since 2026-10-21)"),
              "ba-nyis": ("license needed", "license needed: NYISO's terms ask for written permission, which the ERW has not recorded (warehouse/metadata/license_verdicts.csv; iso_hub_prices_history license needed since 2026-10-21)")}
NO_MARKET = "not built: no organised day-ahead market whose hub prices the warehouse holds covers this place"
LEDGER_COLS = ["series", "place", "target_day", "ts_utc", "local_hour", "made_utc", "inputs_through_utc", "horizon_days", "method", "erw", "lo", "hi"]


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def num(x, nd=1):
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(f) else round(f, nd)


def iso(t):
    return None if t is None or pd.isna(t) else data.utc_iso(t)


def day_str(t):
    return None if t is None or pd.isna(t) else pd.Timestamp(t).strftime("%Y-%m-%d")


def events():
    """{event id as /events names it: (first local day, last local day)} from site/data/regions/events/."""
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "site", "data", "regions", "events", "*.json"))):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        eid = os.path.basename(p)[:-5].replace("_", "-")
        if d.get("start") and d.get("end"):
            out[eid] = (d["start"], d["end"])
    return out


def ledger_path(site, series="demand"):
    return os.path.join(site, f"ledger_{series}.csv")


def read_ledger(site, series="demand"):
    p = ledger_path(site, series)
    if not os.path.exists(p):
        return pd.DataFrame(columns=LEDGER_COLS)
    return pd.read_csv(p, skiprows=data.ip.header_rows(p), dtype={"target_day": str})


def append_ledger(site, rows, series="demand"):
    """Append rows (dicts) whose (series, place, target_day) the ledger does not hold. Never rewrites a row."""
    p = ledger_path(site, series)
    have = read_ledger(site, series)
    held = set(zip(have["series"], have["place"], have["target_day"].astype(str)))
    new = [r for r in rows if (r["series"], r["place"], r["target_day"]) not in held]
    if not new:
        return 0
    first = not os.path.exists(p)
    os.makedirs(site, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        if first:
            f.write("# Energy Research Warehouse (ERW): the ERW forecast's ledger, every forecast as made on its day, never overwritten (tier derived; a model's output, not a published figure)\n")
            if series == "demand":
                f.write(f"# Written by warehouse/predict/run.py; contract {CONTRACT}; method {NOTES['demand']}. One row a place and UTC hour of the target day; made_utc the hour the forecast was made; inputs_through_utc the last hour of the place's demand it read.\n")
                f.write("# Source: erw:predict, from eia930_ba_demand_hourly (U.S. Energy Information Administration, Form EIA-930, public)\n")
            else:
                f.write(f"# Written by warehouse/predict/run.py; contract {CONTRACT}; method {NOTES['price']}. One row a place and UTC hour of the target day, USD/MWh; made_utc the hour the forecast was made; inputs_through_utc the last hour of the hub's day-ahead price it read.\n")
                f.write("# Source: erw:predict, from the hubs' day-ahead prices (ERCOT, SPP, CAISO, public), eia930_ba_demand_hourly and eia_fuel_spot_prices (public)\n")
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS, lineterminator="\n")
        if first:
            w.writeheader()
        for r in new:
            w.writerow(r)
    return len(new)


def demand_place(place, dem, op, ref, made, evs, wx=None):
    """Everything about one place's demand: the backtest frame, the choice, score rows, tomorrow, the file's series."""
    tz = data.place_tz(place, ref)
    s = dem[place]
    o = op[place] if place in op.columns else None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = demand.place_forecasts(s, tz, h=2)
    wk = None
    region = data.place_region(place, ref)
    if wx is not None and region in wx.columns:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            pw = demand.regression_weather_known(res["M"], wx[region], tz, 2)
        res["P"]["with_weather_known"] = pw
        res["lo"]["with_weather_known"], res["hi"]["with_weather_known"] = demand.band(res["M"], pw, 2)
        wk = region
    hr = demand.hourly(res, o)
    choice, maes = score.choose(hr, demand.METHODS, extra=["operator"])
    for suf in ("", "_lo", "_hi"):
        hr["erw" + suf] = hr[choice + suf]
    hr["made_utc"] = pd.to_datetime(hr["day"] - pd.Timedelta(days=1)).dt.tz_localize("UTC") + pd.Timedelta(hours=DEMAND_MADE_HOUR)
    rows = score.rows(place, "demand", hr, SCORED, evs)
    pk = score.peaks(hr, SCORED)
    rows += peak_rows(place, pk)
    weather = None
    if wk is not None:
        # the separate line "with the weather known": scored on its own hours (the region's temperature is held to
        # its last observation), never the ERW forecast, never in the choice
        wm = ["with_weather_known", "regression", "operator"]
        weather = {"what": f"the regression with the region's observed temperature added (region {wk.upper()}, region_weather_hourly): it reads the day's own weather, so it is not a forecast; it shows how much of the regression's error a perfect weather forecast could remove",
                   "region": wk.upper()}
        for cut, days in (("all", None), ("last_2_years", score.CHOICE_DAYS)):
            sm = score.summary(hr, wm, days=days)
            weather[cut] = sm
            for m in wm:
                rows.append([place, "demand_weather_known", m, cut, "", sm["hours"], sm["mae"][m], sm["mape"][m], None])
    # tomorrow: the place's next local day after the hour of the run
    frame = res["frame"]
    last = demand.last_whole_day(frame, tz)
    target = (pd.Timestamp(made).tz_convert(tz).tz_localize(None).normalize() + pd.Timedelta(days=1))
    h = int((target - last).days)
    inputs_through = frame.loc[frame["day"] <= last, "ts"].max()
    tm, tm_held = None, None
    if 2 <= h <= 7:
        if h == 2:
            res_h = res
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                res_h = demand.place_forecasts(s, tz, h=h)
        tm = demand.tomorrow(res_h, tz, target)
        if o is not None:
            tm["operator"] = o.reindex(pd.DatetimeIndex(tm["ts"])).to_numpy()
        else:
            tm["operator"] = np.nan
    else:
        tm_held = f"no data: the last whole day held ({day_str(last)}) is {h} days before the target day; the forecast reads at most 7"
    return {"place": place, "tz": tz, "hr": hr, "choice": choice, "maes": maes, "rows": rows, "tomorrow": tm, "tomorrow_held": tm_held,
            "target": target, "h": h, "inputs_through": inputs_through, "last_whole_day": last, "res": res, "peaks": pk, "weather": weather}


def history_rows(p, ledger, nd=None):
    nd = nd if nd is not None else (2 if p.get("series") == "price" else 1)
    hr = p["hr"]
    last = hr["day"].max()
    x = hr[hr["day"] > last - pd.Timedelta(days=HISTORY_DAYS)].copy()
    x["kind"] = "backtest"
    lg = ledger[(ledger["series"] == p.get("series", "demand")) & (ledger["place"] == p["place"])]
    live = {r["ts_utc"]: r for _, r in lg.iterrows()}
    out = []
    for _, r in x.iterrows():
        ts = iso(r["ts"])
        made, kind, erw, lo, hi = iso(r["made_utc"]), "backtest", r["erw"], r["erw_lo"], r["erw_hi"]
        if ts in live:
            L = live[ts]
            made, kind, erw, lo, hi = L["made_utc"], "live", L["erw"], L["lo"], L["hi"]
        out.append([ts, day_str(r["day"]), int(r["hour"]), made, kind, num(erw, nd), num(lo, nd), num(hi, nd), num(r.get("operator"), nd),
                    num(r["actual"], nd), num(r["yesterday"], nd), num(r["week_ago"], nd)])
    return out


def demand_series(p, made, ledger):
    hr = p["hr"]
    s = {"status": "shown", "held": None, "method": p["choice"], "fit_day": day_str(pd.Timestamp(made)),
         "target_day": day_str(p["target"]), "hub": None, "market": None, "unit": "MW", "method_note": NOTES["demand"],
         "made_utc": iso(pd.Timestamp(made)), "inputs_through_utc": iso(p["inputs_through"]),
         "horizon_days": p["h"],
         "band": "the 10th and 90th percentile of the chosen method's own out-of-sample errors (the log of actual over forecast) at the same local hour, over the 365 days of target days held when the forecast is made",
         "band_coverage_pct": score.coverage(hr, "erw"),
         "tomorrow_columns": ["ts_utc", "local_hour", "erw", "lo", "hi", "operator"], "tomorrow": [],
         "operator_held": None,
         "history_columns": ["ts_utc", "local_day", "local_hour", "made_utc", "kind", "erw", "lo", "hi", "operator", "actual", "yesterday", "week_ago"],
         "history": history_rows(p, ledger),
         "summary": {"last_30_days": score.summary(hr, ["erw", "operator", "yesterday", "week_ago"], days=30),
                     "backtest": score.summary(hr, ["erw", "operator", "yesterday", "week_ago"])},
         "method_mae_last_2_years": {m: num(v, 2) for m, v in p["maes"].items()}}
    tm = p["tomorrow"]
    if tm is None:
        s["tomorrow_held"] = p["tomorrow_held"]
    else:
        c = p["choice"]
        s["tomorrow"] = [[iso(r["ts"]), int(r["hour"]), num(r[c]), num(r[c + "_lo"]), num(r[c + "_hi"]), num(r["operator"])] for _, r in tm.iterrows()]
        s["tomorrow_held"] = None
    # part F: the day's peak, tomorrow's and the record of past ones
    pk = p.get("peaks")
    peak = {"what": "the day's highest hourly demand and its local hour; a method's peak is the highest of its own hourly forecasts for the day, and the hour of it",
            "tomorrow": None, "last_2_years": None, "backtest": None}
    if tm is not None and len(tm):
        c = p["choice"]
        j = tm[c].idxmax()
        if pd.notna(j):
            peak["tomorrow"] = {"local_hour": int(tm.loc[j, "hour"]), "ts_utc": iso(tm.loc[j, "ts"]), "erw": num(tm.loc[j, c]),
                                "lo": num(tm.loc[j, c + "_lo"]), "hi": num(tm.loc[j, c + "_hi"])}
    if pk is not None and len(pk):
        meths = ["erw", "operator", "yesterday", "week_ago"]
        peak["last_2_years"] = score.peak_summary(pk, meths, days=score.CHOICE_DAYS)
        peak["backtest"] = score.peak_summary(pk, meths)
    s["peak"] = peak
    s["with_weather_known"] = p.get("weather")
    return s


def peak_rows(place, pk):
    """Score rows of the day's peak (series demand_peak): `hours` holds the count of days."""
    out = []
    for cut, days in (("all", None), ("last_2_years", score.CHOICE_DAYS)):
        sm = score.peak_summary(pk, SCORED, days=days)
        for m in SCORED:
            v = sm["methods"][m]
            out.append([place, "demand_peak", m, cut, "", sm["days"], v["mae"] if v else None, v["mape"] if v else None, None])
    return out


PRICE_SCORED = ["erw", "yesterday", "week_ago", "regression"]


def price_place(place, grid, pp, dem, ref, gas, made, evs):
    """One place's day-ahead price at its grid's hub: the backtest, the choice, score rows and tomorrow."""
    tz = data.place_tz(place, ref)
    s = pp[grid]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = price.place_forecasts(s, tz, dem[place], tz, gas, hp=1, hd=3)
    hr = demand.hourly(res)
    choice, maes = score.choose(hr, price.METHODS)
    for suf in ("", "_lo", "_hi"):
        hr["erw" + suf] = hr[choice + suf]
    hr["made_utc"] = pd.to_datetime(hr["day"] - pd.Timedelta(days=1)).dt.tz_localize("UTC") + pd.Timedelta(hours=price.PRICE_MADE_HOUR)
    rows = score.rows(place, "price", hr, PRICE_SCORED, evs, mape_floor=price.MAPE_FLOOR, spike_q=price.SPIKE_Q)
    rows += [[place, "price", "operator", "all", "", None, None, None, "not published: no operator publishes a forecast of its day-ahead price"]]
    frame = res["frame"]
    last_p = demand.last_whole_day(frame, tz)
    dframe = demand.local_frame(dem[place], tz)
    last_d = demand.last_whole_day(dframe, tz)
    target = pd.Timestamp(made).tz_convert(tz).tz_localize(None).normalize() + pd.Timedelta(days=1)
    hp, hd = int((target - last_p).days), int((target - last_d).days)
    tm, tm_held = None, None
    if 1 <= hp <= 7 and 1 <= hd <= 7:
        if (hp, hd) == (1, 3):
            res_h = res
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                res_h = price.place_forecasts(s, tz, dem[place], tz, gas, hp=hp, hd=hd)
        tm = demand.tomorrow(res_h, tz, target)
    else:
        tm_held = f"no data: the last whole day of prices held ({day_str(last_p)}) or of demand ({day_str(last_d)}) is more than 7 days before the target day"
    return {"place": place, "series": "price", "grid": grid, "tz": tz, "hr": hr, "choice": choice, "maes": maes, "rows": rows, "tomorrow": tm,
            "tomorrow_held": tm_held, "target": target, "h": hp, "hd": hd, "inputs_through": frame.loc[frame["day"] <= last_p, "ts"].max()}


def price_shown(p, made, ledger):
    hr = p["hr"]
    summ = {}
    for key, days in (("last_30_days", 30), ("backtest", None)):
        sm = score.summary(hr, ["erw", "yesterday", "week_ago"], days=days, mape_floor=price.MAPE_FLOOR)
        sm["mae"]["operator"] = None
        sm["mape"]["operator"] = None
        summ[key] = sm
    s = {"status": "shown", "held": None, "method": p["choice"], "fit_day": day_str(pd.Timestamp(made)), "target_day": day_str(p["target"]),
         "hub": data.HUBS[p["grid"]], "market": "day-ahead", "unit": "USD/MWh", "method_note": NOTES["price"],
         "made_utc": iso(pd.Timestamp(made)), "inputs_through_utc": iso(p["inputs_through"]), "horizon_days": p["h"], "demand_horizon_days": p["hd"],
         "band": "the 10th and 90th percentile of the chosen method's own out-of-sample errors (actual less forecast, USD/MWh) at the same local hour, over the 365 days of target days held when the forecast is made",
         "band_coverage_pct": score.coverage(hr, "erw"),
         "tomorrow_columns": ["ts_utc", "local_hour", "erw", "lo", "hi", "operator"], "tomorrow": [],
         "operator_held": "not published: no operator publishes a forecast of its day-ahead price",
         "history_columns": ["ts_utc", "local_day", "local_hour", "made_utc", "kind", "erw", "lo", "hi", "operator", "actual", "yesterday", "week_ago"],
         "history": history_rows(p, ledger), "summary": summ,
         "method_mae_last_2_years": {m: num(v, 2) for m, v in p["maes"].items()}}
    tm = p["tomorrow"]
    if tm is None:
        s["tomorrow_held"] = p["tomorrow_held"]
    else:
        c = p["choice"]
        s["tomorrow"] = [[iso(r["ts"]), int(r["hour"]), num(r[c], 2), num(r[c + "_lo"], 2), num(r[c + "_hi"], 2), None] for _, r in tm.iterrows()]
        s["tomorrow_held"] = None
    return s


def price_series(place):
    if place in PRICE_HELD:
        status, why = PRICE_HELD[place]
    elif place in PRICE_GRID:
        status, why = "not built", "not built yet: the price forecast is part E of chain 730"
    else:
        status, why = "not built", NO_MARKET
    return {"status": status, "held": why, "method": None, "fit_day": None, "target_day": None, "hub": None, "market": "day-ahead",
            "unit": "USD/MWh", "method_note": NOTES["price"], "made_utc": None, "inputs_through_utc": None, "band": None,
            "band_coverage_pct": None, "tomorrow_columns": ["ts_utc", "local_hour", "erw", "lo", "hi", "operator"], "tomorrow": None,
            "operator_held": "not published", "history_columns": ["ts_utc", "local_day", "local_hour", "made_utc", "kind", "erw", "lo", "hi", "operator", "actual", "yesterday", "week_ago"],
            "history": None, "summary": None}


def head(built):
    return {"contract": CONTRACT, "built": built, "tier": TIER, "label": LABEL}


def write_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), allow_nan=False)
    return os.path.getsize(path)


def write_tables(out, results, score_rows, built):
    """The tables asked of window A, as files in the data standard's series shape (validated by window A)."""
    os.makedirs(out, exist_ok=True)
    head_lines = [
        "# Energy Research Warehouse (ERW): the ERW forecast of hourly demand, the walk-forward backtest (tier derived: a model's output, not a published figure)",
        "# Shape: series (docs/datastandard.md v0). entity eia930:<code>; variable demand_forecast_mw; ts_utc the forecast hour's start (UTC); x_method the method; x_made_utc the hour the forecast is taken as made; x_horizon_days days between the last whole day read and the target day; x_lo, x_hi the band; x_kind backtest. Method: docs/methods/predict.md.",
        f"# Retrieved: {built.replace('-', '').replace(':', '')} (UTC) by warehouse/predict/run.py",
        "# Source: erw:predict the ERW's own forecast from eia930_ba_demand_hourly (Form EIA-930, U.S. Energy Information Administration), https://github.com/SamuelEnrique/erw/blob/main/docs/methods/predict.md",
        "# License: public (derived by the ERW from EIA data).",
    ]
    p = os.path.join(out, "predict_demand_backtest.csv")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(head_lines) + "\n")
        f.write("entity,variable,ts_utc,value,unit,freq,source,x_place,x_method,x_made_utc,x_horizon_days,x_lo,x_hi,x_kind\n")
        for r in results:
            ent = "eia930:" + r["place"].split("-", 1)[1].upper()
            hr = r["hr"]
            # the two regressions only: the two simple methods are the demand table's own hours, a lag apart
            for m in ["regression", "regression_recent"]:
                x = hr.dropna(subset=[m])
                for ts, v, lo, hi, made in zip(x["ts"], x[m], x[m + "_lo"], x[m + "_hi"], x["made_utc"]):
                    f.write(f"{ent},demand_forecast_mw,{iso(ts)},{v:.1f},MW,PT1H,erw:predict,{r['place']},{m},{iso(made)},2,"
                            f"{'' if not np.isfinite(lo) else f'{lo:.1f}'},{'' if not np.isfinite(hi) else f'{hi:.1f}'},backtest\n")
    q = os.path.join(out, "predict_scores.csv")
    with open(q, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Energy Research Warehouse (ERW): the ERW forecast's scores, every place, method and cut (tier derived)\n")
        f.write(f"# Retrieved: {built.replace('-', '').replace(':', '')} (UTC) by warehouse/predict/run.py. Method: docs/methods/predict.md, section \"The scores\".\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(score.COLUMNS)
        for row in score_rows:
            w.writerow(["" if v is None else v for v in row])
    return p, q


def write_price_table(out, prices, built):
    """The price regression's backtest, one row a place and hour (data request 5), in the series shape."""
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, "predict_price_backtest.csv")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Energy Research Warehouse (ERW): the ERW forecast of day-ahead hub prices, the walk-forward backtest of the regression (tier derived: a model's output, not a published figure)\n")
        f.write("# Shape: series (docs/datastandard.md v0). entity the hub; variable lmp_dam_forecast; ts_utc the hour's start (UTC); x_place the place whose demand forecast it reads; x_made_utc the hour the forecast is taken as made (14:00 UTC the day before); x_lo, x_hi the band. Method: docs/methods/predict_price.md.\n")
        f.write(f"# Retrieved: {built.replace('-', '').replace(':', '')} (UTC) by warehouse/predict/run.py\n")
        f.write("# Source: erw:predict, from the day-ahead hub prices of ERCOT, SPP and CAISO, eia930_ba_demand_hourly and eia_fuel_spot_prices (public)\n")
        f.write("# License: public (derived by the ERW from ERCOT, SPP, CAISO and EIA data).\n")
        f.write("entity,variable,ts_utc,value,unit,freq,source,x_place,x_method,x_made_utc,x_lo,x_hi,x_kind\n")
        for place, q in prices.items():
            hr = q["hr"].dropna(subset=["regression"])
            ent = data.HUBS[q["grid"]]
            for ts, v, lo, hi, made in zip(hr["ts"], hr["regression"], hr["regression_lo"], hr["regression_hi"], hr["made_utc"]):
                f.write(f"{ent},lmp_dam_forecast,{iso(ts)},{v:.2f},USD/MWh,PT1H,erw:predict,{place},regression,{iso(made)},"
                        f"{'' if not np.isfinite(lo) else f'{lo:.2f}'},{'' if not np.isfinite(hi) else f'{hi:.2f}'},backtest\n")
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description="The ERW forecast's daily run (chain 730)")
    ap.add_argument("--site-dir", default=SITE)
    ap.add_argument("--out-dir", default=OUT)
    ap.add_argument("--places", nargs="*")
    ap.add_argument("--now", help="the hour the forecast is made (UTC); by default the hour now")
    ap.add_argument("--no-ledger", action="store_true", help="a trial: append nothing to the ledger")
    a = ap.parse_args(argv)
    built = now_utc()
    made = pd.Timestamp(a.now or built).tz_convert("UTC").floor("h") if pd.Timestamp(a.now or built).tzinfo else pd.Timestamp(a.now or built).tz_localize("UTC").floor("h")
    places = a.places or PLACES
    print(f"{built} reading the tables (ERW_DATA_ROOT={data.DATA_ROOT})", flush=True)
    dem = data.demand_panel()
    op = data.operator_panel()
    ref, _ = data.reference()
    names = data.names()
    evs = events()
    wx = data.weather_panel()
    ledger = read_ledger(a.site_dir)
    results, srows, new_ledger = [], [], []
    for place in places:
        if place not in dem.columns:
            raise SystemExit(f"{place}: no demand held")
        p = demand_place(place, dem, op, ref, made, evs, wx)
        results.append(p)
        srows += p["rows"]
        if p["tomorrow"] is not None:
            c = p["choice"]
            for _, r in p["tomorrow"].iterrows():
                new_ledger.append({"series": "demand", "place": place, "target_day": day_str(p["target"]), "ts_utc": iso(r["ts"]),
                                   "local_hour": int(r["hour"]), "made_utc": iso(made), "inputs_through_utc": iso(p["inputs_through"]),
                                   "horizon_days": p["h"], "method": c, "erw": num(r[c]), "lo": num(r[c + "_lo"]), "hi": num(r[c + "_hi"])})
        print(f"  {place}: method {p['choice']} (MAE last two years {p['maes']}); target {day_str(p['target'])}, horizon {p['h']} days", flush=True)
    # the price, for the places whose grid's hub prices are public and current (part E)
    pp = data.price_panel()
    gas = data.gas_series()
    prices, new_price_ledger = {}, []
    for place in places:
        if place not in PRICE_GRID:
            srows += score.held_rows(place, "price", ["erw"], price_series(place)["held"])
            continue
        q = price_place(place, PRICE_GRID[place], pp, dem, ref, gas, made, evs)
        prices[place] = q
        srows += q["rows"]
        if q["tomorrow"] is not None:
            c = q["choice"]
            for _, r in q["tomorrow"].iterrows():
                new_price_ledger.append({"series": "price", "place": place, "target_day": day_str(q["target"]), "ts_utc": iso(r["ts"]),
                                         "local_hour": int(r["hour"]), "made_utc": iso(made), "inputs_through_utc": iso(q["inputs_through"]),
                                         "horizon_days": q["h"], "method": c, "erw": num(r[c], 2), "lo": num(r[c + "_lo"], 2), "hi": num(r[c + "_hi"], 2)})
        print(f"  {place} price ({data.HUBS[q['grid']]}): method {q['choice']} (MAE last two years {q['maes']}); target {day_str(q['target'])}, horizons {q['h']} and {q['hd']} days", flush=True)
    added = 0 if a.no_ledger else append_ledger(a.site_dir, new_ledger)
    added_p = 0 if a.no_ledger else append_ledger(a.site_dir, new_price_ledger, "price")
    ledger = read_ledger(a.site_dir)
    ledger_p = read_ledger(a.site_dir, "price")
    print(f"  ledger: {added} demand rows and {added_p} price rows added", flush=True)
    index_places = []
    for p in results:
        place = p["place"]
        kind, code = place.split("-", 1)
        ds = demand_series(p, made, ledger)
        ps = price_shown(prices[place], made, ledger_p) if place in prices else price_series(place)
        tables = ["eia930_ba_demand_hourly", "eia930_forecast_error_hourly"]
        if place in prices:
            tables += data.PRICE_TABLES + ["eia_fuel_spot_prices"]
        doc = dict(head(built), place=place, name=names.get(place), kind=kind, eia930=code.upper(), time=p["tz"],
                   tables=tables, series={"demand": ds, "price": ps})
        write_json(os.path.join(a.site_dir, f"{place}.json"), doc)
        index_places.append({"place": place, "name": names.get(place), "kind": kind, "eia930": code.upper(), "time": p["tz"], "file": f"{place}.json",
                             "series": {s: {k: v[k] for k in ("status", "held", "method", "fit_day", "target_day", "hub", "market")} for s, v in (("demand", ds), ("price", ps))}})
    idx = dict(head(built), method_notes=NOTES,
               made_rule=f"The demand forecast for a place's day is made at {DEMAND_MADE_HOUR}:00 UTC the day before, from the demand the warehouse holds then (through 23:00 local two days before the day); the day-ahead price forecast at {price.PRICE_MADE_HOUR}:00 UTC the day before, before any grid publishes its day-ahead prices for the day, from the prices of the day before (published two days before) and the demand through three days before; each file gives the hour it was made and the last hour it read.",
               band_rule="The band is the 10th and 90th percentile of the method's own past errors at the same local hour, over the last 365 days held: about eight hours in ten have fallen inside it, and each file prints the share that did.",
               choice_rule="For each place, the ERW's method with the lowest mean absolute error over the last two years of the walk-forward backtest, on the hours where every method and the operator's forecast are held.",
               places=index_places)
    write_json(os.path.join(a.site_dir, "index.json"), idx)
    span_first = min(r["hr"]["day"].min() for r in results)
    span_last = max(r["hr"]["day"].max() for r in results)
    sc = dict(head(built), method_notes=NOTES,
              span={"demand": {"first_day": day_str(span_first), "last_day": day_str(span_last)},
                    "price": {"first_day": day_str(min(q["hr"]["day"].min() for q in prices.values())) if prices else None,
                              "last_day": day_str(max(q["hr"]["day"].max() for q in prices.values())) if prices else None}},
              methods=[{"id": m, "what": METHOD_WORDS[m]} for m in SCORED],
              separate_lines={"with_weather_known": "the regression with the region's observed temperature added: it reads the target day's own weather, so it is not a forecast and never the ERW forecast; scored apart (series demand_weather_known, cuts all and last_2_years) on the hours its weather is held, beside the regression and the operator on the same hours"},
              metrics={"mae": "mean absolute error, in the series' unit", "mape": "mean absolute percent error, in percent"},
              mape_rule="Demand: every hour scored (demand is always above zero). Price: only hours whose actual price is at least 5 USD/MWh in size; a percent of a price near zero means nothing, and the cell is null when no hour qualifies.",
              cuts={"all": "every hour of the backtest held by every method", "last_2_years": "the last 730 days of the backtest (the days the method is chosen on)",
                    "month": "key YYYY-MM", "hour": "key 0 to 23, the place's clock, over the last two years",
                    "top10": "the place's ten highest-demand days of the backtest (by the day's peak hour)", "event": "key: the event's address on /events",
                    "spike": "price only: the hours above the grid's 99th percentile"},
              rows_columns=score.COLUMNS, rows=srows)
    write_json(os.path.join(a.site_dir, "scores.json"), sc)
    p, q = write_tables(a.out_dir, results, srows, built)
    if prices:
        write_price_table(a.out_dir, prices, built)
    print(f"{now_utc()} wrote {len(results)} place files, index.json, scores.json ({len(srows)} rows) to {a.site_dir}; tables {p}, {q}", flush=True)


if __name__ == "__main__":
    main()
