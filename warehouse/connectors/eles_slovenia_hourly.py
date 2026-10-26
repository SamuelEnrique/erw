#!/usr/bin/env python3
"""ELES (Slovenia's transmission system operator): production and take-over on the transmission network, an hour, from 2021,
from its "Prevzem in proizvodnja" page's CSV export (session 2822, chain 144).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eles_slovenia_hourly.csv, from the page's export
(two requests: the page, for its form fields, then the form posted with the CSV button and the date span):

    https://www.eles.si/prevzem-in-proizvodnja   (GET, then POST with __EVENTTARGET dnn$ctr1215$View$ctl00$btn_exportCSV,
                                                   pckDateFrom 01.01.2021, pckDateTo the last ended day)

    entity      eles:si
    variable    the file's columns: forecast_generation (predvidena_proizvodnja), generation (dejanska_proizvodnja),
                forecast_takeover (predviden_prevzem), takeover (dejanski_prevzem), nuclear_krsko (nek), thermal (termo),
                hydro (hidro)
    unit        MW, the hour's mean power (the page states no unit; the figures are MW by their size: Krsko at about 665 to
                700, the take-over about 1,000 to 2,000, Slovenia's load), so also the hour's MWh
    ts_utc      the hour's start in UTC: the label Hn is the local clock hour from n-1 o'clock (Europe/Ljubljana), so the
                spring day skips H03 (23 hours); the autumn day gives H01 to H24 once each (24 of its 25 hours), its 02:00
                hour read as the first one, in summer time; freq PT1H; geo SI
    node        "ELES transmission network, <the file's column>"
    x_*         the file's date and hour label

The page says (in Slovene): since 1 January 2021 ELES publishes the production of producers connected directly to the
transmission network (the pumped storage plant Avce included); producers on the distribution network (small hydro, solar and
others) are not in it, and Slovenia's whole production is on ENTSO-E's transparency platform. Krsko's (NEK's, JEK's) whole
production is shown, half of which belongs to Croatia by the two states' treaty. Only the days ended at the retrieval (in
Ljubljana's time) are kept. Each day's hours are counted against its length in Europe/Ljubljana (23 on the spring change, 25
on the autumn one): the autumn days, which give 24, are counted and listed; a blank has no row; nothing is filled. Checks that stop the run: an
export not the expected CSV (its header), a date or an hour label not readable, a value not a number, a key given twice.

    python warehouse/connectors/eles_slovenia_hourly.py [--offline] [--out-dir DIR]

Ceiling: two requests, the export reused from warehouse/raw/eles_slovenia/ with --offline (the newest saved answer that is the
CSV). www.eles.si's robots file (session 2822, read 1639) disallows /admin/, /Portals/ and the site's code paths, not this
page, and names no Claude agent. License: see the license record (ELES's terms, the licenses round).
"""

import argparse
import csv
import datetime as dt
import glob
import io
import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eles_slovenia_hourly"
CONNECTOR = "eles_slovenia"
SOURCE = "eles:prevzem_in_proizvodnja"
URL = "https://www.eles.si/prevzem-in-proizvodnja"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
TZ = "Europe/Ljubljana"
START = "01.01.2021"
HEAD = ["datum", "ura", "predvidena_proizvodnja", "dejanska_proizvodnja", "predviden_prevzem", "dejanski_prevzem", "nek", "termo", "hidro"]
VARS = {"predvidena_proizvodnja": "forecast_generation", "dejanska_proizvodnja": "generation",
        "predviden_prevzem": "forecast_takeover", "dejanski_prevzem": "takeover", "nek": "nuclear_krsko", "termo": "thermal",
        "hidro": "hydro"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_date", "x_hour"]


def is_export(content):
    return content[:200].lstrip(b"\xef\xbb\xbf").startswith(b"datum;ura;")


def fetch(last_day, log):
    s = requests.Session()
    r = s.get(URL, headers=UA, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for {URL}")
    form = {}
    for m in re.finditer(r"<input[^>]*>", r.text):
        n = re.search(r'name="([^"]+)"', m.group(0))
        if not n or "search" in n.group(1):
            continue
        v = re.search(r'value="([^"]*)"', m.group(0))
        form[n.group(1)] = v.group(1) if v else ""
    if "__VIEWSTATE" not in form or "dnn$ctr1215$View$ctl00$pckDateFrom" not in form:
        raise RuntimeError("the page's export form was not found")
    form.update({"__EVENTTARGET": "dnn$ctr1215$View$ctl00$btn_exportCSV", "__EVENTARGUMENT": "",
                 "dnn$ctr1215$View$ctl00$pckDateFrom": START, "dnn$ctr1215$View$ctl00$pckDateTo": last_day.strftime("%d.%m.%Y")})
    time.sleep(2)
    p = s.post(URL, data=form, headers=UA, timeout=300)
    if p.status_code != 200 or not is_export(p.content):
        raise RuntimeError(f"the export did not answer with its CSV: HTTP {p.status_code}, {p.content[:80]!r}")
    log(f"  POST {URL} ({START} to {last_day:%d.%m.%Y}): {len(p.content)} bytes")
    return p.content, {"retrieved_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "last_modified": p.headers.get("Last-Modified") or ""}


def saved(log):
    """The newest saved answer under URL that is the CSV export (the page's own HTML is saved under the same address)."""
    best = None
    for man in glob.glob(os.path.join(ip.RAW_DIR, CONNECTOR, "*", "manifest.csv")):
        for row in csv.DictReader(open(man, encoding="utf-8")):
            if row["url"] != URL:
                continue
            path = os.path.join(os.path.dirname(man), row["file"])
            if os.path.exists(path) and (best is None or row["retrieved_at"] > best[0]):
                with open(path, "rb") as f:
                    if is_export(f.read(200)):
                        best = (row["retrieved_at"], path, row.get("last_modified") or "")
    if best is None:
        raise RuntimeError(f"offline: no saved CSV export of {URL} in warehouse/raw/{CONNECTOR}/")
    log(f"  raw file reused: {os.path.relpath(best[1], ip.ROOT)}")
    return open(best[1], "rb").read(), {"retrieved_at": best[0], "last_modified": best[2]}


def build(content, retrieved, vintage):
    text = content.decode("utf-8-sig")
    t0 = pd.read_csv(io.StringIO(text), sep=";", dtype=str, keep_default_na=False)
    if list(t0.columns) != HEAD:
        raise RuntimeError(f"the export's header is not the expected one: {list(t0.columns)}")
    ended = (pd.Timestamp(retrieved).tz_convert(TZ) if retrieved else pd.Timestamp.now(tz=TZ)).normalize().tz_localize(None)
    rows, counts = [], {"blank": 0, "in_progress": 0, "odd_days": []}
    days = {}
    for r in t0.itertuples(index=False):
        try:
            d = dt.datetime.strptime(r.datum, "%d.%m.%Y")
        except ValueError:
            raise RuntimeError(f"a date not readable: {r.datum!r}")
        m = re.fullmatch(r"H(\d{2})", r.ura)
        if not m or not 1 <= int(m.group(1)) <= 25:
            raise RuntimeError(f"an hour label not readable: {r.ura!r} on {r.datum}")
        if pd.Timestamp(d) >= ended:
            counts["in_progress"] += 1
            continue
        h = int(m.group(1))
        days.setdefault(d, set()).add(h)
        wall = pd.Timestamp(d) + pd.Timedelta(hours=h - 1)       # Hn: the local clock hour from n-1 o'clock
        try:
            ts = wall.tz_localize(TZ, ambiguous=True, nonexistent="raise").tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            raise RuntimeError(f"an hour that does not exist in {TZ}: {r.datum} {r.ura}")
        for col, var in VARS.items():
            v = getattr(r, col).strip().replace(",", ".")
            if v == "":
                counts["blank"] += 1
                continue
            try:
                value = float(v)
            except ValueError:
                raise RuntimeError(f"{r.datum} {r.ura} {col}: not a number: {v!r}")
            rows.append({"entity": "eles:si", "variable": var, "ts_utc": ts, "value": value, "unit": "MW", "freq": "PT1H",
                         "geo": "SI", "market": "", "node": f"ELES transmission network, {col}", "source": SOURCE,
                         "source_url": URL, "retrieved_at": retrieved, "vintage": vintage, "x_date": r.datum, "x_hour": r.ura})
    for d, hours in days.items():
        length = int((pd.Timestamp(d + dt.timedelta(days=1)).tz_localize(TZ) - pd.Timestamp(d).tz_localize(TZ)) / pd.Timedelta(hours=1))
        if len(hours) != length:
            counts["odd_days"].append((d.strftime("%Y-%m-%d"), length, len(hours)))
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]} ({twice.x_date.iloc[0]} {twice.x_hour.iloc[0]})")
    counts["days"] = len(days)
    return t.sort_values(["variable", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="ELES: Slovenia's transmission network production and take-over, an hour")
    ap.add_argument("--offline", action="store_true", help="the saved export only, no request")
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
        if args.offline:
            content, rec = saved(log)
        else:
            if ip.paused("eles") or ip.paused_host("www.eles.si"):
                raise RuntimeError("ELES is paused (warehouse/metadata/paused_sources.csv): not requested")
            last = pd.Timestamp.now(tz=TZ).normalize().tz_localize(None) - pd.Timedelta(days=1)
            content, rec = fetch(last, log)
        retrieved = rec["retrieved_at"]
        t, counts = build(content, retrieved, rec.get("last_modified") or retrieved)
        if t.empty:
            raise RuntimeError("no observation kept")
        for x in counts["odd_days"]:
            log(f"  a day whose hours do not match its length (day, hours expected, hours given): {x}")
        header = [
            f"Energy Research Warehouse (ERW): ELES, production and take-over on Slovenia's transmission network (Prevzem in proizvodnja, the page's CSV export), an hour, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} (session 2822)",
            "Shape: series (docs/datastandard.md v0). entity eles:si; variable forecast_generation, generation, forecast_takeover, takeover, nuclear_krsko, thermal or hydro; unit MW (the hour's mean; the page states no unit, the figures are MW by their size); ts_utc the hour's start in UTC (Hn is the local clock hour from n-1 o'clock; the autumn change day's one 02:00 hour read as summer time); freq PT1H; geo SI; x_date and x_hour the file's own. "
            "Producers connected to the transmission network only (the pumped storage plant Avce included); Krsko's whole production, half of it Croatia's.",
            f"{len(t)} rows, {counts['days']} days. {counts['in_progress']} rows of a day not ended at the retrieval are not kept. {len(counts['odd_days'])} day(s) whose hours do not match the day's length in Europe/Ljubljana, listed in the run log; {counts['blank']} blanks have no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eles_slovenia_hourly.py; the export retrieved {retrieved}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} ELES, d.o.o., Prevzem in proizvodnja (production and take-over on the transmission network), {URL}, its CSV export",
            "License: see the ERW's license record (docs/licenses.md) for ELES's terms. Source: ELES; reshaped by the ERW.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="ELES (the Slovenian transmission system operator)",
                                    report="Prevzem in proizvodnja (production and take-over on the transmission network), CSV export",
                                    report_url=URL, document_list=URL, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {counts['days']} days; odd days {len(counts['odd_days'])}; in progress {counts['in_progress']}; blanks {counts['blank']}")
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
