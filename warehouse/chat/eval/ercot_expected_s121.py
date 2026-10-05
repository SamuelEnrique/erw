#!/usr/bin/env python3
"""Build the second ERCOT evaluation set for Ask ERCOT (session 121): questions_ercot_s121.yaml.

Energy Research Warehouse (ERW). One hundred questions of five kinds, twenty of each, that the first set
(ercot_expected.py, 54 questions) did not ask:

  join      a question that needs two tables: both must be cited, and the number of each must be in the answer
  vague     a newcomer's question, in a newcomer's words: it must be answered (never refused, never sent back), from
            a table that can bear it; where one reading is plainly the natural one, its number must be there
  followup  a question that depends on the answer before it ("And the year before?"): `first` is the question
            asked first. The page as it stood kept nothing of the previous answer: the "before" arm asks the
            follow-up bare, as the page did
  premise   a question that assumes something the tables contradict: the answer must state what the tables say
            (the true number, and a word of the correction where one is named), never go along with it
  outside   a question the ERCOT tables cannot answer: it must be refused with no number, and the refusal must name
            the nearest thing that is held (a table of the guide, by its name)

Every expected number is computed here from the CSVs in warehouse/output with pandas, independently of
warehouse/chat/tools.py. Every wrong premise is checked here against the tables before it is written: if the tables
come to agree with one, the build stops. Fixed date: TODAY.

    python warehouse/chat/eval/ercot_expected_s121.py        # writes questions_ercot_s121.yaml beside this file

A question: the fields of the first set (id, kind, question, expected, tolerance, text, tables, refuse, internal,
series, context, note) and, where they apply: first (the question before a follow-up), tables_all (groups of
tables: one of each group must be cited), any_of (alternative expected numbers: one group is enough), text_any
(one of these words must be in the answer), tolerances (one for each expected number), nearest (tables one of which the refusal must name; empty: any table of
the guide), status_any (the answer may be an answer or a refusal).
"""

import os
import sys

import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ercot_expected as E  # noqa: E402  the first set's readers: the files as they are

TODAY = E.TODAY
HUB = E.HUB
DAILY, AS, B, K, BA = "ercot_hub_prices_daily", "ercot_as_prices", "storage_buildout_monthly", "battery_stack_monthly", "ba_supply_monthly"
M, C, CI, PA, PM = "merchant_revenue_monthly", "cost_of_power_monthly", "carbon_intensity_monthly", "ercot_peak_premium_annual", "ercot_peak_premium_monthly"
SD, EW, ES, L, Q2 = "storage_daily_cycle", "event_window_daily", "event_study_estimates", "lbnl_interconnection_queue", "ercot_interconnection_queue"
D, G, ST, AQ, O, CAP, SH = "eia930_all_demand", "eia930_all_generation", "eia930_all_storage", "ercot_as_quantities", "storage_owners_monthly", "storage_capacity", "shoulder_hours_monthly"
HIST, DAM, RTM = "ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices"
PRICES = [DAILY, HIST, DAM, RTM, C, PA, PM, "price_board_peak_offpeak"]
FLEET = [B, CAP, O, SH]


def yr(s, y):
    """The rows of a daily or monthly table that are dated in a year."""
    return s[s["ts_utc"].str[:4] == str(y)]["value"]


def mo(s, ym):
    return s[s["ts_utc"].str[:7] == ym]["value"]


def build():
    Q = []
    counts = {}

    def add(kind, question, expected=(), tables=(), **kw):
        counts[kind] = counts.get(kind, 0) + 1
        expected = [round(float(v), 6) for v in expected]
        one = kw.pop("tolerance", None)
        # a tolerance for each number: half a percent of that number (the first set had one for the question, which lets a
        # rate of 0.6 pass beside a count of 4,000); a count is checked to the unit
        tols = kw.pop("tolerances", None) or [one if one else E.tol(v) for v in expected]
        q = {"id": f"{kind[0]}{counts[kind]:02d}", "kind": kind, "question": question, "expected": expected, "tolerances": tols,
             "tolerance": max(tols) if tols else 0.0, "text": list(kw.pop("text", ())), "tables": list(tables),
             "refuse": kind == "outside", "internal": False, "series": False, "context": None, "note": kw.pop("note", "")}
        if "any_of" in kw:
            kw["any_of"] = [[round(float(v), 6) for v in g] for g in kw["any_of"]]
        q.update(kw)
        Q.append(q)

    def d(entity, variable):
        return E.series(DAILY, entity, variable)

    rt, da = d(HUB, "rt_mean"), d(HUB, "da_mean")
    rtmax = d(HUB, "rt_max")
    mw, mwh = E.series(B, "iso:ercot", "battery_operating_mw"), E.series(B, "iso:ercot", "battery_operating_mwh")
    now_mw, now_m = E.newest(mw)
    dem = E.series(BA, "eia930:ERCO", "demand_mwh")
    ci = E.series(CI, "eia930:ERCO", "intensity_generation")
    cid = E.series(CI, "eia930:ERCO", "intensity_demand")
    lw = E.series(C, HUB, "rt_load_weighted")

    def stack(v):
        return E.series(K, HUB, v)

    def merch(v):
        return E.series(M, HUB, v)

    def asp(product):
        return E.series(AS, f"ercot:{product}", "mcpc_dam")

    # ================================================================ join: two tables
    J = lambda *groups: {"tables_all": [list(g) for g in groups]}  # noqa: E731
    add("join", "In August 2023, what was the load-weighted real-time price of power at the hub average, and what was the carbon intensity of ERCOT's generation that month?",
        [E.month(lw, "2023-08"), E.month(ci, "2023-08")], [C, CI], **J([C], [CI]), note="cost_of_power_monthly rt_load_weighted 2023-08; carbon_intensity_monthly intensity_generation 2023-08")
    f2 = stack("foresight_2h_revenue_total_usd_per_mw")
    add("join", "How many MW of batteries were operating in ERCOT in June 2025, and what could a two-hour battery have earned per MW that month with perfect foresight?",
        [E.month(mw, "2025-06"), E.month(f2, "2025-06")], [B, K], **J(FLEET, [K]), note="storage_buildout_monthly battery_operating_mw 2025-06; battery_stack_monthly foresight_2h_revenue_total_usd_per_mw 2025-06")
    jan = mo(rtmax, "2024-01")
    add("join", "In January 2024, what was the highest real-time interval price at the hub average, and how many MWh was ERCOT's demand for the month?",
        [jan.max(), E.month(dem, "2024-01")], [DAILY, BA], **J(PRICES + [EW], [BA]), note="ercot_hub_prices_daily rt_max, max over January 2024; ba_supply_monthly demand_mwh 2024-01")
    ru = asp("REGUP")
    add("join", "What did regulation up (REGUP) clear at on average in 2021 and in 2025, and how many MW of batteries were operating in ERCOT in December of each of those years?",
        [E.local(ru, "2021-01-01", "2022-01-01")["value"].mean(), E.local(ru, "2025-01-01", "2026-01-01")["value"].mean(), E.month(mw, "2021-12"), E.month(mw, "2025-12")], [AS, B],
        **J([AS], FLEET), note="ercot_as_prices REGUP mcpc_dam, means of 2021 and 2025 local; storage_buildout_monthly battery_operating_mw 2021-12 and 2025-12")
    b2 = merch("battery_2h_revenue_per_mw")
    add("join", "What did a merchant two-hour battery earn per MW at the hub's real-time price in August 2023, and how big was ERCOT's operating battery fleet, in MW, that month?",
        [E.month(b2, "2023-08"), E.month(mw, "2023-08")], [M, B], **J([M], FLEET), note="merchant_revenue_monthly battery_2h_revenue_per_mw 2023-08; storage_buildout_monthly battery_operating_mw 2023-08")
    sdc = E.series(SD, "eia930:ERCO", "mwh_discharged")
    day = "2025-08-20"
    pk = d(HUB, "rt_peak_mean")
    add("join", f"On {day}, how many MWh did ERCOT's battery fleet discharge, and what was the average real-time price at the hub average in the peak hours of that day?",
        [float(sdc[sdc["ts_utc"].str[:10] == day]["value"].iloc[0]), float(pk[pk["ts_utc"].str[:10] == day]["value"].iloc[0])], [SD, DAILY],
        **J([SD, ST], PRICES), note=f"storage_daily_cycle mwh_discharged {day}; ercot_hub_prices_daily rt_peak_mean {day}")
    lq = E.rd(L, ["region", "q_status", "type_clean", "capacity_mw"])
    lq = lq[lq["region"] == "ERCOT"]
    act_s = lq[(lq["q_status"] == "active") & (lq["type_clean"] == "Solar")]
    sol_now = E.newest(E.series(B, "iso:ercot", "solar_operating_mw"))[0]
    add("join", "How many MW of solar requests are active in ERCOT's interconnection queue as Berkeley Lab records it, and how many MW of solar are operating in ERCOT in the newest inventory?",
        [pd.to_numeric(act_s["capacity_mw"], errors="coerce").sum(), sol_now], [L, B], **J([L], [B]),
        note="lbnl_interconnection_queue, ERCOT, active, type_clean Solar, sum of capacity_mw; storage_buildout_monthly solar_operating_mw, newest")
    neg = E.series(PA, "ercot:HB_WEST", "n_negative")
    wcr = merch("wind_capture_rate")
    add("join", "How many real-time intervals were priced below zero at HB_WEST in 2023, and what was wind's capture rate at the hub average in April 2023?",
        [E.month(neg, "2023-01"), E.month(wcr, "2023-04")], [PA, M], **J([PA, PM, DAILY], [M]), tolerances=[0.5, E.tol(E.month(wcr, "2023-04"))],
        note="ercot_peak_premium_annual HB_WEST n_negative 2023 (to the unit); merchant_revenue_monthly wind_capture_rate 2023-04")
    d4 = stack("dayahead_4h_revenue_total_usd_per_mw")
    b4 = merch("battery_4h_revenue_per_mw")
    add("join", "For July 2024, what does the battery model give a four-hour battery on the day-ahead schedule per MW, and what did a merchant four-hour battery earn per MW selling at the hub's real-time price?",
        [E.month(d4, "2024-07"), E.month(b4, "2024-07")], [K, M], **J([K], [M]), note="battery_stack_monthly dayahead_4h_revenue_total_usd_per_mw 2024-07; merchant_revenue_monthly battery_4h_revenue_per_mw 2024-07")
    es = E.rd(ES, ["entity", "variable", "ts_utc", "value", "event"])
    pooled = es[(es["event"] == "uri_2021") & (es["entity"] == HUB) & (es["variable"] == "rt_mean_effect_pooled")]
    feb = mo(rt, "2021-02")
    add("join", "What does the event study estimate as Winter Storm Uri's average daily effect on the real-time price at the hub average, and what was the highest daily average real-time price in February 2021?",
        [float(pooled["value"].iloc[0]), feb.max()], [ES, DAILY], **J([ES], PRICES + [EW]), note="event_study_estimates uri_2021 rt_mean_effect_pooled of HB_HUBAVG; ercot_hub_prices_daily rt_mean, max over February 2021")
    aq = E.series(AQ, "ercot:REGUP", "quantity_mw_plan")
    q_sep, p_sep = E.local(aq, "2026-09-03", "2026-10-01")["value"], E.local(ru, "2026-09-03", "2026-10-01")["value"]
    add("join", "From 3 to 30 September 2026, how many MW of regulation up did ERCOT plan to procure in the average hour, and what did regulation up clear at on average over the same days?",
        [q_sep.mean(), p_sep.mean()], [AQ, AS], **J([AQ], [AS]), note=f"ercot_as_quantities REGUP quantity_mw_plan, mean of {len(q_sep)} hours; ercot_as_prices REGUP mcpc_dam, mean of {len(p_sep)} hours, 3 to 30 September 2026 local")
    bat = E.local(E.series(ST, "eia930:ERCO", "net_generation_battery_mw"), "2026-09-01", "2026-10-01")["value"]
    add("join", "In September 2026, what was the highest hourly discharge of ERCOT's battery fleet, and what was the highest real-time interval price at the hub average?",
        [bat.max(), mo(rtmax, "2026-09").max()], [ST, DAILY], **J([ST, SD], PRICES), note="eia930_all_storage net_generation_battery_mw, max of September 2026 local; ercot_hub_prices_daily rt_max, max over September 2026")
    hd = E.local(E.series(D, "eia930:ERCO", "demand_mw"), "2026-09-01", "2026-10-01")["value"]
    add("join", "For September 2026, what was ERCOT's highest hourly demand and what was the average real-time price at the hub average?",
        [hd.max(), mo(rt, "2026-09").mean()], [D, DAILY], **J([D], PRICES), note="eia930_all_demand demand_mw, max of September 2026 local; ercot_hub_prices_daily rt_mean, mean of the days of September 2026")
    # the table gives a grid's total net imports by three measures (the sum of its pairs, EIA's total interchange, the
    # balance of generation and demand): any of the three is an answer
    ni, ni_ti, ni_bal = (E.series(BA, "eia930:ERCO", f"net_import_{m}_share_pct") for m in ("pairs", "total_interchange", "balance"))
    add("join", "In March 2025, what was the carbon intensity of ERCOT's demand, and what share of its demand did net imports meet?",
        [E.month(cid, "2025-03"), E.month(ni, "2025-03")], [CI, BA], **J([CI], [BA]),
        any_of=[[E.month(cid, "2025-03"), E.month(ni_ti, "2025-03")], [E.month(cid, "2025-03"), E.month(ni_bal, "2025-03")]],
        note="carbon_intensity_monthly intensity_demand 2025-03; ba_supply_monthly net_import_pairs_share_pct 2025-03 (or the total-interchange or the balance measure)")
    scr = merch("solar_capture_rate")
    add("join", "What was solar's capture rate at the hub average in May 2025, and how many MW of solar were operating in ERCOT that month?",
        [E.month(scr, "2025-05"), E.month(E.series(B, "iso:ercot", "solar_operating_mw"), "2025-05")], [M, B], **J([M], [B]),
        note="merchant_revenue_monthly solar_capture_rate 2025-05; storage_buildout_monthly solar_operating_mw 2025-05")
    ec = asp("ECRS")
    fa = stack("foresight_2h_revenue_ancillary_usd_per_mw")
    add("join", "What did ECRS clear at on average in July 2023, and how much of a two-hour battery's modelled revenue that month, with perfect foresight, came from ancillary services, per MW?",
        [E.local(ec, "2023-07-01", "2023-08-01")["value"].mean(), E.month(fa, "2023-07")], [AS, K], **J([AS], [K]),
        note="ercot_as_prices ECRS mcpc_dam, mean of July 2023 local; battery_stack_monthly foresight_2h_revenue_ancillary_usd_per_mw 2023-07")
    ev = E.rd(EW, ["entity", "variable", "ts_utc", "value", "event"])
    ell = ev[(ev["event"] == "elliott_2022") & (ev["ts_utc"] >= "2022-12-19") & (ev["ts_utc"] < "2022-12-30") & (ev["entity"] == "eia930:ERCO") & (ev["variable"] == "demand_max_mw")]
    ns = asp("NSPIN")
    add("join", "During Winter Storm Elliott (19 to 29 December 2022), what was ERCOT's highest hourly demand, and what was the highest hourly price of non-spinning reserve in December 2022?",
        [ell["value"].max(), E.local(ns, "2022-12-01", "2023-01-01")["value"].max()], [EW, AS], **J([EW], [AS]),
        note="event_window_daily elliott_2022 demand_max_mw, max; ercot_as_prices NSPIN mcpc_dam, max of December 2022 local")
    dur = E.series(B, "iso:ercot", "battery_operating_mwh_per_mw")
    rtr = E.series(SD, "eia930:ERCO", "round_trip_ratio")
    aug = rtr[rtr["ts_utc"].str[:7] == "2026-08"]["value"]
    add("join", "What is the average duration, in hours, of ERCOT's operating batteries in the newest inventory, and what was the fleet's average daily round-trip ratio in August 2026?",
        [E.newest(dur)[0], aug.mean()], [B, SD], **J(FLEET, [SD]), note=f"storage_buildout_monthly battery_operating_mwh_per_mw, newest; storage_daily_cycle round_trip_ratio, mean of {len(aug)} days of August 2026")
    pmm = E.series(PM, HUB, "peak_minus_midday_median")
    add("join", "In August 2025, by how much did the median peak-hours real-time price exceed the median midday price at the hub average, and what was solar's capture price that month?",
        [E.month(pmm, "2025-08"), E.month(merch("solar_capture_price"), "2025-08")], [PM, M], **J([PM], [M]),
        note="ercot_peak_premium_monthly peak_minus_midday_median 2025-08; merchant_revenue_monthly solar_capture_price 2025-08")
    oq = E.rd(Q2, ["status", "fuel_technology", "capacity_mw"]) if os.path.exists(os.path.join(E.OUT, Q2 + ".csv")) else None
    # a year's demand is demand_all_days_mwh: demand_mwh is over the days the supply figures hold (318 of 2025's 365), and
    # its sum makes 2025 look smaller than 2024, which it was not
    dem_all = E.series(BA, "eia930:ERCO", "demand_all_days_mwh")
    dy24, dy25 = yr(dem_all, 2024).sum(), yr(dem_all, 2025).sum()
    add("join", "How many MWh was ERCOT's demand in all of 2025, and what was the average real-time price at the hub average in 2025?",
        [dy25, yr(rt, 2025).mean()], [BA, DAILY], **J([BA], PRICES),
        note=f"ba_supply_monthly demand_all_days_mwh, sum of the months of 2025 (demand_mwh, over the held days only, sums to {yr(dem, 2025).sum():,.0f} and is not the year's demand); "
             "ercot_hub_prices_daily rt_mean, mean of the days of 2025")

    # ================================================================ vague: a newcomer's words
    V = lambda q, tables, **kw: add("vague", q, (), tables, **kw)  # noqa: E731
    V("Is power expensive in Texas right now?", PRICES, note="any current or recent hub price, said to be what it is")
    V("How much battery does Texas have?", FLEET, any_of=[[now_mw], [E.newest(mwh)[0]]], note=f"the newest operating MW ({now_m}) or MWh")
    V("When is electricity cheapest in Texas?", PRICES + [SH], note="an hour, a time of day or a season, from prices")
    V("Do batteries make money in Texas?", [K, M], text_any=["model", "could", "merchant"], note="the model or the merchant table, said to be what it is and not what batteries earned")
    V("How bad was the 2021 winter storm?", [EW, ES, DAILY, HIST, PA, PM, K, "battery_stack_stress_daily"], note="prices or demand in February 2021")
    V("Is the Texas grid getting cleaner?", [CI], note="carbon intensity over the years")
    V("How much power does Texas use?", [BA, D, EW, SH], note="demand: a month, a year or an hour")
    V("Are prices ever negative?", PRICES, note="intervals or hours below zero")
    V("How much of Texas's power comes from wind?", [G], note="generation by fuel, the newest weeks: the only window held")
    V("What's a normal price for electricity in ERCOT?", PRICES, note="a median or a mean over a stated period")
    V("Who owns the batteries?", [O, CAP], note="owners, the newest inventory")
    V("How many batteries are coming?", [B, O, CAP, L, Q2], note="planned MW or queue MW")
    V("Does Texas import power?", [BA], note="net imports and their share")
    V("What happens to prices in the evening?", PRICES + [SH], note="peak hours against midday or overnight")
    V("How long do Texas batteries last?", FLEET, any_of=[[E.newest(dur)[0]]], note="average duration, hours, the newest inventory")
    V("Is demand growing?", [BA, D], note="demand by year or by month against a year before")
    V("What do reserves cost?", [AS], note="reserve prices, a product and a period stated")
    V("How much could a solar farm earn?", [M], note="merchant solar revenue per MW or capture price")
    top_day = rt.loc[rt["value"].idxmax()]
    V("What was the most expensive day ever?", PRICES + [EW], text_any=["2021"], note=f"February 2021: the highest daily mean is {top_day['ts_utc'][:10]}")
    V("How busy is the interconnection queue?", [L, Q2], note="requests or MW, active")

    # ================================================================ followup: depends on the answer before
    F = lambda first, q, expected, tables, **kw: add("followup", q, expected, tables, first=first, **kw)  # noqa: E731
    F("What was the average real-time price at the ERCOT hub average in 2023?", "And in 2022?", [yr(rt, 2022).mean()], PRICES, note="rt_mean of HB_HUBAVG, mean of the days of 2022")
    F("What was the average real-time price at the ERCOT hub average in 2024?", "What about day-ahead?", [yr(da, 2024).mean()], PRICES, note="da_mean of HB_HUBAVG, mean of the days of 2024")
    w = d("ercot:HB_WEST", "rt_mean")
    F("What was the average real-time price at the ERCOT hub average in 2025?", "And at HB_WEST?", [yr(w, 2025).mean()], PRICES, note="rt_mean of HB_WEST, mean of the days of 2025")
    F("What was the average real-time price at the ERCOT hub average in August 2023?", "What was the highest interval price that month?", [mo(rtmax, "2023-08").max()], PRICES + [EW],
      note="rt_max of HB_HUBAVG, max over August 2023")
    rrs = asp("RRS")
    F("What did regulation up (REGUP) clear at on average in 2022?", "And responsive reserve?", [E.local(rrs, "2022-01-01", "2023-01-01")["value"].mean()], [AS], note="RRS mcpc_dam, mean of 2022 local")
    F("What did ECRS clear at on average in 2024?", "And the year after?", [E.local(ec, "2025-01-01", "2026-01-01")["value"].mean()], [AS], note="ECRS mcpc_dam, mean of 2025 local")
    F("How many MW of batteries were operating in ERCOT in December 2024?", "And a year earlier?", [E.month(mw, "2023-12")], FLEET, note="battery_operating_mw 2023-12")
    F("How many MW of batteries were operating in ERCOT in December 2024?", "How many MWh is that?", [E.month(mwh, "2024-12")], FLEET, note="battery_operating_mwh 2024-12")
    f4 = stack("foresight_4h_revenue_total_usd_per_mw")
    F("What could a two-hour battery have earned per MW in August 2023 with perfect foresight?", "And a four-hour one?", [E.month(f4, "2023-08")], [K], note="foresight_4h_revenue_total_usd_per_mw 2023-08")
    d2 = stack("dayahead_2h_revenue_total_usd_per_mw")
    F("What could a two-hour battery have earned per MW in August 2023 with perfect foresight?", "And on the day-ahead schedule?", [E.month(d2, "2023-08")], [K], note="dayahead_2h_revenue_total_usd_per_mw 2023-08")
    F("How many MWh was ERCOT's demand in July 2025?", "And the same month a year before?", [E.month(dem, "2024-07")], [BA], note="demand_mwh 2024-07")
    F("What was the carbon intensity of ERCOT's generation in April 2025?", "And of its demand?", [E.month(cid, "2025-04")], [CI], note="intensity_demand 2025-04")
    F("What was solar's capture rate at the hub average in June 2024?", "And wind's?", [E.month(wcr, "2024-06")], [M], note="wind_capture_rate 2024-06")
    F("What was solar's capture price at the hub average in June 2024?", "How does that compare with the flat price that month?", [E.month(merch("flat_price"), "2024-06")], [M, C],
      note="merchant_revenue_monthly flat_price 2024-06 (the simple mean of the month's real-time prices)")
    heat = ev[(ev["event"] == "ercot_heat_2023") & (ev["ts_utc"] >= "2023-08-01") & (ev["ts_utc"] < "2023-09-11") & (ev["entity"] == "eia930:ERCO") & (ev["variable"] == "demand_max_mw")]
    F("What was ERCOT's highest hourly demand during Winter Storm Elliott?", "And during the 2023 heat wave?", [heat["value"].max()], [EW], note="event_window_daily ercot_heat_2023 demand_max_mw, max")
    negh = E.series(PA, HUB, "n_negative")
    F("How many fifteen-minute real-time intervals were priced below zero at HB_WEST in 2024?", "And at the hub average?", [E.month(negh, "2024-01")], [PA, PM, DAILY], tolerance=0.5,
      note="ercot_peak_premium_annual HB_HUBAVG n_negative 2024")
    wd = lq[(lq["q_status"] == "withdrawn") & (lq["type_clean"] == "Battery")]
    F("How many interconnection requests in ERCOT has Berkeley Lab recorded as withdrawn?", "How many of those were batteries?", [float(len(wd))], [L], tolerance=0.5,
      note="lbnl_interconnection_queue, ERCOT, withdrawn, type_clean Battery, count")
    chg = E.series(SD, "eia930:ERCO", "mwh_charged")
    F("How many MWh did ERCOT's battery fleet discharge on 2026-08-15?", "And how much did it charge that day?", [float(chg[chg["ts_utc"].str[:10] == "2026-08-15"]["value"].iloc[0])], [SD, ST],
      note="storage_daily_cycle mwh_charged 2026-08-15")
    pkm = E.series(PA, HUB, "peak_median")
    F("What was the median real-time price in the peak hours at the hub average in 2025?", "And overnight?", [E.month(E.series(PA, HUB, "overnight_median"), "2025-01")], [PA], note="ercot_peak_premium_annual overnight_median 2025")
    F("What was the load-weighted real-time price at the hub average in May 2025?", "Was the simple mean lower?", [E.month(E.series(C, HUB, "rt_simple_mean"), "2025-05")], [C, M, DAILY],
      note="cost_of_power_monthly rt_simple_mean 2025-05")

    # ================================================================ premise: the question assumes what the tables contradict
    def P(q, expected, tables, truth, **kw):
        assert truth, f"the tables now agree with the premise of: {q}"
        add("premise", q, expected, tables, **kw)

    m23 = yr(rt, 2023).mean()
    P("Why did real-time prices at the ERCOT hub average come to more than 200 USD per MWh on average in 2023?", [m23], PRICES, m23 < 200, note=f"the mean of 2023 is {m23:.2f}")
    a, b = E.month(mw, "2024-12"), E.month(mw, "2025-12")
    P("ERCOT's battery fleet shrank during 2025. How many MW did it lose between December 2024 and December 2025?", [a, b], FLEET, b > a,
      text_any=["grew", "grown", "rose", "increase", "added", "gain", "higher", "more", "up "], note=f"battery_operating_mw {a} in 2024-12, {b} in 2025-12: it grew")
    first_ecrs = ec["ts_utc"].min()[:7]
    P("ECRS has been an ERCOT reserve product since 2018. What did it clear at on average in 2019?", [], [AS], first_ecrs > "2019-12", text=[first_ecrs[:4]], status_any=True,
      note=f"ECRS begins {first_ecrs}: the answer must say so, as an answer or as a refusal")
    ni25 = yr(ni, 2025)
    P("Texas imports about a third of its electricity. Which month of 2025 had the highest import share, and what was it?", [ni25.max()], [BA],
      max(yr(x, 2025).max() for x in (ni, ni_ti, ni_bal)) < 20, any_of=[[yr(ni_ti, 2025).max()], [yr(ni_bal, 2025).max()]],
      note=f"net_import_pairs_share_pct of 2025: at most {ni25.max():.2f} percent (the other two measures: {yr(ni_ti, 2025).max():.2f}, {yr(ni_bal, 2025).max():.2f})")
    nh = yr(d(HUB, "rt_hours_below_zero"), 2025).sum()
    nint = E.month(negh, "2025-01")
    P("Real-time prices at the ERCOT hub average never go below zero. What is the lowest they got in 2025?", [yr(d(HUB, "rt_min"), 2025).min()], PRICES, yr(d(HUB, "rt_min"), 2025).min() < 0,
      note=f"rt_min of 2025 is below zero ({nint:.0f} intervals, {nh:.0f} hours below zero in 2025)")
    umax = mo(rtmax, "2021-02").max()
    P("During Winter Storm Uri real-time prices at the hub average stayed under 1,000 USD per MWh. How high did they get?", [umax], PRICES + [EW], umax > 1000, note=f"the highest interval price of February 2021 is {umax}")
    y = 2024
    P(f"Day-ahead prices at the hub average are always below real-time prices. By how much were they lower in {y}?", [yr(da, y).mean(), yr(rt, y).mean()], PRICES, yr(da, y).mean() > yr(rt, y).mean(),
      note=f"{y}: da_mean {yr(da, y).mean():.2f}, rt_mean {yr(rt, y).mean():.2f}: day-ahead was higher")
    ru_years = {yy: E.local(ru, f"{yy}-01-01", f"{yy + 1}-01-01")["value"].mean() for yy in range(2018, 2026)}
    hi_y = max(ru_years, key=ru_years.get)
    P("Regulation up has cleared above 100 USD per MW per hour on average in every year since 2018. In which year was it highest?", [ru_years[hi_y]], [AS], min(ru_years.values()) < 100,
      text=[str(hi_y)], note=f"yearly means of REGUP: highest {hi_y} at {ru_years[hi_y]:.2f}; lowest {min(ru_years.values()):.2f}")
    t = E.month(f2, "2023-08")
    P("The battery model gives a two-hour battery 500,000 USD per MW for August 2023 with perfect foresight. How much of that was ancillary services?", [t, E.month(fa, "2023-08")], [K], t < 400000,
      note=f"foresight_2h_revenue_total_usd_per_mw 2023-08 is {t}")
    c19, c25 = yr(ci, 2019).mean(), yr(ci, 2025).mean()
    P("The carbon intensity of ERCOT's generation has risen every year since 2019. How much higher was it in 2025 than in 2019?", [c19, c25], [CI], c25 < c19,
      text_any=["fell", "fallen", "lower", "declin", "decreas", "drop", "down"], note=f"mean intensity_generation {c19:.1f} in 2019, {c25:.1f} in 2025: it fell")
    s25 = scr[scr["ts_utc"].str[:4] == "2025"]
    top = s25.loc[s25["value"].idxmax()]   # the month of 2025 in which solar's capture rate was highest: the premise is put to that month
    s7, name = float(top["value"]), pd.Timestamp(top["ts_utc"]).strftime("%B %Y")
    # the rate is in percent of the flat price: 88 is 88 percent. In no month of 2025 did solar capture the flat price
    P(f"In {name} solar in ERCOT captured more than the flat price. By how much was its capture rate above 100 percent?", [s7], [M], s7 < 100,
      note=f"solar_capture_rate {top['ts_utc'][:7]} is {s7} percent, the highest of 2025: below 100")
    P("ERCOT has more than 50,000 MW of batteries operating. When did it pass that mark?", [now_mw], FLEET, now_mw < 50000, note=f"battery_operating_mw is {now_mw} in {now_m}")
    means24 = {p: E.local(asp(p), "2024-01-01", "2025-01-01")["value"].mean() for p in ("REGUP", "REGDN", "RRS", "NSPIN", "ECRS")}
    top24 = max(means24, key=means24.get)
    P("Non-spinning reserve was the most expensive ERCOT reserve product in 2024. What did it average?", [means24["NSPIN"], means24[top24]], [AS], top24 != "NSPIN",
      note=f"2024 means: {', '.join(f'{k} {v:.2f}' for k, v in means24.items())}: the highest is {top24}")
    hubs = {h: yr(d(f"ercot:{h}", "rt_mean"), 2025).mean() for h in ("HB_NORTH", "HB_SOUTH", "HB_WEST", "HB_HOUSTON")}
    lowest = min(hubs, key=hubs.get)
    top_h = max(hubs, key=hubs.get)
    P(f"{lowest} had the highest real-time prices of ERCOT's four regional hubs in 2025. What did it average?", [hubs[lowest], hubs[top_h]], PRICES, True,
      note=f"2025 rt_mean: {', '.join(f'{k} {v:.2f}' for k, v in hubs.items())}: {lowest} was the lowest and {top_h} the highest")
    nw = E.month(neg, "2024-01")
    P("There were no real-time intervals below zero at HB_WEST in 2024, were there?", [nw], [PA, PM, DAILY], nw > 0, tolerance=0.5, note=f"n_negative of HB_WEST in 2024 is {nw:.0f}")
    pch, pdh = E.series(SD, "eia930:ERCO", "peak_charge_hour"), E.series(SD, "eia930:ERCO", "peak_discharge_hour")
    c_med, d_med = yr(pch, 2026).median(), yr(pdh, 2026).median()
    P("ERCOT's batteries charge in the evening and discharge around midday. At what hours exactly, in 2026?", [], [SD, ST, SH], c_med < d_med,
      text_any=["opposite", "reverse", "other way", "instead", "rather", "in fact", "actually"], note=f"2026 medians: peak charge hour {c_med:.0f}, peak discharge hour {d_med:.0f} local: the other way round")
    act = lq[lq["q_status"] == "active"]
    by_type = pd.to_numeric(act["capacity_mw"], errors="coerce").groupby(act["type_clean"]).sum().sort_values(ascending=False)
    gas = float(by_type.get("Gas", 0.0))
    P("Most of the MW active in ERCOT's interconnection queue is gas, as Berkeley Lab records it. How many MW of gas are active?", [gas, float(by_type.iloc[0])], [L], by_type.index[0] != "Gas",
      note=f"active MW by type: {', '.join(f'{k} {v:,.0f}' for k, v in by_type.head(4).items())}")
    P("ERCOT's demand fell in 2025 compared with 2024. By how many MWh?", [dy24, dy25], [BA], dy25 > dy24, text_any=["rose", "grew", "higher", "increase", "more", "up "],
      note=f"demand_all_days_mwh summed: {dy24:,.0f} in 2024, {dy25:,.0f} in 2025: it rose. (demand_mwh, over held days only, sums lower in 2025 because 47 of its days are left out: "
           "an answer that calls that a fall has gone along with the premise)")
    a22, a23 = mo(rt, "2022-08").mean(), mo(rt, "2023-08").mean()
    P("Why was the average real-time price at the hub average lower in August 2023 than in August 2022?", [a22, a23], PRICES, a23 > a22, note=f"rt_mean: August 2022 {a22:.2f}, August 2023 {a23:.2f}: it was higher")
    d24 = E.month(dur, "2024-12")
    P("ERCOT's batteries average more than six hours of duration. What was the average at the end of 2024?", [d24], FLEET, d24 < 6, note=f"battery_operating_mwh_per_mw 2024-12 is {d24}")

    # ================================================================ outside: what the ERCOT tables do not hold
    X = lambda q, nearest=(), **kw: add("outside", q, (), (), nearest=list(nearest), **kw)  # noqa: E731
    X("What did capacity clear at in PJM's last base residual auction?", note="another grid, and a market ERCOT does not have")
    X("What was the real-time price at CAISO's SP15 hub yesterday?", PRICES, note="another grid: the general chat")
    X("What does a household in Houston pay per kWh on its electricity bill?", PRICES, note="retail prices are not in the ERCOT tables; wholesale hub prices are")
    X("What will the peak-hours real-time price at the hub average be next August?", PRICES, note="a forecast")
    X("What was the real-time price at the resource node ADL_RN yesterday?", PRICES, note="node prices are not in the ERCOT tables; hub prices are")
    X("What was the price of natural gas at the Waha hub last month?", note="gas prices are not in the ERCOT tables")
    X("How much congestion rent did ERCOT collect on its CRR auctions in 2024?", note="congestion and CRRs are not held")
    X("Which power plants tripped offline during Winter Storm Uri, and how many MW each?", [EW, ES, "battery_stack_stress_daily"], note="unit outages are not held; the event's demand and prices are")
    X("How many MWh of wind did ERCOT curtail in 2025?", [G, M], note="curtailment is not in the ERCOT tables of this chat")
    X("How many MW of natural gas plants are installed in ERCOT?", [G, L, Q2], note="the generator inventory is held for batteries only; generation by fuel and the queue are the nearest")
    X("What share of ERCOT's electricity came from nuclear in 2023?", [G], note="generation by fuel is held for the newest weeks only")
    X("What was the average day-ahead price at the hub average in 2012?", PRICES, note="hub prices begin in 2015")
    X("What is the weather forecast for Dallas tomorrow?", note="not energy data the tables hold")
    X("How many customers lost power during Winter Storm Uri?", [EW, ES], note="outage counts are not held; the event's demand and prices are")
    X("How much profit did Vistra make from its Texas batteries in 2024?", [O, K, M, CAP], note="a company's accounts are not held; owners and a model are")
    X("What is the levelized cost of a new solar farm in West Texas?", [M], note="costs are not held; merchant revenue is")
    X("What was the average real-time price in the load zone LZ_WEST in 2024?", PRICES, note="load zones are not held; hubs are")
    X("How much hydrogen is produced in Texas?", note="not held")
    X("What was the day-ahead price at MISO's Indiana hub last week?", PRICES, note="another grid: the general chat")
    X("What is ERCOT's planning reserve margin for the summer of 2027?", [B, L, Q2, AS, AQ], note="reserve margins and forecasts are not held")

    assert counts == {"join": 20, "vague": 20, "followup": 20, "premise": 20, "outside": 20}, counts
    return Q


def main():
    qs = build()
    out = os.path.join(HERE, "questions_ercot_s121.yaml")
    head = ("# Generated by warehouse/chat/eval/ercot_expected_s121.py. Do not edit by hand.\n"
            "# The second ERCOT set (session 121): 100 questions of five kinds. Expected numbers are computed from the CSVs in warehouse/output,\n"
            "# independently of the tools; every wrong premise was checked against the tables when this file was written.\n")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(head)
        yaml.safe_dump({"today": TODAY, "questions": qs}, f, sort_keys=False, allow_unicode=True, width=200)
    print(f"wrote {out}: {len(qs)} questions")
    for q in qs:
        print(f"{q['id']} {q['kind']:8s} {q['expected']} {q.get('any_of', '')} | {q['note'][:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
