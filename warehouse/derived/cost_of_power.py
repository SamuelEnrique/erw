#!/usr/bin/env python3
"""Cost-of-power model v0 (session 37, platform tool 16): what power costs to buy at wholesale, per ISO main hub.
Market-based only: no LCOE, no transmission, distribution, capacity charges or taxes (docs/methods/cost_of_power.md).

Energy Research Warehouse (ERW). Writes three derived series tables to warehouse/output/, partition column ba:

    cost_of_power_monthly          per hub and local month, real-time (market <iso>_rtm) and day-ahead (<iso>_dam):
        rt_load_weighted, da_load_weighted   sum(hourly price x hourly BA demand) / sum(demand), USD/MWh
        rt_simple_mean, da_simple_mean       the plain mean of the same hours, USD/MWh (what a flat load pays)
        rt_shape_premium, da_shape_premium   load-weighted minus simple, USD/MWh (what the grid's load shape pays
                                             above a flat load; negative when demand peaks in cheap hours)
        rt_hours, da_hours                   the hours used, count
        hours_in_month                       the local month's hours (743 or 745 in the months of a clock change), count
    cost_of_power_hourly_profile   per hub, local month (the last 12 held) and local hour of day:
        rt_mean_h00 ... rt_mean_h23          the mean real-time price of that hour of day in that month, USD/MWh
        rt_days_h00 ... rt_days_h23          the hours averaged, count
    cost_of_power_carbon           per hub and local month, over the hours of cost_of_power_monthly's real-time rows:
        rt_load_weighted                     as above, USD/MWh
        intensity_demand                     CO2 consumed x 1000 / demand, kgCO2/MWh (what the BA's load is charged)
        intensity_generation                 CO2 generated x 1000 / net generation, kgCO2/MWh

Prices: each ISO's main hub as the price board names it (price_board.MAIN; PJM is internal and not here). ERCOT's
HB_HUBAVG from ercot_all_hub_prices_history (2015 on) joined to iso_*_hub_prices (the last month); the other ISOs from
the rolling tables, which hold about 33 days. An hour's price is the mean of its intervals, written only when every
interval of the hour is present (4 of 15 minutes, or the one hourly price).
Demand and CO2: EIA's per-BA workbooks (sheet Published Hourly Data), from the emissions connector's extracts under
warehouse/raw/eia930_emissions/ (demand from 2018-07-01; eia930_all_demand keeps 30 days only).

Months that the inputs no longer reach (the rolling tables drop their oldest days) are carried over from the previous
file, never recomputed from less.

    python warehouse/derived/cost_of_power.py
"""

import datetime as dt
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402  (session 82: California's generation from the join)
import eia930_emissions as em  # noqa: E402
import impossible_hours as ih  # noqa: E402  (session 118: the one rule for impossible values; held for this table)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402  (TZ, MAIN, TABLES, HISTORY, read_table, r4)

METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md"
SOURCE = "erw:cost_of_power"
MONTHLY, PROFILE, CARBON = "cost_of_power_monthly", "cost_of_power_hourly_profile", "cost_of_power_carbon"
COLS = ip.SERIES_COLS + ["ba"]
ISOS = ["ercot", "caiso", "isone", "miso", "nyiso", "spp"]  # PJM excluded: its prices are internal
BA = {"ercot": "erco", "caiso": "ciso", "isone": "isne", "miso": "miso", "nyiso": "nyis", "spp": "swpp"}
GEO = {"ercot": "US-TX", "caiso": "US-CA", "isone": "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT", "miso": "US-IN",
       "nyiso": "US-NY", "spp": "US-KS,US-NE,US-OK"}  # the hub's own geo is taken from its price rows when present
PROFILE_MONTHS = 12
HUB_HISTORY = "iso_hub_prices_history"  # session 49: a year of the other ISOs' main hubs
# session 49: a second hub per ISO, priced like the main one and weighted by the same BA's demand: CAISO's NP15, the
# wholesale reference of PG&E's bill (/learn/bill); its demand weights are CAISO's whole BA, not Northern California's
EXTRA = {"caiso": ["TH_NP15_GEN-APND"]}
r4 = pb.r4


def hourly(df):
    """{UTC hour start: mean price} over the hours whose intervals are all present."""
    if df.empty:
        return pd.Series(dtype=float)
    step = pb.step_of(df["freq"].iloc[0])
    per_hour = int(pd.Timedelta(hours=1) / step)
    h = df["ts"].dt.floor("h")
    g = df.groupby(h)["value"].agg(["mean", "size"])
    return g.loc[g["size"] == per_hour, "mean"]


def hours_in_month(month, tz):
    a = pd.Timestamp(f"{month}-01").tz_localize(tz)
    b = (pd.Timestamp(f"{month}-01") + pd.offsets.MonthBegin(1)).tz_localize(tz)
    return int((b - a).total_seconds() // 3600)


def prices_of(iso, mk, log):
    table, market = pb.TABLES[(iso, mk)]
    df = pb.read_table(table, market=market, node=pb.MAIN[iso])
    parts = [df]
    hname = None
    if iso == "ercot":  # the history, then the rolling table from where the history ends
        hname = pb.HISTORY
        hist = pb.read_table(pb.HISTORY, market=market, node=pb.MAIN[iso])
        parts = [hist, df[df["ts"] > hist["ts"].max()] if len(hist) else df]
    elif os.path.exists(os.path.join(ip.OUT_DIR, HUB_HISTORY + ".csv")):
        # session 49: the other ISOs' year of history (iso_hub_prices_history), then the rolling table after it
        hname = HUB_HISTORY
        hist = pb.read_table(HUB_HISTORY, market=market, node=pb.MAIN[iso])
        if len(hist) and len(df) and hist["freq"].iloc[0] != df["freq"].iloc[0]:
            # ISO-NE: the history is 15-minute, the rolling table here hourly; the history's complete hours, as hourly rows
            hh = hourly(hist)
            hist = pd.DataFrame({"ts": hh.index, "value": hh.values}).assign(
                freq=df["freq"].iloc[0], entity=df["entity"].iloc[0], variable=df["variable"].iloc[0], geo=df["geo"].iloc[0],
                market=market, node=pb.MAIN[iso], unit=df["unit"].iloc[0])
        parts = [hist, df[df["ts"] > hist["ts"].max()] if len(hist) else df]
    out = pd.concat([p for p in parts if len(p)], ignore_index=True).sort_values("ts")
    if out["ts"].duplicated().any():
        raise RuntimeError(f"{iso} {mk}: two prices for one interval")
    log(f"  {iso} {mk}: {len(out)} intervals of {pb.MAIN[iso]} ({table}"
        f"{' and ' + hname if hname else ''}), {out['ts'].min()} to {out['ts'].max()}")
    return out, table


def base_row(iso, entity, geo, market, retrieved):
    return dict(entity=entity, geo=geo, market=market, node=pb.MAIN[iso], source=SOURCE, source_url=METHOD_URL,
                retrieved_at=retrieved, vintage="", ba=BA[iso])


def build_iso(iso, x, retrieved, log, left):
    """The rows of the three tables for one ISO. x: the BA's extract hours indexed by UTC hour."""
    tz = pb.TZ[iso]
    monthly, profile, carbon = [], [], []
    rt_hours = None
    months = {}  # {month: base row}: hours_in_month once per month either market holds
    for mk, pre in (("rtm", "rt"), ("dam", "da")):
        df, _ = prices_of(iso, mk, log)
        if df.empty:
            left.append(f"{iso} {mk}: no prices of {pb.MAIN[iso]}")
            continue
        entity, geo, market = df["entity"].iloc[0], df["geo"].iloc[0] or GEO[iso], df["market"].iloc[0]
        base = base_row(iso, entity, geo, market, retrieved)
        p = hourly(df)
        j = pd.DataFrame({"price": p}).join(x[["demand_mwh"]], how="inner").dropna(subset=["price", "demand_mwh"])
        j["month"] = j.index.tz_convert(tz).strftime("%Y-%m")
        for month, g in j.groupby("month"):
            t = f"{month}-01T00:00:00Z"
            lw = (g["price"] * g["demand_mwh"]).sum() / g["demand_mwh"].sum()
            sm = g["price"].mean()
            row = dict(base, ts_utc=t, freq="P1M")
            monthly += [dict(row, variable=f"{pre}_load_weighted", value=r4(lw), unit="USD/MWh"),
                        dict(row, variable=f"{pre}_simple_mean", value=r4(sm), unit="USD/MWh"),
                        dict(row, variable=f"{pre}_shape_premium", value=r4(r4(lw) - r4(sm)), unit="USD/MWh"),
                        dict(row, variable=f"{pre}_hours", value=len(g), unit="count")]
            months.setdefault(month, dict(row, market=""))
        log(f"  {iso} {mk}: {len(p)} complete hours, {len(j)} with demand, months {j['month'].min()} to {j['month'].max()}")
        if mk != "rtm":
            continue
        rt_hours, rt_base = j, base
        # the hour-of-day profile of the last 12 months held (all complete price hours of those months)
        ph = pd.DataFrame({"price": p})
        loc = ph.index.tz_convert(tz)
        ph["month"], ph["hod"] = loc.strftime("%Y-%m"), loc.hour
        keep = sorted(j["month"].unique())[-PROFILE_MONTHS:]
        for (month, hod), g in ph[ph["month"].isin(keep)].groupby(["month", "hod"]):
            row = dict(base, ts_utc=f"{month}-01T00:00:00Z", freq="P1M")
            profile += [dict(row, variable=f"rt_mean_h{hod:02d}", value=r4(g["price"].mean()), unit="USD/MWh"),
                        dict(row, variable=f"rt_days_h{hod:02d}", value=len(g), unit="count")]
    for month, row in sorted(months.items()):
        monthly.append(dict(row, variable="hours_in_month", value=hours_in_month(month, tz), unit="count"))
    # cost against carbon, over the real-time hours of each month
    if rt_hours is not None:
        c = rt_hours.join(x[["co2_emissions_consumed", "co2_emissions_generated", "net_generation_mwh"]], how="left")
        for month, g in c.groupby("month"):
            row = dict(rt_base, ts_utc=f"{month}-01T00:00:00Z", freq="P1M")
            lw = (g["price"] * g["demand_mwh"]).sum() / g["demand_mwh"].sum()
            carbon.append(dict(row, variable="rt_load_weighted", value=r4(lw), unit="USD/MWh"))
            if g["co2_emissions_consumed"].notna().all():
                carbon.append(dict(row, variable="intensity_demand", unit="kgCO2/MWh",
                                   value=r4(g["co2_emissions_consumed"].sum() * 1000 / g["demand_mwh"].sum())))
            else:
                left.append(f"{iso} intensity_demand {month}: CO2 consumed in {g['co2_emissions_consumed'].notna().sum()}"
                            f" of {len(g)} hours")
            ok = g["co2_emissions_generated"].notna().all() and g["net_generation_mwh"].notna().all() \
                and g["net_generation_mwh"].sum() > 0
            if ok:
                carbon.append(dict(row, variable="intensity_generation", unit="kgCO2/MWh",
                                   value=r4(g["co2_emissions_generated"].sum() * 1000 / g["net_generation_mwh"].sum())))
            else:
                left.append(f"{iso} intensity_generation {month}: CO2 generated in "
                            f"{g['co2_emissions_generated'].notna().sum()} of {len(g)} hours")
    return monthly, profile, carbon


def carry(name, new):
    """The previous file's rows of (entity, market) months this run did not compute: months the rolling tables no
    longer reach stay as they were written."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path) or new.empty:
        return new, 0
    old = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    old["value"] = old["value"].astype(float)
    have = set(zip(new["entity"], new["market"], new["ts_utc"]))
    # a month is carried only when this run did not compute it and it is older than every month this run computed for
    # that entity and market
    first = new.groupby(["entity", "market"])["ts_utc"].min()
    mask = [(e, m, t) not in have and t < first.get((e, m), "9999")
            for e, m, t in zip(old["entity"], old["market"], old["ts_utc"])]
    keep = old.loc[pd.Series(mask, index=old.index, dtype=bool), list(new.columns)]
    return pd.concat([keep, new], ignore_index=True), len(keep)


def write(name, rows, title, notes, run_id, used, left, log):
    out = pd.DataFrame(rows)[COLS]
    out, carried = carry(name, out)
    out = out.sort_values(["entity", "market", "variable", "ts_utc"]).reset_index(drop=True)
    if out.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{name}: two rows share an (entity, variable, ts_utc) key")
    header = [
        f"Energy Research Warehouse (ERW): {title} (cost-of-power model v0, derived, session 37)",
        "Shape: series (docs/datastandard.md v0), partition column ba; freq P1M, ts_utc the first day of the ISO's "
        "local month at 00:00:00Z (decision 11); ERCOT America/Chicago, CAISO America/Los_Angeles, NYISO and ISO-NE "
        "America/New_York, MISO EST, SPP America/Chicago (the price board's operating days).",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/cost_of_power.py",
        f"Run log: warehouse/output/logs/cost_of_power_{run_id}.log",
        f"Source: {SOURCE} ERW derived table, cost-of-power method (docs/methods/cost_of_power.md), {METHOD_URL}",
        "Derived from: ercot_all_hub_prices_history; iso_hub_prices_history; iso_rtm_hub_prices; iso_dam_hub_prices; nyiso_rtm_zone_prices; "
        "nyiso_dam_zone_prices; isone_rtm_zone_prices_hourly; isone_dam_zone_prices",
        "Also read: EIA's hourly demand, net generation and CO2 from the per-BA workbooks (source "
        "eia:gridmonitor/knownissues/xls), the emissions connector's extracts: " + "; ".join(used),
        "Hubs: ERCOT HB_HUBAVG, CAISO TH_SP15_GEN-APND, NYISO N.Y.C., MISO INDIANA.HUB, SPP SPPNORTH_HUB, ISO-NE "
        ".H.INTERNAL_HUB (the price board's main hubs). PJM is not here: its prices are internal. Wholesale energy "
        "only: no transmission, distribution, capacity, ancillary charges or taxes.",
        *notes,
        f"Carried over from the previous file (months the rolling tables no longer reach): {carried} rows.",
        f"Hours or months left out: {len(left)}" + (" (" + "; ".join(left[:12]) + ")" if left else ""),
    ]
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
        for h in header + [f"File holds {len(out)} rows, rewritten by this run."]:
            f.write("# " + h + "\n")
        out.to_csv(f, index=False, lineterminator="\n")
    os.replace(path + ".tmp", path)
    log(f"{name}: {len(out)} rows ({carried} carried over)")
    print(f"{name}.csv: rows={len(out)}; carried {carried}")
    return len(out)


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"cost_of_power_{run_id}.log"))
    status = []
    try:
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        monthly, profile, carbon, used, left = [], [], [], [], []
        for iso in ISOS:  # one ISO in memory at a time
            ex = em.latest_extract(BA[iso])
            if ex is None:
                raise RuntimeError(f"no extract of {BA[iso]} under warehouse/raw/eia930_emissions/; nothing written")
            url, lm, got = em.extract_meta(ex)
            used.append(f"{BA[iso]}: {os.path.relpath(ex, ROOT)} ({url}, Last-Modified {lm}, downloaded {got})")
            x = em.read_extract(ex)
            # session 118: an impossible hour of demand weighs nothing and an impossible hour of net generation divides
            # nothing (docs/methods/impossible_hours.md). Written here and HELD: this table is behind a live page, so
            # the rule is applied only when a person has approved the numbers it moves (impossible_hours.HELD)
            x = ih.screen_extract(x, MONTHLY, log=log)
            x.index = pd.to_datetime(x["ts_utc"], utc=True)
            if iso == "caiso":
                # session 82: EIA's California values of 2023-11 to 2025-12-02 sit one hour late (cj.true_hours); and from
                # the join California's net generation is CAISO's own (cost_of_power_carbon's intensity of generation):
                # the month that holds the join, and a month CAISO does not hold wholly, is left out below
                x = cj.join_extract(cj.true_hours(x))
            a, b, c = build_iso(iso, x, retrieved, log, left)
            monthly += a
            profile += b
            carbon += c
            for node in EXTRA.get(iso, []):  # session 49: CAISO's NP15 too, for PG&E's bill, weighted by CAISO's demand
                main_hub = pb.MAIN[iso]
                pb.MAIN[iso] = node
                try:
                    a, b, c = build_iso(iso, x, retrieved, log, left)
                finally:
                    pb.MAIN[iso] = main_hub
                monthly += a
                profile += b
                carbon += c
        for s in left:
            log(f"  LEFT OUT {s}")
        n = {}
        n[MONTHLY] = write(MONTHLY, monthly, "cost of power per ISO main hub and month, load-weighted and simple "
                           "averages of the real-time and day-ahead price",
                           ["Load-weighted: sum over the month's hours of the hour's price x the BA's demand, over the "
                            "sum of demand; simple: the mean of the same hours; shape premium: load-weighted minus simple "
                            "(each rounded to 4 decimals first). A month is complete when rt_hours equals hours_in_month; "
                            "the others are partial and say so on the page."], run_id, used, left, log)
        n[PROFILE] = write(PROFILE, profile, "average real-time price by local hour of day and month, per ISO main hub",
                           [f"The last {PROFILE_MONTHS} local months each hub holds with demand; every complete price "
                            "hour of those months, demand or not. rt_days_hNN counts the hours averaged."],
                           run_id, used, left, log)
        n[CARBON] = write(CARBON, carbon, "load-weighted real-time price and carbon intensity per ISO and month",
                          ["Over the real-time hours of cost_of_power_monthly. intensity_demand: EIA's CO2 emissions "
                           "consumed x 1000 over demand; intensity_generation: CO2 generated x 1000 over net generation "
                           "(the carbon_intensity_* formulas, over the ISO's local month and these hours)."],
                          run_id, used, left, log)
        ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Cost of power, market-based: load-weighted wholesale prices, hour-of-day "
                                      "profiles and carbon (docs/methods/cost_of_power.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public",
                            "tables": [MONTHLY, PROFILE, CARBON]}])
        for t, k in n.items():
            status.append(dict(table=t, market="derived", status="ok", detail=f"{k} rows; {len(left)} left out"))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"cost_of_power FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status = [dict(table=t, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300])
                  for t in (MONTHLY, PROFILE, CARBON)]
    ip.write_status("cost_of_power", run_id, status)
    log.close()
    return 0 if all(s["status"] == "ok" for s in status) else 1


if __name__ == "__main__":
    sys.exit(main())
