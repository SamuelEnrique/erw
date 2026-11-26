"""Audit of the severance tool, finding 1 (session 10207, docs/reviews/severance-model-audit-2026-11-26.md): under the
calculator's table Louisiana's note says oil and condensate are taxed on "the higher of the first purchaser's gross
receipts less trucking, barging and pipeline fees, or the posted field price". The code (site/lib/severance.ts) takes the
receipts less the fees typed and never the posted price, which the page does not hold.

1. Through the page's library (run by Node): Louisiana oil with a transport fee equal to its price owes USD 0.00, and
   with USD 2 a barrel exactly 12.5 percent of the price less 2: no floor acts. Passes on main.
2. The fix on this branch, words only: the decisions fold (decision 9) and the method note say the floor is not held and
   not applied. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "severance.ts").replace("\\", "/")
RULES = os.path.join(ROOT, "site", "data", "severance_rules.json")
JS = """
const { compute } = await import(process.argv[1]);
const fs = await import("node:fs");
const rules = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const x = { state: "LA", product: "oil", volume: 1000, price: 102.07, variant: "la_oil_pre2025" };
const out = {
  none: compute(rules, { ...x, transport: 0 }).baseTotal,
  two: compute(rules, { ...x, transport: 2 }).baseTotal,
  all: compute(rules, { ...x, transport: 102.07 }).baseTotal,
};
console.log(JSON.stringify(out));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class LouisianaFloorNotApplied(unittest.TestCase):
    def test_no_posted_price_floor_acts(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, RULES], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertAlmostEqual(r["none"], 12758.75, places=6)
        self.assertAlmostEqual(r["two"], 0.125 * 1000 * (102.07 - 2), places=6)
        self.assertEqual(r["all"], 0)                                   # the value typed away entirely: no floor
        la = json.loads(src("site", "data", "severance_rules.json"))["states"]["LA"]
        self.assertIn("or the posted field price", la["basis_note"])  # the rule the page prints under the table
        self.assertNotIn("posted", src("site", "lib", "severance.ts").lower())

    def test_the_page_says_the_floor_is_not_applied(self):
        self.assertIn("Louisiana's floor, the posted field price, is not held, so its value here is the price typed less the fees typed, which can be below the value the state taxes.",
                      src("site", "app", "severance", "Decisions.tsx"))
        self.assertIn("no posted price is held, so the floor is not applied and the decisions fold says so", src("docs", "methods", "severance.md"))


if __name__ == "__main__":
    unittest.main()
