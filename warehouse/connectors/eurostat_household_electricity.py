#!/usr/bin/env python3
"""Eurostat's disaggregated final energy consumption in households (nrg_d_hhq), electricity only: each European country's
households' electricity a year by end use (space heating, space cooling, water heating, cooking, lighting and electrical
appliances, other end uses) and their total, from 2010 (session 2798, chain 142, the session's own choice, beside
eurostat_electricity_consumption_annual, session 2757, which holds the households' total from nrg_cb_e).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_household_electricity_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), one request (about 360 KB of SDMX-CSV, the households' balance items of
electricity, SIEC E7000, in GWh):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_d_hhq/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990

    entity      eurostat_household_electricity:<Eurostat geo code>
    variable    the end use (ITEMS below): total (FC_OTH_HH_E), space_heating (_SH), space_cooling (_SC), water_heating (_WH),
                cooking (_CK), lighting_appliances (_LE), other_end_use (_OE)
    unit        MWh: Eurostat's GWh times 1,000
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank for
                Eurostat's aggregate EU27_2020
    node        "<geo code> households' electricity, <the end use's NRG_BAL name>"
    x_*         Eurostat's geo and balance item codes, the observation's flag and confidentiality status

The balance items' names are Eurostat's NRG_BAL codelist's (session 2798 read it, beside this file), written here: the
dataset holds no other item for electricity. The six end uses sum to the total within 1 GWh in every country year that gives
all seven, a check that stops the run. A country year whose seven items are all zero is not written: no country's households
use no electricity, and these are the years a country did not report the split (nineteen countries a year in 2010 to 2012,
none from 2018); the header counts them. Other checks that stop the run: a header not Eurostat's; a unit, frequency, product
or balance item not expected; a value not a number; a key given twice. Countries kept: the EU's members, EFTA's and the
official candidates, with EU27_2020, as eurostat_electricity_consumption_annual keeps them (the United Kingdom, Kosovo and the
euro area aggregates left out). A blank has no row; any other zero is kept; nothing is filled.

    python warehouse/connectors/eurostat_household_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/eurostat_household_electricity/ with --offline. ec.europa.eu's robots file
disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2798,
read again, the same file as session 2790's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse
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

NAME = "eurostat_household_electricity_annual"
CONNECTOR = "eurostat_household_electricity"
SOURCE = "eurostat:nrg_d_hhq"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_d_hhq/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_d_hhq/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG",
          "CONF_STATUS"]
ITEMS = {"FC_OTH_HH_E": "total", "FC_OTH_HH_E_SH": "space_heating", "FC_OTH_HH_E_SC": "space_cooling",
         "FC_OTH_HH_E_WH": "water_heating", "FC_OTH_HH_E_CK": "cooking", "FC_OTH_HH_E_LE": "lighting_appliances",
         "FC_OTH_HH_E_OE": "other_end_use"}
NAMES = {"FC_OTH_HH_E": "Final consumption - other sectors - households - energy use",
         "FC_OTH_HH_E_SH": "Final consumption - other sectors - households - energy use - space heating",
         "FC_OTH_HH_E_SC": "Final consumption - other sectors - households - energy use - space cooling",
         "FC_OTH_HH_E_WH": "Final consumption - other sectors - households - energy use - water heating",
         "FC_OTH_HH_E_CK": "Final consumption - other sectors - households - energy use - cooking",
         "FC_OTH_HH_E_LE": "Final consumption - other sectors - households - energy use - lighting and electrical appliances",
         "FC_OTH_HH_E_OE": "Final consumption - other sectors - households - energy use - other end use"}
PARTS = [k for k in ITEMS if k != "FC_OTH_HH_E"]
TOL = 1.0   # GWh
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_nrg_bal", "x_flag", "x_conf_status"]


def build(content, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.unit) - {"GWH"}) + sorted(set(t0.freq) - {"A"}) + sorted(set(t0.siec) - {"E7000"}) \
        + sorted(set(t0.nrg_bal) - set(ITEMS))
    if bad:
        raise RuntimeError(f"a unit, frequency, product or balance item not expected: {bad}")
    missing = sorted(set(ITEMS) - set(t0.nrg_bal))
    if missing:
        raise RuntimeError(f"a balance item is not in the file: {missing}")
    counts = {"zero": 0, "blank": 0, "left_out_geo": sorted(set(t0.geo) - KEPT),
              "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if v == "":
            counts["blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.nrg_bal} {r.TIME_PERIOD}: not a number: {v!r}")
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        rows.append({"entity": f"eurostat_household_electricity:{r.geo}", "variable": ITEMS[r.nrg_bal],
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": round(value * 1000.0, 3), "unit": "MWh",
                     "freq": "P1Y", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                     "market": "", "node": f"{r.geo} households' electricity, {NAMES[r.nrg_bal]}", "source": SOURCE,
                     "source_url": url, "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo,
                     "x_nrg_bal": r.nrg_bal, "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    allzero = t.groupby(["x_geo_code", "ts_utc"]).value.agg(lambda s: bool((s == 0).all()))
    unreported = sorted(allzero[allzero].index)
    t = t[~t.set_index(["x_geo_code", "ts_utc"]).index.isin(unreported)]
    counts["unreported"] = unreported
    counts["zero"] = int((t.value == 0).sum())
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), counts


def checks(t):
    """The six end uses against the total (a stop): the country years compared."""
    p = t.assign(gwh=t.value / 1000.0).pivot_table(index=["x_geo_code", "ts_utc"], columns="x_nrg_bal", values="gwh", aggfunc="first")
    whole = p.reindex(columns=PARTS + ["FC_OTH_HH_E"]).dropna()
    d = whole[PARTS].sum(axis=1) - whole["FC_OTH_HH_E"]
    if (d.abs() > TOL).any():
        k = d.abs().idxmax()
        raise RuntimeError(f"{k[0]} {k[1][:4]}: the six end uses are not the households' total ({d[k]:+.3f} GWh)")
    return len(d), (float(d.abs().max()) if len(d) else 0.0)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_d_hhq: European households' electricity by end use, a year")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
        t, counts = build(content, URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        compared, worst = checks(t)
        for geo, ts in counts["unreported"]:
            log(f"  all seven items zero, not written: {geo} {ts[:4]}")
        by_year = pd.Series([ts[:4] for _, ts in counts["unreported"]]).value_counts().sort_index()
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, disaggregated final energy consumption in households, electricity, annual (nrg_d_hhq, E7000): households' electricity by end use and its total, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2798)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_household_electricity:<geo>; variable the end use (total FC_OTH_HH_E; space_heating, space_cooling, water_heating, cooking, lighting_appliances, other_end_use); unit MWh (Eurostat's GWh times 1,000); "
            "ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020; x_nrg_bal Eurostat's code.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.variable.nunique()} items. The six end uses sum to the total within {TOL:g} GWh in all {compared:,} country years that give all seven (the largest difference {worst:.3f} GWh). "
            f"{len(counts['unreported'])} country years whose seven items are all zero (the split not reported) are not written ({', '.join(f'{y} {n}' for y, n in by_year.items()) or 'none'}); {counts['zero']:,} other zeros are kept as Eurostat prints them; "
            f"{counts['blank']:,} blanks have no row; nothing is filled. Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_household_electricity.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Disaggregated final energy consumption in households, quantities (nrg_d_hhq), {PAGE}",
            f"  access: {URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_d_hhq. Eurostat bears no responsibility for this reshaping (GWh written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Disaggregated final energy consumption in households, quantities (nrg_d_hhq)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; {compared:,} country years checked (largest {worst:.3f} GWh); {len(counts['unreported'])} unreported not written; zeros kept {counts['zero']:,}; left out {counts['left_out_geo']}")
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
