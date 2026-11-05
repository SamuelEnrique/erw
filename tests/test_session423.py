"""Session 423: the footer's links and the touch targets session 412 left (chain 021).

docs/brand.md section 2: "A link in running text is underlined". The footer's three links stand in its one sentence and
were told from it by their color alone (WCAG 1.4.1; axe-core's link-in-text-block on every page): they are underlined in
app/tokens.css. WCAG 2.2's 2.5.8 (24 px, or spacing) failed in two places, measured by scripts/check-targets.mjs and by
axe-core's target-size: the header's aside at 390 px (its row sits between the menus and the internal line) and the
three names alone on their line on /about; each is 24 px tall now. The internal view's lock link, a muted link in a
muted line, is underlined. Nothing else moves; no figure changes.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_423_REPORT.md")
SHOTS = os.path.join(ROOT, "docs", "brand", "review-423")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def rule(css, selector):
    """The body of the first CSS rule whose selector list is exactly `selector`."""
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return m.group(1) if m else None


class TheFooter(unittest.TestCase):
    def test_the_footers_links_are_underlined(self):
        body = rule(src("site", "app", "tokens.css"), "body:has(.brand-a) > footer a")
        self.assertIsNotNone(body, "the footer's link rule")
        self.assertIn("text-decoration: underline;", body)
        self.assertIn("text-decoration-thickness: 1px;", body)
        self.assertIn("text-underline-offset: 2px;", body)

    def test_the_footer_still_draws_its_three_links_through_the_gate(self):
        layout = src("site", "app", "layout.tsx")
        for s in ('<Link href="/data" gate="quiet">Data and methods</Link>', '<Link href="/terms">Terms</Link>', '<Link href="/privacy">Privacy</Link>'):
            self.assertIn(s, layout)

    def test_a_page_in_review_is_not_underlined_as_a_link(self):
        # a gated link is a span with gate-review or gate-plain: the footer rule names the element a, never a span
        self.assertIn("<span className={`${props.className ?? \"\"} ${gate === \"plain\" ? \"gate-plain\" : \"gate-review\"}`}", src("site", "components", "SiteLink.tsx"))
        self.assertNotIn("footer span", src("site", "app", "tokens.css"))


class TheTargets(unittest.TestCase):
    def test_the_asides_links_are_24_px_tall(self):
        nav = src("site", "components", "Nav.tsx")
        self.assertIn('className="inline-flex min-h-6 items-center no-underline hover:underline"', nav)
        self.assertIn('className="nav-aside ml-auto flex flex-wrap gap-x-4"', nav)   # session 203's row, unchanged

    def test_a_name_alone_on_its_line_on_about_is_24_px_tall(self):
        page = src("site", "app", "about", "page.tsx")
        self.assertIn('className={nameOnly(p.href) ? "inline-flex min-h-6 items-center" : undefined}', page)
        self.assertIn('{nameOnly(p.href) ? null : <>: {p.line}</>}', page)

    def test_the_lock_is_underlined(self):
        self.assertIn('internal view <a href="/internal/lock" className="text-muted underline">lock</a>', src("site", "components", "Nav.tsx"))

    def test_min_h_6_is_24_px(self):
        # Tailwind 4's spacing unit is 0.25rem: min-h-6 is 1.5rem, 24 px at the site's 16 px root
        self.assertRegex(src("site", "package.json"), r'"tailwindcss":\s*"\^4')


class TheCheck(unittest.TestCase):
    def test_the_check_reads_both_rules_and_the_inline_exception(self):
        s = src("site", "scripts", "check-targets.mjs")
        for needle in ("WCAG 1.4.1", "2.5.8", "textDecorationLine", "inline (exempt)", 'const PAGES = ["/", "/about"]', "const WIDTHS = [1280, 390]", "unlock(base)"):
            self.assertIn(needle, s)
        self.assertIn("process.exitCode = code !== 0 ? 1 : failures ? 1 : 0;", s)

    def test_the_spacing_rule_is_wcags(self):
        s = src("site", "scripts", "check-targets.mjs")
        self.assertIn("const cx = t.x + t.w / 2, cy = t.y + t.h / 2, R = 12;", s)
        self.assertIn("if (Math.hypot(ox - cx, oy - cy) < 2 * R) return false;", s)


class TheRecord(unittest.TestCase):
    FILES = [
        ("site", "app", "tokens.css"), ("site", "components", "Nav.tsx"), ("site", "app", "about", "page.tsx"),
        ("site", "scripts", "check-targets.mjs"), ("tests", "test_session423.py"),
    ]

    def test_no_em_or_en_dash_in_what_the_session_wrote(self):
        files = list(self.FILES)
        if os.path.exists(REPORT):
            files.append(("archive", "sessions", "SESSION_423_REPORT.md"))
        if os.path.exists(os.path.join(SHOTS, "README.md")):
            files.append(("docs", "brand", "review-423", "README.md"))
        for p in files:
            text = src(*p)
            self.assertNotIn(chr(0x2014), text, p)
            self.assertNotIn(chr(0x2013), text, p)

    def test_the_shots_before_are_there(self):
        for w in (1280, 390):
            for name in ("home-header", "home-footer", "about"):
                self.assertTrue(os.path.exists(os.path.join(SHOTS, "before", f"{name}_before_{w}.png")), (name, w))


if __name__ == "__main__":
    unittest.main()
