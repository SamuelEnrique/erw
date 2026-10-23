#!/usr/bin/env python3
"""The Department of Energy's U.S. Energy and Employment Report (USEER), its public data: energy employment by sector,
technology and industry, nationally, and by sector and technology in each state (session 2000, chain 056).

Energy Research Warehouse (ERW) connector. One series table from the 2026 USEER's public data workbook (employment in
2025, with 2024's totals):

    https://www.energy.gov/policy/us-energy-employment-jobs-report-useer
    https://www.energy.gov/documents/2026-useer-public-data   (the workbook itself)

    doe_useer_employment   entity useer2026:<geo>:<sector>:<subsector>:<industry>; variable employment; unit count (USEER's
                           survey estimate of workers, as published, not rounded); ts_utc the year's 1 January; freq P1Y;
                           geo US or US-<state>, empty for "Puerto Rico and U.S. Virgin Islands" (one row of USEER's)

    sector     fuels, epg (electric power generation), td (electric power transmission and distribution), storage, tds
               (the two together, the state sheet's), ee (energy efficiency), mvcp (motor vehicles and component parts),
               all (the state sheet's employment by industry)
    subsector  USEER's technology (solar, land_based_wind, battery, ...), or total
    industry   USEER's industry column (agriculture, mining, utilities, construction, manufacturing, trade, pipeline,
               professional_services, other_services, commodity_flows), or total

The sheet "Industry Detail by Sector" gives the nation's blocks (2025 by industry, the 2025 and 2024 totals; the change
column is their difference and is not taken). Its "2025 TDS Employment" block is not taken: its one row, "TDS Total",
repeats the "Pumped Hydro" storage row figure for figure (the publisher's error); the T&D and storage blocks hold the
same workers. The sheet "State Data" gives each state's employment by subsector of each sector and by industry, 2025. The
five "WF Characteristics" sheets (the workforce's sex, ethnicity, race, age, veterans and union shares) are not taken.

A heading not as read, a block not found, a state not in the map, or an (entity, ts_utc) given twice stops the run; a
cell USEER leaves empty has no row; nothing is filled.

    python warehouse/connectors/doe_useer.py [--offline] [--out-dir DIR]

Ceiling: one request (the workbook, saved in warehouse/raw/doe_useer/ and reused offline). energy.gov's robots file
allows /documents/ and /policy/. License: public (the Department of Energy's web policies, read 54 of license_reads.csv:
"Government information at DOE websites is in the public domain").
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

CONNECTOR = "doe_useer"
SOURCE = "doe:useer_2026_public_data"
PAGE = "https://www.energy.gov/policy/us-energy-employment-jobs-report-useer"
URL = "https://www.energy.gov/documents/2026-useer-public-data"
TABLE = "doe_useer_employment"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_sector", "x_subsector", "x_industry"]

# the nation's blocks: the block's title as read, its sector key, its first heading
NATIONAL = [
    ("2025 Fuels Employment, Industry Detail by Subsector", "fuels", "Fuels Subsector"),
    ("2025 EPG Employment, Industry Detail by Subsector", "epg", "EPG Subsector"),
    ("2025 Transmission and Distribution Employment, Industry Detail by Subsector", "td", "T&D Subsector"),
    ("2025 Storage Employment, Industry Detail by Subsector", "storage", "Storage Subsector"),
    ("2025 Energy Efficiency Employment, Industry Detail by Subsector", "ee", "EE Subsector"),
    ("2025 MVCP Employment, Industry Detail by Subsector", "mvcp", "MVCP Subsector"),
]
SKIPPED_BLOCK = "2025 TDS Employment, Industry Detail by Subsector"
INDUSTRIES = {
    "Agriculture (NAICS 11)": "agriculture",
    "Mining and Extraction (NAICS 21)": "mining",
    "Utilities (NAICS 22)": "utilities",
    "Construction (NAICS 23)": "construction",
    "Manufacturing (NAICS 32-33)": "manufacturing",
    "Wholesale Trade (42-45)": "trade",
    "Pipeline Transportation": "pipeline",
    "Professional Services (NAICS 51-56)": "professional_services",
    "Other (NAICS 81)": "other_services",
    "Commodity Flows": "commodity_flows",
    "2025 Employment Total": "total",
    "2024 Employment Total": "total",
    "Employment Change, 2024-2025": None,
}
# the state sheet's blocks: the title as read, its sector key
STATE_BLOCKS = {
    "Fuels Employment by State and Subsector, 2025": "fuels",
    "EPG Employment by State and Subsector, 2025": "epg",
    "TDS Employment by State and Subsector, 2025": "tds",
    "Energy Efficiency Employment by State and Subsector, 2025": "ee",
    "Motor Vehicles Employment by State and Subsector, 2025": "mvcp",
    "Employment by State and Industry, 2025": "all",
}
STATE_INDUSTRIES = {
    "Agriculture and Forestry": "agriculture", "Mining and Extraction": "mining", "Utilities": "utilities",
    "Construction": "construction", "Manufacturing": "manufacturing", "Trade": "trade",
    "Pipeline Transport & Commodity Flows": "pipeline_and_commodity_flows", "Professional Services": "professional_services",
    "Other Services": "other_services",
}
STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
}
PR_USVI = "PR & USVI"


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower().replace("&", " and ")).strip("_")


def number(v):
    if v is None or isinstance(v, str):
        return None
    v = float(v)
    return None if pd.isna(v) else v


def is_total(label):
    return bool(re.search(r"\btotal$", label, re.I))


def row(base, geo, sector, sub, ind, year, value, node):
    ent = f"useer2026:{geo or 'PR_VI'}:{sector}:{sub}:{ind}"
    return dict(base, entity=ent, variable="employment", ts_utc=f"{year}-01-01T00:00:00Z", value=value, unit="count",
                freq="P1Y", geo=geo, market="", node=node, x_sector=sector, x_subsector=sub, x_industry=ind)


def national(d, base):
    titles = {text(d.iloc[i, 0]): i for i in range(len(d))}
    if SKIPPED_BLOCK not in titles:
        raise RuntimeError("the TDS block not found where it was read; look again before taking the sheet")
    out, sums = [], []
    for title, sector, first in NATIONAL:
        if title not in titles:
            raise RuntimeError(f"national block not found: {title}")
        h = titles[title] + 1
        heads = [text(v) for v in d.iloc[h].tolist()]
        if heads[0] != first or [x for x in heads[1:] if x] != list(INDUSTRIES):
            raise RuntimeError(f"{title}: headings not as read: {heads}")
        for i in range(h + 1, len(d)):
            label = text(d.iloc[i, 0])
            if not label:
                break
            sub = "total" if is_total(label) else slug(label)
            parts = 0.0
            for j, head in enumerate(heads[1:], start=1):
                ind = INDUSTRIES.get(head)
                v = number(d.iloc[i, j])
                if ind is None or v is None:
                    continue
                year = "2024" if head.startswith("2024") else "2025"
                if ind != "total":
                    parts += v
                out.append(row(base, "US", sector, sub, ind, year, v, f"{label}, {head}"))
            tot = number(d.iloc[i, heads.index("2025 Employment Total")])
            if tot is not None:
                sums.append(abs(parts - tot) <= 1)
    return out, sums


def states(d, base):
    titles = [text(v) for v in d.iloc[3].tolist()]
    heads = [text(v) for v in d.iloc[4].tolist()]
    starts = [(j, t) for j, t in enumerate(titles) if t]
    if [t for _, t in starts] != list(STATE_BLOCKS):
        raise RuntimeError(f"state blocks not as read: {[t for _, t in starts]}")
    out = []
    for k, (j0, title) in enumerate(starts):
        sector = STATE_BLOCKS[title]
        if heads[j0:j0 + 2] != ["State abbreviation", "State"]:
            raise RuntimeError(f"{title}: headings not as read at column {j0}")
        end = starts[k + 1][0] if k + 1 < len(starts) else len(heads)
        cols = [(j, heads[j]) for j in range(j0 + 2, end) if heads[j]]
        for i in range(5, len(d)):
            st, name = text(d.iloc[i, j0]), text(d.iloc[i, j0 + 1])
            if not st:
                continue
            if st not in STATES and st != PR_USVI:
                raise RuntimeError(f"{title}: a state not in the map: {st}")
            geo = "" if st == PR_USVI else f"US-{st}"
            for j, head in cols:
                v = number(d.iloc[i, j])
                if v is None:
                    continue
                if sector == "all":
                    if head not in STATE_INDUSTRIES:
                        raise RuntimeError(f"an industry not in the map: {head}")
                    sub, ind = "all", STATE_INDUSTRIES[head]
                else:
                    sub, ind = ("total" if is_total(head) else slug(head)), "total"
                out.append(row(base, geo, sector, sub, ind, "2025", v, f"{name}, {head}"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The 2026 USEER's public data: energy employment by sector, technology, industry and state")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=120)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        book = pd.read_excel(io.BytesIO(content), sheet_name=None, header=None)
        for need in ("Industry Detail by Sector", "State Data"):
            if need not in book:
                raise RuntimeError(f"sheet not found: {need}")
        nat, sums = national(book["Industry Detail by Sector"], base)
        s = pd.DataFrame(nat + states(book["State Data"], base))
        if s.duplicated(["entity", "ts_utc"]).any():
            raise RuntimeError(f"an (entity, ts_utc) given twice: {s[s.duplicated(['entity', 'ts_utc'])].entity.head(3).tolist()}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        us = s[s.geo == "US"]
        head = [
            "Energy Research Warehouse (ERW): U.S. Department of Energy, 2026 U.S. Energy and Employment Report (USEER), public data: energy employment "
            "in 2025 by sector, technology (subsector) and industry, nationally (with 2024's totals), and by sector and technology in each state (session 2000)",
            "Shape: series (docs/datastandard.md v0). entity useer2026:<geo>:<sector>:<subsector>:<industry>; variable employment; unit count (USEER's survey "
            "estimate of workers, as published, not rounded); freq P1Y; ts_utc the year's 1 January; geo US, US-<state>, or empty for USEER's one row of "
            "Puerto Rico and the U.S. Virgin Islands; x_sector fuels, epg, td, storage, tds (the state sheet's T&D and storage), ee, mvcp or all; "
            "x_subsector USEER's technology or total; x_industry USEER's industry or total.",
            f"{len(us)} national rows, {len(s) - len(us)} state rows; {s.entity.nunique()} series. A total holds its parts: a sum takes one level. "
            f"Of the nation's {len(sums)} rows with a 2025 total, {sum(sums)} equal the sum of their industries within one worker.",
            "Not taken: the change column (2025 less 2024); the nation's '2025 TDS Employment' block, whose one row repeats the 'Pumped Hydro' storage "
            "row figure for figure (the publisher's error; the T&D and storage blocks hold the same workers); the five workforce characteristics sheets. "
            "A cell USEER leaves empty has no row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/doe_useer.py; the workbook retrieved {base['retrieved_at']}, last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of Energy, U.S. Energy and Employment Report, {PAGE}",
            f"  access: {URL}",
            'License: public (DOE web policies: "Government information at DOE websites is in the public domain"; cite "U.S. Department of Energy, '
            '2026 U.S. Energy and Employment Report").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} series ({len(us)} national); sums {sum(sums)} of {len(sums)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Energy (DOE)",
                                    report="U.S. Energy and Employment Report 2026 (Office of Energy Jobs), public data", report_url=PAGE, document_list=URL,
                                    license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
