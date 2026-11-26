"""Audit of the severance tool, finding 5 (session 10207, docs/reviews/severance-model-audit-2026-11-26.md): the decisions
fold said "Texas condensate owes 4.6 percent with no floor per barrel". The rules file's own quote of Sec. 201.055(b)
taxes condensate "at the same rate as the rate of the tax imposed on oil by Section 202.052", and Sec. 202.052(a)'s rate
is 4.6 percent or 4.6 cents a barrel, whichever is greater. The calculator's choice (no floor for condensate) is a
choice; it acts only below USD 1 a barrel.

1. Through the page's library (run by Node): at USD 0.50 a barrel, 1,000 bbl of Texas condensate owe USD 23.00 and of oil
   USD 46.00; at USD 1 and above the two are equal. Passes on main.
2. The fix on this branch, words only: decision 3 and the method note say the floor is left out by choice. Fails on main."""
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
const t = (product, price) => compute(rules, { state: "TX", product, volume: 1000, price }).baseTotal;
console.log(JSON.stringify({ c50: t("condensate", 0.5), o50: t("oil", 0.5), c100: t("condensate", 1), o100: t("oil", 1), c102: t("condensate", 102.07), o102: t("oil", 102.07) }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TexasCondensateFloor(unittest.TestCase):
    def test_the_cited_section_carries_the_floor_the_code_leaves_out(self):
        tx = json.loads(src("site", "data", "severance_rules.json"))["states"]["TX"]["products"]
        self.assertIn("at the same rate as the rate of the tax imposed on oil by Section 202.052", tx["condensate"]["base"][0]["code"]["quote"])
        self.assertIn("4.6 cents for each barrel", tx["oil"]["base"][0]["code"]["quote"])
        self.assertNotIn("min_per_unit", tx["condensate"]["base"][0])
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, RULES], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertAlmostEqual(r["c50"], 23.0, places=9)
        self.assertAlmostEqual(r["o50"], 46.0, places=9)
        self.assertAlmostEqual(r["c100"], r["o100"], places=9)
        self.assertAlmostEqual(r["c102"], r["o102"], places=9)

    def test_the_fold_says_it_is_a_choice(self):
        d = src("site", "app", "severance", "Decisions.tsx")
        self.assertNotIn("Texas condensate owes 4.6 percent with no floor per barrel.", d)
        self.assertIn("though Sec. 201.055(b) taxes it at the oil rate, which has the floor. The floor acts only below USD 1 a barrel.", d)
        self.assertIn("The section's own words carry the floor, so this is the page's choice, not the law", src("docs", "methods", "severance.md"))


if __name__ == "__main__":
    unittest.main()
