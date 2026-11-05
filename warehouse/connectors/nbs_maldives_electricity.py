#!/usr/bin/env python3
"""The Maldives' electricity: the public sector's production by island a month (2025), and the electricity used in Male'
by sector a year (2009 to 2025), as the Maldives Bureau of Statistics (NBS) gives them in tables 12.2 and 12.1 of its
Statistical Yearbook 2026, both from the State Electric Company Limited (STELCO) (session 2562, chain 126; the ERW held
the Maldives only in EIA's international table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nbs_maldives_electricity.csv, from two
workbooks (no key):

    https://statisticsmaldives.gov.mv/yearbook/2026/wp-content/uploads/sites/13/2026/06/12.2.xlsx
    https://statisticsmaldives.gov.mv/yearbook/2026/wp-content/uploads/sites/13/2026/06/12.1.xlsx

    entity      nbs_mv:<island> (table 12.2: k_male, k_hulhumale, aa_ukulhas, ...; the label in lower case, each run of
                other characters an underscore); nbs_mv:male:<sector> (table 12.1: total, residential,
                manufacturing_commercial, government_buildings, public_places_schools)
    variable    production (12.2, freq P1M); utilization (12.1, freq P1Y)
    unit        MWh; ts_utc the month's or the year's first day; geo MV
    node        NBS's label

Table 12.2's heading says "In '000 kWh" but its cells are kWh: K.Male' would otherwise have made 324 TWh in 2025, and
the Greater Male' islands' production is checked to fall between one and three times Male's use in table 12.1 (in
'000 kWh, its total row says so) for the same year, so a workbook corrected to thousands stops the run rather than
writing figures a thousand times too small. 12.2's cells are divided by 1,000, 12.1's taken as they are. The "Total"
column of 12.2 is not written; each island's months are checked against it, and 12.1's four sectors against its total
(within 1 MWh). The percentage rows of 12.1 and its Dhivehi labels are not taken.

The run stops on a sheet whose title or header row is not found, a row of 12.1 missing or given twice, an island given
twice, a cell that is not a number, or a check missed. Nothing is filled.

    python warehouse/connectors/nbs_maldives_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: two requests a run, saved in warehouse/raw/nbs_mv/ and reused unless --fresh; --offline asks nothing.
statisticsmaldives.gov.mv's robots file closes /mbs/wp-admin/ only (session 2562). License: internal. NBS's pages state
no terms of reuse, and the Maldives Statistics Act (Act 16/2021, its English translation) grants none; internal until a
ruling.
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

NAME = "nbs_maldives_electricity"
CONNECTOR = "nbs_mv"
HOST = "statisticsmaldives.gov.mv"
BASE_URL = "https://statisticsmaldives.gov.mv/yearbook/2026/wp-content/uploads/sites/13/2026/06/"
URL_PROD = BASE_URL + "12.2.xlsx"
URL_USE = BASE_URL + "12.1.xlsx"
SOURCE_PROD = "nbs_mv:yearbook_2026_table_12_2"
SOURCE_USE = "nbs_mv:yearbook_2026_table_12_1"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Maldives Bureau of Statistics (NBS), Statistical Yearbook of Maldives 2026, tables 12.1 and 12.2 (source: State Electric Company Limited)"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
GREATER_MALE = ("k_male", "k_vilimale", "k_hulhumale")
# 12.1: a label's start and its sector; every one must be found once, in the block before the shares
SECTORS = [("Total", "total"), ("Residential", "residential"), ("Manufacturing and", "manufacturing_commercial"),
           ("Government Buildings", "government_buildings"), ("Public Places and", "public_places_schools")]
X_COLS = ["x_table"]


def num(v, where):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise RuntimeError(f"{where}: not a number: {v!r}")
    return float(v)


def slug(label):
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def rows_of(content):
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    if len(wb.worksheets) != 1:
        raise RuntimeError(f"{len(wb.worksheets)} sheets, one expected")
    return [list(r) for r in wb.worksheets[0].iter_rows(values_only=True)]


def label(v):
    return " ".join(str(v).split()) if v is not None else ""


def parse_production(rows, base):
    """Table 12.2: kWh a month by island; returns the rows (MWh) and each island's year (MWh)."""
    title = [label(r[0]) for r in rows if label(r[0]).startswith("Table")]
    m = re.fullmatch(r"Table 12\.2 : MONTHLY ELECTRICITY PRODUCTION BY PUBLIC SECTOR, (\d{4})", title[0]) if len(title) == 1 else None
    if not m:
        raise RuntimeError(f"12.2: the title not found ({title})")
    year = m.group(1)
    head = [i for i, r in enumerate(rows) if [label(v) for v in r[1:14]] == ["Total"] + MONTHS]
    if len(head) != 1:
        raise RuntimeError(f"12.2: the header row not found ({head})")
    out, years, seen = [], {}, set()
    for r in rows[head[0] + 1:]:
        name = label(r[0])
        if name.startswith("Source") or not name:
            break
        if all(v is None for v in r[1:14]):
            continue  # a region's heading
        item = slug(name)
        if item in seen:
            raise RuntimeError(f"12.2: {name!r} given twice")
        seen.add(item)
        total = num(r[1], f"12.2 {name} total")
        vals = [num(v, f"12.2 {name} {mo}") for v, mo in zip(r[2:14], MONTHS)]
        if abs(sum(vals) - total) > 1000:
            raise RuntimeError(f"12.2 {name}: the months make {sum(vals)}, the total {total}")
        years[item] = total / 1000
        for i, v in enumerate(vals):
            out.append(dict(entity=f"nbs_mv:{item}", variable="production", ts_utc=f"{year}-{i + 1:02d}-01T00:00:00Z",
                            value=round(v / 1000, 3), unit="MWh", freq="P1M", geo="MV", market="", node=name,
                            source=SOURCE_PROD, source_url=URL_PROD, **base["prod"], x_table="12.2"))
    if not out or any(g not in years for g in GREATER_MALE):
        raise RuntimeError(f"12.2: the Greater Male' islands not all found ({sorted(years)[:5]})")
    return out, years, year


def parse_use(rows, base):
    """Table 12.1: '000 kWh (MWh) a year by sector, Male'."""
    title = [label(r[0]) for r in rows if label(r[0]).startswith("Table")]
    if len(title) != 1 or not title[0].startswith("Table 12.1 : ELECTRICITY UTILIZATION IN MALE'"):
        raise RuntimeError(f"12.1: the title not found ({title})")
    head = [i for i, r in enumerate(rows) if label(r[0]) == "Load Distribution"]
    if len(head) != 1:
        raise RuntimeError(f"12.1: the header row not found ({head})")
    cols = [(j, int(v)) for j, v in enumerate(rows[head[0]]) if isinstance(v, int) and 1990 <= v <= 2100]
    if not cols or [y for _, y in cols] != list(range(cols[0][1], cols[-1][1] + 1)):
        raise RuntimeError(f"12.1: the years are not a run ({[y for _, y in cols]})")
    got, vals, out = {}, {}, []
    for r in rows[head[0] + 1:]:
        name = label(r[0])
        if name.startswith("%"):
            break  # the shares and the changes follow
        hit = [s for s in SECTORS if name.startswith(s[0])]
        if len(hit) != 1:
            raise RuntimeError(f"12.1: {name!r} matches {len(hit)} rows of the map")
        start, item = hit[0]
        if start in got:
            raise RuntimeError(f"12.1: {name!r} given twice")
        if item == "total" and "000 kWh" not in name:
            raise RuntimeError(f"12.1: the total row's unit is not '000 kWh: {name!r}")
        got[start] = name
        for j, y in cols:
            v = num(r[j], f"12.1 {name} {y}")
            vals[(item, y)] = v
            out.append(dict(entity=f"nbs_mv:male:{item}", variable="utilization", ts_utc=f"{y}-01-01T00:00:00Z", value=round(v, 3),
                            unit="MWh", freq="P1Y", geo="MV", market="", node=name, source=SOURCE_USE, source_url=URL_USE,
                            **base["use"], x_table="12.1"))
    missing = [s[0] for s in SECTORS if s[0] not in got]
    if missing:
        raise RuntimeError(f"12.1: rows missing: {missing}")
    for _, y in cols:
        s = sum(vals[(i, y)] for _, i in SECTORS[1:])
        if abs(s - vals[("total", y)]) > 1:
            raise RuntimeError(f"12.1 {y}: the sectors make {s}, the total {vals[('total', y)]}")
    return out, {y: vals[("total", y)] for _, y in cols}


def parse(prod_rows, use_rows, base):
    prod, years, year = parse_production(prod_rows, base)
    use, totals = parse_use(use_rows, base)
    if int(year) not in totals:
        raise RuntimeError(f"12.1 has no {year} to check 12.2's unit against")
    ratio = sum(years[g] for g in GREATER_MALE) / totals[int(year)]
    if not 1 <= ratio <= 3:
        raise RuntimeError(f"12.2's unit: the Greater Male' islands made {ratio:.3f} times Male's use in {year}, not 1 to 3")
    return pd.DataFrame(prod + use)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NBS: the Maldives' electricity production by island and Male's use by sector")
    ap.add_argument("--offline", action="store_true", help="the saved workbooks only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the workbooks again")
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
        base, rows = {}, {}
        for key, url in (("prod", URL_PROD), ("use", URL_USE)):
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
            base[key] = dict(retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            rows[key] = rows_of(content)
        t = parse(rows["prod"], rows["use"], base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        p = t[t.variable == "production"]
        u = t[(t.entity == "nbs_mv:male:total")]
        head = [
            "Energy Research Warehouse (ERW): Maldives Bureau of Statistics (NBS), Statistical Yearbook 2026, table 12.2 (the public "
            "sector's production by island a month) and table 12.1 (electricity used in Male' by sector a year), from STELCO (session 2562)",
            "Shape: series (docs/datastandard.md v0). entity nbs_mv:<island> (12.2) or nbs_mv:male:<sector> (12.1); variable production "
            "(P1M) or utilization (P1Y); unit MWh; ts_utc the month's or year's first day; geo MV; node NBS's label; x_table the table.",
            f"{len(t)} rows; {p.entity.nunique()} islands made {p.value.sum() / 1e3:,.1f} GWh in {p.ts_utc.str[:4].max()}; Male' used "
            f"{u.value.iloc[-1] / 1e3:,.1f} GWh in {u.ts_utc.str[:4].max()}. Table 12.2's heading says '000 kWh but its cells are kWh "
            "(checked against table 12.1), divided by 1,000; its Total column and 12.1's percentages are not taken; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nbs_maldives_electricity.py; table 12.2 retrieved {base['prod']['retrieved_at']} "
            f"(last modified {base['prod']['vintage']}), table 12.1 retrieved {base['use']['retrieved_at']} (last modified {base['use']['vintage']})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE_PROD} and {SOURCE_USE} {CITATION}",
            f"  access: {URL_PROD} and {URL_USE}",
            "License: internal. NBS's pages state no terms of reuse and the Maldives Statistics Act grants none; internal until a "
            f"ruling. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=s, publisher="Maldives Bureau of Statistics (NBS)", report=r, report_url=u,
                                    document_list="https://statisticsmaldives.gov.mv/yearbook/2026/", license="internal", tables=[NAME])
                               for s, r, u in ((SOURCE_PROD, "Statistical Yearbook 2026, table 12.2: monthly electricity production by public sector", URL_PROD),
                                               (SOURCE_USE, "Statistical Yearbook 2026, table 12.1: electricity utilization in Male'", URL_USE))])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
