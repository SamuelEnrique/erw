"""ERW: EIA's day-ahead demand forecast beside the demand that came, every balancing authority and region, July 2018 on.

Session 8012, chain 505 (part D1). Form EIA-930 asks every balancing authority for its day-ahead demand forecast for
each hour ("Demand Forecast (MW)" in EIA's six-month BALANCE files). This builder sets that forecast beside the demand
the warehouse holds for the same hour (eia930_ba_demand_hourly, the demand the region files and the demand pages use)
and writes the miss: forecast less demand, in MW and in percent of the demand. A region's forecast is the sum of its
demand-filing authorities' forecasts, written for an hour only when every one of them that is needed then holds both
its forecast and its demand (the region files' rule for a region's demand). No forecast of the ERW's own: the forecast
is each authority's, as filed.

Tables: eia930_forecast_error_hourly (one row an entity and hour) and eia930_forecast_error_daily (one row an entity and
whole local day). Page files: site/data/regions/forecast/<region>.json and forecast/ba/<code>.json (contract: section 11
of docs/state/page_files_regions.md). Method: docs/methods/forecast_error.md.

    python warehouse/derived/forecast_error.py [--site-dir PATH] [--no-tables]
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import iso_prices as ip  # noqa: E402
import eia930_region_fuel_hourly as rf  # noqa: E402
import region_files as rp  # noqa: E402

SITE = os.path.join(ROOT, "site", "data", "regions")
METHOD = "docs/methods/forecast_error.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/forecast_error.md"
SOURCE = "erw:forecast_error"
FC = "Demand Forecast (MW)"
TABLES = ["eia930_forecast_error_hourly", "eia930_forecast_error_daily"]
COLS_H = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "x_level", "x_forecast_mw", "x_demand_mw", "x_screened"]
COLS_D = ["entity", "variable", "ts_utc", "value", "unit", "freq", "source", "x_level", "x_tz", "x_hours", "x_bias_mw", "x_mae_mw",
          "x_peak_forecast_mw", "x_peak_demand_mw", "x_peak_miss_pct"]
SCREEN = 3.0
SEASONS = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM", 5: "MAM", 6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}
SEASON_WORDS = {"DJF": "December to February", "MAM": "March to May", "JJA": "June to August", "SON": "September to November"}


def forecasts(log):
    """Every authority's hourly forecast, from every saved six-month file (the newest copy of each)."""
    frames, files = [], []
    for name in rf.files_between(first=(2018, 2)):
        got = rf.saved_copy(name)
        if not got:
            log(f"  {name}: no saved copy")
            continue
        d = pd.read_csv(got[0], usecols=["Balancing Authority", "UTC Time at End of Hour", FC], dtype=str, low_memory=False)
        d["ts"] = pd.to_datetime(d["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True) - pd.Timedelta(hours=1)
        d["f"] = pd.to_numeric(d[FC].str.replace(",", ""), errors="coerce")
        d = d[d["f"] > 0]
        frames.append(pd.DataFrame({"ba": d["Balancing Authority"], "ts": d["ts"], "f": d["f"]}))
        files.append(f"{name} (retrieved {got[1]})")
        log(f"  {name}: {len(d):,} hours with a forecast")
    f = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["ba", "ts"], keep="last")
    return f, files


def region_pair(region, ref, fc, dem):
    """(forecast, demand) of a region: the sums over its demand-filing authorities, held when each needed one holds both."""
    members = [c for c, r in ref.items() if r["region"] == region and r["us"] and not r["generation_only"]]
    fcols, dcols = {}, {}
    for c in members:
        if c in dem:
            dcols[c] = dem[c]
            fcols[c] = fc.get(c, pd.Series(dtype=float))
    if not dcols:
        return None, None
    D = pd.DataFrame(dcols)
    D = D.reindex(pd.date_range(D.index.min(), D.index.max(), freq="h"))
    F = pd.DataFrame({c: s.reindex(D.index) for c, s in fcols.items()})
    need = pd.DataFrame(False, index=D.index, columns=D.columns)
    for c in D.columns:
        r = ref[c]
        on = pd.Series(True, index=D.index)
        if r["activated"]:
            on &= D.index >= pd.Timestamp(r["activated"], tz=r["tz"] or "UTC")
        if r["retired"]:
            on &= D.index < pd.Timestamp(r["retired"], tz=r["tz"] or "UTC")
        need[c] = on
    held = ((D.notna() & F.notna()) | ~need).all(axis=1) & need.any(axis=1)
    return F.where(need).sum(axis=1, min_count=1).where(held), D.where(need).sum(axis=1, min_count=1).where(held)


def frame_of(f, d):
    x = pd.DataFrame({"f": f, "d": d}).dropna()
    x = x[(x["d"] > 0) & (x["f"] > 0)]
    x["miss"] = x["f"] - x["d"]
    x["ape"] = 100 * x["miss"].abs() / x["d"]
    # a forecast above three times the demand or below a third of it is taken as a filing error (the hourly table keeps
    # it, marked x_screened; no figure counts it): SCREEN in the method note
    x["screened"] = (x["f"] > SCREEN * x["d"]) | (x["f"] < x["d"] / SCREEN)
    return x


def stats(x):
    if not len(x):
        return {"hours": 0, "mape_pct": None, "wape_pct": None, "bias_pct": None, "mae_mw": None, "bias_mw": None}
    # wape: the absolute misses summed over the demand summed, percent, which a few hours of very small demand cannot swamp
    return {"hours": int(len(x)), "mape_pct": round(float(x["ape"].mean()), 2), "wape_pct": round(float(100 * x["miss"].abs().sum() / x["d"].sum()), 2),
            "bias_pct": round(float(100 * x["miss"].mean() / x["d"].mean()), 2),
            "mae_mw": round(float(x["miss"].abs().mean()), 1), "bias_mw": round(float(x["miss"].mean()), 1)}


def daily_rows(x, tz):
    x = x[~x["screened"]]
    loc = x.index.tz_convert(tz)
    y = x.assign(day=loc.strftime("%Y-%m-%d"))
    out = []
    for day, g in y.groupby("day"):
        a = pd.Timestamp(day, tz=tz)
        need = int(((a + pd.DateOffset(days=1)) - a) / pd.Timedelta(hours=1))
        if len(g) != need:
            continue
        pf, pd_ = float(g["f"].max()), float(g["d"].max())
        out.append({"day": day, "hours": need, "mape_pct": float(g["ape"].mean()), "bias_mw": float(g["miss"].mean()), "mae_mw": float(g["miss"].abs().mean()),
                    "peak_forecast_mw": pf, "peak_demand_mw": pd_, "peak_miss_pct": 100 * (pf - pd_) / pd_})
    return pd.DataFrame(out)


def doc_of(code, name, level, tz, x, days, weather, events, region):
    screened = int(x["screened"].sum())
    x = x[~x["screened"]]
    loc = x.index.tz_convert(tz)
    by_hour = [stats(x[loc.hour == h]) for h in range(24)]
    seasons = {s: stats(x[pd.Series(loc.month, index=x.index).map(SEASONS).to_numpy() == s]) for s in SEASON_WORDS}
    years = {str(y): stats(x[loc.year == y]) for y in sorted(set(loc.year))}
    doc = {"code": code, "name": name, "level": level, "region": region, "tz": tz, "first_hour": ip.utc_iso(x.index.min()), "last_hour": ip.utc_iso(x.index.max()),
           "overall": dict(stats(x), screened_hours=screened, screen=f"an hour whose forecast is above {SCREEN:g} times the demand or below a third of it is left out"), "by_hour": {k: [h[k] for h in by_hour] for k in ("mape_pct", "wape_pct", "bias_pct", "hours")},
           "by_season": {s: dict(v, words=SEASON_WORDS[s]) for s, v in seasons.items()}, "by_year": years,
           "daily": {"days": list(days["day"]) if len(days) else [], **{k: [round(float(v), 2) for v in days[k]] if len(days) else [] for k in ("mape_pct", "bias_mw", "peak_forecast_mw", "peak_demand_mw", "peak_miss_pct")}}}
    # the hottest and coldest days: the region's population-weighted temperature (region_weather_hourly), daily mean
    if weather is not None and len(days):
        t = weather.tz_convert(tz)
        tday = t.groupby(t.index.strftime("%Y-%m-%d")).agg(["mean", "count"])
        tday = tday[tday["count"] >= 20]["mean"]
        dd = days.set_index("day").join(tday.rename("temp_f"), how="inner")
        cols = ["temp_f", "mape_pct", "bias_mw", "peak_forecast_mw", "peak_demand_mw", "peak_miss_pct"]
        pick = lambda part: [{"day": i, **{k: round(float(r[k]), 2) for k in cols}} for i, r in part.iterrows()]
        doc["hottest_days"] = pick(dd.sort_values("temp_f", ascending=False).head(10)[cols])
        doc["coldest_days"] = pick(dd.sort_values("temp_f").head(10)[cols])
        doc["weather"] = {"table": "region_weather_hourly", "region": region, "basis": "the daily mean of the region's population-weighted hourly temperature, a day with at least 20 hours of it"}
    else:
        doc["hottest_days"], doc["coldest_days"] = None, None
        doc["weather"] = {"why": "no weather held for the region"}
    ev = []
    for e in events:
        a = pd.Timestamp(e["start"], tz=tz)
        b = pd.Timestamp(e["end"], tz=tz) + pd.DateOffset(days=1)
        w = x[(x.index >= a) & (x.index < b)]
        s = stats(w)
        if len(w):
            s.update({"peak_forecast_mw": round(float(w["f"].max()), 1), "peak_demand_mw": round(float(w["d"].max()), 1),
                      "peak_miss_pct": round(float(100 * (w["f"].max() - w["d"].max()) / w["d"].max()), 2)})
        ev.append({"event": e["event"], "title": e["title"], "start": e["start"], "end": e["end"], **s})
    doc["events"] = ev
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-dir", default=SITE)
    ap.add_argument("--no-tables", action="store_true", help="write the page files only (a trial)")
    a = ap.parse_args(argv)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"forecast_error_{run_id}.log"))
    ref, _ = rp.reference()
    index = json.load(open(os.path.join(a.site_dir, "index.json"), encoding="utf-8"))
    names = {b["code"]: b["name"] for b in index["bas"]}
    names.update({r["code"]: r["name"] for r in index["regions"]})
    log("reading the forecasts")
    fc_all, files = forecasts(log)
    fc = {c: g.set_index("ts")["f"].sort_index() for c, g in fc_all.groupby("ba")}
    ba_dem = rp.read("eia930_ba_demand_hourly", ["entity", "variable", "ts_utc", "value"], lambda d: d["variable"] == "demand_mw")
    dem = {e.split(":", 1)[1]: pd.Series(g["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(g["ts"])).sort_index() for e, g in ba_dem.groupby("entity")}
    weather = rp.read("region_weather_hourly", ["entity", "variable", "ts_utc", "value"], lambda d: d["variable"] == "temperature_f")
    wx = {e.split(":", 1)[1]: pd.Series(g["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(g["ts"])).sort_index() for e, g in weather.groupby("entity")}
    events = rp.events_list()
    hourly, daily_t = [], []
    os.makedirs(os.path.join(a.site_dir, "forecast", "ba"), exist_ok=True)
    built = rp.now()
    common = {"built": built, "tables": TABLES + ["eia930_ba_demand_hourly", "region_weather_hourly"], "method": METHOD, "license": "public"}
    held_bas = []
    for b in index["bas"]:
        c = b["code"]
        if not (b.get("us") and b.get("files_eia930")) or c not in fc or c not in dem:
            continue
        x = frame_of(fc[c], dem[c])
        if not len(x):
            continue
        tz = b["tz"] or "America/New_York"
        days = daily_rows(x, tz)
        held_bas.append(c)
        rp.write(a.site_dir, os.path.join("forecast", "ba", c.lower() + ".json"),
                 rp.clean({**common, **doc_of(c, names.get(c, c), "ba", tz, x, days, wx.get(b["region"]), events, b["region"])}))
        hourly.append(pd.DataFrame({"entity": f"eia930:{c}", "ts": x.index, "value": x["miss"].round(1), "x_level": "ba",
                                    "x_forecast_mw": x["f"].round(1), "x_demand_mw": x["d"].round(1), "x_screened": x["screened"].astype(int)}))
        if len(days):
            daily_t.append(days.assign(entity=f"eia930:{c}", x_level="ba", x_tz=tz))
    for r in rp.REGIONS:
        f, d = region_pair(r, ref, fc, dem)
        if f is None:
            continue
        x = frame_of(f, d)
        if not len(x):
            continue
        tz = rp.REGION_TZ[r]
        days = daily_rows(x, tz)
        rp.write(a.site_dir, os.path.join("forecast", r.lower() + ".json"),
                 rp.clean({**common, **doc_of(r, names.get(r, r), "region", tz, x, days, wx.get(r), events, r)}))
        hourly.append(pd.DataFrame({"entity": f"eia930:{r}", "ts": x.index, "value": x["miss"].round(1), "x_level": "region",
                                    "x_forecast_mw": x["f"].round(1), "x_demand_mw": x["d"].round(1), "x_screened": x["screened"].astype(int)}))
        if len(days):
            daily_t.append(days.assign(entity=f"eia930:{r}", x_level="region", x_tz=tz))
    log(f"page files: {len(held_bas)} authorities and the regions")
    if not a.no_tables:
        h = pd.concat(hourly, ignore_index=True)
        h["ts_utc"] = h["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        h = h.assign(variable="demand_forecast_miss_mw", unit="MW", freq="PT1H", source=SOURCE)[COLS_H].sort_values(["entity", "ts_utc"])
        dd = pd.concat(daily_t, ignore_index=True)
        dd = dd.assign(ts_utc=dd["day"] + "T00:00:00Z", variable="demand_forecast_ape_pct", value=dd["mape_pct"].round(3), unit="pct", freq="P1D", source=SOURCE,
                       x_hours=dd["hours"], x_bias_mw=dd["bias_mw"].round(1), x_mae_mw=dd["mae_mw"].round(1), x_peak_forecast_mw=dd["peak_forecast_mw"].round(1),
                       x_peak_demand_mw=dd["peak_demand_mw"].round(1), x_peak_miss_pct=dd["peak_miss_pct"].round(3))[COLS_D].sort_values(["entity", "ts_utc"])
        rule = ("The forecast is the authority's own day-ahead demand forecast for the hour as filed on Form EIA-930 (EIA's six-month BALANCE files, column "
                "\"Demand Forecast (MW)\"); the demand is the warehouse's eia930_ba_demand_hourly for the same hour. Only hours with both above zero. A region's "
                "forecast and demand are sums over its demand-filing authorities, held for an hour only when each needed authority holds both. Method: docs/methods/forecast_error.md.")
        common_lines = [f"Built {run_id} (UTC) by warehouse/derived/forecast_error.py", f"Run log: warehouse/output/logs/forecast_error_{run_id}.log",
                        f"Source: {SOURCE} ERW derived table, {METHOD_URL}", "Derived from: eia930_ba_demand_hourly",
                        "Forecasts from: U.S. Energy Information Administration, Form EIA-930, the six-month BALANCE files saved in warehouse/raw/eia930_region_hourly (column Demand Forecast (MW)): " + "; ".join(files),
                        "License: public (derived by the ERW from U.S. Energy Information Administration data, Form EIA-930)."]
        head_h = ["Energy Research Warehouse (ERW): each balancing authority's and region's day-ahead demand forecast beside the demand that came, by hour, July 2018 on (session 8012, chain 505)",
                  "Shape: series (docs/datastandard.md v0). entity eia930:<code>, variable demand_forecast_miss_mw (value: forecast less demand, MW; above zero the forecast was high), "
                  "x_forecast_mw, x_demand_mw, x_level (ba or region), x_screened (1: the forecast is above three times the demand or below a third of it, taken as a filing error and counted in no figure). " + rule]
        head_d = ["Energy Research Warehouse (ERW): each balancing authority's and region's day-ahead demand forecast against the demand that came, by whole local day, July 2018 on (session 8012, chain 505)",
                  "Shape: series (docs/datastandard.md v0). entity eia930:<code>, variable demand_forecast_ape_pct (value: the mean over the day's hours of the absolute miss over the demand, percent), "
                  "ts_utc the local day at 00:00:00Z (x_tz its zone), x_hours (23, 24 or 25: only whole days), x_bias_mw (mean of forecast less demand), x_mae_mw (mean absolute miss), "
                  "x_peak_forecast_mw and x_peak_demand_mw (the day's highest of each), x_peak_miss_pct. A day with a screened hour (see the hourly table) is not written. " + rule]
        import interchange_pairs as pairs  # the same writer as the pair tables: header lines, then the rows
        pairs.fmt_csv(h, os.path.join(ip.OUT_DIR, "eia930_forecast_error_hourly.csv"), head_h + common_lines + [f"File holds {len(h)} rows, one build; rebuilt whole by each run."], log)
        pairs.fmt_csv(dd, os.path.join(ip.OUT_DIR, "eia930_forecast_error_daily.csv"), head_d + common_lines + [f"File holds {len(dd)} rows, one build; rebuilt whole by each run."], log)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="The day-ahead demand forecast beside the demand that came, every balancing authority and region (docs/methods/forecast_error.md)",
                                report_url=METHOD_URL, document_list="docs/methods/forecast_error.md", license="public", tables=TABLES)])
        log(f"eia930_forecast_error_hourly {len(h):,} rows; eia930_forecast_error_daily {len(dd):,} rows")
    log.close()
    print(f"forecast files: {len(held_bas)} authorities and the regions under {os.path.relpath(os.path.join(a.site_dir, 'forecast'), ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
