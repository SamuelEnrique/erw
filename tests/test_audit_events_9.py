"""Session 10225 (chain 710, the events audit, finding 9): /events/uri-2021 prints "Largest shortfall against the 2019
and 2020 average for the same day: -186,530.50 MWh on 2021-02-21, after the storm". Uri's baseline is the same calendar
day (the first event, before the weekday rule), and 2021-02-21 was a Sunday set against a Thursday (2019) and a Friday
(2020). By the weekday rule every later event uses (the same weekday 364 and 728 days earlier, both held in the table)
the shortfall that day is -37,630.50 MWh. The page's words say "the same day" and are true of the code; the figure
under the other rule moves, so the ruling is the owner's (docs/reviews/events-model-audit-2026-11-26.md). These tests
pass on main: they show the finding, not a fix.
"""
import csv
import datetime as dt
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROWS = os.path.join(ROOT, "replication", "events", "window_rows.csv")


@unittest.skipUnless(os.path.exists(ROWS), "the replication's public rows are not in this checkout")
class UrisShortfallIsASundayAgainstWeekdays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROWS, encoding="utf-8") as fh:
            cls.v = {r["ts_utc"][:10]: float(r["value"]) for r in csv.DictReader(l for l in fh if not l.startswith("#"))
                     if r["event"] == "uri_2021" and r["entity"] == "eia930:ERCO" and r["variable"] == "net_generation_mwh"}

    def test_the_calendar_rule_gives_the_page(self):
        v = self.v
        cal = {d: v[d] - (v[f"2019{d[4:]}"] + v[f"2020{d[4:]}"]) / 2 for d in v if d.startswith("2021") and f"2019{d[4:]}" in v and f"2020{d[4:]}" in v}
        lo = min(cal, key=cal.get)
        self.assertEqual((lo, round(cal[lo], 2)), ("2021-02-21", -186530.5))
        self.assertEqual([dt.date.fromisoformat(x).strftime("%A") for x in ("2021-02-21", "2019-02-21", "2020-02-21")], ["Sunday", "Thursday", "Friday"])

    def test_the_weekday_rule_gives_a_fifth(self):
        v = self.v
        t = dt.date(2021, 2, 21)
        w = [v[(t - dt.timedelta(days=o)).isoformat()] for o in (364, 728)]
        self.assertEqual(round(v["2021-02-21"] - sum(w) / 2, 2), -37630.5)


if __name__ == "__main__":
    unittest.main()
