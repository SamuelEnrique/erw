"""Audit of the prices pages, finding 4 (session 10218, docs/reviews/prices-model-audit-2026-11-26.md): a held grid on
/prices and on its hub's page. Session 7539 drew a held grid's section as its main hub named, both price cells "license
needed", only when the grid's day-ahead read was refused and no row of the grid was read; but latest_prices holds the
held grids' newest intervals (the connector writes NYISO's and ISO-NE's every 15 minutes with license "public", and
MISO's last row of 4 October 2026 stays), and the site reads latest_prices with no hold. Then each zone was listed, its
price "license needed" (components/Num.tsx holds it: no figure reaches the page), the held interval's start printed, and
the day-ahead cell said "no data: no nyiso_dam_zone_prices row since ...", which is not so; the hub's page said "no rows
in nyiso_rtm_zone_prices for this entity in the last 30 days" and "license needed USD/MWh, starting ...".

1. Why (passes on main): the connector writes the held grids to latest_prices as public, and the site's reader of
   latest_prices names no table, so no hold applies to it.
2. The fix on this branch, words only (fails on main): drawn with the pages' own functions on stand-in rows (every price
   0, made for the test), the held grids' sections are the held drawing whatever latest_prices holds, and the hub's page
   says "license needed: the rows of <table> are held, not shown". No figure moves: a held grid had none, and the public
   grids' sections are drawn as before."""
import json
import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class HeldGridsWhateverLatestPricesHolds(unittest.TestCase):
    def test_latest_prices_holds_the_held_grids_and_no_hold_applies(self):
        src = open(os.path.join(ROOT, "warehouse", "connectors", "latest_prices.py"), encoding="utf-8").read()
        self.assertIn('"nyiso": (lambda: gridstatus.NYISO()', src)
        self.assertIn('"isone": (lambda: gridstatus.ISONE()', src)
        self.assertIn('INTERNAL = {"pjm"}', src)
        self.assertIn('license="internal" if iso in INTERNAL else "public"', src)
        data = open(os.path.join(SITE, "lib", "data.ts"), encoding="utf-8").read()
        self.assertRegex(data, r'rest<LatestPrice>\("latest_prices", \{ select: "\*", order: "entity" \}')
        sb = open(os.path.join(SITE, "lib", "supabase.ts"), encoding="utf-8").read()
        self.assertIn('if (!t || !licenseNeeded(t)) return { throw: false, filter: false };', sb)   # no table named: no hold

    def test_the_pages_draw_a_held_grid_as_held(self):
        out = subprocess.run(["node", "--import", "./scripts/prices-read-register.mjs", "scripts/audit-prices-4-draw.mjs"],
                             cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        pages = {p["page"]: p for p in (json.loads(x) for x in out.stdout.splitlines() if x.startswith("{"))}
        first = pages["/prices"]
        self.assertEqual(sorted(first["heldGrids"]), ["ISO-NE", "MISO", "NYISO"])
        self.assertNotRegex(first["text"], r"no data: no (nyiso_dam_zone_prices|isone_dam_zone_prices|iso_dam_hub_prices) row")
        self.assertNotIn("2026-10-04 03:55", first["text"])
        for e, table in (("nyiso:N.Y.C.", "nyiso_rtm_zone_prices"), ("miso:INDIANA.HUB", "iso_rtm_hub_prices")):
            t = pages[e]["text"]
            self.assertEqual(pages[e]["heldMarkets"], ["Real time", "Day-ahead"])
            self.assertIn(f"license needed : the rows of {table} are held, not shown", t)
            self.assertNotIn("no rows in", t)
            self.assertNotRegex(t, r"license needed USD/MWh")
            self.assertEqual(pages[e]["emDashes"], 0)
        self.assertFalse(re.search(r"\b0\.00\b", " ".join(p["text"] for p in pages.values())), "a stand-in price reached a page")


if __name__ == "__main__":
    unittest.main()
