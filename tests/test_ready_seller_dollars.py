"""Session 11408, readied for the owner's ruling (weekend page part 3.4, generator choice 2; the generator audit of 20
November, finding 2, docs/reviews/generator-model-audit-2026-11-20.md, carried from wip/audit-generator-2): one kind of
dollar over 35 years. The debt payment is fixed in money and the hurdle is a money rate, so market revenue and fixed
O&M rise with inflation (2 percent a year, the low end of the audit's 2 to 2.5).

Through site/lib/seller/finance.ts (run by Node) at the default solar case (ERCOT, USD 59.8523 per kW): NPV equals an
independent mirror, -706.90 per kW (it was -766.62; the audit's +59.72); the breakeven PPA price stays a breakeven
(NPV zero at it) and reads 59.22 per MWh (it was 58.36)."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "seller", "finance.ts").replace("\\", "/")
R, E = 59.8523, 2.5799


def mirror(a, debt, infl=0.02):
    n = min(a["term"], a["life"])
    fl = [-a["capex"] * (1 - a["share"] / 100)]
    for t in range(1, a["life"] + 1):
        e = (1 + infl) ** (t - 1)
        fl.append(R * (1 - a["deg"] / 100) ** (t - 1) * e - a["fom"] * e - (debt if t <= n else 0.0))
    return sum(f / (1 + a["hurdle"] / 100) ** t for t, f in enumerate(fl))


class OneKindOfDollar(unittest.TestCase):
    def test_money_flows(self):
        js = ("const F = await import(process.argv[1]);"
              "const a = F.defaultsOf({ capex: 1375, fom: 12.5, life: 35, deg: 0.7 });"
              f"const R = {R}, E = {E}; const c = {{ kind: 'energy', energyKw: E, shape: 'generated', flat: null }};"
              "const p = F.breakevenPpa(a, R, c, 100);"
              "console.log(JSON.stringify({ a, infl: F.INFLATION, debt: F.debtService(a), npv: F.npv(a.hurdle, F.flows(a, R, c)), p,"
              " atP: F.npv(a.hurdle, F.flows({ ...a, cshare: 100, cprice: p }, R, c)) }));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["infl"], 2)
        self.assertAlmostEqual(r["npv"], mirror(r["a"], r["debt"]), places=6)
        self.assertAlmostEqual(r["npv"], -706.90, places=2)
        self.assertAlmostEqual(r["atP"], 0.0, places=6)
        self.assertAlmostEqual(r["p"], 59.22, places=2)


if __name__ == "__main__":
    unittest.main()
