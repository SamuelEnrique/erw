"""Audit of /impact's datacenter, finding 5 (session 11404, chain 770, docs/reviews/impact-datacenter-model-audit-2026-11-28.md):
"Taxes, present value" adds the locality's taxes and the state's in one figure and never said so, nor that no cost of
public services is netted. A county's fiscal analyst needs the county's own part: the property tax is all local, the
income tax all the state's, the sales tax both. For Google's Virginia investment as the picker sets it, with Loudoun
County's 2026 rates and computer equipment schedule typed, a building's taxable share of 40 percent and 300 MW bought
all year, about 69 percent of the present value is local (property and the local part of the sales tax) and 29 percent
the state's (income and the state's part of the sales tax); the electricity tax's shares are not read.

1. Against the page's own files and model (passes on main): through site/lib/dcimpact.ts (run by Node), that case's
   taxes split as above; the model holds no cost of public services.
2. The fix on this branch, words only (fails on main): the line's hover says the total is state and local together,
   whose each part is, and that it is revenue, not a net fiscal effect. No figure moves; a split by level of government
   would add figures: Samuel's ruling."""
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
const x = D.dcDefaults(P, "va", { invest: 9000, brate: 0.875, erate: 4.15, eqv1: 60, eqstep: 15, eqfloor: 10, matshare: 40, mwh: 2628000 });
const r = D.dcRun(x, P);
const st = P.sales.states.va, local = st.avg_local_rate / (st.state_rate + st.avg_local_rate);
console.log(JSON.stringify({ taxes: r.pv.taxes, property: r.pv.property, sales: r.pv.sales, income: r.pv.income, elec: r.pv.elec, localShare: local,
  keys: Object.keys(r.pv).sort() }));
"""


class CountyShare(unittest.TestCase):
    def test_the_total_is_state_and_local_together(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL, DATA], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        local = r["property"] + r["sales"] * r["localShare"]
        state = r["income"] + r["sales"] * (1 - r["localShare"])
        self.assertAlmostEqual(r["taxes"], r["property"] + r["sales"] + r["income"] + r["elec"], delta=1e-6 * r["taxes"])
        self.assertAlmostEqual(local / r["taxes"], 0.692, places=2)
        self.assertAlmostEqual(state / r["taxes"], 0.292, places=2)
        self.assertNotIn("cost", " ".join(r["keys"]))

    def test_the_hover_says_whose_taxes_and_that_no_cost_is_netted(self):
        with open(os.path.join(ROOT, "site", "app", "impact", "Forecast.tsx"), encoding="utf-8") as f:
            t = f.read()
        self.assertIn("state and local together: the property tax is the locality's", t)
        self.assertIn("not a net fiscal effect", t)


if __name__ == "__main__":
    unittest.main()
