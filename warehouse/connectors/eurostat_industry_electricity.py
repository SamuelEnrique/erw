#!/usr/bin/env python3
"""Eurostat's energy consumption in industry by NACE Rev. 2 activity (nrg_d_indq_n), electricity only: each European
country's electricity use a year by industrial activity (mining, the manufacturing divisions and some of their groups, and
construction), from 2017 (session 2818, chain 143, the third own choice, beside eurostat_electricity_consumption_annual, which
holds industry's total from nrg_cb_e).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_industry_electricity_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), two requests: the data (about 1 MB of SDMX-CSV, electricity SIEC E7000 in GWh,
every activity and country; the key freq.unit.siec.nace_r2.geo read from the dataset's structure) and the NACE_R2 codelist:

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_d_indq_n/A.GWH.E7000..?format=SDMX-CSV&compressed=false
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NACE_R2?format=TSV

    entity      eurostat_industry_electricity:<Eurostat geo code>:<the NACE code> (TOTAL, all the activities the dataset gives)
    variable    electricity_consumption; unit MWh (Eurostat's GWh times 1,000)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank for
                EU27_2020
    node        "<geo code> industry electricity, <the NACE name>"
    x_*         Eurostat's geo and NACE codes, the observation's flag and confidentiality status

Zeros stand for splits not reported, as in eurostat_household_electricity_annual: several countries give 0 for every activity
in 2017 to 2019, and some give a division and 0 for each of its groups (Austria's chemicals, C20, 3,408 GWh in 2020 and its
six groups 0). So a country year whose every value is zero is not written, and in each group of the hierarchy (GROUPS below)
children all zero under a positive parent are not written; both are counted in the header and listed in the run log. Then each
group's children are compared with their parent within 0.5 GWh, a case that does not hold counted, kept as published. A
confidential observation (status C) or a blank has no row; any other zero is kept; nothing is filled. Checks that stop the run:
a header not Eurostat's; a frequency, unit, product or activity not expected; a value not a number, or negative; a period not a
year; a key given twice. Countries kept: the EU's members, EFTA's and the official candidates, with EU27_2020, as
eurostat_electricity_consumption_annual keeps them.

    python warehouse/connectors/eurostat_industry_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_industry_electricity/ with --offline. ec.europa.eu's robots file
disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2818,
read again, the same file as session 2813's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse
with the source acknowledged; source: Eurostat.
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

NAME = "eurostat_industry_electricity_annual"
CONNECTOR = "eurostat_industry_electricity"
SOURCE = "eurostat:nrg_d_indq_n"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_d_indq_n/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_d_indq_n/A.GWH.E7000..?format=SDMX-CSV&compressed=false"
CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NACE_R2?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "unit", "siec", "nace_r2", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
GROUPS = {"B07-B09_X_EPRD": ["B07_X_B0721", "B08_X_B0892", "B09"],
          "C10-C12": ["C10", "C11", "C12"], "C13-C15": ["C13", "C14", "C15"], "C17": ["C1711", "C17_X_C1711"],
          "C17_C18": ["C17", "C18"], "C20": ["C201", "C202", "C203", "C204", "C205", "C206"], "C20_C21": ["C20", "C21"],
          "C22_C31_C32": ["C22", "C31", "C32"], "C23": ["C231", "C235", "C23_X_C231_C235"],
          "C24": ["C241-C243_C2451_C2452", "C244_C2453_C2454"], "C25-C28": ["C25", "C26", "C27", "C28"],
          "C29_C30": ["C29", "C30"], "F": ["F41", "F42", "F43"]}
TOL = 0.5   # GWh
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_nace_r2", "x_flag", "x_conf_status"]


def nace_names(content):
    names = {}
    for line in content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        code, _, label = line.partition("\t")
        if not label:
            raise RuntimeError(f"the NACE_R2 codelist: a line without a name: {line[:80]!r}")
        names[code.strip()] = label.strip()
    if names.get("C10") != "Manufacture of food products":
        raise RuntimeError("the NACE_R2 codelist is not Eurostat's")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = (sorted(set(t0.freq) - {"A"}) + sorted(set(t0.unit) - {"GWH"}) + sorted(set(t0.siec) - {"E7000"})
           + sorted(set(t0.nace_r2) - set(names)))
    if bad:
        raise RuntimeError(f"a frequency, unit, product or activity not expected: {bad}")
    counts = {"blank": 0, "confidential": 0, "left_out_geo": sorted(set(t0.geo) - KEPT),
              "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        if v == "":
            counts["confidential" if r.CONF_STATUS.strip() == "C" else "blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.nace_r2} {r.TIME_PERIOD}: not a number: {v!r}")
        if value < 0:
            raise RuntimeError(f"{r.geo} {r.nace_r2} {r.TIME_PERIOD}: a negative value: {v!r}")
        rows.append({"entity": f"eurostat_industry_electricity:{r.geo}:{r.nace_r2}", "variable": "electricity_consumption",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": value, "unit": "MWh", "freq": "P1Y",
                     "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo), "market": "",
                     "node": f"{r.geo} industry electricity, {names[r.nace_r2]}", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_nace_r2": r.nace_r2,
                     "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    # A country year with every value zero, and children all zero under a positive parent: splits not reported.
    key = t.x_geo_code + "|" + t.ts_utc
    allzero = t.groupby(key).value.agg(lambda s: bool((s == 0).all()))
    unreported_years = sorted(allzero[allzero].index)
    drop = key.isin(unreported_years)
    v = {(g, ts, n): x for g, ts, n, x in zip(t.x_geo_code, t.ts_utc, t.x_nace_r2, t.value)}
    unreported_splits = []
    for (g, ts) in {(g, ts) for g, ts in zip(t.x_geo_code, t.ts_utc)}:
        if f"{g}|{ts}" in unreported_years:
            continue
        for parent, kids in GROUPS.items():
            got = [v[(g, ts, k)] for k in kids if (g, ts, k) in v]
            if v.get((g, ts, parent), 0) > 0 and got and all(x == 0 for x in got):
                unreported_splits.append((g, ts[:4], parent))
                drop |= (t.x_geo_code == g) & (t.ts_utc == ts) & t.x_nace_r2.isin(kids)
    counts["unreported_years"] = [k.replace("|", " ")[:7] for k in unreported_years]
    counts["unreported_splits"] = sorted(unreported_splits)
    counts["dropped"] = int(drop.sum())
    t = t[~drop]
    counts["zero"] = int((t.value == 0).sum())
    t = t.assign(value=(t.value * 1000.0).round(3))
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def checks(t):
    """Each group's children against its parent where all are given: (compared, those off by more than TOL GWh)."""
    p = t.assign(gwh=t.value / 1000.0).pivot_table(index=["x_geo_code", "ts_utc"], columns="x_nace_r2", values="gwh", aggfunc="first")
    n, off = 0, []
    for parent, kids in GROUPS.items():
        if parent not in p.columns or any(k not in p.columns for k in kids):
            continue
        x = p[[parent] + kids].dropna()
        d = x[kids].sum(axis=1) - x[parent]
        n += len(x)
        off += [(g, ts[:4], parent, round(float(e), 3)) for (g, ts), e in d[d.abs() > TOL].items()]
    return n, off


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_d_indq_n: European industry's electricity by NACE activity, a year")
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
        if not args.offline and (ip.paused("eurostat") or ip.paused_host("ec.europa.eu")):
            raise RuntimeError("Eurostat is paused (warehouse/metadata/paused_sources.csv): not requested")
        codes, _ = ip.fetch_raw(CONNECTOR, CODES_URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, pause=2, headers=UA, timeout=300)
        t, counts = build(content, nace_names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        if t.empty:
            raise RuntimeError("no observation kept")
        n, off = checks(t)
        for x in counts["unreported_years"]:
            log(f"  every value zero, not written: {x}")
        for x in counts["unreported_splits"]:
            log(f"  a split all zero under a positive parent, not written: {x}")
        for x in off:
            log(f"  children against their parent, kept as published: {x}")
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, energy consumption in industry by NACE Rev. 2 activity, electricity, annual (nrg_d_indq_n, E7000): industry's electricity use by activity, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2818)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_industry_electricity:<geo>:<NACE code>; variable electricity_consumption; unit MWh (Eurostat's GWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020; x_nace_r2 Eurostat's code. "
            "The activities overlap (divisions, their groups, and aggregates of divisions): do not sum them.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.x_nace_r2.nunique()} activities. Zeros standing for splits not reported are not written: {len(counts['unreported_years'])} country years with every value zero, and {len(counts['unreported_splits'])} groups' children all zero under a positive parent ({counts['dropped']:,} observations in all), listed in the run log. "
            f"Each group's children against its parent within {TOL:g} GWh: {n - len(off):,} of {n:,} hold, the others kept as published and listed. {counts['zero']:,} other zeros are kept; {counts['confidential']} confidential observations and {counts['blank']} blanks have no row; nothing is filled. "
            f"Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_industry_electricity.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Energy consumption in industry by NACE Rev. 2 activity, quantities (nrg_d_indq_n), {PAGE}",
            f"  access: {URL} and the activities' names from {CODES_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_d_indq_n. Eurostat bears no responsibility for this reshaping (GWh written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Energy consumption in industry by NACE Rev. 2 activity, quantities (nrg_d_indq_n)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; unreported years {len(counts['unreported_years'])}, splits {len(counts['unreported_splits'])} ({counts['dropped']} obs); groups {n - len(off)} of {n}; zeros {counts['zero']}, confidential {counts['confidential']}")
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
