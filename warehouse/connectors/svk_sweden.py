#!/usr/bin/env python3
"""Sweden's electricity production an hour by production type, all of Sweden, from Svenska kraftnät's Mimer (its
production statistics), 1 January 2020 to 18 March 2025 (session 2351, chain 105: a source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table from six GET downloads of Mimer's Produktionsstatistik
(https://mimer.svk.se/ProductionConsumption/ProductionIndex), one a production type, area SN0 (Hela Sverige):

    https://mimer.svk.se/ProductionConsumption/DownloadText?PeriodFrom=01/01/2020 00:00:00&PeriodTo=03/18/2025 00:00:00
        &ConstraintAreaId=SN0&ProductionSortId=<KK, OK, OP, SE, VA or VI>

    svk_sweden_production_hourly   entity svk:sweden; variable generation_nuclear (KK, Karnkraftproduktion),
               generation_other_thermal (OK, Ovrig varmekraftproduktion), generation_unspecified_measured (OP, Uppmatt
               ospecificerad produktion), generation_solar (SE), generation_hydro (VA) or generation_wind (VI); value in MWh
               (Mimer's settled kWh, Avraknad, divided by 1,000); ts_utc the hour's start in UTC; freq PT1H; geo SE;
               x_published Mimer's publication time as printed (Publiceringstidpunkt)

Mimer's production statistics end with 18 March 2025: "Produktionsstatistik for dygn 2025-03-18 och framat rapporteras
till eSett" (the days from 2025-03-18 on are reported to eSett and published on eSett Open Data), so the table is closed
history. Each file must hold 24 hours for every day (Mimer's hours are a fixed offset: no day has 23 or 25), no hour
twice, no blank figure, and its rows must sum to its "Summa" line, or the run stops.

Time: the hours are Swedish normal time (UTC+1 all year), labelled by their start: no page says so, but every day has
24 hours across the clock changes, and June's mean solar output is symmetric about the 12:00 label, where Sweden's solar
noon falls (about 11:50 normal time; in UTC labels it would fall at 13:00). ts_utc = the label minus one hour (session
2351).

What it counts: production settled hourly at the grid (Avraknad). Nuclear, hydro and wind equal Eurostat's net production
for Sweden to 0.5 percent each year from 2020 to 2024 (exactly in 2021 and 2022); solar is about 58 percent and other
thermal about 50 percent of Eurostat's (production behind the meter and on industrial sites is not in it); all types
together are 95 to 97 percent (session 2351, eurostat_electricity_monthly). Nothing is filled.

    python warehouse/connectors/svk_sweden.py [--offline] [--out-dir DIR]

Ceiling: six requests, each asked again unless --offline. mimer.svk.se has no robots file (HTTP 404); www.svk.se's
disallows only its archive and search paths (session 2351). License: internal until the licenses' round reads
Svenska kraftnat's terms (none found on Mimer or on www.svk.se's about page).
"""

import argparse
import collections
import datetime as dt
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "svk_sweden"
SOURCE = "svk:mimer_production_statistics"
HOST = "mimer.svk.se"
PAGE = "https://mimer.svk.se/ProductionConsumption/ProductionIndex"
TABLE = "svk_sweden_production_hourly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
KINDS = {"KK": "generation_nuclear", "OK": "generation_other_thermal", "OP": "generation_unspecified_measured",
         "SE": "generation_solar", "VA": "generation_hydro", "VI": "generation_wind"}
HEAD = "Period;Avräknad (kWh);Publiceringstidpunkt;"
FIRST, LAST = "01%2F01%2F2020%2000%3A00%3A00", "03%2F18%2F2025%2000%3A00%3A00"
NORMAL_TIME = pd.Timedelta(hours=1)  # Swedish normal time is UTC+1


def url_of(kind):
    return (f"https://mimer.svk.se/ProductionConsumption/DownloadText?PeriodFrom={FIRST}&PeriodTo={LAST}"
            f"&ConstraintAreaId=SN0&ProductionSortId={kind}")


def kwh(s):
    return float(s.strip().replace(" ", "").replace(",", "."))


def parse(text, kind):
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != HEAD:
        raise RuntimeError(f"{kind}: the file's first line is {lines[0][:80]!r}, not {HEAD!r}")
    rows, summa = [], None
    for l in lines[1:]:
        if not l.strip():
            continue
        f = l.split(";")
        if f[0] == "Summa":
            summa = kwh(f[1])
            continue
        if not f[1].strip():
            raise RuntimeError(f"{kind} {f[0]}: a blank figure")
        rows.append((f[0], kwh(f[1]), f[2].strip()))
    if summa is None:
        raise RuntimeError(f"{kind}: no Summa line")
    total = sum(r[1] for r in rows)
    if abs(total - summa) > max(1.0, 1e-9 * abs(summa)):
        raise RuntimeError(f"{kind}: the rows sum to {total:,.3f} kWh, the Summa line {summa:,.3f}")
    stamps = collections.Counter(r[0] for r in rows)
    twice = [s for s, n in stamps.items() if n > 1]
    if twice:
        raise RuntimeError(f"{kind}: hours given twice, {twice[:3]}")
    days = collections.Counter(s[:10] for s in stamps)
    short = {d: n for d, n in days.items() if n != 24}
    if short:
        raise RuntimeError(f"{kind}: days without 24 hours, {dict(list(short.items())[:3])}")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Svenska kraftnat (Mimer): Sweden's production an hour by type, 2020 to 18 March 2025")
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
        frames, got = [], []
        for kind, var in KINDS.items():
            url = url_of(kind)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=3)
            rows = parse(content.decode("utf-8"), kind)
            label = pd.to_datetime([r[0] for r in rows], format="%Y-%m-%d %H:%M")
            frames.append(pd.DataFrame({
                "entity": "svk:sweden", "variable": var,
                "ts_utc": (label - NORMAL_TIME).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "value": [round(r[1] / 1000.0, 6) for r in rows], "unit": "MWh", "freq": "PT1H", "geo": "SE", "market": "",
                "node": "", "source": SOURCE, "source_url": url, "retrieved_at": rec.get("retrieved_at") or "",
                "vintage": ip.vintage_of(rec), "x_published": [r[2] for r in rows]}))
            got.append(rec.get("retrieved_at") or "")
        s = pd.concat(frames, ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + ["x_published"]
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): Svenska kraftnat (Mimer), Produktionsstatistik, all of Sweden an hour by production "
            f"type, {s.ts_utc.min()} to {s.ts_utc.max()} (session 2351)",
            "Shape: series (docs/datastandard.md v0). entity svk:sweden; variable generation_nuclear, generation_other_thermal, "
            "generation_unspecified_measured, generation_solar, generation_hydro or generation_wind; unit MWh (Mimer's settled kWh "
            "divided by 1,000); freq PT1H; ts_utc the hour's start in UTC; geo SE; x_published Mimer's publication time as printed.",
            "Mimer's hours are Swedish normal time (UTC+1 all year) labelled by their start (24 hours every day; June's solar output "
            "centred on the 12:00 label): ts_utc is the label minus one hour. Every file's rows sum to its Summa line (checked). "
            "Closed history: Mimer's production statistics end on 18 March 2025 (later days are on eSett Open Data). Production "
            "settled at the grid: nuclear, hydro and wind equal Eurostat's within 0.5 percent a year; solar is about 58 percent and "
            "other thermal about 50 percent of Eurostat's (session 2351). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/svk_sweden.py; the files retrieved from {min(got)} to {max(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Svenska kraftnat, Mimer, Produktionsstatistik (area SN0, Hela Sverige), {PAGE}",
            "  access: https://mimer.svk.se/ProductionConsumption/DownloadText?...&ConstraintAreaId=SN0&ProductionSortId=<type>, one a type",
            "License: internal until the licenses' round reads Svenska kraftnat's terms. Source: Svenska kraftnat.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.variable.nunique()} variables, {s.ts_utc.min()} to {s.ts_utc.max()}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Svenska kraftnat", report="Mimer, Produktionsstatistik (production statistics), all of Sweden",
                                    report_url=PAGE, document_list="https://mimer.svk.se/", license="internal", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
