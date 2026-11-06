#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "tariffs_policy": the retail side (session 3012).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. The large-load tariffs and
connection rules (utility_large_load_tariffs, large_load_connection_rules) and the policy actions (policy_actions) are
levels and recent months, not years, and are not drafted by year here. Public EIA tables with years:

    eia_retail_sales_monthly        retail sales by state and sector (MWh), 2001 on; US rows held
    eia_retail_electricity_prices   the average retail price by state and sector (USD per MWh), 2001 on
    eia861_utility_reliability      EIA-861's reliability by utility (IEEE SAIDI with major event days, minutes a
                                    customer, and the customers counted), 2015 on
    eia_meters_state_annual         meters by state and type (advanced metering infrastructure among them), 2013 on
    eia_net_metering_state_annual   net-metered capacity by state (MW), 2013 on

    python warehouse/analysis/findings/deep/retail.py --dry-run
    python warehouse/analysis/findings/deep/retail.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import generation  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "tariffs_policy"
STATES = generation.STATES
SALES, PRICES, REL, METERS, NEM = ("eia_retail_sales_monthly", "eia_retail_electricity_prices", "eia861_utility_reliability",
                                    "eia_meters_state_annual", "eia_net_metering_state_annual")


def _by_state(d, pos):
    return d.assign(st=d["entity"].str.split(":").str[pos], year=d["ts_utc"].str[:4].astype(int))


def _states(d, region_prefix, fn, n_of=len):
    rows, tables = [], {}
    for st, g in d.groupby("st"):
        if st not in STATES:
            continue
        region = f"{region_prefix}_{st}"
        for y, s in g.groupby("year"):
            v = fn(s)
            if v is not None:
                rows.append(hm._row(region, STATES[st], y, float(v), n_of(s)))
    return rows


def commercial_sales(in_dir=None):
    """The year's retail sales to the commercial sector (TWh), the US and each state."""
    d = _by_state(hm.series(SALES, in_dir, variables=["retail_sales"]), 2)
    d = d[d["entity"].str.endswith(":COM")]
    rows = _states(d, "com_sales", lambda s: s["value"].sum() / 1e6)
    return {"rows": rows, "tables": {r["region"]: [SALES] for r in rows}}


def res_price(in_dir=None):
    """The mean of the year's monthly average residential retail price (USD per MWh), the US and each state."""
    d = _by_state(hm.series(PRICES, in_dir, variables=["retail_price"]), 2)
    d = d[d["entity"].str.endswith(":RES")]
    rows = _states(d, "res_price", lambda s: s["value"].mean())
    return {"rows": rows, "tables": {r["region"]: [PRICES] for r in rows}}


def res_over_ind(in_dir=None):
    """The mean residential retail price less the mean industrial retail price over the year (USD per MWh)."""
    d = _by_state(hm.series(PRICES, in_dir, variables=["retail_price"]), 2)
    d = d.assign(sec=d["entity"].str.split(":").str[3])
    d = d[d["sec"].isin(["RES", "IND"])]
    w = d.pivot_table(index=["st", "year", "ts_utc"], columns="sec", values="value").dropna().reset_index()
    rows = _states(w, "res_ind_gap", lambda s: (s["RES"] - s["IND"]).mean())
    return {"rows": rows, "tables": {r["region"]: [PRICES] for r in rows}}


def saidi(in_dir=None):
    """The customer-weighted mean of the utilities' IEEE SAIDI with major event days (minutes a customer), the US and
    each state: the utilities that report both their SAIDI and their customers counted."""
    d = hm.series(REL, in_dir, variables=["ieee_saidi_with_med", "ieee_customers"], extra=("geo",))
    d = d.assign(st=d["geo"].astype(str).str[3:], year=d["ts_utc"].str[:4].astype(int))
    w = d.pivot_table(index=["entity", "st", "year"], columns="variable", values="value").dropna().reset_index()
    w = w[w["ieee_customers"] > 0]
    f = lambda s: (s["ieee_saidi_with_med"] * s["ieee_customers"]).sum() / s["ieee_customers"].sum()  # noqa: E731
    rows = [hm._row("saidi_US", "the United States", y, float(f(s)), 1) for y, s in w.groupby("year")]
    rows += _states(w, "saidi", f, n_of=lambda s: 1)
    return {"rows": rows, "tables": {r["region"]: [REL] for r in rows}}


def ami_share(in_dir=None):
    """Advanced metering infrastructure as a percent of all meters, the US and each state."""
    d = _by_state(hm.series(METERS, in_dir, variables=["meters"]), 1)
    d = d[d["entity"].str.endswith(":TOT")].assign(kind=lambda x: x["entity"].str.split(":").str[2])
    w = d.pivot_table(index=["st", "year"], columns="kind", values="value").dropna(subset=["advanced_meter_infrastructure", "all_meters"]).reset_index()
    w = w[w["all_meters"] > 0]
    rows = _states(w, "ami", lambda s: 100 * s["advanced_meter_infrastructure"].sum() / s["all_meters"].sum(), n_of=lambda s: 1)
    return {"rows": rows, "tables": {r["region"]: [METERS] for r in rows}}


def net_metered(in_dir=None):
    """Net-metered capacity, every technology and sector (MW), the US and each state."""
    d = _by_state(hm.series(NEM, in_dir, variables=["capacity"]), 1)
    d = d[d["entity"].str.endswith(":all_technologies:TOT")]
    rows = _states(d, "nem", lambda s: s["value"].sum(), n_of=lambda s: 1)
    return {"rows": rows, "tables": {r["region"]: [NEM] for r in rows}}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_HEAD = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.

    python {{this file}} <{table}.csv>

{label}.
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
d["year"] = d["ts_utc"].str[:4].astype(int)
'''


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    st = region.rsplit("_", 1)[1]
    table = {"commercial_sales": SALES, "res_price": PRICES, "res_over_ind": PRICES, "saidi": REL, "ami_share": METERS, "net_metered": NEM}[name]
    head = PY_HEAD.format(name=name, region=region, table=table, label=P["label"][0].upper() + P["label"][1:] + f", {STATES[st]}")
    if name == "commercial_sales":
        body = f"d = d[(d['entity'] == 'eia:retail_sales:{st}:COM') & (d['variable'] == 'retail_sales')]\nfor y, s in d.groupby('year'):\n    print(y, round(float(s['value'].sum() / 1e6), 6), len(s))\n"
    elif name == "res_price":
        body = f"d = d[(d['entity'] == 'eia:retail_price:{st}:RES') & (d['variable'] == 'retail_price')]\nfor y, s in d.groupby('year'):\n    print(y, round(float(s['value'].mean()), 6), len(s))\n"
    elif name == "res_over_ind":
        body = (f"d = d[d['entity'].isin(['eia:retail_price:{st}:RES', 'eia:retail_price:{st}:IND']) & (d['variable'] == 'retail_price')]\n"
                "d['sec'] = d['entity'].str.split(':').str[3]\nw = d.pivot_table(index=['year', 'ts_utc'], columns='sec', values='value').dropna().reset_index()\n"
                "for y, s in w.groupby('year'):\n    print(y, round(float((s['RES'] - s['IND']).mean()), 6), len(s))\n")
    elif name == "saidi":
        filt = "" if st == "US" else f"d = d[d['geo'] == 'US-{st}']\n"
        body = (filt + "d = d[d['variable'].isin(['ieee_saidi_with_med', 'ieee_customers'])]\n"
                "w = d.pivot_table(index=['entity', 'year'], columns='variable', values='value').dropna().reset_index()\nw = w[w['ieee_customers'] > 0]\n"
                "for y, s in w.groupby('year'):\n    print(y, round(float((s['ieee_saidi_with_med'] * s['ieee_customers']).sum() / s['ieee_customers'].sum()), 6), 1)\n")
    elif name == "ami_share":
        body = (f"d = d[d['entity'].isin(['eia_meters:{st}:advanced_meter_infrastructure:TOT', 'eia_meters:{st}:all_meters:TOT']) & (d['variable'] == 'meters')]\n"
                "d['kind'] = d['entity'].str.split(':').str[2]\nw = d.pivot_table(index='year', columns='kind', values='value').dropna()\nw = w[w['all_meters'] > 0]\n"
                "for y, r in w.iterrows():\n    print(y, round(float(100 * r['advanced_meter_infrastructure'] / r['all_meters']), 6), 1)\n")
    else:
        body = (f"d = d[(d['entity'] == 'eia_net_metering:{st}:all_technologies:TOT') & (d['variable'] == 'capacity')]\n"
                "for y, s in d.groupby('year'):\n    print(y, round(float(s['value'].sum()), 6), 1)\n")
    return head + body


def reproduce_do(name, region):
    st = region.rsplit("_", 1)[1]
    table = {"commercial_sales": SALES, "res_price": PRICES, "res_over_ind": PRICES, "saidi": REL, "ami_share": METERS, "net_metered": NEM}[name]
    lines = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public table.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
             "clear all", f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear', "destring value, replace force", "drop if missing(value)",
             "generate int year = real(substr(ts_utc, 1, 4))"]
    if name == "commercial_sales":
        lines += [f'keep if entity == "eia:retail_sales:{st}:COM" & variable == "retail_sales"', "collapse (sum) measure = value (count) n = value, by(year)",
                  "replace measure = measure / 1000000"]
    elif name == "res_price":
        lines += [f'keep if entity == "eia:retail_price:{st}:RES" & variable == "retail_price"', "collapse (mean) measure = value (count) n = value, by(year)"]
    elif name == "res_over_ind":
        lines += [f'keep if (entity == "eia:retail_price:{st}:RES" | entity == "eia:retail_price:{st}:IND") & variable == "retail_price"',
                  "generate str3 sec = substr(entity, -3, 3)", "keep year ts_utc sec value", "reshape wide value, i(ts_utc) j(sec) string",
                  "drop if missing(valueRES) | missing(valueIND)", "generate double gap = valueRES - valueIND", "collapse (mean) measure = gap (count) n = gap, by(year)"]
    elif name == "saidi":
        lines += ([] if st == "US" else [f'keep if geo == "US-{st}"']) + [
            'keep if variable == "ieee_saidi_with_med" | variable == "ieee_customers"', "keep entity year variable value",
            "reshape wide value, i(entity year) j(variable) string", "drop if missing(valueieee_saidi_with_med) | missing(valueieee_customers) | valueieee_customers <= 0",
            "generate double minutes = valueieee_saidi_with_med * valueieee_customers", "collapse (sum) minutes (sum) cust = valueieee_customers, by(year)",
            "generate double measure = minutes / cust", "generate byte n = 1"]
    elif name == "ami_share":
        lines += [f'keep if (entity == "eia_meters:{st}:advanced_meter_infrastructure:TOT" | entity == "eia_meters:{st}:all_meters:TOT") & variable == "meters"',
                  'generate str3 kind = cond(strpos(entity, "advanced") > 0, "ami", "all")', "keep year kind value", "reshape wide value, i(year) j(kind) string",
                  "drop if missing(valueami) | missing(valueall) | valueall <= 0", "generate double measure = 100 * valueami / valueall", "generate byte n = 1"]
    else:
        lines += [f'keep if entity == "eia_net_metering:{st}:all_technologies:TOT" & variable == "capacity"', "collapse (sum) measure = value, by(year)", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_EIA = "EIA's figures as published, nominal dollars where a price; the latest months are preliminary."
CANDIDATES = [
    C("commercial_sales", FAMILY, commercial_sales, "TWh", 1, 11, 2.0, "WHAT BUSINESSES BUY",
      "the year's retail electricity sales to the commercial sector", lambda w: f"retail electricity sales to the commercial sector in {w}",
      LIMIT_EIA + " EIA's commercial sector holds offices, shops and most data centers that buy at retail, and a utility may class a large load as industrial instead.",
      reproduce("commercial_sales"), consequence=3),
    C("res_price", FAMILY, res_price, "USD per MWh", 1, 11, 5.0, "WHAT HOMES PAY",
      "the mean of the year's monthly average residential retail price", lambda w: f"the average residential electricity price in {w}",
      LIMIT_EIA + " A mean of the months, not weighted by each month's sales.", reproduce("res_price"), consequence=3),
    C("res_over_ind", FAMILY, res_over_ind, "USD per MWh", 1, 11, 5.0, "HOMES AGAINST INDUSTRY",
      "the mean residential retail price less the mean industrial retail price over the year",
      lambda w: f"the residential electricity price in {w} above the industrial price", LIMIT_EIA, reproduce("res_over_ind"), consequence=2),
    C("saidi", FAMILY, saidi, "minutes a customer", 0, 1, 30.0, "MINUTES WITHOUT POWER",
      "the customer-weighted mean of the utilities' IEEE SAIDI with major event days",
      lambda w: f"the average minutes of interruption a customer saw in {w} (customer-weighted SAIDI, major event days included)",
      "EIA-861's utility reports; the utilities that report SAIDI change from year to year, and major storms dominate a year's figure.",
      reproduce("saidi"), first_words="the first year EIA's reliability table holds", consequence=3),
    C("ami_share", FAMILY, ami_share, "percent of meters", 1, 1, 3.0, "SMART METERS",
      "advanced metering infrastructure as a percent of all meters", lambda w: f"the share of meters in {w} that are advanced (AMI)",
      LIMIT_EIA + " EIA-861's meter counts by type, as utilities report them; the ERW's table splits out advanced meters by state only to 2019.", reproduce("ami_share"), first_words="the first year EIA's meter table holds", consequence=2),
    C("net_metered", FAMILY, net_metered, "MW", 0, 1, 200.0, "NET-METERED CAPACITY",
      "net-metered capacity, every technology and sector", lambda w: f"the net-metered capacity in {w}",
      LIMIT_EIA + " Net-metered systems as utilities report them to EIA-861; most is rooftop solar.", reproduce("net_metered"),
      first_words="the first year EIA's net metering table holds", consequence=2),
]
for _P in CANDIDATES:
    _P["rank_region"] = generation._us_first
    _P["rank"] = lambda c: abs(c["change"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family tariffs and policy, the retail side (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_retail", cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
