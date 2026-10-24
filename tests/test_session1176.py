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


class TheRulingsChain091(unittest.TestCase):
    """Session 1188 (chain 091): the list brought current again; chain 078's assertions above stand."""

    def setUp(self):
        self.t = src("docs", "reviews", "grid-rulings-2026-10-23.md").replace("\r\n", "\n")
        rulings = self.t.split("## To finish")[0]
        self.items = [l for l in rulings.splitlines() if l.startswith("- ")]
        self.fin = [l for l in self.t.split("## To finish")[1].splitlines() if l.startswith("- ")]

    def test_none_of_the_37_ruled_said_in_one_line(self):
        self.assertIn("none of the 37 items of chains 077 and 078 has been ruled, so none is struck", self.t)
        # Session 1408: chain 100's lines (sessions 14xx) are counted in TheRulingsChain100; the 45 before them stand.
        self.assertEqual(len([l for l in self.items if not re.search(r"\(Sessions? 14\d\d[^)]*\)$", l)]), 18 + 19 + 8)

    def test_chain_091_items_one_a_line_each_with_its_recommendation(self):
        new = [l for l in self.items if re.search(r"\(Sessions? 11(7[89]|8[0-7])[^)]*\)$", l)]
        self.assertEqual(len(new), 8)
        for l in new:
            self.assertIn("Recommendation:", l)
        by = {s: sum(1 for l in new if l.endswith(f"(Session {s})")) for s in ("1182", "1183", "1184", "1185")}
        self.assertEqual(by, {"1182": 1, "1183": 2, "1184": 2, "1185": 3})
        # each group holds chain 091's lines: three groups, as before
        for head, n in (("## The page's words", 5), ("## The design", 2), ("## The data and licenses", 1)):
            part = self.t.split(head)[1].split("\n## ")[0]
            got = [l for l in part.splitlines() if l.startswith("- ") and re.search(r"\(Session 118[2-5]\)$", l)]
            self.assertEqual(len(got), n, head)

    def test_landing_first_now_1188(self):
        first = self.fin[0]
        for w in ("`wip/1188-grid`", "1152 to 1188", "`c446038c`", "1178 to 1188"):
            self.assertIn(w, first)

    def test_chain_091_to_finish(self):
        fin = "\n".join(self.fin)
        for w in ("changed `site/scripts/check-values.mjs` for every page", "verdict by verdict",
                  "\"17 of 17 drawn\"", "In a browser at that landing: one click on a \"Download this table (CSV)\" link",
                  "Chain 091's expected differences", "Done in chain 091: session 1187"):
            self.assertIn(w, fin)


class TheRulingsChain100(unittest.TestCase):
    """Session 1408 (chain 100): the list brought current again; the assertions above stand."""

    def setUp(self):
        self.t = src("docs", "reviews", "grid-rulings-2026-10-23.md").replace("\r\n", "\n")
        rulings = self.t.split("## To finish")[0]
        self.items = [l for l in rulings.splitlines() if l.startswith("- ")]
        self.fin = [l for l in self.t.split("## To finish")[1].splitlines() if l.startswith("- ")]
        # Session 1417: chain 107's lines (sessions 1410 to 1418) are counted in TheRulingsChain107; chain 100's are 1400 to 1409.
        self.new = [l for l in self.items if re.search(r"\(Sessions? 140\d[^)]*\)$", l)]

    def test_none_of_the_45_ruled_said_in_one_line(self):
        self.assertIn("none of the 45 items of chains 077, 078 and 091 has been ruled, so none is struck", self.t)
        # Session 1425: chain 111's lines (sessions 1419 to 1426) are counted in TheRulingsChain111; the 56 before chain 107's stand.
        self.assertEqual(len([l for l in self.items if not re.search(r"\(Sessions? 14[12]\d[^)]*\)$", l)]), 18 + 19 + 8 + 11)
        self.assertNotIn("~~", self.t)

    def test_chain_100_items_one_a_line_each_with_its_recommendation(self):
        self.assertEqual(len(self.new), 11)
        for l in self.new:
            self.assertIn("Recommendation:", l)
        by = {s: sum(1 for l in self.new if l.endswith(f"(Session {s})")) for s in ("1400", "1401", "1402", "1403", "1404", "1405", "1406", "1407")}
        self.assertEqual(by, {"1400": 0, "1401": 0, "1402": 3, "1403": 3, "1404": 2, "1405": 1, "1406": 2, "1407": 0})
        for head, n in (("## The page's words", 2), ("## The design", 6), ("## The data and licenses", 3)):
            part = self.t.split(head)[1].split("\n## ")[0]
            got = [l for l in part.splitlines() if l.startswith("- ") and re.search(r"\(Session 140[2-6]\)$", l)]
            self.assertEqual(len(got), n, head)

    def test_the_named_items_are_there(self):
        joined = "\n".join(self.new)
        for w in ("`prices_public: true` for NYISO, ISO-NE and MISO", "The Clean tab's license line now names `iso_rtm_hub_prices`",
                  "MISO's time zone", "63 python assertions", "The 413 pins", "raised six of session 1404's render cases' expected counts"):
            self.assertIn(w, joined)

    def test_the_weightiest_first_in_the_data_group(self):
        data = self.t.split("## The data and licenses")[1].split("## To finish")[0]
        lines = [l for l in data.splitlines() if l.startswith("- ")]
        at = [i for i, l in enumerate(lines) if re.search(r"\(Session 140[2-6]\)$", l)]
        self.assertEqual(len(at), 3)
        self.assertGreater(at[0], 3)  # the four first lines of the group stand (TheRulings above)
        self.assertIn("grids.json", lines[at[0]])
        self.assertIn("MISO's time zone", lines[at[2]])

    def test_landing_first_now_1408(self):
        first = self.fin[0]
        for w in ("`wip/1408-grid`", "1152 to 1408", "`c446038c`", "1400 to 1408", "chain 100 merged no main"):
            self.assertIn(w, first)

    def test_chain_100_to_finish(self):
        fin = "\n".join(self.fin)
        for w in ("Chain 100's expected differences", "blocked in session 1401", "the checks blocked in session 1407",
                  "`GRID_FILE_PAGES`", "`grid_hubprice_<grid>`", "`grid_cleanweek_<grid>`", "`grid_network_us48_demand`",
                  "`/grid?grid=us48&view=network` and `/grid?view=network` (13 new keys each",
                  "`docs/brand/review-1402/`", "`review-1403/`", "`review-1406/`"):
            self.assertIn(w, fin)


class TheRulingsChain107(unittest.TestCase):
    """Session 1417 (chain 107): the list brought current again; the assertions above stand."""

    def setUp(self):
        self.t = src("docs", "reviews", "grid-rulings-2026-10-23.md").replace("\r\n", "\n")
        rulings = self.t.split("## To finish")[0]
        self.items = [l for l in rulings.splitlines() if l.startswith("- ")]
        self.fin = [l for l in self.t.split("## To finish")[1].splitlines() if l.startswith("- ")]
        self.new = [l for l in self.items if re.search(r"\(Sessions? 141\d[^)]*\)$", l)]

    def test_none_of_the_56_ruled_said_in_one_line(self):
        self.assertIn("none of the 56 items of chains 077, 078, 091 and 100 has been ruled, so none is struck", self.t)
        # Session 1425: chain 111's lines (sessions 1419 to 1426) are counted in TheRulingsChain111; the 65 before them stand.
        self.assertEqual(len([l for l in self.items if not re.search(r"\(Sessions? 142\d[^)]*\)$", l)]), 18 + 19 + 8 + 11 + 9)
        self.assertNotIn("~~", self.t)

    def test_chain_107_items_one_a_line_each_with_its_recommendation(self):
        self.assertEqual(len(self.new), 9)
        for l in self.new:
            self.assertIn("Recommendation:", l)
        by = {s: sum(1 for l in self.new if l.endswith(f"(Session {s})")) for s in ("1410", "1411", "1412", "1413", "1414", "1415", "1416")}
        self.assertEqual(by, {"1410": 0, "1411": 0, "1412": 1, "1413": 2, "1414": 2, "1415": 2, "1416": 2})
        for head, n in (("## The page's words", 4), ("## The design", 3), ("## The data and licenses", 2)):
            part = self.t.split(head)[1].split("\n## ")[0]
            got = [l for l in part.splitlines() if l.startswith("- ") and re.search(r"\(Session 141[2-6]\)$", l)]
            self.assertEqual(len(got), n, head)

    def test_the_named_items_are_there(self):
        joined = "\n".join(self.new)
        for w in ("\"Method: the computed views, keyed\"", "\"Method: the Clean tab's tables, keyed\"",
                  "\"Method: the Clean tab's carbon blocks, keyed\"", "A hover or a tap on the chart gives the hour (UTC)",
                  "a reader without a pointer", "rows about 33 px tall", "dotted underline", "check-values' list of pages", "66 light reads"):
            self.assertIn(w, joined)
        # the items the reports named again stand once, on their own sessions' lines
        self.assertEqual(sum(1 for l in self.items if "green where demand was below the model" in l), 1)
        self.assertIn("Three items the reports name again are lines already here, not new", self.t)

    def test_the_weightiest_first_in_each_group(self):
        design = [l for l in self.t.split("## The design")[1].split("\n## ")[0].splitlines() if l.startswith("- ")]
        at = [i for i, l in enumerate(design) if re.search(r"\(Session 141[2-6]\)$", l)]
        pins = [i for i, l in enumerate(design) if l.endswith("(Session 1404)")]
        self.assertLess(max(at), min(pins))  # a visitor's lines before the lines on the tests
        self.assertIn("a reader without a pointer", design[at[0]])
        data = [l for l in self.t.split("## The data and licenses")[1].split("## To finish")[0].splitlines() if l.startswith("- ")]
        at = [i for i, l in enumerate(data) if re.search(r"\(Session 141[2-6]\)$", l)]
        diff = [i for i, l in enumerate(data) if "\"DIFF\" line in check-values" in l]
        self.assertEqual(at, [diff[0] + 1, diff[0] + 2])
        words = [l for l in self.t.split("## The page's words")[1].split("\n## ")[0].splitlines() if l.startswith("- ")]
        self.assertTrue(words[-4].endswith("(Session 1416)"), words[-4][-40:])

    def test_landing_first_now_1417(self):
        first = self.fin[0]
        for w in ("`wip/1417-grid`", "1152 to 1417", "1410 to 1417", "`c446038c`", "chain 107 merged none", "HTTP 402"):
            self.assertIn(w, first)

    def test_chain_107_to_finish(self):
        fin = "\n".join(self.fin)
        for w in ("Chain 107's expected differences", "the 54 python modules session 1414's run did not reach", "`89_miso_pause`",
                  "session 1411's failing-read proxy by hand", "Add session 1413's computed views to check-values' list of pages",
                  "`#the-clean-tabs-tables-keyed-whole-session-1414`", "`#yesterday-erco`", "`docs/brand/review-1413/`", "`review-1416/`",
                  "Done in chain 107: session 1411"):
            self.assertIn(w, fin)


class TheRulingsChain111(unittest.TestCase):
    """Session 1425 (chain 111): the list brought current again; the assertions above stand."""

    def setUp(self):
        self.t = src("docs", "reviews", "grid-rulings-2026-10-23.md").replace("\r\n", "\n")
        rulings = self.t.split("## To finish")[0]
        self.items = [l for l in rulings.splitlines() if l.startswith("- ")]
        self.fin = [l for l in self.t.split("## To finish")[1].splitlines() if l.startswith("- ")]
        self.new = [l for l in self.items if re.search(r"\(Sessions? 142\d[^)]*\)$", l)]

    def test_none_of_the_65_ruled_said_in_one_line(self):
        self.assertIn("none of the 65 items of chains 077, 078, 091, 100 and 107 has been ruled, so none is struck", self.t)
        self.assertIn("main at `1cf485c1`", self.t)
        self.assertEqual(len(self.items), 18 + 19 + 8 + 11 + 9 + 6)
        self.assertNotIn("~~", self.t)

    def test_chain_111_items_one_a_line_each_with_its_recommendation(self):
        self.assertEqual(len(self.new), 6)
        for l in self.new:
            self.assertIn("Recommendation:", l)
        by = {s: sum(1 for l in self.new if l.endswith(f"(Session {s})")) for s in ("1419", "1420", "1421", "1422", "1423", "1424")}
        self.assertEqual(by, {"1419": 0, "1420": 2, "1421": 3, "1422": 1, "1423": 0, "1424": 0})
        for head, n in (("## The page's words", 3), ("## The design", 3), ("## The data and licenses", 0)):
            part = self.t.split(head)[1].split("\n## ")[0]
            got = [l for l in part.splitlines() if l.startswith("- ") and re.search(r"\(Session 142[0-4]\)$", l)]
            self.assertEqual(len(got), n, head)

    def test_the_named_items_are_there(self):
        joined = "\n".join(self.new)
        for w in ("\"Download this table (CSV), its source, filter and hour (or window) in the file's first lines.\"",
                  "\"Method: \"Right now\" and the mix in that hour.\"", "\"Method: how tight was it, the daily figures.\"",
                  "existing \"Method\" links", "become named panels on the page", "about 33 px where they were about 29",
                  "`storage_daily_cycle`"):
            self.assertIn(w, joined)
        # the item session 1424 names again stands on session 1158's lines, not repeated
        self.assertEqual(sum(1 for l in self.items if "A line of the map and of the gravity shape answers a mouse" in l), 1)
        self.assertIn("One item a report names again is a line already here, not new", self.t)

    def test_the_weightiest_first_in_each_group(self):
        words = [l for l in self.t.split("## The page's words")[1].split("\n## ")[0].splitlines() if l.startswith("- ")]
        at = [i for i, l in enumerate(words) if re.search(r"\(Session 142[0-4]\)$", l)]
        method = [i for i, l in enumerate(words) if l.endswith("(Session 1184)") and "\"Method: <the section's words>\"" in l]
        self.assertEqual(at, [method[0] + 1, method[0] + 2, method[0] + 3])  # beside the 1182 and 1184 lines they extend
        self.assertTrue(words[at[0]].endswith("(Session 1420)"))
        design = [l for l in self.t.split("## The design")[1].split("\n## ")[0].splitlines() if l.startswith("- ")]
        at = [i for i, l in enumerate(design) if re.search(r"\(Session 142[0-4]\)$", l)]
        rows = [i for i, l in enumerate(design) if l.endswith("(Session 1416)")]
        pins = [i for i, l in enumerate(design) if l.endswith("(Session 1404)")]
        self.assertEqual(at, [rows[0] + 1, rows[0] + 2, rows[0] + 3])
        self.assertLess(max(at), min(pins))  # a visitor's lines before the lines on the tests
        self.assertIn("become named panels", design[at[0]])

    def test_402_first_then_the_landing_now_1425(self):
        first = self.fin[0]
        self.assertTrue(first.startswith("- First, Samuel's: production answers HTTP 402"), first[:80])
        self.assertLess(first.index("HTTP 402"), first.index("Then the combined landing"))
        for w in ("`wip/1425-grid`", "every session from 1152 to 1425", "1419 to 1425", "`c446038c`", "nor chain 111", "DEPLOYMENT_DISABLED"):
            self.assertIn(w, first)

    def test_chain_111_to_finish(self):
        fin = "\n".join(self.fin)
        for w in ("Chain 111's expected differences", "`check-table-downloads.mjs` and `check-download.mjs --grid`",
                  "\"26 of 26 drawn\"", "no `anchor` finding for the eight new fragments", "`check-390.mjs`",
                  "`check-network-v3.mjs`, its day-view sign now `net > 0`", "`docs/brand/review-1424/`",
                  "`tests/test_session1422.py`", "After a ruling that the older blocks with figures become named panels"):
            self.assertIn(w, fin)
        # chain 111's lines come after chain 107's
        at = [i for i, l in enumerate(self.fin) if l.startswith("- Chain 111's expected differences")]
        before = [i for i, l in enumerate(self.fin) if l.startswith("- Screenshots at 1280 and 390 px for chain 107")]
        self.assertEqual(at, [before[0] + 1])


if __name__ == "__main__":
    unittest.main()
