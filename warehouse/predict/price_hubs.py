"""ERW forecast (predict): the day-ahead price at more hubs (session 10603, chain 730, Samuel's order of 27 November 2026,
"more places"). Method note: docs/methods/predict_price.md, section 10. Contract: docs/state/page_files_predict.md.

The place files carry the day-ahead price at one hub a grid (ERCOT HB_NORTH, SPP North Hub, CAISO SP15; section 1).
This run makes the same forecast, by the same code (warehouse/predict/run.py's price_place and price_shown: the same
methods, made at 14:00 UTC the day before, the same choice, band and scores), at the other hubs of those grids whose
prices the warehouse holds over at least two years (predict_rt.MORE_HUBS: ERCOT Houston, South and West, CAISO NP15),
each read with its grid's demand (ERCO's for ERCOT's hubs, CISO's for NP15), as the grid's first hub is.

Writes site/data/predict/price_hubs.json and appends to site/data/predict/ledger_price_hubs.csv (never rewritten).
Reads only warehouse tables; writes no table.

Usage: python warehouse/predict/price_hubs.py [--now <UTC hour>] [--no-ledger] [--site-dir <dir>] [--out-dir <dir>]
"""
import argparse
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import predict_data as data  # noqa: E402
import predict_price as price  # noqa: E402
import predict_rt as rtm  # noqa: E402
import run  # noqa: E402

NOTE = "docs/methods/predict_price.md"
HUB_DEMAND = {"ercot-houston": "ba-erco", "ercot-south": "ba-erco", "ercot-west": "ba-erco", "caiso-np15": "ba-ciso"}
WHAT = ("the ERW forecast of the day-ahead price at more hubs of the three public grids (method note predict_price.md "
        "section 10): the same methods, hour of making, choice, band and scores as the place files' price series, each "
        "hub read with its grid's demand")
WORDS = {"erw": "the ERW method the rule chose for the hub: the lowest mean absolute error of yesterday, week_ago and the regression over the last two years of the backtest",
         "yesterday": "the hub's day-ahead price at the same local hour of the day before the target day (published before the forecast is made)",
         "week_ago": "the hub's day-ahead price at the same local hour seven days before the target day",
         "regression": "the least-squares regression of predict_price.md section 3, one a local hour, refit for every target day on the 730 days before it"}


def one(hub, pp, dem, ref, gas, made, evs, ledger):
    q = run.price_place(HUB_DEMAND[hub], hub, pp, dem, ref, gas, made, evs)
    place = f"hub-{hub}"
    q["rows"] = [[place] + r[1:] for r in q["rows"]]
    q["place"] = place
    q["hub"] = rtm.MORE_HUBS[hub]
    block = run.price_shown(q, made, ledger)
    block = dict({"place": place, "grid": hub, "demand_place": HUB_DEMAND[hub], "time": q["tz"]}, **block)
    new = []
    if q["tomorrow"] is not None:
        c = q["choice"]
        for _, r in q["tomorrow"].iterrows():
            new.append({"series": "price", "place": place, "target_day": run.day_str(q["target"]), "ts_utc": run.iso(r["ts"]),
                        "local_hour": int(r["hour"]), "made_utc": run.iso(made), "inputs_through_utc": run.iso(q["inputs_through"]),
                        "horizon_days": q["h"], "method": c, "erw": run.num(r[c], 2), "lo": run.num(r[c + "_lo"], 2), "hi": run.num(r[c + "_hi"], 2)})
    return block, q, new


def main(argv=None):
    ap = argparse.ArgumentParser(description="The ERW forecast of the day-ahead price at more hubs (session 10603)")
    ap.add_argument("--site-dir", default=run.SITE)
    ap.add_argument("--now")
    ap.add_argument("--no-ledger", action="store_true")
    ap.add_argument("--out-dir", default=run.OUT, help="where the regression's backtest file is written (not a warehouse table)")
    a = ap.parse_args(argv)
    built = run.now_utc()
    t = pd.Timestamp(a.now or built)
    made = (t.tz_convert("UTC") if t.tzinfo else t.tz_localize("UTC")).floor("h")
    dem = data.demand_panel()
    ref, _ = data.reference()
    gas = data.gas_series()
    evs = run.events()
    pp = data.price_panel(rtm.RT_HUBS)
    ledger = run.read_ledger(a.site_dir, "price_hubs")
    hubs, rows, new, qs = [], [], [], {}
    for hub in rtm.MORE_HUBS:
        block, q, lg = one(hub, pp, dem, ref, gas, made, evs, ledger)
        hubs.append(block)
        rows += q["rows"]
        qs[q["place"]] = q
        new += lg
        print(f"  {hub} ({rtm.MORE_HUBS[hub]}): method {q['choice']} (MAE last two years {q['maes']}); target {run.day_str(q['target'])}", flush=True)
    added = 0 if a.no_ledger else run.append_ledger(a.site_dir, new, "price_hubs")
    if added:
        ledger = run.read_ledger(a.site_dir, "price_hubs")
    doc = dict(run.head(built), what=WHAT, method_note=NOTE + ", section 10",
               made_rule=f"made at {price.PRICE_MADE_HOUR}:00 UTC the day before the target local day, before any grid publishes its day-ahead prices for the day, as in the place files",
               methods=[{"id": m, "what": w} for m, w in WORDS.items()],
               cuts=run.PRICE_CUT_WORDS, hubs=hubs, rows_columns=run.score.COLUMNS, rows=rows)
    size = run.write_json(os.path.join(a.site_dir, "price_hubs.json"), doc)
    bt = run.write_price_table(a.out_dir, qs, built, "predict_price_hubs_backtest.csv")
    print(f"{run.now_utc()} wrote price_hubs.json ({len(hubs)} hubs, {len(rows)} score rows, {size:,} bytes), {bt}; ledger: {added} rows added", flush=True)


if __name__ == "__main__":
    main()
