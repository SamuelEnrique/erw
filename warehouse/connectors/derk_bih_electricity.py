#!/usr/bin/env python3
"""Bosnia and Herzegovina's electricity a year, 2021 to 2025, by utility: generation by plant type and consumption by
category, as the State Electricity Regulatory Commission (DERK, in English SERC) gives them in Annex C, "Balance Values
of the Electric Power Sector of Bosnia and Herzegovina", of its report on activities for 2025 (session 2547, chain 125;
the ERW held Bosnia and Herzegovina only in Eurostat's and EIA's international tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/derk_bih_electricity_annual.csv, from one PDF
(no key):

    https://www.derk.ba/DocumentsPDFs/Osnovni_EES_pokazatelji_BiH_en.pdf

The annex is one page of five blocks, one a year, each headed "Year YYYY" and the columns EP BIH, ERS, EP HZHB, Komunalno
Brcko, Other entities and BIH. A column's cell may be empty (EP HZHB has no thermal plant), so the page's text cannot tell
the columns apart: each block is read from the page's words by their place. Its heading words give the columns' right
edges (the figures are right-aligned); a figure belongs to the column whose edge is nearest its own; the words left of
the first column make the row's label.

    entity      derk:ba:<utility>: ep_bih, ers, ep_hzhb, komunalno_brcko, other_entities, total (the BIH column)
    variable    generation_hydro, generation_thermal, generation_solar_wind (larger solar and wind plants),
                generation_small_industrial, generation, consumption_distribution (customers connected to the
                distribution network), transmission_losses, consumption_large_customers, self_consumption_pumping,
                consumption
    unit        MWh (DERK's GWh, to two decimals, times 1,000); ts_utc the year's first day; freq P1Y; geo BA
    node        DERK's row label

An empty cell has no row. The run stops on a block not found, a row label not in the map, two figures under one column,
a figure of another form, a key given twice, a row whose BIH figure differs from the sum of the utilities by more than
0.05 GWh (BIH's consumption holds the transmission losses, given in its column only), a utility whose generation differs from its plant types or whose consumption from its parts by more than 0.05
GWh. Nothing is filled.

    python warehouse/connectors/derk_bih_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/derk_ba/ and reused unless --fresh; --offline asks nothing.
www.derk.ba's robots file closes Joomla's own folders only (session 2547). License: internal. DERK's site states "DERK (c)
2004-2026. All Rights Reserved." and gives no terms of reuse; internal until a ruling.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "derk_bih_electricity_annual"
CONNECTOR = "derk_ba"
SOURCE = "derk:annex_c_balance_2025"
HOST = "www.derk.ba"
URL = "https://www.derk.ba/DocumentsPDFs/Osnovni_EES_pokazatelji_BiH_en.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("State Electricity Regulatory Commission of Bosnia and Herzegovina (DERK/SERC), report on activities 2025, Annex C: "
            "Balance Values of the Electric Power Sector of Bosnia and Herzegovina")
# a column's heading word (the one that ends at the column's right edge) and its utility, in the page's order
COLS = [("BIH", "ep_bih"), ("ERS", "ers"), ("HZHB", "ep_hzhb"), ("Brčko", "komunalno_brcko"), ("entities", "other_entities"),
        ("BIH", "total")]
ROWS = {"Generation in hydropower plants": "generation_hydro", "Generation in thermal power plants": "generation_thermal",
        "Generation in larger solar and wind PPs": "generation_solar_wind", "Generation in small and industrial PPs": "generation_small_industrial",
        "Generation": "generation", "Customers connected to distr. network": "consumption_distribution",
        "Transmission losses": "transmission_losses", "Large customers": "consumption_large_customers",
        "PPs self-consumption and pumping": "self_consumption_pumping", "Consumption": "consumption"}
PARTS = [("generation", ["generation_hydro", "generation_thermal", "generation_solar_wind", "generation_small_industrial"]),
         ("consumption", ["consumption_distribution", "transmission_losses", "consumption_large_customers", "self_consumption_pumping"])]
FIG = r"\d{1,3}(?:,\d{3})*\.\d{2}"
X_COLS = ["x_label"]


def lines_of(words, tol=3):
    out = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if out and abs(w["top"] - out[-1][0]) <= tol:
            out[-1][1].append(w)
        else:
            out.append([w["top"], [w]])
    return [(top, sorted(ws, key=lambda w: w["x0"])) for top, ws in out]


def parse_words(words, base):
    lines = lines_of(words)
    starts = []
    for i, (top, ws) in enumerate(lines):
        texts = [w["text"] for w in ws]
        if "Year" in texts and texts.index("Year") + 1 < len(texts) and re.fullmatch(r"\d{4}", texts[texts.index("Year") + 1]):
            starts.append((i, top, texts[texts.index("Year") + 1]))
    if not starts:
        raise RuntimeError("no year block in the annex")
    rows, seen = [], set()
    for k, (i, top, year) in enumerate(starts):
        end = starts[k + 1][1] - 8 if k + 1 < len(starts) else 1e9  # the next block's first heading line sits about 5 above its "Year"
        near = [w for t, ws in lines if abs(t - top) <= 12 for w in ws]
        edges, used = [], set()
        for word, util in COLS:
            cands = sorted((w for w in near if w["text"] == word and id(w) not in used), key=lambda w: w["x0"])
            if not cands:
                raise RuntimeError(f"{year}: the heading {word!r} not found")
            w = cands[0] if util != "total" else cands[-1]
            used.add(id(w))
            edges.append((w["x1"], util))
        if [u for _, u in sorted(edges)] != [u for _, u in COLS]:
            raise RuntimeError(f"{year}: the headings are not in their order")
        left = min(x for x, _ in edges) - 45
        body = [(t, ws) for t, ws in lines if top + 8 < t < end]
        vals, got = {}, set()
        for t, ws in body:
            label = " ".join(w["text"] for w in ws if w["x1"] < left)
            figs = [w for w in ws if w["x1"] >= left]
            if not figs:
                continue
            if label not in ROWS:
                if any(re.fullmatch(FIG, w["text"]) for w in figs):
                    raise RuntimeError(f"{year}: a row not in the map: {label!r}")
                continue  # a heading's second line or the page's footer ("serc 2025 report on activities 81")
            if label in got:
                raise RuntimeError(f"{year}: {label!r} given twice")
            got.add(label)
            var, cells = ROWS[label], {}
            for w in figs:
                if not re.fullmatch(FIG, w["text"]):
                    raise RuntimeError(f"{year} {label}: not a figure: {w['text']!r}")
                util = min(edges, key=lambda e: abs(e[0] - w["x1"]))[1]
                if util in cells:
                    raise RuntimeError(f"{year} {label}: two figures under {util}")
                cells[util] = float(w["text"].replace(",", ""))
            for util, v in cells.items():
                key = (var, util, year)
                if key in seen:
                    raise RuntimeError(f"{key} given twice")
                seen.add(key)
                vals[(var, util)] = v
                rows.append(dict(entity=f"derk:ba:{util}", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=round(v * 1000, 3), unit="MWh",
                                 freq="P1Y", geo="BA", market="", node=label, **base, x_label=label))
        if got != set(ROWS):
            raise RuntimeError(f"{year}: rows missing: {sorted(set(ROWS) - got)}")
        for var in ROWS.values():
            utils = [u for _, u in COLS if u != "total" and (var, u) in vals]
            # BIH's consumption holds the transmission losses, given in the BIH column only
            extra = vals.get(("transmission_losses", "total"), 0.0) if var == "consumption" else 0.0
            if (var, "total") in vals and utils and abs(sum(vals[(var, u)] for u in utils) + extra - vals[(var, "total")]) > 0.05:
                raise RuntimeError(f"{year} {var}: the utilities sum to {sum(vals[(var, u)] for u in utils):.2f}, not to BIH's {vals[(var, 'total')]}")
        for whole, parts in PARTS:
            for _, util in COLS:
                if (whole, util) in vals:
                    s = sum(vals.get((p, util), 0.0) for p in parts)
                    if abs(s - vals[(whole, util)]) > 0.05:
                        raise RuntimeError(f"{year} {util}: {whole} {vals[(whole, util)]} is not the sum of its parts {s:.2f}")
    return pd.DataFrame(rows), [y for _, _, y in starts]


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [pg for pg in pdf.pages if "Balance Values of the Electric Power Sector" in (pg.extract_text() or "")]
        if len(pages) != 1:
            raise RuntimeError(f"the annex's page found {len(pages)} times")
        return parse_words(pages[0].extract_words(), base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="DERK: Bosnia and Herzegovina's electricity balance by utility, a year")
    ap.add_argument("--offline", action="store_true", help="the saved annex only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the annex again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t, years = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        v = {(x, e.split(":")[-1], ts[:4]): val for x, e, ts, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
        last = max(years)
        head = [
            "Energy Research Warehouse (ERW): State Electricity Regulatory Commission of Bosnia and Herzegovina (DERK/SERC), report on activities "
            f"2025, Annex C: Bosnia and Herzegovina's electricity balance by utility, {min(years)} to {last} (session 2547)",
            "Shape: series (docs/datastandard.md v0). entity derk:ba:<utility> (ep_bih, ers, ep_hzhb, komunalno_brcko, other_entities, total); "
            "variable generation by plant type and in total, consumption by category and in total, transmission_losses; unit MWh (DERK's GWh "
            "times 1,000); ts_utc the year's first day; freq P1Y; geo BA; node DERK's row label.",
            f"{len(t)} rows; in {last} generation {v[('generation', 'total', last)] / 1e6:.3f} TWh, consumption "
            f"{v[('consumption', 'total', last)] / 1e6:.3f} TWh. An empty cell has no row; each BIH figure equals the sum of the utilities (its consumption with the transmission losses); "
            "nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/derk_bih_electricity.py; the annex retrieved {base['retrieved_at']}; last "
            f"modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            f"License: internal. DERK's site states \"DERK (c) 2004-2026. All Rights Reserved.\"; no terms of reuse; internal until a ruling. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities, years {', '.join(sorted(years))}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="State Electricity Regulatory Commission of Bosnia and Herzegovina (DERK)",
                                    report="Report on activities 2025, Annex C: Balance Values of the Electric Power Sector of Bosnia and Herzegovina",
                                    report_url=URL, document_list="https://www.derk.ba/en/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
