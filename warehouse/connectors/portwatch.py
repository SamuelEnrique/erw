#!/usr/bin/env python3
"""IMF PortWatch daily chokepoint transits: Strait of Hormuz, Suez Canal, Panama Canal.

Energy Research Warehouse (ERW) connector, session 8 (docs/price-sources.md,
section 8). Reads IMF PortWatch's public ArcGIS FeatureServer
(Daily_Chokepoints_Data) and writes one `series` table,
portwatch_chokepoint_transits:

    entity    portwatch:<portid>   (chokepoint6 Strait of Hormuz, chokepoint1 Suez Canal,
                                    chokepoint2 Panama Canal)
    variable  n_tanker, n_container, n_dry_bulk, n_general_cargo, n_roro, n_cargo, n_total
              (vessel transits per day, unit count) and capacity_tanker, capacity_container,
              capacity_dry_bulk, capacity_general_cargo, capacity_roro, capacity_cargo,
              capacity (deadweight tonnage of those transits, unit dwt)
    freq      P1D; ts_utc is PortWatch's date at 00:00:00Z

    python warehouse/connectors/portwatch.py

Full history each run (from 2019-01-01), 1,000 rows per request (the
service's maximum), ordered by ObjectId. Completeness: every calendar day
from each chokepoint's first date to its last must be present exactly once,
or the table is not written. The newest date must be within 10 days.

License: internal. Citation "IMF PortWatch"; the IMF terms page returned 403
and commercial reuse is unconfirmed (docs/price-sources.md; session 8
ruling: internal until the terms are confirmed). PortWatch is its own
connector because it is its own source (CLAUDE.md: one connector per source).
"""

import datetime as dt
import os
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "portwatch_chokepoint_transits"
URL = ("https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
       "Daily_Chokepoints_Data/FeatureServer/0/query")
PAGE = "https://portwatch.imf.org/pages/cb5856222a5b4105adc6ee7e880a1730"
SOURCE = "imf:portwatch-daily-chokepoints"
CHOKEPOINTS = {"chokepoint6": "Strait of Hormuz", "chokepoint1": "Suez Canal", "chokepoint2": "Panama Canal"}
KINDS = ["tanker", "container", "dry_bulk", "general_cargo", "roro", "cargo"]
COUNT_VARS = [f"n_{k}" for k in KINDS] + ["n_total"]
CAP_VARS = [f"capacity_{k}" for k in KINDS] + ["capacity"]
PAGE_SIZE = 1000
STALE_DAYS = 10


def fetch(portid, log):
    rows, offset = [], 0
    while True:
        params = {"where": f"portid='{portid}'", "outFields": "*", "f": "json", "orderByFields": "ObjectId",
                  "resultOffset": offset, "resultRecordCount": PAGE_SIZE, "returnGeometry": "false"}

        def call():
            r = requests.get(URL, params=params, timeout=120)
            if r.status_code != 200:
                raise RuntimeError(f"PortWatch HTTP {r.status_code}")
            j = r.json()
            if "error" in j:
                raise RuntimeError(f"PortWatch error {j['error']}")
            return r, j
        r, j = ip.with_retries(f"PortWatch {portid} offset {offset}", call, log)
        got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        feats = [f["attributes"] for f in j.get("features", [])]
        for f in feats:
            f["_url"], f["_got"] = r.url, got
        rows += feats
        log(f"  {portid} offset {offset}: {len(feats)} rows")
        if not j.get("exceededTransferLimit") and len(feats) < PAGE_SIZE:
            break
        if not feats:
            break
        offset += len(feats)
    return pd.DataFrame(rows)


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"portwatch_{run_id}.log"))
    ip.RAW.open("portwatch", run_id)
    results = []
    try:
        frames = []
        for portid, pname in CHOKEPOINTS.items():
            log(f"{pname} ({portid}):")
            d = fetch(portid, log)
            if d.empty:
                raise RuntimeError(f"PortWatch returned no rows for {portid}")
            if set(d["portname"]) != {pname}:
                raise RuntimeError(f"{portid}: portname {set(d['portname'])}, expected {pname}")
            missing = [c for c in COUNT_VARS + CAP_VARS + ["date"] if c not in d.columns]
            if missing:
                raise RuntimeError(f"{portid}: fields missing {missing}")
            if d["date"].duplicated().any():
                raise RuntimeError(f"{portid}: {int(d['date'].duplicated().sum())} dates appear twice")
            days = pd.to_datetime(d["date"], format="%Y-%m-%d")
            full = pd.date_range(days.min(), days.max(), freq="D")
            gap = full.difference(days)
            if len(gap):
                raise RuntimeError(f"{portid}: {len(gap)} days missing between {days.min().date()} and "
                                   f"{days.max().date()}, e.g. {[str(x.date()) for x in gap[:5]]}")
            age = (pd.Timestamp.now().normalize() - days.max()).days
            if age > STALE_DAYS:
                raise RuntimeError(f"{portid}: newest date {days.max().date()} is {age} days old")
            log(f"  {len(d)} days, {days.min().date()} to {days.max().date()}, no gaps")
            long = d.melt(id_vars=["date", "_url", "_got"], value_vars=COUNT_VARS + CAP_VARS,
                          var_name="variable", value_name="value")
            if long["value"].isna().any():
                raise RuntimeError(f"{portid}: {int(long['value'].isna().sum())} empty values")
            frames.append(pd.DataFrame({
                "entity": f"portwatch:{portid}", "variable": long["variable"],
                "ts_utc": long["date"] + "T00:00:00Z", "value": long["value"].astype(float),
                "unit": long["variable"].map(lambda v: "count" if v.startswith("n_") else "dwt"),
                "freq": "P1D", "geo": "", "market": "", "node": pname, "source": SOURCE,
                "source_url": long["_url"].map(ip.redact), "retrieved_at": long["_got"], "vintage": ""}))
        s = pd.concat(frames, ignore_index=True).sort_values(["entity", "variable", "ts_utc"])
        header = [
            "Energy Research Warehouse (ERW): IMF PortWatch daily chokepoint transits: Strait of Hormuz, "
            "Suez Canal, Panama Canal",
            "Shape: series (docs/datastandard.md v0). freq P1D: ts_utc is PortWatch's date at 00:00:00Z. "
            "n_* are vessel transits per day (count); capacity* the deadweight tonnage of those transits (dwt).",
            "Window: the full history the service offers (from 2019-01-01); every run replaces all of it.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/portwatch.py",
            f"Run log: warehouse/output/logs/portwatch_{run_id}.log",
            f"Raw files: warehouse/raw/portwatch/{run_id}/ (not in git)",
            f"Source: {SOURCE} IMF PortWatch Daily Chokepoints Data (ArcGIS FeatureServer), {URL}",
            f"  portal: {PAGE}",
            "License: internal. Cite \"IMF PortWatch\"; IMF terms unconfirmed (terms page 403), so internal "
            "until confirmed (session 8 ruling).",
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="International Monetary Fund (IMF PortWatch)",
                                report="Daily Chokepoints Data (vessel transits)", report_url=PAGE,
                                document_list=URL, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="daily", status="ok", detail=""))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"portwatch {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="daily", status="failed", detail=last[:300]))
    ip.write_status("portwatch", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"portwatch run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
