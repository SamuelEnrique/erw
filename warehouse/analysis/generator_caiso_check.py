#!/usr/bin/env python3
"""The CAISO generator beside published figures (session 253). Changes no table and no page file.

Energy Research Warehouse (ERW). docs/methods/generator_earns_algorithm.md, "CAISO beside published figures (session 253)".

    python warehouse/analysis/generator_caiso_check.py [--cache-dir DIR]

Runs the generator page's own model (merchant_revenue.build_iso, as merchant_hubs.py runs it) for CAISO at each of the
three hubs and zones held (SP15, NP15, ZP26), at real-time and at day-ahead prices, from the tables on this machine,
and adds the months up three ways: the calendar year 2025 (the one whole year held), the last twelve whole months,
and, for the page's own check, the months as the page's files hold them. For solar, wind and a gas peaker it gives
revenue per kW, energy per MW, the capture price, the flat price and the capture rate; then the inputs of the
breakeven PPA price (energy per kW a year and the page's default costs) and the price itself, by the Python mirror
of site/lib/seller/finance.ts that tests/test_session235.py holds to the library.

Beside them, typed below from the documents, each with its table or sheet:

  CAISO's Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance (June 2026), section
  1.3.2, Tables 1.5 and 1.6: a hypothetical new combustion turbine at NP15 and at SP15 prices in 2025.
  Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Update: 2026 Edition (August 2026), the
  public data file: the market value of wind in CAISO in 2025, and LevelTen's PPA index.
  Lawrence Berkeley National Laboratory, U.S. Utility-Scale Solar, 2025 Data Update (October 2025), the public data
  file: the market value of solar in CAISO in 2024 (its newest year), and PPA prices.

The peaker is run twice: as the page runs it (Henry Hub, heat rate 10.725, variable O&M 4.25, no carbon cost), and
"as_dmm" with the three choices of the market monitor's table this model can take (heat rate 9.3, variable O&M 4.80,
and the greenhouse gas allowance on the fuel: 0.053165 tonnes per MMBtu at the report's 2025 average price). What it
cannot take stays in the gap: California's delivered gas price (only Henry Hub is held), start costs, the minimum
load and run time, and the bids the market monitor dispatches against.

Writes warehouse/output/analysis_internal/generator_caiso_check.csv and .json (not in git; internal), and prints the
tables. No request: the published figures are typed below.
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import capture_price as cq  # noqa: E402
import iso_prices as ip  # noqa: E402
import merchant_hubs as mh  # noqa: E402
import merchant_revenue as mr  # noqa: E402
import price_compare as pc  # noqa: E402

OUT_DIR = os.path.join(ROOT, "warehouse", "output", "analysis_internal")
ISO = "caiso"
YEAR = "2025"
NEAR = mr.NEAR
HUB_WORDS = {"TH_SP15_GEN-APND": "SP15", "TH_NP15_GEN-APND": "NP15", "TH_ZP26_GEN-APND": "ZP26"}
SIDES = (("rt", "rtm"), ("da", "dam"))

# ---------------------------------------------------------------------------------------------------------------------
# the published figures, typed from the documents
# ---------------------------------------------------------------------------------------------------------------------
DMM = "CAISO Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance, June 2026"
DMM_URL = "https://www.caiso.com/documents/2025-annual-report-on-market-issues-and-performance.pdf"
# Table 1.6, "Financial analysis of new combustion turbine (2025)", the report's page 116, first scenario ("15-minute
# prices and default energy bids"): capacity factor (percent), real-time energy revenues, operating costs, net revenue,
# USD per kW-year
DMM_CT = {"NP15": {"capacity_factor": 3.43, "revenue": 23.25, "costs": 19.73, "net": 3.52},
          "SP15": {"capacity_factor": 1.32, "revenue": 8.99, "costs": 8.21, "net": 0.78}}
# the same table, the other two scenarios' net revenue (without the 10 percent adder; with 5-minute dispatch)
DMM_CT_OTHER = {"NP15": (4.41, 3.65), "SP15": (1.17, 0.84)}
# Table 1.5, "Assumptions for typical new combustion turbine", the same page
DMM_HEAT_RATE, DMM_VOM, DMM_GHG_T_PER_MMBTU, DMM_CT_FIXED = 9.3, 4.80, 0.053165, 176.0
DMM_GHG_PRICE = 29.89      # USD per tonne: "the average cost of greenhouse gas allowances in bilateral markets", 2025, load-weighted (section 1.2.7, page 96)
DMM_GAS = {"PG&E Citygate": 3.40, "SoCal Citygate": 3.60}   # USD per MMBtu, 2025 averages: the table of average hub prices in section 1.2.6, page 94
DMM_HENRY_HUB_2025 = 3.54   # the same table, Henry Hub

WIND = "Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Update: 2026 Edition, August 2026, public data file"
WIND_URL = "https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx"
# sheet "Value Relative to Flat Profile", "Regional average market value of wind in 2025", the CAISO rows, 2025 USD per
# MWh: a flat profile at all power plants; the wind profile at all power plants; the wind profile at wind plants; the
# same adjusted for curtailment
LBNL_WIND_2025 = {"energy": (34.21, 32.97, 31.21, 30.82), "capacity": (25.70, 26.76, 26.76, 26.40), "total": (59.91, 59.73, 57.97, 57.22)}
LBNL_WIND_PPA_2025 = 78.2   # sheet "LevelTen & Trio 2025 PPA Index", CAISO, LevelTen, 2025 USD per MWh

SOLAR = "Lawrence Berkeley National Laboratory, U.S. Utility-Scale Solar, 2025 Data Update, October 2025, public data file"
SOLAR_URL = "https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx"
# sheet "Value Difference vs. Flat Block", "Regional average market value in 2024", the CAISO rows, 2024 USD per MWh:
# a flat block at all nodes; a flat block at solar nodes; the same with curtailment; the solar profile at solar nodes
LBNL_SOLAR_2024 = {"energy": (34.35, 29.67, 28.11, 8.616), "capacity": (26.60, 25.86, 25.86, 9.247), "total": (60.95, 55.53, 53.97, 17.86)}
LBNL_SOLAR_VALUE_FACTOR_2024 = 0.2931   # the same sheet, CAISO 2024: total value of solar over the flat block's
LBNL_SOLAR_PPA_2024 = {"LevelTen CAISO index": 47.06, "LBNL sample, West (CAISO and non-ISO)": 27.45}   # sheets "LevelTen & Trio 2024 PPA Index", "Annual Average PPA Price"; 2024 USD per MWh

# the page's default costs (site/lib/seller/finance.ts, SPECS and DEFAULTS; Lazard, June 2025, midpoints)
DEFAULTS = {"solar": dict(capex=1375, fom=12.5, life=35), "wind": dict(capex=2100, fom=32.25, life=30), "peaker": dict(capex=1300, fom=13.5, life=30)}
SHARE, RATE, HURDLE, TARGET = 60, 8, 12, 1.25


# ---------------------------------------------------------------------------------------------------------------------
# the finance, as tests/test_session235.py mirrors site/lib/seller/finance.ts
# ---------------------------------------------------------------------------------------------------------------------
def crf(rate, years):
    return 1 / years if rate == 0 else rate / (1 - (1 + rate) ** -years)


def flows(a, rev, unit):
    dy = min(a["term"], a["life"])
    ds = a["capex"] * a["share"] / 100 * crf(a["rate"] / 100, dy)
    contract = a["cshare"] / 100 * a["cprice"] * unit
    out = [-a["capex"] * (1 - a["share"] / 100)]
    for t in range(1, a["life"] + 1):
        market = rev * (1 - a["deg"] / 100) ** (t - 1)
        income = contract + (1 - a["cshare"] / 100) * market if t <= dy else market
        out.append(income - a["fom"] - (ds if t <= dy else 0))
    return out


def npv(rate_pct, fl):
    return sum(v / (1 + rate_pct / 100) ** t for t, v in enumerate(fl))


def breakeven_ppa(a, rev, unit):
    share = a["cshare"] if a["cshare"] > 0 else 100
    at0 = npv(a["hurdle"], flows({**a, "cshare": share, "cprice": 0}, rev, unit))
    dy = min(a["term"], a["life"])
    per = sum(share / 100 * unit / (1 + a["hurdle"] / 100) ** t for t in range(1, dy + 1))
    return -at0 / per if per > 0 else None


def finance(asset, rev_kw, energy_kw):
    """Per kW, the page's defaults: the debt payment, coverage, the contract price (or toll) for coverage of 1.25, NPV
    at the hurdle rate, and the breakeven PPA price (USD per MWh) or toll (USD per kW-month)."""
    d = DEFAULTS[asset]
    a = dict(capex=d["capex"], share=SHARE, rate=RATE, term=d["life"], fom=d["fom"], deg=0, life=d["life"], hurdle=HURDLE, cshare=0, cprice=0)
    ds = a["capex"] * SHARE / 100 * crf(RATE / 100, d["life"])
    unit = 12 if asset == "peaker" else energy_kw
    return {"debt_payment_per_kw": ds, "coverage": (rev_kw - a["fom"]) / ds, "price_for_coverage_1_25": (TARGET * ds + a["fom"]) / unit,
            "npv_per_kw": npv(HURDLE, flows(a, rev_kw, unit)), "breakeven_ppa": breakeven_ppa(a, rev_kw, unit), "unit": "USD/kW-month" if asset == "peaker" else "USD/MWh"}


# ---------------------------------------------------------------------------------------------------------------------
# the model's months, added up over a span
# ---------------------------------------------------------------------------------------------------------------------
def counted(monthly, months, asset):
    """The months of a span the page counts for an asset: held at 90 percent of the month's hours."""
    out = []
    for m in months:
        o = monthly.get(m)
        if o and asset in o and o[asset]["hours"] >= NEAR * o["hours_in_month"]:
            out.append((m, o[asset]))
    return out


def span_sum(monthly, months, asset):
    rows = counted(monthly, months, asset)
    if len(rows) != len(months):
        return {"months_counted": len(rows), "months": len(months)}
    rev = sum(r["revenue_per_mw"] for _, r in rows)
    sales = sum(r["sales_per_mw"] for _, r in rows)
    e = sum(r["energy_per_mw"] for _, r in rows)
    hours = sum(r["hours"] for _, r in rows)
    flat = sum(r["flat_price"] * r["hours"] for _, r in rows) / hours
    cap = sales / e if e else None
    return {"months_counted": len(rows), "months": len(months), "revenue_per_kw": rev / 1000, "energy_mwh_per_mw": e, "capture_price": cap, "flat_price": flat,
            "capture_rate_pct": cap / flat * 100 if cap is not None and flat else None, "hours": hours}


def last_twelve(monthly, asset):
    """The newest counted month and the eleven before it (the page's rule: all twelve counted)."""
    ms = sorted(monthly)
    for i in range(len(ms) - 1, 10, -1):
        span = ms[i - 11:i + 1]
        if len(counted(monthly, span, asset)) == 12:
            return span
    return None


def peaker_as(h, months, heat_rate, vom, adder):
    """The peaker's rule on the model's own hours with another heat rate, variable O&M and an adder on the fuel price
    (USD per MMBtu): margin per kW, hours run, hours held."""
    x = h[h["month"].isin(months)].dropna(subset=["hh"])
    cost = (x["hh"] + adder) * heat_rate + vom
    run = x["p"] > cost
    return {"margin_per_kw": float((x.loc[run, "p"] - cost[run]).sum()) / 1000, "revenue_per_kw": float(x.loc[run, "p"].sum()) / 1000, "costs_per_kw": float(cost[run].sum()) / 1000,
            "hours_run": int(run.sum()), "hours": int(len(x)), "capacity_factor_pct": float(run.mean() * 100), "henry_hub_mean": float(x["hh"].mean())}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the CAISO generator beside published figures (session 253)")
    ap.add_argument("--cache-dir", help="keep the fleet's hours read from EIA's workbook under this folder")
    a = ap.parse_args(argv)
    log = print
    in_dir = ip.OUT_DIR
    cq.SINCE = mh.SINCE
    lic, _ = pc.licenses()
    tables = cq.readable(in_dir, lic, log)
    parts = []
    for i, t in enumerate(tables):
        x = cq.read_one(in_dir, t, log)
        if x is None:
            continue
        x = x[x["entity"].astype(str).str.startswith(ISO + ":")].copy()
        x["rank"] = np.int8(i)
        parts.append(x)
    x = pd.concat(parts, ignore_index=True)
    x["entity"] = x["entity"].astype(str)
    gens, vint = mr.read_gens()
    hh, hhrows = mr.henry_hub()
    fuel, wb = mh.fleet_hours(ISO, a.cache_dir, log)
    with open(mh.CAPTURE, encoding="utf-8") as f:
        capture = json.load(f)["grids"][ISO]
    months_2025 = [f"{YEAR}-{m:02d}" for m in range(1, 13)]
    ghg = DMM_GHG_T_PER_MMBTU * DMM_GHG_PRICE
    rows, detail = [], {"built": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "eia860m": vint, "workbook": os.path.basename(wb), "tables": tables,
                        "henry_hub": f"{hhrows['ts'].min():%Y-%m-%d} to {hhrows['ts'].max():%Y-%m-%d}", "ghg_adder_usd_per_mmbtu": ghg, "hubs": {}}
    rebuilt = {}
    for hub in capture["hubs"]:
        node, entity = hub["id"], hub["entity"]
        e = x[x["entity"] == entity]
        for mk, side in SIDES:
            price, basis, tabs = cq.hourly_side(e, side)
            if price is None or price.empty:
                log(f"  {node} {mk}: no price read")
                continue
            h, monthly, _, _, _, _, over, neg = mr.build_iso(ISO, gens, hh, lambda *_: None, [], price=price.sort_index(), table=", ".join(tabs), fuel=fuel)
            rec = {"market": mk, "basis": basis, "tables": tabs, "first": str(h.index.min()), "last": str(h.index.max()), "assets": {}}
            for asset in ("solar", "wind", "peaker"):
                l12 = last_twelve(monthly, asset)
                spans = {"2025": span_sum(monthly, months_2025, asset), "last12": dict(span_sum(monthly, l12, asset), first=l12[0], last=l12[-1]) if l12 else {"months_counted": 0}}
                for name, s in spans.items():
                    if "revenue_per_kw" in s:
                        s["finance"] = finance(asset, s["revenue_per_kw"], s["energy_mwh_per_mw"] / 1000)
                        rows.append({"hub": HUB_WORDS[node], "market": mk, "asset": asset, "span": name, **{k: v for k, v in s.items() if k != "finance"},
                                     **{k: v for k, v in s["finance"].items()}})
                rec["assets"][asset] = spans
            rec["peaker_as_dmm_2025"] = peaker_as(h, months_2025, DMM_HEAT_RATE, DMM_VOM, ghg)
            rec["peaker_page_rule_2025"] = peaker_as(h, months_2025, mr.HEAT_RATE, mr.VOM, 0.0)
            rec["peaker_page_rule_with_ghg_2025"] = peaker_as(h, months_2025, mr.HEAT_RATE, mr.VOM, ghg)
            rec["over_nameplate"], rec["negative"] = over, neg
            rebuilt[(node, mk)] = monthly
            if node == capture["main"] and mk == "rt":
                rec["_months"] = {m: {a_: {k: o[a_][k] for k in ("energy_per_mw", "revenue_per_mw", "hours")} for a_ in ("solar", "wind", "peaker") if a_ in o} for m, o in sorted(monthly.items())}
            detail["hubs"].setdefault(HUB_WORDS[node], {})[mk] = rec
            log(f"  {HUB_WORDS[node]} {mk}: {len(h):,} hours, {len(monthly)} months ({basis}; {', '.join(tabs)})")
    # the capture file's own figures (the page's table of the price received: the fleet's generation as weights, a
    # month counted at 95 percent of its hours), by its own arithmetic (capture_price.figure, last_twelve, years)
    cap_rows = []
    for hub in capture["hubs"]:
        for mk, _ in SIDES:
            for fuel_name in ("solar", "wind"):
                months = (hub.get(mk) or {}).get(fuel_name) or {}
                l12 = cq.last_twelve(months)
                spans = {"last12": (l12, cq.figure([months[m] for m in l12]) if l12 else None)}
                y = cq.years(months).get(YEAR)
                spans["2025"] = (months_2025, y[2] if y and y[1] else None)
                for name, (ms, fig) in spans.items():
                    if fig:
                        cap_rows.append({"hub": HUB_WORDS[hub["id"]], "market": mk, "fuel": fuel_name, "span": name, "first": ms[0], "last": ms[-1], "capture_price": fig["price"],
                                         "flat_price": fig["flat"], "capture_rate_pct": fig["price"] / fig["flat"] * 100 if fig["flat"] else None, "hours": fig["hours"], "fleet_mwh": fig["mwh"]})
    detail["capture_file"] = cap_rows
    # the denominator of the shape: installed nameplate in CAISO's balancing authority by month, and the wind added in 2026
    ba = gens[gens["balancing_authority"] == mr.BA[ISO]]
    detail["installed_mw"] = {m: {"solar": mr.capacity(gens, mr.BA[ISO], "SUN", m), "wind": mr.capacity(gens, mr.BA[ISO], "WND", m)}
                              for m in [f"2025-{k:02d}" for k in range(1, 13)] + [f"2026-{k:02d}" for k in range(1, 10)]}
    new = ba[(ba["energy_source"] == "WND") & (ba["start"] >= pd.Timestamp("2026-01-01"))]
    detail["wind_added_2026"] = [{"name": n, "state": str(g["state"].iloc[0]), "nameplate_mw": float(g["nameplate_mw"].sum()), "first_month": f"{g['start'].min():%Y-%m}"}
                                 for n, g in new.groupby("name")]
    sp = detail["hubs"]["SP15"]["rt"]
    detail["sp15_rt_months"] = sp.pop("_months")
    # the page's own files against this run: the snapshot at the main hub, the hub files at the other two. A month of
    # the page's file is compared when this run holds it too; revenue per MW, to the cent
    with open(mr.SNAPSHOT, encoding="utf-8") as f:
        snap = json.load(f)
    with open(os.path.join(mh.SITE_DIR, "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    held = {capture["main"]: ("rt", snap["isos"][ISO]["months"], f"merchant_snapshot.json, built {snap['built']}")}
    for node, meta in index["grids"][ISO]["hubs"].items():
        with open(os.path.join(mh.SITE_DIR, *meta["file"].split("/")), encoding="utf-8") as f:
            held[node] = (meta["market"], json.load(f)["months"], f"hubs/{meta['file']}, built {index['built']}")
    agree = []
    for node, (mk, months, words) in held.items():
        mine = rebuilt.get((node, mk))
        for asset in ("solar", "wind", "peaker"):
            both = [m for m in sorted(months) if asset in months[m] and mine and m in mine and asset in mine[m]]
            diffs = [(m, mine[m][asset]["revenue_per_mw"] - months[m][asset]["revenue_per_mw"]) for m in both]
            off = [(m, d) for m, d in diffs if abs(d) > 0.01]
            worst = max(diffs, key=lambda t: abs(t[1])) if diffs else (None, 0.0)
            agree.append({"hub": HUB_WORDS[node], "market": mk, "asset": asset, "file": words, "months_compared": len(both), "months_differ": len(off),
                          "largest_usd_per_mw": worst[1], "largest_at": worst[0], "months_that_differ": [m for m, _ in off]})
    detail["page_files"] = agree
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.DataFrame(rows)
    path = os.path.join(OUT_DIR, "generator_caiso_check.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(f"# Energy Research Warehouse (ERW): the CAISO generator at each hub, by the generator page's model (session 253)\n")
        f.write(f"# Computed {detail['built']} by warehouse/analysis/generator_caiso_check.py from {', '.join(tables)}, EIA-930 ({detail['workbook']}), EIA-860M ({vint}) and eia_fuel_spot_prices\n")
        f.write("# Rows: one per hub, market (rt, da), asset and span (2025; last12, the last twelve counted months). Internal: not a warehouse table\n")
        df.to_csv(f, index=False)
    with open(os.path.join(OUT_DIR, "generator_caiso_check.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(detail, f, indent=1, default=str)
        f.write("\n")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 30)
    show = ["hub", "market", "asset", "span", "revenue_per_kw", "energy_mwh_per_mw", "capture_price", "flat_price", "capture_rate_pct", "coverage", "price_for_coverage_1_25", "breakeven_ppa", "npv_per_kw"]
    print(df[show].round(2).to_string(index=False))
    print("\nthe capture file's own figures (the page's table of the price received)")
    print(pd.DataFrame(cap_rows).round(2).to_string(index=False))
    print("\nthe page's files against this run (revenue per MW by month)")
    print(pd.DataFrame(agree).drop(columns="file").round(2).to_string(index=False))
    print("\nwind added to CAISO's balancing authority in EIA-860M in 2026:", detail["wind_added_2026"])
    print("installed MW:", {m: {k: round(v) for k, v in d.items()} for m, d in detail["installed_mw"].items() if m in ("2025-01", "2025-12", "2026-03", "2026-04", "2026-05", "2026-06", "2026-09")})
    print("SP15 rt, wind MWh per MW by month:", {m: round(o["wind"]["energy_per_mw"], 1) for m, o in detail["sp15_rt_months"].items() if "wind" in o})
    print(f"\nthe gas peaker in {YEAR}, USD per kW, beside {DMM}, Table 1.6 (first scenario)")
    for hubw in ("NP15", "SP15"):
        for mk in ("rt", "da"):
            r = detail["hubs"][hubw][mk]
            p, g, d = r["peaker_page_rule_2025"], r["peaker_page_rule_with_ghg_2025"], r["peaker_as_dmm_2025"]
            print(f"  {hubw} {mk}: the page's rule {p['margin_per_kw']:.2f} (ran {p['capacity_factor_pct']:.1f} percent of {p['hours']} hours; Henry Hub mean {p['henry_hub_mean']:.3f}); "
                  f"with the allowance on the fuel {g['margin_per_kw']:.2f} ({g['capacity_factor_pct']:.1f} percent); as_dmm (9.3, 4.80, allowance) {d['margin_per_kw']:.2f} "
                  f"({d['capacity_factor_pct']:.1f} percent; revenue {d['revenue_per_kw']:.2f}, costs {d['costs_per_kw']:.2f}); theirs net {DMM_CT[hubw]['net']} "
                  f"({DMM_CT[hubw]['capacity_factor']} percent; revenue {DMM_CT[hubw]['revenue']}, costs {DMM_CT[hubw]['costs']})")
    print(f"wrote {os.path.relpath(path, ROOT)} ({len(df)} rows) and generator_caiso_check.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
