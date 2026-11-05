#!/usr/bin/env python3
"""The Internal Revenue Service's Statistics of Income: the residential energy credits individuals claimed, by state and
tax year, from SOI's Historic Table 2 (session 2087, chain 068: what households were paid back for solar, batteries,
heat pumps and insulation, state by state).

Energy Research Warehouse (ERW) connector. One series table from SOI's state data files (www.irs.gov/pub/irs-soi/, one
CSV a tax year, all states and the nation, by size of adjusted gross income; the row of all incomes, AGI_STUB 0, is taken):

    https://www.irs.gov/statistics/soi-tax-stats-historic-table-2             2020 to 2023 (<yy>in55cmcsv.csv)
    https://www.irs.gov/statistics/soi-tax-stats-historic-table-2-2015-2019   2015 to 2019 (15in54cmcsv.csv,
                                                                              16in54cmcsv.csv, 17in54cmcsv.csv,
                                                                              18in55cmagi.csv, 19in55cmcsv.csv)

    irs_soi_energy_credits_annual   entity irs_soi:<SOI's state code> (the states, DC, Puerto Rico from 2018, US for SOI's
                                    own national row, OA for its other areas); variables, as SOI's workbooks name them:
                                    residential_energy_credit_returns and _amount (N07260, A07260, "Residential energy
                                    tax credit", 2015 to 2022), and from 2023, when the credit was split,
                                    residential_clean_energy_credit_returns and _amount (N07262, A07262) and
                                    energy_efficient_home_improvement_credit_returns and _amount (N07265, A07265); unit
                                    count for returns, USD for amounts (SOI's thousands of dollars times 1,000); ts_utc
                                    the tax year's first day; freq P1Y; geo US-<state>, US for the nation, empty for OA;
                                    x_soi_column

A file without STATE, AGI_STUB or a year's columns, a state given twice, or a figure not a number (commas allowed) stops
the run. Nothing is filled.

    python warehouse/connectors/irs_soi_energy.py [--offline] [--out-dir DIR]

Ceiling: nine requests (one file a year), saved in warehouse/raw/irs_soi_energy/ and reused offline. www.irs.gov's robots
file disallows only its statistics index search and site paths. License: public (a work of the U.S. government; read in
the licenses round).
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

CONNECTOR = "irs_soi_energy"
SOURCE = "irs:soi_historic_table_2"
BASE_URL = "https://www.irs.gov/pub/irs-soi/"
PAGE = "https://www.irs.gov/statistics/soi-tax-stats-historic-table-2"
FILES = {2015: "15in54cmcsv.csv", 2016: "16in54cmcsv.csv", 2017: "17in54cmcsv.csv", 2018: "18in55cmagi.csv", 2019: "19in55cmcsv.csv",
         2020: "20in55cmcsv.csv", 2021: "21in55cmcsv.csv", 2022: "22in55cmcsv.csv", 2023: "23in55cmcsv.csv"}
# the credits SOI tabulates, a year's columns: (variable stem, number column, amount column)
COLUMNS = {y: [("residential_energy_credit", "N07260", "A07260")] for y in range(2015, 2023)}
COLUMNS[2023] = [("residential_clean_energy_credit", "N07262", "A07262"), ("energy_efficient_home_improvement_credit", "N07265", "A07265")]
TABLE = "irs_soi_energy_credits_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_soi_column"]


def number(s, what):
    t = s.replace(",", "").strip()
    if not re.fullmatch(r"-?\d+(\.\d+)?", t):
        raise RuntimeError(f"{what}: not a number: {s!r}")
    return float(t)


def read_year(content, year, base):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False, encoding="latin-1")
    d.columns = [c.strip().upper() for c in d.columns]
    need = ["STATE", "AGI_STUB"] + [c for _, n, a in COLUMNS[year] for c in (n, a)]
    miss = [c for c in need if c not in d.columns]
    if miss:
        raise RuntimeError(f"{year}: no column {miss}")
    d = d[d.AGI_STUB.str.strip() == "0"]
    if d.STATE.duplicated().any():
        raise RuntimeError(f"{year}: a state given twice")
    rows = []
    for _, r in d.iterrows():
        st = r.STATE.strip()
        if not re.fullmatch(r"[A-Z]{2}", st):
            raise RuntimeError(f"{year}: a state code not of two letters: {st!r}")
        geo = "US" if st == "US" else "" if st == "OA" else f"US-{st}"
        for stem, ncol, acol in COLUMNS[year]:
            for var, col, unit, scale in ((f"{stem}_returns", ncol, "count", 1), (f"{stem}_amount", acol, "USD", 1000)):
                v = number(r[col], f"{year} {st} {col}") * scale
                rows.append(dict(entity=f"irs_soi:{st}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=v, unit=unit, freq="P1Y",
                                 geo=geo, market="", node=st, **base, x_soi_column=col))
    if not rows:
        raise RuntimeError(f"{year}: no row of all incomes")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="IRS SOI: residential energy credits by state and tax year")
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
        rows = []
        for year, name in FILES.items():
            url = BASE_URL + name
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120, pause=1)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            rows += read_year(content, year, base)
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a state, variable and year given twice")
        s["value"] = s["value"].map(lambda v: f"{v:.0f}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): Internal Revenue Service, Statistics of Income, Historic Table 2 (individual income and tax data by "
            "state): the residential energy credits claimed, tax years 2015 to 2023, all incomes (session 2087)",
            "Shape: series (docs/datastandard.md v0). entity irs_soi:<SOI's state code> (US: SOI's own national row; OA: its other areas); "
            "variables residential_energy_credit_returns and _amount (N07260, A07260, 2015 to 2022), and for 2023, when the credit was split, "
            "residential_clean_energy_credit_* (N07262, A07262) and energy_efficient_home_improvement_credit_* (N07265, A07265); unit count for "
            "returns, USD for amounts (SOI's thousands of dollars times 1,000); ts_utc the tax year's first day; freq P1Y; geo US-<state>, US, or "
            "empty for OA; x_soi_column SOI's column.",
            f"{len(s)} rows, {s.entity.nunique()} places, tax years 2015 to 2023. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/irs_soi_energy.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Internal Revenue Service, SOI Tax Stats, Historic Table 2, {PAGE}",
            "  access: " + "; ".join(f"{y} {BASE_URL}{n}" for y, n in FILES.items()),
            'License: public (a work of the U.S. government; cite "Internal Revenue Service, Statistics of Income").',
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} places")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Internal Revenue Service (IRS), Statistics of Income",
                                    report="SOI Tax Stats: Historic Table 2, individual income and tax data by state", report_url=PAGE,
                                    document_list=BASE_URL, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
