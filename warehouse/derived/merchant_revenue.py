#!/usr/bin/env python3
"""Cost of power v2, the seller's side (session 51): what a merchant generator earns at each ISO's main hub.

Energy Research Warehouse (ERW). Writes one derived series table and the page's snapshot:

    warehouse/output/merchant_revenue_monthly.csv   per ISO main hub, asset type and local month (variables
                                                    <asset>_<metric>, below); tier derived, public; never in Supabase
    site/data/merchant_snapshot.json                what /cost-of-power/seller reads (the table's rows, the hourly
                                                    prices and Henry Hub for the peaker at the reader's heat rate,
                                                    the ERCOT stress days), as /network reads its own snapshot

Assets, each per 1 MW (the page scales by the reader's size; every result here is linear in MW):
    solar, wind      hourly output per MW installed: EIA-930's hourly generation by fuel (the BA workbooks' "Adjusted
                     SUN Gen" and "Adjusted WND Gen", already on disk under warehouse/raw/eia930_emissions/) over the
                     fuel's installed nameplate in that balancing authority that month (EIA-860M, operating and
                     retired generators, by operating and retirement month). A fleet average, not a site.
    battery_2h,      the perfect-foresight optimum of lib/battery.ts's rules at asset scale: hourly, full power or
    battery_4h       nothing, round trip 86 percent (Lazard LCOS v10.0, utility-scale 100 MW / 400 MWh, low end),
                     each local day from empty, at most one full cycle a day. An upper bound: no one knows the day's
                     prices in advance.
    peaker           runs in each hour whose hub price exceeds Henry Hub (that day, or the last trading day before)
                     times the heat rate plus the variable O&M: defaults 10.725 MMBtu/MWh and 4.25 USD/MWh, the
                     midpoints of Lazard LCOE v18.0's gas peaking (new build) ranges. No start costs, minimum run,
                     ramp limits, outages or gas basis.

Metrics per asset and month: revenue_per_mw (USD/MW: sales less purchases or fuel and variable O&M), sales_per_mw
(USD/MW), energy_per_mw (MWh/MW delivered), capture_price (sales / energy, USD/MWh), flat_price (the mean of the
month's priced hours, USD/MWh), capture_rate (capture_price / flat_price, pct), hours (priced hours used, count; for
batteries, days), hours_in_month (count). Prices: the real-time hourly price of cost_of_power.py (prices_of, hourly):
ERCOT's history from 2015 joined to the rolling table; the other ISOs' iso_hub_prices_history (from 2025-09) joined
to theirs. PJM is excluded (internal prices). docs/methods/cost_of_power.md, "The seller's side".

    python warehouse/derived/merchant_revenue.py
"""

import datetime as dt
import json
import math
import os
import sys
import traceback

import numpy as np
import openpyxl
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402  (session 82: California's hours that EIA holds one hour late)
import cost_of_power as cp  # noqa: E402
import event_window as ew  # noqa: E402  (the events' windows)
import eia930_emissions as em  # noqa: E402
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402

NAME = "merchant_revenue_monthly"
SOURCE = "erw:merchant_revenue"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md"
SNAPSHOT = os.path.join(ROOT, "site", "data", "merchant_snapshot.json")
BA = {"ercot": "ERCO", "caiso": "CISO", "isone": "ISNE", "miso": "MISO", "nyiso": "NYIS", "spp": "SWPP"}
SHAPE_START = "2018-07-01"  # EIA-930's generation by fuel begins on 2018-07-01
RTE = 0.86                  # Lazard LCOS v10.0, utility-scale standalone 100 MW / 400 MWh: efficiency 92% to 86%
DURATIONS = [2, 4]          # the two utility-scale durations Lazard prices (100 MW / 200 MWh and 100 MW / 400 MWh)
HEAT_RATE = 10.725          # MMBtu/MWh: Lazard LCOE v18.0, gas peaking (new build), 10,275 to 11,175 Btu/kWh, midpoint
VOM = 4.25                  # USD/MWh: the same, variable O&M 3.50 to 5.00, midpoint
NEAR = 0.9                  # a month counts when it holds at least this share of its hours (the page's rule)
STRESS = ["uri_2021", "elliott_2022", "ercot_heat_2023"]
r4 = pb.r4


def log_open(run_id):
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    return ip.Log(os.path.join(ip.LOG_DIR, f"merchant_revenue_{run_id}.log"))


def workbook_of(ba):
    """The BA workbook the emissions extract was read from (its first header line names it)."""
    ex = em.latest_extract(ba.lower())
    if ex is None:
        raise RuntimeError(f"no extract of {ba} under warehouse/raw/eia930_emissions/")
    with open(ex, encoding="utf-8") as f:
        first = f.readline()
    rel = first.split("ERW extract of ", 1)[1].split(",", 1)[0].strip().replace("\\", "/")
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise RuntimeError(f"{ba}: the workbook {rel} named by {ex} is not on this machine")
    return path, ex


def fuel_hours(path):
    """{UTC hour start: (solar MWh, wind MWh)} from the workbook's Adjusted SUN and WND columns (None where empty)."""
    wb = openpyxl.load_workbook(path, read_only=True)
    rows = wb[em.SHEET].iter_rows(values_only=True)
    hdr = list(next(rows))
    it, isun, iwnd = hdr.index("UTC time"), hdr.index("Adjusted SUN Gen"), hdr.index("Adjusted WND Gen")
    ts, sun, wnd = [], [], []
    for r in rows:
        if r[it] is None:
            continue
        ts.append(pd.Timestamp(r[it], tz="UTC") - pd.Timedelta(hours=1))  # EIA's UTC time is the hour's end
        sun.append(r[isun])
        wnd.append(r[iwnd])
    wb.close()
    df = pd.DataFrame({"sun": pd.to_numeric(pd.Series(sun), errors="coerce").values,
                       "wnd": pd.to_numeric(pd.Series(wnd), errors="coerce").values}, index=pd.DatetimeIndex(ts))
    return df[~df.index.duplicated()].loc[SHAPE_START:]


def capacity(gens, ba, src, month):
    """Nameplate MW of the fuel's generators in the BA operating at the start of the month."""
    ms = pd.Timestamp(month + "-01")
    g = gens[(gens["balancing_authority"] == ba) & (gens["energy_source"] == src)]
    return float(g.loc[(g["start"] <= ms) & (g["ret"].isna() | (g["ret"] > ms)), "nameplate_mw"].sum())


def read_gens():
    def rd(name):
        p = os.path.join(ip.OUT_DIR, name + ".csv")
        n = 0
        with open(p, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
        return pd.read_csv(p, skiprows=n, low_memory=False)
    op, re_ = rd("eia860m_operating_generators"), rd("eia860m_retired_generators")
    g = pd.concat([op.assign(ret=pd.NaT), re_.assign(ret=pd.to_datetime(re_["retirement_date"], errors="coerce"))], ignore_index=True)
    g["start"] = pd.to_datetime(g["operating_year"].astype("Int64").astype(str) + "-"
                                + g["operating_month"].astype("Int64").astype(str).str.zfill(2) + "-01", errors="coerce")
    vint = sorted(set(op["vintage"].dropna().astype(str)))
    return g, vint


def battery_day(prices, hours, rte=RTE):
    """The perfect-foresight optimum of one day for 1 MW of `hours` duration, hourly, from empty, at most one full cycle
    (the energy taken out of the battery is at most its usable energy). Returns (net cash, sales, purchases, delivered
    MWh, actions). Each state of charge and cycled energy is its exact value; two paths meeting keep the better."""
    eta = math.sqrt(rte)
    layer = {(0, 0): (0.0, 0.0, 0.0, 0.0, None, 0, 0.0, 0.0)}  # key: (soc, cycled) in 1e-9 units
    for p in prices:
        nxt = {}
        for (ks, kc), node in layer.items():
            soc, cyc = ks / 1e9, kc / 1e9
            value, sales, buys, deliv = node[0], node[1], node[2], node[3]
            for a in (1, 0, -1):
                s2, c2, sale, buy, d = soc, cyc, 0.0, 0.0, 0.0
                if a == 1:
                    stored = min(eta, hours - soc)
                    if stored <= 0:
                        continue
                    s2, buy = soc + stored, stored / eta * p
                elif a == -1:
                    taken = min(1 / eta, soc, hours - cyc)
                    if taken <= 0:
                        continue
                    s2, c2, d = soc - taken, cyc + taken, taken * eta
                    sale = d * p
                k = (round(s2 * 1e9), round(c2 * 1e9))
                v = value + sale - buy
                had = nxt.get(k)
                if had is None or v > had[0]:
                    nxt[k] = (v, sales + sale, buys + buy, deliv + d, node, a, s2, c2)
        layer = nxt
    best = max(layer.values(), key=lambda n: n[0])
    acts, n = [], best
    while n[4] is not None:
        acts.append(n[5])
        n = n[4]
    return best[0], best[1], best[2], best[3], acts[::-1]


def henry_hub():
    s = pb.read_table("eia_fuel_spot_prices")
    s = s[(s["entity"] == "eia:henry_hub") & (s["variable"] == "spot_price")]
    day = s["ts"].dt.strftime("%Y-%m-%d")
    return pd.Series(s["value"].values, index=pd.to_datetime(day)).sort_index(), s


def build_iso(iso, gens, hh, log, left):
    tz = pb.TZ[iso]
    hub = pb.MAIN[iso]
    df, table = cp.prices_of(iso, "rtm", log)
    price = cp.hourly(df)
    if not len(price):
        raise RuntimeError(f"{iso}: no complete hourly real-time price")
    path, ex = workbook_of(BA[iso])
    fuel = fuel_hours(path)
    if iso == "caiso":
        fuel = cj.true_hours(fuel)  # session 82: EIA's California values of 2023-11 to 2025-12-02 sit one hour late
    log(f"  {iso}: {len(price)} hourly prices {price.index.min()} to {price.index.max()}; fuel hours {len(fuel)} from {os.path.relpath(path, ROOT)}")
    start = max(price.index.min(), pd.Timestamp(SHAPE_START, tz="UTC"))
    h = pd.DataFrame({"p": price}).loc[start:]
    h = h.join(fuel, how="left")
    loc = h.index.tz_convert(tz)
    h["month"] = loc.strftime("%Y-%m")
    h["day"] = loc.strftime("%Y-%m-%d")
    # Henry Hub: the day's price, or the last trading day's before it
    days = pd.to_datetime(sorted(h["day"].unique()))
    hhd = hh.reindex(hh.index.union(days)).sort_index().ffill().reindex(days)
    h["hh"] = h["day"].map(dict(zip(days.strftime("%Y-%m-%d"), hhd.values)))
    caps = {}
    for m in sorted(h["month"].unique()):
        caps[m] = (capacity(gens, BA[iso], "SUN", m), capacity(gens, BA[iso], "WND", m))
    h["sun_mw"] = h["month"].map(lambda m: caps[m][0])
    h["wnd_mw"] = h["month"].map(lambda m: caps[m][1])
    h["solar"] = np.where(h["sun_mw"] > 0, h["sun"] / h["sun_mw"], np.nan)
    h["wind"] = np.where(h["wnd_mw"] > 0, h["wnd"] / h["wnd_mw"], np.nan)
    over = {k: int((h[k] > 1).sum()) for k in ("solar", "wind")}
    neg = {k: int((h[k] < 0).sum()) for k in ("solar", "wind")}
    log(f"  {iso}: hours with output above installed nameplate (EIA-860M lags new plants): solar {over['solar']}, wind {over['wind']};"
        f" negative hours (station use, as EIA reports): solar {neg['solar']}, wind {neg['wind']}")
    # batteries: each local day with every hour priced
    bat = {d: {} for d in DURATIONS}
    for day, g in h.groupby("day"):
        a = pd.Timestamp(day).tz_localize(tz)
        need = int(((a + pd.Timedelta(days=1)).tz_localize(None).tz_localize(tz) - a).total_seconds() // 3600)
        if len(g) != need:
            continue
        for d in DURATIONS:
            bat[d][day] = battery_day(g["p"].tolist(), d)[:4]
    rows, monthly = [], {}
    for m, g in h.groupby("month"):
        him = cp.hours_in_month(m, tz)
        flat = g["p"].mean()
        out = {"flat_price": flat, "hours_in_month": him}
        for asset in ("solar", "wind"):
            x = g.dropna(subset=[asset])
            if not len(x) or x[asset].sum() <= 0:
                continue
            e, s = x[asset].sum(), (x[asset] * x["p"]).sum()
            out[asset] = dict(revenue_per_mw=s, sales_per_mw=s, energy_per_mw=e, capture_price=s / e,
                              flat_price=x["p"].mean(), capture_rate=s / e / x["p"].mean() * 100, hours=len(x))
        for d in DURATIONS:
            vals = [bat[d][day] for day in sorted(g["day"].unique()) if day in bat[d]]
            if not vals:
                continue
            net, sales, buys, deliv = (sum(v[i] for v in vals) for i in range(4))
            out[f"battery_{d}h"] = dict(revenue_per_mw=net, sales_per_mw=sales, energy_per_mw=deliv,
                                        capture_price=sales / deliv if deliv else None, flat_price=flat,
                                        capture_rate=(sales / deliv / flat * 100) if deliv and flat else None, hours=len(vals))
        x = g.dropna(subset=["hh"])
        cost = x["hh"] * HEAT_RATE + VOM
        run = x["p"] > cost
        if len(x):
            e = float(run.sum())
            s = float(x.loc[run, "p"].sum())
            out["peaker"] = dict(revenue_per_mw=s - float(cost[run].sum()), sales_per_mw=s, energy_per_mw=e,
                                 capture_price=s / e if e else None, flat_price=x["p"].mean(),
                                 capture_rate=(s / e / x["p"].mean() * 100) if e else None, hours=len(x))
        monthly[m] = out
    return h, monthly, bat, table, os.path.relpath(path, ROOT), os.path.relpath(ex, ROOT), over, neg


UNIT = {"revenue_per_mw": "USD/MW", "sales_per_mw": "USD/MW", "energy_per_mw": "MWh/MW", "capture_price": "USD/MWh",
        "flat_price": "USD/MWh", "capture_rate": "pct", "hours": "count", "hours_in_month": "count"}


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = log_open(run_id)
    status = []
    try:
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        gens, vint = read_gens()
        hh, hhrows = henry_hub()
        ev = ip.read_series(os.path.join(ip.OUT_DIR, "event_window_daily.csv"), cols=ip.SERIES_COLS + ["ba", "event"])
        ev["ts"] = pd.to_datetime(ev["ts_utc"], utc=True)
        rows, snap, used, left = [], {"built": retrieved, "isos": {}}, [], []
        for iso in cp.ISOS:
            h, monthly, bat, table, wbk, ex, over, neg = build_iso(iso, gens, hh, log, left)
            used.append(f"{iso}: prices {table}{' and ' + pb.HISTORY if iso == 'ercot' else ' and ' + cp.HUB_HISTORY}; "
                        f"fuel {wbk}; capacity eia860m_operating_generators and eia860m_retired_generators ({', '.join(vint)})")
            entity = f"{iso}:{pb.MAIN[iso]}"
            base = dict(entity=entity, freq="P1M", geo=cp.GEO[iso], market=f"{iso}_rtm", node=pb.MAIN[iso], source=SOURCE,
                        source_url=METHOD_URL, retrieved_at=retrieved, vintage="", ba=cp.BA[iso])
            for m, out in sorted(monthly.items()):
                t = f"{m}-01T00:00:00Z"
                rows.append(dict(base, ts_utc=t, variable="flat_price", value=r4(out["flat_price"]), unit="USD/MWh"))
                rows.append(dict(base, ts_utc=t, variable="hours_in_month", value=out["hours_in_month"], unit="count"))
                for asset in ["solar", "wind"] + [f"battery_{d}h" for d in DURATIONS] + ["peaker"]:
                    if asset not in out:
                        continue
                    for k, v in out[asset].items():
                        if v is None or (isinstance(v, float) and not math.isfinite(v)):
                            continue
                        rows.append(dict(base, ts_utc=t, variable=f"{asset}_{k}", value=r4(v), unit=UNIT[k]))
            # the snapshot: monthly per asset, the hourly prices and Henry Hub (the peaker at the reader's heat rate),
            # the ERCOT stress days
            hrs = h.index
            s = {"iso": iso, "hub": pb.MAIN[iso], "ba": BA[iso], "tz": pb.TZ[iso], "start": hrs.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "months": {m: {"flat": r4(o["flat_price"]), "him": o["hours_in_month"],
                                **{a: {k: (r4(v) if v is not None else None) for k, v in o[a].items()} for a in o if isinstance(o[a], dict)}}
                            for m, o in sorted(monthly.items())},
                 "over_nameplate": over, "negative": neg}
            # hourly arrays on a continuous UTC hour grid from the first hour; null where no price. Each month's and each
            # stress day's hours are [i0, i1) on the grid, so the page can recompute the peaker at the reader's heat rate
            grid = pd.date_range(hrs.min(), hrs.max(), freq="h")
            hp = h.reindex(grid)
            gl = grid.tz_convert(pb.TZ[iso])
            gm, gd = pd.Series(gl.strftime("%Y-%m")), pd.Series(gl.strftime("%Y-%m-%d"))
            for m in s["months"]:
                ix = np.flatnonzero(gm.values == m)
                s["months"][m]["i0"], s["months"][m]["i1"] = int(ix.min()), int(ix.max()) + 1
            s["price"] = [None if pd.isna(v) else round(float(v), 2) for v in hp["p"]]
            s["hh"] = [None if pd.isna(v) else round(float(v), 3) for v in hp["hh"]]
            if iso == "ercot":
                stress = {}
                for e in STRESS:
                    x = ev[(ev["event"] == e) & (ev["entity"] == "ercot:HB_HUBAVG") & (ev["variable"] == "rt_mean")]
                    win = next(w for w in ew.MULTI + ew.EVENTS if w["event"] == e)
                    dates = sorted(x["ts"].dt.strftime("%Y-%m-%d"))
                    days = []
                    for day in dates:
                        g = h[h["day"] == day]
                        ix = np.flatnonzero(gd.values == day)
                        d = {"day": day, "window": win["start"] <= day <= win["end"], "hours": len(g),
                             "i0": int(ix.min()) if len(ix) else None, "i1": int(ix.max()) + 1 if len(ix) else None}
                        for asset in ("solar", "wind"):
                            d[asset] = r4((g[asset] * g["p"]).sum()) if g[asset].notna().any() else None
                        for du in DURATIONS:
                            d[f"battery_{du}h"] = r4(bat[du][day][0]) if day in bat[du] else None
                        days.append(d)
                    stress[e] = {"start": win["start"], "end": win["end"], "days": days}
                s["stress"] = stress
            snap["isos"][iso] = s
            log(f"  {iso}: {len(monthly)} months, {sum(1 for r in rows if r['entity'] == entity)} rows")
        cols = ip.SERIES_COLS + ["ba"]
        out = pd.DataFrame(rows)[cols]
        if out.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("two rows share an (entity, variable, ts_utc) key")
        hh_line = (f"Henry Hub: eia_fuel_spot_prices (eia:henry_hub spot_price, {hhrows['ts'].min():%Y-%m-%d} to "
                   f"{hhrows['ts'].max():%Y-%m-%d}); a day without a price takes the last trading day's before it.")
        header = [
            "Energy Research Warehouse (ERW): merchant revenue per MW at each ISO's main hub, by asset type and month "
            "(derived, session 51, the seller's side of the cost of power)",
            "Shape: series (docs/datastandard.md v0), partition column ba. Variables <asset>_<metric>: assets solar, wind, "
            "battery_2h, battery_4h, peaker; metrics revenue_per_mw (USD/MW: sales less purchases, or less fuel and variable "
            "O&M), sales_per_mw (USD/MW), energy_per_mw (MWh/MW delivered), capture_price (USD/MWh), flat_price (USD/MWh, "
            "the mean of the hours the asset used), capture_rate (pct, capture price over flat price), hours (count; for "
            "batteries, the days); and per month flat_price (all priced hours) and hours_in_month. Real-time prices; "
            "merchant only: no PPA, hedge, capacity payment or ancillary service.",
            "Solar and wind: EIA-930 hourly generation by fuel (Adjusted SUN Gen, Adjusted WND Gen) over the fuel's installed "
            "nameplate in the BA that month (EIA-860M operating and retired generators), from 2018-07-01: a fleet average, "
            "not a site; curtailed output is not in it.",
            f"Batteries: perfect-foresight optimum per local day from empty, hourly, full power or nothing, round trip {RTE} "
            "(Lazard LCOS v10.0, utility-scale 100 MW/400 MWh, low end), at most one full cycle a day: an upper bound.",
            f"Peaker: runs when the hub price exceeds Henry Hub x {HEAT_RATE} MMBtu/MWh + {VOM} USD/MWh (Lazard LCOE v18.0, "
            "gas peaking new build, midpoints); no start cost, minimum run, ramp, outage or gas basis. " + hh_line,
            f"Retrieved: {run_id} (UTC) by warehouse/derived/merchant_revenue.py",
            f"Run log: warehouse/output/logs/merchant_revenue_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, the seller's side of the cost of power (docs/methods/cost_of_power.md), {METHOD_URL}",
            "Derived from: ercot_all_hub_prices_history; iso_hub_prices_history; iso_rtm_hub_prices; nyiso_rtm_zone_prices; "
            "isone_rtm_zone_prices_hourly; eia860m_operating_generators; eia860m_retired_generators; eia_fuel_spot_prices; event_window_daily",
            "Inputs per ISO: " + "; ".join(used) + " (the BA workbooks are raw files, not in git; event_window_daily gives the "
            "snapshot's stress days)",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23); PJM excluded.",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)  # rebuilt whole from its inputs each run
        ip.write_csv(out, NAME, header, log, cols=cols, key=["entity", "variable", "ts_utc"])
        snap["defaults"] = {"rte": RTE, "heat_rate": HEAT_RATE, "vom": VOM, "near": NEAR, "durations": DURATIONS}
        snap["source"] = header[2:5] + [hh_line]
        with open(SNAPSHOT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(snap, f, separators=(",", ":"))
        ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Merchant revenue per MW by ISO hub, asset and month (docs/methods/cost_of_power.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": [NAME]}])
        status.append(dict(table=NAME, market="derived", status="ok", detail=f"{len(out)} rows; snapshot {os.path.getsize(SNAPSHOT)} bytes"))
        print(f"merchant_revenue: {len(out):,} rows; snapshot {os.path.getsize(SNAPSHOT):,} bytes")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"merchant_revenue FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status = [dict(table=NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300])]
    ip.write_status("merchant_revenue", run_id, status)
    log.close()
    return 0 if all(s["status"] == "ok" for s in status) else 1


if __name__ == "__main__":
    sys.exit(main())
