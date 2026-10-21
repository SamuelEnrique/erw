"""Session 462: /cost-of-power ("What a datacenter pays"), the decisions block, the method notes and the cross-checks.

Energy Research Warehouse (ERW). What is held to:

  the page draws one "Decisions on this page" block at its foot, before the source line, from lib/decisions.ts through
    the shared component components/tool/DecisionsBlock.tsx: one line a choice, each naming the session that made it;
  the step-by-step note's section 12 is the same list, word for word, before the sign-off, and the sign-off names it;
  the notes no longer say the cost of capital's default is 8 percent (it is 9.6 since session 196), and say what the
    page holds since session 213;
  the cross-checks hold session 448's two rows (the ATB's gas financing, the years counted) and still end the note; the
    page counts 8; the EIA rows say the ERW holds the same figures;
  no default figure moved: the libraries' defaults are as they were;
  no em or en dash in what the session wrote.

No request, no model call; the environment is read, never set.

    python -m unittest tests.test_session462 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))
PAGE = ("site", "app", "cost-of-power", "page.tsx")
NOTE = ("docs", "methods", "datacenter_pays_algorithm.md")
COST = ("docs", "methods", "datacenter_cost.md")
LIB = ("site", "lib", "decisions.ts")
BLOCK = ("site", "components", "tool", "DecisionsBlock.tsx")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def decisions(name):
    """(key, session, ruling, text) of each line of one list of lib/decisions.ts, as the file writes it."""
    s = src(*LIB)
    part = s[s.index(f"export const {name}"):]
    part = part[:part.index("\n];")]
    bs = chr(92)
    pat = r'\{ key: "([^"]+)", session: "([^"]+)"(?:, ruling: "([^"]+)")?,\s*\n\s*text: "((?:[^"\x5c]|\x5c.)*)" \}'
    return [(m.group(1), m.group(2), m.group(3), m.group(4).replace(bs + '"', '"')) for m in re.finditer(pat, part)]


class TheBlock(unittest.TestCase):
    def test_the_page_draws_one_block_at_its_foot_before_the_source_line(self):
        page = src(*PAGE)
        self.assertEqual(page.count("<DecisionsBlock "), 1)
        self.assertIn('<DecisionsBlock id="462" title="Decisions on this page (each with the session that made it, and the ruling where one exists)" items={DATACENTER_DECISIONS} />', page)
        self.assertLess(page.index("<DecisionsBlock "), page.index("<SourceLine tables={[...INDEX.tables,"))
        self.assertGreater(page.index("<DecisionsBlock "), page.index('<ToolSection title="What matters most" id="matters">'))
        self.assertIn('import { DATACENTER_DECISIONS } from "@/lib/decisions";', page)

    def test_the_shared_block_is_the_grid_pages_form(self):
        b = src(*BLOCK)
        self.assertIn('<details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions={id}>', b)
        self.assertIn('<summary className="cursor-pointer py-1 text-accent">{title}</summary>', b)
        self.assertNotIn("style=", b)            # tokens only: no color, font or spacing of its own

    def test_every_line_names_its_session(self):
        rows = decisions("DATACENTER_DECISIONS")
        self.assertEqual(len(rows), 21)
        self.assertEqual(len({r[0] for r in rows}), len(rows))
        for key, session, ruling, text in rows:
            self.assertRegex(session, r"^sessions? \d{3}", key)
            self.assertGreater(len(text), 40, key)
            if ruling:
                self.assertRegex(ruling, r"ruling", key)


class TheNotes(unittest.TestCase):
    def test_section_12_is_the_pages_list_word_for_word(self):
        note = src(*NOTE)
        sec = note[note.index("\n## 12. The decisions on the page (session 462)\n"):note.index("\n## Sign-off\n")]
        lines = [l for l in sec.split("\n") if re.match(r"^\d+\. ", l)]
        rows = decisions("DATACENTER_DECISIONS")
        self.assertEqual(len(lines), len(rows))
        for i, ((key, session, ruling, text), line) in enumerate(zip(rows, lines), 1):
            self.assertEqual(line, f"{i}. {text} ({session}{'; ' + ruling if ruling else ''})", key)
        self.assertIn("Since session 462 it accepts the decisions of section 12", note)

    def test_the_cost_of_capital_is_said_as_it_is(self):
        note, cost = src(*NOTE), src(*COST)
        self.assertNotIn("| Scenarios: hurdle rate (session 194) | 8 percent |", note)
        self.assertIn("| Scenarios: cost of capital (session 194; the default since session 196) | 9.6 percent |", note)
        self.assertNotIn("hurdle rate of 8 percent set equal to the interest rate of Lazard's cost cases. They are the owner's to confirm.", cost)
        self.assertIn("9.6 percent, Lazard's weighted cost of a power plant's builder", cost)
        self.assertIn("**The page as it stands, 21 October 2026** (session 462)", cost)

    def test_the_cross_checks_hold_session_448s_two_rows_and_end_the_note(self):
        note = src(*NOTE)
        self.assertTrue(note.rstrip().split("\n## ")[-1].startswith("Cross-checks"))
        part = note[note.index("\n## Cross-checks"):]
        rows = [l for l in part.split("\n") if l.startswith("| ")][1:]
        rows = [r for r in rows if not set(r.replace("|", "").strip()) <= set("-")]
        self.assertEqual(len(rows), 8)
        self.assertIn("ATB, natural gas (quasi-merchant): term debt 7.5 percent, after-tax equity returns 8.5 percent", part)
        self.assertIn("| Years counted: 20", part)
        self.assertIn("the ERW holds the same figure, `eia_retail_electricity_prices`, `retail_price:TX:IND`, 2026-07, 70.7", part)
        self.assertIn("Session 448's row D1", part)
        self.assertIn('<span data-checked-against="8">Checked against: 8 published figures (EIA, Lazard, the Annual Technology Baseline).', src(*PAGE))


class NothingMoved(unittest.TestCase):
    def test_the_defaults_are_as_they_were(self):
        self.assertIn("export const LIFE = 20, HURDLE = 9.6;", src("site", "lib", "datacenter", "finance.ts"))
        dc = src("site", "lib", "datacenter.ts")
        self.assertIn("gpu: { value: 1.3,", dc)
        self.assertIn("pue: { value: 1.56,", dc)
        self.assertIn("export const NEAR = 0.95;", dc)
        self.assertIn("export const PRIOR_DAYS = 30;", dc)

    def test_no_dash(self):
        for parts in (PAGE, NOTE, COST, LIB, BLOCK, ("tests", "test_session462.py")):
            text = src(*parts)
            for d in DASHES:
                self.assertNotIn(d, text, "/".join(parts))


if __name__ == "__main__":
    unittest.main()
