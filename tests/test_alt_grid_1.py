"""Ruling alternative 1 of /grid (session 7725, 17 November 2026, branch wip/alt-grid-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-grid-2026-11-17.md, line 1): the Mix tab's three
lead figures stand at three different hours; show all three at the newest hour all three hold? On this branch demand, the
exchange and carbon are read at the oldest of their three newest hours when the network snapshot holds that hour
(site/lib/gridalign.ts alignHour; site/components/grid/NowView.tsx); otherwise each keeps its own. On the live site of 17
November the impact file measured, at carbon's 12 November 23:00 UTC: the exchange turns over for three grids (ERCOT a net
import of 145 MW becomes a net export of 20 MW; CAISO an import of 5,604 MW an export of 675 MW; SPP an export of 1,544 MW
an import of 1,112 MW; PJM's export 1,267 to 2,716 MW), demand moves a little (ERCOT 54,008 to 54,234 MW), carbon does not.
On this machine carbon_intensity_hourly ends on 2 November (ERCOT and CAISO; SPP 31 October, PJM 30 October), before the
committed snapshot's week (to 13 November 23:00 UTC), so no hour is shared and every figure keeps its own: the fallback is
pinned on those copies, the rule on made-up hours.

    python -m unittest tests.test_alt_grid_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")


class TheRule(unittest.TestCase):
    def test_the_oldest_newest_hour_inside_the_snapshot(self):
        js = ("const A = await import('./lib/gridalign.ts');"
              "const snap = ['2026-11-12T22:00:00Z', '2026-11-12T23:00:00Z', '2026-11-13T00:00:00Z'];"
              "process.stdout.write(JSON.stringify([A.alignHour(['2026-11-15T23:00:00Z', '2026-11-12T23:00:00Z', '2026-11-15T04:00:00Z'], snap),"
              " A.alignHour(['2026-11-15T23:00:00Z', '2026-11-02T23:00:00Z', '2026-11-13T00:00:00Z'], snap), A.alignHour(['2026-11-15T23:00:00Z', null, undefined], snap)]));")
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        self.assertEqual(json.loads(p.stdout), ["2026-11-12T23:00:00Z", None, None])

    def test_the_view_uses_it(self):
        with open(os.path.join(SITE, "components", "grid", "NowView.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("alignHour([dLatest?.ts_utc, cgLatest?.ts_utc, xLatest], snap.hours)", s)
        self.assertIn("const xHour = hour ?? xLatest;", s)


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in ("eia930_all_demand", "carbon_intensity_hourly")), "the tables are not on this machine")
class OnTheCopiesHere(unittest.TestCase):
    def test_no_shared_hour_so_each_keeps_its_own(self):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-grid-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        f = json.loads(p.stdout)
        self.assertEqual(f["xLatest"], "2026-11-13T23:00:00Z")
        for ba, carbon_day in (("ERCO", "2026-11-02"), ("CISO", "2026-11-02"), ("SWPP", "2026-10-31"), ("PJM", "2026-10-30")):
            self.assertEqual((f[ba]["hour"], f[ba]["main"]["carbon"]["ts_utc"][:10]), (None, carbon_day), ba)


if __name__ == "__main__":
    unittest.main()
