#!/usr/bin/env python3
"""EIA-411: peak load, net internal demand, capacity resources and capacity margins by NERC assessment area, summer and
winter, 1990 to 2016 actual and 2017 to 2027 projected (session 895, chain 049: the siting gaps' "Reserve margins: open").

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia411_capacity_margins_annual.csv, from
the U.S. Energy Information Administration's Form EIA-411 ("Coordinated Bulk Power Supply and Demand Program Report"),
the program's last release (November 2016), linked from https://www.eia.gov/electricity/data/eia411/ :

    xls/peak_load_2016.xls         Table 2: noncoincident peak load, summer and winter (MW)
    xls/summer_capacity_2016.xls   Table 4.A: summer net internal demand and capacity resources (MW), capacity margin (pct)
    xls/winter_capacity_2016.xls   Table 4.B: the same for winter

    entity    eia411:<assessment area> (frcc, npcc, mro, serc, spp, tre, wecc, the regions dissolved since (ecar, maac, main,
              mapp), rfc, pjm, miso, balance_of_eastern_region and contiguous_us as EIA gives them)
    variable  <season>_peak_load, <season>_net_internal_demand, <season>_capacity_resources (MW), <season>_capacity_margin
              (pct: unused capability at peak as a share of capacity resources); season summer or winter
    ts_utc    the peak period's first day as EIA defines it: summer 1 June of the year, winter 1 October of the season's
              first year (1990/1991 is 1990-10-01); freq P1Y; geo US; node the area and its interconnection
    x_projected  actual, or projected (EIA's "E" years)

Every block is found by its heading row ("Interconnection", "NERC Regional Assesment Area", the measure) and its years;
a measure or a year the map does not know stops the run. "NA" or an empty cell has no row; nothing is filled. EIA notes
that capacity margins before 2015 are its own rough calculation from the areas' figures and from 2015 NERC's, and that the
Balance of Eastern Region and the contiguous U.S. are computed by EIA, not precise; both kept as given.

    python warehouse/connectors/eia411.py [--offline]

Ceiling: three requests (the three files; saved in warehouse/raw/eia411/ and reused offline). EIA's robots file allows
/electricity/data/ (it disallows /archive/). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Form EIA-411").
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

NAME = "eia411_capacity_margins_annual"
CONNECTOR = "eia411"
SOURCE = "eia:eia411"
PAGE = "https://www.eia.gov/electricity/data/eia411/"
FILES = ["peak_load_2016.xls", "summer_capacity_2016.xls", "winter_capacity_2016.xls"]
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MEASURES = [("net internal demand", "net_internal_demand", "MW"), ("capacity resources", "capacity_resources", "MW"),
            ("capacity margin", "capacity_margin", "pct"), ("summer", "peak_load", "MW"), ("winter", "peak_load", "MW")]


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def slug(v):
    return re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_")


def blocks(frame, season_of_file):
    """[(variable, unit, season, {column: (first year, projected)}, [(row, area, interconnection)])] of one sheet."""
    out, r, n = [], 0, len(frame)
    while r < n:
        if text(frame.iloc[r, 0]) == "Interconnection" and text(frame.iloc[r, 1]).startswith("NERC Regional"):
            head = text(frame.iloc[r, 2]).lower()
            hit = next((m for m in MEASURES if head.startswith(m[0])), None)
            if not hit:
                raise RuntimeError(f"a measure not in the map: {text(frame.iloc[r, 2])!r}")
            season = hit[0] if hit[1] == "peak_load" else season_of_file
            # the years: the row after the Actual/Projected row, joined with the next where a season is split ("1990/", "1991")
            yr = r + 2
            years = {}
            for c in range(2, frame.shape[1]):
                a, b = text(frame.iloc[yr, c]), text(frame.iloc[yr + 1, c])
                lab = (a + b) if a.endswith("/") else a
                if not lab:
                    continue
                m = re.fullmatch(r"(\d{4})(?:\.0)?(?:\s*/\s*(\d{4}))?(E?)", lab.replace(" ", ""))
                if not m:
                    raise RuntimeError(f"a year not in the form read: {lab!r}")
                years[c] = (int(m.group(1)), m.group(3) == "E")
            first = yr + (2 if any(text(frame.iloc[yr, c]).endswith("/") for c in years) else 1)
            rows, inter, k = [], "", first
            while k < n and text(frame.iloc[k, 1]) and text(frame.iloc[k, 0]) != "Interconnection":
                if text(frame.iloc[k, 0]):
                    inter = text(frame.iloc[k, 0])
                rows.append((k, text(frame.iloc[k, 1]), inter))
                k += 1
            out.append((f"{season}_{hit[1]}", hit[2], season, years, rows))
            r = k
        else:
            r += 1
    return out


def sheet_rows(frame, season_of_file, url, retrieved):
    out = []
    for var, unit, season, years, rows in blocks(frame, season_of_file):
        for k, area, inter in rows:
            for c, (year, projected) in years.items():
                v = pd.to_numeric(frame.iloc[k, c], errors="coerce")
                if pd.isna(v):
                    continue
                ts = f"{year}-06-01T00:00:00Z" if season == "summer" else f"{year}-10-01T00:00:00Z"
                out.append(dict(entity=f"eia411:{slug(area)}", variable=var, ts_utc=ts, value=float(v), unit=unit, freq="P1Y",
                                geo="US", market="", node=f"{area} ({inter})", source=SOURCE, source_url=url,
                                retrieved_at=retrieved, vintage="", x_projected="projected" if projected else "actual"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA-411: peak load, capacity resources and margins by NERC assessment area")
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
        rows, got = [], []
        for f in FILES:
            url = PAGE + "xls/" + f
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=180)
            season = "winter" if f.startswith("winter") else "summer"
            frame = pd.read_excel(io.BytesIO(content), sheet_name="Sheet1", header=None)
            got_rows = sheet_rows(frame, season, url, rec.get("retrieved_at") or "")
            log(f"{f}: {len(got_rows):,} rows")
            rows += got_rows
            got.append(f"{url} (retrieved {rec.get('retrieved_at', '')})")
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"a key given twice: {s.loc[s.duplicated(['entity', 'variable', 'ts_utc']), ['entity', 'variable', 'ts_utc']].head(3).values.tolist()}")
        cols = ip.SERIES_COLS + ["x_projected"]
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        # session 895: a margin is checked against both definitions from the same row's resources and demand; EIA's
        # heading names the capacity margin, but some areas' projections NERC sent are reserve margins. Named, not mended
        as_reserve = []
        for season in ("summer", "winter"):
            w = s[s["variable"].str.startswith(season)].pivot_table(index=["entity", "ts_utc"], columns="variable", values="value")
            if {f"{season}_capacity_resources", f"{season}_net_internal_demand", f"{season}_capacity_margin"} <= set(w.columns):
                cr, nid, cm = w[f"{season}_capacity_resources"], w[f"{season}_net_internal_demand"], w[f"{season}_capacity_margin"]
                hit = (((cr - nid) / nid * 100 - cm).abs() < 0.2) & (((cr - nid) / cr * 100 - cm).abs() >= 0.2)
                for (e, ts) in w.index[hit]:
                    as_reserve.append((season, e.split(":")[1], int(ts[:4])))
        reserve_text = ""
        if as_reserve:
            r = pd.DataFrame(as_reserve, columns=["season", "area", "year"])
            parts = [f"{a} {g.year.min()} to {g.year.max()}" for a, g in r.groupby("area")]
            reserve_text = (f" {len(r)} margins (both seasons) equal resources less demand over demand, a reserve margin, not over resources: "
                            f"{', '.join(parts)}; kept as EIA gives them.")
        header = [
            "Energy Research Warehouse (ERW): EIA-411, peak load, net internal demand, capacity resources and capacity margins by NERC assessment area, summer and winter (session 895)",
            "Shape: series (docs/datastandard.md v0). entity eia411:<assessment area as EIA names it>; variable <season>_peak_load, <season>_net_internal_demand, "
            "<season>_capacity_resources (MW) and <season>_capacity_margin (pct of capacity resources), season summer or winter; ts_utc the peak period's first "
            "day (summer 1 June; winter 1 October of the season's first year, EIA's winter running October to May); freq P1Y; geo US; x_projected actual or projected (EIA's E years).",
            f"The program's last release (November 2016): actual to 2016 and projected to 2027; {s['entity'].nunique()} areas, {len(s):,} rows. Areas change over time "
            "(ECAR, MAAC and MAIN dissolved at the end of 2005 into RFC; MAPP absorbed into MISO, SPP and WECC in 2015); EIA's Balance of Eastern Region gives a "
            "consistent eastern trend. Capacity margins before 2015 are EIA's rough calculation, from 2015 NERC's." + reserve_text + " NA or empty has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia411.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Form EIA-411, Coordinated Bulk Power Supply and Demand Program Report, {PAGE}",
            f"  access: {'; '.join(got)}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-411").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Form EIA-411, Coordinated Bulk Power Supply and Demand Program Report", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique()} areas")
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
