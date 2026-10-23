#!/usr/bin/env python3
"""EPA's Inventory of U.S. Greenhouse Gas Emissions and Sinks (the 1990 to 2022 Inventory, published April 2024): the
nation's emissions by economic sector and source, the electric power industry's by gas and fuel, and each sector's by
gas with the electricity it uses distributed to it, a year from 1990 (session 2136, chain 090: the national total the
facility reports sit inside).

Energy Research Warehouse (ERW) connector. One series table from three tables of the Inventory's Chapter 2 (Trends),
which EPA publishes as CSV files in one zip:

    https://www.epa.gov/system/files/other-files/2024-04/trends-in-greenhouse-gas-emissions-and-removals.zip
        Table 2-10  emissions allocated to economic sectors (direct), each sector's sources under it
        Table 2-11  electric power-related emissions by gas, each gas's fuels or sources under it
        Table 2-12  emissions by economic sector and gas with electricity-related emissions distributed

    epa_ghg_inventory_annual   entity epa_ghgi:<sector> (us for the national totals); variable <table's basis>:<line>
                               (direct, power or distributed, then the slug of the line, see below); unit tCO2e (Decision
                               61; the Inventory's MMT CO2 Eq. times 1,000,000); ts_utc the year's 1 January; freq P1Y; geo
                               US; x_table the Inventory's table; x_sector, x_group and x_line the lines as published (the
                               footnote letter after a word dropped, the stray character before one dropped)

    Table 2-10: a sector's own line is direct:total, each source under it direct:<source>; the national lines
                (Total Gross Emissions, the LULUCF Sector Net Total, Net Emissions) go to epa_ghgi:us.
    Table 2-11: epa_ghgi:electric_power_industry; a gas's line is power:<gas>, each line under it power:<gas>:<source>,
                the table's Total power:total.
    Table 2-12: a sector's line is distributed:total; its Direct Emissions and Electricity-Related lines
                distributed:direct and distributed:electricity_related, each gas under them distributed:<basis>:<gas>.
                Its national lines and U.S. Territories repeat Table 2-10's and are checked against them, not written.

A value EPA prints as + ("does not exceed 0.05 MMT CO2 Eq.") is not written and is counted in the header. A table whose
years are not 1990 onward in order, a line under no sector, a line given twice, a value not a number, or a repeated line
that differs from Table 2-10's stops the run. Nothing is filled. The 1990 to 2023 Inventory was published only as a
draft for comment (January 2025, its page says); this table holds the last final one.

    python warehouse/connectors/epa_ghg_inventory.py [--offline] [--out-dir DIR]

Ceiling: one request, saved in warehouse/raw/epa_ghg_inventory/ and reused offline. www.epa.gov's robots file disallows
site administration paths only. License: public (EPA's verdict, read 55).
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "epa_ghg_inventory"
SOURCE = "epa:ghg_inventory_1990_2022"
URL = "https://www.epa.gov/system/files/other-files/2024-04/trends-in-greenhouse-gas-emissions-and-removals.zip"
PAGE = "https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks-1990-2022"
TABLE = "epa_ghg_inventory_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_table", "x_sector", "x_group", "x_line"]
SECTORS = ["Transportation", "Electric Power Industry", "Industry", "Agriculture", "Commercial", "Residential", "U.S. Territories"]
NATIONAL = ["Total Gross Emissions (Sources)", "LULUCF Sector Net Total", "Net Emissions (Sources and Sinks)"]
GASES_211 = ["CO2", "CH4", "N2O", "SF6", "CF4"]
BASES_212 = {"Direct Emissions": "direct", "Electricity-Related": "electricity_related"}
FOOTNOTE = re.compile(r"(Combustion|Total|HFCs|Percent)[abc]$")


def clean(label):
    return FOOTNOTE.sub(r"\1", label.replace(chr(0xFFFD), "").strip())


def slug(label):
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def read_table(z, name):
    """A Chapter 2 table as its year columns and its lines (label, the values by year), the notes under it dropped."""
    rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig", errors="replace"))))
    years = rows[1][1:]
    n = 0
    while n < len(years) and re.fullmatch(r"\d{4}", years[n].strip()):
        n += 1
    years = [int(y) for y in years[:n]]
    if not years or years[0] != 1990 or years != list(range(1990, 1990 + n)):
        raise RuntimeError(f"{name}: the years are not 1990 onward in order: {rows[1][:6]}")
    lines = []
    for r in rows[2:]:
        if not r or not r[0].strip():
            continue
        cells = [c.strip() for c in r[1:n + 1]]
        if not any(cells):  # a note under the table
            continue
        lines.append((clean(r[0]), cells))
    return years, lines


def values(name, label, years, cells, plus):
    out = []
    for y, c in zip(years, cells):
        if c == "+":
            plus[0] += 1
            continue
        try:
            v = float(c.replace(",", ""))
        except ValueError:
            raise RuntimeError(f"{name}: {label} {y}: a value not a number: {c!r}")
        out.append((y, round(v * 1_000_000)))
    return out


def same(a, b):
    """Two lines' values alike as numbers (EPA prints 1965.0 in one table and 1965 in another)."""
    num = lambda c: None if c in ("", "+") else round(float(c.replace(",", "")), 1)  # noqa: E731
    return len(a) == len(b) and all(num(x) == num(y) for x, y in zip(a, b))


def parse(content, base):
    z = zipfile.ZipFile(io.BytesIO(content))
    rows, plus = [], [0]

    def add(table, entity, variable, sector, group, line, years, cells):
        for y, v in values(table, line, years, cells, plus):
            rows.append(dict(entity=f"epa_ghgi:{entity}", variable=variable, ts_utc=f"{y}-01-01T00:00:00Z", value=v, unit="tCO2e", freq="P1Y",
                             geo="US", market="", node="", **base, x_table=table, x_sector=sector, x_group=group, x_line=line))

    # Table 2-10
    years, lines = read_table(z, "Table 2-10.csv")
    sector, seen210 = None, {}
    for label, cells in lines:
        if label in SECTORS:
            sector = label
            add("2-10", slug(label), "direct:total", label, "", label, years, cells)
            seen210[label] = cells
        elif label in NATIONAL:
            sector = None
            add("2-10", "us", slug(label), "", "", label, years, cells)
            seen210[label] = cells
        elif sector is None:
            raise RuntimeError(f"Table 2-10: a line under no sector: {label!r}")
        else:
            add("2-10", slug(sector), f"direct:{slug(label)}", sector, "", label, years, cells)
    if set(seen210) != set(SECTORS + NATIONAL):
        raise RuntimeError(f"Table 2-10: sectors missing: {sorted(set(SECTORS + NATIONAL) - set(seen210))}")

    # Table 2-11
    years, lines = read_table(z, "Table 2-11.csv")
    gas = None
    for label, cells in lines:
        if label in GASES_211:
            gas = label
            add("2-11", "electric_power_industry", f"power:{slug(label)}", "Electric Power Industry", label, label, years, cells)
        elif label == "Total":
            if not same(cells, seen210["Electric Power Industry"]):
                raise RuntimeError("Table 2-11's Total differs from Table 2-10's Electric Power Industry")
            add("2-11", "electric_power_industry", "power:total", "Electric Power Industry", "", label, years, cells)
        elif gas is None:
            raise RuntimeError(f"Table 2-11: a line under no gas: {label!r}")
        else:
            add("2-11", "electric_power_industry", f"power:{slug(gas)}:{slug(label)}", "Electric Power Industry", gas, label, years, cells)

    # Table 2-12
    years, lines = read_table(z, "Table 2-12.csv")
    sector = basis = None
    for label, cells in lines:
        if label in NATIONAL or label == "U.S. Territories":
            if not same(cells, seen210[label]):
                raise RuntimeError(f"Table 2-12's {label} differs from Table 2-10's")
            sector = basis = None
        elif label in SECTORS:
            sector, basis = label, None
            add("2-12", slug(label), "distributed:total", label, "", label, years, cells)
        elif label in BASES_212 and sector:
            basis = BASES_212[label]
            add("2-12", slug(sector), f"distributed:{basis}", sector, label, label, years, cells)
        elif sector is None or basis is None:
            raise RuntimeError(f"Table 2-12: a line under no sector and basis: {label!r}")
        else:
            add("2-12", slug(sector), f"distributed:{basis}:{slug(label)}", sector, {v: k for k, v in BASES_212.items()}[basis], label, years, cells)
    if not rows:
        raise RuntimeError("no line in the tables")
    return pd.DataFrame(rows), plus[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPA's Inventory of U.S. Greenhouse Gas Emissions and Sinks, 1990 to 2022")
    ap.add_argument("--offline", action="store_true", help="the saved zip only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("www.epa.gov"):
        print(f"{TABLE}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        s, plus = parse(content, base)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            d = s[s.duplicated(["entity", "variable", "ts_utc"], keep=False)]
            raise RuntimeError(f"a line given twice: {d[['entity', 'variable']].drop_duplicates().head(3).values.tolist()}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        gross = s[(s.entity == "epa_ghgi:us") & (s.variable == "total_gross_emissions_sources")].set_index("ts_utc").value
        power = s[(s.entity == "epa_ghgi:electric_power_industry") & (s.variable == "power:co2")].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): EPA, Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022 (April 2024), Chapter 2 Tables 2-10, "
            "2-11 and 2-12: emissions by economic sector and source, the electric power industry's by gas and fuel, each sector's by gas with "
            "electricity distributed (session 2136)",
            "Shape: series (docs/datastandard.md v0). entity epa_ghgi:<sector> or epa_ghgi:us; variable direct:<line> (Table 2-10), power:<gas>[:<line>] "
            "(Table 2-11), distributed:<basis>[:<gas>] (Table 2-12); unit tCO2e (the Inventory's MMT CO2 Eq. times 1,000,000, weighted by the "
            "Inventory's own global warming potentials, which its tables do not name); ts_utc 1 January of the year; freq P1Y; geo US; x_table, x_sector, x_group, x_line as published.",
            f"{len(s)} rows, {s.entity.nunique()} entities, {s.variable.nunique()} variables, {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}; gross "
            f"emissions {gross.iloc[0] / 1e6:,.1f} MMT in {gross.index[0][:4]} and {gross.iloc[-1] / 1e6:,.1f} in {gross.index[-1][:4]}; the electric "
            f"power industry's CO2 {power.iloc[-1] / 1e6:,.1f} MMT in {power.index[-1][:4]}. {plus} values EPA prints as + (under 0.05 MMT) are "
            "not written. Table 2-12's Residential line under Direct Emissions labelled SF6 is kept as EPA labels it. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/epa_ghg_inventory.py; the zip retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} EPA, Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022, {PAGE}",
            f"  access: {URL} (2024 Trends in Greenhouse Gas Emissions Tables)",
            "License: public (a work of the U.S. Environmental Protection Agency; EPA's verdict).",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {plus} values printed as +")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Environmental Protection Agency (EPA)",
                                    report="Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022", report_url=PAGE,
                                    document_list=URL, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
