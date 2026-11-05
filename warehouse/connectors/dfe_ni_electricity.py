#!/usr/bin/env python3
"""Northern Ireland's electricity a month: renewable generation by type, non-renewable generation by fuel, and imports
and exports, as the Department for the Economy (DfE) gives them in its report "Electricity Consumption and Renewable
Generation in Northern Ireland" (April 2025 to March 2026, published 4 June 2026), whose figures' data the report page
holds as CSV files written into the page (session 2544, chain 124: a source of the session's own choosing; the ERW held
Northern Ireland only inside DESNZ's United Kingdom tables and Elexon's Great Britain).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/dfe_ni_electricity_monthly.csv, from one page
(no key), listed on DfE's publication page:

    https://datavis.nisra.gov.uk/Economy/electricity-consumption-and-renewable-generation-report.html

The page links each figure's data as a "data:text/csv;base64," address, the link's text naming the figure ("Figure 6.CSV").
Each is decoded (UTF-16 text with one-byte line ends, so its zero bytes are dropped) and read as CSV. Four figures hold
monthly values and are taken, each found by its header row, not its number:

    Wind, Hydro/Tidal, Bioenergy, Landfill gas, Solar PV (GWh)       renewable_generation by type
    Non-renewable generation, Renewable generation (GWh)              non_renewable_generation, renewable_generation (total)
    Coal, Gas, Distillate and Other (GWh)                             non_renewable_generation by fuel
    Import, Export, Net imports (GWh)                                 imports, exports (written positive), net_imports

    entity      dfe_ni:gb-nir:<item>: total; wind, hydro_tidal, bioenergy, landfill_gas, solar; coal, gas, distillate_other
    variable    renewable_generation, non_renewable_generation, imports, exports, net_imports
    unit        MWh (DfE's GWh times 1,000); ts_utc the month's first day; freq P1M; geo GB-NIR
    node        DfE's column header; x_figure the figure's link text

The figures of rolling twelve-month sums and shares (1 to 5) and the single month's flows (10) are not taken. Each month's
types must sum to the renewable total and its fuels to the non-renewable total within 2 GWh (whole GWh each), and
imports less exports to net imports within 1 GWh; a header not found, a month given twice, a gap between months, a
figure that is not a whole number, or two figures of one header stops the run. Nothing is filled.

    python warehouse/connectors/dfe_ni_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/dfe_ni_electricity/ and reused unless --fresh; --offline asks nothing.
datavis.nisra.gov.uk serves an "Unavailable" page at its robots address (no robots file); www.economy-ni.gov.uk's robots
file asks ClaudeBot for a crawl delay of 5 seconds, which is kept (session 2544). License: public. DfE's Crown copyright
page: "You may use and re-use the information featured on this website (not including logos) free of charge in any format
or medium, under the terms of the Open Government Licence", the source acknowledged; the header acknowledges it.
"""

import argparse
import base64
import csv
import datetime as dt
import html
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "dfe_ni_electricity_monthly"
CONNECTOR = "dfe_ni_electricity"
SOURCE = "dfe_ni:electricity_consumption_renewable_generation_2026"
HOST = "datavis.nisra.gov.uk"
URL = "https://datavis.nisra.gov.uk/Economy/electricity-consumption-and-renewable-generation-report.html"
LIST = "https://www.economy-ni.gov.uk/publications/electricity-consumption-and-renewable-generation-northern-ireland-april-2025-march-2026"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Department for the Economy (Northern Ireland), Electricity Consumption and Renewable Generation in Northern Ireland, "
            "April 2025 to March 2026 (4 June 2026), figures 6 to 9")
# a figure's header (after "Date") and, a column at a time, (variable, item)
FIGURES = {
    ("Wind (GWh)", "Hydro/Tidal (GWh)", "Bioenergy(GWh)", "Landfill gas (GWh)", "Solar PV(GWh)"):
        [("renewable_generation", "wind"), ("renewable_generation", "hydro_tidal"), ("renewable_generation", "bioenergy"),
         ("renewable_generation", "landfill_gas"), ("renewable_generation", "solar")],
    ("Non-renewable generation (GWh)", "Renewable generation (GWh)"):
        [("non_renewable_generation", "total"), ("renewable_generation", "total")],
    ("Coal (GWh)", "Gas (GWh)", "Distillate and Other (GWh)"):
        [("non_renewable_generation", "coal"), ("non_renewable_generation", "gas"), ("non_renewable_generation", "distillate_other")],
    ("Import (GWh)", "Export (Gwh)", "Net imports (Gwh)"):
        [("imports", "total"), ("exports", "total"), ("net_imports", "total")],
}
SUMS = [("renewable_generation", ["wind", "hydro_tidal", "bioenergy", "landfill_gas", "solar"], 2),
        ("non_renewable_generation", ["coal", "gas", "distillate_other"], 2)]
X_COLS = ["x_figure"]


def figures_of(page):
    """[(link text, decoded CSV text)] of the page's CSV links."""
    out = []
    for m in re.finditer(r'href="data:text/csv;base64,([A-Za-z0-9+/=]+)"[^>]*>(.*?)</a>', page, re.S):
        raw = base64.b64decode(m.group(1))
        if raw[:2] == b"\xff\xfe":
            raw = raw[2:]
        text = raw.replace(b"\x00", b"").decode("utf-8")
        out.append((html.unescape(re.sub(r"<[^>]+>|\s+", " ", m.group(2))).strip(), text))
    if not out:
        raise RuntimeError("no CSV figure in the page")
    return out


def parse_figures(figs, base):
    rows, seen, found = [], set(), {}
    for name, text in figs:
        recs = list(csv.reader(io.StringIO(text)))
        recs = [r for r in recs if r]
        if not recs or recs[0][0] != "Date":
            continue
        head = tuple(recs[0][1:])
        if head not in FIGURES:
            continue
        if head in found:
            raise RuntimeError(f"two figures with the header {head}: {found[head]} and {name}")
        found[head] = name
        months = []
        for r in recs[1:]:
            if not re.fullmatch(r"\d{4}-\d{2}-01", r[0]) or len(r) != len(head) + 1:
                raise RuntimeError(f"{name}: a row of another form: {r}")
            months.append(r[0][:7])
            for cell, label, (var, item) in zip(r[1:], head, FIGURES[head]):
                if not re.fullmatch(r"-?\d+", cell.strip()):
                    raise RuntimeError(f"{name} {r[0]} {label}: not a whole number: {cell!r}")
                v = float(cell)
                if var == "exports":
                    v = -v
                k = (var, item, r[0][:7])
                if k in seen:
                    raise RuntimeError(f"{k} given twice")
                seen.add(k)
                rows.append(dict(entity=f"dfe_ni:gb-nir:{item}", variable=var, ts_utc=f"{r[0][:7]}-01T00:00:00Z", value=v * 1000,
                                 unit="MWh", freq="P1M", geo="GB-NIR", market="", node=label, **base, x_figure=name))
        ms = [pd.Period(m, "M") for m in months]
        for a, b in zip(ms, ms[1:]):
            if b != a + 1:
                raise RuntimeError(f"{name}: a gap or a month out of order: {a} then {b}")
    missing = [h for h in FIGURES if h not in found]
    if missing:
        raise RuntimeError(f"figures not found: {missing}")
    t = pd.DataFrame(rows)
    v = {(x, e.split(":")[-1], ts[:7]): val / 1000 for x, e, ts, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
    for month in sorted({k[2] for k in v}):
        for var, parts, tol in SUMS:
            if (var, "total", month) in v and all((var, p, month) in v for p in parts):
                s = sum(v[(var, p, month)] for p in parts)
                if abs(s - v[(var, "total", month)]) > tol:
                    raise RuntimeError(f"{month} {var}: its parts sum to {s}, not to {v[(var, 'total', month)]}")
        if ("imports", "total", month) in v:
            if abs(v[("imports", "total", month)] - v[("exports", "total", month)] - v[("net_imports", "total", month)]) > 1:
                raise RuntimeError(f"{month}: imports less exports is not net imports")
    return t, found


def parse(content, base):
    return parse_figures(figures_of(content.decode("utf-8", errors="replace")), base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="DfE Northern Ireland: electricity generation and trade a month")
    ap.add_argument("--offline", action="store_true", help="the saved page only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the page again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=5)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t, found = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        first, last = t.ts_utc.min()[:7], t.ts_utc.max()[:7]
        y = t[(t.entity == "dfe_ni:gb-nir:total") & (t.ts_utc.str[:4] == "2025")].groupby("variable").value.sum()
        head = [
            "Energy Research Warehouse (ERW): Department for the Economy (Northern Ireland), Electricity Consumption and Renewable Generation in "
            "Northern Ireland, April 2025 to March 2026: generation by type and fuel, and trade, a month (session 2544)",
            "Shape: series (docs/datastandard.md v0). entity dfe_ni:gb-nir:<item>; variable renewable_generation (total and by type), "
            "non_renewable_generation (total and by fuel), imports, exports (written positive), net_imports; unit MWh (DfE's GWh times 1,000); "
            "ts_utc the month's first day; freq P1M; geo GB-NIR; node DfE's column header; x_figure the figure's link text.",
            f"{len(t)} rows, {first} to {last}, from {', '.join(sorted(found.values()))}; in 2025 renewable generation "
            f"{y.get('renewable_generation', 0) / 1e6:.3f} TWh, non-renewable {y.get('non_renewable_generation', 0) / 1e6:.3f} TWh, net imports "
            f"{y.get('net_imports', 0) / 1e6:.3f} TWh. The rolling twelve-month figures are not taken; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/dfe_ni_electricity.py; the page retrieved {base['retrieved_at']}; last modified "
            f"{base['vintage'] or 'not stated'}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {LIST})",
            "License: public. Contains public sector information from the Department for the Economy (Northern Ireland), re-used under the "
            "Open Government Licence (DfE's Crown copyright page); the figures are DfE's, scaled from GWh to MWh, with exports written positive.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities, {first} to {last}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Department for the Economy (Northern Ireland)",
                                    report="Electricity Consumption and Renewable Generation in Northern Ireland, April 2025 to March 2026, figures 6 to 9",
                                    report_url=URL, document_list=LIST, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
