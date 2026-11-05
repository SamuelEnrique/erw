"""Session 2591: CBS Curacao's Manufacturing page (Curacao's electricity production a year, Aqualectra's figures).

Energy Research Warehouse (ERW). Tests warehouse/connectors/cbs_curacao_electricity.py on page text built here (made up for
the test, not CBS's): the header found once, each year's electricity column taken (million kWh to MWh) and the water column
passed over, the source line naming Aqualectra; a header missing, another source, a year missing and a row of another
form stopping the run; the sector rule and the registration. No network.

    python -m unittest tests.test_session2591 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import cbs_curacao_electricity as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def page(rows="2022 14,000,000 800.5 2023 15,000,000 900.0", src="Source: Curacao Water and Power Company (Aqualectra) More"):
    return f"Menu Manufacturing {C.HEAD} {rows} {src} Contact"


class Parse(unittest.TestCase):
    def test_rows(self):
        t = C.parse_text(page(), BASE)
        self.assertEqual(list(t.value), [800500.0, 900000.0])
        self.assertEqual(list(t.ts_utc), ["2022-01-01T00:00:00Z", "2023-01-01T00:00:00Z"])
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        for s in (page().replace(C.HEAD, "Water Production"), page(src="Source: Ministry of Economic Development"),
                  page(rows="2021 14,000,000 800.5 2023 15,000,000 900.0"), page(rows="2022 14,000,000 800.5 2023 n/a 900.0")):
            with self.assertRaises(RuntimeError):
                C.parse_text(s, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_registration(self):
        self.assertEqual(B.sector_of(C.NAME), "power")
        self.assertIn(C.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
