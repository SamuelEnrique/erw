"""Audit of /impact's datacenter, finding 1 (session 11404, chain 770, docs/reviews/impact-datacenter-model-audit-2026-11-28.md):
Texas, the page's default state, and Tennessee exempt a qualifying datacenter's equipment from sales and use tax, and the
ERW's own ground names both as unread (docs/reviews/impact-datacenter-sources-2026-11-26.md: "Texas's data center
exemption (Tax Code 151.359) stays unread", "Tennessee's exemption stays unread"). The page said only "No datacenter
sales tax exemption of this state has been read: the sales tax is before exemptions" in the field's hover, and the A and
B table's "Sales and use tax" cell, whose hover says "paid, after the state's datacenter exemption where the project
meets its thresholds", printed the tax before any exemption with no mark. Every dollar of the default Texas page's
taxes is that sales tax (present value USD 1.58 billion; USD 2.68 billion over the life), and Tennessee's likewise.

1. Against the page's own files and model (passes on main): no rule is held for Texas or Tennessee; the ground names both
   as unread; through site/lib/dcimpact.ts (run by Node) the default Texas and Tennessee runs' taxes are all sales tax,
   before equal to paid.
2. The fix on this branch, words only (fails on main): the field's hover names Texas's statute and Tennessee's exemption
   as unread (site/lib/dcui.ts, DC_UNREAD_EXEMPTION); the sales cell says "before any exemption" wherever no rule is
   held or the rule is words only (site/app/impact/Forecast.tsx); the other-states chart says the two bars are before
   an exemption in statute (site/app/impact/Datacenter.tsx). No figure moves."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = "file:///" + os.path.join(ROOT, "site", "lib", "dcimpact.ts").replace("\\", "/")
DATA = os.path.join(ROOT, "site", "data", "forecast")
JS = """
const D = await import(process.argv[1]);
const fs = await import("node:fs");
const data = (n) => JSON.parse(fs.readFileSync(process.argv[2] + "/" + n, "utf-8"));
const A = data("datacenter_announced.json"), W = data("datacenter_wages.json");
const P = { announced: { defaults: A.defaults }, rules: data("datacenter_rules.json"), wages: W, sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
const out = {};
for (const st of ["tx", "tn"]) { const r = D.dcRun(D.dcDefaults(P, st), P); out[st] = { taxes: r.pv.taxes, sales: r.pv.sales, before: r.sums.salesbefore, paid: r.sums.sales, held: r.exemption.held }; }
console.log(JSON.stringify(out));
"""


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class UnreadExemptions(unittest.TestCase):
    def test_no_rule_held_and_the_ground_names_both(self):
        rules = json.loads(read("site", "data", "forecast", "datacenter_rules.json"))["states"]
        for st in ("tx", "tn"):
            self.assertNotIn("sales_exemption", rules.get(st, {}), st)
        ground = read("docs", "reviews", "impact-datacenter-sources-2026-11-26.md")
        self.assertIn("Texas's data center exemption (Tax Code 151.359) stays unread", ground)
        self.assertIn("Tennessee's exemption stays unread", ground)

    def test_the_default_taxes_are_all_sales_tax_before_exemption(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL, DATA], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        for st in ("tx", "tn"):
            self.assertFalse(r[st]["held"])
            self.assertAlmostEqual(r[st]["sales"], r[st]["taxes"], delta=1e-6 * r[st]["taxes"])
            self.assertEqual(r[st]["before"], r[st]["paid"])
        self.assertAlmostEqual(r["tx"]["taxes"], 1577476774.40, delta=1.0)
        self.assertAlmostEqual(r["tx"]["paid"], 2684352000.0, delta=1.0)

    def test_the_page_says_the_tax_is_before_an_unread_exemption(self):
        ui = read("site", "lib", "dcui.ts")
        self.assertIn("Tax Code 151.359", ui)
        self.assertIn("DC_UNREAD_EXEMPTION[s]", ui)
        f = read("site", "app", "impact", "Forecast.tsx")
        self.assertIn("before any exemption", f)
        self.assertIn("data-before-exemption", f)
        d = read("site", "app", "impact", "Datacenter.tsx")
        self.assertIn("exists in statute but could not be read", d)
        self.assertIn("Texas and Tennessee have datacenter exemptions in statute", d)


if __name__ == "__main__":
    unittest.main()
