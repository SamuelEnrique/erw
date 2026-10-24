#!/usr/bin/env python3
"""Côte d'Ivoire's electricity a year, from the electricity regulator ANARE-CI's "Open Data" pages: gross generation by
kind (hydro, thermal, isolated plants), national consumption by voltage (low; high and medium) and the system's peak
demand, 1960 to 2020 (session 2463, chain 119: Côte d'Ivoire's electricity, from the regulator, since CI-ENERGIES' host
does not resolve).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/anare_cotedivoire_electricity_annual.csv, from
the HTML tables (wpDataTables) of three pages of anare.ci, three requests:

    https://anare.ci/big-data-2/production-brute-delectricite-2/   "Production brute d'electricite (GWh)"
    https://anare.ci/anare/consommation-nat-2/                      "Consommation nat (GWh)": BT, HT/MT
    https://anare.ci/anare/pointe-mw-2/                             "Pointe MW"

    entity     anare_ci:CI; geo CI; node Cote d'Ivoire; ts_utc the year's 1 January; freq P1Y
    variable   generation_hydro, generation_thermal, generation_isolated ("Centrales Isolees"), MWh (ANARE-CI's GWh,
               the unit its charts give, times 1,000); consumption_low_voltage (BT), consumption_high_medium_voltage
               (HT/MT), MWh; peak_demand, MW

A year printed twice with the same figures (2019 in the generation table) is taken once; twice with different figures
stops the run. A blank cell has no row. The pages give no total; none is computed. The installed capacity page draws a
chart without a table and is not read. A header not ANARE-CI's, a year that does not read or a value that is not a
number stops the run. Nothing is filled.

    python warehouse/connectors/anare_cotedivoire.py [--offline] [--out-dir DIR]

Ceiling: three requests, reused from warehouse/raw/anare_cotedivoire/ with --offline. www.anare.ci and anare.ci (where
www.anare.ci redirects) have robots files of one line, "User-agent: *", which disallow nothing (session 2463). License:
internal until a ruling: the pages state no terms of reuse.
"""

import argparse
import datetime as dt
import html
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "anare_cotedivoire_electricity_annual"
CONNECTOR = "anare_cotedivoire"
SOURCE = "anare_ci:open_data"
PAGE = "https://anare.ci/"
PAGES = {
    "generation": ("https://anare.ci/big-data-2/production-brute-delectricite-2/", ["Année", "Hydraulique", "Thermique", "Centrales Isolées"],
                   [("generation_hydro", "MWh", 1000.0), ("generation_thermal", "MWh", 1000.0), ("generation_isolated", "MWh", 1000.0)]),
    "consumption": ("https://anare.ci/anare/consommation-nat-2/", ["Année", "BT", "HT/MT"],
                    [("consumption_low_voltage", "MWh", 1000.0), ("consumption_high_medium_voltage", "MWh", 1000.0)]),
    "peak": ("https://anare.ci/anare/pointe-mw-2/", ["Année", "MW"], [("peak_demand", "MW", 1.0)]),
}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def cells(tr):
    return [html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c))).strip() for c in re.findall(r"(?s)<t[hd][^>]*>(.*?)</t[hd]>", tr)]


def table(page, head, what):
    """{year: [values]} of the page's one table, its header checked, a year twice allowed only with the same figures."""
    tabs = re.findall(r"(?s)<table.*?</table>", page)
    if len(tabs) != 1:
        raise RuntimeError(f"{what}: {len(tabs)} tables, not one")
    rows = [cells(tr) for tr in re.findall(r"(?s)<tr.*?</tr>", tabs[0])]
    if not rows or rows[0] != head:
        raise RuntimeError(f"{what}: the header is not ANARE-CI's: {rows[0] if rows else None}")
    out = {}
    for r in rows[1:]:
        if len(r) != len(head) or not re.fullmatch(r"(19|20)\d\d", r[0]):
            raise RuntimeError(f"{what}: a row that does not read: {r}")
        vals = []
        for c in r[1:]:
            c = c.replace(" ", "").replace(" ", "")
            if c == "":
                vals.append(None)
            elif re.fullmatch(r"\d+(?:[.,]\d+)?", c):
                vals.append(float(c.replace(",", ".")))
            else:
                raise RuntimeError(f"{what} {r[0]}: not a number: {c!r}")
        y = int(r[0])
        if y in out and out[y] != vals:
            raise RuntimeError(f"{what}: {y} twice with different figures")
        out[y] = vals
    return out


def parse(pages):
    """{(variable, year): (value, unit, url)} from the three pages' HTML ({key: html})."""
    out = {}
    for key, (url, head, vars_) in PAGES.items():
        for y, vals in table(pages[key], head, key).items():
            for (var, unit, f), v in zip(vars_, vals):
                if v is not None:
                    out[(var, y)] = (v * f, unit, url)
    return out


def finish(rows, retrieved, vintage):
    t = pd.DataFrame([dict(entity="anare_ci:CI", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v, 3), unit=u, freq="P1Y",
                           geo="CI", market="", node="Cote d'Ivoire", source=SOURCE, source_url=url, retrieved_at=retrieved.get(url, ""),
                           vintage=vintage.get(url, "")) for (var, y), (v, u, url) in rows.items()], columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ANARE-CI's open data: Cote d'Ivoire's generation by kind, consumption by voltage and peak, a year")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
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
        if not args.offline and (ip.paused("anare_ci") or ip.paused_host("anare.ci")):
            raise RuntimeError("ANARE-CI is paused (warehouse/metadata/paused_sources.csv): not requested")
        pages, retrieved, vintage = {}, {}, {}
        for key, (url, _, _) in PAGES.items():
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
            pages[key] = content.decode("utf-8", errors="replace")
            retrieved[url], vintage[url] = rec.get("retrieved_at") or "", ip.vintage_of(rec)
        t = finish(parse(pages), retrieved, vintage)
        header = [
            f"Energy Research Warehouse (ERW): ANARE-CI (Autorite nationale de regulation du secteur de l'electricite de Cote d'Ivoire), open data: gross generation by kind, national consumption by voltage and the peak demand, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2463)",
            "Shape: series (docs/datastandard.md v0). entity anare_ci:CI; ts_utc the year's 1 January; freq P1Y; geo CI. variable generation_hydro, generation_thermal, generation_isolated (\"Centrales Isolees\"), consumption_low_voltage (BT), consumption_high_medium_voltage (HT/MT), "
            "MWh (ANARE-CI's GWh times 1,000; the unit its charts give); peak_demand, MW. source_url the page each row comes from.",
            f"{len(t)} rows. The pages give no total and none is computed; a blank cell has no row; 2019, printed twice in the generation table with the same figures, is taken once. The installed capacity page has a chart and no table and is not read. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/anare_cotedivoire.py; the pages retrieved " + ", ".join(sorted(set(retrieved.values()))),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} ANARE-CI, Open Data: Production brute d'electricite, Consommation nat, Pointe MW, {PAGE}",
            "  access: " + ", ".join(u for u, _, _ in PAGES.values()),
            "License: internal. ANARE-CI's pages state no terms of reuse; internal until a ruling. Cite: ANARE-CI, Open Data.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="ANARE-CI, Cote d'Ivoire's electricity regulator",
                                    report="Open Data: gross generation, national consumption, peak demand (annual)",
                                    report_url=PAGE, document_list=PAGES["generation"][0], license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]}")
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
