#!/usr/bin/env python3
"""Eurostat's rate of electrification (nrg_ind_re): the share of electricity in each European country's final energy
consumption a year, overall and by sector and branch (industry and its thirteen branches, transport and its modes, households,
services, agriculture, fishing) and in the energy sector's own use, from 1990 (session 2806, chain 143, in place of INE Portugal,
whose www and bare names answer HTTP 403 at their robots files).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_electrification_rate_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), two requests: the data (about 3 MB of SDMX-CSV, the whole dataset) and the
NRG_BAL codelist (the balance items' names):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_re?format=SDMX-CSV&compressed=false
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV

    entity      eurostat_electrification:<Eurostat geo code>:<NRG_BAL code>, the balance item whose energy use is measured
                (FC_E final consumption's energy use; FC_IND_E industry, FC_TRA_E transport, FC_OTH_E other sectors and their
                parts; NRG_E the energy sector's own use and its parts)
    variable    electrification_rate
    unit        pct (electricity's share of the item's energy use, as Eurostat gives it)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank for
                Eurostat's aggregate EU27_2020
    node        "<geo code> electrification rate, <the NRG_BAL name>"
    x_*         Eurostat's geo and balance item codes, the observation's flag and confidentiality status

Final consumption's energy use is the sum of industry's, transport's and the other sectors', so its rate lies between theirs;
households' and services' together lie between households' and services'. Both are compared in every country year that gives
the three (or two) rates, within 0.01 points, and the cases where they do not hold are counted in the header and listed in the
run log, kept as Eurostat publishes them. Checks that stop the run: a header not Eurostat's; a unit, frequency or balance item
not expected; a value not a number, or outside 0 to 100; a period not a year; a key given twice. A blank (Eurostat's flag m,
missing) has no row; zeros are kept; nothing is filled. Countries kept: the EU's members, EFTA's and the official candidates,
with EU27_2020, as eurostat_electricity_consumption_annual keeps them (the United Kingdom, Kosovo and EU28 left out).

    python warehouse/connectors/eurostat_electrification.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_electrification/ with --offline. ec.europa.eu's robots file disallows
the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2806, read again,
the same file as session 2804's). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the
source acknowledged; source: Eurostat.
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

NAME = "eurostat_electrification_rate_annual"
CONNECTOR = "eurostat_electrification"
SOURCE = "eurostat:nrg_ind_re"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_re/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_re?format=SDMX-CSV&compressed=false"
CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
TOL = 0.01   # points
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
KEPT = EU | {"CH", "IS", "LI", "NO"} | {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"} | {"EU27_2020"}
AGGREGATES = {"EU27_2020"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_nrg_bal", "x_flag", "x_conf_status"]


def item_names(content):
    names = {}
    for line in content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        code, _, label = line.partition("\t")
        if not label:
            raise RuntimeError(f"the NRG_BAL codelist: a line without a name: {line[:80]!r}")
        names[code.strip()] = label.strip()
    if names.get("FC_E") != "Final consumption - energy use":
        raise RuntimeError("the NRG_BAL codelist is not Eurostat's")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.unit) - {"PC"}) + sorted(set(t0.freq) - {"A"}) + sorted(set(t0.nrg_bal) - set(names))
    if bad:
        raise RuntimeError(f"a unit, frequency or balance item not expected: {bad}")
    counts = {"zero": 0, "blank": 0, "left_out_geo": sorted(set(t0.geo) - KEPT),
              "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        if v == "":
            counts["blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.nrg_bal} {r.TIME_PERIOD}: not a number: {v!r}")
        if not 0 <= value <= 100:
            raise RuntimeError(f"{r.geo} {r.nrg_bal} {r.TIME_PERIOD}: a share outside 0 to 100: {v!r}")
        if value == 0:
            counts["zero"] += 1
        rows.append({"entity": f"eurostat_electrification:{r.geo}:{r.nrg_bal}", "variable": "electrification_rate",
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": value, "unit": "pct", "freq": "P1Y",
                     "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo), "market": "",
                     "node": f"{r.geo} electrification rate, {names[r.nrg_bal]}", "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo, "x_nrg_bal": r.nrg_bal,
                     "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "ts_utc"]).reset_index(drop=True), counts


def between(p, whole, parts):
    """The country years where `whole` lies outside its parts' range by more than TOL: (compared, those outside)."""
    if whole not in p.columns or any(k not in p.columns for k in parts):
        return 0, []
    x = p[[whole] + parts].dropna()
    lo, hi = x[parts].min(axis=1), x[parts].max(axis=1)
    off = x[(x[whole] < lo - TOL) | (x[whole] > hi + TOL)]
    return len(x), [(g, ts[:4], round(float(w), 3)) for (g, ts), w in off[whole].items()]


def checks(t):
    p = t.pivot_table(index=["x_geo_code", "ts_utc"], columns="x_nrg_bal", values="value", aggfunc="first")
    return {"final": between(p, "FC_E", ["FC_IND_E", "FC_TRA_E", "FC_OTH_E"]),
            "households_services": between(p, "FC_OTH_HH_CP_E", ["FC_OTH_HH_E", "FC_OTH_CP_E"])}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ind_re: the rate of electrification in Europe, a year")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, pause=2, headers=UA, timeout=300)
        t, counts = build(content, item_names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        if t.empty:
            raise RuntimeError("no observation kept")
        ck = checks(t)
        for k, (_, off) in ck.items():
            for g, y, w in off:
                log(f"  {k}: outside its parts' range, kept as published: {g} {y} ({w})")
        (nf, of), (nh, oh) = ck["final"], ck["households_services"]
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, rate of electrification by end-user, annual (nrg_ind_re): electricity's share of final energy consumption by sector and branch, and of the energy sector's own use, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2806)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_electrification:<geo>:<NRG_BAL code>; variable electrification_rate; unit pct (Eurostat's PC); ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020; x_nrg_bal Eurostat's code.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.x_nrg_bal.nunique()} balance items. Final consumption's rate lies within industry's, transport's and the other sectors' (within {TOL:g} points) in {nf - len(of):,} of {nf:,} country years, households' and services' together within theirs in {nh - len(oh):,} of {nh:,}; "
            f"the others ({len(of)} and {len(oh)}) are kept as Eurostat publishes them and listed in the run log. Zeros are kept ({counts['zero']:,}); {counts['blank']:,} blanks (flag m) have no row; nothing is filled. Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. "
            f"Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_electrification.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Rate of electrification by end-user (nrg_ind_re), {PAGE}",
            f"  access: {URL} and the balance items' names from {CODES_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_ind_re. Eurostat bears no responsibility for this reshaping.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Rate of electrification by end-user (nrg_ind_re)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; final within {nf - len(of)} of {nf}, households and services within {nh - len(oh)} of {nh}; zeros {counts['zero']}, blanks {counts['blank']}; left out {counts['left_out_geo']}")
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
