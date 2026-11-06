#!/usr/bin/env python3
"""The Czech Statistical Office's (CZSO's) regional energy tables, from "Comparison of Regions in the Czech Republic": each
Czech region's installed capacity and gross electricity production by type of plant, and its net electricity consumption by
economic activity, a year (the 2025 edition, 2024's figures; session 2809, chain 143). The figures are the Energy Regulatory
Office's (ERU), as the CZSO publishes them.

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/czso_cz_regional_electricity_annual.csv, from the
edition's tables in one zip (one request), tables 14.101 and 14.103 of its chapter 14 (Energy):

    https://csu.gov.cz/docs/107508/4491dd21-67d2-55cf-a3e6-926ec9c4b345/33020525.zip?version=1.1
    (14_energetika/2514101.xlsx and 14_energetika/2514103.xlsx; the edition's page:
     https://csu.gov.cz/produkty/comparison-of-regions-in-the-czech-republic-2025)

    entity      czso_regions:<the region's ISO 3166-2 code, CZ-10 to CZ-80, or CZ for Czechia>:<the item's slug>
    variable    installed_capacity (MW, at 31 December), gross_production (MWh, the table's GWh times 1,000) or
                net_consumption (MWh)
    item        for capacity and production: total, steam, combined_cycle, hydro (pumped storage included), gas_combustion,
                nuclear, wind, solar; for consumption: total, industry, energy, transport, construction, agriculture_forestry,
                households, trade_services (trade, services, education and health care)
    unit        MW or MWh; ts_utc the year's 1 January at 00:00:00Z; freq P1Y; geo CZ
    node        "CZSO <ISO code>, <the table's English label>" (ASCII; the Czech name is in x_region)
    x_*         the region's Czech name, the table's number and the row's Czech label

Each table's shares (per cent) and households' consumption per inhabitant (kWh) are not written: they are computed from the
rows written. "- " (nothing) is zero; a blank has no row; nothing is filled. Compared, within 0.5 MW or 0.5 GWh: the regions
against Czechia in every row, and the types (or activities) against each region's total; a case that does not hold is counted
in the header and listed in the run log, kept as published. Checks that stop the run: a member not in the zip, a title without
its year, a header without the fourteen regions and Czechia, a row not in the expected structure, a value not a number.

    python warehouse/connectors/czso_regional_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/czso_regions/ with --offline. csu.gov.cz's robots file (read 1613; www.czso.cz
redirects to it, read 1614) disallows three paths to every reader, none of these, and names no Claude agent. License: the
CZSO's conditions (read 1617): "Statistical information released by the Czech Statistical Office through the website
https://csu.gov.cz is licensed under CC BY 4.0", the terms to be mentioned and adjusted or derived data labelled so; source:
Czech Statistical Office (CZSO), from the Energy Regulatory Office's data.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "czso_cz_regional_electricity_annual"
CONNECTOR = "czso_regions"
SOURCE = "czso:comparison_of_regions_14_energy"
URL = "https://csu.gov.cz/docs/107508/4491dd21-67d2-55cf-a3e6-926ec9c4b345/33020525.zip?version=1.1"
PAGE = "https://csu.gov.cz/produkty/comparison-of-regions-in-the-czech-republic-2025"
TERMS = "https://csu.gov.cz/conditions_for_use_and_further_dissemination"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MEMBERS = {"14101": "14_energetika/2514101.xlsx", "14103": "14_energetika/2514103.xlsx"}
REGIONS = {"Česko Czechia": "CZ", "Hl. m. Praha": "CZ-10", "Středočeský": "CZ-20", "Jihočeský": "CZ-31", "Plzeňský": "CZ-32",
           "Karlovarský": "CZ-41", "Ústecký": "CZ-42", "Liberecký": "CZ-51", "Královéhradecký": "CZ-52", "Pardubický": "CZ-53",
           "Vysočina": "CZ-63", "Jihomoravský": "CZ-64", "Olomoucký": "CZ-71", "Zlínský": "CZ-72", "Moravskoslezský": "CZ-80"}
TYPES = {"parní elektrárny": "steam", "paroplynové elektrárny": "combined_cycle",
         "vodní elektrárny včetně přečerpávacích": "hydro", "plynové a spalovací elektrárny": "gas_combustion",
         "jaderné elektrárny": "nuclear", "větrné elektrárny": "wind", "fotovoltaické elektrárny": "solar"}
SECTORS = {"průmysl": "industry", "energetika": "energy", "doprava": "transport", "stavebnictví": "construction",
           "zemědělství a lesnictví": "agriculture_forestry", "domácnosti": "households",
           "obchod, služby, školství a zdravotnictví": "trade_services"}
BLOCKS = {"14101": [("Instalovaný výkon", "installed_capacity", "MW", 1.0, TYPES),
                    ("Výroba elektřiny brutto", "gross_production", "MWh", 1000.0, TYPES)],
          "14103": [("Spotřeba elektřiny netto (GWh)", "net_consumption", "MWh", 1000.0, SECTORS)]}
TOL = 0.5
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_region", "x_table", "x_label"]


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", str(s))).strip() if s is not None else ""


def slug_ascii(s):
    """A label in ASCII for the node (the console of a Windows run cannot print every Czech letter)."""
    import unicodedata
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def number(c, where):
    if c is None or (isinstance(c, str) and c.strip() == ""):
        return None
    if isinstance(c, str) and c.strip() == "-":
        return 0.0
    if isinstance(c, (int, float)):
        return float(c)
    raise RuntimeError(f"{where}: not a number: {c!r}")


def read_table(content, code):
    rows = [r for r in openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True)]
    title = next((clean(r[0]) for r in rows if r and clean(r[0]).startswith(code[:2] + "." + code[2:])), "")
    m = re.search(r"v roce (\d{4})", title)
    if not title.startswith(code[:2] + "." + code[2:]) or not m:
        raise RuntimeError(f"table {code}: a title without its number or year: {title!r}")
    year = int(m.group(1))
    hdr = next((i for i, r in enumerate(rows) if r and clean(r[2]) == "Hl. m. Praha"), None)
    if hdr is None:
        raise RuntimeError(f"table {code}: no header row with the regions")
    names = ["Česko Czechia"] + [clean(c) for c in rows[hdr][2:16]]
    if names != list(REGIONS):
        raise RuntimeError(f"table {code}: the regions are not the fourteen and Czechia: {names}")
    out = []
    block = None
    for r in rows[hdr + 1:]:
        label = clean(r[0])
        if not label:
            continue
        starts = [b for b in BLOCKS[code] if label.startswith(b[0])]
        if starts:
            block = starts[0]
            item, lab = "total", label
        elif label.startswith("podíl"):                 # the total's share of Czechia's, one row: the block goes on
            continue
        elif label.startswith(("Podíl", "Spotřeba elektřiny netto v domác")):   # the shares' block, or a head's use
            block = None
            continue
        elif block is not None:
            if label not in block[4]:
                raise RuntimeError(f"table {code}: a row not in the structure under {block[0]!r}: {label!r}")
            item, lab = block[4][label], label
        else:
            continue
        english = clean(r[16]) if len(r) > 16 else ""
        for name, c in zip(REGIONS, r[1:16]):
            v = number(c, f"table {code} {label} {name}")
            out.append((block[1], block[2], block[3], REGIONS[name], name, item, lab, english, v))
    return year, out


def build(zcontent, retrieved, vintage):
    z = zipfile.ZipFile(io.BytesIO(zcontent))
    missing = [m for m in MEMBERS.values() if m not in z.namelist()]
    if missing:
        raise RuntimeError(f"a member not in the zip: {missing}")
    rows, years = [], set()
    for code, member in MEMBERS.items():
        year, out = read_table(z.read(member), code)
        years.add(year)
        for var, unit, k, iso, name, item, lab, english, v in out:
            if v is None:
                continue
            rows.append({"entity": f"czso_regions:{iso}:{item}", "variable": var, "ts_utc": f"{year}-01-01T00:00:00Z",
                         "value": round(v * k, 3), "unit": unit, "freq": "P1Y", "geo": "CZ", "market": "",
                         "node": f"CZSO {iso}, {english or slug_ascii(lab)}", "source": SOURCE, "source_url": URL,
                         "retrieved_at": retrieved, "vintage": vintage, "x_region": name, "x_table": code[:2] + "." + code[2:],
                         "x_label": lab})
    if len(years) != 1:
        raise RuntimeError(f"the tables are of different years: {sorted(years)}")
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]}")
    return t.sort_values(["variable", "entity"]).reset_index(drop=True)


def checks(t):
    x = t.assign(region=t.entity.str.split(":").str[1], item=t.entity.str.split(":").str[2])
    x["v"] = x.value / x.unit.map({"MW": 1.0, "MWh": 1000.0})
    off, n = [], 0
    for (var, item), g in x.groupby(["variable", "item"]):
        reg = g[g.region != "CZ"].v.sum()
        cz = g[g.region == "CZ"].v
        if len(cz):
            n += 1
            if abs(reg - cz.iloc[0]) > TOL:
                off.append((var, item, "regions against Czechia", round(reg - cz.iloc[0], 3)))
    for (var, region), g in x.groupby(["variable", "region"]):
        tot = g[g.item == "total"].v
        if len(tot):
            n += 1
            d = g[g.item != "total"].v.sum() - tot.iloc[0]
            if abs(d) > TOL:
                off.append((var, region, "parts against the total", round(d, 3)))
    return n, off


def main(argv=None):
    ap = argparse.ArgumentParser(description="CZSO: Czech regions' electricity capacity, production and consumption, a year")
    ap.add_argument("--offline", action="store_true", help="the saved zip only, no request")
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
        if not args.offline and (ip.paused("czso") or ip.paused_host("csu.gov.cz")):
            raise RuntimeError("the CZSO is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180)
        t = build(content, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        n, off = checks(t)
        for x in off:
            log(f"  not as expected, kept as published: {x}")
        year = t.ts_utc.iloc[0][:4]
        tot = {v: t[(t.entity == "czso_regions:CZ:total") & (t.variable == v)].value.iloc[0] for v in t.variable.unique()}
        header = [
            f"Energy Research Warehouse (ERW): Czech Statistical Office (CZSO), Comparison of Regions in the Czech Republic 2025, tables 14.101 and 14.103: each region's installed capacity and gross electricity production by type of plant, and its net consumption by activity, {year} (the Energy Regulatory Office's data) (session 2809)",
            "Shape: series (docs/datastandard.md v0). entity czso_regions:<ISO 3166-2 region, or CZ>:<item>; variable installed_capacity (MW, at 31 December), gross_production or net_consumption (MWh, the tables' GWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo CZ; x_region, x_table and x_label the tables' own.",
            f"{len(t)} rows, {t.entity.str.split(':').str[1].nunique()} areas. Czechia {year}: capacity {tot.get('installed_capacity', 0):,.1f} MW, gross production {tot.get('gross_production', 0):,.0f} MWh, net consumption {tot.get('net_consumption', 0):,.0f} MWh. "
            f"The regions against Czechia and the types or activities against each total, within {TOL:g} MW or GWh: {n - len(off)} of {n} comparisons hold; {len(off)} kept as published and listed in the run log. The tables' shares and the households' consumption a head are not written. '- ' is zero; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/czso_regional_electricity.py; the zip retrieved {rec.get('retrieved_at') or ''} (last modified {rec.get('last_modified') or 'not given'})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Czech Statistical Office (CZSO), Comparison of Regions in the Czech Republic 2025, 14. Energy (source: Energy Regulatory Office), {PAGE}",
            f"  access: {URL} (members {', '.join(MEMBERS.values())})",
            f"License: CC BY 4.0, the CZSO's conditions for use ({TERMS}). Reshaped by the ERW (GWh written as MWh); not unaltered official statistics of the CZSO.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Czech Statistical Office (CZSO)",
                                    report="Comparison of Regions in the Czech Republic 2025, 14. Energy (tables 14.101 and 14.103)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows for {year}; {n - len(off)} of {n} comparisons hold; {tot}")
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
