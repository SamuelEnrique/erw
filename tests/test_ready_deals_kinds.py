"""Session 11408 (chain 770, part C): the deal tracker's AI view, the other choice of the deals audit's finding 3
(docs/reviews/deals-model-audit-2026-11-26.md; its test branch wip/audit-deals-7, carried over here and turned to assert
the new rule). Not for landing until the owner rules.

The rule on this branch: US dollars are summed only grouped by the kind of supply, and a rumored or cancelled deal's
dollars are never added; by buyer, grid or quarter no dollar sum is drawn. Measured on the warehouse's rows (583 rows,
578 deals folded, 212 tagged): the seven kinds' dollars USD 3,059,388,000,000 on origin/main, 2,824,038,000,000 here;
82 buyer cells with a dollar sum on main, none here.

1. Through the page's library (site/lib/dealsai.ts, run by Node): a buyer's cell has no dollar sum, a rumored raise is
   not added by the kind of supply, a signed contract is.
2. The view draws the dollar column only by the kind of supply."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dealsai.ts").replace("\\", "/")
JS = """
const A = await import(%s);
const d = (id, kind, status, dollars) => ({ id, date: "2026-02-10", month: "2026-02", year: "2026", type: "", group: "other", status, buyer: "B", seller: "S",
  others: [], names: ["B", "S"], asset: "", technology: "", state: "", country: "", grid: "", mw: null, mwh: null, dollars, price: null, priceOther: null,
  termYears: null, ai: true, storage: false, kinds: [], source: "", links: [], folded: [], kind, buyerName: "B", sellerName: "S", aiBasis: "" });
const ds = [d("a", "capital", "rumored", 40e9), d("b", "compute_capacity", "signed", 10e9), d("c", "compute_capacity", "cancelled", 5e9)];
const cells = (dim) => A.aiCells(ds, dim).map((c) => [c.value, c.usd, c.withUsd]);
console.log(JSON.stringify({ buyer: cells("buyer"), supply: cells("supply"), quarter: cells("quarter"), dims: A.USD_DIMENSIONS }));
""" % json.dumps(LIB)


def node():
    out = subprocess.run(["node", "--input-type=module"], input=JS, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout.strip().splitlines()[-1])


class TheDollarSumsByOneKind(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = node()

    def test_only_the_kind_of_supply_sums_dollars(self):
        self.assertEqual(self.r["dims"], ["supply"])
        self.assertEqual(self.r["buyer"], [["B", None, 0]])
        self.assertEqual(self.r["quarter"], [["2026-Q1", None, 0]])

    def test_rumored_and_cancelled_dollars_are_not_added(self):
        self.assertEqual(sorted(self.r["supply"]), [["capital", None, 0], ["compute", 10e9, 1]])

    def test_the_view_draws_the_dollar_column_by_kind_only(self):
        with open(os.path.join(ROOT, "site", "app", "deals", "ai", "view.tsx"), encoding="utf-8") as f:
            view = f.read()
        self.assertIn("const usdShown = USD_DIMENSIONS.includes(by);", view)
        self.assertIn('...(usdShown ? ["US dollars stated"] : [])', view)
        self.assertIn("{usdShown ? <td", view)
        self.assertNotIn(chr(0x2014), view)


if __name__ == "__main__":
    unittest.main()
