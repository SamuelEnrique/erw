#!/usr/bin/env python3
"""Eurostat's shares of energy from renewable sources (nrg_ind_ren, the Renewable Energy Directive's SHARES results): each
European country's renewable share of gross final energy consumption a year from 2004, overall and in electricity, heating and
cooling and transport, with the newer district heating and cooling and waste heat shares (session 2762, chain 139, the session's
own choice, beside eurostat_electricity_production_annual and eurostat_electricity_consumption_annual).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_renewable_shares_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), two requests: the whole dataset (about 0.2 MB of SDMX-CSV, every key) and the
NRG_BAL codelist (the shares' names):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ren/A...?format=SDMX-CSV&compressed=false
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV

    entity      eurostat_renewable_shares:<Eurostat geo code>
    variable    the share (ITEMS below): renewable_share_overall (REN), renewable_share_electricity (REN_ELC),
                renewable_share_heating_cooling (REN_HEAT_CL), renewable_share_transport (REN_TRA),
                renewable_waste_heat_share_district_heating_cooling (REN_WHC_DHEAT_DCL), waste_heat_share_heating_cooling
                (REN_HEAT_CL_WHC)
    unit        pct (Eurostat's PC, per cent of the sector's gross final consumption, as Eurostat computes it under the
                directive: hydro and wind normalised, multipliers in transport)
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank for
                Eurostat's aggregate EU27_2020
    node        "<geo code> share, <the NRG_BAL name>"
    x_*         Eurostat's geo and balance item codes, the observation's flag (p, provisional) and confidentiality status

Checks that stop the run: a header not Eurostat's; a unit other than PC, a frequency other than A, or a share not in ITEMS; a
value not a number or below 0; a key given twice. A share above 100 is kept (electricity can exceed 100 where renewable output,
normalised, exceeds consumption) and counted in the header. Countries kept: the EU's members, EFTA's and the official candidates,
with EU27_2020, as eurostat_electricity_production_annual keeps them (Kosovo left out). A blank has no row; zeros are kept;
nothing is filled.

    python warehouse/connectors/eurostat_renewable_shares.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_renewable_shares/ with --offline. ec.europa.eu's robots file leaves
/eurostat/api/dissemination/ open and names no Claude agent (session 2762, read 1508). License: Eurostat's copyright notice (the
record's verdict, session 2123): reuse with the source acknowledged; source: Eurostat.
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

NAME = "eurostat_renewable_shares_annual"
CONNECTOR = "eurostat_renewable_shares"
SOURCE = "eurostat:nrg_ind_ren"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_ren/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ren/A...?format=SDMX-CSV&compressed=false"
CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "CONF_STATUS"]
ITEMS = {"REN": "renewable_share_overall", "REN_ELC": "renewable_share_electricity",
         "REN_HEAT_CL": "renewable_share_heating_cooling", "REN_TRA": "renewable_share_transport",
         "REN_WHC_DHEAT_DCL": "renewable_waste_heat_share_district_heating_cooling",
         "REN_HEAT_CL_WHC": "waste_heat_share_heating_cooling"}
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
    if names.get("REN") != "Renewable energy - overall" or any(k not in names for k in ITEMS):
        raise RuntimeError("the NRG_BAL codelist is not Eurostat's, or lacks a share kept")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.unit) - {"PC"}) + sorted(set(t0.freq) - {"A"}) + sorted(set(t0.nrg_bal) - set(ITEMS))
    if bad:
        raise RuntimeError(f"a unit, frequency or share not expected: {bad}")
    counts = {"zero": 0, "blank": 0, "over_100": 0, "provisional": 0, "left_out_geo": sorted(set(t0.geo) - KEPT),
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
        if value < 0:
            raise RuntimeError(f"{r.geo} {r.nrg_bal} {r.TIME_PERIOD}: a share below 0: {value}")
        counts["zero"] += value == 0
        counts["over_100"] += value > 100
        counts["provisional"] += r.OBS_FLAG.strip() == "p"
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        rows.append({"entity": f"eurostat_renewable_shares:{r.geo}", "variable": ITEMS[r.nrg_bal],
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": value, "unit": "pct",
                     "freq": "P1Y", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                     "market": "", "node": f"{r.geo} share, {names[r.nrg_bal]}", "source": SOURCE,
                     "source_url": url, "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo,
                     "x_nrg_bal": r.nrg_bal, "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_ind_ren: European renewable energy shares, a year")
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
        eu = t[(t.x_geo_code == "EU27_2020") & (t.variable == "renewable_share_overall")].set_index("ts_utc").value
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, shares of energy from renewable sources (nrg_ind_ren, SHARES), overall and in electricity, heating and cooling and transport, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2762)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_renewable_shares:<geo>; variable renewable_share_overall REN, renewable_share_electricity REN_ELC, renewable_share_heating_cooling REN_HEAT_CL, renewable_share_transport REN_TRA, "
            "renewable_waste_heat_share_district_heating_cooling REN_WHC_DHEAT_DCL, waste_heat_share_heating_cooling REN_HEAT_CL_WHC; unit pct (of the sector's gross final consumption, Eurostat's directive method: hydro and wind normalised, transport multipliers); "
            "ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020; x_nrg_bal Eurostat's code; x_flag p is provisional.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.variable.nunique()} shares; {counts['provisional']} provisional, {counts['over_100']} above 100 (kept), {counts['zero']} zeros kept, {counts['blank']} blanks without a row; nothing is filled. "
            "The EU27's overall share: " + ", ".join(f"{k[:4]} {eu[k]:.2f}" for k in eu.index if k[:4] in ("2004", "2014", "2024")) + ". "
            f"Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_renewable_shares.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Share of energy from renewable sources (nrg_ind_ren), {PAGE}",
            f"  access: {URL} and the shares' names from {CODES_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_ind_ren. Eurostat bears no responsibility for this reshaping.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Share of energy from renewable sources (nrg_ind_ren)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; provisional {counts['provisional']}, above 100 {counts['over_100']}; left out {counts['left_out_geo']}")
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
