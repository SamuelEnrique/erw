#!/usr/bin/env python3
"""The datacenter tracker's rollups: facilities and stated MW by grid, state and operator (session 2236, chain 156).

Energy Research Warehouse (ERW). Read from `datacenter_projects` (the facilities the news names,
`warehouse/datacenters/extract.py`), written as the series shape so the page and Ask read one number a key:

    entity    grid:<ERCOT|PJM|...|none>, state:<XX|none>, operator:<canonical name|none>, tracker:all
    variable  facilities; facilities_with_mw; facilities_without_mw; mw_stated; and mw_stated_<status> for planned,
              under_construction, operating, withdrawn and none (a facility whose stories state no status)
    ts_utc    the day the rollup was built (00:00 UTC); unit count or MW; freq P1D (a daily snapshot)

The grid is the facility's `grid` (named in its stories, or the state's main grid: `grid_basis` says which); the
operator is the operator, else the developer, joined to one name as the deal tracker joins counterparties
(`warehouse/deals/counterparties.py`). A sum is of the MW the stories state, whatever its basis (`mw_basis`: IT,
total, a tenant's share, a phase, unstated); the facilities that state none are counted beside it, never as zero.

    python warehouse/derived/datacenter_tracker_rollups.py              # warehouse/output/datacenter_tracker_rollups.csv (data lock)
    python warehouse/derived/datacenter_tracker_rollups.py --out DIR    # elsewhere (no lock)
"""

import argparse
import datetime as dt
import os
import sys

import pandas as pd


def _hdr(path):
    """The number of "#" header lines before a table's column row (iso_prices.header_rows: never comment="#")."""
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters"))
import counterparties as cp  # noqa: E402
import facility_fields as ff  # noqa: E402

NAME = "datacenter_tracker_rollups"
STATUSES = ["planned", "under_construction", "operating", "withdrawn"]
SOURCE_URL = "https://github.com/SamuelEnrique/erw/blob/main/warehouse/derived/datacenter_tracker_rollups.py"
# Session 3775 (chain 212): the rows name this source, and build_coverage.py sets a table's license from its sources'
# entries in warehouse/metadata/sources.csv. No run ever registered it, so every daily run that reached coverage with this
# table written stopped there ("sources ['erw:datacenter_projects'] are not in sources.csv; cannot set its license", the
# runs of 7 and 12 November) and committed nothing. Internal, as its one input datacenter_projects is (license needed since
# 21 October 2026).
SOURCE = "erw:datacenter_projects"
SOURCE_ENTRY = dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                    report="The datacenter tracker's rollups by grid, state and operator, from datacenter_projects (docs/methods/datacenter_tracker_rollups.md)",
                    report_url="https://github.com/SamuelEnrique/erw/blob/main/docs/methods/datacenter_tracker_rollups.md",
                    document_list="docs/methods/datacenter_tracker_rollups.md", license="internal", tables=[NAME])


def rollups(fac, day):
    """The series rows (a list of dicts) of one day's rollups from the facilities frame."""
    fac = fac.copy()
    if "grid" not in fac.columns or (fac["grid"] == "").all():
        fac = pd.DataFrame([ff.derive(r) for r in fac.to_dict("records")])
    names = cp.Names([x for x in list(fac.get("operator", [])) + list(fac.get("developer", [])) if x], aliases=None)
    fac["_operator"] = [names.name(o or d) if (o or d) else "" for o, d in zip(fac["operator"], fac["developer"])]
    fac["_mw"] = pd.to_numeric(fac["mw"], errors="coerce")
    fac["_status"] = fac["status"].where(fac["status"].isin(STATUSES), "none")
    out = []
    groups = [("all", fac.assign(_k="all").groupby("_k"))]
    for dim, col in (("grid", "grid"), ("state", "state"), ("operator", "_operator")):
        f = fac.assign(_k=fac[col].where(fac[col] != "", "none"))
        groups.append((dim, f.groupby("_k")))
    ts = f"{day}T00:00:00Z"
    for dim, g in groups:
        for k, part in g:
            entity = "tracker:all" if dim == "all" else f"{dim}:{k}"
            with_mw = part["_mw"].notna()
            vals = {"facilities": (len(part), "count"), "facilities_with_mw": (int(with_mw.sum()), "count"),
                    "facilities_without_mw": (int((~with_mw).sum()), "count"),
                    "mw_stated": (float(part["_mw"].sum()) if with_mw.any() else None, "MW")}
            for s in STATUSES + ["none"]:
                p = part[part["_status"] == s]
                vals[f"mw_stated_{s}"] = (float(p["_mw"].sum()) if p["_mw"].notna().any() else None, "MW")
            for v, (x, unit) in vals.items():
                if x is None:
                    continue   # no facility of the group states MW: no sum, never a zero
                out.append({"entity": entity, "variable": v, "ts_utc": ts, "value": x, "unit": unit, "freq": "P1D",
                            "geo": f"US-{k}" if dim == "state" and k != "none" else "", "market": "", "node": "",
                            "source": SOURCE, "source_url": SOURCE_URL, "retrieved_at": ts,
                            "vintage": ts})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    import iso_prices as ip
    src = os.path.join(ip.OUT_DIR, "datacenter_projects.csv")
    fac = pd.read_csv(src, skiprows=_hdr(src), dtype=str, keep_default_na=False)
    day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    rows = pd.DataFrame(rollups(fac, day), columns=ip.SERIES_COLS)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    header = [
        "Energy Research Warehouse (ERW): the datacenter tracker's rollups by grid, state and operator (platform tool 4)",
        "Shape: series (docs/datastandard.md); derived from datacenter_projects by warehouse/derived/datacenter_tracker_rollups.py (session 2236). One row a group, a variable and a day.",
        f"Retrieved: {run_id} (UTC) from warehouse/output/datacenter_projects.csv ({len(fac)} facilities)",
        "Columns: entity grid:<grid> (named in the stories, or the state's main grid), state:<XX>, operator:<name> (the operator, else the developer, joined as warehouse/deals/counterparties.py joins names), tracker:all; a sum is of the MW the stories state, any basis; facilities_without_mw counts the rest; a group with no stated MW has no sum.",
        "License: as datacenter_projects (license needed since 2026-10-21).",
        "Sources: datacenter_projects (the news the ERW scores).",
    ]
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        path = os.path.join(args.out, NAME + ".csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            for h in header:
                f.write("# " + h + "\n")
            rows.to_csv(f, index=False, lineterminator="\n")
        print(f"{path}: {len(rows)} rows")
    else:
        log = ip.Log(os.path.join(ip.LOG_DIR, f"datacenter_tracker_rollups_{run_id}.log"))
        ip.write_csv(rows, NAME, header, log)
        ip.update_sources([SOURCE_ENTRY])   # session 3775: before coverage reads the table's sources
        log.close()
    print(f"datacenter_tracker_rollups: {len(rows)} rows from {len(fac)} facilities")
    return 0


if __name__ == "__main__":
    sys.exit(main())
