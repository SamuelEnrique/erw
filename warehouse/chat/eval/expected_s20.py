#!/usr/bin/env python3
"""Build the session 20 evaluation set: the 30 questions of expected.py plus 15 on the new tables.

Energy Research Warehouse (ERW), session 20, Task 2. The 30 questions are recomputed by
expected.py from today's tables (one answer moved since session 13: q27, the news stories dated
2026-09-25, because later ingests added two). The 15 new ones cover curtailment, the energy mix,
retail sales by sector, the trader view, deals and datacenters. Every expected answer is computed
here with pandas straight from the CSVs, independently of warehouse/chat/tools.py and of the erw
package: the energy mix from the EIA source table (not the derived groups), and the trader
metrics from the raw day-ahead and real-time price tables and Henry Hub (not the derived table).
Writes warehouse/chat/eval/questions_s20.yaml (45 questions, today = 2026-09-26).

    python warehouse/chat/eval/expected_s20.py
"""

import os
import sys
import tempfile

import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import expected as e  # noqa: E402  the session 12 generator: csv(), local_day(), r(), TODAY

OUT_FILE = os.path.join(HERE, "questions_s20.yaml")


def q(qid, sector, shape, question, expected, tables, tol=0.01, text=(), note=""):
    return {"id": qid, "sector": sector, "shape": shape, "question": question,
            "expected": [e.r(x) for x in expected], "tolerance": tol, "text": list(text),
            "tables": tables, "refuse": False, "internal": False, "note": note}


def new_questions():
    Q = []
    # ---- curtailment -------------------------------------------------------------------------
    c = e.csv("caiso_curtailment_daily")
    apr = c[(c["variable"] == "curtailed_solar_mwh") & (c["ts_utc"].dt.strftime("%Y-%m") == "2026-04")]
    assert apr["ts_utc"].nunique() == 30
    Q.append(q("s20q01", "power", "series", "What was CAISO's total solar curtailment in April 2026, in MWh?",
               [apr["value"].sum()], ["caiso_curtailment_daily", "iso_curtailment_monthly"], tol=1,
               note="sum of the 30 daily curtailed_solar_mwh values"))
    s = e.csv("spp_curtailment_daily")
    w25 = s[(s["entity"] == "spp:SPP") & (s["variable"] == "curtailed_wind_mwh") & (s["ts_utc"].dt.year == 2025)]
    Q.append(q("s20q02", "power", "series",
               "What was the total wind curtailment in SPP's own balancing authority area (entity spp:SPP) in calendar 2025, in MWh?",
               [w25["value"].sum()], ["spp_curtailment_daily", "iso_curtailment_monthly"], tol=1,
               note=f"sum of {w25['ts_utc'].nunique()} daily values"))
    er = e.csv("ercot_wind_solar_hsl_daily")
    x = er[(er["variable"] == "wind_below_hsl_mwh") & (er["ts_utc"].dt.strftime("%Y-%m-%d") == "2026-09-24")]
    assert len(x) == 1
    Q.append(q("s20q03", "power", "series",
               "By how many MWh did ERCOT's system-wide wind output fall below its High Sustained Limit on the operating day 2026-09-24?",
               [x["value"].iloc[0]], ["ercot_wind_solar_hsl_daily"], tol=0.5))

    # ---- energy mix (from the EIA source table) ------------------------------------------------
    g = e.csv("eia_state_generation_monthly")
    tx = g[(g["entity"] == "eia:generation:TX:COW") & (g["ts_utc"].dt.strftime("%Y-%m") == "2026-07")]
    Q.append(q("s20q04", "power", "series", "What was Texas's net generation from coal in July 2026, in MWh?",
               [tx["value"].iloc[0]], ["state_generation_mix_monthly", "eia_state_generation_monthly"], tol=1))
    us = g[(g["entity"] == "eia:generation:US:WND") & (g["ts_utc"].dt.year == 2025)]
    assert len(us) == 12
    Q.append(q("s20q05", "power", "series", "What was total US net generation from wind in calendar 2025, in MWh?",
               [us["value"].sum()], ["state_generation_mix_monthly", "eia_state_generation_monthly"], tol=1))
    sun = g[g["entity"].str.fullmatch(r"eia:generation:[A-Z]{2}:SUN") & (g["ts_utc"].dt.year == 2025)].copy()
    sun["st"] = sun["entity"].str.split(":").str[2]
    tot = sun[sun["st"] != "US"].groupby("st")["value"].sum().sort_values()
    names = {"CA": "California", "TX": "Texas"}
    top = tot.index[-1]
    Q.append(q("s20q06", "power", "series",
               "Which state, by name, had the most utility-scale solar net generation in calendar 2025, and how many MWh?",
               [tot.iloc[-1]], ["state_generation_mix_monthly", "eia_state_generation_monthly"], tol=1,
               text=[names.get(top, top)], note=f"runner-up {tot.index[-2]} {tot.iloc[-2]:.2f}"))

    # ---- retail sales by sector ----------------------------------------------------------------
    rs = e.csv("eia_retail_sales_monthly")
    va = rs[(rs["entity"] == "eia:retail_sales:VA:COM") & (rs["ts_utc"].dt.year == 2025)]
    assert len(va) == 12
    Q.append(q("s20q07", "power", "series",
               "What were Virginia's commercial-sector retail electricity sales in calendar 2025, in MWh?",
               [va["value"].sum()], ["eia_retail_sales_monthly"], tol=1))
    ind = rs[(rs["entity"] == "eia:retail_sales:US:IND") & (rs["ts_utc"].dt.strftime("%Y-%m") == "2026-07")]
    Q.append(q("s20q08", "power", "series",
               "What were US industrial-sector retail electricity sales in July 2026, in MWh?",
               [ind["value"].iloc[0]], ["eia_retail_sales_monthly"], tol=1))
    cu = rs[(rs["entity"] == "eia:customers:TX:RES") & (rs["ts_utc"].dt.strftime("%Y-%m") == "2026-07")]
    Q.append(q("s20q09", "power", "series",
               "How many residential electricity customers did Texas have in July 2026, according to EIA?",
               [cu["value"].iloc[0]], ["eia_retail_sales_monthly"], tol=0.5))

    # ---- trader view (from the raw price tables) ---------------------------------------------
    da = e.csv("ercot_dam_hub_prices")
    d = e.local_day(da[da["node"] == "HB_NORTH"], "America/Chicago", "2026-09-20")
    assert len(d) == 24
    Q.append(q("s20q10", "power", "derived",
               "In the ERW's trader view, what was ERCOT HB_NORTH's average day-ahead price on the ERCOT operating day 2026-09-20?",
               [d["value"].mean()], ["ercot_trader_daily", "ercot_dam_hub_prices"],
               note="mean of the 24 hourly day-ahead prices of the local day"))
    mda = e.csv("miso_dam_hub_prices")
    mrt = e.csv("miso_rtm_hub_prices")
    a = mda[mda["node"] == "INDIANA.HUB"].set_index("ts_utc")["value"]
    b = mrt[mrt["node"] == "INDIANA.HUB"].set_index("ts_utc")["value"]
    sp = (b - a).dropna()
    day = sp.index.tz_convert("EST").strftime("%Y-%m-%d")
    sp = sp[(day >= "2026-09-01") & (day <= "2026-09-24")]
    Q.append(q("s20q11", "power", "derived",
               "What was the largest hourly real-time minus day-ahead price spread at MISO's INDIANA.HUB over the operating days "
               "2026-09-01 to 2026-09-24 (both included), in USD/MWh?",
               [sp.max()], ["miso_trader_daily", "miso_rtm_hub_prices", "miso_dam_hub_prices"],
               note=f"hour starting {sp.idxmax()}; MISO operating days in EST"))
    nda = e.csv("nyiso_dam_zone_prices")
    nd = e.local_day(nda[nda["node"] == "N.Y.C."], "America/New_York", "2026-09-18")
    assert len(nd) == 24
    fuel = e.csv("eia_fuel_spot_prices")
    hh = fuel[(fuel["entity"] == "eia:henry_hub") & (fuel["ts_utc"].dt.strftime("%Y-%m-%d") == "2026-09-18")]
    assert len(hh) == 1
    Q.append(q("s20q12", "power", "derived",
               "What was the implied heat rate (day-ahead average price over Henry Hub spot) at NYISO zone N.Y.C. on the operating day "
               "2026-09-18, in MMBtu/MWh?",
               [nd["value"].mean() / hh["value"].iloc[0]], ["nyiso_trader_daily"],
               note=f"DA mean {nd['value'].mean():.4f} / Henry Hub {hh['value'].iloc[0]}"))

    # ---- deals and datacenters ---------------------------------------------------------------
    ed = e.csv("energy_deals")
    Q.append(q("s20q13", "deals", "events",
               "How many deals in the ERW's deal table are mergers and acquisitions (deal type m_and_a)?",
               [int((ed["deal_type"] == "m_and_a").sum())], ["energy_deals"], tol=0.5))
    pf = ed[(ed["deal_type"] == "project_finance") & (ed["dollars"] != "")]
    Q.append(q("s20q14", "deals", "events",
               "What is the total stated value in US dollars of the project finance deals (deal type project_finance) in the deal table?",
               [pf["dollars"].astype(float).sum()], ["energy_deals"], tol=1,
               note=f"{len(pf)} project finance deals state dollars"))
    dc = e.csv("datacenter_projects")
    Q.append(q("s20q15", "datacenters", "entities", "How many datacenter facilities in the ERW's datacenter table are in Virginia?",
               [int((dc["state"] == "VA").sum())], ["datacenter_projects"], tol=0.5))
    return Q


def main():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "q30.yaml")
        e.main(["--out", path])
        base = yaml.safe_load(open(path, encoding="utf-8"))
    Q = base["questions"] + new_questions()
    assert len(Q) == 45
    with open(OUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Energy Research Warehouse (ERW): evaluation set for warehouse/chat/ask.py (session 20: 45 questions).\n"
                "# Generated by warehouse/chat/eval/expected_s20.py (the 30 of expected.py, recomputed, and 15 new) from the\n"
                f"# CSVs in warehouse/output with pandas, independently of warehouse/chat/tools.py. Fixed date: today = {e.TODAY}.\n"
                "# Do not edit by hand.\n")
        yaml.safe_dump({"today": e.TODAY, "questions": Q}, f, sort_keys=False, allow_unicode=True, width=120)
    for x in Q[30:]:
        print(x["id"], x["expected"], x["text"], x["note"])


if __name__ == "__main__":
    main()
