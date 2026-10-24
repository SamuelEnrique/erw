"""Session 1176 (chain 078): the Grid tool's method notes and the rulings list brought current.

Energy Research Warehouse (ERW). No network, no model, no site.

    python -m unittest tests.test_session1176 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)

# Each note, and the sessions of chain 078 its section names in its index line.
NOTES = {
    "grid_network": ("1165", "1167", "1171", "1172", "1175", "1170"),
    "grid_network_v3": ("1170", "1167"),
    "generation_mix_hourly": ("1166", "1167", "1169", "1168", "1171", "1174"),
    "grid_stress": ("1166", "1168"),
    "scarcity_hours_by_grid": ("1174",),
    "ercot_grid_notices": ("1174",),
    "eia930_balance": ("1165",),
    "california_reliability": ("1166", "1174"),
}


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def chain_section(text):
    """The note's first section headed with chain 078 or a session of it, up to the next second-level heading."""
    m = re.search(r"^## [^\n]*(chain 078|session 11(6[4-9]|7[0-7]))[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(3) if m else None


class TheNotes(unittest.TestCase):
    def test_each_note_opens_its_chain_078_section_with_one_index_line(self):
        for n, sessions in NOTES.items():
            sec = chain_section(src("docs", "methods", f"{n}.md").replace("\r\n", "\n"))
            self.assertIsNotNone(sec, n)
            first = sec.strip().split("\n\n")[0]
            self.assertTrue(first.startswith("Chain 078 in this note (sessions 1164 to 1177): "), (n, first[:80]))
            for s in sessions:
                self.assertIn(s, first, (n, s))

    def test_each_session_has_its_decisions(self):
        g = src("docs", "methods", "grid_network.md")
        for w in ("Decisions (chain 078):", "Decisions (session 1167):", "Decisions (session 1171):",
                  "Decisions (session 1172):", "Decisions (session 1175):", "grid_balance.json",
                  "check-network-v3.mjs` counts the rings", "TypeScript parser", "`named` false"):
            self.assertIn(w, g)
        self.assertIn("Decisions (chain 078, session 1170):", src("docs", "methods", "grid_network_v3.md"))
        h = src("docs", "methods", "generation_mix_hourly.md")
        for w in ("Decisions (session 1167):", "shownQueue", "isone_queue:137", "eia930_caiso_break.md"):
            self.assertIn(w, h)
        s = src("docs", "methods", "grid_stress.md")
        for w in ("Decisions (session 1168):", "`notes` and `tip`", "caisoJoinDay()", "A finding, not changed"):
            self.assertIn(w, s)
        self.assertIn("Decisions (session 1174):", src("docs", "methods", "scarcity_hours_by_grid.md"))
        self.assertIn("The hourly 7-day mix is not marked", src("docs", "methods", "ercot_grid_notices.md"))
        self.assertIn("Decisions (session 1165):", src("docs", "methods", "eia930_balance.md"))
        c = src("docs", "methods", "california_reliability.md")
        for w in ("Decisions (chain 078):", "awe|rows|any", "awe|newest|any"):
            self.assertIn(w, c)

    def test_no_em_dash(self):
        for n in NOTES:
            self.assertNotIn(EM, src("docs", "methods", f"{n}.md"), n)
        self.assertNotIn(EM, src("docs", "reviews", "grid-rulings-2026-10-23.md"))


class TheRulings(unittest.TestCase):
    def setUp(self):
        self.t = src("docs", "reviews", "grid-rulings-2026-10-23.md").replace("\r\n", "\n")
        rulings = self.t.split("## To finish")[0]
        self.items = [l for l in rulings.splitlines() if l.startswith("- ")]

    def test_none_ruled_said_in_one_line(self):
        self.assertIn("\nNone of the 18 items of chain 077 has been ruled: no owner input since 23 October 2026, so none is struck.\n",
                      self.t)

    def test_chain_078_items_one_a_line_each_with_its_recommendation(self):
        new = [l for l in self.items if re.search(r"\(Sessions? 11(6[4-9]|7[0-5])[^)]*\)$", l)]
        self.assertEqual(len(new), 19)
        for l in new:
            self.assertIn("Recommendation:", l)
        # every session that put an item is on a line: 1164 put none, 1173's shares 1166's line
        for s in ("1165", "1166", "1167", "1168", "1169", "1170", "1171", "1172", "1173", "1174", "1175"):
            self.assertTrue(any(s in l.rsplit("(", 1)[1] for l in new), s)

    def test_the_weightiest_first(self):
        data = self.t.split("## The data and licenses")[1].split("## To finish")[0]
        firsts = [l for l in data.splitlines() if l.startswith("- ")][:4]
        for w, l in zip(("NYISO's and MISO's queue positions", "`site/lib/supabase.ts`", "`caiso_fuel_supply`",
                         "ERCOT notices connector"), firsts):
            self.assertIn(w, l)

    def test_landing_b_first_to_finish(self):
        fin = self.t.split("## To finish")[1]
        first = [l for l in fin.splitlines() if l.startswith("- ")][0]
        for w in ("`wip/1162-grid`", "`wip/1176-grid`", "1164 to 1176"):
            self.assertIn(w, first)


if __name__ == "__main__":
    unittest.main()
