#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "oil_products_world", first part (session 3013).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Public EIA tables:

    eia_fuel_spot_prices                WTI at Cushing and Brent, daily (USD per barrel)
    eia_product_spot_prices             product spot prices, daily (USD per gallon): Gulf Coast conventional gasoline
                                        (EER_EPMRU_PF4_RGC_DPG), Gulf Coast ULSD (EER_EPD2DXL0_PF4_RGC_DPG), Gulf Coast jet
                                        fuel (EER_EPJK_PF4_RGC_DPG)
    eia_retail_fuel_prices              the US average retail regular gasoline price, weekly (EMM_EPMR_PTE_NUS_DPG)
    eia_net_imports_monthly             US net imports of crude oil and petroleum products (MTTNTUS2, thousand b/d)
    eia_crude_imports_by_country        US crude imports by country of origin (MCRIMUS<cc>2) and in all (MCRIMUS2)
    eia_crude_production_state_monthly  crude field production by state and in all (NUS), thousand b/d

A crack is the product's price in dollars a barrel (42 gallons) less WTI's, the days that hold both. Shares are of
the year's sums. Brent against WTI was drafted in session 3003 (fuels_carbon.py) and is not asked again.

    python warehouse/analysis/findings/deep/oil.py --dry-run
    python warehouse/analysis/findings/deep/oil.py --load
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

FAMILY = "oil_products_world"
FUEL, PROD, RETAIL, NET, IMP, CRUDE = ("eia_fuel_spot_prices", "eia_product_spot_prices", "eia_retail_fuel_prices", "eia_net_imports_monthly",
                                       "eia_crude_imports_by_country", "eia_crude_production_state_monthly")
PRODUCTS = {"gasoline": ("eia:EER_EPMRU_PF4_RGC_DPG", "Gulf Coast conventional gasoline"), "diesel": ("eia:EER_EPD2DXL0_PF4_RGC_DPG", "Gulf Coast ultra-low sulfur diesel"),
            "jet": ("eia:EER_EPJK_PF4_RGC_DPG", "Gulf Coast jet fuel")}
COUNTRIES = {"CA": "Canada", "MX": "Mexico", "SA": "Saudi Arabia", "CO": "Colombia", "NI": "Nigeria", "VE": "Venezuela", "KU": "Kuwait", "AO": "Angola",
             "BR": "Brazil", "EC": "Ecuador", "UK": "the United Kingdom", "NO": "Norway", "AG": "Algeria", "TD": "Trinidad and Tobago"}
STATES = generation.STATES
RETAIL_GAS = "eia:EMM_EPMR_PTE_NUS_DPG"


def _wti(in_dir):
    d = hm.series(FUEL, in_dir, variables=["spot_price"], entities=["eia:wti_cushing"])
    return d.assign(day=d["ts_utc"].str[:10]).set_index("day")["value"]


def _crack(in_dir, key):
    ent, words = PRODUCTS[key]
    p = hm.series(PROD, in_dir, variables=["spot_price"], entities=[ent])
    p = p.assign(day=p["ts_utc"].str[:10]).set_index("day")["value"] * 42.0
    w = _wti(in_dir)
    both = p.to_frame("p").join(w.rename("w"), how="inner")
    both = both.assign(year=both.index.str[:4].astype(int))
    rows = [hm._row(f"crack_{key}", words, y, float((s["p"] - s["w"]).mean()), len(s)) for y, s in both.groupby("year")]
    return {"rows": rows, "tables": {f"crack_{key}": [PROD, FUEL]}}


def gasoline_crack(in_dir=None):
    """Gulf Coast conventional gasoline in USD a barrel less WTI, the year's mean of the days with both."""
    return _crack(in_dir, "gasoline")


def diesel_crack(in_dir=None):
    """Gulf Coast ULSD in USD a barrel less WTI, the year's mean of the days with both."""
    return _crack(in_dir, "diesel")


def jet_crack(in_dir=None):
    """Gulf Coast jet fuel in USD a barrel less WTI, the year's mean of the days with both."""
    return _crack(in_dir, "jet")


def _retail(in_dir):
    r = hm.series(RETAIL, in_dir, variables=["retail_price"], entities=[RETAIL_GAS])
    return r.assign(year=r["ts_utc"].str[:4].astype(int))


def crude_share_of_pump(in_dir=None):
    """WTI's mean over the year in USD a gallon (a barrel over 42) as a percent of the year's mean retail regular gasoline price."""
    r = _retail(in_dir)
    w = _wti(in_dir)
    wy = w.groupby(w.index.str[:4].astype(int)).mean() / 42.0
    rows = [hm._row("us_pump_crude", "US regular gasoline", y, float(100 * wy[y] / s["value"].mean()), len(s)) for y, s in r.groupby("year") if y in wy.index]
    return {"rows": rows, "tables": {"us_pump_crude": [RETAIL, FUEL]}}


def pump_over_spot(in_dir=None):
    """The year's mean retail regular gasoline price less the year's mean Gulf Coast conventional gasoline spot price (USD a gallon)."""
    r = _retail(in_dir)
    p = hm.series(PROD, in_dir, variables=["spot_price"], entities=[PRODUCTS["gasoline"][0]])
    py = p.groupby(p["ts_utc"].str[:4].astype(int))["value"].mean()
    rows = [hm._row("us_pump_spot", "US regular gasoline", y, float(s["value"].mean() - py[y]), len(s)) for y, s in r.groupby("year") if y in py.index]
    return {"rows": rows, "tables": {"us_pump_spot": [RETAIL, PROD]}}


def net_imports(in_dir=None):
    """US net imports of crude oil and petroleum products, the year's mean of its months (thousand barrels a day)."""
    d = hm.series(NET, in_dir, variables=["net_imports_crude_and_products"], entities=["eia_net_imports:MTTNTUS2"]).drop_duplicates("ts_utc")
    d = d.assign(year=d["ts_utc"].str[:4].astype(int))
    rows = [hm._row("us_net_imports", "the United States", y, float(s["value"].mean()), len(s)) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"us_net_imports": [NET]}}


def import_share(in_dir=None):
    """A country's share of US crude oil imports over the year (percent of the year's sum of monthly thousand b/d)."""
    d = hm.series(IMP, in_dir, variables=["imports"], entities=["eia:MCRIMUS2"] + [f"eia:MCRIMUS{c}2" for c in COUNTRIES]).drop_duplicates(["entity", "ts_utc"])
    d = d.assign(year=d["ts_utc"].str[:4].astype(int))
    tot = d[d["entity"] == "eia:MCRIMUS2"].groupby("year")["value"].sum()
    rows, tables = [], {}
    for c, name in COUNTRIES.items():
        g = d[d["entity"] == f"eia:MCRIMUS{c}2"]
        for y, s in g.groupby("year"):
            if tot.get(y, 0) > 0:
                rows.append(hm._row(f"imp_{c}", name, y, float(100 * s["value"].sum() / tot[y]), len(s)))
        tables[f"imp_{c}"] = [IMP]
    return {"rows": rows, "tables": tables}


def state_crude_share(in_dir=None):
    """A state's share of US crude field production over the year (percent of the year's sum of monthly thousand b/d)."""
    d = hm.series(CRUDE, in_dir, variables=["field_production_per_day"]).drop_duplicates(["entity", "ts_utc"])
    d = d.assign(code=d["entity"].str.split(":").str[1], year=d["ts_utc"].str[:4].astype(int))
    tot = d[d["code"] == "NUS"].groupby("year")["value"].sum()
    rows, tables = [], {}
    for code, g in d[d["code"].str.match(r"^S[A-Z]{2}$")].groupby("code"):
        st = code[1:]
        if st not in STATES:
            continue
        for y, s in g.groupby("year"):
            if tot.get(y, 0) > 0:
                rows.append(hm._row(f"crude_{st}", STATES[st], y, float(100 * s["value"].sum() / tot[y]), len(s)))
        tables[f"crude_{st}"] = [CRUDE]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_READ = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables.

    python {{this file}} {args}

{label}.
"""
import sys

import pandas as pd


def read(path):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.dropna(subset=["value"])


'''


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    if name.endswith("_crack"):
        ent = PRODUCTS[name.split("_")[0]][0]
        return (PY_READ.format(name=name, region=region, args=f"<{PROD}.csv> <{FUEL}.csv>", label=label)
                + f"p = read(sys.argv[1])\np = p[(p['entity'] == {ent!r}) & (p['variable'] == 'spot_price')]\np = p.assign(day=p['ts_utc'].str[:10]).set_index('day')['value'] * 42.0\n"
                + "w = read(sys.argv[2])\nw = w[(w['entity'] == 'eia:wti_cushing') & (w['variable'] == 'spot_price')]\nw = w.assign(day=w['ts_utc'].str[:10]).set_index('day')['value']\n"
                + "b = p.to_frame('p').join(w.rename('w'), how='inner')\nfor y, s in b.groupby(b.index.str[:4].astype(int)):\n    print(y, round(float((s['p'] - s['w']).mean()), 6), len(s))\n")
    if name == "crude_share_of_pump":
        return (PY_READ.format(name=name, region=region, args=f"<{RETAIL}.csv> <{FUEL}.csv>", label=label)
                + f"r = read(sys.argv[1])\nr = r[(r['entity'] == {RETAIL_GAS!r}) & (r['variable'] == 'retail_price')]\n"
                + "w = read(sys.argv[2])\nw = w[(w['entity'] == 'eia:wti_cushing') & (w['variable'] == 'spot_price')]\n"
                + "wy = w.groupby(w['ts_utc'].str[:4].astype(int))['value'].mean() / 42.0\n"
                + "for y, s in r.groupby(r['ts_utc'].str[:4].astype(int)):\n    if y in wy.index:\n        print(y, round(float(100 * wy[y] / s['value'].mean()), 6), len(s))\n")
    if name == "pump_over_spot":
        return (PY_READ.format(name=name, region=region, args=f"<{RETAIL}.csv> <{PROD}.csv>", label=label)
                + f"r = read(sys.argv[1])\nr = r[(r['entity'] == {RETAIL_GAS!r}) & (r['variable'] == 'retail_price')]\n"
                + f"p = read(sys.argv[2])\np = p[(p['entity'] == {PRODUCTS['gasoline'][0]!r}) & (p['variable'] == 'spot_price')]\n"
                + "py = p.groupby(p['ts_utc'].str[:4].astype(int))['value'].mean()\n"
                + "for y, s in r.groupby(r['ts_utc'].str[:4].astype(int)):\n    if y in py.index:\n        print(y, round(float(s['value'].mean() - py[y]), 6), len(s))\n")
    if name == "net_imports":
        return (PY_READ.format(name=name, region=region, args=f"<{NET}.csv>", label=label)
                + "d = read(sys.argv[1])\nd = d[(d['entity'] == 'eia_net_imports:MTTNTUS2') & (d['variable'] == 'net_imports_crude_and_products')].drop_duplicates('ts_utc')\n"
                + "for y, s in d.groupby(d['ts_utc'].str[:4].astype(int)):\n    print(y, round(float(s['value'].mean()), 6), len(s))\n")
    if name == "import_share":
        c = region.split("_")[1]
        return (PY_READ.format(name=name, region=region, args=f"<{IMP}.csv>", label=label + f", {COUNTRIES[c]}")
                + f"d = read(sys.argv[1])\nd = d[d['entity'].isin(['eia:MCRIMUS2', 'eia:MCRIMUS{c}2']) & (d['variable'] == 'imports')].drop_duplicates(['entity', 'ts_utc'])\n"
                + "d['year'] = d['ts_utc'].str[:4].astype(int)\ntot = d[d['entity'] == 'eia:MCRIMUS2'].groupby('year')['value'].sum()\n"
                + f"for y, s in d[d['entity'] == 'eia:MCRIMUS{c}2'].groupby('year'):\n    if tot.get(y, 0) > 0:\n        print(y, round(float(100 * s['value'].sum() / tot[y]), 6), len(s))\n")
    st = region.split("_")[1]
    return (PY_READ.format(name=name, region=region, args=f"<{CRUDE}.csv>", label=label + f", {STATES[st]}")
            + "d = read(sys.argv[1])\nd = d[d['variable'] == 'field_production_per_day'].drop_duplicates(['entity', 'ts_utc'])\n"
            + "d['code'], d['year'] = d['entity'].str.split(':').str[1], d['ts_utc'].str[:4].astype(int)\ntot = d[d['code'] == 'NUS'].groupby('year')['value'].sum()\n"
            + f"for y, s in d[d['code'] == 'S{st}'].groupby('year'):\n    if tot.get(y, 0) > 0:\n        print(y, round(float(100 * s['value'].sum() / tot[y]), 6), len(s))\n")


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.",
            "clear all"]
    if name.endswith("_crack") or name in ("crude_share_of_pump", "pump_over_spot"):
        if name.endswith("_crack"):
            ent, other, var = PRODUCTS[name.split("_")[0]][0], PROD, "spot_price"
        elif name == "crude_share_of_pump":
            ent, other, var = RETAIL_GAS, RETAIL, "retail_price"
        else:
            ent, other, var = RETAIL_GAS, RETAIL, "retail_price"
        lines = head + [f'import delimited "{FUEL if name != "pump_over_spot" else PROD}.csv", varnames(1) stringcols(_all) clear',
                        ('keep if entity == "eia:wti_cushing" & variable == "spot_price"' if name != "pump_over_spot"
                         else f'keep if entity == "{PRODUCTS["gasoline"][0]}" & variable == "spot_price"'),
                        "destring value, replace force", "drop if missing(value)", "generate str10 day = substr(ts_utc, 1, 10)", "keep day value",
                        "rename value base", "duplicates drop day, force", "save base_prices, replace",
                        f'import delimited "{other}.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{ent}" & variable == "{var}"',
                        "destring value, replace force", "drop if missing(value)", "generate str10 day = substr(ts_utc, 1, 10)", "keep day value", "duplicates drop day, force"]
        if name.endswith("_crack"):
            lines += ["merge 1:1 day using base_prices, keep(match) nogenerate", "generate double crack = value * 42 - base",
                      "generate int year = real(substr(day, 1, 4))", "collapse (mean) measure = crack (count) n = crack, by(year)"]
        else:
            lines += ["generate int year = real(substr(day, 1, 4))", "collapse (mean) retail = value (count) n = value, by(year)", "save retail_years, replace",
                      "use base_prices, clear", "generate int year = real(substr(day, 1, 4))", "collapse (mean) base, by(year)",
                      "merge 1:1 year using retail_years, keep(match) nogenerate",
                      ("generate double measure = 100 * (base / 42) / retail" if name == "crude_share_of_pump" else "generate double measure = retail - base")]
    elif name == "net_imports":
        lines = head + [f'import delimited "{NET}.csv", varnames(1) stringcols(_all) clear', 'keep if entity == "eia_net_imports:MTTNTUS2" & variable == "net_imports_crude_and_products"',
                        "destring value, replace force", "drop if missing(value)", "duplicates drop ts_utc, force", "generate int year = real(substr(ts_utc, 1, 4))",
                        "collapse (mean) measure = value (count) n = value, by(year)"]
    elif name == "import_share":
        c = region.split("_")[1]
        lines = head + [f'import delimited "{IMP}.csv", varnames(1) stringcols(_all) clear',
                        f'keep if (entity == "eia:MCRIMUS2" | entity == "eia:MCRIMUS{c}2") & variable == "imports"', "destring value, replace force", "drop if missing(value)",
                        "duplicates drop entity ts_utc, force", "generate int year = real(substr(ts_utc, 1, 4))",
                        'generate double tot = value if entity == "eia:MCRIMUS2"', f'generate double one = value if entity == "eia:MCRIMUS{c}2"',
                        "egen byte has = tag(ts_utc) if !missing(one)", "collapse (sum) tot (sum) one (sum) n = has, by(year)", "keep if tot > 0 & n > 0",
                        "generate double measure = 100 * one / tot"]
    else:
        st = region.split("_")[1]
        lines = head + [f'import delimited "{CRUDE}.csv", varnames(1) stringcols(_all) clear', 'keep if variable == "field_production_per_day"',
                        "destring value, replace force", "drop if missing(value)", "duplicates drop entity ts_utc, force",
                        'generate str4 code = word(subinstr(entity, ":", " ", .), 2)', f'keep if code == "NUS" | code == "S{st}"',
                        "generate int year = real(substr(ts_utc, 1, 4))", 'generate double tot = value if code == "NUS"', f'generate double one = value if code == "S{st}"',
                        "egen byte has = tag(ts_utc) if !missing(one)", "collapse (sum) tot (sum) one (sum) n = has, by(year)", "keep if tot > 0 & n > 0",
                        "generate double measure = 100 * one / tot"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_SPOT = "EIA's daily spot closes, nominal dollars; a crack is the product less crude at one place, not a refiner's margin, which counts its own crude and costs."
CANDIDATES = [
    C("gasoline_crack", FAMILY, gasoline_crack, "USD per barrel", 2, 200, 2.0, "THE GASOLINE CRACK",
      "Gulf Coast conventional gasoline in dollars a barrel less WTI, the year's mean of the days with both",
      lambda w: "the mean spread of Gulf Coast gasoline over WTI crude", LIMIT_SPOT, reproduce("gasoline_crack"), consequence=3),
    C("diesel_crack", FAMILY, diesel_crack, "USD per barrel", 2, 200, 2.0, "THE DIESEL CRACK",
      "Gulf Coast ultra-low sulfur diesel in dollars a barrel less WTI, the year's mean of the days with both",
      lambda w: "the mean spread of Gulf Coast diesel over WTI crude", LIMIT_SPOT, reproduce("diesel_crack"), consequence=3),
    C("jet_crack", FAMILY, jet_crack, "USD per barrel", 2, 200, 2.0, "THE JET FUEL CRACK",
      "Gulf Coast jet fuel in dollars a barrel less WTI, the year's mean of the days with both",
      lambda w: "the mean spread of Gulf Coast jet fuel over WTI crude", LIMIT_SPOT, reproduce("jet_crack"), consequence=2),
    C("crude_share_of_pump", FAMILY, crude_share_of_pump, "percent of the retail price", 1, 40, 3.0, "CRUDE'S SHARE AT THE PUMP",
      "WTI's mean over the year in dollars a gallon as a percent of the year's mean retail regular gasoline price",
      lambda w: "WTI crude's mean price a gallon as a share of the mean US retail price of regular gasoline",
      "Two annual means of nominal prices; a refiner buys more crude than WTI, and the retail price includes taxes.", reproduce("crude_share_of_pump"), consequence=3),
    C("pump_over_spot", FAMILY, pump_over_spot, "USD per gallon", 3, 40, 0.1, "FROM THE GULF COAST TO THE PUMP",
      "the year's mean retail regular gasoline price less the year's mean Gulf Coast conventional gasoline spot price",
      lambda w: "the mean US retail price of regular gasoline above the Gulf Coast spot price",
      "Nominal dollars; the gap holds taxes, transport, blending and the stations' margins together, and the measure does not separate them.",
      reproduce("pump_over_spot"), consequence=2),
    C("net_imports", FAMILY, net_imports, "thousand barrels a day", 0, 11, 500.0, "NET IMPORTS OF OIL",
      "US net imports of crude oil and petroleum products, the year's mean of its months",
      lambda w: "US net imports of crude oil and petroleum products", "EIA's monthly figures, the latest preliminary; a negative figure is net exports.",
      reproduce("net_imports"), first_words="the first year the ERW's table holds", consequence=3),
    C("import_share", FAMILY, import_share, "percent of US crude imports", 1, 11, 3.0, "WHERE US CRUDE IMPORTS COME FROM",
      "a country's share of US crude oil imports over the year", lambda w: f"{w}'s share of US crude oil imports",
      "EIA's imports by country of origin, monthly thousand barrels a day summed over the year; a country's share of a total that itself changed.",
      reproduce("import_share"), consequence=3),
    C("state_crude_share", FAMILY, state_crude_share, "percent of US crude production", 1, 11, 2.0, "A STATE'S SHARE OF US CRUDE",
      "a state's share of US crude field production over the year", lambda w: f"{w}'s share of US crude oil production",
      "EIA's field production by state, the latest months estimated; the federal offshore is in the US total and in no state.",
      reproduce("state_crude_share"), consequence=3),
]
for _P in CANDIDATES:
    if _P["name"] in ("import_share", "state_crude_share"):
        _P["rank"] = lambda c: abs(c["change"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family oil and products (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_oil", cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
