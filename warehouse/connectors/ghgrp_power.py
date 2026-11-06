#!/usr/bin/env python3
"""EPA's Greenhouse Gas Reporting Program: each power plant's reported CO2 by year (session 492).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/epa_ghgrp_power_co2.csv, from the U.S.
Environmental Protection Agency's GHGRP data summary spreadsheets (one workbook a reporting year, sheet "Direct Emitters"
or "Direct Point Emitters"), for the facilities that report under subpart D (electricity generation) that year, with the
plant's ORIS code from EPA's own GHGRP-to-ORIS crosswalk:

    page        https://www.epa.gov/ghgreporting/data-sets
    files       the newest <year>_data_summary_spreadsheets.zip the page links (ghgp_data_<year>.xlsx, 2010 on)
                and ghgrp_oris_power_plant_crosswalk_*.xlsx

    entity      ghgrp:<GHGRP facility id>; node the facility's name; geo US-<state>; ts_utc the reporting year's 1 January;
                freq P1Y
    variable    co2_non_biogenic and co2_biogenic, metric tons of CO2 (tCO2), as the facility reported them
    x_*         FRS id, ORIS codes (the crosswalk's, ";"-joined), subparts, NAICS, the workbook's year

Not taken: methane, nitrous oxide and the totals, which the summary gives in metric tons of CO2 equivalent (AR4 GWPs):
CO2e is not in the standard's unit vocabulary, and CO2 itself is not CO2e; the header says so. A blank cell has no row;
nothing is filled. A facility given twice in a year stops the run.

    python warehouse/connectors/ghgrp_power.py

Ceiling: three requests (the page, the zip, the crosswalk; files already in warehouse/raw/ghgrp/ are reused). License:
public (EPA, record 55 of license_reads.csv; cite "U.S. EPA, Greenhouse Gas Reporting Program, data summary <year>").
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "epa_ghgrp_power_co2"
CONNECTOR = "ghgrp"
SOURCE = "epa:ghgrp"
PAGE = "https://www.epa.gov/ghgreporting/data-sets"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_frs_id", "x_oris", "x_subparts", "x_naics", "x_reporting_year"]
TAKEN = {"CO2 emissions (non-biogenic)": "co2_non_biogenic", "Biogenic CO2 emissions (metric tons)": "co2_biogenic"}
SUBPART_D = re.compile(r"(?:^|,)\s*D\s*(?:,|$)")


def links(page_html):
    """(the newest summary zip, its year, the ORIS crosswalk) as the page links them."""
    zips = re.findall(r'href="([^"]*?(\d{4})_data_summary_spreadsheets\.zip)"', page_html, re.I)
    cross = re.findall(r'href="([^"]*ghgrp_oris_power_plant_crosswalk[^"]*\.xlsx)"', page_html, re.I)
    if not zips or not cross:
        raise RuntimeError("the data-sets page links no data summary zip or no ORIS crosswalk")
    url, year = max(zips, key=lambda z: int(z[1]))
    full = lambda u: u if u.startswith("http") else "https://www.epa.gov" + u  # noqa: E731
    return full(url), int(year), full(sorted(cross)[-1])


def crosswalk(frame):
    """{GHGRP facility id: "oris;oris2;..."} from EPA's crosswalk sheet (its first row the headings)."""
    d = frame.copy()
    d.columns = [str(c).strip() for c in d.iloc[0]]
    d = d.iloc[1:]
    oris = [c for c in d.columns if c.upper().startswith("ORIS CODE")]
    out = {}
    for _, r in d.iterrows():
        fid = pd.to_numeric(r["GHGRP Facility ID"], errors="coerce")
        if pd.isna(fid):
            continue
        codes = [str(int(v)) for v in (pd.to_numeric(r[c], errors="coerce") for c in oris) if pd.notna(v)]
        out[int(fid)] = ";".join(codes)
    return out


def year_rows(book, year, url, retrieved, cross):
    x = pd.ExcelFile(io.BytesIO(book))
    sheet = next(n for n in x.sheet_names if n.lower().startswith("direct"))
    top = pd.read_excel(x, sheet, header=None, nrows=8)
    r = next(i for i in range(8) if str(top.iloc[i, 0]).strip().lower().startswith("facility id"))
    d = pd.read_excel(x, sheet, header=r)
    d.columns = [str(c).strip() for c in d.columns]
    missing = [c for c in ["Facility Id", "Facility Name", "State", "Industry Type (subparts)"] + list(TAKEN) if c not in d.columns]
    if missing:
        raise RuntimeError(f"{year}: the sheet lacks {missing}")
    d = d[d["Industry Type (subparts)"].astype(str).str.contains(SUBPART_D)]
    fid = pd.to_numeric(d["Facility Id"], errors="coerce")
    d = d[fid.notna()]
    fid = fid[fid.notna()].astype(int)
    if fid.duplicated().any():
        raise RuntimeError(f"{year}: a facility given twice")
    out = []
    for (_, row), f in zip(d.iterrows(), fid):
        for col, var in TAKEN.items():
            v = pd.to_numeric(row[col], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(entity=f"ghgrp:{f}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=float(v), unit="tCO2", freq="P1Y",
                            geo=f"US-{str(row['State']).strip()}", market="", node=str(row["Facility Name"]).strip(), source=SOURCE,
                            source_url=url, retrieved_at=retrieved, vintage="",
                            x_frs_id="" if pd.isna(row.get("FRS Id")) else str(row.get("FRS Id")).replace(".0", ""),
                            x_oris=cross.get(f, ""), x_subparts=str(row["Industry Type (subparts)"]).strip(),
                            x_naics="" if pd.isna(row.get("Primary NAICS Code")) else str(row.get("Primary NAICS Code")).replace(".0", ""),
                            x_reporting_year=str(year)))
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPA GHGRP: each power plant's reported CO2 by year")
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
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, fresh=True, headers=UA)
        zurl, last, curl = links(page.decode("utf-8", errors="replace"))
        z, rec = ip.fetch_raw(CONNECTOR, zurl, log, headers=UA, timeout=600)
        c, _ = ip.fetch_raw(CONNECTOR, curl, log, headers=UA, timeout=600)
        cross = crosswalk(pd.read_excel(io.BytesIO(c), "ORIS Crosswalk", header=None))
        zf = zipfile.ZipFile(io.BytesIO(z))
        years = sorted(int(m.group(1)) for n in zf.namelist() for m in [re.fullmatch(r"ghgp_data_(\d{4})\.xlsx", n)] if m)
        frames = []
        for y in years:
            t = year_rows(zf.read(f"ghgp_data_{y}.xlsx"), y, zurl, rec["retrieved_at"], cross)
            frames.append(t)
            log(f"  {y}: {t['entity'].nunique():,} facilities, {len(t):,} rows")
        s = pd.concat(frames, ignore_index=True)[ip.SERIES_COLS + X_COLS]
        header = [
            f"Energy Research Warehouse (ERW): EPA Greenhouse Gas Reporting Program, power plants' (subpart D) reported CO2, {years[0]} to {years[-1]} (session 492)",
            "Shape: series (docs/datastandard.md v0). entity ghgrp:<facility id>; variables co2_non_biogenic and co2_biogenic in metric tons of CO2 (tCO2), as reported; ts_utc the reporting year's 1 January; freq P1Y; x_oris the ORIS codes from EPA's crosswalk.",
            "Not taken: methane, nitrous oxide and the totals (EPA gives them in metric tons CO2e; CO2e is not in the standard's units). A blank cell has no row; nothing is filled.",
            f"Facilities: {s['entity'].nunique():,}; with an ORIS code: {s.loc[s['x_oris'] != '', 'entity'].nunique():,}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ghgrp_power.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Environmental Protection Agency, Greenhouse Gas Reporting Program, data summary spreadsheets ({last}), {PAGE}",
            f"  access: {zurl} and {curl}",
            f'License: public (a work of the U.S. government; cite "U.S. EPA, Greenhouse Gas Reporting Program, data summary {last}").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Environmental Protection Agency (EPA)",
                                    report="Greenhouse Gas Reporting Program, data summary spreadsheets", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{years[0]} to {years[-1]}: {len(s):,} rows"))
        print(f"{NAME}: {years[0]} to {years[-1]}, {len(s):,} rows, {s['entity'].nunique():,} facilities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
