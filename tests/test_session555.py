"""Session 555: EIA's petroleum supply and disposition, eight products, a month. Held on real records (June 2026, the
U.S. product supplied of crude oil and petroleum products): thousand barrels and thousand barrels a day as two variables of
two series, the month as ts_utc, an unknown process or area stops; the table is held from /data and Redivis v1 until
uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_petroleum_snd as P  # noqa: E402
import release_v1 as R  # noqa: E402

MONTH = {"period": "2026-06", "duoarea": "NUS", "product": "EP00", "process": "VPP", "series": "MTTUPUS1",
         "series-description": "U.S. Product Supplied of Crude Oil and Petroleum Products (Thousand Barrels)", "value": "622077", "units": "MBBL"}
DAY = dict(MONTH, series="MTTUPUS2", value="20736", units="MBBL/D",
           **{"series-description": "U.S. Product Supplied of Crude Oil and Petroleum Products (Thousand Barrels per Day)"})


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = P.rows([MONTH, DAY], "u", "r").set_index("entity")
        m = t.loc["eia_petroleum_snd:MTTUPUS1"]
        self.assertEqual((m["variable"], m["value"], m["unit"], m["ts_utc"], m["freq"]), ("product_supplied", 622077.0, "kbbl", "2026-06-01T00:00:00Z", "P1M"))
        d = t.loc["eia_petroleum_snd:MTTUPUS2"]
        self.assertEqual((d["variable"], d["unit"]), ("product_supplied_per_day", "kbbl/d"))

    def test_eight_products(self):
        self.assertEqual(len(P.PRODUCTS), 8)
        self.assertIn("EP00", P.PRODUCTS)

    def test_an_unknown_process_or_area_stops(self):
        for bad in (dict(MONTH, process="XYZ"), dict(MONTH, duoarea="SCA")):
            with self.assertRaises(RuntimeError):
                P.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_petroleum_snd_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_petroleum_snd_monthly", R.STORAGE_HELD["eia_petroleum_snd_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_petroleum_snd.py", "tests/test_session555.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
