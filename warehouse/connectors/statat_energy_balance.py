#!/usr/bin/env python3
"""Austria's electricity balance each year from 1970 to 2024, as Statistics Austria (Statistik Austria) gives it in its energy
balances, sheet "Electricity" of "Energy balances Austria 1970-2024" (session 2764, chain 140: Austria's national statistics
office, beside E-Control's monthly statistics, held since chain 080).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statat_austria_electricity_annual.csv, from one
file (no key), an OpenDocument spreadsheet of 10 MB whose content.xml (263 MB) is read by streaming, with the standard library
only (no ODS reader is a dependency of the ERW):

    https://www.statistik.at/fileadmin/pages/99/energy_balances_austria_1970-2024_data.ods

The sheet gives the balance three times (in TJ, in MWh, and the conversion factor between them); this table reads its block "in
MWh", its "Final energy use by sectors" block in MWh and its "Energy sector use" block in MWh, so no unit is converted.

    entity      statat_ele:at for a balance item's total; statat_ele:<plant>[:<owner>[:<fuel>[:<sub-fuel>]]] for the
                transformation input and output by plant type (coke_oven, blast_furnace, refinery, charcoal_production,
                power_plants, chp_plants, heating_plants, gas_production), owner (public_plants, autoproducers) and fuel (the row
                as a slug without "from"); statat_ele:sector:<sector> for final energy use by sector; statat_ele:branch:<branch>
                for the energy sector's use by branch
    variable    the balance item: indigenous_primary_production, imports, stock_changes, recycling_prod_trans, exports,
                gross_inland_consumption, transformation_input, transformation_output, energy_sector_use, transport_losses,
                non_energy_use, final_energy_use
    unit        MWh; ts_utc the year's first day; freq P1Y; geo AT; node the sheet's labels, outermost first; the energy sector's branches from 1999, where the sheet begins them

Statistics Austria's "Gross inland consumption" of electricity is its net imports (no electricity is produced as primary
energy in the balance's convention; generation is the transformation output). A row that is 0 in every year is not written
(counted in the header); a zero in a written row stays a zero. A sub-fuel breakdown that is 0 in a year while its fuel is not
(the breakdown begins later, as the hydropower sizes in 2000) is not checked that year and is counted.

Checks that stop the run, within 1 MWh in every year:
    gross inland consumption = primary production + imports + stock changes + recycling - exports;
    final energy use = gross inland consumption - transformation input + transformation output - energy sector use
                       - transport losses - non energy use;
    each parent row = the sum of its direct children (plant types, owners, fuels, sub-fuels) where the children are split;
    final energy use = industry + transport + other sectors, each the sum of its branches;
    the energy sector use by branch sums to its total, which equals the balance's.
A year row not each year from 1970, a label not in the sheet's known structure, a key given twice, or a value not a number
stops the run. Nothing is filled.

    python warehouse/connectors/statat_energy_balance.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/statistik_austria/ and reused unless --fresh; --offline asks nothing.
www.statistik.at's robots file closes only its search pages and names no Claude agent (session 2764, read 1509). License:
Statistics Austria's general terms, section 10 (read 1518): reproduction, distribution and making available, commercial or
not, are permitted with the source "STATISTIK AUSTRIA" cited and edits stated; public.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "statat_austria_electricity_annual"
CONNECTOR = "statistik_austria"
SOURCE = "statat:energy_balances_1970_2024"
HOST = "www.statistik.at"
URL = "https://www.statistik.at/fileadmin/pages/99/energy_balances_austria_1970-2024_data.ods"
PAGE = "https://www.statistik.at/en/statistics/energy-and-environment/energy/energy-balances"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "STATISTIK AUSTRIA, Energy balances Austria 1970-2024, sheet Electricity"
SHEET = "Electricity"
YEARS = list(range(1970, 2025))
TOL = 1.0
TOP = ["Indigenious primary production", "Imports", "Stock changes", "Recycling/Prod. Trans.", "Exports",
       "Gross inland consumption", "Transformation input", "Transformation output", "Energy sector use", "Transport losses",
       "Non energy use", "Final energy use"]
VAR = {"Indigenious primary production": "indigenous_primary_production", "Recycling/Prod. Trans.": "recycling_prod_trans"}
PLANT = ["Coke oven", "Blast furnace", "Refinery", "Charcoal production", "Power plants", "CHP plants", "Heating plants",
         "Gas production"]
OWN = ["Public plants", "Autoproducers"]
FUELS = ["from hard coal", "from lignite", "from oil", "from natural gas", "from coal gas", "from waste", "from renewables",
         "from hydropower", "from wind, pv, geothermal", "from electricity", "from solar, ambient heat, geothermal"]
GROUPS = {"from waste": ["from industrial waste non-renewable", "from municipal waste non-renewable"],
          "from coal gas": ["from coke oven gas", "from blast furnace gas"],
          "from renewables": ["from municipal waste renewable", "from fuelwood", "from wood pellets", "from wood waste",
                              "from black liquor", "from landfill gas", "from sewage sludge gas", "from other wind",
                              "from liquid biofuels", "from other solid biofuels"],
          "from hydropower": ["from hydropower <=1MW", "from hydropower 1 - 10 MW", "from hydropower >10MW"],
          "from wind, pv, geothermal": ["from wind", "from PV", "from geothermal", "from process heat"]}
INDUSTRY = ["Iron and Steel", "Chemical and Petrochemical", "Non Ferrous Metals", "Non Metalic Minerals", "Transport Equipment",
            "Machinery", "Mining and Quarrying", "Food Tobacco and Beverages", "Pulp Paper and Print", "Wood and Wood Products",
            "Construction", "Textiles and Leather", "Non Specified Industry"]
TRANSPORT = ["Railways", "Other Transport", "Pipeline Transport", "Internal Navigation", "Air Transport"]
OTHER = ["Commercial and Public Services", "Residential", "Agriculture"]
SECTORS = INDUSTRY + TRANSPORT + OTHER + ["Industry", "Transport", "Other Sectors"]
BRANCHES = ["Oil and gas extraction", "Coal mines", "Oil refineries", "Coke ovens", "Blast furnaces",
            "Electricity, CHP and heat plants", "Total"]
X_COLS = []
_T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
_O = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
_X = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"


def sheet_rows(content, name, max_cols=80):
    """The rows of one sheet of an .ods file, read by streaming its content.xml: each a list of floats (office:value) or
    strings (the cell's text), trailing blanks dropped, a repeated empty row kept once."""
    rows, inside, found = [], False, False
    with zipfile.ZipFile(io.BytesIO(content)).open("content.xml") as f:
        for ev, el in ET.iterparse(f, events=("start", "end")):
            if ev == "start" and el.tag == _T + "table":
                inside = el.get(_T + "name") == name
                found = found or inside
            elif ev == "end" and el.tag == _T + "table":
                if inside:
                    return rows
                el.clear()
            elif ev == "end" and el.tag == _T + "table-row":
                if inside:
                    row = []
                    for c in el:
                        if c.tag not in (_T + "table-cell", _T + "covered-table-cell"):
                            continue
                        n = int(c.get(_T + "number-columns-repeated", "1"))
                        v = c.get(_O + "value")
                        if v is None:
                            v = " ".join("".join(p.itertext()) for p in c.findall(_X + "p")) or None
                        else:
                            v = float(v)
                        row += [v] * min(n, max_cols - len(row))
                        if len(row) >= max_cols:
                            break
                    while row and row[-1] is None:
                        row.pop()
                    rr = int(el.get(_T + "number-rows-repeated", "1"))
                    rows += [row] * (rr if row else 1)
                el.clear()
    raise RuntimeError(f"no sheet named {name!r}" if not found else f"the sheet {name!r} did not end")


def slug(s):
    s = re.sub(r"^from ", "", s)
    s = s.replace("<=", "le").replace(">", "gt").replace("&", "and")
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", s.lower())).strip("_")


def block_start(rows, label, after=0):
    """The index of the year row of the block titled `label` (the title, then a row whose first cell is blank or a unit)."""
    for i in range(after, len(rows) - 1):
        r = rows[i]
        if r and r[0] == label:
            for k in range(i + 1, min(i + 3, len(rows))):
                if len(rows[k]) > 1 and rows[k][1] == float(YEARS[0]):
                    return k
    raise RuntimeError(f"no block {label!r} with a year row")


def numbers(r, where, years=None):
    """The row's value in each year; where `years` (the block's year row) is blank, the cell must be blank and is None."""
    vals = list(r[1:1 + len(YEARS)]) + [None] * (len(YEARS) - len(r[1:1 + len(YEARS)]))
    for j, v in enumerate(vals):
        if years is not None and years[j] is None:
            if v is not None:
                raise RuntimeError(f"{where}: a value in a year the block does not cover: {YEARS[j]}")
        elif not isinstance(v, float):
            raise RuntimeError(f"{where}: not a number in {YEARS[j]}: {v!r}")
    return vals


def parse_sheet(rows):
    y = block_start(rows, "in MWh")
    if rows[y][1:1 + len(YEARS)] != [float(v) for v in YEARS]:
        raise RuntimeError("the MWh block's years are not each year from 1970 to 2024")
    vals, nodes = {}, {}
    top = plant = own = grp = None
    for r in rows[y + 1:]:
        if not r or r[0] is None:
            if top == "Final energy use":
                break
            continue
        lab = r[0]
        if lab in TOP:
            top, plant, own, grp = lab, None, None, None
            key = (lab,)
        elif top in ("Transformation input", "Transformation output") and lab in PLANT:
            plant, own, grp = lab, None, None
            key = (top, lab)
        elif plant and lab in OWN:
            own, grp = lab, None
            key = (top, plant, lab)
        elif own and lab in FUELS:
            grp = lab if lab in GROUPS else None
            key = (top, plant, own, lab)
        elif own and grp and lab in GROUPS[grp]:
            key = (top, plant, own, grp, lab)
        else:
            raise RuntimeError(f"a label not in the known structure: {lab!r} (under {top}, {plant}, {own}, {grp})")
        if key in vals:
            raise RuntimeError(f"{key} given twice")
        vals[key] = numbers(r, " / ".join(key))
        if lab == "Final energy use":
            break
    if [k[0] for k in vals if len(k) == 1] != TOP:
        raise RuntimeError("the balance items are not the twelve expected, in order")
    sec_at = block_start(rows, "in MWh", after=block_start(rows, "Final energy use by sectors") - 2)
    sec = {}
    for r in rows[sec_at + 1:sec_at + 1 + len(SECTORS)]:
        if not r or r[0] not in SECTORS or r[0] in sec:
            raise RuntimeError(f"the sectors' MWh block: an unexpected row {r[:2]}")
        sec[r[0]] = numbers(r, r[0])
    br_title = [i for i, r in enumerate(rows) if r and r[0] == "Energy sector use" and i > sec_at]
    br_year = [i for i in br_title if len(rows[i + 1]) > 1 and rows[i + 1][0] == "in MWh"]
    if len(br_year) != 1:
        raise RuntimeError("no single energy sector use block in MWh")
    yr = list(rows[br_year[0] + 1][1:1 + len(YEARS)]) + [None] * len(YEARS)
    yr = yr[:len(YEARS)]
    if [int(v) for v in yr if v is not None] != [YEARS[j] for j, v in enumerate(yr) if v is not None] or yr[-1] is None:
        raise RuntimeError("the energy sector's MWh block: its years are not in their columns")
    br = {}
    for r in rows[br_year[0] + 2:br_year[0] + 2 + len(BRANCHES)]:
        if not r or r[0] not in BRANCHES or r[0] in br:
            raise RuntimeError(f"the energy sector's MWh block: an unexpected row {r[:2]}")
        br[r[0]] = numbers(r, r[0], yr)
    return vals, sec, br


def check(vals, sec, br):
    """The identities, within TOL MWh in every year; returns the count of (parent, year) pairs whose children are not split."""
    unsplit = 0
    g = lambda k, j: vals[(k,)][j]
    for j, yr in enumerate(YEARS):
        gic = g(TOP[0], j) + g("Imports", j) + g("Stock changes", j) + g("Recycling/Prod. Trans.", j) - g("Exports", j)
        if abs(gic - g("Gross inland consumption", j)) > TOL:
            raise RuntimeError(f"{yr}: gross inland consumption is not production plus net imports and stocks")
        fe = (g("Gross inland consumption", j) - g("Transformation input", j) + g("Transformation output", j)
              - g("Energy sector use", j) - g("Transport losses", j) - g("Non energy use", j))
        if abs(fe - g("Final energy use", j)) > TOL:
            raise RuntimeError(f"{yr}: final energy use is not the balance's remainder ({fe - g('Final energy use', j):+.1f} MWh)")
        for k in vals:
            kids = [c for c in vals if len(c) == len(k) + 1 and c[:len(k)] == k]
            if not kids:
                continue
            s = sum(vals[c][j] for c in kids)
            if all(vals[c][j] == 0 for c in kids) and vals[k][j] != 0 and len(k) >= 4:
                unsplit += 1
                continue
            if abs(s - vals[k][j]) > TOL:
                raise RuntimeError(f"{yr} {' / '.join(k)}: its parts make {s:,.1f} MWh, it {vals[k][j]:,.1f}")
        for tot, parts in (("Industry", INDUSTRY), ("Transport", TRANSPORT), ("Other Sectors", OTHER)):
            if abs(sum(sec[p][j] for p in parts) - sec[tot][j]) > TOL:
                raise RuntimeError(f"{yr}: {tot}'s branches do not make it")
        if abs(sec["Industry"][j] + sec["Transport"][j] + sec["Other Sectors"][j] - g("Final energy use", j)) > TOL:
            raise RuntimeError(f"{yr}: the sectors do not make final energy use")
        if br["Total"][j] is None:
            continue
        if abs(sum(br[b][j] for b in BRANCHES[:-1]) - br["Total"][j]) > TOL or abs(br["Total"][j] - g("Energy sector use", j)) > TOL:
            raise RuntimeError(f"{yr}: the energy sector's branches do not make its use")
    return unsplit


def rows_of(vals, sec, br, base):
    out, dropped = [], 0

    def add(entity, variable, node, series):
        nonlocal dropped
        if all(v == 0 or v is None for v in series):
            dropped += 1
            return
        for yr, v in zip(YEARS, series):
            if v is None:
                continue
            out.append(dict(entity=entity, variable=variable, ts_utc=f"{yr}-01-01T00:00:00Z", value=round(v, 3), unit="MWh",
                            freq="P1Y", geo="AT", market="", node=node, **base))

    for k, series in vals.items():
        var = VAR.get(k[0], slug(k[0]))
        ent = "statat_ele:at" if len(k) == 1 else "statat_ele:" + ":".join(slug(x) for x in k[1:])
        add(ent, var, " / ".join(k), series)
    for s in SECTORS:
        add(f"statat_ele:sector:{slug(s)}", "final_energy_use", f"Final energy use by sectors / {s}", sec[s])
    for b in BRANCHES[:-1]:
        add(f"statat_ele:branch:{slug(b)}", "energy_sector_use", f"Energy sector use / {b}", br[b])
    return pd.DataFrame(out), dropped


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Austria: Austria's electricity balance a year from 1970")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the file again")
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
        vals, sec, br = parse_sheet(sheet_rows(content, SHEET))
        unsplit = check(vals, sec, br)
        t, dropped = rows_of(vals, sec, br, base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        out = t[(t.entity == "statat_ele:at") & (t.variable == "transformation_output")].set_index("ts_utc").value
        fe = t[(t.entity == "statat_ele:at") & (t.variable == "final_energy_use")].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Statistics Austria, Energy balances Austria 1970-2024, sheet Electricity, its blocks in "
            "MWh: the balance items, the transformation input and output by plant type, owner and fuel, final energy use by sector "
            "and the energy sector's use by branch, each year from 1970 to 2024 (session 2764)",
            "Shape: series (docs/datastandard.md v0). entity statat_ele:at (a total), statat_ele:<plant>[:<owner>[:<fuel>[:<sub-fuel>]]], "
            "statat_ele:sector:<sector> or statat_ele:branch:<branch>; variable the balance item; unit MWh (the sheet's own MWh "
            "blocks, nothing converted); ts_utc the year's first day; freq P1Y; geo AT; node the sheet's labels. Gross inland "
            "consumption of electricity is its net imports; generation is the transformation output.",
            f"{len(t)} rows; generation (transformation output) and final energy use, MWh: " + ", ".join(
                f"{k[:4]} {out[k]:,.0f} and {fe[k]:,.0f}" for k in out.index if k[:4] in ("1970", "2000", "2024"))
            + f". The balance, every parent row and the sectors checked every year within {TOL:g} MWh; {unsplit} parent years "
            f"whose fuel breakdown is not yet split are not checked; {dropped} rows that are 0 in every year are not written; "
            "nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statat_energy_balance.py; the file retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {PAGE})",
            "License: Statistics Austria's general terms, section 10: reproduction and distribution, commercial or not, with the "
            "source cited and edits stated. Credit: STATISTIK AUSTRIA; edited by the ERW (reshaped, zero rows left out).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities, {t.variable.nunique()} variables; unsplit {unsplit}, "
              f"zero rows left {dropped}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Austria (Statistik Austria)",
                                    report="Energy balances Austria 1970-2024, sheet Electricity", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])  # general terms, section 10
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
