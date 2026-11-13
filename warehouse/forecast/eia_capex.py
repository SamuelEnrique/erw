#!/usr/bin/env python3
"""EIA's capital cost by state and city for four technologies (session 4201, chain 239: the forecast tool).

Energy Research Warehouse (ERW), tool 17. The forecast model's default capital cost is the overnight cost that EIA's
capital cost study for AEO2025 gives for the technology in the state (Sargent & Lundy for EIA, "Capital Cost and
Performance Characteristic Estimates for Utility Scale Electric Power Generating Technologies", SL-018001, Final Rev A,
6 December 2023; released 10 January 2024; 2023 dollars), from its Appendix A, "Labor location-based cost
adjustments": for each technology, one row per state and city with the base cost, the location variation and the total
location project cost in $/kW. A state with several cities gets each city, and the state's default is their plain mean
(docs/methods/forecast.md, section 2). Where EIA writes N/A (geothermal outside the states with a resource), the state is
listed under not_given and no cost is held.

    pdftotext -layout capital_cost_AEO2025.pdf cap.txt
    .venv\\Scripts\\python.exe warehouse/forecast/eia_capex.py cap.txt

Writes site/data/forecast/eia_capex.json. Exit 0 written, 1 a table did not read as expected (nothing written), 2 bad input.
"""

import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "site", "data", "forecast", "eia_capex.json")
SOURCE_URL = "https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2025.pdf"
# the forecast tool's technology -> (the appendix table, its title's words, the case's base $/kW, the case's net MW, its basis)
TABLES = {
    "land_based_wind": ("1-13", "Onshore Wind - Large Plant Footprint: Great Plains Region", 1489, 200, "kW net (AC)"),
    "utility_pv": ("1-16", "Solar PV w/ Single Axis Tracking", 1502, 150, "kW AC (150 MWAC)"),
    "natural_gas": ("1-5", "Combined-Cycle 2x2x1", 868, 1227, "kW net"),
    "geothermal": ("1-11", "Geothermal", 3963, 50, "kW net (binary cycle, 50 MW net)"),
}
STATES = {
    "Alabama": "al", "Alaska": "ak", "Arizona": "az", "Arkansas": "ar", "California": "ca", "Colorado": "co", "Connecticut": "ct",
    "Delaware": "de", "District of Columbia": "dc", "Florida": "fl", "Georgia": "ga", "Hawaii": "hi", "Idaho": "id", "Illinois": "il",
    "Indiana": "in", "Iowa": "ia", "Kansas": "ks", "Kentucky": "ky", "Louisiana": "la", "Maine": "me", "Maryland": "md",
    "Massachusetts": "ma", "Michigan": "mi", "Minnesota": "mn", "Mississippi": "ms", "Missouri": "mo", "Montana": "mt",
    "Nebraska": "ne", "Nevada": "nv", "New Hampshire": "nh", "New Jersey": "nj", "New Mexico": "nm", "New York": "ny",
    "North Carolina": "nc", "North Dakota": "nd", "Ohio": "oh", "Oklahoma": "ok", "Oregon": "or", "Pennsylvania": "pa",
    "Rhode Island": "ri", "South Carolina": "sc", "South Dakota": "sd", "Tennessee": "tn", "Texas": "tx", "Utah": "ut",
    "Vermont": "vt", "Virginia": "va", "Washington": "wa", "West Virginia": "wv", "Wisconsin": "wi", "Wyoming": "wy",
}
ROW = re.compile(r"^(?P<state>" + "|".join(sorted(map(re.escape, STATES), key=len, reverse=True)) + r")\s{2,}(?P<city>.+?)\s{2,}"
                 r"(?P<base>[\d,]+)\s+(?P<var>\d\.\d\d)\s+(?P<delta>\(?[\d,]+\)?)\s+(?P<total>[\d,]+)\s*$")

NA = re.compile(r"^(" + "|".join(sorted(map(re.escape, STATES), key=len, reverse=True)) + r")\s{2,}.+?\s{2,}N/A\s+N/A\s+N/A\s+N/A\s*$")


def num(s):
    s = s.replace(",", "")
    return -float(s.strip("()")) if s.startswith("(") else float(s)


def read(text):
    lines = text.splitlines()
    out, problems = {}, []
    for tech, (table, words, base, mw, basis) in TABLES.items():
        start = next((i for i, l in enumerate(lines) if re.search(rf"Table {re.escape(table)} -- Location Adjustment for {re.escape(words)}\s*$", l)), None)
        if start is None:
            problems.append(f"{tech}: Table {table} ({words}) not found")
            continue
        rows, i = [], start + 1
        while i < len(lines) and not re.search(r"Table 1-\d+ -- Location Adjustment", lines[i]):
            m = ROW.match(lines[i].strip())
            if m:
                rows.append(m)
            i += 1
        states = {}
        for m in rows:
            b, var, delta, total = num(m["base"]), float(m["var"]), num(m["delta"]), num(m["total"])
            if b != base:
                problems.append(f"{tech} {m['state']} {m['city']}: base {b}, not the case's {base}")
            if abs(b + delta - total) > 1.01:  # the report rounds each figure to the dollar
                problems.append(f"{tech} {m['state']} {m['city']}: {b} + {delta} is not {total}")
            s = states.setdefault(STATES[m["state"]], {"state": m["state"], "cities": []})
            s["cities"].append({"city": m["city"].strip(), "location_variation": var, "usd_per_kw": total})
        for s in states.values():
            s["usd_per_kw"] = round(sum(c["usd_per_kw"] for c in s["cities"]) / len(s["cities"]), 2)
        na = sorted({STATES[m.group(1)] for l in lines[start + 1:i] for m in [NA.match(l.strip())] if m})
        if len(states) + len(na) < 45 or (tech != "geothermal" and len(states) < 45):
            problems.append(f"{tech}: {len(states)} states with a cost and {len(na)} N/A read from Table {table}")
        out[tech] = {"table": f"Appendix A, Table {table}, Location Adjustment for {words}", "base_usd_per_kw": base,
                     "case_mw": mw, "basis": basis, "dollar_year": 2023, "states": dict(sorted(states.items())),
                     "not_given": [s for s in na if s not in states]}
    return out, problems


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or not os.path.exists(argv[0]):
        print("usage: eia_capex.py <pdftotext -layout output of the report>", file=sys.stderr)
        return 2
    data, problems = read(open(argv[0], encoding="utf-8", errors="replace").read())
    if problems:
        for p in problems[:20]:
            print("eia_capex:", p, file=sys.stderr)
        return 1
    doc = {
        "about": "EIA's overnight capital cost by state and city (2023 dollars, $/kW of the basis named), from the capital cost "
                 "study for AEO2025, Appendix A (labor location-based cost adjustments). A state's usd_per_kw is the plain mean "
                 "of its cities' totals. Overnight cost excludes financing during construction (the report's own words: "
                 "\"presented as an overnight cost in 2023 dollars and thus excludes allowance for funds used during construction\").",
        "source": "U.S. Energy Information Administration (Sargent & Lundy), Capital Cost and Performance Characteristic Estimates "
                  "for Utility Scale Electric Power Generating Technologies, SL-018001 Final Rev A (6 December 2023), released "
                  "10 January 2024 for AEO2025",
        "source_url": SOURCE_URL,
        "read": "2026-11-13, chain 239 session 4200 (runs/w4/probe.csv request 21)",
        "written_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "written_by": "warehouse/forecast/eia_capex.py",
        "technologies": data,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print("eia_capex: " + ", ".join(f"{t} {len(v['states'])} states" for t, v in data.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
