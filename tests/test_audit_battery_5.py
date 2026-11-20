"""Audit of "What a battery earns", finding 5 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the figure
the page calls the "Breakeven toll" (site/lib/battery/finance.ts, breakevenToll) is the toll at which debt is covered
1.25 times. It is not a breakeven for anyone who owns the battery.

1. With the page's own library (finance.ts, run by Node) at the default case: a toll on the whole battery at that price,
   for the debt's years (the page's own contract, share 100, price the toll), leaves equity an NPV of USD -845.78 per kW
   at 12 percent, below the merchant case's -697.80; the toll at which equity's NPV is zero is USD 13.62 per kW-month.
   This passes on main: it shows the fault.
2. The fix on this branch: the label says what the figure is, "Toll for 1.25 times coverage". This fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "battery", "finance.ts").replace("\\", "/")
R = 81.4022  # the default case's last twelve months, USD per kW (the public dispatch file)


def node(js):
    out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


class TollIsNotABreakeven(unittest.TestCase):
    def test_equity_loses_more_at_the_toll_than_merchant(self):
        r = node("const F = await import(process.argv[1]);"
                 "const a = F.defaultsOf({ capex: 1110, fom: 22 });"
                 f"const R = {R};"
                 "const toll = F.breakevenToll(a);"
                 "const at = (p) => F.npv(a.hurdle, F.flows({ ...a, cshare: 100, cprice: p }, R));"
                 "let lo = 0, hi = 100; for (let i = 0; i < 100; i++) { const m = (lo + hi) / 2; if (at(m) < 0) lo = m; else hi = m; }"
                 "console.log(JSON.stringify({ toll, atToll: at(toll), merchant: F.npv(a.hurdle, F.flows(a, R)), zero: lo }));")
        self.assertAlmostEqual(r["toll"], 4.19, places=2)
        self.assertAlmostEqual(r["merchant"], -697.80, places=1)
        self.assertAlmostEqual(r["atToll"], -845.78, places=1)
        self.assertLess(r["atToll"], r["merchant"])               # the "breakeven" toll is worse for equity than merchant
        self.assertAlmostEqual(r["zero"], 13.62, places=2)        # the toll at which equity breaks even at 12 percent

    def test_label_says_what_the_figure_is(self):
        for p in (("site", "lib", "battery", "view.ts"), ("site", "app", "cost-of-power", "battery", "Scenarios.tsx")):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                t = f.read()
            self.assertNotIn("Breakeven toll", t, os.path.join(*p))
            self.assertIn("Toll for 1.25 times coverage", t, os.path.join(*p))


if __name__ == "__main__":
    unittest.main()
