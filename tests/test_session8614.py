"""Session 8614 (chain 504, 19 November 2026): a finger on a region's hour by hour chart.

Energy Research Warehouse (ERW). On a phone a tap on the chart showed no card (row 42 of
docs/reviews/grid-map-read-2026-11-19.md): the card came up on a pointer's move, and a tap is a press and a lift with
no move between; the lift is also the touch pointer's leave. A finger's press now reads the hour as a move does, and a
touch's leave is let pass, so the card of a tap stays until the next tap. A mouse is as it was. The browser check taps
with a finger at 390 px (site/scripts/check-grid-regions.mjs). Nothing here sets the environment or makes a request.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AFingerOnTheChart(unittest.TestCase):
    def setUp(self):
        self.c = src("site", "components", "grid", "RegionHours.tsx")

    def test_a_fingers_press_reads_the_hour(self):
        self.assertIn('onPointerDown={(e) => { if (e.pointerType === "touch") point(e); }}', self.c)

    def test_a_touchs_leave_does_not_take_the_card_off(self):
        self.assertIn('onPointerMove={point} onPointerLeave={(e) => { if (e.pointerType !== "touch") setAt(null); }}', self.c)
        self.assertNotIn("onPointerLeave={() => setAt(null)}", self.c)

    def test_one_reading_of_the_hour_for_a_press_and_a_move(self):
        self.assertEqual(self.c.count("Math.floor((e.clientX - box.left - L) / bw)"), 1)
        self.assertIn("const point = (e: PointerEvent<SVGSVGElement>) =>", self.c)
        self.assertIn("setAt(i >= 0 && i < n ? i : null);", self.c)

    def test_the_card_is_the_one_it_was(self):
        self.assertIn('data-hours-card={t[at]} data-chart-card="1"', self.c)
        self.assertIn("pointer-events-none absolute top-6 z-10 border border-rule bg-paper", self.c)


class TheCheckAndTheRead(unittest.TestCase):
    def test_the_check_taps_with_a_finger_and_puts_the_mouse_back(self):
        s = src("site", "scripts", "check-grid-regions.mjs")
        a = s.index('await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 1 });')
        b = s.index('await send("Emulation.setTouchEmulationEnabled", { enabled: false });')
        self.assertLess(a, b)
        self.assertIn('{ type: "touchStart"', s[a:b])
        self.assertIn("it stays after the finger lifts", s[a:b])

    def test_the_row_is_written_and_the_rows_number_on(self):
        r = src("docs", "reviews", "grid-map-read-2026-11-19.md")
        self.assertIn("## A finger on a phone (session 8614)", r)
        rows = [int(x) for x in re.findall(r"^\| (\d+) \|", r, flags=re.M)]
        self.assertEqual(rows, list(range(1, len(rows) + 1)))
        self.assertGreaterEqual(rows[-1], 42)   # later sessions add rows after it (session 8617: rows 43 and 44)
        self.assertRegex(r, r"(?m)^\| 42 \|.*\| fixed \(session 8614\)")

    def test_no_em_dash(self):
        for p in (("site", "components", "grid", "RegionHours.tsx"), ("site", "scripts", "check-grid-regions.mjs"), ("tests", "test_session8614.py"), ("docs", "reviews", "grid-map-read-2026-11-19.md")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
