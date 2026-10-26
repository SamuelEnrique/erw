#!/usr/bin/env python3
"""Eurostat's recharging points for electric vehicles by power category (road_if_rchevpow): each European country's public
recharging points a year by current (AC, DC) and power band, from 2019 (session 2813, chain 143, the session's own choice,
beside eurostat_ev_recharging_annual, session 2804, which holds the points' total with the stations and pools).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_ev_recharging_power_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), one request (about 90 KB of SDMX-CSV, the whole dataset):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_if_rchevpow?format=SDMX-CSV&compressed=false

    entity      eurostat_ev_power:<Eurostat geo code>:<the POWER code> (TOTAL, AC, DC and the bands below)
    variable    recharging_points; unit count (Eurostat's NR)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR)
    node        "<geo code> recharging points, <the band>"
    x_*         Eurostat's geo and power codes, the observation's flag (i: see Eurostat's metadata) and confidentiality status

The bands' names are the POWER codelist's (session 2813 read it, read 1624), written here in ASCII: AC below 7.4 kW (slow,
single-phase), 7.4 to 22 kW (medium-speed, three-phase), above 22 kW (fast, three-phase); DC below 50 kW (slow), 50 to 150 kW
(fast), 150 to 350 kW (ultra-fast, level 1), 350 kW and above (ultra-fast, level 2). Compared in every country year that gives
them: the total against AC plus DC, and AC and DC against their bands; a case that does not hold is counted in the header and
listed in the run log, kept as published. A blank has no row; zeros are kept; nothing is filled. Checks that stop the run: a
header not Eurostat's; a frequency, unit or power code not expected; a value not a number, or negative; a period not a year; a
key given twice. Countries kept: the EU's members, EFTA's and the official candidates, as eurostat_ev_recharging_annual keeps
them (the United Kingdom left out, named in the header).

    python warehouse/connectors/eurostat_ev_recharging_power.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/eurostat_ev_recharging_power/ with --offline. ec.europa.eu's robots file
disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2813,
read again, the same file as session 2812's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse
with the source acknowledged; source: Eurostat.
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

NAME = "eurostat_ev_recharging_power_annual"
CONNECTOR = "eurostat_ev_recharging_power"
SOURCE = "eurostat:road_if_rchevpow"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/road_if_rchevpow/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/road_if_rchevpow?format=SDMX-CSV&compressed=false"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "power", "geo", "unit", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
BANDS = {"TOTAL": "total", "AC": "alternating current", "DC": "direct current",
         "AC_KW_LT7P4": "AC below 7.4 kW (slow, single-phase)",
         "AC_KW_LE7P4-LE22": "AC 7.4 to 22 kW (medium-speed, three-phase)",
         "AC_KW_GT22": "AC above 22 kW (fast, three-phase)",
         "DC_KW_LT50": "DC below 50 kW (slow)",
         "DC_KW_LE50-LT150": "DC 50 to 150 kW (fast)",
         "DC_KW_LE150-LT350": "DC 150 to 350 kW (ultra-fast, level 1)",
         "DC_KW_GE350": "DC 350 kW and above (ultra-fast, level 2)"}
AC_BANDS = ["AC_KW_LT7P4", "AC_KW_LE7P4-LE22", "AC_KW_GT22"]
DC_BANDS = ["DC_KW_LT50", "DC_KW_LE50-LT150", "DC_KW_LE150-LT350", "DC_KW_GE350"]
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_power", "x_flag", "x_conf_status"]


def build(content, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.freq) - {"A"}) + sorted(set(t0.unit) - {"NR"}) + sorted(set(t0.power) - set(BANDS))
    if bad:
        raise RuntimeError(f"a frequency, unit or power code not expected: {bad}")
    counts = {"zero": 0, "blank": 0, "left_out_geo": sorted(set(t0.geo) - KEPT),
              "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        if v == "":
            counts["blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.power} {r.TIME_PERIOD}: not a number: {v!r}")
        if value < 0:
            raise RuntimeError(f"{r.geo} {r.power} {r.TIME_PERIOD}: a negative value: {v!r}")
        if value == 0:
            counts["zero"] += 1
        rows.append({"entity": f"eurostat_ev_power:{r.geo}:{r.power}", "variable": "recharging_points",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": value, "unit": "count", "freq": "P1Y",
                     "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo), "market": "",
                     "node": f"{r.geo} recharging points, {BANDS[r.power]}", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_power": r.power,
                     "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def checks(t):
    """The total against AC plus DC, AC and DC against their bands: {check: (compared, those off)}."""
    p = t.pivot_table(index=["x_geo_code", "ts_utc"], columns="x_power", values="value", aggfunc="first")
    out = {}
    for name, whole, parts in (("total", "TOTAL", ["AC", "DC"]), ("ac", "AC", AC_BANDS), ("dc", "DC", DC_BANDS)):
        if whole not in p.columns or any(k not in p.columns for k in parts):
            out[name] = (0, [])
            continue
        x = p[[whole] + parts].dropna()
        d = x[parts].sum(axis=1) - x[whole]
        out[name] = (len(x), [(g, ts[:4], float(e)) for (g, ts), e in d[d != 0].items()])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat road_if_rchevpow: European EV recharging points by power, a year")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        if not args.offline and (ip.paused("eurostat") or ip.paused_host("ec.europa.eu")):
            raise RuntimeError("Eurostat is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180)
        t, counts = build(content, URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        if t.empty:
            raise RuntimeError("no observation kept")
        ck = checks(t)
        for k, (_, off) in ck.items():
            for x in off:
                log(f"  {k}: the parts less the whole {x[2]:+.0f}, kept as published: {x[0]} {x[1]}")
        said = "; ".join(f"{k} {n - len(o)} of {n}" for k, (n, o) in ck.items())
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, recharging points for electric vehicles by power category, annual (road_if_rchevpow), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2813)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_ev_power:<geo>:<POWER code> (TOTAL, AC, DC, AC_KW_LT7P4 below 7.4 kW, AC_KW_LE7P4-LE22 7.4 to 22 kW, AC_KW_GT22 above 22 kW, DC_KW_LT50 below 50 kW, DC_KW_LE50-LT150 50 to 150 kW, DC_KW_LE150-LT350 150 to 350 kW, DC_KW_GE350 350 kW and above); "
            "variable recharging_points; unit count; ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR); x_power Eurostat's code.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas. The parts against their whole, exactly, in every country year that gives them: {said}; the others kept as published and listed in the run log. Zeros are kept ({counts['zero']}); {counts['blank']} blanks have no row; nothing is filled. "
            f"{int((t.x_flag == 'i').sum())} observations carry Eurostat's flag i, kept in x_flag. Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_ev_recharging_power.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Recharging points for electric vehicles by power category (road_if_rchevpow), {PAGE}",
            f"  access: {URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, road_if_rchevpow. Eurostat bears no responsibility for this reshaping.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Recharging points for electric vehicles by power category (road_if_rchevpow)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; {said}; zeros {counts['zero']}, blanks {counts['blank']}; left out {counts['left_out_geo']}")
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
