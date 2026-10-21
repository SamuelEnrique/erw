#!/usr/bin/env python3
"""EIA's Short-Term Energy Outlook: retail electricity prices, Henry Hub and the generation mix, monthly, each release
kept (session 491).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_steo_forecasts.csv, from the U.S.
Energy Information Administration's API v2, route steo (the current release only; the API keeps no earlier one):

    https://api.eia.gov/v2/steo/data/?frequency=monthly&data[]=value&facets[seriesId][]=<id>...&start=<year>-01
    the release's date from https://www.eia.gov/outlooks/steo/ ("Release Date: <Month> <day>, <year>")

    entity    eia_steo:<seriesId>; variable value; node the series' name; ts_utc the month's first day; freq P1M
    vintage   the release's date (ISO): each release is kept, merged on (entity, variable, ts_utc, vintage), as
              docs/datastandard.md rule 5 allows when a table says so; this table says so
    x_kind    forecast (a month from the release's month on) or history (EIA's own figure for an earlier month)
    series    ESRCU, ESCMU, ESICU, ESTCU (residential, commercial, industrial, all-sector retail electricity price) for the
              U.S. and every census division; NGHHUUS (Henry Hub spot); the U.S. generation shares (*EPSHR_US)

Units into the standard's vocabulary: cents per kWh as USD/kWh (times 0.01, nominal dollars, as the STEO gives them);
dollars per MMBtu as USD/MMBtu; a share as a ratio (a percent divided by 100 when EIA gives percent). A unit not in the
map stops the run. Forecasts are EIA's: nothing is filled or interpolated.

    python warehouse/connectors/eia_steo.py                 # from January 2020

Ceiling: 20 requests a run (the series list, the page, the data in pages of 5,000; 3 seconds apart; a 429 or a 5xx asked
once more after 60 seconds). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Short-Term Energy Outlook, <release>").
"""

import argparse
import datetime as dt
import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_steo_forecasts"
CONNECTOR = "eia_steo"
SOURCE = "eia:steo"
API = "https://api.eia.gov/v2/steo/"
PAGE = "https://www.eia.gov/outlooks/steo/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CEILING, PAUSE, RETRY_WAIT = 20, 3, 60
FIRST = "2020-01"
PRICE = re.compile(r"^ES(RC|CM|IC|TC)U_[A-Z]{2,3}$")
SHARE = re.compile(r"^[A-Z]{2}EPSHR_US$")
OTHER = {"NGHHUUS"}
UNITS = {"cents per kilowatthour": ("USD/kWh", 0.01), "cents per kilowatt hour": ("USD/kWh", 0.01), "cents/kwh": ("USD/kWh", 0.01), "dollars per million btu": ("USD/MMBtu", 1.0),
         "$/mmbtu": ("USD/MMBtu", 1.0), "fraction": ("ratio", 1.0), "percent": ("ratio", 0.01), "percentage": ("ratio", 0.01), "%": ("ratio", 0.01)}
KEY = ["entity", "variable", "ts_utc", "vintage"]
X_COLS = ["x_kind", "x_units_published"]


def wanted(series_ids):
    return sorted(s for s in series_ids if PRICE.match(s) or SHARE.match(s) or s in OTHER)


def release_date(page_html):
    m = re.search(r"Release Date:\s*([A-Z][a-z]+ \d{1,2}, \d{4})", re.sub(r"<[^>]+>", " ", page_html))
    if not m:
        raise RuntimeError("the STEO page names no release date")
    return dt.datetime.strptime(m.group(1), "%B %d, %Y").date()


def unit_of(u):
    k = str(u).strip().lower()
    if k not in UNITS:
        raise RuntimeError(f"a unit not in the map: {u!r}")
    return UNITS[k]


def rows(data, release, url, retrieved):
    first_forecast = f"{release.year}-{release.month:02d}"
    out = []
    for r in data:
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        unit, factor = unit_of(r.get("unit", ""))
        out.append(dict(entity=f"eia_steo:{r['seriesId']}", variable="value", ts_utc=f"{r['period']}-01T00:00:00Z", value=float(v) * factor,
                        unit=unit, freq="P1M", geo="US", market="", node=r.get("seriesDescription", r.get("seriesName", "")), source=SOURCE,
                        source_url=url, retrieved_at=retrieved, vintage=f"{release.isoformat()}T00:00:00Z",
                        x_kind="forecast" if r["period"] >= first_forecast else "history", x_units_published=r.get("unit", "")))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(KEY).any():
        raise RuntimeError("an (entity, variable, ts_utc, vintage) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA Short-Term Energy Outlook: electricity prices, Henry Hub, generation shares")
    ap.add_argument("--start", default=FIRST, help="the first month, YYYY-MM")
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
    asked = [0]

    def get(url, params=None, headers=None):
        for attempt in (1, 2):
            if asked[0] >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached")
            asked[0] += 1
            time.sleep(PAUSE)
            r = requests.get(url, params=params, headers=headers, timeout=120)
            if r.status_code < 500 and r.status_code != 429:
                r.raise_for_status()
                return r
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        series = wanted(f["id"] for f in get(API + "facet/seriesId/", dict(api_key=key)).json()["response"]["facets"])
        release = release_date(get(PAGE, headers=UA).text)
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frames, offset = [], 0
        while True:
            r = get(API + "data/", {"api_key": key, "frequency": "monthly", "data[]": "value", "facets[seriesId][]": series,
                                    "start": args.start, "length": 5000, "offset": offset})
            resp = r.json()["response"]
            frames.append(rows(resp["data"], release, ip.redact(r.url.split("&offset")[0]), retrieved))
            offset += len(resp["data"])
            if offset >= int(resp["total"]) or not resp["data"]:
                break
        s = pd.concat(frames, ignore_index=True)
        if s.duplicated(KEY).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS + X_COLS]
        header = [
            f"Energy Research Warehouse (ERW): EIA Short-Term Energy Outlook of {release.isoformat()}, retail electricity prices, Henry Hub and the generation mix, monthly (session 491)",
            "Shape: series (docs/datastandard.md v0), each release kept: the key is (entity, variable, ts_utc, vintage), vintage the release's date (docs/datastandard.md rule 5). entity eia_steo:<seriesId>; variable value; ts_utc the month's first day; freq P1M; x_kind forecast or history.",
            f"FORECASTS from {release.year}-{release.month:02d} on, EIA's; earlier months are EIA's history. Units: cents/kWh as USD/kWh (nominal), USD/MMBtu, shares as ratios. Series {len(series)}; months from {args.start}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_steo.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Short-Term Energy Outlook (API v2, route steo), {PAGE}",
            f"  access: {API}data/?frequency=monthly&data[]=value&facets[seriesId][]=<id>&start={args.start}",
            f'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Short-Term Energy Outlook, {release:%B %Y}").',
        ]
        ip.write_csv(s, NAME, header, log, cols=ip.SERIES_COLS + X_COLS, key=KEY)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Short-Term Energy Outlook (API v2)", report_url=PAGE, document_list=API, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"STEO {release}: {len(s):,} rows"))
        print(f"{NAME}: STEO of {release}, {len(s):,} rows, {s['entity'].nunique()} series, forecast from {release.year}-{release.month:02d}; {asked[0]} requests")
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
