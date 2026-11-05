"""Session 546: SEDS' other series. The table now carries electricity's and natural gas's consumption by sector and
natural gas's prices by sector, in units the vocabulary holds; held on a real record of 2024; a page already saved is
reused.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_seds as S  # noqa: E402

NEW = ["ESRCB", "ESCCB", "ESICB", "ESACB", "NGRCB", "NGCCB", "NGICB", "NGEIB", "NGACB", "NGRCD", "NGCCD", "NGICD", "NGEID", "NGTCD"]


class TheSeries(unittest.TestCase):
    def test_the_new_series_are_asked(self):
        for sid in NEW:
            self.assertIn(sid, S.SERIES)
        self.assertEqual(len(S.SERIES), len(set(S.SERIES)))

    def test_a_real_record(self):
        rec = {"period": 2024, "seriesId": "NGEID", "seriesDescription": "Natural gas price in the electric power sector", "stateId": "TX",
               "value": "2.85", "unit": "Dollars per million Btu"}
        r = S.rows([rec], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["unit"], r["geo"], r["ts_utc"]), ("eia_seds:NGEID:TX", "USD/MMBtu", "US-TX", "2024-01-01T00:00:00Z"))

    def test_saved_pages_are_reused(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "eia_seds.py"), encoding="utf-8") as h:
            src = h.read()
        self.assertIn("ip.raw_cached(CONNECTOR, url)", src)
        self.assertIn('"--offline"', src)
        self.assertNotIn(chr(0x2014), src)


if __name__ == "__main__":
    unittest.main()
