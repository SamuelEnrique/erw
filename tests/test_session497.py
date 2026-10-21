"""Session 497: two faults that need no ruling.

1. check-values compared the queue's active MW on /datacenters?view=grids (dcq|<grid>|<zone>|active_mw) with the
   number as the table holds it (298,605.97), while the page writes it whole (app/datacenters/GridsView.tsx whole()), so
   the key failed on every build (sessions 461 and 417). The whole-MW rule of check-values (session 16, session 356) now
   names it; the MW asked, which the page writes with its decimals (mw()), is left to the exact rule.
2. The five-grid cards' render frames (/research/card/<id>?render=1, photographed at 1600 x 900 and 1080 x 1350):
   since sessions 317 and 318 the small multiples are a column of SVG panels, each about 170 px tall with its title and
   its Chart | Table toggle, in a box the canvas sized (250 px wide frame); the column ran past its box over the callouts
   and the paragraph, and its labels below the 1600 x 900 picture (952 and 924 px, session 474). In the wide frame the
   panels stand side by side again inside the same box, and the toggle, a control, is off the picture in both frames.
   The measures are the browser's (docs/brand/review-497/before/ and after/measures.txt, check-findings-grids); these
   tests hold the rules in the files."""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
VALUES = os.path.join(SITE, "scripts", "check-values.mjs")
GRIDS_VIEW = os.path.join(SITE, "app", "datacenters", "GridsView.tsx")
RENDER = os.path.join(SITE, "app", "research", "card", "render.css")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_497_REPORT.md")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def whole_rule():
    m = re.search(r"const whole = /(.+)/\.test\(check\);", read(VALUES))
    assert m, "the whole-MW rule of check-values"
    return re.compile(m.group(1))


class WholeMw(unittest.TestCase):
    def test_the_active_mw_key_is_read_whole(self):
        w = whole_rule()
        self.assertTrue(w.search("dcq|ercot|-|active_mw"))
        self.assertTrue(w.search("dcq|caiso|SP15|active_mw"))

    def test_the_other_queue_keys_keep_the_exact_rule(self):
        w = whole_rule()
        for k in ("dcq|ercot|-|mw_asked", "dcq|ercot|-|sites", "dcq|ercot|-|active_positions", "dcq|ercot|-|active_mw_x"):
            self.assertFalse(w.search(k), k)

    def test_the_rules_before_it_still_hold(self):
        w = whole_rule()
        self.assertTrue(w.search("projects|mw|solar"))
        self.assertTrue(w.search("datacenters|state_mw|TX"))

    def test_the_page_writes_active_mw_whole_and_mw_asked_with_decimals(self):
        s = read(GRIDS_VIEW)
        self.assertRegex(s, r"\|active_mw`\} raw=\{g\.activeMw\}>\{whole\(g\.activeMw\)\}")
        self.assertRegex(s, r"\|mw_asked`\} raw=\{g\.mwAsked\}>\{mw\(g\.mwAsked\)\}")


class RenderFrame(unittest.TestCase):
    def setUp(self):
        self.css = read(RENDER)
        self.s497 = self.css[self.css.index("Session 497"):]

    def test_the_toggle_is_off_the_picture(self):
        self.assertIn(".finding-render div:has(> [data-chart-table]) { display: none; }", self.s497)

    def test_the_wide_frame_stands_the_panels_side_by_side(self):
        m = re.search(r"@media \(min-aspect-ratio: 3/2\) \{\s*\.finding-render \[data-finding-chart=\"multiples\"\]\[data-option-kind=\"panels\"\] \{([^}]*)\}", self.s497)
        self.assertTrue(m)
        body = m.group(1)
        for rule in ("display: grid;", "grid-auto-flow: column;", "grid-auto-columns: minmax(0, 1fr);"):
            self.assertIn(rule, body)

    def test_no_box_height_or_value_changed(self):
        # the boxes' heights are session 182's, untouched: the panels are placed, not shrunk or cut
        for line in ('.finding-render [data-finding-chart="multiples"] { height: 430px !important; }',
                     '.finding-render [data-finding="peak_hour_grids"] [data-finding-chart="multiples"] { height: 620px !important; }',
                     '.finding-render [data-finding-chart="multiples"] { height: 250px !important; }'):
            self.assertEqual(self.css.count(line), 1, line)
        self.assertNotIn("overflow: hidden", self.s497)

    def test_no_dash(self):
        dash = re.compile("[" + chr(0x2013) + chr(0x2014) + "]")
        mine = [read(RENDER)[read(RENDER).index("Session 497"):], read(__file__)]
        if os.path.exists(REPORT):
            mine.append(read(REPORT))
        for text in mine:
            self.assertIsNone(dash.search(text))

if __name__ == "__main__":
    unittest.main()
