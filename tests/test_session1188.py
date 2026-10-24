"""Session 1188 (chain 091): the Grid tool's method notes brought current with chain 091's rules.

Energy Research Warehouse (ERW). No network, no model, no site.

    python -m unittest tests.test_session1188 -v

The rulings list's chain 091 count is in tests/test_session1176.py (TheRulingsChain091).
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)

# Each note, and the sessions of chain 091 its first chain 091 section names in its index line.
NOTES = {
    "grid_network": ("1180", "1181", "1182", "1183", "1184", "1186", "1187", "1179", "1185"),
    "generation_mix_hourly": ("1179", "1181", "1186", "1185"),
    "generation_mix": ("1185",),
    "scarcity_hours_by_grid": ("1181", "1182", "1183", "1184", "1185", "1186"),
    "california_reliability": ("1181", "1182", "1183", "1184", "1186"),
    "ercot_grid_notices": ("1181", "1182", "1183", "1184", "1186"),
    "grid_network_v3": ("1181", "1182", "1183", "1184", "1185"),
    "grid_stress": ("1181", "1182", "1183", "1184"),
    "eia930_balance": ("1181", "1182", "1183", "1184", "1186"),
}


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def chain_section(text):
    """The note's first section headed with chain 091, up to the next second-level heading."""
    m = re.search(r"^## [^\n]*chain 091[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


class TheNotes(unittest.TestCase):
    def test_each_note_opens_its_chain_091_section_with_one_index_line(self):
        for n, sessions in NOTES.items():
            sec = chain_section(src("docs", "methods", f"{n}.md"))
            self.assertIsNotNone(sec, n)
            first = sec.strip().split("\n\n")[0]
            self.assertTrue(first.startswith("Chain 091 in this note (sessions 1178 to 1189): "), (n, first[:80]))
            for s in sessions:
                self.assertIn(s, first, (n, s))

    def test_each_chain_091_section_has_its_decisions(self):
        for n in NOTES:
            sec = chain_section(src("docs", "methods", f"{n}.md"))
            self.assertRegex(sec, r"\nDecisions \((chain 091|session 11[78]\d)", n)

    def test_what_was_missing_is_there(self):
        g = src("docs", "methods", "grid_network.md")
        stored = g.split("## The stored answers, refreshed (chain 091, 24 October 2026)")[1].split("\n## ")[0]
        for w in ("Decisions (session 1187):", "`joinGrades`", "`newestAskings`", "eval_s1133_s1114_run.json",
                  "eval_s1114_grades.json", "f2b163cf"):
            self.assertIn(w, stored)
        self.assertIn("\"The stored answers, refreshed\" below", g)
        for w in ("CAISO's whole read is guarded at its Grid readers", "outside `/api/download`'s sixty requests"):
            self.assertIn(w, g)
        h = src("docs", "methods", "generation_mix_hourly.md")
        sub = h.split("### The energy mix panel in chain 091 (sessions 1181 to 1186)")[1].split("\n## ")[0]
        for w in ("Decisions (chain 091, for this panel", "`METHOD_MIX`", "#mix-panel", "grid_mix_us48_monthly"):
            self.assertIn(w, sub)
        m = src("docs", "methods", "generation_mix.md")
        for w in ("Decisions (session 1185, the rest of its report", "`METHOD_MIX_US48`", "`TABLE_KEY`", "9,200 rows"):
            self.assertIn(w, m)
        for n, c in (("scarcity_hours_by_grid", "METHOD_SCARCITY"), ("california_reliability", "METHOD_CAISO_ALERTS"),
                     ("ercot_grid_notices", "METHOD_ERCOT_NOTICES"), ("grid_network_v3", "METHOD_REPLAY"),
                     ("grid_stress", "METHOD_STRESS_TIGHT")):
            self.assertIn(c, chain_section(src("docs", "methods", f"{n}.md")), n)

    def test_the_linked_headings_stand(self):
        # session 1184's links open these headings; adding the sections must not rename one
        for n, h in (("grid_network", "## The Grid tool's panels, every figure keyed (chain 077, 23 October 2026)"),
                     ("generation_mix_hourly", "## The Mix tab's energy mix, keyed, hourly and by month (chain 077, 23 October 2026)"),
                     ("generation_mix", "## The Lower 48 by month, the sum of the states (chain 091, 24 October 2026)"),
                     ("scarcity_hours_by_grid", "## On the Grid tool (session 1154, 23 October 2026)"),
                     ("california_reliability", "## On the Grid tool: the alert state (session 1155, 23 October 2026)"),
                     ("ercot_grid_notices", "## 6. On the Grid tool: the notice state (session 1174, 24 October 2026)"),
                     ("grid_network_v3", "## The outside grids' demand in the replay (chain 078, 24 October 2026)"),
                     ("grid_stress", "### The large tables, keyed whole (session 1168)")):
            self.assertEqual(src("docs", "methods", f"{n}.md").count("\n" + h + "\n"), 1, (n, h))

    def test_no_em_dash(self):
        for n in NOTES:
            self.assertNotIn(EM, src("docs", "methods", f"{n}.md"), n)
        self.assertNotIn(EM, src("docs", "reviews", "grid-rulings-2026-10-23.md"))
        self.assertNotIn(EM, src("archive", "sessions", "SESSION_1188_REPORT.md"))


# Session 1408 (chain 100): each note's first chain 100 section, and the sessions its index line names.
NOTES_100 = {
    "grid_network": ("1405", "1406", "1404", "1402", "1403", "1400", "1401", "1407", "1408"),
    "generation_mix_hourly": ("1402", "1403", "1404", "1405", "1406", "1400", "1401", "1407", "1408"),
}


def chain_100_sections(text):
    """Every section of the note headed with chain 100, each up to the next second-level heading."""
    return re.findall(r"^## [^\n]*chain 100[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)


class TheNotesChain100(unittest.TestCase):
    def test_each_note_opens_its_chain_100_sections_with_one_index_line(self):
        for n, sessions in NOTES_100.items():
            secs = chain_100_sections(src("docs", "methods", f"{n}.md"))
            self.assertTrue(secs, n)
            first = secs[0].strip().split("\n\n")[0]
            self.assertTrue(first.startswith("Chain 100 in this note (sessions 1400 to 1409): "), (n, first[:80]))
            for s in sessions:
                self.assertIn(s, first, (n, s))
            self.assertEqual(sum(s.count("Chain 100 in this note (sessions 1400 to 1409)") for s in secs), 1, n)

    def test_each_chain_100_section_has_its_decisions(self):
        for n in NOTES_100:
            for sec in chain_100_sections(src("docs", "methods", f"{n}.md")):
                self.assertRegex(sec, r"\nDecisions \((chain 100, )?session 140\d", n)

    def test_what_was_missing_is_there(self):
        h = src("docs", "methods", "generation_mix_hourly.md")
        for w in ("Decisions (chain 100, session 1402, the rest of its report, written by session 1408):",
                  "Decisions (chain 100, session 1403, the rest of its report, written by session 1408):",
                  "`prices_public: true`", "`scripts/page_tables.py` reads every import", "not `eia930_all_emissions`",
                  "`METHOD_HUB_PRICE` in `site/lib/gridAnchors.ts`", "(`METHOD_CLEAN_WEEK`)", "`America/Chicago` and `Etc/GMT+5`"):
            self.assertIn(w, h)
        g = src("docs", "methods", "grid_network.md")
        for w in ("Decisions (session 1405, the rest of its report, written by session 1408):", "`data-ask-order`",
                  "`data-ask-example-tab`", "`gridAskExamples`",
                  "Decisions (session 1406, the rest of its report, written by session 1408):", "`LOWER48_DEMAND_ANCHOR`",
                  "## Every panel drawn, a render case each (chain 100, 24 October 2026)", "Decisions (session 1404, written by session 1408):",
                  "a session that adds a panel adds its case to `CASES`", "No pin is retired"):
            self.assertIn(w, g)
        # session 1406's section still runs to "## Not here" with every word its test holds (tests/test_session1406.py)
        self.assertLess(g.index("## The Lower 48 on the Network tab (chain 100"), g.index("## Every panel drawn, a render case each"))
        self.assertLess(g.index("## Every panel drawn, a render case each"), g.index("## Not here"))

    def test_the_linked_headings_stand(self):
        for n, h in (("generation_mix_hourly", "## The hub's price beside the hourly mix (chain 100, 24 October 2026)"),
                     ("generation_mix_hourly", "## The cleanest hours, live (chain 100, 24 October 2026)"),
                     ("grid_network", "## The Lower 48 on the Network tab (chain 100, 24 October 2026)")):
            self.assertEqual(src("docs", "methods", f"{n}.md").count("\n" + h + "\n"), 1, (n, h))

    def test_no_em_dash(self):
        for n in NOTES_100:
            self.assertNotIn(EM, src("docs", "methods", f"{n}.md"), n)
        for p in (("archive", "sessions", "SESSION_1408_REPORT.md"), ("tests", "test_session1176.py"), ("tests", "test_session1162.py")):
            if os.path.exists(os.path.join(ROOT, *p)):
                self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
