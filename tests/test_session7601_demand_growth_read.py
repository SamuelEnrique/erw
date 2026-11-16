"""Session 7601 (chain 305, part A): the demand growth page read in a browser for the old laptop's rows 24 to 27 of
docs/state/browser_reads_wanted.md, and the one fault the read found.

On /explore/demand-growth the second chart ("growth since 2019, year by year, by window") draws three bars a year and
no label on them: its label formatter gives none. The hover card took its figures from that same formatter, so every
line of every card read "percent" with no number ("The year so far (January to October)  percent", where +33.34
percent was due), on production too. The chart's hover words for a reader with no script (the SVG's own title) held the
figures, which is what the page's test read, so the test passed while the card a reader sees was empty. The chart now
hands the card its own words.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


class TheSecondChartsCard(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "explore", "demand-growth", "page.tsx")
        self.bars = src("site", "components", "tool", "GroupedBars.tsx")

    def chart(self):
        m = re.search(r'<GroupedBars id="growth-by-window"[\s\S]*?\}\)\} />', self.page)
        self.assertTrue(m, "the chart of growth by window is on the page")
        return m.group(0)

    def test_the_chart_still_draws_no_label_on_its_bars(self):
        self.assertIn('fmt={() => ""}', self.chart())

    def test_the_card_is_handed_its_own_words(self):
        c = self.chart()
        self.assertIn('cards: vs.map((v) => (v === undefined ? "not held" : `${signedText(v)} percent`)),', c)
        # the same words as the title a reader with no script gets, figure for figure
        self.assertIn('vs[k] === undefined ? "not held" : signedText(vs[k]!) + " percent"', c)

    def test_a_cards_own_words_stand_in_place_of_the_formatter(self):
        # components/tool/GroupedBars.tsx (session 1878): a group's `cards` are the card's lines, else the formatter's
        self.assertIn("g.cards?.[k] !== undefined ? { text: g.cards[k] } : { text: g.values[k] === null ? \"not held\" : `${fmt(g.values[k] as number)} ${unit}` }", self.bars)

    def test_no_other_chart_of_the_page_blanks_its_card(self):
        blank = [m.start() for m in re.finditer(re.escape('fmt={() => ""}'), self.page)]
        self.assertEqual(len(blank), 1, "one chart gives its bars no label")
        for at in blank:
            self.assertIn("cards: ", self.page[at:at + 900])

    def test_the_figure_is_written_as_the_page_writes_a_percent(self):
        self.assertIn('const signedText = (v: number) => `${v > 0 ? "+" : ""}${v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;', self.page)


class TheFaultsFile(unittest.TestCase):
    def test_the_last_row_is_the_read_and_is_fixed(self):
        doc = src("docs", "reviews", "demand-growth-faults-2026-11-16.md")
        rows = re.findall(r"(?m)^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", doc)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, 21)), "twenty rows, numbered in order")
        last = rows[-1]
        self.assertIn('read "percent" with no number', last[2])
        self.assertIn("wip/7601-demand-growth-read", last[3])
        self.assertEqual(last[4].strip(), "fixed")

    def test_no_dash(self):
        for parts in (("tests", "test_session7601_demand_growth_read.py"), ("docs", "reviews", "demand-growth-faults-2026-11-16.md"), ("site", "app", "explore", "demand-growth", "page.tsx")):
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts[-1])
            self.assertNotIn(EN_DASH, text, parts[-1])


if __name__ == "__main__":
    unittest.main()
