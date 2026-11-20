"""Sessions 7802 and 7803 (chain 401 part C, tables 5 and 6): the county-name rule of warehouse/derived/eia_county_region.py,
on names as EIA-861's Service Territory sheet and the Census Bureau print them, and the station rule of
warehouse/connectors/noaa_region_weather.py (95 percent of each year's hours to the end of ISD-Lite).

Energy Research Warehouse (ERW). docs/methods/county_population_and_regions.md, docs/methods/region_weather.md.

    python -m unittest tests.test_session7802_county_region -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_county_region as ecr  # noqa: E402
import noaa_region_weather as nrw  # noqa: E402


class CountyNames(unittest.TestCase):
    def test_eia_and_census_names_meet(self):
        # (EIA-861's form of a name, the Bureau's form): the forms the two print (Dona Ana and Baltimore City as on 18 November 2026)
        for eia, census in (("Anderson", "Anderson County"), ("Dona Ana", "Doña Ana County"), ("Acadia", "Acadia Parish"),
                            ("Baltimore City", "Baltimore city"), ("St. Louis", "St. Louis County"), ("Saint Clair", "St. Clair County"),
                            ("De Kalb", "DeKalb County"), ("Prince George's", "Prince George's County")):
            self.assertEqual(ecr.key(eia), ecr.key(census), (eia, census))

    def test_a_city_and_its_county_stay_apart(self):
        self.assertNotEqual(ecr.key("Baltimore"), ecr.key("Baltimore city"))
        self.assertNotEqual(ecr.key("Fairfax"), ecr.key("Fairfax city"))


class StationRule(unittest.TestCase):
    def hours(self, drop_share=0.0, year=None):
        idx = pd.date_range(nrw.START, nrw.SEAM, freq="h", inclusive="left", tz="UTC")
        s = pd.Series(10.0, index=idx)
        if drop_share and year:
            y = s[s.index.year == year].index
            s = s.drop(y[: int(len(y) * drop_share)])
        return s

    def test_every_hour_held_is_complete(self):
        self.assertTrue(nrw.complete(self.hours()))

    def test_six_percent_short_in_one_year_is_not(self):
        self.assertFalse(nrw.complete(self.hours(0.06, 2021)))
        self.assertTrue(nrw.complete(self.hours(0.04, 2021)))

    def test_2018_counts_from_july_and_2025_to_the_seam(self):
        s = self.hours()
        self.assertEqual(s.index.min(), pd.Timestamp("2018-07-01T00:00:00Z"))
        self.assertEqual(s.index.max(), pd.Timestamp("2025-07-31T23:00:00Z"))


if __name__ == "__main__":
    unittest.main()
