#!/usr/bin/env python3
"""Where the next gigawatts for AI can come from: one row of measures per ISO region (session 62, the flagship analysis).

Energy Research Warehouse (ERW) derived table, tier derived, public (every input is public; PJM's prices are licensed
for internal use and are not held, so PJM's cost measures are absent, never estimated):

    warehouse/output/ai_power_regions.csv   series; entity iso:<caiso|ercot|isone|miso|nyiso|pjm|spp>; x_window and x_note

    python warehouse/derived/ai_power_regions.py

The year is September 2025 to August 2026 (WINDOW), the latest twelve complete months every price input holds. The
measures, each from a warehouse table (docs/reports/ai_gigawatts_methods.md is the methods appendix):

  cost       flat_rt_price_usd_mwh   what a flat load pays at the region's main hub in real time (cost_of_power_monthly,
                                     rt_simple_mean weighted by rt_hours); flat_da_price_usd_mwh the same, day-ahead;
             flat_1gw_cost_musd      a flat 1 GW for a year (8,760 h) at that price, USD million: wholesale energy only
  carbon     carbon_intensity_kg_mwh the mean of the year's daily consumption-based intensity over the days held
                                     (carbon_intensity_daily, intensity_demand); flat_1gw_co2_kt a flat 1 GW for a year at it, kt CO2
  stress     scarcity_hours_200 and scarcity_hours_1000   hours whose real-time hub price averaged at least USD 200 and
                                     1,000/MWh (iso_hub_prices_history; ERCOT ercot_all_hub_prices_history); max_rt_hour_usd_mwh;
             emergency_days          CAISO only: days with an ISO-wide Flex Alert or emergency, 2018-07 to 2025-04
                                     (caiso_grid_emergencies, as the Flex Alert scorecard reads it); not held elsewhere;
             event_largest_effect_pct  the largest pooled demand effect of a studied event, percent of its counterfactual
                                     (event_study_estimates, temperature-controlled where held; x_note names the event)
  connection lbnl_active_gw, lbnl_active_requests   active requests at the end of 2025 (lbnl_interconnection_queue);
             lbnl_median_years_to_cod  median years from request to operation, requests that came online 2018 to 2025;
             lbnl_completion_pct     share of the requests made 2000 to 2019 that came online;
             queue_active_gw         active MW in the ISO's own queue as of late September 2026 (<iso>_interconnection_queue)
  imports    net_import_share_pct    the year's demand less net generation over demand, EIA's own balance (the EIA-930 workbook
                                     extract, complete hours);
             pair_import_share_pct, net_import_days_pct, peak_import_share_pct   from the pair sums (eia930_daily_interchange,
                                     minus the BA's summed interchange with every neighbour) over complete days: the pair-sum
                                     share, the share of days the BA was a net importer, and the mean net import share on the
                                     ten highest-demand complete days; interchange_days the complete days, screened_pair_days
                                     the pair-days left out as implausible
"""

import datetime as dt
import glob
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "ai_power_regions"
SOURCE = "erw:ai_power_regions"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/reports/ai_gigawatts_methods.md"
WINDOW = ("2025-09-01", "2026-09-01")  # [start, end)
TS = f"{WINDOW[0]}T00:00:00Z"
# region: (BA, hub entity, price market, LBNL region, our queue table, display name)
REGIONS = {
    "caiso": ("CISO", "caiso:TH_SP15_GEN-APND", "caiso_rtm", "CAISO", "caiso", "CAISO"),
    "ercot": ("ERCO", "ercot:HB_HUBAVG", "ercot", "ERCOT", "ercot", "ERCOT"),
    "isone": ("ISNE", "isone:.H.INTERNAL_HUB", "isone_rtm", "ISO-NE", "isone", "ISO-NE"),
    "miso": ("MISO", "miso:INDIANA.HUB", "miso_rtm", "MISO", "miso", "MISO"),
    "nyiso": ("NYIS", "nyiso:N.Y.C.", "nyiso_rtm", "NYISO", "nyiso", "NYISO"),
    "pjm": ("PJM", None, None, "PJM", None, "PJM"),
    "spp": ("SWPP", "spp:SPPNORTH_HUB", "spp_rtm", "SPP", "spp", "SPP"),
}


def read(name, usecols=None):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, usecols=usecols)


def in_window(ts):
    t = pd.to_datetime(ts, utc=True)
    return (t >= pd.Timestamp(WINDOW[0], tz="UTC")) & (t < pd.Timestamp(WINDOW[1], tz="UTC"))


def cost():
    c = read("cost_of_power_monthly")
    c = c[in_window(c["ts_utc"])]
    c["v"] = pd.to_numeric(c["value"])
    out = {}
    for r, (_, hub, *_rest) in REGIONS.items():
        if hub is None:
            continue
        g = c[c["entity"] == hub].pivot(index="ts_utc", columns="variable", values="v")
        if len(g) != 12:
            raise RuntimeError(f"cost_of_power_monthly: {hub} has {len(g)} months in the year, not 12")
        rt = float((g["rt_simple_mean"] * g["rt_hours"]).sum() / g["rt_hours"].sum())
        da = float((g["da_simple_mean"] * g["da_hours"]).sum() / g["da_hours"].sum())
        out[r] = dict(flat_rt_price_usd_mwh=rt, flat_da_price_usd_mwh=da, flat_1gw_cost_musd=rt * 8760 * 1000 / 1e6,
                      rt_hours_priced=float(g["rt_hours"].sum()))
    return out


def carbon():
    """The mean of the year's daily consumption-based intensity over the days held. The monthly table keeps only complete
    months (4 to 12 of the year's, by region), which would weight the seasons unevenly; the daily table holds 233 (SPP) to
    365 days."""
    ci = read("carbon_intensity_daily", ["entity", "variable", "ts_utc", "value"])
    ci = ci[in_window(ci["ts_utc"]) & (ci["variable"] == "intensity_demand")]
    out = {}
    for r, (ba, *_rest) in REGIONS.items():
        g = pd.to_numeric(ci[ci["entity"] == f"eia930:{ba}"]["value"])
        if len(g):
            out[r] = dict(carbon_intensity_kg_mwh=float(g.mean()), flat_1gw_co2_kt=float(g.mean()) * 8760 * 1000 / 1e6,
                          carbon_days=float(len(g)))
    return out


def hourly_rt(region):
    _, hub, market, *_ = REGIONS[region]
    if region == "ercot":
        h = read("ercot_all_hub_prices_history", ["entity", "variable", "ts_utc", "value"])
        h = h[(h["entity"] == hub) & (h["variable"] == "spp_rtm")]
    else:
        h = read("iso_hub_prices_history", ["entity", "variable", "ts_utc", "value", "market"])
        h = h[(h["entity"] == hub) & (h["market"] == market)]
    h = h[in_window(h["ts_utc"])]
    t = pd.to_datetime(h["ts_utc"], utc=True).dt.floor("h")
    return pd.Series(pd.to_numeric(h["value"]).to_numpy(), index=t).groupby(level=0).mean()


def stress():
    out = {}
    for r, (_, hub, *_rest) in REGIONS.items():
        if hub is None:
            continue
        s = hourly_rt(r)
        out[r] = dict(scarcity_hours_200=float((s >= 200).sum()), scarcity_hours_1000=float((s >= 1000).sum()),
                      max_rt_hour_usd_mwh=float(s.max()), rt_hours_seen=float(len(s)))
    return out


def emergencies():
    import flex_alert_scorecard as fa
    days = fa.alert_days(read("caiso_grid_emergencies"))
    return {"caiso": dict(emergency_days=float(len(days)))}


def events():
    es = read("event_study_estimates", ["entity", "variable", "ts_utc", "value", "event"])
    out = {}
    for r, (ba, *_rest) in REGIONS.items():
        g = es[(es["entity"] == f"eia930:{ba}") & (es["event"] != "covid_2020")]
        best = None
        for ev, e in g.groupby("event"):
            v = e.set_index("variable")["value"]
            eff, cf = ("demand_mwh_effect_pooled_temp", "demand_mwh_counterfactual_mean_temp") if "demand_mwh_effect_pooled_temp" in v else \
                ("demand_mwh_effect_pooled", "demand_mwh_counterfactual_mean")
            if eff in v and cf in v:
                pct = float(v[eff]) / float(v[cf]) * 100
                if best is None or abs(pct) > abs(best[0]):
                    best = (pct, ev, "temperature-controlled" if eff.endswith("_temp") else "day-of-week and year")
        if best:
            out[r] = dict(event_largest_effect_pct=best[0], _note_event=f"{best[1]} ({best[2]})", _event_id=best[1])
    return out


def lbnl():
    q = read("lbnl_interconnection_queue", ["status", "capacity_mw", "region", "q_date", "on_date", "q_year"])
    q["mw"] = pd.to_numeric(q["capacity_mw"], errors="coerce")
    out = {}
    for r, v in REGIONS.items():
        g = q[q["region"] == v[3]]
        act = g[g["status"] == "active"]
        on = g[(g["status"] == "operating") & (g["on_date"] != "") & (g["q_date"] != "")]
        on = on[pd.to_datetime(on["on_date"]).dt.year.between(2018, 2025)]
        yrs = (pd.to_datetime(on["on_date"]) - pd.to_datetime(on["q_date"])).dt.days / 365.25
        yrs = yrs[yrs >= 0]
        cohort = g[pd.to_numeric(g["q_year"], errors="coerce").between(2000, 2019)]
        out[r] = dict(lbnl_active_gw=float(act["mw"].sum() / 1000), lbnl_active_requests=float(len(act)),
                      lbnl_median_years_to_cod=float(yrs.median()) if len(yrs) else np.nan, lbnl_cod_sample=float(len(yrs)),
                      lbnl_completion_pct=float((cohort["status"] == "operating").mean() * 100) if len(cohort) else np.nan,
                      lbnl_cohort_requests=float(len(cohort)))
    return out


def own_queues():
    out = {}
    for r, v in REGIONS.items():
        table = v[4]
        if table is None:
            continue
        q = read(f"{table}_interconnection_queue", ["status", "capacity_mw", "retrieved_at"])
        a = q[q["status"] == "active"]
        out[r] = dict(queue_active_gw=float(pd.to_numeric(a["capacity_mw"], errors="coerce").sum() / 1000),
                      _note_queue=f"retrieved {q['retrieved_at'].max()[:10]}")
    return out


def extract(ba):
    import eia930_emissions as em
    ex = em.latest_extract(ba.lower())
    x = em.read_extract(ex)[["ts_utc", "demand_mwh", "net_generation_mwh"]]
    x = x[in_window(x["ts_utc"])]
    return x, ex


def screen(it):
    """Pair-days left out as implausible: further than 10 median absolute deviations (at least 500 MWh) from the pair's own
    median over its whole history (2019 on). EIA's daily interchange holds days no tie can carry (SWPP-MISO 2,159,056 MWh on
    2026-07-21, more than SPP's whole daily demand)."""
    g = it.groupby("entity")["v"]
    med = g.transform("median")
    mad = (it["v"] - med).abs().groupby(it["entity"]).transform("median")
    return (it["v"] - med).abs() > 10 * np.maximum(mad, 500)


def imports():
    """The headline share is EIA's own balance, demand less net generation over demand, from the BA's complete hours (the
    workbook extract). The pair sums (eia930_daily_interchange) give the per-day measures, over complete days only: a day
    counts when every regular neighbour (a pair present on at least half the year's days) reported it and none of its
    pair-days was screened out. EIA's daily interchange is missing for about 50 days of the year in every region, which is
    why the pairs are not the headline."""
    it = read("eia930_daily_interchange", ["entity", "ts_utc", "value", "ba"])
    it["v"] = pd.to_numeric(it["value"])
    bad = screen(it)
    it = it.assign(bad=bad)[in_window(it["ts_utc"])]
    out = {}
    for r, (ba, *_rest) in REGIONS.items():
        g = it[it["ba"] == ba.lower()].assign(day=lambda z: z["ts_utc"].str[:10])
        days_all = g["day"].nunique()
        regular = g.groupby("entity")["day"].nunique()
        regular = set(regular[regular >= 0.5 * days_all].index)
        ok_days = []
        for day, gd in g.groupby("day"):
            have = set(gd.loc[~gd["bad"], "entity"])
            if regular <= have and not gd["bad"].any():
                ok_days.append(day)
        gd = g[g["day"].isin(ok_days)]
        daily_export = gd.groupby("day")["v"].sum()
        x, ex = extract(ba)
        d = pd.to_numeric(x["demand_mwh"], errors="coerce")
        ng = pd.to_numeric(x["net_generation_mwh"], errors="coerce")
        ok = d.notna() & ng.notna()
        dd = d.groupby(pd.to_datetime(x["ts_utc"], utc=True).dt.strftime("%Y-%m-%d")).sum()
        dd = dd.reindex(daily_export.index)
        day_share = (-daily_export / dd).dropna()
        top = dd.dropna().sort_values(ascending=False).index[:10]
        out[r] = dict(net_import_share_pct=float((d[ok].sum() - ng[ok].sum()) / d[ok].sum() * 100),
                      pair_import_share_pct=float(-daily_export.sum() / dd.sum() * 100),
                      net_import_days_pct=float((daily_export < 0).mean() * 100),
                      peak_import_share_pct=float(day_share.reindex(top).mean() * 100),
                      interchange_days=float(len(daily_export)), interchange_days_reported=float(days_all),
                      screened_pair_days=float(g["bad"].sum()), demand_twh=float(d[ok].sum()) / 1e6)
    return out


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ai_power_regions_{run_id}.log"))
    results = []
    try:
        parts = {}
        for name, fn in (("cost", cost), ("carbon", carbon), ("stress", stress), ("emergencies", emergencies), ("events", events),
                         ("lbnl", lbnl), ("queues", own_queues), ("imports", imports)):
            got = fn()
            for r, d in got.items():
                parts.setdefault(r, {}).update(d)
            log(f"{name}: {len(got)} regions")
        rows = []
        units = {"usd_mwh": "USD/MWh", "musd": "USD", "kg_mwh": "kgCO2/MWh", "kt": "tCO2", "pct": "pct", "gw": "MW", "twh": "MWh"}
        for r, d in parts.items():
            notes = "; ".join(v for k, v in d.items() if k.startswith("_note_"))
            for k, v in d.items():
                if k == "_event_id":  # the event, as a variable the site can read (Supabase keeps no x_ columns for series)
                    rows.append((f"iso:{r}", f"event_largest_is_{v}", TS, 1.0, "count", "studied event windows (event_study_estimates)", ""))
                    continue
                if k.startswith("_note_") or v is None or (isinstance(v, float) and not np.isfinite(v)):
                    continue
                unit = "year" if k.endswith("_years_to_cod") else next((u for s, u in units.items() if k.endswith(s)), "count")
                val = v
                # the standard's units: GW and TWh as MW and MWh; USD million and kt CO2 as USD and tCO2
                if k.endswith("_gw"):
                    k, val = k[:-3] + "_mw", v * 1000
                elif k.endswith("_twh"):
                    k, val = k[:-4] + "_mwh", v * 1e6
                elif k.endswith("_musd"):
                    k, val = k[:-5] + "_usd", v * 1e6
                elif k.endswith("_kt"):
                    k, val = k[:-3] + "_t", v * 1000
                ts = "2026-01-01T00:00:00Z" if k.startswith("lbnl_") else "2026-09-30T00:00:00Z" if k.startswith("queue_") else \
                    "2018-07-01T00:00:00Z" if k == "emergency_days" else TS
                window = ("Berkeley Lab Queued Up 2026 edition, requests through 2025" if k.startswith("lbnl_") else
                          "the ISO's queue as retrieved in late September 2026" if k.startswith("queue_") else
                          "2018-07 to 2025-04, CAISO's Grid Emergencies History Report" if k == "emergency_days" else
                          "studied event windows (event_study_estimates)" if k.startswith("event_") else
                          f"{WINDOW[0]} to {WINDOW[1]} (twelve months)")
                # whole units for amounts (USD, tonnes, MW, MWh, counts), two decimals for rates, shares and prices
                digits = 0 if unit in ("USD", "tCO2", "MW", "MWh", "count") else 2
                rows.append((f"iso:{r}", k, ts, round(float(val), digits), unit, window, notes if k in ("event_largest_effect_pct", "queue_active_mw") else ""))
        s = pd.DataFrame(rows, columns=["entity", "variable", "ts_utc", "value", "unit", "x_window", "x_note"])
        s = s.assign(freq="", geo="", market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
        cols = ip.SERIES_COLS + ["x_window", "x_note"]
        header = [
            "Energy Research Warehouse (ERW): where the next gigawatts for AI can come from, one row of measures per ISO region (derived, session 62)",
            "Shape: series (docs/datastandard.md v0); entity iso:<region>; one row per region and measure; x_window the measure's period, "
            "x_note its event or snapshot. Cost: flat_rt_price_usd_mwh, flat_da_price_usd_mwh, flat_1gw_cost_usd (a flat 1 GW for a year, "
            "wholesale energy only). Carbon: carbon_intensity_kg_mwh, flat_1gw_co2_t. Stress: scarcity_hours_200, scarcity_hours_1000, "
            "max_rt_hour_usd_mwh, emergency_days (CAISO only), event_largest_effect_pct and event_largest_is_<event> (1: which event). Connection: lbnl_active_mw, lbnl_active_requests, "
            "lbnl_median_years_to_cod, lbnl_completion_pct, queue_active_mw. Imports: net_import_share_pct, net_import_days_pct, "
            "peak_import_share_pct, pair_import_share_pct (net_import_share_pct is EIA's balance, demand less net generation; the others are "
            "from the pair sums over complete days). Counts behind them: rt_hours_priced, rt_hours_seen, carbon_days, lbnl_cod_sample, "
            "lbnl_cohort_requests, interchange_days, interchange_days_reported, screened_pair_days, demand_mwh.",
            f"The year: {WINDOW[0]} to {WINDOW[1]}. PJM's prices are licensed for internal use and not held: PJM has no cost or price-stress "
            "measure here.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/ai_power_regions.py",
            f"Run log: warehouse/output/logs/ai_power_regions_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, the AI gigawatts report's methods appendix (docs/reports/ai_gigawatts_methods.md), {METHOD_URL}",
            "Derived from: cost_of_power_monthly; carbon_intensity_daily; iso_hub_prices_history; ercot_all_hub_prices_history; "
            "caiso_grid_emergencies; event_study_estimates; lbnl_interconnection_queue; caiso_interconnection_queue; ercot_interconnection_queue; "
            "isone_interconnection_queue; miso_interconnection_queue; nyiso_interconnection_queue; spp_interconnection_queue; "
            "eia930_daily_interchange; eia930_all_demand",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): EIA, NOAA, the ISOs' public "
            "data, Berkeley Lab and GridTracker (CC BY 4.0: attribute Lawrence Berkeley National Laboratory and GridTracker).",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)
        ip.write_csv(s[cols], NAME, header, log, cols=cols)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="Where the next gigawatts for AI can come from (warehouse/derived/ai_power_regions.py)",
                                report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
        msg = f"{len(s)} rows, {s['entity'].nunique()} regions"
        log(msg)
        print(f"ai_power_regions: {msg}")
        results.append(dict(table=NAME, market="all", status="ok", detail=msg))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"ai_power_regions FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("ai_power_regions", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
