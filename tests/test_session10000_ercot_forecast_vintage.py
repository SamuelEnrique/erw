"""Session 10000 (chain 701, request 5 of docs/state/data_requests_predict.md): ERCOT's 24-hour wind and solar forecast
rows carry the posting's publication time in vintage, and that time is at least 24 hours before the hour. Made-up
postings; no request."""
import importlib.util
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    spec = importlib.util.spec_from_file_location("ewsf_t", os.path.join(ROOT, "warehouse", "connectors", "ercot_wind_solar_forecast.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def posting(day, gen, fc):
    return pd.DataFrame({"DELIVERY_DATE": [day] * 2, "HOUR_ENDING": [1, 2], "DSTFlag": ["N", "N"],
                         "SYSTEM_WIDE_GEN": gen, "STWPF_SYSTEM_WIDE": fc})


class TheVintageIsThePosting(unittest.TestCase):
    def test_the_forecast_rows_name_their_posting(self):
        m = load()
        early = pd.Timestamp("2026-11-24T00:30:00Z")   # more than a day before 2026-11-26 local hour 1
        late = pd.Timestamp("2026-11-25T23:30:00Z")    # under a day before: its forecast is not the 24-hour one
        ps = [(early, posting("11/26/2026", [None, None], [100.0, 110.0])),
              (late, posting("11/26/2026", [90.0, 95.0], [120.0, 130.0]))]
        actual, forecast = m.pairs(ps, "STWPF_SYSTEM_WIDE")
        self.assertEqual(sorted(forecast.tolist()), [100.0, 110.0])
        rows = m.rows("wind", actual, forecast, "ercot:t", "u", "r")
        fc = [r for r in rows if r["variable"] == "wind_forecast_24h_mw"]
        self.assertTrue(fc and all(r["vintage"] == "2026-11-24T00:30:00Z" for r in fc))
        for r in fc:
            self.assertLessEqual(pd.Timestamp(r["vintage"]), pd.Timestamp(r["ts_utc"]) - pd.Timedelta(hours=24))
        self.assertTrue(all(r["vintage"] == "" for r in rows if r["variable"] == "wind_actual_mw"))


if __name__ == "__main__":
    unittest.main()
