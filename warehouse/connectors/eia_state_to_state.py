#!/usr/bin/env python3
"""EIA's U.S. state-to-state natural gas pipeline capacity: each interstate pipeline's capacity at each state border it
crosses, a year a row, from 1990 (session 2090, chain 068: the gas that can move between states, beside the pipeline
projects the ERW already holds).

Energy Research Warehouse (ERW) connector. One series table from the data page of EIA's U.S. State-to-State Capacity
workbook (www.eia.gov/naturalgas/data.php, "Pipelines"; the newest issue is taken from the page's links):

    https://www.eia.gov/naturalgas/pipelines/EIA-StatetoStateCapacity_<Mon><Year>.xlsx   sheet "Pipeline State2State
        Capacity": year, Pipeline, Region From, Region To, State From, County From, State To, County To,
        Capacity (mmcfd), Notes

    eia_state_to_state_capacity   entity eia_s2s:<pipeline>:<state from>:<county from>:<state to>:<county to>:<n> (each
                                  part lower case with underscores; n the crossing's place among the year's rows with
                                  the same five, as EIA lists them, since a pipeline can cross the same counties on two
                                  lines); variable capacity; unit bcf/d (EIA's MMcf a day over 1,000); ts_utc the year's
                                  first day; freq P1Y; geo US-<state to> where it is a state or DC, else empty (Canada
                                  and Mexico's provinces and states); node the pipeline as EIA names it; x_ the regions,
                                  states and counties from and to, the capacity in MMcf a day as published, and EIA's notes

A sheet without these columns, a year not a year or a capacity not a number stops the run. Nothing is filled; a row EIA
lists twice is kept twice (two places), as EIA's own pivot tables sum it.

    python warehouse/connectors/eia_state_to_state.py [--offline] [--out-dir DIR]

Ceiling: two requests (the data page and the workbook), saved in warehouse/raw/eia_state_to_state/ and reused offline;
the page is asked fresh when not offline. License: public (EIA, read 1).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "eia_state_to_state"
SOURCE = "eia:state_to_state_capacity"
PAGE = "https://www.eia.gov/naturalgas/data.php"
HOST = "https://www.eia.gov"
SHEET = "Pipeline State2State Capacity"
TABLE = "eia_state_to_state_capacity"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
NEED = ["year", "Pipeline", "Region From", "Region To", "State From", "County From", "State To", "County To", "Capacity (mmcfd)", "Notes"]
X_COLS = ["x_region_from", "x_region_to", "x_state_from", "x_county_from", "x_state_to", "x_county_to", "x_capacity_mmcfd", "x_notes"]
MON = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
          "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
          "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
          "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
          "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
          "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
          "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_") or "none"


def newest(page_html):
    found = []
    for href in re.findall(r'href="([^"]*EIA-StatetoStateCapacity_([A-Za-z]{3})(\d{4})\.xlsx)"', page_html):
        url, mon, year = href
        if mon.lower() in MON:
            found.append((int(year), MON[mon.lower()], url if url.startswith("http") else HOST + url))
    if not found:
        raise RuntimeError("no EIA-StatetoStateCapacity_<Mon><Year>.xlsx link on the page")
    return max(found)


def read(content):
    d = pd.read_excel(io.BytesIO(content), sheet_name=SHEET, header=1, dtype=str).fillna("")
    d.columns = [c.strip() for c in d.columns]
    miss = [c for c in NEED if c not in d.columns]
    if miss:
        raise RuntimeError(f"the sheet has no column {miss}; its columns are {list(d.columns)}")
    d = d[NEED].apply(lambda s: s.str.strip())
    d = d[(d != "").any(axis=1)]
    if (~d.year.str.fullmatch(r"(19|20)\d{2}")).any():
        raise RuntimeError(f"a year not a year: {d.year[~d.year.str.fullmatch(r'(19|20)[0-9]{2}')].head(3).tolist()}")
    cap = pd.to_numeric(d["Capacity (mmcfd)"].str.replace(",", "", regex=False), errors="coerce")
    if cap.isna().any():
        raise RuntimeError(f"a capacity not a number: {d.loc[cap.isna(), 'Capacity (mmcfd)'].head(3).tolist()}")
    d["cap"] = cap
    return d


def build(d, base):
    key = ["year", "Pipeline", "State From", "County From", "State To", "County To"]
    d = d.copy()
    d["n"] = d.groupby(key).cumcount() + 1
    ent = ("eia_s2s:" + d.Pipeline.map(slug) + ":" + d["State From"].map(slug) + ":" + d["County From"].map(slug) + ":"
           + d["State To"].map(slug) + ":" + d["County To"].map(slug) + ":" + d.n.astype(str))
    return pd.DataFrame({
        "entity": ent, "variable": "capacity", "ts_utc": d.year + "-01-01T00:00:00Z", "value": (d.cap / 1000).round(6), "unit": "bcf/d",
        "freq": "P1Y", "geo": d["State To"].map(lambda s: f"US-{STATES[s]}" if s in STATES else ""), "market": "", "node": d.Pipeline, **base,
        "x_region_from": d["Region From"], "x_region_to": d["Region To"], "x_state_from": d["State From"], "x_county_from": d["County From"],
        "x_state_to": d["State To"], "x_county_to": d["County To"], "x_capacity_mmcfd": d["Capacity (mmcfd)"], "x_notes": d.Notes})


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's state-to-state natural gas pipeline capacity, a year")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
        y, mo, url = newest(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        s = build(read(content), base)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a crossing and year given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): U.S. Energy Information Administration (EIA), U.S. State-to-State Capacity (natural gas pipelines), "
            f"the {y}-{mo:02d} issue, sheet \"{SHEET}\": each pipeline's capacity at each state border it crosses, a year (session 2090)",
            "Shape: series (docs/datastandard.md v0). entity eia_s2s:<pipeline>:<state from>:<county from>:<state to>:<county to>:<n> (n the "
            "crossing's place among the year's rows with the same five); variable capacity; unit bcf/d (EIA's MMcf a day over 1,000, kept as "
            "published in x_capacity_mmcfd); ts_utc the year's first day; freq P1Y; geo US-<state to>, empty for Canada and Mexico; node the "
            "pipeline; x_ the regions, states, counties and EIA's notes.",
            f"{len(s)} rows, {s.entity.nunique()} crossings, {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}. A row EIA lists twice is kept twice. "
            "Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_state_to_state.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} EIA, Natural Gas Data, Pipelines, {PAGE}",
            f"  access: {url}",
            'License: public (EIA: "U.S. government publications are in the public domain"; cite "U.S. Energy Information Administration").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} crossings")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="EIA", report="U.S. State-to-State Capacity (natural gas pipelines)",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
