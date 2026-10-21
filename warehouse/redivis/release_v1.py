#!/usr/bin/env python3
"""Redivis release v1, prepared (session 275): everything a person needs for one click, and nothing done on Redivis.

Energy Research Warehouse (ERW). docs/redivis/release-v1.md is the person's steps. This builds the package from what
the repository and this machine hold, makes no request and writes nothing to Redivis:

    python warehouse/redivis/release_v1.py                     docs/redivis/release-v1/: tables.csv, variables.csv, README.md
    python warehouse/redivis/release_v1.py --out-dir DIR       read the tables from DIR (a worktree reads the main checkout's)
    python warehouse/redivis/release_v1.py --check             the files agree with coverage and the license record (exit 1 if not)

Which tables are in v1: every table that coverage.csv flags public and that is public on 21 October 2026, the public
day: not "license needed" in warehouse/metadata/license_status.csv without a recorded permission, not retired
(retired_tables.csv), not a consolidated table's old member (table_migrations.csv). The rest of the public dataset's
draft is named in tables.csv with its reason, so the person removes exactly those before the click. The metadata tables
the uploader adds (erw_coverage, erw_sources, erw_headers) are in v1 too.

    tables.csv     table, in_v1, reason, shape, rows, first, last, interval, description (the header's title line),
                   license_line (the header's own "License:" line), citation, publishers
    variables.csv  table, name, kind (series variable or column), unit
    README.md      the dataset's README, for Redivis's dataset description
"""

import argparse
import csv
import datetime as dt
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
META = os.path.join(ROOT, "warehouse", "metadata")
DOCS = os.path.join(ROOT, "docs", "redivis", "release-v1")
PUBLIC_DAY = "2026-10-21"
DATASET = "energy_research_warehouse"
METADATA_TABLES = ("erw_coverage", "erw_sources", "erw_headers")
SERIES_FIRST = ["entity", "variable", "ts_utc", "value"]


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def header(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            out.append(ln[1:].strip())
    return out


def held(day=PUBLIC_DAY):
    """{table: reason} of the tables held from the public day: license needed, no permission recorded."""
    out = {}
    for r in rows(os.path.join(META, "license_status.csv")):
        if r["status"] == "license needed" and r["from"] <= day and not r.get("permission"):
            out[r["table"]] = f"license needed from {r['from']} ({r['publishers']}: {r['verdict']}); held whole for v1"
    return out


# Session 375: a public table the draft cannot hold for Redivis's storage (the account's free 10 GB is full, session
# 363). It is marked "held", not dropped: in v1 by its license, uploaded once the storage is settled (the owner's).
STORAGE_HELD = {
    "node_basis_daily": "held: Redivis storage (the account's free 10 GB is full; refused on 20 October 2026, session 363). "
                        "In v1 by its license once uploaded: python warehouse/redivis/upload.py node_basis_daily, after the storage is settled",
    # session 385: in the draft until 20 October, when the daily's upload was refused for storage (17:32 UTC) and the
    # uploader, which deletes a table before it uploads the new copy, left it out (Redivis answers 404 for it)
    "ercot_all_hub_prices_history": "held: Redivis storage (the account's free 10 GB is full; the upload of 20 October 2026, 17:32 UTC, "
                                    "was refused and the table is no longer in the draft, session 385). In v1 by its license once "
                                    "uploaded again: python warehouse/redivis/upload.py ercot_all_hub_prices_history, after the storage is settled",
}
# Session 489: the public tables of sessions 485 to 496 and 507, written on 21 October 2026 and never uploaded (an upload is a
# person's, and the storage is full). Held the same way: in v1 by their license once uploaded.
for _t in ("boem_renewable_leases", "egrid_power_plants", "eia861_utility_sales", "eia_aeo_electricity",
           "eia_seds_state_energy", "eia_steo_forecasts", "epa_ghgrp_power_co2", "nlr_atb_electricity_costs",
           "uswtdb_wind_turbines", "eia923_plant_fuel_annual", "eia861m_utility_sales_monthly",
           "eia_nuclear_outages_daily", "eia_nuclear_outages_facility_daily",
           "eia_gas_prices_state_monthly", "eia_gas_consumption_state_monthly", "eia_coal_prices_annual",
           "eia_gas_storage_state_monthly", "eia_state_capacity_annual", "eia_crude_production_state_monthly",
           "eia_gas_production_state_monthly"):  # 510 to 528 the same way
    STORAGE_HELD[_t] = ("held: not yet on Redivis (written 21 October 2026, session 489; the account's free 10 GB is full, "
                        f"session 363). In v1 by its license once uploaded: python warehouse/redivis/upload.py {_t}, after the "
                        "storage is settled")


def plan(day=PUBLIC_DAY):
    """[(table, in_v1, reason)] over coverage, in coverage's order."""
    cov = rows(os.path.join(META, "coverage.csv"))
    retired = {r["table"] for r in rows(os.path.join(META, "retired_tables.csv"))}
    migrated = {r["old_table"] if "old_table" in r else r[list(r)[0]] for r in rows(os.path.join(META, "table_migrations.csv"))}
    hold = held(day)
    out = []
    for r in cov:
        t = r["table"]
        if r["license"] != "public":
            continue   # an internal table is never in the public dataset (upload.py routes it to the private one)
        if t in retired:
            out.append((t, "no", "retired (warehouse/metadata/retired_tables.csv)"))
        elif t in migrated:
            out.append((t, "no", "a consolidated table's old member (warehouse/metadata/table_migrations.csv)"))
        elif t in hold:
            out.append((t, "no", hold[t]))
        elif t in STORAGE_HELD:
            out.append((t, "held", STORAGE_HELD[t]))
        else:
            out.append((t, "yes", "public, and public on the public day"))
    return out


def verdicts(path=os.path.join(ROOT, "docs", "licenses.md")):
    """{table: (publishers, verdict today)} from docs/licenses.md, "Every table" (session 205's record)."""
    out, on = {}, False
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("## "):
                on = ln.strip() == "## Every table"
                continue
            m = re.match(r"^\| `([a-z0-9_]+)` \| ([^|]*) \| ([^|]*) \|", ln) if on else None
            if m:
                out[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
    return out


def citation(table, sources, publishers):
    reps = [s for s in sources if table in [x.strip() for x in re.split(r"[;,]", s.get("tables", ""))]]
    names = sorted({s["publisher"] for s in reps}) or ([publishers] if publishers else [])
    reports = sorted({s["report"] for s in reps})
    head = "; ".join(names) if names else "Energy Research Warehouse (ERW)"
    rep = (" " + "; ".join(reports) + ".") if reports else ""
    return (f"{head}.{rep} Via the Energy Research Warehouse (ERW), table `{table}`, Redivis dataset `{DATASET}`, version v1 "
            "(released <date of the click>).")


def shape(cols):
    if cols[:4] == SERIES_FIRST:
        return "series"
    if cols[:2] == ["entity_id", "entity_type"]:
        return "entities"
    if "event_id" in cols:
        return "events"
    return "other"


def variables(path, cols, kind):
    """[(name, kind, unit)]: a series table's variables with their units (read in chunks), else its columns."""
    if kind != "series":
        return [(c, "column", "") for c in cols]
    seen = set()
    n = len(header(path))
    for ch in pd.read_csv(path, skiprows=n, usecols=["variable", "unit"], dtype=str, keep_default_na=False, chunksize=500_000):
        seen |= set(zip(ch["variable"], ch["unit"]))
    return [(v, "series variable", u) for v, u in sorted(seen)]


def build(out_dir, day=PUBLIC_DAY):
    cov = {r["table"]: r for r in rows(os.path.join(META, "coverage.csv"))}
    sources = rows(os.path.join(META, "sources.csv"))
    pubs = {r["table"]: r["publishers"] for r in rows(os.path.join(META, "license_tables.csv"))}
    record = verdicts()
    tables, variables_out, missing = [], [], []
    for t, in_v1, reason in plan(day):
        c = cov[t]
        path = os.path.join(out_dir, t + ".csv")
        head = header(path) if os.path.exists(path) else []
        title = (head[0] if head else "").replace("Energy Research Warehouse (ERW): ", "", 1)
        lic = next((h for h in head if h.startswith("License:")), "")
        if not lic and t in record:   # no license line in the header: the license record's verdict for the table
            who, verdict = record[t]
            lic = f"License: public. The publishers' own terms ({who}), as the ERW read them: {verdict} (docs/licenses.md)."
        cols, kind = [], ""
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                for ln in f:
                    if not ln.startswith("#"):
                        cols = next(csv.reader([ln]))
                        break
            kind = shape(cols)
            if in_v1 in ("yes", "held"):
                variables_out += [dict(table=t, name=n, kind=k, unit=u) for n, k, u in variables(path, cols, kind)]
        elif in_v1 == "yes":
            missing.append(t)
        tables.append(dict(table=t, in_v1=in_v1, reason=reason, shape=kind, rows=c["n_rows"], first=c["ts_min"], last=c["ts_max"],
                           interval=c["interval"], description=title, license_line=lic, citation=citation(t, sources, pubs.get(t, "")),
                           publishers=pubs.get(t, "")))
    for m in METADATA_TABLES:
        tables.append(dict(table=m, in_v1="yes", reason="metadata the uploader adds (warehouse/redivis/upload.py)", shape="metadata",
                           rows="", first="", last="", interval="", description={"erw_coverage": "warehouse/metadata/coverage.csv: every table, its range, rows, license and sources",
                                                                                 "erw_sources": "warehouse/metadata/sources.csv: the source registry",
                                                                                 "erw_headers": "every provenance header line of every table in the dataset"}[m],
                           license_line="License: public (the ERW's own metadata).", citation=f"Energy Research Warehouse (ERW), table `{m}`, Redivis dataset `{DATASET}`, version v1.",
                           publishers="Energy Research Warehouse (ERW)"))
    return tables, variables_out, missing


def readme(tables, day=PUBLIC_DAY):
    v1 = [t for t in tables if t["in_v1"] == "yes" and t["shape"] != "metadata"]
    out = [t for t in tables if t["in_v1"] == "no"]
    stored = [t for t in tables if t["in_v1"] == "held"]
    stored_names = ", ".join("`" + t["table"] + "`" for t in stored)
    stored_line = (f" {len(stored)} public table{'s' if len(stored) != 1 else ''} ({stored_names}) "
                   f"{'are' if len(stored) != 1 else 'is'} in version 1 by license but not yet in the dataset: the account's storage is "
                   "full, and the table is added once it is settled.") if stored else ""
    by_shape = {}
    for t in v1:
        by_shape[t["shape"]] = by_shape.get(t["shape"], 0) + 1
    return "\n".join([
        "# Energy Research Warehouse (ERW), version 1",
        "",
        "The live, citable record of the US energy system: prices, flows, projects, deals and policy across power, natural gas, oil, nuclear, renewables, "
        "storage and transmission, with the global prices and events that move US markets. Every source is reshaped into three standard table shapes "
        "so that tables can be joined and compared: `series` (one row per observation: entity, variable, ts_utc, value), `entities` (one row per "
        "physical or corporate thing) and `events` (one row per deal, filing or announcement). Timestamps are UTC; power is MW and prices are USD per "
        "MWh unless a `unit` column says otherwise. The data standard: https://github.com/SamuelEnrique/erw/blob/main/docs/datastandard.md",
        "",
        f"**Version 1 holds {len(v1)} tables** ({', '.join(f'{n} {s}' for s, n in sorted(by_shape.items()))}) and three metadata tables "
        "(`erw_coverage`, `erw_sources`, `erw_headers`). Every table's description is its provenance header: the source report, its address, when "
        "it was retrieved, the method, and its license line.",
        "",
        "## What is not in it",
        "",
        f"{len(out)} tables of the warehouse's public draft are not in version 1: a table whose publisher's terms ask for permission or a license "
        f"that has not been recorded is held from {day} (the ERW's license record, https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md), "
        "and retired tables and the old members of consolidated tables are not tables of the warehouse. Tables licensed for internal use are never "
        "in this dataset." + stored_line,
        "",
        "## How to cite",
        "",
        "Cite the organization that published the data, then the ERW table and this version. For example:",
        "",
        "> U.S. Energy Information Administration (EIA). Spot prices. Via the Energy Research Warehouse (ERW), table `eia_fuel_spot_prices`, "
        f"Redivis dataset `{DATASET}`, version v1.",
        "",
        "Each table's own citation is in `docs/redivis/release-v1/tables.csv` in the repository.",
        "",
        "## How it is made",
        "",
        "One connector per source pulls, reshapes and validates; the validator is the gate a table passes before upload. Uploads write a draft only; "
        "a version is released by a person after reading what the draft changes. Code, methods and the session reports: "
        "https://github.com/SamuelEnrique/erw",
        "",
        "## Credit",
        "",
        "The Energy Research Warehouse is adapted, with permission, from the infrastructure and documents of the Item Response Warehouse "
        "(github.com/ben-domingue/irw).",
        "",
    ])


def write(out_dir, docs=DOCS):
    tables, vars_, missing = build(out_dir)
    os.makedirs(docs, exist_ok=True)
    cols = ["table", "in_v1", "reason", "shape", "rows", "first", "last", "interval", "description", "license_line", "citation", "publishers"]
    with open(os.path.join(docs, "tables.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(tables)
    with open(os.path.join(docs, "variables.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["table", "name", "kind", "unit"], lineterminator="\n")
        w.writeheader()
        w.writerows(vars_)
    with open(os.path.join(docs, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(readme(tables))
    return tables, vars_, missing


def check(docs=DOCS):
    """The written list against today's plan: the same tables, the same in_v1. Returns the problems."""
    have = {r["table"]: r["in_v1"] for r in rows(os.path.join(docs, "tables.csv"))}
    want = {t: v for t, v, _ in plan()} | {m: "yes" for m in METADATA_TABLES}
    return [f"{t}: tables.csv says {have.get(t)}, the record says {want.get(t)}" for t in sorted(set(have) | set(want)) if have.get(t) != want.get(t)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "warehouse", "output"), help="the folder that holds the tables")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        bad = check()
        for b in bad:
            print(b)
        print(f"release v1: {len(bad)} difference(s) between docs/redivis/release-v1/tables.csv and the license record")
        return 1 if bad else 0
    tables, vars_, missing = write(a.out_dir)
    v1 = sum(1 for t in tables if t["in_v1"] == "yes")
    print(f"docs/redivis/release-v1: {v1} tables in v1 (with the three metadata tables), {len(tables) - v1} public tables held out; "
          f"{len(vars_)} variables and columns; written {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%MZ}")
    for t in missing:
        print(f"MISSING: {t} is in v1 but not in {a.out_dir}: its variables are not listed")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
