#!/usr/bin/env python3
"""Who supplies a grid (session 68): each balancing authority's net imports from each neighbour, by month, and the
three measures of its total net imports side by side.

Energy Research Warehouse (ERW). Writes one derived series table:

    warehouse/output/ba_supply_monthly.csv    per balancing authority, neighbour and month from 2019

A month's days are EIA's Eastern days, the day boundary of both interchange tables. Positive always means the
neighbour supplied the balancing authority (a net import); EIA's own sign is the opposite and is flipped once, here.

Per pair (entity eia930:<BA>-<NEIGHBOUR>, as the balancing authority itself reported it):
    net_import_mwh            the month's held days
    net_import_share_pct      that over the balancing authority's demand on the same days (where demand is held)
    neighbor_report_mwh       the same flow as the neighbour reported it, on the held days the neighbour also reported
    neighbor_report_days      those days (count)
Per balancing authority (entity eia930:<BA>):
    net_import_pairs_mwh                the sum of the pairs, held days (the pair-sum measure)
    net_import_total_interchange_mwh    EIA's own total interchange (eia930_daily_total_interchange), held days that have it
    net_import_balance_mwh              demand less net generation, held days whose 24 hours of both are held
    net_import_<measure>_share_pct      each over demand on the share days (held days whose demand is held), share_days
    total_interchange_all_days_mwh, total_interchange_days   EIA's total interchange over every day it reports
    balance_all_days_mwh, balance_days, demand_all_days_mwh  the balance over every complete day
    demand_mwh                          demand on the held days
    days_held, days_left_out, days_in_month, thin_month (1 when fewer than two thirds of the month's days are held)

Held days (session 62's rules, warehouse/derived/ai_power_regions.py): a day counts for a balancing authority when
every regular neighbour reported it (a regular neighbour reports on at least half of the month's days that have any
report) and none of its pair-days was screened out. A pair-day is screened out when it is further than 10 median
absolute deviations (at least 500 MWh) from the pair's own median over its whole history: EIA's daily interchange holds
days no tie can carry (SWPP-MISO, 2,159,056 MWh on 2026-07-21). Nothing is filled: a day left out is counted, and a
month with no held day has no flow row.

Demand and net generation are held for the seven ISO balancing authorities only (EIA's per-BA workbooks, the emissions
connector's extracts, hourly from 2018-07). For the others the flows are in MWh and no share is written.

    python warehouse/derived/ba_supply.py
    python warehouse/derived/ba_supply.py --out-dir C:/scratch

Method: docs/methods/grid_network.md, "Who supplies a grid".
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_board as pb  # noqa: E402

NAME = "ba_supply_monthly"
SOURCE = "erw:ba_supply"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md"
PAIRS, TOTAL = "eia930_daily_interchange", "eia930_daily_total_interchange"
ISO_BAS = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"]  # demand and net generation are held for these
DAY_TZ = "America/New_York"  # EIA's Eastern day
MADS, FLOOR = 10, 500.0
THIN = 2 / 3
COLS = ip.SERIES_COLS + ["ba", "x_to_ba"]
r4 = pb.r4


def read(name, cols, in_dir=None):
    path = os.path.join(in_dir or ip.OUT_DIR, name + ".csv")
    return pd.read_csv(path, skiprows=ip.header_rows(path), usecols=cols, dtype=str, keep_default_na=False)


def screen(it):
    """True for a pair-day further than MADS median absolute deviations (at least FLOOR MWh) from its pair's median."""
    g = it.groupby("entity")["v"]
    med = g.transform("median")
    mad = (it["v"] - med).abs().groupby(it["entity"]).transform("median")
    return (it["v"] - med).abs() > MADS * np.maximum(mad, FLOOR)


def balance_days(hours):
    """Daily demand and net generation of one balancing authority from its hourly extract, Eastern days whose every hour
    holds both: a frame indexed by day with d and ng (MWh)."""
    t = pd.to_datetime(hours["ts_utc"], utc=True).dt.tz_convert(DAY_TZ)
    x = pd.DataFrame({"day": t.dt.strftime("%Y-%m-%d"), "d": pd.to_numeric(hours["demand_mwh"], errors="coerce"),
                      "ng": pd.to_numeric(hours["net_generation_mwh"], errors="coerce")})
    g = x.groupby("day").agg(n=("d", "size"), nd=("d", "count"), nn=("ng", "count"), d=("d", "sum"), ng=("ng", "sum"))
    want = pd.Series({d: int((pd.Timestamp(d).tz_localize(DAY_TZ) + pd.DateOffset(days=1) - pd.Timestamp(d).tz_localize(DAY_TZ)) / pd.Timedelta(hours=1))
                      for d in g.index})
    return g[(g["n"] == want) & (g["nd"] == g["n"]) & (g["nn"] == g["n"])][["d", "ng"]]


def held_days(g):
    """The held days of one balancing authority's pair-days of one month (columns entity, day, bad)."""
    days = sorted(g["day"].unique())
    n = g.groupby("entity")["day"].nunique()
    regular = set(n[n >= 0.5 * len(days)].index)
    out = []
    for day, gd in g.groupby("day"):
        if not gd["bad"].any() and regular <= set(gd["entity"]):
            out.append(day)
    return out


def build(it, ti, bal, last_day):
    """The table's rows (dicts without the provenance columns). it: pair-days (entity, ba, to, day, v, bad), v positive
    when ba exports; ti: (ba, day, v); bal: {BA: frame by day with d, ng}; last_day: the newest day of the pair table."""
    rows = []
    it = it.assign(month=it["day"].str[:7])
    ti_by = {b: g.set_index("day")["v"] for b, g in ti.groupby("ba")}
    rev = it.set_index(["ba", "to", "day"])["v"]
    groups = {k: g for k, g in it.groupby(["ba", "month"], sort=True)}
    empty = it.iloc[0:0]
    keys = []
    for ba, first in it.groupby("ba")["month"].min().items():
        # every month from the balancing authority's first report to the table's last day, so a month EIA reported
        # nothing for is counted as left out, not skipped
        keys += [(ba, str(m)) for m in pd.period_range(first, last_day[:7], freq="M")]
    for ba, month in keys:
        g = groups.get((ba, month), empty)
        t = f"{month}-01T00:00:00Z"
        m0 = pd.Timestamp(month + "-01")
        m1 = min(m0 + pd.offsets.MonthEnd(0), pd.Timestamp(last_day))
        n_days = int((m1 - m0).days) + 1
        held = held_days(g)
        b = bal.get(ba)
        tb = ti_by.get(ba)

        def add(entity, to, variable, value, unit):
            rows.append(dict(entity=entity, variable=variable, ts_utc=t, value=value, unit=unit, ba=ba.lower(), x_to_ba=to.lower()))
        me = f"eia930:{ba}"
        add(me, "", "days_held", len(held), "count")
        add(me, "", "days_left_out", n_days - len(held), "count")
        add(me, "", "days_in_month", n_days, "count")
        add(me, "", "thin_month", 1 if len(held) < THIN * n_days else 0, "count")
        # the measures over every day each one holds, whatever the pairs did
        mdays = [d.strftime("%Y-%m-%d") for d in pd.date_range(m0, m1)]
        if tb is not None:
            x = tb.reindex(mdays).dropna()
            if len(x):
                add(me, "", "total_interchange_all_days_mwh", r4(-x.sum()), "MWh")
                add(me, "", "total_interchange_days", len(x), "count")
        if b is not None:
            x = b.reindex(mdays).dropna()
            if len(x):
                add(me, "", "balance_all_days_mwh", r4((x["d"] - x["ng"]).sum()), "MWh")
                add(me, "", "demand_all_days_mwh", r4(x["d"].sum()), "MWh")
                add(me, "", "balance_days", len(x), "count")
        if not held:
            continue  # no held day: no flow row, never a zero
        gh = g[g["day"].isin(held)]
        # the share days: held days whose demand is held too; every share is over them, numerator and denominator alike
        share = [d for d in held if b is not None and d in b.index]
        demand = float(b["d"].reindex(share).sum()) if share else None
        if demand:
            add(me, "", "demand_mwh", r4(demand), "MWh")
            add(me, "", "share_days", len(share), "count")
        total = 0.0
        for entity, gp in gh.groupby("entity", sort=True):
            to = gp["to"].iloc[0]
            v = -float(gp["v"].sum())  # EIA: positive when the reporting BA exports; here, positive when the neighbour supplied
            total += v
            add(entity, to, "net_import_mwh", r4(v), "MWh")
            if demand:
                add(entity, to, "net_import_share_pct", r4(-float(gp.loc[gp["day"].isin(share), "v"].sum()) / demand * 100), "pct")
            other = [(to, ba, d) for d in gp["day"]]
            got = rev.reindex(other).dropna()
            if len(got):
                add(entity, to, "neighbor_report_mwh", r4(float(got.sum())), "MWh")  # the neighbour's export to this BA
                add(entity, to, "neighbor_report_days", len(got), "count")
        add(me, "", "net_import_pairs_mwh", r4(total), "MWh")
        if demand:
            add(me, "", "net_import_pairs_share_pct", r4(-float(gh.loc[gh["day"].isin(share), "v"].sum()) / demand * 100), "pct")
        if tb is not None:
            x = tb.reindex(held).dropna()
            if len(x) == len(held):
                add(me, "", "net_import_total_interchange_mwh", r4(-float(x.sum())), "MWh")
                xs = tb.reindex(share)
                if demand and xs.notna().all():
                    add(me, "", "net_import_total_interchange_share_pct", r4(-float(xs.sum()) / demand * 100), "pct")
        if demand:
            x = b.reindex(share)
            add(me, "", "net_import_balance_mwh", r4(float((x["d"] - x["ng"]).sum())), "MWh")
            add(me, "", "net_import_balance_share_pct", r4(float((x["d"] - x["ng"]).sum()) / demand * 100), "pct")
    return rows


def load(in_dir, log):
    it = read(PAIRS, ["entity", "ts_utc", "value", "ba", "x_to_ba"], in_dir)
    it = pd.DataFrame({"entity": it["entity"], "ba": it["ba"].str.upper(), "to": it["x_to_ba"].str.upper(), "day": it["ts_utc"].str[:10],
                       "v": pd.to_numeric(it["value"])})
    it["bad"] = screen(it)
    ti = read(TOTAL, ["ts_utc", "value", "ba"], in_dir)
    ti = pd.DataFrame({"ba": ti["ba"].str.upper(), "day": ti["ts_utc"].str[:10], "v": pd.to_numeric(ti["value"])})
    import eia930_emissions as em
    bal, used = {}, []
    for ba in ISO_BAS:
        ex = em.latest_extract(ba.lower())
        if ex is None:
            log(f"  {ba}: no workbook extract on this machine; its balance and shares are not written")
            continue
        bal[ba] = balance_days(em.read_extract(ex)[["ts_utc", "demand_mwh", "net_generation_mwh"]])
        used.append(f"{ba}: {os.path.relpath(ex, ROOT)} ({len(bal[ba])} complete days)")
    return it, ti, bal, used


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: who supplies a grid (ba_supply_monthly)")
    ap.add_argument("--out-dir", help="write the table, log, registry and status under this directory; the inputs are still read from warehouse/output")
    a = ap.parse_args(argv)
    in_dir = ip.OUT_DIR
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    missing = [t for t in (PAIRS, TOTAL) if not os.path.exists(os.path.join(in_dir, t + ".csv"))]
    if missing:
        print(f"ba_supply SKIPPED: input tables not on this machine: {', '.join(missing)}")
        ip.write_status("ba_supply", run_id, [dict(table=NAME, market="derived", status="skipped", detail="inputs missing: " + ", ".join(missing))])
        return 0
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ba_supply_{run_id}.log"))
    status = []
    try:
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        it, ti, bal, used = load(in_dir, log)
        last_day = it["day"].max()
        rows = build(it, ti, bal, last_day)
        out = pd.DataFrame(rows).assign(freq="P1M", geo="", market="", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")[COLS]
        if out.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("two rows share an (entity, variable, ts_utc) key")
        out = out.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        held = out[out["variable"] == "days_held"]["value"].sum()
        left = out[out["variable"] == "days_left_out"]["value"].sum()
        header = [
            "Energy Research Warehouse (ERW): who supplies a grid: each balancing authority's net imports from each neighbour by month, "
            "from 2019, and three measures of its total net imports (derived, session 68)",
            "Shape: series (docs/datastandard.md v0), partition column ba; freq P1M, ts_utc the first day of the month at 00:00:00Z; a "
            "month's days are EIA's Eastern days. Positive means the neighbour supplied the balancing authority (a net import). Pair "
            "rows (entity eia930:<BA>-<NEIGHBOUR>, x_to_ba the neighbour): net_import_mwh, net_import_share_pct, neighbor_report_mwh, "
            "neighbor_report_days. Balancing authority rows (entity eia930:<BA>): net_import_pairs_mwh, "
            "net_import_total_interchange_mwh, net_import_balance_mwh (the balance on the share days) and each one's _share_pct of demand "
            "over the share days (held days whose demand is held; share_days); "
            "total_interchange_all_days_mwh, total_interchange_days, balance_all_days_mwh, demand_all_days_mwh, balance_days; "
            "demand_mwh; days_held, days_left_out, days_in_month, thin_month.",
            f"Held days: every regular neighbour reported (present on at least half of the month's reported days) and no pair-day "
            f"screened out; screened: further than {MADS} median absolute deviations (at least {FLOOR:g} MWh) from the pair's median "
            f"over its history ({int(it['bad'].sum()):,} of {len(it):,} pair-days). Balancing-authority days held {int(held):,}, left "
            f"out {int(left):,}. thin_month is 1 when fewer than two thirds of the month's days are held. Nothing filled.",
            "Demand and net generation (the balance, and every share) are held for the seven ISO balancing authorities only: "
            + "; ".join(used) + ". Elsewhere flows are in MWh and no share is written.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/ba_supply.py",
            f"Run log: warehouse/output/logs/ba_supply_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, who supplies a grid (docs/methods/grid_network.md), {METHOD_URL}",
            f"Derived from: {PAIRS}; {TOTAL}",
            "Also read: EIA's hourly demand and net generation from the per-BA workbooks (source eia:gridmonitor/knownissues/xls), the "
            "emissions connector's extracts (raw files, not in git).",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23); every input is public "
            "domain (EIA).",
            f"File holds {len(out)} rows, {out['ts_utc'].min()} to {out['ts_utc'].max()}, rewritten by this run.",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        ip._require_lock(path, f"writing {NAME}")
        with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
            for h in header:
                f.write("# " + h + "\n")
            out.to_csv(f, index=False, lineterminator="\n")
        os.replace(path + ".tmp", path)
        ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Who supplies a grid: net imports by neighbour and month (docs/methods/grid_network.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": [NAME]}])
        log(f"{NAME}: {len(out)} rows")
        print(f"{NAME}.csv: rows={len(out)}")
        status.append(dict(table=NAME, market="derived", status="ok", detail=f"{len(out)} rows"))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"ba_supply {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status = [dict(table=NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300])]
    ip.write_status("ba_supply", run_id, status)
    log.close()
    return 0 if all(s["status"] == "ok" for s in status) else 1


if __name__ == "__main__":
    sys.exit(main())
