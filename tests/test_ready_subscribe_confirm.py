"""wip/ready-subscribe-confirm (session 11406, chain 770, part C): the other choice of the small pages audit of
26 November, finding 4 (docs/reviews/small-pages-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the confirmation email's link confirms on a GET, so a mail scanner or link prefetcher that follows it confirms
an address that may never have asked (session 59 moved the unsubscribe link off a GET for this reason). On this branch
the link opens /subscribe, which asks ("Send ERW's emails to <address>?"), and only the page's button (a POST from the
site's own page) confirms. Figures: none on a page; how many past confirmations were a scanner's cannot be told (the
table keeps only confirmed_at). The audit's test (tests/test_audit_small_4.py on wip/audit-small-4) is carried, its
ruling class now passing."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


CONFIRM = ("site", "app", "api", "subscribe", "confirm", "route.ts")


class AGetOnlyAsks(unittest.TestCase):
    def test_a_get_only_asks_and_a_post_confirms(self):
        r = src(*CONFIRM)
        get = r.split("export async function GET", 1)[1].split("export async function POST", 1)[0]
        self.assertNotIn("subscribe_confirm", get)
        self.assertIn('confirmsub: "1"', get)
        post = r.split("export async function POST", 1)[1]
        self.assertIn('rpc<boolean>("subscribe_confirm"', post)
        self.assertIn('if (form.get("confirm") !== "yes")', post)
        self.assertIn("sameOrigin(req)", post)
        self.assertIn('limited(req, "confirm", 60, 3600)', post)

    def test_the_page_asks(self):
        p = src("site", "app", "subscribe", "page.tsx")
        self.assertRegex(p, re.compile(r'const confirmSub = one\("confirmsub"\) === "1"'))
        self.assertIn('<form method="post" action="/api/subscribe/confirm"', p)
        self.assertIn("Send ERW&apos;s emails to <strong>{one(\"e\")}</strong>?", p)
        self.assertIn("Nothing is confirmed until you press the button.", p)


if __name__ == "__main__":
    unittest.main()
