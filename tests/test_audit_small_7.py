"""Session 10238, the small pages' audit, finding 7 (docs/reviews/small-pages-audit-2026-11-26.md): /subscribe said the
address is "never shared". The sign-up route posts it to Resend's API for the confirmation, and the sender posts it to
Resend for every issue. The page now names Resend. How a reader asks for removal (no address or form is named on the
page) is Samuel's to say, and is not changed here."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheSenders(unittest.TestCase):
    def test_each_address_goes_to_resend(self):
        self.assertIn('fetch("https://api.resend.com/emails"', src("site", "app", "api", "subscribe", "route.ts"))
        self.assertIn('RESEND = "https://api.resend.com/emails"', src("warehouse", "news", "email_digest.py"))


class ThePage(unittest.TestCase):
    def test_the_page_names_resend(self):
        p = re.sub(r"\s+", " ", src("site", "app", "subscribe", "page.tsx"))
        self.assertNotIn("never shared", p)
        self.assertIn("it is shared with no one but Resend, the service that sends the emails", p)


if __name__ == "__main__":
    unittest.main()
