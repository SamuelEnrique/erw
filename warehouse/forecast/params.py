#!/usr/bin/env python3
"""The forecast tool's generated parameters (session 4201, chain 239): deflator, sales tax, income tax, capacity factors.

Energy Research Warehouse (ERW), tool 17 (docs/methods/forecast.md). Each part reads a saved source body or a warehouse
table and writes one file in site/data/forecast/, with the source, the request that read it and the arithmetic named.
Nothing is filled: a state the source does not give is absent from the file, and the tool says so.

    .venv\\Scripts\\python.exe warehouse/forecast/params.py deflator <EIA STEO answer, series GDPDIUS, json>
    .venv\\Scripts\\python.exe warehouse/forecast/params.py sales <Tax Foundation 2026 sales tax rates page, html>
    .venv\\Scripts\\python.exe warehouse/forecast/params.py income <Tax Foundation 2026 income tax rates page, html>
    .venv\\Scripts\\python.exe warehouse/forecast/params.py cf [warehouse/output folder]

Exit 0 written, 1 the source did not read as expected (nothing written), 2 bad input.
"""

import csv
import datetime as dt
import html
import json
import os
import re
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DATA = os.path.join(ROOT, "site", "data", "forecast")
STATES = {
    "Alabama": "al", "Alaska": "ak", "Arizona": "az", "Arkansas": "ar", "California": "ca", "Colorado": "co", "Connecticut": "ct",
    "Delaware": "de", "District of Columbia": "dc", "Washington DC": "dc", "D.C.": "dc", "DC": "dc", "Florida": "fl", "Georgia": "ga", "Hawaii": "hi",
    "Idaho": "id", "Illinois": "il", "Indiana": "in", "Iowa": "ia", "Kansas": "ks", "Kentucky": "ky", "Louisiana": "la", "Maine": "me",
    "Maryland": "md", "Massachusetts": "ma", "Michigan": "mi", "Minnesota": "mn", "Mississippi": "ms", "Missouri": "mo", "Montana": "mt",
    "Nebraska": "ne", "Nevada": "nv", "New Hampshire": "nh", "New Jersey": "nj", "New Mexico": "nm", "New York": "ny",
    "North Carolina": "nc", "North Dakota": "nd", "Ohio": "oh", "Oklahoma": "ok", "Oregon": "or", "Pennsylvania": "pa",
    "Rhode Island": "ri", "South Carolina": "sc", "South Dakota": "sd", "Tennessee": "tn", "Texas": "tx", "Utah": "ut",
    "Vermont": "vt", "Virginia": "va", "Washington": "wa", "West Virginia": "wv", "Wisconsin": "wi", "Wyoming": "wy",
}
TF_NOTICE = ("Tax Foundation, licensed CC BY-NC 4.0 (https://taxfoundation.org/copyright-notice/, read 2026-11-13): materials may be "
             "reproduced for non-commercial purposes with clear attribution and the page's URL. docs/licenses.md: may be public as "
             "the ERW is today; needs permission if the ERW sells anything.")


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write(name, doc):
    os.makedirs(DATA, exist_ok=True)
    doc = {**doc, "written_at": now(), "written_by": "warehouse/forecast/params.py"}
    with open(os.path.join(DATA, name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")


def cells(row):
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]


def tables(text):
    return [[cells(r) for r in re.findall(r"<tr.*?</tr>", t, re.S)] for t in re.findall(r"<table.*?</table>", text, re.S)]


def pct(s):
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)%", s.strip())
    return round(float(m.group(1)) / 100, 6) if m else None


def money(s):
    m = re.match(r"\$([\d,]+)", s.strip())
    return float(m.group(1).replace(",", "")) if m else None


def state_of(name):
    base = re.sub(r"\s*\(.*$", "", name.lstrip("- ").strip())
    return STATES.get(base)


# ---- the deflator -------------------------------------------------------------------------------------------------
def deflator(path):
    d = json.load(open(path, encoding="utf-8"))
    rows = d["response"]["data"]
    idx = {int(r["period"]): float(r["value"]) for r in rows if r.get("seriesId", "GDPDIUS") == "GDPDIUS"}
    unit = {r.get("unit") for r in rows}
    if not {2010, 2017, 2025} <= set(idx) or unit != {"Index, 2017 = 100"}:
        return None, f"deflator: years {sorted(idx)} or unit {unit} not as expected"
    return {
        "about": "GDP implicit price deflator (Index, 2017 = 100), annual: BEA's NIPA Table 1.1.9 line as EIA's Short-Term Energy "
                 "Outlook carries it (series GDPDIUS). The forecast tool works in 2025 dollars: a figure of year y is multiplied by "
                 "index(2025) / index(y). 2026 is EIA's projection and is not used.",
        "source": "U.S. Energy Information Administration, Short-Term Energy Outlook, API v2 steo/data, series GDPDIUS (annual)",
        "source_url": "https://api.eia.gov/v2/steo/data/?frequency=annual&data[]=value&facets[seriesId][]=GDPDIUS",
        "read": "2026-11-13, chain 239 session 4200 (runs/w4/eia_requests.csv)",
        "base_year": 2025,
        "index": {str(y): v for y, v in sorted(idx.items()) if y <= 2025},
    }, None


# ---- sales tax ----------------------------------------------------------------------------------------------------
def sales(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    for tb in tables(t):
        if tb and tb[0][:4] == ["State", "State Tax Rate", "State Tax Rank", "Average Local Tax Rate"]:
            out = {}
            for r in tb[1:]:
                s = state_of(r[0])
                if not s:
                    continue
                st, loc = pct(r[1]), pct(r[3])
                if st is None or loc is None:
                    return None, f"sales: {r} did not read"
                out[s] = {"state_rate": st, "avg_local_rate": loc, "row": r[0]}
            if len(out) < 51:
                return None, f"sales: {len(out)} states read"
            return {
                "about": "State sales tax rate and population-weighted average local rate, midyear 2026 (Tax Foundation's table). "
                         "The tool applies them to the taxable share of construction spending before any exemption the state "
                         "gives generating equipment, which this table does not hold (docs/methods/forecast.md, section 5).",
                "source": "Tax Foundation, State and Local Sales Tax Rates, Midyear 2026",
                "source_url": "https://taxfoundation.org/data/all/state/2026-sales-tax-rates-midyear/",
                "read": "2026-11-13, chain 239 session 4200 (runs/w4/probe.csv request 23)",
                "license": TF_NOTICE,
                "states": dict(sorted(out.items())),
            }, None
    return None, "sales: the table was not found"


# ---- income tax ---------------------------------------------------------------------------------------------------
def income(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    for tb in tables(t):
        if not tb or not tb[0] or tb[0][0] != "State" or "Single Filer (Rates)" not in tb[0]:
            continue
        out, cur = {}, None
        for r in tb[1:]:
            if len(r) < 12:
                continue
            s = state_of(r[0])
            if not s:
                return None, f"income: row {r[0]!r} names no state"
            if not r[0].startswith("-"):
                cur = s
                notes = re.findall(r"\(([^)]*)\)", r[0])
                ded, ex = r[7], r[9]
                out[s] = {"name": re.sub(r"\s*\(.*$", "", r[0]), "footnotes": notes[0] if notes else "", "brackets": [],
                          "standard_deduction_single": money(ded), "standard_deduction_text": ded,
                          "personal_exemption_single": money(ex) if "credit" not in ex.lower() else None,
                          "personal_credit_single": money(ex) if "credit" in ex.lower() else None, "personal_exemption_text": ex}
            elif s != cur:
                return None, f"income: continuation {r[0]!r} under {cur}"
            rate = r[1].strip()
            if r[0].startswith("-") and not rate:
                continue  # the table's blank spacer row under a state
            if rate.lower() == "none":
                out[s]["none"] = True
                continue
            if re.fullmatch(r"(?i)capital gains income only", rate):
                out[s]["none"] = True  # no tax on wages (Washington taxes capital gains only)
                out[s]["none_text"] = rate
                continue
            p, b = pct(rate), money(r[3])
            if p is None or b is None:
                return None, f"income: {r[0]} rate {r[1]!r} bracket {r[3]!r} did not read"
            out[s]["brackets"].append({"over_usd": b, "rate": p})
        for s, v in out.items():
            v["brackets"].sort(key=lambda x: x["over_usd"])
            if not v.get("none") and not v["brackets"]:
                return None, f"income: {s} has no bracket"
            if v["brackets"] and v["brackets"][0]["over_usd"] > 0:
                # the table starts the first rate above a threshold (Ohio: 2.75% over USD 26,050): income below it is untaxed
                v["brackets"].insert(0, {"over_usd": 0.0, "rate": 0.0, "implied": "below the table's first threshold"})
        if len(out) < 51:
            return None, f"income: {len(out)} states read"
        return {
            "about": "State individual income tax for a single filer, 2026 (Tax Foundation's table as of February 2026): each "
                     "bracket's rate over its threshold, the standard deduction and the personal exemption or credit. The tool "
                     "taxes each job's average earnings as one single filer's wages (docs/methods/forecast.md, section 6). The "
                     "table's footnotes (recapture, phase-outs, local income taxes) are not modeled; each state's footnote letters "
                     "are kept.",
            "source": "Tax Foundation, State Individual Income Tax Rates and Brackets, 2026",
            "source_url": "https://taxfoundation.org/data/all/state/state-income-tax-rates-2026/",
            "read": "2026-11-13, chain 239 session 4200 (runs/w4/probe.csv request 24)",
            "license": TF_NOTICE,
            "states": dict(sorted(out.items())),
        }, None
    return None, "income: the table was not found"


# ---- capacity factors ---------------------------------------------------------------------------------------------
def rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def cf(folder):
    plants = {r["entity_id"].split(":")[-1]: r["x_state"].lower() for r in rows(os.path.join(folder, "eia860_plants_annual.csv"))}
    wind, solar, ilr = {}, {}, {}
    for r in rows(os.path.join(folder, "lbnl_wind_capacity_factors.csv")):
        pid = r["node"].replace("EIA plant ", "").strip()
        if r["variable"] != "capacity_factor" or not r["ts_utc"].startswith("2025") or not r["x_cod"]:
            continue
        cod = int(r["x_cod"][:4])  # a plant built in phases reads "2002-03": its first year
        if 2019 <= cod <= 2024 and pid in plants:
            wind.setdefault(plants[pid], []).append(float(r["value"]))
    for r in rows(os.path.join(folder, "lbnl_solar_projects.csv")):
        if r["technology"] != "PV" or not r["cod_year"] or not r["cf_2024"]:
            continue
        if 2019 <= int(float(r["cod_year"])) <= 2023:
            s = (r["state"] or "").lower()
            solar.setdefault(s, []).append(float(r["cf_2024"]))
            if r["ilr"]:
                ilr.setdefault(s, []).append(float(r["ilr"]))

    def summary(d, n_min=3):
        allv = [x for v in d.values() for x in v]
        out = {s: {"median": round(statistics.median(v), 4), "plants": len(v)} for s, v in sorted(d.items()) if len(v) >= n_min}
        return out, {"median": round(statistics.median(allv), 4), "plants": len(allv)}
    w, wus = summary(wind)
    s, sus = summary(solar)
    i, ius = summary(ilr)
    if len(w) < 10 or len(s) < 10:
        return None, f"cf: {len(w)} wind states, {len(s)} solar states"
    return {
        "about": "Capacity factors for the production taxes (and the gas plant's fuel): the median plant of each state with at "
                 "least 3 plants, else the national median. Wind: 2025 capacity factor of plants with a commercial operation "
                 "year 2019 to 2024 (lbnl_wind_capacity_factors), the plant's state from EIA-860 (eia860_plants_annual). Solar "
                 "PV: 2024 capacity factor (AC) of plants with a commercial operation year 2019 to 2023 (lbnl_solar_projects), "
                 "and their inverter loading ratio (DC over AC), which converts JEDI's per-MW-DC figures to the reader's MW AC.",
        "tables": ["lbnl_wind_capacity_factors", "lbnl_solar_projects", "eia860_plants_annual"],
        "land_based_wind": {"states": w, "us": wus, "year": 2025, "cod": "2019-2024"},
        "utility_pv": {"states": s, "us": sus, "year": 2024, "cod": "2019-2023", "basis": "AC"},
        "utility_pv_ilr": {"states": i, "us": ius, "cod": "2019-2023"},
    }, None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in ("deflator", "sales", "income", "cf"):
        print(__doc__, file=sys.stderr)
        return 2
    kind = argv[0]
    arg = argv[1] if len(argv) > 1 else os.path.join(ROOT, "warehouse", "output")
    if not os.path.exists(arg):
        print(f"params: {arg} does not exist", file=sys.stderr)
        return 2
    doc, err = {"deflator": deflator, "sales": sales, "income": income, "cf": cf}[kind](arg)
    if err:
        print("params:", err, file=sys.stderr)
        return 1
    name = {"deflator": "deflator.json", "sales": "sales_tax.json", "income": "income_tax.json", "cf": "capacity_factors.json"}[kind]
    write(name, doc)
    print(f"params: {kind} written to site/data/forecast/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
