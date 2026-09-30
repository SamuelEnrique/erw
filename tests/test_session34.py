"""Session 34, item 8: who the digests go to. The shadow Digest and Roundup (Haiku's scores, subject "SHADOW HAIKU")
go to one address only, never to a subscriber, until the expiry in warehouse/config/shadow.yaml (2026-10-06); the
published digest goes to the fixed recipients and every confirmed subscriber.

Energy Research Warehouse (ERW). Nothing is sent and no model is called: Resend's endpoint and the subscriber list are
replaced by fakes that record what would have gone out.

    python -m unittest tests.test_session34 -v
"""

import datetime as dt
import os
import re
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/news"):
    sys.path.insert(0, os.path.join(ROOT, p))

import email_digest as em  # noqa: E402
import shadow  # noqa: E402

A, B, C = "owner@example.org", "second@example.org", "subscriber@example.org"


class Sent:
    """A fake requests.post for Resend: records each message."""

    def __init__(self):
        self.messages = []

    def __call__(self, url, headers=None, timeout=None, json=None):
        self.messages.append(json)
        return types.SimpleNamespace(status_code=200, json=lambda: {"id": "fake"}, text="")


class Env:
    def __init__(self, **values):
        self.values = values

    def __call__(self, name):
        return self.values.get(name, "")


DIGEST = os.path.join(ROOT, "docs", "digest", "2026-09-28.md")   # a published digest, as the daily run wrote it
ROUNDUP = os.path.join(ROOT, "docs", "roundup", "2026-W39.md")   # a published Roundup


class ShadowRecipients(unittest.TestCase):
    def setUp(self):
        self.sent = Sent()
        self.saved = (em.env, em.requests.post, em.subscribers)
        em.requests.post = self.sent
        em.subscribers = lambda kind, log: (_ for _ in ()).throw(AssertionError("the shadow read the subscribers"))

    def tearDown(self):
        em.env, em.requests.post, em.subscribers = self.saved

    def test_one_fixed_recipient_gets_the_shadow_with_its_prefix(self):
        em.env = Env(RESEND_API_KEY="k", DIGEST_RECIPIENTS=A, EMAIL_SUBSCRIBERS="1", EMAIL_TOKEN_SECRET="s")
        out = shadow.send("daily", DIGEST, "claude-haiku-4-5", lambda m: None)
        self.assertEqual([m["to"] for m in self.sent.messages], [[A]])
        self.assertTrue(self.sent.messages[0]["subject"].startswith("SHADOW HAIKU: "))
        self.assertIn("sent", out)

    def test_shadow_recipient_wins_over_the_fixed_list(self):
        em.env = Env(RESEND_API_KEY="k", DIGEST_RECIPIENTS=f"{A},{B}", SHADOW_RECIPIENT=A)
        shadow.send("roundup", ROUNDUP, "claude-haiku-4-5", lambda m: None)
        self.assertEqual([m["to"] for m in self.sent.messages], [[A]])

    def test_a_list_of_two_gets_nothing(self):
        em.env = Env(RESEND_API_KEY="k", DIGEST_RECIPIENTS=f"{A},{B}")
        out = shadow.send("daily", DIGEST, "claude-haiku-4-5", lambda m: None)
        self.assertEqual(self.sent.messages, [])
        self.assertIn("not sent", out)


class ShadowExpiry(unittest.TestCase):
    def test_expires_2026_10_06_and_the_kill_switch(self):
        self.assertEqual(shadow.config()["expires"], "2026-10-06")
        saved_dt, saved_model = shadow.dt, os.environ.get("SHADOW_MODEL")
        try:
            os.environ["SHADOW_MODEL"] = "claude-haiku-4-5"
            for day, runs in (("2026-10-05", True), ("2026-10-06", False), ("2026-10-07", False)):
                fixed = dt.datetime.fromisoformat(day + "T14:00:00+00:00")
                shadow.dt = types.SimpleNamespace(datetime=types.SimpleNamespace(now=lambda tz=None: fixed),
                                                  timezone=dt.timezone)
                self.assertEqual(shadow.gate(lambda m: None)[0] is not None, runs, day)
            shadow.dt = saved_dt
            os.environ["SHADOW_MODEL"] = ""
            self.assertIsNone(shadow.gate(lambda m: None)[0])
        finally:
            shadow.dt = saved_dt
            if saved_model is None:
                os.environ.pop("SHADOW_MODEL", None)
            else:
                os.environ["SHADOW_MODEL"] = saved_model


class PublishedDigestRecipients(unittest.TestCase):
    def test_fixed_recipients_and_confirmed_subscribers_get_the_published_digest(self):
        sent = Sent()
        saved = (em.env, em.requests.post, em.subscribers, em.suppressed)
        try:
            em.requests.post = sent
            em.env = Env(RESEND_API_KEY="k", DIGEST_RECIPIENTS=A, EMAIL_SUBSCRIBERS="1", EMAIL_TOKEN_SECRET="s")
            em.subscribers = lambda kind, log: {C: ["power"]}
            em.suppressed = lambda log: set()
            n, _ = em.send("daily", DIGEST, lambda m: None)
        finally:
            em.env, em.requests.post, em.subscribers, em.suppressed = saved
        self.assertEqual(n, 2)
        self.assertEqual(sorted(m["to"][0] for m in sent.messages), sorted([A, C]))
        self.assertFalse(any(m["subject"].startswith("SHADOW") for m in sent.messages))


class Workflows(unittest.TestCase):
    def read(self, p):
        with open(os.path.join(ROOT, p), encoding="utf-8") as f:
            return f.read()

    def test_the_daily_job_sends_the_published_digest_then_the_shadow(self):
        wf = self.read(".github/workflows/daily-prices.yml")
        for line in ('SHADOW_MODEL: claude-haiku-4-5', 'EMAIL_SUBSCRIBERS: "1"', "EMAIL_TOKEN_SECRET: ${{ secrets.",
                     "DIGEST_RECIPIENTS: ${{ secrets."):
            self.assertIn(line, wf)
        sh = self.read("warehouse/run_daily.sh")
        self.assertLess(sh.index("warehouse/news/email_digest.py --auto"), sh.index("warehouse/news/shadow.py digest"))
        self.assertIn("model_step news_score \"$PYTHON\" warehouse/news/score.py", sh)

    def test_the_roundup_job_sends_the_shadow_roundup(self):
        wf = self.read(".github/workflows/roundup.yml")
        self.assertIn("python warehouse/news/shadow.py roundup", wf)
        self.assertIn("python warehouse/news/email_digest.py --roundup", wf)
        self.assertEqual(len(re.findall(r'EMAIL_SUBSCRIBERS: "1"', wf)), 1)  # the published Roundup's step only


if __name__ == "__main__":
    unittest.main()
