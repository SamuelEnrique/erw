#!/usr/bin/env python3
"""Build the evaluation set for warehouse/chat/ask.py (session 12, Task 3).

Energy Research Warehouse (ERW). Computes the expected answer of every question
directly from the CSVs in warehouse/output with pandas, independently of
warehouse/chat/tools.py and of the erw package: each CSV is read on its own
(provenance lines skipped by count), filtered and aggregated here. The ERCOT
peak-premium answers are recomputed from the raw 15-minute yearly tables, not
read from the derived tables. Writes warehouse/chat/eval/questions.yaml.

    python warehouse/chat/eval/expected.py

The questions are fixed to TODAY (2026-09-26): relative words such as "yesterday"
are resolved against it, and eval.py passes the same date to the model.
Each question has:
  expected   numbers the answer must contain, each within its tolerance
  text       words the answer must contain (for example the ISO that won)
  tables     tables a correct citation may name (at least one must be cited)
  refuse     true when the right answer is "not in the warehouse"
  internal   true when the answer must say the table is internal
"""

import os

import numpy as np
import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
TODAY = "2026-09-26"


def csv(name):
    path = os.path.join(OUT, name + ".csv")
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    df = pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)
    if "ts_utc" in df:
        df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
        df["value"] = df["value"].astype(float)
    return df


def local_day(df, tz, day):
    start = pd.Timestamp(day, tz=tz).tz_convert("UTC")
    end = (pd.Timestamp(day, tz=tz) + pd.Timedelta(days=1)).tz_convert("UTC")
    return df[(df["ts_utc"] >= start) & (df["ts_utc"] < end)]


def between(df, a, b):
    return df[(df["ts_utc"] >= pd.Timestamp(a, tz="UTC")) & (df["ts_utc"] < pd.Timestamp(b, tz="UTC"))]


def one(df, **eq):
    for k, v in eq.items():
        df = df[df[k] == v]
    return df


def r(x, d=4):
    return float(round(float(x), d))


def main():
    Q = []

    def add(qid, sector, shape, question, expected=(), tol=0.01, text=(), tables=(), refuse=False,
            internal=False, note=""):
        Q.append({"id": qid, "sector": sector, "shape": shape, "question": question,
                  "expected": [r(v) for v in expected], "tolerance": tol, "text": list(text),
                  "tables": list(tables), "refuse": refuse, "internal": internal, "note": note})

    # ---- power prices ----------------------------------------------------------------
    dam = pd.concat([csv("ercot_dam_hub_prices"), csv("ercot_dam_hub_prices_2026")])
    d = local_day(one(dam, node="HB_NORTH"), "America/Chicago", "2026-09-25")
    assert len(d) == 24, len(d)
    add("q01", "power", "series",
        "What was yesterday's average day-ahead price at ERCOT's HB_NORTH hub, over the ERCOT operating day (America/Chicago)?",
        [d["value"].mean()], tables=["ercot_dam_hub_prices", "ercot_dam_hub_prices_2026"],
        note="mean of the 24 hourly spp_dam values of 2026-09-25 local")

    rt_tables = {"ERCOT": ["ercot_rtm_hub_prices"], "CAISO": ["caiso_rtm_hub_prices"],
                 "NYISO": ["nyiso_rtm_zone_prices"], "ISO-NE": ["isone_rtm_zone_prices", "isone_rtm_zone_prices_hourly"],
                 "MISO": ["miso_rtm_hub_prices"]}
    best = {}
    for iso, ts in rt_tables.items():
        for t in ts:
            w = between(csv(t), "2026-09-18", "2026-09-25")
            if len(w) and (iso not in best or w["value"].max() > best[iso][0]):
                best[iso] = (w["value"].max(), t)
    win = max(best, key=lambda k: best[k][0])
    add("q02", "power", "series",
        "Across the public real-time hub and zone price tables, which ISO had the highest single real-time price between 2026-09-18 and 2026-09-24 (UTC, both days included), and what was it?",
        [best[win][0]], text=[win], tables=[best[win][1]],
        note="max per ISO: " + ", ".join(f"{k} {v[0]:.2f} ({v[1]})" for k, v in best.items()))

    def peak_iqr(year):
        df = one(csv(f"ercot_rtm_hub_prices_{year}"), node="HB_HUBAVG")
        h = df["ts_utc"].dt.tz_convert("America/Chicago").dt.hour
        v = df.loc[(h >= 16) & (h < 21), "value"].to_numpy()
        return np.percentile(v, 75) - np.percentile(v, 25)
    i15, i25 = peak_iqr(2015), peak_iqr(2025)
    add("q03", "power", "derived",
        "What was the ERCOT HB_HUBAVG peak-block (16:00 to 21:00) interquartile range of real-time prices in 2015, and in 2025?",
        [i15, i25], tables=["ercot_peak_premium_annual", "ercot_rtm_hub_prices_2015", "ercot_rtm_hub_prices_2025"],
        note="recomputed from the raw 15-minute tables")

    caiso = one(csv("caiso_dam_hub_prices"), node="TH_SP15_GEN-APND")
    w = between(caiso, "2026-09-01", "2026-09-25")
    add("q04", "power", "series",
        "What was the highest day-ahead LMP at CAISO's SP15 trading hub (TH_SP15_GEN-APND) between 2026-09-01 and 2026-09-24 (UTC, both days included)?",
        [w["value"].max()], tables=["caiso_dam_hub_prices"])

    ny = local_day(one(csv("nyiso_rtm_zone_prices"), node="N.Y.C."), "America/New_York", "2026-09-20")
    add("q05", "power", "series",
        "What was the average real-time price in NYISO's N.Y.C. zone on 2026-09-20, New York local time?",
        [ny["value"].mean()], tables=["nyiso_rtm_zone_prices"], note=f"{len(ny)} fifteen-minute means")

    ew = between(one(csv("ercot_rtm_hub_prices"), node="HB_WEST"), "2026-09-01", "2026-09-25")
    add("q06", "power", "series",
        "What was the median ERCOT real-time settlement point price at HB_WEST from 2026-09-01 to 2026-09-24 (UTC, both days included)?",
        [ew["value"].median()], tables=["ercot_rtm_hub_prices"])

    y25 = one(csv("ercot_rtm_hub_prices_2025"), node="HB_WEST")
    add("q07", "power", "series",
        "How many 15-minute real-time intervals at ERCOT HB_WEST had a price at or below zero in 2025 (ERCOT operating year)?",
        [int((y25["value"] <= 0).sum())], tol=0.5, tables=["ercot_rtm_hub_prices_2025", "ercot_peak_premium_annual"])

    hub25 = one(csv("ercot_rtm_hub_prices_2025"), node="HB_HUBAVG")["value"].to_numpy()
    add("q08", "power", "derived",
        "What was the 99.9th percentile of ERCOT HB_HUBAVG real-time prices in 2025?",
        [np.percentile(hub25, 99.9)], tables=["ercot_peak_premium_annual", "ercot_rtm_hub_prices_2025"])

    ne = local_day(one(csv("isone_dam_zone_prices"), node=".H.INTERNAL_HUB"), "America/New_York", "2026-09-24")
    add("q09", "power", "series",
        "What was the average day-ahead LMP at the ISO-NE internal hub on 2026-09-24, New England local time?",
        [ne["value"].mean()], tables=["isone_dam_zone_prices"])

    mi = local_day(one(csv("miso_rtm_hub_prices"), node="INDIANA.HUB"), "Etc/GMT+5", "2026-09-23")
    add("q10", "power", "series",
        "What was the highest hourly real-time LMP at MISO's Indiana hub on 2026-09-23, MISO market time (EST)?",
        [mi["value"].max()], tables=["miso_rtm_hub_prices"], note=f"{len(mi)} hours")

    sp = between(one(csv("spp_dam_hub_prices"), node="SPPNORTH_HUB"), "2026-09-15", "2026-09-25")
    add("q11", "power", "series",
        "What was the lowest day-ahead LMP at SPP's North hub between 2026-09-15 and 2026-09-24 (UTC, both days included)?",
        [sp["value"].min()], tables=["spp_dam_hub_prices"])

    y23 = one(csv("ercot_rtm_hub_prices_2023"), node="HB_HUBAVG")
    loc = y23["ts_utc"].dt.tz_convert("America/Chicago")
    aug = y23[(loc.dt.month == 8) & (loc.dt.hour >= 16) & (loc.dt.hour < 21)]
    add("q12", "power", "derived",
        "What was the median real-time price at ERCOT HB_HUBAVG in the 16:00 to 21:00 peak block in August 2023?",
        [aug["value"].median()], tables=["ercot_peak_premium_monthly", "ercot_rtm_hub_prices_2023"])

    # ---- demand and generation ---------------------------------------------------------
    us = between(one(csv("eia930_us48_demand"), variable="demand_mw"), "2026-09-01", "2026-09-25")
    add("q13", "power", "series",
        "What was the highest hourly US Lower 48 electricity demand between 2026-09-01 and 2026-09-24 (UTC, both days included), in MW?",
        [us["value"].max()], tol=0.5, tables=["eia930_us48_demand"])

    so = between(one(csv("eia930_erco_generation"), variable="net_generation_solar_mw"), "2026-09-20", "2026-09-21")
    assert len(so) == 24
    add("q14", "power", "series",
        "What was the sum of ERCOT's 24 hourly solar net generation values (MW) on 2026-09-20 (UTC day)?",
        [so["value"].sum()], tol=0.5, tables=["eia930_erco_generation"])

    ca = between(one(csv("eia930_ciso_demand"), variable="demand_mw"), "2026-09-15", "2026-09-16")
    add("q15", "power", "series",
        "What was CAISO's average hourly demand on 2026-09-15 (UTC day), in MW?",
        [ca["value"].mean()], tol=0.5, tables=["eia930_ciso_demand"])

    # ---- oil, gas, products, retail ------------------------------------------------------
    fu = csv("eia_fuel_spot_prices")
    hh = one(fu, entity="eia:henry_hub")
    v = hh[hh["ts_utc"] == pd.Timestamp("2026-09-15", tz="UTC")]["value"]
    assert len(v) == 1
    add("q16", "gas", "series", "What was the Henry Hub natural gas spot price on 2026-09-15?",
        [v.iloc[0]], tables=["eia_fuel_spot_prices", "fred_daily_spot_prices"])

    br = between(one(fu, entity="eia:brent"), "2026-08-01", "2026-09-01")
    add("q17", "oil", "series", "What was the average Brent crude spot price in August 2026, according to EIA?",
        [br["value"].mean()], tables=["eia_fuel_spot_prices"], note=f"{len(br)} trading days")

    mx = hh.loc[hh["value"].idxmax()]
    add("q18", "gas", "series",
        "What is the highest Henry Hub spot price in the warehouse, and on what date was it?",
        [mx["value"]], text=[mx["ts_utc"].strftime("%Y")], tables=["eia_fuel_spot_prices", "fred_daily_spot_prices"],
        note=f"on {mx['ts_utc']:%Y-%m-%d}")

    ps = one(csv("eia_product_spot_prices"), entity="eia:EER_EPMRU_PF4_Y35NY_DPG")
    lt = ps.loc[ps["ts_utc"].idxmax()]
    add("q19", "products", "series",
        "What is the latest New York Harbor conventional regular gasoline spot price in the warehouse?",
        [lt["value"]], tol=0.001, tables=["eia_product_spot_prices"], note=f"{lt['ts_utc']:%Y-%m-%d}, USD/gal")

    st = one(csv("eia_petroleum_stocks_weekly"), entity="eia:WCESTUS1")
    ls = st.loc[st["ts_utc"].idxmax()]
    add("q20", "oil", "series",
        "What were US commercial crude oil stocks (excluding the Strategic Petroleum Reserve) in the latest week in the warehouse?",
        [ls["value"]], tol=0.5, tables=["eia_petroleum_stocks_weekly"], note=f"week of {ls['ts_utc']:%Y-%m-%d}, kbbl")

    rp = one(csv("eia_retail_electricity_prices"), entity="eia:retail_price:TX:RES")
    rv = rp[rp["ts_utc"] == pd.Timestamp("2026-07-01", tz="UTC")]["value"]
    add("q21", "power", "series",
        "What was the average residential retail electricity price in Texas in July 2026?",
        [rv.iloc[0]], tables=["eia_retail_electricity_prices"], note="USD/MWh")

    im = one(csv("eia_crude_imports_by_country"), entity="eia:MCRIMUSCA2")
    iv = im[im["ts_utc"] == pd.Timestamp("2026-06-01", tz="UTC")]["value"]
    add("q22", "oil", "series",
        "How much crude oil did the US import from Canada in June 2026?",
        [iv.iloc[0]], tol=0.5, tables=["eia_crude_imports_by_country"], note="kbbl/d")

    wti = one(fu, entity="eia:wti_cushing")
    wv = between(wti, "2026-09-01", "2026-09-25")
    add("q23", "oil", "series",
        "What was the lowest WTI Cushing spot price between 2026-09-01 and 2026-09-24?",
        [wv["value"].min()], tables=["eia_fuel_spot_prices", "fred_daily_spot_prices"])

    # ---- entities ------------------------------------------------------------------------
    op = csv("eia860m_operating_generators")
    tx = op[(op["state"] == "TX") & (op["technology_group"] == "natural_gas")]
    add("q24", "power", "entities",
        "How many operating natural gas generators are there in Texas in the EIA-860M inventory, and what is their total nameplate capacity in MW?",
        [len(tx), tx["nameplate_mw"].astype(float).sum()], tol=0.5, tables=["eia860m_operating_generators"])

    pl = csv("eia860m_planned_generators")
    sol = pl[pl["technology_group"] == "solar"]
    add("q25", "power", "entities",
        "What is the total nameplate capacity of planned solar generators (planned and under construction) in the EIA-860M inventory?",
        [sol["nameplate_mw"].astype(float).sum()], tol=0.5, tables=["eia860m_planned_generators"])

    eq = csv("ercot_interconnection_queue")
    act = eq[eq["status"] == "active"]
    add("q26", "power", "entities",
        "How many active projects are in the ERCOT interconnection queue, and what is their total capacity in MW?",
        [len(act), act["capacity_mw"].replace("", np.nan).astype(float).sum()], tol=0.5,
        tables=["ercot_interconnection_queue"])

    # ---- events ----------------------------------------------------------------------------
    ni = csv("news_index")
    ed = pd.to_datetime(ni["event_date"].where(ni["event_date"].str.contains("T"), ni["event_date"] + "T00:00:00Z"), utc=True)
    n25 = int(((ed >= pd.Timestamp("2026-09-25", tz="UTC")) & (ed < pd.Timestamp("2026-09-26", tz="UTC"))).sum())
    add("q27", "news", "events", "How many news stories in the news index are dated 2026-09-25 (UTC)?",
        [n25], tol=0.5, tables=["news_index"])

    # ---- internal ----------------------------------------------------------------------------
    pj = csv("pjm_rpm_capacity_prices")
    rto = pj[(pj["entity"] == "pjm:RTO") & (pj["ts_utc"] == pd.Timestamp("2025-06-01", tz="UTC"))]
    assert len(rto) == 1, rto
    add("q28", "capacity", "series",
        "What was the PJM RTO capacity clearing price for the 2025/2026 delivery year?",
        [rto["value"].iloc[0]], tables=["pjm_rpm_capacity_prices"], internal=True,
        note="USD/MW-day; the table is internal and the answer must say so")

    # ---- not in the warehouse -----------------------------------------------------------------
    add("q29", "power", "none", "What was the PJM Western Hub real-time LMP on 2026-09-20?", refuse=True,
        note="no PJM energy price table")
    add("q30", "metals", "none", "What is the latest lithium carbonate spot price?", refuse=True,
        note="no lithium prices")

    with open(os.path.join(HERE, "questions.yaml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# Energy Research Warehouse (ERW): evaluation set for warehouse/chat/ask.py (session 12).\n"
                "# Generated by warehouse/chat/eval/expected.py from the CSVs in warehouse/output with pandas,\n"
                f"# independently of warehouse/chat/tools.py. Fixed date: today = {TODAY}. Do not edit by hand.\n")
        yaml.safe_dump({"today": TODAY, "questions": Q}, f, sort_keys=False, allow_unicode=True, width=120)
    for q in Q:
        print(q["id"], q["expected"], q["text"], q["note"])


if __name__ == "__main__":
    main()
