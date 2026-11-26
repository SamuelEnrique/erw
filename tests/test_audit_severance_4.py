"""Audit of the severance tool, finding 4 (session 10207, docs/reviews/severance-model-audit-2026-11-26.md): the
calculator's lead said "Local taxes, county levies and federal royalties are not here", yet New Mexico's ad valorem
production tax, levied at the rate of the production unit's county district (35 rows of TRD's table), is a base line of
the total when a district is chosen, and is left out by default.

1. Through the page's library (run by Node): the New Mexico oil total with a district less the total without one is the
   district's rate times the taxable value, and at the median district it is 13.6 to 14.9 percent of the larger total.
   Passes on main.
2. The fix on this branch, words only: the lead names the exception, and that a Texas or Louisiana total holds no local
   tax; the method note follows. Fails on main."""
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
const out = {};
for (const [p, price] of [["oil", 102.07], ["gas", 2.99]]) {
  const list = rules.states.NM.products[p].base.find((b) => b.rate === "district").districts.list.map((d) => d.rate).sort((a, b) => a - b);
  const med = list[Math.floor(list.length / 2)];
  const x = { state: "NM", product: p, volume: 1000, price };
  const none = compute(rules, { ...x, adval: 0 }), with_ = compute(rules, { ...x, adval: Math.round(med * 1e6) / 1e4 });
  out[p] = { none: none.baseTotal, med: with_.baseTotal, taxable: with_.taxable, rate: med, n: list.length };
}
console.log(JSON.stringify(out));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class NewMexicoDistrictIsALocalLevy(unittest.TestCase):
    def test_the_district_is_a_line_of_the_total(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, RULES], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        for p, lo, hi in (("oil", 14.8, 14.95), ("gas", 13.5, 13.65)):
            self.assertEqual(r[p]["n"], 35)
            self.assertAlmostEqual(r[p]["med"] - r[p]["none"], r[p]["rate"] * r[p]["taxable"], places=6)
            share = (r[p]["med"] - r[p]["none"]) / r[p]["med"] * 100
            self.assertTrue(lo < share < hi, (p, share))

    def test_the_lead_names_the_exception(self):
        page = src("site", "app", "severance", "page.tsx")
        self.assertNotIn("Local taxes, county levies and", page)
        self.assertIn("New Mexico&apos;s ad valorem production tax, levied at the rate of the production unit&apos;s county district, is in", page)
        self.assertIn("A Texas or Louisiana total here holds no local tax.", page)
        self.assertIn("**A local levy in the total.**", src("docs", "methods", "severance.md"))


if __name__ == "__main__":
    unittest.main()
