"""Ready branch for the severance tool (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.3, the
severance tool; audit docs/reviews/severance-model-audit-2026-11-26.md, finding 2, test wip/audit-severance-2, carried
over and turned). Not the default: it waits for Samuel's ruling.

The other choice: Louisiana condensate without the trucking, barging and pipeline deduction, as the statute's "gross
value" reads (site/data/severance_rules.json, LA value_deduction products oil only). Measured through the page's own
library: 1,000 bbl at USD 102.07 with USD 2 a barrel owe USD 12,508.75 on main and 12,758.75 here (+250.00); with no
fee typed (the default) both owe 12,758.75. Louisiana oil keeps its deduction."""
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
const c = { state: "LA", product: "condensate", volume: 1000, price: 102.07 };
const o = { ...c, product: "oil" };
console.log(JSON.stringify({ none: compute(rules, { ...c, transport: 0 }).baseTotal, two: compute(rules, { ...c, transport: 2 }).baseTotal,
  oilNone: compute(rules, { ...o, transport: 0 }).baseTotal, oilTwo: compute(rules, { ...o, transport: 2 }).baseTotal }));
"""


class LouisianaCondensateOnGrossValue(unittest.TestCase):
    def setUp(self):
        with open(RULES, encoding="utf-8") as f:
            self.la = json.load(f)["states"]["LA"]

    def test_the_rules(self):
        self.assertEqual(self.la["value_deduction"]["products"], ["oil"])
        self.assertIn("condensate on its gross value at the time and place of severance (La. R.S. 47:633), with no deduction",
                      self.la["basis_note"])
        self.assertIn("or the posted field price", self.la["basis_note"])
        self.assertIn("twelve and one-half percent of gross value", self.la["products"]["condensate"]["base"][0]["quote"])

    def test_the_words(self):
        with open(os.path.join(ROOT, "site", "app", "severance", "Decisions.tsx"), encoding="utf-8") as f:
            self.assertIn("fees on oil (condensate is taxed on its gross value, with no deduction)", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "severance.md"), encoding="utf-8") as f:
            self.assertIn("Louisiana condensate: gross, with no deduction", f.read())

    def test_the_figures(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, RULES], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertAlmostEqual(r["none"], 12758.75, places=6)
        self.assertAlmostEqual(r["two"], 12758.75, places=6)               # no deduction on condensate
        self.assertAlmostEqual(r["oilNone"] - r["oilTwo"], 250.0, places=6)  # oil keeps it: 12.5 percent of USD 2 x 1,000 bbl


if __name__ == "__main__":
    unittest.main()
