#!/usr/bin/env python3
"""NLR (formerly NREL) Annual Technology Baseline: each electricity technology's projected costs, by year (session 487,
the owner's instruction of 21 October 2026).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nlr_atb_electricity_costs.csv, from the
National Laboratory of the Rockies' (NLR, formerly NREL) Electricity Annual Technology Baseline (ATB), its flat file in
the Open Energy Data Initiative's public bucket:

    https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/<atb year>/<version>/ATBe.parquet
    (the newest year and version the bucket lists; 2025 v1.0.0 on 21 October 2026)

    entity    nlr_atb_<atb year>:<technology>:<detail>:<scenario>, lower case: the ATB's technology, its techdetail,
              techdetail2, resourcedetail and scale joined, and its scenario (advanced, moderate, conservative)
    variable  capex (USD/kW), occ (overnight capital cost, USD/kW), fixed_om (USD/kW-year), variable_om (USD/MWh),
              fuel (USD/MWh), capacity_factor (ratio), lcoe (USD/MWh)
    ts_utc    the projection year's 1 January (2023 to 2050 and beyond, as the ATB gives); freq P1Y
    x_*       the ATB's own fields (technology, details, scale, scenario, its display name, default flag, maturity)

The ATB's default view only, as session 312 read its workbook: the R&D cost case (no tax credits) and a 30-year cost
recovery period. The rows repeat for each recovery period wherever the value does not depend on it (CAPEX, O&M), so one
period is enough, and 30 years exists for every technology. Values are the ATB's, in its dollar year (2023 dollars for the
2025 ATB, as its workbook says): nothing is converted, filled or interpolated. A key repeated stops the run.

    python warehouse/connectors/nlr_atb_costs.py

Ceiling: two requests (the bucket's listing and the file; a file already in warehouse/raw/nlr_atb_costs/ is reused).
License: public with credit (NLR's data terms, read 19 October 2026 and kept in warehouse/raw/nlr_atb/terms/: use and copy
without fee, the notice kept and DOE/NLR credited; cite "NLR (formerly NREL), <year> Electricity Annual Technology
Baseline").
"""

import argparse
import datetime as dt
import email.utils
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "nlr_atb_electricity_costs"
CONNECTOR = "nlr_atb_costs"
SOURCE = "nlr:atb_electricity"
PAGE = "https://atb.nrel.gov/electricity/"
BUCKET = "https://oedi-data-lake.s3.amazonaws.com/"
LIST = BUCKET + "?list-type=2&prefix=ATB/electricity/parquet/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CASE, CRP = "R&D", 30
DOLLAR_YEAR = {2025: 2023}   # the ATB's dollar year, as its workbook states it (session 312)
PARAMS = {"CAPEX": ("capex", "USD/kW"), "OCC": ("occ", "USD/kW"), "Fixed O&M": ("fixed_om", "USD/kW-year"),
          "Variable O&M": ("variable_om", "USD/MWh"), "Fuel": ("fuel", "USD/MWh"), "CF": ("capacity_factor", "ratio"),
          "LCOE": ("lcoe", "USD/MWh")}
X_COLS = ["x_technology", "x_techdetail", "x_techdetail2", "x_resourcedetail", "x_scale", "x_scenario", "x_display_name",
          "x_default", "x_maturity", "x_case", "x_crp_years", "x_dollar_year", "x_atb_version"]


def newest_key(listing_xml):
    """The newest ATBe.parquet in the bucket's listing: the highest year, then the highest version."""
    keys = re.findall(r"<Key>(ATB/electricity/parquet/(\d{4})/v(\d+)\.(\d+)\.(\d+)/ATBe\.parquet)</Key>", listing_xml)
    if not keys:
        raise RuntimeError("the bucket lists no ATB/electricity/parquet/<year>/<version>/ATBe.parquet")
    k = max(keys, key=lambda x: tuple(int(v) for v in x[1:]))
    return k[0], int(k[1]), f"v{k[2]}.{k[3]}.{k[4]}"


def slug(*parts):
    s = ":".join(re.sub(r"[^a-z0-9]+", "_", str(p).lower()).strip("_") for p in parts if str(p) not in ("", "None", "nan"))
    return re.sub(r"_+", "_", s)


def rows(d, atb_year, url, retrieved, version, vintage=""):
    k = d[d["core_metric_parameter"].isin(PARAMS) & d["core_metric_case"].eq(CASE)
          & pd.to_numeric(d["crpyears"], errors="coerce").eq(CRP)].copy()
    if k.empty:
        raise RuntimeError(f"ATB {atb_year}: no row of the {CASE} case at {CRP} years")
    detail = k.apply(lambda r: slug(r["techdetail"], r["techdetail2"] if r["techdetail2"] != r["techdetail"] else "",
                                    r["resourcedetail"] if r["resourcedetail"] not in (r["techdetail"], r["techdetail2"]) else "", r["scale"]), axis=1)
    out = pd.DataFrame({
        "entity": f"nlr_atb_{atb_year}:" + k["technology"].map(lambda t: slug(t)) + ":" + detail + ":" + k["scenario"].map(lambda s: slug(s)),
        "variable": k["core_metric_parameter"].map(lambda p: PARAMS[p][0]),
        "ts_utc": pd.to_numeric(k["core_metric_variable"]).astype(int).astype(str) + "-01-01T00:00:00Z",
        "value": pd.to_numeric(k["value"], errors="coerce"), "unit": k["core_metric_parameter"].map(lambda p: PARAMS[p][1]),
        "freq": "P1Y", "geo": "US", "market": "", "node": k["display_name"].fillna(""), "source": SOURCE, "source_url": url,
        "retrieved_at": retrieved, "vintage": vintage,
        "x_technology": k["technology"], "x_techdetail": k["techdetail"].fillna(""), "x_techdetail2": k["techdetail2"].fillna(""),
        "x_resourcedetail": k["resourcedetail"].fillna(""), "x_scale": k["scale"].fillna(""), "x_scenario": k["scenario"],
        "x_display_name": k["display_name"].fillna(""), "x_default": k["default"].astype(str), "x_maturity": k["maturity"].astype(str),
        "x_case": CASE, "x_crp_years": str(CRP), "x_dollar_year": str(DOLLAR_YEAR.get(atb_year, "")), "x_atb_version": f"{atb_year} {version}",
    })
    out = out[out["value"].notna()]
    if out.duplicated(["entity", "variable", "ts_utc"]).any():
        dup = out[out.duplicated(["entity", "variable", "ts_utc"], keep=False)].head(3)
        raise RuntimeError(f"ATB {atb_year}: an (entity, variable, ts_utc) is given twice: {dup[['entity', 'variable', 'ts_utc']].values.tolist()}")
    return out.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NLR ATB: electricity technologies' projected costs, by year")
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
        listing, _ = ip.fetch_raw(CONNECTOR, LIST, log, fresh=True, headers=UA)
        key, atb_year, version = newest_key(listing.decode("utf-8", errors="replace"))
        if atb_year not in DOLLAR_YEAR:
            raise RuntimeError(f"ATB {atb_year}: its dollar year is not recorded in DOLLAR_YEAR; read it from the ATB first")
        url = BUCKET + key
        content, rec = ip.fetch_raw(CONNECTOR, url, log, headers=UA, timeout=600)
        lm = rec.get("last_modified") or ""  # the file's publication time (Last-Modified), as the vintage
        vintage = email.utils.parsedate_to_datetime(lm).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if lm else ""
        s = rows(pd.read_parquet(io.BytesIO(content)), atb_year, url, rec["retrieved_at"], version, vintage)
        s = s[ip.SERIES_COLS + X_COLS]
        header = [
            f"Energy Research Warehouse (ERW): NLR (formerly NREL) {atb_year} Electricity Annual Technology Baseline, projected costs by technology and year (session 487)",
            f"Shape: series (docs/datastandard.md v0). entity nlr_atb_{atb_year}:<technology>:<detail>:<scenario>; variables capex and occ (USD/kW), fixed_om (USD/kW-year), variable_om, fuel and lcoe (USD/MWh), capacity_factor (ratio); ts_utc the projection year's 1 January; freq P1Y; node the ATB's display name.",
            f"The ATB's default view: the {CASE} cost case (no tax credits) and a {CRP}-year cost recovery period. Dollars of {DOLLAR_YEAR[atb_year]}, as the ATB gives them; nothing converted, filled or interpolated.",
            f"Technologies {s['x_technology'].nunique()}, entities {s['entity'].nunique():,}, years {s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nlr_atb_costs.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} National Laboratory of the Rockies (NLR, formerly NREL), {atb_year} Electricity Annual Technology Baseline (ATB) {version}, {PAGE}",
            f"  access: {url}",
            f'License: public with credit (NLR data terms; cite "NLR (formerly NREL), {atb_year} Electricity Annual Technology Baseline").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="National Laboratory of the Rockies (NLR, formerly NREL)",
                                    report="Electricity Annual Technology Baseline (ATB), flat file", report_url=PAGE,
                                    document_list=LIST, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"ATB {atb_year} {version}: {len(s):,} rows"))
        print(f"{NAME}: ATB {atb_year} {version}, {len(s):,} rows, {s['entity'].nunique():,} entities, {s['x_technology'].nunique()} technologies")
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
