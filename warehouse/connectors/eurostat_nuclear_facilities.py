#!/usr/bin/env python3
"""Eurostat's nuclear energy facilities (nrg_inf_nuc): each European country's nuclear fuel cycle a year, its enrichment
capacity, the production and capacity of its fresh fuel and MOX fuel plants and of its reprocessing plants, and its nuclear
heat production (session 2812, chain 143, the session's own choice, from session 2799's reading of Eurostat's dataflow list).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_nuclear_fuel_cycle_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), two requests: the data (about 380 KB of SDMX-CSV, the whole dataset) and the
PLANT_TEC codelist (the items' names):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_nuc?format=SDMX-CSV&compressed=false
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/PLANT_TEC?format=TSV

    entity      eurostat_nuclear:<Eurostat geo code>
    variable    the item (ITEMS below): enrichment_capacity (CAP_EN), fresh_fuel_production (PRD_FF) and
                fresh_fuel_production_capacity (PRDCAP_FF), mox_fuel_production (PRD_MOXF) and mox_fuel_production_capacity
                (PRDCAP_MOXF), reprocessing_production (PRD_UP, uranium and plutonium) and reprocessing_capacity (CAP_UP),
                nuclear_heat_production (PRD_NUCH)
    unit        SWU (Eurostat's tSWU times 1,000), t (tonnes of heavy metal, Eurostat's THM), or MWh (nuclear heat: Eurostat's
                ktoe times 11,630, one tonne of oil equivalent being 41.868 GJ, 11.63 MWh)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank for
                Eurostat's aggregates (EU27_2020)
    node        "<geo code> nuclear facilities, <the PLANT_TEC name>"
    x_*         Eurostat's geo and item codes, its unit, the observation's flag and confidentiality status

Not written: the annual average burnup of discharged fuel (BAA_IRRADF, GWd/tHM), a unit the ERW does not hold. A blank (flag m,
or a confidential observation, status C) has no row and is counted; zeros are kept (most countries have no fuel cycle plant);
nothing is filled. Compared: each plant type's production against its capacity, a production above its capacity counted in the
header and listed in the run log, kept as published. Checks that stop the run: a header not Eurostat's; an item or unit not
expected, or an item in another unit; a value not a number, or negative; a period not a year; a key given twice. Countries
kept: the EU's members, EFTA's and the official candidates, with EU27_2020, as eurostat_electricity_consumption_annual keeps
them.

    python warehouse/connectors/eurostat_nuclear_facilities.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_nuclear_facilities/ with --offline. ec.europa.eu's robots file
disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2812,
read again, the same file as session 2806's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse
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

NAME = "eurostat_nuclear_fuel_cycle_annual"
CONNECTOR = "eurostat_nuclear_facilities"
SOURCE = "eurostat:nrg_inf_nuc"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_inf_nuc/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_nuc?format=SDMX-CSV&compressed=false"
CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/PLANT_TEC?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "plant_tec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
ITEMS = {"CAP_EN": ("enrichment_capacity", "TSWU", "SWU", 1000.0),
         "PRD_FF": ("fresh_fuel_production", "THM", "t", 1.0),
         "PRDCAP_FF": ("fresh_fuel_production_capacity", "THM", "t", 1.0),
         "PRD_MOXF": ("mox_fuel_production", "THM", "t", 1.0),
         "PRDCAP_MOXF": ("mox_fuel_production_capacity", "THM", "t", 1.0),
         "PRD_UP": ("reprocessing_production", "THM", "t", 1.0),
         "CAP_UP": ("reprocessing_capacity", "THM", "t", 1.0),
         "PRD_NUCH": ("nuclear_heat_production", "KTOE", "MWh", 11630.0)}
NOT_WRITTEN = {"BAA_IRRADF": "GWD_THM"}
PAIRS = [("PRD_FF", "PRDCAP_FF"), ("PRD_MOXF", "PRDCAP_MOXF"), ("PRD_UP", "CAP_UP")]
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_plant_tec", "x_unit", "x_flag", "x_conf_status"]


def item_names(content):
    names = {}
    for line in content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        code, _, label = line.partition("\t")
        if not label:
            raise RuntimeError(f"the PLANT_TEC codelist: a line without a name: {line[:80]!r}")
        names[code.strip()] = label.strip()
    if any(k not in names for k in ITEMS) or not names.get("PRD_NUCH", "").startswith("Production of nuclear heat"):
        raise RuntimeError("the PLANT_TEC codelist is not Eurostat's, or lacks an item")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    expected = {k: v[1] for k, v in ITEMS.items()} | NOT_WRITTEN
    bad = sorted(set(t0.freq) - {"A"}) + sorted({f"{a} in {b}" for a, b in zip(t0.plant_tec, t0.unit) if expected.get(a) != b})
    if bad:
        raise RuntimeError(f"a frequency, item or unit not expected: {bad}")
    counts = {"blank": 0, "confidential": 0, "zero": 0, "not_written": int(t0.plant_tec.isin(NOT_WRITTEN).sum()),
              "left_out_geo": sorted(set(t0.geo) - KEPT), "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT) & t0.plant_tec.isin(ITEMS)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        if v == "":
            counts["confidential" if r.CONF_STATUS.strip() == "C" else "blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.plant_tec} {r.TIME_PERIOD}: not a number: {v!r}")
        if value < 0:
            raise RuntimeError(f"{r.geo} {r.plant_tec} {r.TIME_PERIOD}: a negative value: {v!r}")
        if value == 0:
            counts["zero"] += 1
        var, _, unit, k = ITEMS[r.plant_tec]
        rows.append({"entity": f"eurostat_nuclear:{r.geo}", "variable": var, "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z",
                     "value": round(value * k, 3), "unit": unit, "freq": "P1Y",
                     "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo), "market": "",
                     "node": f"{r.geo} nuclear facilities, {names[r.plant_tec]}", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_plant_tec": r.plant_tec,
                     "x_unit": r.unit, "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), counts


def checks(t):
    """Each plant type's production against its capacity: (compared, those above)."""
    p = t.pivot_table(index=["x_geo_code", "ts_utc"], columns="x_plant_tec", values="value", aggfunc="first")
    n, above = 0, []
    for prd, cap in PAIRS:
        if prd in p.columns and cap in p.columns:
            x = p[[prd, cap]].dropna()
            n += len(x)
            above += [(g, ts[:4], prd, float(a), float(b)) for (g, ts), a, b in zip(x.index, x[prd], x[cap]) if a > b]
    return n, above


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_inf_nuc: Europe's nuclear fuel cycle facilities, a year")
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
        if not args.offline and (ip.paused("eurostat") or ip.paused_host("ec.europa.eu")):
            raise RuntimeError("Eurostat is paused (warehouse/metadata/paused_sources.csv): not requested")
        codes, _ = ip.fetch_raw(CONNECTOR, CODES_URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, pause=2, headers=UA, timeout=180)
        t, counts = build(content, item_names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        if t.empty:
            raise RuntimeError("no observation kept")
        n, above = checks(t)
        for x in above:
            log(f"  production above its capacity, kept as published: {x}")
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, nuclear energy facilities, annual (nrg_inf_nuc): enrichment capacity, fresh and MOX fuel and reprocessing plants' production and capacity, nuclear heat production, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2812)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_nuclear:<geo>; variable enrichment_capacity (unit SWU, Eurostat's tSWU times 1,000), fresh_fuel_production, fresh_fuel_production_capacity, mox_fuel_production, mox_fuel_production_capacity, reprocessing_production, reprocessing_capacity (unit t, tonnes of heavy metal), "
            "nuclear_heat_production (unit MWh, Eurostat's ktoe times 11,630); ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020; x_plant_tec and x_unit Eurostat's codes.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.variable.nunique()} items. Production against capacity in {n:,} country-year-plant comparisons: {len(above)} above, kept as published and listed in the run log. Zeros are kept ({counts['zero']:,}); {counts['blank']} blanks and {counts['confidential']} confidential observations have no row; "
            f"the burnup (BAA_IRRADF, GWd/tHM, {counts['not_written']} observations) is not written, its unit not the ERW's; nothing is filled. Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_nuclear_facilities.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Nuclear energy facilities (nrg_inf_nuc), {PAGE}",
            f"  access: {URL} and the items' names from {CODES_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_inf_nuc. Eurostat bears no responsibility for this reshaping (tSWU written as SWU, ktoe as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Nuclear energy facilities (nrg_inf_nuc)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; production above capacity {len(above)} of {n}; zeros {counts['zero']}, blanks {counts['blank']}, confidential {counts['confidential']}; left out {counts['left_out_geo']}")
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
