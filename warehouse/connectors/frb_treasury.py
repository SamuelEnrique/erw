#!/usr/bin/env python3
"""US Treasury yields at 2, 10 and 30 years, daily, from the Federal Reserve Board's own H.15 data download (session 207).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/frb_treasury_yields.csv: the market yield
on U.S. Treasury securities at 2-year, 10-year and 30-year constant maturity, quoted on an investment basis, percent a
year, by business day from 2019-01-01. The numbers are the Board of Governors of the Federal Reserve System's (release
H.15, Selected Interest Rates), read from the Board's Data Download Program, the preformatted package "Treasury Constant
Maturities" (CSV, every maturity, all observations), one request a run:
    https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&...
Entities are frb:tcm_2y, frb:tcm_10y and frb:tcm_30y; node is the Board's unique identifier of the column
(H15/H15/RIFLGFCY02_N.B, ..._10_N.B, ..._30_N.B). The other eight maturities in the package are read and not written.

    python warehouse/connectors/frb_treasury.py [--out-dir DIR]

Session 207 (the owner's ruling of 12 October 2026, docs/licenses.md): the same three series were held until then as
fred_treasury_yields, read through FRED (Federal Reserve Bank of St. Louis), whose terms forbid storing FRED content
without the Bank's written consent. The Board's own release is a work of a U.S. government agency, public domain. The
check of 13 October 2026 (archive/sessions/SESSION_207_REPORT.md): every value of the FRED copy equals the Board's for
the same day and maturity. Cite: Board of Governors of the Federal Reserve System (US), H.15 Selected Interest Rates.

The Board writes "ND" for a business day with no value (a market holiday): such a day is not written and is counted.
Nothing is filled. The table is written only if its newest day is within STALE_DAYS. Note (the Board's page, read
13 October 2026): the Board plans to retire the "Build Your Package" option of its Data Download Program the week of
9 November 2026 and points users to FRED; the preformatted package this reads is not named in that notice. If the
address stops answering, the step fails loudly and the table stays as it was.
"""
import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

CONNECTOR = "frb_treasury"
NAME = "frb_treasury_yields"
START = "2019-01-01"
STALE_DAYS = 10
PACKAGE = "bf17364827e38702b42a58cf8eaa3f78"  # the Board's preformatted package "Treasury Constant Maturities", H.15
URL = (f"https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series={PACKAGE}&lastobs=&from=01/01/2019"
       "&to=12/31/2099&filetype=csv&label=include&layout=seriescolumn")
RELEASE = "https://www.federalreserve.gov/releases/h15/"
# the Board's series identifier (the CSV's column) -> (entity, the maturity in words)
SERIES = {"RIFLGFCY02_N.B": ("frb:tcm_2y", "2-year"), "RIFLGFCY10_N.B": ("frb:tcm_10y", "10-year"),
          "RIFLGFCY30_N.B": ("frb:tcm_30y", "30-year")}
# the Board's server answers an empty body to a request without a browser-like agent (13 October 2026)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ERW data machine; Energy Research Warehouse, github.com/SamuelEnrique/erw)"}
SOURCE_ENTRY = dict(source="frb:h15_treasury_yields", publisher="Board of Governors of the Federal Reserve System",
                    report="H.15 Selected Interest Rates: market yield on U.S. Treasury securities at constant maturity, "
                           "the Data Download Program's package Treasury Constant Maturities (daily)",
                    report_url=RELEASE, document_list="https://www.federalreserve.gov/datadownload/Choose.aspx?rel=H15",
                    license="public", tables=[NAME])


def parse(text, url, retrieved):
    """The Board's package CSV as the table's rows, and the number of business days listed with no value (ND)."""
    lines = text.splitlines()
    head = [i for i, ln in enumerate(lines) if ln.startswith('"Time Period"')]
    if not head:
        raise RuntimeError("the Board's CSV has no 'Time Period' row")
    ids = next(csv_row for csv_row in (pd.read_csv(io.StringIO(ln), header=None).iloc[0].tolist() for ln in lines if ln.startswith('"Unique Identifier: "')))
    df = pd.read_csv(io.StringIO("\n".join(lines[head[0]:])), dtype=str, keep_default_na=False)
    missing = [sid for sid in SERIES if sid not in df.columns]
    if missing:
        raise RuntimeError(f"the Board's columns {list(df.columns)} lack {missing}")
    frames, empty = [], 0
    for sid, (entity, words) in SERIES.items():
        col = df[sid].str.strip()
        blank = col.isin(["", "ND"])
        value = pd.to_numeric(col.where(~blank), errors="coerce")
        bad = df[value.isna() & ~blank]
        if len(bad):
            raise RuntimeError(f"{sid}: values that are not numbers {list(bad[sid].unique()[:5])}")
        keep = value.notna()
        uid = next((u for u in ids if isinstance(u, str) and u.endswith("/" + sid)), f"H15/H15/{sid}")
        frames.append(pd.DataFrame({
            "entity": entity, "variable": "yield",
            "ts_utc": pd.to_datetime(df.loc[keep, "Time Period"]).dt.strftime("%Y-%m-%dT00:00:00Z").values,
            "value": value[keep].values, "unit": "pct", "freq": "P1D", "geo": "US", "market": "", "node": uid,
            "source": SOURCE_ENTRY["source"], "source_url": url, "retrieved_at": retrieved, "vintage": "",
        }))
        empty += int((~keep).sum())
    return pd.concat(frames, ignore_index=True), empty, len(df)


def build(run_id, log):
    content, rec = ip.fetch_raw(CONNECTOR, URL, log, fresh=True, pause=1, headers=HEADERS)
    if not content:
        raise RuntimeError("the Board answered an empty body")
    table, empty, days = parse(content.decode("utf-8"), URL, rec["retrieved_at"])
    table = table[table["ts_utc"] >= f"{START}T00:00:00Z"]
    for sid, (entity, words) in SERIES.items():
        t = table[table["entity"] == entity]
        log(f"  {sid} ({words}): {len(t)} values, newest {t['ts_utc'].max()[:10]}")
    age = (pd.Timestamp.now(tz="UTC") - pd.Timestamp(table["ts_utc"].max())).days
    if age > STALE_DAYS:
        raise RuntimeError(f"the newest day the Board holds is {table['ts_utc'].max()[:10]}, {age} days old (limit {STALE_DAYS})")
    header = [
        "Energy Research Warehouse (ERW): US Treasury yields at 2, 10 and 30 years, constant maturity, daily from 2019 (session 207)",
        "Shape: series (docs/datastandard.md v0). yield: the market yield on U.S. Treasury securities at constant maturity, quoted on an investment basis, percent a year (unit pct); ts_utc is the business day at 00:00:00Z; freq P1D. node is the Board's series identifier.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/frb_treasury.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Source: {SOURCE_ENTRY['source']} {SOURCE_ENTRY['publisher']}, {SOURCE_ENTRY['report']}, {RELEASE}",
        f"  access: {URL}",
        f"Rows read: {days:,} business days of 11 maturities; the three written: " + ", ".join(SERIES)
        + f". Business days the Board lists with no value (ND, market holidays) among the three, not written: {empty}. Nothing is filled.",
        "Replaces fred_treasury_yields (the same series through FRED, retired by session 207 on the owner's ruling of 12 October 2026: FRED's terms forbid storing its content).",
        "License: public. A work of the Board of Governors of the Federal Reserve System, a U.S. government agency. Cite: Board of Governors of the Federal Reserve System (US), H.15 Selected Interest Rates.",
    ]
    return table, header, f"{days} business days read, {empty} ND among the three series"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    try:
        ip.RAW.open(CONNECTOR, run_id)
        table, header, note = build(run_id, log)
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)     # the whole history from START is read each run, so revisions are picked up
        ip.write_csv(table[ip.SERIES_COLS], NAME, header, log)
        if not args.out_dir:
            ip.update_sources([SOURCE_ENTRY])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(table)} rows; {note}"))
        print(f"{NAME}: {len(table):,} values, newest {table['ts_utc'].max()[:10]}; {note}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{CONNECTOR} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
