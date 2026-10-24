#!/usr/bin/env python3
"""South Korea's electricity generation by source a year, and its peak and base demand a month, from the Korea Power
Exchange's Electric Power Statistics Information System (EPSIS) (session 2297, chain 105).

Energy Research Warehouse (ERW) connector. Two series tables from two of EPSIS's English pages, each of which carries its
whole table in the page's own script (the grid is filled from figures written into the page; other periods come only by
POST requests, which this connector does not send):

    https://epsis.kpx.or.kr/epsisnew/selectEkgeGepTotChart.do?menuId=060101&locale=eng   (Generation Output by Source, MWh)
    https://epsis.kpx.or.kr/epsisnew/selectEkgeEpsAepChart.do?menuId=030200&locale=eng   (Average Peak/Base Demand by Month, MW)

    kpx_korea_generation_annual   entity kpx:korea; variable generation_<column> (one a column of KPX's table, its
               groups' totals and the utilities' and the whole country's totals among them, x_group and x_label naming
               the column as KPX heads it); value in MWh as published; ts_utc the year's first day; freq P1Y; geo KR;
               the years ended before the retrieval only
    kpx_korea_demand_monthly   entity kpx:korea; variable peak_demand_daily_mean or base_demand_daily_mean (the mean of
               the month's daily peak, or base, demand: KPX's page names it "Average Peak/Base Demand by Month", and
               January to September 2026 equal the means of the daily page's figures to the megawatt, session 2297);
               value in MW as published; ts_utc the month's first day; freq P1M; geo KR; the months ended before the
               retrieval (Korea's time) only

A cell KPX leaves empty, "-" or "..." is no row; a subtotal more than 1 MWh a part from its parts is named in the header
(eight years of KPX's table, 1962 to 2016, at most 1.2% in 1963), and more than 5% stops the run. A month not ended is no
row, and a month KPX shows as 0 (not published; the base view itself shows a 0 as "-") is no row. An ended year KPX
publishes in part is no row, each named in the header: before 2005 the peak view holds one to seven months a year (one in
each of 1993 to 2001, a summer or winter month), and the base view begins in November 2025
(its first month 12,277 MW, a fifth of December's 57,565). The table runs from January 2005 (peak) and January 2026
(base). Nothing is filled.

    python warehouse/connectors/kpx_korea.py [--offline] [--out-dir DIR] [--table generation|demand]

Ceiling: two requests, each page asked again unless --offline. www.kpx.or.kr's robots file allows these paths;
epsis.kpx.or.kr has no robots file (its robots address answers with the application's page). data.go.kr's sets need a
key the ERW does not hold. License: internal until the licenses' round reads KPX's terms (EPSIS's pages carry "Copyright(C)
2020 Korea Power Exchange. All Right Reserved.").
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "kpx_korea"
SOURCE_GEN = "kpx:epsis_generation_by_source"
SOURCE_DEM = "kpx:epsis_peak_base_demand_monthly"
HOST = "epsis.kpx.or.kr"
GEN_URL = "https://epsis.kpx.or.kr/epsisnew/selectEkgeGepTotChart.do?menuId=060101&locale=eng"
DEM_URL = "https://epsis.kpx.or.kr/epsisnew/selectEkgeEpsAepChart.do?menuId=030200&locale=eng"
TABLE_GEN = "kpx_korea_generation_annual"
TABLE_DEM = "kpx_korea_demand_monthly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
KST = dt.timezone(dt.timedelta(hours=9))
# KPX's column: (variable, group, KPX's heading)
GEN_COLS = {
    "c1": ("generation_hydro_general", "Hydro", "General"),
    "c2": ("generation_hydro_pumped_storage", "Hydro", "Pumped-Storage"),
    "c3": ("generation_hydro_small", "Hydro", "Small hydro"),
    "c4": ("generation_hydro_total", "Hydro", "Total"),
    "c5": ("generation_steam_anthracite_coal", "Steam", "Anthracite coal"),
    "c6": ("generation_steam_bituminous_coal", "Steam", "Bituminous coal"),
    "c7": ("generation_steam_heavy_oil", "Steam", "Heavy oil"),
    "c8": ("generation_steam_lng", "Steam", "LNG"),
    "c9": ("generation_steam_total", "Steam", "Total"),
    "c10": ("generation_combined_cycle_general", "Combined cycle", "General"),
    "c11": ("generation_combined_cycle_heat_and_electric", "Combined cycle", "Heat & Electric"),
    "c24": ("generation_combined_cycle_lng", "Combined cycle", "LNG"),
    "c25": ("generation_combined_cycle_oil", "Combined cycle", "Oil"),
    "c12": ("generation_combined_cycle_total", "Combined cycle", "Total"),
    "c14": ("generation_nuclear", "", "Nuclear"),
    "c16": ("generation_new_and_renewable", "", "New & Renewable"),
    "c15": ("generation_group_energy", "", "Group Energy"),
    "c13": ("generation_internal_combustion", "", "Internal Combustion"),
    "c23": ("generation_others", "", "Others"),
    "c17": ("generation_utilities_total", "", "Total"),
    "c18": ("generation_non_utility_purchased_power", "Non-utility in common use", "Purchased power"),
    "c19": ("generation_non_utility_self_consumption", "Non-utility in common use", "Self consumption"),
    "c20": ("generation_non_utility_total", "Non-utility in common use", "Total"),
    "c21": ("generation_total_utilities_and_purchased", "Total generation", "Utilities + Purchased power"),
    "c22": ("generation_total_utilities_and_non_utility", "Total generation", "Utilities + Non-utility in common use"),
}
SUMS = {  # a subtotal and its parts, as KPX's table adds them
    "c4": ["c1", "c2", "c3"], "c9": ["c5", "c6", "c7", "c8"], "c12": ["c10", "c11", "c24", "c25"],
    "c17": ["c4", "c9", "c12", "c13", "c14", "c15", "c16", "c23"], "c20": ["c18", "c19"],
    "c21": ["c17", "c18"], "c22": ["c17", "c20"],
}
DEM_VARS = {"0": "peak_demand_daily_mean", "1": "base_demand_daily_mean"}
X_GEN = ["x_group", "x_label"]
X_DEM = ["x_kpx_view"]
YEAR_BLOCK = re.compile(r'if\("(\d{4})" >= beginDate && "\1" <= endDate\)\{(.*?)gridData\.push\(\{"Year":"\1"', re.S)
CELL = re.compile(r'(c\d+) = textFormmat\("([^"]*)",count\)')
DEM_CELL = re.compile(r'(c\d+) = (?:textFormmat\("([^"]*)",count\)|\("([^"]*)" == 0\))')  # the base view: ("60392.0" == 0) ? "-" : ...
STOP_SHARE = 0.05  # a subtotal this far from its parts stops the run (a column misread); a smaller difference is named


def figure(s):
    s = s.strip().replace(",", "")
    if s in ("", "-", "..."):
        return None
    return float(s)


def parse_generation(text, base, now):
    if "(Unit : MWh)" not in text:
        raise RuntimeError("the generation page does not print (Unit : MWh)")
    rows, seen, diffs = [], set(), []
    for m in YEAR_BLOCK.finditer(text):
        year = int(m.group(1))
        if year in seen:
            raise RuntimeError(f"the year {year} given twice")
        seen.add(year)
        if year >= now.year:
            continue  # a year not ended at the retrieval
        cells = {c: figure(v) for c, v in CELL.findall(m.group(2))}
        unknown = set(cells) - set(GEN_COLS)
        if unknown:
            raise RuntimeError(f"{year}: columns not known: {sorted(unknown)}")
        for tot, parts in SUMS.items():
            if cells.get(tot) is None:
                continue
            got = sum(cells.get(p) or 0.0 for p in parts)
            if abs(got - cells[tot]) > len(parts):  # KPX's rounding: 1 MWh a part
                if abs(got - cells[tot]) > STOP_SHARE * max(abs(cells[tot]), 1.0):
                    raise RuntimeError(f"{year}: {GEN_COLS[tot][0]} is {cells[tot]:,.3f} MWh, its parts sum to {got:,.3f}")
                diffs.append(f"{year} {GEN_COLS[tot][0]} {cells[tot] - got:+,.1f}")
        for c, v in cells.items():
            if v is None:
                continue
            var, group, label = GEN_COLS[c]
            rows.append(dict(base, entity="kpx:korea", variable=var, ts_utc=f"{year}-01-01T00:00:00Z", value=v, unit="MWh",
                             freq="P1Y", geo="KR", market="", node="", x_group=group, x_label=label))
    if not rows:
        raise RuntimeError("no year read from the generation page")
    return rows, diffs


def parse_demand(text, base, now):
    if "(Unit : MW)" not in text:
        raise RuntimeError("the demand page does not print (Unit : MW)")
    parts = re.split(r'if\(dataType == "(\d)"\) \{\s*(?=\s*if\("\d{4}" >= beginDate)', text)
    rows, short = [], []
    blocks = {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}
    if sorted(blocks) != ["0", "1"]:
        raise RuntimeError(f"the demand page's views are {sorted(blocks)}, not peak (0) and base (1)")
    for kind, block in blocks.items():
        block = block.split("} else", 1)[0] if kind == "0" else block
        years = re.findall(r'if\("(\d{4})" >= beginDate && "\1" <= endDate\)\{(.*?)gridData\.push\(\{"Year":"\1"', block, re.S)
        if not years:
            raise RuntimeError(f"no year in the {DEM_VARS[kind]} view")
        seen = set()
        for y, body in years:
            year = int(y)
            if year in seen:
                raise RuntimeError(f"{DEM_VARS[kind]}: the year {year} given twice")
            seen.add(year)
            cells = {c: figure(a or b) for c, a, b in DEM_CELL.findall(body)}
            months = []
            for mo in range(1, 13):
                v = cells.get(f"c{mo}")
                ended = dt.date(year + (mo == 12), mo % 12 + 1, 1) <= now.date()
                if not ended or not v:  # a month not ended, or one KPX did not publish (0; the base view shows it as "-")
                    continue
                months.append((mo, v))
            if year < now.year and len(months) < 12:
                # an ended year KPX publishes in part: before 2005 the peak view holds one to seven months a year, its
                # 1993 to 2001 figures one month each; the base view begins in November 2025
                if months:
                    short.append(f"{'peak' if kind == '0' else 'base'} {year} ({len(months)} month{'s' if len(months) > 1 else ''})")
                continue
            for mo, v in months:
                rows.append(dict(base, entity="kpx:korea", variable=DEM_VARS[kind], ts_utc=f"{year}-{mo:02d}-01T00:00:00Z", value=v,
                                 unit="MW", freq="P1M", geo="KR", market="", node="",
                                 x_kpx_view="peak" if kind == "0" else "base"))
    return rows, short


def main(argv=None):
    ap = argparse.ArgumentParser(description="KPX (EPSIS): South Korea's generation by source a year, and its peak and base demand a month")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--table", choices=["generation", "demand"], help="write one table only (both by default)")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results, sources = [], []
    jobs = [j for j in ("generation", "demand") if args.table in (None, j)]
    for job in jobs:
        table = TABLE_GEN if job == "generation" else TABLE_DEM
        try:
            if ip.paused(CONNECTOR) or ip.paused_host(HOST):
                raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
            url, source = (GEN_URL, SOURCE_GEN) if job == "generation" else (DEM_URL, SOURCE_DEM)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=3)
            got = rec.get("retrieved_at") or ""
            now = pd.Timestamp(got).tz_convert(KST) if got else dt.datetime.now(KST)
            base = dict(source=source, source_url=url, retrieved_at=got, vintage=ip.vintage_of(rec))
            text = content.decode("utf-8", errors="replace")
            common = [
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/kpx_korea.py; the page retrieved at {got}",
                f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            ]
            if job == "generation":
                rows, diffs = parse_generation(text, base, now)
                cols = ip.SERIES_COLS + X_GEN
                s = pd.DataFrame(rows)
                years = f"{s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}"
                head = [
                    f"Energy Research Warehouse (ERW): Korea Power Exchange (EPSIS), Generation Output by Source, South Korea, the years {years} (session 2297)",
                    "Shape: series (docs/datastandard.md v0). entity kpx:korea; variable generation_<KPX's column> (x_group and x_label name it "
                    "as KPX heads it); unit MWh as published; freq P1Y; ts_utc the year's first day; geo KR.",
                    "Every column of KPX's table, its subtotals among them (hydro, steam, combined cycle, the utilities' total, the non-utility "
                    "generators in common use, and the two national totals): a sum of rows double counts. The subtotals equal their parts to "
                    "KPX's rounding (1 MWh a part) except, in MWh, KPX's total less its parts: "
                    f"{'; '.join(diffs) or 'none'} (kept as published; over 5% would stop the run). A cell KPX leaves empty is no row; a 0 is "
                    "KPX's figure. The years ended before the retrieval only. Nothing is filled.",
                    *common,
                    f"Source: {SOURCE_GEN} Korea Power Exchange, Electric Power Statistics Information System (EPSIS), Generation Output by Source, {GEN_URL}",
                    "  access: the figures written into the page's script (other periods come only by POST, not sent)",
                    "License: internal until the licenses' round reads KPX's terms (the page: Copyright(C) 2020 Korea Power Exchange. All Right "
                    "Reserved.). Source: Korea Power Exchange.",
                ]
            else:
                rows, short = parse_demand(text, base, now)
                cols = ip.SERIES_COLS + X_DEM
                s = pd.DataFrame(rows)
                head = [
                    f"Energy Research Warehouse (ERW): Korea Power Exchange (EPSIS), Average Peak/Base Demand by Month, South Korea, "
                    f"{s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} (session 2297)",
                    "Shape: series (docs/datastandard.md v0). entity kpx:korea; variable peak_demand_daily_mean or base_demand_daily_mean (the "
                    "month's mean of the daily peak, or base, demand); unit MW as published; freq P1M; ts_utc the month's first day; geo KR; "
                    "x_kpx_view peak or base.",
                    "KPX's page names it Average Peak/Base Demand by Month; January to September 2026 equal the means of EPSIS's daily Peak/Base "
                    "Demand page to the megawatt (session 2297). The months ended before the retrieval (Korea's time) only; a month KPX "
                    "shows as 0 is not published, no row. An ended year KPX publishes in part is no row (before 2005 the peak view's months "
                    "are not a full year's means, its 1993 to 2001 figures one month a year; the base view begins in November 2025): "
                    f"{'; '.join(short) or 'none'}. Nothing is filled.",
                    *common,
                    f"Source: {SOURCE_DEM} Korea Power Exchange, Electric Power Statistics Information System (EPSIS), Average Peak/Base Demand by Month, {DEM_URL}",
                    "  access: the figures written into the page's script (other periods come only by POST, not sent)",
                    "License: internal until the licenses' round reads KPX's terms (the page: Copyright(C) 2020 Korea Power Exchange. All Right "
                    "Reserved.). Source: Korea Power Exchange.",
                ]
            if s.duplicated(["entity", "variable", "ts_utc"]).any():
                raise RuntimeError("a key given twice")
            s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
            ip.write_snapshot(s, table, head, log, cols)
            results.append(dict(table=table, market="all", status="ok", detail=f"{len(s)} rows"))
            sources.append(dict(source=source, publisher="Korea Power Exchange", report=head[0].split("(EPSIS), ")[1].split(", South Korea")[0],
                                report_url=url, document_list="https://epsis.kpx.or.kr/epsisnew/selectMain.do?locale=eng", license="internal", tables=[table]))
            print(f"{table}: {len(s):,} rows, {s.variable.nunique()} variables, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}")
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"{table} FAILED, no output file written:\n{tb}")
            print(f"{table} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=table, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if sources:
            ip.update_sources(sources)
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if results and all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
