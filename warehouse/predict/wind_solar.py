"""ERW forecast (predict): the daily run of the wind and solar forecast (chain 730, part F). Writes
site/data/predict/wind_solar.json (the forecast for the next local day, the backtest's scores beside the operators'
own forecasts where held) and appends to site/data/predict/ledger_wind_solar.csv (every forecast as made, never
overwritten). Method note: docs/methods/predict_wind_solar.md. Reads only warehouse tables; writes no table.

Usage: python warehouse/predict/wind_solar.py [--now <UTC hour>] [--no-ledger] [--site-dir <dir>] [--places ...]
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
sys.path.append(os.path.join(HERE, "..", "derived"))
import predict_data as data  # noqa: E402
import predict_demand as demand  # noqa: E402
import predict_score as score  # noqa: E402
import predict_ws as ws  # noqa: E402

SITE = os.path.join(data.ROOT, "site", "data", "predict")
CONTRACT = "docs/state/page_files_predict.md"
NOTE = "docs/methods/predict_wind_solar.md"
MADE_HOUR = 20
CHOICE_DAYS = 730
HISTORY_DAYS = 35
# session 10603 (more places; data request 10 done by window A): every authority among the forecast's 64 places whose
# wind or solar output eia930_ba_wind_solar_hourly holds, except the six that are each a whole region (their region's
# entry shows them) and CISO (grid-caiso, CAISO's own hubs, shows it); method note predict_wind_solar.md section 8
BA_PLACES = [f"ba-{c.lower()}" for c in ["AECI", "AVA", "AZPS", "BANC", "BPAT", "CHPD", "CPLE", "CPLW", "DUK", "EPE", "FMPP", "FPC",
                                         "FPL", "IID", "IPCO", "JEA", "LDWP", "LGEE", "MISO", "NEVP", "NWMT", "PACE", "PACW", "PNM",
                                         "PSCO", "PSEI", "SC", "SCEG", "SEC", "SRP", "SWPP", "TAL", "TEC", "TEPC", "WALC"]]
PLACES = [f"region-{r.lower()}" for r in data.REGIONS] + ["grid-caiso"] + BA_PLACES
NAMES = {"grid-caiso": "CAISO, its three trading hubs (NP15, SP15, ZP26)"}
# session 10603, data request 11 (a) of chain 720: the place files that show each entry (a region shows its own; ba-erco is
# Texas; CAISO's own hubs are CISO's footprint, so ba-ciso shows grid-caiso); an authority that is a whole region is
# shown by its region's entry; an authority added shows its own
SHOWN_FOR = {"region-tex": ["region-tex", "ba-erco"], "grid-caiso": ["ba-ciso"], "region-ne": ["region-ne", "ba-isne"],
             "region-ny": ["region-ny", "ba-nyis"], "region-mida": ["region-mida", "ba-pjm"], "region-se": ["region-se", "ba-soco"],
             "region-ten": ["region-ten", "ba-tva"]}
# session 10603, data request 12 of chain 720: the words of the cuts of this file's rows
CUT_WORDS = {"all": "every hour of the backtest held by every method", "last_2_years": "the last 730 days of the backtest (the days the method is chosen on)",
             "month": "key YYYY-MM", "hour": "key 0 to 23, the place's clock, over the last two years",
             "with_operator": "the hours where the operator's forecast is also held", "with_operator_month": "the same, key YYYY-MM",
             "with_operator_available": "CAISO only: the same hours scored against the output available (actual plus the curtailment CAISO reports)"}
OPERATOR = {"region-tex": "ERCOT's short-term wind and solar forecasts (STWPF, STPPF), the newest posting published at least 24 hours before the hour (ercot_wind_solar_forecast, from 27 September 2026)",
            "grid-caiso": "CAISO's day-ahead market forecast of wind and solar (caiso_wind_solar_forecast, market run DAM, from June 2023), against CAISO's own actual output of the same hubs"}
TARGET = {"grid-caiso": "CAISO's actual wind or solar output, its three trading hubs summed (caiso_wind_solar_forecast, market run ACTUAL)"}
NOT_HELD = "not held: the warehouse holds no forecast of this region's wind or solar by its operator"
NOT_HELD_BA = "not held: the warehouse holds no forecast of this authority's wind or solar by its operator"
COLUMNS = ["place", "fuel", "method", "cut", "key", "hours", "mae_mw", "nmae_pct", "held"]
LEDGER_COLS = ["fuel", "place", "target_day", "ts_utc", "local_hour", "made_utc", "inputs_through_utc", "horizon_days", "method", "erw", "lo", "hi"]
METHOD_WORDS = {"erw": "the method the rule chose for the place and fuel (the lowest mean absolute error of the ERW's methods over the last two years)",
                "operator": "the operator's own forecast, where the warehouse holds it (Texas: ERCOT; grid-caiso: CAISO)",
                "yesterday": "the same local hour of the latest whole day read (two days before the target day)",
                "profile7": "the mean of the same local hour over the seven latest whole days read",
                "regression": "least squares by local hour on the latest day's hour and mean, the seven-day mean of the hour and its fourteen-day highest, refit every day on the 365 days before it, never below zero"}


def iso(t):
    return pd.Timestamp(t).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def num(x, nd=1):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return round(x, nd) if np.isfinite(x) else None


def place_tz(place):
    import region_files as rp
    if place == "grid-caiso":
        return "America/Los_Angeles"
    kind, code = place.split("-", 1)
    if kind == "ba":
        # the authority's own clock, as its place file counts its days (predict_data.place_tz)
        ref, _ = data.reference()
        return data.place_tz(place, ref)
    return rp.REGION_TZ[code.upper()]


def rows_for(place, fuel, x, methods, cut_list):
    out = []
    for cut, key, mask in cut_list:
        g = x[mask]
        for m in methods:
            n, mae, nmae = ws.metric(g, m)
            out.append([place, fuel, m, cut, key, n, mae, nmae, None])
    return out


def cuts(x):
    last = x["day"].max()
    recent = (x["day"] > last - pd.Timedelta(days=CHOICE_DAYS)).to_numpy()
    out = [("all", "", np.ones(len(x), dtype=bool)), ("last_2_years", "", recent)]
    mo = x["day"].dt.strftime("%Y-%m").to_numpy()
    for m in sorted(set(mo)):
        out.append(("month", m, mo == m))
    hrs = x["hour"].to_numpy()
    for h in range(24):
        out.append(("hour", str(h), recent & (hrs == h)))
    return out


def summary(x, methods, days=None):
    if days is not None and len(x):
        x = x[x["day"] > x["day"].max() - pd.Timedelta(days=days)]
    out = {"first_day": x["day"].min().strftime("%Y-%m-%d") if len(x) else None,
           "last_day": x["day"].max().strftime("%Y-%m-%d") if len(x) else None, "hours": int(len(x)), "mae_mw": {}, "nmae_pct": {}}
    for m in methods:
        _, mae, nmae = ws.metric(x, m)
        out["mae_mw"][m] = mae
        out["nmae_pct"][m] = nmae
    return out


def one(place, fuel, df, made, curt=None):
    """The backtest, choice, scores and tomorrow of one place and fuel."""
    a, o = ws.series_of(df, place, fuel)
    tz = place_tz(place)
    if a is None or a.dropna().empty:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = ws.place_forecasts(a.dropna(), tz)
    hr = ws.hourly(res, o)
    if o is None:
        hr["operator"] = np.nan
    last = hr["day"].max()
    rec = hr[hr["day"] > last - pd.Timedelta(days=CHOICE_DAYS)].dropna(subset=["actual"] + ws.METHODS)
    maes = {m: ws.metric(rec, m)[1] for m in ws.METHODS}
    # session 10603: the choice on the unrounded error (on the MAE rounded to 0.1 MW, every method of a place with a few MW
    # of output tied and the tie went to profile7 by name, the worse method; New York's solar was one); a true tie by name
    raw = {m: float((rec[m] - rec["actual"]).abs().mean()) for m in ws.METHODS if len(rec)}
    choice = min((v, m) for m, v in raw.items() if np.isfinite(v))[1]
    for suf in ("", "_lo", "_hi"):
        hr["erw" + suf] = hr[choice + suf]
    methods = ["erw"] + ws.METHODS
    c = hr.dropna(subset=["actual"] + methods).reset_index(drop=True)
    rows = rows_for(place, fuel, c, methods, cuts(c))
    op_held = o is not None and hr["operator"].notna().any()
    with_op, with_op_avail = None, None
    if op_held:
        co = hr.dropna(subset=["actual", "operator"] + methods).reset_index(drop=True)
        mo = co["day"].dt.strftime("%Y-%m").to_numpy()
        cl = [("with_operator", "", np.ones(len(co), dtype=bool))] + [("with_operator_month", m, mo == m) for m in sorted(set(mo))]
        rows += rows_for(place, fuel, co, methods + ["operator"], cl)
        with_op = summary(co, methods + ["operator"])
        if place == "grid-caiso" and curt is not None:
            # CAISO forecasts the output available; its actual is net of the curtailment it reports: the same hours
            # scored against actual plus curtailment, every method alike (method note, section 4)
            cv = curt[fuel].reindex(pd.DatetimeIndex(co["ts"])).to_numpy()
            ca = co.assign(actual=co["actual"].to_numpy() + cv)[np.isfinite(cv)].reset_index(drop=True)
            rows += rows_for(place, fuel, ca, methods + ["operator"], [("with_operator_available", "", np.ones(len(ca), dtype=bool))])
            with_op_avail = summary(ca, methods + ["operator"])
    else:
        rows += [[place, fuel, "operator", "all", "", None, None, None, NOT_HELD_BA if place.startswith("ba-") else NOT_HELD]]
    inside = None
    r2 = c[c["day"] > c["day"].max() - pd.Timedelta(days=CHOICE_DAYS)].dropna(subset=["erw_lo", "erw_hi"])
    if len(r2):
        inside = round(float(((r2["actual"] >= r2["erw_lo"]) & (r2["actual"] <= r2["erw_hi"])).mean() * 100), 1)
    frame = res["frame"]
    lastday = demand.last_whole_day(frame, tz)
    target = pd.Timestamp(made).tz_convert(tz).tz_localize(None).normalize() + pd.Timedelta(days=1)
    h = int((target - lastday).days)
    tomorrow, held = None, None
    if h == ws.H:
        tm = demand.tomorrow(res, tz, target)
        opv = o.reindex(pd.DatetimeIndex(tm["ts"])).to_numpy() if o is not None else np.full(len(tm), np.nan)
        tomorrow = [[iso(t), int(k), num(v), num(lo), num(hi), num(ov)] for t, k, v, lo, hi, ov in
                    zip(tm["ts"], tm["hour"], tm[choice], tm[choice + "_lo"], tm[choice + "_hi"], opv)]
        if all(r[2] is None for r in tomorrow):
            # session 10603 (data request 11 (b) of chain 720): no row of nulls; the reason instead
            gap = frame[(frame["day"] > target - pd.Timedelta(days=16)) & (frame["day"] <= lastday)]
            days = pd.date_range(target - pd.Timedelta(days=15), lastday, freq="D")
            short = [d.strftime("%Y-%m-%d") for d in days if int((gap["day"] == d).sum()) < len(demand.day_hours(tz, d))]
            tomorrow = None
            held = (f"no forecast: the method chosen ({choice}) reads every hour of the days before the target day, and the "
                    f"output held is missing hours on {', '.join(short) if short else 'a day it reads'}")
    else:
        held = f"no forecast: the last whole day held ({lastday.date()}) is {h} days before the target day, and this forecast reads exactly two"
    hist = c[c["day"] > c["day"].max() - pd.Timedelta(days=HISTORY_DAYS)]
    history = [[iso(r.ts), r.day.strftime("%Y-%m-%d"), int(r.hour), num(r.erw), num(r.erw_lo), num(r.erw_hi), num(r.operator), num(r.actual), num(r.yesterday)]
               for r in hist.itertuples()]
    inputs_through = frame.loc[frame["day"] <= lastday, "ts"].max()
    block = {"status": "shown", "method": choice, "method_mae_last_2_years": {m: num(v) for m, v in maes.items()},
             "target_series": TARGET.get(place, f"EIA-930's net generation from {fuel} for the authority (eia930_ba_wind_solar_hourly)" if place.startswith("ba-") else f"EIA-930's net generation from {fuel} for the region (eia930_region_fuel_hourly)"),
             "operator": OPERATOR.get(place) if op_held else None, "operator_held": None if op_held else (NOT_HELD_BA if place.startswith("ba-") else NOT_HELD),
             "made_utc": iso(made), "inputs_through_utc": iso(inputs_through), "target_day": target.strftime("%Y-%m-%d"), "horizon_days": h,
             "band": "the 10th and 90th percentile of the chosen method's own past errors (actual less forecast, MW) at the same local hour over 365 days, the low end not clipped, a plant's net output at night being a little below zero",
             "band_coverage_pct": inside,
             "band_coverage": score.coverage_detail(hr[hr["day"] <= c["day"].max()].dropna(subset=["actual"] + methods), "erw"),
             "tomorrow_columns": ["ts_utc", "local_hour", "erw", "lo", "hi", "operator"], "tomorrow": tomorrow, "tomorrow_held": held,
             "summary": {"last_2_years": summary(c, methods, days=CHOICE_DAYS), "backtest": summary(c, methods), "with_operator": with_op, "with_operator_available": with_op_avail},
             "history_columns": ["ts_utc", "local_day", "local_hour", "erw", "lo", "hi", "operator", "actual", "yesterday"],
             "history": history}
    ledger = []
    if tomorrow:
        for t, k, v, lo, hi, _ in tomorrow:
            ledger.append({"fuel": fuel, "place": place, "target_day": target.strftime("%Y-%m-%d"), "ts_utc": t, "local_hour": k,
                           "made_utc": iso(made), "inputs_through_utc": iso(inputs_through), "horizon_days": h, "method": choice,
                           "erw": v, "lo": lo, "hi": hi})
    return block, rows, ledger, hr


def read_ledger(site):
    p = os.path.join(site, "ledger_wind_solar.csv")
    if not os.path.exists(p):
        return pd.DataFrame(columns=LEDGER_COLS)
    return pd.read_csv(p, skiprows=data.ip.header_rows(p), dtype={"target_day": str})


def append_ledger(site, rows):
    """Append rows whose (fuel, place, target_day) the ledger does not hold; never rewrites a row."""
    p = os.path.join(site, "ledger_wind_solar.csv")
    have = read_ledger(site)
    held = set(zip(have["fuel"], have["place"], have["target_day"].astype(str)))
    new = [r for r in rows if (r["fuel"], r["place"], r["target_day"]) not in held]
    if not new:
        return 0
    first = not os.path.exists(p)
    os.makedirs(site, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        if first:
            f.write("# Energy Research Warehouse (ERW): the ERW forecast of wind and solar output, every forecast as made on its day, never overwritten (tier derived; a model's output, not a published figure)\n")
            f.write(f"# Written by warehouse/predict/wind_solar.py; contract {CONTRACT}; method {NOTE}. One row a fuel, place and UTC hour of the target day, MW; made_utc the hour the forecast was made; inputs_through_utc the last hour of output it read.\n")
            f.write("# Source: erw:predict, from eia930_region_fuel_hourly (U.S. Energy Information Administration, Form EIA-930, public) and caiso_wind_solar_forecast (California ISO, OASIS, public)\n")
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS, lineterminator="\n")
        if first:
            w.writeheader()
        for r in new:
            w.writerow(r)
    return len(new)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The ERW forecast of wind and solar output (chain 730, part F)")
    ap.add_argument("--site-dir", default=SITE)
    ap.add_argument("--places", nargs="*")
    ap.add_argument("--now")
    ap.add_argument("--no-ledger", action="store_true")
    a = ap.parse_args(argv)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    t = pd.Timestamp(a.now or built)
    made = (t.tz_convert("UTC") if t.tzinfo else t.tz_localize("UTC")).floor("h")
    df = ws.all_panels()
    curt = ws.curtailment() if os.path.exists(data.table_path(ws.CURTAIL)) else None
    names = data.names()
    places, rows, ledger = [], [], []
    for place in a.places or PLACES:
        entry = {"place": place, "name": NAMES.get(place) or names.get(place, place), "time": place_tz(place),
                 "shown_for": SHOWN_FOR.get(place, [place]), "fuels": {}}
        for fuel in ws.FUELS:
            got = one(place, fuel, df, made, curt)
            if got is None:
                entry["fuels"][fuel] = {"status": "not held", "held": f"not held: no {fuel} output is held for this place"}
                rows.append([place, fuel, "erw", "all", "", None, None, None, entry["fuels"][fuel]["held"]])
                continue
            block, r, lg, _ = got
            entry["fuels"][fuel] = block
            rows += r
            ledger += lg
            print(f"  {place} {fuel}: method {block['method']} {block['method_mae_last_2_years']}; operator {'held' if block['operator'] else 'not held'}", flush=True)
        places.append(entry)
    added = 0 if a.no_ledger else append_ledger(a.site_dir, ledger)
    doc = {"contract": CONTRACT, "built": built, "tier": "derived", "label": "ERW forecast", "method_note": NOTE,
           "made_rule": "made at 20:00 UTC the day before the target local day, from output through two days before it; no weather enters",
           "units": "MW; nmae_pct is the mean absolute error over the mean actual output of the same hours, in percent (a percent of each hour means nothing at night)",
           "methods": [{"id": m, "words": w} for m, w in METHOD_WORDS.items()],
           "cuts": CUT_WORDS, "places": places, "rows_columns": COLUMNS, "rows": rows}
    os.makedirs(a.site_dir, exist_ok=True)
    with open(os.path.join(a.site_dir, "wind_solar.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), allow_nan=False)
    print(f"{built} wrote wind_solar.json ({len(places)} places, {len(rows)} score rows); ledger: {added} rows added", flush=True)


if __name__ == "__main__":
    main()
