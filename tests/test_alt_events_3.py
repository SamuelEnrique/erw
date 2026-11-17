"""Ruling alternative 3 of /events (session 7712, 17 November 2026, branch wip/alt-events-3; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-events-2026-11-17.md, line 3): a temperature
version for the three newest events (January 2025 cold, June 2025 heat, January 2026 cold), as the other six have? Their
pages have no station rows in event_window_daily. On this branch they read noaa_grid_weather_daily (the grid's mean of
NOAA ISD-Lite stations, base 65 F: that table's stations, a like method on other rows), with a hover saying so
(lib/eventstudy.ts noaaGridWeather, NOAA_GRID_ENTITY, NOAA_DAILY_EVENTS; components/EventStudy.tsx reads it for those events;
scripts/check-values.mjs recomputes it. The live set does not serve the table (main holds it from the catalogue, and the
branch leaves that to the data machine): until it is served the pages read as on main. New figures, pinned with the site's own code on the replication's public rows and the local NOAA table where
it is on the machine (warehouse/output, or the folder ERW_TABLES_DIR names): PJM January 2025 412,096 to 90,681 MWh a
day (weather share 78.0 percent), June 2025 380,844 to 149,728 (60.7), January 2026 677,815 to 154,838 (77.2, its
interval crossing 0: -90,945 to 400,621); ERCOT 248,041 to 128,300 (48.3) and 346,005 to 116,860 (66.2); SPP 110,081 to
72,827 (33.8) and 200,299 to 69,515 (65.3).

    python -m unittest tests.test_alt_events_3 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
NOAA = os.path.join(TABLES, "noaa_grid_weather_daily.csv")


@unittest.skipUnless(os.path.exists(NOAA), "noaa_grid_weather_daily is not on this machine")
class TheThreeNewestEvents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = dict(os.environ, EVENTS_DRAW_UNHELD="1")
        p = subprocess.run(["node", "--import", "./scripts/events-page-register.mjs", "scripts/alt-events-figures.mjs", NOAA], cwd=SITE, capture_output=True, text=True, timeout=600, env=env)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_estimates(self):
        want = {"cold_2025|eia930:PJM": (412096, 90681, 78.0), "east_heat_2025|eia930:PJM": (380844, 149728, 60.7), "cold_2026|eia930:PJM": (677815, 154838, 77.2),
                "cold_2025|eia930:ERCO": (248041, 128300, 48.3), "cold_2026|eia930:ERCO": (346005, 116860, 66.2),
                "cold_2025|eia930:SWPP": (110081, 72827, 33.8), "cold_2026|eia930:SWPP": (200299, 69515, 65.3)}
        got = {k: (round(v["without"]), round(v["with"]), round(v["share"], 1)) for k, v in self.f["studies"].items()}
        self.assertEqual(got, want)

    def test_january_2026_crosses_zero(self):
        s = self.f["studies"]["cold_2026|eia930:PJM"]
        self.assertEqual((round(s["lo"]), round(s["hi"])), (-90945, 400621))

    def test_the_page_draws_it(self):
        self.assertEqual(self.f["drawn"], {"noaaTip": True, "pooledTemp": 2, "noStation": False, "elliottNoaa": False})


if __name__ == "__main__":
    unittest.main()
