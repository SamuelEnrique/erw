"""Session 3717 (chain 208): the one-email rule checked against what the chain watch sent (roadmap item 6).

From 30 October to 5 November 2026 the alerts' memory in erw_health held two rows of a sent email, a daily red on
31 October (daily prices, merge tests, newly failed) and one on 1 November (the data machine's dm_test_findings, newly
failed), and no "ready": no machine went idle that week. The other memory rows (a morning summary each day, the failures
a daily red named) are recorded, not emailed. Nothing extra was sent. The day's summary did not say which memory rows
were emails, so the check needed erw_health: the summary now lists them (warehouse/health.py emails_sent). No network.
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def health():
    spec = importlib.util.spec_from_file_location("health_s3717", os.path.join(ROOT, "warehouse", "health.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def row(at, wf, step, status="ok", reason=""):
    return {"at": at, "workflow": wf, "step": step, "status": status, "reason": reason, "run_id": None}


# 31 October 2026's memory rows, as erw_health held them (read by session 3717)
OCT31 = [row("2026-10-31T14:00:00+00:00", "alerts", "morning summary", reason="summary|2026-10-31"),
         row("2026-10-31T14:15:00+00:00", "alerts", "daily red", reason="daily red|2026-10-31"),
         row("2026-10-31T14:15:00+00:00", "alerts", "failure", reason="failed|daily prices|merge tests|2026-10-31T14:14"),
         row("2026-10-31T14:14:00+00:00", "daily prices", "merge tests", status="failed", reason="FAILED (failures=5, errors=2)")]


class TheEmailsSent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = health()

    def test_the_sender_sends_two_kinds(self):
        with open(os.path.join(ROOT, "scripts", "alert.py"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn('READY, DAILY_RED = "ready", "daily red"', text)
        self.assertEqual(self.h.EMAIL_KINDS, ("ready", "daily red"))

    def test_a_day_lists_its_emails_and_what_was_only_recorded(self):
        out = self.h.emails_sent(OCT31)
        self.assertEqual(out[1], "## Emails the chain watch sent")
        sent = [ln for ln in out if ln.startswith("- ")]
        self.assertEqual(sent, ["- 14:15 UTC, daily red: daily red|2026-10-31"])
        self.assertIn("Recorded, not emailed: failure 1; morning summary 1.", out)

    def test_a_quiet_day_says_none(self):
        out = self.h.emails_sent([row("2026-11-02T15:00:00+00:00", "alerts", "morning summary", reason="summary|2026-11-02")])
        self.assertIn("- none", out)

    def test_the_rendered_summary_carries_the_section(self):
        text = self.h.render("2026-10-31", OCT31)
        self.assertIn("## Emails the chain watch sent", text)
        self.assertIn("- 14:15 UTC, daily red: daily red|2026-10-31", text)

    def test_at_most_one_daily_red_a_day_in_a_summary(self):
        # the rule, read from any summary that lists its emails (the files written from session 3717 on)
        folder = os.path.join(ROOT, "queue", "summary")
        if not os.path.isdir(folder):
            self.skipTest("no summaries in this copy")
        for name in sorted(os.listdir(folder)):
            if not name.endswith("-health.md"):
                continue
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                text = f.read()
            if "## Emails the chain watch sent" not in text:
                continue
            section = text.split("## Emails the chain watch sent", 1)[1].split("\n## ", 1)[0]
            self.assertLessEqual(section.count(", daily red: "), 1, name)


if __name__ == "__main__":
    unittest.main()
