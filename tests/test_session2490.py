"""Session 2490: EWA's Statistical Book 2024 (Bahrain's electricity, 2020 to 2024).

Energy Research Warehouse (ERW). Tests warehouse/connectors/ewa_bahrain_electricity.py on page texts built here (made up
for the test, not EWA's): Arabic-Indic digits read as ASCII, GWh and million kWh to MWh, a link's negative flow kept, a
cell "-" with no row, a cell out of its table's form not written and counted, page 10's sums checked against page 9's
and not written, the load table's ratio and increase columns not taken; a missing table, a year out of order and a row
of another width stopping the run; white characters dropped from a page; the sector rule and the holds. No network.

    python -m unittest tests.test_session2490 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ewa_bahrain_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
T = list(S.TABLES)
NL = chr(10)


def rows(cells):
    return NL.join(f"{c} {y}" for c, y in zip(cells, S.YEARS))


P9 = rows(["100 -10 5 - 30 20 25 15 15"] * 5)
P10 = rows(["100 -5 80 25"] * 5)
P12 = rows(["1,000 600 300 0 100 0 0 0 0"] * 5)
P15 = T[3] + NL + rows(["20.0% - 800 - 4,000 5,000"] * 5)
P44 = rows(["50 1 9 5.348 35"] + ["50 1 9 5 35"] * 4)


def pages(p9=P9, p10=P10, p12=P12, p15=P15, p44=P44):
    return [(9, T[0] + NL + "Total GCC Link" + NL + p9), (10, T[1] + NL + p10), (12, T[2] + NL + p12),
            (15, "Development of Electricity Transmission Network" + NL + rows(["1 2 3 4 5 6 7 8"] * 5) + NL + p15),
            (44, T[4] + NL + p44 + NL + "2020 2021 2022 2023 2024")]


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        t = S.parse_text(pages(), BASE, counts)
        r = {(a, b, c): v for a, b, c, v in zip(t.entity, t.variable, t.ts_utc, t.value)}
        y = "2020-01-01T00:00:00Z"
        self.assertEqual(r[("ewa:bh:total", "supply", y)], 100000.0)
        self.assertEqual(r[("ewa:bh:gcc_link", "net_imports", y)], -10000.0)
        self.assertEqual(r[("ewa:bh:al_dur", "sent_out", y)], 30000.0)
        self.assertNotIn(("ewa:bh:al_dur_2", "sent_out", y), r)
        self.assertEqual(r[("ewa:bh:ipp_stations", "sent_out", y)], 80000.0)
        self.assertFalse(any(v.startswith("check_") for v in t.variable))
        self.assertEqual(r[("ewa:bh:total", "capacity_with_links", y)], 1000.0)
        self.assertEqual(r[("ewa:bh:gcc_link", "net_transfer_capacity", y)], 600.0)
        self.assertEqual(r[("ewa:bh:system", "peak_load", y)], 4000.0)
        self.assertEqual(r[("ewa:bh:system", "minimum_load", y)], 800.0)
        self.assertEqual(r[("ewa:bh:system", "installed_capacity", y)], 5000.0)
        self.assertEqual(r[("ewa:bh:domestic", "consumption", y)], 50000.0 - 15000.0)
        self.assertNotIn(("ewa:bh:commercial", "consumption", y), r)
        self.assertEqual(r[("ewa:bh:commercial", "consumption", "2021-01-01T00:00:00Z")], 5000.0)
        self.assertEqual(counts, {"cells out of form": 1})
        self.assertEqual(set(t.unit[t.variable.isin(["peak_load", "max_generation_capacity"])]), {"MW"})
        self.assertEqual(set(t.geo), {"BH"})

    def test_digits(self):
        self.assertEqual(S.ascii_digits(chr(0x0661) + "8,66" + chr(0x0661) + " 2" + chr(0x0660) + "22"), "18,661 2022")

    def test_stops(self):
        bad = [pages(p10=rows(["90 -5 80 25"] * 5)),            # page 10's total not page 9's
               pages(p12=rows(["1,000 600 300"] * 5)),            # a row of another width
               pages(p44=P44.replace("2023", "2019")),            # a year out of order
               pages()[:4]]                                       # a table missing
        for p in bad:
            with self.assertRaises(RuntimeError):
                S.parse_text(p, BASE, {})

    def test_white_dropped(self):
        class Page:
            def __init__(self, objs):
                self.objs = objs

            def filter(self, f):
                return Page([o for o in self.objs if f(o)])

            def extract_text(self):
                return "".join(o["text"] for o in self.objs)
        pg = Page([{"object_type": "char", "text": "2", "non_stroking_color": (0, 0, 0, 0.8)},
                   {"object_type": "char", "text": "9", "non_stroking_color": (1.0, 1.0, 1.0)},
                   {"object_type": "char", "text": chr(0x0660), "non_stroking_color": None}])
        self.assertEqual(S.visible_text(pg), "20")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
