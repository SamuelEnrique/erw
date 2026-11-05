"""Session 605: EIA's weekly heating oil and propane prices. Held on a real record (the U.S. residential heating oil price,
2 March 2026): USD/gal kept, EIA's week date as ts_utc, a state's geo, an unknown process or area stops; the table is held
from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_heating_fuel_prices as H  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-03-02", "duoarea": "NUS", "product": "EPD2F", "process": "PRS", "series": "W_EPD2F_PRS_NUS_DPG",
        "series-description": "U.S. Weekly No. 2 Heating Oil Residential Price (Dollars per Gallon)", "value": "4.268", "units": "$/GAL"}


class TheRows(unittest.TestCase):
    def test_a_row(self):
        r = H.rows([REAL], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"], r["freq"], r["geo"]),
                         ("eia_heating_price:W_EPD2F_PRS_NUS_DPG", "residential_price", 4.268, "USD/gal", "2026-03-02T00:00:00Z", "P1W", "US"))

    def test_a_state(self):
        r = H.rows([dict(REAL, duoarea="SPA", series="W_EPD2F_PRS_SPA_DPG")], "u", "r").iloc[0]
        self.assertEqual(r["geo"], "US-PA")

    def test_an_unknown_process_or_area_stops(self):
        for bad in (dict(REAL, process="PG1"), dict(REAL, duoarea="Z99")):
            with self.assertRaises(RuntimeError):
                H.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_heating_fuel_prices_weekly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_heating_fuel_prices_weekly", R.STORAGE_HELD["eia_heating_fuel_prices_weekly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_heating_fuel_prices.py", "tests/test_session605.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
