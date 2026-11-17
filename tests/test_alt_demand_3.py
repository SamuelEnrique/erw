"""Ruling alternative 3 of /demand (session 7728, 17 November 2026, branch wip/alt-demand-3; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-demand-2026-11-17.md, line 3): a section on a
zone's own load growth? On this branch /demand?grid=ercot draws ERCOT's load zones, each zone's mean hourly load in 2019
and in the newest whole year, from site/data/zone_growth.json, built by site/scripts/build-zone-growth.mjs from
ercot_zone_load_hourly (ERCOT's Hourly Load Data Archives, public). No figure that stands moves; the held grids' zones
are not read. Pinned with the build script on the local table where it is on the machine (warehouse/output, or the folder
ERW_TABLES_DIR names), and on the committed file: 2019 against 2025, Far West 3,435 to 7,478 MW (+117.7 percent), North
854 to 1,689 (+97.8), South Central 6,970 to 8,877 (+27.4), Coast 12,354 to 14,745 (+19.4), North Central 13,819 to 15,307
(+10.8), West 1,292 to 1,384 (+7.2); ERCOT as a whole 43,817 to 55,733 (+27.2).

    python -m unittest tests.test_alt_demand_3 -v
"""

import json
import os
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
WANT = {"ercot:FWEST": (3435, 7478, 117.7), "ercot:NORTH": (854, 1689, 97.8), "ercot:SCENT": (6970, 8877, 27.4), "ercot:COAST": (12354, 14745, 19.4),
        "ercot:NCENT": (13819, 15307, 10.8), "ercot:WEST": (1292, 1384, 7.2), "ercot:system": (43817, 55733, 27.2)}


def check(case, f):
    case.assertEqual((f["base"], f["last"]), ("2019", "2025"))
    got = {z["entity"]: (round(z["base_mw"]), round(z["last_mw"]), round(z["change_pct"], 1)) for z in f["zones"] if z["entity"] in WANT}
    case.assertEqual(got, WANT)
    case.assertTrue(all(z["entity"].startswith("ercot:") for z in f["zones"]))


class TheCommittedFile(unittest.TestCase):
    def test_the_file(self):
        with open(os.path.join(SITE, "data", "zone_growth.json"), encoding="utf-8") as fh:
            check(self, json.load(fh))

    def test_the_page_draws_it_on_ercots_view(self):
        with open(os.path.join(SITE, "app", "demand", "page.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn('import zoneJson from "@/data/zone_growth.json";', s)
        self.assertIn('ba === "ERCO" && zoneJson.last', s)


@unittest.skipUnless(os.path.exists(os.path.join(TABLES, "ercot_zone_load_hourly.csv")), "ercot_zone_load_hourly is not on this machine")
class TheBuildScript(unittest.TestCase):
    def test_built_from_the_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "zone_growth.json")
            p = subprocess.run(["node", "scripts/build-zone-growth.mjs", TABLES, out], cwd=SITE, capture_output=True, text=True, timeout=300)
            self.assertEqual(p.returncode, 0, p.stderr)
            with open(out, encoding="utf-8") as fh:
                check(self, json.load(fh))


if __name__ == "__main__":
    unittest.main()
