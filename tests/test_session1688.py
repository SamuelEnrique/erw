"""Session 1688 (chain 189): /learn/bill's table gives every data cell a header. AccessLint (td-has-header, serious)
found the group rows' cells and the lines' cells all <td>, so a screen reader read each amount with no name. Each
row's first cell is now a header: a group row's of its group (rowgroup), each line's, the total's and the per-kWh's of
its row; their classes keep the look. Source reading only. Nothing here sets the environment at import.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src():
    with open(os.path.join(ROOT, "site", "app", "learn", "bill", "BillCalc.tsx"), encoding="utf-8") as f:
        return f.read()


class TheBillTable(unittest.TestCase):
    def test_every_row_starts_with_a_header(self):
        s = src()
        body = s[s.index("<tbody>"):s.index("</tbody>")]
        rows = re.findall(r"<tr[^>]*>\s*<(t[hd])", body)
        self.assertEqual(len(rows), 4)
        self.assertEqual(set(rows), {"th"})

    def test_the_scopes(self):
        s = src()
        self.assertIn('<th scope="rowgroup" colSpan={2}', s)
        self.assertEqual(s.count('<th scope="row"'), 3)

    def test_the_look_is_kept(self):
        s = src()
        self.assertIn('className="py-1 pr-2 text-left font-normal"', s)
        self.assertIn('className="pt-2 text-left text-xs font-normal uppercase tracking-wide text-muted"', s)


if __name__ == "__main__":
    unittest.main()
