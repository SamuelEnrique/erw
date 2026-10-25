#!/usr/bin/env python3
"""Peru's production of crude oil, natural gas liquids and natural gas a month, January 2000 to the latest month
published, as the Banco Central de Reserva del Peru (BCRP) gives it in BCRPData's monthly series "Produccion minera e
hidrocarburos (miles de unidades recuperables)" (codes PN01882AM, PN01883AM and PN01884AM), from INEI and the
Ministerio de Energia y Minas (MINEM) (session 2567, chain 126, a source of the session's own choosing; the ERW held
Peru's oil and gas only in EIA's international tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/bcrp_peru_hydrocarbons_monthly.csv, from
one request to BCRPData's API (no key):

    https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01882AM-PN01883AM-PN01884AM/json/2000-1/<year>-<month>/ing

    entity      bcrp_pe:crude_oil, bcrp_pe:natural_gas_liquids (unit kbbl, BCRP's thousand barrels as given);
                bcrp_pe:natural_gas (unit MMcf, BCRP's million cubic feet as given)
    variable    production
    ts_utc      the month's first day; freq P1M; geo PE
    node        BCRP's series name

The response must name the three series asked, in order and each with the unit the map gives it, and every month from
January 2000 to the last month asked. A cell "n.d." is not written; any other cell that is not a number stops the run.
Nothing is filled. The mining series of the same list (copper, gold and the rest) are not taken.

    python warehouse/connectors/bcrp_peru_hydrocarbons.py [--offline] [--fresh] [--out-dir DIR] [--to YYYY-M]

Ceiling: one request a run, saved in warehouse/raw/bcrp_pe/ and reused unless --fresh; --offline asks nothing.
estadisticas.bcrp.gob.pe has no robots file (HTTP 404, session 2566). License: public. BCRPData's Condiciones de Uso:
"Puede reproducirse total o parcialmente, sin autorizacion expresa, siempre y cuando se cite la fuente."; the source
cited is BCRP's, and INEI's and MINEM's as the original.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "bcrp_peru_hydrocarbons_monthly"
CONNECTOR = "bcrp_pe"
SOURCE = "bcrp_pe:bcrpdata_produccion_hidrocarburos"
HOST = "estadisticas.bcrp.gob.pe"
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/"
LIST = "https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/produccion-minera-e-hidrocarburos-miles-de-unidades-recuperables"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Banco Central de Reserva del Peru (BCRP), BCRPData, monthly series: Produccion minera e hidrocarburos (miles de "
            "unidades recuperables), Hidrocarburos (PN01882AM, PN01883AM, PN01884AM), sources: INEI and Ministerio de Energia y Minas (MINEM)")
A = chr(0xED)
O = chr(0xF3)
U = chr(0xFA)
# code, the series name's end as BCRP prints it, the entity's item, the unit
SERIES = [("PN01882AM", "Hidrocarburos - Petr" + O + "leo (miles de barriles)", "crude_oil", "kbbl"),
          ("PN01883AM", "Hidrocarburos - L" + A + "quidos de gas natural (miles de barriles)", "natural_gas_liquids", "kbbl"),
          ("PN01884AM", "Hidrocarburos - Gas Natural (millones de pies c" + U + "bicos)", "natural_gas", "MMcf")]
TO = "2026-8"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
X_COLS = ["x_series_code"]


def url(to=TO):
    return API + "-".join(s[0] for s in SERIES) + f"/json/2000-1/{to}/ing"


def months(to=TO):
    y, m = (int(x) for x in to.split("-"))
    return [f"{MONTHS[k % 12]}.{2000 + k // 12}" for k in range((y - 2000) * 12 + m)]


def parse(doc, base, to=TO):
    names = [s.get("name", "") for s in doc["config"]["series"]]
    if len(names) != len(SERIES) or not all(n.endswith(" - " + s[1]) for n, s in zip(names, SERIES)):
        raise RuntimeError(f"not the series asked: {names}")
    got, want = [p["name"] for p in doc["periods"]], months(to)
    if got != want:
        raise RuntimeError(f"months {got[:1]}..{got[-1:]} ({len(got)}), not {want[0]}..{want[-1]} ({len(want)})")
    out = []
    for j, (code, label, item, unit) in enumerate(SERIES):
        for p in doc["periods"]:
            v = p["values"][j]
            if v == "n.d.":
                continue
            if not re.fullmatch(r"\d+(\.\d+)?", v):
                raise RuntimeError(f"{code} {p['name']}: not a figure: {v!r}")
            mo, yr = p["name"].split(".")
            out.append(dict(entity=f"bcrp_pe:{item}", variable="production", ts_utc=f"{yr}-{MONTHS.index(mo) + 1:02d}-01T00:00:00Z",
                            value=round(float(v), 4), unit=unit, freq="P1M", geo="PE", market="", node=label, **base, x_series_code=code))
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="BCRP: Peru's crude oil, natural gas liquids and natural gas production a month")
    ap.add_argument("--offline", action="store_true", help="the saved response only, no request")
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
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_hc_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        content, rec = ip.fetch_raw(CONNECTOR, url(args.to), log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=2)
        base = dict(source=SOURCE, source_url=LIST, retrieved_at=rec.get("retrieved_at") or "", vintage="")
        t = parse(json.loads(content.decode("utf-8-sig")), base, args.to)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        y = {e: t[(t.entity == f"bcrp_pe:{e}") & (t.ts_utc.str[:4] == "2025")].value.sum() for e in ("crude_oil", "natural_gas")}
        head = [
            "Energy Research Warehouse (ERW): Banco Central de Reserva del Peru (BCRP), BCRPData, Produccion minera e hidrocarburos: "
            "Peru's crude oil, natural gas liquids and natural gas production a month, from INEI and MINEM (session 2567)",
            "Shape: series (docs/datastandard.md v0). entity bcrp_pe:crude_oil, bcrp_pe:natural_gas_liquids (kbbl) or "
            "bcrp_pe:natural_gas (MMcf); variable production; ts_utc the month's first day; freq P1M; geo PE; node BCRP's name; "
            "x_series_code BCRP's code.",
            f"{len(t)} rows, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}; in 2025 crude oil {y['crude_oil'] / 1e3:,.1f} million barrels, "
            f"natural gas {y['natural_gas'] / 1e3:,.1f} bcf. The figures as BCRP gives them; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/bcrp_peru_hydrocarbons.py; the response retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_hc_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {url(args.to)} (list: {LIST})",
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
                                    report="BCRPData monthly series: Produccion minera e hidrocarburos, Hidrocarburos (PN01882AM, PN01883AM, PN01884AM; sources INEI and MINEM)",
                                    report_url=LIST, document_list=LIST, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR + "_hc", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
