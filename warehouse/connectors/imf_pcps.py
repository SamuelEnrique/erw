#!/usr/bin/env python3
"""IMF primary commodity prices, monthly: uranium, lithium, cobalt, nickel and copper (session 132, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/imf_commodity_prices.csv, from the
International Monetary Fund's Primary Commodity Price System (PCPS), read from the IMF's own data service
(https://api.imf.org/external/sdmx/3.0/, dataflow IMF.RES/PCPS, area G001 "World", US dollars, monthly), from 2019-01.
Entities are imf:PCPS:<indicator>. A value is the IMF's average of the month, in the unit the IMF's commodity tables
state: US dollars a metric ton for cobalt, copper, lithium and nickel, US dollars a pound for uranium. These are
monthly averages, not daily prices, and the board labels them monthly.

    python warehouse/connectors/imf_pcps.py [--out-dir DIR]

A month the IMF lists with no value is not written and is counted. Nothing is filled. The table is written only if its
newest month is within 150 days.

License: public, with attribution, on the IMF's terms as session 132 could read them. The IMF's "Copyright and Usage"
page (https://www.imf.org/en/about/copyright-and-terms) answered this machine HTTP 403, so its words were read through
a web search's quotation of the page, not on the page: "You may download, extract, copy, create derivative works,
publish, distribute, and use Data obtained from IMF Sites", subject to conditions that include citing the source,
saying so when the data are materially transformed, and not altering the data in a way that affects their nature or
accuracy. A person should read the page before this table is opened to visitors (docs/methods/price_board.md).
Cite: International Monetary Fund, Primary Commodity Price System. Ceiling: session 132's 1,500,000 rows in all; this
pull reads about 500.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

CONNECTOR = "imf_pcps"
NAME = "imf_commodity_prices"
START = "2019-01"
STALE_DAYS = 150
# indicator: (what it is, unit, as the IMF's commodity tables state it)
SERIES = {
    "PURAN": ("Uranium", "USD/lb"),
    "PLITH": ("Lithium", "USD/t"),
    "PCOBA": ("Cobalt", "USD/t"),
    "PNICK": ("Nickel", "USD/t"),
    "PCOPP": ("Copper", "USD/t"),
}
API = "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/PCPS/+/G001." + "+".join(SERIES) + f".USD.M?c[TIME_PERIOD]=ge:{START}"
PAGE = "https://www.imf.org/en/Research/commodity-prices"
SOURCE_ENTRY = dict(source="imf:pcps", publisher="International Monetary Fund (IMF)", report="Primary Commodity Price System (PCPS), monthly prices",
                    report_url=PAGE, document_list="https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.RES/PCPS/", license="public", tables=[NAME])


def parse(body, url, retrieved):
    """The IMF's SDMX-JSON answer as the table's rows, and the number of months listed with no value."""
    data = body["data"]
    st = data["structures"][0]
    dims = [d["id"] for d in st["dimensions"]["series"]]
    ind = [v["id"] for v in st["dimensions"]["series"][dims.index("INDICATOR")]["values"]]
    periods = [v.get("id") or v.get("value") for v in st["dimensions"]["observation"][0]["values"]]
    rows, empty = [], 0
    for key, s in data["dataSets"][0]["series"].items():
        code = ind[int(key.split(":")[dims.index("INDICATOR")])]
        if code not in SERIES:
            raise RuntimeError(f"the IMF answered with an indicator that was not asked for: {code}")
        what, unit = SERIES[code]
        for i, obs in s["observations"].items():
            m = re.fullmatch(r"(\d{4})-M(\d{2})", str(periods[int(i)]))
            if not m:
                raise RuntimeError(f"{code}: a period that is not a month: {periods[int(i)]!r}")
            if obs[0] in (None, "", "NaN"):
                empty += 1
                continue
            rows.append(dict(entity=f"imf:PCPS:{code}", variable="price", ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=float(obs[0]), unit=unit,
                             freq="P1M", geo="", market="", node=what, source=SOURCE_ENTRY["source"], source_url=url, retrieved_at=retrieved, vintage=""))
    return pd.DataFrame(rows, columns=ip.SERIES_COLS), empty


def build(run_id, log):
    def call():
        r = requests.get(API, headers={"Accept": "application/json"}, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"IMF HTTP {r.status_code}: {r.text[:200]}")
        return r
    r = ip.with_retries("IMF PCPS", call, log)
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    table, empty = parse(r.json(), API, retrieved)
    got = set(table["entity"].str.rsplit(":", n=1).str[1])
    if got != set(SERIES):
        raise RuntimeError(f"the IMF answered for {sorted(got)}, asked for {sorted(SERIES)}")
    age = (pd.Timestamp.now(tz="UTC") - pd.Timestamp(table["ts_utc"].max())).days
    if age > STALE_DAYS:
        raise RuntimeError(f"the newest month the IMF holds is {table['ts_utc'].max()[:7]}, {age} days old (limit {STALE_DAYS})")
    header = [
        "Energy Research Warehouse (ERW): IMF primary commodity prices, monthly averages from 2019: uranium, lithium, cobalt, nickel, copper (session 132)",
        "Shape: series (docs/datastandard.md v0). price: the IMF's average price of the month, US dollars; ts_utc is the first day of the month at 00:00:00Z; freq P1M. node is the commodity. Units per row (USD/t, uranium USD/lb), as the IMF's commodity tables state them.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/imf_pcps.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Source: {SOURCE_ENTRY['source']} International Monetary Fund, {SOURCE_ENTRY['report']}, {PAGE}",
        f"  access: {API}",
        f"Rows read: {len(table) + empty:,}. Months the IMF lists with no value, not written: {empty}. Nothing is filled. These are monthly averages, not daily prices.",
        "License: public with attribution, on the IMF's Copyright and Usage terms as read through a search result's quotation (the page itself answered HTTP 403): a person should confirm before the table is opened. Cite: International Monetary Fund, Primary Commodity Price System.",
    ]
    return table, header, f"{len(table) + empty} rows read"


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
