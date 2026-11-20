"""Audit of "What a battery earns", finding 9 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the cash flows
mix two kinds of dollars. Revenue and fixed O&M are flat in today's dollars (no inflation, the note's section 11.1), the
debt payment is a level payment fixed in money at an 8 percent interest rate, and the sum is discounted at 12 percent, a
rate quoted in money. Flat real flows need a real rate; a fixed money payment needs money flows.

1. The page's library (run by Node): from year 1 to year 2 the flow falls by the degradation alone (revenue and O&M are
   not escalated) while the debt payment is the same number every year.
2. Either consistent reading raises the default NPV (USD -697.80 per kW): money flows (revenue and O&M up with inflation,
   the debt fixed) at 12 percent, or real flows (the debt deflated) at the real rate, at 2 and 2.5 percent inflation:
   -658.13 and -650.15 at 2 percent, -647.10 and -636.85 at 2.5 percent.
It passes on main: it shows the fault. Nothing is written."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")
R = 81.4022  # the default case's last twelve months, USD per kW (the public dispatch file)


def page():
    js = ("const F = await import(process.argv[1]);"
          "const a = F.defaultsOf({ capex: 1110, fom: 22 });"
          f"const R = {R};"
          "const p = F.projection(a, R);"
          "console.log(JSON.stringify({ fl: F.flows(a, R), npv: F.npv(a.hurdle, F.flows(a, R)), debt: p.map((r) => r.debt), income: p.map((r) => r.income),"
          " a: { capex: a.capex, share: a.share, rate: a.rate, term: a.term, fom: a.fom, deg: a.deg, life: a.life, hurdle: a.hurdle } }));")
    out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


def consistent(a, infl):
    """(money flows at the money rate, real flows at the real rate), NPV per kW."""
    r, s, n = a["rate"] / 100, a["share"] / 100, min(a["term"], a["life"])
    ds = a["capex"] * s * r / (1 - (1 + r) ** -n)
    h = a["hurdle"] / 100
    real = (1 + h) / (1 + infl) - 1
    money = [-a["capex"] * (1 - s)] + [(R * (1 - a["deg"] / 100) ** (t - 1) - a["fom"]) * (1 + infl) ** (t - 1) - (ds if t <= n else 0)
                                       for t in range(1, a["life"] + 1)]
    flat = [-a["capex"] * (1 - s)] + [R * (1 - a["deg"] / 100) ** (t - 1) - a["fom"] - (ds / (1 + infl) ** t if t <= n else 0)
                                      for t in range(1, a["life"] + 1)]
    npv = lambda rate, fl: sum(f / (1 + rate) ** t for t, f in enumerate(fl))  # noqa: E731
    return npv(h, money), npv(real, flat)


class TwoKindsOfDollars(unittest.TestCase):
    def test_flat_revenue_against_a_fixed_money_payment(self):
        p = page()
        self.assertAlmostEqual(p["npv"], -697.80, places=1)
        self.assertEqual(len(set(round(d, 9) for d in p["debt"])), 1)              # the same payment every year
        self.assertAlmostEqual(p["income"][1] / p["income"][0], 1 - p["a"]["deg"] / 100, places=12)   # no escalation

    def test_either_consistent_reading_raises_the_npv(self):
        a = page()["a"]
        m2, r2 = consistent(a, 0.02)
        m25, r25 = consistent(a, 0.025)
        self.assertAlmostEqual(m2, -658.13, places=1)
        self.assertAlmostEqual(r2, -650.15, places=1)
        self.assertAlmostEqual(m25, -647.10, places=1)
        self.assertAlmostEqual(r25, -636.85, places=1)


if __name__ == "__main__":
    unittest.main()
