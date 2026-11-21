"""Session 8615 (chain 504, 19 November 2026): the resource map read by the keyboard.

Energy Research Warehouse (ERW). docs/brand.md asks that whatever a hover card says be reachable by keyboard. On the
resource map the arrow keys moved the map and plus and minus zoomed it, and no value could be read (row 15 of
docs/reviews/resources-read-2026-11-19.md). When the map takes the keyboard's focus, the card now reads the place at the
map's centre, marked by a small ring, and reads it again after each move or zoom; it is announced as it changes; a
pointer takes the reading back. The browser check does it with the Tab key and an arrow key
(site/scripts/check-resources.mjs). Nothing here sets the environment or makes a request.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheKeyboardReadsTheCentre(unittest.TestCase):
    def setUp(self):
        self.m = src("site", "app", "resources", "ResourceMap.tsx")

    def test_focus_by_the_keyboard_reads_the_centre(self):
        self.assertIn('const onFocus = (e: React.FocusEvent<HTMLCanvasElement>) => { if (e.currentTarget.matches(":focus-visible")) { live.current.keys = true; readCentre(); } };', self.m)
        self.assertIn("const readCentre = () => { const r = readRef.current?.(size.current.w / 2, size.current.h / 2); if (r) setHover({ ...r, keys: true }); };", self.m)
        self.assertIn("onKeyDown={onKey} onFocus={onFocus} onBlur={onBlur}", self.m)

    def test_a_key_makes_the_keyboard_the_reader_and_the_rest_reads_the_new_centre(self):
        self.assertIn("if (keys[e.key]) { e.preventDefault(); live.current.keys = true; keys[e.key](); }", self.m)
        a = self.m.index("const settle = useCallback(() => {")
        s = self.m[a:self.m.index("const moved = useCallback(", a)]
        self.assertIn("if (L.keys && readRef.current) { const r = readRef.current(size.current.w / 2, size.current.h / 2); setHover(r ? { ...r, keys: true } : null); }", s)
        self.assertIn("else if (lp && !L.dragging && readRef.current) setHover(readRef.current(lp.x, lp.y));", s)

    def test_a_pointer_takes_the_reading_back_and_leaving_the_map_ends_it(self):
        self.assertIn("lastPointer.current = { x, y }; live.current.keys = false;", self.m)
        a = self.m.index("const onDown = ")
        self.assertIn("live.current.keys = false;", self.m[a:a + 500])
        self.assertIn("const onBlur = () => { if (live.current.keys) { live.current.keys = false; setHover(null); } };", self.m)

    def test_the_card_is_announced_only_for_the_keyboard_and_the_centre_is_marked(self):
        self.assertIn('role="status" aria-live={hover.keys ? "polite" : "off"} data-hover-keys={hover.keys ? "1" : "0"}', self.m)
        self.assertIn('{hover?.keys ? <div aria-hidden="true" data-centre-mark="1"', self.m)
        self.assertIn("style={{ left: hover.x, top: hover.y }}", self.m)

    def test_the_maps_label_says_what_the_keys_do(self):
        self.assertIn("With the keyboard: the arrow keys move the map, plus and minus zoom, and the value at the map's centre is read out", self.m)

    def test_the_keys_are_the_ones_they_were(self):
        self.assertIn('ArrowLeft: () => step(-1, 0), ArrowRight: () => step(1, 0), ArrowUp: () => step(0, -1), ArrowDown: () => step(0, 1), "+": () => zoom(1.5), "=": () => zoom(1.5), "-": () => zoom(1 / 1.5)', self.m)


class MarkupOnlyThroughTheRenderer(unittest.TestCase):
    """Row 17, and what this session got wrong. The method document shown in the fold brings its own title as a second
    heading of level 1. The first fix wrote the levels into the renderer's markup from the page (a function wrapped
    round render()), and the site's rule is that markup reaches a page only through the renderer (tests 177 and 5153):
    the landing desk's suite caught it, because only the map's own tests had been run here. The change was taken out;
    the row waits for a ruling. This holds the page to the rule."""

    def test_the_method_document_is_set_by_the_renderer_and_nothing_else(self):
        v = src("site", "app", "resources", "view.tsx")
        # session 9001 (chain 601's desk): window 3's session 9818 renders the note's headings under the page's own
        # (one h1 a page, no level skipped), so the call carries { under: true }
        self.assertIn('<article className="prose-erw" dangerouslySetInnerHTML={{ __html: render(doc, "docs/methods/resources.md", { under: true }) }} />', v)
        self.assertEqual(re.findall(r"dangerouslySetInnerHTML=\{\{ __html: (\w+)", v), ["render"])

    def test_no_function_that_rewrites_markup_is_left_behind(self):
        self.assertNotIn("headingsUnder", src("site", "lib", "resources.ts"))
        self.assertNotIn("headingsUnder", src("site", "app", "resources", "view.tsx"))
        self.assertNotIn("data-method-doc-under", src("site", "scripts", "check-resources.mjs"))


class TheCheckAndTheRead(unittest.TestCase):
    def test_the_check_uses_the_tab_key_and_an_arrow(self):
        s = src("site", "scripts", "check-resources.mjs")
        self.assertIn('await key("Tab", "Tab", 9);', s)
        self.assertIn('await key("ArrowRight", "ArrowRight", 39);', s)
        self.assertIn("the Tab key brings the map into focus and the card reads its centre, marked by a ring", s)
        self.assertIn("the mouse takes the reading back", s)
        # the keyboard is tried on the wide screen, before the phone's emulation is set
        self.assertLess(s.index('await key("Tab", "Tab", 9);'), s.index('await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 1 });'))

    def test_the_row_is_written_and_the_rows_number_on(self):
        r = src("docs", "reviews", "resources-read-2026-11-19.md")
        rows = [int(x) for x in re.findall(r"^\| (\d+) \|", r, flags=re.M)]
        self.assertEqual(rows, list(range(1, len(rows) + 1)))
        self.assertGreaterEqual(rows[-1], 17)
        self.assertRegex(r, r"(?m)^\| 15 \|.*\| fixed \(session 8615\)")
        self.assertRegex(r, r"(?m)^\| 17 \|.*\| ruling: for Samuel")

    def test_no_em_dash(self):
        for p in (("site", "app", "resources", "ResourceMap.tsx"), ("site", "scripts", "check-resources.mjs"), ("tests", "test_session8615_resources.py"), ("docs", "reviews", "resources-read-2026-11-19.md"), ("docs", "methods", "resources.md")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
