"""Session 2822: ELES, production and take-over on Slovenia's transmission network an hour.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eles_slovenia_hourly.py on an export built here (made up for the
test, not ELES's): the hour labels read as local clock hours, the spring change day's skipped H03 and the autumn day's 24 of
25 hours (counted), a day not ended at the retrieval not kept, a blank given no row; an export whose header is not ELES's, a
date or hour label not readable, a value not a number and a key given twice stopping the run; the sector rule and the holds.
No network.

    python -m unittest tests.test_session2822 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eles_slovenia_hourly as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ";".join(A.HEAD)


def day(date, hours, value="700"):
    return [f"{date};H{h:02d};1000;990;1200;1210;{value};300;200" for h in hours]


def export(lines):
    return (chr(0xfeff) + HEAD + chr(13) + chr(10) + (chr(13) + chr(10)).join(lines) + chr(13) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_times(self):
        lines = day("28.03.2021", [1, 2] + list(range(4, 25))) + day("31.10.2021", range(1, 25)) + day("01.11.2021", [1])
        t, counts = A.build(export(lines), "2026-10-26T06:45:00Z", "v")
        v = t[t.variable == "nuclear_krsko"].set_index(["x_date", "x_hour"]).ts_utc
        self.assertEqual(v[("28.03.2021", "H01")], "2021-03-27T23:00:00Z")
        self.assertEqual(v[("28.03.2021", "H04")], "2021-03-28T01:00:00Z")    # 03:00 CEST, after the skipped hour
        self.assertEqual(v[("31.10.2021", "H03")], "2021-10-31T00:00:00Z")    # 02:00 read as summer time
        self.assertEqual(v[("31.10.2021", "H04")], "2021-10-31T02:00:00Z")    # 03:00 CET
        self.assertEqual(v[("01.11.2021", "H01")], "2021-10-31T23:00:00Z")
        self.assertEqual(counts["odd_days"], [("2021-10-31", 25, 24), ("2021-11-01", 24, 1)])
        self.assertEqual((len(t), set(t.unit), set(t.freq)), ((23 + 24 + 1) * 7, {"MW"}, {"PT1H"}))

    def test_ended_days_and_blanks(self):
        lines = day("24.10.2026", range(1, 25)) + day("26.10.2026", [1])
        lines[0] = lines[0].replace(";990;", ";;")
        t, counts = A.build(export(lines), "2026-10-26T06:45:00Z", "v")    # 26 October has not ended in Ljubljana
        self.assertEqual((counts["in_progress"], counts["blank"]), (1, 1))
        self.assertEqual(len(t), 24 * 7 - 1)

    def test_stops(self):
        good = day("24.10.2026", [1, 2])
        for content in (export(good).replace(b"datum;ura", b"date;hour"), export(["2026-10-24;H01;1;1;1;1;1;1;1"]),
                        export(["24.10.2026;X01;1;1;1;1;1;1;1"]), export(["24.10.2026;H01;1;n.a.;1;1;1;1;1"]),
                        export(good + good[:1])):
            with self.assertRaises(RuntimeError):
                A.build(content, "2026-10-26T06:45:00Z", "v")
        self.assertTrue(A.is_export(export(good)))
        self.assertFalse(A.is_export(b"<!DOCTYPE html>"))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
