"""Session 5001 (chain 233): /cost-of-power/battery, the decisions block, held to the method note.

Energy Research Warehouse (ERW). What is held to:

  the battery page draws one "Decisions on this page" block at its foot, after the scenarios and before the source
    line, from lib/decisions.ts (BATTERY_DECISIONS) through the shared component of session 462, drawn open (the owner's
    ruling of 12 October 2026: the battery page has nothing collapsed);
  the shared component draws the other two pages' blocks closed, as before (no `open` passed there);
  the method note's section 12 is the same list, word for word, before the sign-off block, which names it;
  every line names its session, the keys are unique, and the list states the rulings the page follows (20 percent
    debt, 12 percent hurdle, whole months, 86 percent round trip);
  no em or en dash in what the session wrote.

No request, no model call.

    python -m unittest tests.test_session5001 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))
PAGE = ("site", "app", "cost-of-power", "battery", "page.tsx")
NOTE = ("docs", "methods", "battery_earns_algorithm.md")
LIB = ("site", "lib", "decisions.ts")
BLOCK = ("site", "components", "tool", "DecisionsBlock.tsx")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def decisions(name):
    s = src(*LIB)
    part = s[s.index(f"export const {name}"):]
    part = part[:part.index("\n];")]
    bs = chr(92)
    pat = r'\{ key: "([^"]+)", session: "([^"]+)"(?:, ruling: "([^"]+)")?,\s*\n\s*text: "((?:[^"\x5c]|\x5c.)*)" \}'
    return [(m.group(1), m.group(2), m.group(3), m.group(4).replace(bs + '"', '"')) for m in re.finditer(pat, part)]


class TheBlock(unittest.TestCase):
    def test_the_page_draws_one_open_block_before_the_source_line(self):
        page = src(*PAGE)
        self.assertEqual(page.count("<DecisionsBlock "), 1)
        self.assertIn('<DecisionsBlock id="5001" title="Decisions on this page (each with the session that made it, and the ruling where one exists)" items={BATTERY_DECISIONS} open />', page)
        self.assertLess(page.index("</BatteryDecisions>"), page.index("<DecisionsBlock "))
        self.assertLess(page.index("<DecisionsBlock "), page.index("<SourceLine "))
        self.assertIn('import { BATTERY_DECISIONS } from "@/lib/decisions";', page)

    def test_the_component_stays_closed_unless_asked(self):
        block = src(*BLOCK)
        self.assertIn("open = false", block)
        self.assertIn("open={open || undefined}", block)
        for page in (("site", "app", "cost-of-power", "seller", "page.tsx"), ("site", "app", "cost-of-power", "page.tsx")):
            tag = re.search(r"<DecisionsBlock [^>]*/>", src(*page)).group(0)
            self.assertNotIn(" open", tag, page)

    def test_every_line_names_its_session(self):
        rows = decisions("BATTERY_DECISIONS")
        self.assertEqual(len(rows), 17)
        self.assertEqual(len({r[0] for r in rows}), len(rows))
        for key, session, _ruling, text in rows:
            self.assertRegex(session, r"^sessions? \d", key)
            self.assertTrue(text.endswith("."), key)

    def test_the_rulings_are_stated(self):
        text = " ".join(r[3] for r in decisions("BATTERY_DECISIONS"))
        for words in ("20 percent of the capital at 8 percent over 20 years", "discounted at 12 percent",
                      "whole months only", "86 percent round trip", "nothing collapsed", "0 by default"):
            self.assertIn(words, text)


class TheNote(unittest.TestCase):
    def test_section_12_is_the_list_word_for_word(self):
        note = src(*NOTE)
        start = note.index("## 12. The decisions on the page (session 5001)")
        end = note.index("## Sign-off")
        self.assertLess(start, end)
        listed = re.findall(r"^\d+\. (.+)$", note[start:end], re.M)
        want = [f"{t} ({s}{'; ' + r if r else ''})" for _k, s, r, t in decisions("BATTERY_DECISIONS")]
        self.assertEqual(listed, want)

    def test_the_sign_off_names_section_12(self):
        note = src(*NOTE)
        sign = note[note.index("\n## Sign-off\n"):note.index("\n## Checks\n")]
        self.assertIn("- the decisions of section 12, the list the page shows at its foot;", sign)
        self.assertIn("- Signed off by:", sign)


class NoDashes(unittest.TestCase):
    def test_no_dash(self):
        for parts in (PAGE, LIB, BLOCK, ("tests", "test_session5001.py")):
            s = src(*parts)
            for d in DASHES:
                self.assertNotIn(d, s, parts)
        note = src(*NOTE)
        sec = note[note.index("## 12. The decisions"):note.index("## Sign-off")]
        for d in DASHES:
            self.assertNotIn(d, sec)


if __name__ == "__main__":
    unittest.main()
