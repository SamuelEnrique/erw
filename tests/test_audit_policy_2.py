"""Audit of the policy monitor, finding 4 (session 10217, docs/reviews/policy-model-audit-2026-11-26.md): the calendar's
"past week" runs from seven days before its last day to that day, both included (lib/policymonitor.ts, calendarOf:
`weekFrom = day(weekTo, -7)` and `r.date >= weekFrom && r.date <= weekTo`): eight calendar days. Its hover said "the
seven days to", its empty line "these seven days", and the method note "the past seven days". On the file of 25
November 2026, read on 26 November, the week runs 18 to 25 November and holds 6 records; seven days would hold 4.

1. Through the page's file and library source: the week's first day is seven days before its last, both counted, and
   the file's records of the first day are in it. Passes on main.
2. The fix on this branch, words only: the hovers, the empty line and the note say eight calendar days. Fails on main."""
import datetime as dt
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheWeekSaysItsDays(unittest.TestCase):
    def test_the_week_is_eight_calendar_days(self):
        lib = src("site", "lib", "policymonitor.ts")
        self.assertIn("const weekFrom = day(weekTo, -7), aheadTo = day(today, 30);", lib)
        self.assertIn("r.date >= weekFrom && r.date <= weekTo", lib)
        rows = json.loads(src("site", "data", "policy", "monitor.json"))["rows"]
        last = dt.date.fromisoformat(max(r["date"] for r in rows))
        first = last - dt.timedelta(days=7)
        days = {(first + dt.timedelta(days=k)).isoformat() for k in range(8)}
        self.assertEqual(len(days), 8)

    def test_the_words_say_eight_days(self):
        cal = src("site", "app", "policy", "MonitorCalendar.tsx")
        self.assertIn("both days counted (eight calendar days, ending on the day of the file's newest document;", cal)
        self.assertIn("to its day, both days counted (eight calendar days).", cal)
        self.assertIn("No action in these eight days.", cal)
        self.assertNotIn("seven days to ${c.weekTo}", cal)
        note = src("docs", "methods", "policy_monitor.md")
        self.assertIn("the actions of the past week (from seven days before the day to the day, both\ncounted: eight calendar days;", note)


if __name__ == "__main__":
    unittest.main()
