"""Session 2602: Solomon Power's Annual Report 2025, Energy Produced, the Solomon Islands' production by station (2017 to 2025).

Energy Research Warehouse (ERW). Tests warehouse/connectors/siea_solomon_electricity.py on page lines built here (made up for
the test, not the report's): the table found by its title, each station's figures taken and stated in MWh, Henderson's
figures from the line after its label, Ranadi's years printed "Not Available" not written; a title found twice, a station
missing, a short line and stations that miss the total stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2602 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import siea_solomon_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def page(total="13.5 15.7 18.2", lungga="10 11 12", drop=None, twice=False):
    lines = ["Energy produced in 2025 compared with the previous years", "Station 2023 2024 2025",
             f"Lungga {lungga}", "Honiara 1 1.5 2", "Outstations 2 2.5 3", "Henderson", "0.5 0.6 1", "Solar (1 MW)",
             "Ranadi Solar Not", "0.1 0.2", "(50kW) Available", f"Total {total}", "Peak demand 19,296 kW"]
    lines = [ln for ln in lines if not (drop and ln.startswith(drop))]
    return (["Contents"] + lines + (lines[:1] if twice else []))


class Parse(unittest.TestCase):
    def test_rows(self):
        t = S.parse_lines(page(), BASE)
        r = {(e.split(":")[-1], ts[:4]): v for e, ts, v in zip(t.entity, t.ts_utc, t.value)}
        self.assertEqual(r[("lungga", "2025")], 12000.0)
        self.assertEqual(r[("henderson_solar", "2024")], 600.0)
        self.assertEqual(r[("ranadi_solar", "2025")], 200.0)
        self.assertNotIn(("ranadi_solar", "2023"), r)
        self.assertEqual(r[("total", "2023")], 13500.0)
        self.assertEqual(len(t), 5 * 3 + 2)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        for p in (page(twice=True), page(drop="Honiara"), page(lungga="10 11"), page(total="13.5 15.7 19")):
            with self.assertRaises(RuntimeError):
                S.parse_lines(p, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
