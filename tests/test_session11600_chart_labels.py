"""Session 11600 (chain 780): two charts whose labels were printed over each other on a phone.

The read of 28 November (docs/reviews/browser-read-2026-11-28.md, rows CH2 and CH3, with pictures) found, at 390 px:

- /cost-of-power, "Cost by year": the twelve years under the bars printed over each other, each about 29 px wide in a
  column of 19. The category chart of site/components/svgchart.tsx thinned its labels only from thirteen columns up.
- /emissions (the Grid tool's Clean view), the heat map of the cleanest hours: the hours stood end to end
  ("00:0003:0006:00") and on the legend's first words. The heat chart wrote a label every k-th column with no room
  between two, and placed the labels from the foot of the drawing, which is 16 px taller where the legend takes a
  second line.

Three lines of site/components/svgchart.tsx:

- a category chart whose widest label is clearly wider than a column (by more than 15 percent) writes every k-th
  label, however few its columns; one whose labels fit, or nearly, writes all, as before; thirteen columns and more
  thin as they did;
- a heat chart's column labels keep 6 px between one and the next;
- and stand right under the cells whatever the drawing's height.

    python -m pytest tests/test_session11600_chart_labels.py
"""
import math
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def text_width(s, size=12):
    """site/components/svgchart.tsx, textWidth: the chart's own estimate of a label's width."""
    return len(s) * size * 0.56


def every_k(labels, bw):
    """The category chart's rule as the file now writes it."""
    n = len(labels)
    widest = max([1] + [text_width(s, 11) for s in labels])
    return math.ceil(widest / bw) if n > 12 or widest > bw * 1.15 else 1


class TheCategoryChart(unittest.TestCase):
    def setUp(self):
        self.chart = src("site", "components", "svgchart.tsx")

    def test_the_rule_as_written(self):
        self.assertIn("const textWidth = (s: string, size = 12) => s.length * size * 0.56;", self.chart)
        self.assertIn("const widestX = Math.max(1, ...x.map((s) => textWidth(s, 11)));", self.chart)
        self.assertIn("const everyK = every ?? (n > 12 || widestX > bw * 1.15 ? Math.ceil(widestX / bw) : 1);", self.chart)
        self.assertNotIn("const everyK = every ?? (n > 12 ? ", self.chart)

    def test_twelve_years_on_a_phone_are_thinned(self):
        years = [str(y) for y in range(2015, 2027)]
        self.assertEqual(len(years), 12)
        # as seen at 390 px: a column of 19 px, a year about 25 px wide by the chart's estimate
        k = every_k(years, 19)
        self.assertEqual(k, 2)
        self.assertLess(text_width("2015", 11), k * 19)   # a label now has room before the next one written

    def test_labels_that_fit_are_all_written_as_before(self):
        years = [str(y) for y in range(2015, 2027)]
        self.assertEqual(every_k(years, 70), 1)           # a wide screen
        self.assertEqual(every_k(years, 22), 1)           # nearly: within 15 percent, as before
        self.assertEqual(every_k(["Wind", "Solar", "Gas"], 100), 1)

    def test_thirteen_columns_and_more_thin_as_they_did(self):
        months = [f"2026-{m:02d}" for m in range(1, 13)] + ["2027-01"]
        for bw in (20, 45, 80):
            self.assertEqual(every_k(months, bw), math.ceil(text_width("2026-01", 11) / bw))


class TheHeatChart(unittest.TestCase):
    def setUp(self):
        self.chart = src("site", "components", "svgchart.tsx")

    def test_the_labels_keep_room_between_them(self):
        self.assertIn("const everyC = Math.max(1, Math.ceil((Math.max(1, ...cols.map((c) => textWidth(c, 11))) + 6) / cw));", self.chart)
        # 24 hours on a phone: a cell about 11 px, an hour about 31 px: every fourth hour, where every third stood end to end
        cw = (358 - 80 - 10) / 24
        self.assertEqual(max(1, math.ceil((text_width("00:00", 11) + 6) / cw)), 4)
        self.assertEqual(max(1, math.ceil(text_width("00:00", 11) / cw)), 3)
        # on a wide screen every hour is written, as before
        self.assertEqual(max(1, math.ceil((text_width("00:00", 11) + 6) / 45)), 1)

    def test_the_labels_stand_under_the_cells_whatever_the_height(self):
        self.assertIn('{cols.map((c, j) => (j % everyC === 0 ? <text key={c} x={L + j * cw + cw / 2} y={TOP + rows.length * ch + 14} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{c}</text> : null))}', self.chart)
        self.assertNotIn("y={height - BOT + 14}", self.chart)
        # where the legend is one line the place is the one it was: height - BOT + 14 with height = TOP + rows * ch + BOT
        self.assertIn("const height = TOP + rows.length * ch + BOT + (split ? 16 : 0);", self.chart)

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.chart)


if __name__ == "__main__":
    unittest.main()
