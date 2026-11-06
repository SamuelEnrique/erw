#!/usr/bin/env python3
"""ERW, the Grid tool (/grid): the figures the page prints, written to page_figures.json and page_figures.csv, and the
network's hour written to snapshot_hour.csv for Stata (session 3703, chain 208).

Three groups, each as the page draws it:

- network: the Network and Gravity tabs' keyed figures (net|..., the gravity shape's generation and share) and the
  network's carbon intensity per grid, computed by the page's own functions (network_figures.mjs runs site/lib/
  gridKeys.ts, networkV3.ts, network.ts and networkGravity.ts with node) on a network snapshot: the committed
  site/data/grid_network.json by default, or the hourly copy the page reads from public Storage. The gravity shape's
  generation comes from eia930_all_generation at the hour shown, when the tables given hold it.
- carbon: the Clean tab's monthly block, each of the seven grids' first and last month of carbon_intensity_monthly
  (intensity_generation), the months site/data/carbon_left_out.json lists left out (components/grid/Emissions.tsx
  Monthly); each figure is the row its key names, from the tables given.
- ask: the Ask panel's stored answers (site/data/grid_ask_examples.json), the first five of each grid as the panel
  shows them, each figure with the query it came from; an answer whose table is held for its grid on the day prints
  "license needed" (site/lib/gridask.ts heldTableOf, site/lib/license.ts licenseHeldRow).

    python replication/grid/figures_of_the_page.py [--snapshot PATH] [--tables DIR] [--day YYYY-MM-DD] [--check]

--tables is a folder of the warehouse's tables as CSV (default warehouse/output, where the data and code machines keep
them); a table not there leaves its figures out, said in the file. --check writes nothing and exits 1 when the files
differ from what would be written. Standard library and pandas; node for the network group. Method:
docs/methods/grid_network.md, "Replication".
"""

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import tempfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SNAPSHOT = os.path.join(ROOT, "site", "data", "grid_network.json")
TABLES = os.path.join(ROOT, "warehouse", "output")
LICENSE = os.path.join(ROOT, "site", "data", "license_status.json")
LEFT_OUT = os.path.join(ROOT, "site", "data", "carbon_left_out.json")
ASK = os.path.join(ROOT, "site", "data", "grid_ask_examples.json")
OUT_JSON = os.path.join(HERE, "page_figures.json")
OUT_CSV = os.path.join(HERE, "page_figures.csv")
OUT_HOUR = os.path.join(HERE, "snapshot_hour.csv")
ISOS = ["ERCO", "CISO", "PJM", "MISO", "NYIS", "ISNE", "SWPP"]   # components/grid/Emissions.tsx ISOS, the network's seven
GRID_PREFIX = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "PJM": "pjm", "SPP": "spp", "CAISO": "caiso", "ERCOT": "ercot"}
GRID_NAMES = set(GRID_PREFIX.values())
NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_table(folder, table, usecols=None, entities=None, variables=None):
    """A table of the warehouse as CSV ('#' header lines skipped), or None when the folder does not hold it. Read in
    chunks and filtered as it is read, so a table of a gigabyte fits in little memory."""
    path = os.path.join(folder, table + ".csv")
    if not os.path.exists(path):
        return None
    parts = []
    for chunk in pd.read_csv(path, comment="#", dtype=str, usecols=usecols, chunksize=500_000, keep_default_na=False):
        if entities is not None:
            chunk = chunk[chunk["entity"].isin(entities)]
        if variables is not None:
            chunk = chunk[chunk["variable"].isin(variables)]
        parts.append(chunk)
    return pd.concat(parts, ignore_index=True) if parts else None


def retrieved(folder, table):
    """The table's own "Retrieved:" header line, which says when its copy was made; "" when the folder does not hold it."""
    path = os.path.join(folder, table + ".csv")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if line.startswith("# Retrieved:"):
                return line[len("# Retrieved:"):].strip()[:80]
    return ""


# ---------------------------------------------------------------- the license hold, as site/lib/license.ts
def license_tables():
    return load(LICENSE)["tables"]


def license_needed(tables, table, day):
    r = tables.get(table)
    return bool(r) and r.get("status") == "license needed" and day >= r.get("from", "9999")


def grid_of_entity(entity):
    """site/lib/license.ts gridOfEntity: "isone:.H.INTERNAL_HUB" and "iso:isone" are ISO-NE's; "nyiso_queue:1630" NYISO's."""
    m = re.match(r"^([a-z0-9_-]+):(.*)$", entity or "", re.I)
    if not m:
        return ""
    head = m.group(1).lower()
    if head in GRID_NAMES:
        return head
    q = re.match(r"^([a-z]+)_(?:load_)?queue$", head)
    if q and q.group(1) in GRID_NAMES:
        return q.group(1)
    if head == "iso" and m.group(2).lower() in GRID_NAMES:
        return m.group(2).lower()
    return ""


def license_held_row(tables, table, entity, day):
    """site/lib/license.ts licenseHeldRow with an entity given."""
    if not license_needed(tables, table, day):
        return False
    r = tables[table]
    if r.get("hold") == "row":
        return False
    who = r.get("publishers", [])
    if not (who and all(p in GRID_PREFIX for p in who)):
        return True
    g = grid_of_entity(entity)
    return bool(g) and any(GRID_PREFIX[p] == g for p in who)


def held_table_of(tables, example, day):
    """site/lib/gridask.ts heldTableOf."""
    for s in example["sources"]:
        ents = s.get("entities") or [""]
        for t in s["tables"]:
            for ent in ents:
                entity = ent if grid_of_entity(ent) else f"iso:{example['grid']}"
                if license_held_row(tables, t, entity, day):
                    return t
    return None


# ---------------------------------------------------------------- the three groups
def generation_week(snapshot, tables_dir):
    """{BA: [MW per hour of the snapshot, or None]} from eia930_all_generation, as the page's live read gives it."""
    snap = load(snapshot)
    df = read_table(tables_dir, "eia930_all_generation", usecols=["entity", "variable", "ts_utc", "value"],
                    entities=[f"eia930:{b}" for b in ISOS + ["US48"]], variables=["net_generation_mw"])
    if df is None or not len(df):
        return None
    df = df[df["ts_utc"].isin(set(snap["hours"]))]
    if not len(df):
        return None
    at = {(r.entity, r.ts_utc): float(r.value) for r in df.itertuples() if r.value != ""}
    return {b: [at.get((f"eia930:{b}", h)) for h in snap["hours"]] for b in ISOS + ["US48"]}


def network_group(snapshot, tables_dir):
    gen = generation_week(snapshot, tables_dir)
    with tempfile.TemporaryDirectory() as d:
        argv = ["node", "--no-warnings", os.path.join(HERE, "network_figures.mjs"), snapshot]
        if gen:
            gp = os.path.join(d, "generation.json")
            with open(gp, "w", encoding="utf-8") as f:
                json.dump(gen, f)
            argv.append(gp)
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", cwd=ROOT, timeout=120)
    if p.returncode != 0:
        raise SystemExit(f"network_figures.mjs failed: {p.stderr[-800:]}")
    out = json.loads(p.stdout)
    out["generation_held"] = bool(gen)
    return out


def carbon_group(tables_dir):
    df = read_table(tables_dir, "carbon_intensity_monthly", usecols=["entity", "variable", "ts_utc", "value"],
                    entities=[f"eia930:{b}" for b in ISOS], variables=["intensity_generation"])
    if df is None:
        return None, []
    left = {(m["entity"], m["variable"], m["month"]) for m in load(LEFT_OUT)["months"]}
    df = df[[(e, v, t[:7]) not in left for e, v, t in zip(df["entity"], df["variable"], df["ts_utc"])]].sort_values("ts_utc")
    out = []
    for b in ISOS:
        rows = df[df["entity"] == f"eia930:{b}"]
        if not len(rows):
            continue
        for tag, r in (("first", rows.iloc[0]), ("last", rows.iloc[-1])):
            out.append({"group": "carbon", "name": f"{b}: carbon intensity of its generation, its {tag} month held ({r['ts_utc'][:7]}), kg CO2 per MWh",
                        "check": f"series|carbon_intensity_monthly|{r['entity']}|intensity_generation|{r['ts_utc']}",
                        "raw": float(r["value"]), "page_text": "", "held": False, "source": None})
    return sorted(df["ts_utc"].str[:7].unique())[-1] if len(df) else None, out


def scopes():
    """The grid chats' scope rules (warehouse/chat/tools.py scope_rows): each grid's ba, ISO, market prefix and queue table
    (docs/grids/grids.json) and, by table, the rule that admitted it (docs/grids/grid_tables.json)."""
    grids = {g["slug"]: g for g in load(os.path.join(ROOT, "docs", "grids", "grids.json"))["grids"]}
    ruled = load(os.path.join(ROOT, "docs", "grids", "grid_tables.json"))["grids"]
    return grids, ruled


def scope_of(example, table, grids, ruled):
    """The rule an answer's rows were kept by: a grid's own chat or the Grid panel's profile reads only that grid's rows;
    the general chat reads every row (None)."""
    if example.get("via") not in ("panel", "grid") or example["grid"] not in grids:
        return None
    g = grids[example["grid"]]
    return {"slug": g["slug"], "by": (ruled.get(example["grid"], {}).get("by") or {}).get(table), "ba": g.get("ba"), "iso": g.get("iso"),
            "market_prefix": g.get("market_prefix"), "queue_table": g.get("queue_table"), "filters": (g.get("filters") or {}).get(table)}


def ask_group(day):
    tables, file = license_tables(), load(ASK)
    grids, ruled = scopes()
    out = []
    for grid, g in file["grids"].items():
        for e in g["examples"][: file["max_examples"]]:
            held = held_table_of(tables, e, day)
            for k, s in enumerate(e["sources"]):
                for j, fig in enumerate(s.get("figures") or []):
                    out.append({"group": "ask", "name": f"{grid}: {e['id']}, source {k + 1}, figure {j + 1}: {e['question'][:120]}",
                                "check": f"ask|{e['id']}|{k}|{j}", "raw": None if held else float(fig.replace(",", "")),
                                "page_text": "license needed" if held else fig, "held": bool(held),
                                "source": {"tool": s["tool"], "tables": s["tables"], "filter": s.get("filter", ""),
                                           "scope": scope_of(e, s["tables"][0], grids, ruled)},
                                "asked_at": e.get("asked_at_utc", ""),
                                "decimals": len(fig.split(".")[1]) if "." in fig else 0})
    return out


def build(snapshot, tables_dir, day):
    net = network_group(snapshot, tables_dir)
    last_month, carbon = carbon_group(tables_dir)
    ask = ask_group(day)
    figures = [{"group": f["tab"], "name": f["name"], "check": f["check"], "raw": f["raw"], "page_text": "", "held": False, "source": None}
               for f in net["figures"]] + carbon + ask
    for f in figures:
        # half of the last digit the page shows: lib/format.ts shown() writes a whole number as a count, any other with
        # two decimals; a stored answer's figure, as its text has it
        if f["group"] == "ask":
            f["tolerance"] = 0.5 * 10 ** -f["decimals"]
        else:
            f["tolerance"] = 0.5 if f["raw"] is not None and float(f["raw"]).is_integer() else 0.005
    snap = load(snapshot)
    doc = {
        "_about": ("The Grid tool (/grid): the figures the page prints, each with its check key and value. The network group is the page's "
                   "own code (network_figures.mjs) on the snapshot named here; the carbon group is the rows of carbon_intensity_monthly the "
                   "Clean tab's monthly block names, read from the tables named here; the ask group is the Ask panel's stored answers, as "
                   "the panel shows them on the day. Written by figures_of_the_page.py; replicate.py recomputes each figure without the "
                   "page's code, from the snapshot and the tables."),
        "written_for_day": day,
        "snapshot": os.path.relpath(snapshot, ROOT).replace(os.sep, "/") if snapshot.startswith(ROOT) else snapshot,
        "snapshot_built": snap["built"],
        "hour_shown": net["hour"],
        "pairs": net["pairs"],
        "reporting": net["reporting"],
        "generation_held": net["generation_held"],
        "tables": "warehouse/output" if os.path.normpath(tables_dir).replace(os.sep, "/").endswith("warehouse/output") else tables_dir,
        "tables_retrieved": {t: retrieved(tables_dir, t) for t in ("carbon_intensity_monthly", "carbon_intensity_hourly", "eia930_all_emissions",
                                                                   "eia930_all_generation", "cost_of_power_monthly", "merchant_revenue_monthly")},
        "carbon_last_month_held": last_month,
        "ask_file_built_by": load(ASK)["built_by"],
        "not_replicated": ("the Mix tab's latest-hour figures and the Clean tab's latest hours (live reads of eia930_all_demand, "
                           "eia930_all_generation and carbon_intensity_hourly as the page is drawn: replicate.py's mix_now applies the page's "
                           "rules to rows a reader reads with the public key, and this chain read none); the hourly carbon intensity itself "
                           "(its denominators are EIA's per-BA workbooks, which no table holds); the Mix tab's other views (site/data/mix, "
                           "clean, stress, mixplus: built from EIA's workbooks on the data machine)"),
        "figures": figures,
    }
    cols = ["group", "check", "name", "page_text", "raw", "tolerance", "held"]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for f in figures:
        w.writerow(["" if f[c] is None else (int(f[c]) if c == "held" else f[c]) for c in cols])
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n", buf.getvalue(), hour_csv(snap, net["hour"])


def hour_csv(snap, hour):
    """The snapshot's hour shown, for Stata: one row per tie with a flow, per node's demand and intensity."""
    h = snap["hours"].index(hour)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["kind", "id", "other", "ts_utc", "value"])
    for l in snap["links"]:
        v = l["mw"][h]
        if v is not None:
            w.writerow(["tie", l["a"], l["b"], hour, v])
    for n in snap["nodes"]:
        if n.get("demand_recent") and hour in n["demand_recent"]:
            w.writerow(["demand", n["id"], "", hour, n["demand_recent"][hour]])
        elif n.get("demand_ts") == hour and n.get("demand_mw") is not None:
            w.writerow(["demand", n["id"], "", hour, n["demand_mw"]])
    return buf.getvalue()


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--snapshot", default=SNAPSHOT)
    ap.add_argument("--tables", default=TABLES)
    ap.add_argument("--day", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    texts = build(os.path.abspath(a.snapshot), os.path.abspath(a.tables), a.day)
    paths = (OUT_JSON, OUT_CSV, OUT_HOUR)
    if a.check:
        same = True
        for p, t in zip(paths, texts):
            if not os.path.exists(p):
                same = False
                continue
            with open(p, encoding="utf-8") as f:
                same = same and f.read() == t
        print("the page's figures are current" if same else "page_figures.json, page_figures.csv or snapshot_hour.csv differs: write them again")
        return 0 if same else 1
    for p, t in zip(paths, texts):
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    figs = json.loads(texts[0])["figures"]
    by = {}
    for f in figs:
        by[f["group"]] = by.get(f["group"], 0) + 1
    print(f"{len(figs)} figures written ({', '.join(f'{k} {v}' for k, v in by.items())}; {sum(1 for f in figs if f['held'])} license needed)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
