#!/usr/bin/env python3
"""EIA-861: each utility's operations, its peak demand, sources and dispositions of energy and its revenue, a year (session 882, chain 048).

Energy Research Warehouse (ERW) connector. One series table from the U.S. Energy Information Administration's Form
EIA-861 annual files (Operational_Data_<year>.xlsx in f861<year>.zip; the zips eia861_sales.py saved):

    eia861_operational_data   summer_peak_demand, winter_peak_demand (MW); the sources of energy (MWh): net_generation,
                              wholesale_purchases, exchange_received, exchange_delivered, exchange_net, wheeled_received,
                              wheeled_delivered, wheeled_net, transmission_by_others_losses, total_sources; its dispositions
                              (MWh): retail_sales, sales_for_resale, furnished_without_charge, consumed_without_charge,
                              energy_losses, total_disposition; its revenue (USD, EIA's thousand dollars times 1,000):
                              revenue_retail_sales, revenue_delivery_customers, revenue_sales_for_resale,
                              revenue_credits_adjustments, revenue_transmission, revenue_other, revenue_total

    entity    eia861_op:<utility>:<state>; ts_utc the data year's 1 January; freq P1Y; geo US-<state>; node the
              utility's name; x_utility_number, x_state, x_ownership, x_nerc_region and x_data_type (O observed,
              I imputed) as EIA gives them

Every column is found by its group and its own heading, not by position; a heading the map does not know stops the run
(EIA's "Retail Sales" became "Sales to Ultimate Customers", both read as retail_sales; the Short Form column of 2019
on is read past, as eia861_programs.py reads it past). Net figures can be negative.
EIA's aggregates 88888 and 99999 are left out, as eia861_sales.py leaves them; a "." cell has no row; nothing is
filled. Two rows EIA gives under one utility and state with different values have no key: both are left out and named
in the header (chain 030's rule).

    python warehouse/connectors/eia861_operations.py --years 2015 ... 2025 --offline

Ceiling: two requests a year (the page and the zip), none when both are saved in warehouse/raw/eia861/. EIA's robots
file disallows /archive/ (session 666): a year there is read only from a zip already saved. License: public (EIA, record 1
of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-861").
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
from eia861_sales import NOT_UTILITIES, PAGE, UA, held_text, zip_url  # noqa: E402  the same page, zips and aggregates
from eia861_programs import paths, text  # noqa: E402  the stacked-heading reader

CONNECTOR = "eia861"
NAME = "eia861_operational_data"
PREFIX = "eia861_op"
SOURCE = "eia:eia861:operational_data"
# (group, the heading's start) -> (variable, unit, scale); the group is the top heading carried right
MAP = {
    ("demand", "summer peak demand"): ("summer_peak_demand", "MW", 1.0),
    ("demand", "winter peak demand"): ("winter_peak_demand", "MW", 1.0),
    ("energy sources", "net generation"): ("net_generation", "MWh", 1.0),
    ("energy sources", "wholesale power purchases"): ("wholesale_purchases", "MWh", 1.0),
    ("energy sources", "exchange energy received"): ("exchange_received", "MWh", 1.0),
    ("energy sources", "exchange energy delivered"): ("exchange_delivered", "MWh", 1.0),
    ("energy sources", "net power exchanged"): ("exchange_net", "MWh", 1.0),
    ("energy sources", "wheeled power received"): ("wheeled_received", "MWh", 1.0),
    ("energy sources", "wheeled power delivered"): ("wheeled_delivered", "MWh", 1.0),
    ("energy sources", "net wheeled power"): ("wheeled_net", "MWh", 1.0),
    ("energy sources", "transmission by other"): ("transmission_by_others_losses", "MWh", 1.0),
    ("energy sources", "total sources"): ("total_sources", "MWh", 1.0),
    ("disposition", "retail sales"): ("retail_sales", "MWh", 1.0),
    ("disposition", "sales to ultimate customers"): ("retail_sales", "MWh", 1.0),
    ("disposition", "sales for resale"): ("sales_for_resale", "MWh", 1.0),
    ("disposition", "furnished without charge"): ("furnished_without_charge", "MWh", 1.0),
    ("disposition", "consumed by respondent without"): ("consumed_without_charge", "MWh", 1.0),
    ("disposition", "total energy losses"): ("energy_losses", "MWh", 1.0),
    ("disposition", "total disposition"): ("total_disposition", "MWh", 1.0),
    ("electric revenues", "from retail sales"): ("revenue_retail_sales", "USD", 1000.0),
    ("electric revenues", "from delivery customers"): ("revenue_delivery_customers", "USD", 1000.0),
    ("electric revenues", "from sales for resale"): ("revenue_sales_for_resale", "USD", 1000.0),
    ("electric revenues", "from credits or adjustments"): ("revenue_credits_adjustments", "USD", 1000.0),
    ("electric revenues", "from transmission"): ("revenue_transmission", "USD", 1000.0),
    ("electric revenues", "from other"): ("revenue_other", "USD", 1000.0),
    ("electric revenues", "total"): ("revenue_total", "USD", 1000.0),
}
CHARS = {"data year": None, "utility number": None, "utility name": None, "state": None, "ownership type": "x_ownership",
         "nerc region": "x_nerc_region"}
X = ["x_utility_number", "x_state", "x_ownership", "x_nerc_region", "x_data_type"]


def sheet_rows(frame, year, url, retrieved, skipped):
    hr, cols = paths(frame)
    chars, figs = {}, {}
    for c, p in cols:
        head = p[-1]
        if head == "short form":                # 2019 on, read past as eia861_programs.py reads it past
            continue
        if head in CHARS:
            chars[head] = c
        elif head.startswith("data type"):
            chars["data type"] = c
        else:
            hit = [k for k in MAP if p[0].startswith(k[0]) and head.startswith(k[1])]
            if len(hit) != 1:
                raise RuntimeError(f"{year}: column {c} {p} is not in the map")
            var = MAP[hit[0]][0]
            if var in figs:
                raise RuntimeError(f"{year}: {var} found twice")
            figs[var] = (c,) + MAP[hit[0]][1:]
    for k in ("data year", "utility number", "utility name", "state"):
        if k not in chars:
            raise RuntimeError(f"{year}: the heading '{k}' is missing")
    if len(figs) != len({v[0] for v in MAP.values()}):
        raise RuntimeError(f"{year}: {len(figs)} figures found, not {len({v[0] for v in MAP.values()})}")
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[chars["data year"]], errors="coerce").eq(year)]
    d = d[~pd.to_numeric(d[chars["utility number"]], errors="coerce").isin(NOT_UTILITIES)]
    out = []
    for _, r in d.iterrows():
        util, state = text(r[chars["utility number"]]), text(r[chars["state"]])
        base = dict(entity=f"{PREFIX}:{util}:{state}", ts_utc=f"{year}-01-01T00:00:00Z", freq="P1Y",
                    geo=f"US-{state}" if state else "US", market="", node=text(r[chars["utility name"]]), source=SOURCE,
                    source_url=url, retrieved_at=retrieved, vintage="", x_utility_number=util, x_state=state,
                    x_ownership=text(r[chars["ownership type"]]) if "ownership type" in chars else "",
                    x_nerc_region=text(r[chars["nerc region"]]) if "nerc region" in chars else "",
                    x_data_type=text(r[chars["data type"]]) if "data type" in chars else "")
        for var, (c, unit, scale) in figs.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, variable=var, value=float(v) * scale, unit=unit))
    t = pd.DataFrame(out)
    if len(t):
        # chain 030's rule: a row EIA gives twice with every field the same is kept once; two different rows under one
        # utility and state have no key and are both left out, the whole record, counted
        t = t.drop_duplicates()
        twice = t.duplicated(["entity", "variable", "ts_utc"], keep=False)
        if twice.any():
            bad = set(t.loc[twice, "entity"])
            skipped.setdefault("no key", set()).update(f"{e} {year}" for e in bad)
            t = t[~t["entity"].isin(bad)]
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-861 utilities' operational data")
    ap.add_argument("--years", type=int, nargs="+", required=True, help="the data years")
    ap.add_argument("--offline", action="store_true", help="never a request: the saved page and zips, or nothing")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia861_operations_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        html = page.decode("utf-8", errors="replace")
        frames, urls, skipped = [], [], {}
        for y in sorted(args.years):
            url, year = zip_url(html, y)
            if "/archive/" in url and not ip.raw_cached(CONNECTOR, url):
                raise RuntimeError(f"{url} is under /archive/, which EIA's robots file disallows (session 666), and is not saved; not asked")
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=600)
            zf = zipfile.ZipFile(io.BytesIO(content))
            name = next((n for n in zf.namelist() if n in (f"Operational_Data_{year}.xlsx", f"Operational_Data{year}.xlsx")), None)
            if not name:
                raise RuntimeError(f"f861{year}.zip holds no Operational_Data file")
            xl = pd.ExcelFile(io.BytesIO(zf.read(name)))
            for sheet in xl.sheet_names:
                t = sheet_rows(pd.read_excel(xl, sheet, header=None), year, url, rec["retrieved_at"], skipped)
                log(f"{year} {sheet}: {len(t):,} rows")
                frames.append(t)
            urls.append(url)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row in both sheets")
        cols = ip.SERIES_COLS + X
        s = s[cols]
        years = sorted({int(t[:4]) for t in s["ts_utc"]})
        nokey = sorted(skipped.get("no key", ()))
        header = [
            "Energy Research Warehouse (ERW): EIA-861 operational data, each utility's peak demand, sources and dispositions of energy and revenue, by state, a year (session 882)",
            f"Shape: series (docs/datastandard.md v0). entity {PREFIX}:<utility>:<state>; variables summer_peak_demand and winter_peak_demand (MW); "
            "net_generation, wholesale_purchases, exchange_received, exchange_delivered, exchange_net, wheeled_received, wheeled_delivered, wheeled_net, "
            "transmission_by_others_losses, total_sources (MWh, the sources of energy); retail_sales, sales_for_resale, furnished_without_charge, "
            "consumed_without_charge, energy_losses, total_disposition (MWh); revenue_retail_sales, revenue_delivery_customers, revenue_sales_for_resale, "
            "revenue_credits_adjustments, revenue_transmission, revenue_other, revenue_total (USD, EIA's thousand dollars times 1,000); net figures can be "
            "negative; ts_utc the data year's 1 January; freq P1Y; node the utility's name; x_data_type O observed, I imputed.",
            f"Years held: {held_text(years)}; {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities. EIA's aggregates 88888 and 99999 left out; a '.' cell has no row; nothing is filled."
            + (f" Rows EIA gives twice with two values, left out (no key): {', '.join(nokey)}." if nokey else ""),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia861_operations.py (the zips as saved by earlier runs)",
            f"Run log: warehouse/output/logs/eia861_operations_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-861 Annual Electric Power Industry Report (Operational_Data_<year>.xlsx), {PAGE}",
            f"  access: {'; '.join(urls)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-861").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-861 Annual Electric Power Industry Report, operational data",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{held_text(years)}: {len(s):,} rows"))
        print(f"{NAME}: {held_text(years)}, {len(s):,} rows, {s['x_utility_number'].nunique():,} utilities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia861_operations FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status("eia861_operations", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
