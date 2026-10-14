#!/usr/bin/env python3
"""CAISO's southern areas beside the SP15 hub (session 273): is the gap to the market monitor's LA Basin the hub?

Energy Research Warehouse (ERW). docs/methods/battery_stack.md, "CAISO beside its market monitor". Session 246 ran the
battery model at the SP15 hub, the market monitor's way (energy and regulation day-ahead, round trip 0.85), and got
USD 84.72 per kW for 2025 against the monitor's 77.3 for "CAISO System" and 62.6, 64.2 and 66.3 for its southern
local capacity areas (LA Basin; Big Creek/Ventura; San Diego/Imperial Valley; its Table 1.8, which reaches 111.7 in
Greater Fresno). That gap was not explained. This asks CAISO's node list which load aggregation points stand for
those areas, pulls their day-ahead prices for 2025, and runs the same model on each, beside the hub:

    python warehouse/analysis/caiso_southern_nodes.py --pull     CAISO's list of aggregated nodes (one request), then
                                                                 the day-ahead LMP of the chosen nodes for 2025, a day at
                                                                 a time (OASIS PRC_LMP through gridstatus, as the hub
                                                                 history's pull asks it), saved under warehouse/raw/
    python warehouse/analysis/caiso_southern_nodes.py            the model on each node's prices (no request)

Writes warehouse/output/analysis_internal/caiso_southern_nodes_2025.csv (USD per kW by node, energy, regulation,
total) and prints it beside the monitor's table. Not a warehouse table: an analysis, internal, for review.

The nodes. CAISO's sub load aggregation points (sub-LAPs) and its utility default LAPs are the aggregated pricing
nodes that stand for load areas: SCE's (SLAP_SCE*), SDG&E's (SLAP_SDG1) and PG&E's Fresno area (SLAP_PGF1) for the
monitor's southern areas and its highest one. Which sub-LAP lies in which local capacity area is CAISO's planning
geography, not a field of the node list: the mapping below is the ERW's, by the areas' names, and says so.
"""

import argparse
import copy
import datetime as dt
import io
import os
import sys
import zipfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402
import iso_prices as ip  # noqa: E402

YEAR = "2025"
NAME = "caiso_southern_nodes"
OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal", f"{NAME}_{YEAR}.csv")
PRICES = os.path.join(ROOT, "warehouse", "output", "analysis_internal", f"{NAME}_dam_{YEAR}.csv")
HUB = "TH_SP15_GEN-APND"
# the ERW's reading of the monitor's areas by name (Table 1.8); a node the list does not hold is dropped and said
NODES = {
    "DLAP_SCE-APND": "SCE's default LAP (all of SCE)",
    "SLAP_SCEC-APND": "SCE Core (LA Basin)",
    "SLAP_SCEW-APND": "SCE West (LA Basin)",
    "SLAP_SCNW-APND": "SCE Northwest (Big Creek/Ventura)",
    "SLAP_SCEN-APND": "SCE North (Big Creek/Ventura)",
    "SLAP_SCHD-APND": "SCE High Desert",
    "SLAP_SCLD-APND": "SCE Low Desert",
    "DLAP_SDGE-APND": "SDG&E's default LAP (San Diego/Imperial Valley)",
    "SLAP_PGF1-APND": "PG&E Fresno (Greater Fresno)",
    "DLAP_PGAE-APND": "PG&E's default LAP (all of PG&E)",
}
MONITOR = {"CAISO System": 77.3, "LA Basin": 62.6, "Big Creek/Ventura": 64.2, "San Diego/Imperial Valley": 66.3, "Greater Fresno": 111.7}
LIST_URL = ("http://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=ATL_APNODE&APnode_type=ALL&version=1"
            "&startdatetime=20250601T07:00-0000&enddatetime=20250602T07:00-0000")
CEILING = 120_000   # rows of prices this analysis may pull: 10 nodes x 8,760 hours is 87,600


def node_list(log):
    """CAISO's aggregated pricing nodes (ATL_APNODE), as a frame. One request, saved."""
    blob, _ = ip.fetch_raw(NAME, LIST_URL, log, headers={"User-Agent": "ERW energy research warehouse (https://github.com/SamuelEnrique/erw)"})
    z = zipfile.ZipFile(io.BytesIO(blob))
    return pd.read_csv(z.open(z.namelist()[0]), dtype=str, keep_default_na=False)


def pull(log):
    from gridstatus import CAISO, Markets
    lst = node_list(log)
    col = next(c for c in lst.columns if c.upper() in ("APNODE_ID", "APNODE", "NODE_ID", "PNODE_ID"))
    have = set(lst[col])
    nodes = [n for n in NODES if n in have]
    for n in NODES:
        if n not in have:
            log(f"  {n}: not in CAISO's list of aggregated nodes on 2025-06-01; left out")
    log(f"  CAISO's list: {len(lst):,} aggregated nodes; {len(nodes)} of {len(NODES)} chosen are in it")
    c = CAISO()
    frames, rows = [], 0
    for day in pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31", freq="D"):
        if rows + len(nodes) * 25 > CEILING:
            raise RuntimeError(f"{rows:,} rows pulled; the next day would pass the ceiling of {CEILING:,}")
        df = c.get_lmp(date=day, end=day + pd.Timedelta(days=1), market=Markets.DAY_AHEAD_HOURLY, locations=nodes, sleep=5)
        rows += len(df)
        frames.append(df[["Interval Start", "Location", "LMP"]])
        if day.day == 1:
            log(f"  {day:%Y-%m}: {rows:,} rows so far")
    out = pd.concat(frames, ignore_index=True)
    os.makedirs(os.path.dirname(PRICES), exist_ok=True)
    with open(PRICES, "w", encoding="utf-8", newline="") as f:
        f.write(f"# ERW analysis, internal (session 273): CAISO OASIS PRC_LMP, day-ahead, {YEAR}, the nodes of "
                f"warehouse/analysis/caiso_southern_nodes.py; retrieved {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ}; "
                "raw responses under warehouse/raw/caiso_southern_nodes/. Credit: the California ISO.\n")
        out.to_csv(f, index=False, lineterminator="\n")
    return len(out), nodes


def model(series, log=lambda s: None):
    """The model the monitor's way (energy and regulation, round trip 0.85) on one node's day-ahead prices, for YEAR:
    USD per kW of energy, regulation and the total, and the days solved."""
    m = bs.MARKETS["caiso"]
    saved = copy.deepcopy(m["products"])
    solve, check = bs.solve_day, bs.check_day
    try:
        bs.MARKETS["caiso"]["products"] = [p for p in saved if p["key"] in ("regup", "regdn")]
        bs.ALL_MARKETS["caiso"] = bs.MARKETS["caiso"]
        bs.solve_day = lambda e, r, spec, dur, **k: solve(e, r, spec, dur, **{**k, "rte": 0.85})
        bs.check_day = lambda sol, spec, dur, **k: check(sol, spec, dur, **{**k, "rte": 0.85})
        reserve = bs.as_prices(m["as_table"], bs.MARKETS["caiso"]["products"])
        days, _ = bs.build_market("caiso", {"rtm": series, "dam": series}, reserve, log, until=f"{YEAR}-12-31")
    finally:
        bs.MARKETS["caiso"]["products"] = saved
        bs.ALL_MARKETS["caiso"] = bs.MARKETS["caiso"]
        bs.solve_day, bs.check_day = solve, check
    d = {day: v for day, v in days[("dayahead", 4)].items() if day[:4] == YEAR}
    e = sum(v["energy"] for v in d.values()) / 1000
    r = sum(v.get("regup", 0.0) + v.get("regdn", 0.0) for v in d.values()) / 1000
    return round(e, 2), round(r, 2), round(e + r, 2), len(d)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pull", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    if a.pull:
        ip.RAW.open(NAME, run_id)
        n, nodes = pull(log)
        print(f"{NAME}: {n:,} rows of day-ahead prices for {len(nodes)} nodes, {YEAR}")
    p = pd.read_csv(PRICES, comment="#")
    p["ts"] = pd.to_datetime(p["Interval Start"], utc=True)
    rows = []
    hub, _ = bs.energy_prices("caiso", "dam", lambda s: None)
    rows.append(dict(node=HUB, what="the SP15 hub (the page's)", **dict(zip(("energy", "regulation", "total", "days"), model(hub)))))
    for node, what in NODES.items():
        s = p[p["Location"] == node].set_index("ts")["LMP"].sort_index()
        if s.empty:
            continue
        s = s[~s.index.duplicated()]
        rows.append(dict(node=node, what=what, **dict(zip(("energy", "regulation", "total", "days"), model(s)))))
    out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(f"# ERW analysis, internal (session 273): the battery model the market monitor's way (4 hours, energy and regulation "
                f"day-ahead, round trip 0.85) on each node's day-ahead prices of {YEAR}, USD per kW; warehouse/analysis/caiso_southern_nodes.py\n")
        out.to_csv(f, index=False, lineterminator="\n")
    print(out.to_string(index=False))
    print("the market monitor, Table 1.8 (USD per kW, 2025):", MONITOR)
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
