"""Session 3938 (chain 267): request 1 of docs/state/data_requests_forecast.md, and the STEO table's second release.

The GDP implicit price deflator (GDPDIUS) is read annual from 2009 into eia_steo_forecasts, unit index, a year from the
release's own on marked forecast. The table keeps each release (vintage), and the validator keys it by vintage only
when the header says decision 77's words: without them the release of 10 November 2026 was refused as 10,176
duplicate keys. Made-up values; no network.
"""
import datetime as dt
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import eia_steo  # noqa: E402


class TheDeflator(unittest.TestCase):
    def test_annual_rows(self):
        data = [{"period": "2025", "seriesId": "GDPDIUS", "seriesDescription": "GDP Implicit Price Deflator", "value": "100.5", "unit": "Index, 2017 = 100"},
                {"period": "2026", "seriesId": "GDPDIUS", "seriesDescription": "GDP Implicit Price Deflator", "value": "102.0", "unit": "Index, 2017 = 100"}]
        t = eia_steo.rows_annual(data, dt.date(2026, 11, 10), "https://example.invalid/", "2026-11-14T00:00:00Z")
        self.assertEqual(list(t["ts_utc"]), ["2025-01-01T00:00:00Z", "2026-01-01T00:00:00Z"])
        self.assertEqual(set(t["unit"]), {"index"})
        self.assertEqual(set(t["freq"]), {"P1Y"})
        self.assertEqual(list(t["x_kind"]), ["history", "forecast"])
        self.assertEqual(eia_steo.ANNUAL, ["GDPDIUS"])

    def test_the_header_keeps_the_revisions(self):
        import erw_validate
        src = open(eia_steo.__file__, encoding="utf-8").read()
        self.assertIn(erw_validate.REVISIONS_KEPT, src)


if __name__ == "__main__":
    unittest.main()
