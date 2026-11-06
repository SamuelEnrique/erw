"""Session 2504: NCSI's Energy Statistics 2026, tables 11 and 12 (Oman's electricity by governorate and by source).

Energy Research Warehouse (ERW). Tests warehouse/connectors/ncsi_oman_electricity.py on page texts built here (made up for
the test, not NCSI's): a governorate's nine figures in the years' order (connections, distribution, production), GWh and
thousands scaled, a cell "-" with no row, the name split over two lines found on the line of figures, table 11 printed
twice and read once, table 12's TWh, its title's line not read as a row; table 11's total against table 12's, a row of
another width and the second print differing stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2504 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ncsi_oman_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
NL = chr(10)
ROWS = ["Muscat 476.7 13,555.4 427.9 464.1 13,035.3 483.2 x Muscat 451.0 12,607.6 604.2",
        "Al Buraimai 43.1 773.7 - 42.4 745.1 - x Al Buraimai 41.6 735.9 -",
        "Ash Sharqiyah x",
        "97.4 1,867.5 10,837.3 94.2 1,819.4 10,606.7 Ash Sharqiyah South 91.4 1,671.1 9,896.4 x",
        "Total 617.2 16,196.6 11,265.2 600.8 15,599.8 11,089.9 x Total 584.4 15,014.6 10,500.6 x"]


def p11(rows=ROWS):
    return NL.join(["Table (11)", S.T11, "2025 2024 2023", "Governorate (000)", "Cont.d Table (11)", S.T11] + rows + ["Source: Public Services Regulatory Authority"])


def p12(total=("11.3", "11.1", "10.5")):
    return NL.join(["Table (12)", S.T12, "Item 2025 2024 2023 x", "Diesel 0.6 0.6 0.7 x", "Gas 10.7 10.5 9.8 x",
                    "Total %s %s %s x" % total, "Source: Public Services Regulatory Authority",
                    "Total production of renewable energy stations by type", "Total 4.5 2.4 x"])


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        t = S.parse_text(["intro", p11(), p11(), p12()], BASE, counts)
        r = {(e, v, ts[:4]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("ncsi:om:muscat", "connections", "2025")], 476700.0)
        self.assertEqual(r[("ncsi:om:muscat", "distribution", "2025")], 13555400.0)
        self.assertEqual(r[("ncsi:om:muscat", "production", "2023")], 604200.0)
        self.assertNotIn(("ncsi:om:al_buraimi", "production", "2024"), r)
        self.assertEqual(r[("ncsi:om:ash_sharqiyah_south", "production", "2025")], 10837300.0)
        self.assertEqual(r[("ncsi:om:gas", "production_by_source", "2024")], 10.5e6)
        self.assertEqual(r[("ncsi:om:total", "production_by_source", "2025")], 11.3e6)
        self.assertEqual(counts["table 11 printed"], 2)
        self.assertEqual(set(t.unit[t.variable == "connections"]), {"count"})

    def test_stops(self):
        bad = [["x", p11(), p12(total=("12.3", "11.1", "10.5"))],                                  # the totals differ
               ["x", p11(ROWS[:1] + ["Dhofar 1.0 2.0 3.0"] + ROWS[1:]), p12()],                      # a row of another width
               ["x", p11(), p11([r.replace("476.7", "476.8") for r in ROWS]), p12()],                # the second print differs
               ["x", p12()]]                                                                        # no table 11
        for pages in bad:
            with self.assertRaises(RuntimeError):
                S.parse_text(pages, BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
