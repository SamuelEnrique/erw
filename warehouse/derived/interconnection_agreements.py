#!/usr/bin/env python3
"""Generation with a signed interconnection agreement, not yet operating, from Berkeley Lab's Queued Up file (session
854, chain 046): the All grids tab's headroom row "generation with a signed interconnection agreement".

Energy Research Warehouse (ERW). Two derived tables from lbnl_interconnection_queue (held; no request is made). Method:
docs/methods/interconnection_agreements.md.

    python warehouse/derived/interconnection_agreements.py                 # both tables, under the data lock
    python warehouse/derived/interconnection_agreements.py --out-dir DIR   # a trial: the tables under DIR

interconnection_agreements_signed (entities, one row a request): every request still in the queue (Berkeley Lab's
status active or suspended) whose study phase is "IA Executed" or that gives an agreement date (ia_date), and that gives
no operation date. Berkeley Lab marks a signed agreement both ways and neither covers the other (on 23 October 2026,
1,101 requests had both, 1,188 the phase only, 357 the date only); a request with either is counted. A request that
gives an operation date is left out and counted in the header.

interconnection_agreements_by_grid (series): by grid (Berkeley Lab's region: the seven ISOs, West and Southeast) and for
the U.S., the queue as the file holds it (data to the end of 2025, ts_utc 2025-01-01, freq P1Y): projects_signed and
mw_signed, and beside them active_projects and active_mw (every request still in the queue) and signed_share_pct (the
signed MW over the active MW); by grid and fuel, projects_signed and mw_signed; and by grid and the year of the agreement
(the requests that give an ia_date), projects_signed_in_year and mw_signed_in_year. Nothing is filled or estimated.
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

INPUT = "lbnl_interconnection_queue"
NAME, SUMMARY = "interconnection_agreements_signed", "interconnection_agreements_by_grid"
SOURCE = "erw:interconnection_agreements"
STILL = ("active", "suspended")
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"]
EXTRA = ["queue_id", "grid", "state", "county", "utility", "transmission_provider", "fuel", "ia_date", "ia_phase",
         "request_date", "proposed_date", "signed_by"]
SNAPSHOT_TS = "2025-01-01T00:00:00Z"   # Queued Up's 2026 edition: requests to the end of 2025


def read_table(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


def key(v):
    return "us" if v == "US" else re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_") or "unknown"


def signed(q):
    """The requests still in the queue with a signed agreement and no operation date, and the counts: (table, counts)."""
    still = q[q["status"].isin(STILL)]
    phase, date = still["ia_phase"].eq("IA Executed"), still["ia_date"].ne("")
    s = still[phase | date]
    counts = {"in the queue": len(still), "phase and date": int((phase & date).sum()), "phase only": int((phase & ~date).sum()),
              "date only": int((~phase & date).sum())}
    counts["with an operation date, left out"] = int(s["on_date"].ne("").sum())
    s = s[s["on_date"].eq("")]
    by = s["ia_phase"].eq("IA Executed").map({True: "phase", False: ""}) + s["ia_date"].ne("").map({True: "+date", False: ""})
    t = pd.DataFrame({
        "entity_id": s["entity_id"], "entity_type": "project", "name": s["name"], "geo": s["geo"], "lat": s["lat"],
        "lon": s["lon"], "capacity_mw": s["capacity_mw"], "status": s["status"], "status_date": s["ia_date"],
        "operator": s["operator"], "source": SOURCE, "source_url": s["source_url"], "retrieved_at": s["retrieved_at"],
        "vintage": s["vintage"], "queue_id": s["q_id"], "grid": s["region"], "state": s["state"], "county": s["county"],
        "utility": s["utility"], "transmission_provider": s["lbnl_entity"], "fuel": s["type_clean"], "ia_date": s["ia_date"],
        "ia_phase": s["ia_phase"], "request_date": s["q_date"], "proposed_date": s["prop_date"],
        "signed_by": by.str.lstrip("+")})
    return t.sort_values("entity_id").reset_index(drop=True), counts, still


def summary(t, still):
    t = t.assign(mw=pd.to_numeric(t["capacity_mw"], errors="coerce"))
    still = still.assign(mw=pd.to_numeric(still["capacity_mw"], errors="coerce"))
    src_url, ret = t["source_url"].iloc[0], t["retrieved_at"].iloc[0]
    rows = []

    def add(entity, node, var, ts, v, unit):
        rows.append(dict(entity=entity, variable=var, ts_utc=ts, value=round(float(v), 2), unit=unit, freq="P1Y", geo="US",
                         market="", node=node, source=SOURCE, source_url=src_url, retrieved_at=ret, vintage=""))

    grids = sorted(t["grid"].unique())
    for grid in grids + ["US"]:
        g = t if grid == "US" else t[t["grid"] == grid]
        a = still if grid == "US" else still[still["region"] == grid]
        e = f"interconnection_agreements:{key(grid)}"
        add(e, grid, "projects_signed", SNAPSHOT_TS, len(g), "count")
        add(e, grid, "mw_signed", SNAPSHOT_TS, g["mw"].sum(), "MW")
        add(e, grid, "active_projects", SNAPSHOT_TS, len(a), "count")
        add(e, grid, "active_mw", SNAPSHOT_TS, a["mw"].sum(), "MW")
        add(e, grid, "signed_share_pct", SNAPSHOT_TS, 100.0 * g["mw"].sum() / a["mw"].sum() if a["mw"].sum() else 0.0, "pct")
        for fuel, f in g.groupby("fuel"):
            ef = f"{e}:{key(fuel)}"
            add(ef, f"{grid}, {fuel or 'fuel not given'}", "projects_signed", SNAPSHOT_TS, len(f), "count")
            add(ef, f"{grid}, {fuel or 'fuel not given'}", "mw_signed", SNAPSHOT_TS, f["mw"].sum(), "MW")
        dated = g[g["ia_date"].ne("")]
        for y, f in dated.groupby(pd.to_datetime(dated["ia_date"], errors="coerce").dt.year):
            ts = f"{int(y)}-01-01T00:00:00Z"
            add(e, grid, "projects_signed_in_year", ts, len(f), "count")
            add(e, grid, "mw_signed_in_year", ts, f["mw"].sum(), "MW")
    s = pd.DataFrame(rows, columns=ip.SERIES_COLS)
    if s.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return s.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generation with a signed interconnection agreement, not yet operating (Queued Up)")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    inp = os.path.join(ip.OUT_DIR, INPUT + ".csv")
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"interconnection_agreements_{run_id}.log"))
    try:
        q = read_table(inp)
        t, counts, still = signed(q)
        s = summary(t, still)
        vin = t["vintage"].iloc[0]
        common = [
            f"Derived from: {INPUT}",
            f"Built by warehouse/derived/interconnection_agreements.py from Berkeley Lab and GridTracker's Queued Up ({vin}); method docs/methods/interconnection_agreements.md",
            f"Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/interconnection_agreements_{run_id}.log",
            "Source: lbnl:queued_up Lawrence Berkeley National Laboratory and GridTracker, Queued Up data file, https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics",
            'License: CC BY 4.0 (Berkeley Lab: "The Queued Up data file is licensed CC BY 4.0"; attribute it to Lawrence Berkeley National Laboratory and GridTracker). The selection and sums are the ERW\'s arithmetic on it.',
        ]
        h1 = [f"Energy Research Warehouse (ERW): interconnection requests with a signed agreement, not yet operating, {vin} (session 854)",
              "Shape: entities (docs/datastandard.md v0). entity_id the queue table's own; entity_type project; status Berkeley Lab's (active or suspended); status_date the agreement date where given; signed_by phase (study phase IA Executed), date (an agreement date) or both; grid Berkeley Lab's region.",
              f"Rows: {len(t):,} of {counts['in the queue']:,} requests still in the queue (phase and date {counts['phase and date']:,}, phase only {counts['phase only']:,}, date only {counts['date only']:,}); "
              f"left out: {counts['with an operation date, left out']:,} that give an operation date. Nothing is filled."] + common
        h2 = [f"Energy Research Warehouse (ERW): generation with a signed interconnection agreement by grid, fuel and year of agreement, {vin} (session 854)",
              "Shape: series (docs/datastandard.md v0). entity interconnection_agreements:<grid> (the seven ISOs, west, southeast, us) or :<grid>:<fuel>; at ts_utc 2025-01-01 (the queue at the end of 2025) projects_signed, mw_signed, active_projects, active_mw, signed_share_pct; "
              "at each year of agreement projects_signed_in_year and mw_signed_in_year (requests that give an agreement date); freq P1Y.",
              f"Rows: {len(s):,}, from {NAME}'s {len(t):,} requests."] + common
        ip.write_snapshot(t, NAME, h1, log, cols=ENTITY_COLS + EXTRA)
        ip.write_snapshot(s, SUMMARY, h2, log, cols=ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="Generation with a signed interconnection agreement, from Berkeley Lab's Queued Up file (docs/methods/interconnection_agreements.md)",
                                    report_url="https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interconnection_agreements.md",
                                    document_list="docs/methods/interconnection_agreements.md", license="public", tables=[NAME, SUMMARY])])
        print(f"{NAME}: {len(t):,} requests; {SUMMARY}: {len(s):,} rows; {counts}")
        rc = 0
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"interconnection_agreements FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
