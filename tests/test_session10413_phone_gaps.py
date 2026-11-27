"""Session 10413 (chain 720, part E): the new views at a phone's width, by a finger.

Each view of sessions 10408 to 10411 was taken through its page's cases (docs/reviews/pages-ground-2026-11-26.md,
sections 4 and 5) at 390 px with touch events. Three kinds of link were under 24 px tall, the least a finger's target
may be (WCAG 2.5.8), and are not links inside a sentence:

- a company's name in the table of every company on /equities (18 px),
- a filing's link under a filed figure on /equities (15 px),
- a place's name in the table of every place on /forecast (18 px).

Each has padding now and a negative margin of the same size: the row or the line keeps its height (307 rows of
companies would otherwise grow), and only the place a finger lands grows. Measured in a build after the change: a
name 48 px (it wraps on a phone), a filing's link 30 px.

Left as they are, for the owner or the part's own window: the Chart and Table switch of the site's shared charts
(22 px, on every page with a chart) and the links of the shared source line (links in a line of text). The "i" mark is
no gap: drawn 16 px wide, its own code gives it a 24 px place to tap (site/components/tool/ToolPage.tsx, Tip).

    python -m pytest tests/test_session10413_phone_gaps.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)
PAD = 'className="inline-block py-1 -my-1"'


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class AFingersHeight(unittest.TestCase):
    def test_a_companys_name_in_the_table(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn('<SiteLink key="n" href={hrefOf(q, { a: c.id }, first, "#line")} ' + PAD + " title=", view)

    def test_a_filings_link(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn('? <a href={secUrl(f.url)!} className="inline-block py-1.5 -my-1.5" title=', view)

    def test_a_places_name_in_the_table(self):
        view = src("site", "app", "forecast", "view.tsx")
        self.assertIn('const name = <SiteLink key="n" href={hrefOf({ a: p.place, b: null, s, day: null, m: null })} ' + PAD + ">{placeWords(p)}</SiteLink>;", view)

    def test_the_padding_is_taken_back_by_a_margin_so_no_row_grows(self):
        for parts in (("site", "app", "equities", "view.tsx"), ("site", "app", "forecast", "view.tsx")):
            text = src(*parts)
            # wherever this session's padding is, the same negative margin stands beside it
            self.assertEqual(text.count("inline-block py-1 -my-1"), text.count("inline-block py-1 -my-1\""), parts[-2])
            self.assertNotIn('"inline-block py-1.5"', text)

    def test_the_node_tests_hold_it(self):
        self.assertIn("every company's name in the table has a finger's height", src("site", "scripts", "test-equities-filed.mjs"))
        self.assertIn("every filing's link has a finger's height", src("site", "scripts", "test-equities-filed.mjs"))
        self.assertIn("every place's name in the table has a finger's height", src("site", "scripts", "test-forecast.mjs"))


class Words(unittest.TestCase):
    def test_no_em_dash(self):
        self.assertNotIn(EM, src("tests", "test_session10413_phone_gaps.py").replace("chr(0x2014)", ""))


if __name__ == "__main__":
    unittest.main()
