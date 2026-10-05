#!/usr/bin/env python3
"""What Texas's storage resources were awarded day-ahead, by month (session 115).

Energy Research Warehouse (ERW). Method: docs/methods/ercot_storage_dam_awards.md. No request is made.

Table: ercot_storage_dam_awards_monthly, derived from ercot_dam_esr_awards (ERCOT's 60-Day DAM Disclosure, the Energy
Storage Resource file, one row per resource and hour). One entity, ercot:esr_fleet, and for each local (Central) month:

  resources, resources_with_award     resources with a row in the month; those with any award in it (count)
  mw                                  the sum of each resource's highest HSL in the month (MW). A resource with no
                                      award is in it: it was there to be awarded
  resource_hours, resource_hours_energy_award   rows of the month; those with a day-ahead energy award (count)
  energy_sold_mwh, energy_bought_mwh  positive and negative Awarded Quantity (MWh; an award of 1 MW for the hour)
  energy_sold_usd, energy_bought_usd  each at the resource's own Energy Settlement Point Price, that hour (USD)
  revenue_energy_usd                  sold less bought: energy net of charging (USD)
  revenue_<service>_usd               the service's award times its clearing price (MCPC), each hour: regup, regdn,
                                      rrs (its three kinds of award at the one RRS price), ecrs, nspin (USD)
  revenue_ancillary_usd, revenue_total_usd      the five services; energy and the five (USD)
  <each revenue>_per_mw               over the month's mw (USD/MW; a page's per kW is this over 1,000)
  days_held, days_missing, days_in_month        operating days with rows; days with none between the table's first and
                                      last operating day; the calendar's days (count)

What it is not: day-ahead awards only. No real-time settlement, no deployment energy, no contracts. A floor on market
revenue, not what any battery earned.

Nothing is filled. A day with no rows adds nothing to any sum and is counted in days_missing (or, before the first
day ERCOT published the file and after the last day held, only in the difference between days_in_month and
days_held). An award without its price stops the build: it is never valued at another price.

No duration class is written: ERCOT's file states each resource's power (HSL) and never its energy, and the warehouse
holds no match of ERCOT's resource names to the EIA-860M plants, where energy is stated (the method says what it
would take).

    python warehouse/derived/ercot_storage_dam_awards.py
    python warehouse/derived/ercot_storage_dam_awards.py --out-dir <dir> [--input <csv>]   # a trial: records nothing
"""

import argparse
import calendar
import datetime as dt
import math
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "ercot_storage_dam_awards_monthly"
INPUT = "ercot_dam_esr_awards"
SOURCE = "erw:ercot_storage_dam_awards"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_dam_awards.md"
TZ = "America/Chicago"
ENTITY = "ercot:esr_fleet"
COLS = ip.SERIES_COLS
KEY = ["entity", "variable", "ts_utc"]
# the service's name in the table -> (its award columns in the input, its price column)
SERVICES = {"regup": (["x_regup_award_mw"], "x_regup_mcpc"), "regdn": (["x_regdn_award_mw"], "x_regdn_mcpc"),
            "rrs": (["x_rrspfr_award_mw", "x_rrsffr_award_mw", "x_rrsufr_award_mw"], "x_rrs_mcpc"),
            "ecrs": (["x_ecrs_award_mw"], "x_ecrs_mcpc"), "nspin": (["x_nonspin_award_mw"], "x_nonspin_mcpc")}
REVENUES = ["energy"] + list(SERVICES) + ["ancillary", "total"]
SUMS = ["energy_sold_mwh", "energy_bought_mwh", "energy_sold_usd", "energy_bought_usd"] + [f"revenue_{s}_usd" for s in SERVICES]
CHUNK = 200_000


def _num(s):
    """A column of the input as numbers; a blank is no number (NaN), never a zero."""
    return pd.to_numeric(s.where(s != ""), errors="raise")


def by_resource(df):
    """A slice of the input, as one row per (local month, resource, local day): the highest HSL, the rows, the sums.

    Raises ValueError for an award that has no price beside it: nothing is valued at a price ERCOT did not print."""
    local = pd.to_datetime(df["ts_utc"], utc=True).dt.tz_convert(TZ)
    out = pd.DataFrame({"month": local.dt.strftime("%Y-%m"), "day": local.dt.strftime("%Y-%m-%d"), "entity": df["entity"].values})
    out["hsl"] = _num(df["value"]).values
    q, p = _num(df["x_energy_award_mw"]), _num(df["x_energy_price_usd_per_mwh"])
    has = q.notna() & (q != 0)
    if (has & p.isna()).any():
        raise ValueError(f"{int((has & p.isna()).sum())} energy awards have no settlement point price")
    out["rows"] = 1
    out["energy_rows"] = has.astype(int).values
    out["energy_sold_mwh"] = q.where(q > 0, 0.0).fillna(0.0).values
    out["energy_bought_mwh"] = (-q.where(q < 0, 0.0)).fillna(0.0).values
    out["energy_sold_usd"] = (q.where(q > 0, 0.0) * p).where(has, 0.0).fillna(0.0).values
    out["energy_bought_usd"] = (-(q.where(q < 0, 0.0)) * p).where(has, 0.0).fillna(0.0).values
    any_award = has.copy()
    for name, (awards, price) in SERVICES.items():
        a = sum(_num(df[c]).fillna(0.0) for c in awards)
        m = _num(df[price])
        got = a != 0
        if (got & m.isna()).any():
            raise ValueError(f"{int((got & m.isna()).sum())} {name} awards have no clearing price")
        out[f"revenue_{name}_usd"] = (a * m).where(got, 0.0).values
        any_award |= got
    out["award_rows"] = any_award.astype(int).values
    agg = {"hsl": "max", "rows": "sum", "energy_rows": "sum", "award_rows": "sum"}
    agg.update({c: "sum" for c in SUMS})
    return out.groupby(["month", "entity", "day"], as_index=False).agg(agg)


def combine(parts):
    """The slices together, one row per (local month, resource): the highest HSL of the month, the sums, the days."""
    d = pd.concat(parts, ignore_index=True)
    agg = {"hsl": "max", "rows": "sum", "energy_rows": "sum", "award_rows": "sum"}
    agg.update({c: "sum" for c in SUMS})
    res = d.groupby(["month", "entity"], as_index=False).agg(agg)
    days = d.groupby("month")["day"].agg(lambda s: sorted(set(s)))
    return res, days


def monthly(res, days):
    """The fleet's months: {month: {variable: value}} from the per-resource rows and each month's days held."""
    all_days = sorted(d for m in days.index for d in days[m])
    first, last = dt.date.fromisoformat(all_days[0]), dt.date.fromisoformat(all_days[-1])
    out = {}
    for month, g in res.groupby("month"):
        y, m = int(month[:4]), int(month[5:])
        n = calendar.monthrange(y, m)[1]
        held = set(days[month])
        span = [dt.date(y, m, i) for i in range(1, n + 1) if first <= dt.date(y, m, i) <= last]
        mw = math.fsum(g["hsl"])  # fsum: the same sum whatever the order of the resources
        v = {"resources": int(len(g)), "resources_with_award": int((g["award_rows"] > 0).sum()), "mw": round(mw, 4),
             "resource_hours": int(g["rows"].sum()), "resource_hours_energy_award": int(g["energy_rows"].sum())}
        for c in SUMS:
            v[c] = round(math.fsum(g[c]), 2)
        v["revenue_energy_usd"] = round(v["energy_sold_usd"] - v["energy_bought_usd"], 2)
        v["revenue_ancillary_usd"] = round(sum(v[f"revenue_{s}_usd"] for s in SERVICES), 2)
        v["revenue_total_usd"] = round(v["revenue_energy_usd"] + v["revenue_ancillary_usd"], 2)
        if mw > 0:
            for r in REVENUES:
                v[f"revenue_{r}_usd_per_mw"] = round(v[f"revenue_{r}_usd"] / mw, 4)
        v["days_held"] = len(held)
        v["days_missing"] = sum(1 for d in span if d.isoformat() not in held)
        v["days_in_month"] = n
        out[month] = v
    return out


def unit_of(variable):
    if variable == "mw":
        return "MW"
    if variable.endswith("_mwh"):
        return "MWh"
    if variable.endswith("_usd_per_mw"):
        return "USD/MW"
    if variable.endswith("_usd"):
        return "USD"
    return "count"


def rows_of(months, retrieved):
    recs = []
    for month, v in sorted(months.items()):
        for variable, value in v.items():
            recs.append({"entity": ENTITY, "variable": variable, "ts_utc": f"{month}-01T00:00:00Z", "value": repr(float(value)) if not isinstance(value, int) else str(value),
                         "unit": unit_of(variable), "freq": "P1M", "geo": "US-TX", "market": "ercot_dam", "node": "", "source": SOURCE, "source_url": METHOD_URL,
                         "retrieved_at": retrieved, "vintage": ""})
    return pd.DataFrame(recs, columns=COLS)


def read_input(path, log):
    """The input, a slice at a time (it is about two million rows): the per-resource rows and the days of each month."""
    n = ip.header_rows(path)
    parts, total = [], 0
    for chunk in pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[], chunksize=CHUNK):
        total += len(chunk)
        parts.append(by_resource(chunk))
    log(f"{os.path.basename(path)}: {total:,} rows read")
    res, days = combine(parts)
    return res, days, total


def build(out_dir, input_path, log, run_id, retrieved):
    if not os.path.exists(input_path):
        raise RuntimeError(f"{INPUT} is not on this machine: nothing is written")
    res, days, total = read_input(input_path, log)
    months = monthly(res, days)
    new = rows_of(months, retrieved)
    path = os.path.join(out_dir, NAME + ".csv")
    if os.path.exists(path):  # an unchanged row keeps its retrieved_at, so the loader rewrites only what changed
        old = ip.read_series(path, COLS)
        j = new.merge(old[KEY + ["value", "retrieved_at"]], on=KEY, how="left", suffixes=("", "_old"))
        same = (pd.to_numeric(j["value"]) == pd.to_numeric(j["value_old"])).values
        new["retrieved_at"] = j["retrieved_at_old"].where(same, j["retrieved_at"]).values
        gone = old[~pd.MultiIndex.from_frame(old[KEY]).isin(pd.MultiIndex.from_frame(new[KEY]))]
        if len(gone):
            raise RuntimeError(f"{len(gone)} rows of the last run's table have no row now (the input lost a month?): nothing is written")
    out = new.sort_values(KEY).reset_index(drop=True)
    if out.duplicated(KEY).any():
        raise RuntimeError(f"{NAME}: duplicate (entity, variable, ts_utc) keys")
    all_days = sorted(d for m in days.index for d in days[m])
    missing = sum(v["days_missing"] for v in months.values())
    head = [
        "Energy Research Warehouse (ERW): what ERCOT's Energy Storage Resources were awarded day-ahead, the fleet by local month (derived, session 115)",
        "Shape: series (docs/datastandard.md v0, Decision 40); freq P1M, ts_utc the first day of the local (Central) month at 00:00:00Z; one entity, ercot:esr_fleet. "
        "Variables: resources, resources_with_award, resource_hours, resource_hours_energy_award (count); mw (MW: the sum of each resource's highest HSL in the month; a "
        "resource with no award is in it); energy_sold_mwh, energy_bought_mwh (MWh); energy_sold_usd, energy_bought_usd, revenue_energy_usd (sold less bought: net of "
        "charging, each award at the resource's own settlement point price); revenue_regup_usd, revenue_regdn_usd, revenue_rrs_usd, revenue_ecrs_usd, revenue_nspin_usd "
        "(each award times its clearing price, MCPC), revenue_ancillary_usd, revenue_total_usd (USD); each revenue also _per_mw, over the month's mw (USD/MW; per kW is "
        "this over 1,000); days_held, days_missing, days_in_month (count).",
        "WHAT IT IS NOT: day-ahead awards only. No real-time settlement, no deployment energy, no contracts. It is a floor on market revenue and not what any battery "
        "earned. \"revenue\" in a variable's name is an award valued at its day-ahead price, nothing more.",
        f"Operating days held: {len(all_days)}, {all_days[0]} to {all_days[-1]} (local, Central); {missing} missing between them. Nothing is filled for a missing day: it "
        "adds nothing to a sum and is counted in days_missing. A month's first or last days outside that span are only the difference of days_in_month and days_held.",
        "No duration class: ERCOT's file states a resource's power and never its energy, and the warehouse holds no match of ERCOT's resource names to EIA-860M's plants "
        "(docs/methods/ercot_storage_dam_awards.md).",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_storage_dam_awards.py, from {total:,} rows of {INPUT}",
        f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        f"Source: {SOURCE} ERW derived table, ERCOT storage resources' day-ahead awards by month (docs/methods/ercot_storage_dam_awards.md), {METHOD_URL}",
        f"Derived from: {INPUT}",
        "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23); its one input is public (ERCOT's terms allow raw data to be "
        "\"used, reproduced, and redistributed in compilations, charts, and analyses\", https://www.ercot.com/help/terms).",
        f"File holds {len(out)} rows, rewritten whole by this run.",
    ]
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in head:
            f.write("# " + line + "\n")
        out.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    for month, v in sorted(months.items()):
        log(f"  {month}: {v['days_held']} of {v['days_in_month']} days ({v['days_missing']} missing), {v['resources']} resources, {v['mw']:.1f} MW, "
            f"energy {v['revenue_energy_usd']:,.2f}, ancillary {v['revenue_ancillary_usd']:,.2f}, total {v['revenue_total_usd']:,.2f} USD, "
            f"{v.get('revenue_total_usd_per_mw', float('nan')):.2f} USD/MW")
    print(f"{NAME}.csv: rows={len(out)} months={len(months)} days={len(all_days)}")
    return out, months


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT storage resources' day-ahead awards by month (derived)")
    ap.add_argument("--out-dir", help="a trial: write the table here and record nothing")
    ap.add_argument("--input", help="the input table's file (default: warehouse/output/ercot_dam_esr_awards.csv)")
    a = ap.parse_args(argv)
    trial = bool(a.out_dir)
    out_dir = a.out_dir or ip.OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log = ip.Log(os.path.join(out_dir if trial else ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        if not trial:
            ip._require_lock(os.path.join(out_dir, NAME + ".csv"), f"writing {NAME}")
        out, months = build(out_dir, a.input or os.path.join(ip.OUT_DIR, INPUT + ".csv"), log, run_id, retrieved)
        results.append(dict(table=NAME, market="derived", status="ok", detail=f"{len(out)} rows; {len(months)} months"))
        if not trial:
            ip.update_sources([{"source": SOURCE, "publisher": "Energy Research Warehouse (ERW), derived",
                                "report": "ERCOT storage resources' day-ahead awards by month (docs/methods/ercot_storage_dam_awards.md)",
                                "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": [NAME]}])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not trial:
        ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
