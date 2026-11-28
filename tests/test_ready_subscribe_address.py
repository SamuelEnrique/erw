"""wip/ready-subscribe-address (session 11406, chain 770, part C): the other choice of the small pages audit of
26 November, finding 13 (docs/reviews/small-pages-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main /subscribe?confirm=1&e=<text>&t=<64 hex digits> draws "Stop every ERW email to <text>?" for any text of any
length. On this branch the form is drawn only for an address of the form the unsubscribe route accepts, 254 characters
at most. A real link's address is well formed, so no sent email's link changes (before and after: the form); a
crafted link shows no form. The audit's test (tests/test_audit_small_13.py on wip/audit-small-13) is carried, its
ruling class now passing, and the page's own rule is run on four addresses."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


PAGE = ("site", "app", "subscribe", "page.tsx")
ROUTE_RULE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class TheAddressIsChecked(unittest.TestCase):
    def test_the_page_checks_the_address_before_drawing_it(self):
        line = next(l for l in src(*PAGE).splitlines() if "const confirm =" in l)
        self.assertIn('one("e").length <= 254 && /^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(one("e"))', line)
        self.assertIn("/^[0-9a-f]{64}$/.test(one(\"t\"))", line)

    def test_the_same_rule_as_the_route(self):
        self.assertIn("email.length > 254 || !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)", src("site", "app", "api", "unsubscribe", "route.ts"))
        ok = lambda e: len(e) <= 254 and bool(ROUTE_RULE.match(e))  # noqa: E731  the page's rule, in Python
        self.assertTrue(ok("reader@example.org"))
        self.assertFalse(ok("Your account is closed, call this number"))
        self.assertFalse(ok("a@b"))
        self.assertFalse(ok("x" * 250 + "@b.org"))


if __name__ == "__main__":
    unittest.main()
