"""Session 915: Berkeley Lab's wind and solar PPA prices, one row a PPA.

Energy Research Warehouse (ERW). Tests warehouse/connectors/lbnl_ppa_prices.py on sheets built here in LBNL's form
(figures made up for the test, not LBNL's): the wind sheet's columns, the solar sheet's one region a row, '#N/A' read as
empty, a second identical row given its own id, a row with two regions or headings not as read stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session915 -v
"""

import datetime as dt
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import lbnl_ppa_prices as L  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

NA = "#N/A"
WIND = [["Levelized wind PPA prices"], [None], ["PPA Execution Date", "Capacity (MW)", "Term (years)", "Region", "Macro Region", "Real 2025$/MWh"],
        [dt.datetime(2020, 5, 1), 100, 20, "SPP", "Central", 22.5], [dt.datetime(2020, 5, 1), 100, 20, "SPP", "Central", 22.5]]
SOLAR_HEAD = ["PPA Execution Date", "Capacity (MW)", "Term (years)"] + L.REGIONS + [None, "Hawaii", "West", "Central", "Northeast", "Southeast"]


def solar_row(d, mw, region_col, macro_col, price):
    r = [d, mw, 20] + [NA] * 10 + [None] + [NA] * 5
    r[region_col], r[macro_col] = price, price
    return r


class Sheets(unittest.TestCase):
    def test_wind_and_solar(self):
        w = L.wind_rows(pd.DataFrame(WIND))
        s = L.solar_rows(pd.DataFrame([["title"], SOLAR_HEAD, solar_row(dt.datetime(2019, 3, 2), 50, 3, 15, 30.0)]))
        self.assertEqual(s[0][4:], ("CAISO", "West", 30.0))
        t = L.events(w + s, {"wind": "uw", "solar": "us"}, {"wind": "r", "solar": "r"}, {"wind": "2025", "solar": "2024"})
        self.assertEqual(len(t), 3)
        ids = t.event_id.tolist()
        self.assertTrue(any(i.endswith("-2") for i in ids))
        row = t[t.x_technology == "solar"].iloc[0]
        self.assertEqual((row.event_date, row.mw, row.price, row.x_dollar_year, row.currency), ("2019-03-02", 50.0, 30.0, "2024", "USD"))

    def test_stops(self):
        bad = solar_row(dt.datetime(2019, 3, 2), 50, 3, 15, 30.0)
        bad[4] = 31.0
        with self.assertRaises(RuntimeError):
            L.solar_rows(pd.DataFrame([SOLAR_HEAD, bad]))
        head = [list(WIND[2])]
        head[0][5] = "Nominal $/MWh"
        with self.assertRaises(RuntimeError):
            L.wind_rows(pd.DataFrame(head + WIND[3:]))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "lbnl_ppa_prices"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
