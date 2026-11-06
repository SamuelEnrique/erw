#!/usr/bin/env python3
"""The generator pipeline by grid: EIA-860M's planned generators by balancing authority, state, fuel, status and planned
year, each snapshot month, and what moved between two consecutive snapshots (session 2951, chain 157).

Energy Research Warehouse (ERW). One derived table, generator_pipeline_by_grid, from what this machine holds of EIA-860M:
the current snapshot (eia860m_planned_generators and eia860m_operating_generators, one vintage each) and an earlier
month's workbook kept in the raw files (warehouse/raw/eia860m_retired_all/<run>/*_<month>_generator<year>.xlsx, the
Planned, Planned_PR, Operating and Operating_PR sheets). Method: docs/methods/generator_pipeline_by_grid.md. No request.

    python warehouse/derived/generator_pipeline_by_grid.py               # the table (data lock)
    python warehouse/derived/generator_pipeline_by_grid.py --out-dir DIR # a trial

    entity    eia860m_pipeline:<balancing authority>:<state>:<energy source code>:<EIA status>:<planned year> for a cell
              of a snapshot; eia860m_pipeline:<balancing authority> and eia860m_pipeline:US for the moves
    ts_utc    the snapshot's month (its first day); freq P1M
    variables a cell: planned_mw (nameplate MW), planned_count (generators), datacenter_mw (the MW of the cell's
              datacenter-tagged generators: a plant or owner whose name names a data center or a lab, the rule below)
              the moves from the month before to this one, keyed by plant and generator id: entered_mw (planned now, in
              neither list before), online_mw (planned before, operating now), left_mw (planned before, in neither list
              now: cancelled, postponed or withdrawn; EIA's own Canceled sheet of this month is not held, so the three
              are not told apart), status_moved_mw (planned in both, its EIA status changed), slipped_mw (planned in both,
              its planned year later now), each with its _count
A generator with no balancing authority is under "none". Nameplate MW as EIA gives it; nothing is filled.
"""

import argparse
import datetime as dt
import glob
import io
import os
import re
import sys
import traceback

import openpyxl
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "generator_pipeline_by_grid"
SOURCE = "erw:generator_pipeline_by_grid"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generator_pipeline_by_grid.md"
PLANNED, OPERATING = "eia860m_planned_generators", "eia860m_operating_generators"
RAW = os.path.join(ROOT, "warehouse", "raw", "eia860m_retired_all")
DATACENTER = re.compile(r"data ?cent(?:er|re)|datacenter|\blabs?\b|laborator", re.I)
MONTHS = {m.lower(): i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                                 "September", "October", "November", "December"], 1)}
COLS = ip.SERIES_COLS + ["x_ba", "x_state", "x_energy_source", "x_status", "x_planned_year", "x_from_vintage"]
MOVES = ("entered", "online", "left", "status_moved", "slipped")


def key(plant, gen):
    return f"{str(plant).strip()}:{str(gen).strip()}"


def current(folder):
    """(the planned frame, the set of operating keys, the vintage 'YYYY-MM') from the snapshot tables."""
    p, o = os.path.join(folder, f"{PLANNED}.csv"), os.path.join(folder, f"{OPERATING}.csv")
    d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
    op = pd.read_csv(o, skiprows=ip.header_rows(o), dtype=str, keep_default_na=False, usecols=["plant_id", "generator_id", "vintage"])
    vint = sorted(d["vintage"].unique())
    if len(vint) != 1 or sorted(op["vintage"].unique()) != vint:
        raise RuntimeError(f"the planned and operating tables are not one vintage: {vint}, {sorted(op['vintage'].unique())}")
    plan = pd.DataFrame({"key": [key(a, b) for a, b in zip(d["plant_id"], d["generator_id"])], "ba": d["balancing_authority"],
                         "state": d["state"], "fuel": d["energy_source"], "status": d["eia_status"],
                         "year": d["planned_operation_date"].str[:4], "mw": pd.to_numeric(d["nameplate_mw"], errors="coerce"),
                         "tag": d["name"].str.contains(DATACENTER) | d["operator"].str.contains(DATACENTER)})
    return plan, {key(a, b) for a, b in zip(op["plant_id"], op["generator_id"])}, vint[0]


def workbook_vintage(path):
    m = re.search(r"_([a-z]+)_generator(\d{4})\.xlsx$", os.path.basename(path).lower())
    return f"{m.group(2)}-{MONTHS[m.group(1)]:02d}" if m and m.group(1) in MONTHS else None


def earlier(before, raw=RAW):
    """The newest raw workbook of a month before `before` ('YYYY-MM'): (path, vintage) or (None, None)."""
    found = {}
    for p in sorted(glob.glob(os.path.join(raw, "*", "*_generator*.xlsx"))):
        v = workbook_vintage(p)
        if v and v < before:
            found[v] = p
    if not found:
        return None, None
    v = max(found)
    return found[v], v


def sheet(wb, name):
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if r and "Plant ID" in [str(c).strip() if c is not None else "" for c in r])
    head = [str(c).strip() if c is not None else "" for c in rows[hi]]
    body = [r for r in rows[hi + 1:] if r and r[head.index("Plant ID")] not in (None, "")]
    return pd.DataFrame(body, columns=head)


def from_workbook(path):
    """(the planned frame, the operating keys) of an EIA-860M generator workbook."""
    wb = openpyxl.load_workbook(io.BytesIO(open(path, "rb").read()), read_only=True, data_only=True)
    plan = pd.concat([sheet(wb, s) for s in ("Planned", "Planned_PR") if s in wb.sheetnames], ignore_index=True)
    op = pd.concat([sheet(wb, s) for s in ("Operating", "Operating_PR") if s in wb.sheetnames], ignore_index=True)

    def col(d, start):
        return next(c for c in d.columns if c.startswith(start))
    p = pd.DataFrame({"key": [key(a, b) for a, b in zip(plan["Plant ID"], plan["Generator ID"])],
                      "ba": plan[col(plan, "Balancing Authority")].fillna("").astype(str), "state": plan["Plant State"].fillna("").astype(str),
                      "fuel": plan["Energy Source Code"].fillna("").astype(str), "status": plan["Status"].fillna("").astype(str).str.split(")").str[0].str.strip("( "),
                      "year": plan["Planned Operation Year"].apply(lambda v: str(int(v)) if v not in (None, "") else ""),
                      "mw": pd.to_numeric(plan[col(plan, "Nameplate Capacity")], errors="coerce"),
                      "tag": plan["Plant Name"].fillna("").astype(str).str.contains(DATACENTER) | plan["Entity Name"].fillna("").astype(str).str.contains(DATACENTER)})
    return p, {key(a, b) for a, b in zip(op["Plant ID"], op["Generator ID"])}


def cells(plan, vintage, source_url):
    rows = []
    plan = plan.assign(ba=plan["ba"].replace("", "none"))
    for (ba, st, fu, sta, yr), g in plan.groupby(["ba", "state", "fuel", "status", "year"]):
        ent = f"eia860m_pipeline:{ba}:{st}:{fu}:{sta}:{yr}"
        for var, val, unit in (("planned_mw", round(float(g["mw"].sum()), 3), "MW"), ("planned_count", int(len(g)), "count"),
                               ("datacenter_mw", round(float(g.loc[g["tag"], "mw"].sum()), 3), "MW")):
            rows.append({"entity": ent, "variable": var, "ts_utc": f"{vintage}-01T00:00:00Z", "value": val, "unit": unit, "freq": "P1M",
                         "geo": f"US-{st}" if re.match(r"^[A-Z]{2}$", st) else "US", "market": "", "node": "", "source": SOURCE,
                         "source_url": source_url, "vintage": vintage, "x_ba": ba, "x_state": st, "x_energy_source": fu, "x_status": sta,
                         "x_planned_year": yr, "x_from_vintage": ""})
    return rows


def moves(before, before_op, now, now_op):
    """{move: frame of the generators that made it} from the month before to now."""
    b, n = before.set_index("key"), now.set_index("key")
    both = b.index.intersection(n.index)
    out = {"entered": n.loc[n.index.difference(b.index).difference(list(before_op))],
           "online": b.loc[[k for k in b.index if k in now_op and k not in n.index]],
           "left": b.loc[[k for k in b.index if k not in n.index and k not in now_op]],
           "status_moved": n.loc[[k for k in both if b.at[k, "status"] != n.at[k, "status"]]],
           "slipped": n.loc[[k for k in both if (b.at[k, "year"] or "0") < (n.at[k, "year"] or "0") and b.at[k, "year"]]]}
    return out


def move_rows(mv, vintage, from_vintage, source_url):
    rows = []
    for name, g in mv.items():
        g = g.assign(ba=g["ba"].replace("", "none"))
        groups = list(g.groupby("ba")) + [("US", g)]
        for ba, x in groups:
            for var, val, unit in ((f"{name}_mw", round(float(x["mw"].sum()), 3), "MW"), (f"{name}_count", int(len(x)), "count")):
                rows.append({"entity": f"eia860m_pipeline:{ba}", "variable": var, "ts_utc": f"{vintage}-01T00:00:00Z", "value": val, "unit": unit,
                             "freq": "P1M", "geo": "US", "market": "", "node": "", "source": SOURCE, "source_url": source_url, "vintage": vintage,
                             "x_ba": ba, "x_state": "", "x_energy_source": "", "x_status": "", "x_planned_year": "", "x_from_vintage": from_vintage})
    return rows


def build(folder=None, raw=RAW):
    folder = folder or ip.OUT_DIR
    now, now_op, vint = current(folder)
    path, prev = earlier(vint, raw)
    url = f"https://www.eia.gov/electricity/data/eia860m/"
    rows = cells(now, vint, url)
    info = {"vintage": vint, "earlier": prev, "earlier_path": path, "tagged": int(now["tag"].sum())}
    if path:
        before, before_op = from_workbook(path)
        rows += cells(before, prev, url)
        mv = moves(before, before_op, now, now_op)
        rows += move_rows(mv, vint, prev, url)
        info["moves"] = {k: (len(v), round(float(v["mw"].sum()), 1)) for k, v in mv.items()}
        info["tagged_earlier"] = int(before["tag"].sum())
    t = pd.DataFrame(rows, columns=COLS)
    return t.sort_values(["ts_utc", "entity", "variable"]).reset_index(drop=True), info


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the EIA-860M generator pipeline by grid and its monthly moves (session 2951)")
    ap.add_argument("--out-dir", help="a trial: the table under this folder")
    a = ap.parse_args(argv)
    folder = ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        t, info = build(folder)
        t["retrieved_at"] = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
        mv = info.get("moves", {})
        header = [
            "Energy Research Warehouse (ERW): EIA-860M's planned generators by balancing authority, state, fuel, status and planned year, each snapshot month, and the moves between two months (derived, session 2951)",
            "Shape: series (docs/datastandard.md v0). entity eia860m_pipeline:<BA>:<state>:<energy source>:<status>:<year> (a cell) or eia860m_pipeline:<BA> and :US (the moves); "
            "ts_utc the snapshot month; variables planned_mw, planned_count, datacenter_mw for a cell; entered_, online_, left_, status_moved_, slipped_ (mw and count) for the moves.",
            f"Snapshots: {info['vintage']} (eia860m_planned_generators and eia860m_operating_generators) and {info.get('earlier') or 'none earlier held'}"
            + (f" ({os.path.relpath(info['earlier_path'], ROOT).replace(os.sep, '/')})" if info.get("earlier_path") else "") + ".",
            "Moves " + (f"{info['earlier']} to {info['vintage']}: " + "; ".join(f"{k} {n} generators, {mw} MW" for k, (n, mw) in mv.items()) if mv else "none: no earlier month held") + ".",
            f"Datacenter-tagged (plant or owner name matching {DATACENTER.pattern!r}): {info['tagged']} planned generators in {info['vintage']}"
            + (f", {info.get('tagged_earlier', 0)} in {info['earlier']}" if mv else "") + ".",
            f"Derived from: {PLANNED}; {OPERATING}",   # the earlier month's workbook is named in the Snapshots line (a raw file, not a table)
            f"Built by warehouse/derived/generator_pipeline_by_grid.py; method docs/methods/generator_pipeline_by_grid.md",
            f"Retrieved: {run_id} (UTC), computed from the tables and files held; no request was made.",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            "Source: eia:860m U.S. Energy Information Administration, EIA-860M Monthly Update to the Annual Electric Generator Report",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-860M").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=COLS)
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="EIA-860M's generator pipeline by grid and its monthly moves (docs/methods/generator_pipeline_by_grid.md)",
                                    report_url=METHOD_URL, document_list="docs/methods/generator_pipeline_by_grid.md", license="public", tables=[NAME])])
        print(f"{NAME}: {len(t)} rows; {info['vintage']} and {info.get('earlier')}; moves {mv}; tagged {info['tagged']}")
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
