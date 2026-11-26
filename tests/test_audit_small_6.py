"""Session 10238, the small pages' audit, finding 6 (docs/reviews/small-pages-audit-2026-11-26.md): /subscribe said every
email carries "a signed unsubscribe link that works in one click". Since session 59 the link (a GET) only opens
/subscribe?confirm=1, which asks; the page's button (a POST) unsubscribes; one click unsubscribes only through a mail
program's own button (RFC 8058, the List-Unsubscribe headers)."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheRoute(unittest.TestCase):
    def test_the_link_asks_and_the_button_or_a_mail_program_unsubscribes(self):
        u = src("site", "app", "api", "unsubscribe", "route.ts")
        get = u.split("export async function GET", 1)[1].split("export async function POST", 1)[0]
        self.assertIn('confirm: "1"', get)
        self.assertNotIn("subscribe_unsubscribe", get)
        self.assertIn('form.get("List-Unsubscribe") === "One-Click"', u)
        self.assertIn('form.get("confirm") === "yes"', u)
        self.assertIn('"List-Unsubscribe-Post": "List-Unsubscribe=One-Click"', src("warehouse", "news", "email_digest.py"))


class ThePage(unittest.TestCase):
    def test_the_page_says_how_the_link_works(self):
        p = re.sub(r"\s+", " ", src("site", "app", "subscribe", "page.tsx"))
        self.assertNotIn("a signed unsubscribe link that works in one click", p)
        self.assertIn("it opens this page, and one press of its button stops every email", p)
        self.assertIn("a mail program that shows its own unsubscribe button stops them in one click", p)


if __name__ == "__main__":
    unittest.main()
