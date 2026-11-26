"""Audit of the severance tool, finding 2 (session 10207, docs/reviews/severance-model-audit-2026-11-26.md): Louisiana
condensate takes the trucking, barging and pipeline deduction (site/data/severance_rules.json, LA value_deduction,
products oil and condensate), though the deduction's own quote names oil and the condensate rule's quote taxes condensate
on "gross value". A fix (no deduction for condensate) would move a figure a reader sees once a transport fee is typed,
so it is not made: this test shows the finding and is not for landing. For Samuel's ruling, default "left as it is".

Measured: 1,000 bbl at USD 102.07 with USD 2 a barrel, USD 12,508.75 against 12,758.75 (-250.00, -1.96 percent)."""
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
const x = { state: "LA", product: "condensate", volume: 1000, price: 102.07 };
console.log(JSON.stringify({ none: compute(rules, { ...x, transport: 0 }).baseTotal, two: compute(rules, { ...x, transport: 2 }).baseTotal }));
"""


class LouisianaCondensateDeduction(unittest.TestCase):
    def setUp(self):
        with open(RULES, encoding="utf-8") as f:
            self.la = json.load(f)["states"]["LA"]

    def test_the_cited_texts(self):
        vd = self.la["value_deduction"]
        self.assertEqual(vd["products"], ["oil", "condensate"])
        self.assertIn("the value of oil shall be", vd["quote"])
        self.assertNotIn("condensate", vd["quote"])                     # the deduction's passage names oil only
        cond = self.la["products"]["condensate"]["base"][0]
        self.assertIn("twelve and one-half percent of gross value", cond["quote"])

    def test_the_code_deducts_on_condensate(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, RULES], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertAlmostEqual(r["none"], 12758.75, places=6)
        self.assertAlmostEqual(r["none"] - r["two"], 250.0, places=6)    # 12.5 percent of USD 2 x 1,000 bbl
        self.assertAlmostEqual((r["two"] - r["none"]) / r["none"] * 100, -1.9594, places=3)


if __name__ == "__main__":
    unittest.main()
