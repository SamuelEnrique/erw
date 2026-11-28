"""Session 11408, readied for the owner's ruling (weekend page part 3.4, generator choice 1; the generator audit of 20
November, finding 1, docs/reviews/generator-model-audit-2026-11-20.md, carried from wip/audit-generator-1): the NPV
to equity after federal income tax (21 percent), with 5-year MACRS depreciation (half-year convention) on a basis cut
by half the investment credit, the debt's interest deductible, a loss used as it arises.

1. The page's library (site/lib/seller/finance.ts, run by Node) equals an independent mirror at the default solar case
   (ERCOT, USD 59.8523 per kW): NPV -526.10 per kW (it was -766.62 with no tax).
2. The breakeven PPA price stays a breakeven: NPV at it is zero; it reads 53.59 per MWh (it was 58.36).
3. The decision and the note's section 13 say the NPV is after tax, word for word alike."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "seller", "finance.ts").replace("\\", "/")
NOTE = os.path.join(ROOT, "docs", "methods", "generator_earns_algorithm.md")
DECISIONS = os.path.join(ROOT, "site", "lib", "decisions.ts")
R, E = 59.8523, 2.5799
MACRS5 = [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]


def page():
    js = ("const F = await import(process.argv[1]);"
          "const a = F.defaultsOf({ capex: 1375, fom: 12.5, life: 35, deg: 0.7 });"
          f"const R = {R}, E = {E}; const c = {{ kind: 'energy', energyKw: E, shape: 'generated', flat: null }};"
          "const p = F.breakevenPpa(a, R, c, 100);"
          "console.log(JSON.stringify({ a, npv: F.npv(a.hurdle, F.flows(a, R, c)), debt: F.debtService(a), p,"
          " atP: F.npv(a.hurdle, F.flows({ ...a, cshare: 100, cprice: p }, R, c)) }));")
    out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


def mirror(a, debt, tax=0.21):
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


class GeneratorAfterTax(unittest.TestCase):
    def test_the_library_is_after_tax(self):
        p = page()
        self.assertEqual((p["a"]["itc"], p["a"]["ptc"], p["a"]["hurdle"]), (0, 0, 12))
        self.assertAlmostEqual(p["npv"], mirror(p["a"], p["debt"]), places=6)
        self.assertAlmostEqual(p["npv"], -526.10, places=2)

    def test_the_breakeven_is_still_a_breakeven(self):
        p = page()
        self.assertAlmostEqual(p["atP"], 0.0, places=6)
        self.assertAlmostEqual(p["p"], 53.59, places=2)

    def test_the_words_say_after_tax(self):
        words = "The NPV is after federal income tax at 21 percent with 5-year depreciation, discounted at 12 percent"
        with open(NOTE, encoding="utf-8") as f:
            note = f.read()
        with open(DECISIONS, encoding="utf-8") as f:
            dec = f.read()
        self.assertIn("12. " + words, note)
        self.assertIn(words, dec)
        self.assertNotIn("No tax, no tax credit, no repowering", note)


if __name__ == "__main__":
    unittest.main()
