#!/usr/bin/env python3
"""Great Britain's electricity demand a day, as Elexon's Balancing Mechanism Reporting Service publishes it: the Initial
National Demand Outturn per day (INDOD), from 2020 (session 2162, chain 094: Great Britain's grid beside the U.S. ones,
in place of NESO's data portal, whose file host api.neso.energy disallows every reader in its robots file).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/elexon_gb_demand_daily.csv, from the BMRS
Insights API (no key), one request a window of at most two years (the endpoint's limit is 731 days):

    https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/daily?settlementDateFrom=<from>&settlementDateTo=<to>&format=csv

The answer is "PublishTime,SettlementDate,Demand", one line a settlement day. The API's own description: "The total daily
energy volume is the total demand volume for the previous day expressed on an initial National Demand outturn (INDO)
basis, i.e. excluding station transformer, pumping and interconnector export demand. It is calculated from summing the
half hourly INDO demands (divided by two to convert to MWh)." Embedded generation that the transmission system does not
see is not in it. The endpoint's daily series begins on 27 April 2021 (the first window, asked from 1 January 2020,
answers from then), and in October 2026 it gave no figure for 74 days between that day and the end of 2022, most of
May and June 2021 among them; the header counts the days without a figure.

    entity      elexon:GB; variable indo_daily; unit MWh; freq P1D; geo GB (ISO 3166's code for the United Kingdom, the
                nearest the standard has: the figure covers Great Britain, without Northern Ireland)
    ts_utc      the settlement day at 00:00:00Z (Decision 11, as EIA-930's daily tables write a day); the settlement day
                is Great Britain's own day (Europe/London), which begins at 23:00Z the day before in summer time
    x_*         the settlement date as Elexon gives it, and the time Elexon published the day's figure

Values as published; a day Elexon gives no figure for has no row; nothing is filled. A header not the endpoint's, a date
not YYYY-MM-DD, a value that is not a whole number or a day given twice stops the run. Prices are not taken (GBP is a
standing question for the owner).

    python warehouse/connectors/elexon_demand.py [--end YYYY-MM-DD] [--offline] [--out-dir DIR]

Ceiling: four requests (2020 to 2021, 2022 to 2023, 2024 to 2025, 2026 to the day before --end), each reused from
warehouse/raw/elexon_demand/ with --offline. data.elexon.co.uk has no robots file (HTTP 404, session 2162). License:
Elexon's licence to use BMRS open data (copy, publish, distribute, adapt and exploit, commercially too, with the
attribution "Contains BMRS data (c) Elexon Limited copyright and database right [year]" and, where possible, a link to
the licence), written in the header word for word.
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

NAME = "elexon_gb_demand_daily"
CONNECTOR = "elexon_demand"
SOURCE = "elexon:indod"
PAGE = "https://bmrs.elexon.co.uk/"
API = "https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/daily?settlementDateFrom={a}&settlementDateTo={b}&format=csv"
LICENCE = "https://www.elexon.co.uk/bsc/data/balancing-mechanism-reporting-agent/copyright-licence-bmrs-data/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
WINDOWS = [("2020-01-01", "2021-12-31"), ("2022-01-01", "2023-12-31"), ("2024-01-01", "2025-12-31"), ("2026-01-01", None)]
HEADER = ["PublishTime", "SettlementDate", "Demand"]
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_settlement_date", "x_publish_time"]


def windows(end):
    """The request windows, the last ending the day before `end`."""
    last = (dt.date.fromisoformat(end) - dt.timedelta(days=1)).isoformat()
    out = []
    for a, b in WINDOWS:
        b = last if b is None or b > last else b
        if a <= b:
            out.append((a, b))
    return out


def rows_of(text, url, retrieved, vintage):
    t = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"{url}: the header is not the endpoint's: {list(t.columns)}")
    out = []
    for r in t.to_dict("records"):
        day, v = r["SettlementDate"].strip(), r["Demand"].strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise RuntimeError(f"{url}: a date not YYYY-MM-DD: {day!r}")
        if v == "":
            continue
        if not re.fullmatch(r"\d+", v):
            raise RuntimeError(f"{url}: {day}: a demand not a whole number: {v!r}")
        out.append({"entity": "elexon:GB", "variable": "indo_daily", "ts_utc": f"{day}T00:00:00Z", "value": float(v),
                    "unit": "MWh", "freq": "P1D", "geo": "GB", "market": "", "node": "Great Britain",
                    "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": vintage,
                    "x_settlement_date": day, "x_publish_time": r["PublishTime"].strip()})
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t.x_settlement_date[t.x_settlement_date.duplicated()]
    if len(twice):
        raise RuntimeError(f"a day given twice: {list(twice)[:3]}")
    return t.sort_values("ts_utc").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Elexon BMRS: Great Britain's daily demand outturn (INDOD), 2020 on")
    ap.add_argument("--end", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
                    help="the last window ends the day before this UTC day; the same day reuses the saved answers")
    ap.add_argument("--offline", action="store_true", help="the saved answers only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.end):
        ap.error("--end is a day, YYYY-MM-DD")
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
        if not args.offline and (ip.paused("elexon") or ip.paused_host("data.elexon.co.uk")):
            raise RuntimeError("Elexon is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for a, b in windows(args.end):
            url = API.format(a=a, b=b)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120)
            rows += rows_of(content.decode("utf-8", errors="replace"), url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append((a, b, rec.get("retrieved_at") or ""))
        t = finish(rows)
        year = t.x_settlement_date.str[:4]
        by = t.groupby(year).agg(days=("value", "size"), twh=("value", "sum"))
        first, last = dt.date.fromisoformat(t.x_settlement_date.min()), dt.date.fromisoformat(t.x_settlement_date.max())
        absent = (last - first).days + 1 - len(t)
        header = [
            f"Energy Research Warehouse (ERW): Elexon BMRS, Great Britain's Initial National Demand Outturn per day (INDOD), {t.x_settlement_date.min()} to {t.x_settlement_date.max()} (session 2162)",
            "Shape: series (docs/datastandard.md v0). entity elexon:GB; variable indo_daily (MWh, the half-hourly INDO summed, excluding station transformer, pumping and interconnector export demand); "
            "ts_utc the settlement day at 00:00:00Z (Decision 11), the day being Great Britain's own (Europe/London); freq P1D; geo GB.",
            f"{len(t)} days: " + "; ".join(f"{y} {int(r.days)} days, {r.twh / 1e6:,.1f} TWh" for y, r in by.iterrows())
            + f". {absent} days between the first and the last have no figure from Elexon. Embedded generation the transmission system does not see is not in it. A day without a figure has no row; nothing is filled. Prices are not taken.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/elexon_demand.py; the windows retrieved " + "; ".join(f"{a} to {b} {r}" for a, b, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Elexon Limited, Balancing Mechanism Reporting Service (BMRS), Insights API, demand/outturn/daily (INDOD), {PAGE}",
            f"  access: {API.format(a='<from>', b='<to>')}",
            f"License: public. Contains BMRS data {chr(0xA9)} Elexon Limited copyright and database right {dt.date.today().year}. Licence: {LICENCE}",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Elexon Limited (BMRS)",
                                    report="Balancing Mechanism Reporting Service, Initial National Demand Outturn per day (INDOD)",
                                    report_url=PAGE, document_list=API.format(a="<from>", b="<to>"), license="public",
                                    tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} days"))
        print(f"{NAME}: {len(t)} days, {t.x_settlement_date.min()} to {t.x_settlement_date.max()}")
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
