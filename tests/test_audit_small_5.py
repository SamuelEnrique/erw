"""Session 10238, the small pages' audit, finding 5 (docs/reviews/small-pages-audit-2026-11-26.md): /about and /subscribe
said the Roundup is sent on Sundays at "4 PM Pacific". It is scheduled at 23:00 UTC (roundup.yml, and pg_cron in
migration 015), which is 4 PM on Pacific daylight time and 3 PM on Pacific standard time (from the first Sunday of
November to the second Sunday of March): on 29 November 2026, 3 PM."""
import os
import re
import unittest
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


def pacific_hour(utc):
    """The US rule since 2007: daylight time from the second Sunday of March 02:00 to the first Sunday of November 02:00."""
    def nth_sunday(y, m, n):
        d = datetime(y, m, 1, tzinfo=timezone.utc)
        return d + timedelta(days=(6 - d.weekday()) % 7 + 7 * (n - 1))
    start = nth_sunday(utc.year, 3, 2) + timedelta(hours=10)
    end = nth_sunday(utc.year, 11, 1) + timedelta(hours=9)
    return (utc + timedelta(hours=-7 if start <= utc < end else -8)).hour


class TheSchedule(unittest.TestCase):
    def test_the_roundup_runs_at_23_utc(self):
        self.assertIn('cron: "0 23 * * 0"', src(".github", "workflows", "roundup.yml"))
        self.assertIn("select cron.schedule('erw-roundup', '0 23 * * 0',", src("warehouse", "supabase", "migrations", "015_scheduler.sql"))

    def test_23_utc_is_4_pm_in_summer_and_3_pm_in_winter(self):
        self.assertEqual(pacific_hour(datetime(2026, 7, 5, 23, tzinfo=timezone.utc)), 16)
        self.assertEqual(pacific_hour(datetime(2026, 11, 29, 23, tzinfo=timezone.utc)), 15)


class ThePages(unittest.TestCase):
    def test_neither_page_says_4_pm_alone(self):
        for p in (("site", "app", "about", "page.tsx"), ("site", "app", "subscribe", "page.tsx")):
            t = re.sub(r"\s+", " ", src(*p))
            self.assertNotIn("(4 PM Pacific)", t)
            self.assertNotIn("Sundays, 4 PM Pacific:", t)

    def test_both_say_the_winter_hour(self):
        self.assertIn("23:00 UTC (4 PM Pacific in summer time; 3 PM from early November to mid-March", re.sub(r"\s+", " ", src("site", "app", "about", "page.tsx")))
        self.assertIn("Sundays, 23:00 UTC (4 PM Pacific in summer time, 3 PM in winter):", src("site", "app", "subscribe", "page.tsx"))


if __name__ == "__main__":
    unittest.main()
