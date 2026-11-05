"""Session 625: EIA's natural gas exports and imports by country. Held on real records (U.S. natural gas exports, January
2026, 833,543 MMcf; the price of LNG re-exports to Argentina): MMcf as volume and USD/Mcf as price, the area code in
the series, an unknown area or unit stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_trade as G  # noqa: E402
import release_v1 as R  # noqa: E402

US = {"period": "2026-01", "duoarea": "NUS-Z00", "area-name": "U.S.", "product": "EPG0", "process": "EEX", "series": "N9130US2",
      "series-description": "U.S. Natural Gas Exports (MMcf)", "value": "833543", "units": "MMCF"}
AR = {"period": "2026-01", "duoarea": "NUS-NAT", "product": "EPG0", "process": "ERE", "series": "NGM_EPG0_ERE_NUS-NAT_DMCF",
      "series-description": "Price of Liquefied U.S. Natural Gas Re-Exports to Argentina (Dollars per Thousand Cubic Feet)",
      "value": "9.12", "units": "$/MCF"}


class TheRows(unittest.TestCase):
    def test_volume_and_price(self):
        t = G.rows([US, AR], "u", "r", "natural-gas/move/expc")
        self.assertEqual(list(t["variable"]), ["volume", "price"])
        self.assertEqual(list(t["unit"]), ["MMcf", "USD/Mcf"])
        self.assertEqual((t.iloc[0]["entity"], t.iloc[0]["value"], t.iloc[0]["ts_utc"], t.iloc[0]["source"]),
                         ("eia_gas_trade:N9130US2", 833543.0, "2026-01-01T00:00:00Z", "eia:natural-gas/move/expc"))

    def test_an_unknown_area_or_unit_stops(self):
        for bad in (dict(US, duoarea="R10"), dict(US, units="BCF")):
            with self.assertRaises(RuntimeError):
                G.rows([bad], "u", "r", "natural-gas/move/expc")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_gas_trade_country_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_gas_trade_country_monthly", R.STORAGE_HELD["eia_gas_trade_country_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_gas_trade.py", "tests/test_session625.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
