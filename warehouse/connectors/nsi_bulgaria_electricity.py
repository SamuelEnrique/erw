#!/usr/bin/env python3
"""Bulgaria's electricity a month, as the National Statistical Institute (NSI) gives it in its time-series workbook
"Production and deliveries of electricity" (Energy-1.4.Electricity_en.xlsx, last modified 24 August 2026): gross and net
production, imports, exports and total net consumption, and, for 2026, net production by source (session 2539, chain
124: a source of the session's own choosing; the ERW held Bulgaria only in Eurostat's, EIA's and Energy-Charts'
international tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nsi_bulgaria_electricity_monthly.csv, from one
workbook (no key):

    https://www.nsi.bg/sites/default/files/files/data/timeseries/Energy-1.4.Electricity_en.xlsx

The workbook holds one sheet a year, as NSI publishes it: on 24 October 2026, "2019" (twelve months, the totals only)
and "2026" (January to July, net production by source as well). Each sheet's month headers ("months of 2019" over I to
XII, or "I.2026") give the months; every sheet the workbook holds is read, and the header says which.

    entity      nsi:bg:<item>: total; a source of net production (nuclear, coal, petroleum_products, natural_gas,
                combustible_renewables, hydro, wind, solar, other)
    variable    gross_production, net_production, imports, exports, net_consumption
    unit        MWh (NSI's GWh times 1,000); ts_utc the month's first day; freq P1M; geo BG
    node        NSI's row label; x_period the month (YYYY-MM)

NSI's "-" (no case registered) has no row; ".", "x" or any other mark stops the run, as do a row label not in the map,
a month header of another form, a key given twice, and a month whose sources differ from its net production by more
than 5 GWh (nine figures, each rounded to a whole GWh: May 2026's differ by 3). Nothing is filled.

    python warehouse/connectors/nsi_bulgaria_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/nsi_bg_energy/ and reused unless --fresh; --offline asks nothing.
www.nsi.bg's robots file closes /admin/ only (session 2539). License: internal. NSI's licence (section 2.1.1) allows
reproduction and use, commercial included, with the author named, but "You may not disseminate derivative or collective
works"; a reshaped table may be one, so the table is internal until a ruling.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "nsi_bulgaria_electricity_monthly"
CONNECTOR = "nsi_bg_energy"
SOURCE = "nsi_bg:energy_1_4_electricity"
HOST = "www.nsi.bg"
URL = "https://www.nsi.bg/sites/default/files/files/data/timeseries/Energy-1.4.Electricity_en.xlsx"
PAGE = "https://www.nsi.bg/en/statistical-data/81/293"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "National Statistical Institute, Bulgaria (NSI), Production and deliveries of electricity (Energy-1.4.Electricity_en.xlsx)"
ROWS = {"Gross production": ("gross_production", "total"), "Net production": ("net_production", "total"),
        "of which Nuclear": ("net_production", "nuclear"), "of which Coal": ("net_production", "coal"),
        "of which Petroleum products": ("net_production", "petroleum_products"), "of which Natural gas": ("net_production", "natural_gas"),
        "of which Combustible renewables": ("net_production", "combustible_renewables"), "of which Hydro": ("net_production", "hydro"),
        "of which Wind": ("net_production", "wind"), "of which Solar photovoltaic": ("net_production", "solar"),
        "of which Other sources": ("net_production", "other"), "Import": ("imports", "total"), "Export": ("exports", "total"),
        "Total net consumption": ("net_consumption", "total")}
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
SKIP = {"PRODUCTION AND DELIVERIES OF ELECTRICITY", "Electricity", "- no case registered", "x not applicable",
        ". no available or missing data", "0 less than half of unit employed"}
X_COLS = ["x_period"]


def months_of(rows):
    """{column: 'YYYY-MM'} from a sheet's month headers."""
    for i, r in enumerate(rows):
        cells = {j: str(c).strip() for j, c in enumerate(r) if c is not None and j > 0}
        if not cells:
            continue
        if all(re.fullmatch(r"(I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)\.\d{4}", c) for c in cells.values()):
            return {j: f"{c.split('.')[1]}-{ROMAN.index(c.split('.')[0]) + 1:02d}" for j, c in cells.items()}, i
        if len(cells) == 1 and re.fullmatch(r"months of \d{4}", next(iter(cells.values()))):
            year = next(iter(cells.values()))[-4:]
            nxt = {j: str(c).strip() for j, c in enumerate(rows[i + 1]) if c is not None and j > 0}
            if [nxt[j] for j in sorted(nxt)] != ROMAN[:len(nxt)]:
                raise RuntimeError(f"months of {year}: the month row is not I to XII: {nxt}")
            return {j: f"{year}-{ROMAN.index(c) + 1:02d}" for j, c in nxt.items()}, i + 1
    raise RuntimeError("no month header in the sheet")


def gwh(c):
    s = str(c).strip()
    if s == "-":
        return None
    if not re.fullmatch(r"\d+", s):
        raise RuntimeError(f"not a figure: {s!r}")
    return float(s)


def parse_sheets(sheets, base):
    """sheets: {name: [row tuples]}."""
    rows, seen, read = [], set(), []
    for name, sheet in sheets.items():
        cols, hrow = months_of(sheet)
        vals = {}
        for r in sheet[hrow + 1:]:
            if not r or r[0] is None:
                continue
            label = str(r[0]).strip()
            if label in SKIP:
                continue
            if label not in ROWS:
                raise RuntimeError(f"sheet {name}: a row not in the map: {label!r}")
            var, item = ROWS[label]
            for j, month in cols.items():
                v = gwh(r[j] if j < len(r) else None)
                k = (var, item, month)
                if k in seen:
                    raise RuntimeError(f"{k} given twice")
                seen.add(k)
                vals[k] = v
                if v is not None:
                    rows.append(dict(entity=f"nsi:bg:{item}", variable=var, ts_utc=f"{month}-01T00:00:00Z", value=v * 1000, unit="MWh",
                                     freq="P1M", geo="BG", market="", node=label, **base, x_period=month))
        for month in cols.values():
            parts = [v for (var, item, m), v in vals.items() if var == "net_production" and item != "total" and m == month]
            if parts and abs(sum(p or 0 for p in parts) - vals[("net_production", "total", month)]) > 5:
                raise RuntimeError(f"{month}: the sources sum to {sum(p or 0 for p in parts)}, not to net production")
        read.append(f"{name} ({min(cols.values())} to {max(cols.values())})")
    if not rows:
        raise RuntimeError("no figure in the workbook")
    return pd.DataFrame(rows), read


def parse(content, base):
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    sheets = {ws.title: [tuple(r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}
    wb.close()
    return parse_sheets(sheets, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NSI Bulgaria: production and deliveries of electricity a month")
    ap.add_argument("--offline", action="store_true", help="the saved workbook only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the workbook again")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t, read = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): National Statistical Institute, Bulgaria (NSI), Production and deliveries of electricity, a month "
            "(session 2539)",
            "Shape: series (docs/datastandard.md v0). entity nsi:bg:<item> (total, or a source of net production); variable gross_production, "
            "net_production, imports, exports, net_consumption; unit MWh (NSI's GWh times 1,000); ts_utc the month's first day; freq P1M; "
            "geo BG; node NSI's row label; x_period the month.",
            f"{len(t)} rows from the workbook's sheets {', '.join(read)}: the workbook holds no other year, so the months between are not "
            "here. A cell of - (no case registered) has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nsi_bulgaria_electricity.py; the workbook retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {PAGE})",
            "License: internal. NSI's licence allows reproduction and use, commercial included, with the author named, but not the "
            f"dissemination of derivative or collective works; internal until a ruling. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities; sheets {', '.join(read)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="National Statistical Institute, Bulgaria (NSI)",
                                    report="Production and deliveries of electricity (time series workbook Energy-1.4)", report_url=URL,
                                    document_list=PAGE, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
