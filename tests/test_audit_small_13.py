"""Session 10238, the small pages' audit, finding 13 (docs/reviews/small-pages-audit-2026-11-26.md), a test only, not for
landing: /subscribe?confirm=1&e=<text>&t=<64 hex digits> draws "Stop every ERW email to <text>?" in bold for any text
of any length, since the page checks the token's form and not the address's. React escapes it, so nothing runs; but a
link can put a sentence of anyone's choosing on the ERW's own page. The fix (draw the form only for an address of the
form the routes accept, at most 254 characters) changes what is drawn and is Samuel's ruling, default "left as it is".

The first class passes on main (it shows the finding); the second fails on main and would pass with the fix."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


PAGE = ("site", "app", "subscribe", "page.tsx")


class TheFinding(unittest.TestCase):
    def test_the_form_is_drawn_for_any_address_text(self):
        p = src(*PAGE)
        self.assertIn('const confirm = one("confirm") === "1" && one("e") && /^[0-9a-f]{64}$/.test(one("t"));', p)
        self.assertIn("Stop every ERW email to <strong>{one(\"e\")}</strong>?", p)

    def test_the_routes_check_the_address(self):
        self.assertIn("email.length > 254 || !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)", src("site", "app", "api", "unsubscribe", "route.ts"))


class TheRuling(unittest.TestCase):
    def test_the_page_checks_the_address_before_drawing_it(self):
        line = next(l for l in src(*PAGE).splitlines() if "const confirm =" in l)
        self.assertRegex(line, re.compile(r"254|@"))


if __name__ == "__main__":
    unittest.main()
