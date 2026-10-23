#!/usr/bin/env python3
"""EPA's Renewable Fuel Standard: the RINs generated and the renewable fuel produced, a month by D code and a year by D
code and fuel, from the EPA Moderated Transaction System (EMTS) as EPA publishes it (session 2030, chain 058: the
credits behind the biofuels the ERW held only as EIA's plant production).

Energy Research Warehouse (ERW) connector. Two series tables from the "Historical Monthly Data" CSV files on EPA's
Public Data for the Renewable Fuel Standard page; EPA re-issues each file every month with the whole history, and the
newest link on each listing page is taken:

    https://www.epa.gov/fuels-registration-reporting-and-compliance-help/public-data-renewable-fuel-standard
    .../spreadsheet-rin-generation-and-renewable-fuel     RIN generation and renewable fuel volume production by month
                                                          (rindata_<mon><year>.csv: FUEL_CODE, RIN_YEAR, Production Month,
                                                          RIN_QUANTITY, BATCH_VOLUME)
    .../spreadsheet-rin-generation-and-renewable-fuel-0   ... by fuel type (fuelproduction_<mon><year>.csv: RIN Year, Fuel,
                                                          Fuel Code, Fuel Category, Fuel Category Code, RIN Quantity,
                                                          Batch Volume)

    epa_rfs_rins_monthly   entity epa_rfs:d<code>; variables rins_generated (unit count) and batch_volume (unit gal, the
                           renewable fuel's volume in gallons, Decision 59); ts_utc the month's first day (RIN_YEAR and
                           Production Month); freq P1M; geo US; node the D code's name as the fuel type file gives it
    epa_rfs_fuel_annual    entity epa_rfs:d<code>:<fuel category code>; the same variables; ts_utc the RIN year's first
                           day; freq P1Y; geo US; node the fuel category as EPA names it (x_fuel_category), x_d_code_name

The D codes' names come from the fuel type file; a code in the monthly file it does not name stops the run, as does a
file without the columns above, a quantity not a whole number, or a month or year given twice. A month or fuel EPA does
not list has no row; nothing is filled. The latest year is partial (to the month the file names), and EPA's figures
change when reports are corrected (its page says so): each run replaces the tables whole.

    python warehouse/connectors/epa_rfs_rins.py [--offline] [--out-dir DIR]

Ceiling: four requests (two listing pages, two files), saved in warehouse/raw/epa_rfs_rins/ and reused offline.
www.epa.gov's robots file disallows only site machinery and search paths. EPA's bulk file API is not asked (no key).
License: public (EPA, read 55 of license_reads.csv: the agency's information is in the public domain unless noted).
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

CONNECTOR = "epa_rfs_rins"
SOURCE = "epa:rfs_emts"
HOST = "https://www.epa.gov"
PAGE = HOST + "/fuels-registration-reporting-and-compliance-help/public-data-renewable-fuel-standard"
LISTS = {"month": HOST + "/fuels-registration-reporting-and-compliance-help/spreadsheet-rin-generation-and-renewable-fuel",
         "fuel": HOST + "/fuels-registration-reporting-and-compliance-help/spreadsheet-rin-generation-and-renewable-fuel-0"}
STEMS = {"month": "rindata", "fuel": "fuelproduction"}
MONTHLY, ANNUAL = "epa_rfs_rins_monthly", "epa_rfs_fuel_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MON = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
COLS = {"month": ["FUEL_CODE", "RIN_YEAR", "Production Month", "RIN_QUANTITY", "BATCH_VOLUME"],
        "fuel": ["RIN Year", "Fuel", "Fuel Code", "Fuel Category", "Fuel Category Code", "RIN Quantity", "Batch Volume"]}
X_ANNUAL = ["x_fuel_category", "x_d_code_name"]


def newest(page_html, stem):
    """The newest <stem>_<mon><year>.csv a listing page links, as (year, month, absolute url)."""
    found = []
    for href in re.findall(r'href="([^"]+\.csv)"', page_html):
        m = re.search(rf"/{stem}_([a-z]{{3}})(\d{{4}})\.csv$", href, re.I)
        if m and m.group(1).lower() in MON:
            found.append((int(m.group(2)), MON[m.group(1).lower()], href if href.startswith("http") else HOST + href))
    if not found:
        raise RuntimeError(f"no {stem}_<month><year>.csv link on the listing page")
    return max(found)


def read(content, kind):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    d.columns = [c.strip() for c in d.columns]
    miss = [c for c in COLS[kind] if c not in d.columns]
    if miss:
        raise RuntimeError(f"{kind} file: no column {miss}; its columns are {list(d.columns)}")
    d = d[COLS[kind]].apply(lambda s: s.str.strip())
    d = d[(d != "").any(axis=1)]
    for c in COLS[kind]:
        if c in ("Fuel", "Fuel Category"):
            continue
        bad = ~d[c].str.replace(",", "", regex=False).str.fullmatch(r"-?\d+")
        if bad.any():
            raise RuntimeError(f"{kind} file: {c} not a whole number: {d.loc[bad, c].head(3).tolist()}")
        d[c] = d[c].str.replace(",", "", regex=False).astype("int64")
    return d


def d_names(fuel):
    names = fuel.groupby("Fuel Code")["Fuel"].agg(lambda s: sorted(set(s)))
    two = names[names.map(len) > 1]
    if len(two):
        raise RuntimeError(f"a D code with two names: {two.to_dict()}")
    return names.map(lambda s: s[0]).to_dict()


def monthly(m, names, base):
    unknown = sorted(set(m["FUEL_CODE"]) - set(names))
    if unknown:
        raise RuntimeError(f"D codes the fuel type file does not name: {unknown}")
    if not m["Production Month"].between(1, 12).all():
        raise RuntimeError("a production month outside 1 to 12")
    ts = m["RIN_YEAR"].astype(str) + "-" + m["Production Month"].map("{:02d}".format) + "-01T00:00:00Z"
    rows = []
    for var, col, unit in (("rins_generated", "RIN_QUANTITY", "count"), ("batch_volume", "BATCH_VOLUME", "gal")):
        rows.append(pd.DataFrame({"entity": "epa_rfs:d" + m["FUEL_CODE"].astype(str), "variable": var, "ts_utc": ts, "value": m[col],
                                  "unit": unit, "freq": "P1M", "geo": "US", "market": "", "node": m["FUEL_CODE"].map(names), **base}))
    return pd.concat(rows, ignore_index=True)


def annual(f, names, base):
    ent = "epa_rfs:d" + f["Fuel Code"].astype(str) + ":" + f["Fuel Category Code"].astype(str)
    ts = f["RIN Year"].astype(str) + "-01-01T00:00:00Z"
    rows = []
    for var, col, unit in (("rins_generated", "RIN Quantity", "count"), ("batch_volume", "Batch Volume", "gal")):
        rows.append(pd.DataFrame({"entity": ent, "variable": var, "ts_utc": ts, "value": f[col], "unit": unit, "freq": "P1Y", "geo": "US",
                                  "market": "", "node": f["Fuel Category"], **base, "x_fuel_category": f["Fuel Category"],
                                  "x_d_code_name": f["Fuel Code"].map(names)}))
    return pd.concat(rows, ignore_index=True)


def once(s, name):
    dup = s.duplicated(["entity", "variable", "ts_utc"])
    if dup.any():
        raise RuntimeError(f"{name}: an (entity, variable, ts_utc) given twice: {s.loc[dup, ['entity', 'ts_utc']].head(3).values.tolist()}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPA's Renewable Fuel Standard: RINs generated and renewable fuel produced")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
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
        frames, used = {}, {}
        for kind in ("fuel", "month"):
            page, _ = ip.fetch_raw(CONNECTOR, LISTS[kind], log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
            y, mo, url = newest(page.decode("utf-8", errors="replace"), STEMS[kind])
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120, pause=1)
            frames[kind] = read(content, kind)
            used[kind] = dict(url=url, through=f"{y}-{mo:02d}", retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        names = d_names(frames["fuel"])
        bm = dict(source=SOURCE, source_url=used["month"]["url"], retrieved_at=used["month"]["retrieved_at"], vintage=used["month"]["vintage"])
        bf = dict(source=SOURCE, source_url=used["fuel"]["url"], retrieved_at=used["fuel"]["retrieved_at"], vintage=used["fuel"]["vintage"])
        sm = monthly(frames["month"], names, bm)
        sa = annual(frames["fuel"], names, bf)
        once(sm, MONTHLY)
        once(sa, ANNUAL)
        codes = "; ".join(f"D{k} {v}" for k, v in sorted(names.items()))
        common = [
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/epa_rfs_rins.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Environmental Protection Agency, Public Data for the Renewable Fuel Standard (EMTS), {PAGE}",
        ]
        lic = 'License: public (EPA: the agency\'s information is in the public domain unless noted; cite "U.S. EPA, Renewable Fuel Standard, EMTS data").'
        cols_m = ip.SERIES_COLS
        sm = sm[cols_m].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head_m = [
            "Energy Research Warehouse (ERW): U.S. EPA, Renewable Fuel Standard, RIN generation and renewable fuel volume production by month, "
            f"by D code, {sm.ts_utc.min()[:7]} to {sm.ts_utc.max()[:7]} (session 2030)",
            "Shape: series (docs/datastandard.md v0). entity epa_rfs:d<code>; variables rins_generated (unit count) and batch_volume (unit gal, the "
            "renewable fuel's volume, Decision 59); ts_utc the month's first day (EPA's RIN_YEAR and Production Month); freq P1M; geo US; node the D "
            f"code's name as EPA's fuel type file gives it ({codes}).",
            f"{len(sm)} rows. The file runs through {used['month']['through']}; the latest year is partial, and EPA's figures change when reports are "
            "corrected. A month EPA does not list has no row; nothing is filled.",
        ] + common + [f"  access: {LISTS['month']} (the newest link), {used['month']['url']}", lic]
        ip.write_snapshot(sm, MONTHLY, head_m, log, cols_m)
        results.append(dict(table=MONTHLY, market="all", status="ok", detail=f"{len(sm)} rows"))
        cols_a = ip.SERIES_COLS + X_ANNUAL
        sa = sa[cols_a].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head_a = [
            "Energy Research Warehouse (ERW): U.S. EPA, Renewable Fuel Standard, RIN generation and renewable fuel volume production by fuel type, "
            f"a RIN year by D code and fuel category, {sa.ts_utc.min()[:4]} to {sa.ts_utc.max()[:4]} (session 2030)",
            "Shape: series (docs/datastandard.md v0). entity epa_rfs:d<code>:<EPA's fuel category code>; variables rins_generated (count) and "
            "batch_volume (gal, Decision 59); ts_utc the RIN year's first day; freq P1Y; geo US; node and x_fuel_category the fuel category as EPA "
            "names it; x_d_code_name the D code's name.",
            f"{len(sa)} rows, {sa.entity.nunique()} fuels. The file runs through {used['fuel']['through']}; the latest year is partial. A year and fuel "
            "EPA does not list has no row; nothing is filled.",
        ] + common + [f"  access: {LISTS['fuel']} (the newest link), {used['fuel']['url']}", lic]
        ip.write_snapshot(sa, ANNUAL, head_a, log, cols_a)
        results.append(dict(table=ANNUAL, market="all", status="ok", detail=f"{len(sa)} rows"))
        print(f"{MONTHLY}: {len(sm)} rows to {used['month']['through']}; {ANNUAL}: {len(sa)} rows, {sa.entity.nunique()} fuels")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results = [dict(table=t, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]) for t in (MONTHLY, ANNUAL)]
    if not args.out_dir:
        if results and all(r["status"] == "ok" for r in results):
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Environmental Protection Agency (EPA)",
                                    report="Public Data for the Renewable Fuel Standard: RIN generation and renewable fuel volume production (EMTS)",
                                    report_url=PAGE, document_list=LISTS["month"], license="public", tables=[MONTHLY, ANNUAL])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
