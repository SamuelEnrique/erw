"""Audit of "What a datacenter pays", finding 1 (session 10203, docs/reviews/datacenter-model-audit-2026-11-26.md): the
scenarios' row "All-in power per GPU-hour, over the years counted" (site/app/cost-of-power/LoadScenarios.tsx, on
levelGpuHour in site/lib/datacenter/finance.ts) holds market energy, the other charges typed and the upfront cost, and
nothing else. At the defaults it is the energy-only power per GPU-hour to the bit, while the page's own delivery table
(site/data/datacenter/texas_delivery.json) adds about a quarter to the energy in Oncor's area.

1. With the page's own libraries (run by Node) on the page's own files, the default case: the "all-in" figure equals the
   power per GPU-hour of market energy alone, and Oncor's delivery at 100 MW is more than a fifth of the energy price.
   This passes on main: it shows the fault.
2. The fix on this branch, words only: the row is labelled "Levelized power per GPU-hour", its note says what it holds and
   that no delivery, ancillary service or loss charge is in it unless typed; the chart's words follow. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = lambda *p: "file:///" + os.path.join(ROOT, *p).replace("\\", "/")  # noqa: E731
JS = """
const [L, F, D] = await Promise.all([import(process.argv[1]), import(process.argv[2]), import(process.argv[3])]);
const fs = await import("node:fs");
const dir = process.argv[4];
const index = JSON.parse(fs.readFileSync(dir + "/index.json", "utf-8"));
const files = index.grids.ercot.years.map((y) => JSON.parse(fs.readFileSync(dir + "/ercot_" + y + ".json", "utf-8")));
const ms = L.monthsRuled(files, "LZ_NORTH", "rt", { run: "flat", n: 0, pct: 0, shift: 0 }, "forecast").months;
const s = L.span(L.lastTwelve(ms));
const way = { per: s.per, cost: s.cost, energy: s.energy, held: s.held, flatCost: s.flatCost, down: s.down, bad: null, of: 0 };
const a = F.defaultsOf({ run: F.FLAT, gpu: L.DEFAULTS.gpu, pue: L.DEFAULTS.pue });
const r = F.resultOf({ ...a, growth: 0 }, way);   // wip/ready-datacenter-inflation: prices rise 2 percent a year by default; the finding is read with no change of prices
const del = JSON.parse(fs.readFileSync(dir + "/texas_delivery.json", "utf-8"));
const oncor = D.deliveryOf(del.rows, "Oncor", 100).total;
console.log(JSON.stringify({ allIn: r.allIn, gpuHour: r.gpuHour, energyOnly: (s.per * a.gpu * a.pue) / 1000, price: s.per, oncor }));
"""


def node():
    out = subprocess.run(["node", "--input-type=module", "-e", JS, URL("site", "lib", "datacenter.ts"), URL("site", "lib", "datacenter", "finance.ts"),
                          URL("site", "lib", "datacenter", "delivery.ts"), os.path.join(ROOT, "site", "data", "datacenter")],
                         capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


class AllInIsEnergyAlone(unittest.TestCase):
    def test_all_in_is_market_energy_alone_at_the_defaults(self):
        r = node()
        self.assertAlmostEqual(r["allIn"], r["energyOnly"], places=12)   # nothing but market energy in the "all-in" figure
        self.assertAlmostEqual(r["allIn"], r["gpuHour"], places=12)
        self.assertGreater(r["oncor"] / r["price"], 0.2)                    # the page's own delivery table: about a quarter more

    def test_row_says_what_it_holds(self):
        with open(os.path.join(ROOT, "site", "app", "cost-of-power", "LoadScenarios.tsx"), encoding="utf-8") as f:
            t = f.read()
        self.assertNotIn("All-in power per GPU-hour", t)
        self.assertNotIn("all-in power per GPU-hour", t)
        self.assertIn('"Levelized power per GPU-hour, over the years counted"', t)
        self.assertIn("no delivery, ancillary service or loss charge unless typed as other charges", t)
        self.assertIn('moves: "levelized power per GPU-hour"', t)
        with open(os.path.join(ROOT, "docs", "methods", "datacenter_pays_algorithm.md"), encoding="utf-8") as f:
            note = f.read()
        self.assertIn("**levelized power per GPU-hour**", note)
        self.assertIn("finding 1), which changed the label and the row's note and no figure", note)


if __name__ == "__main__":
    unittest.main()
