"""Audit of "What a generator earns", finding 2 (session 9841, docs/reviews/generator-model-audit-2026-11-20.md): revenue and
fixed O&M are flat in today's dollars, the debt payment is a level payment fixed in money over 35 years, and the sum is
discounted at 12 percent, a money rate (site/lib/seller/finance.ts, flows and npv). The battery page's finding 9.

1. The page's library (run by Node), the default case (ERCOT solar): the debt payment is one number in all 35 years,
   and year 2's income is year 1's times (1 - 0.007): no inflation.
2. Money flows (revenue and O&M rising with inflation, the debt fixed) at 12 percent: USD -706.90 per kW at 2 percent
   inflation and -689.20 at 2.5, against the page's -766.62.
It passes on main: it shows the fault. Nothing is written."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "seller", "finance.ts").replace("\\", "/")
R = 59.8523


def page():
    js = ("const F = await import(process.argv[1]);"
          "const a = F.defaultsOf({ capex: 1375, fom: 12.5, life: 35, deg: 0.7 });"
          f"const R = {R};"
          "const inc = [1, 2].map((t) => F.incomeInYear(a, R, t));"
          "console.log(JSON.stringify({ a, debt: F.debtService(a), inc, fl: F.flows(a, R), npv: F.npv(a.hurdle, F.flows(a, R)) }));")
    out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


class GeneratorTwoKindsOfDollars(unittest.TestCase):
    def test_flat_flows_and_a_fixed_payment(self):
        p = page()
        a = p["a"]
        self.assertAlmostEqual(p["inc"][1] / p["inc"][0], 1 - a["deg"] / 100, places=12)
        for t in range(1, a["life"] + 1):                     # flow + debt = income - fom: the same payment every year
            self.assertAlmostEqual(p["fl"][t] + p["debt"], R * (1 - a["deg"] / 100) ** (t - 1) - a["fom"], places=9)
        self.assertAlmostEqual(p["npv"], -766.62, places=1)

    def test_money_flows_at_the_money_rate(self):
        p = page()
        a, debt = p["a"], p["debt"]
        for infl, want in ((0.02, -706.90), (0.025, -689.20)):
            fl = [-a["capex"] * (1 - a["share"] / 100)] + [(R * (1 - a["deg"] / 100) ** (t - 1) - a["fom"]) * (1 + infl) ** (t - 1) - debt
                                                           for t in range(1, a["life"] + 1)]
            self.assertAlmostEqual(sum(f / 1.12 ** t for t, f in enumerate(fl)), want, places=1)


if __name__ == "__main__":
    unittest.main()
