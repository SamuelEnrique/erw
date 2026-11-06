#!/usr/bin/env python3
"""EIA's Uranium Marketing Annual Report, its summary tables: the uranium U.S. reactor owners and operators bought (by
seller, origin and contract type) and its price, their feed deliveries, enrichment services and loadings, and foreign
purchases, sales and inventories, a year from 2003 (session 904, chain 049: a public source the ERW did not hold, the fuel
of the nuclear fleet).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_uranium_marketing_annual.csv, from five
workbooks linked from https://www.eia.gov/uranium/marketing/ (Form EIA-858, Uranium Marketing Annual Survey):

    xls/umartableS1afigureS1.xlsx    S1a: uranium purchased (million pounds U3O8 equivalent)
    xls/umartableS1bfigureS2.xlsx    S1b: its weighted-average price (dollars per pound U3O8 equivalent)
    xls/umartableS2figuresS3n4.xlsx  S2: feed deliveries and uranium loaded (million pounds), enrichment services
                                     purchased (million SWU) and their average price (dollars per SWU)
    xls/umartableS3afigureS5.xlsx    S3a: foreign purchases, foreign sales and commercial inventories (million pounds)
    xls/umartableS3bfigureS6.xlsx    S3b: the weighted-average prices of foreign purchases and sales (dollars per pound)

    entity    eia_uranium:us; variable each column's meaning (purchased_total, price_purchased_spot, feed_deliveries,
              enrichment_total, inventories_total and the rest, mapped by heading below); unit lb (EIA's million pounds of
              U3O8 equivalent times 1,000,000), USD/lb, SWU (million SWU times 1,000,000) or USD/SWU (Decision 55);
              ts_utc the delivery year's 1 January; freq P1Y; geo US; node EIA's column heading

A value EIA withholds ("W") or does not give ("-", "- -", "NA") has no row; nothing is filled. A heading the map does not
know stops the run. EIA notes that totals may not equal the sum of their parts because of independent rounding, and that
average prices are not adjusted for inflation.

    python warehouse/connectors/eia_uranium_marketing.py [--offline]

Ceiling: five requests (the workbooks; saved in warehouse/raw/eia_uranium_marketing/ and reused offline). EIA's robots
file allows /uranium/marketing/. License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Uranium Marketing Annual Report").
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

NAME = "eia_uranium_marketing_annual"
CONNECTOR = "eia_uranium_marketing"
SOURCE = "eia:uranium_marketing_annual"
PAGE = "https://www.eia.gov/uranium/marketing/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SELLERS = [("Total purchased", "total"), ("Purchased from U.S. producers", "from_us_producers"),
           ("Purchased from U.S. brokers and traders", "from_us_brokers_traders"),
           ("Purchased from other owners and operators", "from_other_owners_suppliers"),
           ("Purchased from foreign suppliers", "from_foreign_suppliers"), ("U.S.-origin uranium", "us_origin"),
           ("Foreign-origin uranium", "foreign_origin"), ("Spot contracts", "spot"), ("Long-term contracts", "long_term")]
FOREIGN = [("Foreign purchases by U.S. suppliers", "foreign_purchases_us_suppliers"),
           ("Foreign purchases by owners and operators", "foreign_purchases_owners"), ("Total foreign purchases", "foreign_purchases_total"),
           ("U.S. broker and trader purchases from foreign suppliers", "broker_purchases_from_foreign"), ("Foreign sales", "foreign_sales")]
TABLES = {
    "umartableS1afigureS1.xlsx": [(h, f"purchased_{v}", "lb", 1e6) for h, v in SELLERS],
    "umartableS1bfigureS2.xlsx": [(h, f"price_purchased_{v}", "USD/lb", 1.0) for h, v in SELLERS],
    "umartableS2figuresS3n4.xlsx": [("Feed deliveries", "feed_deliveries", "lb", 1e6),
                                    ("Uranium in fuel assemblies loaded", "uranium_loaded", "lb", 1e6),
                                    ("U.S.-origin enrichment services", "enrichment_us_origin", "SWU", 1e6),
                                    ("Foreign-origin enrichment services", "enrichment_foreign_origin", "SWU", 1e6),
                                    ("Total purchased enrichment services", "enrichment_total", "SWU", 1e6),
                                    ("Average price (US$ per SWU)", "enrichment_price", "USD/SWU", 1.0)],
    "umartableS3afigureS5.xlsx": [(h, v, "lb", 1e6) for h, v in FOREIGN] + [
        ("U.S. supplier owned uranium inventories", "inventories_us_suppliers", "lb", 1e6),
        ("Owners and operators of U.S. civilian nuclear power reactors owned uranium inventories", "inventories_owners", "lb", 1e6),
        ("Total commercial uranium inventories", "inventories_total", "lb", 1e6)],
    "umartableS3bfigureS6.xlsx": [(h, f"price_{v}", "USD/lb", 1.0) for h, v in FOREIGN],
}


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def sheet_rows(frame, fname, url, retrieved):
    heads = [r for r in range(min(12, len(frame))) if text(frame.iloc[r, 0]) in ("Delivery year", "Year")]
    if not heads:
        raise RuntimeError(f"{fname}: no heading row")
    hr = heads[0]
    spec = TABLES[fname]
    cols = {}
    for c in range(1, frame.shape[1]):
        h = text(frame.iloc[hr, c])
        if not h:
            continue
        hit = [s for s in spec if h.startswith(s[0])]
        if len(hit) != 1:
            raise RuntimeError(f"{fname}: a heading not in the map: {h!r}")
        cols[c] = hit[0] + (h,)
    if len(cols) != len(spec):
        raise RuntimeError(f"{fname}: {len(cols)} columns found, not {len(spec)}")
    out = []
    for _, r in frame.iloc[hr + 1:].iterrows():
        y = text(r[0])
        if not re.fullmatch(r"\d{4}", y):
            continue
        for c, (_, var, unit, scale, heading) in cols.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(entity="eia_uranium:us", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=float(v) * scale, unit=unit,
                            freq="P1Y", geo="US", market="", node=heading, source=SOURCE, source_url=url, retrieved_at=retrieved,
                            vintage=""))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's Uranium Marketing Annual Report, its summary tables")
    ap.add_argument("--offline", action="store_true", help="the saved workbooks only, no request")
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
        rows, got = [], []
        for fname in TABLES:
            url = f"{PAGE}xls/{fname}"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120)
            got_rows = sheet_rows(pd.read_excel(io.BytesIO(content), header=None), fname, url, rec.get("retrieved_at") or "")
            log(f"{fname}: {len(got_rows):,} rows")
            rows += got_rows
            got.append(f"{url} (retrieved {rec.get('retrieved_at', '')})")
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        s = s[ip.SERIES_COLS].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        header = [
            "Energy Research Warehouse (ERW): EIA, Uranium Marketing Annual Report, the summary tables: uranium bought by U.S. reactor owners and operators, its price, feed, enrichment, loadings, foreign trade and inventories (session 904)",
            "Shape: series (docs/datastandard.md v0). entity eia_uranium:us; variable the column's meaning (purchased_<seller or origin or contract>, price_purchased_<...>, "
            "feed_deliveries, uranium_loaded, enrichment_<origin or total>, enrichment_price, foreign_purchases_<...>, foreign_sales, broker_purchases_from_foreign, "
            "inventories_<...>, price_<...>); unit lb (pounds of U3O8 equivalent: EIA's million pounds times 1,000,000), USD/lb, SWU (million SWU times 1,000,000), "
            "USD/SWU (Decision 55); ts_utc the delivery year's 1 January; freq P1Y; geo US; node EIA's heading.",
            f"Years {s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}; {len(s):,} rows. W (withheld) and - have no row; nothing is filled. EIA: totals may not equal "
            "the sum of components because of independent rounding; prices are not adjusted for inflation.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_uranium_marketing.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Uranium Marketing Annual Report (Form EIA-858), tables S1a to S3b, {PAGE}",
            f"  access: {'; '.join(got)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Uranium Marketing Annual Report").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Uranium Marketing Annual Report (Form EIA-858), summary tables", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows")
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
