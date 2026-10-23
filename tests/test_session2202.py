"""Session 2202 (chain 086, 23 October 2026): the interconnection explorer figure by figure, and the stacked chart's hover
card. Every figure of /explore/interconnection carries its source in its hover (components/Num.tsx `source`, from
lib/explore/source.ts and the figure's own key; the header's count names the header line it is read from), each headline
number a Tip with the same words; a held queue's figures stay "license needed" with no source words; the tool pages'
stacked and line chart (components/tool/SeriesChart.tsx) draws the brand's hover card for the pointer and the keyboard.
Energy Research Warehouse (ERW)."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)
FILES = [("site", "components", "tool", "SeriesChart.tsx"), ("site", "app", "explore", "interconnection", "page.tsx"), ("tests", "test_session2202.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheStackedChart(unittest.TestCase):
    def test_it_draws_the_brands_card_for_the_pointer_and_the_keyboard(self):
        s = src("site", "components", "tool", "SeriesChart.tsx")
        self.assertIn('data-chart-card="1"', s)
        self.assertIn("border border-rule bg-paper px-3 py-2 text-xs", s)
        self.assertIn('className="font-mono text-ink"', s)
        for key in ("ArrowRight", "ArrowLeft", "Home", "End", "Escape"):
            self.assertIn(f'e.key === "{key}"', s)
        self.assertIn("tabIndex={0} onMouseMove={onMove} onMouseLeave={() => setHover(null)} onKeyDown={onKey}", s)
        self.assertIn("{table ? null : card}", s, "no card over the table")
        # the stacked total on the card only where there is more than one series; "not held" where a value is null
        self.assertIn('{kind === "stacked" && series.length > 1 ? <div className="flex justify-between gap-4 border-t border-rule pt-0.5">', s)
        self.assertIn('{s.values[hover] === null ? "not held" : `${fmt(s.values[hover]!)} ${unit}`}', s)
        # the <title> a category stays, and no hex value is written
        self.assertIn("<title>{says ? says(i) :", s)
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{6}\b", s))

    def test_the_figure_is_positioned_so_the_card_sits_in_it(self):
        s = src("site", "components", "tool", "SeriesChart.tsx")
        self.assertIn('<figure ref={wrap} className="relative mb-10 min-w-0" data-series-chart={id}', s)


class ThePage(unittest.TestCase):
    def setUp(self):
        self.p = src("site", "app", "explore", "interconnection", "page.tsx")

    def test_every_figure_passes_its_source_and_each_headline_a_tip(self):
        p = self.p
        self.assertIn('import { sourceOf } from "@/lib/explore/source";', p)
        self.assertEqual(p.count("<Num "), 2, "the N helper and the header's count")
        self.assertIn("<Num check={key(q, y, v)} raw={x} source={sourceWords(q, y, v)}>", p)
        self.assertIn("sourceOf(key(q, y, v), `${queueName(q)}'s queue, entry year ${y}`)", p)
        self.assertIn("tip={tipOf(v, label)}", p)
        self.assertEqual(p.count("tip={"), 1, "the three headline numbers are drawn through one map")

    def test_the_headers_count_names_the_header_line_it_is_read_from(self):
        self.assertIn('source={`${TABLE}: the header line "${UNDATED}", ${name}. Source: the table\'s own header', self.p)

    def test_a_held_queue_shows_no_figure_and_no_source(self):
        # the hold is drawn before any figure: Num draws "license needed" for a held table and carries no title of its own
        self.assertIn("if (held) {", self.p)
        self.assertIn("data-license-held={TABLE}", self.p)
        num = src("site", "components", "Num.tsx")
        self.assertTrue(num.index("const held = heldBy(check);") < num.index("title={source}"))

    def test_no_em_dash_in_the_files(self):
        for parts in FILES:
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
