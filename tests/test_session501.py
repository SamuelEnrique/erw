"""Session 501: session 448's battery rows as checks.

Energy Research Warehouse (ERW). docs/methods/battery_earns_algorithm.md's "Cross-checks" table takes eight of session
448's ten battery rows (docs/reviews/cross-checks-external.json) after session 464's two Modo rows; B14 (the investment
tax credit's words) waits for Samuel's ruling, and B12 (the breakeven toll) gives the default of sessions 67 to 207, so
both stay out. The page's "Checked against" count follows the table (17 to 25). No figure the page shows moves.

    python -m unittest tests.test_session501 -v
"""

import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOTE = os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md")
PAGE = os.path.join(ROOT, "site", "app", "cost-of-power", "battery", "page.tsx")
ROWS = os.path.join(ROOT, "docs", "reviews", "cross-checks-external.json")
LEFT_OUT = ("Investment tax credit", "Breakeven toll")


def src(p):
    with open(p, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def table_rows(note):
    lines = note.split("\n")
    i = lines.index("## Cross-checks")
    while not lines[i].startswith("| Our figure"):
        i += 1
    rows = []
    for line in lines[i + 2:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip() for c in line.strip().strip("|").split(" | ")])
    return rows


def landed():
    with open(ROWS, encoding="utf-8") as f:
        d = json.load(f)
    note = next(n for n in d["notes"] if n["note"] == "battery_earns_algorithm")
    return [r for r in note["rows"] if not r["our"].startswith(LEFT_OUT)]


class TheRows(unittest.TestCase):
    def setUp(self):
        self.note = src(NOTE)
        self.rows = table_rows(self.note)
        self.want = landed()

    def test_eight_rows_land(self):
        self.assertEqual(len(self.want), 8)

    def test_the_page_counts_every_row(self):
        n = int(re.search(r'data-checked-against="(\d+)"', src(PAGE)).group(1))
        self.assertEqual(n, 25)
        self.assertEqual(len(self.rows), n)
        self.assertIn("Checked against: 25 published figures (", src(PAGE))

    def test_the_rows_are_session_448s_word_for_word_after_modos_two(self):
        self.assertIn("USD 56.01 per kW", self.rows[15][0])
        self.assertIn("46.8 percent", self.rows[16][0])
        for got, r in zip(self.rows[17:], self.want):
            self.assertEqual(got, [r["our"], r["published"], r["source"], r["gap"], r["reason"]], r["our"][:50])

    def test_b12_and_b14_are_not_rows(self):
        for got in self.rows[17:]:
            self.assertFalse(got[0].startswith(LEFT_OUT), got[0][:50])

    def test_the_note_says_what_landed_and_what_waits(self):
        i = self.note.index("**Session 501 (21 October 2026, chain 023): eight rows of session 448**")
        line = self.note[i:self.note.index("\n", i)]
        for s in ("B14", "Samuel's ruling", "B12", "USD 4.19 per kW-month", "No figure on the page moved", "from 17 to 25"):
            self.assertIn(s, line)

    def test_no_dash(self):
        for t in (self.note, src(PAGE), src(__file__)):
            self.assertNotIn(chr(0x2014), t)
            self.assertNotIn(chr(0x2013), t)


if __name__ == "__main__":
    unittest.main()
