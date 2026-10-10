#!/usr/bin/env python3
"""The battery model's day-ahead ancillary revenue beside ERCOT's real storage awards (session 178).

Energy Research Warehouse (ERW). Two tables already held are set side by side, over the same local months, in the same
unit (USD per kW of power and month):

    battery_stack_monthly              the model: ercot:HB_HUBAVG, <strategy>_<N>h_revenue_ancillary_usd_per_mw (the
                                       awards the model takes at ERCOT's day-ahead clearing prices, per MW of the battery)
    ercot_storage_dam_awards_monthly   the fleet: ercot:esr_fleet, revenue_ancillary_usd_per_mw (every Energy Storage
                                       Resource's day-ahead ancillary award times its clearing price, over the month's
                                       mw: the sum of each resource's highest HSL in the month, a resource with no award
                                       in it)

A month is in the comparison only when both tables hold every day of it (days_held = days_in_month in each): a partial
month is never scaled. The ratio is the model's sum over those months divided by the fleet's. This is the arithmetic of
the one line on /cost-of-power/battery (site/lib/batterystack.ts, awardsBeside), written again in Python; the test
tests/test_session178.py holds the two to each other.

With --quantities the raw awards (ercot_dam_esr_awards, about 540 MB) are read as well, for what the monthly table does
not carry: the megawatts awarded in each product in the average hour, as a share of the fleet's mw.

    python warehouse/derived/battery_awards_compare.py --in-dir C:/.../warehouse/output --out-dir C:/.../runs/session178
    python warehouse/derived/battery_awards_compare.py --in-dir DIR --out-dir DIR2 --quantities

With --snapshot the page's file is written too: site/data/battery_awards_beside.json, the comparison for each strategy
and duration, which /cost-of-power/battery imports for its one line (as the grids in review are read from
site/data/battery_stack_review.json). The page makes no new read of the live set for it.

    python warehouse/derived/battery_awards_compare.py --in-dir DIR --out-dir DIR2 --snapshot

It writes no table of the warehouse and needs no data lock: a small CSV under --out-dir, and with --snapshot a site
file. Method: docs/methods/battery_earns_algorithm.md.
"""

import argparse
import calendar
import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

MODEL, FLEET, RAW = "battery_stack_monthly", "ercot_storage_dam_awards_monthly", "ercot_dam_esr_awards"
MODEL_ENTITY, FLEET_ENTITY = "ercot:HB_HUBAVG", "ercot:esr_fleet"
PRODUCTS = ["regup", "regdn", "rrs", "ecrs", "nspin"]
RAW_AWARDS = {"regup": ["x_regup_award_mw"], "regdn": ["x_regdn_award_mw"],
              "rrs": ["x_rrspfr_award_mw", "x_rrsffr_award_mw", "x_rrsufr_award_mw"],
              "ecrs": ["x_ecrs_award_mw"], "nspin": ["x_nonspin_award_mw"]}
CASES = [(s, d) for s in ("foresight", "dayahead") for d in (2, 4, 8)]
SNAPSHOT = os.path.join(ROOT, "site", "data", "battery_awards_beside.json")


def retrieved(in_dir, name):
    """The table's own "Retrieved:" header line, its time only; "" when it has none."""
    with open(os.path.join(in_dir, name + ".csv"), encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if line.startswith("# Retrieved: "):
                return line[len("# Retrieved: "):].split(" ")[0].strip()
    return ""


def snapshot(mt, ft, in_dir, built):
    """The page's file: per strategy and duration, the months both tables hold whole and the two figures in USD per kW
    of power and month, each rounded to four decimals, and their ratio. Every number in it is a sum of rows of the two
    tables."""
    fleet = by_month(ft, FLEET_ENTITY)
    cases = {}
    for strat, dur in CASES:
        r = beside(by_month(mt, MODEL_ENTITY, f"{strat}_{dur}h_"), fleet)
        if r is None or r["ratio"] is None:
            continue
        cases[f"{strat}_{dur}h"] = dict(first=r["months"][0], last=r["months"][-1], months=r["n"],
                                        model=round(r["model_kw_month"], 4), fleet=round(r["fleet_kw_month"], 4),
                                        ratio=round(r["ratio"], 4))
    return dict(built=built, unit="USD per kW of power and month", model_table=MODEL, model_entity=MODEL_ENTITY,
                fleet_table=FLEET, fleet_entity=FLEET_ENTITY,
                retrieved={MODEL: retrieved(in_dir, MODEL), FLEET: retrieved(in_dir, FLEET)}, cases=cases)


def read(in_dir, name):
    path = os.path.join(in_dir, name + ".csv")
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)


def by_month(table, entity, prefix=""):
    """{month: {variable without the prefix: value}} of one entity."""
    t = table[(table["entity"] == entity) & table["variable"].str.startswith(prefix)]
    out = {}
    for v, ts, x in zip(t["variable"], t["ts_utc"], t["value"]):
        out.setdefault(ts[:7], {})[v[len(prefix):]] = float(x)
    return out


def whole(v):
    return "days_held" in v and v["days_held"] == v.get("days_in_month")


def beside(model, fleet):
    """The months both hold whole, and over them the two sums (USD per MW), per product and together."""
    months = sorted(m for m in fleet if whole(fleet[m]) and m in model and whole(model[m])
                    and "revenue_ancillary_usd_per_mw" in model[m] and "revenue_ancillary_usd_per_mw" in fleet[m])
    if not months:
        return None
    out = dict(months=months, n=len(months))
    for k in ["ancillary"] + PRODUCTS:
        out[f"model_{k}"] = sum(model[m].get(f"revenue_{k}_usd_per_mw", 0.0) for m in months)
        out[f"fleet_{k}"] = sum(fleet[m].get(f"revenue_{k}_usd_per_mw", 0.0) for m in months)
    out["model_kw_month"] = out["model_ancillary"] / 1000 / len(months)
    out["fleet_kw_month"] = out["fleet_ancillary"] / 1000 / len(months)
    out["ratio"] = out["model_ancillary"] / out["fleet_ancillary"] if out["fleet_ancillary"] > 0 else None
    return out


def quantities(in_dir, months, fleet, chunk=400000):
    """From the raw awards: per month of `months`, the megawatt-hours awarded in each product, over the fleet's mw times
    the month's hours: the share of the fleet's power held in that product in the average hour."""
    path = os.path.join(in_dir, RAW + ".csv")
    cols = ["ts_utc"] + [c for cs in RAW_AWARDS.values() for c in cs]
    sums = {}
    for part in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=cols, dtype=str, keep_default_na=False, chunksize=chunk):
        local = pd.to_datetime(part["ts_utc"], utc=True).dt.tz_convert("America/Chicago").dt.strftime("%Y-%m")
        for k, cs in RAW_AWARDS.items():
            q = sum(pd.to_numeric(part[c], errors="coerce").fillna(0.0) for c in cs)
            for m, v in q.groupby(local).sum().items():
                sums.setdefault(m, dict.fromkeys(PRODUCTS, 0.0))[k] += float(v)
    out = {}
    for m in months:
        y, mo = int(m[:4]), int(m[5:7])
        a = pd.Timestamp(f"{m}-01").tz_localize("America/Chicago")
        b = (pd.Timestamp(f"{m}-01") + pd.offsets.MonthBegin(1)).tz_localize("America/Chicago")
        hours = (b - a).total_seconds() / 3600
        assert calendar.monthrange(y, mo)[1] == fleet[m]["days_in_month"]
        out[m] = {k: sums.get(m, {}).get(k, 0.0) / (fleet[m]["mw"] * hours) for k in PRODUCTS}
        out[m]["all"] = sum(out[m][k] for k in PRODUCTS)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the battery model's ancillary revenue beside ERCOT's storage awards")
    ap.add_argument("--in-dir", default=ip.OUT_DIR, help="read the tables from this directory; nothing is written there")
    ap.add_argument("--out-dir", required=True, help="write battery_awards_compare.csv here")
    ap.add_argument("--quantities", action="store_true", help="also read the raw awards for the megawatts awarded")
    ap.add_argument("--snapshot", nargs="?", const=SNAPSHOT, help="also write the page's file (default site/data/battery_awards_beside.json)")
    a = ap.parse_args(argv)
    in_dir = os.path.abspath(a.in_dir)
    missing = [t for t in (MODEL, FLEET) if not os.path.exists(os.path.join(in_dir, t + ".csv"))]
    if missing:
        print(f"battery_awards_compare SKIPPED: input tables not on this machine: {', '.join(missing)}")
        return 0
    mt, ft = read(in_dir, MODEL), read(in_dir, FLEET)
    fleet = by_month(ft, FLEET_ENTITY)
    rows = []
    for strat, dur in CASES:
        r = beside(by_month(mt, MODEL_ENTITY, f"{strat}_{dur}h_"), fleet)
        if r is None:
            print(f"{strat} {dur}h: no month is held whole by both tables")
            continue
        rows.append(dict(strategy=strat, duration_hours=dur, first_month=r["months"][0], last_month=r["months"][-1], months=r["n"],
                         model_usd_per_kw_month=round(r["model_kw_month"], 4), fleet_usd_per_kw_month=round(r["fleet_kw_month"], 4),
                         ratio=round(r["ratio"], 4),
                         **{f"model_{k}_usd_per_kw_month": round(r[f"model_{k}"] / 1000 / r["n"], 4) for k in PRODUCTS},
                         **{f"fleet_{k}_usd_per_kw_month": round(r[f"fleet_{k}"] / 1000 / r["n"], 4) for k in PRODUCTS}))
        print(f"{strat} {dur}h: {r['months'][0]} to {r['months'][-1]} ({r['n']} months): model {r['model_kw_month']:.4f}, "
              f"fleet {r['fleet_kw_month']:.4f} USD per kW-month, ratio {r['ratio']:.4f}")
    os.makedirs(a.out_dir, exist_ok=True)
    out = os.path.join(a.out_dir, "battery_awards_compare.csv")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# ERW session 178: the battery model's day-ahead ancillary revenue beside ERCOT's storage awards; USD per kW-month; "
                f"from {MODEL} and {FLEET}; months both hold whole\n")
        pd.DataFrame(rows).to_csv(f, index=False, lineterminator="\n")
    months = beside(by_month(mt, MODEL_ENTITY, "foresight_4h_"), fleet)["months"] if rows else []
    if a.snapshot:
        snap = snapshot(mt, ft, in_dir, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        if not snap["cases"]:
            print("battery_awards_compare FAILED: no case could be compared; the page's file is not written", file=sys.stderr)
            return 1
        with open(a.snapshot, "w", encoding="utf-8", newline="\n") as f:
            json.dump(snap, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"snapshot: {os.path.relpath(a.snapshot, ROOT)} ({len(snap['cases'])} cases)")
    for m in months:
        v = fleet[m]
        print(f"fleet {m}: {v['mw']:.1f} MW, {int(v['resources'])} resources, {int(v['resources_with_award'])} with an award, "
              f"ancillary {v['revenue_ancillary_usd_per_mw'] / 1000:.4f} USD per kW")
    if a.quantities and months:
        if not os.path.exists(os.path.join(in_dir, RAW + ".csv")):
            print(f"quantities SKIPPED: {RAW} is not on this machine")
            return 0
        q = quantities(in_dir, months, fleet)
        with open(os.path.join(a.out_dir, "battery_awards_quantities.csv"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# ERW session 178: megawatt-hours awarded day-ahead to ERCOT's storage resources by product; over the fleet's mw times "
                    f"the month's hours; from {RAW} and {FLEET}\n")
            f.write("month,fleet_mw," + ",".join(f"share_{k}" for k in PRODUCTS) + ",share_all\n")
            for m in months:
                f.write(f"{m},{fleet[m]['mw']}," + ",".join(f"{q[m][k]:.6f}" for k in PRODUCTS) + f",{q[m]['all']:.6f}\n")
                print(f"awarded share {m}: " + ", ".join(f"{k} {q[m][k] * 100:.2f}%" for k in PRODUCTS) + f", together {q[m]['all'] * 100:.2f}%")
        mean = {k: sum(q[m][k] for m in months) / len(months) for k in PRODUCTS + ["all"]}
        print("awarded share, mean of the months: " + ", ".join(f"{k} {mean[k] * 100:.2f}%" for k in PRODUCTS) + f", together {mean['all'] * 100:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
