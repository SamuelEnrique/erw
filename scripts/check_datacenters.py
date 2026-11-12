#!/usr/bin/env python3
"""Every figure of the datacenter tracker's charts, traced to datacenter_facilities by a second computation (session
2246, chain 156).

Energy Research Warehouse (ERW). `/datacenters` draws three charts with the page's functions (`site/lib/dcrollups.ts`,
`dcFigures()`), each figure keyed `dcchart|<planned|operator|power>|<x>|<series>`. In the form of
`scripts/check_deals.py` (and `scripts/check_digest.py`), this script recomputes every figure from the warehouse's CSV
with its own code, runs the page's functions on the same rows (`site/scripts/datacenters-figures.mjs`, with node), and
compares the two, key by key:

    planned    by the quarter first reported, the MW the counted facilities state that are planned or under
               construction, by grid (the four grids with the most, the rest as other), and those stating none
    operator   the ten operators (else developers) with the most MW stated
    power      the counted facilities by the kind of power stated, and their share to a tenth of a percent

Counted: a named US state, a status other than withdrawn or cancelled. The grid: the table's own (session 2243), else
the grid that serves most of the state.

    python scripts/check_datacenters.py                 # warehouse/output/datacenter_facilities.csv, read only
    python scripts/check_datacenters.py --in-dir DIR    # another copy

Exit 1 when any figure fails or is on one side only, or when none was compared; 0 otherwise. Writes nothing but a
temporary file of the rows for node.
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
STATES = set(("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC "
              "ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY").split())
STATE_GRID = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", "CT": "ISO-NE", "ME": "ISO-NE", "MA": "ISO-NE", "NH": "ISO-NE",
              "RI": "ISO-NE", "VT": "ISO-NE", "PA": "PJM", "NJ": "PJM", "MD": "PJM", "DE": "PJM", "VA": "PJM", "WV": "PJM",
              "OH": "PJM", "DC": "PJM", "MN": "MISO", "IA": "MISO", "WI": "MISO", "MI": "MISO", "LA": "MISO", "OK": "SPP",
              "KS": "SPP", "NE": "SPP"}
STD = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source",
       "source_url", "retrieved_at", "vintage"]


def _hdr(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n


def num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def recompute(t):
    rows = []
    for r in t.to_dict("records"):
        st = (r.get("state") or "").upper()
        if st not in STATES or (r.get("status") or "").lower() in ("withdrawn", "cancelled"):
            continue
        rows.append({"grid": r.get("grid") or STATE_GRID.get(st, ""), "mw": num(r["capacity_mw"]), "status": (r.get("status") or "").lower(),
                     "op": r.get("operator") or "", "first": r.get("first_story_at") or "", "power": r.get("power_kind") or "none"})
    out = {}
    ahead = [r for r in rows if r["status"] in ("planned", "under_construction")]
    gmw = {}
    for r in ahead:
        if r["mw"] is not None and r["grid"]:
            gmw[r["grid"]] = gmw.get(r["grid"], 0) + r["mw"]
    top = [g for g, _ in sorted(gmw.items(), key=lambda x: (-x[1], x[0]))[:4]]
    dated = [r for r in ahead if len(r["first"]) >= 7 and r["first"][:4].isdigit()]
    for q in sorted({f"{r['first'][:4]}-Q{(int(r['first'][5:7]) - 1) // 3 + 1}" for r in dated}):
        inq = [r for r in dated if f"{r['first'][:4]}-Q{(int(r['first'][5:7]) - 1) // 3 + 1}" == q]
        for g in top + ["other"]:
            out[f"dcchart|planned|{q}|{g}"] = sum(r["mw"] or 0 for r in inq if (r["grid"] if r["grid"] in top else "other") == g)
        out[f"dcchart|planned|{q}|without"] = sum(1 for r in inq if r["mw"] is None)
    ops = {}
    for r in rows:
        e = ops.setdefault(r["op"], [0.0, 0, 0])
        e[2] += 1
        if r["mw"] is not None:
            e[0] += r["mw"]
            e[1] += 1
    ranked = sorted(((o, e) for o, e in ops.items() if o and e[1] > 0), key=lambda x: (-x[1][0], -x[1][2], x[0]))[:10]
    for o, e in ranked:
        out[f"dcchart|operator|{o}|mw"] = e[0]
    kinds = {}
    for r in rows:
        kinds[r["power"]] = kinds.get(r["power"], 0) + 1
    for k, n in kinds.items():
        out[f"dcchart|power|{k}|facilities"] = n
        out[f"dcchart|power|{k}|pct"] = round(1000 * n / len(rows)) / 10 if rows else 0
    return out


def page_figures(t):
    exe = shutil.which("node")
    if not exe:
        raise SystemExit("check_datacenters: node is not on this machine")
    rows = [{"entity_id": r["entity_id"], "capacity_mw": r["capacity_mw"], "status": r["status"], "operator": r["operator"],
             "extra": {k: v for k, v in r.items() if k not in STD and v != ""}} for r in t.to_dict("records")]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(rows, f)
        tmp = f.name
    try:
        r = subprocess.run([exe, os.path.join("scripts", "datacenters-figures.mjs"), tmp], cwd=SITE, capture_output=True,
                           text=True, timeout=300)
    finally:
        os.remove(tmp)
    if r.returncode != 0:
        raise SystemExit(f"check_datacenters: the page's functions failed: {r.stderr[-1500:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def compare(page, mine):
    lines, bad = [], 0
    for k in sorted(set(page) | set(mine)):
        if k not in mine:
            lines.append(f"page only  {k} = {page[k]}")
            bad += 1
        elif k not in page:
            lines.append(f"check only {k} = {mine[k]}")
            bad += 1
        elif math.isclose(float(page[k]), float(mine[k]), rel_tol=1e-9, abs_tol=1e-6):
            lines.append(f"ok         {k} = {mine[k]}")
        else:
            lines.append(f"FAIL       {k}: page {page[k]}, check {mine[k]}")
            bad += 1
    return lines, bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in-dir", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    path = os.path.join(args.in_dir, "datacenter_facilities.csv")
    t = pd.read_csv(path, skiprows=_hdr(path), dtype=str, keep_default_na=False)
    lines, bad = compare(page_figures(t), recompute(t))
    for line in lines:
        if not args.quiet or not line.startswith("ok"):
            print(line)
    print(f"check_datacenters: {len(lines) - bad} of {len(lines)} figures agree ({len(t)} facilities)")
    return 1 if bad or not lines else 0


if __name__ == "__main__":
    sys.exit(main())
