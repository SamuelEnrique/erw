#!/usr/bin/env python3
"""Kyrgyzstan's electricity a year, from the National Statistical Committee of the Kyrgyz Republic's dynamic tables: the
generation of the power stations by kind (1992 to the latest year) and the electricity balance (1990 on): produced,
imported, consumed by branch of the economy, lost in the public networks and exported (session 2462, chain 119:
Kyrgyzstan's electricity).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nsc_kyrgyzstan_electricity_annual.csv, from
two Excel files of stat.gov.kg's manufacturing pages, each with two sheets (the old classification to 2013, and GKED-3,
the current one, from 2011), two requests:

    https://www.stat.gov.kg/en/statistics/download/dynamic/344/    1.05.01.03 Production of electric power on power-stations
    https://www.stat.gov.kg/en/statistics/download/dynamic/1248/   1.05.01.02 Electro-balance of the economy

    entity     nsc_kg:KG; geo KG; node Kyrgyzstan; ts_utc the year's 1 January; freq P1Y; unit MWh (the committee's million
               kWh times 1,000)
    variable   from 1.05.01.03: generation (all power stations), generation_hydro, generation_thermal, generation_other
               from 1.05.01.02: produced, imports, consumption (the branches and the losses together, as the committee
               totals it), consumption_manufacturing, consumption_agriculture, consumption_transport,
               consumption_construction, consumption_public_utilities (to 2006: from 2007 the committee puts it in
               manufacturing) and consumption_social_services (the old classification, to 2010), consumption_other_activities (GKED-3, from 2011), network_losses, exports

The years 2011 to 2013 are in both sheets of each file; the old sheet gives the years before 2011 and GKED-3 the years from
2011, and the overlap must agree within 0.15 million kWh. The committee's footnotes, in its Kyrgyz and Russian columns:
imports "actually including flows" (transit); manufacturing including, from 2007 and in GKED-3, the electricity
distributed for communal and household needs and to the population. So consumption_manufacturing holds households' supply
from 2007; the header says so. The balance's "produced" and the stations' "generation" differ by up to 0.3 million kWh in
three years (2003, 2004, 2010); both are kept as published. A "-" has no row; a footnote mark in a cell ("4293,5 2") is
read as the number before it. Checks a year, within 0.15 million kWh (1.05 in a year whose figures are printed in whole
million kWh, 1990 to 2002): hydro, thermal and other add to generation; the branches and the losses add to consumption;
produced and imports equal consumption and exports. A check that fails is the committee's own figure: kept as published
and named in the header (one when written: 2001, where produced and imports are 55 million kWh over consumption and
exports); more than six stops the run. A label or a year not the committee's or a value that is not a number stops the
run. Nothing is filled.

    python warehouse/connectors/nsc_kyrgyzstan.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/nsc_kyrgyzstan/ with --offline. www.stat.gov.kg has no robots file (HTTP
404, sessions 2436 and 2462). License: the committee's open data page publishes its open data under Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 ("Based on data from the official website of the NSC KR www.stat.kg"); chain
117's verdict: may be public as the ERW is today, written permission if it sells anything; public, with the citation.
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

NAME = "nsc_kyrgyzstan_electricity_annual"
CONNECTOR = "nsc_kyrgyzstan"
SOURCE = "nsc_kg:dynamic_tables"
PAGE = "https://www.stat.gov.kg/en/statistics/promyshlennost/"
URLS = {"344": "https://www.stat.gov.kg/en/statistics/download/dynamic/344/",
        "1248": "https://www.stat.gov.kg/en/statistics/download/dynamic/1248/"}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]
GEN = {"The electric power are produced": "generation", "Hydroelectric power stations": "generation_hydro",
       "Thermoelectric power stations": "generation_thermal", "Otherelectric power stations": "generation_other"}
BAL = {"Electricity produced": "produced", "Electricity imported": "imports", "Electricity consumed in:": "consumption",
       "Manufacturing": "consumption_manufacturing", "Agriculture": "consumption_agriculture", "Transport": "consumption_transport",
       "Construction": "consumption_construction", "Public utilities": "consumption_public_utilities",
       "Social services": "consumption_social_services", "Other activities": "consumption_other_activities",
       "Transmission losses": "network_losses", "Electricity exported": "exports"}
TOL = 0.15
MAX_GAPS = 6  # the committee's own figures that fail a check, kept and named in the header; more stops the run


def num(v, what):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s in ("-", ""):
        return None
    m = re.fullmatch(r"(\d+(?:[.,]\d+)?)(?:\s+\d)?", s)  # "4293,5 2": the number, then a footnote mark
    if not m:
        raise RuntimeError(f"{what}: not a number: {v!r}")
    return float(m.group(1).replace(",", "."))


def sheet(d, labels, what):
    """{variable: {year: value}} of one sheet: the years on row 5, the English labels in the third column."""
    head = d.iloc[4].tolist()
    if str(head[2]).strip() != "Items":
        raise RuntimeError(f"{what}: the header is not the committee's: {head[:4]}")
    years = {}
    for j, v in enumerate(head[3:], start=3):
        if v is None or (isinstance(v, float) and pd.isna(v)):
            continue
        y = num(v, f"{what} year")
        if y is None or y != int(y) or not 1980 <= y <= 2100:
            raise RuntimeError(f"{what}: a year that does not read: {v!r}")
        years[j] = int(y)
    out = {}
    for i in range(6, d.shape[0]):
        lab = d.iloc[i, 2]
        if not isinstance(lab, str) or not lab.strip():
            continue
        lab = lab.strip()
        if lab not in labels:
            raise RuntimeError(f"{what}: a line not in the map: {lab!r}")
        var = labels[lab]
        if var in out:
            raise RuntimeError(f"{what}: {lab} twice")
        out[var] = {y: num(d.iloc[i, j], f"{what} {lab} {y}") for j, y in years.items()}
    return out


def joined(old, new, what):
    """The old classification's years before 2011 and GKED-3's from 2011, the overlap checked."""
    out = {}
    for var in set(old) | set(new):
        o, n = old.get(var, {}), new.get(var, {})
        for y in set(o) & set(n):
            if o[y] is not None and n[y] is not None and abs(o[y] - n[y]) > TOL:
                raise RuntimeError(f"{what} {var} {y}: the two sheets differ ({o[y]} and {n[y]})")
        vals = {y: v for y, v in o.items() if y < 2011}
        vals.update({y: v for y, v in n.items() if y >= 2011})
        out[var] = vals
    return out


def parse(gen_book, bal_book):
    """The rows from the two files' sheets ({sheet name: DataFrame} each): {(variable, year): (value, file)}."""
    gs = list(gen_book.items())
    bs = list(bal_book.items())
    if len(gs) != 2 or len(bs) != 2:
        raise RuntimeError("a file without its two sheets")
    gen = joined(sheet(gs[0][1], GEN, "1.05.01.03"), sheet(gs[1][1], GEN, "1.05.01.03 GKED-3"), "1.05.01.03")
    bal = joined(sheet(bs[0][1], BAL, "1.05.01.02"), sheet(bs[1][1], BAL, "1.05.01.02 GKED-3"), "1.05.01.02")
    g = lambda d, k, y: (d.get(k) or {}).get(y) or 0.0  # noqa: E731

    def tol(d, keys, y):  # a year printed in whole million kWh is checked to the rounding of its figures
        vals = [(d.get(k) or {}).get(y) for k in keys]
        return 1.05 if all(v is None or v == int(v) for v in vals) else TOL

    gaps = []
    kinds = ("generation", "generation_hydro", "generation_thermal", "generation_other")
    for y in gen["generation"]:
        if gen["generation"][y] is None:
            continue
        parts = sum(g(gen, k, y) for k in kinds[1:])
        if abs(parts - gen["generation"][y]) > tol(gen, kinds, y):
            gaps.append((y, "the kinds of station and generation", round(parts, 1), gen["generation"][y]))
    sectors = [k for k in BAL.values() if k.startswith("consumption_")]
    for y in bal["consumption"]:
        if bal["consumption"][y] is None:
            continue
        parts = sum(g(bal, k, y) for k in sectors) + g(bal, "network_losses", y)
        if abs(parts - bal["consumption"][y]) > tol(bal, sectors + ["network_losses", "consumption"], y):
            gaps.append((y, "the branches and losses and consumption", round(parts, 1), bal["consumption"][y]))
        supply = g(bal, "produced", y) + g(bal, "imports", y)
        if abs(supply - bal["consumption"][y] - g(bal, "exports", y)) > tol(bal, ["produced", "imports", "consumption", "exports"], y):
            gaps.append((y, "produced and imports, and consumption and exports", round(supply, 1), round(bal["consumption"][y] + g(bal, "exports", y), 1)))
    if len(gaps) > MAX_GAPS:
        raise RuntimeError(f"{len(gaps)} checks fail, more than {MAX_GAPS}: the files may have changed form; first {gaps[:3]}")
    out = {}
    for d, f in ((gen, "344"), (bal, "1248")):
        for var, vals in d.items():
            for y, v in vals.items():
                if v is not None:
                    out[(var, y)] = (v, f)
    return out, gaps


def finish(rows, retrieved, vintage):
    t = pd.DataFrame([dict(entity="nsc_kg:KG", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * 1000, 3), unit="MWh",
                           freq="P1Y", geo="KG", market="", node="Kyrgyzstan", source=SOURCE, source_url=URLS[f],
                           retrieved_at=retrieved.get(f, ""), vintage=vintage.get(f, "")) for (var, y), (v, f) in rows.items()], columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NSC Kyrgyzstan: generation by kind of station and the electricity balance, a year")
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
        if not args.offline and (ip.paused("nsc_kg") or ip.paused_host("www.stat.gov.kg")):
            raise RuntimeError("NSC Kyrgyzstan is paused (warehouse/metadata/paused_sources.csv): not requested")
        books, retrieved, vintage = {}, {}, {}
        for f, url in URLS.items():
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
            books[f] = pd.read_excel(io.BytesIO(content), sheet_name=None, header=None)
            retrieved[f], vintage[f] = rec.get("retrieved_at") or "", ip.vintage_of(rec)
        rows, gaps = parse(books["344"], books["1248"])
        t = finish(rows, retrieved, vintage)
        header = [
            f"Energy Research Warehouse (ERW): National Statistical Committee of the Kyrgyz Republic, generation by kind of power station and the electricity balance of the economy, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2462)",
            "Shape: series (docs/datastandard.md v0). entity nsc_kg:KG; unit MWh (the committee's million kWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo KG. variable: generation, generation_hydro, generation_thermal, generation_other (table 1.05.01.03); "
            "produced, imports, consumption (the branches and the network losses together), consumption_manufacturing, _agriculture, _transport, _construction, _public_utilities (to 2006; from 2007 within manufacturing) and _social_services (to 2010), _other_activities (from 2011), network_losses, exports (table 1.05.01.02).",
            f"{len(t)} rows. The old classification gives the years to 2010 and GKED-3 those from 2011; the two agree in 2011 to 2013. The committee's footnotes: imports include transit flows; manufacturing includes, from 2007, the electricity distributed for communal and household needs and to the population. "
            "The balance's produced and the stations' generation differ by up to 0.3 million kWh in three years; both are kept. Each year's kinds add to generation, the branches and losses to consumption, and produced and imports equal consumption and exports, within 0.15 million kWh (1.05 in a year printed in whole million kWh)"
            + ("".join(f"; in {y} {what} do not agree ({a:,.1f} against {b:,.1f} million kWh), the committee's figures kept as published" for y, what, a, b in gaps) if gaps else "")
            + ". Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nsc_kyrgyzstan.py; table 1.05.01.03 retrieved {retrieved['344']}, table 1.05.01.02 {retrieved['1248']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} National Statistical Committee of the Kyrgyz Republic, dynamic tables 1.05.01.03 and 1.05.01.02, {PAGE}",
            f"  access: {URLS['344']} and {URLS['1248']}",
            "License: public with the citation, under the committee's open data licence, Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (chain 117's verdict: may be public as the ERW is today; written permission if it sells anything). "
            "Based on data from the official website of the NSC KR www.stat.kg.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="National Statistical Committee of the Kyrgyz Republic",
                                    report="Dynamic tables 1.05.01.03 (production of electric power on power-stations) and 1.05.01.02 (electro-balance of the economy)",
                                    report_url=PAGE, document_list=URLS["344"], license="public", tables=[NAME])])
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
