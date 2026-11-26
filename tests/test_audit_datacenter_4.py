"""Audit of "What a datacenter pays", finding 4 (session 10203, docs/reviews/datacenter-model-audit-2026-11-26.md): two
kinds of dollars. Every figure is the sum of each month's own dollars, never adjusted and never said to be (the cost
chart sets 2015 beside 2026). In scenarios A and B the last twelve months are repeated flat for 20 years (no change of
prices by default) and discounted at 9.6 percent, Lazard's weighted cost of capital, which is a rate in money: a flat
real cost at a money rate. The battery audit's finding 9 and the generator audit's finding 2, on a buyer's page.

This branch makes no fix: a fix moves the present value the page prints, which is Samuel's ruling. The test shows the
size, through the page's own library (site/lib/datacenter/finance.ts and site/lib/datacenter.ts, run by Node) on the
page's own files: with prices rising 2 percent a year (an assumption of this audit, the usual planning figure) the
present value of the default case is 14.63 percent higher (USD 261.19 million to 299.42 million for 100 MW on the files
of 12 November 2026), 18.78 percent at 2.5; the fixed price with the same present value 39.06 and 40.47 against 34.07.
The ratio does not depend on the prices; the dollars do, and are printed for the record."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = lambda *p: "file:///" + os.path.join(ROOT, *p).replace("\\", "/")  # noqa: E731
JS = """
const [L, F] = await Promise.all([import(process.argv[1]), import(process.argv[2])]);
const fs = await import("node:fs");
const dir = process.argv[3];
const index = JSON.parse(fs.readFileSync(dir + "/index.json", "utf-8"));
const files = index.grids.ercot.years.map((y) => JSON.parse(fs.readFileSync(dir + "/ercot_" + y + ".json", "utf-8")));
const s = L.span(L.lastTwelve(L.monthsRuled(files, "LZ_NORTH", "rt", { run: "flat", n: 0, pct: 0, shift: 0 }, "forecast").months));
const w = { per: s.per, cost: s.cost, energy: s.energy, held: s.held, flatCost: s.flatCost, down: 0, bad: null, of: 0 };
const a = F.defaultsOf({ run: F.FLAT, gpu: 1.3, pue: 1.56 });
const at = (g) => F.resultOf({ ...a, growth: g }, w);
console.log(JSON.stringify({ hurdle: a.hurdle, growth: a.growth, life: a.life, pv0: at(0).pv * 100, pv2: at(2).pv * 100, pv25: at(2.5).pv * 100, lev0: at(0).level, lev2: at(2).level, lev25: at(2.5).level }));
"""


class TwoKindsOfDollars(unittest.TestCase):
    def test_flat_prices_at_a_money_rate(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL("site", "lib", "datacenter.ts"), URL("site", "lib", "datacenter", "finance.ts"),
                              os.path.join(ROOT, "site", "data", "datacenter")], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        self.assertEqual((r["hurdle"], r["growth"], r["life"]), (9.6, 0, 20))     # Lazard's money rate on flat prices
        self.assertAlmostEqual(r["pv2"] / r["pv0"] - 1, 0.14634, places=4)        # +14.6 percent at 2 percent a year
        self.assertAlmostEqual(r["pv25"] / r["pv0"] - 1, 0.18779, places=4)       # +18.8 percent at 2.5
        self.assertGreater(r["lev2"] / r["lev0"], 1.14)

    def test_no_word_says_which_dollars(self):
        for p in (("site", "app", "cost-of-power", "page.tsx"), ("site", "app", "cost-of-power", "LoadScenarios.tsx"), ("site", "lib", "datacenter", "finance.ts")):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                t = f.read().lower()
            for w in ("inflation", "nominal", "real dollars", "today's dollars"):
                self.assertNotIn(w, t, os.path.join(*p))


if __name__ == "__main__":
    unittest.main()
