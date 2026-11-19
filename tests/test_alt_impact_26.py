"""Ruling alternative 26 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-26; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 26): a third column,
B less A? On this branch the A and B table has it (site/app/impact/Forecast.tsx). Pinned with the page's own view drawn to
HTML (site/scripts/alt-impact-diff.mjs), Lone Mountain with the local option on (A) and off (B): first-year property B less
A USD 1.07 million; over the life 16.55 million; taxes, present value 8.94 million; the jobs rows 0. 13 cells are added.

    python -m unittest tests.test_alt_impact_26 -v
"""

import json
import os
import re
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, SITE  # noqa: E402

QUERY = "tech=geothermal&state=nv&mw=36&cost=4956.83&start=2026&iaval=1&own=1.0917&ownyears=60&btech=geothermal&bstate=nv&bmw=36&bcost=4956.83&bstart=2026&biaval=0&bown=1.0917&bownyears=60"


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class BLessA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-impact-diff.mjs", JEDI_CSV, QUERY], cwd=SITE, capture_output=True, text=True, timeout=600)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_column(self):
        self.assertTrue(self.f["head"])
        self.assertEqual(len(self.f["diffs"]), 13)

    def test_lone_mountain_option_off_less_on(self):
        d = self.f["diffs"]
        self.assertEqual((M(d["prop1"]["raw"]), M(d["propl"]["raw"]), M(d["pvtax"]["raw"])), (1.07, 16.55, 8.94))
        self.assertEqual((d["cjobs"]["raw"], d["ojobs"]["raw"]), (0, 0))

    def test_on_a_phone_a_figure_is_wider_than_its_cell_and_no_word_of_one_is(self):
        """Browser row 341: the page was 409 px wide at 390. The widest figure of the third column, on one line, ends at
        409 px; no single word of any cell is wider than a cell, so breaking at the spaces is enough."""
        cells = self.f["cells"]
        self.assertEqual(len(cells), 39)
        widest = max((cells[k] for k in cells if k.startswith("d|")), key=len)
        self.assertEqual(widest, "+USD 16.6 million")
        self.assertEqual(int(GUTTER + 2 * COLUMN + PAD + len(widest) * CHAR), 409)
        self.assertGreater(max(len(t) for t in cells.values()) * CHAR, ROOM)
        for k, t in cells.items():
            for word in t.split():
                self.assertLessEqual(len(word) * CHAR, ROOM, (k, word))


class OnAPhone(unittest.TestCase):
    """Session 8401 (chain 503), browser row 341. A figure's cell is kept on one line in the mono face by the brand's rule
    for every table (site/app/tokens.css); with three cells a row on a phone that line no longer fits. Under 640 px the
    A and B table's figures break at their spaces."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(SITE, "app", "tokens.css"), encoding="utf-8") as f:
            cls.css = f.read()
        with open(os.path.join(SITE, "app", "impact", "Forecast.tsx"), encoding="utf-8") as f:
            cls.page = f.read()

    def test_three_cells_a_row_under_640_and_each_a_figure_cell(self):
        self.assertIn('className="grid grid-cols-3 border-b border-rule align-top sm:table-row" data-row={l.key}', self.page)
        self.assertEqual(self.page.count('"px-3 py-1.5 text-right sm:table-cell"'), 2, "the A and B cells and the B less A cell")
        self.assertIn(".brand-a tbody td.text-right {\n  white-space: nowrap;", self.css, "the rule the cells fall under")

    def test_the_figures_break_at_their_spaces_under_640(self):
        rules = phone_rules(self.css)
        self.assertIn(CELLS, rules, "no rule for the A and B table's figure cells under 640 px")
        self.assertIn("white-space: normal;", rules[CELLS])
        self.assertIn("overflow-wrap: anywhere;", rules[CELLS])

    def test_the_rule_wins_over_the_one_line_rule(self):
        # a class, an attribute and a class against two classes: the more specific selector, whatever the order
        self.assertTrue(CELLS.endswith("tbody td.text-right") and CELLS.startswith(".brand-a [data-compare-table] "))
        self.assertIn('data-compare-table="1"', self.page)


GUTTER, PAD = 16, 12                      # <main>'s px-4 (the brand takes the sheet's own frame away) and a cell's px-3
COLUMN = (390 - 2 * GUTTER) / 3           # three equal columns of a 390 px screen
ROOM = COLUMN - 2 * PAD                   # what a cell's words have
CHAR = 14 * 0.6                           # IBM Plex Mono at 14 px: 0.6 em a character
CELLS = ".brand-a [data-compare-table] tbody td.text-right"


def phone_rules(css):
    """Every rule inside an `@media (max-width: 639px)` block of the sheet: its declarations by its selector."""
    out = {}
    head = "@media (max-width: 639px) {"
    at = css.find(head)
    while at != -1:
        i, depth = at + len(head), 1
        while depth and i < len(css):
            depth += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css[at + len(head):i - 1]):
            for sel in re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S).split(","):
                out[sel.strip()] = out.get(sel.strip(), "") + m.group(2)
        at = css.find(head, i)
    return out


if __name__ == "__main__":
    unittest.main()
