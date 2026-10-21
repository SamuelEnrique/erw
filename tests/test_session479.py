"""Session 479: the streak's missing hours. health_days.json counted a day missing only when a job made no run at all,
so pg_cron's six hours of startup timeouts (20 to 21 October 2026) left 21 October green. A job with fewer than half
its expected runs is now listed as short in the day's record; it ends the streak only when SHORT_ENDS_STREAK is set."""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import health  # noqa: E402


def rows(workflow, n):
    return [{"workflow": workflow, "status": "ok", "run_id": str(i), "step": "start", "at": "2026-10-21T00:00"} for i in range(n)]


def full_day(**fewer):
    out = []
    for wf, n in health.EXPECTED.items():
        out += rows(wf, fewer.get(wf.replace(" ", "_"), n))
    return out


class Short(unittest.TestCase):
    def test_a_job_under_half_its_runs_is_short(self):
        rec = health.day_record(full_day(chain_watch=40, latest_prices=47))
        self.assertEqual(rec["short"], ["chain watch", "latest prices"])
        self.assertEqual(rec["missing"], [])

    def test_half_or_more_is_not_short(self):
        self.assertEqual(health.day_record(full_day(chain_watch=48))["short"], [])

    def test_a_daily_job_is_never_short_only_missing(self):
        rec = health.day_record([r for r in full_day() if r["workflow"] != "daily prices"])
        self.assertEqual((rec["short"], rec["missing"]), ([], ["daily prices"]))

    def test_short_days_do_not_end_the_streak_until_ruled(self):
        days = {"2026-10-20": health.day_record(full_day()), "2026-10-21": health.day_record(full_day(chain_watch=40))}
        self.assertEqual(health.green_streak(days), (2, "2026-10-21"))
        with mock.patch.object(health, "SHORT_ENDS_STREAK", True):
            self.assertEqual(health.green_streak(days), (0, "2026-10-21"))


if __name__ == "__main__":
    unittest.main()
