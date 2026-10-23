#!/usr/bin/env python3
"""The Bonneville Power Administration's balancing authority: its load and its wind, solar, hydro, thermal and nuclear
generation and net interchange, BPA's five-minute values averaged to the hour (session 2148, chain 092: the Northwest's
federal grid, which the ERW held only as EIA-930's BPAT).

Energy Research Warehouse (ERW) connector. One series table from BPA's yearly workbooks of "Total Load, Wind Gen, Wind
Forecast, Solar Gen, Solar Forecast, Hydro, Thermal, and Net Interchange" (five-minute values), linked from

    https://transmission.bpa.gov/Business/Operations/Wind/default.aspx   (OPITabularReports/WindGenTotalLoadYTD_<year>.xls[x])

    bpa_ba_hourly   entity bpa:bpat; variables load, wind_generation, solar_generation (2022 on), hydro_generation,
               thermal_generation (BPA's fossil and biomass), nuclear_generation, net_interchange (positive an export, as
               BPA's net interchange); value the mean of the hour's five-minute values (MW, so equal to the hour's MWh);
               ts_utc the hour's start; freq PT1H; geo empty (the BA spans Oregon, Washington, Idaho and Montana); ba bpat;
               x_intervals how many five-minute values the hour holds (12 in a full hour); x_format new (2022 on, with
               BPA's UTC column) or old (2021 and before, Pacific local time)

Each sheet must hold a header row beginning "Date/Time" whose columns are named as read (BPA's names, matched by their
words); a column not found stops the run. The new format's times are BPA's UTC column; the old format's are Pacific
local time, put into UTC by their order across the clock changes (the repeated hour of November is the second time
through). A five-minute value that is empty has no part in its hour's mean; an hour with no value of a variable has no
row; a time given twice, or not five minutes after the one before (other than across the old format's clock changes),
stops the run. The forecasts (base schedule and basepoint) are not taken. Nothing is filled.

    python warehouse/connectors/bpa_ba.py [--offline] [--out-dir DIR] [--first YEAR]

Ceiling: one request for the page and one a year (2020 to this year by default), saved in warehouse/raw/bpa_ba/; the
page and this year's file are asked again unless --offline (they change), an earlier year's file is reused.
transmission.bpa.gov has no robots file (its /robots.txt is sent on to www.bpa.gov's site, whose robots file disallows
only /customerportal/). License: may be public (BPA, a power marketing administration of the Department of Energy,
whose notice is read 54); see license_verdicts.csv.
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

CONNECTOR = "bpa_ba"
SOURCE = "bpa:ba_load_generation"
HOST = "transmission.bpa.gov"
PAGE = "https://transmission.bpa.gov/Business/Operations/Wind/default.aspx"
TABLE = "bpa_ba_hourly"
FIRST = 2020
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_intervals", "x_format"]
# a column's words (upper case, spaces squeezed) -> variable; forecasts are not taken
WANTED = [("TOTAL BPA CONTROL AREA LOAD", "load"), ("TOTAL WIND GENERATION IN BPA CONTROL AREA", "wind_generation"),
          ("TOTAL SOLAR GENERATION IN BPA CONTROL AREA", "solar_generation"), ("TOTAL HYDRO GENERATION", "hydro_generation"),
          ("TOTAL FOSSIL/BIOMASS GENERATION", "thermal_generation"), ("TOTAL NUCLEAR GENERATION", "nuclear_generation"),
          ("NET INTERCHANGE", "net_interchange")]
NEW_ONLY = {"solar_generation"}


def squeeze(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().upper()


def year_links(page):
    out = {}
    for h in re.findall(r'href=["\']?([^"\' >]*WindGenTotalLoadYTD_(\d{4})\.xlsx?)', page, re.I):
        out[int(h[1])] = urllib.parse.urljoin(PAGE, h[0])
    if not out:
        raise RuntimeError("the page links no WindGenTotalLoadYTD workbook")
    return out


def columns(head, fmt):
    cols = {}
    for words, var in WANTED:
        hit = [j for j, c in enumerate(head) if squeeze(c).startswith(words) and "FORECAST" not in squeeze(c)]
        if len(hit) > 1:
            raise RuntimeError(f"two columns for {var}: {[head[j] for j in hit]}")
        if not hit:
            if var in NEW_ONLY and fmt == "old":
                continue
            raise RuntimeError(f"no column for {var} in {[str(c)[:40] for c in head]}")
        cols[var] = hit[0]
    return cols


def sheets(content, name):
    """Each sheet's rows as lists, from .xlsx (openpyxl, read only) or .xls (xlrd)."""
    if name.lower().endswith(".xlsx"):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        for ws in wb.worksheets:
            yield ws.title, (list(r) for r in ws.iter_rows(values_only=True))
    else:
        import xlrd
        wb = xlrd.open_workbook(file_contents=content)
        for sh in wb.sheets():
            yield sh.name, (sh.row_values(i) for i in range(sh.nrows))


def number(x):
    if x is None or (isinstance(x, str) and not x.strip()):
        return None
    if isinstance(x, bool):
        raise RuntimeError(f"not a number: {x!r}")
    try:
        return float(x)
    except (TypeError, ValueError):
        raise RuntimeError(f"not a number: {x!r}")


def read_year(content, name, year):
    """The year's five-minute rows: a frame of (utc, variable, value), and the format."""
    recs, fmt = [], None
    for title, rows in sheets(content, name):
        head = None
        for r in rows:
            if head is None:
                if r and str(r[0]).strip() == "Date/Time":
                    head = r
                    f = "new" if len(r) > 1 and str(r[1]).strip() == "Date/Time (UTC)" else "old"
                    if fmt and f != fmt:
                        raise RuntimeError(f"{name}: sheets of two formats")
                    fmt = f
                    cols = columns(head, fmt)
                continue
            if not r or r[0] is None or not str(r[0]).strip():
                continue
            t = str(r[1] if fmt == "new" else r[0]).strip()
            recs.append([t] + [number(r[j]) if j < len(r) else None for j in cols.values()])
        if head is None and title not in ("Details",):
            raise RuntimeError(f"{name} sheet {title!r}: no 'Date/Time' header row")
    if not recs:
        raise RuntimeError(f"{name}: no row")
    t = pd.DataFrame(recs, columns=["t"] + list(cols))
    stamp = pd.to_datetime(t.t, format="%m/%d/%y %H:%M")
    if fmt == "new":
        utc = stamp.dt.tz_localize("UTC")
    else:
        utc = stamp.dt.tz_localize("America/Los_Angeles", ambiguous="infer", nonexistent="raise").dt.tz_convert("UTC")
    t["utc"] = utc
    if t.utc.duplicated().any():
        raise RuntimeError(f"{name}: a time given twice: {t.utc[t.utc.duplicated()].iloc[0]}")
    step = t.utc.diff().dropna()
    bad = step[step != pd.Timedelta(minutes=5)]
    if len(bad):
        i = bad.index[0]
        raise RuntimeError(f"{name}: {t.t[i - 1]} to {t.t[i]} is not five minutes ({len(bad)} such steps)")
    if (t.utc.dt.tz_convert("America/Los_Angeles").dt.year != year).any() and fmt == "old":
        raise RuntimeError(f"{name}: a local time outside {year}")
    return t.drop(columns="t"), fmt


def hourly(t, fmt, base):
    long = t.melt(id_vars="utc", var_name="variable", value_name="value").dropna(subset=["value"])
    long["hour"] = long.utc.dt.floor("h")
    g = long.groupby(["variable", "hour"]).value.agg(["mean", "size"]).reset_index()
    out = pd.DataFrame(dict(entity="bpa:bpat", variable=g.variable, ts_utc=g.hour.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            value=g["mean"].round(3), unit="MW", freq="PT1H", geo="", market="", node="BPA balancing authority",
                            ba="bpat", x_intervals=g["size"].astype(int), x_format=fmt))
    for k, v in base.items():
        out[k] = v
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="BPA's balancing authority load and generation, five-minute values to the hour")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--first", type=int, default=FIRST, help=f"the first year (default {FIRST})")
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
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        links = year_links(page.decode("utf-8", errors="replace"))
        this_year = max(links)
        frames, fmts, latest, urls = [], {}, "", []
        for year in sorted(y for y in links if y >= args.first):
            url = links[year]
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=(year == this_year and not args.offline),
                                        headers=UA, timeout=300, pause=2)
            base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            t, fmt = read_year(content, url, year)
            h = hourly(t, fmt, base)
            log(f"  {year} ({fmt}): {len(t):,} five-minute rows, {len(h):,} hourly rows")
            frames.append(h)
            fmts[year] = fmt
            urls.append(url)
            latest = max(latest, base["retrieved_at"])
            del t
        s = pd.concat(frames, ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("an (entity, variable, ts_utc) given twice (an hour on both sides of a year's end)")
        cols = ip.SERIES_COLS + ["ba"] + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        short = int((s.x_intervals < 12).sum())
        head = [
            f"Energy Research Warehouse (ERW): Bonneville Power Administration, the BPA balancing authority's load and wind, solar, hydro, "
            f"thermal and nuclear generation and net interchange, five-minute values averaged to the hour, {s.ts_utc.min()[:10]} to "
            f"{s.ts_utc.max()[:10]} (session 2148)",
            "Shape: series (docs/datastandard.md v0). entity bpa:bpat; variables load, wind_generation, solar_generation (2022 on), "
            "hydro_generation, thermal_generation (BPA's fossil/biomass), nuclear_generation, net_interchange (positive an export); value the "
            "hour's mean of BPA's five-minute values (MW, the hour's MWh); freq PT1H; ts_utc the hour's start; ba bpat; x_intervals the "
            "five-minute values in the hour (12 when full); x_format new (BPA's UTC column, 2022 on) or old (Pacific local time, 2021 and "
            "before, put into UTC by order across the clock changes).",
            f"BPA's notes: the balancing authority's loads and resources, including some that are not BPA's; not BPA loads served by "
            f"transfer, scheduled out of region, or served in other BAs such as Seattle's and Tacoma's; five-minute interpolated snapshots. "
            f"{short:,} hourly rows hold fewer than 12 five-minute values (empty values, or the year's last hours). Forecasts not taken. "
            "Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/bpa_ba.py; the latest file retrieved {latest}; formats "
            + ", ".join(f"{y} {f}" for y, f in fmts.items()),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Bonneville Power Administration, Transmission Services, VER and Balancing Authority Monitoring, {PAGE}",
            f"  access: {urls[0].rsplit('/', 1)[0]}/WindGenTotalLoadYTD_<year>.xls[x], {min(fmts)} to {max(fmts)}",
            "License: may be public (BPA is a power marketing administration of the Department of Energy, whose notice puts government "
            "information on its websites in the public domain and asks that the Department be acknowledged; see license_verdicts.csv). "
            "Cite the Bonneville Power Administration.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.variable.nunique()} variables, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}; short hours {short:,}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Bonneville Power Administration (BPA)",
                                    report="VER and Balancing Authority Monitoring: Total Load, Wind, Solar, Hydro, Thermal and Net Interchange "
                                           "(five-minute, yearly workbooks)", report_url=PAGE, document_list=PAGE, license="public",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
