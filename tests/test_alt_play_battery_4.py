"""Ruling alternative 4 of /play/battery (session 7718, 17 November 2026, branch wip/alt-play-battery-4; not a default on
main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-play-battery-2026-11-17.md, line 4): say on the
August 2023 heat day's line that 10 August 2023 was ERCOT's demand record of 2023? On this branch the day's line gains one
clause and a figure (site/lib/levels.ts DAY_RECORDS): 85,464 MW in the hour from 5 p.m. Central, from the warehouse's own
row (ercot_zone_load_hourly, ercot:system, ERCOT's Hourly Load Data Archives). The rulings file quotes Potomac Economics'
85.7 GW, a document the warehouse has not read; the warehouse's own figure is 236 MW (0.28 percent) under it. No figure
that stands moves. Pinned on the line the levels library gives, and on the local table where it is on the machine
(warehouse/output, or the folder ERW_TABLES_DIR names): the highest of 2023's 8,760 hours.

    python -m unittest tests.test_alt_play_battery_4 -v
"""

import csv
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "ercot_zone_load_hourly.csv")


class TheLine(unittest.TestCase):
    def test_the_heat_days_line(self):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e",
                            "const L = await import('./lib/levels.ts'); process.stdout.write(JSON.stringify(L.FAMOUS.map((l) => [l.slug, l.why])));"],
                           cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stderr[-1500:])
        why = dict(json.loads(p.stdout))
        self.assertTrue(why["heat"].endswith("It held ERCOT's highest hour of 2023: 85,464 MW in the hour from 5 p.m. Central (ERCOT's hourly load archive)."))
        self.assertNotIn("highest hour of 2023", why["uri"])


@unittest.skipUnless(os.path.exists(CSV), "ercot_zone_load_hourly is not on this machine")
class OnTheTable(unittest.TestCase):
    def test_the_highest_hour_of_2023(self):
        hours = []
        with open(CSV, encoding="utf-8") as f:
            for r in csv.reader(line for line in f if not line.startswith("#")):
                if r[0] == "ercot:system" and r[1] == "load" and r[2].startswith("2023"):
                    hours.append((float(r[3]), r[2]))
        top = max(hours)
        self.assertEqual((len(hours), round(top[0]), top[1]), (8760, 85464, "2023-08-10T22:00:00Z"))


if __name__ == "__main__":
    unittest.main()
