#!/usr/bin/env python3
"""The reactor fleet by reactor and year, and by grid and year: capacity, outages, refueling cadence, uprates, restarts
and retirements (session 2955, chain 157).

Energy Research Warehouse (ERW). One derived table, nuclear_fleet_status, from EIA's daily nuclear outages by reactor
(eia_nuclear_outages_generator_daily, EIA's estimates from the NRC's daily power reactor status reports, 2007 on) and
each reactor's grid from EIA-860M (eia860m_operating_generators, its plant's balancing authority). Method:
docs/methods/nuclear_fleet_status.md. No request.

    python warehouse/derived/nuclear_fleet_status.py               # the table (data lock)
    python warehouse/derived/nuclear_fleet_status.py --out-dir DIR # a trial

    entity    nuclear_fleet:<facility>:<generator> (a reactor, node its name) and nuclear_fleet:grid:<BA> and :US
    ts_utc    the year's first day; freq P1Y
    variables a reactor: capacity_mw (the year's highest daily capacity), outage_share (outage MW-days over capacity
              MW-days), full_outage_days (days at 99 percent out or more), long_outages (runs of 14 or more full-outage
              days, the refueling and long outages), available_mwh ((capacity less outage) x 24 summed over the days),
              days_held, capacity_change_mw (capacity_mw less the year before's: an uprate or derate), first_day and
              last_day (x_first, x_last, as dates: a reactor's first and last days held, its restart or retirement)
              the fleet: capacity_mw, available_mwh, outage_share, reactors (count), by grid and for the US
A year with fewer than 300 days held for a reactor is written with days_held only, but for its first and last years
(a restart or a retirement), whose figures are its own. Nothing is filled.
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "nuclear_fleet_status"
SOURCE = "erw:nuclear_fleet_status"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/nuclear_fleet_status.md"
OUTAGES, PLANTS = "eia_nuclear_outages_generator_daily", "eia860m_operating_generators"
FULL, LONG, NEAR_YEAR = 0.99, 14, 300
UNITS = {"capacity_mw": "MW", "outage_share": "ratio", "full_outage_days": "count", "long_outages": "count", "available_mwh": "MWh",
         "days_held": "count", "capacity_change_mw": "MW", "reactors": "count"}
COLS = ip.SERIES_COLS + ["x_facility", "x_generator", "x_ba", "x_first", "x_last"]


def read_outages(path):
    keep = []
    for ch in pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, chunksize=500_000,
                          usecols=["entity", "variable", "ts_utc", "value", "node"]):
        keep.append(ch[ch["variable"].isin(["capacity", "outage"])])
    d = pd.concat(keep, ignore_index=True)
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    w = d.pivot_table(index=["entity", "ts_utc"], columns="variable", values="v", aggfunc="first").reset_index()
    names = d.drop_duplicates("entity").set_index("entity")["node"]
    w["day"] = pd.to_datetime(w["ts_utc"].str[:10])
    return w, names


def ba_of(path):
    """{facility id: balancing authority} from EIA-860M's operating nuclear generators (energy source NUC)."""
    d = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, usecols=["plant_id", "energy_source", "balancing_authority"])
    d = d[d["energy_source"] == "NUC"]
    return d.groupby("plant_id")["balancing_authority"].agg(lambda v: sorted(set(v))[0]).to_dict()


def runs(full):
    """The lengths of the runs of True in a day-ordered boolean series."""
    out, n = [], 0
    for x in full:
        if x:
            n += 1
        elif n:
            out.append(n)
            n = 0
    if n:
        out.append(n)
    return out


def reactor_years(g):
    g = g.sort_values("day")
    first, last = g["day"].min(), g["day"].max()
    out = {}
    for y, x in g.groupby(g["day"].dt.year):
        cap, outage = x["capacity"], x["outage"].fillna(0).clip(lower=0)
        days = int(cap.notna().sum())
        f = {"days_held": days}
        whole = days >= NEAR_YEAR or y in (first.year, last.year)
        if whole and cap.sum() > 0:
            share = (outage / cap.where(cap > 0)).fillna(0)
            f.update({"capacity_mw": float(cap.max()), "outage_share": float(min(outage.sum() / cap.sum(), 1.0)),
                      "full_outage_days": int((share >= FULL).sum()), "long_outages": int(sum(1 for r in runs(share >= FULL) if r >= LONG)),
                      "available_mwh": float(((cap - outage).clip(lower=0) * 24).sum())})
        out[int(y)] = f
    for y in sorted(out):
        if "capacity_mw" in out[y] and "capacity_mw" in out.get(y - 1, {}):
            out[y]["capacity_change_mw"] = out[y]["capacity_mw"] - out[y - 1]["capacity_mw"]
    return out, first, last


def build(folder=None):
    folder = folder or ip.OUT_DIR
    w, names = read_outages(os.path.join(folder, f"{OUTAGES}.csv"))
    bas = ba_of(os.path.join(folder, f"{PLANTS}.csv"))
    rows, fleet = [], {}
    for ent, g in w.groupby("entity"):
        fac, gen = ent.split(":")[1:3]
        ba = bas.get(fac, "none")
        yrs, first, last = reactor_years(g)
        for y, f in yrs.items():
            for var, val in f.items():
                rows.append({"entity": f"nuclear_fleet:{fac}:{gen}", "variable": var, "ts_utc": f"{y}-01-01T00:00:00Z", "value": round(val, 4) if isinstance(val, float) else val,
                             "unit": UNITS[var], "freq": "P1Y", "geo": "US", "market": "", "node": names.get(ent, ""), "source": SOURCE, "source_url": METHOD_URL,
                             "vintage": "", "x_facility": fac, "x_generator": gen, "x_ba": ba, "x_first": first.strftime("%Y-%m-%d"), "x_last": last.strftime("%Y-%m-%d")})
            if "capacity_mw" in f:
                for key in (ba, "US"):
                    a = fleet.setdefault((key, y), {"capacity_mw": 0.0, "available_mwh": 0.0, "cap_days": 0.0, "out_days": 0.0, "reactors": 0})
                    a["capacity_mw"] += f["capacity_mw"]
                    a["available_mwh"] += f["available_mwh"]
                    a["reactors"] += 1
                    x = g[g["day"].dt.year == y]
                    a["cap_days"] += float(x["capacity"].sum())
                    a["out_days"] += float(x["outage"].fillna(0).clip(lower=0).sum())
    for (key, y), a in sorted(fleet.items()):
        ent = "nuclear_fleet:US" if key == "US" else f"nuclear_fleet:grid:{key}"
        for var, val in (("capacity_mw", a["capacity_mw"]), ("available_mwh", a["available_mwh"]), ("reactors", a["reactors"]),
                         ("outage_share", a["out_days"] / a["cap_days"] if a["cap_days"] else None)):
            if val is None:
                continue
            rows.append({"entity": ent, "variable": var, "ts_utc": f"{y}-01-01T00:00:00Z", "value": round(val, 4) if isinstance(val, float) else val,
                         "unit": UNITS[var], "freq": "P1Y", "geo": "US", "market": "", "node": "", "source": SOURCE, "source_url": METHOD_URL, "vintage": "",
                         "x_facility": "", "x_generator": "", "x_ba": "" if key == "US" else key, "x_first": "", "x_last": ""})
    t = pd.DataFrame(rows, columns=COLS)
    return t.sort_values(["entity", "ts_utc", "variable"]).reset_index(drop=True), w["day"].min(), w["day"].max()


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the reactor fleet by reactor and year, and by grid (session 2955)")
    ap.add_argument("--out-dir", help="a trial: the table under this folder")
    a = ap.parse_args(argv)
    folder = ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        t, d0, d1 = build(folder)
        t["retrieved_at"] = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
        n = t[t["entity"].str.count(":") == 2]["entity"].nunique()
        header = [
            "Energy Research Warehouse (ERW): the U.S. reactor fleet by reactor and year, and by grid and year: capacity, outages, long outages, available energy, uprates, restarts and retirements (derived, session 2955)",
            "Shape: series (docs/datastandard.md v0). entity nuclear_fleet:<facility>:<generator> (a reactor), nuclear_fleet:grid:<BA>, nuclear_fleet:US; ts_utc the year's first day, freq P1Y; variables "
            + ", ".join(f"{k} ({u})" for k, u in UNITS.items()) + "; x_first and x_last a reactor's first and last days held.",
            f"Days {d0:%Y-%m-%d} to {d1:%Y-%m-%d}; {n} reactors. A year with fewer than {NEAR_YEAR} days held gets days_held only, but a reactor's first and last years. "
            f"A full-outage day is {int(FULL * 100)} percent out or more; a long outage {LONG} or more such days in a row. A reactor's grid is its plant's balancing authority in EIA-860M (none where EIA-860M lists no operating NUC generator at the plant).",
            f"Derived from: {OUTAGES}; {PLANTS}",
            "Built by warehouse/derived/nuclear_fleet_status.py; method docs/methods/nuclear_fleet_status.md",
            f"Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Source: eia:nuclear-outages U.S. Energy Information Administration, Status of U.S. Nuclear Outages (from the NRC's power reactor status reports); EIA-860M",
            'License: public (works of the U.S. government; cite "U.S. Energy Information Administration").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=COLS)
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="The U.S. reactor fleet by reactor and year, and by grid (docs/methods/nuclear_fleet_status.md)",
                                    report_url=METHOD_URL, document_list="docs/methods/nuclear_fleet_status.md", license="public", tables=[NAME])])
        print(f"{NAME}: {len(t)} rows, {n} reactors, {d0:%Y-%m-%d} to {d1:%Y-%m-%d}")
        rc = 0
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
