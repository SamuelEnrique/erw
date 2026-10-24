#!/usr/bin/env python3
"""Azerbaijan's electricity balance a year from 2007, and its electricity production and plant capacity by type of plant
from 1913, from the State Statistical Committee of the Republic of Azerbaijan's energy tables (session 2450, chain 118:
Azerbaijan's electricity balance).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statsaz_azerbaijan_electricity_annual.csv,
from three workbooks (Excel 97) of the Committee's Energy section (https://stat.gov.az/source/balance_fuel/?lang=en),
three requests:

    https://stat.gov.az/source/balance_fuel/en/003_1.18en.xls  sheet 3_1_18, "3.1.18 Electricity", million kWh, 2007 to
        2025: the electricity balance, every line with a value (balance_<line>: production, electricity plants and their
        kinds, CHP plants, import, export (negative, as printed), total supply, statistical difference, energy industries'
        own use, losses in transmission and distribution, final consumption and its sectors)
    https://stat.gov.az/source/balance_fuel/en/005_4en.xls  sheet 5.4, "Production of electricity, million kWh": the total
        and its parts by kind of plant (production_<kind>), 1913 to 2025 (single years before 2000: 1913, 1920, ... 1995)
    https://stat.gov.az/source/balance_fuel/en/005_3en.xls  sheet 5.3, "Plant capacity, MW", as of the end of the year:
        the total and its parts by kind of plant (capacity_<kind>), the same years

    entity statsaz:AZ; geo AZ; node Azerbaijan; ts_utc the year's 1 January; freq P1Y; unit MWh (million kWh times
    1,000) for the balance and production, MW for capacity

The workbooks' other sheets (the same balance in thousand toe and terajoules) are not taken. A dash ("-", nil) or "..."
(not available) has no row; nothing is filled. Checks, each stopping the run: in the balance, production is electricity
plants plus CHP plants, and electricity plants are their kinds; production (5.4) is its parts; capacity (5.3) is its
parts; the balance's production equals 5.4's within 1 GWh in each year both give; all within 1 GWh or 1 MW. A label,
year or value that does not read stops it too.

    python warehouse/connectors/statsaz_azerbaijan.py [--offline] [--out-dir DIR]

Ceiling: three requests, reused from warehouse/raw/statsaz_azerbaijan/ with --offline. stat.gov.az has no robots file
(its robots.txt answers with the home page, session 2450; www.stat.gov.az reset the connection). License: public with
the source cited (session 2450; the record's verdict, may be public): the site's footer reads "It is necessary to refer
to the information on the site..!" ("Saytdakı məlumatlardan istifadə edərkən istinad etmək zəruridir..!").
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd
import xlrd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "statsaz_azerbaijan_electricity_annual"
CONNECTOR = "statsaz_azerbaijan"
SOURCE = "statsaz:energy"
PAGE = "https://stat.gov.az/source/balance_fuel/?lang=en"
BASE = "https://stat.gov.az/source/balance_fuel/en/"
BALANCE, PRODUCTION, CAPACITY = "003_1.18en.xls", "005_4en.xls", "005_3en.xls"
PROD_COLS = {"production of electricity": "total", "fuel-fired electricity and chp plants": "fuel_fired_and_chp",
             "hydroelectric power plants": "hydro", "avtopro-ducers (working with fuel)": "autoproducers_fuel",
             "by generator": "by_generator", "wind power plants": "wind", "solar power plants": "solar",
             "electricity generated from was-tes incine-ration": "waste_incineration",
             "electricity generated from bio-mass inci-neration": "biomass_incineration"}
CAP_COLS = {"plant capacity as of the end of the year": "total", "fuel-fired electricity and chp plants - total": "fuel_fired_and_chp",
            "hydroelectric power plants": "hydro", "wind power plants": "wind", "solar power plants": "solar",
            "municipal solid waste plant": "municipal_solid_waste", "biogas power plants": "biogas"}
TOL = 1.0
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def text(x):
    return re.sub(r"\s+", " ", str(x or "")).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower().replace("pub.", "public")).strip("_")


def val(x, what):
    if isinstance(x, str):
        s = x.strip()
        if s in ("", "-", "...", "…"):
            return None
        raise RuntimeError(f"{what}: not a number: {x!r}")
    return float(x)


def year(x, what):
    if isinstance(x, float) and x == int(x) and 1900 <= x <= 2100:
        return int(x)
    try:
        y = int(float(str(x).strip()))
    except ValueError:
        raise RuntimeError(f"{what}: not a year: {x!r}")
    if not 1900 <= y <= 2100:
        raise RuntimeError(f"{what}: not a year: {x!r}")
    return y


def balance(book):
    s = book.sheet_by_name("3_1_18")
    if "million kwh" not in " ".join(text(s.cell_value(r, c)).lower() for r in range(4) for c in range(s.ncols)):
        raise RuntimeError("3_1_18: not in million kWh")
    years = {c: year(s.cell_value(3, c), f"3_1_18 column {c}") for c in range(2, s.ncols) if s.cell_value(3, c) != ""}
    out, seen = {}, {}
    for r in range(5, s.nrows):
        label = text(s.cell_value(r, 1))
        if not label:
            continue
        var = "balance_" + slug(label)
        if var in seen:   # "Electricity plants" and "CHP plants" come twice: in production, and as transformation input
            var = "balance_transformation_" + slug(label)
        if var in seen:
            raise RuntimeError(f"3_1_18: {label!r} three times")
        seen[var] = label
        for c, y in years.items():
            v = val(s.cell_value(r, c), f"3_1_18 {label} {y}")
            if v is not None:
                out[(var, y)] = v
    for y in years.values():
        g = lambda k: out.get(("balance_" + k, y), 0.0)  # noqa: E731
        if abs(g("electricity_plants_ep") + g("chp_plants") - g("production")) > TOL:
            raise RuntimeError(f"3_1_18 {y}: electricity plants and CHP plants add to {g('electricity_plants_ep') + g('chp_plants')}, production is {g('production')}")
        kinds = sum(g(k) for k in ("ep_working_with_fuel", "hydroelectric_power_plants", "wind_power_plants", "solar_power_plants",
                                   "electricity_generated_from_waste_incineration"))
        if abs(kinds - g("electricity_plants_ep")) > TOL:
            raise RuntimeError(f"3_1_18 {y}: the kinds add to {kinds}, electricity plants are {g('electricity_plants_ep')}")
    return out, seen


def by_kind(book, sheet, cols, what):
    s = book.sheet_by_index(0)
    head = {}
    for c in range(s.ncols):
        for r in (3, 4):
            lab = text(s.cell_value(r, c)).lower()
            if lab in cols:
                head[c] = cols[lab]
    if sorted(head.values()) != sorted(cols.values()):
        raise RuntimeError(f"{what}: columns not as read: {sorted(head.values())}")
    out = {}
    for r in range(5, s.nrows):
        if text(s.cell_value(r, 1)) == "":
            continue
        y = year(s.cell_value(r, 1), f"{what} row {r}")
        for c, k in head.items():
            v = val(s.cell_value(r, c), f"{what} {y} {k}")
            if v is not None:
                out[(k, y)] = v
    for y in {y for _, y in out}:
        parts = sum(v for (k, yy), v in out.items() if yy == y and k != "total")
        tot = out.get(("total", y))
        has_parts = any(k != "total" for (k, yy) in out if yy == y)
        if tot is not None and has_parts and abs(parts - tot) > TOL:
            # before 2000 the parts are not all given ("..."): checked only where every part is printed
            if y >= 2000:
                raise RuntimeError(f"{what} {y}: the parts add to {parts}, the total is {tot}")
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Azerbaijan's State Statistical Committee: the electricity balance, production and capacity, a year")
    ap.add_argument("--offline", action="store_true", help="the saved workbooks only, no request")
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
        if not args.offline and (ip.paused("statsaz") or ip.paused_host("stat.gov.az")):
            raise RuntimeError("Azerbaijan's State Statistical Committee is paused (warehouse/metadata/paused_sources.csv): not requested")
        books, got = {}, []
        for f in (BALANCE, PRODUCTION, CAPACITY):
            content, rec = ip.fetch_raw(CONNECTOR, BASE + f, log, offline=args.offline, pause=2, headers=UA, timeout=180)
            books[f] = (xlrd.open_workbook(file_contents=content), rec)
            got.append(rec.get("retrieved_at") or "")
        bal, labels = balance(books[BALANCE][0])
        prod = by_kind(books[PRODUCTION][0], "5.4", PROD_COLS, "5.4")
        cap = by_kind(books[CAPACITY][0], "5.3", CAP_COLS, "5.3")
        gap = max(abs(bal[("balance_production", y)] - prod[("total", y)]) for (k, y) in prod if k == "total" and ("balance_production", y) in bal)
        if gap > TOL:
            raise RuntimeError(f"the balance's production and 5.4's differ by up to {gap} million kWh")
        rows = []
        for f, data, prefix, unit, factor in ((BALANCE, bal, "", "MWh", 1000.0), (PRODUCTION, prod, "production_", "MWh", 1000.0),
                                             (CAPACITY, cap, "capacity_", "MW", 1.0)):
            rec = books[f][1]
            for (k, y), v in data.items():
                rows.append(dict(entity="statsaz:AZ", variable=prefix + k, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * factor, 3), unit=unit,
                                 freq="P1Y", geo="AZ", market="", node=(labels.get(k) if f == BALANCE else f"{'Production of electricity' if prefix == 'production_' else 'Plant capacity, end of year'}: {k}"),
                                 source=SOURCE, source_url=BASE + f, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec)))
        t = finish(rows)
        header = [
            f"Energy Research Warehouse (ERW): State Statistical Committee of the Republic of Azerbaijan, the electricity balance (2007 to 2025), electricity production and plant capacity by kind of plant ({t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]}) (session 2450)",
            "Shape: series (docs/datastandard.md v0). entity statsaz:AZ; variable balance_<line> (table 3.1.18: production, electricity plants and their kinds, CHP plants, import, export (negative, as printed), total supply, statistical difference, "
            "transformation input, energy industries' own use, losses, final consumption and its sectors), production_<kind> (table 5.4) in MWh (million kWh times 1,000), capacity_<kind> (table 5.3, end of year) in MW; "
            "ts_utc the year's 1 January; freq P1Y; geo AZ. The balance's lines and the kinds overlap (totals hold their parts): a sum takes one level. Before 2000 only single years are given (1913, 1920 to 1990 by ten, 1995).",
            f"{len(t)} rows, {t.variable.nunique()} variables. Production is electricity plants plus CHP plants, electricity plants are their kinds, and production and capacity are their kinds from 2000, within 1 GWh or 1 MW; "
            f"the balance's production equals table 5.4's within {gap:.1f} GWh. A dash or ... has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statsaz_azerbaijan.py; the workbooks retrieved {min(got)} to {max(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} State Statistical Committee of the Republic of Azerbaijan, Energy: tables 3.1.18 (Electricity, million kWh), 5.4 (Production of electricity) and 5.3 (Plant capacity), {PAGE}",
            f"  access: {BASE}{BALANCE}, {BASE}{PRODUCTION}, {BASE}{CAPACITY}",
            "License: public with the source cited (the record's verdict, may be public): the site reads \"It is necessary to refer to the information on the site..!\". Cite: State Statistical Committee of the Republic of Azerbaijan, stat.gov.az.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="State Statistical Committee of the Republic of Azerbaijan",
                                    report="Energy: 3.1.18 Electricity balance, 5.4 Production of electricity, 5.3 Plant capacity",
                                    report_url=PAGE, document_list=BASE + BALANCE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} variables; production gap {gap:.2f} GWh")
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
