#!/usr/bin/env python3
"""Suriname's electricity a year: EBS's demand by category (2019 to 2023), its net generation and net consumption (2019 to
2023), its installed and available capacity (2019 to 2021), and Staatsolie's generation for EBS at Afobaka (hydro) and Tout
Lui Faut (thermal) and its back-up plant in Saramacca (2019 to 2023), as the Algemeen Bureau voor de Statistiek (ABS) gives
them in tables 7.1, 7.4, 7.8 and 7.9 of its eleventh Milieustatistieken / Environment Statistics publication (December
2024), from N.V. EnergieBedrijven Suriname (EBS) and Staatsolie (session 2563, chain 126; the ERW held Suriname only in
EIA's international table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/abs_suriname_electricity_annual.csv, from one
PDF (no key):

    https://statistics-suriname.org/wp-content/uploads/2024/12/Elfde-Milieustatistieken-pub-dec-2024.pdf

    entity      abs_sr:ebs (net_generation, net_consumption, installed_capacity, available_capacity);
                abs_sr:ebs:<category> (demand: residential, commercial, industrial, other, total);
                abs_sr:staatsolie:<plant> (generation: afobaka_hydro, tout_lui_faut_thermal, saramacca_backup)
    unit        MWh (table 7.4's kWh divided by 1,000; table 7.8's billion kWh times 1,000,000; table 7.9's GWh times
                1,000, its MWh as given); MW (table 7.1); ts_utc the year's first day; freq P1Y; geo SR
    node        ABS's label (English part)

Each table's page is found by its title line as printed above the table (the contents page prints the titles run
together with others), and read from its title to its "Bron" line. Table 7.8 prints its billions with a comma or a point
for the decimal ("1,366", "1.377"): both are read as the decimal, and every figure must fall between 0.5 and 5 billion
kWh, net consumption below net generation. Table 7.4's four categories are checked against its total (within 1 MWh),
table 7.1's available capacity against its installed. Not taken: the connections (7.2, 7.3), the sales by district
(7.5, whose total of 132.7 GWh in 2023 does not agree with table 7.4's 1,408.1 GWh), the prices (7.6, SRD) and 7.8's
capacity in GW (7.1 gives it in MW). Nothing is filled.

    python warehouse/connectors/abs_suriname_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/abs_sr/ and reused unless --fresh; --offline asks nothing.
statistics-suriname.org's robots file asks a crawl delay of 30 seconds (session 2563), kept by the one request.
License: public. ABS's site: "Except where otherwise noted, content on this site is licensed under a Creative Commons
Attribution 4.0 International license."; the publication notes no other license ("Copyright December 2024 ABS").
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

NAME = "abs_suriname_electricity_annual"
CONNECTOR = "abs_sr"
SOURCE = "abs_sr:milieustatistieken_2024_tables_7_1_7_4_7_8_7_9"
HOST = "statistics-suriname.org"
URL = "https://statistics-suriname.org/wp-content/uploads/2024/12/Elfde-Milieustatistieken-pub-dec-2024.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Algemeen Bureau voor de Statistiek in Suriname (ABS), Milieustatistieken Publicatie / Environment Statistics "
            "Publication, December 2024, tables 7.1, 7.4, 7.8 and 7.9 (sources: N.V. EnergieBedrijven Suriname; Staatsolie)")
TITLES = {"7.1": r"Tabel 7\.1: Beschikbaar en ge.nstalleerd vermogen \(MW\), (\d{4})-(\d{4})",
          "7.4": r"Tabel 7\.4: Elektriciteitsvraag \(kWh\), (\d{4})-(\d{4})",
          "7.8": r"Tabel 7\.8: Geselecteerde energiedata van EnergieBedrijven Suriname \(EBS\), (\d{4})-(\d{4})",
          "7.9": r"Tabel 7\.9: Elektriciteitsopwekking door Staatsolie Maatschappij Suriname, (\d{4})-(\d{4})"}
DEMAND = [("Huishoudens/Residential", "residential"), ("Bedrijven/Commercial", "commercial"), ("Industrieel/Industrial", "industrial"),
          ("Anders/Other", "other"), ("Totaal/Total", "total")]
# table 7.9: the line above each figure line, its unit and its plant
PLANTS = [("Energie productie/ Energy production", "MWh", "saramacca_backup", "Energy production (back-up production in Saramacca)"),
          ("Tout Lui Faut Thermal Power Plant t.b.v. EBS/", "GWh", "tout_lui_faut_thermal", "Tout Lui Faut Thermal Power Plant for the purpose of EBS"),
          ("Afobaka Hydro Operations t.b.v. EPAR (EBS)/", "GWh", "afobaka_hydro", "Afobaka Hydro Operations for the purpose of EPAR (EBS)")]
FIG = r"\d{1,3}(?:,\d{3})*"
X_COLS = ["x_table"]


def block(texts, key):
    """The table's lines, title to its source line, and its years."""
    hits = [(i, j) for i, t in enumerate(texts) for j, ln in enumerate(t) if re.fullmatch(TITLES[key], ln)]
    if len(hits) != 1:
        raise RuntimeError(f"table {key}: its title found {len(hits)} times")
    i, j = hits[0]
    m = re.fullmatch(TITLES[key], texts[i][j])
    years = list(range(int(m.group(1)), int(m.group(2)) + 1))
    out = []
    for ln in texts[i][j + 1:]:
        if ln.startswith("Bron"):
            return out, years
        out.append(ln)
    raise RuntimeError(f"table {key}: no source line after the title")


def head_years(lines, years, key):
    want = " ".join(str(y) for y in years)
    if not any(re.sub(r"#", "", ln).endswith(want) for ln in lines):
        raise RuntimeError(f"table {key}: no header line of the years {want}")


def row(entity, variable, year, value, unit, node, table, base):
    return dict(entity=entity, variable=variable, ts_utc=f"{year}-01-01T00:00:00Z", value=round(value, 3), unit=unit, freq="P1Y",
                geo="SR", market="", node=node, **base, x_table=table)


def parse_demand(lines, years, base):
    head_years(lines, years, "7.4")
    vals, out = {}, []
    for label, item in DEMAND:
        hit = [ln for ln in lines if re.fullmatch(re.escape(label) + r"( " + FIG + r")+", ln)]
        if len(hit) != 1:
            raise RuntimeError(f"table 7.4: {label!r} found {len(hit)} times")
        figs = [float(f.replace(",", "")) for f in hit[0][len(label):].split()]
        if len(figs) != len(years):
            raise RuntimeError(f"table 7.4: {label!r} has {len(figs)} figures for {len(years)} years")
        for y, v in zip(years, figs):
            vals[(item, y)] = v / 1000
            out.append(row(f"abs_sr:ebs:{item}", "demand", y, v / 1000, "MWh", label.split("/")[-1], "7.4", base))
    for y in years:
        s = sum(vals[(i, y)] for _, i in DEMAND[:-1])
        if abs(s - vals[("total", y)]) > 1:
            raise RuntimeError(f"table 7.4 {y}: the categories make {s}, the total {vals[('total', y)]}")
    return out


def parse_selected(lines, years, base):
    head_years(lines, years, "7.8")
    found = {}
    for var, pat in (("net_generation", r"Billion"), ("net_consumption", r"Net Consumptie/ Net Consumption")):
        hit = [ln for ln in lines if re.fullmatch(pat + r"( \d[.,]\d{3})+", ln)]
        if len(hit) != 1:
            raise RuntimeError(f"table 7.8: the {var} line found {len(hit)} times")
        figs = [float(f.replace(",", ".")) for f in hit[0][len(pat):].split()]
        if len(figs) != len(years) or not all(0.5 <= v <= 5 for v in figs):
            raise RuntimeError(f"table 7.8: {var} {figs} is not {len(years)} figures of 0.5 to 5 billion kWh")
        found[var] = figs
    if not all(c < g for c, g in zip(found["net_consumption"], found["net_generation"])):
        raise RuntimeError("table 7.8: net consumption is not below net generation")
    nodes = {"net_generation": "Total Electricity Net Generation", "net_consumption": "Net Consumption"}
    return [row("abs_sr:ebs", var, y, v * 1e6, "MWh", nodes[var], "7.8", base) for var, figs in found.items() for y, v in zip(years, figs)]


def parse_staatsolie(lines, years, base):
    head_years(lines, years, "7.9")
    out = []
    for above, unit, item, node in PLANTS:
        at = [k for k, ln in enumerate(lines) if ln == above]
        if len(at) != 1 or at[0] + 1 >= len(lines):
            raise RuntimeError(f"table 7.9: {above!r} found {len(at)} times")
        m = re.fullmatch(re.escape(unit) + r"((?: \d+)+)", lines[at[0] + 1])
        if not m:
            raise RuntimeError(f"table 7.9: no {unit} line below {above!r}: {lines[at[0] + 1]!r}")
        figs = [float(f) for f in m.group(1).split()]
        if len(figs) != len(years):
            raise RuntimeError(f"table 7.9: {item} has {len(figs)} figures for {len(years)} years")
        k = 1000 if unit == "GWh" else 1
        out += [row(f"abs_sr:staatsolie:{item}", "generation", y, v * k, "MWh", node, "7.9", base) for y, v in zip(years, figs)]
    return out


def parse_capacity(lines, years, base):
    if "Jaar/Year Installed Capacity Available Capacity" not in lines:
        raise RuntimeError("table 7.1: its header line not found")
    out = []
    for y in years:
        hit = [ln for ln in lines if re.fullmatch(rf"{y}#? (\d+\.\d) (\d+\.\d)", ln)]
        if len(hit) != 1:
            raise RuntimeError(f"table 7.1: {y} found {len(hit)} times")
        inst, avail = (float(v) for v in re.fullmatch(rf"{y}#? (\d+\.\d) (\d+\.\d)", hit[0]).groups())
        if avail > inst:
            raise RuntimeError(f"table 7.1 {y}: available {avail} MW above installed {inst} MW")
        out += [row("abs_sr:ebs", "installed_capacity", y, inst, "MW", "Installed Capacity", "7.1", base),
                row("abs_sr:ebs", "available_capacity", y, avail, "MW", "Available Capacity", "7.1", base)]
    return out


def parse_texts(texts, base):
    """texts: each page's lines."""
    out = []
    for key, fn in (("7.1", parse_capacity), ("7.4", parse_demand), ("7.8", parse_selected), ("7.9", parse_staatsolie)):
        lines, years = block(texts, key)
        out += fn(lines, years, base)
    return pd.DataFrame(out)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        texts = [(pg.extract_text() or "").split("\n") for pg in pdf.pages]
    return parse_texts(texts, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ABS: Suriname's electricity demand, generation and capacity (EBS, Staatsolie)")
    ap.add_argument("--offline", action="store_true", help="the saved publication only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the publication again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=300, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        v = {(x, e, ts[:4]): val for x, e, ts, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
        last = max(t.ts_utc.str[:4])
        head = [
            "Energy Research Warehouse (ERW): Algemeen Bureau voor de Statistiek (ABS), Suriname, Milieustatistieken / Environment "
            "Statistics Publication (December 2024), tables 7.1, 7.4, 7.8 and 7.9: EBS's demand, generation and capacity, Staatsolie's "
            "generation (session 2563)",
            "Shape: series (docs/datastandard.md v0). entity abs_sr:ebs, abs_sr:ebs:<category> or abs_sr:staatsolie:<plant>; variable "
            "demand, net_generation, net_consumption, generation, installed_capacity, available_capacity; unit MWh or MW; ts_utc the "
            "year's first day; freq P1Y; geo SR; node ABS's label; x_table the table.",
            f"{len(t)} rows; in {last} EBS's net generation {v[('net_generation', 'abs_sr:ebs', last)] / 1e6:.3f} TWh, demand "
            f"{v[('demand', 'abs_sr:ebs:total', last)] / 1e6:.3f} TWh, Afobaka {v[('generation', 'abs_sr:staatsolie:afobaka_hydro', last)] / 1e6:.3f} TWh. "
            "Table 7.8's billions read with a comma or a point as the decimal; the sales by district (7.5), the connections and the "
            "prices are not taken; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/abs_suriname_electricity.py; the publication retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            "License: public. ABS licenses its site's content under Creative Commons Attribution 4.0 International except where otherwise "
            f"noted; the publication notes no other license. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Algemeen Bureau voor de Statistiek in Suriname (ABS)",
                                    report="Milieustatistieken Publicatie / Environment Statistics Publication, December 2024, tables 7.1, 7.4, 7.8 and 7.9",
                                    report_url=URL, document_list="https://statistics-suriname.org/milieustatistieken-2/", license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
