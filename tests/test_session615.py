"""Session 615: EIA's refinery and blender net input, a month. Held on real records (the Indiana-Illinois-Kentucky refining
district's net input of crude oil and petroleum products, March 2026, in thousand barrels and thousand barrels a
day): kbbl and kbbl/d kept, the month's first day as ts_utc, an unknown area, unit or process stops; the table is held
from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_refinery_inputs as I  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-03", "duoarea": "R2A", "area-name": "NA", "product": "EP00", "product-name": "Crude Oil and Petroleum Products",
        "process": "YIR", "process-name": "Refinery and Blender Net Input", "series": "MTTRI2A1",
        "series-description": "Refining District Indiana-Illinois-Kentucky Refinery and Blender Net Input of Crude Oil and Petroleum Products (Thousand Barrels)",
        "value": "82847", "units": "MBBL"}


class TheRows(unittest.TestCase):
    def test_both_units(self):
        t = I.rows([REAL, dict(REAL, series="MTTRI2A2", value="2672", units="MBBL/D")], "u", "r")
        self.assertEqual(list(t["variable"]), ["net_input", "net_input_per_day"])
        self.assertEqual(list(t["unit"]), ["kbbl", "kbbl/d"])
        self.assertEqual((t.iloc[0]["entity"], t.iloc[0]["value"], t.iloc[0]["ts_utc"], t.iloc[0]["freq"]),
                         ("eia_refinery_inputs:MTTRI2A1", 82847.0, "2026-03-01T00:00:00Z", "P1M"))

    def test_an_unknown_area_unit_or_process_stops(self):
        for bad in (dict(REAL, duoarea="R9Z"), dict(REAL, units="B/D"), dict(REAL, process="YPR")):
            with self.assertRaises(RuntimeError):
                I.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_refinery_inputs_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_refinery_inputs_monthly", R.STORAGE_HELD["eia_refinery_inputs_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_refinery_inputs.py", "tests/test_session615.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
