#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "prices", third part: the fuels and carbon (session 3003).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Eight candidates on public
tables: the World Bank's Pink Sheet (wb_commodity_prices_monthly, CC BY 4.0: US gas against Europe's gas and Japan's
LNG, from 2000), EIA's gas prices by state (eia_gas_prices_state_monthly, from 2001: what homes and power plants pay
against the citygate price), California's allowance auctions and LCFS credits (carb_auction_allowance_prices,
carb_lcfs_credit_prices), and EIA's daily spot closes (eia_fuel_spot_prices: Brent against WTI, Henry Hub's winter).
The claim about another country's price is always a comparison with a US price; no claim is about another country.

    python warehouse/analysis/findings/deep/fuels_carbon.py --dry-run
    python warehouse/analysis/findings/deep/fuels_carbon.py --load
"""

import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "prices"
STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "the District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}
FROM_YEAR = 2000                   # the Pink Sheet comparisons start here: the claim is about this century's years


def _pink_gap(in_dir, other, region, words):
    d = hm.series("wb_commodity_prices_monthly", in_dir, variables=["price"], entities=[f"wb_pink:{other}", "wb_pink:natural_gas_us"])
    w = d.pivot_table(index="ts", columns="entity", values="value").dropna()
    w = w[w.index.year >= FROM_YEAR]
    gap = w[f"wb_pink:{other}"] - w["wb_pink:natural_gas_us"]
    rows = [hm._row(region, words, y, float(s.mean()), len(s)) for y, s in gap.groupby(gap.index.year)]
    return {"rows": rows, "tables": {region: ["wb_commodity_prices_monthly"]}}


def europe_gas_premium(in_dir=None):
    """The year's mean of the World Bank's Europe gas price less its US gas price (USD per MMBtu), from 2000."""
    return _pink_gap(in_dir, "natural_gas_europe", "us_europe_gas", "European gas against US gas (World Bank Pink Sheet)")


def japan_lng_premium(in_dir=None):
    """The year's mean of the World Bank's Japan LNG price less its US gas price (USD per MMBtu), from 2000."""
    return _pink_gap(in_dir, "liquefied_natural_gas_japan", "us_japan_lng", "Japan's LNG against US gas (World Bank Pink Sheet)")


def _state_gap(in_dir, var, region_prefix):
    d = hm.series("eia_gas_prices_state_monthly", in_dir, variables=[var, "price_citygate"], extra=("geo", "market", "node"))
    d = d[d["geo"].astype(str).str.match(r"^US-[A-Z]{2}$")]
    w = d.pivot_table(index=["geo", "ts"], columns="variable", values="value").dropna().reset_index()
    rows, tables = [], {}
    for geo, g in w.groupby("geo"):
        region, words = f"{region_prefix}_{geo[3:]}", STATES.get(geo[3:], geo)
        gap = g[var] - g["price_citygate"]
        for y, s in gap.groupby(g["ts"].dt.year):
            rows.append(hm._row(region, words, y, float(s.mean()), len(s)))
        tables[region] = ["eia_gas_prices_state_monthly"]
    return {"rows": rows, "tables": tables}


def residential_markup(in_dir=None):
    """By state: the year's mean of the residential gas price less the citygate price (USD per Mcf), months with both."""
    return _state_gap(in_dir, "price_residential", "state_res")


def power_vs_citygate(in_dir=None):
    """By state: the year's mean of the price power plants paid for gas less the citygate price (USD per Mcf)."""
    return _state_gap(in_dir, "price_electric_power", "state_pow")


def industrial_vs_citygate(in_dir=None):
    """By state: the year's mean of the industrial gas price less the citygate price (USD per Mcf), months with both."""
    return _state_gap(in_dir, "price_industrial", "state_ind")


def carb_allowance_price(in_dir=None):
    """The year's mean settlement price of California's quarterly current-vintage allowance auctions (USD per tCO2)."""
    d = hm.series("carb_auction_allowance_prices", in_dir, variables=["settlement_price"], entities=["carb:current_auction"])
    rows = [hm._row("us_ca_allowance", "California's cap-and-trade allowance auctions", y, float(s["value"].mean()), len(s))
            for y, s in d.groupby(d["ts"].dt.year)]
    return {"rows": rows, "tables": {"us_ca_allowance": ["carb_auction_allowance_prices"]}}


def lcfs_credit_price(in_dir=None):
    """The year's mean of the weekly average LCFS credit price (USD per tCO2)."""
    d = hm.series("carb_lcfs_credit_prices", in_dir, variables=["credit_price_weekly_avg"], entities=["carb:lcfs_credit"])
    rows = [hm._row("us_ca_lcfs", "California's Low Carbon Fuel Standard credits", y, float(s["value"].mean()), len(s))
            for y, s in d.groupby(d["ts"].dt.year)]
    return {"rows": rows, "tables": {"us_ca_lcfs": ["carb_lcfs_credit_prices"]}}


def brent_wti_spread(in_dir=None):
    """The year's mean of the daily Brent spot close less the WTI Cushing close (USD per barrel), days with both."""
    d = hm.series("eia_fuel_spot_prices", in_dir, variables=["spot_price"], entities=["eia:brent", "eia:wti_cushing"])
    w = d.pivot_table(index="ts", columns="entity", values="value").dropna()
    gap = w["eia:brent"] - w["eia:wti_cushing"]
    rows = [hm._row("us_brent_wti", "Brent against WTI at Cushing", y, float(s.mean()), len(s)) for y, s in gap.groupby(gap.index.year)]
    return {"rows": rows, "tables": {"us_brent_wti": ["eia_fuel_spot_prices"]}}


def henry_hub_winter(in_dir=None):
    """The mean Henry Hub close of the year's January, February and December as a percent of the year's mean close."""
    d = hm.series("eia_fuel_spot_prices", in_dir, variables=["spot_price"], entities=["eia:henry_hub"])
    d = d[d["value"] > 0]
    rows = []
    for y, s in d.groupby(d["ts"].dt.year):
        w = s.loc[s["ts"].dt.month.isin([1, 2, 12]), "value"].mean()
        rows.append(hm._row("us_henry_hub_winter", "Henry Hub, Louisiana", y, float(100 * w / s["value"].mean()), len(s)))
    return {"rows": rows, "tables": {"us_henry_hub_winter": ["eia_fuel_spot_prices"]}}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_READ = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <{table}.csv>

{words}
"""
import sys

import pandas as pd

with open(sys.argv[1], encoding="utf-8") as f:
    skip = 0
    for line in f:
        if not line.startswith("#"):
            break
        skip += 1
d = pd.read_csv(sys.argv[1], skiprows=skip, dtype=str)
d["value"] = pd.to_numeric(d["value"], errors="coerce")
d = d.dropna(subset=["value"])
d["ts"] = pd.to_datetime(d["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
'''

PY_BODY = {
    "pink": ("w = d[d['variable'] == 'price'].pivot_table(index='ts', columns='entity', values='value').dropna(subset=[{a!r}, 'wb_pink:natural_gas_us'])\n"
             "w = w[w.index.year >= 2000]\ngap = w[{a!r}] - w['wb_pink:natural_gas_us']\n"
             "for y, s in gap.groupby(gap.index.year):\n    print(y, round(float(s.mean()), 6), len(s))\n"),
    "state": ("d = d[(d['geo'] == {geo!r}) & d['variable'].isin([{var!r}, 'price_citygate'])]\n"
              "w = d.pivot_table(index='ts', columns='variable', values='value').dropna()\ngap = w[{var!r}] - w['price_citygate']\n"
              "for y, s in gap.groupby(gap.index.year):\n    print(y, round(float(s.mean()), 6), len(s))\n"),
    "series": ("d = d[(d['entity'] == {entity!r}) & (d['variable'] == {var!r})]\n"
               "for y, s in d.groupby(d['ts'].dt.year):\n    print(y, round(float(s['value'].mean()), 6), len(s))\n"),
    "brent": ("d = d[d['variable'] == 'spot_price']\nw = d.pivot_table(index='ts', columns='entity', values='value').dropna(subset=['eia:brent', 'eia:wti_cushing'])\n"
              "gap = w['eia:brent'] - w['eia:wti_cushing']\nfor y, s in gap.groupby(gap.index.year):\n    print(y, round(float(s.mean()), 6), len(s))\n"),
    "winter": ("d = d[(d['entity'] == 'eia:henry_hub') & (d['variable'] == 'spot_price') & (d['value'] > 0)]\n"
               "for y, s in d.groupby(d['ts'].dt.year):\n    w = s.loc[s['ts'].dt.month.isin([1, 2, 12]), 'value'].mean()\n"
               "    print(y, round(float(100 * w / s['value'].mean()), 6), len(s))\n"),
}

SPEC = {
    "europe_gas_premium": ("pink", "wb_commodity_prices_monthly", {"a": "wb_pink:natural_gas_europe"}),
    "japan_lng_premium": ("pink", "wb_commodity_prices_monthly", {"a": "wb_pink:liquefied_natural_gas_japan"}),
    "residential_markup": ("state", "eia_gas_prices_state_monthly", {"var": "price_residential"}),
    "power_vs_citygate": ("state", "eia_gas_prices_state_monthly", {"var": "price_electric_power"}),
    "industrial_vs_citygate": ("state", "eia_gas_prices_state_monthly", {"var": "price_industrial"}),
    "carb_allowance_price": ("series", "carb_auction_allowance_prices", {"entity": "carb:current_auction", "var": "settlement_price"}),
    "lcfs_credit_price": ("series", "carb_lcfs_credit_prices", {"entity": "carb:lcfs_credit", "var": "credit_price_weekly_avg"}),
    "brent_wti_spread": ("brent", "eia_fuel_spot_prices", {}),
    "henry_hub_winter": ("winter", "eia_fuel_spot_prices", {}),
}


def reproduce_py(name, region):
    kind, table, args = SPEC[name]
    if kind == "state":
        args = dict(args, geo="US-" + region.rsplit("_", 1)[1])
    P = next(p for p in CANDIDATES if p["name"] == name)
    return PY_READ.format(name=name, region=region, table=table, words=P["label"][0].upper() + P["label"][1:] + ", by calendar year.") + PY_BODY[kind].format(**args)


def reproduce_do(name, region):
    import findings_common as common
    kind, table, args = SPEC[name]
    lines = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
             "clear all", f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear', "destring value, replace force", "drop if missing(value)",
             "generate int year = real(substr(ts_utc, 1, 4))", "generate int month = real(substr(ts_utc, 6, 2))"]
    if kind == "pink":
        lines += [f'keep if variable == "price" & (entity == "{args["a"]}" | entity == "wb_pink:natural_gas_us")', "keep if year >= 2000",
                  'generate str5 side = cond(entity == "wb_pink:natural_gas_us", "us", "other")', "keep ts_utc year side value",
                  "reshape wide value, i(ts_utc) j(side) string", "drop if missing(valueus) | missing(valueother)", "generate double gap = valueother - valueus",
                  "collapse (mean) measure = gap (count) n = gap, by(year)"]
    elif kind == "state":
        geo = "US-" + region.rsplit("_", 1)[1]
        lines += [f'keep if geo == "{geo}" & (variable == "{args["var"]}" | variable == "price_citygate")',
                  'generate str4 side = cond(variable == "price_citygate", "city", "use")', "keep ts_utc year side value",
                  "reshape wide value, i(ts_utc) j(side) string", "drop if missing(valuecity) | missing(valueuse)", "generate double gap = valueuse - valuecity",
                  "collapse (mean) measure = gap (count) n = gap, by(year)"]
    elif kind == "series":
        lines += [f'keep if entity == "{args["entity"]}" & variable == "{args["var"]}"', "collapse (mean) measure = value (count) n = value, by(year)"]
    elif kind == "brent":
        lines += ['keep if variable == "spot_price" & (entity == "eia:brent" | entity == "eia:wti_cushing")',
                  'generate str5 side = cond(entity == "eia:brent", "brent", "wti")', "keep ts_utc year side value",
                  "reshape wide value, i(ts_utc) j(side) string", "drop if missing(valuebrent) | missing(valuewti)", "generate double gap = valuebrent - valuewti",
                  "collapse (mean) measure = gap (count) n = gap, by(year)"]
    elif kind == "winter":
        lines += ['keep if entity == "eia:henry_hub" & variable == "spot_price" & value > 0', "generate double winter = value if inlist(month, 1, 2, 12)",
                  "collapse (mean) all_mean = value (mean) win_mean = winter (count) n = value, by(year)", "generate double measure = 100 * win_mean / all_mean"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
CANDIDATES = [
    C("europe_gas_premium", FAMILY, europe_gas_premium, "USD per MMBtu", 2, 12, 1.0, "EUROPE'S GAS AGAINST US GAS",
      "the year's mean of the World Bank's Europe gas price less its US gas price, from 2000",
      lambda w: "the mean premium of the World Bank's European gas price over its US gas price",
      "Monthly index prices in nominal dollars; the Europe index is the World Bank's, not a price any US exporter received.",
      reproduce("europe_gas_premium"), first_words="the first year this comparison counts", consequence=3),
    C("japan_lng_premium", FAMILY, japan_lng_premium, "USD per MMBtu", 2, 12, 1.0, "JAPAN'S LNG AGAINST US GAS",
      "the year's mean of the World Bank's Japan LNG import price less its US gas price, from 2000",
      lambda w: "the mean premium of the World Bank's Japan LNG import price over its US gas price",
      "Monthly prices in nominal dollars; Japan's is a delivered import price, the US one a hub price, so the gap includes shipping and liquefaction.",
      reproduce("japan_lng_premium"), first_words="the first year this comparison counts", consequence=2),
    C("residential_markup", FAMILY, residential_markup, "USD per Mcf", 2, 10, 1.0, "WHAT HOMES PAY ABOVE CITYGATE",
      "the year's mean of the residential gas price less the citygate price, months with both",
      lambda w: f"the mean residential gas price in {w} above its citygate price",
      "Nominal dollars per thousand cubic feet; a mean of months, not weighted by the gas each month delivered, and EIA withholds some months for some states.",
      reproduce("residential_markup"), consequence=2),
    C("power_vs_citygate", FAMILY, power_vs_citygate, "USD per Mcf", 2, 10, 1.0, "WHAT POWER PLANTS PAY AGAINST CITYGATE",
      "the year's mean of the gas price power plants paid less the citygate price, months with both",
      lambda w: f"the mean gas price power plants in {w} paid against the state's citygate price",
      "Nominal dollars per thousand cubic feet; EIA withholds many states' power-plant months, so a state's mean rests on the months it shows.",
      reproduce("power_vs_citygate"), consequence=2),
    C("industrial_vs_citygate", FAMILY, industrial_vs_citygate, "USD per Mcf", 2, 10, 1.0, "WHAT INDUSTRY PAYS AGAINST CITYGATE",
      "the year's mean of the industrial gas price less the citygate price, months with both",
      lambda w: f"the mean industrial gas price in {w} against the state's citygate price",
      "Nominal dollars per thousand cubic feet; many large industrial buyers buy gas directly and EIA's industrial price covers only the gas sold to them by utilities.",
      reproduce("industrial_vs_citygate"), consequence=2),
    C("carb_allowance_price", FAMILY, carb_allowance_price, "USD per tCO2", 2, 4, 2.0, "CALIFORNIA'S CARBON PRICE",
      "the year's mean settlement price of California's quarterly current-vintage allowance auctions",
      lambda w: "the mean settlement price of California's quarterly cap-and-trade allowance auctions",
      "Four auctions a year in nominal dollars; the auction floor price rises each year by rule, and the measure does not separate the floor from the market.",
      reproduce("carb_allowance_price"), consequence=2),
    C("lcfs_credit_price", FAMILY, lcfs_credit_price, "USD per tCO2", 2, 40, 10.0, "CALIFORNIA'S LCFS CREDIT",
      "the year's mean of the weekly average Low Carbon Fuel Standard credit price",
      lambda w: "the mean weekly price of California's Low Carbon Fuel Standard credits",
      "Weekly averages of reported credit transfers in nominal dollars; a mean of weeks, not weighted by the credits each week moved.",
      reproduce("lcfs_credit_price"), consequence=2),
    C("brent_wti_spread", FAMILY, brent_wti_spread, "USD per barrel", 2, 200, 1.0, "BRENT AGAINST WTI",
      "the year's mean of the daily Brent spot close less the WTI Cushing close, days with both",
      lambda w: "the mean daily premium of Brent crude over WTI at Cushing",
      "Nominal dollars; the two are spot closes at different places and qualities, and the spread includes the cost of moving crude between them.",
      reproduce("brent_wti_spread"), consequence=2),
    C("henry_hub_winter", FAMILY, henry_hub_winter, "percent of the year's mean", 1, 200, 5.0, "HENRY HUB'S WINTER",
      "the mean Henry Hub close of the year's January, February and December as a percent of the year's mean close",
      lambda w: "the mean Henry Hub spot close in January, February and December",
      "Calendar months of one year: the December belongs to the next winter, and one cold spell can carry a year.",
      reproduce("henry_hub_winter"), consequence=2),
]


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family prices, fuels and carbon (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_fuels", cands, a.in_dir, dry_run=not a.load)
    return 0


if __name__ == "__main__":
    sys.exit(main())
