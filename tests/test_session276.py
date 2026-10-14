"""Session 276: subscribe, the email domain, the usage count.

Energy Research Warehouse (ERW). scripts/live_check.py runs the live routes end to end (subscribe, confirm,
unsubscribe; the usage count and /internal/usage); scripts/resend_domain.py prints the exact DNS records Resend writes
for a domain; docs/runbook.md holds the steps. Held here, with no network: the link and cookie are signed as the site
signs them; each step of the checks reads what it should and fails when a step does not hold; the checks refuse an
address that is not Resend's test address; the record lines; the runbook's records and commands.
"""

import hashlib
import hmac
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import live_check as L  # noqa: E402
import resend_domain as R  # noqa: E402

EM = chr(0x2014)


class Resp:
    def __init__(self, status=200, json_=None, headers=None, text=""):
        self.status_code, self._j, self.headers, self.text = status, json_, headers or {}, text

    def json(self):
        return self._j

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class FakeSite:
    """The live site and the database, as the routes leave them."""

    def __init__(self, break_confirm=False):
        self.row = None
        self.suppressed = False
        self.count = 5
        self.break_confirm = break_confirm

    def post(self, url, data=None, headers=None, **k):
        if url.endswith("/api/subscribe"):
            self.row = dict(email="x", daily=True, weekly=True, topics=["power_prices"], confirmed_at=None, unsubscribed_at=None)
            return Resp(303, headers={"location": "/subscribe?state=check"})
        if url.endswith("/api/unsubscribe"):
            self.row["unsubscribed_at"] = "2026-10-14T10:00:00Z"
            self.suppressed = True
            return Resp(303, headers={"location": "/subscribe?state=unsubscribed"})
        if url.endswith("/api/usage"):
            self.count += 1
            return Resp(204)
        raise AssertionError(url)

    def get(self, url, params=None, headers=None, **k):
        if url.endswith("/api/subscribe/confirm"):
            if not self.break_confirm:
                self.row["confirmed_at"] = "2026-10-14T10:00:00Z"
            return Resp(303, headers={"location": f"/subscribe?state={'badlink' if self.break_confirm else 'confirmed'}"})
        if url.endswith("/subscribers"):
            return Resp(200, [self.row] if self.row else [])
        if url.endswith("/email_suppressions"):
            return Resp(200, [{"email": "x"}] if self.suppressed else [])
        if url.endswith("/site_usage_events"):
            return Resp(200, [{"n": self.count}])
        if url.endswith("/internal/usage"):
            return Resp(200, text="<td>/cost-of-power/battery</td>")
        raise AssertionError(url)


ENV = {"SUPABASE_URL": "https://x.supabase.co", "SUPABASE_SERVICE_KEY": "k", "EMAIL_TOKEN_SECRET": "s", "INTERNAL_COSTS_TOKEN": "t" * 30,
       "SITE_URL": "https://erw-flame.vercel.app"}


class TheChecks(unittest.TestCase):
    def test_signed_as_the_site_signs(self):
        self.assertEqual(L.token(" A@B.co ", "confirm", "s"), hmac.new(b"s", b"a@b.co:confirm", hashlib.sha256).hexdigest())
        self.assertEqual(L.internal_cookie("tok"), hashlib.sha256(b"erw-internal-view:tok").hexdigest())

    def test_every_step_holds_on_a_working_site_and_one_broken_step_fails(self):
        with mock.patch.dict(os.environ, ENV), redirect_stdout(io.StringIO()):
            self.assertTrue(L.check_subscribe(L.TEST_EMAIL, http=FakeSite()))
            self.assertFalse(L.check_subscribe(L.TEST_EMAIL, http=FakeSite(break_confirm=True)))
            self.assertTrue(L.check_usage("/cost-of-power/battery", http=FakeSite()))

    def test_only_resends_test_addresses(self):
        with mock.patch.dict(os.environ, ENV), redirect_stdout(io.StringIO()), mock.patch("sys.stderr", io.StringIO()):
            with self.assertRaises(SystemExit) as e:
                L.main(["subscribe", "--email", "someone@example.org"])
        self.assertEqual(e.exception.code, 2)
        self.assertTrue(L.TEST_EMAIL.endswith("@resend.dev"))


class TheDomain(unittest.TestCase):
    def test_the_record_lines_are_resends_own(self):
        d = {"name": "mail.example.org", "records": [
            {"record": "SPF", "name": "send.mail", "type": "MX", "value": "feedback-smtp.us-east-1.amazonses.com", "priority": 10, "status": "not_started"},
            {"record": "DKIM", "name": "resend._domainkey.mail", "type": "TXT", "value": "p=MIGf", "status": "not_started"}]}
        out = R.lines(d)
        self.assertEqual(len(out), 3)
        self.assertIn("feedback-smtp.us-east-1.amazonses.com", out[1])
        self.assertIn("p=MIGf", out[2])

    def test_the_runbook_has_the_records_and_the_commands(self):
        with open(os.path.join(ROOT, "docs", "runbook.md"), encoding="utf-8") as f:
            text = f.read()
        part = text.split("## The sending domain: the DNS records Resend needs (session 276)", 1)[1]
        for piece in ("`feedback-smtp.us-east-1.amazonses.com`", "`v=spf1 include:amazonses.com ~all`", "`resend._domainkey.mail`",
                      "`v=DMARC1; p=none;`", "python scripts/resend_domain.py add mail.<your domain>", "python scripts/live_check.py subscribe",
                      "**0 domains in the Resend account.**"):
            self.assertIn(piece, part)
        self.assertNotIn(EM, text)
        for rel in ("scripts/live_check.py", "scripts/resend_domain.py", "tests/test_session276.py"):
            with open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8") as f:
                self.assertNotIn(EM, f.read(), rel)


if __name__ == "__main__":
    unittest.main()
