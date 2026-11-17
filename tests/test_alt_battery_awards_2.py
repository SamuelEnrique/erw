"""Ruling alternative 2 of /cost-of-power/battery/awards (session 7705, 17 November 2026, branch wip/alt-battery-awards-2;
not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-awards-2026-11-17.md, line 2): give the
gap's three parts for each month, not only for the months together? On this branch the offers section adds a table, the
same three parts month by month (site/lib/storageawards.ts gapByMonth: gapOf on one month's rows at a time). Pinned with
the page's own library on the public tables (site/scripts/alt-battery-awards-figures.mjs), where they are on the machine
(warehouse/output, or the folder ERW_TABLES_DIR names): together, January to July 2026, gap USD 23.61 per kW, never
offered 9.70, not awarded 14.53, price -0.62 (unchanged); by month, never offered 34.5 percent (January) to 44.2 percent
(April), not awarded 58.8 (May) to 67.7 percent (January), price -2.2 to -5.4 percent (June); July 2026 gap 2.19, parts
0.95, 1.30 and -0.06. Seven months, four cells each.

    python -m unittest tests.test_alt_battery_awards_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
NEED = ("ercot_storage_dam_awards_monthly", "battery_stack_monthly", "ercot_storage_dam_offers_monthly")


@unittest.skipUnless(all(os.path.exists(os.path.join(TABLES, f"{t}.csv")) for t in NEED), "the public tables are not on this machine")
class TheThreePartsByMonth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-battery-awards-figures.mjs", TABLES], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)
        cls.m = {x["m"]: x for x in cls.f["byMonth"]}

    def test_together_is_unchanged(self):
        t = self.f["together"]
        self.assertEqual([round(t[k], 2) for k in ("gap", "never", "unawarded", "price")], [23.61, 9.70, 14.53, -0.62])

    def test_july(self):
        j = self.m["2026-07"]
        self.assertEqual([round(j[k], 2) for k in ("gap", "never", "unawarded", "price")], [2.19, 0.95, 1.30, -0.06])

    def test_the_shares_by_month(self):
        share = {m: {k: x[k] / x["gap"] * 100 for k in ("never", "unawarded", "price")} for m, x in self.m.items()}
        self.assertEqual(sorted(self.m), ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07"])
        never, unawarded, price = ({m: round(s[k], 1) for m, s in share.items()} for k in ("never", "unawarded", "price"))
        self.assertEqual((min(never, key=never.get), never["2026-01"], max(never, key=never.get), never["2026-04"]), ("2026-01", 34.5, "2026-04", 44.2))
        self.assertEqual((min(unawarded, key=unawarded.get), unawarded["2026-05"], max(unawarded, key=unawarded.get), unawarded["2026-01"]), ("2026-05", 58.8, "2026-01", 67.7))
        self.assertEqual((min(price, key=price.get), price["2026-06"]), ("2026-06", -5.4))

    def test_the_parts_add_up_each_month(self):
        for m, x in self.m.items():
            self.assertAlmostEqual(x["never"] + x["unawarded"] + x["price"], x["gap"], places=9, msg=m)

    def test_the_section_draws_the_table(self):
        self.assertEqual(self.f["drawn"], 28)


if __name__ == "__main__":
    unittest.main()
