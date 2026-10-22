"""Session 626: EIA's underground natural gas storage capacity. Held on a real record (the East region's total underground
storage capacity, January 2026, 2,187,730 MMcf): MMcf kept, a state's geo, an AGA region of the early years accepted,
a process in the wrong unit or an unknown area stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_storage_capacity as C  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-01", "duoarea": "R83", "area-name": "NA", "product": "EPG0", "process": "SAC", "series": "N5290832",
        "series-description": "East Region Natural Gas Total Underground Storage Capacity (MMcf)", "value": "2187730", "units": "MMCF"}


class TheRows(unittest.TestCase):
    def test_a_row(self):
        r = C.rows([REAL], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"], r["geo"]),
                         ("eia_gas_storage_capacity:N5290832", "total_capacity", 2187730.0, "MMcf", "2026-01-01T00:00:00Z", "US"))

    def test_a_state_a_count_and_an_aga_region(self):
        t = C.rows([dict(REAL, duoarea="SPA", process="SAD", units="COUNT", series="N5010PA2", value="49"),
                    dict(REAL, duoarea="R87", series="N5290872")], "u", "r")
        self.assertEqual(list(t["geo"]), ["US-PA", "US"])
        self.assertEqual((t.iloc[0]["variable"], t.iloc[0]["unit"]), ("storage_fields", "count"))

    def test_the_wrong_unit_or_area_stops(self):
        for bad in (dict(REAL, units="COUNT"), dict(REAL, duoarea="R99")):
            with self.assertRaises(RuntimeError):
                C.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_gas_storage_capacity_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_gas_storage_capacity_monthly", R.STORAGE_HELD["eia_gas_storage_capacity_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_gas_storage_capacity.py", "tests/test_session626.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()
