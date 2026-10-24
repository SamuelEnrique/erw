#!/usr/bin/env python3
"""Zambia's electricity a year, from the Energy Regulation Board's Statistical Bulletin 2025: generation by power station
(ZESCO's large hydro, mini hydro and diesel plants and the independent power producers), 2013 to 2025; consumption by
economic sector, 2015 to 2025; exports by exporter and ZESCO's imports, 2024 and 2025; installed capacity by technology,
2025 (session 2420, chain 115: Zambia's generation and demand).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/erb_zambia_electricity_annual.csv, from the
bulletin's tables 13 to 19 and 26 (read with pdfplumber: the text lines, and table 16's columns by its table extraction),
one request:

    https://www.erb.org.zm/wp-content/uploads/files/statBullet2025.pdf

    entity     erb_zm:station:<slug>     a power station (node its name, x_group its table's group)
               erb_zm:group:<group>      a table's printed total: zesco_major_hydro (table 13), zesco_mini_hydro (14),
                                         zesco_diesel (15), ipp (16)
               erb_zm:sector:<slug>      an economic sector's consumption (table 19), total its Grand Total
               erb_zm:exporter:<slug>    exports by exporter (table 17): the power traders, their total, ZESCO, and total
               erb_zm:importer:zesco     ZESCO's imports (table 18)
               erb_zm:technology:<slug>  installed capacity by technology (table 26), total its Total
    variable   generation, consumption, exports, imports (MWh: ERB's GWh times 1,000); capacity (MW)
    ts_utc     the year's 1 January; freq P1Y; geo ZM

ERB writes "-" where a plant had no output or a sector no figure: no row. A "0" is kept. Each table's rows must add to its
printed total within 0.1 GWh (0.1 MW), and the four groups' totals for 2025 to table 12's national total; a header not
ERB's, a station or label not in the map, a value that is not a number or a failed check stops the run.

Table 17's power traders' total for 2025 (544.17 GWh) leaves out Africa GreenCo's 12.96 GWh listed above it; the rows
and totals are kept as printed, and that one gap is allowed (any other stops the run).

Table 12's own IPP line for 2025 (5,873.17 GWh) is 2.50 GWh under table 16's IPP total (5,875.67), the CEC emergency
generators' 2.50; table 12's national total (14,560.23) equals the four groups' totals. Table 12 is a check only.

Table 19's 2019 column is the same as its 2021 column in every sector (12,831.30 GWh in all); the 2022 bulletin gives
these figures as 2021's (12,831,360.78 MWh), so 2019's are not taken while the two columns are equal (session 2420).
The bulletin's other years are not checked against earlier bulletins. Earlier bulletins are not read here. Imports are
ZESCO's only (table 18): the bulletin's figure 6 also charts the power traders' imports, as a chart, not taken.

    python warehouse/connectors/erb_zambia.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/erb_zambia/ with --offline. www.erb.org.zm's robots file disallows only
/wp-admin/ and names no AI agent (session 2420). License: internal; session 2425's verdict, needs written permission: the site's footer reads "Copyright
2026 All Rights Reserved", and no page read states terms of reuse.
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

NAME = "erb_zambia_electricity_annual"
CONNECTOR = "erb_zambia"
SOURCE = "erb_zm:statistical_bulletin"
PAGE = "https://www.erb.org.zm/statistics"
URL = "https://www.erb.org.zm/wp-content/uploads/files/statBullet2025.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_group", "x_table"]
TOL = 0.1

# tables 13 to 15: the header line as printed, and the stations in its order
LINE_TABLES = {
    "13": ("zesco_major_hydro", "Year Kafue Gorge Kariba North Bank Victoria falls Total (GWh)",
           ["Kafue Gorge", "Kariba North Bank", "Victoria Falls"]),
    "14": ("zesco_mini_hydro", "Year Chishimba Falls Lunzua Lusiwasi Lower Lusiwasi Upper Musonda Falls Shiwan'gandu Total (GWh)",
           ["Chishimba Falls", "Lunzua", "Lusiwasi Lower", "Lusiwasi Upper", "Musonda Falls", "Shiwan'gandu"]),
    "15": ("zesco_diesel", "Year Chama Itezhi tezhi Kabompo Luangwa Lundazi Shang'ombo Zambezi Total (GWh)",
           ["Chama", "Itezhi Tezhi (diesel)", "Kabompo", "Luangwa", "Lundazi", "Shang'ombo", "Zambezi"]),
}
IPPS = ["Bangweulu Power Limited", "Itezhi tezhi Power Corporation", "Kafue Gorge Lower", "Kariba North Bank Extension",
        "Lunsemfwa Hydro Power Limited", "Maamba Energy Limited", "Ndola Energy Corporation Limited", "Kafue Gorge Mini Hydro",
        "Chisamba", "Solar century", "United Capital Fertiliser", "Ngonye Power Limited", "Dangote", "CEC Emergency Generators"]
SECTORS = {"Agriculture": "agriculture", "Construction": "construction", "Domestic (Including households)": "domestic",
           "Energy and water": "energy_and_water", "Finance and property": "finance_and_property",
           "Manufacturing": "manufacturing", "Mining": "mining", "Others": "others", "PSA": "psa", "Trade": "trade",
           "Transport": "transport", "Grand Total": "total"}
EXPORTERS = {"Enterprise Power": "enterprise_power", "Kanona Power Company Limited": "kanona_power",
             "Africa GreenCo": "africa_greenco", "Petrodex": "petrodex",
             "Power Trader Total Exports (GWh)": "power_traders_total", "ZESCO ZESCO": "zesco",
             "ZESCO Total Exports (GWh)": None, "Grand Total Exports (GWh)": "total"}
TECHNOLOGIES = {"Hydro": "hydro", "Coal": "coal", "Diesel": "diesel", "Solar": "solar", "Heavy Fuel Oil": "heavy_fuel_oil",
                "Total": "total"}
NUM = r"-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower().replace("'", "")).strip("_")


def num(tok, what):
    t = (tok or "").strip()
    if t == "-":
        return None
    if not re.fullmatch(NUM, t):
        raise RuntimeError(f"{what}: not a number: {t!r}")
    return float(t.replace(",", ""))


def adds(parts, total, what):
    got = sum(v for v in parts if v is not None)
    if total is None or abs(got - total) > TOL:
        raise RuntimeError(f"{what}: the parts add to {got:.2f}, the printed total is {total}")


def segment(text, n):
    """The body text of table n: from its last title (the list of tables comes first) to the next table's title."""
    i = text.rfind(f"Table {n}:")
    if i < 0:
        raise RuntimeError(f"no Table {n} in the bulletin")
    j = text.find("Table ", i + 10)
    return text[i:j if j > 0 else len(text)]


def read(content):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        texts = [(p.extract_text() or "").replace("’", "'").replace("‘", "'") for p in pdf.pages]
        text = "\n".join(texts)
        k = max(i for i, t in enumerate(texts) if "Table 16:" in t)
        tables = pdf.pages[k].extract_tables()
    return parse(text, tables)


def parse(text, tables):
    """The rows from the bulletin's text and Table 16's page tables (as pdfplumber gives them)."""
    out = []  # (entity, variable, year, value, unit, node, group, table)

    for n, (group, header, stations) in LINE_TABLES.items():
        seg = segment(text, n)
        lines = seg.splitlines()
        if header not in lines:
            raise RuntimeError(f"Table {n}'s header is not ERB's: {lines[1:2]}")
        years = set()
        for line in lines:
            m = re.match(r"(20\d\d) (.+)$", line)
            if not m:
                continue
            y, toks = int(m.group(1)), m.group(2).split()
            if len(toks) != len(stations) + 1:
                raise RuntimeError(f"Table {n} {y}: {len(toks)} values, not {len(stations) + 1}")
            vals = [num(t, f"Table {n} {y}") for t in toks]
            adds(vals[:-1], vals[-1], f"Table {n} {y}")
            if y in years:
                raise RuntimeError(f"Table {n}: {y} twice")
            years.add(y)
            for s, v in zip(stations, vals):
                if v is not None:
                    out.append((f"erb_zm:station:{slug(s)}", "generation", y, v * 1000, "MWh", s, group, n))
            out.append((f"erb_zm:group:{group}", "generation", y, vals[-1] * 1000, "MWh", f"{group} (Table {n} total)", group, n))
        if min(years) != 2013 or len(years) != max(years) - 2012:
            raise RuntimeError(f"Table {n}: years {sorted(years)}")

    ipp = next((t for t in tables if t and (t[0][0] or "").strip() == "Year" and "Bangweulu" in " ".join(c or "" for c in t[0])), None)
    if ipp is None:
        raise RuntimeError("no Table 16 (the IPPs) on its page")
    names = [re.sub(r"\s+", " ", c).strip() for c in ipp[0] if c]
    if names != ["Year"] + IPPS + ["Total GWh"]:
        raise RuntimeError(f"Table 16's header is not ERB's: {names}")
    years = set()
    for row in ipp[1:]:
        cells = [c.strip() for c in row if c and c.strip()]
        if not cells:
            continue
        y = int(cells[0]) if re.fullmatch(r"20\d\d", cells[0]) else None
        if y is None or len(cells) != len(IPPS) + 2:
            raise RuntimeError(f"Table 16: a row that does not read: {cells}")
        vals = [num(t, f"Table 16 {y}") for t in cells[1:]]
        adds(vals[:-1], vals[-1], f"Table 16 {y}")
        years.add(y)
        for s, v in zip(IPPS, vals):
            if v is not None:
                out.append((f"erb_zm:station:{slug(s)}", "generation", y, v * 1000, "MWh", s, "ipp", "16"))
        out.append(("erb_zm:group:ipp", "generation", y, vals[-1] * 1000, "MWh", "ipp (Table 16 total)", "ipp", "16"))
    if sorted(years) != list(range(2013, max(years) + 1)):
        raise RuntimeError(f"Table 16: years {sorted(years)}")

    seg = segment(text, "12")
    nat = {}
    for line in seg.splitlines():
        m = re.match(rf"(ZESCO's Major-Hydro|ZESCO's Mini-Hydro|ZESCO's Diesel|IPPs|Total) ({NUM})$", line)
        if m:
            nat[m.group(1)] = num(m.group(2), "Table 12")
    m = re.search(r"Table 12: National Electricity Generation (\d{4})", seg)
    if len(nat) != 5 or not m:
        raise RuntimeError(f"Table 12 does not read: {nat}")
    ny = int(m.group(1))
    groups = [v for e, var, y, v, *_ in out if e.startswith("erb_zm:group:") and y == ny]
    if len(groups) != 4 or abs(sum(groups) / 1000 - nat["Total"]) > TOL:
        raise RuntimeError(f"the four groups' {ny} totals add to {sum(groups) / 1000:.2f}, Table 12's total is {nat['Total']}")

    seg = segment(text, "19")
    lines = seg.splitlines()
    head = next((l for l in lines if l.startswith("Electricity Consumption (GWh) ")), "")
    years = [int(y) for y in head.split()[3:]]
    if not years or years != list(range(years[0], years[0] + len(years))):
        raise RuntimeError(f"Table 19's header is not ERB's: {head!r}")
    cons = {}
    for line in lines:
        for label in SECTORS:
            if line.startswith(label + " "):
                toks = line[len(label) + 1:].split()
                if len(toks) != len(years):
                    raise RuntimeError(f"Table 19 {label}: {len(toks)} values")
                cons[label] = [num(t, f"Table 19 {label}") for t in toks]
    if set(cons) != set(SECTORS):
        raise RuntimeError(f"Table 19: rows missing: {set(SECTORS) - set(cons)}")
    for k, y in enumerate(years):
        adds([cons[l][k] for l in SECTORS if l != "Grand Total"], cons["Grand Total"][k], f"Table 19 {y}")
    drop = set()
    if 2019 in years and 2021 in years and all(cons[l][years.index(2019)] == cons[l][years.index(2021)] for l in SECTORS):
        drop.add(2019)
    for label, s in SECTORS.items():
        for y, v in zip(years, cons[label]):
            if v is not None and y not in drop:
                out.append((f"erb_zm:sector:{s}", "consumption", y, v * 1000, "MWh", label, "consumption", "19"))

    seg = segment(text, "17")
    lines = seg.splitlines()
    m = next((re.match(r"Exporter Trader Name (\d{4}) (\d{4}) % Change$", l) for l in lines if l.startswith("Exporter ")), None)
    if not m:
        raise RuntimeError("Table 17's header is not ERB's")
    ty = [int(m.group(1)), int(m.group(2))]
    exp = {}
    for line in lines:
        for label in EXPORTERS:
            mm = re.fullmatch(rf"{re.escape(label)} ({NUM}|-) ({NUM}|-) -?[\d.,]+%", line)
            if mm:
                exp[label] = [num(mm.group(1), label), num(mm.group(2), label)]
    if set(exp) != set(EXPORTERS):
        raise RuntimeError(f"Table 17: rows missing: {set(EXPORTERS) - set(exp)}")
    traders = ["Enterprise Power", "Kanona Power Company Limited", "Africa GreenCo", "Petrodex"]
    short = {}
    for k, y in enumerate(ty):
        parts = sum(exp[l][k] or 0 for l in traders)
        gap = round(parts - exp["Power Trader Total Exports (GWh)"][k], 2)
        if abs(gap) > TOL:
            if gap != exp["Africa GreenCo"][k]:  # ERB's 2025 trader total leaves out Africa GreenCo's exports (session 2420)
                adds([exp[l][k] for l in traders], exp["Power Trader Total Exports (GWh)"][k], f"Table 17 traders {y}")
            short[y] = gap
        adds([exp["Power Trader Total Exports (GWh)"][k], exp["ZESCO ZESCO"][k]], exp["Grand Total Exports (GWh)"][k], f"Table 17 {y}")
        if exp["ZESCO ZESCO"][k] != exp["ZESCO Total Exports (GWh)"][k]:
            raise RuntimeError(f"Table 17 {y}: ZESCO's row and its total differ")
    for label, s in EXPORTERS.items():
        if s:
            for y, v in zip(ty, exp[label]):
                if v is not None:
                    out.append((f"erb_zm:exporter:{s}", "exports", y, v * 1000, "MWh", label.replace(" (GWh)", "").replace("ZESCO ZESCO", "ZESCO"), "trade", "17"))
    seg = segment(text, "18")
    m = re.search(rf"Importer (\d{{4}}) (\d{{4}}) % Change\nZESCO ({NUM}) ({NUM}) ", seg)
    if not m or [int(m.group(1)), int(m.group(2))] != ty:
        raise RuntimeError("Table 18 does not read")
    for y, g in zip(ty, (3, 4)):
        out.append(("erb_zm:importer:zesco", "imports", y, num(m.group(g), "Table 18") * 1000, "MWh", "ZESCO", "trade", "18"))

    seg = segment(text, "26")
    m = re.search(r"Technology (\d{4}) Installed Capacity \(MW\) % Share", seg)
    if not m:
        raise RuntimeError("Table 26's header is not ERB's")
    cy = int(m.group(1))
    cap = {}
    for line in seg.splitlines():
        for label in TECHNOLOGIES:
            mm = re.fullmatch(rf"{re.escape(label)} ({NUM}) [\d.]+%", line)
            if mm:
                cap[label] = num(mm.group(1), label)
    if set(cap) != set(TECHNOLOGIES):
        raise RuntimeError(f"Table 26: rows missing: {set(TECHNOLOGIES) - set(cap)}")
    adds([v for l, v in cap.items() if l != "Total"], cap["Total"], "Table 26")
    for label, s in TECHNOLOGIES.items():
        out.append((f"erb_zm:technology:{s}", "capacity", cy, cap[label], "MW", label, "capacity", "26"))
    return out, drop, nat, short


def finish(rows, retrieved, vintage):
    t = pd.DataFrame([dict(entity=e, variable=v, ts_utc=f"{y}-01-01T00:00:00Z", value=round(x, 3), unit=u, freq="P1Y", geo="ZM",
                           market="", node=node, source=SOURCE, source_url=URL, retrieved_at=retrieved, vintage=vintage,
                           x_group=g, x_table=f"Table {n}") for e, v, y, x, u, node, g, n in rows], columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"a key given twice: {t[t.duplicated(['entity', 'variable', 'ts_utc'], keep=False)].entity.tolist()[:4]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERB's Statistical Bulletin 2025: Zambia's generation by station, consumption, trade and capacity")
    ap.add_argument("--offline", action="store_true", help="the saved bulletin only, no request")
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
        if not args.offline and (ip.paused("erb_zm") or ip.paused_host("www.erb.org.zm")):
            raise RuntimeError("ERB is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
        rows, drop, nat, short = read(content)
        t = finish(rows, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        gen = t[t.variable == "generation"]
        header = [
            f"Energy Research Warehouse (ERW): Energy Regulation Board (ERB), Zambia, Statistical Bulletin 2025: generation by power station {gen.ts_utc.min()[:4]} to {gen.ts_utc.max()[:4]}, consumption by sector, exports and imports, installed capacity by technology (session 2420)",
            "Shape: series (docs/datastandard.md v0). entity erb_zm:station:<slug> (a power station; x_group zesco_major_hydro, zesco_mini_hydro, zesco_diesel or ipp), erb_zm:group:<group> (a table's printed total), erb_zm:sector:<slug> (consumption by economic sector; total ERB's Grand Total; psa as ERB labels it), "
            "erb_zm:exporter:<slug>, erb_zm:importer:zesco, erb_zm:technology:<slug>; variable generation, consumption, exports, imports (MWh, ERB's GWh times 1,000) or capacity (MW); ts_utc the year's 1 January; freq P1Y; geo ZM; x_table the bulletin's table.",
            f"{len(t)} rows. ERB's \"-\" has no row; a 0 is kept. Each table's rows add to its printed total within 0.1 GWh (MW), and the four groups' 2025 totals to Table 12's national total ({nat['Total']:,.2f} GWh); Table 12's IPP line ({nat['IPPs']:,.2f}) is under Table 16's IPP total by the CEC emergency generators' output. "
            "Itezhi Tezhi (diesel) is ZESCO's diesel plant, not the IPP Itezhi tezhi Power Corporation's hydro plant. Nothing is filled.",
            ("Consumption for 2019 is not taken: the bulletin's 2019 column is the same as its 2021 column in every sector, and the 2022 bulletin gives these figures as 2021's. " if 2019 in drop else "")
            + "".join(f"Table 17's power traders' total for {y} is {g:,.2f} GWh under its trader rows, Africa GreenCo's exports, as printed; ZESCO's and the traders' totals add to the grand total. " for y, g in short.items())
            + "Exports and imports are 2024 and 2025 only, and imports are ZESCO's only (Table 18; the bulletin's Figure 6 also charts the power traders' imports, not taken); installed capacity 2025 only; the bulletin gives no system peak demand.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/erb_zambia.py; the bulletin retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Energy Regulation Board, Zambia, 2025 Statistical Bulletin, tables 12 to 19 and 26, {PAGE}",
            f"  access: {URL}",
            "License: internal. ERB's site reads \"Copyright 2026 All Rights Reserved\" and states no terms of reuse; session 2425's verdict: needs written permission. Cite: Energy Regulation Board, Statistical Bulletin 2025.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Regulation Board, Zambia (ERB)",
                                    report="Statistical Bulletin 2025, tables 12 to 19 and 26 (generation by station, consumption by sector, trade, installed capacity)",
                                    report_url=PAGE, document_list=URL, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; consumption years not taken: {sorted(drop)}")
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
