#!/usr/bin/env python3
"""Peru's electricity production a month by department, January 2005 to the latest month published, as the Banco Central
de Reserva del Peru (BCRP) gives it in BCRPData's monthly series "Produccion de electricidad por departamento" (codes
RD13043DM to RD13067DM: the 24 departments and the total, in GWh), from the Ministerio de Energia y Minas (MINEM)
(session 2566, chain 126, a source of the session's own choosing; the ERW held Peru only in EIA's international table,
and chain 105's session 2296 could not read COES's files).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/bcrp_peru_electricity_monthly.csv, from
BCRPData's API (no key), ten series a request at most, so three requests:

    https://estadisticas.bcrp.gob.pe/estadisticas/series/api/<codes>/json/2005-1/<year>-<month>/ing

    entity      bcrp_pe:<department> (amazonas, ancash, ..., ucayali; the name in lower case without accents, each run
                of other characters an underscore) and bcrp_pe:total
    variable    production
    unit        MWh (BCRP's GWh times 1,000); ts_utc the month's first day; freq P1M; geo PE
    node        BCRP's series name (the department as BCRP spells it)

Each response must name the series asked, in order, each "Produccion de electricidad por departamento - <name> (gwh)",
and every month from January 2005 to the last month asked. A cell "n.d." (no data) is not written; any other cell that
is not a number stops the run. The departments must add to the total within 0.5% each month (BCRP's own figures differ
by up to 10 GWh, 0.22%, in April 2021); both are kept as given. Nothing is filled.

    python warehouse/connectors/bcrp_peru_electricity.py [--offline] [--fresh] [--out-dir DIR] [--to YYYY-M]

Ceiling: three requests a run, saved in warehouse/raw/bcrp_pe/ and reused unless --fresh; --offline asks nothing.
estadisticas.bcrp.gob.pe has no robots file (HTTP 404, session 2566). License: public. BCRPData's Condiciones de Uso:
"Puede reproducirse total o parcialmente, sin autorizacion expresa, siempre y cuando se cite la fuente."; the source
cited is BCRP's, and MINEM's as the original.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback
import unicodedata

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "bcrp_peru_electricity_monthly"
CONNECTOR = "bcrp_pe"
SOURCE = "bcrp_pe:bcrpdata_produccion_electricidad_departamento"
HOST = "estadisticas.bcrp.gob.pe"
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/"
LIST = "https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/produccion-de-electricidad-por-departamento"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Banco Central de Reserva del Peru (BCRP), BCRPData, monthly series: Produccion de electricidad por departamento "
            "(RD13043DM to RD13067DM), source: Ministerio de Energia y Minas (MINEM)")
CODES = [f"RD{n}DM" for n in range(13043, 13068)]  # 24 departments, then the total
TO = "2026-6"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
PREFIX = "Producci" + chr(0xF3) + "n de electricidad por departamento - "
X_COLS = ["x_series_code"]


def slug(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def urls(to=TO):
    return [API + "-".join(CODES[i:i + 10]) + f"/json/2005-1/{to}/ing" for i in range(0, len(CODES), 10)]


def months(to=TO):
    y, m = (int(x) for x in to.split("-"))
    return [f"{MONTHS[k % 12]}.{2005 + k // 12}" for k in range((y - 2005) * 12 + m)]


def parse(docs, base, to=TO):
    """docs: the responses' JSON, in the order of urls()."""
    want = months(to)
    cols, out = [], []
    for i, d in enumerate(docs):
        codes = CODES[i * 10:i * 10 + 10]
        names = [s.get("name", "") for s in d["config"]["series"]]
        if len(names) != len(codes) or not all(n.startswith(PREFIX) and n.endswith(" (gwh)") for n in names):
            raise RuntimeError(f"response {i + 1}: not the series asked: {names}")
        got = [p["name"] for p in d["periods"]]
        if got != want:
            raise RuntimeError(f"response {i + 1}: months {got[:2]}..{got[-1:]} ({len(got)}), not {want[0]}..{want[-1]} ({len(want)})")
        for j, (code, name) in enumerate(zip(codes, names)):
            label = name[len(PREFIX):-len(" (gwh)")]
            cols.append((code, label))
            for p in d["periods"]:
                v = p["values"][j]
                if v == "n.d.":
                    continue
                if not re.fullmatch(r"-?\d+(\.\d+)?", v):
                    raise RuntimeError(f"{code} {p['name']}: not a figure: {v!r}")
                mo, yr = p["name"].split(".")
                out.append(dict(entity=f"bcrp_pe:{slug(label)}", variable="production", ts_utc=f"{yr}-{MONTHS.index(mo) + 1:02d}-01T00:00:00Z",
                                value=round(float(v) * 1000, 3), unit="MWh", freq="P1M", geo="PE", market="", node=label, **base,
                                x_series_code=code))
    if len(cols) != len(CODES) or cols[-1][1] != "Total" or len({slug(c[1]) for c in cols}) != len(CODES):
        raise RuntimeError(f"the series are not 24 departments and the total: {[c[1] for c in cols]}")
    t = pd.DataFrame(out)
    tot = t[t.entity == "bcrp_pe:total"].set_index("ts_utc").value
    parts = t[t.entity != "bcrp_pe:total"].groupby("ts_utc").value.sum()
    off = ((parts.reindex(tot.index) - tot).abs() > 0.005 * tot)
    if off.any():
        raise RuntimeError(f"the departments miss the total by more than 0.5% in {list(tot.index[off])[:5]}")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="BCRP: Peru's electricity production a month by department (MINEM)")
    ap.add_argument("--offline", action="store_true", help="the saved responses only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the series again")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--to", default=TO, help="the last month asked, YYYY-M (default %(default)s)")
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
        docs, recs = [], []
        for u in urls(args.to):
            content, rec = ip.fetch_raw(CONNECTOR, u, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=2)
            docs.append(json.loads(content.decode("utf-8-sig")))
            recs.append(rec)
        base = dict(source=SOURCE, source_url=LIST, retrieved_at=min(r.get("retrieved_at") or "" for r in recs), vintage="")
        t = parse(docs, base, args.to)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = t[t.entity == "bcrp_pe:total"]
        y = tot[tot.ts_utc.str[:4] == "2025"].value.sum()
        head = [
            "Energy Research Warehouse (ERW): Banco Central de Reserva del Peru (BCRP), BCRPData, Produccion de electricidad por "
            "departamento: Peru's electricity production a month by department, from MINEM (session 2566)",
            "Shape: series (docs/datastandard.md v0). entity bcrp_pe:<department> or bcrp_pe:total; variable production; unit MWh "
            "(BCRP's GWh times 1,000); ts_utc the month's first day; freq P1M; geo PE; node BCRP's name; x_series_code BCRP's code.",
            f"{len(t)} rows, {t.entity.nunique()} entities, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}; the total for 2025 "
            f"{y / 1e6:.3f} TWh. The departments add to the total within 0.5% each month (BCRP's own figures differ by up to 10 GWh); "
            "both kept as given; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/bcrp_peru_electricity.py; the three responses retrieved "
            + ", ".join(r.get("retrieved_at") or "" for r in recs),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {API}<codes>/json/2005-1/{args.to}/ing (list: {LIST})",
            "License: public. BCRPData's Condiciones de Uso allow reproduction in whole or in part without express permission, the "
            f"source cited. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Banco Central de Reserva del Peru (BCRP)",
                                    report="BCRPData monthly series: Produccion de electricidad por departamento (RD13043DM to RD13067DM; source MINEM)",
                                    report_url=LIST, document_list=LIST, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
