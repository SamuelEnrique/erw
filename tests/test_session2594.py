"""Session 2594: the Government of Jersey's Energy Trends 2025, the electricity column of its energy balances (2023 to 2025).

Energy Research Warehouse (ERW). Tests warehouse/connectors/je_jersey_electricity.py on page lines built here (made up for
the test, not the report's): each balance found by its title, the electricity column (the third of four figures) taken and
stated in MWh at 11.63 a toe, a footnote number after a label removed, the toe kept; a title found twice, a row missing, a
supply that misses its parts and sectors that miss final consumption stopping the run; the sector rule and the holds. No
network.

    python -m unittest tests.test_session2594 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import je_jersey_electricity as J  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def balance(title, supply="1,100", final="1,000", drop=None):
    rows = [("Production", "100"), ("Net Imports17", "1,000"), ("Stock change", "0"), ("Primary supply", supply),
            ("Statistical difference18", "-10"), ("Primary demand", "1,110"), ("Electricity Generation", "5"),
            ("Energy industry own use and losses", "100"), ("Final consumption", final), ("Commercial", "400"), ("Residential", "500"),
            ("Road", "50"), ("Air", "0"), ("Marine", "0"), ("Agriculture", "50")]
    lines = [title, "Liquid", "Gas Electricity Total", "fuels"]
    for label, e in rows:
        if label != drop:
            lines.append(f"{label} 7,000 0 {e} 9,999")
    return lines + ["17 Net Imports is the sum of imports minus exports", "13"]


def pages(**kw):
    return [["Contents"], balance("Table 5: Energy Balance for Jersey, 2025; toe", **kw),
            balance("Table A3: Energy Balance for Jersey, 2023 (updated), toe"), balance("Table A5: Energy Balance for Jersey, 2024 (updated); toe")]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = J.parse_pages(pages(), BASE)
        r = {(e.split(":")[-1], ts[:4]): (v, x) for e, ts, v, x in zip(t.entity, t.ts_utc, t.value, t.x_toe)}
        self.assertEqual(r[("net_imports", "2025")], (11630.0, 1000.0))
        self.assertEqual(r[("statistical_difference", "2023")], (-116.3, -10.0))
        self.assertEqual(r[("residential", "2024")][0], 5815.0)
        self.assertEqual(len(t), 15 * 3)
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [pages() + [balance("Table 5: Energy Balance for Jersey, 2025; toe")], pages(drop="Road"), pages(supply="1,200"),
               pages(final="1,100")]
        for p in bad:
            with self.assertRaises(RuntimeError):
                J.parse_pages(p, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(J.NAME), "power")
        self.assertIn(J.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {J.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
