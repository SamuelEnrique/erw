#!/usr/bin/env python3
"""Battery storage units of the US, operating, planned and retired, from the EIA-860M tables the ERW holds.

Energy Research Warehouse (ERW), session 31 (Part C4). No pull: reads eia860m_operating_generators,
eia860m_planned_generators and eia860m_retired_generators and keeps every battery unit (prime mover BA, EIA's
"Batteries" technology, energy source MWH), one row per generator, into the entities table

    warehouse/output/storage_capacity.csv

Columns: the entities columns (capacity_mw is EIA's nameplate MW), then plant_id, generator_id, state, county,
balancing_authority (EIA's code as written), iso (the ISO where the BA code is one of the seven ISOs: CISO CAISO,
ERCO ERCOT, ISNE ISO-NE, MISO MISO, NYIS NYISO, PJM PJM, SWPP SPP; empty otherwise), net_summer_mw, eia_status,
operating_year (operating and retired units), planned_year (planned units: the year of EIA's planned operation date),
retirement_date, source_table, input_source_url, and since session 34 energy_capacity_mwh: EIA's Nameplate Energy
Capacity (MWh) from the EIA-860M tables. EIA gives it for operating and retired units; its Planned sheet has no such
column, so planned units have none. It is never estimated from MW.

    python warehouse/derived/storage_capacity.py

A snapshot: each run replaces the table (write_snapshot), so a unit EIA drops leaves it. Method:
docs/methods/storage.md.
"""

import datetime as dt
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "storage_capacity"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage.md"
INPUTS = {"operating": "eia860m_operating_generators", "planned": "eia860m_planned_generators",
          "retired": "eia860m_retired_generators"}
ISO_OF_BA = {"CISO": "CAISO", "ERCO": "ERCOT", "ISNE": "ISO-NE", "MISO": "MISO", "NYIS": "NYISO", "PJM": "PJM",
             "SWPP": "SPP"}
ENT = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
       "source", "source_url", "retrieved_at", "vintage"]
COLS = ENT + ["plant_id", "generator_id", "state", "county", "balancing_authority", "iso", "net_summer_mw",
              "eia_status", "operating_year", "planned_year", "retirement_date", "source_table", "input_source_url",
              "energy_capacity_mwh"]  # session 34


def read(name):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"storage_capacity_{run_id}.log"))
    status = dict(table=NAME, market="derived", status="ok", detail="")
    missing = [t for t in INPUTS.values() if not os.path.exists(os.path.join(ip.OUT_DIR, t + ".csv"))]
    if missing:  # session 10 ruling 3: a derived table without its inputs on the runner skips with a warning
        msg = f"inputs not on this machine: {', '.join(missing)}; the table is left as it is"
        log(f"SKIPPED: {msg}")
        print(f"storage_capacity SKIPPED: {msg}")
        ip.write_status("storage_capacity", run_id, [dict(status, status="skipped", detail=msg)])
        log.close()
        return 0
    try:
        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        parts = []
        for kind, table in INPUTS.items():
            d = read(table)
            b = d[(d["prime_mover"] == "BA")].copy()
            other = b[(b["technology"] != "Batteries") | (b["energy_source"] != "MWH")]
            if len(other):  # a unit EIA codes BA but names otherwise: kept, and logged
                log(f"  {table}: {len(other)} BA units with technology or energy source other than Batteries/MWH")
            b["source_table"] = table
            b["planned_year"] = b["planned_operation_date"].str[:4] if "planned_operation_date" in b else ""
            for c in ("operating_year", "retirement_date", "energy_capacity_mwh"):
                if c not in b:
                    b[c] = ""
            log(f"  {table}: {len(b)} battery units, {pd.to_numeric(b['nameplate_mw']).sum():,.1f} MW")
            parts.append(b)
        a = pd.concat(parts, ignore_index=True)
        if a["entity_id"].duplicated().any():
            dup = a.loc[a["entity_id"].duplicated(keep=False), ["entity_id", "source_table"]]
            raise RuntimeError(f"a unit is in two of the EIA-860M tables: {dup.head(6).to_dict('records')}")
        out = pd.DataFrame({
            "entity_id": a["entity_id"], "entity_type": "generator", "name": a["name"], "geo": a["geo"],
            "lat": a["lat"], "lon": a["lon"], "capacity_mw": a["nameplate_mw"], "status": a["status"],
            "status_date": a["status_date"], "operator": a["operator"], "source": "erw:storage_capacity",
            "source_url": METHOD_URL, "retrieved_at": now, "vintage": a["vintage"], "plant_id": a["plant_id"],
            "generator_id": a["generator_id"], "state": a["state"], "county": a["county"],
            "balancing_authority": a["balancing_authority"], "iso": a["balancing_authority"].map(ISO_OF_BA).fillna(""),
            "net_summer_mw": a["net_summer_mw"], "eia_status": a["eia_status"], "operating_year": a["operating_year"],
            "planned_year": a["planned_year"], "retirement_date": a["retirement_date"], "source_table": a["source_table"],
            "input_source_url": a["source_url"], "energy_capacity_mwh": a["energy_capacity_mwh"]})[COLS].sort_values("entity_id").reset_index(drop=True)
        vint = sorted(set(a["source_url"]))
        header = [
            "Energy Research Warehouse (ERW): Battery storage units, operating, planned and retired, from EIA-860M "
            "(derived, session 31)",
            "Shape: entities (docs/datastandard.md), a snapshot: each run replaces the table. One row per battery "
            "generator (prime mover BA). capacity_mw is EIA's nameplate MW.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/storage_capacity.py",
            f"Run log: warehouse/output/logs/storage_capacity_{run_id}.log",
            f"Source: erw:storage_capacity ERW derived table, storage method (docs/methods/storage.md), {METHOD_URL}",
            "Derived from: " + "; ".join(INPUTS.values()),
            "  input sources: eia:860m (" + "; ".join(vint) + ")",
            "iso: the ISO of the unit's balancing authority where it is one of the seven (CISO CAISO, ERCO ERCOT, ISNE "
            "ISO-NE, MISO, NYIS NYISO, PJM, SWPP SPP), else empty. energy_capacity_mwh: EIA's Nameplate Energy "
            "Capacity (MWh) (session 34), given by EIA for operating and retired units, not for planned ones; never "
            "estimated from MW.",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23).",
        ]
        ip.write_snapshot(out, NAME, header, log, COLS)
        ip.update_sources([{"source": "erw:storage_capacity", "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Battery storage units from EIA-860M (docs/methods/storage.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": [NAME]}])
        by = out.assign(mw=pd.to_numeric(out["capacity_mw"]), mwh=pd.to_numeric(out["energy_capacity_mwh"])
                        ).groupby("status").agg(size=("mw", "size"), mw=("mw", "sum"), mwh=("mwh", "sum"))
        status["detail"] = "; ".join(f"{s}: {int(r['size'])} units, {r['mw']:,.1f} MW, {r['mwh']:,.1f} MWh"
                                     for s, r in by.iterrows())
        log(status["detail"])
        print(f"storage_capacity: {len(out)} units; {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"storage_capacity FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("storage_capacity", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
