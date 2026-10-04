#!/usr/bin/env python3
"""Who owns the batteries: operating and planned battery storage by reporting company and grid, from EIA-860M.

Energy Research Warehouse (ERW), session 87 (the site's /storage/owners, in review). No pull: reads the two EIA-860M
tables of the newest inventory (eia860m_operating_generators, eia860m_planned_generators) and writes one derived
`series` table, and the snapshot the review page reads:

    storage_owners_monthly           freq P1M, one inventory month; the company rows and the grid rows below
    site/data/storage_owners.json    the same rows for the page (--snapshot; the page is in review and the table is held
                                     out of the live set, so the page reads this file and not Supabase)

    python warehouse/derived/storage_owners.py                                  # warehouse/output (the data lock)
    python warehouse/derived/storage_owners.py --inputs-dir D --out-dir S       # a trial run: nothing in warehouse/output
    python warehouse/derived/storage_owners.py --snapshot                       # also write site/data/storage_owners.json

Method: docs/methods/storage_owners.md. In short:

- A battery is a generator with prime mover BA, as in storage_buildout.py; the grid of a unit is its balancing
  authority code where that is one of the seven ISOs, else outside_isos; `us` is every unit. Operating is EIA's
  operating inventory (statuses OP, SB, OS, OA); planned is EIA's planned inventory.
- The owner is EIA-860M's Entity: the company that reports the plant to EIA, by its Entity ID (entity
  eia860:utility:<id>) and Entity Name. It is the plant's owner or operator, very often a project company. EIA-860M
  does not name a parent, and nothing here merges names: two project companies of one developer are two owners.
  Ownership shares are in the annual EIA-860 (Schedule 4), which this table does not read.
- Per company and grid: operating MW (nameplate), operating MWh (Nameplate Energy Capacity, of the units that report
  it), the average duration (that MWh over the MW of the same units; omitted, never zero, where no unit reports
  energy), units, planned MW and units, the rank by operating MW in the grid (1 the largest; ties by name, so a rank
  is given once), and the share of the grid's operating MW.
- Per grid (entity iso:<grid>, us:outside_isos, us:total): companies with operating batteries, companies with planned
  ones, the operating and planned totals, and the share of operating MW held by the 5 and the 10 largest companies.
  The operating totals are the newest month of storage_buildout_monthly (tested equal).
- MW and MWh are summed as whole ten-thousandths (storage_buildout.scaled); a share or a duration is rounded half up.
  A planned MWh is never written: EIA's Planned sheet has no energy column.
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import storage_buildout as sb  # noqa: E402

NAME = "storage_owners_monthly"
SOURCE = "erw:storage_owners"
METHOD = "docs/methods/storage_owners.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_owners.md"
INPUTS = {"operating": "eia860m_operating_generators", "planned": "eia860m_planned_generators"}
GRIDS = list(sb.ISO_OF_BA.values()) + ["outside_isos", "us"]  # caiso ... spp, the rest, and every unit
GRID_ENTITY = {**{g: f"iso:{g}" for g in sb.ISO_OF_BA.values()}, "outside_isos": sb.OUTSIDE, "us": sb.TOTAL}
COLS = ip.SERIES_COLS + ["x_grid", "x_metric", "x_owner"]
SNAPSHOT = os.path.join(ROOT, "site", "data", "storage_owners.json")
TOP = (5, 10)
SCALE = sb.SCALE


def grid_of(ba):
    return sb.ISO_OF_BA.get(ba, "outside_isos")


def pct(num, den):
    """num over den as a percentage to two decimals, half up; None when the denominator is zero."""
    if den == 0:
        return None
    return float((Decimal(num) * 100 / Decimal(den)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def units(op, pl):
    """One row per battery unit: owner id and name, grid, table, MW, MWh (None where EIA gives none)."""
    rows = []
    for table, d in (("operating", op), ("planned", pl)):
        for r in d[d["prime_mover"] == "BA"].to_dict("records"):
            if not r["utility_id"] or not r["operator"]:
                raise RuntimeError(f"{r['entity_id']}: no Entity ID or Entity Name in the {table} table")
            mwh = None
            if table == "operating" and r["energy_capacity_mwh"] != "":
                mwh = sb.scaled(r["energy_capacity_mwh"], f"{r['entity_id']} energy_capacity_mwh")
            rows.append(dict(unit=r["entity_id"], owner=r["utility_id"], name=r["operator"], grid=grid_of(r["balancing_authority"]),
                             table=table, mw=sb.scaled(r["nameplate_mw"], f"{r['entity_id']} nameplate_mw"), mwh=mwh))
    u = pd.DataFrame(rows)
    names = u.groupby("owner")["name"].nunique()
    if (names > 1).any():
        raise RuntimeError(f"an Entity ID carries more than one name: {sorted(names[names > 1].index)[:6]}")
    return u


def build(op, pl, log=lambda m: None):
    """The table's rows as dicts (entity, grid, metric, value, unit, owner), and the counts the header states."""
    vint = sorted(set(op["vintage"]) | set(pl["vintage"]))
    if len(vint) != 1:
        raise RuntimeError(f"the two EIA-860M tables are not one vintage: {vint}")
    u = units(op, pl)
    out = []

    def add(entity, grid, metric, value, unit, owner=""):
        out.append(dict(entity=entity, grid=grid, metric=metric, value=value, unit=unit, owner=owner))
    for grid in GRIDS:
        g = u if grid == "us" else u[u["grid"] == grid]
        o, p = g[g["table"] == "operating"], g[g["table"] == "planned"]
        total_mw = int(o["mw"].sum())
        held = o[o["mwh"].notna()]
        ge = GRID_ENTITY[grid]
        add(ge, grid, "operating_mw", total_mw / SCALE, "MW")
        add(ge, grid, "operating_mwh", int(held["mwh"].sum()) / SCALE, "MWh")
        add(ge, grid, "operating_units", float(len(o)), "count")
        add(ge, grid, "owners_operating", float(o["owner"].nunique()), "count")
        add(ge, grid, "planned_mw", int(p["mw"].sum()) / SCALE, "MW")
        add(ge, grid, "planned_units", float(len(p)), "count")
        add(ge, grid, "owners_planned", float(p["owner"].nunique()), "count")
        if sb.ratio(int(held["mwh"].sum()), int(held["mw"].sum())) is not None:
            add(ge, grid, "operating_hours", sb.ratio(int(held["mwh"].sum()), int(held["mw"].sum())), "MWh/MW")
        by = {}
        for owner, name in g[["owner", "name"]].drop_duplicates().itertuples(index=False):
            oo, pp = o[o["owner"] == owner], p[p["owner"] == owner]
            hh = oo[oo["mwh"].notna()]
            by[owner] = dict(name=name, mw=int(oo["mw"].sum()), mwh=int(hh["mwh"].sum()), mw_held=int(hh["mw"].sum()),
                             units=len(oo), planned_mw=int(pp["mw"].sum()), planned_units=len(pp))
        ranked = sorted((k for k, v in by.items() if v["units"]), key=lambda k: (-by[k]["mw"], by[k]["name"], k))
        for n in TOP:
            if total_mw:
                add(ge, grid, f"top{n}_share_pct", pct(sum(by[k]["mw"] for k in ranked[:n]), total_mw), "pct")
        for owner, v in by.items():
            e = f"eia860:utility:{owner}"
            if v["units"]:
                add(e, grid, "operating_mw", v["mw"] / SCALE, "MW", v["name"])
                add(e, grid, "operating_mwh", v["mwh"] / SCALE, "MWh", v["name"])
                add(e, grid, "operating_units", float(v["units"]), "count", v["name"])
                add(e, grid, "operating_rank", float(ranked.index(owner) + 1), "count", v["name"])
                add(e, grid, "operating_share_pct", pct(v["mw"], total_mw), "pct", v["name"])
                if sb.ratio(v["mwh"], v["mw_held"]) is not None:
                    add(e, grid, "operating_hours", sb.ratio(v["mwh"], v["mw_held"]), "MWh/MW", v["name"])
            if v["planned_units"]:
                add(e, grid, "planned_mw", v["planned_mw"] / SCALE, "MW", v["name"])
                add(e, grid, "planned_units", float(v["planned_units"]), "count", v["name"])
    o, p = u[u["table"] == "operating"], u[u["table"] == "planned"]
    stats = dict(vintage=vint[0], operating_units=len(o), planned_units=len(p), owners_operating=int(o["owner"].nunique()),
                 owners_planned=int(p["owner"].nunique()), owners_both=len(set(o["owner"]) & set(p["owner"])),
                 no_energy_units=int(o["mwh"].isna().sum()))
    log(f"  {stats}")
    return out, stats


def to_series(rows, vintage, retrieved):
    d = pd.DataFrame(rows)
    return pd.DataFrame({
        "entity": d["entity"], "variable": d["grid"] + "_" + d["metric"], "ts_utc": vintage + "-01T00:00:00Z",
        "value": d["value"], "unit": d["unit"], "freq": "P1M", "geo": "US", "market": "", "node": "", "source": SOURCE,
        "source_url": METHOD_URL, "retrieved_at": retrieved, "vintage": "", "x_grid": d["grid"], "x_metric": d["metric"],
        "x_owner": d["owner"],
    }).sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)[COLS]


def snapshot(s, st, run_id, urls):
    """The page's file: the newest inventory month's rows, compact. Every number in it is a row of the table."""
    month = s["ts_utc"].max()
    d = s[s["ts_utc"] == month]
    owners, grids = {}, {}
    for r in d.to_dict("records"):
        if r["entity"].startswith("eia860:utility:"):
            o = owners.setdefault(r["entity"], dict(name=r["x_owner"], grids={}))
            o["grids"].setdefault(r["x_grid"], {})[r["x_metric"]] = r["value"]
        else:
            grids.setdefault(r["x_grid"], dict(entity=r["entity"]))[r["x_metric"]] = r["value"]
    return dict(table=NAME, month=month[:7], built=run_id, source="EIA-860M, inventory of " + st["vintage"], source_urls=urls,
                counts=st, grids=grids, owners=owners)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--inputs-dir", help="read the two EIA-860M tables from this directory (default: warehouse/output)")
    ap.add_argument("--out-dir", help="write the table, log, registry and status under this directory (a trial run)")
    ap.add_argument("--snapshot", action="store_true", help="also write site/data/storage_owners.json (with --out-dir: under it)")
    a = ap.parse_args(argv)
    inputs_dir = os.path.abspath(a.inputs_dir) if a.inputs_dir else ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"storage_owners_{run_id}.log"))
    status = dict(table=NAME, market="derived", status="ok", detail="")
    missing = [t for t in INPUTS.values() if not os.path.exists(os.path.join(inputs_dir, t + ".csv"))]
    if missing:  # session 10 ruling 3: a derived table without its inputs on the runner skips with a warning
        msg = f"inputs not on this machine: {', '.join(missing)}; the table is left as it is"
        log(f"SKIPPED: {msg}")
        print(f"storage_owners SKIPPED: {msg}")
        ip.write_status("storage_owners", run_id, [dict(status, status="skipped", detail=msg)])
        log.close()
        return 0
    try:
        op, pl = (sb.read(os.path.join(inputs_dir, INPUTS[k] + ".csv")) for k in ("operating", "planned"))
        reg = pd.read_csv(sb.REGISTRY, dtype=str, keep_default_na=False)
        lic = dict(zip(reg["source"], reg["license"]))
        srcs = sorted(set(op["source"]) | set(pl["source"]))
        unknown = [x for x in srcs if x not in lic]
        if unknown:
            raise RuntimeError(f"input sources {unknown} are not in the registry; cannot set the license")
        license_ = "internal" if any(lic[x] == "internal" for x in srcs) else "public"
        urls = sorted(set(op["source_url"]) | set(pl["source_url"]))
        rows, st = build(op, pl, log)
        s = to_series(rows, st["vintage"], ip.utc_iso(pd.Timestamp.now(tz="UTC")))
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("two rows share an (entity, variable, ts_utc) key")
        out_path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(out_path):  # Decision 26: an unchanged row keeps the retrieved_at of the run that first wrote it
            prev = ip.read_series(out_path, COLS)
            prev["value"] = pd.to_numeric(prev["value"])
            key = ["entity", "variable", "ts_utc", "value"]
            s = s.merge(prev[key + ["retrieved_at"]].rename(columns={"retrieved_at": "_prev"}), on=key, how="left")
            s["retrieved_at"] = s["_prev"].fillna(s["retrieved_at"])
            s = s.drop(columns="_prev")
        header = [
            "Energy Research Warehouse (ERW): Who owns the batteries: operating and planned battery storage by reporting "
            f"company and grid; EIA-860M inventory of {st['vintage']} (derived, session 87)",
            "Shape: series (docs/datastandard.md v0). freq P1M: ts_utc is the inventory month. entity eia860:utility:<EIA "
            "Entity ID> for a company (its name as EIA writes it in x_owner), and iso:<caiso|ercot|isone|miso|nyiso|pjm|spp>, "
            "us:outside_isos, us:total for a grid. Variables <grid>_<metric>, also in x_grid and x_metric; grid is one of "
            "caiso, ercot, isone, miso, nyiso, pjm, spp, outside_isos, us (every unit).",
            "Company metrics: operating_mw (nameplate), operating_mwh (Nameplate Energy Capacity of the units that report "
            "it), operating_hours (that MWh over the MW of the same units; omitted where none reports energy), "
            "operating_units, operating_rank (the position by operating MW in the grid, 1 the largest; ties by name; unit count), "
            "operating_share_pct (of the grid's operating MW), planned_mw, planned_units. A company has a metric only "
            "where it has a unit: no zero rows. Grid metrics: operating_mw, operating_mwh, operating_hours, operating_units, "
            "owners_operating, planned_mw, planned_units, owners_planned, top5_share_pct, top10_share_pct (the share of "
            "operating MW of the 5 and 10 largest companies).",
            "The owner is EIA-860M's Entity: the company that reports the plant, its owner or operator, often a project "
            "company. EIA-860M names no parent and nothing here merges names; ownership shares are in the annual EIA-860, "
            "which is not read. No planned MWh: EIA's Planned sheet has no energy column.",
            f"Counts: {st['operating_units']} operating battery units of {st['owners_operating']} companies "
            f"({st['no_energy_units']} units carry no energy value), {st['planned_units']} planned units of "
            f"{st['owners_planned']} companies; {st['owners_both']} companies have both.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/storage_owners.py",
            f"Run log: warehouse/output/logs/storage_owners_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, storage owners method ({METHOD}), {METHOD_URL}",
            "Derived from: " + "; ".join(INPUTS.values()),
            f"  input sources: {'; '.join(srcs)} ({'; '.join(urls)}), inventory month {st['vintage']}",
            f"License: {license_}. A derived table inherits the most restrictive license of its inputs (Decision 23).",
        ]
        ip.write_csv(s[COLS], NAME, header, log, cols=COLS)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report=f"Battery storage by reporting company and grid ({METHOD})", report_url=METHOD_URL,
                                document_list=METHOD, license=license_, tables=[NAME])])
        if a.snapshot:
            path = os.path.join(ip.OUT_DIR, "storage_owners.json") if a.out_dir else SNAPSHOT
            held = ip.read_series(os.path.join(ip.OUT_DIR, NAME + ".csv"), COLS)
            held["value"] = pd.to_numeric(held["value"])
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(snapshot(held, st, run_id, urls), f, indent=0, sort_keys=True)
                f.write("\n")
            log(f"snapshot: {os.path.relpath(path, ROOT)}")
        status["detail"] = (f"{len(s)} rows, inventory {st['vintage']}; {st['operating_units']} operating units of "
                            f"{st['owners_operating']} companies, {st['planned_units']} planned of {st['owners_planned']}")
        log(status["detail"])
        print(f"storage_owners: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"storage_owners FAILED, no output file written: {last}", file=sys.stderr)
        status.update(status="failed", detail=last[:300])
    ip.write_status("storage_owners", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
