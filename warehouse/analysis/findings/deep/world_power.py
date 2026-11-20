#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, a new family "world_power": Europe's electricity by country, session 8223.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md (part D: the families with the fewest
drafts; this one had none). Table eurostat_electricity_monthly (public, Eurostat nrg_cb_em and nrg_cb_pem, monthly from
2016): each country's net production by fuel and its flows.

    eu_share_<fuel>   a fuel's share of the country's net production (percent): coal and manufactured gases (C0000),
                      natural gas (G3000), nuclear (N9000), wind (RA300), solar (RA400)
    eu_net_imports    imports less exports as a percent of the electricity available to the internal market

Years with all twelve months; the countries that produced at least 50 TWh net in 2025, and the EU's aggregate where
Eurostat publishes it (EU27_2020).

    python warehouse/analysis/findings/deep/world_power.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/world_power.py --load
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import hourly930 as h  # noqa: E402  (sets builder.CHAIN to 502)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "world_power"
MIN_TWH = 50.0
FUEL = {"eu_share_coal": ("C0000", "coal and manufactured gases"), "eu_share_gas": ("G3000", "natural gas"), "eu_share_nuclear": ("N9000", "nuclear"),
        "eu_share_wind": ("RA300", "wind"), "eu_share_solar": ("RA400", "solar")}
GEO = {"EU27_2020": "the European Union (27)", "DE": "Germany", "FR": "France", "ES": "Spain", "IT": "Italy", "PL": "Poland", "SE": "Sweden", "NO": "Norway", "TR": "Turkey",
       "UK": "the United Kingdom", "NL": "the Netherlands", "BE": "Belgium", "FI": "Finland", "AT": "Austria", "CZ": "Czechia", "PT": "Portugal", "RO": "Romania", "EL": "Greece",
       "UA": "Ukraine", "CH": "Switzerland", "DK": "Denmark", "HU": "Hungary", "BG": "Bulgaria", "SK": "Slovakia", "IE": "Ireland", "RS": "Serbia"}
CTX = {}


def data(in_dir):
    def build():
        keep = {f"net_production:{c}" for c, _ in FUEL.values()} | {"net_production:TOTAL", "flow:IMP", "flow:EXP", "flow:AIM"}
        d = h.read("eurostat_electricity_monthly", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"], keep=lambda c: c["variable"].isin(keep))
        d = d.dropna(subset=["value"])
        d["geo"] = d["entity"].str.split(":").str[1]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        g = d.groupby(["geo", "variable", "year"])["value"].agg(["sum", "size"]).reset_index()
        return g[g["size"] == 12]
    return hm._cached(("c502_eurostat", in_dir), build)


def _keep(g):
    t = g[(g["variable"] == "net_production:TOTAL") & (g["year"] == 2025)]
    return set(t[t["sum"] >= MIN_TWH * 1e6]["geo"]) | {"EU27_2020"}


def _share(name):
    code = FUEL[name][0]

    def f(in_dir=None):
        g = data(in_dir)
        keep = _keep(g)
        w = g[g["geo"].isin(keep)].pivot_table(index=["geo", "year"], columns="variable", values="sum").reset_index()
        rows, tabs = [], {}
        col = f"net_production:{code}"
        if col not in w:
            return {"rows": [], "tables": {}}
        for geo, x in w.dropna(subset=[col, "net_production:TOTAL"]).groupby("geo"):
            k = f"eu_{geo.lower()}"
            for _, r in x.iterrows():
                if r["net_production:TOTAL"] > 0:
                    rows.append(hm._row(k, GEO.get(geo, geo), int(r["year"]), float(r[col] / r["net_production:TOTAL"] * 100), 12))
            tabs[k] = ["eurostat_electricity_monthly"]
        return {"rows": rows, "tables": tabs}
    return f


def eu_net_imports(in_dir=None):
    g = data(in_dir)
    keep = _keep(g)
    w = g[g["geo"].isin(keep)].pivot_table(index=["geo", "year"], columns="variable", values="sum").reset_index()
    rows, tabs = [], {}
    for geo, x in w.dropna(subset=["flow:IMP", "flow:EXP", "flow:AIM"]).groupby("geo"):
        k = f"eu_{geo.lower()}"
        for _, r in x.iterrows():
            if r["flow:AIM"] > 0:
                rows.append(hm._row(k, GEO.get(geo, geo), int(r["year"]), float((r["flow:IMP"] - r["flow:EXP"]) / r["flow:AIM"] * 100), 12))
        tabs[k] = ["eurostat_electricity_monthly"]
    return {"rows": rows, "tables": tabs}


eu_share_coal, eu_share_gas, eu_share_nuclear, eu_share_wind, eu_share_solar = (_share(n) for n in FUEL)


def reproduce_py(name, region):
    geo = region.split("_", 1)[1].upper()
    geo = "EU27_2020" if geo == "EU27_2020" else geo
    if name == "eu_net_imports":
        vars_, expr = ["flow:IMP", "flow:EXP", "flow:AIM"], "(t['flow:IMP'] - t['flow:EXP']) / t['flow:AIM'] * 100"
    else:
        code = FUEL[name][0]
        vars_, expr = [f"net_production:{code}", "net_production:TOTAL"], f"t['net_production:{code}'] / t['net_production:TOTAL'] * 100"
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == 'eurostat_elec:{geo}') & d['variable'].isin({vars_!r})].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['value'])\nd['year'] = d['ts_utc'].str[:4].astype(int)\n"
            "g = d.groupby(['variable', 'year'])['value'].agg(['sum', 'size']).reset_index()\ng = g[g['size'] == 12]\n"
            "w = g.pivot_table(index='year', columns='variable', values='sum').dropna()\nfor y, t in w.iterrows():\n"
            f"    print(y, round(float({expr}), 6), 12)\n")
    what = ("Imports less exports as a percent of the electricity available to the internal market" if name == "eu_net_imports"
            else f"{FUEL[name][1].capitalize()}'s share (percent) of net production") + f", {geo}, years with all twelve months of every figure."
    return h.py_doc(name, region, ["eurostat_electricity_monthly"], what) + h.PY_READ + body


def reproduce_do(name, region):
    geo = region.split("_", 1)[1].upper()
    if name == "eu_net_imports":
        vars_ = ["flow:IMP", "flow:EXP", "flow:AIM"]
    else:
        vars_ = [f"net_production:{FUEL[name][0]}", "net_production:TOTAL"]
    cond = " | ".join(f'variable == "{v}"' for v in vars_)
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table eurostat_electricity_monthly.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "eurostat_electricity_monthly.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "eurostat_elec:{geo}"', f"keep if {cond}",
             "keep variable ts_utc value", "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))",
             "generate str12 v = subinstr(subinstr(variable, \"net_production:\", \"np_\", 1), \"flow:\", \"fl_\", 1)",
             "collapse (sum) s = value (count) months = value, by(v year)", "keep if months == 12", "drop months", "reshape wide s, i(year) j(v) string"]
    if name == "eu_net_imports":
        lines += ["drop if missing(sfl_IMP) | missing(sfl_EXP) | missing(sfl_AIM)", "generate double measure = 100 * (sfl_IMP - sfl_EXP) / sfl_AIM"]
    else:
        c = FUEL[name][0]
        lines += [f"drop if missing(snp_{c}) | missing(snp_TOTAL)", f"generate double measure = 100 * snp_{c} / snp_TOTAL"]
    lines += ["generate byte n = 12", "sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = "Eurostat's monthly electricity statistics as published, the latest months provisional; net production; a year counts with all twelve months of every figure."
CANDIDATES = [C(n, FAMILY, fn, "percent", 1, 12, 3.0, f"EUROPE'S ELECTRICITY: {FUEL[n][1].upper()}", f"{FUEL[n][1]}'s share of the country's net production",
                (lambda wd: (lambda w: f"the share of {wd} in the net electricity production of {w}"))(FUEL[n][1]), L, reproduce(n), consequence=2)
              for n, fn in (("eu_share_coal", eu_share_coal), ("eu_share_gas", eu_share_gas), ("eu_share_nuclear", eu_share_nuclear), ("eu_share_wind", eu_share_wind),
                            ("eu_share_solar", eu_share_solar))]
CANDIDATES.append(C("eu_net_imports", FAMILY, eu_net_imports, "percent", 1, 12, 3.0, "EUROPE'S ELECTRICITY: NET IMPORTS",
                    "imports less exports as a percent of the electricity available", lambda w: f"the net imports of electricity of {w} as a percent of the electricity available to it",
                    L + " A negative figure is a year of net exports.", reproduce("eu_net_imports"), consequence=2))
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["rank_region"] = lambda r: 1e9 if r == "eu_eu27_2020" else 0.0
    _P["max_per"] = 3


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, Europe's electricity")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=16)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run(FAMILY, CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
