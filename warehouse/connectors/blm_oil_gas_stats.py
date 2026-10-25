#!/usr/bin/env python3
"""The Bureau of Land Management's oil and gas statistics: federal onshore leases, acreage, drilling permits approved,
wells spud and producible wells, by state and fiscal year (session 2106, chain 069: the federal lands where much of the
West's oil and gas is drilled, beside ONRR's production on them).

Energy Research Warehouse (ERW) connector. One series table from BLM's workbook "All Fed O&G Statistics by Year by
State" (Tables 1 to 10 and their Summary, fiscal years 2001 to the latest), linked from

    https://www.blm.gov/programs/energy-and-minerals/oil-and-gas/oil-and-gas-statistics

    blm_oil_gas_statistics_annual   entity blm_oil_gas:<state postal code>; variables leases_in_effect (Table 1, count),
               acres_under_lease (Table 2, acre), new_leases_issued (Table 3, count), acres_newly_leased (Table 4, acre),
               producing_leases (Table 5, count), producing_acres (Table 6, acre), apds_approved (Table 7, count: applications
               for permit to drill approved), wells_spud (Table 8, count), producible_service_well_bores (Table 9, count),
               producible_service_completions (Table 10, count); ts_utc 1 October of the year before the fiscal year (FY 2025
               begins 1 October 2024); freq P1Y; geo US-<state>; node the state as BLM names it; x_fiscal_year; x_table;
               x_as_of the date the workbook says its figures stand at

The figures are federal only: BLM's notes say they leave out Indian leases and wells. Tables 1, 2, 5, 6, 9 and 10 are
counts on the last day of the fiscal year; Tables 3, 4, 7 and 8 are counts during it. Each sheet must hold a header row
"Geographic State" with columns "FY <year>", one row a state and a total row; the states must sum to BLM's total in every
year, and each total must equal the Summary sheet's, or the run stops. The total rows are checked and not kept (a sum of
the table's rows gives them). A state not in the map, a state given twice, a sheet not found, a year column missing, or
a cell that is not a number stops the run. Nothing is filled.

    python warehouse/connectors/blm_oil_gas_stats.py [--offline] [--out-dir DIR]

Ceiling: two requests (the statistics page, read for the workbook's address, and the workbook; both saved in
warehouse/raw/blm_oil_gas_stats/ and reused offline; asked again unless --offline, since the page and the workbook keep their addresses). BLM's robots file disallows /core/, /profiles/, /search/, /admin/
and the user pages, not /programs/ or /sites/default/files/. License: may be public (the Department of the Interior's
notice, read 159: materials produced by federal agencies are generally in the public domain); cite BLM as the source.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import urllib.parse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "blm_oil_gas_stats"
SOURCE = "blm:oil_gas_statistics"
HOST = "www.blm.gov"
PAGE = "https://www.blm.gov/programs/energy-and-minerals/oil-and-gas/oil-and-gas-statistics"
TABLE = "blm_oil_gas_statistics_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_fiscal_year", "x_table", "x_as_of"]
# table number: (variable, unit, the Summary row's words lowered with letters only, starting after any footnote digit)
TABLES = {
    1: ("leases_in_effect", "count", "totalnumberofleasesineffect"),
    2: ("acres_under_lease", "acre", "totalnumberofacresleased"),
    3: ("new_leases_issued", "count", "totalnumberofnewleasesissuedduringtheyear"),
    4: ("acres_newly_leased", "acre", "totalnumberofacresleasedduringtheyear"),
    5: ("producing_leases", "count", "totalnumberofproducingleasesonfederallands"),
    6: ("producing_acres", "acre", "totalnumberofproducingacresonfederallands"),
    7: ("apds_approved", "count", "totalnumberofapdsapprovedbyyearonfederallands"),
    8: ("wells_spud", "count", "totalnumberofwellsstartedspudduringtheyearonfederallands"),
    9: ("producible_service_well_bores", "count", "totalnumberofproducibleandserviceholesonfederallands"),
    10: ("producible_service_completions", "count", "totalnumberofproducibleandservicecompletionsonfederallands"),
}
STATES = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
          "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
          "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
          "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
          "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
          "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
          "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}


def letters(s):
    return re.sub(r"[^a-z]", "", str(s).lower())


def number(x, where):
    if isinstance(x, bool) or isinstance(x, str) or pd.isna(x):
        raise RuntimeError(f"{where}: not a number: {x!r}")
    return float(x)


def workbook_url(page):
    """The one link on the statistics page to the workbook of Tables 1 to 10 by year and state, the latest fiscal year's."""
    hrefs = set(re.findall(r'href="([^"]+\.xlsx)"', page))
    hits = []
    for h in hrefs:
        name = urllib.parse.unquote(h).lower()
        m = re.search(r"by year by state.*fy ?(\d{2,4})\.xlsx$", name) or re.search(r"fy(\d{4})-oil-and-gas-statistics-all-fed", name)
        if "all fed" in name.replace("-", " ") and m:
            fy = int(m.group(1))
            hits.append((fy + 2000 if fy < 100 else fy, h))
    if not hits:
        raise RuntimeError("the statistics page links no 'All Fed O&G Statistics by Year by State' workbook")
    hits.sort()
    fy, h = hits[-1]
    if sum(1 for f, _ in hits if f == fy) != 1:
        raise RuntimeError(f"more than one workbook for FY {fy}: {[x for f, x in hits if f == fy]}")
    return urllib.parse.urljoin(PAGE, h), fy


def as_of(v, where):
    t = str(v.iat[0, 0]).strip()
    m = re.fullmatch(r"As of (\d{1,2})/(\d{1,2})/(\d{4})", t)
    if not m:
        raise RuntimeError(f"{where}: the first cell is not 'As of m/d/yyyy': {t!r}")
    return f"{int(m.group(3)):04d}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"


def summary(x):
    """The Summary sheet's national totals: {table number: {fiscal year: value}}."""
    v = pd.read_excel(x, "Summary", header=None, dtype=object, keep_default_na=False)
    h = [i for i in range(min(len(v), 10)) if any(re.fullmatch(r"FY +\d{4}", str(c).strip()) for c in v.iloc[i])]
    if len(h) != 1:
        raise RuntimeError("Summary: no single header row of fiscal years")
    years = {j: int(m.group(1)) for j in range(v.shape[1]) if (m := re.fullmatch(r"FY +(\d{4})", str(v.iat[h[0], j]).strip()))}
    out = {}
    for i in range(h[0] + 1, len(v)):
        key = letters(re.sub(r"^\s*\d\s+", "", str(v.iat[i, 0])))
        n = [k for k, (_, _, words) in TABLES.items() if key == words]
        if n:
            if n[0] in out:
                raise RuntimeError(f"Summary: {key} given twice")
            out[n[0]] = {fy: number(v.iat[i, j], f"Summary {key} FY {fy}") for j, fy in years.items()}
    missing = sorted(set(TABLES) - set(out))
    if missing:
        raise RuntimeError(f"Summary: no row for Tables {missing}")
    return out, years


def parse(x, n, base, totals):
    var, unit, _ = TABLES[n]
    names = [s for s in x.sheet_names if re.match(rf"Table {n}\b", s.strip())]
    if len(names) != 1:
        raise RuntimeError(f"Table {n}: not one sheet ({x.sheet_names})")
    v = pd.read_excel(x, names[0], header=None, dtype=object, keep_default_na=False)
    when = as_of(v, names[0])
    h = [i for i in range(min(len(v), 10)) if str(v.iat[i, 0]).strip() == "Geographic State"]
    if len(h) != 1:
        raise RuntimeError(f"{names[0]}: no single 'Geographic State' header row")
    h = h[0]
    # Table 3 writes "FY  2020" on, with two spaces
    years = {j: int(m.group(1)) for j in range(1, v.shape[1]) if (m := re.fullmatch(r"FY +(\d{4})", str(v.iat[h, j]).strip()))}
    if sorted(years.values()) != sorted(totals[n]):
        raise RuntimeError(f"{names[0]}: its years differ from the Summary's: {sorted(years.values())}")
    out, seen, total = [], set(), None
    for i in range(h + 1, len(v)):
        name = str(v.iat[i, 0]).strip()
        if not name:
            if any(str(v.iat[i, j]).strip() for j in years):
                raise RuntimeError(f"{names[0]} row {i}: figures with no state")
            continue
        if name.upper() == "TOTAL":
            total = {fy: number(v.iat[i, j], f"{names[0]} total FY {fy}") for j, fy in years.items()}
            break
        if name not in STATES:
            raise RuntimeError(f"{names[0]} row {i}: not a state in the map: {name!r}")
        if name in seen:
            raise RuntimeError(f"{names[0]}: {name} given twice")
        seen.add(name)
        st = STATES[name]
        for j, fy in years.items():
            out.append(dict(base, entity=f"blm_oil_gas:{st.lower()}", variable=var, ts_utc=f"{fy - 1}-10-01T00:00:00Z",
                            value=number(v.iat[i, j], f"{names[0]} {name} FY {fy}"), unit=unit, freq="P1Y", geo=f"US-{st}", market="",
                            node=name, x_fiscal_year=str(fy), x_table=f"Table {n}", x_as_of=when))
    if total is None:
        raise RuntimeError(f"{names[0]}: no total row")
    if len(seen) != len(STATES):
        raise RuntimeError(f"{names[0]}: {len(seen)} states, not {len(STATES)}: missing {sorted(set(STATES) - seen)}")
    for fy, t in total.items():
        s = sum(r["value"] for r in out if r["x_fiscal_year"] == str(fy))
        if abs(s - t) > 0.6:
            raise RuntimeError(f"{names[0]} FY {fy}: the states sum to {s}, BLM's total is {t}")
        if abs(t - totals[n][fy]) > 0.6:
            raise RuntimeError(f"{names[0]} FY {fy}: the total {t} differs from the Summary's {totals[n][fy]}")
    return out, when


def main(argv=None):
    ap = argparse.ArgumentParser(description="BLM's oil and gas statistics: federal leases, acreage, permits and wells by state and fiscal year")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        page, prec = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        url, fy = workbook_url(page.decode("utf-8", errors="replace"))
        log(f"  workbook for FY {fy}: {url}")
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        x = pd.ExcelFile(io.BytesIO(content))
        totals, _ = summary(x)
        rows, dates = [], set()
        for n in TABLES:
            got, when = parse(x, n, base, totals)
            log(f"  Table {n}: {len(got)} rows, as of {when}")
            rows += got
            dates.add(when)
        s = pd.DataFrame(rows)
        if max(s.x_fiscal_year.astype(int)) != fy:
            raise RuntimeError(f"the workbook's last year is FY {max(s.x_fiscal_year.astype(int))}, its name says FY {fy}")
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        first, last = s.x_fiscal_year.astype(int).min(), s.x_fiscal_year.astype(int).max()
        head = [
            f"Energy Research Warehouse (ERW): Bureau of Land Management, Oil and Gas Statistics, federal onshore leases, acreage, drilling "
            f"permits approved, wells spud and producible wells by state, fiscal years {first} to {last} (session 2106)",
            "Shape: series (docs/datastandard.md v0). entity blm_oil_gas:<state>; variables leases_in_effect, acres_under_lease, new_leases_issued, "
            "acres_newly_leased, producing_leases, producing_acres, apds_approved, wells_spud, producible_service_well_bores, "
            "producible_service_completions (count, or acre for the acreage); freq P1Y; ts_utc 1 October before the fiscal year; geo US-<state>; "
            "node the state as BLM names it; x_fiscal_year; x_table (BLM's Tables 1 to 10); x_as_of the date BLM's sheets give.",
            f"{s.entity.nunique()} states, every state BLM lists (zeros kept as BLM prints them). Federal only: BLM's notes say Indian leases "
            "and wells are not included, so some states' totals are below BLM's reports that include both. Leases, acreage, producing leases "
            "and acres, well bores and completions stand on the fiscal year's last day; new leases, acres leased, permits approved and wells "
            "spud are counted during it. BLM's notes: the well and permit data come from its Automated Fluid Minerals Support System, which "
            "updates often, and earlier years are from Public Land Statistics. The total rows were checked against the states and the "
            "Summary sheet and are not kept.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/blm_oil_gas_stats.py; the workbook retrieved {base['retrieved_at']}; "
            f"its sheets as of {', '.join(sorted(dates))}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of the Interior, Bureau of Land Management, Oil and Gas Statistics, {PAGE}",
            f"  access: {url}",
            "License: may be public (the Department of the Interior's notice: materials produced by federal agencies are generally in the "
            "public domain; see license_verdicts.csv). Cite the Bureau of Land Management as the source.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} states, FY {first} to {last}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of the Interior, Bureau of Land Management (BLM)",
                                    report="Oil and Gas Statistics: All Federal Oil and Gas Statistics by Year by State (Tables 1 to 10)",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
