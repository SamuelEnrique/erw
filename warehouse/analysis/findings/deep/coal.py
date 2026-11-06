#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 166, session 3175): coal and uranium.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-06.md. Public EIA tables, annual:

    eia_coal_production_annual      production, mines and employees by state, region, rank and mine type (US:TOT:ALL the
                                    US, WY Wyoming, APP Appalachia; UND underground)
    eia_coal_delivered_price_annual the delivered price of coal by location and sector (US:98, electric power)
    eia_uranium_marketing_annual    EIA's Uranium Marketing Annual Report: purchases by origin, contract and price,
                                    enrichment by origin, owners and operators of US reactors

oil_world.py's two rules (a series' yearly mean, or one series over another, the years that hold both) and its scripts'
templates are used as they are; an annual figure is its year's one observation.

    python warehouse/analysis/findings/deep/coal.py --dry-run
    python warehouse/analysis/findings/deep/coal.py --load
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
import oil_world as ow  # noqa: E402

FAMILY = "coal_uranium_metals"
PROD, PRICE, U = "eia_coal_production_annual", "eia_coal_delivered_price_annual", "eia_uranium_marketing_annual"
US = "eia_coal_production:US:TOT:ALL"
SPEC = {
    "wyoming_share": (PROD, "share", ("eia_coal_production:WY:TOT:ALL", "production"), (US, "production"), 100.0),
    "appalachia_share": (PROD, "share", ("eia_coal_production:APP:TOT:ALL", "production"), (US, "production"), 100.0),
    "underground_share": (PROD, "share", ("eia_coal_production:US:TOT:UND", "production"), (US, "production"), 100.0),
    "tons_per_employee": (PROD, "share", (US, "production"), (US, "employees"), 1.0),
    "power_coal_price": (PRICE, "mean", ("eia_coal_delivered:US:98", "price"), None, 1.0),
    "us_origin_uranium": (U, "share", ("eia_uranium:us", "purchased_us_origin"), ("eia_uranium:us", "purchased_total"), 100.0),
    "uranium_price": (U, "mean", ("eia_uranium:us", "price_purchased_total"), None, 1.0),
    "spot_uranium_share": (U, "share", ("eia_uranium:us", "purchased_spot"), ("eia_uranium:us", "purchased_total"), 100.0),
    "us_enrichment_share": (U, "share", ("eia_uranium:us", "enrichment_us_origin"), ("eia_uranium:us", "enrichment_total"), 100.0),
}


def compute(d, kind, num, den, scale):
    """oil_world's rules; a share whose two series share an entity is read by variable."""
    d = d.drop_duplicates(["entity", "variable", "ts_utc"]).assign(year=d["ts_utc"].str[:4].astype(int))
    a = d[(d["entity"] == num[0]) & (d["variable"] == num[1])]
    if kind == "mean":
        return {int(y): (float(s["value"].mean() * scale), 1) for y, s in a.groupby("year")}
    b = d[(d["entity"] == den[0]) & (d["variable"] == den[1])]
    m = a.merge(b[["ts_utc", "value"]], on="ts_utc", suffixes=("", "_den"))
    return {int(y): (float(s["value"].sum() * scale / s["value_den"].sum()), 1) for y, s in m.groupby("year") if s["value_den"].sum() != 0}


def _fn(name, region, words):
    table, kind, num, den, scale = SPEC[name]

    def fn(in_dir=None):
        ents = sorted({num[0]} | ({den[0]} if den else set()))
        d = hm.series(table, in_dir, entities=ents)[["entity", "variable", "ts_utc", "value"]]
        return {"rows": [hm._row(region, words, y, v, n) for y, (v, n) in compute(d, kind, num, den, scale).items()], "tables": {region: [table]}}
    fn.__name__ = name
    return fn


def reproduce_py(name, region):
    table, kind, num, den, scale = SPEC[name]
    P = next(p for p in CANDIDATES if p["name"] == name)
    rule = "the year's figure (an annual table: one row a year)." if kind == "mean" else "one series over another, the years that hold both."
    text = ow.PY.format(name=name, region=region, table=table, label=P["label"][0].upper() + P["label"][1:], kind=kind, rule=rule, num_e=num[0], num_v=num[1])
    if kind == "mean":
        return text + "for y, s in a.groupby('year'):\n    print(y, round(float(s['value'].mean() * {scale!r}), 6), 1)\n".format(scale=scale)
    return text + ("b = d[(d['entity'] == {den_e!r}) & (d['variable'] == {den_v!r})]\nm = a.merge(b[['ts_utc', 'value']], on='ts_utc', suffixes=('', '_den'))\n"
                   "for y, s in m.groupby('year'):\n    if s['value_den'].sum() != 0:\n        print(y, round(float(s['value'].sum() * {scale!r} / s['value_den'].sum()), 6), 1)\n"
                   ).format(den_e=den[0], den_v=den[1], scale=scale)


def reproduce_do(name, region):
    table, kind, num, den, scale = SPEC[name]
    lines = [f"* ERW findings hunt (chain 166): reproduce candidate {name} for {region} from the ERW's public table.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.",
             "clear all", f'import delimited "{table}.csv", varnames(1) stringcols(_all) clear', "destring value, replace force", "drop if missing(value)",
             "duplicates drop entity variable ts_utc, force", "generate int year = real(substr(ts_utc, 1, 4))"]
    if kind == "mean":
        lines += [f'keep if entity == "{num[0]}" & variable == "{num[1]}"', "collapse (mean) measure = value, by(year)", f"replace measure = measure * {scale!r}"]
    else:
        lines += [f'keep if (entity == "{num[0]}" & variable == "{num[1]}") | (entity == "{den[0]}" & variable == "{den[1]}")',
                  f'generate str3 side = cond(entity == "{num[0]}" & variable == "{num[1]}", "num", "den")', "keep year ts_utc side value",
                  "reshape wide value, i(ts_utc) j(side) string", "drop if missing(valuenum) | missing(valueden)",
                  "collapse (sum) num = valuenum (sum) den = valueden, by(year)", "keep if den != 0", f"generate double measure = num * {scale!r} / den"]
    lines += ["generate byte n = 1", "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LIMIT_COAL = "EIA's annual coal data as published, the latest year preliminary."
LIMIT_U = "EIA's Uranium Marketing Annual Report: what the owners and operators of US reactors bought, in pounds of U3O8 equivalent; EIA withholds some years' figures."
CANDIDATES = [
    C("wyoming_share", FAMILY, _fn("wyoming_share", "wy_coal", "Wyoming"), "percent of US coal production", 1, 1, 2.0, "WYOMING'S COAL",
      "Wyoming's coal production as a percent of the US", lambda w: "Wyoming's share of US coal production", LIMIT_COAL, reproduce("wyoming_share"), consequence=2),
    C("appalachia_share", FAMILY, _fn("appalachia_share", "app_coal", "Appalachia"), "percent of US coal production", 1, 1, 2.0, "APPALACHIA'S COAL",
      "Appalachia's coal production as a percent of the US", lambda w: "Appalachia's share of US coal production", LIMIT_COAL, reproduce("appalachia_share"), consequence=2),
    C("underground_share", FAMILY, _fn("underground_share", "us_underground", "the United States"), "percent of US coal production", 1, 1, 2.0, "COAL FROM UNDERGROUND",
      "underground mines' share of US coal production", lambda w: "the share of US coal mined underground", LIMIT_COAL, reproduce("underground_share"), consequence=2),
    C("tons_per_employee", FAMILY, _fn("tons_per_employee", "us_tons_employee", "the United States"), "short tons per employee", 0, 1, 500.0, "COAL PER MINER",
      "US coal production over EIA's average employees at the mines", lambda w: "US coal production per mine employee",
      LIMIT_COAL + " EIA's average employees; the mix of surface and underground mines moves the figure.", reproduce("tons_per_employee"), consequence=2),
    C("power_coal_price", FAMILY, _fn("power_coal_price", "us_power_coal", "the United States"), "USD per short ton", 2, 1, 1.0, "WHAT POWER PLANTS PAY FOR COAL",
      "the average delivered price of coal to the electric power sector", lambda w: "the average delivered price of coal to US power plants",
      LIMIT_COAL + " Nominal dollars a short ton, not a Btu: a ton of Wyoming coal holds less heat than a ton of Appalachian.", reproduce("power_coal_price"), consequence=2),
    C("us_origin_uranium", FAMILY, _fn("us_origin_uranium", "us_uranium_origin", "the United States"), "percent of uranium purchased", 1, 1, 2.0, "URANIUM OF US ORIGIN",
      "the uranium of US origin as a percent of all the uranium the owners and operators of US reactors bought",
      lambda w: "the share of the uranium bought for US reactors that was of US origin", LIMIT_U, reproduce("us_origin_uranium"), first_words="the first year EIA's report holds", consequence=3),
    C("uranium_price", FAMILY, _fn("uranium_price", "us_uranium_price", "the United States"), "USD per pound U3O8e", 2, 1, 2.0, "WHAT US REACTORS PAY FOR URANIUM",
      "the weighted average price of the uranium the owners and operators of US reactors bought", lambda w: "the average price US reactor owners paid for uranium",
      LIMIT_U + " Nominal dollars, long-term and spot contracts together.", reproduce("uranium_price"), first_words="the first year EIA's report holds", consequence=3),
    C("spot_uranium_share", FAMILY, _fn("spot_uranium_share", "us_uranium_spot", "the United States"), "percent of uranium purchased", 1, 1, 3.0, "URANIUM BOUGHT SPOT",
      "spot contracts' share of the uranium the owners and operators of US reactors bought", lambda w: "the spot market's share of the uranium bought for US reactors",
      LIMIT_U, reproduce("spot_uranium_share"), first_words="the first year EIA's report holds", consequence=2),
    C("us_enrichment_share", FAMILY, _fn("us_enrichment_share", "us_enrich_origin", "the United States"), "percent of enrichment services", 1, 1, 2.0, "ENRICHMENT OF US ORIGIN",
      "enrichment of US origin as a percent of the enrichment services bought for US reactors",
      lambda w: "the share of the enrichment bought for US reactors that was done in the US", LIMIT_U + " Separative work units (SWU).",
      reproduce("us_enrichment_share"), first_words="the first year EIA's report holds", consequence=3),
]


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt, coal and uranium (chain 166)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--replace", action="store_true", help="correct the open drafts of the same claims in place")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    cands = [P for P in CANDIDATES if not a.only or P["name"] == a.only]
    builder.run(FAMILY, cands, a.in_dir, dry_run=not a.load, replace=a.replace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
