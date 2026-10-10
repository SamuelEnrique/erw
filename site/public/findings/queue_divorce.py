"""Finding: "Till queue do us part." (session 170).

Berkeley Lab's Queued Up (the ERW table lbnl_interconnection_queue): of the capacity that requested interconnection in
2000 to 2020, the share withdrawn, operating, active and suspended, by technology, set against the one marriage figure
a public source gives with a definition (CDC/NCHS FastStats, quoted below). The joke bends to the data: the headline
follows the comparison the numbers allow, never the other way round.

The marriage statistic (pulled once, session 170, 3 requests of a ceiling of 5, robots and terms read first):
  CDC/NCHS FastStats "Marriage and Divorce", https://www.cdc.gov/nchs/fastats/marriage-divorce.htm, retrieved
  2026-10-09 (sha256 a9e3725e2ef3d4e6dcc8c8eb09a77fa0fd51bde29ff85f20c23f506e5da48021), "Data are for the U.S.":
  "Number of marriages: 2,041,926", "Marriage rate: 6.1 per 1,000 total population", "Number of divorces: 672,502
  (45 reporting States and D.C.)", "Divorce rate: 2.4 per 1,000 population (45 reporting States and D.C.)",
  "Sources: National Marriage and Divorce Rate Trends for 2000-2023 (data shown are provisional 2023)".
  Terms, https://www.cdc.gov/other/agencymaterials.html (sha256 213845d3cbbe12535b8d1492141e1497c91477fd4a9f9a9f96cbdce48c88d04f):
  "Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain, and
  may be freely used or reproduced without obtaining copyright permission." and "Attribution to the agency that
  developed the material must be provided in your use of the materials."
The CDC publishes crude rates per 1,000 population, not the share of marriages that end in divorce. The card
therefore compares the queue's withdrawn share with the divorce rate as a share of the marriage rate in the same
year (2.4 over 6.1), and says that this is what it is.
"""

import os

import pandas as pd

from common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, read_table

NAME = "queue_divorce"
TITLE = "TILL QUEUE DO US PART"
KIND = "visual"
INPUTS = {
    "first_year": {"label": "First request year", "default": 2000, "choices": [2000, 2005, 2010]},
    "last_year": {"label": "Last request year", "default": 2020, "choices": [2015, 2018, 2020]},
}
TABLES = ["lbnl_interconnection_queue"]
CSV_NAME = "erw_2026_queue_outcomes_technology.csv"
CDC = {"source": "CDC/NCHS FastStats, Marriage and Divorce", "url": "https://www.cdc.gov/nchs/fastats/marriage-divorce.htm",
       "retrieved": "2026-10-09", "year": "provisional 2023", "marriages": 2041926, "marriage_rate_per_1000": 6.1,
       "divorces": 672502, "divorce_rate_per_1000": 2.4, "divorce_states": "45 reporting States and D.C.",
       "definition": "crude rates per 1,000 total population in the year, marriages for the U.S. and divorces for 45 reporting States and D.C.; "
                     "not the share of marriages that end in divorce, which the CDC does not publish here"}
STATUSES = ["withdrawn", "operational", "active", "suspended", "unknown"]
STATUS_WORDS = {"withdrawn": "Withdrawn", "operational": "Operating", "active": "Active", "suspended": "Suspended", "unknown": "Unknown"}
TECH = {"Solar": "Solar", "Wind": "Wind", "Battery": "Battery", "Solar+Battery": "Solar and battery", "Gas": "Gas"}


def technology(t):
    return TECH.get(t, "Other")


def compute(params, in_dir=None):
    y0, y1 = int(params.get("first_year", 2000)), int(params.get("last_year", 2020))
    q = read_table("lbnl_interconnection_queue", in_dir, usecols=["q_year", "q_status", "type_clean", "capacity_mw", "region"])
    if q.empty:
        raise NoData("lbnl_interconnection_queue is empty")
    q = q[q["q_year"] != ""]
    q["q_year"] = q["q_year"].astype(float).astype(int)
    q = q[(q["q_year"] >= y0) & (q["q_year"] <= y1)].copy()
    q["mw"] = pd.to_numeric(q["capacity_mw"], errors="coerce")
    no_mw = int(q["mw"].isna().sum())
    q = q[q["mw"].notna()]
    q["tech"] = q["type_clean"].map(technology)
    q["status"] = q["q_status"].where(q["q_status"].isin(STATUSES), "unknown")
    rows = []
    groups = [("All technologies", q)] + [(t, g) for t, g in q.groupby("tech")]
    for name, g in groups:
        total = float(g["mw"].sum())
        r = {"technology": name, "projects": int(len(g)), "requested_gw": total / 1000.0}
        for s in STATUSES:
            mw = float(g.loc[g["status"] == s, "mw"].sum())
            r[f"{s}_gw"] = mw / 1000.0
            r[f"{s}_pct"] = (mw / total * 100.0) if total > 0 else None
        rows.append(r)
    rows.sort(key=lambda r: (r["technology"] != "All technologies", -r["requested_gw"]))
    for r in rows:
        r["cdc_marriage_rate_per_1000"] = CDC["marriage_rate_per_1000"]
        r["cdc_divorce_rate_per_1000"] = CDC["divorce_rate_per_1000"]
    meta = {"first_year": y0, "last_year": y1, "projects_without_mw": no_mw, "edition": "2026 edition (through 2025)"}
    return rows, meta


def numbers_from_rows(rows, params=None):
    allr = next(r for r in rows if r["technology"] == "All technologies")
    by = {r["technology"]: r for r in rows}
    worst = max((r for r in rows if r["technology"] != "All technologies"), key=lambda r: r["withdrawn_pct"] or 0)
    best = min((r for r in rows if r["technology"] != "All technologies"), key=lambda r: r["withdrawn_pct"] or 101)
    n = {"requested_gw": allr["requested_gw"], "projects": allr["projects"],
         "withdrawn_pct": allr["withdrawn_pct"], "operational_pct": allr["operational_pct"], "active_pct": allr["active_pct"],
         "suspended_pct": allr["suspended_pct"], "withdrawn_gw": allr["withdrawn_gw"], "operational_gw": allr["operational_gw"],
         "worst_tech": worst["technology"], "worst_withdrawn_pct": worst["withdrawn_pct"],
         "best_tech": best["technology"], "best_withdrawn_pct": best["withdrawn_pct"],
         "cdc_marriage_rate": allr["cdc_marriage_rate_per_1000"], "cdc_divorce_rate": allr["cdc_divorce_rate_per_1000"],
         "cdc_ratio_pct": allr["cdc_divorce_rate_per_1000"] / allr["cdc_marriage_rate_per_1000"] * 100.0,
         "gas_withdrawn_pct": by.get("Gas", {}).get("withdrawn_pct"), "solar_withdrawn_pct": by.get("Solar", {}).get("withdrawn_pct"),
         "wind_withdrawn_pct": by.get("Wind", {}).get("withdrawn_pct")}
    n["queue_over_cdc"] = n["withdrawn_pct"] / n["cdc_ratio_pct"]
    return n


def chart(rows):
    techs = [r["technology"] for r in rows]
    return {"kind": "stacked_bar_pct", "x": techs, "x_label": "Technology (requests of 2000 to 2020)",
            "series": [{"name": STATUS_WORDS[s], "type": "bar", "unit": "percent of MW", "values": [r[f"{s}_pct"] for r in rows],
                        "gw": [r[f"{s}_gw"] for r in rows]} for s in STATUSES],
            "requested_gw": [r["requested_gw"] for r in rows], "projects": [r["projects"] for r in rows],
            "reference": {"name": "US divorce rate over marriage rate (CDC, provisional 2023)", "value": CDC["divorce_rate_per_1000"] / CDC["marriage_rate_per_1000"] * 100.0},
            "y_left_label": "percent of requested MW"}


def card(rows, params, meta):
    n = numbers_from_rows(rows)
    y0, y1 = meta["first_year"], meta["last_year"]
    ratio = n["queue_over_cdc"]
    if n["withdrawn_pct"] > n["cdc_ratio_pct"] * 1.5:
        sub = f"The queue walks away {fmt(ratio, 1)} times as often as the altar does, on the only comparison the CDC's figures allow"
    elif n["withdrawn_pct"] > n["cdc_ratio_pct"]:
        sub = "The queue quits a little more often than marriages do, on the comparison the CDC's figures allow"
    else:
        sub = "The punchline fails: marriages end more often than queue requests do, on the CDC's crude rates"
    why = (f"Of the {fmt(n['requested_gw'], 0)} GW that asked to connect in {y0} to {y1} ({fmt(n['projects'], 0)} requests in Berkeley Lab's "
           f"Queued Up, 2026 edition), {fmt(n['withdrawn_pct'], 1)} percent was withdrawn, {fmt(n['operational_pct'], 1)} percent is operating, "
           f"{fmt(n['active_pct'], 1)} percent is still active and {fmt(n['suspended_pct'], 1)} percent suspended. {n['worst_tech']} fared worst "
           f"({fmt(n['worst_withdrawn_pct'], 1)} percent withdrawn) and {n['best_tech']} best ({fmt(n['best_withdrawn_pct'], 1)} percent). "
           f"The CDC's FastStats give a marriage rate of {n['cdc_marriage_rate']} and a divorce rate of {n['cdc_divorce_rate']} per 1,000 population "
           f"(provisional 2023; divorces from 45 reporting states and D.C.): the divorce rate is {fmt(n['cdc_ratio_pct'], 0)} percent of the marriage "
           f"rate, a crude ratio of two rates in one year, not the share of marriages that end in divorce, which the CDC does not publish there. "
           f"On that ratio the queue's {fmt(n['withdrawn_pct'], 0)} percent is {fmt(ratio, 1)} times the altar's.")
    foot = (f"Data: Berkeley Lab, Queued Up, {meta['edition']} (ERW table lbnl_interconnection_queue, retrieved 2026-10-02): every request with a "
            f"queue year {y0} to {y1} and a capacity in MW ({fmt(n['projects'], 0)} requests; {meta['projects_without_mw']} without a MW figure left out). "
            "Shares are percent of requested MW by Berkeley Lab's status (withdrawn, operational, active, suspended; unknown kept as its own "
            "share) and by its type_clean, grouped: Solar, Wind, Battery, Solar and battery, Gas, and Other (hydro, coal, nuclear, offshore wind, "
            "geothermal, wind and battery, other). Marriage: CDC/NCHS FastStats, Marriage and Divorce, retrieved 2026-10-09, provisional 2023: "
            f"{CDC['marriages']:,} marriages, {CDC['marriage_rate_per_1000']} per 1,000 total population; {CDC['divorces']:,} divorces, "
            f"{CDC['divorce_rate_per_1000']} per 1,000 population, 45 reporting states and D.C. Definition: {CDC['definition']}. "
            "Source: CDC (public domain, attribution required).")
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub, "params": {"first_year": y0, "last_year": y1},
        "inputs_words": {"first_year": str(y0), "last_year": str(y1)},
        "chart": chart(rows),
        "callouts": [
            callout("Requested capacity withdrawn", f"{y0} to {y1}", f"{fmt(n['withdrawn_pct'], 0)}% of {fmt(n['requested_gw'], 0)} GW",
                    "operating", f"{fmt(n['operational_pct'], 0)}%"),
            callout("Withdrawn, worst and best technology", n["worst_tech"], f"{fmt(n['worst_withdrawn_pct'], 0)}%", n["best_tech"], f"{fmt(n['best_withdrawn_pct'], 0)}%"),
            callout("US divorce rate over marriage rate (CDC, 2023)", "per 1,000", f"{n['cdc_divorce_rate']} / {n['cdc_marriage_rate']}", "ratio", f"{fmt(n['cdc_ratio_pct'], 0)}%"),
        ],
        "why": why, "footnote": foot, "numbers": n, "cdc": CDC,
        "source_line": "Source: Berkeley Lab Queued Up (2026 edition), ERW table lbnl_interconnection_queue; CDC/NCHS FastStats (public domain).",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       f"Rows: one per technology (and all), requests of {y0} to {y1} in Berkeley Lab's Queued Up: requested GW and the GW and percent of MW by status",
                       f"CDC/NCHS FastStats marriage and divorce rates per 1,000 population ({CDC['year']}), {CDC['url']}; sources: lbnl_interconnection_queue"],
    }


def stata(params):
    V = ["projects", "requested_gw"] + [f"{s}_gw" for s in STATUSES] + [f"{s}_pct" for s in STATUSES] + ["cdc_marriage_rate_per_1000", "cdc_divorce_rate_per_1000"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces the card's shares from {CSV_NAME}.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(1) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "gen cdc_ratio_pct = cdc_divorce_rate_per_1000 / cdc_marriage_rate_per_1000 * 100",
        "gen queue_over_cdc = withdrawn_pct / cdc_ratio_pct",
        "list technology requested_gw withdrawn_pct operational_pct active_pct suspended_pct queue_over_cdc, noobs",
    ])


SOURCE_PATH = os.path.abspath(__file__)
