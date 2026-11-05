"""Session 2514: the package tests' reading of docs/coverage.md, a cell's escaped bar included.

Energy Research Warehouse (ERW). The daily run's package tests stopped at collection on 24 October 2026 (run
40100535695, "1 error in 0.49s"): `econtrol_austria_electricity_monthly`'s variables cell holds an escaped bar
(`build_coverage.md_line` writes "|" as "\\|"), and `coverage_md_rows` split every row on each bar. It now splits on
the unescaped ones. This test reads the file the same way: every row parses, with a whole number of rows, and the
tables are coverage.csv's. (Their counts are not compared: on 24 October `ercot_rtm_node_prices` reads 734,448 in the
markdown and 764,400 in coverage.csv on main, before this chain.) No network.

    python -m unittest tests.test_session2514 -v
"""

import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def split(ln):
    return [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip()[1:-1])]


class CoverageMarkdown(unittest.TestCase):
    def test_the_package_test_splits_on_unescaped_bars_only(self):
        with open(os.path.join(ROOT, "package", "tests", "test_erw.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('re.split(r"(?<!\\\\)\\|", ln.strip()[1:-1])', src)
        self.assertEqual(split(r"| `t` | a \| b | 1,234 |"), ["`t`", r"a \| b", "1,234"])

    def test_every_row_parses_and_the_tables_are_coverage_csv_s(self):
        with open(os.path.join(ROOT, "docs", "coverage.md"), encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.startswith("|")]
        header = split(lines[0])
        t_col, r_col = header.index("Table"), header.index("Rows")
        md = {}
        for ln in lines[2:]:
            cells = split(ln)
            self.assertEqual(len(cells), len(header), cells[0])
            md[cells[t_col].strip("`")] = int(cells[r_col].replace(",", ""))
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            cov = {r["table"] for r in csv.DictReader(f)}
        self.assertEqual(set(md), cov)
        self.assertTrue(all(isinstance(v, int) for v in md.values()))
        self.assertTrue(any(r"\|" in ln for ln in lines[2:]))     # the escaped bar the fix is for is still there


if __name__ == "__main__":
    unittest.main()
