#!/usr/bin/env python3
"""JEDI's default construction cost per MW, by technology and location (session 4200, chain 239: the forecast tool).

Energy Research Warehouse (ERW), tool 17. The forecast model scales JEDI's construction effects by the reader's
spending over JEDI's own default spending for that state (docs/methods/forecast.md, section 2). nlr_jedi_multipliers
holds JEDI's effects per MW but not the cost they rest on; this script reads that cost from the same evaluation that
made the table: warehouse/connectors/jedi_recalc.py's files, one per model, where each location's construction cost
is the denominator of its local share (the `local` cells of jedi_recalc.MODELS). Nothing is estimated: the cost is the
workbook's own formula result at that location, the same pass whose 24 figures per location this script checks
against the table (to its six-decimal rounding) before it writes anything.

    # jedi_recalc's files are made in its own environment (pycel), see that script; chain 239 ran it unchanged with
    # its RAW and OUT pointed outside warehouse/ (runs/w4/jedi_run.py), since this chain writes no warehouse data:
    .venv\\Scripts\\python.exe warehouse/forecast/jedi_costs.py --recalc <folder of jedi_recalc's json files>

Writes site/data/forecast/jedi_costs.json. Exit 0 written, 1 a check failed (nothing written), 2 bad input.
"""

import argparse
import csv
import datetime as dt
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
TABLE = os.path.join(ROOT, "warehouse", "output", "nlr_jedi_multipliers.csv")
OUT = os.path.join(ROOT, "site", "data", "forecast", "jedi_costs.json")
TOL = 1e-4  # the table rounds each figure to six decimals; a jobs figure near 0.05 rounds by up to 1e-5 relative


def models():
    """jedi_recalc.MODELS without importing pycel: the dict is read from the script's source."""
    import ast
    src = open(os.path.join(ROOT, "warehouse", "connectors", "jedi_recalc.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("MODELS", "MEASURES"):
            # the dict is written with dict(...) calls: the expression alone, with nothing but dict to call
            out[node.targets[0].id] = eval(compile(ast.Expression(node.value), "jedi_recalc.py", "eval"), {"__builtins__": {}, "dict": dict})
    return out["MODELS"], out["MEASURES"]


def table_rows(path):
    t = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            t[(r["x_technology"], r["x_location"].strip().upper(), r["x_phase"], r["x_effect"], r["variable"])] = (float(r["value"]), r["x_state"].lower() or "us")
    return t


def build(recalc, table_path=TABLE):
    MODELS, MEASURES = models()
    table = table_rows(table_path)
    out, problems = {}, []
    for tech, m in MODELS.items():
        p = os.path.join(recalc, f"{tech}.json")
        if not os.path.exists(p):
            problems.append(f"{tech}: no file {p}")
            continue
        d = json.load(open(p, encoding="utf-8"))
        rows = {}
        for loc, r in d["results"].items():
            L = loc.strip().upper()
            mw = r[m["mw"]] * m["mw_scale"]
            loc_cell, cost_cell = m["local"]["construction"]
            cost = r[cost_cell]  # every model states its construction cost in dollars
            code, n = None, 0
            for phase, effect, row, _ in m["rows"]:
                for meas, col in MEASURES:
                    v = r[f"{m['summary']}!{col}{row}"] * (1 if meas == "jobs" else m["scale"]) / mw
                    hit = table.get((tech, L, phase, effect, meas))
                    if hit is None:
                        continue
                    t, code = hit
                    n += 1
                    if abs(v - t) > TOL * max(1e-9, abs(t)):
                        problems.append(f"{tech} {L} {phase}:{effect}:{meas}: recalc {v} against the table's {t}")
            if n == 0:
                continue  # a location the table does not hold (JEDI's own error there): no cost either
            if n != 24:
                problems.append(f"{tech} {L}: {n} of 24 figures found in the table")
            rows[code] = {"location": L, "cost_usd": round(cost, 2), "project_mw": round(mw, 6),
                          "cost_usd_per_mw": round(cost / mw, 2), "cells": cost_cell}
        out[tech] = {"file": d["file"], "sha256": d["sha256"], "dollar_year": int(next(iter(d["results"].values()))[m["dollar_year"]]),
                     "mw_basis": m["mw_basis"], "evaluated_at": d.get("evaluated_at"), "states": dict(sorted(rows.items()))}
    return out, problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--recalc", default=os.path.join(ROOT, "warehouse", "raw", "nlr_jedi", "recalc"))
    ap.add_argument("--table", default=TABLE)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    if not os.path.isdir(a.recalc) or not os.path.exists(a.table):
        print(f"jedi_costs: need jedi_recalc's folder ({a.recalc}) and the table ({a.table})", file=sys.stderr)
        return 2
    data, problems = build(a.recalc, a.table)
    if problems:
        for p in problems[:20]:
            print("jedi_costs:", p, file=sys.stderr)
        print(f"jedi_costs: {len(problems)} problems, nothing written", file=sys.stderr)
        return 1
    doc = {
        "about": "JEDI's default construction cost per MW of its default project, by technology and location: each "
                 "workbook's own formula result with Project Location set to that location (warehouse/connectors/jedi_recalc.py), "
                 "the denominator of nlr_jedi_multipliers' construction local share. Dollars of each model's own dollar year. "
                 "Every location's 24 figures were checked against nlr_jedi_multipliers before this file was written.",
        "source": "National Laboratory of the Rockies (NLR, formerly NREL), JEDI models, https://www.nlr.gov/analysis/jedi/models",
        "notice": "NLR's data terms (https://www.nlr.gov/disclaimer): the user is granted the right, without any fee or cost, to use "
                  "or copy the Data, provided that this entire notice appears in all copies of the Data; credit DOE/NLR/ALLIANCE; "
                  "the Data are provided as is.",
        "written_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "written_by": "warehouse/forecast/jedi_costs.py",
        "technologies": data,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    n = sum(len(v["states"]) for v in data.values())
    print(f"jedi_costs: {n} locations of {len(data)} models written to {os.path.relpath(a.out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
