"""Session 10220 (congestion audit, finding 3): the window a figure covers, and the days it is dated by.

/congestion said "324 days held in 2026" and titled the places' table "2026" without saying the year ends on the newest
day held (20 November 2026 on the file built that day); CAISO's places start on 10 August 2023, so their "2023" is under
five months; and "Bound N hours from <first> to <last>" printed UTC days while the decisions say each operator's own
clock (an SPP hour from 18:00 Central standard time is the next UTC day).

The first class shows the facts from the page file (passes on main). The second holds the words of the fix (fails on
main). Printing the operator's own days in place of the UTC days would move dates a reader sees: for Samuel's ruling.
"""
import datetime as dt
import json
import os
import unittest
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")
TZ = {"spp": ZoneInfo("America/Chicago"), "caiso": ZoneInfo("America/Los_Angeles")}


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def local_day(ts, op):
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ[op]).date().isoformat()


@unittest.skipUnless(os.path.exists(FILE), "the congestion file is not on this machine")
class TheWindowAndItsDays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FILE, encoding="utf-8") as f:
            cls.f = json.load(f)

    def test_the_newest_year_is_not_whole(self):
        for op, O in self.f["constraints"].items():
            y = O["years"][-1]
            last = local_day(O["last"], op)
            self.assertTrue(last.startswith(y))
            days = (dt.date.fromisoformat(last) - dt.date(int(y), 1, 1)).days + 1
            self.assertEqual(O["days_held"][y], days, op)
            self.assertLess(days, 365)

    def test_caiso_places_start_inside_2023(self):
        for p in self.f["places"]["caiso"]:
            self.assertEqual(local_day(p["first"], "caiso"), "2023-08-10")
            self.assertEqual(p["by_year"]["2023"]["hours"], 3457)

    def test_first_and_last_are_utc_days_and_many_differ_from_the_operators(self):
        moved = {}
        for op, O in self.f["constraints"].items():
            n = m = 0
            for c in O["constraints"].values():
                for f in ("first", "last"):
                    n += 1
                    m += local_day(c[f], op) != c[f][:10]
            moved[op] = (m, n)
            self.assertGreater(m, 0, op)
        if self.f["built"].startswith("2026-11-20"):
            self.assertEqual(moved, {"spp": (187, 614), "caiso": (127, 480)})


class TheWordsSayIt(unittest.TestCase):
    def test_the_page_names_the_window_and_the_days(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn('data-window-line="1"', s)
        self.assertIn("the newest day held; the year is not whole", s)
        self.assertIn("(days in UTC, not the operator&apos;s clock)", s)
        self.assertIn('data-months-line="1"', s)
        self.assertIn("the days held differ by place", s)
        self.assertIn('const TZ: Record<string, string> = { spp: "America/Chicago", caiso: "America/Los_Angeles" };', s)
        self.assertNotIn("export const TZ", s)

    def test_the_decision_and_the_note_say_it(self):
        d = src("site", "app", "congestion", "Decisions.tsx")
        self.assertIn("The dates a constraint first and last bound are UTC days", d)
        self.assertIn("The newest year is not whole", d)
        self.assertIn("**Windows and days** (session 10220)", src("docs", "methods", "grid_congestion.md"))

    def test_no_em_dash(self):
        for p in (("site", "app", "congestion", "page.tsx"), ("site", "app", "congestion", "Decisions.tsx"),
                  ("docs", "methods", "grid_congestion.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
