#!/usr/bin/env python3
"""France's electricity every half hour: consumption, production by source and net physical exchanges, from RTE's
eco2mix files (session 2238, chain 101: France's grid by fuel; ODRE, the queue file's first address, disallows its API
and downloads to every reader but Googlebot, so RTE's own download host is used).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/rte_eco2mix_france_halfhourly.csv, from
the national files RTE links on its eco2mix download page (www.rte-france.com/eco2mix/telecharger-les-indicateurs, whose
script eco2mix_dl.js builds the addresses):

    https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_<year>.zip   (definitive, 2020 to 2025)
    https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_En-cours-Consolide.zip        (consolidated, this year)

Each zip holds one tab-separated text file (named .xls, Windows-1252), one line every quarter hour of French local time
("Date", "Heures"); the measures are filled every half hour, the quarter-hour lines holding only forecasts and
commercial exchanges. Taken, in MW as published:

    consumption (Consommation), oil (Fioul), coal (Charbon), gas (Gaz), nuclear (Nucleaire), wind (Eolien), solar
    (Solaire), hydro (Hydraulique), pumping (Pompage, negative), bioenergy (Bioenergies), physical_exchanges (Ech.
    physiques, the net), battery_charging (Stockage batterie), battery_discharging (Destockage batterie), wind_onshore
    (Eolien terrestre), wind_offshore (Eolien offshore)

Not taken: the day-ahead and same-day forecasts, the CO2 rate (the files state no unit), the commercial exchanges by
border (hourly values repeated on every quarter hour) and the sub-sources (TAC, cogeneration and the rest). The files
state no unit either for the measures; they are MW: a year's consumption, each half hour's MW times half an hour,
agrees with Ember's French demand (session 2238's cross-check).

    entity      rte_eco2mix:FR; node France; geo FR; freq PT30M; unit MW
    ts_utc      the half hour's start in UTC, from French local time (Europe/Paris)
    x_*         RTE's data nature (definitive or consolidated), the local date and hour

French local time, placed in UTC: RTE's grid has 96 quarter hours every day. On the spring change it prints 02:00 to
02:45, which do not exist in French time (their values repeat their neighbours'), and on the autumn change it prints
02:00 to 02:45 once, though they occur twice. Both kinds are left out and counted, never guessed. Where RTE prints 0
for both onshore and offshore wind beside a total that is not 0 (all of 2021), the split is a placeholder and is left
out, counted; elsewhere onshore plus offshore can differ from the total on some half hours, kept as published. "ND" and a blank have
no row; nothing is filled. A header not RTE's, a perimeter not France, a value that is not a number, a date or hour not
in RTE's form, or a half hour given twice stops the run.

    python warehouse/connectors/rte_eco2mix.py [--first 2020] [--offline] [--out-dir DIR]

Ceiling: one request a year and one for this year, reused from warehouse/raw/rte_eco2mix/ with --offline. Neither
eco2mix.rte-france.com (HTTP 404) nor www.rte-france.com's robots file bars these paths (session 2238). License:
RTE's legal notice, "Les donnees publiees sur le portail www.rte-france.com sont publiques et leur reutilisation est
permise sous reserve de mentionner la source", with modification of the content forbidden: the values are kept as
published, reshaped from wide to long. Cite: RTE, eco2mix.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "rte_eco2mix_france_halfhourly"
CONNECTOR = "rte_eco2mix"
SOURCE = "rte:eco2mix_national"
PAGE = "https://www.rte-france.com/eco2mix/telecharger-les-indicateurs"
YEAR_URL = "https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_{year}.zip"
CURRENT_URL = "https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_En-cours-Consolide.zip"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
PARIS = ZoneInfo("Europe/Paris")
FIELDS = {"Consommation": "consumption", "Fioul": "oil", "Charbon": "coal", "Gaz": "gas", "Nucléaire": "nuclear",
          "Eolien": "wind", "Solaire": "solar", "Hydraulique": "hydro", "Pompage": "pumping", "Bioénergies": "bioenergy",
          "Ech. physiques": "physical_exchanges", "Stockage batterie": "battery_charging",
          "Déstockage batterie": "battery_discharging", "Eolien terrestre": "wind_onshore", "Eolien offshore": "wind_offshore"}
FIRST = ["Périmètre", "Nature", "Date", "Heures", "Consommation"]
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_nature", "x_local_date", "x_local_hour"]


def local_to_utc(day, hour):
    """French local date and hour to the UTC instant, or None where the local time does not exist (spring) or occurs
    twice (autumn), which RTE's fixed 96-quarter-hour day cannot tell apart."""
    naive = dt.datetime.strptime(f"{day} {hour}", "%Y-%m-%d %H:%M")
    a, b = naive.replace(tzinfo=PARIS, fold=0), naive.replace(tzinfo=PARIS, fold=1)
    ua, ub = a.astimezone(dt.timezone.utc), b.astimezone(dt.timezone.utc)
    if ua.astimezone(PARIS).replace(tzinfo=None) != naive:
        return None, "nonexistent"  # a spring-change time: back from UTC it reads an hour off
    if ua != ub:
        return None, "ambiguous"  # an autumn-change time: two instants
    return ua.strftime("%Y-%m-%dT%H:%M:%SZ"), ""


def file_rows(content, url, retrieved, vintage, counts):
    z = zipfile.ZipFile(io.BytesIO(content))
    names = z.namelist()
    if len(names) != 1:
        raise RuntimeError(f"{url}: {len(names)} files in the zip, one expected")
    lines = z.read(names[0]).decode("cp1252").splitlines()
    head = [h.strip() for h in lines[0].split("\t")]
    if head[:5] != FIRST:
        raise RuntimeError(f"{url}: the header is not RTE's: {head[:5]}")
    idx = {h: i for i, h in enumerate(head)}
    missing = [k for k in FIELDS if k not in idx]
    if missing:
        raise RuntimeError(f"{url}: columns missing: {missing}")
    out = []
    for line in lines[1:]:
        if not line.strip() or line.startswith("RTE ne pourra"):
            continue
        c = line.split("\t")
        if c[0] != "France":
            raise RuntimeError(f"{url}: a perimeter not France: {c[0]!r}")
        day, hour = c[2].strip(), c[3].strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) or not re.fullmatch(r"\d{2}:\d{2}", hour):
            raise RuntimeError(f"{url}: a date or hour not in RTE's form: {day!r} {hour!r}")
        vals = {var: (c[idx[k]].strip() if idx[k] < len(c) else "") for k, var in FIELDS.items()}
        if all(v in ("", "ND") for v in vals.values()):
            continue
        # a zero split of wind where wind is not zero is RTE's placeholder (all of 2021), not a measure: left out
        if vals["wind_onshore"] in ("0", "0.0") and vals["wind_offshore"] in ("0", "0.0") and vals["wind"] not in ("", "ND", "0"):
            vals["wind_onshore"] = vals["wind_offshore"] = ""
            counts["zero_split"] += 1
        ts, why = local_to_utc(day, hour)
        if ts is None:
            counts[why] += 1
            continue
        for var, v in vals.items():
            if v in ("", "ND"):
                continue
            try:
                value = float(v)
            except ValueError:
                raise RuntimeError(f"{url}: {day} {hour} {var}: not a number: {v!r}")
            out.append({"entity": "rte_eco2mix:FR", "variable": var, "ts_utc": ts, "value": value, "unit": "MW",
                        "freq": "PT30M", "geo": "FR", "market": "", "node": "France", "source": SOURCE, "source_url": url,
                        "retrieved_at": retrieved, "vintage": vintage, "x_nature": c[1].strip(), "x_local_date": day,
                        "x_local_hour": hour})
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a half hour given twice: {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="RTE eco2mix: France's consumption, production by source and exchanges, every half hour")
    ap.add_argument("--first", type=int, default=2020)
    ap.add_argument("--last", type=int, default=2025, help="the last definitive year")
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
        if not args.offline and (ip.paused("rte") or ip.paused_host("eco2mix.rte-france.com")):
            raise RuntimeError("RTE is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        counts = {"ambiguous": 0, "nonexistent": 0, "zero_split": 0}
        urls = [YEAR_URL.format(year=y) for y in range(args.first, args.last + 1)] + [CURRENT_URL]
        for url in urls:
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
            rows += file_rows(content, url, rec.get("retrieved_at") or "", ip.vintage_of(rec), counts)
            got.append((url.rsplit("_", 1)[-1].replace(".zip", ""), rec.get("retrieved_at") or ""))
        t = finish(rows)
        span = t.groupby("variable").ts_utc.agg(["min", "max", "size"])
        header = [
            f"Energy Research Warehouse (ERW): RTE, eco2mix, France's consumption, production by source and net physical exchanges every half hour, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} (session 2238)",
            "Shape: series (docs/datastandard.md v0). entity rte_eco2mix:FR; variable consumption, oil, coal, gas, nuclear, wind, solar, hydro, pumping (negative), bioenergy, physical_exchanges (net), "
            "battery_charging, battery_discharging, wind_onshore, wind_offshore; unit MW; ts_utc the half hour's start in UTC from French local time; freq PT30M; geo FR; x_nature RTE's definitive or consolidated.",
            f"{len(t)} rows: " + "; ".join(f"{v} {int(r['size'])} from {r['min'][:10]}" for v, r in span.iterrows())
            + f". Left out, never guessed: {counts['nonexistent']} half hours of the spring change that do not exist in French time and {counts['ambiguous']} of the autumn change that occur twice (RTE prints them once). "
            f"Wind's onshore and offshore split left out in {counts['zero_split']} half hours where RTE prints 0 for both beside a total (all of 2021); elsewhere the split can differ from the total, as published. "
            "'ND' and blanks have no row; nothing is filled. The files state no unit: MW, as a year's consumption agrees with Ember's demand.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/rte_eco2mix.py; the files retrieved " + "; ".join(f"{k} {r}" for k, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} RTE (Reseau de Transport d'Electricite), eco2mix, national definitive and consolidated files, {PAGE}",
            f"  access: {YEAR_URL.format(year='<year>')}; {CURRENT_URL}",
            "License: public. RTE's legal notice: the data published on www.rte-france.com are public and their reuse is permitted provided the source is cited; their modification is forbidden (values kept as published, reshaped from wide to long). Cite: RTE, eco2mix.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="RTE (Reseau de Transport d'Electricite)",
                                    report="eco2mix, national definitive and consolidated files (France, every half hour)",
                                    report_url=PAGE, document_list=YEAR_URL.format(year="<year>"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; left out {counts['nonexistent']} nonexistent and {counts['ambiguous']} ambiguous half hours")
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
