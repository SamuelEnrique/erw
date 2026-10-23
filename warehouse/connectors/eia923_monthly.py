#!/usr/bin/env python3
"""EIA-923: each plant's monthly net generation and fuel consumed, by prime mover and fuel (session 897, chain 049).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia923_plant_fuel_monthly.csv, from the
U.S. Energy Information Administration's Form EIA-923 yearly zips (f923_<year>.zip, the workbook
EIA923_Schedules_2_3_4_5_M_<month>_<year>_<date>.xlsx, sheets "Page 1 Generation and Fuel Data" and "Page 1 Puerto Rico"),
linked from https://www.eia.gov/electricity/data/eia923/ :

    entity    eia923m:<plant id>:<reported prime mover>:<reported fuel type code>:<nuclear unit id, empty for none>
    variable  net_generation (MWh), fuel_consumed and fuel_consumed_electric (TBtu: EIA's MMBtu times 0.000001, the
              second the part consumed to make electricity, as eia923_plant_fuel_annual gives fuel in TBtu)
    ts_utc    the month's first day; freq P1M; geo US-<plant state> (PR for Puerto Rico); node the plant's name;
              x_operator_id, x_operator_name, x_nerc_region, x_ba_code, x_sector_name, x_chp, x_mer_fuel_type as EIA gives them

A month EIA has not yet reported ("."), or leaves empty, has no row; nothing is filled. Plant 99999, EIA's state-level
increment (an aggregate by state and fuel, not a plant), is left out. The physical quantities (in each
fuel's own unit), the heat content per unit and the energy storage sheet are not taken. A key EIA gives twice with two
different values has no key: both records are left out whole and named in the header (chain 030's rule). A heading not
in the form read stops the run.

Years: only those whose zip EIA keeps outside /archive/ (its robots file disallows /archive/, session 666): when written,
2025 and 2026 (to date), as the page read in session 897 links them; an older year answers 404 there and stops the run.

    python warehouse/connectors/eia923_monthly.py --years 2025 [2026] [--offline]

Ceiling: one request a year (the zip, saved in warehouse/raw/eia923_monthly/ and reused); the page is not asked for.
License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information Administration, Form EIA-923").
"""

import argparse
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

NAME = "eia923_plant_fuel_monthly"
CONNECTOR = "eia923_monthly"
SOURCE = "eia:eia923:monthly"
PAGE = "https://www.eia.gov/electricity/data/eia923/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEETS = ["Page 1 Generation and Fuel Data", "Page 1 Puerto Rico"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
FIGURES = {"Netgen": ("net_generation", "MWh", 1.0), "Tot_MMBtu": ("fuel_consumed", "TBtu", 1e-6),
           "Elec_MMBtu": ("fuel_consumed_electric", "TBtu", 1e-6)}
CHARS = {"Plant Id": "plant", "Nuclear Unit Id": "nuclear", "Plant Name": "name", "Operator Name": "x_operator_name",
         "Operator Id": "x_operator_id", "Plant State": "state", "NERC Region": "x_nerc_region", "EIA Sector Number": None,
         "Sector Name": "x_sector_name", "Reported Prime Mover": "prime_mover", "Reported Fuel Type Code": "fuel",
         "MER Fuel Type Code": "x_mer_fuel_type", "Balancing Authority Code": "x_ba_code",
         "Combined Heat And Power Plant": "x_chp", "Respondent Frequency": "x_respondent_frequency", "YEAR": "year"}
X = ["x_operator_id", "x_operator_name", "x_nerc_region", "x_ba_code", "x_sector_name", "x_chp", "x_mer_fuel_type", "x_respondent_frequency"]


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def zip_url(year):
    """The year's zip outside /archive/ (the page links xls/f923_<year>.zip for the newest years, archive/xls/ for the
    rest); the page itself is not asked for (session 897's ceiling). A year EIA has moved answers 404 and stops the run."""
    return PAGE + f"xls/f923_{year}.zip"


def sheet_rows(frame, year, url, retrieved, skipped):
    heads = [r for r in range(min(10, len(frame))) if text(frame.iloc[r, 0]) == "Plant Id"]
    if not heads:
        raise RuntimeError(f"{year}: no heading row names 'Plant Id'")
    hr = heads[0]
    cols, figs = {}, {}
    for c, v in enumerate(frame.iloc[hr]):
        h = text(v)
        if not h or h == "Reserved":
            continue
        m = re.fullmatch(r"(\w+) (January|February|March|April|May|June|July|August|September|Septembe|October|November|December)", h)
        if m:
            month = next(i for i, mn in enumerate(MONTHS, 1) if mn.startswith(m.group(2)))
            if m.group(1) in FIGURES:
                figs[(m.group(1), month)] = c
            elif m.group(1) not in ("Quantity", "Elec_Quantity", "MMBtuPer_Unit"):
                raise RuntimeError(f"{year}: a monthly heading not in the form read: {h!r}")
            continue
        key = next((k for k in CHARS if h.startswith(k)), None)
        if key is None:
            if re.match(r"(Total Fuel Consumption|Elec Fuel Consumption|Electric Fuel Consumption|Net Generation|Physical Unit Label|Census Region|NAICS Code)", h):
                continue                                               # the year-to-date totals and fields not taken
            raise RuntimeError(f"{year}: a heading not in the form read: {h!r}")
        if CHARS[key]:
            cols[CHARS[key]] = c
    if len(figs) != 36:
        raise RuntimeError(f"{year}: {len(figs)} monthly figures found, not 36")
    for k in ("plant", "name", "state", "prime_mover", "fuel", "year"):
        if k not in cols:
            raise RuntimeError(f"{year}: the field '{k}' is missing")
    d = frame.iloc[hr + 1:]
    d = d[pd.to_numeric(d[cols["year"]], errors="coerce").eq(year)]
    # plant 99999 is EIA's "State-Fuel Level Increment", an aggregate by state, not a plant: left out, named in the header
    d = d[pd.to_numeric(d[cols["plant"]], errors="coerce").ne(99999)]
    out = []
    for _, r in d.iterrows():
        nuclear = text(r[cols["nuclear"]]) if "nuclear" in cols else ""
        nuclear = "" if nuclear == "." else nuclear
        plant, state = text(r[cols["plant"]]), text(r[cols["state"]])
        base = dict(entity=f"eia923m:{plant}:{text(r[cols['prime_mover']])}:{text(r[cols['fuel']])}:{nuclear}", freq="P1M",
                    geo=f"US-{state}" if state else "US", market="", node=text(r[cols["name"]]), source=SOURCE, source_url=url,
                    retrieved_at=retrieved, vintage="", **{x: text(r[cols[x]]) if x in cols else "" for x in X})
        for (fig, month), c in figs.items():
            v = pd.to_numeric(r[c], errors="coerce")
            if pd.isna(v):
                continue
            var, unit, scale = FIGURES[fig]
            out.append(dict(base, variable=var, ts_utc=f"{year}-{month:02d}-01T00:00:00Z", value=float(v) * scale, unit=unit))
    t = pd.DataFrame(out)
    if len(t):
        t = t.drop_duplicates()
        twice = t.duplicated(["entity", "variable", "ts_utc"], keep=False)
        if twice.any():
            bad = set(t.loc[twice, "entity"])
            skipped.setdefault("no key", set()).update(f"{e} {year}" for e in bad)
            t = t[~t["entity"].isin(bad)]
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-923: each plant's monthly net generation and fuel consumed")
    ap.add_argument("--years", type=int, nargs="+", required=True)
    ap.add_argument("--offline", action="store_true", help="the saved page and zips only, no request")
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
        frames, got, skipped, books = [], [], {}, []
        for y in sorted(args.years):
            url = zip_url(y)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=900)
            zf = zipfile.ZipFile(io.BytesIO(content))
            name = next((n for n in zf.namelist() if n.startswith("EIA923_Schedules_2_3_4_5")), None)
            if not name:
                raise RuntimeError(f"f923_{y}.zip holds no schedules workbook: {zf.namelist()}")
            books.append(name)
            xl = pd.ExcelFile(io.BytesIO(zf.read(name)))
            for sheet in SHEETS:
                if sheet not in xl.sheet_names:
                    raise RuntimeError(f"{name} holds no sheet {sheet!r}")
                t = sheet_rows(pd.read_excel(xl, sheet, header=None), y, url, rec.get("retrieved_at") or "", skipped)
                log(f"{y} {sheet}: {len(t):,} rows")
                frames.append(t)
            got.append(f"{url} (retrieved {rec.get('retrieved_at', '')})")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row in two sheets")
        cols = ip.SERIES_COLS + X
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        nokey = sorted(skipped.get("no key", ()))
        months = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA-923, each plant's monthly net generation and fuel consumed, by prime mover and fuel (session 897)",
            "Shape: series (docs/datastandard.md v0). entity eia923m:<plant>:<prime mover>:<fuel type code>:<nuclear unit, empty for none>; variable "
            "net_generation (MWh), fuel_consumed and fuel_consumed_electric (TBtu, EIA's MMBtu times 0.000001); ts_utc the month's first day; freq P1M; "
            "geo US-<state>; node the plant's name; x_* EIA's fields.",
            f"Months {months} (workbooks {', '.join(books)}); {len(s):,} rows, {s['entity'].str.split(':').str[1].nunique():,} plants. A month EIA has not "
            "reported ('.') has no row; nothing is filled. EIA's state-level increments (plant 99999) left out. Physical quantities, heat content per unit and the energy storage sheet not taken."
            + (f" Records EIA gives twice with two values, left out (no key): {', '.join(nokey)}." if nokey else ""),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia923_monthly.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-923, Schedules 2, 3, 4 and 5, page 1, {PAGE}",
            f"  access: {'; '.join(got)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-923").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-923, monthly generation and fuel consumption by plant", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{months}: {len(s):,} rows"))
        print(f"{NAME}: {months}, {len(s):,} rows")
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
