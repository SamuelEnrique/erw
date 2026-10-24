#!/usr/bin/env python3
"""Eurostat's monthly imports of natural gas and of LNG by partner country (nrg_ti_gasm): each European country's gas
from each country it imports from, in energy, from 2015 (session 2213, chain 098: where Europe's gas comes from, the
United States' LNG among its partners; a source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_gas_imports_monthly.csv, from
Eurostat's SDMX 2.1 dissemination API (no key). The data set is large, so Eurostat answers a request with a queued job;
the connector polls the job's status and then fetches its result:

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ti_gasm?format=SDMX-CSV&compressed=false&startPeriod=2015-01
    https://ec.europa.eu/eurostat/api/dissemination/1.0/async/status/<job id>
    https://ec.europa.eu/eurostat/api/dissemination/1.0/async/data/<job id>          (the SDMX-CSV, about 190 MB)

    entity      eurostat_gas_imports:<Eurostat geo code>:<SIEC code>:<partner code> (G3000 natural gas, G3200 liquefied
                natural gas, a part of G3000); node the importing country, product and partner as Eurostat codes them
    variable    imports
    unit        MWh: Eurostat's terajoules of gross calorific value (TJ_GCV) times 277.7778 (1 TJ = 1,000,000 MJ and
                1 MWh = 3,600 MJ, an exact definition); the file's million cubic metres (MIO_M3) are not taken
    ts_utc      the month's first day at 00:00:00Z; freq P1M; geo the importing country's ISO alpha-2 (Eurostat's EL is
                GR), blank for Eurostat's aggregates EU27_2020 and EA21
    x_*         Eurostat's geo, SIEC and partner codes, the observation's flag and confidentiality status

Importing countries kept: the EU's members, EFTA's and the official candidates, with the two aggregates, as
eurostat_renewable_capacity_annual keeps them under Eurostat's terms (the United Kingdom and Kosovo left out); every
partner is kept, aggregates such as TOTAL and NSP (not specified) among them, as Eurostat publishes them.

**Zeros are not written:** Eurostat prints a value for every partner in every month, about 97% of them zero; a zero and a
blank both have no row, and the header counts each. Nothing is filled. A header not Eurostat's, a value that is not a
number, a unit or frequency not expected, or a key given twice stops the run.

    python warehouse/connectors/eurostat_gas_imports.py [--job ID --offline] [--out-dir DIR]

Ceiling: one request to submit, at most twelve status polls 20 seconds apart, one to fetch; --offline with --job reads
that job's saved result from warehouse/raw/eurostat_gas_imports/. ec.europa.eu's robots file disallows the old SDMX path
and the search pages, not /eurostat/api/dissemination/ (sessions 2123 and 2213). License: Eurostat's copyright notice
(the record's verdict, session 2123): reuse with the source acknowledged; source: Eurostat.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import time
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eurostat_gas_imports_monthly"
CONNECTOR = "eurostat_gas_imports"
SOURCE = "eurostat:nrg_ti_gasm"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_gasm/default/table"
SUBMIT = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ti_gasm?format=SDMX-CSV&compressed=false&startPeriod=2015-01"
STATUS = "https://ec.europa.eu/eurostat/api/dissemination/1.0/async/status/{job}"
DATA = "https://ec.europa.eu/eurostat/api/dissemination/1.0/async/data/{job}"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "siec", "partner", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG",
          "CONF_STATUS"]
TJ_TO_MWH = 1_000_000 / 3_600
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020", "EA21", "EA20"}
AGGREGATES = {"EU27_2020", "EA21", "EA20"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_siec", "x_partner", "x_flag", "x_conf_status"]
JOB = re.compile(r"<(?:\w+:)?id>([0-9a-f-]{36})</(?:\w+:)?id>")


def build(content, url, retrieved, vintage, chunksize=500_000):
    """The job's SDMX-CSV, read in chunks: the energy rows of the kept countries, zeros and blanks left out."""
    rows, counts = [], {"zero": 0, "blank": 0, "left_out_geo": set()}
    reader = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False, chunksize=chunksize)
    for ch in reader:
        if list(ch.columns) != HEADER:
            raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(ch.columns)}")
        bad = sorted(set(ch.unit) - {"TJ_GCV", "MIO_M3"}) + sorted(set(ch.freq) - {"M"})
        if bad:
            raise RuntimeError(f"a unit or frequency not expected: {bad}")
        counts["left_out_geo"] |= set(ch.geo) - KEPT
        ch = ch[(ch.unit == "TJ_GCV") & ch.geo.isin(KEPT)]
        for r in ch.itertuples(index=False):
            v = r.OBS_VALUE.strip()
            if v == "":
                counts["blank"] += 1
                continue
            try:
                value = float(v)
            except ValueError:
                raise RuntimeError(f"{r.geo} {r.siec} {r.partner} {r.TIME_PERIOD}: not a number: {v!r}")
            if value == 0:
                counts["zero"] += 1
                continue
            if not re.fullmatch(r"\d{4}-\d{2}", r.TIME_PERIOD):
                raise RuntimeError(f"a period not a month: {r.TIME_PERIOD!r}")
            rows.append({"entity": f"eurostat_gas_imports:{r.geo}:{r.siec}:{r.partner}", "variable": "imports",
                         "ts_utc": f"{r.TIME_PERIOD}-01T00:00:00Z", "value": round(value * TJ_TO_MWH, 3), "unit": "MWh",
                         "freq": "P1M", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                         "market": "", "node": f"{r.geo} {r.siec} from {r.partner}", "source": SOURCE, "source_url": url,
                         "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_siec": r.siec,
                         "x_partner": r.partner, "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ti_gasm: European imports of natural gas and LNG by partner, a month")
    ap.add_argument("--job", help="an Eurostat async job id whose result is saved (with --offline) or ready")
    ap.add_argument("--offline", action="store_true", help="the saved result only, no request (needs --job)")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.offline and not args.job:
        ap.error("--offline needs --job")
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
        job = args.job
        if not job:
            sub, _ = ip.fetch_raw(CONNECTOR, SUBMIT, log, fresh=True, headers=UA, timeout=120)
            m = JOB.search(sub.decode("utf-8", errors="replace"))
            if not m:
                raise RuntimeError("Eurostat's answer named no queued job")
            job = m.group(1)
            for _ in range(12):
                time.sleep(20)
                st, _ = ip.fetch_raw(CONNECTOR, STATUS.format(job=job), log, fresh=True, headers=UA, timeout=60)
                s = st.decode("utf-8", errors="replace")
                if "AVAILABLE" in s:
                    break
                if "EXPIRED" in s or "FAILED" in s:
                    raise RuntimeError(f"job {job}: {s[-200:]}")
            else:
                raise RuntimeError(f"job {job} not available after twelve polls")
        url = DATA.format(job=job)
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=900)
        t, counts = build(content, url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        by = t.groupby("x_siec").size()
        us = t[(t.x_partner == "US") & (t.x_siec == "G3200") & (t.x_geo_code == "EU27_2020")]
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, imports of natural gas and LNG by partner country, monthly (nrg_ti_gasm), {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2213)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_gas_imports:<geo>:<SIEC>:<partner> (G3000 natural gas, G3200 LNG, a part of it); variable imports; unit MWh (Eurostat's TJ of gross calorific value "
            "times 277.7778); ts_utc the month's first day; freq P1M; geo ISO alpha-2 (EL is GR), blank for EU27_2020 and EA21.",
            f"{len(t)} rows ({'; '.join(f'{k} {v}' for k, v in by.items())}). Zeros and blanks have no row: {counts['zero']:,} zeros and {counts['blank']:,} blanks of the kept rows are left out. "
            f"Importing countries left out by Eurostat's terms: {' '.join(sorted(counts['left_out_geo'])) or 'none'}. The EU's LNG from the United States, latest month {us.ts_utc.max()[:7] if len(us) else 'none'}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_gas_imports.py; job {job}'s result retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Imports of natural gas by partner country, monthly data (nrg_ti_gasm), {PAGE}",
            f"  access: {SUBMIT}, then {DATA.format(job='<job id>')}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_ti_gasm. Eurostat bears no responsibility for this reshaping (zeros left out, TJ written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Imports of natural gas by partner country, monthly data (nrg_ti_gasm)",
                                    report_url=PAGE, document_list=SUBMIT, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; zeros left out {counts['zero']:,}, blanks {counts['blank']:,}")
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
