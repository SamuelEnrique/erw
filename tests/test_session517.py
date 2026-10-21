"""Session 517: EIA's natural gas prices by state, a month.

Energy Research Warehouse (ERW). Held on real records of EIA's API (January 2026, Arkansas and the U.S.): the variable is
the process's, USD/Mcf kept, the area as geo, a withheld figure with no row, an unknown process, unit or area stops the
run; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_prices_state as G  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = [
    {"period": "2026-01", "duoarea": "SAR", "process": "PCS", "series": "N3020AR3", "series-description": "Arkansas Price of Natural Gas Sold to Commercial Consumers (Dollars per Thousand Cubic Feet)", "value": "12.11", "units": "$/MCF"},
    {"period": "2026-01", "duoarea": "NUS", "process": "PCS", "series": "N3020US3", "series-description": "U.S. Price of Natural Gas Sold to Commercial Consumers (Dollars per Thousand Cubic Feet)", "value": "11.26", "units": "$/MCF"},
    {"period": "2026-01", "duoarea": "SAR", "process": "PEU", "series": "N3045AR3", "series-description": "Arkansas Natural Gas Price Sold to Electric Power Consumers (Dollars per Thousand Cubic Feet)", "value": None, "units": "$/MCF"},
    {"period": "2026-01", "duoarea": "NUS", "process": "PEU", "series": "N3045US3", "series-description": "U.S. Natural Gas Electric Power Price (Dollars per Thousand Cubic Feet)", "value": "10.5", "units": "$/MCF"},
]


class TheRows(unittest.TestCase):
    def setUp(self):
        self.t = G.rows(REAL, "https://api.eia.gov/v2/natural-gas/pri/sum/data/", "2026-10-21T20:06:00Z").set_index("entity")

    def test_withheld_has_no_row(self):
        self.assertEqual(sorted(self.t.index), ["eia_gas_price:PCS:NUS", "eia_gas_price:PCS:SAR", "eia_gas_price:PEU:NUS"])

    def test_values(self):
        r = self.t.loc["eia_gas_price:PCS:SAR"]
        self.assertEqual((r["variable"], r["value"], r["unit"], r["geo"], r["ts_utc"], r["freq"]),
                         ("price_commercial", 12.11, "USD/Mcf", "US-AR", "2026-01-01T00:00:00Z", "P1M"))
        self.assertEqual(self.t.loc["eia_gas_price:PEU:NUS", "geo"], "US")
        self.assertEqual(self.t.loc["eia_gas_price:PEU:NUS", "variable"], "price_electric_power")

    def test_unknown_process_unit_or_area_stops(self):
        for bad in (dict(REAL[0], process="VFA"), dict(REAL[0], units="$/MMBTU"), dict(REAL[0], duoarea="R10")):
            with self.assertRaises(RuntimeError):
                G.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_gas_prices_state_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_gas_prices_state_monthly", R.STORAGE_HELD["eia_gas_prices_state_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_gas_prices_state.py", "tests/test_session517.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
