#!/usr/bin/env python3
"""Berkeley Lab's hybrid power plants: every operating U.S. plant that pairs generators of two kinds, or a generator and
storage, at one site (PV+storage, wind+storage, fossil+PV and the rest), with its capacities, storage size and
duration, online dates, coupling and the uses its battery reports (session 979, chain 055: the operating side of
lbnl_hybrid_ppa_prices and lbnl_interconnection_queue's hybrids).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/lbnl_hybrid_plants.csv, from the sheet
"01. Operating Plants" of LBNL's "Hybrid Power Plants: Status of Operating and Proposed Plants, 2026 Data Update" data
file (plants operating through 2025):

    https://eta-publications.lbl.gov/publications/hybrid-power-plants-status-4

    entity_id    lbnl_hybrid:<EIA plant id>, or lbnl_hybrid:none-<name as a slug> where LBNL writes "missing"
    entity_type  plant; name EIA's plant name; geo US-<state>; lat, lon; capacity_mw the generators' and storage's
                 total (MW); status empty (LBNL lists operating plants); status_date empty
    x_*          LBNL's columns, renamed: region, final type and type, duration (hours), storage to generation ratio
                 (percent), generator 1 to 3 and storage capacity (MW), storage energy (MWh), the battery's and generator
                 1's online dates, coupling, storage technology, the number of battery uses and each use as LBNL marks it

The sheet's queue companion ("03. Hybrids in Queues") is LBNL's Queued Up data, held as lbnl_interconnection_queue, and
is not taken again. A heading not as read or an id given twice stops the run; a blank stays blank; nothing is filled.

    python warehouse/connectors/lbnl_hybrid_plants.py [--offline]

Ceiling: one request (the data file, saved in warehouse/raw/lbnl_hybrid_plants/ and reused offline). The file's notice
is the Department of Energy's contract notice only (the U.S. Government's license to publish "for U.S. Government
purposes"), without the CC BY 4.0 statement of LBNL's other data files: the table is held internal pending the owner.
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

NAME = "lbnl_hybrid_plants"
CONNECTOR = "lbnl_hybrid_plants"
SOURCE = "lbnl:hybrid_plants"
PAGE = "https://eta-publications.lbl.gov/publications/hybrid-power-plants-status-4"
URL = "https://eta-publications.lbl.gov/sites/default/files/2026-09/lbnl_hybrid_data_file_thru2025.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEET = "01. Operating Plants"
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
NAMED = ["State", "EIA Plant name", "EIA Plant ID", "Total Capacity, Generators and Storage (MW)", "Latitude", "Longitude"]
FIELDS = {"Region": "region", "Final Type": "final_type", "Type": "type", "Duration (Hrs)": "duration_h",
          "Storage:Generation Ratio (%)": "storage_generation_ratio_pct", "Generator 1 Capacity (MW)": "generator1_mw",
          "Generator 2 Capacity (MW)": "generator2_mw", "Generator 3 Capacity (MW)": "generator3_mw", "Storage Capacity (MW)": "storage_mw",
          "Nameplate Storage Energy Capacity (MWh)": "storage_mwh", "Battery Online Date": "battery_online", "Generator 1 Online Date": "generator1_online",
          "Coupling": "coupling", "Storage Technology 1": "storage_technology", "Total Number of Uses for Battery": "battery_uses_n",
          "Arbitrage": "use_arbitrage", "Frequency Regulation": "use_frequency_regulation", "Load Following": "use_load_following",
          "Ramping / Spinning Reserve": "use_ramping_spinning_reserve", "Co-Located Renewable Firming": "use_renewable_firming",
          "Transmission and Distribution Deferral": "use_td_deferral", "System Peak Shaving": "use_peak_shaving", "Load Management": "use_load_management",
          "Voltage or Reactive Power Support": "use_voltage_support", "Backup Power": "use_backup_power",
          "Excess Wind and Solar Generation": "use_excess_wind_solar"}
EXTRA = ["x_" + v for v in FIELDS.values()]


def cell(v):
    if v is None or v is pd.NaT or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, (pd.Timestamp, dt.datetime)):
        return pd.Timestamp(v).strftime("%Y-%m-%d")
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def plants(frame, base):
    cols = [str(c) for c in frame.columns]
    if cols != NAMED[:4] + ["Region"] + NAMED[4:] + list(FIELDS)[1:]:
        raise RuntimeError(f"headings not as read: {cols}")
    rows = []
    for _, r in frame.iterrows():
        pid = cell(r["EIA Plant ID"])
        name = cell(r["EIA Plant name"])
        if not name:
            continue
        eid = f"lbnl_hybrid:{pid}" if pid and pid != "missing" else f"lbnl_hybrid:none-{slug(name)}"
        st = cell(r["State"])
        cap = pd.to_numeric(r["Total Capacity, Generators and Storage (MW)"], errors="coerce")
        row = dict(entity_id=eid, entity_type="plant", name=name, geo=f"US-{st}" if re.fullmatch(r"[A-Z]{2}", st) else "",
                   lat=cell(r["Latitude"]), lon=cell(r["Longitude"]), capacity_mw="" if pd.isna(cap) else float(cap), status="", status_date="",
                   operator="", **base)
        for k, v in FIELDS.items():
            row["x_" + v] = cell(r[k])
        rows.append(row)
    t = pd.DataFrame(rows)
    if t.entity_id.duplicated().any():
        raise RuntimeError(f"an id given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].tolist()[:3]}")
    return t[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Berkeley Lab's operating hybrid power plants")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{URL} is not a workbook")
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = plants(pd.read_excel(io.BytesIO(content), sheet_name=SHEET, header=1), base)
        cap = pd.to_numeric(t.capacity_mw, errors="coerce")
        alone = int((t.x_type == "Storage").sum())
        kinds = t[t.x_final_type != ""].x_final_type.value_counts().to_dict()
        header = [
            "Energy Research Warehouse (ERW): Berkeley Lab, operating U.S. hybrid power plants through 2025 (Hybrid Power Plants: Status of Operating and Proposed Plants, 2026 Data Update, sheet '01. Operating Plants') (session 979)",
            "Shape: entities (docs/datastandard.md v0). entity_id lbnl_hybrid:<EIA plant id> (none-<name> where LBNL writes 'missing'); entity_type plant; "
            "geo US-<state>; capacity_mw the generators' and storage's total; status empty (operating plants); x_* LBNL's columns, renamed.",
            f"{len(t) - alone:,} hybrid plants, {cap.sum():,.0f} MW in all, by LBNL's final type: {', '.join(f'{v} {k}' for k, v in kinds.items())}; "
            f"and {alone} storage-only plants LBNL lists beside them (type Storage, final type and total capacity empty, storage MW given). A blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/lbnl_hybrid_plants.py; the data file retrieved {base['retrieved_at']}, last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Lawrence Berkeley National Laboratory, Hybrid Power Plants: Status of Operating and Proposed Plants, 2026 Data Update, {PAGE}",
            f"  access: {URL}",
            "License: the file's notice is the Department of Energy's contract notice only (the U.S. Government's license 'for U.S. Government purposes'), "
            "without the CC BY 4.0 statement of LBNL's other data files: held internal pending the owner (session 979).",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Lawrence Berkeley National Laboratory (Berkeley Lab)",
                                    report="Hybrid Power Plants: Status of Operating and Proposed Plants (operating plants)", report_url=PAGE,
                                    document_list=URL, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} plants"))
        print(f"{NAME}: {len(t):,} plants, {cap.sum():,.0f} MW")
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
