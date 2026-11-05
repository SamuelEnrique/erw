"""Sessions 674 to 678: a method note for every table first written on 21 or 22 October 2026 (chain 043).

Energy Research Warehouse (ERW). docs/reviews/method-notes-plan-2026-10-23.md lists 78 tables in 49 notes; each note
must exist, name its tables on its "Tables: " line, and carry no em or en dash. docs/coverage.md links a table's note in
its last column, Method (build_coverage.py). No network.

    python -m unittest tests.test_session674 -v
"""

import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import build_coverage as B  # noqa: E402

PLAN = os.path.join(ROOT, "docs", "reviews", "method-notes-plan-2026-10-23.md")


def plan():
    """{note file: [tables]} from the plan's tables."""
    out = {}
    with open(PLAN, encoding="utf-8") as f:
        for ln in f:
            m = re.match(r"^\| `docs/methods/([a-z0-9_]+\.md)` \| ([^|]+) \|", ln)
            if m:
                out[m.group(1)] = re.findall(r"`([a-z0-9_]+)`", m.group(2))
    return out


class Notes(unittest.TestCase):
    def test_the_plan_holds_78_tables_in_49_notes(self):
        p = plan()
        self.assertEqual(len(p), 49)
        self.assertEqual(sum(len(v) for v in p.values()), 78)

    def test_every_note_names_its_tables_and_has_no_dash(self):
        for note, tables in plan().items():
            path = os.path.join(ROOT, "docs", "methods", note)
            self.assertTrue(os.path.exists(path), note)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn(chr(0x2014), text, note)
            self.assertNotIn(chr(0x2013), text, note)
            line = next((ln for ln in text.splitlines() if ln.startswith("Tables: ")), "")
            self.assertTrue(set(tables) <= set(re.findall(r"`([a-z0-9_]+)`", line)), note)

    def test_coverage_links_each_table_to_its_note(self):
        for note, tables in plan().items():
            for t in tables:
                self.assertEqual(B.method_cell(t), f"[{note[:-3]}](methods/{note})", t)

    def test_a_line_from_before_the_method_column_gains_it_once(self):
        old = "| `eia_drilling_monthly` | " + " | ".join(["x"] * 15) + " |"
        new = B.with_method(old)
        self.assertTrue(new.endswith(" [eia_drilling_monthly](methods/eia_drilling_monthly.md) |"))
        self.assertEqual(B.with_method(new), new)
        self.assertEqual(B.MD_COLS[-1], "Method")

    def test_no_em_dash_here(self):
        with open(os.path.abspath(__file__), encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
