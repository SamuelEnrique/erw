"""Session 2808: the SFOE's weekly electricity balance (ogd51), Switzerland's balance on each Wednesday.

Energy Research Warehouse (ERW). Tests warehouse/connectors/bfe_weekly_balance.py on a file built here (made up for the test,
not the SFOE's): GWh written as MWh on the Wednesday's date; Erzeugung_netto written as generation_less_storage_pumps on a day
it is that and as net_generation on a day it is the generation before the pumps; national consumption compared, a case off
counted; a date not a Wednesday and a step other than seven days counted; a header not the file's, a value not a number and a
date given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2808 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import bfe_weekly_balance as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(f'"{c}"' for c in ["Datum"] + list(A.COLUMNS))


def data(netto2="120", use2="125", value="40", day3="2024-12-25", twice=False):
    lines = [HEAD,
             f"2024-12-11,40,30,25,,,,5,10,90,50,15,125",          # netto = 100 - 10: generation less the pumps
             f"2024-12-18,{value},30,25,,,,5,10,90,50,15,125",
             f"{day3},40,30,25,,,,5,0,100,40,15,125",               # no pumping: both measures, read as less the pumps
             f"2025-01-01,40,30,25,10,5,10,,20,{netto2},40,15,{use2}"]  # netto = 120, the generation before the pumps
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t, counts = A.build(data(), "r", "v")
        self.assertEqual(counts["definition"], {"less_pumps": 3, "before_pumps": 1})
        self.assertEqual(counts["use"][0], 4)
        self.assertEqual(len(counts["use"][1]), 0)
        self.assertEqual((counts["not_wednesday"], counts["steps"]), ([], []))
        v = {(r.variable, r.ts_utc[:10]): r.value for r in t.itertuples()}
        self.assertEqual(v[("generation_less_storage_pumps", "2024-12-11")], 90000.0)
        self.assertEqual(v[("net_generation", "2025-01-01")], 120000.0)
        self.assertNotIn(("net_generation", "2024-12-11"), v)
        self.assertEqual(v[("solar", "2025-01-01")], 10000.0)
        self.assertNotIn(("other", "2025-01-01"), v)                         # a blank has no row
        self.assertEqual(set(t.freq), {"P1D"})

    def test_counted(self):
        _, counts = A.build(data(use2="130", day3="2024-12-24"), "r", "v")
        self.assertEqual(len(counts["use"][1]), 1)
        self.assertEqual(counts["not_wednesday"], ["2024-12-24"])
        self.assertEqual(counts["steps"], [("2024-12-18", 6), ("2024-12-24", 8)])
        _, counts = A.build(data(netto2="110"), "r", "v")                    # neither measure
        self.assertEqual(counts["neither"], ["2025-01-01"])

    def test_stops(self):
        for content in (data(value="n.a."), data(twice=True), HEAD.replace("Datum", "Date").encode("utf-8") + b"\n"):
            with self.assertRaises(RuntimeError):
                A.build(content, "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
