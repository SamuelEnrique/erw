#!/usr/bin/env python3
"""EPA's eGRID subregions: each of the 27 eGRID subregions' nameplate capacity, net generation, CO2 and CO2-equivalent
emissions, total and non-baseload output emission rates, and resource mix, the eGRID data year (session 985, chain 055:
the regional emission factors beside egrid_power_plants' plants, from the same workbook).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/egrid_subregions_annual.csv, from the
subregion sheet (SRL<yy>) of the eGRID workbook egrid.py saves (warehouse/raw/egrid/), read again from there:

    https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_rev2.xlsx   (eGRID2023, revision 2)

    entity     egrid:<subregion acronym>; ts_utc the data year's 1 January; freq P1Y; geo empty; node the subregion's name
    variables  nameplate_capacity (MW), net_generation (MWh), co2_emissions and co2e_emissions (tCO2: eGRID's short tons
               times 0.90718474), co2_rate, co2e_rate and co2_rate_nonbaseload (kgCO2/MWh: eGRID's lb/MWh times
               0.45359237), and share_<coal|oil|gas|nuclear|hydro|biomass|wind|solar|geothermal|other_fossil|
               other_unknown|renewables|nonrenewables> (ratio: eGRID's resource mix as a fraction)

A field not in the sheet, or a subregion given twice, stops the run; eGRID's "--" has no row; nothing is filled.

    python warehouse/connectors/egrid_subregions.py [--offline]

Ceiling: one request, and none while egrid.py's saved workbook is on the machine. License: public (EPA, a U.S.
government work; license_verdicts.csv).
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "egrid_subregions_annual"
CONNECTOR = "egrid_subregions"
SAVED_BY = "egrid"
SOURCE = "epa:egrid_subregions"
PAGE = "https://www.epa.gov/egrid/download-data"
URL = "https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_rev2.xlsx"
YEAR = 2023
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHORT_TON_T, LB_KG = 0.90718474, 0.45359237
FIELDS = {"SRNAMEPCAP": ("nameplate_capacity", "MW", 1.0), "SRNGENAN": ("net_generation", "MWh", 1.0),
          "SRCO2AN": ("co2_emissions", "tCO2", SHORT_TON_T), "SRCO2EQA": ("co2e_emissions", "tCO2", SHORT_TON_T),
          "SRCO2RTA": ("co2_rate", "kgCO2/MWh", LB_KG), "SRC2ERTA": ("co2e_rate", "kgCO2/MWh", LB_KG),
          "SRNBCO2": ("co2_rate_nonbaseload", "kgCO2/MWh", LB_KG),
          "SRCLPR": ("share_coal", "ratio", 1.0), "SROLPR": ("share_oil", "ratio", 1.0), "SRGSPR": ("share_gas", "ratio", 1.0),
          "SRNCPR": ("share_nuclear", "ratio", 1.0), "SRHYPR": ("share_hydro", "ratio", 1.0), "SRBMPR": ("share_biomass", "ratio", 1.0),
          "SRWIPR": ("share_wind", "ratio", 1.0), "SRSOPR": ("share_solar", "ratio", 1.0), "SRGTPR": ("share_geothermal", "ratio", 1.0),
          "SROFPR": ("share_other_fossil", "ratio", 1.0), "SROPPR": ("share_other_unknown", "ratio", 1.0),
          "SRTRPR": ("share_renewables", "ratio", 1.0), "SRTNPR": ("share_nonrenewables", "ratio", 1.0)}


def build(frame, base):
    missing = [c for c in ["YEAR", "SUBRGN", "SRNAME"] + list(FIELDS) if c not in frame.columns]
    if missing:
        raise RuntimeError(f"fields not in the sheet: {missing}")
    if frame.SUBRGN.duplicated().any():
        raise RuntimeError("a subregion given twice")
    rows = []
    for _, r in frame.iterrows():
        if int(r["YEAR"]) != YEAR:
            raise RuntimeError(f"a row of another year: {r['YEAR']}")
        for code, (var, unit, scale) in FIELDS.items():
            v = pd.to_numeric(r[code], errors="coerce")
            if pd.isna(v):
                continue
            rows.append(dict(base, entity=f"egrid:{r['SUBRGN']}", variable=var, ts_utc=f"{YEAR}-01-01T00:00:00Z", value=round(float(v) * scale, 6),
                             unit=unit, freq="P1Y", geo="", market="", node=str(r["SRNAME"]).strip()))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPA's eGRID subregions")
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
        hit = ip.raw_cached(SAVED_BY, URL) or ip.raw_cached(CONNECTOR, URL)
        if hit:
            content, rec = hit
            log(f"  saved file reused: {rec['file']}")
        else:
            content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=600)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        frame = pd.read_excel(io.BytesIO(content), sheet_name=f"SRL{YEAR % 100:02d}", header=1)
        s = build(frame, base)
        s = s[ip.SERIES_COLS].sort_values(["entity", "variable"]).reset_index(drop=True)
        gen = s[s.variable == "net_generation"].value.sum()
        co2 = s[s.variable == "co2_emissions"].value.sum()
        header = [
            f"Energy Research Warehouse (ERW): EPA, eGRID{YEAR} subregions: nameplate capacity, net generation, CO2 and CO2e emissions, output emission rates and resource mix (session 985)",
            "Shape: series (docs/datastandard.md v0). entity egrid:<subregion>; variables nameplate_capacity (MW), net_generation (MWh), co2_emissions and "
            "co2e_emissions (tCO2: eGRID's short tons times 0.90718474), co2_rate, co2e_rate, co2_rate_nonbaseload (kgCO2/MWh: lb/MWh times 0.45359237), "
            f"share_<fuel> (ratio: the resource mix); ts_utc {YEAR}-01-01; freq P1Y; geo empty.",
            f"{s.entity.nunique()} subregions; {gen / 1e6:,.1f} TWh and {co2 / 1e6:,.1f} million tCO2 in all. eGRID's '--' has no row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/egrid_subregions.py; the workbook retrieved {base['retrieved_at']}, last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{SAVED_BY}/ (not in git; the workbook egrid.py saves)",
            f"Source: {SOURCE} U.S. Environmental Protection Agency, Emissions & Generation Resource Integrated Database (eGRID{YEAR}), subregion sheet SRL{YEAR % 100:02d}, {PAGE}",
            f"  access: {URL}",
            "License: public (a work of the U.S. government; cite EPA, eGRID).",
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Environmental Protection Agency (EPA)", report=f"eGRID{YEAR} (subregion sheet)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{NAME}: {len(s)} rows, {s.entity.nunique()} subregions, {gen / 1e6:,.1f} TWh")
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
