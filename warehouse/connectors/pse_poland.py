#!/usr/bin/env python3
"""Poland's power balance a quarter hour, from PSE, Poland's transmission system operator: demand, generation by kind
of unit, wind and solar, and the cross-border exchange balance (session 2252, chain 102: Poland's grid, the largest
coal-fired system of the European Union, beside the ERW's U.S. grids).

Energy Research Warehouse (ERW) connector. One series table from PSE's reports API (Data API builder, OData filters),
its report his-wlk-cal ("Wielkosci podstawowe", the basic quantities), one request a calendar year of business days:

    https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date ge '<year>-01-01' and business_date le '<year>-12-31'&$first=40000

    pse_poland_balance_15min   entity pse:pl; variable as PSE labels each field in its reports app (English labels):
               demand (KSE power demand), generation_scheduled_total (jg: the generation of the scheduled units, JGw, JGm,
               JGz and JGa), generation_jgw1 and generation_jgw2 (scheduled generating units, ZAK 1 and 2),
               generation_jgm1 and generation_jgm2 (scheduled energy storage units, ZAK 1 and 2), charging_jgm (the storage
               units' charging power), generation_jgz2 (scheduled wind and photovoltaic units, ZAK 2), generation_jnwrb
               (units not actively participating in the balancing market), generation_jga (the scheduled generator
               units JGa; one quarter hour of 2024 only), wind, solar, exchange_parallel and
               exchange_non_parallel (the domestic balance of cross-border exchange, parallel and non-parallel); value in
               MW, the quarter hour's power as PSE gives it; ts_utc the quarter hour's start (PSE's period in UTC); freq
               PT15M; geo PL; x_field PSE's field name; x_business_date PSE's business day (Polish local time)

PSE's fields jgo, jgz1 and jgz3 hold no figure in any year read and are not taken. A blank figure has no row;
the business day in progress at retrieval (whose later quarter hours PSE lists empty) is not taken (chain 098's ended
days). The quarter hours are keyed by PSE's UTC period: the local day of the spring change has 92 and the autumn one
100, and PSE's local stamps repeat (02a) where the clock goes back. A field not in the map, a UTC period given twice, or
an answer that fills its page (40,000 rows) stops the run. Nothing is filled. The report starts on business day
13 June 2024 (one quarter hour, 21:45 UTC); prices are not taken (PLN).

    python warehouse/connectors/pse_poland.py [--offline] [--out-dir DIR]

Ceiling: one request a year from 2024 (three in 2026), each asked again unless --offline, since PSE republishes its
figures (its publication stamps run to January 2026 for 2024's). api.raporty.pse.pl has no robots file (HTTP 404, its
app's page); www.pse.pl's disallows only a careers path. License: internal until the licenses' round reads PSE's terms.
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback
import urllib.parse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "pse_poland"
SOURCE = "pse:his-wlk-cal"
HOST = "api.raporty.pse.pl"
PAGE = "https://raporty.pse.pl/report/his-wlk-cal"
TABLE = "pse_poland_balance_15min"
FIRST_YEAR = 2024
PAGE_ROWS = 40000
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FIELDS = {"demand": "demand", "jg": "generation_scheduled_total", "jgw1": "generation_jgw1", "jgw2": "generation_jgw2",
          "jgm1": "generation_jgm1", "jgm2": "generation_jgm2", "jgm": "charging_jgm", "jgz2": "generation_jgz2",
          "jnwrb": "generation_jnwrb", "jga": "generation_jga", "wi": "wind", "pv": "solar", "swm_p": "exchange_parallel", "swm_np": "exchange_non_parallel"}
EMPTY = {"jgo", "jgz1", "jgz3"}
META = {"dtime", "dtime_utc", "period", "period_utc", "business_date", "publication_ts", "publication_ts_utc"}
X_COLS = ["x_field", "x_business_date"]


def url_of(year):
    q = {"$filter": f"business_date ge '{year}-01-01' and business_date le '{year}-12-31'", "$first": str(PAGE_ROWS)}
    return "https://api.raporty.pse.pl/api/his-wlk-cal?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def parse(content, year, base, today, counts):
    v = json.loads(content)["value"]
    if len(v) >= PAGE_ROWS:
        raise RuntimeError(f"{year}: the answer fills its page ({len(v)} rows); some rows may be missing")
    out, seen = [], set()
    for r in v:
        extra = set(r) - set(FIELDS) - EMPTY - META
        if extra:
            raise RuntimeError(f"{year}: fields not in the map: {sorted(extra)}")
        filled = [k for k in EMPTY if r.get(k) is not None]
        if filled:
            raise RuntimeError(f"{year}: a field read as empty now holds a figure: {filled}")
        if r["business_date"] >= today:
            counts["day in progress"] = counts.get("day in progress", 0) + 1
            continue
        start = pd.Timestamp(r["dtime_utc"]) - pd.Timedelta(minutes=15)
        if r["period_utc"].split(" - ")[0] != start.strftime("%H:%M"):
            raise RuntimeError(f"{year}: a period unlike its stamp: {r['period_utc']} {r['dtime_utc']}")
        ts = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        if ts in seen:
            raise RuntimeError(f"{year}: {ts} given twice")
        seen.add(ts)
        for k, var in FIELDS.items():
            if r.get(k) is None:
                counts[f"{k} blank"] = counts.get(f"{k} blank", 0) + 1
                continue
            out.append(dict(base, entity="pse:pl", variable=var, ts_utc=ts, value=float(r[k]), unit="MW", freq="PT15M", geo="PL", market="",
                            node="Poland (KSE)", x_field=k, x_business_date=r["business_date"]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="PSE: Poland's power balance a quarter hour (his-wlk-cal)")
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
        for year in range(FIRST_YEAR, now.year + 1):
            content, rec = ip.fetch_raw(CONNECTOR, url_of(year), log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300, pause=1)
            base = dict(source=SOURCE, source_url=url_of(year), retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            # the day in progress is the Polish business day of the retrieval (Warsaw time)
            at = pd.Timestamp(rec.get("retrieved_at") or now.isoformat()).tz_convert("Europe/Warsaw").strftime("%Y-%m-%d")
            rows += parse(content, year, base, at, counts)
            got.append((year, base["retrieved_at"]))
        s = pd.DataFrame(rows)
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): PSE (Polskie Sieci Elektroenergetyczne), Poland's power balance a quarter hour, report his-wlk-cal, "
            f"{s.ts_utc.min()} to {s.ts_utc.max()} (session 2252)",
            "Shape: series (docs/datastandard.md v0). entity pse:pl; variable demand, generation_scheduled_total (jg), generation_jgw1, "
            "generation_jgw2, generation_jgm1, generation_jgm2, charging_jgm, generation_jgz2, generation_jnwrb, generation_jga, wind, solar, exchange_parallel, "
            "exchange_non_parallel (PSE's labels in the docstring); unit MW; freq PT15M; ts_utc the quarter hour's start (PSE's UTC period); "
            "geo PL; x_field PSE's field; x_business_date PSE's business day (local).",
            f"Not taken, counted: {', '.join(f'{k} {v:,}' for k, v in sorted(counts.items())) or 'none'} (the day in progress at retrieval, "
            "and blank figures). PSE's jgo, jgz1 and jgz3 are empty in every year read. Prices are not taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/pse_poland.py; the years retrieved {', '.join(f'{y} {a}' for y, a in got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} PSE S.A., Raporty OSP, report his-wlk-cal (basic quantities of the KSE), {PAGE}",
            "  access: https://api.raporty.pse.pl/api/his-wlk-cal, one calendar year of business days a request",
            "License: internal until the licenses' round reads PSE's terms. Cite PSE S.A., Raporty OSP.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.variable.nunique()} variables, {s.ts_utc.min()} to {s.ts_utc.max()}; not taken {counts}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="PSE S.A. (Polskie Sieci Elektroenergetyczne)",
                                    report="Raporty OSP, his-wlk-cal: basic quantities of the KSE, a quarter hour", report_url=PAGE,
                                    document_list="https://api.raporty.pse.pl/api/openapi", license="internal", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
