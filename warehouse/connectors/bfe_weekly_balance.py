#!/usr/bin/env python3
"""The Swiss Federal Office of Energy's (SFOE's) weekly electricity balance (ENSTAT, ogd51): Switzerland's generation by type,
storage pumps' use, imports, exports and national consumption on one day a week, each Wednesday, from 2003 (session 2808,
chain 143, in place of the Federal Statistical Office, whose datasets on opendata.swiss hold no electricity table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/bfe_ch_electricity_wednesdays.csv, from one CSV
(one request), listed on opendata.swiss as "ENSTAT: Wochenstatistik Elektrizitaetsbilanz":

    https://www.bfe-ogd.ch/ogd51/ogd51_wochenstatistik_elektrizitaetsbilanz.csv

    entity      bfe_weekly:ch
    variable    the file's column (COLUMNS below): run_of_river, storage_hydro, nuclear, thermal, wind, solar, other (each
                Erzeugung_*), storage_pumps (Verbrauch_speicherpumpen), imports, exports, national_consumption (Landesverbrauch);
                Erzeugung_netto as generation_less_storage_pumps on the days it is that (through 2024) and as net_generation
                on the days it is the generation before the pumps (from 2025), x_definition saying which
    unit        MWh: the file's GWh times 1,000, the energy of that one day
    ts_utc      the Wednesday's date at 00:00:00Z, a Swiss local day as the file gives it (no time zone converted); freq P1D;
                geo CH
    node        "SFOE weekly balance (Wednesdays), <the file's column>"

"Based on Wednesday data" (the dataset's description): each row is one Wednesday's energy, not a week's. Before 2025 thermal,
wind and solar are inside "other" (Erzeugung_andere, conventional thermal and other generation); from 2025 they are columns of
their own and "other" is blank. Erzeugung_netto changed with them (session 2808 found it): through 2024 it is the generation
less the storage pumps, from 2025 the generation before them, each within 0.05 GWh on every day; each day's figure is written
under the measure it matches, so neither series mixes the two. A blank has no row; nothing is filled. National consumption is
compared with the generation less the storage pumps plus imports less exports in every row, within 0.05 GWh; a row that does
not hold is counted and listed in the run log, kept as published. A date not a
Wednesday, and a step between dates other than seven days, are counted, kept. Checks that stop the run: a header not the
file's, a date not a date, a value not a number, a date given twice.

    python warehouse/connectors/bfe_weekly_balance.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/bfe_weekly/ with --offline. www.bfe-ogd.ch has no robots file (HTTP 404, read
1612, as session 2343 found). The dataset's DCAT record on ckan.opendata.swiss (its `/dataset/` path, which that host's robots
file allows) gives the file and the licence terms_by. License: opendata.swiss's "Open use. Must provide the source." (terms_by),
the SFOE's verdict on record (session 2343); source: Swiss Federal Office of Energy (SFOE).
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "bfe_ch_electricity_wednesdays"
CONNECTOR = "bfe_weekly"
SOURCE = "bfe:ogd51"
URL = "https://www.bfe-ogd.ch/ogd51/ogd51_wochenstatistik_elektrizitaetsbilanz.csv"
PAGE = "https://opendata.swiss/de/dataset/enstat-wochenstatistik-elektrizitatsbilanz-erzeugung-und-abgabe-elektrischer-energie-in-der-sch"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLUMNS = {"Erzeugung_laufwerk_GWh": "run_of_river", "Erzeugung_speicherwerk_GWh": "storage_hydro",
           "Erzeugung_kernkraftwerk_GWh": "nuclear", "Erzeugung_thermisch_GWh": "thermal", "Erzeugung_windkraftwerk_GWh": "wind",
           "Erzeugung_photovoltaik_GWh": "solar", "Erzeugung_andere_GWh": "other", "Verbrauch_speicherpumpen_GWh": "storage_pumps",
           "Erzeugung_netto_GWh": "net_generation", "Einfuhr_GWh": "imports", "Ausfuhr_GWh": "exports",
           "Landesverbrauch_GWh": "national_consumption"}
GENERATION = ["Erzeugung_laufwerk_GWh", "Erzeugung_speicherwerk_GWh", "Erzeugung_kernkraftwerk_GWh", "Erzeugung_thermisch_GWh",
              "Erzeugung_windkraftwerk_GWh", "Erzeugung_photovoltaik_GWh", "Erzeugung_andere_GWh"]
TOL = 0.05   # GWh
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_column", "x_definition"]


def build(content, retrieved, vintage):
    t0 = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    if list(t0.columns) != ["Datum"] + list(COLUMNS):
        raise RuntimeError(f"the header is not the file's: {list(t0.columns)}")
    try:
        days = pd.to_datetime(t0.Datum, format="%Y-%m-%d")
    except ValueError as e:
        raise RuntimeError(f"a date not a date: {e}")
    if days.duplicated().any():
        raise RuntimeError(f"a date given twice: {t0.Datum[days.duplicated()].iloc[0]}")
    vals = {}
    for c in COLUMNS:
        s = t0[c].str.strip()
        bad = s[(s != "") & pd.to_numeric(s, errors="coerce").isna()]
        if len(bad):
            raise RuntimeError(f"{c}: not a number: {bad.iloc[0]!r}")
        vals[c] = pd.to_numeric(s.replace("", None), errors="coerce")
    v = pd.DataFrame(vals)
    v.index = days
    counts = {"not_wednesday": [d.strftime("%Y-%m-%d") for d in days if d.dayofweek != 2],
              "steps": [(a.strftime("%Y-%m-%d"), int((b - a).days)) for a, b in zip(days[:-1], days[1:]) if (b - a).days != 7]}
    gen = v[GENERATION].sum(axis=1, min_count=1)
    less_pumps = gen - v.Verbrauch_speicherpumpen_GWh
    # Erzeugung_netto is the generation less the storage pumps through 2024, and the generation before them from 2025
    # (session 2808 found it): each day's figure is written under the measure it matches.
    definition = pd.Series("neither", index=v.index)
    definition[(v.Erzeugung_netto_GWh - gen).abs() <= TOL] = "before_pumps"
    definition[(v.Erzeugung_netto_GWh - less_pumps).abs() <= TOL] = "less_pumps"
    definition[v.Erzeugung_netto_GWh.isna()] = ""
    counts["definition"] = definition[definition != ""].value_counts().to_dict()
    counts["neither"] = [d.strftime("%Y-%m-%d") for d in definition[definition == "neither"].index]
    has2 = less_pumps.notna() & v[["Einfuhr_GWh", "Ausfuhr_GWh", "Landesverbrauch_GWh"]].notna().all(axis=1)
    d_use = (less_pumps + v.Einfuhr_GWh - v.Ausfuhr_GWh - v.Landesverbrauch_GWh)[has2]
    counts["use"] = (len(d_use), d_use[d_use.abs() > TOL])
    rows = []
    for c, var in COLUMNS.items():
        for day, x in v[c].dropna().items():
            d = definition[day] if c == "Erzeugung_netto_GWh" else ""
            name = {"less_pumps": "generation_less_storage_pumps", "before_pumps": "net_generation"}.get(d, var)
            rows.append({"entity": "bfe_weekly:ch", "variable": name, "ts_utc": day.strftime("%Y-%m-%dT00:00:00Z"),
                         "value": round(float(x) * 1000.0, 3), "unit": "MWh", "freq": "P1D", "geo": "CH", "market": "",
                         "node": f"SFOE weekly balance (Wednesdays), {c}", "source": SOURCE, "source_url": URL,
                         "retrieved_at": retrieved, "vintage": vintage, "x_column": c, "x_definition": d})
    counts["blank"] = int(v.isna().sum().sum())
    t = pd.DataFrame(rows, columns=COLS).sort_values(["variable", "ts_utc"]).reset_index(drop=True)
    return t, counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="SFOE ogd51: Switzerland's electricity balance on each Wednesday")
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
        if not args.offline and (ip.paused("bfe") or ip.paused_host("www.bfe-ogd.ch")):
            raise RuntimeError("the SFOE is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        t, counts = build(content, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        if t.empty:
            raise RuntimeError("no observation kept")
        n_use, off_use = counts["use"]
        for day, d in off_use.items():
            log(f"  national consumption off by {d:+.3f} GWh, kept as published: {day:%Y-%m-%d}")
        for x in counts["neither"]:
            log(f"  Erzeugung_netto matches neither measure, written as net_generation: {x}")
        dfn = counts["definition"]
        for x in counts["not_wednesday"]:
            log(f"  a date not a Wednesday, kept: {x}")
        for a, s in counts["steps"]:
            log(f"  a step of {s} days after {a}")
        header = [
            f"Energy Research Warehouse (ERW): Swiss Federal Office of Energy (SFOE), ENSTAT weekly electricity balance (ogd51): Switzerland's generation by type, storage pumps, imports, exports and national consumption on each Wednesday, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} (session 2808)",
            "Shape: series (docs/datastandard.md v0). entity bfe_weekly:ch; variable run_of_river, storage_hydro, nuclear, thermal, wind, solar, other, storage_pumps, generation_less_storage_pumps (Erzeugung_netto through 2024), net_generation (Erzeugung_netto from 2025, before the pumps), imports, exports or national_consumption; unit MWh (the file's GWh times 1,000), the energy of that one day; "
            "ts_utc the Wednesday's date at 00:00:00Z, a Swiss local day as the file gives it; freq P1D; geo CH; x_column the file's column; x_definition, for Erzeugung_netto, less_pumps or before_pumps. Before 2025 thermal, wind and solar are inside other; from 2025 they are columns of their own.",
            f"{len(t)} rows, {t.ts_utc.nunique()} days. The file's Erzeugung_netto is the generation less the storage pumps on {dfn.get('less_pumps', 0):,} days (written generation_less_storage_pumps; through 2024) and the generation before them on {dfn.get('before_pumps', 0):,} (written net_generation; from 2025), within {TOL:g} GWh; {dfn.get('neither', 0)} match neither (net_generation, x_definition neither). "
            f"National consumption equals the generation less the storage pumps plus imports less exports in {n_use - len(off_use):,} of {n_use:,} days; the others are kept as published and listed in the run log. {len(counts['not_wednesday'])} date(s) not a Wednesday and {len(counts['steps'])} step(s) other than seven days, kept. {counts['blank']:,} blanks have no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/bfe_weekly_balance.py; the file retrieved {rec.get('retrieved_at') or ''} (last modified {rec.get('last_modified') or 'not given'})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Swiss Federal Office of Energy (SFOE), ENSTAT: Wochenstatistik Elektrizitaetsbilanz, {PAGE}",
            f"  access: {URL}",
            "License: opendata.swiss terms_by, \"Open use. Must provide the source.\" Source: Swiss Federal Office of Energy (SFOE); reshaped by the ERW (GWh written as MWh).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Swiss Federal Office of Energy (SFOE)",
                                    report="ENSTAT: Wochenstatistik Elektrizitaetsbilanz (weekly electricity balance, Wednesdays)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.ts_utc.nunique()} days; netto {dfn}; use off {len(off_use)} of {n_use}; not Wednesday {counts['not_wednesday']}; steps {counts['steps']}")
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
