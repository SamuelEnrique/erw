"""Session 11408, readied for the owner's ruling (weekend page part 3.4, battery choice 9; the battery audit of 20
November, finding 9, docs/reviews/battery-model-audit-2026-11-20.md, carried from wip/audit-battery-9): one kind of
dollar in the NPV. The debt payment is fixed in money and the hurdle is a money rate, so revenue and fixed O&M rise
with inflation (2 percent a year, the low end of the audit's 2 to 2.5).

Through site/lib/battery/finance.ts (run by Node) at the headline 80.4016 per kW: the debt payment is one number every
year, year 1's revenue is the headline, year t's is the headline x 0.974^(t-1) x 1.02^(t-1), and NPV equals an
independent mirror: -665.32 per kW (it was -704.23)."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")
R = 80.4016


def mirror(a, infl=0.02):
    rate, share, n = a["rate"] / 100, a["share"] / 100, min(a["term"], a["life"])
    ds = a["capex"] * share * rate / (1 - (1 + rate) ** -n)
    fl = [-a["capex"] * (1 - share)]
    for t in range(1, a["life"] + 1):
        e = (1 + infl) ** (t - 1)
        fl.append(R * (1 - a["deg"] / 100) ** (t - 1) * e - a["fom"] * e - (ds if t <= n else 0.0))
    return sum(f / (1 + a["hurdle"] / 100) ** t for t, f in enumerate(fl))


class OneKindOfDollar(unittest.TestCase):
    def test_money_flows(self):
        js = ("const F = await import(process.argv[1]);"
              "const a = F.defaultsOf({ capex: 1110, fom: 22 });"
              f"const R = {R}; const fl = F.flows(a, R);"
              "console.log(JSON.stringify({ a, infl: F.INFLATION, npv: F.npv(a.hurdle, fl), r1: F.revenueInYear(a, R, 1), r10: F.revenueInYear(a, R, 10),"
              " debt: F.projection(a, R).map((y) => y.debt) }));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["infl"], 2)
        self.assertEqual(len(set(round(d, 9) for d in r["debt"])), 1)       # the payment is fixed in money
        self.assertAlmostEqual(r["r1"], R, places=9)
        self.assertAlmostEqual(r["r10"], R * 0.974 ** 9 * 1.02 ** 9, places=9)
        self.assertAlmostEqual(r["npv"], mirror(r["a"]), places=6)
        self.assertAlmostEqual(r["npv"], -665.32, places=2)


if __name__ == "__main__":
    unittest.main()
