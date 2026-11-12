"""Session 2864: the health summary's blind spot (5 November 2026).

Energy Research Warehouse (ERW). From 31 October to 5 November 2026 the daily run stopped at its first step every day,
and each day's summary read "3 failures" over some 650 steps, with no word that no price had reached main for six days.
warehouse/health.py summary now opens with "Stale on main": every scheduled job whose last success is older than its
schedule allows (the daily run's commit on main, 1 day; the Roundup's, 8 days; the hourly network's last ok step,
3 hours), with the days; and a job every one of whose runs failed at its first step is counted as failed for the whole
day. A failed step's reason is no longer a library's warning. No request, no model call: every read is given.
"""
import datetime as dt
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import health  # noqa: E402

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 11, 5, 20, 0, tzinfo=UTC)


def row(at, wf, run, step, status, reason=""):
    return {"at": at, "workflow": wf, "run_id": run, "step": step, "status": status, "reason": reason}


# the day of 4 November 2026 as erw_health held it, in short: two daily runs, each failed at its first step
DAY = [row("2026-11-04T14:21:00+00:00", "daily prices", 41843237101, "merge tests", "failed", "FAILED (failures=5, errors=2)"),
       row("2026-11-04T14:22:00+00:00", "daily prices", 41843237101, "health summary", "ok"),
       row("2026-11-04T20:54:00+00:00", "daily prices", 41908133445, "merge tests", "failed", "FAILED (failures=5, errors=2)"),
       row("2026-11-04T03:05:00+00:00", "hourly network", 1, "network", "ok"),
       row("2026-11-04T04:05:00+00:00", "hourly network", 2, "network", "failed", "Error: x"),
       row("2026-11-04T04:06:00+00:00", "hourly network", 2, "load", "ok"),
       row("2026-11-04T05:05:00+00:00", "hourly network", 3, "start", "skipped", "a duplicate"),
       row("2026-11-04T17:57:00+00:00", "local:SU-4QC3QR3", None, "dm_test_findings", "failed", "FAILED (failures=1)")]


class WholeDay(unittest.TestCase):
    def test_a_job_whose_every_run_stopped_at_its_first_step_failed_for_the_day(self):
        self.assertEqual(health.whole_day_failures(DAY), {"daily prices": "merge tests"})

    def test_a_job_with_one_good_run_did_not(self):
        rows = DAY + [row("2026-11-04T22:00:00+00:00", "daily prices", 42, "merge tests", "ok"), row("2026-11-04T22:30:00+00:00", "daily prices", 42, "daily run", "ok")]
        self.assertEqual(health.whole_day_failures(rows), {})

    def test_the_headline_says_so(self):
        md = health.render("2026-11-04", DAY)
        self.assertIn("**4 failures** over 8 recorded steps. **1 job failed for the whole day**, every run stopped at its first step: daily prices (merge tests).", md)
        self.assertNotIn("Stale on main", md)                     # no list given: the line is left out
        self.assertNotIn(chr(0x2014), md)


class StaleOnMain(unittest.TestCase):
    COMMITS = [(dt.datetime(2026, 10, 30, 16, 27, tzinfo=UTC), "Daily prices 2026-10-30: ok: ercot caiso"),
               (dt.datetime(2026, 11, 1, 23, 28, tzinfo=UTC), "Energy Roundup 2026-W44"),
               (dt.datetime(2026, 11, 5, 18, 48, tzinfo=UTC), "Page files 2026-11-05 (the data machine's daily run)"),
               # session 3754: the health summary's own commit, within its day
               (dt.datetime(2026, 11, 5, 14, 30, tzinfo=UTC), "Health summary 2026-11-04 (warehouse/health.py)")]
    LATEST = NOW - dt.timedelta(minutes=20)

    def test_the_daily_run_six_days_stale_and_the_others_within_their_limits(self):
        st = health.stale_on_main(now=NOW, commits=self.COMMITS, oks={"hourly network": NOW - dt.timedelta(hours=1), "latest prices": self.LATEST})
        self.assertEqual([(s[0], round(s[3], 1), s[4]) for s in st], [("daily prices", 6.1, 1.0)])
        line = health.stale_line(st)
        self.assertEqual(line, "**Stale on main:** daily prices, 6.1 days (its last commit on main, 'Daily prices ...', 2026-10-30 16:27 UTC; allowed 1 day).")
        md = health.render("2026-11-04", DAY, st)
        self.assertEqual(md.splitlines()[2], line)                # the first line under the title

    def test_the_roundup_past_eight_days_and_the_network_past_three_hours(self):
        st = health.stale_on_main(now=NOW + dt.timedelta(days=5), commits=self.COMMITS, oks={"hourly network": NOW - dt.timedelta(hours=4), "latest prices": self.LATEST})
        self.assertEqual([s[0] for s in st], ["daily prices", "energy roundup", "hourly network", "latest prices", "health summary"])
        self.assertIn("latest prices, 120.3 hours (its last ok step in erw_health", health.stale_line(st))
        self.assertIn("allowed 1 hour)", health.stale_line(st))
        self.assertIn("hourly network, 124.0 hours (its last ok step in erw_health", health.stale_line(st))   # session 2884: in hours
        self.assertIn("allowed 3 hours", health.stale_line(st))
        self.assertIn("allowed 8 days", health.stale_line(st))

    def test_none_found_in_the_window(self):
        st = health.stale_on_main(now=NOW, commits=[], oks={"hourly network": None})
        self.assertEqual([(s[0], s[2]) for s in st], [("daily prices", None), ("energy roundup", None), ("hourly network", None),
                                                       ("latest prices", None), ("health summary", None)])
        self.assertIn("daily prices, none in 30 days", health.stale_line(st))

    def test_nothing_stale_and_a_read_that_failed(self):
        fresh = [(NOW - dt.timedelta(hours=5), "Daily prices 2026-11-05: ok"), (NOW - dt.timedelta(days=3), "Energy Roundup 2026-W45"),
                 (NOW - dt.timedelta(hours=6), "Health summary 2026-11-04 (warehouse/health.py)")]
        st = health.stale_on_main(now=NOW, commits=fresh, oks={"hourly network": NOW - dt.timedelta(minutes=30), "latest prices": self.LATEST})
        self.assertEqual(st, [])
        self.assertTrue(health.stale_line(st).startswith("**Stale on main:** none ("))
        self.assertEqual(health.stale_line("HTTPError: 403"), "**Stale on main:** not read (HTTPError: 403).")

    def test_a_shallow_checkout_reads_githubs_api(self):
        class P:
            def __init__(self, out):
                self.stdout, self.returncode = out, 0
        asked = []

        class R:
            def raise_for_status(self):
                pass

            def json(self):
                return [{"commit": {"committer": {"date": "2026-10-30T16:27:00Z"}, "message": "Daily prices 2026-10-30: ok\n\nmore"}}]

        def get(url, **kw):
            asked.append((url, kw["params"]))
            return R()
        cs = health.main_commits(NOW - dt.timedelta(days=30), run=lambda *a, **k: P("true\n"), get=get)
        self.assertEqual(cs, [(dt.datetime(2026, 10, 30, 16, 27, tzinfo=UTC), "Daily prices 2026-10-30: ok")])
        self.assertEqual(len(asked), 1)
        self.assertTrue(asked[0][0].endswith("/commits"))
        self.assertEqual((asked[0][1]["sha"], asked[0][1]["since"]), ("main", "2026-10-06T20:00:00Z"))

    def test_a_full_checkout_reads_git_and_asks_nothing(self):
        class P:
            def __init__(self, out):
                self.stdout, self.returncode = out, 0
        calls = []

        def run(cmd, **kw):
            calls.append(cmd)
            return P("false\n") if "rev-parse" in cmd else P("2026-10-30T09:27:00-07:00\tDaily prices 2026-10-30: ok\n")
        cs = health.main_commits(NOW, run=run, get=lambda *a, **k: self.fail("no request"))
        self.assertEqual(cs, [(dt.datetime(2026, 10, 30, 16, 27, tzinfo=UTC), "Daily prices 2026-10-30: ok")])
        self.assertEqual(calls[1][:3], ["git", "log", "origin/main"])


class TheSummaryFile(unittest.TestCase):
    def test_a_summary_written_elsewhere_reads_nothing_and_has_no_stale_line(self):
        with tempfile.TemporaryDirectory() as d:
            path, _ = health.summary("2026-11-04", out_dir=d, rows=DAY)
            with open(path, encoding="utf-8") as f:
                text = f.read()
        self.assertNotIn("Stale on main", text)
        self.assertIn("failed for the whole day", text)

    def test_a_given_list_is_written_first(self):
        st = [("daily prices", "its last commit on main, 'Daily prices ...'", dt.datetime(2026, 10, 30, 16, 27, tzinfo=UTC), 6.15, 1.0)]
        with tempfile.TemporaryDirectory() as d:
            path, _ = health.summary("2026-11-04", out_dir=d, rows=DAY, stale=st)
            with open(path, encoding="utf-8") as f:
                self.assertEqual(f.read().splitlines()[2], health.stale_line(st))

    def test_the_workflow_gives_the_step_a_token_for_the_api(self):
        with open(os.path.join(ROOT, ".github", "workflows", "daily-prices.yml"), encoding="utf-8") as f:
            wf = f.read()
        step = wf[wf.index("- name: Write yesterday's health summary"):]
        step = step[:step.index("run: |")]
        self.assertIn("GH_TOKEN: ${{ github.token }}", step)


class TheReason(unittest.TestCase):
    def test_a_librarys_warning_is_not_why(self):
        tail = ["FAIL: test_x (test_session701.Energy.test_x)", "Ran 7314 tests in 586.416s", "FAILED (failures=5, errors=2)",
                "Warning: The 'generic' unit for NumPy timedelta is deprecated, and will raise an error in the future."]
        self.assertEqual(health.reason_of(tail, True), "FAILED (failures=5, errors=2)")
        self.assertEqual(health.reason_of(["a", "Traceback", "ValueError: x", "exit"], True), "ValueError: x")   # session 61's case


if __name__ == "__main__":
    unittest.main()
