"""Session 10238, the small pages' audit, finding 4 (docs/reviews/small-pages-audit-2026-11-26.md), a test only, not for
landing: the confirmation link confirms on a GET. Session 58/59 moved the unsubscribe off a GET because a mail scanner
or link prefetcher followed the link in a sent email and unsubscribed the address; the confirmation link is the same
kind of link, and a scanner that follows it confirms an address that may never have asked ("Nothing is sent to the
address until the link in it is followed"). The fix (the link opens /subscribe, which asks; a POST confirms) changes
what is stored and is Samuel's ruling, default "left as it is".

The first class passes on main (it shows the finding); the second fails on main and would pass with the fix."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


CONFIRM = ("site", "app", "api", "subscribe", "confirm", "route.ts")


class TheFinding(unittest.TestCase):
    def test_a_get_of_the_confirmation_link_confirms(self):
        r = src(*CONFIRM)
        get = r.split("export async function GET", 1)[1]
        self.assertIn('rpc<boolean>("subscribe_confirm"', get)

    def test_the_unsubscribe_link_was_moved_off_a_get_for_scanners(self):
        u = src("site", "app", "api", "unsubscribe", "route.ts")
        self.assertIn("the likeliest cause is a mail scanner or link prefetcher following the link (a GET)", u)
        self.assertNotIn("subscribe_unsubscribe", u.split("export async function GET", 1)[1].split("export async function POST", 1)[0])


class TheRuling(unittest.TestCase):
    def test_a_get_only_asks_and_a_post_confirms(self):
        r = src(*CONFIRM)
        get = r.split("export async function GET", 1)[1].split("export async function POST", 1)[0]
        self.assertNotIn("subscribe_confirm", get)
        self.assertRegex(r, re.compile(r"export async function POST"))


if __name__ == "__main__":
    unittest.main()
