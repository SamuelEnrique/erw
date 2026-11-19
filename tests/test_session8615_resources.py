"""Session 8615 (chain 504, 19 November 2026): the resource map read by the keyboard.

Energy Research Warehouse (ERW). docs/brand.md asks that whatever a hover card says be reachable by keyboard. On the
resource map the arrow keys moved the map and plus and minus zoomed it, and no value could be read (row 15 of
docs/reviews/resources-read-2026-11-19.md). When the map takes the keyboard's focus, the card now reads the place at the
map's centre, marked by a small ring, and reads it again after each move or zoom; it is announced as it changes; a
pointer takes the reading back. The browser check does it with the Tab key and an arrow key
(site/scripts/check-resources.mjs). Nothing here sets the environment or makes a request.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NODE = shutil.which("node")
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


@unittest.skipUnless(NODE, "node is not installed")
class OneHeadingOfLevelOne(unittest.TestCase):
    """Row 17: the method document shown in the fold under the map brought its own h1, a second on the page."""

    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--input-type=module", "-e",
                            "import { headingsUnder as u } from './lib/resources.ts';"
                            "console.log(JSON.stringify({ a: u('<h1>T</h1><p>x</p><h2 id=\"s\">S</h2><h3>a</h3><h4>b</h4>', 3), kept: u('<h2 aria-level=\"2\">S</h2>', 3),"
                            " none: u('<h1>T</h1>', 0), text: u('<p>the h1 of a page</p><header>x</header>', 3) }));"],
                           cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert r.returncode == 0, r.stderr
        cls.d = json.loads(r.stdout.strip().splitlines()[-1])

    def test_each_heading_keeps_its_tag_and_takes_its_level_in_the_page(self):
        self.assertEqual(self.d["a"], '<h1 aria-level="4">T</h1><p>x</p><h2 id="s" aria-level="5">S</h2><h3 aria-level="6">a</h3><h4 aria-level="6">b</h4>')

    def test_a_level_already_said_is_kept_and_no_level_above_changes_nothing(self):
        self.assertEqual(self.d["kept"], '<h2 aria-level="2">S</h2>')
        self.assertEqual(self.d["none"], "<h1>T</h1>")

    def test_only_heading_tags_are_touched(self):
        self.assertEqual(self.d["text"], "<p>the h1 of a page</p><header>x</header>")

    def test_the_page_puts_the_document_under_its_h3(self):
        v = src("site", "app", "resources", "view.tsx")
        self.assertIn('dangerouslySetInnerHTML={{ __html: headingsUnder(render(doc, "docs/methods/resources.md"), 3) }}', v)
        a = v.index('<section data-method-doc="1">')
        self.assertIn("<h3 ", v[a:a + 200])


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
        self.assertRegex(r, r"(?m)^\| 17 \|.*\| fixed \(session 8615\)")

    def test_no_em_dash(self):
        for p in (("site", "app", "resources", "ResourceMap.tsx"), ("site", "scripts", "check-resources.mjs"), ("tests", "test_session8615_resources.py"), ("docs", "reviews", "resources-read-2026-11-19.md"), ("docs", "methods", "resources.md")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
