"""Session 2015: Berkeley Lab's Tracking the Sun, summarised by state, segment and year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/lbnl_tracking_the_sun.py's summary on systems built here in
the public file's form (figures made up for the test, not Berkeley Lab's): the counts, the DC capacity in MW, the median
price per kW over priced systems only, a battery, the file's -1 as missing and as the unknown segment, a system with no
date or one after the file's date left out; a file without a needed column stopping the run. No network.

    python -m unittest tests.test_session2015 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import lbnl_tracking_the_sun as T  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def systems(rows):
    return pd.DataFrame(rows, columns=T.COLS)


class Summary(unittest.TestCase):
    def test_rows(self):
        d = systems([
            ["2023-05-01", 5.0, 15000.0, "RES", -1.0],
            ["2023-07-01", 10.0, 30000.0, "RES", 13.5],
            ["2023-08-01", 4.0, -1.0, "RES", -1.0],      # no price: counts, its size counts, not priced
            ["2023-09-01", -1.0, 20000.0, "RES", -1.0],  # no size: counts, not in capacity, not priced
            ["2022-01-15", 100.0, 200000.0, "-1", -1.0],  # the file's missing segment
            [None, 7.0, 21000.0, "COM", -1.0],           # no date: no row
            ["2038-03-29", 7.0, 21000.0, "COM", -1.0],   # after the file's date: no row
        ])
        rows, no_year = T.summarise(d, "AZ", BASE, cutoff=pd.Timestamp("2025-02-28"))
        self.assertEqual(no_year, 2)
        got = {(r["entity"], r["variable"], r["ts_utc"][:4]): r for r in rows}
        res = lambda v: got[("tts:az_res", v, "2023")]["value"]  # noqa: E731
        self.assertEqual((res("systems"), res("systems_priced"), res("systems_battery")), (4, 2, 1))
        self.assertAlmostEqual(res("capacity_dc"), 0.019)
        self.assertEqual(res("price_median"), 3000.0)
        self.assertEqual(got[("tts:az_res", "price_median", "2023")]["unit"], "USD/kW")
        self.assertEqual(got[("tts:az_res", "capacity_dc", "2023")]["unit"], "MW")
        u = got[("tts:az_unknown", "systems", "2022")]
        self.assertEqual((u["x_segment"], u["geo"], u["freq"]), ("unknown", "US-AZ", "P1Y"))
        self.assertFalse(any(k[0] == "tts:az_com" for k in got))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            T.summarise(systems([["2023-01-01", 5.0, 1.0, "RES", -1.0]]).drop(columns=["pv_system_size_dc"]), "AZ", BASE)

    def test_slug(self):
        self.assertEqual(T.slug("NON-PROFIT"), "non_profit")


if __name__ == "__main__":
    unittest.main()
