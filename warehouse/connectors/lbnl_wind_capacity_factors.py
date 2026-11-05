#!/usr/bin/env python3
"""Berkeley Lab's wind project capacity factors: each land-based wind plant's capacity factor in calendar year 2025, with
its commercial operation period and whether it was repowered (session 944, chain 053: the performance side of
lbnl_ppa_prices' wind contracts, from the same data file).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/lbnl_wind_capacity_factors.csv, from the
"Capacity Factor in 2025 by COD" sheet of LBNL's Land-Based Wind Energy Technology Data Update, 2026 Edition, the data
file lbnl_ppa_prices.py saves (warehouse/raw/lbnl_ppa_prices/), read again from there:

    https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx

    entity    lbnl_wind:<EIA plant code>; variable capacity_factor (unit ratio, a fraction, as LBNL gives it); ts_utc
              2025-01-01; freq P1Y; geo US; node "EIA plant <code>"
    x_*       x_cod (LBNL's commercial operation year or period, 1998-99 and the years after), x_repower (partial repower,
              full repower or empty)

LBNL names no project, only its EIA plant code. A heading not as read or a plant given twice stops the run; nothing is
filled.

    python warehouse/connectors/lbnl_wind_capacity_factors.py [--offline]

Ceiling: one request, and none while lbnl_ppa_prices' saved file is on the machine. License: CC BY 4.0, as the file's
copyright notice states; cite Berkeley Lab.
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

NAME = "lbnl_wind_capacity_factors"
CONNECTOR = "lbnl_wind_capacity_factors"
SAVED_BY = "lbnl_ppa_prices"
SOURCE = "lbnl:wind_capacity_factors"
PAGE = "https://eta-publications.lbl.gov/publications/land-based-wind-energy-technology-0"
URL = "https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEET = "Capacity Factor in 2025 by COD"
X_COLS = ["x_cod", "x_repower"]


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def rows(frame, base):
    h = None
    for i in range(min(40, len(frame))):
        if text(frame.iloc[i, 12]) == "Code" and text(frame.iloc[i, 13]) == "Repower":
            h = i
            break
    if h is None or text(frame.iloc[h - 2, 10]) != "2025" or text(frame.iloc[h, 10]) != "Factor" or text(frame.iloc[h, 11]) != "COD":
        raise RuntimeError("the sheet's project columns (2025 Capacity Factor, Project COD, EIA Plant Code, Repower) are not as read")
    out, seen = [], set()
    for _, r in frame.iloc[h + 1:].iterrows():
        code = text(r.iloc[12])
        if not code:
            continue
        code = code[:-2] if code.endswith(".0") else code
        if code in seen:
            raise RuntimeError(f"an EIA plant code given twice: {code}")
        seen.add(code)
        v = pd.to_numeric(r.iloc[10], errors="coerce")
        if pd.isna(v):
            continue
        out.append(dict(base, entity=f"lbnl_wind:{code}", variable="capacity_factor", ts_utc="2025-01-01T00:00:00Z", value=float(v), unit="ratio",
                        freq="P1Y", geo="US", market="", node=f"EIA plant {code}", x_cod=text(r.iloc[11]).replace(".0", ""),
                        x_repower=text(r.iloc[13])))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Berkeley Lab's wind plants' 2025 capacity factors")
    ap.add_argument("--offline", action="store_true", help="the saved data file only, no request")
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
        if content[:2] != b"PK":
            raise RuntimeError(f"{URL} is not a workbook")
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        s = pd.DataFrame(rows(pd.read_excel(io.BytesIO(content), sheet_name=SHEET, header=None), base))
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values("entity").reset_index(drop=True)
        rep = s.x_repower.value_counts().to_dict()
        header = [
            "Energy Research Warehouse (ERW): Berkeley Lab, land-based wind plants' capacity factors in calendar year 2025 (Land-Based Wind Energy Technology Data Update, 2026 Edition) (session 944)",
            "Shape: series (docs/datastandard.md v0). entity lbnl_wind:<EIA plant code>; variable capacity_factor (unit ratio: a fraction); ts_utc "
            "2025-01-01; freq P1Y; geo US; x_cod LBNL's commercial operation year or period; x_repower partial repower, full repower or empty.",
            f"{len(s):,} plants (repowered: {', '.join(f'{v} {k}' for k, v in rep.items() if k)}); median capacity factor {s.value.median():.3f}. "
            "LBNL names no project, only its EIA plant code. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/lbnl_wind_capacity_factors.py; the data file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{SAVED_BY}/ (not in git; the file lbnl_ppa_prices.py saves)",
            f"Source: {SOURCE} Lawrence Berkeley National Laboratory, Land-Based Wind Energy Technology Data Update, 2026 Edition (August 2026), sheet '{SHEET}', {PAGE}",
            f"  access: {URL}",
            "License: CC BY 4.0, as the data file's copyright notice states; cite Berkeley Lab and the report.",
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Lawrence Berkeley National Laboratory (Berkeley Lab)",
                                    report="Land-Based Wind Energy Technology Data Update (Capacity Factor in 2025 by COD)", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} plants"))
        print(f"{NAME}: {len(s):,} plants")
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
