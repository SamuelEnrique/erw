"""Session 11407 (chain 770, part C): the ruling on congestion audit finding 3 readied, a constraint's first and last
binding days on the operator's own clock.

The file stamps each hour in UTC (the start of the hour). /congestion printed "Bound N hours from <first> to <last>" as
UTC days beside a clock decision that promises each operator's own clock. Carried over from
tests/test_audit_congestion_3.py (branch wip/audit-congestion-3): here the page turns the two stamps into the operator's
day (Central for SPP, Pacific for CAISO). On the file built 2026-11-28, 182 of SPP's 614 first and last dates and 125
of CAISO's 480 move back a day, none forward; the default constraint's two dates do not move.
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
    """What page.tsx's localDay gives: the operator's calendar day of a UTC stamp."""
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ[op]).date().isoformat()


@unittest.skipUnless(os.path.exists(FILE), "the congestion file is not on this machine")
class TheOperatorsDays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FILE, encoding="utf-8") as f:
            cls.f = json.load(f)

    def test_dates_move_back_a_day_and_never_forward(self):
        moved = {}
        for op, O in self.f["constraints"].items():
            n = back = fwd = 0
            for c in O["constraints"].values():
                for f in ("first", "last"):
                    n += 1
                    back += local_day(c[f], op) < c[f][:10]
                    fwd += local_day(c[f], op) > c[f][:10]
            self.assertGreater(back, 0, op)
            self.assertEqual(fwd, 0, op)
            moved[op] = (back, n)
        if self.f["built"].startswith("2026-11-28"):
            self.assertEqual(moved, {"spp": (182, 614), "caiso": (125, 480)})

    def test_an_spp_evening_hour_is_the_day_before_in_utc(self):
        self.assertEqual(local_day("2026-11-19T00:00:00Z", "spp"), "2026-11-18")
        self.assertEqual(local_day("2026-07-02T00:00:00Z", "caiso"), "2026-07-01")
        self.assertEqual(local_day("2026-11-18T06:00:00Z", "spp"), "2026-11-18")


class ThePageDoesIt(unittest.TestCase):
    def test_the_constraint_line_prints_the_operators_days(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn("Bound {whole(C.hours)} hours from {localDay(C.first, op)} to {localDay(C.last, op)}", s)
        self.assertIn('<span data-local-days="1">(days on the operator&apos;s clock)</span>', s)
        self.assertNotIn("C.first.slice(0, 10)", s)
        self.assertNotIn("days in UTC", s)

    def test_the_decision_and_the_note_say_it(self):
        d = src("site", "app", "congestion", "Decisions.tsx")
        self.assertIn("The dates a constraint first and last bound are the operator's own days too", d)
        self.assertNotIn("are UTC days", d)
        n = src("docs", "methods", "grid_congestion.md")
        self.assertIn("the page prints their days on the operator's clock (session 11407", n)

    def test_no_em_dash(self):
        for p in (("site", "app", "congestion", "page.tsx"), ("site", "app", "congestion", "Decisions.tsx"),
                  ("docs", "methods", "grid_congestion.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
