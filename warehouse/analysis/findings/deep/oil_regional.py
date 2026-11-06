#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164), family "oil_products_world", third part (session 3015).

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Tables:

    eia_regional_retail_fuel_prices   weekly retail regular gasoline by PADD and state, 2019 on (public)
    eia_retail_fuel_prices            weekly US retail regular gasoline and diesel, from 1994 (public)
    eia_product_spot_prices           Mont Belvieu propane, daily (public)
    eia_fuel_spot_prices              WTI, daily (public)
    portwatch_chokepoint_transits     IMF PortWatch's daily transits through the Suez Canal, the Panama Canal and the
                                      Strait of Hormuz, 2019 on. INTERNAL (the session 8 ruling; the IMF asks permission
                                      for a commercial reuse): its drafts carry "License needed" before their figure

    python warehouse/analysis/findings/deep/oil_regional.py --dry-run
    python warehouse/analysis/findings/deep/oil_regional.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "oil_products_world"
REG, RET, PROD, FUEL, PW = ("eia_regional_retail_fuel_prices", "eia_retail_fuel_prices", "eia_product_spot_prices", "eia_fuel_spot_prices",
                            "portwatch_chokepoint_transits")
US_GAS, US_DIESEL = "eia:EMM_EPMR_PTE_NUS_DPG", "eia:EMD_EPD2D_PTE_NUS_DPG"
AREAS = {"SCA": "California", "R10": "the East Coast (PADD 1)", "R20": "the Midwest (PADD 2)", "R30": "the Gulf Coast (PADD 3)",
         "R40": "the Rocky Mountains (PADD 4)", "R50": "the West Coast (PADD 5)", "R5XCA": "the West Coast outside California"}
PROPANE = "eia:EER_EPLLPA_PF4_Y44MB_DPG"
CHOKES = {"portwatch:chokepoint1": ("suez", "the Suez Canal"), "portwatch:chokepoint2": ("panama", "the Panama Canal"), "portwatch:chokepoint6": ("hormuz", "the Strait of Hormuz")}
LICENSE = "License needed (IMF PortWatch's portwatch_chokepoint_transits is held internal):"


def _weekly(table, in_dir, ents, var):
    d = hm.series(table, in_dir, variables=[var], entities=ents)
    return d.assign(day=d["ts_utc"].str[:10])


def gas_premium(in_dir=None):
    """An area's weekly retail regular gasoline price less the US price, the year's mean of the weeks with both (USD a gallon)."""
    d = _weekly(REG, in_dir, [US_GAS] + [f"eia:EMM_EPMR_PTE_{a}_DPG" for a in AREAS], "retail_price")
    w = d.pivot_table(index="day", columns="entity", values="value")
    rows, tables = [], {}
    for a, words in AREAS.items():
        ent = f"eia:EMM_EPMR_PTE_{a}_DPG"
        if ent not in w:
            continue
        b = w[[ent, US_GAS]].dropna()
        gap = b[ent] - b[US_GAS]
        for y, s in gap.groupby(gap.index.str[:4].astype(int)):
            rows.append(hm._row(f"gasprem_{a}", words, y, float(s.mean()), len(s)))
        tables[f"gasprem_{a}"] = [REG]
    return {"rows": rows, "tables": tables}


def diesel_premium(in_dir=None):
    """The US weekly retail diesel price less the retail regular gasoline price, the year's mean of the weeks with both (USD a gallon)."""
    d = _weekly(RET, in_dir, [US_GAS, US_DIESEL], "retail_price")
    w = d.pivot_table(index="day", columns="entity", values="value").dropna()
    gap = w[US_DIESEL] - w[US_GAS]
    rows = [hm._row("us_diesel_premium", "the United States", y, float(s.mean()), len(s)) for y, s in gap.groupby(gap.index.str[:4].astype(int))]
    return {"rows": rows, "tables": {"us_diesel_premium": [RET]}}


def propane_to_crude(in_dir=None):
    """Mont Belvieu propane in dollars a barrel as a percent of WTI, the year's mean of the days with both."""
    p = _weekly(PROD, in_dir, [PROPANE], "spot_price").set_index("day")["value"] * 42.0
    w = _weekly(FUEL, in_dir, ["eia:wti_cushing"], "spot_price").set_index("day")["value"]
    b = p.to_frame("p").join(w.rename("w"), how="inner")
    b = b[b["w"] > 0]
    r = 100 * b["p"] / b["w"]
    rows = [hm._row("us_propane_crude", "Mont Belvieu propane", y, float(s.mean()), len(s)) for y, s in r.groupby(r.index.str[:4].astype(int))]
    return {"rows": rows, "tables": {"us_propane_crude": [PROD, FUEL]}}


def tanker_transits(in_dir=None):
    """Tanker transits through a chokepoint over the year (count), IMF PortWatch: the sum of its daily counts."""
    d = hm.series(PW, in_dir, variables=["n_tanker"], entities=list(CHOKES)).drop_duplicates(["entity", "ts_utc"])
    d = d.assign(year=d["ts_utc"].str[:4].astype(int))
    rows, tables = [], {}
    for ent, g in d.groupby("entity"):
        key, words = CHOKES[ent]
        for y, s in g.groupby("year"):
            rows.append(hm._row(f"chk_{key}", words, y, float(s["value"].sum()), len(s)))
        tables[f"chk_{key}"] = [PW]
    return {"rows": rows, "tables": tables}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
PY_READ = '''"""ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's tables.

    python {{this file}} {args}

{label}.
"""
import sys

import pandas as pd


def read(path, entities, variable):
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                break
            skip += 1
    d = pd.read_csv(path, skiprows=skip, usecols=["entity", "variable", "ts_utc", "value"], dtype=str)
    d = d[d["entity"].isin(entities) & (d["variable"] == variable)].copy()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d["day"] = d["ts_utc"].str[:10]
    return d


'''


def reproduce_py(name, region):
    P = next(p for p in CANDIDATES if p["name"] == name)
    label = P["label"][0].upper() + P["label"][1:]
    if name == "gas_premium":
        a = region.split("_", 1)[1]
        ent = f"eia:EMM_EPMR_PTE_{a}_DPG"
        return (PY_READ.format(name=name, region=region, args=f"<{REG}.csv>", label=label + f", {AREAS[a]}")
                + f"d = read(sys.argv[1], [{US_GAS!r}, {ent!r}], 'retail_price')\nw = d.pivot_table(index='day', columns='entity', values='value')[[{ent!r}, {US_GAS!r}]].dropna()\n"
                + f"gap = w[{ent!r}] - w[{US_GAS!r}]\nfor y, s in gap.groupby(gap.index.str[:4].astype(int)):\n    print(y, round(float(s.mean()), 6), len(s))\n")
    if name == "diesel_premium":
        return (PY_READ.format(name=name, region=region, args=f"<{RET}.csv>", label=label)
                + f"d = read(sys.argv[1], [{US_GAS!r}, {US_DIESEL!r}], 'retail_price')\nw = d.pivot_table(index='day', columns='entity', values='value').dropna()\n"
                + f"gap = w[{US_DIESEL!r}] - w[{US_GAS!r}]\nfor y, s in gap.groupby(gap.index.str[:4].astype(int)):\n    print(y, round(float(s.mean()), 6), len(s))\n")
    if name == "propane_to_crude":
        return (PY_READ.format(name=name, region=region, args=f"<{PROD}.csv> <{FUEL}.csv>", label=label)
                + f"p = read(sys.argv[1], [{PROPANE!r}], 'spot_price').set_index('day')['value'] * 42.0\nw = read(sys.argv[2], ['eia:wti_cushing'], 'spot_price').set_index('day')['value']\n"
                + "b = p.to_frame('p').join(w.rename('w'), how='inner')\nb = b[b['w'] > 0]\nr = 100 * b['p'] / b['w']\n"
                + "for y, s in r.groupby(r.index.str[:4].astype(int)):\n    print(y, round(float(s.mean()), 6), len(s))\n")
    ent = next(k for k, v in CHOKES.items() if f"chk_{v[0]}" == region)
    return (PY_READ.format(name=name, region=region, args=f"<{PW}.csv>", label=label + f", {CHOKES[ent][1]} (IMF PortWatch, held internal: license needed)")
            + f"d = read(sys.argv[1], [{ent!r}], 'n_tanker').drop_duplicates(['entity', 'ts_utc'])\n"
            + "for y, s in d.groupby(d['ts_utc'].str[:4].astype(int)):\n    print(y, round(float(s['value'].sum()), 6), len(s))\n")


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain 164): reproduce candidate {name} for {region} from the ERW's tables.",
            "* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.",
            "clear all"]
    if name in ("gas_premium", "diesel_premium"):
        if name == "gas_premium":
            a = region.split("_", 1)[1]
            table, one, base = REG, f"eia:EMM_EPMR_PTE_{a}_DPG", US_GAS
        else:
            table, one, base = RET, US_DIESEL, US_GAS
        lines = head + [f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear', f'keep if (entity == "{one}" | entity == "{base}") & variable == "retail_price"',
                        "destring value, replace force", "drop if missing(value)", "generate str10 day = substr(ts_utc, 1, 10)",
                        f'generate str4 side = cond(entity == "{one}", "one", "base")', "keep day side value", "duplicates drop day side, force",
                        "reshape wide value, i(day) j(side) string", "drop if missing(valueone) | missing(valuebase)", "generate double gap = valueone - valuebase",
                        "generate int year = real(substr(day, 1, 4))", "collapse (mean) measure = gap (count) n = gap, by(year)"]
    elif name == "propane_to_crude":
        lines = head + [f'import delimited "{FUEL}.csv", varnames(1) stringcols(_all) clear', 'keep if entity == "eia:wti_cushing" & variable == "spot_price"',
                        "destring value, replace force", "keep if value > 0 & !missing(value)", "generate str10 day = substr(ts_utc, 1, 10)", "keep day value",
                        "rename value wti", "duplicates drop day, force", "save wti_days, replace",
                        f'import delimited "{PROD}.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{PROPANE}" & variable == "spot_price"',
                        "destring value, replace force", "drop if missing(value)", "generate str10 day = substr(ts_utc, 1, 10)", "keep day value", "duplicates drop day, force",
                        "merge 1:1 day using wti_days, keep(match) nogenerate", "generate double ratio = 100 * value * 42 / wti",
                        "generate int year = real(substr(day, 1, 4))", "collapse (mean) measure = ratio (count) n = ratio, by(year)"]
    else:
        ent = next(k for k, v in CHOKES.items() if f"chk_{v[0]}" == region)
        lines = head + ["* IMF PortWatch's table is held internal (license needed); this file is for the review, not for publication.",
                        f'import delimited "{PW}.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{ent}" & variable == "n_tanker"',
                        "destring value, replace force", "drop if missing(value)", "duplicates drop entity ts_utc, force", "generate int year = real(substr(ts_utc, 1, 4))",
                        "collapse (sum) measure = value (count) n = value, by(year)"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
CANDIDATES = [
    C("gas_premium", FAMILY, gas_premium, "USD per gallon", 3, 45, 0.05, "WHAT A REGION PAYS AT THE PUMP",
      "an area's retail regular gasoline price less the US price, the year's mean of the weeks with both",
      lambda w: f"the retail price of regular gasoline in {w} above the US average",
      "EIA's weekly retail prices, nominal dollars, taxes included; the ERW's regional table begins in 2019.",
      reproduce("gas_premium"), first_words="the first year the ERW's regional table holds", consequence=3),
    C("diesel_premium", FAMILY, diesel_premium, "USD per gallon", 3, 45, 0.05, "DIESEL AGAINST GASOLINE AT THE PUMP",
      "the US retail diesel price less the retail regular gasoline price, the year's mean of the weeks with both",
      lambda w: "the US retail price of diesel above regular gasoline",
      "EIA's weekly retail prices, nominal dollars, taxes included; federal and state taxes differ between the two fuels.",
      reproduce("diesel_premium"), consequence=2),
    C("propane_to_crude", FAMILY, propane_to_crude, "percent of WTI", 1, 200, 5.0, "PROPANE AGAINST CRUDE",
      "Mont Belvieu propane in dollars a barrel as a percent of WTI, the year's mean of the days with both",
      lambda w: "the Mont Belvieu propane price as a share of WTI's, a barrel against a barrel,",
      "Spot closes in nominal dollars; a barrel of propane holds less energy than a barrel of crude.", reproduce("propane_to_crude"), consequence=2),
    C("tanker_transits", FAMILY, tanker_transits, "tanker transits", 0, 330, 200.0, "TANKERS THROUGH A CHOKEPOINT",
      "tanker transits through a chokepoint over the year, IMF PortWatch",
      lambda w: f"the number of tanker transits through {w}",
      "IMF PortWatch's daily counts from ships' AIS signals; a tanker carries crude, products, chemicals or gas, and the count is not a volume.",
      reproduce("tanker_transits"), first_words="the first year PortWatch's table holds", consequence=3),
]
for _P in CANDIDATES:
    if _P["name"] == "tanker_transits":
        _P["license_note"] = LICENSE
        _P["max_per"] = 3
    if _P["name"] == "gas_premium":
        _P["area"] = lambda r: "west" if r in ("gasprem_SCA", "gasprem_R50", "gasprem_R5XCA") else r   # California is most of PADD 5: one story


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, family oil, regions and chokepoints (chain 164)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY + "_regional", cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
