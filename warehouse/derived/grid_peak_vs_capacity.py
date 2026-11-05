#!/usr/bin/env python3
"""Each grid's peak demand against its installed capacity (session 672, chain 043): the All grids tab's headroom column.

Energy Research Warehouse (ERW). One derived table, grid_peak_vs_capacity, from two tables the warehouse holds (no request
is made). Method: docs/methods/grid_peak_vs_capacity.md.

    python warehouse/derived/grid_peak_vs_capacity.py                 # the table, under the data lock
    python warehouse/derived/grid_peak_vs_capacity.py --out-dir DIR   # a trial: the table under DIR

Peak: eia930_demand_growth's peak_demand_mw of the grid's balancing authority for the last whole year it holds (the
highest hour EIA-930 reports that passes that table's test for faulty hours; x_at the hour). Capacity:
eia860m_operating_generators, the net summer capacity (MW) of every operating generator whose balancing authority is the
grid's, summed. EIA-860M names each generator's balancing authority, so no state is mapped to a grid; the states the grid's
generators stand in are listed, and a state with more than 1 percent of its capacity in another balancing authority is
named as split.

Entity grid_peak_vs_capacity:<grid> (caiso, ercot, isone, miso, nyiso, pjm, spp); ts_utc 1 January of the peak's year;
freq P1Y. Variables:
    peak_demand_mw                 MW     the year's peak hour (x_at its start, UTC)
    capacity_mw                    MW     net summer capacity of the generators in the EIA-860M list that began operating by
                                          the end of the peak's year (a generator retired since is not in the list: the
                                          figure is the list's, read back, not that year's own)
    capacity_mw_listed             MW     every operating generator in the list (its vintage in x_vintage)
    capacity_solar_mw, capacity_wind_mw, capacity_storage_mw   MW   parts of capacity_mw (energy source SUN, WND, MWH)
    peak_to_capacity               ratio  peak_demand_mw / capacity_mw
    capacity_over_peak_pct         pct    (capacity_mw - peak_demand_mw) / peak_demand_mw * 100
Net summer capacity counts solar, wind and storage at their summer ratings, not at what they give in the peak hour: the
ratio is not a reserve margin as a planner computes one (NERC's anticipated reserve margin discounts them).
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "grid_peak_vs_capacity"
SOURCE = "erw:grid_peak_vs_capacity"
PEAKS, GENERATORS = "eia930_demand_growth", "eia860m_operating_generators"
GRIDS = {"caiso": "CISO", "ercot": "ERCO", "isone": "ISNE", "miso": "MISO", "nyiso": "NYIS", "pjm": "PJM", "spp": "SWPP"}
SPLIT_SHARE = 0.01
COLS = ip.SERIES_COLS + ["x_at", "x_vintage", "x_states", "x_split_states"]


def read_table(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


def build(peaks, gens, method_url):
    p = peaks[peaks["variable"] == "peak_demand_mw"].copy()
    g = gens.assign(mw=pd.to_numeric(gens["net_summer_mw"], errors="coerce"),
                    year=pd.to_numeric(gens["operating_year"], errors="coerce"))
    by_state = g.groupby(["state", "balancing_authority"])["mw"].sum()
    state_total = g.groupby("state")["mw"].sum()
    vintage = sorted(gens["vintage"].unique())[-1]
    rows = []
    for grid, ba in GRIDS.items():
        pk = p[p["entity"] == f"eia930:{ba}"].sort_values("ts_utc")
        if pk.empty:
            raise RuntimeError(f"{PEAKS} holds no peak for eia930:{ba}")
        last = pk.iloc[-1]
        year = int(last["ts_utc"][:4])
        peak = float(last["value"])
        mine = g[g["balancing_authority"] == ba]
        cap = mine[mine["year"] <= year]
        capacity = float(cap["mw"].sum())
        if capacity <= 0:
            raise RuntimeError(f"{GENERATORS} lists no capacity for {ba} by {year}")
        states = sorted(s for s in mine["state"].unique() if s)
        split = [s for s in states if (state_total[s] - by_state.get((s, ba), 0.0)) > SPLIT_SHARE * state_total[s]]
        base = dict(entity=f"{NAME}:{grid}", ts_utc=last["ts_utc"], freq="P1Y", geo="US", market="", node=grid.upper(),
                    source=SOURCE, source_url=method_url, retrieved_at=last["retrieved_at"], vintage="", x_at="",
                    x_vintage=vintage, x_states=";".join(states), x_split_states=";".join(split))
        vals = [("peak_demand_mw", peak, "MW"), ("capacity_mw", capacity, "MW"),
                ("capacity_mw_listed", float(mine["mw"].sum()), "MW"),
                ("capacity_solar_mw", float(cap.loc[cap["energy_source"] == "SUN", "mw"].sum()), "MW"),
                ("capacity_wind_mw", float(cap.loc[cap["energy_source"] == "WND", "mw"].sum()), "MW"),
                ("capacity_storage_mw", float(cap.loc[cap["energy_source"] == "MWH", "mw"].sum()), "MW"),
                ("peak_to_capacity", round(peak / capacity, 4), "ratio"),
                ("capacity_over_peak_pct", round((capacity - peak) / peak * 100, 2), "pct")]
        for var, v, unit in vals:
            rows.append(dict(base, variable=var, value=round(v, 4) if unit == "ratio" else round(v, 2), unit=unit,
                             x_at=last["x_at"] if var == "peak_demand_mw" else ""))
    return pd.DataFrame(rows, columns=COLS).sort_values(["entity", "variable"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Each grid's peak demand against its installed capacity")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    peaks_path, gens_path = (os.path.join(ip.OUT_DIR, t + ".csv") for t in (PEAKS, GENERATORS))
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"grid_peak_vs_capacity_{run_id}.log"))
    try:
        url = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_peak_vs_capacity.md"
        gens = read_table(gens_path)
        t = build(read_table(peaks_path), gens, url)
        year = t["ts_utc"].iloc[0][:4]
        header = [
            f"Energy Research Warehouse (ERW): each grid's peak demand in {year} against the net summer capacity of its balancing authority's generators (session 672)",
            "Shape: series (docs/datastandard.md v0). entity grid_peak_vs_capacity:<grid>; variables peak_demand_mw (x_at the hour), capacity_mw (online by the end of the year), capacity_mw_listed, capacity_solar_mw, capacity_wind_mw, capacity_storage_mw (MW), peak_to_capacity (ratio), capacity_over_peak_pct (pct); x_states the states of the grid's generators, x_split_states those with more than 1% of their capacity in another balancing authority.",
            "Net summer capacity counts solar, wind and storage at their summer ratings: the ratio is not a planner's reserve margin.",
            f"Derived from: {PEAKS}; {GENERATORS}",
            f"Built by warehouse/derived/grid_peak_vs_capacity.py from EIA-930 peaks (the ERW's peak test) and EIA-860M (vintage {gens['vintage'].max()}); method docs/methods/grid_peak_vs_capacity.md",
            f"Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/grid_peak_vs_capacity_{run_id}.log",
            "Source: eia:930 and eia:860m U.S. Energy Information Administration, Form EIA-930 Hourly Electric Grid Monitor and Form EIA-860M Monthly Update to the Annual Electric Generator Report",
            'License: public (works of the U.S. government; cite "U.S. Energy Information Administration, Forms EIA-930 and EIA-860M").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="Each grid's peak demand against its balancing authority's generators' net summer capacity (docs/methods/grid_peak_vs_capacity.md)",
                                    report_url=url, document_list="docs/methods/grid_peak_vs_capacity.md", license="public", tables=[NAME])])
        piv = t.pivot(index="node", columns="variable", values="value")
        print(f"{NAME}: {len(t)} rows; " + "; ".join(f"{g} {r['peak_to_capacity']:.2f}" for g, r in piv.iterrows()))
        rc = 0
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"grid_peak_vs_capacity FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        rc = 1
    log.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
