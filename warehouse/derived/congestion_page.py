#!/usr/bin/env python3
"""ERW: congestion rolled up, two monthly tables and the page file site/data/conditions/congestion.json (chain 601,
part C, step 2, session 9000).

Energy Research Warehouse (ERW). Reads constraints_binding_hourly and price_congestion_hourly (written by
warehouse/connectors/grid_congestion.py); makes no request. Contract: docs/state/page_files_conditions.md. Method:
docs/methods/grid_congestion.md. Writes:

  constraints_binding_monthly   for each constraint and month (the operator's local month): hours_bound (count),
                                shadow_price_mean, shadow_price_abs_mean, shadow_price_abs_max (USD/MWh)
  price_congestion_monthly      for each hub and zone and month: lmp_mean, energy_mean, congestion_mean, loss_mean,
                                ghg_mean (USD/MWh, the means of the hours held), congestion_share_pct (the month's
                                mean congestion part over its mean LMP, times 100; no row when the mean LMP is not
                                above zero), hours_held (count)
  site/data/conditions/congestion.json

No figure of the ERW's own beyond counts, sums, means, highs and shares of what the operators published. A
constraint is named as the operator names it, with no guess at where it is.

    python warehouse/derived/congestion_page.py                 # the tables and the site's file
    python warehouse/derived/congestion_page.py --out-dir DIR   # a trial: tables and file under DIR
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402
import grid_congestion as gc  # noqa: E402

SITE_FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")
METHOD = "docs/methods/grid_congestion.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_congestion.md"
TZ = {"spp": "America/Chicago", "caiso": "America/Los_Angeles"}
TIME_WORDS = {"spp": "Central clock time (SPP's operating day)", "caiso": "Pacific clock time (CAISO's operating day)"}
TOP = 25
OPERATORS = [
    dict(id="spp", name="SPP", status="shown"),
    dict(id="caiso", name="CAISO", status="shown"),
    dict(id="ercot", name="ERCOT", status="source needed",
         why="ERCOT publishes its shadow prices only on paths its robots file disallows, or through an API whose key "
             "has not been made (the owner's ruling of 6 November 2026)"),
    dict(id="pjm", name="PJM", status="license needed", why="PJM's terms forbid non-members to republish its data"),
    dict(id="nyiso", name="NYISO", status="license needed", why="NYISO's terms reserve its data; written permission needed"),
    dict(id="isone", name="ISO-NE", status="license needed", why="ISO-NE's terms ask written permission"),
    dict(id="miso", name="MISO", status="paused", why="MISO's terms forbid automated access; the ERW paused it on 4 October 2026"),
]
PLACE_NAMES = {
    "SPPNORTH_HUB": "SPP North hub", "SPPSOUTH_HUB": "SPP South hub",
    "TH_NP15_GEN-APND": "NP15 trading hub", "TH_SP15_GEN-APND": "SP15 trading hub", "TH_ZP26_GEN-APND": "ZP26 trading hub",
    "DLAP_PGAE-APND": "PG&E default load area", "DLAP_SCE-APND": "SCE default load area",
    "DLAP_SDGE-APND": "SDG&E default load area", "DLAP_VEA-APND": "VEA default load area",
}


def read(name, cols):
    p = os.path.join(ip.OUT_DIR, name + ".csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, usecols=cols, dtype=str, keep_default_na=False)
    fh.close()
    d["value"] = pd.to_numeric(d["value"], errors="raise")
    return d


def localize(d):
    d["op"] = d["market"].str.split("_").str[0]
    ts = pd.to_datetime(d["ts_utc"], utc=True)
    loc = pd.Series(index=d.index, dtype="datetime64[ns]")
    for op, tz in TZ.items():
        m = d["op"] == op
        loc[m] = ts[m].dt.tz_convert(tz).dt.tz_localize(None)
    d["local"] = loc
    d["month"] = d["local"].dt.strftime("%Y-%m")
    d["year"] = d["local"].dt.year.astype(str)
    d["moy"] = d["local"].dt.month
    d["hod"] = d["local"].dt.hour
    return d


def r(x, n=2):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


def month_ts(month):
    return f"{month}-01T00:00:00Z"


def monthly_constraints(c, run_at):
    g = c.groupby(["entity", "market", "month"])
    m = g["value"].agg(hours="count", mean="mean").join(
        g["abs"].agg(abs_mean="mean", abs_max="max")).reset_index()
    first = c.groupby("entity")[["x_constraint", "x_contingency"]].first()
    m = m.join(first, on="entity")
    rows = []
    for var, col, unit in [("hours_bound", "hours", "count"), ("shadow_price_mean", "mean", "USD/MWh"),
                           ("shadow_price_abs_mean", "abs_mean", "USD/MWh"), ("shadow_price_abs_max", "abs_max", "USD/MWh")]:
        rows.append(pd.DataFrame({
            "entity": m["entity"], "variable": var, "ts_utc": m["month"].map(month_ts), "value": m[col].round(5),
            "unit": unit, "freq": "P1M", "geo": np.where(m["market"] == "spp_dam", gc.SPP_GEO, gc.CAISO_GEO),
            "market": m["market"], "node": "", "source": "erw:constraints_binding_monthly", "source_url": METHOD_URL,
            "retrieved_at": run_at, "vintage": "", "x_constraint": m["x_constraint"], "x_contingency": m["x_contingency"]}))
    return pd.concat(rows, ignore_index=True)


def monthly_prices(p, run_at):
    w = p.pivot_table(index=["entity", "node", "market", "month", "ts_utc"], columns="variable", values="value").reset_index()
    g = w.groupby(["entity", "node", "market", "month"])
    parts = [v for v in ["lmp_dam", "energy_dam", "congestion_dam", "loss_dam", "ghg_dam"] if v in w.columns]
    m = g[parts].mean().join(g.size().rename("hours")).reset_index()
    rows = []
    for v in parts:
        s = m[m[v].notna()]
        rows.append(s.assign(variable=v.replace("_dam", "_mean"), value=s[v].round(5), unit="USD/MWh"))
    s = m[m["lmp_dam"] > 0]
    rows.append(s.assign(variable="congestion_share_pct", value=(100 * s["congestion_dam"] / s["lmp_dam"]).round(4), unit="pct"))
    rows.append(m.assign(variable="hours_held", value=m["hours"], unit="count"))
    out = pd.concat(rows, ignore_index=True)
    return pd.DataFrame({
        "entity": out["entity"], "variable": out["variable"], "ts_utc": out["month"].map(month_ts), "value": out["value"],
        "unit": out["unit"], "freq": "P1M", "geo": np.where(out["market"] == "spp_dam", gc.SPP_GEO, gc.CAISO_GEO),
        "market": out["market"], "node": out["node"], "source": "erw:price_congestion_monthly", "source_url": METHOD_URL,
        "retrieved_at": run_at, "vintage": ""})[ip.SERIES_COLS]


def join_elements(d):
    """Session 11407 (the ruling readied for congestion audit finding 2): one row an element and hour.

    The table's entity is the element under one contingency (name|contingency), and SPP's files until November 2021
    name no contingency, so one element stood on several rows. Here the page's constraint is the element
    (x_constraint, the operator's name alone): an hour it bound under several contingencies is one hour, its size there
    the sizes summed (one more megawatt on the element relaxes each), and its signed price the prices summed. The
    contingencies it was listed under are kept, in order, with "" for a listing that names none.
    """
    d = d.assign(entity=d["op"] + ":" + d["x_constraint"])
    conts = d.groupby("entity")["x_contingency"].agg(lambda s: sorted(set(s))).rename("contingencies")
    keep = ["local", "year", "month", "moy", "hod", "x_constraint", "x_monitored", "x_constraint_type", "x_nerc_id"]
    g = d.groupby(["entity", "ts_utc"], sort=True)
    e = g[["value", "abs"]].sum().join(g[keep].first()).reset_index()
    e = e.join(conts, on="entity")
    e["x_contingency"] = e["contingencies"].map(lambda c: c[0] if len(c) == 1 else "")
    e["op"] = d["op"].iloc[0]
    return e


def constraint_page(c):
    out = {}
    for op, d in c.groupby("op"):
        d = join_elements(d)
        years = sorted(d["year"].unique())
        days = d.groupby("year")["local"].apply(lambda s: s.dt.normalize().nunique()).to_dict()
        ent = d.groupby("entity")
        tot = pd.DataFrame({"hours": ent.size(), "cost": ent["abs"].sum(), "abs_mean": ent["abs"].mean(),
                            "abs_max": ent["abs"].max()})
        by_year = d.groupby(["year", "entity"])["abs"].agg(hours="count", cost="sum", abs_mean="mean", abs_max="max").reset_index()
        chosen = set(tot.nlargest(TOP, "hours").index) | set(tot.nlargest(TOP, "cost").index)
        top = {}
        for y, g in by_year.groupby("year"):
            h = g.nlargest(TOP, "hours")
            k = g.nlargest(TOP, "cost")
            chosen |= set(h["entity"]) | set(k["entity"])
            top[y] = {"by_hours": h["entity"].tolist(), "by_cost": k["entity"].tolist()}
        top["all"] = {"by_hours": tot.nlargest(TOP, "hours").index.tolist(), "by_cost": tot.nlargest(TOP, "cost").index.tolist()}
        detail = {}
        for e in sorted(chosen):
            x = d[d["entity"] == e]
            first = x.iloc[0]
            mon = x.groupby("month")["abs"].agg(["count", "mean", "max"])
            sm = x.groupby("month")["value"].mean()
            grid = np.zeros((12, 24), dtype=int)
            for (mo, hr), n in x.groupby(["moy", "hod"]).size().items():
                grid[mo - 1, hr] = n
            yr = by_year[by_year["entity"] == e].set_index("year")
            detail[e] = {
                "name": first["x_constraint"], "contingency": first["x_contingency"] or None,
                "contingencies": first["contingencies"] if len(first["contingencies"]) > 1 else None,
                "monitored": first["x_monitored"] or None, "type": first["x_constraint_type"] or None,
                "nerc_id": first["x_nerc_id"] or None, "first": x["ts_utc"].min(), "last": x["ts_utc"].max(),
                "hours": int(len(x)), "abs_mean": r(x["abs"].mean()), "abs_max": r(x["abs"].max()),
                "cost": r(x["abs"].sum(), 1),
                "by_year": {y: {"hours": int(v["hours"]), "abs_mean": r(v["abs_mean"]), "abs_max": r(v["abs_max"]),
                                "cost": r(v["cost"], 1)} for y, v in yr.iterrows()},
                "monthly": [[m, int(v["count"]), r(v["mean"]), r(v["max"]), r(sm[m])] for m, v in mon.iterrows()],
                "hod_month": grid.tolist(),
            }
        n_by_year = by_year.groupby("year").size().to_dict()
        out[op] = {"time": TIME_WORDS[op], "years": years, "days_held": {y: int(days[y]) for y in years},
                   "constraints_by_year": {y: int(n_by_year[y]) for y in years},
                   "hours_by_year": {y: int((d["year"] == y).sum()) for y in years},
                   "first": d["ts_utc"].min(), "last": d["ts_utc"].max(), "top": top, "constraints": detail}
    return out


def place_page(p):
    w = p.pivot_table(index=["op", "node", "ts_utc", "year", "month", "moy", "hod"], columns="variable", values="value").reset_index()
    out = {}
    for (op, node), x in w.groupby(["op", "node"]):
        years = sorted(x["year"].unique())
        mon = x.groupby("month")
        monthly = []
        for m, v in mon:
            lmp, cong = v["lmp_dam"].mean(), v["congestion_dam"].mean()
            monthly.append([m, int(len(v)), r(lmp), r(v["energy_dam"].mean()), r(cong), r(v["loss_dam"].mean()),
                            r(v["ghg_dam"].mean()) if "ghg_dam" in v else None,
                            r(100 * cong / lmp, 1) if lmp > 0 else None])
        by_year, hod = {}, {}
        for y, v in x.groupby("year"):
            lmp, cong = v["lmp_dam"].mean(), v["congestion_dam"].mean()
            by_year[y] = {"hours": int(len(v)), "lmp_mean": r(lmp), "congestion_mean": r(cong),
                          "congestion_share_pct": r(100 * cong / lmp, 1) if lmp > 0 else None,
                          "hours_congestion_up": int((v["congestion_dam"] > 0).sum()),
                          "hours_congestion_down": int((v["congestion_dam"] < 0).sum()),
                          "congestion_max": r(v["congestion_dam"].max()), "congestion_min": r(v["congestion_dam"].min())}
            grid = [[None] * 24 for _ in range(12)]
            for (mo, hr), s in v.groupby(["moy", "hod"])["congestion_dam"]:
                grid[mo - 1][hr] = r(s.mean())
            hod[y] = grid
        out.setdefault(op, []).append({"id": f"{op}:{node}", "node": node, "name": PLACE_NAMES.get(node, node),
                                       "time": TIME_WORDS[op], "years": years, "first": x["ts_utc"].min(),
                                       "last": x["ts_utc"].max(),
                                       "monthly_columns": ["month", "hours", "lmp_mean", "energy_mean", "congestion_mean",
                                                           "loss_mean", "ghg_mean", "congestion_share_pct"],
                                       "monthly": monthly, "by_year": by_year, "hod_month_congestion_mean": hod})
    return out


def header(name, what, inputs, run_id):
    return [
        f"Energy Research Warehouse (ERW): {what} (derived, chain 601 session 9000)",
        "Shape: series (docs/datastandard.md v0); freq P1M, ts_utc the first day of the operator's local month at "
        "00:00:00Z (SPP Central, CAISO Pacific).",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/congestion_page.py",
        f"Source: erw:{name} ERW derived table, {METHOD_URL}",
        "Derived from: " + "; ".join(inputs),
        "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): SPP "
        "(with citation; a commercial publication needs SPP's written authorization), CAISO (credit the California ISO).",
        f"Method: {METHOD}",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: congestion roll-ups and page file")
    ap.add_argument("--out-dir")
    ap.add_argument("--in-dir", help="read the hourly tables from this directory (a trial); default warehouse/output")
    a = ap.parse_args(argv)
    site_file = SITE_FILE
    src_dir = a.in_dir or ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
        site_file = os.path.join(a.out_dir, "congestion.json")
    out_dir = ip.OUT_DIR
    ip.OUT_DIR = src_dir  # read from the warehouse
    os.makedirs(os.path.join(out_dir, "logs"), exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log = ip.Log(os.path.join(out_dir, "logs", f"congestion_page_{run_id}.log"))
    c = read(gc.T_CONS, ["entity", "ts_utc", "value", "market", "x_constraint", "x_contingency", "x_monitored",
                         "x_constraint_type", "x_nerc_id"])
    p = read(gc.T_PRICE, ["entity", "variable", "ts_utc", "value", "market", "node"])
    c = localize(c)
    c["abs"] = c["value"].abs()
    p = localize(p)
    ip.OUT_DIR = out_dir
    gc.write("constraints_binding_monthly", monthly_constraints(c, run_at), ip.SERIES_COLS + ["x_constraint", "x_contingency"],
             header("constraints_binding_monthly", "binding constraints by month: hours bound and shadow prices "
                    "(SPP and CAISO, day-ahead)", [gc.T_CONS], run_id), log)
    gc.write("price_congestion_monthly", monthly_prices(p, run_at), ip.SERIES_COLS,
             header("price_congestion_monthly", "the parts of the day-ahead price at hubs and zones by month, and the "
                    "share of the price that was congestion (SPP and CAISO)", [gc.T_PRICE], run_id), log)
    page = {
        "built": run_at, "method": METHOD, "contract": "docs/state/page_files_conditions.md", "license": "public",
        "tables": [gc.T_CONS, gc.T_PRICE, "constraints_binding_monthly", "price_congestion_monthly"],
        "unit": "USD/MWh", "market": "day-ahead",
        "sign_rule": "Shadow prices are as each operator prints them: SPP's negative, CAISO's positive. Ranks, means "
                     "and highs use the size of the price (its absolute value).",
        "cost_rule": "A constraint's cost here is its shadow price summed over the hours it bound (USD/MWh times hours), "
                     "a ranking of how often and how dearly it bound; no flow is published, so no dollar total is made.",
        "share_rule": "A month's congestion share is its mean congestion part over its mean LMP, times 100; none when the "
                      "mean LMP is not above zero.",
        "operators": OPERATORS,
        "sources": {
            "spp": {"constraints": "SPP, Day-Ahead Binding Constraints (portal.spp.org, da-binding-constraints)",
                    "prices": "SPP, Day-Ahead LMP by Settlement Location (portal.spp.org, da-lmp-by-settlement-location)"},
            "caiso": {"constraints": "California ISO, OASIS PRC_NOMOGRAM (nomogram and branch shadow prices, DAM)",
                      "prices": "California ISO, OASIS PRC_LMP (DAM: LMP, energy, congestion, loss, greenhouse gas)"},
        },
        "constraints": constraint_page(c),
        "places": place_page(p),
    }
    os.makedirs(os.path.dirname(site_file), exist_ok=True)
    with open(site_file, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(page, fh, separators=(",", ":"), ensure_ascii=False)
    size = os.path.getsize(site_file)
    msg = f"{os.path.relpath(site_file, ROOT)}: {size:,} bytes"
    print(msg)
    log(msg)
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
