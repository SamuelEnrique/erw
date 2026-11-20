"""Audit of "What a battery earns", finding 8 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the NPV to
equity is computed with no tax at all (site/lib/battery/finance.ts, flows): no investment tax credit by default, no
depreciation, no income tax, and it is discounted at a cost of equity, which is a return after tax.

1. The page's library (run by Node): the default credit is 0, and a 30 percent credit raises NPV by exactly 30 percent of
   the capital cost, USD 333 per kW (no basis cut, no tax): the flows hold no tax term.
2. The same default case after federal tax (21 percent, 5-year MACRS with the half-year convention, the basis cut by half
   the credit, interest deductible, losses used as they arise), every other figure the page's: USD -578.85 per kW with
   no credit, -271.66 with the 30 percent credit, against the page's -697.80.
It passes on main: it shows the fault. Nothing is written."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")
R = 81.4022  # the default case's last twelve months, USD per kW (the public dispatch file)
MACRS5 = [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]


def page():
    js = ("const F = await import(process.argv[1]);"
          "const a = F.defaultsOf({ capex: 1110, fom: 22 });"
          f"const R = {R};"
          "console.log(JSON.stringify({ itc: a.itc, base: F.npv(a.hurdle, F.flows(a, R)), credit: F.npv(a.hurdle, F.flows({ ...a, itc: 30 }, R)),"
          " a: { capex: a.capex, share: a.share, rate: a.rate, term: a.term, fom: a.fom, deg: a.deg, life: a.life, hurdle: a.hurdle } }));")
    out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


def after_tax_npv(a, itc, tax=0.21):
    rate, share, n = a["rate"] / 100, a["share"] / 100, min(a["term"], a["life"])
    ds = a["capex"] * share * rate / (1 - (1 + rate) ** -n)
    bal, basis = a["capex"] * share, a["capex"] * (1 - itc / 2)
    fl = [-a["capex"] * (1 - share) + a["capex"] * itc]
    for t in range(1, a["life"] + 1):
        rev = R * (1 - a["deg"] / 100) ** (t - 1)
        interest = bal * rate if t <= n else 0.0
        bal -= (ds - interest) if t <= n else 0.0
        dep = basis * MACRS5[t - 1] if t <= len(MACRS5) else 0.0
        fl.append(rev - a["fom"] - (ds if t <= n else 0.0) - tax * (rev - a["fom"] - interest - dep))
    return sum(f / (1 + a["hurdle"] / 100) ** t for t, f in enumerate(fl))


class NoTax(unittest.TestCase):
    def test_the_page_holds_no_tax_and_no_credit(self):
        p = page()
        self.assertEqual(p["itc"], 0)
        self.assertAlmostEqual(p["base"], -697.80, places=1)
        self.assertAlmostEqual(p["credit"] - p["base"], 0.30 * 1110, places=6)   # the credit alone, untaxed

    def test_after_tax_the_npv_is_higher(self):
        a = page()["a"]
        self.assertAlmostEqual(after_tax_npv(a, 0.0), -578.85, places=1)
        self.assertAlmostEqual(after_tax_npv(a, 0.30), -271.66, places=1)


if __name__ == "__main__":
    unittest.main()
