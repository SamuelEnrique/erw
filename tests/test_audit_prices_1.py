"""Audit of the prices pages, finding 1 (session 10218, docs/reviews/prices-model-audit-2026-11-26.md): "Where power is
cheap" (/prices/compare) said ERCOT's eight load zones "are not in this comparison", that "the zones" are in the month
and not in the twelve months, and counted the twelve months' rows as "17 hubs", while the site's copy has held ERCOT's
load zones in both periods since session 7052 (8 of the 17 rows of the twelve months, 8 of the 19 of the month), and the
default view's sentence named "ERCOT, Austin Energy load zone" the dearest of "the 17 hubs compared". The lead spoke of
"five grids" where three are shown.

1. What the file holds (passes on main): ERCOT's eight load zones in both periods, beside its six hubs.
2. The fix on this branch, words only (fails on main): drawn with the page's own function, the page no longer says the
   load zones are not compared, counts hubs and zones apart, and names the grids shown. Every figure is the file's, as
   before: no figure moves."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
ZONES = {f"ercot:LZ_{z}" for z in ("AEN", "CPS", "HOUSTON", "LCRA", "NORTH", "RAYBN", "SOUTH", "WEST")}


def load():
    with open(os.path.join(SITE, "data", "price_compare.json"), encoding="utf-8") as f:
        return json.load(f)


def draw(*queries):
    out = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/audit-prices-1-draw.mjs", *[json.dumps(q) for q in queries]],
                         cwd=SITE, capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return [json.loads(x) for x in out.stdout.strip().splitlines() if x.startswith("{")]


class LoadZonesAreCompared(unittest.TestCase):
    def test_the_file_holds_ercots_load_zones_in_both_periods(self):
        f = load()
        for period in ("year", "month"):
            got = {r["entity"] for r in f[period]}
            self.assertTrue(ZONES <= got, f"{period}: {sorted(ZONES - got)}")
        self.assertEqual(sum(1 for r in f["year"] if r["entity"] in ZONES), 8)

    @unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
    def test_the_page_says_so_and_counts_hubs_and_zones_apart(self):
        f = load()
        n_year = len(f["year"])
        default, month = draw({}, {"period": "month"})
        t = default["text"]
        self.assertNotIn("they are not in this comparison", t)
        self.assertNotIn("the zones and the other hubs are held since late August 2026", t)
        self.assertNotIn("of five grids", t)
        self.assertIn(f"Twelve months of history are held for {n_year} hubs and zones ({n_year - 8} hubs and 8 of ERCOT's load zones, held since 2015)", t)
        self.assertIn(f"Twelve months to October 2026: {n_year} hubs and zones", t)
        self.assertIn(f"of the {n_year} hubs and zones compared", t)
        self.assertIn("ERCOT's eight load zones are compared here, in both periods", t)
        self.assertIn("The hub and zone prices of three grids, CAISO, ERCOT and SPP, side by side", t)
        self.assertIn(f"of the {len(f['month'])} hubs and zones compared", month["text"])
        self.assertEqual(default["emDashes"], 0)
        # every figure is still the file's own: the sentence's count and the cheapest and dearest averages
        self.assertEqual(default["marked"]["count"], str(n_year))
        avg = sorted(r["dam_avg_price"] for r in f["year"])
        self.assertEqual(default["marked"]["sum|cheapest"], f"{avg[0]:,.2f}")
        self.assertEqual(default["marked"]["sum|dearest"], f"{avg[-1]:,.2f}")


if __name__ == "__main__":
    unittest.main()
