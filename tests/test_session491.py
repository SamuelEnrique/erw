"""Session 491: EIA's Short-Term Energy Outlook. Each release kept by its date in vintage; a month from the release's
month on is a forecast, an earlier one EIA's history; units into the standard's vocabulary; an unknown unit stops the
run; the wanted series are the retail prices, Henry Hub and the U.S. generation shares."""

import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_steo as st  # noqa: E402

REL = dt.date(2026, 10, 6)


def api(sid, period, value, unit):
    return dict(seriesId=sid, period=period, value=value, unit=unit, seriesDescription=sid)


class Steo(unittest.TestCase):
    def test_forecast_or_history_and_the_vintage(self):
        t = st.rows([api("ESTCU_US", "2026-09", "14.2", "cents per kilowatt hour"), api("ESTCU_US", "2026-10", "13.9", "cents per kilowatthour")],
                    REL, "u", "r")
        self.assertEqual(list(t["x_kind"]), ["history", "forecast"])
        self.assertEqual(set(t["vintage"]), {"2026-10-06T00:00:00Z"})
        self.assertAlmostEqual(t["value"].iloc[0], 0.142)
        self.assertEqual(set(t["unit"]), {"USD/kWh"})

    def test_shares_and_henry_hub(self):
        t = st.rows([api("NGEPSHR_US", "2026-01", "40.5", "percentage"), api("NGHHUUS", "2026-01", "3.10", "dollars per million Btu")], REL, "u", "r")
        self.assertEqual([(u, round(v, 4)) for u, v in zip(t["unit"], t["value"])], [("ratio", 0.405), ("USD/MMBtu", 3.1)])

    def test_an_unknown_unit_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "not in the map"):
            st.rows([api("NGHHUUS", "2026-01", "3.1", "dollars per barrel")], REL, "u", "r")

    def test_the_series_wanted(self):
        self.assertEqual(st.wanted(["ESRCU_US", "ESICU_NEC", "NGHHUUS", "NGHHMCF", "NGEPSHR_US", "PAEPTOT", "ESTCU_US"]),
                         ["ESICU_NEC", "ESRCU_US", "ESTCU_US", "NGEPSHR_US", "NGHHUUS"])

    def test_the_release_date_from_the_page(self):
        self.assertEqual(st.release_date("<p><b>Release Date:</b> October 6, 2026</p>"), REL)


if __name__ == "__main__":
    unittest.main()
