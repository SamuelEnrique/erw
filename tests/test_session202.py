"""Session 202: one alert policy (docs/machines.md, "One alert policy"), the record of days and the green streak.

What is held to:

  a silence is said once: the memory of what was said (rows of erw_health, workflow "alerts") makes a late check
    still send and a doubled check not repeat; without the memory, only the quarter of an hour after 30 minutes;
  a failed step is one email for that failure: not when the step's run before failed too, not for a retry that
    passed, one email for more than five at once, one a day for the model cap;
  successes send nothing: scripts/notify.py sends only with --failed;
  the morning summary: 07:00 Pacific by the time-zone table or by the rule, once a day, one line a job, a machine and a
    landing, the word green or red first, red lines first, a daily job with no run red;
  the record of days: counts by job, the failures that count, and the streak: 0 when the newest day failed, ended by
    a gap; the repository's own file agrees with its own days; the page shows the file's number;
  no test reads or writes the live memory by default.

No network, no database, no email: every transport is a stand-in.
"""

import datetime as dt
import io
import json
import os
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("scripts", "warehouse"):
    sys.path.insert(0, os.path.join(ROOT, p))
import alert  # noqa: E402
import duty  # noqa: E402
import health  # noqa: E402
import notify  # noqa: E402

UTC = dt.timezone.utc
EM = chr(0x2014)


def at(h, m=0, day=12):
    return dt.datetime(2026, 10, day, h, m, tzinfo=UTC)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def row(step, status="failed", wf="daily prices", when=None, reason="HTTP 500", run_id="900"):
    return {"at": (when or at(14, 45)).isoformat(), "workflow": wf, "run_id": run_id, "step": step, "status": status, "reason": reason}


class Table:
    """A stand-in for erw_health behind PostgREST: get() answers the queries scripts/alert.py makes, post() adds a row."""

    def __init__(self, rows=()):
        self.rows, self.gets = list(rows), 0

    def get(self, url, headers=None, timeout=30):
        self.gets += 1
        q = dict((k, v[0]) for k, v in __import__("urllib.parse").parse.parse_qs(url.split("?", 1)[1]).items())
        out = list(self.rows)
        for k, v in q.items():
            if k in ("select", "order", "limit"):
                continue
            op, _, val = v.partition(".")
            if k == "at":
                t = alert.parse(val)
                out = [r for r in out if (alert.parse(r["at"]) >= t if op == "gte" else alert.parse(r["at"]) < t)]
            elif op == "eq":
                out = [r for r in out if str(r.get(k)) == val]
            elif op == "neq":
                out = [r for r in out if str(r.get(k)) != val]
            elif op == "like":
                out = [r for r in out if str(r.get(k) or "").startswith(val.rstrip("*"))]
        out.sort(key=lambda r: r["at"], reverse=q.get("order") == "at.desc")
        if q.get("limit"):
            out = out[:int(q["limit"])]
        text = json.dumps(out)
        return types.SimpleNamespace(status_code=200, text=text, json=lambda: json.loads(text))

    def post(self, url, headers=None, timeout=30, json=None):
        if "resend" in url:
            self.mails = getattr(self, "mails", []) + [json]
            return types.SimpleNamespace(status_code=200, text="{}", json=lambda: {})
        self.rows.append({"at": getattr(self, "now", at(15, 0)).isoformat(), **json})
        return types.SimpleNamespace(status_code=201, text="", json=lambda: None)


ENV = {"SUPABASE_URL": "https://x.supabase.co/rest/v1/", "SUPABASE_SERVICE_KEY": "k", "RESEND_API_KEY": "r", "DIGEST_RECIPIENTS": "a@x, b@x", "DIGEST_FROM": "ERW <e@x>"}
env = lambda name: ENV.get(name, "")  # noqa: E731


class TheMemory(unittest.TestCase):
    def test_due_is_once_with_the_memory_and_the_first_quarter_without_it(self):
        self.assertFalse(alert.due(29, 30, "k", set()))
        self.assertTrue(alert.due(30, 30, "k", set()))
        self.assertTrue(alert.due(400, 30, "k", set()))                # a late check still sends
        self.assertFalse(alert.due(31, 30, "k", {"k"}))                # a doubled check does not repeat
        self.assertTrue(alert.due(44, 30, "k", None))
        self.assertFalse(alert.due(45, 30, "k", None))                 # without the memory: one window, so one line

    def test_what_was_said_is_a_row_of_erw_health_and_is_read_back(self):
        t = Table()
        self.assertEqual(alert.told(at(15, 0), t.get, env), set())
        self.assertTrue(alert.say("idle alarm", "quiet|laptop|2026-10-12T14:00", t.post, env))
        self.assertEqual(t.rows[0]["workflow"], "alerts")
        self.assertEqual((t.rows[0]["step"], t.rows[0]["status"]), ("idle alarm", "ok"))
        self.assertEqual(alert.told(at(15, 30), t.get, env), {"quiet|laptop|2026-10-12T14:00"})
        self.assertEqual(alert.told(at(15, 0) + dt.timedelta(hours=alert.MEMORY_HOURS + 1), t.get, env), set())   # it is forgotten after its time

    def test_a_memory_that_cannot_be_read_is_none_and_one_that_cannot_be_written_is_false(self):
        def broken(*a, **k):
            raise OSError("no network")
        self.assertIsNone(alert.told(at(15, 0), broken, env))
        self.assertFalse(alert.say("failure", "k", broken, env))
        self.assertIsNone(alert.told(at(15, 0), Table().get, lambda name: ""))     # no key

    def test_a_test_never_reaches_the_live_memory_by_default(self):
        # five rows were written to the live table from a test run on 12 October 2026, before this guard
        self.assertIsNone(alert.told(at(15, 0)))
        self.assertFalse(alert.say("idle alarm", "quiet|a-test|2026-10-12T00:00"))
        self.assertTrue(alert.in_a_test(alert.http_post, alert.http_post))
        self.assertFalse(alert.in_a_test(Table().post, alert.http_post))


class AFailureIsToldOnce(unittest.TestCase):
    def run_check(self, t, now, minutes=60):
        t.now = now
        out = io.StringIO()
        with redirect_stdout(out):
            code = alert.failures(minutes, False, now, t.get, t.post, env)
        return code, getattr(t, "mails", []), out.getvalue()

    def test_a_new_failure_is_one_email_and_not_again(self):
        t = Table([row("isone", "ok", when=at(14, 45, 11)), row("isone", when=at(14, 45), reason="RTM_HOURLY: HTTP 500 from the publisher")])
        code, mails, said = self.run_check(t, at(14, 50))
        self.assertEqual(code, 0)
        self.assertEqual(len(mails), 2)                                                     # one message to each of the two fixed recipients
        self.assertEqual(mails[0]["subject"], "ERW: isone failed (daily prices)")
        self.assertIn("isone of daily prices failed at 14:45 UTC (run 900): RTM_HOURLY: HTTP 500 from the publisher.", mails[0]["text"])
        self.assertIn("Said once", mails[0]["text"])
        self.assertLessEqual(len(mails[0]["text"].strip()), 300)
        self.assertNotIn(EM, mails[0]["text"])
        self.assertEqual([r["reason"] for r in t.rows if r["workflow"] == "alerts"], ["failed|daily prices|isone|2026-10-12T14:45"])
        code, mails, said = self.run_check(t, at(15, 5))                                    # the next check, the same hour
        self.assertEqual((code, len(mails)), (0, 2))
        self.assertIn("quiet: no step newly failed", said)

    def test_a_step_that_failed_at_its_run_before_is_the_same_failure(self):
        t = Table([row("isone", when=at(14, 45, 11)), row("isone", when=at(14, 45))])     # yesterday and today
        code, mails, said = self.run_check(t, at(14, 50))
        self.assertEqual((code, mails), (0, []))
        # a skip between the two is not an outcome: still the same failure
        t = Table([row("latest prices", wf="latest prices", when=at(14, 15)), row("latest prices", "skipped", wf="latest prices", when=at(14, 30)),
                   row("latest prices", wf="latest prices", when=at(14, 45))])
        self.assertEqual(self.run_check(t, at(14, 50), minutes=20)[1], [])
        # once it passes and fails again, it is a new failure
        t = Table([row("isone", when=at(14, 45, 10)), row("isone", "ok", when=at(14, 45, 11)), row("isone", when=at(14, 45))])
        self.assertEqual(len(self.run_check(t, at(14, 50))[1]), 2)

    def test_a_retry_that_passed_is_not_a_failure(self):
        t = Table([row("network snapshot", "retried", wf="hourly network", when=at(14, 45))])
        self.assertEqual(self.run_check(t, at(14, 50))[1], [])

    def test_more_than_five_at_once_are_one_email(self):
        t = Table([row(f"step{i}", when=at(14, 40 + i)) for i in range(7)])
        code, mails, said = self.run_check(t, at(14, 50))
        self.assertEqual(len(mails), 2)                                                     # one email, two recipients
        self.assertEqual(mails[0]["subject"], "ERW: 7 scheduled steps failed")
        self.assertIn("step0 (daily prices), step1 (daily prices)", mails[0]["text"])
        self.assertEqual(len([r for r in t.rows if r["workflow"] == "alerts"]), 7)          # each is remembered
        self.assertEqual(len(self.run_check(t, at(15, 5))[1]), 2)                           # and none is said again

    def test_five_are_five_emails(self):
        t = Table([row(f"step{i}", when=at(14, 40 + i)) for i in range(5)])
        self.assertEqual(len(self.run_check(t, at(14, 50))[1]), 10)

    def test_the_model_cap_is_said_once_a_day(self):
        why = "daily model cap reached: USD 1.10 spent today of USD 1.00 (DAILY_MODEL_USD); not run"
        t = Table([row("news_score", "skipped", when=at(14, 20), reason=why), row("digest", "skipped", when=at(14, 30), reason=why)])
        code, mails, said = self.run_check(t, at(14, 50))
        self.assertEqual(mails[0]["subject"], "ERW: the daily model cap skipped 2 steps")
        self.assertIn("not run today: news_score, digest.", mails[0]["text"])
        t.rows.append(row("funfact", "skipped", when=at(15, 10), reason=why))
        self.assertEqual(len(self.run_check(t, at(15, 20))[1]), 2)                          # not again that day

    def test_without_the_memory_only_the_last_quarter_of_an_hour_is_read(self):
        t = Table([row("isone", when=at(14, 20)), row("caiso", when=at(14, 45))])
        new = alert.new_failures(at(14, 50), 60, None, t.get, env)
        self.assertEqual([r["step"] for _, r in new], ["caiso"])

    def test_an_email_that_cannot_be_sent_is_exit_1_and_is_not_remembered(self):
        t = Table([row("isone", when=at(14, 45))])
        t.now = at(14, 50)

        def refuse(subject, line, dry):
            raise RuntimeError("Resend HTTP 500")
        with redirect_stdout(io.StringIO()):
            code = alert.failures(60, False, at(14, 50), t.get, t.post, env, send=refuse)
        self.assertEqual(code, 1)
        self.assertEqual([r for r in t.rows if r["workflow"] == "alerts"], [])              # so the next check tries again

    def test_the_memorys_own_rows_are_never_a_failure(self):
        t = Table([row("failure", wf="alerts", when=at(14, 45))])
        self.assertEqual(self.run_check(t, at(14, 50))[1], [])


class SuccessesSendNothing(unittest.TestCase):
    def test_a_finished_session_is_not_emailed(self):
        out = io.StringIO()
        sent = []
        keep, notify.send = notify.send, lambda *a, **k: sent.append(a) or 2
        try:
            with redirect_stdout(out):
                code = notify.main(["--session", "202", "--branch", "task/202-reliability", "--line", "landed"])
            self.assertEqual((code, sent), (0, []))
            self.assertIn("Successes send nothing", out.getvalue())
            with redirect_stdout(io.StringIO()):
                code = notify.main(["--session", "202", "--branch", "wip/202-reliability", "--line", "could not finish", "--failed"])
            self.assertEqual((code, len(sent)), (0, 1))
        finally:
            notify.send = keep

    def test_the_daily_workflow_no_longer_sends_a_line_a_run(self):
        self.assertNotIn("health.py alert", src(".github", "workflows", "daily-prices.yml"))
        watch = src(".github", "workflows", "chain-watch.yml")
        self.assertIn('--step "new failures" --retries 0 -- python scripts/alert.py failures', watch)
        self.assertIn('--step "morning summary" --retries 0 -- python scripts/alert.py summary', watch)

    def test_the_roundup_tells_its_own_failures_and_is_not_told_twice(self):
        # its workflow is not touched: its own last step sends the line of a failed run, so the chain watch leaves it
        self.assertIn('python warehouse/health.py alert --run-id "${{ github.run_id }}"', src(".github", "workflows", "roundup.yml"))
        self.assertNotIn("scripts/alert.py", src(".github", "workflows", "roundup.yml"))
        t = Table([row("write the Roundup", wf="energy roundup", when=at(14, 45)), row("isone", when=at(14, 46))])
        new = alert.new_failures(at(14, 50), 60, set(), t.get, env)
        self.assertEqual([r["workflow"] for _, r in new], ["daily prices"])
        self.assertTrue(any(t_.startswith("daily prices: 1 failed in 1") for _, t_ in alert.summary_lines(t.rows, [])))   # the morning summary lists both
        self.assertTrue(any(t_.startswith("energy roundup: 1 failed") for _, t_ in alert.summary_lines(t.rows, [])))


class TheMorningSummary(unittest.TestCase):
    def test_seven_pacific_is_14_utc_in_summer_and_15_in_winter_by_table_or_by_rule(self):
        for now, hour in ((at(14, 0), 7), (dt.datetime(2026, 12, 1, 15, 0, tzinfo=UTC), 7), (dt.datetime(2026, 11, 1, 8, 59, tzinfo=UTC), 1),
                          (dt.datetime(2026, 11, 1, 9, 0, tzinfo=UTC), 1), (dt.datetime(2026, 3, 8, 9, 59, tzinfo=UTC), 1), (dt.datetime(2026, 3, 8, 10, 0, tzinfo=UTC), 3)):
            self.assertEqual(alert.pacific(now).hour, hour, now)
            keep = sys.modules.get("zoneinfo")
            sys.modules["zoneinfo"] = None   # a machine without the time-zone table: the rule
            try:
                self.assertEqual(alert.pacific(now).hour, hour, f"by the rule, {now}")
            finally:
                if keep is None:
                    del sys.modules["zoneinfo"]
                else:
                    sys.modules["zoneinfo"] = keep

    def lines(self):
        rows = ([row("latest prices", "ok", wf="latest prices", when=at(1, 15 * (i % 4)), run_id=str(i)) for i in range(8)]
                + [row("gate", "ok", when=at(14, 4, 11), run_id="77"), row("isone", when=at(14, 45, 11), run_id="77", reason="RTM_HOURLY: HTTP 500"),
                   row("carbon_auctions", when=at(14, 50, 11), run_id="77", reason="the page changed"), row("supabase_load", when=at(15, 20, 11), run_id="77", reason="exit 1"),
                   row("redivis_upload", when=at(15, 30, 11), run_id="77", reason="exit 1")]
                + [row("network snapshot", "retried", wf="hourly network", when=at(3, 5), run_id="5"), row("network snapshot", "ok", wf="hourly network", when=at(4, 5), run_id="6")]
                + [row("idle", "ok", wf="local:samueloldlaptop", when=at(6, 10), run_id=None), row("quiet|x", "ok", wf="alerts", when=at(2, 0))])
        runs = [{"branch": "task/201-tooling", "conclusion": "success", "id": 1, "at": at(17, 0, 11)},
                {"branch": "task/198-battery-data", "conclusion": "failure", "id": 38172045438, "at": at(1, 0)},
                {"branch": "task/198-battery-data", "conclusion": "success", "id": 0, "at": at(0, 30)},     # an older run of the same branch
                {"branch": "wip/203-brand-battery", "conclusion": "in_progress", "id": 3, "at": at(13, 50)}]
        return alert.summary_lines(rows, runs)

    def test_one_line_each_green_or_red_and_red_first(self):
        ls = self.lines()
        self.assertEqual([c for c, _ in ls], ["red", "red", "red", "open", "green", "green", "green", "green"])
        text = {t.split(":")[0]: (c, t) for c, t in ls}
        self.assertEqual(text["chain watch"], ("red", "chain watch: no run recorded"))                      # a daily job with no run is red
        self.assertEqual(text["daily prices"][0], "red")
        self.assertIn("daily prices: 4 failed in 1 run: isone (RTM_HOURLY: HTTP 500); carbon_auctions (the page changed); supabase_load (exit 1); and 1 more",
                      text["daily prices"][1])
        self.assertEqual(text["latest prices"], ("green", "latest prices: 8 runs, no failure"))
        self.assertEqual(text["hourly network"], ("green", "hourly network: 2 runs, no failure; 1 passed at the second try"))
        self.assertEqual(text["machine samueloldlaptop"], ("green", "machine samueloldlaptop: 1 step, no failure; last: idle at 06:10 UTC"))
        self.assertEqual(text["task/201-tooling"], ("green", "task/201-tooling: checks passed, merged into main"))
        self.assertEqual(text["task/198-battery-data"], ("red", "task/198-battery-data: checks failure (run 38172045438), not merged"))   # its newest run
        self.assertEqual(text["wip/203-brand-battery"][0], "open")
        self.assertFalse(any("alerts" in t for _, t in ls))                                               # the memory is not a job

    def test_the_mail_says_the_count_the_span_and_the_streak_in_text_and_in_html(self):
        subject, text, html = alert.summary_mail(at(14, 5), self.lines(), "Scheduled jobs green for 0 days (counted to 2026-10-11, UTC).")
        self.assertEqual(subject, "ERW morning summary, 12 October 2026: 4 green, 3 red")
        self.assertIn("The runs from 11 October 14:00 to 12 October 14:05 UTC, one line each.", text)
        self.assertIn("Scheduled jobs green for 0 days (counted to 2026-10-11, UTC).", text)
        self.assertIn("red    chain watch: no run recorded", text)
        self.assertIn("green  latest prices: 8 runs, no failure", text)
        for body in (text, html):
            self.assertNotIn(EM, body)
        self.assertIn("<table", html)
        self.assertEqual(html.count("<tr>"), 8)
        self.assertIn("&amp;" if "&" in text else "green", html)
        self.assertNotIn("http://", html)                                                                 # nothing is loaded from anywhere
        self.assertNotIn("<script", html)

    def summary(self, now, t, **kw):
        t.now = now
        out = io.StringIO()
        with redirect_stdout(out):
            code = alert.summary(now=now, get=t.get, post=t.post, env=env, **kw)
        return code, getattr(t, "mails", []), out.getvalue()

    def test_it_is_sent_by_the_first_check_at_or_after_seven_once_a_day(self):
        t = Table([row("latest prices", "ok", wf="latest prices", when=at(13, 0))])
        code, mails, said = self.summary(at(13, 50), t)                                     # 06:50 Pacific
        self.assertEqual((code, mails), (0, []))
        self.assertIn("quiet: it is 06:50 Pacific", said)
        code, mails, said = self.summary(at(14, 20), t)                                     # the 07:00 run was late: still sent
        self.assertEqual((code, len(mails)), (0, 2))
        self.assertIn("ERW morning summary, 12 October 2026", mails[0]["subject"])
        self.assertIn("html", mails[0])
        self.assertEqual([r["reason"] for r in t.rows if r["workflow"] == "alerts"], ["summary|2026-10-12"])
        code, mails, said = self.summary(at(14, 35), t)
        self.assertEqual(len(mails), 2)                                                     # not again that day
        self.assertIn("was sent", said)
        code, mails, said = self.summary(at(14, 5, 13), t)                                  # the next morning
        self.assertEqual(len(mails), 4)

    def test_without_the_memory_only_the_first_quarter_of_an_hour_sends(self):
        class NoMemory(Table):
            def get(self, url, headers=None, timeout=30):
                if "workflow=eq.alerts" in url:
                    raise OSError("no answer")
                return super().get(url, headers, timeout)
        t = NoMemory([row("latest prices", "ok", wf="latest prices", when=at(13, 0))])
        self.assertEqual(len(self.summary(at(14, 10), t)[1]), 2)
        t = NoMemory([row("latest prices", "ok", wf="latest prices", when=at(13, 0))])
        code, mails, said = self.summary(at(14, 20), t)
        self.assertEqual((code, mails), (0, []))
        self.assertIn("the memory could not be read", said)

    def test_a_dry_run_prints_it_writes_the_html_and_sends_and_remembers_nothing(self):
        t = Table([row("isone", when=at(13, 0))])
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "out", "summary.html")
            code, mails, said = self.summary(at(3, 0), t, dry_run=True, html_path=f)       # any hour
            self.assertEqual((code, mails), (0, []))
            self.assertIn("Subject: ERW morning summary", said)
            self.assertIn("red    daily prices: 1 failed in 1 run: isone (HTTP 500)", said)
            self.assertTrue(open(f, encoding="utf-8").read().startswith("<!doctype html>"))
        self.assertEqual([r for r in t.rows if r["workflow"] == "alerts"], [])

    def test_the_streak_line_is_read_from_the_record_and_is_empty_without_it(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "health_days.json")
            self.assertEqual(alert.streak_words(f), "")
            json.dump({"green_days": 1, "counted_to": "2026-10-11"}, open(f, "w", encoding="utf-8"))
            self.assertEqual(alert.streak_words(f), "Scheduled jobs green for 1 day (counted to 2026-10-11, UTC).")
            json.dump({"green_days": 7, "counted_to": "2026-10-19"}, open(f, "w", encoding="utf-8"))
            self.assertEqual(alert.streak_words(f), "Scheduled jobs green for 7 days (counted to 2026-10-19, UTC).")


class TheRecordOfDays(unittest.TestCase):
    def day(self, n_failed=0, extra=()):
        rows = [row("latest prices", "ok", wf="latest prices", run_id=str(i)) for i in range(3)] + [row("x", "failed") for _ in range(n_failed)] + list(extra)
        return rows

    def full(self, n_failed=0):
        """A day on which each of the four jobs that run every day recorded a run."""
        return self.day(n_failed) + [row("s", "ok", wf=w, run_id="1") for w in ("hourly network", "daily prices", "chain watch")]

    def test_a_day_counts_each_job_and_the_failures_that_count(self):
        rec = health.day_record(self.day(1, [row("network snapshot", "retried", wf="hourly network"), row("quiet|x", "ok", wf="alerts"),
                                             row("session198_check", "failed", wf="local:SU-4QC3QR3", run_id=None),
                                             row("dm_sync", "failed", wf="local:lab-desktop", run_id=None, reason="the  lock\nwas held")]))
        self.assertEqual(rec["jobs"]["latest prices"], {"ok": 3, "skipped": 0, "retried": 0, "failed": 0, "runs": 3})
        self.assertEqual(rec["jobs"]["hourly network"]["retried"], 1)
        self.assertNotIn("alerts", rec["jobs"])                                             # the memory is no job
        # a scheduled workflow's failure counts, and a machine's daily run's (dm_); a session's own row is shown, not counted
        self.assertEqual(rec["failed"], 2)
        self.assertEqual([(f["workflow"], f["step"]) for f in rec["failures"]], [("daily prices", "x"), ("local:lab-desktop", "dm_sync")])
        self.assertEqual(rec["failures"][1]["reason"], "the lock was held")
        self.assertEqual(rec["jobs"]["local:SU-4QC3QR3"]["failed"], 1)
        self.assertEqual(rec["missing"], ["chain watch"])                                   # of the four that run every day, the one with no row
        every = [row("s", "ok", wf=w, run_id="1") for w in ("latest prices", "hourly network", "daily prices", "chain watch")]
        self.assertEqual(health.day_record(every)["missing"], [])

    def test_the_streak_is_0_when_the_newest_day_failed_and_is_ended_by_a_failure_or_a_gap(self):
        g, r = {"rows": 5, "failed": 0}, {"rows": 5, "failed": 2}
        self.assertEqual(health.green_streak({}), (0, None))
        self.assertEqual(health.green_streak({"2026-10-10": g, "2026-10-11": r}), (0, "2026-10-11"))
        self.assertEqual(health.green_streak({"2026-10-09": r, "2026-10-10": g, "2026-10-11": g}), (2, "2026-10-11"))
        self.assertEqual(health.green_streak({"2026-10-08": g, "2026-10-10": g, "2026-10-11": g}), (2, "2026-10-11"))     # 9 October is missing
        self.assertEqual(health.green_streak({"2026-10-10": {"rows": 0, "failed": 0}, "2026-10-11": g}), (1, "2026-10-11"))
        # a job that runs every day and recorded no run: the day is not green
        no_daily = {"rows": 5, "failed": 0, "missing": ["daily prices"]}
        self.assertEqual(health.green_streak({"2026-10-09": g, "2026-10-10": no_daily, "2026-10-11": g}), (1, "2026-10-11"))
        self.assertEqual(health.green_streak({"2026-10-10": g, "2026-10-11": no_daily}), (0, "2026-10-11"))
        week = {f"2026-10-{d:02d}": g for d in range(13, 20)}
        self.assertEqual(health.green_streak(week), (7, "2026-10-19"))                      # the public day's gate: seven
        self.assertEqual(health.green_streak({**week, "2026-10-20": r}), (0, "2026-10-20"))

    def test_the_file_is_added_to_day_by_day_and_keeps_its_newest_days(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "site", "data", "health_days.json")
            path, n, to = health.write_days({"2026-10-10": self.full(1), "2026-10-11": self.full()}, f, at(14, 0))
            self.assertEqual((n, to), (1, "2026-10-11"))
            path, n, to = health.write_days({"2026-10-12": self.full()}, f, at(14, 0, 13))                              # the next day's summary adds a day
            self.assertEqual((n, to), (2, "2026-10-12"))
            got = json.load(open(f, encoding="utf-8"))
            self.assertEqual((got["green_days"], got["counted_to"], sorted(got["days"])), (2, "2026-10-12", ["2026-10-10", "2026-10-11", "2026-10-12"]))
            self.assertEqual(got["written"], "2026-10-13T14:00Z")
            path, n, to = health.write_days({"2026-10-12": self.full(3)}, f)                                            # a day written again is replaced
            self.assertEqual((n, to), (0, "2026-10-12"))
            path, n, to = health.write_days({"2026-10-13": []}, f)                                                     # a day with no row is not recorded
            self.assertEqual(sorted(json.load(open(f, encoding="utf-8"))["days"])[-1], "2026-10-12")
            keep, health.DAYS_KEPT = health.DAYS_KEPT, 2
            try:
                health.write_days({"2026-10-13": self.full()}, f)
                self.assertEqual(sorted(json.load(open(f, encoding="utf-8"))["days"]), ["2026-10-12", "2026-10-13"])
            finally:
                health.DAYS_KEPT = keep
            self.assertNotIn(EM, open(f, encoding="utf-8").read())

    def test_a_summary_written_elsewhere_does_not_touch_the_record(self):
        before = src("site", "data", "health_days.json")
        with tempfile.TemporaryDirectory() as d:
            health.summary("2026-10-11", d, rows=self.day(1))
        self.assertEqual(src("site", "data", "health_days.json"), before)


class TheCausesThatWereCode(unittest.TestCase):
    """runs/session202/failures.md: what failed in the scheduled jobs from 29 September to 12 October 2026 and was ours."""

    def test_the_board_builder_skips_the_carbon_credit_rows_when_their_table_is_absent(self):
        # row 1: FileNotFoundError on carb_lcfs_credit_prices.csv stopped the builder on the runner, 7 to 12 October
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import board_page  # noqa: E402
        old = board_page.ip.OUT_DIR
        board_page.ip.OUT_DIR = os.path.join(ROOT, "runs", "no_such_folder_session202")
        try:
            b, lines = board_page.Board(), []
            board_page.build_lcfs(b, lines.append)
            self.assertEqual(b.rows, [])                                                    # page_keep.py keeps the held rows
            self.assertEqual(len(lines), 1)
            self.assertIn("carb_lcfs_credit_prices not on this machine, skipped", lines[0])
        finally:
            board_page.ip.OUT_DIR = old
        s = src("warehouse", "derived", "board_page.py")
        self.assertEqual(s.count('table_daily("carb_lcfs_credit_prices")'), 1)              # read in one place, behind the check
        self.assertIn("    build_lcfs(b, log)\n", s.replace("\r\n", "\n"))

    def test_the_package_tests_hold_to_coverage_not_to_lists_written_by_hand(self):
        # rows 2 to 6: five tests of the daily run's "package tests" step, failing since 5 to 8 October
        s = src("package", "tests", "test_erw.py")
        self.assertEqual(s.count('own_first_line(meta["header"])'), 4)
        self.assertNotIn('meta["header"][0].startswith', s)
        self.assertNotIn('(cov["validator_status"] == "pass").all()', s)
        self.assertNotIn('held(variable="spp_rtm") == ERCOT_RTM', s)
        self.assertNotIn('erw.filter(sector="equities") == []', s)
        for org in ('"imf": "International Monetary Fund"', '"cftc": "Commodity Futures Trading Commission"'):
            self.assertIn(org, s)

    def test_a_restored_tables_first_header_line_is_read_past_the_note(self):
        ns = {}
        s = src("package", "tests", "test_erw.py").replace("\r\n", "\n")
        exec(s[s.index("def own_first_line(header):"):s.index("EVENT_TABLES = ")], ns)
        note = "Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run 20261011T155107Z-github (2026-10-11T15:51:07Z); that run's own header of the table follows"
        own = "Energy Research Warehouse (ERW): ercot_dam_esr_awards"
        self.assertTrue(ns["own_first_line"]([own, "source: x"]))
        self.assertTrue(ns["own_first_line"]([note, own, "source: x"]))
        self.assertFalse(ns["own_first_line"]([note, "source: x"]))
        self.assertFalse(ns["own_first_line"]([]))

    def test_the_connectors_are_as_they_were(self):
        # the chain's rule: a session does not touch the connectors. Rows 9 and 10 are a patch a person applies.
        self.assertIn(r'native_load_(\d{4})\.(?:zip|xlsx|xls)', src("warehouse", "connectors", "ercot_zone_load.py"))
        self.assertNotIn("EmptyDataError", src("warehouse", "connectors", "iso_prices.py").split("def rtm_hourly(day):")[1][:1500])


class TheRepositorysOwn(unittest.TestCase):
    def test_the_record_agrees_with_its_own_days(self):
        d = json.loads(src("site", "data", "health_days.json"))
        self.assertEqual((d["green_days"], d["counted_to"]), health.green_streak(d["days"]))
        for day, rec in d["days"].items():
            dt.date.fromisoformat(day)
            self.assertEqual(rec["failed"], len(rec["failures"]), day)
            self.assertGreater(rec["rows"], 0, day)
            self.assertIsInstance(rec["missing"], list, day)
            self.assertNotIn("alerts", rec["jobs"], day)

    def test_the_page_shows_the_files_number_behind_the_cookie(self):
        page = src("site", "app", "internal", "health", "page.tsx")
        self.assertIn('import record from "@/data/health_days.json";', page)
        self.assertIn("Scheduled jobs green for {n(green)} {green === 1 ? \"day\" : \"days\"}.", page)
        self.assertIn("if (!(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();", page)
        self.assertNotIn("searchParams", page)                                              # no token in an address
        self.assertNotIn("SERVICE", page)                                                   # the site holds no service key
        self.assertIn("/internal/health", src("site", "scripts", "check-security.mjs"))
        self.assertIn("/internal/health", src("docs", "tools.md"))

    def test_the_policy_is_written_where_a_session_reads_it(self):
        doc = src("docs", "machines.md")
        self.assertIn("### One alert policy (session 202)", doc)
        for words in ("successes send nothing", "07:00 Pacific, once a day", "once for that silence", "Scheduled jobs green for N days"):
            self.assertIn(words, doc, words)
        self.assertNotIn("again every hour after", doc)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in ("scripts/alert.py", "scripts/duty.py", "scripts/notify.py", "warehouse/health.py", "site/app/internal/health/page.tsx",
                  "site/scripts/check-internal-health.mjs", "site/data/health_days.json", ".github/workflows/chain-watch.yml",
                  ".github/workflows/daily-prices.yml", "tests/test_session202.py"):
            self.assertNotIn(EM, src(*f.split("/")), f)

    def test_the_idle_check_takes_a_stand_in_for_the_memory(self):
        kept, sent = [], []
        r = {"name": "duty:laptop", "holder": "laptop", "task": "session 202", "acquired": at(5, 0), "renewed": at(5, 0), "expires": at(21, 0)}
        code = duty.check(False, now=at(6, 10), read=lambda: [r], send=lambda s, line, dry: sent.append(s) or 1, out=lambda s: None,
                          told=lambda t: set(), say=lambda kind, key: kept.append((kind, key)) or True)
        self.assertEqual((code, sent, kept), (0, ["ERW: a machine has run nothing for 30 minutes"], [("idle alarm", "quiet|laptop|2026-10-12T05:00")]))
        code = duty.check(False, now=at(7, 10), read=lambda: [r], send=lambda s, line, dry: sent.append(s) or 1, out=lambda s: None,
                          told=lambda t: {k for _, k in kept}, say=lambda kind, key: kept.append((kind, key)) or True)
        self.assertEqual(len(sent), 1)                                                       # an hour later: nothing more


if __name__ == "__main__":
    unittest.main()
