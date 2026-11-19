#!/usr/bin/env python3
"""The findings hunt of chain 502, part D, family demand: what each state consumes, from EIA's SEDS, session 8212.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Table eia_seds_state_energy
(public, EIA's State Energy Data System, 1990 to 2024; no draft had read it): each state's consumption by source and sector.

    seds_total        total energy consumption (TBtu, series TETCB)
    seds_elec_comm    electricity sold to the commercial sector (TWh; ESCCB in TBtu over 3.412)
    seds_elec_ind     electricity sold to the industrial sector (TWh; ESICB)
    seds_gas_power    natural gas consumed by the electric power sector (TBtu, NGEIB)
    seds_renew_share  renewable energy's share of total energy consumption (percent, RETCB over TETCB)

Texas's and the United States' commercial electricity are chain 164's drafts (retail sales to the commercial sector) and
are folded here.

    python warehouse/analysis/findings/deep/seds502.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/seds502.py --load
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
import partd  # noqa: E402

FAMILY = "demand"
TBTU_PER_TWH = 3.412
SERIES = {"seds_total": ("TETCB", None), "seds_elec_comm": ("ESCCB", TBTU_PER_TWH), "seds_elec_ind": ("ESICB", TBTU_PER_TWH), "seds_gas_power": ("NGEIB", None)}
SKIP = {("seds_elec_comm", "sd_tx"), ("seds_elec_comm", "sd_us")}
CTX = {}


def seds(in_dir):
    def build():
        d = h.read("eia_seds_state_energy", in_dir, ["entity", "ts_utc", "value"], ["value"])
        d["series"], d["st"] = d["entity"].str.split(":").str[1], d["entity"].str.split(":").str[2]
        d["year"] = d["ts_utc"].str[:4].astype(int)
        return d.dropna(subset=["value"])
    return hm._cached(("c502_seds", in_dir), build)


def place(st):
    return "the United States" if st == "US" else partd.STATES.get(st, st)


def _series(name):
    code, div = SERIES[name]

    def f(in_dir=None):
        d = seds(in_dir)
        d = d[d["series"] == code]
        rows, tabs = [], {}
        for st, g in d.groupby("st"):
            if st != "US" and st not in partd.STATES:
                continue
            k = f"sd_{st.lower()}"
            if (name, k) in SKIP:
                continue
            for _, r in g.iterrows():
                rows.append(hm._row(k, place(st), int(r["year"]), float(r["value"] / div if div else r["value"]), 1))
            tabs[k] = ["eia_seds_state_energy"]
        return {"rows": rows, "tables": tabs}
    return f


seds_total, seds_elec_comm, seds_elec_ind, seds_gas_power = (_series(n) for n in SERIES)


def seds_renew_share(in_dir=None):
    d = seds(in_dir)
    w = d[d["series"].isin(["RETCB", "TETCB"])].pivot_table(index=["st", "year"], columns="series", values="value", aggfunc="first").dropna().reset_index()
    rows, tabs = [], {}
    for st, g in w.groupby("st"):
        if st != "US" and st not in partd.STATES:
            continue
        k = f"sd_{st.lower()}"
        for _, r in g.iterrows():
            if r["TETCB"] > 0:
                rows.append(hm._row(k, place(st), int(r["year"]), float(r["RETCB"] / r["TETCB"] * 100), 1))
        tabs[k] = ["eia_seds_state_energy"]
    return {"rows": rows, "tables": tabs}


def reproduce_py(name, region):
    st = region.split("_")[1].upper()
    if name == "seds_renew_share":
        body = (f"d = read(sys.argv[1], ['entity', 'ts_utc', 'value'])\nd = d[d['entity'].isin(['eia_seds:RETCB:{st}', 'eia_seds:TETCB:{st}'])].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                "w = d.pivot_table(index='ts_utc', columns='entity', values='value', aggfunc='first').dropna()\nfor ts, r in w.iterrows():\n"
                f"    if r['eia_seds:TETCB:{st}'] > 0:\n        print(int(ts[:4]), round(float(r['eia_seds:RETCB:{st}'] / r['eia_seds:TETCB:{st}'] * 100), 6), 1)\n")
        what = f"Renewable energy's share (percent) of {st}'s total energy consumption, by year."
    else:
        code, div = SERIES[name]
        conv = f" / {div}" if div else ""
        body = (f"d = read(sys.argv[1], ['entity', 'ts_utc', 'value'])\nd = d[d['entity'] == 'eia_seds:{code}:{st}'].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                f"for _, r in d.dropna(subset=['value']).sort_values('ts_utc').iterrows():\n    print(int(r['ts_utc'][:4]), round(float(r['value']{conv}), 6), 1)\n")
        what = f"SEDS series {code} for {st}, by year" + (" (TBtu over 3.412: TWh)." if div else " (TBtu).")
    return h.py_doc(name, region, ["eia_seds_state_energy"], what) + h.PY_READ + body


def reproduce_do(name, region):
    st = region.split("_")[1].upper()
    lines = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public table eia_seds_state_energy.",
             "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
             "clear all", 'import delimited "eia_seds_state_energy.csv", varnames(1) stringcols(_all) clear']
    if name == "seds_renew_share":
        lines += [f'keep if entity == "eia_seds:RETCB:{st}" | entity == "eia_seds:TETCB:{st}"', "keep entity ts_utc value", "destring value, replace force",
                  "generate str5 code = substr(entity, 10, 5)", "drop entity", "reshape wide value, i(ts_utc) j(code) string", "drop if missing(valueRETCB) | missing(valueTETCB)",
                  "keep if valueTETCB > 0", "generate int year = real(substr(ts_utc, 1, 4))", "generate double measure = 100 * valueRETCB / valueTETCB", "generate byte n = 1"]
    else:
        code, div = SERIES[name]
        lines += [f'keep if entity == "eia_seds:{code}:{st}"', "keep ts_utc value", "destring value, replace force", "drop if missing(value)",
                  "generate int year = real(substr(ts_utc, 1, 4))", f"generate double measure = value{' / ' + str(div) if div else ''}", "generate byte n = 1"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
L = "EIA's State Energy Data System, the latest release; the newest year is revised with each release; a state's consumption, wherever the energy was produced."
CANDIDATES = [
    C("seds_total", FAMILY, seds_total, "TBtu", 0, 1, 50.0, "WHAT A STATE CONSUMES", "the state's total energy consumption",
      lambda w: f"the total energy consumption of {w}", L, reproduce("seds_total"), consequence=3),
    C("seds_elec_comm", FAMILY, seds_elec_comm, "TWh", 1, 1, 2.0, "ELECTRICITY FOR COMMERCE", "the electricity sold to the state's commercial sector",
      lambda w: f"the electricity sold to the commercial sector of {w}", L + " TBtu over 3.412 gives TWh.", reproduce("seds_elec_comm"), consequence=3),
    C("seds_elec_ind", FAMILY, seds_elec_ind, "TWh", 1, 1, 2.0, "ELECTRICITY FOR INDUSTRY", "the electricity sold to the state's industrial sector",
      lambda w: f"the electricity sold to the industrial sector of {w}", L + " TBtu over 3.412 gives TWh.", reproduce("seds_elec_ind"), consequence=3),
    C("seds_gas_power", FAMILY, seds_gas_power, "TBtu", 0, 1, 50.0, "GAS BURNED FOR POWER", "the natural gas the state's electric power sector consumed",
      lambda w: f"the natural gas consumed by the electric power sector of {w}", L, reproduce("seds_gas_power"), consequence=3),
    C("seds_renew_share", FAMILY, seds_renew_share, "percent", 1, 1, 2.0, "RENEWABLES' SHARE OF A STATE'S ENERGY", "renewable energy's share of the state's total energy consumption",
      lambda w: f"renewable energy's share of the total energy consumption of {w}", L + " Renewables as SEDS counts them, wood and biofuels included.", reproduce("seds_renew_share"), consequence=2),
]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["rank_region"] = lambda r: 1e9 if r == "sd_us" else 0.0
    _P["max_per"] = 4


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, demand (SEDS)")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=18)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("seds502", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
