"""Audit of "What a generator earns", finding 1 (session 9841, docs/reviews/generator-model-audit-2026-11-20.md): the NPV
to equity holds no income tax and no depreciation (site/lib/seller/finance.ts, flows), and is discounted at a cost of
equity, a return after tax. The battery page's finding 8 (session 9840) on the generator page's default case.

1. The page's library (run by Node), the default case (ERCOT solar, hub average; R = 59.8523 per kW from the public hourly
   file): no credit by default, and NPV at 12 percent is USD -766.62 per kW.
2. The same case after federal tax (21 percent; 5-year MACRS, half-year convention; interest deductible on the level loan's
   schedule; losses used as they arise), every other figure the page's: USD -526.10 per kW.
It passes on main: it shows the fault. Nothing is written."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "seller", "finance.ts").replace("\\", "/")
R = 59.8523
MACRS5 = [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]


def page():
    js = ("const F = await import(process.argv[1]);"
          "const a = F.defaultsOf({ capex: 1375, fom: 12.5, life: 35, deg: 0.7 });"
          f"const R = {R};"
          "console.log(JSON.stringify({ a, npv: F.npv(a.hurdle, F.flows(a, R)), debt: F.debtService(a) }));")
    out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


def after_tax(a, debt, tax=0.21):
    rate, share, n = a["rate"] / 100, a["share"] / 100, min(a["term"], a["life"])
    bal = a["capex"] * share
    fl = [-a["capex"] * (1 - share)]
    for t in range(1, a["life"] + 1):
        rev = R * (1 - a["deg"] / 100) ** (t - 1)
        interest = bal * rate if t <= n else 0.0
        bal -= (debt - interest) if t <= n else 0.0
        dep = a["capex"] * MACRS5[t - 1] if t <= len(MACRS5) else 0.0
        fl.append(rev - a["fom"] - (debt if t <= n else 0.0) - tax * (rev - a["fom"] - interest - dep))
    return sum(f / (1 + a["hurdle"] / 100) ** t for t, f in enumerate(fl))


class GeneratorNoTax(unittest.TestCase):
    def test_no_tax_in_the_flows(self):
        p = page()
        self.assertEqual((p["a"]["itc"], p["a"]["ptc"], p["a"]["hurdle"]), (0, 0, 12))
        self.assertAlmostEqual(p["debt"] * 100000, 7078769, delta=1)
        self.assertAlmostEqual(p["npv"], -766.62, places=1)

    def test_after_federal_tax(self):
        p = page()
        self.assertAlmostEqual(after_tax(p["a"], p["debt"]), -526.10, places=1)


if __name__ == "__main__":
    unittest.main()
