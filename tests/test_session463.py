"""Session 463: /cost-of-power/seller ("What a generator earns"), the decisions block, the method note and the cross-checks.

Energy Research Warehouse (ERW). What is held to:

  the page draws one "Decisions on this page" block at its foot, after the scenarios and before the source line, from
    lib/decisions.ts through the shared component of session 462; session 298's sentence in the source line stays;
  the step-by-step note's section 13 is the same list, word for word, and a sign-off block follows it, before "Checks";
  the note's section 7 says what the scenarios hold since sessions 212, 298 and 353, and section 8 the NPV since ruling
    7a and how a reader runs the replication;
  the cross-checks hold session 448's thirteen rows before the ten CAISO rows (session 257 keeps those last) and still
    end the note; the page counts 34;
  the replication runs from its own folder with the standard library alone and prints the page's default figures;
  no default figure moved; no em or en dash in what the session wrote.

No request, no model call; the environment is read, never set.

    python -m unittest tests.test_session463 -v
"""

import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))
PAGE = ("site", "app", "cost-of-power", "seller", "page.tsx")
NOTE = ("docs", "methods", "generator_earns_algorithm.md")
LIB = ("site", "lib", "decisions.ts")
SELLER = ("site", "public", "seller")


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
    def test_the_page_draws_one_block_before_the_source_line(self):
        page = src(*PAGE)
        self.assertEqual(page.count("<DecisionsBlock "), 1)
        self.assertIn('<DecisionsBlock id="463" title="Decisions on this page (each with the session that made it, and the ruling where one exists)" items={GENERATOR_DECISIONS} />', page)
        self.assertLess(page.index("</SellerDecisions>"), page.index("<DecisionsBlock "))
        self.assertLess(page.index("<DecisionsBlock "), page.index("<SourceLine "))
        self.assertIn('<span data-decisions="298">', page)                  # session 298's sentence stays

    def test_every_line_names_its_session(self):
        rows = decisions("GENERATOR_DECISIONS")
        self.assertEqual(len(rows), 23)
        self.assertEqual(len({r[0] for r in rows}), len(rows))
        for key, session, ruling, text in rows:
            self.assertRegex(session, r"^sessions? \d", key)
            self.assertGreater(len(text), 30, key)
            if ruling:
                self.assertRegex(ruling, r"ruling", key)


class TheNote(unittest.TestCase):
    def test_section_13_is_the_pages_list_and_a_sign_off_follows(self):
        note = src(*NOTE)
        sec = note[note.index("\n## 13. The decisions on the page (session 463)\n"):note.index("\n## Sign-off\n")]
        lines = [l for l in sec.split("\n") if re.match(r"^\d+\. ", l)]
        rows = decisions("GENERATOR_DECISIONS")
        self.assertEqual(len(lines), len(rows))
        for i, ((key, session, ruling, text), line) in enumerate(zip(rows, lines), 1):
            self.assertEqual(line, f"{i}. {text} ({session}{'; ' + ruling if ruling else ''})", key)
        self.assertEqual(note.count("\n## Sign-off\n"), 1)
        self.assertLess(note.index("\n## Sign-off\n"), note.index("\n## Checks\n"))
        self.assertIn("- Signed off by:\n- Date:\n- Items of section 10 ruled, and how:", note)
        self.assertLess(note.index("<!-- end of the session 253 section -->"), note.index("\n## 13. The decisions"))

    def test_sections_7_and_8_say_the_page_as_it_stands(self):
        note = src(*NOTE)
        self.assertNotIn("the contract of 4.10 is the one exception", note)
        self.assertIn("since session 353 the two tax credits are scenario inputs", note)
        self.assertIn("USD -74.16 million until session 298's ruling 7a, USD -76.66 million since", note)
        self.assertIn("**Run it** (session 463, in session 381's form", note)

    def test_the_cross_checks_hold_session_448s_rows_before_caisos_ten(self):
        note = src(*NOTE)
        self.assertTrue(note.rstrip().split("\n## ")[-1].startswith("Cross-checks"))
        part = note[note.index("\n## Cross-checks\n"):]
        rows = [l for l in part.split("\n") if l.startswith("| ")][1:]
        self.assertEqual(len(rows), 34)
        new = [r for r in rows if "(session 448)" in r]
        self.assertEqual(len(new), 13)
        self.assertEqual(rows.index(new[0]), 11)
        self.assertEqual(rows.index(new[-1]), 23)
        self.assertIn("Session 463 inserted thirteen rows of session 448's reading", part)
        self.assertIn('<span data-checked-against="34">Checked against: 34 published figures (Lazard, the Annual Technology Baseline, EIA', src(*PAGE))


class TheReplication(unittest.TestCase):
    def test_the_mirror_runs_from_its_folder_alone(self):
        folder = os.path.join(ROOT, *SELLER)
        r = subprocess.run([sys.executable, "-I", "erw_2026_generator_replication.py"], cwd=folder, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        out = r.stdout
        for line in ("revenue, last twelve months, USD per kW: 59.85", "price received, weighted by generation, USD per MWh: 23.27",
                     "capture rate, percent of the flat average: 72", "debt coverage, last twelve months, times: 0.67",
                     "NPV at the hurdle rate, USD million for 100 MW: -76.66", "breakeven PPA price, the whole of the energy for the PPA term, USD per MWh: 58.36"):
            self.assertIn(line, out)


class NothingMoved(unittest.TestCase):
    def test_the_defaults_are_as_they_were(self):
        fin = src("site", "lib", "seller", "finance.ts")
        self.assertIn("export const HURDLE = 12;", fin)
        self.assertIn("hurdle: HURDLE, cshare: 0, cprice: 0, ppa: costs.life, itc: 0, ptc: 0 };", fin)
        self.assertIn("export const BATTERY_DEG = 2.6;", fin)

    def test_no_dash(self):
        for parts in (PAGE, NOTE, LIB, ("tests", "test_session463.py"), ("docs", "reviews", "packs", "generator.md")):
            text = src(*parts)
            for d in DASHES:
                self.assertNotIn(d, text, "/".join(parts))


if __name__ == "__main__":
    unittest.main()
