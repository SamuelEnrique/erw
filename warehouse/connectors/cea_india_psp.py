#!/usr/bin/env python3
"""India's power supply position a fiscal year, by state, region and all India, from the Central Electricity Authority's
monthly Energy Power Supply Position reports: the energy required, the energy supplied and the energy not supplied
(session 2295, chain 105: India's demand met, in place of Grid-India, whose hosts reset the connection).

Energy Research Warehouse (ERW) connector. One series table from the March report of each fiscal year (April to March),
whose second block gives the year's totals; the reports are PDFs on CEA's site, each at a fixed address listed on its
dashboard page:

    https://cea.nic.in/reports/dashboardView?headingId=107&subHeadingId=1003&subSubHeadingId=10010   (the list)
    https://cea.nic.in/api/dashboardReports/download-pdf/en/<id>                                    (each report)

    cea_india_psp_annual   entity cea_psp:<state, region or all_india as a slug> ("others" carry their region:
               others_northern_region); variable energy_requirement, energy_supplied or energy_not_supplied; value in MWh
               (CEA's MU, million units of net energy, times 1,000); ts_utc the fiscal year's first day (1 April); freq P1Y;
               geo IN; node the name as CEA prints it (English), its footnote marks (#, *, (*), (**)) taken off; x_kind state,
               region or country, or state_outside_region_total for a place CEA marks # and leaves out of its region's total
               (Lakshadweep and Andaman-Nicobar), or other_entities for the 2025-26 report's "Others" (CEA's note: "other
               miscellaneous entities drawing power directly from ISTS"); x_region the region a state is in; x_fiscal_year as
               CEA writes it (2025-26)

Each report must print its period as "April,YYYY to March,YYYY"; each line of the table must end with eight figures (the
month's requirement, supply, shortfall and percent, then the year's), a name split over two lines is joined, and a
region's line closes the states above it. The regions must sum to All India to CEA's rounding (5 MU a region), or the run
stops; a region's line can hold more than its states (CEA marks such regions ##, consumption it does not show by state:
the reports of 2022-23 to 2024-25), and every gap of a region marked ##, or of any region over the tolerance, is named in
the header (session 2353: the North-Eastern Region's 8 and 9 MU are under it). The month's figures and the percents are not taken (the percents follow from
the energies). Nothing is filled.

    python warehouse/connectors/cea_india_psp.py [--offline] [--out-dir DIR]

Ceiling: one request a fiscal year (six, the March reports of 2021 to 2026), each asked again unless --offline (CEA
revises reports; every report's English title says Revised). cea.nic.in's robots file allows every path. grid-india.in
and www.grid-india.in reset the connection at their robots files (session 2295). License: internal. CEA's copyright
policy allows reproduction free of charge after prior permission asked by email (session 2299's verdict, needs written
permission; docs/licenses.md).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "cea_india_psp"
SOURCE = "cea:power_supply_position_energy"
HOST = "cea.nic.in"
PAGE = "https://cea.nic.in/reports/dashboardView?headingId=107&subHeadingId=1003&subSubHeadingId=10010&title=Power%20Supply%20Position%20-%20Energy&lang=en"
TABLE = "cea_india_psp_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
REPORTS = {  # the March report of each fiscal year, as the dashboard lists it
    "2020-21": "84cabd50-b0fd-47d0-9d2a-9d22785299e3", "2021-22": "9e2ffc5a-167e-4a15-977b-dd64fe986b2a",
    "2022-23": "9e139873-65eb-469e-8aee-d62e2ad1f14e", "2023-24": "b36ce22b-480b-4f47-8885-4bfdc4bfabe3",
    "2024-25": "812d4632-b9c8-48f5-92ca-4ba04863aef1", "2025-26": "895565cb-8252-4fa6-a3b3-8a02d27922ee"}
NUM = r"[\d,]+(?:\.\d+)?"
LINE = re.compile(rf"^(?P<label>.*?)\s*(?P<nums>(?:{NUM}\s+){{7}}{NUM})\s*$")
X_COLS = ["x_kind", "x_region", "x_fiscal_year"]
TOLERANCE = 5.0  # MU


def url_of(rid):
    return f"https://cea.nic.in/api/dashboardReports/download-pdf/en/{rid}"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def english(label):
    name = label.split("/")[-1] if "/" in label else label
    name = re.sub(r"\s+", " ", re.sub(r"\(?[#*]+\)?", "", name)).strip()  # CEA's footnote marks off (session 2353)
    return name if name and all(ord(c) < 128 for c in name) else ""


def mu(tok):
    return float(tok.replace(",", ""))


def parse(content, fy, base, gaps):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        lines = [l.strip() for p in pdf.pages for l in (p.extract_text() or "").splitlines() if l.strip()]
    start = int(fy[:4])
    period = [l for l in lines if re.search(rf"April,\s*{start}\s*-?\s*(?:to)?\s*March,\s*{start + 1}", l) or re.search(rf"April,\s*{start}\s*to\s*March,\s*{start + 1}", l)]
    if not period:
        raise RuntimeError(f"{fy}: the report does not print April,{start} to March,{start + 1}")
    entries, pending = [], None
    for i, l in enumerate(lines):
        m = LINE.match(l)
        if not m:
            if pending is not None and english(l):
                pending["name"] = english(l)
                entries.append(pending)
                pending = None
            continue
        nums = m.group("nums").split()
        lab = m.group("label")
        row = {"name": english(lab), "fy": [mu(x) for x in nums[4:7]], "outside": bool(re.search(r"(?<!#)#(?!#)", lab)),
               "marked": "##" in lab}
        if row["name"]:
            entries.append(row)
        else:
            pending = row  # the name is printed on the next line
    states, out, regions, india = [], [], {}, None
    for e in entries:
        n = e["name"]
        if re.search(r"(?i)\bregion\b", n):
            region = re.sub(r"(?i)\s*region$", " Region", n).strip()
            req = sum(s["fy"][0] for s in states if not s["outside"])
            if e.get("marked") or abs(req - e["fy"][0]) > TOLERANCE * max(1, len(states)):
                gaps[f"{fy} {region}"] = round(e["fy"][0] - req)  # the region's line holds more than its states (CEA's ## mark)
            for s in states:
                others = s["name"] == "Others"  # 2025-26: entities drawing power directly from ISTS (CEA's note)
                nm = f"Others ({region})" if others else s["name"]
                kind = "other_entities" if others else ("state_outside_region_total" if s["outside"] else "state")
                out.append((nm, kind, region, s["fy"]))
            out.append((region, "region", "", e["fy"]))
            regions[region] = e["fy"]
            states = []
        elif re.search(r"(?i)all india", n):
            india = e["fy"]
            out.append(("All India", "country", "", e["fy"]))
        else:
            states.append(e)
    if india is None or not regions:
        raise RuntimeError(f"{fy}: no All India or region line")
    tot = sum(v[0] for v in regions.values())
    if abs(tot - india[0]) > TOLERANCE * len(regions):
        raise RuntimeError(f"{fy}: the regions sum to {tot:,.0f} MU, All India {india[0]:,.0f}")
    rows = []
    for nm, kind, region, fyv in out:
        for var, v in zip(["energy_requirement", "energy_supplied", "energy_not_supplied"], fyv):
            rows.append(dict(base, entity=f"cea_psp:{slug(nm)}", variable=var, ts_utc=f"{start}-04-01T00:00:00Z", value=v * 1000.0, unit="MWh",
                             freq="P1Y", geo="IN", market="", node=nm, x_kind=kind, x_region=region, x_fiscal_year=fy))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="CEA: India's energy power supply position a fiscal year, by state and region")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        rows, got, gaps = [], [], {}
        for fy, rid in REPORTS.items():
            content, rec = ip.fetch_raw(CONNECTOR, url_of(rid), log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=1)
            base = dict(source=SOURCE, source_url=url_of(rid), retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            rows += parse(content, fy, base, gaps)
            got.append(base["retrieved_at"])
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"a key given twice: {s[s.duplicated(['entity', 'variable', 'ts_utc'])].entity.unique()[:5]}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): Central Electricity Authority (India), Energy Power Supply Position, the fiscal years "
            f"{s.x_fiscal_year.min()} to {s.x_fiscal_year.max()} by state, region and all India (session 2295)",
            "Shape: series (docs/datastandard.md v0). entity cea_psp:<state, region or all_india>; variable energy_requirement, energy_supplied "
            "or energy_not_supplied; unit MWh (CEA's MU of net energy times 1,000); freq P1Y; ts_utc the fiscal year's first day (1 April); geo "
            "IN; node CEA's name, its footnote marks taken off; x_kind state, region, country, state_outside_region_total (a place "
            "CEA marks # and leaves out of its region's total: Lakshadweep, Andaman-Nicobar) or other_entities (2025-26's Others, "
            "entities drawing power directly from ISTS, CEA's note); x_region; x_fiscal_year.",
            "From each March report's year-to-date block. The regions sum to All India to CEA's rounding (checked). A region's line can hold "
            "more than its states (CEA marks it ##); every gap of a region marked ## or over the tolerance (5 MU a place), in MU: "
            f"{', '.join(f'{k} {v:+,}' for k, v in gaps.items()) or 'none'}. The month's figures and the percents are not taken. "
            "Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cea_india_psp.py; the reports retrieved from {min(got)} to {max(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Central Electricity Authority, Government of India, Power Supply Position - Energy (monthly reports), {PAGE}",
            "  access: https://cea.nic.in/api/dashboardReports/download-pdf/en/<id>, the March report of each fiscal year",
            "License: internal. CEA's copyright policy allows reproduction free of charge after prior permission asked by email (session "
            "2299's verdict: needs written permission). Source: Central Electricity Authority.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} entities, fiscal years {s.x_fiscal_year.min()} to {s.x_fiscal_year.max()}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Central Electricity Authority (India)", report="Power Supply Position - Energy, monthly reports",
                                    report_url=PAGE, document_list=PAGE, license="internal", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
