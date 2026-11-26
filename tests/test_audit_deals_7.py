"""Audit of the energy deal tracker, finding 3, the figure (session 10215, docs/reviews/deals-model-audit-2026-11-26.md).
A test only, not for landing: the fix would move figures a reader sees, so it waits for the owner's ruling (default: left
as it is).

The AI view sums the US dollars of the tagged deals of each group, of every kind and stage. The other choice: US dollars
summed only where the group is one kind of supply (the "kind of supply" grouping), and rumored talks left out of a sum.
Measured on the rows of 12 November 2026 (583 rows, 578 deals folded, 212 tagged): 15 of the 82 buyers' sums, 3 of the 4
grids' and 6 of the 7 quarters' add two kinds of supply or more (USD 1.13, 3.04 and 3.06 trillion would lose their sum);
rumored deals are USD 235 billion of the USD 3.06 trillion (2.82 trillion without them); the register's doubtful pairs
count USD 55 billion twice.

1. Through the page's library (site/lib/dealsai.ts, run by Node): today a buyer's sum adds a capital deal and a compute
   contract, rumored or not. Passes on main (the rule as it is).
2. On the warehouse's rows, where this checkout holds them (warehouse/output/energy_deals.csv, else skipped): the tagged
   deals' rumored US dollars are more than nothing and some buyer's sum adds two kinds of supply. Passes on main; it says
   how far the other choice would move the figures."""
import csv
import json
import os
import re
import subprocess
import unittest
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dealsai.ts").replace("\\", "/")
CSV = os.environ.get("ERW_DEALS_CSV") or os.path.join(ROOT, "warehouse", "output", "energy_deals.csv")
JS = """
const A = await import(%s);
const d = (id, kind, status, dollars) => ({ id, date: "2026-02-10", month: "2026-02", year: "2026", type: "", group: "other", status, buyer: "B", seller: "S",
  others: [], names: ["B", "S"], asset: "", technology: "", state: "", country: "", grid: "", mw: null, mwh: null, dollars, price: null, priceOther: null,
  termYears: null, ai: true, storage: false, kinds: [], source: "", links: [], folded: [], kind, buyerName: "B", sellerName: "S", aiBasis: "" });
const cells = A.aiCells([d("a", "capital", "rumored", 40e9), d("b", "compute_capacity", "signed", 10e9)], "buyer");
console.log(JSON.stringify(cells.map((c) => [c.value, c.usd])));
""" % json.dumps(LIB)
FORM = {"ppa": "ppa", "offtake": "offtake", "project_finance": "project_finance", "m_and_a": "m_and_a", "debt": "capital",
        "equity_raise": "capital", "tax_equity": "capital", "joint_venture": "capital", "fuel_supply": "fuel_supply",
        "behind_the_meter": "behind_the_meter", "nuclear_restart": "nuclear_restart_uprate", "smr": "smr"}


def supply(r):
    t = (r.get("technology") or "").lower()
    k = r.get("kind") or FORM.get(r.get("deal_type", ""), "other")
    if k in ("nuclear_restart_uprate", "smr") or re.search(r"nuclear|reactor|smr|fusion", t):
        return "nuclear"
    if k == "gas_buildout" or re.search(r"\bgas\b|lng|turbine", t):
        return "gas"
    if k == "storage" or re.search(r"solar|wind|batter|storage|hydro|geotherm|renewable", t):
        return "renewables_storage"
    if k == "compute_capacity":
        return "compute"
    if k in ("ppa", "offtake", "behind_the_meter"):
        return "grid"
    if k in ("capital", "m_and_a", "project_finance"):
        return "capital"
    return "other"


class TheDollarSumsByOneKind(unittest.TestCase):
    def test_today_a_buyers_sum_adds_kinds_and_stages(self):
        out = subprocess.run(["node", "--input-type=module"], input=JS, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout.strip().splitlines()[-1]), [["B", 50e9]])

    @unittest.skipUnless(os.path.exists(CSV), "the warehouse's energy_deals.csv is not in this checkout (held; read on the data machine)")
    def test_on_the_rows_the_other_choice_would_move_the_sums(self):
        with open(CSV, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
        ai = [r for r in rows if (r.get("ai_power") or "").lower() == "true" and (r.get("dollars") or r.get("usd"))]
        rumored = sum(float(r.get("dollars") or r.get("usd")) for r in ai if r.get("status") == "rumored")
        kinds = defaultdict(set)
        for r in ai:
            kinds[r.get("buyer_name") or r.get("buyer") or r.get("seller_name") or r.get("seller") or ""].add(supply(r))
        mixed = sum(1 for v in kinds.values() if len(v) > 1)
        print(f"tagged deals stating USD {len(ai)}; rumored USD {rumored:,.0f}; buyers whose sum adds two kinds or more {mixed} of {len(kinds)}")
        self.assertGreater(rumored, 0)
        self.assertGreater(mixed, 0)


if __name__ == "__main__":
    unittest.main()
