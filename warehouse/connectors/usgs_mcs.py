#!/usr/bin/env python3
"""The U.S. Geological Survey's Mineral Commodity Summaries for the minerals of batteries and grids: lithium, cobalt,
nickel, natural graphite, copper and the rare earths (session 954), and since session 981 aluminum, gallium, germanium,
indium, manganese, the platinum-group metals, the heavy rare earths, silicon, tellurium and vanadium, each chapter's U.S. salient statistics (production, imports,
exports, apparent consumption, prices, stocks, employment, net import reliance), its import sources and its world mine
production and reserves by country (session 954, chain 054).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/usgs_mcs_critical_minerals.csv, from the
Mineral Commodity Summaries 2026 Data Release, "Commodity Salient U.S. and World Statistics" (ScienceBase item
69837e43b66b01367d7ec7c7), its one CSV, MCS2026_Commodities_Data.csv:

    https://www.sciencebase.gov/catalog/item/69837e43b66b01367d7ec7c7

    entity     usgs_mcs:<chapter>:<country>:<the statistic's detail>, each a slug of USGS's words
    variable   production, import, export, consumption, price, stock, employment, net_import_reliance, reserves,
               capacity, shipment, supply, or import_share (the import sources, a share of 2021 to 2024: ts_utc 2021-01-01, freq P4Y)
    unit       t (metric tons; thousand metric tons times 1,000, kilograms over 1,000), USD/t, USD/kg (dollars per troy
               ounce times 32.1507466), USD/lb (cents per pound over 100),
               pct, count; ts_utc the year's 1 January; freq P1Y; geo US for the United States, empty elsewhere
    x_*        the chapter, section, commodity, country, statistic and its detail, USGS's unit, its notes, and whether
               the commodity is on the 2025 critical minerals list

USGS's marks have no row: W (withheld to avoid disclosing company data), NA, E (net exporter), a dash (zero, as USGS
prints it), s (less than half a unit, or included in the world total) and a bound such as ">50" are counted in the
header, not written as numbers. The file is in Windows-1252;
its em dash in the section names is written as a colon. A heading or unit not as read, or a key given twice, stops the
run; nothing is filled.

    python warehouse/connectors/usgs_mcs.py [--offline]

Ceiling: one request (the CSV, saved in warehouse/raw/usgs_mcs/ and reused offline). ScienceBase's robots file allows
every path to every reader; its content signals reserve AI training, which the ERW does not do. License: USGS's data are
in the U.S. public domain (license_verdicts.csv, session 496); cite the data release.
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

NAME = "usgs_mcs_critical_minerals"
CONNECTOR = "usgs_mcs"
SOURCE = "usgs:mcs_2026_data"
PAGE = "https://www.sciencebase.gov/catalog/item/69837e43b66b01367d7ec7c7"
URL = ("https://www.sciencebase.gov/catalog/file/get/69837e43b66b01367d7ec7c7"
       "?f=__disk__d3%2Fac%2F84%2Fd3ac8466552946c5e8caa2c2c6338d9e1aff655d")
CITATION = ("U.S. Geological Survey, 2026, Mineral Commodity Summaries 2026 Data Release, "
            "Commodity Salient U.S. and World Statistics; Mineral commodity summaries 2026, https://doi.org/10.3133/mcs2026")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
# session 981: the other chapters of the energy transition, beside session 954's six
CHAPTERS = ["COBALT", "COPPER", "GRAPHITE (NATURAL)", "LITHIUM", "NICKEL", "RARE EARTHS",
            "ALUMINUM", "GALLIUM", "GERMANIUM", "INDIUM", "MANGANESE", "PLATINUM-GROUP METALS", "RARE EARTHS (Heavy)", "SILICON",
            "TELLURIUM", "VANADIUM"]
HEAD = ["MCS chapter", "Section", "Commodity", "Country", "Statistics", "Statistics_detail", "Unit", "Year", "Value", "Notes",
        "Is critical mineral 2025", "Other notes"]
UNITS = {"metric tons": ("t", 1.0), "thousand metric tons": ("t", 1000.0), "dollars per metric ton": ("USD/t", 1.0),
         "dollars per kilogram": ("USD/kg", 1.0), "dollars per pound": ("USD/lb", 1.0), "cents per pound": ("USD/lb", 0.01),
         "percent": ("pct", 1.0), "number": ("count", 1.0),
         # session 981: kilograms as metric tons over 1,000; a troy ounce is 31.1034768 g exactly
         "kilograms": ("t", 0.001), "dollars per troy ounce": ("USD/kg", 1000 / 31.1034768)}
VARIABLES = {"Production": "production", "Import": "import", "Export": "export", "Consumption": "consumption", "Price": "price",
             "Stock": "stock", "Employment": "employment", "Net import reliance": "net_import_reliance", "Reserves": "reserves",
             "Import sources 2021-2024": "import_share", "Capacity": "capacity", "Shipment": "shipment", "Supply": "supply"}
# USGS's punctuation, by code point (no such character is written into this file)
EM, EN, RSQ, LSQ, LDQ, RDQ = (chr(c) for c in (0x2014, 0x2013, 0x2019, 0x2018, 0x201C, 0x201D))
X_COLS = ["x_chapter", "x_section", "x_commodity", "x_country", "x_statistic", "x_detail", "x_usgs_unit", "x_notes", "x_critical_2025"]


def clean(s):
    """USGS's Windows-1252 punctuation in plain characters: the em dash as a colon, the en dash as a hyphen."""
    s = str(s).replace(EM, ": ").replace(EN, "-").replace(RSQ, "'").replace(LSQ, "'")
    s = s.replace(LDQ, '"').replace(RDQ, '"')
    return re.sub(r"\s+", " ", s).replace(" : ", ": ").strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", clean(s).lower()).strip("_")


def build(frame, base):
    if list(frame.columns) != HEAD:
        raise RuntimeError(f"headings not as read: {list(frame.columns)}")
    f = frame[frame["MCS chapter"].isin(CHAPTERS)]
    missing = sorted(set(CHAPTERS) - set(f["MCS chapter"]))
    if missing:
        raise RuntimeError(f"chapters not in the file: {missing}")
    rows, marks = [], {}
    for _, r in f.iterrows():
        if r["Unit"] not in UNITS:
            raise RuntimeError(f"a unit not in the map: {r['Unit']!r}")
        if r["Statistics"] not in VARIABLES:
            raise RuntimeError(f"a statistic not in the map: {r['Statistics']!r}")
        raw = clean(r["Value"])
        v = pd.to_numeric(raw.replace(",", ""), errors="coerce")
        if pd.isna(v):
            m = "dash" if str(r["Value"]).strip() == EM else (raw or "blank")
            marks[m] = marks.get(m, 0) + 1
            continue
        unit, scale = UNITS[r["Unit"]]
        if clean(r["Statistics_detail"]).endswith("dollars per metric ton unit"):
            # session 981: manganese's price is per metric ton unit (10 kg of content) by its detail, though the unit
            # column says per metric ton: written per metric ton of content, times 100
            if r["Unit"] != "dollars per metric ton":
                raise RuntimeError(f"a metric ton unit price with the unit {r['Unit']!r}")
            unit, scale = "USD/t", 100.0
        year = clean(r["Year"])
        if re.fullmatch(r"\d{4}", year):
            ts, freq = f"{year}-01-01T00:00:00Z", "P1Y"
        elif year == "2021-24" and r["Statistics"] == "Import sources 2021-2024":
            ts, freq = "2021-01-01T00:00:00Z", "P4Y"
        else:
            raise RuntimeError(f"a year not as read: {year!r}")
        country = clean(r["Country"])
        detail = clean(r["Statistics_detail"])
        rows.append(dict(base, entity=f"usgs_mcs:{slug(r['MCS chapter'])}:{slug(country)}:{slug(detail)}", variable=VARIABLES[r["Statistics"]],
                         ts_utc=ts, value=float(v) * scale, unit=unit, freq=freq, geo="US" if country == "United States" else "", market="",
                         node=f"{clean(r['Commodity'])}, {country}: {detail}", x_chapter=clean(r["MCS chapter"]), x_section=clean(r["Section"]),
                         x_commodity=clean(r["Commodity"]), x_country=country, x_statistic=clean(r["Statistics"]), x_detail=detail,
                         x_usgs_unit=r["Unit"], x_notes=clean(r["Notes"]), x_critical_2025=clean(r["Is critical mineral 2025"])))
    t = pd.DataFrame(rows)
    # session 981: USGS prints some U.S. figures in two sections (the salient statistics and the world table, the
    # platinum-group metals' mine production): a repeat with the same value is kept once, the first section's
    key = ["entity", "variable", "ts_utc"]
    same = t.duplicated(key + ["value"])
    if same.any():
        marks["repeated in two sections, kept once"] = int(same.sum())
        t = t[~same]
    if t.duplicated(key).any():
        d = t[t.duplicated(key, keep=False)].head(3)
        raise RuntimeError(f"a key given twice with two values: {d[['entity', 'ts_utc', 'value']].values.tolist()}")
    return t, marks


def main(argv=None):
    ap = argparse.ArgumentParser(description="USGS Mineral Commodity Summaries: the minerals of batteries and grids")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=300)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        frame = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False, encoding="cp1252")
        t, marks = build(frame, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        k = t.groupby("variable").size().to_dict()
        twice = marks.pop("repeated in two sections, kept once", 0)
        header = [
            "Energy Research Warehouse (ERW): U.S. Geological Survey, Mineral Commodity Summaries 2026: the minerals of the energy transition (lithium, cobalt, nickel, graphite, copper, the rare earths, aluminum, gallium, germanium, indium, manganese, the platinum-group metals, silicon, tellurium, vanadium), U.S. salient statistics, import sources and world mine production and reserves by country (session 954)",
            "Shape: series (docs/datastandard.md v0). entity usgs_mcs:<chapter>:<country>:<the statistic's detail>; variables production, import, export, "
            "consumption, price, stock, employment, net_import_reliance, reserves, capacity, shipment, supply, import_share (2021 to 2024: ts_utc "
            "2021-01-01, freq P4Y); units t (metric tons: thousand metric tons times 1,000, kilograms over 1,000), USD/t, USD/kg (troy ounces converted at "
            "31.1034768 g), USD/lb (cents per pound over 100), pct, count; what is weighed (a content or a "
            "gross weight) is in the node; ts_utc the year's 1 January; freq P1Y; geo US for the United States, empty elsewhere.",
            f"Rows: {', '.join(f'{v} {n}' for n, v in k.items())}; {t['entity'].nunique()} series, years {t['ts_utc'].min()[:4]} to {t['ts_utc'].max()[:4]}. "
            f"USGS's marks have no row: {', '.join(f'{v} {m}' for m, v in sorted(marks.items(), key=lambda x: -x[1]))} (W withheld, E net exporter, a dash "
            "zero as USGS prints it, s less than half a unit or in the world total, a bound such as >50). "
            f"{twice} figures USGS prints in two sections with the same value are kept once. The section's em dash is written as a colon. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/usgs_mcs.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}, {PAGE}",
            f"  access: {URL}",
            "License: U.S. public domain (USGS-authored data, license_verdicts.csv); cite the data release.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Geological Survey (USGS)",
                                    report="Mineral Commodity Summaries 2026 Data Release, Commodity Salient U.S. and World Statistics",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} rows"))
        print(f"{NAME}: {len(t):,} rows {k}; marks {marks}")
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
