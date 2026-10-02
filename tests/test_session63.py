"""Session 63: the digest guard (warehouse/news/email_digest.py, digest_sends in migration 018).

Energy Research Warehouse (ERW). Nothing is sent: Resend and Supabase's REST API are replaced by one fake that records
each message and keeps the digest_sends rows with the table's two unique keys, (kind, day) and (kind, issue).

    python -m unittest tests.test_session63 -v
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

# session 59: only the reserved test address and its +tags, never a real recipient
A, B = "erw-test+owner@example.invalid", "erw-test+second@example.invalid"
DIGEST = os.path.join(ROOT, "docs", "digest", "2026-09-28.md")
OTHER = os.path.join(ROOT, "docs", "digest", "2026-09-25.md")
ROUNDUP = os.path.join(ROOT, "docs", "roundup", "2026-W39.md")


def reply(code, body=None):
    return types.SimpleNamespace(status_code=code, json=lambda: body if body is not None else {}, text=str(body))


class Fake:
    """Resend and the digest_sends table. fail_after: Resend fails on that message (1-based)."""

    def __init__(self, fail_after=None):
        self.rows, self.messages, self.fail_after, self.next_id = [], [], fail_after, 1

    def post(self, url, headers=None, timeout=None, json=None):
        if url == em.RESEND:
            if self.fail_after is not None and len(self.messages) + 1 >= self.fail_after:
                return reply(500, {"message": "fake failure"})
            self.messages.append(json)
            return reply(200, {"id": f"fake-{len(self.messages)}"})
        assert url.endswith("/digest_sends"), url
        if any(r["kind"] == json["kind"] and (r["day"] == json["day"] or r["issue"] == json["issue"]) for r in self.rows):
            return reply(409, {"code": "23505"})
        row = {**json, "id": self.next_id, "status": "claimed", "recipients": None, "claimed_at": "now"}
        self.next_id += 1
        self.rows.append(row)
        return reply(201, [row])

    def get(self, url, headers=None, timeout=None, params=None):
        if url.endswith("/digest_sends"):
            kind = params["kind"][3:]
            day, issue = re.match(r"\(day\.eq\.(.+),issue\.eq\.(.+)\)", params["or"]).groups()
            return reply(200, [r for r in self.rows if r["kind"] == kind and (r["day"] == day or r["issue"] == issue)])
        raise AssertionError(url)

    def patch(self, url, headers=None, timeout=None, params=None, json=None):
        for r in self.rows:
            if r["id"] == int(params["id"][3:]):
                r.update(json)
        return reply(204)

    def delete(self, url, headers=None, timeout=None, params=None):
        self.rows = [r for r in self.rows if r["id"] != int(params["id"][3:])]
        return reply(204)


class Guard(unittest.TestCase):
    def setUp(self):
        self.fake = Fake()
        self.saved = (em.env, em.requests.post, em.requests.get, em.requests.patch, em.requests.delete, em.subscribers,
                      em.suppressed, em.send_day)
        self.use(self.fake)
        values = dict(RESEND_API_KEY="k", DIGEST_RECIPIENTS=f"{A},{B}", SUPABASE_URL="https://fake.supabase.co",
                      SUPABASE_SERVICE_KEY="s")
        em.env = lambda name: values.get(name, "")
        em.subscribers = lambda kind, log: {}
        em.suppressed = lambda log: set()
        self.day = "2026-10-02"
        real = self.saved[7]
        em.send_day = lambda kind, now=None: self.day if now is None else real(kind, now)

    def use(self, fake):
        em.requests.post, em.requests.get, em.requests.patch, em.requests.delete = fake.post, fake.get, fake.patch, fake.delete

    def tearDown(self):
        (em.env, em.requests.post, em.requests.get, em.requests.patch, em.requests.delete, em.subscribers,
         em.suppressed, em.send_day) = self.saved

    def test_the_first_send_claims_and_settles(self):
        n, _ = em.send("daily", DIGEST, lambda m: None)
        self.assertEqual(n, 2)
        self.assertEqual(len(self.fake.rows), 1)
        r = self.fake.rows[0]
        self.assertEqual((r["kind"], r["day"], r["issue"], r["status"], r["recipients"]), ("daily", self.day, "2026-09-28", "sent", 2))

    def test_a_second_send_the_same_day_is_skipped(self):
        em.send("daily", DIGEST, lambda m: None)
        with self.assertRaises(em.AlreadySent) as cm:
            em.send("daily", OTHER, lambda m: None)  # a manual dispatch with a newer brief, the same day
        self.assertIn("already sent", str(cm.exception))
        self.assertEqual(len(self.fake.messages), 2)  # nobody got a second email

    def test_the_same_issue_on_another_day_is_skipped(self):
        em.send("daily", DIGEST, lambda m: None)
        self.day = "2026-10-03"  # the brief did not move on: yesterday's issue is not sent again
        with self.assertRaises(em.AlreadySent):
            em.send("daily", DIGEST, lambda m: None)
        self.assertEqual(len(self.fake.messages), 2)

    def test_the_next_day_sends(self):
        em.send("daily", DIGEST, lambda m: None)
        self.day = "2026-10-03"
        n, _ = em.send("daily", OTHER, lambda m: None)
        self.assertEqual(n, 2)
        self.assertEqual(len(self.fake.rows), 2)

    def test_the_daily_and_the_roundup_do_not_block_each_other(self):
        em.send("daily", DIGEST, lambda m: None)
        n, _ = em.send("roundup", ROUNDUP, lambda m: None)
        self.assertEqual(n, 2)

    def test_a_failure_before_any_message_releases_the_claim(self):
        self.fake.fail_after = 1
        with self.assertRaises(RuntimeError):
            em.send("daily", DIGEST, lambda m: None)
        self.assertEqual(self.fake.rows, [])
        self.fake.fail_after = None  # the retry sends
        n, _ = em.send("daily", DIGEST, lambda m: None)
        self.assertEqual(n, 2)

    def test_a_failure_part_way_keeps_the_claim_as_partial(self):
        self.fake.fail_after = 2
        with self.assertRaises(RuntimeError):
            em.send("daily", DIGEST, lambda m: None)
        self.assertEqual((self.fake.rows[0]["status"], self.fake.rows[0]["recipients"]), ("partial", 1))
        self.fake.fail_after = None
        with self.assertRaises(em.AlreadySent):  # the first recipient never gets it twice
            em.send("daily", DIGEST, lambda m: None)
        self.assertEqual(len(self.fake.messages), 1)

    def test_no_guard_no_send(self):
        values = dict(RESEND_API_KEY="k", DIGEST_RECIPIENTS=A)
        em.env = lambda name: values.get(name, "")
        with self.assertRaises(RuntimeError) as cm:
            em.send("daily", DIGEST, lambda m: None)
        self.assertIn("send guard", str(cm.exception))
        self.assertEqual(self.fake.messages, [])

    def test_nothing_configured_claims_nothing(self):
        values = dict(SUPABASE_URL="https://fake.supabase.co", SUPABASE_SERVICE_KEY="s")
        em.env = lambda name: values.get(name, "")
        n, detail = em.send("daily", DIGEST, lambda m: None)
        self.assertEqual((n, self.fake.rows), (0, []))
        self.assertIn("not sent", detail)

    def test_main_reports_a_second_send_as_skipped(self):
        statuses = []
        saved = (em.ip.write_status, em.KINDS)
        try:
            em.ip.write_status = lambda connector, run_id, results: statuses.append(results)
            em.KINDS = {**em.KINDS, "daily": (em.KINDS["daily"][0], em.KINDS["daily"][1], DIGEST)}
            out = os.path.join(ROOT, "docs", "digest", "email")
            before = {f: open(os.path.join(out, f), "rb").read() for f in os.listdir(out) if f.startswith("2026-09-28-daily")}
            try:
                self.assertEqual(em.main([]), 0)
                self.assertEqual(em.main([]), 0)
            finally:  # leave the saved copies as they were
                for f, b in before.items():
                    open(os.path.join(out, f), "wb").write(b)
                for f in os.listdir(out):
                    if f.startswith("2026-09-28-daily") and f not in before:
                        os.remove(os.path.join(out, f))
        finally:
            em.ip.write_status, em.KINDS = saved
        self.assertEqual([s[0]["status"] for s in statuses], ["ok", "skipped"])
        self.assertIn("already sent", statuses[1][0]["detail"])
        self.assertEqual(len(self.fake.messages), 2)


class Days(unittest.TestCase):
    def test_the_roundup_window_runs_to_monday_0300(self):
        mon = dt.datetime(2026, 10, 5, 2, 30, tzinfo=dt.timezone.utc)
        self.assertEqual(em.send_day("roundup", mon), "2026-10-04")
        self.assertEqual(em.send_day("daily", mon), "2026-10-05")
        self.assertEqual(em.send_day("roundup", dt.datetime(2026, 10, 4, 23, 0, tzinfo=dt.timezone.utc)), "2026-10-04")

    def test_the_migration_has_both_unique_keys_and_no_public_access(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "migrations", "018_game_v3_digest_sends.sql"), encoding="utf-8") as f:
            sql = f.read()
        self.assertIn("unique (kind, day)", sql)
        self.assertIn("unique (kind, issue)", sql)
        self.assertIn("revoke all on public.digest_sends from anon, authenticated", sql)
        self.assertIn("(-v3)?$", sql)


if __name__ == "__main__":
    unittest.main()
