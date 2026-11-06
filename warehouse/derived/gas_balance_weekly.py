#!/usr/bin/env python3
"""The gas balance: each week's working gas in storage by region, its change and its place in the five years before;
and each month's U.S. balance of supply and demand with LNG's share (session 2956, chain 157).

Energy Research Warehouse (ERW). One derived table, gas_balance_weekly, from EIA's tables the warehouse holds:
eia_gas_storage_weekly (working gas by region, weekly), and, monthly, eia_gas_production_state_monthly (U.S. dry
production), eia_gas_consumption_state_monthly (U.S. consumption, total and electric power) and eia_gas_trade_monthly
(pipeline and LNG imports and exports). Method: docs/methods/gas_balance_weekly.md. No request.

    python warehouse/derived/gas_balance_weekly.py               # the table (data lock)
    python warehouse/derived/gas_balance_weekly.py --out-dir DIR # a trial

    weekly    entity gas_storage:<region> (EIA's region: east, midwest, mountain, pacific, south_central, salt, nonsalt,
              lower48), ts_utc the report's week, freq P1W: working_gas_bcf; net_change_bcf (against the week before,
              7 days earlier only); five_year_min_bcf, five_year_max_bcf, five_year_avg_bcf (the same ISO week of the five
              years before, all five held); vs_five_year_avg_bcf; five_year_position_pct (0 at the five-year low, 100 at
              the high)
    monthly   entity gas_balance:US, ts_utc the month, freq P1M (MMcf): dry_production, imports, consumption,
              power_burn (electric power consumption), exports, lng_exports, implied_balance (dry production plus
              imports less consumption less exports: what went to storage, the losses and EIA's balancing item);
              lng_share_pct (LNG exports over dry production), power_share_pct (power burn over consumption)
Weekly production, demand and LNG feedgas are not held, so the week has no implied balance of its own. Nothing is filled.
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

NAME = "gas_balance_weekly"
SOURCE = "erw:gas_balance_weekly"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/gas_balance_weekly.md"
STORAGE, PROD, CONS, TRADE = "eia_gas_storage_weekly", "eia_gas_production_state_monthly", "eia_gas_consumption_state_monthly", "eia_gas_trade_monthly"
REGIONS = {"NW2_EPG0_SWO_R31_BCF": "east", "NW2_EPG0_SWO_R32_BCF": "midwest", "NW2_EPG0_SWO_R33_BCF": "south_central",
           "NW2_EPG0_SWO_R34_BCF": "mountain", "NW2_EPG0_SWO_R35_BCF": "pacific", "NW2_EPG0_SWO_R48_BCF": "lower48",
           "NW2_EPG0_SSO_R33_BCF": "salt", "NW2_EPG0_SNO_R33_BCF": "nonsalt"}
MONTHLY = {"dry_production": (PROD, "eia_gas_production:NUS:N9070US"), "consumption": (CONS, "eia_gas_consumption:VC0:NUS"),
           "power_burn": (CONS, "eia_gas_consumption:VEU:NUS")}
IMPORTS = ("eia:N9102CN2", "eia:N9102MX2", "eia:N9103US2")
EXPORTS = ("eia:N9132CN2", "eia:N9132MX2", "eia:N9133US2")
LNG_EXPORTS = "eia:N9133US2"
COLS = ip.SERIES_COLS + ["x_region"]


def read(folder, table, entities=None):
    p = os.path.join(folder, f"{table}.csv")
    d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, usecols=["entity", "variable", "ts_utc", "value"])
    if entities is not None:
        d = d[d["entity"].isin(entities)]
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    d["t"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def row(ent, var, t, val, unit, freq, region):
    return {"entity": ent, "variable": var, "ts_utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": round(float(val), 4), "unit": unit, "freq": freq,
            "geo": "US", "market": "", "node": "", "source": SOURCE, "source_url": METHOD_URL, "vintage": "", "x_region": region}


def weekly(d):
    rows = []
    for code, region in REGIONS.items():
        s = d[d["entity"] == f"eia:{code}"].dropna(subset=["v"]).set_index("t")["v"].sort_index()
        s = s[~s.index.duplicated(keep="last")]
        iso = s.index.isocalendar()
        by = {(int(y), int(w)): v for (y, w), v in zip(zip(iso["year"], iso["week"]), s.values)}
        ent = f"gas_storage:{region}"
        prev_t, prev_v = None, None
        for t, v in s.items():
            rows.append(row(ent, "working_gas_bcf", t, v, "bcf", "P1W", region))
            if prev_t is not None and (t - prev_t).days == 7:
                rows.append(row(ent, "net_change_bcf", t, v - prev_v, "bcf", "P1W", region))
            prev_t, prev_v = t, v
            y, w = int(t.isocalendar()[0]), int(t.isocalendar()[1])
            past = [by.get((y - k, w)) for k in range(1, 6)]
            if all(x is not None for x in past):
                lo, hi, avg = min(past), max(past), sum(past) / 5
                rows += [row(ent, "five_year_min_bcf", t, lo, "bcf", "P1W", region), row(ent, "five_year_max_bcf", t, hi, "bcf", "P1W", region),
                         row(ent, "five_year_avg_bcf", t, avg, "bcf", "P1W", region), row(ent, "vs_five_year_avg_bcf", t, v - avg, "bcf", "P1W", region)]
                if hi > lo:
                    rows.append(row(ent, "five_year_position_pct", t, 100.0 * (v - lo) / (hi - lo), "pct", "P1W", region))
    return rows


def monthly(folder):
    parts = {}
    for var, (table, ent) in MONTHLY.items():
        x = read(folder, table, [ent]).dropna(subset=["v"])
        parts[var] = x.groupby("t")["v"].sum()
    tr = read(folder, TRADE, list(IMPORTS + EXPORTS)).dropna(subset=["v"])
    full = lambda ents: tr[tr["entity"].isin(ents)].groupby("t").filter(lambda g: g["entity"].nunique() == len(ents)).groupby("t")["v"].sum()
    parts["imports"], parts["exports"] = full(IMPORTS), full(EXPORTS)
    parts["lng_exports"] = tr[tr["entity"] == LNG_EXPORTS].groupby("t")["v"].sum()
    m = pd.DataFrame(parts)
    rows = []
    for t, r in m.iterrows():
        for var in m.columns:
            if pd.notna(r[var]):
                rows.append(row("gas_balance:US", var, t, r[var], "MMcf", "P1M", "US"))
        need = ["dry_production", "imports", "consumption", "exports"]
        if all(pd.notna(r[k]) for k in need):
            rows.append(row("gas_balance:US", "implied_balance", t, r["dry_production"] + r["imports"] - r["consumption"] - r["exports"], "MMcf", "P1M", "US"))
        if pd.notna(r["lng_exports"]) and pd.notna(r["dry_production"]) and r["dry_production"] > 0:
            rows.append(row("gas_balance:US", "lng_share_pct", t, 100.0 * r["lng_exports"] / r["dry_production"], "pct", "P1M", "US"))
        if pd.notna(r["power_burn"]) and pd.notna(r["consumption"]) and r["consumption"] > 0:
            rows.append(row("gas_balance:US", "power_share_pct", t, 100.0 * r["power_burn"] / r["consumption"], "pct", "P1M", "US"))
    return rows


def build(folder=None):
    folder = folder or ip.OUT_DIR
    rows = weekly(read(folder, STORAGE)) + monthly(folder)
    t = pd.DataFrame(rows, columns=COLS)
    return t.sort_values(["entity", "ts_utc", "variable"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the weekly gas storage balance and the monthly U.S. gas balance (session 2956)")
    ap.add_argument("--out-dir", help="a trial: the table under this folder")
    a = ap.parse_args(argv)
    folder = ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        t = build(folder)
        t["retrieved_at"] = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
        w, mo = t[t["freq"] == "P1W"], t[t["freq"] == "P1M"]
        header = [
            "Energy Research Warehouse (ERW): working gas in storage by region each week, its change and its place in the five years before; and the monthly U.S. gas balance with LNG's and power's shares (derived, session 2956)",
            "Shape: series (docs/datastandard.md v0). entity gas_storage:<region> (freq P1W) and gas_balance:US (freq P1M); variables working_gas_bcf, net_change_bcf, five_year_min_bcf, "
            "five_year_max_bcf, five_year_avg_bcf, vs_five_year_avg_bcf, five_year_position_pct (weekly); dry_production, imports, consumption, power_burn, exports, lng_exports, implied_balance (MMcf), "
            "lng_share_pct, power_share_pct (monthly).",
            f"Weeks {w['ts_utc'].min()[:10]} to {w['ts_utc'].max()[:10]}; months {mo['ts_utc'].min()[:7]} to {mo['ts_utc'].max()[:7]}. The five-year figures need the same ISO week in all five years before; "
            "a week's change needs the week exactly 7 days before. Weekly production, demand and LNG feedgas are not held, so a week has no implied balance of its own.",
            f"Derived from: {STORAGE}; {PROD}; {CONS}; {TRADE}",
            "Built by warehouse/derived/gas_balance_weekly.py; method docs/methods/gas_balance_weekly.md",
            f"Retrieved: {run_id} (UTC), computed from the tables held; no request was made.",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Source: eia:natural-gas U.S. Energy Information Administration, Weekly Natural Gas Storage Report and Natural Gas Monthly",
            'License: public (works of the U.S. government; cite "U.S. Energy Information Administration").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=COLS)
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="The weekly gas storage balance and the monthly U.S. gas balance (docs/methods/gas_balance_weekly.md)",
                                    report_url=METHOD_URL, document_list="docs/methods/gas_balance_weekly.md", license="public", tables=[NAME])])
        print(f"{NAME}: {len(t)} rows ({len(w)} weekly, {len(mo)} monthly)")
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
