#!/usr/bin/env python3
"""Berkeley Lab's PV+battery PPA prices: each hybrid PPA in LBNL's sample, greenfield or a battery retrofitted to an
operating PV plant, with the plant, the PV and battery sizes, the dates, and the levelized price of the PV, the battery
adder and the two together (session 940, chain 053: lbnl_ppa_prices holds PV-only contracts; this holds the hybrids).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/lbnl_hybrid_ppa_prices.csv, from the "PV+Battery
Hybrid PPA Price" sheet of LBNL's Utility-Scale Solar, 2025 Data Update data file, the one lbnl_ppa_prices.py saves:

    https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx

    event_id     lbnl_hybrid:<EIA ID, or the plant's name as a slug>:<greenfield|retrofit>
    event_date   the PPA's execution date (greenfield) or the retrofit's (retrofit); event_type ppa_hybrid
    entity_ids   lbnl_solar:<EIA ID> for each EIA id the row names (a retrofit names the PV plant and the battery, "58542/65857")
    mw           the PV capacity (MW-AC); price the PV+battery price levelized over the term, in real 2024 USD per MWh of PV
                 output (the sheet's PV+BESS_$_per_MWh-PV_real); currency USD
    x_*          the kind (greenfield or retrofit), state, plant, LBNL's "Year added", PV MWh a year, battery MW, MWh, duration
                 and its ratio to PV, the PV-equivalent duration, the PV and battery PPA executions and CODs, and the price's
                 parts: the PV price (USD/MWh), the battery adder per MWh of PV, per MWh stored and per MW-month (real 2024 USD)

The prices are LBNL's levelized real values (the file's other price sheets name 2024 dollars). A heading not as read, or a
row with a price but no date, stops the run; a blank stays blank; nothing is filled.

    python warehouse/connectors/lbnl_hybrid_ppa_prices.py [--offline]

Ceiling: one request, and none while lbnl_ppa_prices' saved file is on the machine. License: CC BY 4.0, as the file's
copyright notice states; cite Berkeley Lab.
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

NAME = "lbnl_hybrid_ppa_prices"
CONNECTOR = "lbnl_hybrid_ppa_prices"
SAVED_BY = "lbnl_ppa_prices"
SOURCE = "lbnl:hybrid_ppa_prices"
PAGE = "https://eta-publications.lbl.gov/publications/us-utility-scale-solar-2025-data"
URL = "https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEET = "PV+Battery Hybrid PPA Price"
HEAD = ["HI", "Non-HI", "PPA_Execution", "BESS:PV Ratio", "ESA_Execution", "BESS:PV Ratio", "", "State", "Plant_Name", "Year added", "EIA ID",
        "PV MW-AC", "Avg Annual PV MWh", "BESS MW", "BESS MWh", "BESS Duration", "BESS:PV Ratio",
        "PV-Equivalent Duration (Storage Energy / PV Capacity)", "PV PPA Execution", "BESS PPA Execution", "PV COD", "BESS COD",
        "Retrofit_Execution", "Retrofit_COD", "PV_$_per_MWh_real", "BESS_$_per_MWh-PV_real", "BESS_$_per_MWh-stored_real",
        "BESS_$_per_MW-month_real", "PV+BESS_$_per_MWh-PV_real"]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url", "retrieved_at"]
X = {9: "x_year_added", 12: "x_pv_mwh_year", 13: "x_bess_mw", 14: "x_bess_mwh", 15: "x_bess_duration_h", 16: "x_bess_pv_ratio",
     17: "x_pv_equivalent_duration_h", 24: "x_pv_usd_mwh", 25: "x_bess_adder_usd_mwh_pv", 26: "x_bess_adder_usd_mwh_stored",
     27: "x_bess_adder_usd_mw_month"}
DATES = {18: "x_pv_ppa_execution", 19: "x_bess_ppa_execution", 20: "x_pv_cod", 21: "x_bess_cod", 22: "x_retrofit_execution", 23: "x_retrofit_cod"}
X_COLS = ["x_kind", "x_state", "x_plant", "x_eia_id"] + list(X.values()) + list(DATES.values()) + ["x_dollar_year"]


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def num(v):
    x = pd.to_numeric(text(v), errors="coerce")
    return "" if pd.isna(x) else (int(x) if float(x).is_integer() else float(x))


def day(v):
    d = pd.to_datetime(text(v), errors="coerce")
    return "" if pd.isna(d) else d.strftime("%Y-%m-%d")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def events(frame, url, retrieved):
    h = None
    for i in range(min(40, len(frame))):
        if text(frame.iloc[i, 2]) == "PPA_Execution" and text(frame.iloc[i, 8]) == "Plant_Name":
            h = i
            break
    if h is None:
        raise RuntimeError("no heading row with PPA_Execution and Plant_Name in the sheet's first 40 rows")
    head = [text(v) for v in frame.iloc[h, :len(HEAD)]]
    if head != HEAD:
        raise RuntimeError(f"the sheet's headings are not as read: {head}")
    out, seen = [], {}
    for _, r in frame.iloc[h + 1:].iterrows():
        plant, price = text(r.iloc[8]), num(r.iloc[28])
        if not plant:
            continue
        green, retro = day(r.iloc[2]), day(r.iloc[4])
        kind, date = ("greenfield", green) if green else ("retrofit", retro)
        if not date:
            if price == "":
                continue
            raise RuntimeError(f"a hybrid PPA with a price and no date: {plant}")
        eia = text(r.iloc[10])
        ids = [p.strip() for p in re.split(r"[/,;]", eia) if p.strip()]
        key = f"{eia.replace('/', '_') if eia else slug(plant)}:{kind}"
        seen[key] = seen.get(key, 0) + 1
        row = {"event_id": f"lbnl_hybrid:{key}" + (f"-{seen[key]}" if seen[key] > 1 else ""), "event_date": date, "event_type": "ppa_hybrid",
               "parties": "", "entity_ids": ";".join(f"lbnl_solar:{i}" for i in ids), "mw": num(r.iloc[11]), "price": price,
               "currency": "USD" if price != "" else "", "status": "", "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
               "x_kind": kind, "x_state": text(r.iloc[7]), "x_plant": plant.replace("_", " "), "x_eia_id": eia, "x_dollar_year": "2024"}
        for c, n in X.items():
            row[n] = num(r.iloc[c])
        for c, n in DATES.items():
            row[n] = day(r.iloc[c])
        out.append(row)
    t = pd.DataFrame(out)
    return t[EVENT_COLS + X_COLS].sort_values(["event_date", "event_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Berkeley Lab's PV+battery hybrid PPA prices")
    ap.add_argument("--offline", action="store_true", help="the saved data file only, no request")
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
        hit = ip.raw_cached(SAVED_BY, URL) or ip.raw_cached(CONNECTOR, URL)
        if hit:
            content, rec = hit
            log(f"  saved file reused: {rec['file']}")
        else:
            content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{URL} is not a workbook")
        retrieved = rec.get("retrieved_at") or ""
        t = events(pd.read_excel(io.BytesIO(content), sheet_name=SHEET, header=None), URL, retrieved)
        n = t.x_kind.value_counts().to_dict()
        priced = int((t.price != "").sum())
        header = [
            "Energy Research Warehouse (ERW): Berkeley Lab, PV+battery hybrid PPA prices, one row a PPA, greenfield or retrofit (Utility-Scale Solar, 2025 Data Update) (session 940)",
            "Shape: events (docs/datastandard.md v0). event_id lbnl_hybrid:<EIA ID or plant>:<greenfield|retrofit>; event_date the PPA's or the "
            "retrofit's execution; event_type ppa_hybrid; entity_ids lbnl_solar:<EIA ID> for each id named; mw the PV capacity (MW-AC); price the "
            "PV+battery price levelized, real 2024 USD per MWh of PV output; x_* the plant, sizes, dates and the price's parts (PV, battery adder "
            "per MWh of PV, per MWh stored, per MW-month).",
            f"{len(t)} hybrid PPAs ({', '.join(f'{v} {k}' for k, v in n.items())}), {priced} with a combined price. Values as LBNL publishes them; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/lbnl_hybrid_ppa_prices.py; the data file retrieved {retrieved}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{SAVED_BY}/ (not in git; the file lbnl_ppa_prices.py saves)",
            f"Source: {SOURCE} Lawrence Berkeley National Laboratory, Utility-Scale Solar, 2025 Data Update (October 2025), sheet '{SHEET}', {PAGE}",
            f"  access: {URL}",
            "License: CC BY 4.0, as the data file's copyright notice states; cite Berkeley Lab and the report.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Lawrence Berkeley National Laboratory (Berkeley Lab)",
                                    report="Utility-Scale Solar Data Update (PV+Battery Hybrid PPA Price)", report_url=PAGE,
                                    document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} PPAs"))
        print(f"{NAME}: {len(t)} hybrid PPAs ({n}), {priced} priced")
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
