#!/usr/bin/env python3
"""Eurostat's supply, transformation and consumption of electricity (nrg_cb_e): each European country's electricity available
for final consumption a year, its final consumption by sector (industry, transport, commercial and public services, households,
agriculture and forestry, fishing, not elsewhere specified), the energy sector's own use, losses and the statistical difference,
from 1990 (session 2757, chain 139, the session's own choice, beside eurostat_electricity_production_annual, session 2413).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_electricity_consumption_annual.csv, from
Eurostat's SDMX 2.1 dissemination API (no key), two requests: the data (about 6 MB of SDMX-CSV, every balance item of electricity,
SIEC E7000, in GWh) and the NRG_BAL codelist (the balance items' names):

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_e/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV

    entity      eurostat_electricity_consumption:<Eurostat geo code>
    variable    the balance item (ITEMS below): available_for_final_consumption (AFC), final_consumption (FC), energy_sector_use
                (NRG_E), losses (LOSS), statistical_differences (STATDIFF), and final consumption's energy use by sector:
                industry (FC_IND_E), transport (FC_TRA_E), commercial_public_services (FC_OTH_CP_E), households (FC_OTH_HH_E),
                agriculture_forestry (FC_OTH_AF_E), fishing (FC_OTH_FISH_E), other_not_specified (FC_OTH_NSP_E)
    unit        MWh: Eurostat's GWh times 1,000
    ts_utc      the year's 1 January at 00:00:00Z; freq P1Y; geo the country's ISO alpha-2 (Eurostat's EL is GR), blank for
                Eurostat's aggregate EU27_2020
    node        "<geo code> electricity, <the NRG_BAL name>"
    x_*         Eurostat's geo and balance item codes, the observation's flag and confidentiality status

The file's other balance items (production, trade, the transformation input, the industry and transport sectors' branches, the
energy sector's branches, the loss items' parts) are not written: production and trade are held already
(eurostat_electricity_production_annual, eurostat_electricity_trade_annual), and the branches are a later table's. In this dataset
Eurostat's final consumption (FC) includes the energy sector's own use: FC equals NRG_E plus the seven sectors, which the
header counts within 1 GWh, the country years where it does not hold kept as Eurostat publishes them and listed in the run log
(2025 so far gives the totals without the sectors). Checks that stop the run: a header not Eurostat's; a unit, frequency, product
or balance item not expected; a value not a number; a key given twice; AFC not FC plus STATDIFF within 1 GWh in a country year
that has all three. Countries kept: the EU's members, EFTA's and the official candidates, with EU27_2020, as
eurostat_electricity_production_annual keeps them (the United Kingdom, Kosovo and the euro area aggregate left out). A blank has
no row; zeros are kept; nothing is filled.

    python warehouse/connectors/eurostat_electricity_consumption.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/eurostat_electricity_consumption/ with --offline. ec.europa.eu's robots file
disallows the old SDMX path and the search pages, not /eurostat/api/dissemination/, and names no Claude agent (session 2757,
read 1507). License: Eurostat's copyright notice (the record's verdict, session 2123): reuse with the source acknowledged;
source: Eurostat.
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

NAME = "eurostat_electricity_consumption_annual"
CONNECTOR = "eurostat_electricity_consumption"
SOURCE = "eurostat:nrg_cb_e"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_e/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_e/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990"
CODES_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "nrg_bal", "siec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG",
          "CONF_STATUS"]
ITEMS = {"AFC": "available_for_final_consumption", "FC": "final_consumption", "NRG_E": "energy_sector_use", "LOSS": "losses",
         "STATDIFF": "statistical_differences", "FC_IND_E": "industry", "FC_TRA_E": "transport",
         "FC_OTH_CP_E": "commercial_public_services", "FC_OTH_HH_E": "households", "FC_OTH_AF_E": "agriculture_forestry",
         "FC_OTH_FISH_E": "fishing", "FC_OTH_NSP_E": "other_not_specified"}
SECTORS = ["FC_IND_E", "FC_TRA_E", "FC_OTH_CP_E", "FC_OTH_HH_E", "FC_OTH_AF_E", "FC_OTH_FISH_E", "FC_OTH_NSP_E"]
TOL = 1.0   # GWh
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
    if names.get("FC") != "Final consumption" or any(k not in names for k in ITEMS):
        raise RuntimeError("the NRG_BAL codelist is not Eurostat's, or lacks a balance item kept")
    return names


def build(content, names, url, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t0.columns)}")
    bad = sorted(set(t0.unit) - {"GWH"}) + sorted(set(t0.freq) - {"A"}) + sorted(set(t0.siec) - {"E7000"}) \
        + sorted(set(t0.nrg_bal) - set(names))
    if bad:
        raise RuntimeError(f"a unit, frequency, product or balance item not expected: {bad}")
    missing = sorted(set(ITEMS) - set(t0.nrg_bal))
    if missing:
        raise RuntimeError(f"a balance item kept is not in the file: {missing}")
    counts = {"zero": 0, "blank": 0, "left_out_geo": sorted(set(t0.geo) - KEPT),
              "left_out_items": len(set(t0.nrg_bal) - set(ITEMS)), "last_update": ", ".join(sorted(set(t0["LAST UPDATE"])))}
    rows = []
    for r in t0[t0.geo.isin(KEPT) & t0.nrg_bal.isin(ITEMS)].itertuples(index=False):
        v = r.OBS_VALUE.strip()
        if v == "":
            counts["blank"] += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r.geo} {r.nrg_bal} {r.TIME_PERIOD}: not a number: {v!r}")
        if value == 0:
            counts["zero"] += 1
        if not re.fullmatch(r"\d{4}", r.TIME_PERIOD):
            raise RuntimeError(f"a period not a year: {r.TIME_PERIOD!r}")
        rows.append({"entity": f"eurostat_electricity_consumption:{r.geo}", "variable": ITEMS[r.nrg_bal],
                     "ts_utc": f"{r.TIME_PERIOD}-01-01T00:00:00Z", "value": round(value * 1000.0, 3), "unit": "MWh",
                     "freq": "P1Y", "geo": "" if r.geo in AGGREGATES else ("GR" if r.geo == "EL" else r.geo),
                     "market": "", "node": f"{r.geo} electricity, {names[r.nrg_bal]}", "source": SOURCE,
                     "source_url": url, "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": r.geo,
                     "x_nrg_bal": r.nrg_bal, "x_flag": r.OBS_FLAG.strip(), "x_conf_status": r.CONF_STATUS.strip()})
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), counts


def checks(t):
    """AFC against FC plus STATDIFF (a stop), and FC against NRG_E plus the sectors (counted): the country years compared and
    those off by more than TOL GWh."""
    p = t.assign(gwh=t.value / 1000.0).pivot_table(index=["x_geo_code", "ts_utc"], columns="x_nrg_bal", values="gwh", aggfunc="first")
    a = (p["FC"] + p["STATDIFF"] - p["AFC"]).dropna()
    if (a.abs() > TOL).any():
        k = a.abs().idxmax()
        raise RuntimeError(f"{k[0]} {k[1][:4]}: available for final consumption is not final consumption plus the statistical "
                           f"difference ({a[k]:+.3f} GWh)")
    whole = p[SECTORS + ["NRG_E", "FC"]].dropna()
    d = whole[SECTORS + ["NRG_E"]].sum(axis=1) - whole["FC"]
    return len(a), len(d), d[d.abs() > TOL]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_cb_e: European electricity consumption by sector, a year")
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
        n_afc, compared, off = checks(t)
        for (geo, ts), g in off.sort_values().items():
            log(f"  NRG_E plus the seven sectors less FC: {g:.3f} GWh, {geo} {ts[:4]}")
        by_geo = off.groupby(level=0).size().sort_values(ascending=False)
        worst = f"; the largest {off.abs().max():.1f} GWh ({off.abs().idxmax()[0]} {off.abs().idxmax()[1][:4]})" if len(off) else ""
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, supply, transformation and consumption of electricity, annual (nrg_cb_e, E7000): available for final consumption, final consumption by sector, the energy sector's use, losses and statistical differences, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2757)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_electricity_consumption:<geo>; variable the balance item (available_for_final_consumption AFC, final_consumption FC, energy_sector_use NRG_E, losses LOSS, statistical_differences STATDIFF; the sectors' energy use industry, transport, "
            "commercial_public_services, households, agriculture_forestry, fishing, other_not_specified); unit MWh (Eurostat's GWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (EL is GR), blank for EU27_2020; x_nrg_bal Eurostat's code. "
            "In this dataset FC includes the energy sector's own use: FC = NRG_E + the seven sectors.",
            f"{len(t)} rows, {t.x_geo_code.nunique()} areas, {t.variable.nunique()} balance items ({counts['left_out_items']} other items in the file not written). Zeros are kept as Eurostat prints them ({counts['zero']:,}); {counts['blank']:,} blanks have no row; nothing is filled. "
            f"AFC equals FC plus STATDIFF within {TOL:g} GWh in all {n_afc:,} country years. FC equals NRG_E plus the seven sectors within {TOL:g} GWh in {compared - len(off):,} of {compared:,} country years that give all eight; the other {len(off)} "
            f"({', '.join(f'{g} {n}' for g, n in by_geo.items()) or 'none'}) are kept as Eurostat publishes them and listed in the run log{worst}. "
            f"Areas left out: {' '.join(counts['left_out_geo']) or 'none'}. Eurostat's last update, as its file gives it (no time zone): {counts['last_update']}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_electricity_consumption.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Supply, transformation and consumption of electricity (nrg_cb_e), {PAGE}",
            f"  access: {URL} and the balance items' names from {CODES_URL}",
            "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_cb_e. Eurostat bears no responsibility for this reshaping (GWh written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Supply, transformation and consumption of electricity (nrg_cb_e)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; zeros kept {counts['zero']:,}, blanks {counts['blank']:,}; FC off in {len(off)} of {compared:,}{worst}; left out {counts['left_out_geo']}")
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
