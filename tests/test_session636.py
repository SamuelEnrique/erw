"""Sessions 632 and 636: EIA's crude oil imports by country of origin, destination and grade. Held on a real record
(Algeria to PADD 1's ports, light sweet, January 2026, 658 kbbl): kbbl kept, EIA's ids in the entity, a region origin,
an unknown destination type or grade stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_crude_imports_detail as C  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-01", "originId": "CTY_AG", "originName": "Algeria", "originType": "CTY", "originTypeName": "Country",
        "destinationId": "PP_1", "destinationName": "PADD1 (East Coast)", "destinationType": "PP", "destinationTypeName": "Port PADD",
        "gradeId": "LSW", "gradeName": "Light Sweet", "quantity": "658", "quantity-units": "thousand barrels"}


class TheRows(unittest.TestCase):
    def test_a_row(self):
        r = C.rows([REAL], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"]),
                         ("eia_crude_imports:CTY_AG:PP_1:LSW", "imports", 658.0, "kbbl", "2026-01-01T00:00:00Z"))
        self.assertEqual(r["node"], "Algeria to PADD1 (East Coast) (Port PADD), Light Sweet")

    def test_a_region_or_unknown_type_stops(self):
        for bad in (dict(REAL, originType="REG"), dict(REAL, destinationType="XX"), dict(REAL, gradeId="ZZZ")):
            with self.assertRaises(RuntimeError):
                C.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_crude_imports_detail_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_crude_imports_detail_monthly", R.STORAGE_HELD["eia_crude_imports_detail_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_crude_imports_detail.py", "tests/test_session636.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
