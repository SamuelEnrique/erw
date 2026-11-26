"""Audit of the datacenter power tracker, finding 6 (session 10211, docs/reviews/tracker-model-audit-2026-11-26.md): the
view by grid prices "the cheapest and the dearest load zone ... at the calculator's defaults". The default buys in real
time where twelve complete months of real-time prices are held, else day-ahead, and no real-time price is held for four
of ERCOT's eight zones, so on the page's files of 12 November 2026 the range set Houston's real-time USD 34.02 beside
Austin Energy's day-ahead 39.01, unsaid. In one market (day-ahead) the low end is South's 34.87.

1. Through the page's library (site/lib/datacenter.ts, regionCosts, on site/data/datacenter/, run by Node with the
   site's loaders): the cheapest ERCOT zone is bought in real time and the dearest in day-ahead. Passes on main.
2. The fix on this branch, words only: the bullet says each zone is in its own market. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
JS = """
const { INDEX, yearFiles } = await import("./scripts/datacenter-ways.mjs");
const D = await import("./lib/datacenter.ts");
const cs = D.regionCosts(yearFiles("ercot"), INDEX.grids.ercot, ["zone"]).sort((a, b) => a.per - b.per);
console.log(JSON.stringify({ lo: [cs[0].buy, cs[0].per], hi: [cs.at(-1).buy, cs.at(-1).per], buys: [...new Set(cs.map((c) => c.buy))].sort(), n: cs.length }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class ThePriceRangeSaysItsMarkets(unittest.TestCase):
    def test_the_two_ends_are_in_different_markets(self):
        out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS], cwd=SITE,
                             capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        if r["buys"] != ["da", "rt"]:
            self.skipTest("the page's files no longer price ERCOT's zones in two markets")
        self.assertEqual(r["lo"][0], "rt")
        self.assertEqual(r["hi"][0], "da")
        self.assertLess(r["lo"][1], r["hi"][1])

    def test_the_bullet_says_each_zone_is_in_its_own_market(self):
        self.assertIn("Energy only. Each zone is in its own market, real time where twelve complete months are held, else day-ahead, so the two ends "
                      "can be in different markets; the power side of the facilities view names each zone&apos;s market.",
                      src("site", "app", "datacenters", "GridsView.tsx"))


if __name__ == "__main__":
    unittest.main()
