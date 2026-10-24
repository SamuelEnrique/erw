#!/usr/bin/env python3
"""The Census Bureau's value of construction put in place (C30), a month from January 1993, by type and owner: private
construction (data centers from 2014, power, electric, manufacturing among its 67 types) and public construction
(federal, state and local, power among them), seasonally adjusted at annual rates and not adjusted (session 2258, chain
102: what the United States builds, data centers and power plants beside the rest, in dollars a month).

Energy Research Warehouse (ERW) connector. One series table from four workbooks of the Census Bureau's construction
spending time series (www.census.gov/construction/c30/historical_data.html):

    https://www.census.gov/construction/c30/xlsx/privsatime.xlsx   private, seasonally adjusted annual rate
    https://www.census.gov/construction/c30/xlsx/privtime.xlsx     private, not seasonally adjusted
    https://www.census.gov/construction/c30/xlsx/pubsatime.xlsx    public, seasonally adjusted annual rate
    https://www.census.gov/construction/c30/xlsx/pubtime.xlsx      public, not seasonally adjusted

    census_c30_construction_monthly   entity census_c30:<owner>:<type> (owner private, public, state_local or federal, from
               the column's own words; type the column's name as a slug, its footnote figure dropped); variable
               value_put_in_place (not seasonally adjusted, the month's spending) or value_put_in_place_saar (seasonally
               adjusted, at an annual rate); value in USD (the Census Bureau's millions of dollars times 1,000,000); ts_utc
               the month's first day; freq P1M; geo US; node the column as the Census Bureau names it; x_column; x_status
               p (preliminary) or r (revised) as the Census Bureau marks the month

A blank cell has no row (the data center column begins in January 2014). Each workbook must open on its title, state
millions of dollars, carry a Date column and the months as Mon-YY; a column name given twice, a month given twice, or a
figure that does not read stops the run. The notes under the months end the sheet. Nothing is filled.

    python warehouse/connectors/census_c30.py [--offline] [--out-dir DIR]

Ceiling: four requests (the workbooks, each asked again unless --offline, since the Census Bureau revises the months each
release at the same addresses). www.census.gov has no robots file (HTTP 404); its private power detail workbook
(privatepower.xlsx) answered HTTP 500 and is not asked. License: public (the Census Bureau's verdict on record; a work of
the U.S. government).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import openpyxl
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "census_c30"
SOURCE = "census:c30_construction_spending"
HOST = "www.census.gov"
PAGE = "https://www.census.gov/construction/c30/historical_data.html"
TABLE = "census_c30_construction_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FILES = [("privsatime", "private", "value_put_in_place_saar", "Value of Private Construction Put in Place - Seasonally Adjusted Annual Rate"),
         ("privtime", "private", "value_put_in_place", "Value of Private Construction Put in Place - Not Seasonally Adjusted"),
         ("pubsatime", "public", "value_put_in_place_saar", "Value of Public Construction Put in Place - Seasonally Adjusted Annual Rate"),
         ("pubtime", "public", "value_put_in_place", "Value of Public Construction Put in Place - Not Seasonally Adjusted")]
OWNERS = [("Total State and Local Construction", "state_local"), ("State ", "state_local"), ("Total Federal Construction", "federal"),
          ("Federal ", "federal"), ("Total Public Construction", "public"), ("Public ", "public")]
X_COLS = ["x_column", "x_status"]
MONTH = re.compile(r"^([A-Z][a-z]{2})-(\d{2})([pr]?)$")


def url_of(stem):
    return f"https://www.census.gov/construction/c30/xlsx/{stem}.xlsx"


def clean(c):
    return re.sub(r"\s+", " ", str(c).replace("_x000D_", " ")).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def owner_type(col, kind):
    name = re.sub(r"\d+$", "", col).strip()  # the footnote figure
    if kind == "private":
        return "private", slug(name)
    for prefix, owner in OWNERS:
        if name.startswith(prefix):
            rest = name[len(prefix):].strip() if not prefix.startswith("Total") else "total"
            return owner, slug(rest)
    raise RuntimeError(f"a public column not in the map: {col!r}")


def parse(content, stem, kind, var, title, base, counts):
    ws = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    if clean(rows[0][0]) != title or "Millions of dollars" not in clean(rows[1][0]):
        raise RuntimeError(f"{stem}: not the workbook read: {rows[0][0]!r} {rows[1][0]!r}")
    h = next(i for i, r in enumerate(rows) if r and r[0] == "Date")
    cols = [(j, clean(c)) for j, c in enumerate(rows[h]) if j > 0 and c not in (None, "") and clean(c) != "None"]
    names = [c for _, c in cols]
    if len(set(names)) != len(names):
        raise RuntimeError(f"{stem}: a column given twice")
    ents = {j: owner_type(c, kind) for j, c in cols}
    out, seen = [], set()
    for r in rows[h + 1:]:
        if not r or r[0] is None or not isinstance(r[0], str) or not MONTH.match(r[0].strip()):
            if r and isinstance(r[0], str) and (r[0].startswith("Source") or r[0].startswith("The Census") or r[0].startswith("(")):
                break
            if r and any(x not in (None, "") for x in r):
                break
            continue
        mon, yy, st = MONTH.match(r[0].strip()).groups()
        year = 1900 + int(yy) if int(yy) >= 90 else 2000 + int(yy)
        month = dt.datetime.strptime(mon, "%b").month
        ts = f"{year}-{month:02d}-01T00:00:00Z"
        if ts in seen:
            raise RuntimeError(f"{stem}: {ts} given twice")
        seen.add(ts)
        for j, c in cols:
            v = r[j] if j < len(r) else None
            if v in (None, ""):
                counts[f"{stem} blank"] = counts.get(f"{stem} blank", 0) + 1
                continue
            if not isinstance(v, (int, float)):
                raise RuntimeError(f"{stem} {r[0]} {c}: a figure that does not read: {v!r}")
            owner, typ = ents[j]
            out.append(dict(base, entity=f"census_c30:{owner}:{typ}", variable=var, ts_utc=ts, value=float(v) * 1e6, unit="USD", freq="P1M",
                            geo="US", market="", node=c, x_column=c, x_status=st))
    if not out:
        raise RuntimeError(f"{stem}: no figure")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Census Bureau C30: the value of construction put in place, a month, by type and owner")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        rows, counts, got = [], {}, []
        for stem, kind, var, title in FILES:
            content, rec = ip.fetch_raw(CONNECTOR, url_of(stem), log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
            base = dict(source=SOURCE, source_url=url_of(stem), retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            rows += parse(content, stem, kind, var, title, base, counts)
            got.append(base["retrieved_at"])
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"a key given twice: {s[s.duplicated(['entity', 'variable', 'ts_utc'])].head(3).to_dict('records')}")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): U.S. Census Bureau, Construction Spending (C30), the value of construction put in place by type and "
            f"owner, a month, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} (session 2258)",
            "Shape: series (docs/datastandard.md v0). entity census_c30:<owner>:<type> (private, public, state_local, federal); variable "
            "value_put_in_place (not seasonally adjusted) or value_put_in_place_saar (seasonally adjusted annual rate); unit USD (millions times "
            "1,000,000); freq P1M; ts_utc the month's first day; geo US; x_column the Census Bureau's column; x_status p preliminary, r revised.",
            f"Blank cells, no row: {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'} (the data center column begins in "
            "January 2014). Details may not add to totals (the Census Bureau's note). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/census_c30.py; the workbooks retrieved from {min(got)} to {max(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Census Bureau, Construction Spending, monthly time series (privsatime, privtime, pubsatime, pubtime), {PAGE}",
            "  access: https://www.census.gov/construction/c30/xlsx/<file>.xlsx",
            "License: public (a work of the U.S. government; see license_verdicts.csv). Source: U.S. Census Bureau, Construction Spending.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.entity.nunique()} series types, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Census Bureau", report="Construction Spending (C30), monthly time series by type",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
