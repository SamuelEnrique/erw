"""Session 8614 (chain 504, 19 November 2026): the resource map's record at rest follows the frame it describes.

Energy Research Warehouse (ERW). The map writes what it has drawn (data-drawn on the map's box, data-level on a
layer's row) when the view comes to rest, by a timer of 160 ms; the frame is drawn by requestAnimationFrame. Where the
frame came later than the timer, the record was written first and stayed wrong until the map next moved: the browser
check read "0 cells in view", or the coarser level, with the layer on the canvas (one run in three on this laptop, two
layers on production). The rest now draws a frame that is asked for and not yet drawn before it writes the record.
The browser check holds every frame back 400 ms and reads the record (site/scripts/check-resources.mjs). Nothing here
sets the environment or makes a request.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheRecordAtRest(unittest.TestCase):
    def setUp(self):
        self.m = src("site", "app", "resources", "ResourceMap.tsx")
        a = self.m.index("const settle = useCallback(() => {")
        self.settle = self.m[a:self.m.index("const moved = useCallback(", a)]

    def test_a_pending_frame_is_drawn_before_the_record_is_written(self):
        s = self.settle
        self.assertIn("const pending = raf.current !== 0;", s)
        self.assertIn("if (pending) { cancelAnimationFrame(raf.current); raf.current = 0; }", s)
        self.assertIn("if (L.moving) { L.moving = false; draw(); } else if (pending) draw();", s)
        self.assertLess(s.index("else if (pending) draw();"), s.index("el.dataset.drawn = JSON.stringify(S.drawn);"))
        self.assertLess(s.index("else if (pending) draw();"), s.index("setLevels("))

    def test_one_frame_and_no_more(self):
        # a frame at rest is drawn once: the pending one is cancelled before the rest's own
        s = self.settle
        self.assertLess(s.index("cancelAnimationFrame(raf.current)"), s.index("L.moving = false; draw();"))
        import re
        self.assertEqual(len(re.findall(r"(?<![A-Za-z])draw\(\);", s)), 2)   # the two arms of one choice ("redraw();" is another thing)

    def test_the_rest_is_still_a_timer_of_160_ms(self):
        self.assertIn("}, 160);", self.settle)


class AFingerOnAPhone(unittest.TestCase):
    """Rows 11 and 12 of the second read (docs/reviews/resources-read-2026-11-19.md). A finger that lifts is also a
    touch pointer that leaves the map: the leave took off the card the tap had just put up (measured on a build: up at
    166 ms, gone at 177 ms). And beside the finger the card was a column some 160 px wide."""

    def setUp(self):
        self.m = src("site", "app", "resources", "ResourceMap.tsx")

    def test_a_touchs_leave_does_not_take_the_card_off(self):
        self.assertIn('onPointerLeave={(e) => { if (e.pointerType === "touch") return; lastPointer.current = null; setHover(null); }}', self.m)
        self.assertNotIn("onPointerLeave={() => { lastPointer.current = null; setHover(null); }}", self.m)

    def test_a_tap_still_reads_the_place_and_a_drag_still_clears(self):
        self.assertIn('if (pointer.current && !live.current.dragging && e.pointerType === "touch") setHover(readAt(e.clientX - r.left, e.clientY - r.top));', self.m)
        a = self.m.index("const moved = useCallback(")
        self.assertIn("setHover(null);", self.m[a:a + 300])

    def test_on_a_narrow_map_the_card_takes_the_maps_width(self):
        self.assertIn("const NARROW_MAP = 480;", self.m)
        self.assertIn('data-hover-wide={hover.w < NARROW_MAP ? "1" : "0"}', self.m)
        self.assertIn('? { left: 6, right: 6, maxWidth: "none", top: hover.y > hover.h * 0.6 ? undefined : hover.y + 14, bottom: hover.y > hover.h * 0.6 ? hover.h - hover.y + 14 : undefined }', self.m)

    def test_on_a_wide_map_the_card_stands_where_it_stood(self):
        self.assertIn(": { left: hover.x > hover.w * 0.6 ? undefined : hover.x + 14, right: hover.x > hover.w * 0.6 ? hover.w - hover.x + 14 : undefined, top: hover.y > hover.h * 0.6 ? undefined : hover.y + 14, bottom: hover.y > hover.h * 0.6 ? hover.h - hover.y + 14 : undefined }}", self.m)

    def test_the_check_taps_with_a_finger(self):
        s = src("site", "scripts", "check-resources.mjs")
        self.assertIn('await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 1 });', s)
        self.assertIn('await send("Input.dispatchTouchEvent", { type: "touchStart"', s)
        self.assertIn("a finger's tap shows the value and it stays after the finger lifts", s)
        self.assertIn("a drag of the finger moves the map", s)
        # the wide screen is put back for the checks that follow
        self.assertLess(s.index('await send("Emulation.clearDeviceMetricsOverride");'), s.rindex("the page asks nothing of any other site"))
        self.assertLess(s.index("a drag of the finger moves the map"), s.index('await send("Emulation.clearDeviceMetricsOverride");'))


class TheSecondRead(unittest.TestCase):
    def test_its_cases_and_rows_are_written(self):
        r = src("docs", "reviews", "resources-read-2026-11-19.md")
        self.assertIn("## A second read (session 8614)", r)
        import re
        rows = [int(x) for x in re.findall(r"^\| (\d+) \|", r, flags=re.M)]
        self.assertEqual(rows, list(range(1, len(rows) + 1)))
        self.assertGreaterEqual(len(rows), 14)
        for n in (6, 7, 8, 9, 10):
            self.assertRegex(r, rf"(?m)^{n}\. \*\*")
        self.assertNotIn(EM, r)


class TheCheck(unittest.TestCase):
    def test_frames_are_held_back_longer_than_the_rest(self):
        s = src("site", "scripts", "check-resources.mjs")
        self.assertIn("window.requestAnimationFrame = (f) =>", s)
        self.assertIn("}, 400)); return k; };", s)
        self.assertIn("with every frame held back 400 ms, the record at rest still names", s)

    def test_no_em_dash(self):
        for p in (("site", "app", "resources", "ResourceMap.tsx"), ("site", "scripts", "check-resources.mjs"), ("tests", "test_session8614_resources.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
