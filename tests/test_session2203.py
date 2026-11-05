"""Session 2203 (chain 086, 23 October 2026): the four explorer pages at 390 px, their accessibility and their links.
The before state is production's (main, none of the chain on it): the shots at 1280 and 390, check-390.mjs's reading
(0 findings) and check-links.mjs's (0 findings) under docs/brand/review-2203/. AccessLint is not on this machine
(docs/tooling.md: the old laptop and the desktop), so the mechanical pass was made by reading: every select a label, every
table a caption and header cells, every SVG a role and a label, every tip reachable by keyboard, focus visible; the one
fix is the shared tip mark's target, 24 px in both directions. Energy Research Warehouse (ERW)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)
REVIEW = os.path.join(ROOT, "docs", "brand", "review-2203")
PAGES = ["explore-ercot-peak-premium", "explore-demand-growth", "explore-interconnection", "prices-ercot"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBefore(unittest.TestCase):
    def test_the_eight_before_shots_and_the_two_listings_are_kept(self):
        for p in PAGES:
            for w in ("1280", "390"):
                f = os.path.join(REVIEW, f"{p}_{w}_before.png")
                self.assertTrue(os.path.exists(f) and os.path.getsize(f) > 10_000, f)
        s390 = src("docs", "brand", "review-2203", "check-390-before.txt")
        self.assertIn("4 pages read, 0 not read, 0 with a finding", s390)
        links = src("docs", "brand", "review-2203", "check-links-before.txt")
        self.assertIn("0 findings, 0 waiting for a ruling, 2 aliases", links)


class TheAccessibilityPassByReading(unittest.TestCase):
    def test_every_select_has_a_label(self):
        self.assertIn("<label className=\"flex flex-col text-xs text-muted\">\n      {label}\n      <select", src("site", "components", "AutoSubmit.tsx"))
        e = src("site", "app", "explorer", "ercot-peak-premium", "Explorer.tsx")
        self.assertEqual(e.count("<label className=\"flex items-center gap-2\">"), 2)
        self.assertEqual(e.count("<select "), 2)

    def test_every_table_has_a_caption_and_header_cells(self):
        t = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn('<caption className="sr-only">{caption}</caption>', t)
        self.assertIn('scope="col"', t)
        self.assertIn('scope="row"', t)
        for page in (("site", "app", "explore", "ercot-peak-premium", "page.tsx"), ("site", "app", "explore", "demand-growth", "page.tsx"), ("site", "app", "explore", "interconnection", "page.tsx")):
            p = src(*page)
            self.assertEqual(p.count("<ToolTable "), p.count("caption={"), "/".join(page))

    def test_every_chart_is_an_image_with_a_label_and_the_cards_are_reachable_by_keyboard(self):
        for f in (("site", "components", "tool", "GroupedBars.tsx"), ("site", "components", "tool", "SeriesChart.tsx"), ("site", "components", "svgchart.tsx"), ("site", "components", "TimeChart.tsx")):
            s = src(*f)
            self.assertIn('role="img"', s, "/".join(f))
            self.assertIn("aria-label=", s, "/".join(f))
        self.assertIn("tabIndex={0}", src("site", "components", "tool", "BarsHover.tsx"))
        self.assertIn("tabIndex={0}", src("site", "components", "tool", "SeriesChart.tsx"))

    def test_the_tip_is_reachable_by_keyboard_and_its_target_is_24_px(self):
        t = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn("aria-describedby={`tip-${id}`}", t)
        self.assertIn('role="tooltip" id={`tip-${id}`}', t)
        self.assertIn("before:absolute before:-inset-1 before:content-['']", t, "a 16 px mark with a 24 px target")
        css = src("site", "app", "tokens.css")
        self.assertIn(".brand-a .tip:focus-within [role=\"tooltip\"]", css)
        self.assertIn("outline: 2px solid var(--color-ink);", css)

    def test_no_em_dash_in_the_files(self):
        for parts in (("site", "components", "tool", "ToolPage.tsx"), ("tests", "test_session2203.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
