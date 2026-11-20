#!/usr/bin/env python3
"""The findings hunt of chain 502, part D: earthquakes in the oil and gas states, and reactors' power, session 8221.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. Two public tables no draft had read:

    usgs_comcat_earthquakes_south_central (USGS ComCat, 2010 on, magnitude 2.5 and above, the box of Oklahoma, Kansas,
    Texas and New Mexico), family other_us:
        quakes_m3      the year's earthquakes of magnitude 3.0 and above whose place USGS names in the state
    nrc_reactor_status (the NRC's daily power reactor status, 2020 on), family markets_operations:
        reactor_power  the year's mean daily power level (percent of full power), the US fleet (all reactors' days) and
                       each reactor

No finding here says why the earthquakes came; the counts are what the catalog holds.

    python warehouse/analysis/findings/deep/misc502.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/misc502.py --load
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

MIN_MAG = 3.0
QSTATES = ["Oklahoma", "Texas", "New Mexico", "Kansas", "Colorado"]
CTX = {}


def quakes_m3(in_dir=None):
    d = h.read("usgs_comcat_earthquakes_south_central", in_dir, ["event_id", "event_date", "x_magnitude", "x_place_state"], ["x_magnitude"])
    d = d.dropna(subset=["x_magnitude"])
    d = d[d["x_magnitude"] >= MIN_MAG].drop_duplicates("event_id")
    d["year"] = d["event_date"].str[:4].astype(int)
    rows, tabs = [], {}
    for st in QSTATES:
        g = d[d["x_place_state"] == st]
        k = "eq_" + st.lower().replace(" ", "_")
        by = g.groupby("year").size()
        for y in range(2010, 2027):
            rows.append(hm._row(k, st, y, float(by.get(y, 0)), 1))
        tabs[k] = ["usgs_comcat_earthquakes_south_central"]
    return {"rows": rows, "tables": tabs}


def reactor_power(in_dir=None):
    d = h.read("nrc_reactor_status", in_dir, ["entity", "variable", "ts_utc", "value", "node"], ["value"], keep=lambda c: c["variable"] == "power_pct")
    d = d.dropna(subset=["value"])
    d["year"] = d["ts_utc"].str[:4].astype(int)
    rows, tabs = [], {"rp_us": ["nrc_reactor_status"]}
    for y, s in d.groupby("year"):
        rows.append(hm._row("rp_us", "the US reactor fleet", y, float(s["value"].mean()), len(s) / max(1, s["entity"].nunique())))
    last = d.groupby("entity")["year"].max()
    for e, g in d.groupby("entity"):
        if last[e] < 2025 or e == "nrc:sequoyah_2":    # Sequoyah 2 is chain 164's draft of reactor outage days (nuc-6152-2)
            continue
        k = "rp_" + e.split(":")[1]
        for y, s in g.groupby("year"):
            rows.append(hm._row(k, f"the {g['node'].iloc[-1]} reactor", y, float(s["value"].mean()), len(s)))
        tabs[k] = ["nrc_reactor_status"]
    return {"rows": rows, "tables": tabs}


def reproduce_py(name, region):
    if name == "quakes_m3":
        st = next(s for s in QSTATES if "eq_" + s.lower().replace(" ", "_") == region)
        body = (f"d = read(sys.argv[1], ['event_id', 'event_date', 'x_magnitude', 'x_place_state'])\nd['m'] = pd.to_numeric(d['x_magnitude'], errors='coerce')\n"
                f"d = d[(d['m'] >= {MIN_MAG}) & (d['x_place_state'] == '{st}')].drop_duplicates('event_id')\nby = d.groupby(d['event_date'].str[:4].astype(int)).size()\n"
                "for y in range(2010, 2027):\n    print(y, int(by.get(y, 0)), 1)\n")
        return h.py_doc(name, region, ["usgs_comcat_earthquakes_south_central"], f"The earthquakes of magnitude {MIN_MAG} and above whose place USGS names in {st}, by year.") + h.PY_READ + body
    if region == "rp_us":
        body = ("d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[d['variable'] == 'power_pct'].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\n"
                "d = d.dropna(subset=['value'])\nfor y, s in d.groupby(d['ts_utc'].str[:4]):\n    print(y, round(float(s['value'].mean()), 6), round(len(s) / s['entity'].nunique(), 6))\n")
        return h.py_doc(name, region, ["nrc_reactor_status"], "The mean daily power level (percent) over all US reactors' days, by year; the third figure is the days a reactor.") + h.PY_READ + body
    e = "nrc:" + region.split("_", 1)[1]
    body = (f"d = read(sys.argv[1], ['entity', 'variable', 'ts_utc', 'value'])\nd = d[(d['entity'] == '{e}') & (d['variable'] == 'power_pct')].copy()\n"
            "d['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['value'])\nfor y, s in d.groupby(d['ts_utc'].str[:4]):\n    print(y, round(float(s['value'].mean()), 6), len(s))\n")
    return h.py_doc(name, region, ["nrc_reactor_status"], f"The mean daily power level (percent) of {e}, by year.") + h.PY_READ + body


def reproduce_do(name, region):
    head = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce candidate {name} for {region} from the ERW's public tables.",
            "* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
            "clear all"]
    if name == "quakes_m3":
        st = next(s for s in QSTATES if "eq_" + s.lower().replace(" ", "_") == region)
        lines = head + ['import delimited "usgs_comcat_earthquakes_south_central.csv", varnames(1) stringcols(_all) clear', "destring x_magnitude, replace force",
                        f'keep if x_magnitude >= {MIN_MAG} & x_place_state == "{st}"', "duplicates drop event_id, force", "generate int year = real(substr(event_date, 1, 4))",
                        "generate byte one = 1", "collapse (sum) measure = one, by(year)", "generate byte n = 1",
                        "* A year with no earthquake is a year of zero, as the Python prints it."]
    elif region == "rp_us":
        lines = head + ['import delimited "nrc_reactor_status.csv", varnames(1) stringcols(_all) clear', 'keep if variable == "power_pct"', "keep entity ts_utc value",
                        "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", "bysort year entity: generate byte firstr = _n == 1",
                        "collapse (mean) measure = value (count) days = value (sum) reactors = firstr, by(year)", "generate double n = days / reactors"]
    else:
        e = "nrc:" + region.split("_", 1)[1]
        lines = head + ['import delimited "nrc_reactor_status.csv", varnames(1) stringcols(_all) clear', f'keep if entity == "{e}" & variable == "power_pct"', "keep ts_utc value",
                        "destring value, replace force", "drop if missing(value)", "generate int year = real(substr(ts_utc, 1, 4))", "collapse (mean) measure = value (count) n = value, by(year)"]
    lines += ["sort year", "list year measure n, noobs"]
    return common.do_file(lines)


def reproduce(name):
    return lambda region: {"py": reproduce_py(name, region), "do": reproduce_do(name, region)}


C = builder.candidate
CANDIDATES = [
    C("quakes_m3", "other_us", quakes_m3, "earthquakes", 0, 1, 10.0, "EARTHQUAKES IN THE OIL AND GAS STATES", f"the year's earthquakes of magnitude {MIN_MAG} and above in the state",
      lambda w: f"the count of earthquakes of magnitude {MIN_MAG:g} and above that USGS places in {w}",
      "USGS's ComCat as of 23 October 2026, magnitude 2.5 and above in the box of Oklahoma, Kansas, Texas and New Mexico, by the state the catalog's place names; a count, not a cause.",
      reproduce("quakes_m3"), consequence=2),
    C("reactor_power", "markets_operations", reactor_power, "percent of full power", 1, 330, 2.0, "HOW HARD REACTORS RUN", "the year's mean daily power level",
      lambda w: f"the mean daily power level of {w}", "The NRC's daily power reactor status as reported each morning; a reactor's day at 0 percent counts, a shut reactor leaves the fleet.",
      reproduce("reactor_power"), consequence=2),
]
for _P in CANDIDATES:
    _P["rank"] = lambda c: abs(c["change"])
    _P["rank_region"] = lambda r: 1e9 if r == "rp_us" else 0.0
    _P["max_per"] = 4


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, part D, earthquakes and reactors")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=8)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    CTX["in_dir"] = a.in_dir or common.DEFAULT_IN_DIR
    builder.run("misc502", CANDIDATES, CTX["in_dir"], dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
