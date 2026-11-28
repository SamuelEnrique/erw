"""Session 11600 (chain 780): the figures over a group of bars do not stand on each other.

The read of 28 November (docs/reviews/browser-read-2026-11-28.md, row CH1, with a picture) found on
/datacenters?view=grids, "ERCOT: what a flat load paid, by year", the figures of three bars a year written on each
other in nearly every group ("30.82" on "37.54", "36.35" on "46.56"): the middle bar's figure could not be read.

site/components/tool/GroupedBars.tsx raised every second figure by 12 units where bars are narrow (session 1855). That
keeps two bars' figures apart. With three bars of near heights the raised middle figure lands on the third's, whose bar
is a little taller. `figureYs` now places each figure 6 units over its own bar and raises it clear of any figure
before it in the group that it would stand on, and of any it then meets; never above the line under the series' names.

The rule is mirrored here in Python and held on the picture's own case, on two bars, on bars far apart in height and
on a bar that is not held.

    python -m pytest tests/test_session11600_bars_figures.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)
LINE, CHAR = 13, 6.6


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def figure_ys(xs, tops, widths, floor=26):
    """site/components/tool/GroupedBars.tsx, figureYs, line for line."""
    ys = []
    for k, top in enumerate(tops):
        if top is None:
            ys.append(None)
            continue
        y = top - 6
        for _ in range(len(tops)):
            hit = next((j for j, yj in enumerate(ys) if yj is not None and abs(xs[k] - xs[j]) < (widths[k] + widths[j]) / 2 + 2 and abs(y - yj) < LINE), None)
            if hit is None:
                break
            y = ys[hit] - LINE
        ys.append(max(floor, y))
    return ys


def stand_on_each_other(xs, ys, widths):
    return [(i, j) for i in range(len(ys)) for j in range(i + 1, len(ys)) if ys[i] is not None and ys[j] is not None
            and abs(xs[i] - xs[j]) < (widths[i] + widths[j]) / 2 and abs(ys[i] - ys[j]) < LINE - 0.001]


class TheRule(unittest.TestCase):
    def test_the_file_writes_the_rule_mirrored_here(self):
        g = src("site", "components", "tool", "GroupedBars.tsx")
        self.assertIn("export const FIGURE_LINE = 13, FIGURE_CHAR = 6.6;", g)
        self.assertIn("export function figureYs(xs: number[], tops: (number | null)[], widths: number[], floor = 26): (number | null)[] {", g)
        self.assertIn("const hit = ys.findIndex((yj, j) => yj !== null && Math.abs(xs[k] - xs[j]) < (widths[k] + widths[j]) / 2 + 2 && Math.abs(y - yj) < FIGURE_LINE);", g)
        self.assertIn("y = (ys[hit] as number) - FIGURE_LINE;", g)
        self.assertIn("ys.push(Math.max(floor, y));", g)
        self.assertIn("const ys = figureYs(g.values.map((_, k) => x0 + k * bw + bw / 2), g.values.map((v, k) => (v === null ? null : tops[k])), g.values.map((v) => (v === null ? 0 : fmt(v).length * FIGURE_CHAR)));", g)
        self.assertIn('<text key={k} x={x0 + k * bw + bw / 2} y={ys[k] as number} textAnchor="middle"', g)
        self.assertNotIn(EM, g)

    def test_the_pictures_case_three_bars_of_near_heights(self):
        # 2018 on the page: the cheapest zone 30.82, the North zone 30.82, the dearest 37.54, the first of nine groups
        # of three bars; the chart's tallest bar (2021, 151.76) sets the scale, so the three stand low and close
        W, H, L, R, top, bot = 760, 300, 54, 10, 30, 44
        hi = 151.76 * 1.12
        gw = (W - L - R) / 9
        bw = min(46, gw * 0.72 / 3)
        x0 = L + (gw - bw * 3) / 2
        xs = [x0 + k * bw + bw / 2 for k in range(3)]
        tops = [top + ((hi - v) / hi) * (H - top - bot) for v in (30.82, 30.82, 37.54)]
        widths = [5 * CHAR] * 3
        old = [tops[k] - 6 - (12 if k % 2 else 0) for k in range(3)]
        self.assertTrue(stand_on_each_other(xs, old, widths), "the rule of session 1855 put the middle figure on the third")
        new = figure_ys(xs, tops, widths)
        self.assertEqual(stand_on_each_other(xs, new, widths), [])
        self.assertEqual(new[0], tops[0] - 6)   # the first figure stays over its own bar

    def test_every_group_of_the_picture(self):
        years = [[30.82, 30.82, 37.54], [36.35, 36.35, 46.56], [21.82, 21.82, 30.80], [146.46, 150.61, 151.76], [59.90, 62.93, 70.05],
                 [45.12, 48.69, 60.05], [26.41, 26.41, 35.71], [32.66, 32.66, 42.18], [34.02, 34.07, 39.01]]
        W, H, L, R, top, bot = 760, 300, 54, 10, 30, 44
        hi = 151.76 * 1.12
        y = lambda v: top + ((hi - v) / hi) * (H - top - bot)
        gw = (W - L - R) / 9
        bw = min(46, gw * 0.72 / 3)
        for i, vals in enumerate(years):
            x0 = L + i * gw + (gw - bw * 3) / 2
            xs = [x0 + k * bw + bw / 2 for k in range(3)]
            widths = [len(f"{v:.2f}") * CHAR for v in vals]
            ys = figure_ys(xs, [y(v) for v in vals], widths)
            self.assertEqual(stand_on_each_other(xs, ys, widths), [], vals)
            self.assertTrue(all(v >= 26 for v in ys), vals)

    def test_two_bars_far_apart_in_height_are_left_over_their_bars(self):
        xs, tops, widths = [100, 118], [200, 120], [33, 33]
        self.assertEqual(figure_ys(xs, tops, widths), [194, 114])

    def test_two_bars_of_one_height_the_second_is_raised_one_line(self):
        xs, tops, widths = [100, 118], [200, 200], [33, 33]
        self.assertEqual(figure_ys(xs, tops, widths), [194, 181])

    def test_figures_that_have_room_side_by_side_are_not_raised(self):
        xs, tops, widths = [100, 150, 200], [200, 200, 200], [33, 33, 33]
        self.assertEqual(figure_ys(xs, tops, widths), [194, 194, 194])

    def test_a_bar_that_is_not_held_has_no_figure_and_moves_none(self):
        # the first and the third are 36 units apart and 33 wide: they have room side by side, and the bar between
        # them, which is not held, raises neither
        xs, tops, widths = [100, 118, 136], [200, None, 200], [33, 0, 33]
        self.assertEqual(figure_ys(xs, tops, widths), [194, None, 194])
        # nearer than their widths, the third is raised clear of the first, not of the one that is not held
        xs, tops, widths = [100, 112, 124], [200, None, 200], [33, 0, 33]
        self.assertEqual(figure_ys(xs, tops, widths), [194, None, 181])

    def test_never_above_the_line_under_the_names(self):
        xs, tops, widths = [100, 118, 136], [40, 40, 40], [40, 40, 40]
        self.assertTrue(all(v >= 26 for v in figure_ys(xs, tops, widths)))


class TheOlderTest(unittest.TestCase):
    def test_session_1855s_test_reads_the_new_rule(self):
        t = src("tests", "test_session1855.py")
        self.assertIn('self.assertIn("const ys = figureYs(", g)', t)


if __name__ == "__main__":
    unittest.main()
