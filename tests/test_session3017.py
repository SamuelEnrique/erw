"""Session 3017 (chain 164): the second pass over the drafts (deep/check.py) and the cards' check (deep/check_cards.py).

Energy Research Warehouse (ERW). Small files written here; no warehouse file, no network, no database.
"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
import check  # noqa: E402
import check_cards  # noqa: E402

SCRIPT = '''# Expected: 2015 1.5, 2025 3.5, change 2.0 (MW); tolerance 0.5 percent of the change.
"""A test script.

    python {this file} <a_table.csv>

"""
import sys
for ln in open(sys.argv[1], encoding="utf-8"):
    print(ln.strip())
'''


class SecondPass(unittest.TestCase):
    def test_the_usage_line_and_a_span_of_yearly_tables(self):
        self.assertEqual(check.args_of('"""x\n\n    python {this file} <a.csv> <b.csv>\n"""'), ["a.csv", "b.csv"])
        got = check.args_of("    python {this file} <t_2019.csv> ... <t_2021.csv>")
        self.assertEqual(got, ["t_2019.csv", "t_2020.csv", "t_2021.csv"])
        self.assertEqual(check.expected_of(SCRIPT)["last"], 3.5)

    def test_a_draft_reproduces_or_is_named(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "x.reproduce.py")
            with open(path, "w", encoding="utf-8") as f:
                f.write(SCRIPT)
            with open(os.path.join(d, "a_table.csv"), "w", encoding="utf-8") as f:
                f.write("2015 1.5 12\n2025 3.505 12\n")
            self.assertTrue(check.check_one(path, d)["ok"])                       # within 0.5 percent of the change
            with open(os.path.join(d, "a_table.csv"), "w", encoding="utf-8") as f:
                f.write("2015 1.5 12\n2025 3.6 12\n")
            res = check.check_one(path, d)
            self.assertFalse(res["ok"])
            self.assertIn("expected", res["why"])


class Cards(unittest.TestCase):
    def row(self, **change):
        csv = "# h\n# h\n# h\n# h\nregion,year,value,n_observations,full_year\nr,2015,1.0,1,1\nr,2016,2.0,1,1\nr,2017,3.0,1,1\nr,2026,9.0,1,0\n"
        card = {"draft": True, "chart": {"kind": "flag_line", "x": [2015, 2016, 2017], "series": [{"values": [1.0, 2.0, 3.0]}], "mark": {"x": 2017}},
                "hunt": {"files": ["d.csv"], "limits": "Some limits.", "tests": [{"passed": True}] * 5}, "footnote": "x Limits: Some limits.",
                "numbers": {"first_year": 2015, "last_year": 2017}, "subtitle": "X was 3 in 2017, against 1 in 2015, the first full year the ERW holds."}
        card.update(change)
        return {"id": "d", "state": "draft", "card": card, "files": {"d.csv": {"kind": "text", "content": csv}}}

    def test_a_card_that_holds_and_one_that_does_not(self):
        self.assertEqual(check_cards.problems(self.row()), [])
        bad = self.row(chart={"kind": "flag_line", "x": [2015, 2016, 2017], "series": [{"values": [1.0, 2.5, 3.0]}], "mark": {"x": 2017}})
        self.assertIn("a chart point is not the CSV's value", check_cards.problems(bad))
        self.assertIn("no limits sentence", check_cards.problems(self.row(footnote="nothing")))


if __name__ == "__main__":
    unittest.main()
