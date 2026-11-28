"""wip/ready-datacenter-inflation (session 11406, chain 770, part C): the other choice of the datacenter audit of
26 November, finding 4 (docs/reviews/datacenter-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the scenarios repeat the last twelve months flat for 20 years and discount them at 9.6 percent, a rate in
money. On this branch the default change of prices is 2 percent a year (the Federal Reserve's longer-run goal for
inflation), so the money rate discounts money of the same kind. The present value of the default case for 100 MW rises
14.63 percent (USD 261.19 million to 299.42 million), the fixed price with the same present value 34.07 to 39.06 and
the all-in GPU-hour 0.0691 to 0.0792; the year's power per GPU-hour does not move. The audit's own test
(tests/test_audit_datacenter_4.py on wip/audit-datacenter-4) is carried here, asserting the new default."""
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
const r = F.resultOf(a, w), r0 = F.resultOf({ ...a, growth: 0 }, w);
console.log(JSON.stringify({ hurdle: a.hurdle, growth: a.growth, life: a.life, pv: r.pv * 100, pv0: r0.pv * 100, lev: r.level, lev0: r0.level, gpuh: r.gpuHour, gpuh0: r0.gpuHour, allIn: r.allIn, allIn0: r0.allIn }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class PricesRiseByDefault(unittest.TestCase):
    def test_default_present_value_with_prices_rising(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL("site", "lib", "datacenter.ts"), URL("site", "lib", "datacenter", "finance.ts"),
                              os.path.join(ROOT, "site", "data", "datacenter")], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        self.assertEqual((r["hurdle"], r["growth"], r["life"]), (9.6, 2, 20))      # the new default: 2 percent a year
        self.assertAlmostEqual(r["pv"] / r["pv0"] - 1, 0.14634, places=4)          # +14.6 percent, as the audit measured
        self.assertGreater(r["lev"] / r["lev0"], 1.14)
        self.assertEqual(r["gpuh"], r["gpuh0"])                                      # the year's power per GPU-hour does not move
        self.assertAlmostEqual(r["allIn"] / r["allIn0"] - 1, 0.14634, places=4)    # the all-in GPU-hour moves with the present value

    def test_the_words_say_which_dollars(self):
        lib = src("site", "lib", "datacenter", "finance.ts")
        self.assertIn("export const GROWTH = 2;", lib)
        self.assertIn("growth: GROWTH", lib)
        self.assertIn("the Federal Reserve's longer-run goal for inflation", lib)
        self.assertIn("a rate in money, discounts money of the same kind", lib)
        note = src("docs", "methods", "datacenter_pays_algorithm.md")
        self.assertIn("| Change of prices, percent a year | `ae`, `be` | 2 (until the ruling", note)
        self.assertNotIn("the change of prices and the upfront cost default to none", note)


if __name__ == "__main__":
    unittest.main()
