"""Session 10000 (chain 701, row 41 of docs/state/data_requests_five_tools.md): the consumer price index (CPI-U, as EIA's
STEO carries it, series CICPIUS, index 1982-1984 = 1.00) is read monthly from January 1990 by eia_steo.py, one request
more a run. No network: the rows are built from a page of EIA's own shape."""
import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_steo as E  # noqa: E402


class TheConsumerPriceIndex(unittest.TestCase):
    def test_the_series_and_its_first_month(self):
        self.assertEqual(E.MONTHLY_LONG, ["CICPIUS"])
        self.assertEqual(E.MONTHLY_LONG_FIRST, "1990-01")
        self.assertNotIn("CICPIUS", E.wanted(["CICPIUS", "NGHHUUS"]))   # asked on its own, not in the 2020 list

    def test_the_rows_as_eia_gives_them(self):
        page = [{"period": "1990-01", "seriesId": "CICPIUS", "seriesDescription": "Consumer Price Index (all urban consumers)",
                 "value": "1.275", "unit": "Index, 1982-1984=1.00"},
                {"period": "2026-12", "seriesId": "CICPIUS", "seriesDescription": "Consumer Price Index (all urban consumers)",
                 "value": "3.36", "unit": "Index, 1982-1984=1.00"}]
        t = E.rows(page, dt.date(2026, 11, 10), "https://api.eia.gov/v2/steo/data/", "2026-11-27T18:50:00Z")
        self.assertEqual(list(t["entity"]), ["eia_steo:CICPIUS"] * 2)
        self.assertEqual(list(t["unit"]), ["index", "index"])
        self.assertEqual(list(t["value"]), [1.275, 3.36])
        self.assertEqual(list(t["x_kind"]), ["history", "forecast"])
        self.assertEqual(t["ts_utc"].iloc[0], "1990-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
