"""Session 2516: NVE's reservoir statistics (Norway's hydropower reservoirs a week, from 1995).

Energy Research Warehouse (ERW). Tests warehouse/connectors/nve_norway_reservoirs.py on an answer built here (made up for
the test, not NVE's): the three area types named, the share times 100 and TWh to MWh, a field without a number with no
row, the date kept as the week's stock date; an unknown area type, a week given twice, a bad date and an answer that is
not a list stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2516 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nve_norway_reservoirs as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def rec(kind, nr, day="2026-10-18", share=0.5, stored=10.0, cap=20.0):
    return {"dato_Id": day, "omrType": kind, "omrnr": nr, "iso_aar": 2026, "iso_uke": 42, "fyllingsgrad": share,
            "fylling_TWh": stored, "kapasitet_TWh": cap}


class Parse(unittest.TestCase):
    def test_rows(self):
        t = S.parse([rec("NO", 0), rec("EL", 2, share=None), rec("VASS", 3)], BASE)
        r = {(e, v): x for e, v, x in zip(t.entity, t.variable, t.value)}
        self.assertEqual(r[("nve:no:no", "filling_share")], 50.0)
        self.assertEqual(r[("nve:no:no", "stored_energy")], 10e6)
        self.assertEqual(r[("nve:no:region_3", "capacity")], 20e6)
        self.assertNotIn(("nve:no:no2", "filling_share"), r)
        self.assertIn(("nve:no:no2", "capacity"), r)
        self.assertEqual(set(t.ts_utc), {"2026-10-18T00:00:00Z"})
        self.assertEqual(set(t.freq), {"P1W"})
        self.assertEqual(set(t.x_iso_week), {"2026-W42"})

    def test_stops(self):
        for bad in ([rec("XX", 1)], [rec("EL", 1), rec("EL", 1)], [rec("NO", 0, day="18.10.2026")], {"a": 1}):
            with self.assertRaises(RuntimeError):
                S.parse(bad, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
