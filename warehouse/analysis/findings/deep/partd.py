#!/usr/bin/env python3
"""The findings hunt of chain 502, part D: the families with the fewest drafts, their largest unread tables, session 8208.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md (part D: chain 164's families with
the fewest drafts, emissions_climate 7, coal_uranium_metals 8, gas 11, read from the largest public tables no draft had
read, runs/c502/unread.py). Each candidate writes into its family's folder.

    ghg_power_state     epa_ghgrp_facility_emissions: the direct emissions EPA's reporting facilities in the power plant
                        sector reported, by state (million t CO2e)
    ghg_onshore_basin   the same table: the emissions reported for onshore oil and gas production, by basin
    coal_basin_share    eia_coal_receipts_annual: a basin's share of the coal power plants received (by tons)
    coal_mode_share     the same table: a transport mode's share of the coal received
    coal_sulfur         the same table: the tonnage-weighted sulfur content of the coal received (percent)
    gas_net_receipts    eia_gas_interstate_annual: a state's net interstate receipts of natural gas (Bcf; negative: it
                        sent more to other states than it received)

    python warehouse/analysis/findings/deep/partd.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/partd.py --load
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

STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "the District of Columbia",
          "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
          "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
          "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
          "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
          "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}
CTX = {}


def ghg(in_dir):
    def build():
        d = h.read("epa_ghgrp_facility_emissions", in_dir, ["entity", "variable", "ts_utc", "value", "geo", "x_sectors", "x_basin"], ["value"])
        d["year"] = d["ts_utc"].str[:4].astype(int)
        return d.dropna(subset=["value"])
    return hm._cached(("c502_ghg", in_dir), build)


def ghg_power_state(in_dir=None):
    d = ghg(in_dir)
    d = d[(d["variable"] == "emissions_direct") & d["x_sectors"].str.contains("Power Plants", regex=False)]
    d = d[d["geo"].str.match(r"^US-[A-Z]{2}$")]
    rows, tabs = [], {}
    for st, g in d.groupby(d["geo"].str[3:]):
        if st not in STATES:
            continue
        k = f"ghgpp_{st.lower()}"
        for y, s in g.groupby("year"):
            rows.append(hm._row(k, f"the power plants of {STATES[st]} that report to EPA", y, float(s["value"].sum() / 1e6), 1))
        tabs[k] = ["epa_ghgrp_facility_emissions"]
    return {"rows": rows, "tables": tabs}


def ghg_onshore_basin(in_dir=None):
    d = ghg(in_dir)
    d = d[(d["variable"] == "emissions_onshore_production") & (d["x_basin"] != "")]
    rows, tabs = [], {}
    for b, g in d.groupby("x_basin"):
        k = "ghgon_" + b.split(" - ")[0].lower()
        for y, s in g.groupby("year"):
            rows.append(hm._row(k, f"onshore oil and gas production in the {b.split(' - ', 1)[-1]}", y, float(s["value"].sum() / 1e6), 1))
        tabs[k] = ["epa_ghgrp_facility_emissions"]
    return {"rows": rows, "tables": tabs}


def coal(in_dir):
    def build():
        d = h.read("eia_coal_receipts_annual", in_dir, ["entity", "variable", "ts_utc", "value", "x_mine_basin", "x_transport_mode"], ["value"],
                   keep=lambda c: c["variable"].isin(["quantity", "sulfur_content"]))
        w = d.pivot_table(index=["entity", "ts_utc", "x_mine_basin", "x_transport_mode"], columns="variable", values="value", aggfunc="first").reset_index()
        w["year"] = w["ts_utc"].str[:4].astype(int)
        return w.dropna(subset=["quantity"])
    return hm._cached(("c502_coal", in_dir), build)


def _share(col, keep, prefix, words_fn):
    def f(in_dir=None):
        d = coal(in_dir)
        tot = d.groupby("year")["quantity"].sum()
        rows, tabs = [], {}
        for v, g in d.groupby(col):
            if v not in keep:
                continue
            k = prefix + v.lower().replace(" ", "_").replace("/", "_")
            by = g.groupby("year")["quantity"].sum()
            for y, q in by.items():
                rows.append(hm._row(k, words_fn(v), y, float(q / tot[y] * 100), 1))
            tabs[k] = ["eia_coal_receipts_annual"]
        return {"rows": rows, "tables": tabs}
    return f


BASINS = {"Powder River Basin", "Illinois Basin", "Appalachia Northern", "Appalachia Central", "Uinta Basin", "Other Western", "Other Interior"}
MODES = {"Rail", "River", "Truck", "Tramway/Conveyor"}
coal_basin_share = _share("x_mine_basin", BASINS, "cb_", lambda v: f"coal from the {v} (EIA's mine basin)" if "Basin" in v else f"coal from {v} (EIA's mine basin)")
coal_mode_share = _share("x_transport_mode", MODES, "cm_", lambda v: f"coal delivered by {v.lower().replace('tramway/conveyor', 'tramway or conveyor')}")


def coal_sulfur(in_dir=None):
    d = coal(in_dir).dropna(subset=["sulfur_content"])
    rows = [hm._row("cs_us", "the coal US power plants received", y, float((s["sulfur_content"] * s["quantity"]).sum() / s["quantity"].sum()), 1) for y, s in d.groupby("year")]
    return {"rows": rows, "tables": {"cs_us": ["eia_coal_receipts_annual"]}}


def gas_net_receipts(in_dir=None):
    d = h.read("eia_gas_interstate_annual", in_dir, ["entity", "variable", "ts_utc", "value"], ["value"], keep=lambda c: (c["variable"] == "net_receipts") & c["entity"].str.endswith("-Z0S"))
    d = d.dropna(subset=["value"])
    rows, tabs = [], {}
    for e, g in d.groupby("entity"):
        code = e.split(":")[-1].split("-")[0]
        if not (code.startswith("S") and code[1:] in STATES):
            continue
        st = code[1:]
        k = f"gn_{st.lower()}"
        for _, r in g.iterrows():
            rows.append(hm._row(k, STATES[st], int(r["ts_utc"][:4]), float(r["value"] / 1000), 1))
        tabs[k] = ["eia_gas_interstate_annual"]
    return {"rows": rows, "tables": tabs}


# ---------------------------------------------------------------------------------------------------------------------
# the reproduction scripts
# ---------------------------------------------------------------------------------------------------------------------
def reproduce_py(name, region):
    if name in ("ghg_power_state", "ghg_onshore_basin"):
        if name == "ghg_power_state":
            st = region.split("_")[1].upper()
            f = f"d = d[(d['variable'] == 'emissions_direct') & d['x_sectors'].str.contains('Power Plants', regex=False) & (d['geo'] == 'US-{st}')]\n"
            what = f"The direct emissions (million t CO2e) of the power plant sector's reporting facilities in {STATES[st]}, by year."
        else:
            code = region.split("_")[1]
            f = f"d = d[(d['variable'] == 'emissions_onshore_production') & d['x_basin'].str.lower().str.startswith('{code} - ')]\n"
            what = f"The emissions (million t CO2e) reported for onshore oil and gas production in basin {code.upper()}, by year."
        body = ("d = read(sys.argv[1], ['variable', 'ts_utc', 'value', 'geo', 'x_sectors', 'x_basin'])\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['value'])\n"
                + f + "for y, s in d.groupby(d['ts_utc'].str[:4]):\n    print(y, round(float(s['value'].sum() / 1e6), 6), 1)\n")
        return h.py_doc(name, region, ["epa_ghgrp_facility_emissions"], what) + h.PY_READ + body
    if name.startswith("coal_"):
        head = ("d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value', 'x_mine_basin', 'x_transport_mode'])\nd = d[d['variable'].isin(['quantity', 'sulfur_content'])].copy()\n"
                "d['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                "w = d.pivot_table(index=['entity', 'ts_utc', 'x_mine_basin', 'x_transport_mode'], columns='variable', values='value', aggfunc='first').reset_index()\n"
                "w = w.dropna(subset=['quantity'])\nw['year'] = w['ts_utc'].str[:4].astype(int)\n")
        if name == "coal_sulfur":
            body = head + "w = w.dropna(subset=['sulfur_content'])\nfor y, s in w.groupby('year'):\n    print(y, round(float((s['sulfur_content'] * s['quantity']).sum() / s['quantity'].sum()), 6), 1)\n"
            what = "The tonnage-weighted sulfur content (percent) of the coal US power plants received, by year."
        else:
            col = "x_mine_basin" if name == "coal_basin_share" else "x_transport_mode"
            pool = BASINS if name == "coal_basin_share" else MODES
            v = next(x for x in pool if region.endswith(x.lower().replace(" ", "_").replace("/", "_")))
            body = head + f"tot = w.groupby('year')['quantity'].sum()\nby = w[w['{col}'] == {v!r}].groupby('year')['quantity'].sum()\nfor y, q in by.items():\n    print(y, round(float(q / tot[y] * 100), 6), 1)\n"
            what = f"The share (percent, by tons) of the coal US power plants received with {col} {v}, by year."
        return h.py_doc(name, region, ["eia_coal_receipts_annual"], what) + h.PY_READ + body
    st = region.split("_")[1].upper()
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['variable'] == 'net_receipts') & d['entity'].str.endswith(':S{st}-Z0S')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nfor _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():\n    print(int(r['ts_utc'][:4]), round(float(r['value'] / 1000), 6), 1)\n")
    return h.py_doc(name, region, ["eia_gas_interstate_annual"], f"{STATES[st]}'s net interstate receipts of natural gas (Bcf), by year.") + h.PY_READ + body


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
            "clear all"]
    if name in ("ghg_power_state", "ghg_onshore_basin"):
        lines = head + ['import delimited "epa_ghgrp_facility_emissions.csv", varnames(1) stringcols(_all) clear']
        if name == "ghg_power_state":
            st = region.split("_")[1].upper()
            lines += [f'keep if variable == "emissions_direct" & strpos(x_sectors, "Power Plants") > 0 & geo == "US-{st}"']
        else:
            code = region.split("_")[1]
            lines += [f'keep if variable == "emissions_onshore_production" & lower(substr(x_basin, 1, {len(code) + 3})) == "{code} - "']
        lines += ["destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", "collapse (sum) measure = value, by(year)",
                  "replace measure = measure / 1000000", "generate byte n = 1"]
    elif name.startswith("coal_"):
        lines = head + ['import delimited "eia_coal_receipts_annual.csv", varnames(1) stringcols(_all) clear', 'keep if variable == "quantity" | variable == "sulfur_content"',
                        "keep entity ts_utc x_mine_basin x_transport_mode variable value", "destring value, replace force",
                        "reshape wide value, i(entity ts_utc x_mine_basin x_transport_mode) j(variable) string", "drop if missing(valuequantity)",
                        "generate int year = real(substr(ts_utc, 1, 4))"]
        if name == "coal_sulfur":
            lines += ["drop if missing(valuesulfur_content)", "generate double ws = valuesulfur_content * valuequantity", "collapse (sum) ws = ws (sum) q = valuequantity, by(year)",
                      "generate double measure = ws / q", "generate byte n = 1"]
        else:
            col = "x_mine_basin" if name == "coal_basin_share" else "x_transport_mode"
            pool = BASINS if name == "coal_basin_share" else MODES
            v = next(x for x in pool if region.endswith(x.lower().replace(" ", "_").replace("/", "_")))
            lines += [f'generate double mine = valuequantity * ({col} == "{v}")', "collapse (sum) mine = mine (sum) q = valuequantity, by(year)",
                      "generate double measure = 100 * mine / q", "generate byte n = 1"]
    else:
        st = region.split("_")[1].upper()
        lines = head + ['import delimited "eia_gas_interstate_annual.csv", varnames(1) stringcols(_all) clear',
                        f'keep if variable == "net_receipts" & substr(entity, -8, 8) == ":S{st}-Z0S"', "keep ts_utc value", "destring value, replace force", "drop if missing(value)",
                        "generate int year = real(substr(ts_utc, 1, 4))", "generate double measure = value / 1000", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
LG = "EPA's Greenhouse Gas Reporting Program as the facilities reported it (facilities above its 25,000 t threshold); a facility that drops below it leaves the sum."
LC = "EIA's receipts of coal by power plants, mine to plant, as the table holds them; a share by tons, not by heat; shipments without a basin or mode are in the total only."
CANDIDATES = [
    C("ghg_power_state", "emissions_climate", ghg_power_state, "million t CO2e", 1, 1, 2.0, "WHAT POWER PLANTS REPORT TO EPA", "the direct emissions the state's reporting power plants reported",
      lambda w: f"the sum of the direct emissions reported by {w}", LG, reproduce("ghg_power_state"), consequence=3, first_words="the first year the ERW holds"),
    C("ghg_onshore_basin", "emissions_climate", ghg_onshore_basin, "million t CO2e", 2, 1, 0.5, "EMISSIONS FROM OIL AND GAS PRODUCTION",
      "the emissions reported for onshore oil and gas production in the basin", lambda w: f"the sum of the emissions reported for {w}", LG + " The basin is the American Association of Petroleum Geologists' province.",
      reproduce("ghg_onshore_basin"), consequence=3),
    C("coal_basin_share", "coal_uranium_metals", coal_basin_share, "percent", 1, 1, 2.0, "WHERE POWER PLANTS' COAL COMES FROM", "a basin's share of the coal power plants received",
      lambda w: f"the share of {w} in the coal US power plants received", LC, reproduce("coal_basin_share"), consequence=3),
    C("coal_mode_share", "coal_uranium_metals", coal_mode_share, "percent", 1, 1, 2.0, "HOW COAL REACHES POWER PLANTS", "a mode's share of the coal power plants received",
      lambda w: f"the share of {w} in the coal US power plants received", LC, reproduce("coal_mode_share"), consequence=2),
    C("coal_sulfur", "coal_uranium_metals", coal_sulfur, "percent sulfur", 2, 1, 0.1, "THE SULFUR IN POWER PLANTS' COAL", "the tonnage-weighted sulfur content of the coal received",
      lambda w: f"the tonnage-weighted sulfur content of {w}", LC, reproduce("coal_sulfur"), consequence=2),
    C("gas_net_receipts", "gas", gas_net_receipts, "Bcf", 0, 1, 50.0, "GAS BETWEEN STATES", "the state's net interstate receipts of natural gas",
      lambda w: f"the net of the interstate receipts and deliveries of natural gas of {w} (negative: it sent more to other states than it received)",
      "EIA's interstate movements as reported by the pipelines; a state's net receipts include gas passing through it to other states.", reproduce("gas_net_receipts"), consequence=3),
]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["max_per"] = {"ghg_power_state": 5, "ghg_onshore_basin": 4, "coal_basin_share": 4, "coal_mode_share": 2, "coal_sulfur": 1, "gas_net_receipts": 6}[_P["name"]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=22)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("part_d", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
