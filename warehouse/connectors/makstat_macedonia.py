#!/usr/bin/env python3
"""North Macedonia's electricity a month from January 2012: imports, exports, gross inland consumption, gross and net
production by kind of plant, the energy branch's own use, distribution losses and final consumption, as the State
Statistical Office publishes it in MakStat (table 125_Ene_Mk_EEmes_ml.px) (session 2357, chain 110: in Pakistan's place,
whose publishers closed to the reader).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/makstat_macedonia_electricity_monthly.csv,
from MakStat's PxWeb API (no key): the table's metadata by GET and one JSON-stat 2.0 query by POST to the same address,
as chain 106's csp_latvia_electricity.py reads Latvia's:

    https://makstat.stat.gov.mk/PXWeb/api/v1/en/MakStat/Energija/MesecEnergetStatistiki/125_Ene_Mk_EEmes_ml.px
    "Electricity in MWh, by months"

    entity      makstat:mk
    variable    imports, exports, gross_inland_consumption, gross_production_total and gross_production_<plant> (thermal
                power plants, CHP plants and autoproducers' thermal stations, hydro, solar, wind, biogas),
                net_production_total and net_production_<plant> (the same six), energy_branch_consumption,
                distribution_losses, available_for_final_consumption, final_consumption_households; node the indicator
                as MakStat writes it; x_code its code (0 to 20)
    unit        MWh as published; ts_utc the month's first day; freq P1M; geo MK

Totals are MakStat's lines, never sums made here (the plants are checked against them: a month whose plants differ from
its total by more than 1 MWh a plant is named in the header); a cell MakStat leaves empty has no row; nothing is filled.
A metadata without the two variables, an indicator list not the 21 expected, a month not of the form YYYYMmm, a value
array not the size of the dimensions, or an indicator and month given twice stops the run.

    python warehouse/connectors/makstat_macedonia.py [--offline] [--out-dir DIR]

Ceiling: two requests (the metadata and the query), saved together in warehouse/raw/makstat_macedonia/ and reused
offline. makstat.stat.gov.mk has no robots file (HTTP 404, session 2357). License: internal until the licenses' round
reads the State Statistical Office's terms.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "makstat_macedonia_electricity_monthly"
CONNECTOR = "makstat_macedonia"
SOURCE = "makstat:125_Ene_Mk_EEmes_ml"
HOST = "makstat.stat.gov.mk"
TABLE_URL = "https://makstat.stat.gov.mk/PXWeb/api/v1/en/MakStat/Energija/MesecEnergetStatistiki/125_Ene_Mk_EEmes_ml.px"
PAGE = "https://makstat.stat.gov.mk/PXWeb/pxweb/en/MakStat/MakStat__Energija__MesecEnergetStatistiki/125_Ene_Mk_EEmes_ml.px/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SAVED = "query_125_Ene_Mk_EEmes_ml.json"
PLANTS = ["thermal_power_plants", "chp_and_autoproducer_thermal", "hydro", "solar", "wind", "biogas"]
VARIABLES = (["imports", "exports", "gross_inland_consumption", "gross_production_total"]
             + [f"gross_production_{p}" for p in PLANTS] + ["net_production_total"] + [f"net_production_{p}" for p in PLANTS]
             + ["energy_branch_consumption", "distribution_losses", "available_for_final_consumption", "final_consumption_households"])
LABELS = ["Imports", "Exports", "Gross inland consumption", "Total Gross Electricity production", "Thermal Power Plants",
          "CHP plants and Autoprod. thermal power stations", "Hydro Power Plants", "Solar Plants", "Wind power plants",
          "Biogas plants", "Total Net Electricity production", "Thermal Power Plants",
          "CHP plants and Autoprod. thermal power stations", "Hydro Power Plants", "Solar Plants", "Wind power plants",
          "Biogas plants", "Consumption of the energy branch", "Distribution losses", "Available for final consumption",
          "Final electricity consumption in households"]
X_COLS = ["x_code"]
# MakStat writes most months 2012M01, some 2019_09, and one with the Cyrillic letter (2026<U+041C>01) (session 2357)
MONTH = re.compile("(\\d{4})[M_М](\\d\\d)")


def plain(label):
    return re.sub(r"^[.\s]+", "", label).strip()


def query(meta):
    v = meta.get("variables", [])
    if len(v) != 2:
        raise RuntimeError(f"the table's variables are not two: {[x.get('code') for x in v]}")
    ind, time = v
    if [plain(t) for t in ind["valueTexts"]] != LABELS:
        raise RuntimeError(f"the indicators are not the 21 expected: {ind['valueTexts']}")
    bad = [t for t in time["valueTexts"] if not MONTH.fullmatch(t)]
    if bad:
        raise RuntimeError(f"a month not of the form YYYYMmm (or YYYY_mm) in the metadata: {bad[:5]}")
    return {"query": [{"code": x["code"], "selection": {"filter": "item", "values": x["values"]}} for x in (ind, time)],
            "response": {"format": "json-stat2"}}


def parse(js, meta, base):
    ind, time = meta["variables"]
    dims = js.get("id")
    if dims != [ind["code"], time["code"]]:
        raise RuntimeError(f"the answer's dimensions are not the two expected: {dims}")
    cats = []
    for d in dims:
        idx = js["dimension"][d]["category"]["index"]
        cats.append(sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx))
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{len(js['value'])} values for dimensions of size {js['size']}")
    months = dict(zip(time["values"], time["valueTexts"]))
    rows = []
    for k, (code, mcode) in enumerate(itertools.product(*cats)):
        v = js["value"][k]
        if v is None:
            continue
        m = MONTH.fullmatch(months[mcode])
        i = int(code)
        rows.append(dict(entity="makstat:mk", variable=VARIABLES[i], ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=float(v),
                         unit="MWh", freq="P1M", geo="MK", market="", node=LABELS[i], **base, x_code=str(i)))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an indicator and month given twice")
    return t


def plants_off(t):
    """Months whose plants differ from MakStat's total by more than 1 MWh a plant, gross and net."""
    out = []
    for kind in ("gross", "net"):
        w = t[t.variable.str.startswith(f"{kind}_production_")].pivot_table(index="ts_utc", columns="variable", values="value")
        if f"{kind}_production_total" not in w:
            continue
        parts = [c for c in w.columns if c != f"{kind}_production_total"]
        d = w[f"{kind}_production_total"] - w[parts].fillna(0).sum(axis=1)
        out += [f"{kind} {ts[:7]} {x:+,.0f}" for ts, x in d.items() if abs(x) > len(parts)]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="MakStat 125_Ene_Mk_EEmes_ml: North Macedonia's electricity, a month")
    ap.add_argument("--offline", action="store_true", help="the saved metadata and answer only, no request")
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
    path = os.path.join(ip.RAW_DIR, CONNECTOR, SAVED)
    try:
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        if args.offline:
            if not os.path.exists(path):
                raise RuntimeError(f"offline: no saved query at {path}")
            saved = json.load(open(path, encoding="utf-8"))
            meta, js, retrieved = saved["meta"], saved["answer"], saved["retrieved_at"]
            query(meta)
            log(f"  saved metadata and answer reused: {path} (retrieved {retrieved})")
        else:
            mcontent, _ = ip.fetch_raw(CONNECTOR, TABLE_URL, log, fresh=True, headers=UA, timeout=90, pause=1)
            meta = json.loads(mcontent.decode("utf-8-sig"))
            body = query(meta)
            r = requests.post(TABLE_URL, json=body, headers=UA, timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} for the query")
            js, retrieved = json.loads(r.content.decode("utf-8-sig")), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            json.dump({"retrieved_at": retrieved, "query": body, "meta": meta, "answer": js}, open(path, "w", encoding="utf-8"))
            log(f"  POST {TABLE_URL}: {len(r.content)} bytes, saved with the metadata as {path}")
        upd = js.get("updated", "") or ""
        if upd.startswith("9999"):  # a placeholder some PxWeb servers answer, not a date
            upd = ""
        base = dict(source=SOURCE, source_url=TABLE_URL, retrieved_at=retrieved, vintage=upd)
        t = parse(js, meta, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        off = plants_off(t)
        neg = t[(t.variable == "gross_inland_consumption") & (t.value < 0)].ts_utc.str[:7].tolist()  # impossible, kept as published
        g = t[t.variable == "gross_production_total"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        g = g[g["size"] == 12]["sum"] / 1e6
        head = [
            "Energy Research Warehouse (ERW): State Statistical Office of North Macedonia, MakStat table 125_Ene_Mk_EEmes_ml, Electricity "
            f"in MWh, by months, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2357)",
            "Shape: series (docs/datastandard.md v0). entity makstat:mk; variable imports, exports, gross_inland_consumption, "
            "gross_production_total and gross_production_<plant>, net_production_total and net_production_<plant> (thermal_power_plants, "
            "chp_and_autoproducer_thermal, hydro, solar, wind, biogas), energy_branch_consumption, distribution_losses, "
            "available_for_final_consumption, final_consumption_households; unit MWh as published; ts_utc the month's first day; freq "
            "P1M; geo MK; node the indicator as MakStat writes it; x_code its code.",
            f"{len(t)} rows, {t.variable.nunique()} indicators; gross production TWh a full year: "
            + ", ".join(f"{k} {v:.2f}" for k, v in g.items()) + ". Totals are MakStat's lines (a sum of rows double counts); months whose "
            f"plants differ from the total by more than 1 MWh a plant: {'; '.join(off) or 'none'}. Gross inland consumption is negative, "
            f"as published, in {len(neg)} month(s): {', '.join(neg) or 'none'}; net production of autoproducers' and CHP thermal plants "
            "can be negative (their own use above their output). A cell left empty has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/makstat_macedonia.py; the query answered {retrieved}; updated {base['vintage'] or 'not given'}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (the metadata and the answer; not in git)",
            f"Source: {SOURCE} State Statistical Office of North Macedonia, MakStat, Energy, Monthly energy statistics, {PAGE}",
            f"  access: {TABLE_URL} (the metadata by GET and one JSON-stat query by POST)",
            "License: internal until the licenses' round reads the State Statistical Office's terms. Source: State Statistical Office of North Macedonia.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} indicators, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}; plants off {len(off)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="State Statistical Office of North Macedonia (MakStat)",
                                    report="MakStat table 125_Ene_Mk_EEmes_ml: Electricity in MWh, by months",
                                    report_url=PAGE, document_list=TABLE_URL, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
