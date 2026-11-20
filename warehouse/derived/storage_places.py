#!/usr/bin/env python3
"""ERW: batteries by balancing authority and by state, the page file site/data/storage/places.json (session 8014, chain 581 part F1).

Energy Research Warehouse (ERW). Writes one new page file; no table, no request. Read by /storage/places (any authority
or state, two side by side, beside the seven grids' figures /storage has). Method: docs/methods/storage_places.md.

Every battery unit of EIA's monthly generator inventory (Form EIA-860M), the units the storage page counts (prime mover
BA): operating units' nameplate MW and nameplate energy capacity MWh (where EIA gives it), and by year of start; planned
units' MW by EIA's planned year and status (EIA's planned sheet gives no MWh). Placed by the unit's own balancing
authority and state as EIA-860M prints them. Nothing is estimated: MWh is never computed from MW, and a unit with no
authority in EIA-860M is counted under "not named".

    python warehouse/derived/storage_places.py                # site/data/storage/places.json
    python warehouse/derived/storage_places.py --site-dir DIR # a trial
"""
import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SITE_FILE = os.path.join(ROOT, "site", "data", "storage", "places.json")
GRIDS = {"CISO": "CAISO", "ERCO": "ERCOT", "ISNE": "ISO-NE", "MISO": "MISO", "NYIS": "NYISO", "PJM": "PJM", "SWPP": "SPP"}
SOURCE = "U.S. Energy Information Administration, Preliminary Monthly Electric Generator Inventory (Form EIA-860M)"


def read(name, cols):
    p = os.path.join(OUT, name + ".csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, usecols=cols, dtype=str, keep_default_na=False)
    fh.close()
    for c in ("nameplate_mw", "energy_capacity_mwh"):
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d


def r1(v):
    return None if v is None or pd.isna(v) else round(float(v), 1)


def place(op, pl, key, value):
    o, p = op[op[key] == value], pl[pl[key] == value]
    mwh_known = o["energy_capacity_mwh"].notna() & (o["energy_capacity_mwh"] > 0)
    years = {}
    for y, g in o.groupby("operating_year"):
        years[y or "no year"] = {"mw": r1(g["nameplate_mw"].sum()), "mwh": r1(g.loc[g["energy_capacity_mwh"].notna(), "energy_capacity_mwh"].sum()), "units": int(len(g))}
    planned = {}
    for y, g in p.assign(year=p["planned_operation_date"].str.slice(0, 4)).groupby("year"):
        planned[y or "no date"] = {"mw": r1(g["nameplate_mw"].sum()), "units": int(len(g)),
                                   "under_construction_mw": r1(g.loc[g["status"] == "under_construction", "nameplate_mw"].sum())}
    return {"operating_mw": r1(o["nameplate_mw"].sum()), "operating_units": int(len(o)),
            "operating_mwh": r1(o.loc[mwh_known, "energy_capacity_mwh"].sum()) if mwh_known.any() else None,
            "operating_mw_with_mwh": r1(o.loc[mwh_known, "nameplate_mw"].sum()) if mwh_known.any() else None,
            "units_without_mwh": int((~mwh_known).sum()),
            "planned_mw": r1(p["nameplate_mw"].sum()), "planned_units": int(len(p)),
            "by_year_of_start": dict(sorted(years.items())), "planned_by_year": dict(sorted(planned.items()))}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: batteries by balancing authority and by state")
    ap.add_argument("--site-dir")
    a = ap.parse_args(argv)
    cols = ["plant_id", "generator_id", "state", "balancing_authority", "prime_mover", "nameplate_mw", "vintage"]
    op = read("eia860m_operating_generators", cols + ["energy_capacity_mwh", "operating_year"])
    pl = read("eia860m_planned_generators", cols + ["planned_operation_date", "status"])
    op, pl = op[op["prime_mover"] == "BA"].copy(), pl[pl["prime_mover"] == "BA"].copy()
    for d in (op, pl):
        d["ba"] = d["balancing_authority"].replace("", "not named")
    with open(os.path.join(ROOT, "site", "data", "regions", "index.json"), encoding="utf-8") as fh:
        meta = {b["code"]: b for b in json.load(fh)["bas"]}
    bas = {}
    for code in sorted(set(op["ba"]) | set(pl["ba"])):
        m = meta.get(code, {})
        bas[code] = {"code": code, "name": m.get("name") if m else None, "region": m.get("region") if m else None, "grid": GRIDS.get(code),
                     **place(op, pl, "ba", code)}
    states = {}
    for st in sorted(set(op["state"]) | set(pl["state"])):
        if st:
            states[st] = {"state": st, **place(op, pl, "state", st)}
    us = place(op.assign(all="US"), pl.assign(all="US"), "all", "US")
    doc = {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "method": "docs/methods/storage_places.md", "license": "public",
           "tables": ["eia860m_operating_generators", "eia860m_planned_generators"], "source": SOURCE, "vintage": op["vintage"].iloc[0] if len(op) else None,
           "units": "MW nameplate; MWh nameplate energy capacity where EIA gives it (operating units only; EIA's planned sheet has none)",
           "rule": "Every battery unit (prime mover BA) of EIA-860M, placed by its own balancing authority and state as EIA prints them; a unit with no authority is under 'not named'. MWh is summed only over the units that give it, and the MW of those units is given beside it.",
           "us": us, "authorities": bas, "states": states}
    path = os.path.join(a.site_dir, "places.json") if a.site_dir else SITE_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), allow_nan=False)
    print(f"storage_places: {len(bas)} authorities, {len(states)} states; operating {us['operating_mw']:,} MW in {us['operating_units']} units; {os.path.getsize(path):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
