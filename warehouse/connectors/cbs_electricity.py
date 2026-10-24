#!/usr/bin/env python3
"""The Netherlands' electricity balance, a month from January 1976, as Statistics Netherlands (CBS) publishes it (table
84575NED, "Elektriciteitsbalans; aanbod en verbruik"): gross and net production by source, imports and exports by
country, distribution losses and net consumption (session 2231, chain 099: a source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cbs_netherlands_electricity_monthly.csv,
from CBS's dataset download (a zip of semicolon-separated files):

    https://datasets.cbs.nl/csv/CBS/nl/84575NED   Observations.csv (Measure, Perioden, Value, ValueAttribute),
                                                  MeasureCodes.csv (the 30 measures, all "mln kWh"),
                                                  PeriodenCodes.csv (the periods and their status)

    entity      cbs:nl
    variable    the measure's English name in this connector's map of CBS's 30 codes (gross_production, own_use,
                net_production, net_nuclear, net_fuels, net_coal, net_oil_products, net_natural_gas, net_biomass,
                net_other_fuels, net_hydro, net_wind, net_wind_onshore, net_wind_offshore, net_solar, net_other_sources,
                import, import_belgium, ..., export, export_norway, distribution_losses, net_consumption); node CBS's
                Dutch name; x_measure CBS's code; x_status the period's status (Definitief, NaderVoorlopig, Voorlopig)
    unit        MWh (CBS's million kWh times 1,000); ts_utc the month's first day; freq P1M; geo NL

Only the monthly periods (CBS's "MM" codes) are taken; the years and quarters are not. CBS's description: "Volledige
gegevens per maand zijn beschikbaar vanaf 2015. Vanaf 1936 per jaar en vanaf 1976 per maand zijn alleen de totale
productie, invoer en uitvoer bekend" (complete monthly figures from 2015; from 1976 a month only the total production,
imports and exports); a cell CBS leaves empty has no row. Totals are CBS's measures, never sums made here. A measure code
not in the map, a unit other than "mln kWh", a period code of another form, a value that is not a number or a month given
twice stops the run. Nothing is filled.

    python warehouse/connectors/cbs_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request (the zip), saved in warehouse/raw/cbs_electricity/ and reused offline. opendata.cbs.nl's robots file
disallows its OData paths, which this connector does not use; datasets.cbs.nl has no robots file (HTTP 404, session
2231). License: CC BY 4.0, as the table's own properties and CBS's catalog state (License
https://creativecommons.org/licenses/by/4.0/); source "CBS".
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "cbs_netherlands_electricity_monthly"
CONNECTOR = "cbs_electricity"
SOURCE = "cbs:84575NED"
URL = "https://datasets.cbs.nl/csv/CBS/nl/84575NED"
PAGE = "https://dataportal.cbs.nl/detail/CBS/84575NED"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COUNTRIES = {"L008552": "belgium", "L008588": "denmark", "L008592": "germany", "L008776": "united_kingdom", "L008704": "norway"}
NAMES = {"M002264": "gross_production", "M002431": "own_use", "M002417_2": "net_production", "E006602": "net_nuclear",
         "M005225_2": "net_fuels", "D004599": "net_coal", "E006479": "net_oil_products", "E006560": "net_natural_gas",
         "E006566": "net_biomass", "M000847": "net_other_fuels", "E006587": "net_hydro", "E006588_2": "net_wind",
         "E006637": "net_wind_onshore", "E006638": "net_wind_offshore", "E006590": "net_solar", "M001201": "net_other_sources",
         "M001250_2": "import", "M001263_2": "export", "M002138": "distribution_losses", "M005824": "net_consumption"}
NAMES.update({f"{c}_1": f"import_{n}" for c, n in COUNTRIES.items()})
NAMES.update({f"{c}_2": f"export_{n}" for c, n in COUNTRIES.items()})
X_COLS = ["x_measure", "x_status"]


def read(z, name):
    return pd.read_csv(io.BytesIO(z.read(name)), sep=";", dtype=str, keep_default_na=False)


def parse(content, base):
    z = zipfile.ZipFile(io.BytesIO(content))
    for n in ("Observations.csv", "MeasureCodes.csv", "PeriodenCodes.csv"):
        if n not in z.namelist():
            raise RuntimeError(f"the zip has no {n}: {z.namelist()}")
    m = read(z, "MeasureCodes.csv")
    bad = sorted(set(m.Identifier) - set(NAMES))
    if bad:
        raise RuntimeError(f"a measure not in the map: {bad}")
    if set(m.Unit) != {"mln kWh"}:
        raise RuntimeError(f"a unit other than mln kWh: {sorted(set(m.Unit))}")
    title = dict(zip(m.Identifier, m.Title))
    p = read(z, "PeriodenCodes.csv")
    status = dict(zip(p.Identifier, p.Status))
    o = read(z, "Observations.csv")
    if not {"Measure", "Perioden", "Value"} <= set(o.columns):
        raise RuntimeError(f"Observations.csv's columns: {list(o.columns)}")
    rows = []
    for r in o[o.Perioden.str.contains("MM")].itertuples():
        mm = re.fullmatch(r"(\d{4})MM(\d\d)", r.Perioden)
        if not mm:
            raise RuntimeError(f"a monthly period code of another form: {r.Perioden!r}")
        if r.Measure not in NAMES:
            raise RuntimeError(f"an observation of a measure not in the map: {r.Measure!r}")
        v = r.Value.strip()
        if v == "":
            continue
        try:
            value = float(v) * 1000
        except ValueError:
            raise RuntimeError(f"{r.Measure} {r.Perioden}: not a number: {v!r}")
        rows.append(dict(entity="cbs:nl", variable=NAMES[r.Measure], ts_utc=f"{mm.group(1)}-{mm.group(2)}-01T00:00:00Z", value=value, unit="MWh",
                         freq="P1M", geo="NL", market="", node=title[r.Measure], **base, x_measure=r.Measure, x_status=status.get(r.Perioden, "")))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no monthly value in the file")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a measure and month given twice")
    props = read(z, "Properties.csv") if "Properties.csv" in z.namelist() else pd.DataFrame()
    lic = props.License.iloc[0] if "License" in props else ""
    return t, lic


def main(argv=None):
    ap = argparse.ArgumentParser(description="CBS table 84575NED: the Netherlands' electricity balance, a month")
    ap.add_argument("--offline", action="store_true", help="the saved zip only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("datasets.cbs.nl"):
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t, lic = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        n = t[t.variable == "net_consumption"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        n = n[n["size"] == 12]["sum"] / 1e6
        st = t.x_status.value_counts().to_dict()
        head = [
            "Energy Research Warehouse (ERW): Statistics Netherlands (CBS), table 84575NED, Elektriciteitsbalans; aanbod en verbruik (the electricity "
            f"balance), a month, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2231)",
            "Shape: series (docs/datastandard.md v0). entity cbs:nl; variable the measure's English name (gross_production, own_use, net_production and "
            "its sources, import and export with their countries, distribution_losses, net_consumption); unit MWh (CBS's million kWh times 1,000); ts_utc "
            "the month's first day; freq P1M; geo NL; node CBS's Dutch name; x_measure CBS's code; x_status the period's status.",
            f"{len(t)} rows, {t.variable.nunique()} measures; statuses: " + ", ".join(f"{k} {v}" for k, v in sorted(st.items()))
            + "; net consumption TWh a full year: " + ", ".join(f"{k} {v:.1f}" for k, v in n.items() if k >= "2015")
            + ". Only CBS's monthly periods are taken. A cell CBS leaves empty has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cbs_electricity.py; the zip retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statistics Netherlands (CBS), table 84575NED, {PAGE}",
            f"  access: {URL}",
            f"License: public (CC BY 4.0, the table's own License property: {lic or 'https://creativecommons.org/licenses/by/4.0/'}). Source: CBS.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} measures, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Netherlands (CBS)", report="Table 84575NED: Elektriciteitsbalans; aanbod en verbruik",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
