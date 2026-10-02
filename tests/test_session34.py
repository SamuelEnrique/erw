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

# session 59: the fixed test address (email_digest.TEST_ADDRESS) and its +tags, never a real recipient
A, B, C = "erw-test+owner@example.invalid", "erw-test+second@example.invalid", "erw-test+subscriber@example.invalid"


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
        saved = (em.env, em.requests.post, em.subscribers, em.suppressed, em.claim, em.settle)
        try:
            em.claim = lambda kind, issue, log, now=None: 1  # session 63: the send guard (tests/test_session63.py)
            em.settle = lambda claim_id, sent, total, log: None
            em.requests.post = sent
            em.env = Env(RESEND_API_KEY="k", DIGEST_RECIPIENTS=A, EMAIL_SUBSCRIBERS="1", EMAIL_TOKEN_SECRET="s")
            em.subscribers = lambda kind, log: {C: ["power"]}
            em.suppressed = lambda log: set()
            n, _ = em.send("daily", DIGEST, lambda m: None)
        finally:
            em.env, em.requests.post, em.subscribers, em.suppressed, em.claim, em.settle = saved
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


class ArchiveChunks(unittest.TestCase):
    """Session 34: a run's part over the bucket's size limit is stored as numbered chunks that read back as one."""

    def test_large_part_is_chunked_and_reads_back_in_order(self):
        import gzip
        import io
        import numpy as np
        import pandas as pd
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "archive"))
        import archive as A

        class FakeBucket:
            def __init__(self):
                self.objects = {}

            def put(self, path, data, overwrite=False):
                self.objects[path] = data

        rng = np.random.default_rng(34)
        df = pd.DataFrame({"_run_id": "r1", "value": rng.random(20000).astype(str)})
        b = FakeBucket()
        saved = A.PART_MAX
        try:
            A.PART_MAX = 60_000
            n = A.put_part(b, "t/2026-09", "r1", df)
        finally:
            A.PART_MAX = saved
        self.assertGreater(n, 1)
        names = sorted(b.objects)
        self.assertTrue(all(x.startswith("t/2026-09/r1.p") for x in names))
        self.assertTrue(all(len(v) <= 60_000 for v in b.objects.values()))
        self.assertEqual({A.run_of(x.split("/")[-1]) for x in names}, {"r1"})
        back = pd.concat([pd.read_csv(io.BytesIO(gzip.decompress(b.objects[x])), dtype=str) for x in names])
        self.assertEqual(back["value"].tolist(), df["value"].tolist())
        small = FakeBucket()
        self.assertEqual(A.put_part(small, "t/2026-09", "r2", df.head(10)), 1)
        self.assertEqual(list(small.objects), ["t/2026-09/r2.csv.gz"])
        self.assertEqual(A.run_of("r2.csv.gz"), "r2")


class ArchiveStateChunks(unittest.TestCase):
    """Session 34: an index larger than the bucket's limit is stored as chunks behind a pointer and read back whole."""

    def test_state_round_trip_and_pointer(self):
        import numpy as np
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "archive"))
        import archive as A

        class FakeBucket:
            def __init__(self):
                self.objects = {}

            def put(self, path, data, overwrite=False):
                self.objects[path] = data

            def get(self, path):
                return self.objects.get(path)

        rng = np.random.default_rng(34)
        data = A.pack_state(rng.integers(0, 2**63, 30000, dtype=np.uint64),
                            rng.integers(0, 2**63, 30000, dtype=np.uint64), "r1")
        b = FakeBucket()
        b.objects["_state/t.npz"] = b"an older single index"
        saved = A.PART_MAX
        try:
            A.PART_MAX = 100_000
            A.state_put(b, "t", data)
            self.assertGreater(len([k for k in b.objects if k.startswith("_state/t.npz.p")]), 1)
            self.assertLess(len(b.objects["_state/t.npz"]), 2_000)  # the pointer replaced the older index
            self.assertEqual(A.state_get(b, "t"), data)
            small = A.pack_state(np.array([1], dtype=np.uint64), np.array([2], dtype=np.uint64), "r2")
            A.state_put(b, "u", small)
            self.assertEqual(A.state_get(b, "u"), small)
        finally:
            A.PART_MAX = saved
