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
import predict_weather as wxmod  # noqa: E402
import predict_ws as wsmod  # noqa: E402
import wind_solar as wsrun  # noqa: E402

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
# more places (session 10603, Samuel's order of 27 November): every other balancing authority whose EIA-930 demand runs
# to the latest day held and covers at least two years (read 27 November 2026 in eia930_ba_demand_hourly); method note
# section 23 names the seven left out and why
MORE_BAS = ["AECI", "AVA", "AZPS", "BANC", "CHPD", "CPLW", "DOPD", "EPE", "FMPP", "GCPD", "GVL", "HST", "IID", "IPCO", "JEA",
            "LDWP", "LGEE", "NEVP", "NWMT", "PACW", "PGE", "PNM", "PSEI", "SC", "SCEG", "SCL", "SEC", "SPA", "SRP", "TAL",
            "TEC", "TEPC", "TIDC", "TPWR", "WALC"]
CORE_PLACES = [f"region-{r.lower()}" for r in data.REGIONS] + [f"ba-{b.lower()}" for b in LARGE_BAS]   # the 29 places of session 10600
PLACES = CORE_PLACES + [f"ba-{b.lower()}" for b in MORE_BAS]
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


WX_MIN_DAYS = 30
WX_WHAT = ("the regression with the weather (method note section 19), fitted on the airport's observed temperature of "
           "the days held when the forecast is made and applied with the National Weather Service's hourly forecast for "
           "the airport, as issued no later than 20:00 UTC the day before the target day (weather_forecast_issued_hourly, "
           "and the rows of weather_forecast_hourly whose issue was that early). A separate line, never the ERW forecast: "
           "it is scored only on the days such a forecast is held, which began in late September 2026, and below "
           "30 days the status says too few days to judge. with_airport_weather_known applies the same coefficients to "
           "the airport's observed temperature (not a forecast), so the cost of the weather forecast's own error is seen")


def weather_forecast_line(place, res, hr, tz, wxf, target):
    """The separate line "with the weather forecast" of one place (method note section 19): (file block, score rows)."""
    rows_f, obs = wxf
    airport = wxmod.PLACE_AIRPORT[place]
    M = res["M"]
    F, V = wxmod.forecast_matrix(rows_f, airport, tz, M.index, made_hour=DEMAND_MADE_HOUR)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        Pf, Po = demand.regression_weather_forecast(M, obs[airport], F, tz, res["h"])
    pos = pd.Series(np.arange(len(M)), index=M.index)
    i = pos.reindex(hr["day"]).to_numpy()
    k = hr["hour"].to_numpy()
    x = hr[["ts", "day", "hour", "actual", "erw", "operator", "regression", "regression_recent"]].copy()
    x["with_weather_forecast"] = Pf[i, k]
    x["with_airport_weather_known"] = Po[i, k]
    wm = ["with_weather_forecast", "with_airport_weather_known", "erw", "operator", "regression", "regression_recent"]
    c = score.common(x, wm)
    days = int(c["day"].nunique())
    sm = score.summary(x, wm)
    out = {"what": WX_WHAT, "airport": airport, "min_days": WX_MIN_DAYS, "days": days,
           "status": "scored" if days >= WX_MIN_DAYS else "too_few_days", "all": sm, "tomorrow": None, "tomorrow_issue_utc": None}
    srows = [[place, "demand_weather_forecast", m, "all", "", sm["hours"], sm["mae"][m], sm["mape"][m], None] for m in wm]
    j = len(M) - 1
    if pd.Timestamp(target) == M.index.max() and np.isfinite(Pf[j]).all():
        dh = demand.day_hours(tz, target)
        out["tomorrow"] = [[iso(t), int(hh), num(Pf[j, hh])] for t, hh in zip(dh["ts"], dh["hour"])]
        out["tomorrow_columns"] = ["ts_utc", "local_hour", "with_weather_forecast"]
        out["tomorrow_issue_utc"] = iso(pd.Timestamp(V[j]).tz_localize("UTC"))
    return out, srows


NET_WHAT = ("net demand: the demand less the output of wind and solar (method note section 20). The ERW's is its demand "
            "forecast less its wind and solar forecasts (warehouse/predict/wind_solar.py), all made at 20:00 UTC the day before "
            "from data through two days before; yesterday is the same hour of the latest whole day read, net; the operator's, "
            "where all three of its forecasts are held (Texas, from 27 September 2026), its demand forecast as filed on "
            "EIA-930 less ERCOT's wind and solar forecasts published at least 24 hours ahead. nmae_pct: the mean absolute "
            "error over the mean net demand of the same hours (a percent of an hour's net demand, which can be near zero, "
            "means nothing). No band: the three bands are not combined")


def net_place(place):
    """The wind and solar place whose footprint is the place's own: a region itself, and ERCO (Texas is ERCOT alone)."""
    if place.startswith("region-"):
        return place
    return "region-tex" if place == "ba-erco" else None


def net_demand_line(p, wsdf, made, wp):
    """The net demand block of one place and its score rows (series net_demand)."""
    place = p["place"]
    d = p["hr"][["ts", "day", "hour", "actual", "erw", "operator", "yesterday"]].copy()
    tm = {}
    for fuel in wsmod.FUELS:
        got = wsrun.one(wp, fuel, wsdf, made)
        if got is None:
            return {"what": NET_WHAT, "status": "not held", "held": f"not held: no {fuel} output is held for {wp}"}, []
        block, _, _, hw = got
        hw = hw[["ts", "actual", "erw", "operator", "yesterday"]].set_index("ts")
        for col in ("actual", "erw", "operator", "yesterday"):
            d[f"{fuel}_{col}"] = hw[col].reindex(pd.DatetimeIndex(d["ts"])).to_numpy()
        tm[fuel] = block.get("tomorrow")
    x = pd.DataFrame({"ts": d["ts"], "day": d["day"], "hour": d["hour"]})
    for col in ("actual", "erw", "operator", "yesterday"):
        x[col] = d[col] - d[f"wind_{col}"] - d[f"solar_{col}"]
    c = x.dropna(subset=["actual", "erw", "yesterday"]).reset_index(drop=True)
    rows = []
    out = {"what": NET_WHAT, "status": "shown", "wind_solar_place": wp, "last_2_years": None, "backtest": None, "with_operator": None,
           "tomorrow_columns": ["ts_utc", "local_hour", "erw"], "tomorrow": None}
    for cut, days in (("all", None), ("last_2_years", score.CHOICE_DAYS)):
        g = c if days is None else c[c["day"] > c["day"].max() - pd.Timedelta(days=days)]
        sm = wsrun.summary(g, ["erw", "yesterday"])
        out["backtest" if cut == "all" else cut] = sm
        for m in ("erw", "yesterday"):
            rows.append([place, "net_demand", m, cut, "", sm["hours"], sm["mae_mw"][m], sm["nmae_pct"][m], None])
    co = x.dropna(subset=["actual", "erw", "yesterday", "operator"])
    if len(co):
        sm = wsrun.summary(co, ["erw", "yesterday", "operator"])
        out["with_operator"] = sm
        for m in ("erw", "yesterday", "operator"):
            rows.append([place, "net_demand", m, "with_operator", "", sm["hours"], sm["mae_mw"][m], sm["nmae_pct"][m], None])
    else:
        rows.append([place, "net_demand", "operator", "all", "", None, None, None,
                     "not held: the warehouse holds no wind and solar forecast of this place's operator"])
    t = p.get("tomorrow")
    if t is not None and tm.get("wind") and tm.get("solar"):
        w = {r[0]: r[2] for r in tm["wind"]}
        s = {r[0]: r[2] for r in tm["solar"]}
        c0 = p["choice"]
        net = []
        for _, r in t.iterrows():
            k = iso(r["ts"])
            if k in w and k in s and None not in (w[k], s[k]) and np.isfinite(r[c0]):
                net.append([k, int(r["hour"]), num(r[c0] - w[k] - s[k])])
        out["tomorrow"] = net or None
    return out, rows


def demand_place(place, dem, op, ref, made, evs, wx=None, wxf=None):
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
    # part F: the operator's filing checked against the demand it forecasts (method note section 18); judges the
    # comparator only, never the choice above
    filing = score.filing_check(hr) if o is not None else None
    rows = score.rows(place, "demand", hr, SCORED, evs, sound=score.sound_months(filing) if filing else None)
    pk = score.peaks(hr, SCORED)
    # the peak's own choice, by the same rule on the peak's error (part F: "scored the same way"): the candidate whose
    # day peaks missed least over the last two years; "erw" in the peak's record is that method's peak
    peak_choice = choice
    if len(pk):
        pm = score.peak_summary(pk, demand.METHODS, days=score.CHOICE_DAYS)["methods"]
        peak_choice = min((v["mae"], m) for m, v in pm.items() if v)[1]
        pk["erw"] = pk[peak_choice]
        pk["erw_hour"] = pk[peak_choice + "_hour"]
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
    wfl = None
    if wxf is not None and place in wxmod.PLACE_AIRPORT:
        wfl, wrows = weather_forecast_line(place, res, hr, tz, wxf, target)
        rows += wrows
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
            "target": target, "h": h, "inputs_through": inputs_through, "last_whole_day": last, "res": res, "peaks": pk, "weather": weather, "peak_choice": peak_choice,
            "filing": filing, "weather_forecast": wfl}


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


def from_ledger(p, ledger, series="demand"):
    """Session 10000 (chain 701, done-line request 577): one forecast for a target day in the ledger and the place file.
    The ledger keeps the first making of a day and never rewrites it, while a second run on the same day (three landings
    on 26 November) rebuilt the place files with a newer making, so the page drew one forecast for tomorrow and its
    ledger kept another. When the ledger already holds this place's target day, the place file's tomorrow is the ledger's
    making: its values, band, method and the hour it was made. Returns (p, made_utc, method) changed, or (p, None, None)."""
    if ledger is None or ledger.empty or p.get("tomorrow") is None:
        return p, None, None
    lg = ledger[(ledger["series"] == series) & (ledger["place"] == p["place"]) & (ledger["target_day"] == day_str(p["target"]))]
    if lg.empty:
        return p, None, None
    m = str(lg["method"].iloc[0])
    tm = p["tomorrow"]
    op = dict(zip(pd.to_datetime(tm["ts"], utc=True), tm["operator"])) if "operator" in tm.columns else {}
    ts = pd.to_datetime(lg["ts_utc"], utc=True)
    t2 = pd.DataFrame({"ts": ts.values, "hour": lg["local_hour"].astype(int).values,
                       m: pd.to_numeric(lg["erw"], errors="coerce").values,
                       m + "_lo": pd.to_numeric(lg["lo"], errors="coerce").values,
                       m + "_hi": pd.to_numeric(lg["hi"], errors="coerce").values,
                       "operator": [op.get(t) for t in ts]})
    t2["ts"] = pd.to_datetime(t2["ts"], utc=True)
    return dict(p, tomorrow=t2.reset_index(drop=True), choice=m), str(lg["made_utc"].iloc[0]), m


def demand_series(p, made, ledger):
    now_choice = p["choice"]
    p, made_first, _ = from_ledger(p, ledger, "demand")
    hr = p["hr"]
    s = {"status": "shown", "held": None, "method": p["choice"], "fit_day": day_str(pd.Timestamp(made)),
         "target_day": day_str(p["target"]), "hub": None, "market": None, "unit": "MW", "method_note": NOTES["demand"],
         "made_utc": iso(pd.Timestamp(made)), "inputs_through_utc": iso(p["inputs_through"]),
         "horizon_days": p["h"],
         "band": "the 10th and 90th percentile of the chosen method's own out-of-sample errors (the log of actual over forecast) at the same local hour, over the 365 days of target days held when the forecast is made",
         "band_coverage_pct": score.coverage(hr, "erw"),
         "band_coverage": score.coverage_detail(hr, "erw"),
         "tomorrow_columns": ["ts_utc", "local_hour", "erw", "lo", "hi", "operator"], "tomorrow": [],
         "operator_held": None,
         "history_columns": ["ts_utc", "local_day", "local_hour", "made_utc", "kind", "erw", "lo", "hi", "operator", "actual", "yesterday", "week_ago"],
         "history": history_rows(p, ledger),
         "summary": {"last_30_days": score.summary(hr, ["erw", "operator", "yesterday", "week_ago"], days=30, also=SCORED),
                     "backtest": score.summary(hr, ["erw", "operator", "yesterday", "week_ago"], also=SCORED)},
         "method_mae_last_2_years": {m: num(v, 2) for m, v in p["maes"].items()}}
    if made_first is not None:
        s["made_utc"] = made_first
        s["tomorrow_from"] = ("the ledger: the forecast first made for this day, kept as made (a later run the same day does "
                              f"not replace it); the method chosen now is {now_choice}")
    tm = p["tomorrow"]
    if tm is None:
        s["tomorrow_held"] = p["tomorrow_held"]
    else:
        c = p["choice"]
        s["tomorrow"] = [[iso(r["ts"]), int(r["hour"]), num(r[c]), num(r[c + "_lo"]), num(r[c + "_hi"]), num(r["operator"])] for _, r in tm.iterrows()]
        s["tomorrow_held"] = None
    # part F: the day's peak, tomorrow's and the record of past ones
    pk = p.get("peaks")
    peak = {"what": "the day's highest hourly demand and its local hour; a method's peak is the highest of its own hourly forecasts for the day, and the hour of it; erw is the method chosen for the peak (method), the candidate whose day peaks missed least over the last two years",
            "method": p.get("peak_choice", p["choice"]), "tomorrow": None, "last_2_years": None, "backtest": None}
    if tm is not None and len(tm):
        # session 10000 (done-line request 577): tomorrow drawn from the ledger holds the ledger's method only, so its
        # peak is that making's highest hour, and says so
        c = p["choice"] if made_first is not None else p.get("peak_choice", p["choice"])
        if made_first is not None:
            peak["tomorrow_method"] = c
        j = tm[c].idxmax()
        if pd.notna(j):
            peak["tomorrow"] = {"local_hour": int(tm.loc[j, "hour"]), "ts_utc": iso(tm.loc[j, "ts"]), "erw": num(tm.loc[j, c]),
                                "lo": num(tm.loc[j, c + "_lo"]), "hi": num(tm.loc[j, c + "_hi"])}
    if pk is not None and len(pk):
        meths = ["erw", "operator", "yesterday", "week_ago", "regression", "regression_recent"]
        peak["last_2_years"] = score.peak_summary(pk, meths, days=score.CHOICE_DAYS)
        peak["backtest"] = score.peak_summary(pk, meths)
    s["peak"] = peak
    s["with_weather_known"] = p.get("weather")
    s["operator_filing"] = operator_filing(p)
    s["with_weather_forecast"] = p.get("weather_forecast")
    return s


def operator_filing(p):
    """The filing check of the operator's forecast (method note section 18) and the scores on the sound months."""
    fc = p.get("filing")
    if not fc:
        return None
    # the last two years counted as the score file's cut counts them: from the last day every scored method holds
    c = score.common(p["hr"], SCORED)
    recent = c[c["day"] > c["day"].max() - pd.Timedelta(days=score.CHOICE_DAYS)]
    ok = recent[recent["day"].dt.strftime("%Y-%m").isin(sorted(score.sound_months(fc)))]
    out = {"what": FILING_WHAT}
    out.update(fc)
    out["sound_last_2_years"] = score.summary(ok, ["erw", "operator", "yesterday", "week_ago"], also=SCORED)
    return out


def peak_rows(place, pk):
    """Score rows of the day's peak (series demand_peak): `hours` holds the count of days."""
    out = []
    for cut, days in (("all", None), ("last_2_years", score.CHOICE_DAYS)):
        sm = score.peak_summary(pk, SCORED, days=days)
        for m in SCORED:
            v = sm["methods"][m]
            out.append([place, "demand_peak", m, cut, "", sm["days"], v["mae"] if v else None, v["mape"] if v else None, None])
    return out


FILING_WHAT = ("the operator's day-ahead forecast as filed on Form EIA-930, set against the demand it forecasts: by month, the "
               "filed forecast's sum as a percent of the demand's over the hours both hold; a month more than 5 percent from 100 "
               "is flagged, a level that far off for a whole month being a break in the filing (a footprint or a definition), "
               "not a forecaster's error. shift_mape_last_2_years: the filed forecast's error with its hours moved by -1, 0 and "
               "1 (1: the forecast stamped an hour earlier set against each hour's demand). sound_last_2_years: the scores of "
               "the last two years on the unflagged months only. The ERW forecast reads none of this: it judges the comparator")


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
    now_choice = p["choice"]
    p, made_first, _ = from_ledger(p, ledger, "price")   # session 10000 (done-line request 577)
    hr = p["hr"]
    summ = {}
    for key, days in (("last_30_days", 30), ("backtest", None)):
        sm = score.summary(hr, ["erw", "yesterday", "week_ago"], days=days, mape_floor=price.MAPE_FLOOR, also=PRICE_SCORED)
        sm["mae"]["operator"] = None
        sm["mape"]["operator"] = None
        summ[key] = sm
    s = {"status": "shown", "held": None, "method": p["choice"], "fit_day": day_str(pd.Timestamp(made)), "target_day": day_str(p["target"]),
         "hub": p.get("hub") or data.HUBS[p["grid"]], "market": "day-ahead", "unit": "USD/MWh", "method_note": NOTES["price"],
         "made_utc": iso(pd.Timestamp(made)), "inputs_through_utc": iso(p["inputs_through"]), "horizon_days": p["h"], "demand_horizon_days": p["hd"],
         "band": "the 10th and 90th percentile of the chosen method's own out-of-sample errors (actual less forecast, USD/MWh) at the same local hour, over the 365 days of target days held when the forecast is made",
         "band_coverage_pct": score.coverage(hr, "erw"),
         "band_coverage": score.coverage_detail(hr, "erw"),
         "tomorrow_columns": ["ts_utc", "local_hour", "erw", "lo", "hi", "operator"], "tomorrow": [],
         "operator_held": "not published: no operator publishes a forecast of its day-ahead price",
         "history_columns": ["ts_utc", "local_day", "local_hour", "made_utc", "kind", "erw", "lo", "hi", "operator", "actual", "yesterday", "week_ago"],
         "history": history_rows(p, ledger), "summary": summ,
         "method_mae_last_2_years": {m: num(v, 2) for m, v in p["maes"].items()}}
    if made_first is not None:
        s["made_utc"] = made_first
        s["tomorrow_from"] = ("the ledger: the forecast first made for this day, kept as made (a later run the same day does "
                              f"not replace it); the method chosen now is {now_choice}")
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


def write_price_table(out, prices, built, name="predict_price_backtest.csv"):
    """The price regression's backtest, one row a place and hour (data request 5), in the series shape."""
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, name)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Energy Research Warehouse (ERW): the ERW forecast of day-ahead hub prices, the walk-forward backtest of the regression (tier derived: a model's output, not a published figure)\n")
        f.write("# Shape: series (docs/datastandard.md v0). entity the hub; variable lmp_dam_forecast; ts_utc the hour's start (UTC); x_place the place whose demand forecast it reads; x_made_utc the hour the forecast is taken as made (14:00 UTC the day before); x_lo, x_hi the band. Method: docs/methods/predict_price.md.\n")
        f.write(f"# Retrieved: {built.replace('-', '').replace(':', '')} (UTC) by warehouse/predict/run.py\n")
        f.write("# Source: erw:predict, from the day-ahead hub prices of ERCOT, SPP and CAISO, eia930_ba_demand_hourly and eia_fuel_spot_prices (public)\n")
        f.write("# License: public (derived by the ERW from ERCOT, SPP, CAISO and EIA data).\n")
        f.write("entity,variable,ts_utc,value,unit,freq,source,x_place,x_method,x_made_utc,x_lo,x_hi,x_kind\n")
        for place, q in prices.items():
            hr = q["hr"].dropna(subset=["regression"])
            ent = q.get("hub") or data.HUBS[q["grid"]]
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
    wxf = None
    if all(os.path.exists(data.table_path(t)) for t in (wxmod.ISSUED, wxmod.LATEST, wxmod.NOAA, wxmod.NWS_OBS)):
        wxf = (wxmod.issued_rows(), wxmod.observed())
    ledger = read_ledger(a.site_dir)
    results, srows, new_ledger = [], [], []
    for place in places:
        if place not in dem.columns:
            raise SystemExit(f"{place}: no demand held")
        p = demand_place(place, dem, op, ref, made, evs, wx, wxf)
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
    # part F: net demand (method note section 20), for the regions and ERCO, from the wind and solar forecast
    netd = {}
    if os.path.exists(data.table_path(wsmod.REGION_FUEL)):
        wsdf = wsmod.panels()
        for p in results:
            wp = net_place(p["place"])
            if wp is None:
                continue
            line, nrows = net_demand_line(p, wsdf, made, wp)
            netd[p["place"]] = line
            srows += nrows
    index_places = []
    for p in results:
        place = p["place"]
        kind, code = place.split("-", 1)
        ds = demand_series(p, made, ledger)
        ds["net_demand"] = netd.get(place)
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
              separate_lines_added={"with_weather_forecast": "series demand_weather_forecast (session 10602): the regression with the airport's observed temperature in the fit and the NWS forecast as issued by 20:00 UTC the day before in the forecast; scored only on the days such a forecast is held, never the ERW forecast (method note section 19)",
                                    "net_demand": "series net_demand (session 10602): the demand less wind and solar; for this series the column mape holds the mean absolute error over the mean net demand of the same hours, in percent (method note section 20)"},
              cuts_added={"operator_sound": "demand: the hours of the months whose operator filing passes the filing check (the filed forecast within 5 percent of the demand over the month; method note section 18)",
                          "operator_sound_last_2_years": "the same, over the last 730 days",
                          "with_operator": "net demand: the hours where the operator's demand, wind and solar forecasts are all held"},
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
