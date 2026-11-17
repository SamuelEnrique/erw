"""Ruling alternative 1 of /demand (session 7728, 17 November 2026, branch wip/alt-demand-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-demand-2026-11-17.md, line 1): fit the weather
view on more years than 2019 to 2021, so the hot 2025 and 2026 summer peaks can be called findings? On this branch the
builder (warehouse/derived/demand_weather.py TRAIN) fits on 2019 to 2024, six left-out years; the years 2022 to 2024 are
then in the fit and are no longer reported. Pinned with the builder's own analyse() on EIA-930's hourly workbooks and
noaa_grid_weather_hourly where they are on the machine (ERW_RAW_DIR, the folder of the eia930_emissions workbooks, and
ERW_TABLES_DIR, or the repository's own folders). ERCOT's 2026 summer peak: unexplained +11.89 percent against an
uncertainty of 9.88, a finding (main: +15.37, not a finding, hotter than any hour of the fit); its 2025 peak loses its
mark (+9.64 against 9.88; main +12.72 against 6.32); ERCOT's 2025 energy +16.25 (13.23; main +23.86, 4.09).

    python -m unittest tests.test_alt_demand_1 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import demand_growth as dg  # noqa: E402
import demand_weather as dw  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
RAW = os.environ.get("ERW_RAW_DIR") or dg.RAW
WEATHER = os.path.join(TABLES, "noaa_grid_weather_hourly.csv")


class TheFitYears(unittest.TestCase):
    def test_the_fit_is_2019_to_2024(self):
        self.assertEqual(dw.TRAIN, (2019, 2020, 2021, 2022, 2023, 2024))


@unittest.skipUnless(os.path.exists(WEATHER) and os.path.isdir(RAW), "the workbooks or the weather table are not on this machine")
class Ercot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dg.RAW = RAW
        demand, _ = dw.read_demand("ERCO")
        cls.res = dw.analyse(demand, dw.read_weather(WEATHER).get("ERCO"), "America/Chicago", "ERCO")

    def g(self, y, k):
        return self.res["years"][y][k]

    def test_the_2026_summer_peak_is_a_finding(self):
        g = self.g(2026, "summer_peak")
        self.assertEqual((round(g["unexplained_pct"], 2), round(g["uncertainty_pct"], 2), g["holdouts"], g["finding"]), (11.89, 9.88, 6, True))

    def test_the_2025_summer_peak_loses_its_mark(self):
        g = self.g(2025, "summer_peak")
        self.assertEqual((round(g["unexplained_pct"], 2), round(g["uncertainty_pct"], 2), g["finding"]), (9.64, 9.88, False))

    def test_the_2025_energy(self):
        g = self.g(2025, "energy")
        self.assertEqual((round(g["unexplained_pct"], 2), round(g["uncertainty_pct"], 2), g["finding"]), (16.25, 13.23, True))

    def test_2022_to_2024_are_not_reported(self):
        self.assertFalse(any(y in self.res["years"] and self.res["years"][y] for y in (2022, 2023, 2024)))


if __name__ == "__main__":
    unittest.main()
