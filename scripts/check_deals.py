#!/usr/bin/env python3
"""Every figure of the deals' charts, traced to energy_deals by a second computation (session 2241, chain 156).

Energy Research Warehouse (ERW). `/deals?view=charts` draws four charts from `energy_deals` with the page's functions
(`site/lib/dealsai.ts`, `figures()`), each figure keyed `deals|chart_<mw|price|ai|party>|<x>|<series>`. This script, in
the form of `scripts/check_digest.py`, recomputes every figure from the warehouse's CSV with its own code (the rules
of the method note, written again here in Python, not imported from the site), runs the page's functions on the same
rows (`site/scripts/deals-figures.mjs`, with node), and compares the two, key by key:

    chart_mw      a quarter's MW stated by one kind of supply, and the quarter's deals that state no MW
    chart_price   a priced PPA's or offtake's price in US dollars per MWh
    chart_ai      a quarter's AI-power MW, its MW stated, and the AI-power share of it to a tenth of a percent
    chart_party   a counterparty's MW stated (the ten with the most)

    python scripts/check_deals.py                 # warehouse/output/energy_deals.csv, read only
    python scripts/check_deals.py --in-dir DIR    # the CSV of another copy

Each figure is one line: ok, FAIL (the two disagree), or "page only" / "check only" (a key one side has and the other
does not). Exit 1 when any figure fails or is on one side only, or when no figure was compared; 0 otherwise. Writes
nothing but a temporary file of the rows for node.
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pandas as pd


def _hdr(path):
    """The number of "#" header lines before a table's column row (iso_prices.header_rows: never comment="#")."""
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
FORM_KIND = {"ppa": "ppa", "offtake": "offtake", "project_finance": "project_finance", "m_and_a": "m_and_a",
             "debt": "capital", "equity_raise": "capital", "tax_equity": "capital", "joint_venture": "capital",
             "fuel_supply": "fuel_supply", "behind_the_meter": "behind_the_meter",
             "nuclear_restart": "nuclear_restart_uprate", "smr": "smr"}
STATE_GRID = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", "CT": "ISO-NE", "ME": "ISO-NE", "MA": "ISO-NE", "NH": "ISO-NE",
              "RI": "ISO-NE", "VT": "ISO-NE", "PA": "PJM", "NJ": "PJM", "MD": "PJM", "DE": "PJM", "VA": "PJM", "WV": "PJM",
              "OH": "PJM", "DC": "PJM", "MN": "MISO", "IA": "MISO", "WI": "MISO", "MI": "MISO", "LA": "MISO", "OK": "SPP",
              "KS": "SPP", "NE": "SPP"}


def num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def supply(kind, tech):
    t = (tech or "").lower()
    if kind in ("nuclear_restart_uprate", "smr") or re.search(r"nuclear|reactor|smr|fusion", t):
        return "nuclear"
    if kind == "gas_buildout" or re.search(r"\bgas\b|natural gas|lng|turbine", t):
        return "gas"
    if kind == "storage" or re.search(r"solar|wind|batter|storage|hydro|geotherm|renewable", t):
        return "renewables_storage"
    if kind == "compute_capacity":
        return "compute"
    if kind in ("ppa", "offtake", "behind_the_meter"):
        return "grid"
    if kind in ("capital", "m_and_a", "project_finance"):
        return "capital"
    return "other"


def quarter(date):
    return f"{date[:4]}-Q{(int(date[5:7]) - 1) // 3 + 1}"


def deals_of(path):
    d = pd.read_csv(path, skiprows=_hdr(path), dtype=str, keep_default_na=False)
    with open(os.path.join(SITE, "data", "deal_duplicates.json"), encoding="utf-8") as f:
        pairs = json.load(f)["pairs"]
    ids = set(d["event_id"])
    folded = {p["duplicate"] for p in pairs if p["ruling"] == "fold" and p["duplicate"] in ids and p["kept"] in ids}
    return d, folded


def recompute(d, folded):
    rows = []
    for r in d.to_dict("records"):
        if r["event_id"] in folded:
            continue
        kind = r.get("kind") or FORM_KIND.get(r["deal_type"], "other")
        s = supply(kind, r.get("technology"))
        rows.append({"id": r["event_id"], "date": r["event_date"][:10], "q": quarter(r["event_date"][:10]),
                     "group": s if s in ("nuclear", "gas", "renewables_storage", "grid") else "other",
                     "mw": num(r["mw"]), "price": num(r["price"]), "type": r["deal_type"],
                     "ai": str(r.get("ai_power", "")).lower() == "true",
                     "names": list(dict.fromkeys(x.strip() for x in ((r.get("buyer_name") or r["buyer"]) + "; " +
                                                                     (r.get("seller_name") or r["seller"])).split("; ") if x.strip()))})
    out = {}
    for q in sorted({r["q"] for r in rows}):
        inq = [r for r in rows if r["q"] == q]
        for g in ("nuclear", "gas", "renewables_storage", "grid", "other"):
            out[f"deals|chart_mw|{q}|{g}"] = sum(r["mw"] for r in inq if r["group"] == g and r["mw"] is not None)
        out[f"deals|chart_mw|{q}|without"] = sum(1 for r in inq if r["mw"] is None)
        all_mw = sum(r["mw"] for r in inq if r["mw"] is not None)
        ai_mw = sum(r["mw"] for r in inq if r["mw"] is not None and r["ai"])
        if all_mw > 0:
            out[f"deals|chart_ai|{q}|share"] = round(1000 * ai_mw / all_mw) / 10
        out[f"deals|chart_ai|{q}|ai_mw"] = ai_mw
        out[f"deals|chart_ai|{q}|all_mw"] = all_mw
    for r in rows:
        if r["type"] in ("ppa", "offtake") and r["price"] is not None:
            out[f"deals|chart_price|{r['id']}|price"] = r["price"]
    by = {}
    for r in rows:
        for n in r["names"]:
            e = by.setdefault(n, [0.0, 0])
            if r["mw"] is not None:
                e[0] += r["mw"]
                e[1] += 1
    top = sorted(((n, e) for n, e in by.items() if e[1] > 0), key=lambda x: (-x[1][0], x[0]))[:10]
    for n, e in top:
        out[f"deals|chart_party|{n}|mw"] = e[0]
    return out


def page_figures(d):
    exe = shutil.which("node")
    if not exe:
        raise SystemExit("check_deals: node is not on this machine")
    std = {"event_id", "event_date", "status", "mw", "price", "source", "source_url"}
    rows = [{"event_id": r["event_id"], "event_date": r["event_date"], "status": r["status"], "mw": r["mw"],
             "price": r["price"], "currency": r.get("currency", ""), "parties": r.get("parties", ""), "source": r["source"],
             "source_url": r["source_url"], "extra": {k: v for k, v in r.items() if k not in std and v != ""}}
            for r in d.to_dict("records")]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(rows, f)
        tmp = f.name
    try:
        r = subprocess.run([exe, os.path.join("scripts", "deals-figures.mjs"), tmp], cwd=SITE, capture_output=True,
                           text=True, timeout=300)
    finally:
        os.remove(tmp)
    if r.returncode != 0:
        raise SystemExit(f"check_deals: the page's functions failed: {r.stderr[-1500:]}")
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
    ap.add_argument("--quiet", action="store_true", help="print the failures and the count only")
    args = ap.parse_args(argv)
    d, folded = deals_of(os.path.join(args.in_dir, "energy_deals.csv"))
    page, mine = page_figures(d), recompute(d, folded)
    lines, bad = compare(page, mine)
    for line in lines:
        if not args.quiet or not line.startswith("ok"):
            print(line)
    n = len(lines)
    print(f"check_deals: {n - bad} of {n} figures agree ({len(d)} deals, {len(folded)} folded)")
    return 1 if bad or n == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
