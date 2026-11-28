"""Audit of /impact's datacenter, finding 2 (session 11404, chain 770, docs/reviews/impact-datacenter-model-audit-2026-11-28.md):
the on-site-only totals did not say what they leave out. Supply chain and induced effects are held only for Virginia,
Georgia and Minnesota (their own published studies). In the other 48 states the A and B table's construction and
operating jobs, their earnings, the income tax and the earnings' present value are on site only, and the cell said
nothing (only the row's hover, "elsewhere on site only"); the page's lead said "Jobs, earnings and output are NLR's JEDI
models read for every state" and "Gross effects of an input-output model", which no datacenter figure is. Set beside a
Virginia scenario in the same table, the same project shows 3.4 times the operating jobs for no reason but the state's
study. The "Taxes, present value" cell named the property and electricity taxes it leaves out, not the building's sales
tax (its taxable share is not given by default) nor the income tax of supply chain and induced jobs.

1. Against the page's own files and model (passes on main): through site/lib/dcimpact.ts (run by Node) AWS's Madison
   County project (Mississippi, the row the picker sets) has on-site jobs equal to its total; Virginia's ratios give 3.39
   operating jobs per on-site job; the Mississippi project with Virginia's ratios has 81 percent more taxes in present
   value; the Virginia default with a building's taxable share of 40 percent has 9.8 percent more.
2. The fix on this branch, words only (fails on main): the cells say "on site only" where no study is held, the total
   names the building's sales tax and the supply chain and induced income tax among what it leaves out, and the lead
   says what a datacenter's figures rest on, and the source line names its sources. No figure moves."""
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
const A = data("datacenter_announced.json");
const P = { announced: { defaults: A.defaults }, rules: data("datacenter_rules.json"), wages: data("datacenter_wages.json"), sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
const idx = P.deflator.index;
const row = A.rows.find((r) => r.id === "ms_aws_madison_2024");
const set = { invest: Math.round(row.investment.value * idx["2025"] / idx[String(row.investment.year)] / 1e4) / 100, perm: row.permanent_jobs.value };
const ms = D.dcRun(D.dcDefaults(P, "ms", set), P);
const Q = JSON.parse(JSON.stringify(P)); Q.rules.multipliers.ms = P.rules.multipliers.va;
const msva = D.dcRun(D.dcDefaults(Q, "ms", set), Q);
const va = D.dcRun(D.dcDefaults(P, "va"), P), va40 = D.dcRun(D.dcDefaults(P, "va", { matshare: 40 }), P);
console.log(JSON.stringify({ invest: set.invest, chain: ms.chain.held, on: ms.operations.jobs.onsite, tot: ms.operations.jobs.total,
  vaRatio: va.operations.jobs.total / va.operations.jobs.onsite, ms: ms.pv.taxes, msva: msva.pv.taxes, va: va.pv.taxes, va40: va40.pv.taxes,
  held: Object.keys(P.rules.multipliers).sort() }));
"""


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class OnSiteOnly(unittest.TestCase):
    def test_the_totals_are_on_site_only_outside_three_states(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL, DATA], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        self.assertEqual(r["held"], ["ga", "mn", "va"])
        self.assertAlmostEqual(r["invest"], 10263.83, places=2)
        self.assertFalse(r["chain"])
        self.assertEqual(r["on"], r["tot"])
        self.assertAlmostEqual(r["vaRatio"], 3.3885, places=3)
        self.assertGreater(r["msva"] / r["ms"], 1.8)       # +81.2 percent
        self.assertGreater(r["va40"] / r["va"], 1.09)      # +9.8 percent

    def test_the_page_says_on_site_only_and_what_the_total_leaves_out(self):
        f = read("site", "app", "impact", "Forecast.tsx")
        self.assertIn("on site only", f)
        self.assertIn("data-onsite-only", f)
        self.assertIn("the building's sales tax", f)
        self.assertIn("supply chain and induced income tax", f)
        p = read("site", "app", "impact", "page.tsx")
        self.assertNotIn("Jobs, earnings and output are NLR&apos;s JEDI models read for every state", p)
        self.assertIn("which no JEDI model covers", p)
        self.assertIn("Virginia, Georgia and Minnesota", p)
        # the source line named only the plants' sources; it now names a datacenter's
        self.assertIn("A datacenter&apos;s figures rest on other sources", p)
        self.assertIn("Census County Business Patterns 2023", p)


if __name__ == "__main__":
    unittest.main()
