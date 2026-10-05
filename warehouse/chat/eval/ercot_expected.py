#!/usr/bin/env python3
"""Build the ERCOT evaluation set for Ask ERCOT (session 92): questions_ercot.yaml.

Energy Research Warehouse (ERW). Every expected number is computed here from the CSVs in warehouse/output with
pandas, independently of warehouse/chat/tools.py (no tool, no erw package: the files as they are). Fixed date:
TODAY. From simple lookups to questions that join two tables, with questions the tables cannot answer and questions
that depend on the page the reader came from.

    python warehouse/chat/eval/ercot_expected.py            # writes questions_ercot.yaml beside this file

A question: id, kind (lookup, series, join, refuse, context), question, expected (numbers), tolerance, text (words
the answer must contain), tables (any one cited is enough), refuse, internal, series (the answer must come with a
series), context (the view the reader came from, for the kind context), note (how the number was computed).
"""

import os
import sys

import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
TODAY = "2026-10-04"
TZ = "America/Chicago"
HUB = "ercot:HB_HUBAVG"
HIST = "ercot_all_hub_prices_history"
DAILY = "ercot_hub_prices_daily"  # session 114: the history by day, the table the site holds
_cache = {}


def rd(name, usecols=None):
    key = (name, tuple(usecols or ()))
    if key not in _cache:
        path = os.path.join(OUT, name + ".csv")
        with open(path, encoding="utf-8") as f:
            skip = sum(1 for line in f if line.startswith("#"))
        df = pd.read_csv(path, skiprows=skip, usecols=usecols, dtype=str, keep_default_na=False)
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
        if "ts_utc" in df.columns:
            df["ts"] = pd.to_datetime(df["ts_utc"], utc=True)
        _cache[key] = df
    return _cache[key]


def series(name, entity, variable, extra=None):
    df = rd(name, ["entity", "variable", "ts_utc", "value"] + list((extra or {}).keys()))
    m = (df["entity"] == entity) & (df["variable"] == variable)
    for k, v in (extra or {}).items():
        m &= df[k] == v
    return df[m].sort_values("ts")


def local(s, start, end):
    """Rows whose interval starts in [start, end) of ERCOT's local time."""
    a, b = pd.Timestamp(start, tz=TZ), pd.Timestamp(end, tz=TZ)
    return s[(s["ts"] >= a) & (s["ts"] < b)]


def month(s, ym):
    """A monthly table's row of a month (dated the month's first day, 00:00Z)."""
    r = s[s["ts_utc"].str[:7] == ym]
    assert len(r) == 1, (ym, len(r))
    return float(r["value"].iloc[0])


def newest(s):
    return float(s["value"].iloc[-1]), s["ts_utc"].iloc[-1][:7]


def tol(*values):
    return round(max(0.011, 0.005 * max(abs(v) for v in values)), 4)


def build():
    Q = []

    def add(kind, question, expected, tables, text=(), refuse=False, internal=False, wants_series=False, context=None, note="", tolerance=None):
        expected = [round(float(v), 6) for v in expected]
        if HIST in tables and DAILY not in tables:  # session 114: a past price may be read from the daily summary
            tables = list(tables) + [DAILY]
        Q.append({"id": f"e{len(Q) + 1:02d}", "kind": kind, "question": question, "expected": expected,
                  "tolerance": tolerance if tolerance is not None else (tol(*expected) if expected else 0.0), "text": list(text), "tables": list(tables),
                  "refuse": refuse, "internal": internal, "series": wants_series, "context": context, "note": note})

    hist = "ercot_all_hub_prices_history"
    rt = series(hist, HUB, "spp_rtm")
    # ---------------------------------------------------------------- lookups: prices
    v = local(rt, "2023-01-01", "2024-01-01")["value"]
    add("lookup", "What was the average real-time price at ERCOT's hub average in 2023 (ERCOT's local year)?", [v.mean()], [hist, "price_board_peak_offpeak"],
        note=f"mean of {len(v)} fifteen-minute spp_rtm values of HB_HUBAVG, 2023 local")
    da_n = local(series(hist, "ercot:HB_NORTH", "spp_dam"), "2022-07-01", "2022-08-01")["value"]
    add("lookup", "What was the average day-ahead price at HB_NORTH in July 2022?", [da_n.mean()], [hist],
        note=f"mean of {len(da_n)} hourly spp_dam values, July 2022 local")
    y21 = local(rt, "2021-01-01", "2022-01-01")
    top = y21.loc[y21["value"].idxmax()]
    add("lookup", "What was the highest real-time price at the ERCOT hub average in 2021, and in which month did it happen?", [top["value"]], [hist, "ercot_peak_premium_annual", "ercot_peak_premium_monthly"],
        text=["February"], note=f"max spp_rtm of HB_HUBAVG in 2021 local, at {top['ts_utc']}")
    pp = series("ercot_peak_premium_annual", "ercot:HB_WEST", "n_negative")
    add("lookup", "How many fifteen-minute real-time intervals were priced below zero at HB_WEST in 2024?", [month(pp, "2024-01")], ["ercot_peak_premium_annual"],
        note="ercot_peak_premium_annual, HB_WEST, n_negative, the row of 2024", tolerance=0.5)
    pk = series("ercot_peak_premium_annual", HUB, "peak_minus_midday_median")
    add("lookup", "By how much did the median peak-hours real-time price exceed the median midday price at the hub average in 2025?", [month(pk, "2025-01")],
        ["ercot_peak_premium_annual"], note="ercot_peak_premium_annual, HB_HUBAVG, peak_minus_midday_median, 2025")
    # ---------------------------------------------------------------- lookups: reserves
    ru = series("ercot_as_prices", "ercot:REGUP", "mcpc_dam")
    v = local(ru, "2022-01-01", "2023-01-01")["value"]
    add("lookup", "What was the average day-ahead price of regulation up (REGUP) in ERCOT in 2022?", [v.mean()], ["ercot_as_prices"],
        note=f"mean of {len(v)} hourly mcpc_dam values of ercot:REGUP, 2022 local")
    ec = local(series("ercot_as_prices", "ercot:ECRS", "mcpc_dam"), "2023-08-01", "2023-09-01")["value"]
    add("lookup", "What did ECRS clear at on average in August 2023?", [ec.mean()], ["ercot_as_prices"], note=f"mean of {len(ec)} hourly values, August 2023 local")
    ns = local(series("ercot_as_prices", "ercot:NSPIN", "mcpc_dam"), "2023-01-01", "2024-01-01")
    add("lookup", "What was the highest hourly price of non-spinning reserve (NSPIN) in 2023?", [ns["value"].max()], ["ercot_as_prices"],
        note=f"max of ercot:NSPIN mcpc_dam in 2023 local, at {ns.loc[ns['value'].idxmax(), 'ts_utc']}")
    # ---------------------------------------------------------------- lookups: the fleet
    B = "storage_buildout_monthly"
    mw = series(B, "iso:ercot", "battery_operating_mw")
    now_mw, now_m = newest(mw)
    add("lookup", "How many MW of batteries are operating in ERCOT in the newest inventory held?", [now_mw], [B, "storage_capacity", "storage_owners_monthly"],
        note=f"battery_operating_mw, {now_m}; the same total is the sum of storage_capacity's operating units and storage_owners_monthly's ercot_operating_mw")
    add("lookup", "What is the average duration, in hours, of ERCOT's operating batteries?", [newest(series(B, "iso:ercot", "battery_operating_mwh_per_mw"))[0]], [B, "storage_capacity", "storage_owners_monthly"],
        note=f"battery_operating_mwh_per_mw, {now_m}")
    add("lookup", "How many MW of batteries were operating in ERCOT in August 2025?", [month(mw, "2025-08")], [B], note="battery_operating_mw, 2025-08")
    add("lookup", "How many MW of ERCOT's operating batteries have a duration of two to under four hours?", [newest(series(B, "iso:ercot", "battery_operating_mw_2to4h"))[0]], [B],
        note=f"battery_operating_mw_2to4h, {now_m}")
    add("lookup", "How many MW of batteries are planned in ERCOT?", [newest(series(B, "iso:ercot", "battery_planned_mw"))[0]], [B, "storage_owners_monthly"],
        note=f"battery_planned_mw, {now_m}")
    O = "storage_owners_monthly"
    own = rd(O, ["entity", "variable", "ts_utc", "value", "x_grid", "x_owner", "x_metric"])
    own = own[own["x_grid"] == "ercot"]
    first = own[(own["x_metric"] == "operating_rank") & (own["value"] == 1)].iloc[0]
    first_mw = float(own[(own["entity"] == first["entity"]) & (own["x_metric"] == "operating_mw")]["value"].iloc[0])
    add("lookup", "Which company reports the most operating battery capacity in ERCOT, and how many MW?", [first_mw], [O], text=[first["x_owner"].split()[0]],
        note=f"operating_rank 1 is {first['x_owner']}; its ercot_operating_mw")
    add("lookup", "What share of ERCOT's operating battery capacity do the ten largest reporting companies hold?",
        [float(own[own["variable"] == "ercot_top10_share_pct"]["value"].iloc[0])], [O], note="iso:ercot, ercot_top10_share_pct")
    add("lookup", "How many companies report operating batteries in ERCOT?", [float(own[own["variable"] == "ercot_owners_operating"]["value"].iloc[0])], [O],
        note="iso:ercot, ercot_owners_operating", tolerance=0.5)
    # ---------------------------------------------------------------- lookups: the shoulder, the model
    S = "shoulder_hours_monthly"
    need = series(S, "iso:ercot", "shoulder_hours_needed")
    add("lookup", "In August 2026, how many hours would ERCOT's batteries have needed to cover the evening shoulder on the average day?", [month(need, "2026-08")], [S],
        note="shoulder_hours_needed, 2026-08")
    w10 = series(S, "iso:ercot", "year_worst10_mean_shoulder_hours_needed")
    add("lookup", "On the ten worst evenings of 2026, how many hours of storage did ERCOT's shoulder ask for on average?", [month(w10, "2026-01")], [S],
        note="year_worst10_mean_shoulder_hours_needed, the row of 2026")
    K = "battery_stack_monthly"
    f4 = series(K, HUB, "foresight_4h_revenue_total_usd_per_mw")
    add("lookup", "With perfect foresight, what could a four-hour battery have earned per MW in ERCOT in February 2021?", [month(f4, "2021-02")], [K],
        note="foresight_4h_revenue_total_usd_per_mw, 2021-02")
    d2 = series(K, HUB, "dayahead_2h_revenue_ancillary_usd_per_mw")
    add("lookup", "Under the day-ahead strategy, how much of a two-hour battery's revenue per MW came from ancillary services in June 2024?", [month(d2, "2024-06")], [K],
        note="dayahead_2h_revenue_ancillary_usd_per_mw, 2024-06")
    # ---------------------------------------------------------------- lookups: events and studies
    E = "event_window_daily"
    ev = rd(E, ["entity", "variable", "ts_utc", "value", "event"])
    uri = ev[(ev["event"] == "uri_2021") & (ev["ts_utc"] >= "2021-02-07") & (ev["ts_utc"] < "2021-02-25")]
    rmax = uri[(uri["entity"] == HUB) & (uri["variable"] == "rt_max")]
    add("lookup", "During Winter Storm Uri, what was the highest real-time price at the ERCOT hub average?", [rmax["value"].max()], [E, hist, "ercot_peak_premium_monthly", "ercot_peak_premium_annual"],
        note="event_window_daily, uri_2021, rt_max of HB_HUBAVG, max over 2021-02-07 to 2021-02-24")
    dm = uri[(uri["entity"] == "eia930:ERCO") & (uri["variable"] == "demand_mwh")]
    low = dm.loc[dm["value"].idxmin()]
    add("lookup", "On which day of Winter Storm Uri was ERCOT's demand lowest, and how many MWh was it?", [low["value"]], [E], text=[low["ts_utc"][:10]],
        note=f"event_window_daily, uri_2021, demand_mwh of eia930:ERCO, min over the event's days: {low['ts_utc'][:10]}")
    heat = ev[(ev["event"] == "ercot_heat_2023") & (ev["ts_utc"] >= "2023-08-01") & (ev["ts_utc"] < "2023-09-11") & (ev["entity"] == "eia930:ERCO") & (ev["variable"] == "demand_max_mw")]
    add("lookup", "What was ERCOT's highest hourly demand during the 2023 heat wave?", [heat["value"].max()], [E],
        note="event_window_daily, ercot_heat_2023, demand_max_mw, max over 2023-08-01 to 2023-09-10")
    # ---------------------------------------------------------------- lookups: the queue
    L = "lbnl_interconnection_queue"
    lq = rd(L, ["region", "q_status", "type_clean", "capacity_mw"])
    lq = lq[lq["region"] == "ERCOT"]
    add("lookup", "How many interconnection requests in ERCOT has Berkeley Lab recorded as withdrawn?", [float((lq["q_status"] == "withdrawn").sum())], [L],
        note="lbnl_interconnection_queue, region ERCOT, q_status withdrawn, count", tolerance=0.5)
    act_b = lq[(lq["q_status"] == "active") & (lq["type_clean"] == "Battery")]
    add("lookup", "How many MW of stand-alone battery requests are active in ERCOT's queue, by Berkeley Lab's count?", [pd.to_numeric(act_b["capacity_mw"], errors="coerce").sum()], [L],
        note=f"sum of capacity_mw over {len(act_b)} rows: region ERCOT, q_status active, type_clean Battery")
    EQ = "ercot_interconnection_queue"
    eq = rd(EQ, ["status", "fuel_technology", "capacity_mw"])
    n = ((eq["status"] == "active") & (eq["fuel_technology"] == "Other - Battery Energy Storage")).sum()
    add("lookup", "In ERCOT's own queue report, how many battery storage projects are active?", [float(n)], [EQ],
        note="ercot_interconnection_queue, status active, fuel_technology Other - Battery Energy Storage, count", tolerance=0.5)
    # ---------------------------------------------------------------- lookups: cost, revenue, carbon, demand
    C = "cost_of_power_monthly"
    add("lookup", "What did ERCOT's load pay on average at the hub in real time in August 2026, weighted by demand?", [month(series(C, HUB, "rt_load_weighted"), "2026-08")], [C],
        note="cost_of_power_monthly, rt_load_weighted, 2026-08")
    M = "merchant_revenue_monthly"
    add("lookup", "What price did solar capture at the ERCOT hub in July 2025?", [month(series(M, HUB, "solar_capture_price"), "2025-07")], [M],
        note="merchant_revenue_monthly, solar_capture_price, 2025-07")
    CI = "carbon_intensity_monthly"
    add("lookup", "What was the carbon intensity of ERCOT's generation in November 2025?", [month(series(CI, "eia930:ERCO", "intensity_generation"), "2025-11")], [CI],
        note="carbon_intensity_monthly, intensity_generation, 2025-11 (December 2025 is not held)")
    BA = "ba_supply_monthly"
    add("lookup", "How many MWh was ERCOT's demand in August 2025?", [month(series(BA, "eia930:ERCO", "demand_mwh"), "2025-08")], [BA], note="ba_supply_monthly, demand_mwh, 2025-08")
    D = "eia930_all_demand"
    dem = series(D, "eia930:ERCO", "demand_mw")
    sep = local(dem, "2026-09-01", "2026-10-01")
    add("lookup", "What was ERCOT's highest hourly demand in September 2026?", [sep["value"].max()], [D],
        note=f"max of demand_mw over {len(sep)} hours of September 2026 local, at {sep.loc[sep['value'].idxmax(), 'ts_utc']}")
    G = "eia930_all_generation"
    sol = local(series(G, "eia930:ERCO", "net_generation_solar_mw"), "2026-09-01", "2026-10-01")["value"]
    add("lookup", "What was ERCOT's average solar generation in September 2026, in MW?", [sol.mean()], [G], note=f"mean of {len(sol)} hourly values, September 2026 local")
    ST = "eia930_all_storage"
    bat = series(ST, "eia930:ERCO", "net_generation_battery_mw")
    add("lookup", "What is the highest hourly discharge of ERCOT's battery fleet on record in the warehouse?", [bat["value"].max()], [ST],
        note=f"max of net_generation_battery_mw since 2024-11-07, at {bat.loc[bat['value'].idxmax(), 'ts_utc']}")
    SD = "storage_daily_cycle"
    dis = series(SD, "eia930:ERCO", "mwh_discharged")
    add("lookup", "How many MWh did ERCOT's batteries discharge on 15 September 2026?", [float(dis[dis["ts_utc"].str[:10] == "2026-09-15"]["value"].iloc[0])], [SD],
        note="storage_daily_cycle, mwh_discharged, 2026-09-15")
    F = "ferc_eqr_contracts"
    fq = rd(F, ["x_point_of_delivery_balancing_authority", "x_product_name"])
    add("lookup", "How many contract rows filed with FERC name ERCOT as the delivery balancing authority?", [float((fq["x_point_of_delivery_balancing_authority"] == "ERCO").sum())],
        [F], internal=True, note="ferc_eqr_contracts, x_point_of_delivery_balancing_authority ERCO, count", tolerance=0.5)
    # ---------------------------------------------------------------- series: the answer rests on values over time
    m22 = local(rt, "2022-01-01", "2023-01-01")
    by = m22.groupby(m22["ts"].dt.tz_convert(TZ).dt.strftime("%Y-%m"))["value"].mean()
    add("series", "How did the monthly average real-time price at the ERCOT hub average move through 2022, and which month was highest?", [by.max()], [hist],
        text=[pd.Timestamp(by.idxmax() + "-01").strftime("%B")], wants_series=True, note=f"monthly means of spp_rtm in 2022 local; the highest is {by.idxmax()}")
    add("series", "How has ERCOT's operating battery fleet grown year by year since 2020? Give the MW at the end of 2020 and of 2025.",
        [month(mw, "2020-12"), month(mw, "2025-12")], [B, "storage_capacity"], wants_series=True, note="battery_operating_mw, 2020-12 and 2025-12")
    yr = f4.groupby(f4["ts_utc"].str[:4])["value"].sum()
    add("series", "Year by year since 2018, what could a four-hour battery have earned per MW in ERCOT with perfect foresight? Which year was highest?", [yr.max()], [K],
        text=[yr.idxmax()], wants_series=True, note=f"sum of the months of foresight_4h_revenue_total_usd_per_mw by year; the highest is {yr.idxmax()}")
    ruy = ru.groupby(ru["ts"].dt.tz_convert(TZ).dt.strftime("%Y"))["value"].mean()
    add("series", "How has the average price of regulation up changed by year since 2018? Give 2021 and 2024.", [ruy["2021"], ruy["2024"]], ["ercot_as_prices"],
        wants_series=True, note="mean of ercot:REGUP mcpc_dam by local year: 2021 and 2024")
    sh = series(S, "iso:ercot", "shoulder_hours_needed")
    s25 = sh[sh["ts_utc"].str[:4] == "2025"]
    add("series", "Month by month in 2025, how many hours would ERCOT's batteries have needed to cover the evening shoulder? Which month asked the most?", [s25["value"].max()], [S],
        text=[pd.Timestamp(s25.loc[s25["value"].idxmax(), "ts_utc"]).strftime("%B")], wants_series=True, note="shoulder_hours_needed, the months of 2025; the highest month")
    ci = series(CI, "eia930:ERCO", "intensity_generation")
    ciy = ci.groupby(ci["ts_utc"].str[:4])["value"].mean()
    add("series", "How has the carbon intensity of ERCOT's generation changed by year? Give the average of the months held of 2019 and of 2025.", [ciy["2019"], ciy["2025"]], [CI],
        wants_series=True, note="mean of the monthly intensity_generation by year: 2019 and 2025")
    # ---------------------------------------------------------------- joins: two tables
    lw = series(C, HUB, "rt_load_weighted")
    l23 = lw[lw["ts_utc"].str[:4] == "2023"]
    top_m = l23.loc[l23["value"].idxmax(), "ts_utc"][:7]
    add("join", "In the month of 2023 when ERCOT's load paid the most at the hub in real time (load-weighted), what could a four-hour battery have earned per MW with perfect foresight?",
        [month(f4, top_m)], [K], text=[pd.Timestamp(top_m + "-01").strftime("%B")],
        note=f"cost_of_power_monthly rt_load_weighted is highest in {top_m} ({l23['value'].max():.4f}); battery_stack_monthly foresight_4h_revenue_total_usd_per_mw of that month")
    add("join", "In August 2026, how did the hours of storage the evening shoulder asked for compare with the average duration of ERCOT's batteries in the inventory?",
        [month(need, "2026-08"), month(series(B, "iso:ercot", "battery_operating_mwh_per_mw"), "2026-08")], [S, B],
        note="shoulder_hours_monthly shoulder_hours_needed 2026-08, and storage_buildout_monthly battery_operating_mwh_per_mw 2026-08")
    feb = local(rt, "2021-02-01", "2021-03-01")["value"]
    rfeb = local(ru, "2021-02-01", "2021-03-01")["value"]
    add("join", "In February 2021, what was the average real-time hub price, and what was the average price of regulation up?", [feb.mean(), rfeb.mean()], [hist, "ercot_as_prices"],
        note="mean spp_rtm of HB_HUBAVG and mean mcpc_dam of ercot:REGUP, February 2021 local")
    add("join", "How does ERCOT's operating battery capacity compare with its highest hourly demand in September 2026?", [now_mw, sep["value"].max()], [B, D, "storage_capacity"],
        note="storage_buildout_monthly battery_operating_mw (newest) and the max of eia930_all_demand demand_mw in September 2026 local")
    add("join", "How many MW of batteries operate in ERCOT today, and how many MW of stand-alone battery requests are active in Berkeley Lab's queue data?",
        [now_mw, pd.to_numeric(act_b["capacity_mw"], errors="coerce").sum()], [B, L, "storage_capacity"], note="storage_buildout_monthly newest battery_operating_mw; lbnl sum of active Battery capacity_mw")
    l22 = lw[lw["ts_utc"] >= "2022-01"]
    top2 = l22.loc[l22["value"].idxmax(), "ts_utc"][:7]
    add("join", "Since January 2022, in which month did ERCOT's load pay the most at the hub in real time (load-weighted), and what was the carbon intensity of generation that month?",
        [month(ci, top2)], [CI], text=[pd.Timestamp(top2 + "-01").strftime("%B")],
        note=f"cost_of_power_monthly rt_load_weighted since 2022-01 is highest in {top2}; carbon_intensity_monthly intensity_generation of that month")
    sc = series(M, HUB, "solar_capture_price")
    add("join", "In July 2025, what price did solar capture at the hub, and what did load pay on average in real time, weighted by demand?", [month(sc, "2025-07"), month(lw, "2025-07")], [M, C],
        note="merchant_revenue_monthly solar_capture_price and cost_of_power_monthly rt_load_weighted, 2025-07")
    d4 = series(K, HUB, "dayahead_4h_revenue_total_usd_per_mw")
    add("join", "For Winter Storm Uri's month, February 2021: what was the highest real-time hub price, and what could a four-hour battery have earned per MW on day-ahead prices alone?",
        [rmax["value"].max(), month(d4, "2021-02")], [K, E, hist], note="event_window_daily rt_max max (or the history's max) and battery_stack_monthly dayahead_4h_revenue_total_usd_per_mw 2021-02")
    # ---------------------------------------------------------------- what the tables do not hold
    for q in ("What was the average day-ahead price at PJM's Western Hub last week?",
              "How many MWh did ERCOT generate from natural gas in each hour of 14 July 2022?",
              "What was the average real-time price in the Houston load zone, LZ_HOUSTON, in 2023?",
              "How much revenue did the Gambit battery near Angleton actually earn in 2023?",
              "What will the average real-time hub price be in 2027?"):
        add("refuse", q, [], [], refuse=True, note="not held: another grid, hourly fuel mix before the newest weeks, load zones, a real battery's revenue, a forecast")
    # ---------------------------------------------------------------- context: the view the reader came from
    d8 = series(K, HUB, "dayahead_8h_revenue_total_usd_per_mw")
    add("context", "What could this battery have earned per MW in July 2025?", [month(d8, "2025-07")], [K],
        context={"view": "/cost-of-power/battery", "title": "What a battery earns", "settings": {"grid": "ERCOT", "duration": "8 hours", "strategy": "day-ahead prices only (dayahead)", "size": "100 MW"}},
        note="the view's 8 hours and day-ahead strategy: dayahead_8h_revenue_total_usd_per_mw, 2025-07")
    add("context", "How many hours of storage did the shoulder ask for in this month, and how many did the batteries hold?",
        [month(need, "2025-01"), month(series(S, "iso:ercot", "fleet_hours"), "2025-01")], [S],
        context={"view": "/shoulder", "title": "The shoulder hours", "settings": {"grid": "ERCOT", "month": "2025-01"}},
        note="the view's month 2025-01: shoulder_hours_needed and fleet_hours")
    add("context", "How much was added over the last twelve months?", [newest(series(B, "iso:ercot", "battery_operating_mw_net_added_12m"))[0]], [B],
        context={"view": "/storage/buildout", "title": "How much storage has been built", "settings": {"grid": "ERCOT", "measure": "power, MW"}},
        note="the view's grid and measure: battery_operating_mw_net_added_12m, newest")
    # The model spend cap of session 92 (USD 5 for both arms and the fixes between) holds the set to 44 questions:
    # thirteen lookups that repeat a kind another question asks are built and left out (LEFT_OUT, by their text).
    kept = [q for q in Q if not any(q["question"].startswith(t) for t in LEFT_OUT)]
    Q = kept  # session 114: add() now appends to the kept list, so the ten past-price questions follow the 44
    past_prices(add, rt)
    for i, q in enumerate(kept, 1):
        q["id"] = f"e{i:02d}"
    return kept


def past_prices(add, rt):
    """Session 114: ten questions on past hub prices, older than the weeks the site's interval tables hold. Every
    expected number is computed from the interval history (ercot_all_hub_prices_history), never from the daily
    summary the chat is taught to read, so the set also checks that table. A mean is the mean of the intervals; the
    chat's mean of daily means differs from it only through a day of 23 or 25 hours, far inside the tolerance."""
    T = [DAILY, HIST]
    note = "session 114, past prices: from the intervals of ercot_all_hub_prices_history; "
    da = series(HIST, HUB, "spp_dam")
    v = local(da, "2019-01-01", "2020-01-01")["value"]
    add("lookup", "What was the average day-ahead price at the ERCOT hub average in 2019?", [v.mean()], T, note=note + f"mean of {len(v)} hourly spp_dam values, 2019 local")
    w = local(series(HIST, "ercot:HB_WEST", "spp_rtm"), "2020-03-01", "2020-04-01")["value"]
    add("lookup", "What was the average real-time price at HB_WEST in March 2020?", [w.mean()], T, note=note + f"mean of {len(w)} fifteen-minute spp_rtm values, March 2020 local")
    h = local(series(HIST, "ercot:HB_HOUSTON", "spp_dam"), "2023-01-01", "2024-01-01")
    top = h.loc[h["value"].idxmax()]
    add("lookup", "What was the highest day-ahead price at HB_HOUSTON in 2023, and in which month was it?", [top["value"]], T,
        text=[top["ts"].tz_convert(TZ).strftime("%B")], note=note + f"max spp_dam of HB_HOUSTON in 2023 local, at {top['ts_utc']}")
    lo = local(series(HIST, "ercot:HB_WEST", "spp_rtm"), "2022-01-01", "2023-01-01")["value"]
    add("lookup", "What was the lowest real-time price at HB_WEST in 2022?", [lo.min()], T, note=note + f"min of {len(lo)} fifteen-minute spp_rtm values, 2022 local")
    y23 = local(rt, "2023-01-01", "2024-01-01")["value"]
    add("lookup", "For how many hours was the real-time price at the ERCOT hub average above 200 USD/MWh in 2023?", [(y23 > 200).sum() * 0.25], T,
        note=note + f"{int((y23 > 200).sum())} fifteen-minute intervals above 200, a quarter of an hour each", tolerance=0.3)
    wd = local(series(HIST, "ercot:HB_WEST", "spp_dam"), "2024-01-01", "2025-01-01")["value"]
    add("lookup", "For how many hours was the day-ahead price at HB_WEST below zero in 2024?", [(wd < 0).sum()], T,
        note=note + f"hourly spp_dam values below zero of {len(wd)}, 2024 local", tolerance=0.5)
    n = local(series(HIST, "ercot:HB_NORTH", "spp_dam"), "2023-08-01", "2023-09-01")
    loc = n["ts"].dt.tz_convert(TZ)
    pk = n[(loc.dt.weekday < 5) & (loc.dt.hour >= 6) & (loc.dt.hour < 22)]["value"]  # August has no NERC holiday
    add("lookup", "What was the average peak-hours day-ahead price at HB_NORTH in August 2023?", [pk.mean()], T,
        note=note + f"mean of {len(pk)} hourly values, hours ending 7 to 22 local on Monday to Friday, August 2023")
    yr = local(da, "2015-01-01", "2026-01-01")
    by = yr.groupby(yr["ts"].dt.tz_convert(TZ).dt.year)["value"].mean()
    add("series", "How did the yearly average day-ahead price at the ERCOT hub average move from 2015 to 2025, and which year was highest?", [by.max()], T,
        text=[str(int(by.idxmax()))], wants_series=True, note=note + f"yearly means of hourly spp_dam by local year; highest {int(by.idxmax())}")
    u = local(rt, "2021-02-15", "2021-02-16")["value"]
    add("lookup", "What was the average real-time price at the ERCOT hub average on 15 February 2021?", [u.mean()], T, note=note + f"mean of {len(u)} fifteen-minute values, the local day")
    sd = local(series(HIST, "ercot:HB_SOUTH", "spp_dam"), "2022-01-01", "2023-01-01")["value"]
    sr = local(series(HIST, "ercot:HB_SOUTH", "spp_rtm"), "2022-01-01", "2023-01-01")["value"]
    add("join", "In 2022, what was the average day-ahead price at HB_SOUTH, and what was the average real-time price there?", [sd.mean(), sr.mean()], T,
        note=note + f"means of {len(sd)} hourly spp_dam and {len(sr)} fifteen-minute spp_rtm values, 2022 local")


LEFT_OUT = (
    "By how much did the median peak-hours", "What was the highest hourly price of non-spinning", "How many MW of batteries were operating in ERCOT in August 2025",
    "How many MW of batteries are planned", "How many companies report", "Under the day-ahead strategy, how much of a two-hour",
    "What was ERCOT's highest hourly demand during the 2023 heat wave", "In ERCOT's own queue report", "What price did solar capture at the ERCOT hub in July 2025",
    "How many MWh was ERCOT's demand in August 2025", "What was ERCOT's average solar generation", "How many MWh did ERCOT's batteries discharge",
    "How many MW of ERCOT's operating batteries have a duration",
)


def main():
    Q = build()
    spec = {"today": TODAY, "questions": Q}
    path = os.path.join(HERE, "questions_ercot.yaml")
    head = ("# Energy Research Warehouse (ERW): the ERCOT evaluation set for Ask ERCOT (session 92: 44 questions; session 114: ten more on past prices, %d in all).\n"
            "# Generated by warehouse/chat/eval/ercot_expected.py from the CSVs in warehouse/output with pandas, independently of\n"
            "# warehouse/chat/tools.py. Fixed date: today = %s. Do not edit by hand.\n") % (len(Q), TODAY)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(head)
        yaml.safe_dump(spec, f, sort_keys=False, allow_unicode=True, width=120)
    kinds = {}
    for q in Q:
        kinds[q["kind"]] = kinds.get(q["kind"], 0) + 1
    print(f"wrote {os.path.relpath(path, ROOT)}: {len(Q)} questions {kinds}")
    for q in Q:
        print(f"  {q['id']} {q['kind']:7s} {q['expected']} +-{q['tolerance']} {q['text']} | {q['question'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
