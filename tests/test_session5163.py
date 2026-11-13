"""Session 5163: the records of the security list agree with themselves and with the code
(docs/reviews/security-faults-2026-11-13.md, docs/security.md).

Energy Research Warehouse (ERW). No network, no model, no build: the two documents and the source are read.

    the list's own count of its rows by state is the count of the rows as they read
    no row is open; a row said fixed names a test that exists
    the limits docs/security.md lists by name and number are the limits in the route handlers

    python -m unittest tests.test_session5163 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIST = ("docs", "reviews", "security-faults-2026-11-13.md")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def rows():
    """{number: (state cell, last cell)} of the list's table."""
    out = {}
    for line in src(*LIST).splitlines():
        m = re.match(r"^\| (\d+) \|", line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            out[int(m.group(1))] = (cells[4], cells[5] if len(cells) > 5 else "")
    return out


def state(cell):
    c = cell.lower()
    for word in ("closed", "fixed", "ruling", "noted", "open"):
        if c.startswith(("**" + word, word)):
            return word
    return "?"


class TheListCountsItself(unittest.TestCase):
    def test_the_rows_are_numbered_without_a_gap(self):
        r = rows()
        self.assertEqual(sorted(r), list(range(1, len(r) + 1)))
        self.assertGreaterEqual(len(r), 32)

    def test_no_row_is_open_and_every_row_has_a_state(self):
        for n, (cell, _) in rows().items():
            self.assertIn(state(cell), ("closed", "fixed", "ruling", "noted"), f"row {n}: {cell[:60]}")

    def test_the_table_of_where_the_list_stands(self):
        t = src(*LIST)
        stand = t[t.index("## Where the list stands"):]
        stand = stand[:stand.index("\n## ", 5)]
        said = {}
        for line in stand.splitlines():
            m = re.match(r"^\| (closed|fixed|ruling|noted)\b[^|]*\|([^|]*)\|\s*(\d+)\s*\|$", line)
            if m:
                said[m.group(1)] = (sorted(int(x) for x in re.findall(r"(?<![\w`.])(\d+)(?![\w.])", m.group(2).split(", and row")[0])), int(m.group(3)))
        self.assertEqual(sorted(said), ["closed", "fixed", "noted", "ruling"])
        by_state = {}
        for n, (cell, _) in rows().items():
            by_state.setdefault(state(cell), []).append(n)
        # row 8 is fixed in part and ruled in part: the table names it in both lines' words, and counts it once, as fixed
        self.assertEqual(said["closed"][0], sorted(by_state["closed"]))
        self.assertEqual(said["noted"][0], sorted(by_state["noted"]))
        self.assertEqual(said["ruling"][0], sorted(by_state["ruling"]))
        self.assertEqual(sorted(said["fixed"][0] + [8]), sorted(by_state["fixed"]))
        self.assertEqual(said["closed"][1] + said["fixed"][1] + said["ruling"][1] + said["noted"][1], len(rows()))
        first = stand.splitlines()[2]
        self.assertIn(f"{len(rows())} rows.", first)
        self.assertIn("**None is open**", first)

    def test_a_row_said_fixed_or_closed_names_a_test_that_exists(self):
        for n, (cell, last) in rows().items():
            if state(cell) not in ("fixed", "closed"):
                continue
            named = re.findall(r"`(tests/test_session\w+\.py)`", cell + " " + last)
            self.assertTrue(named, f"row {n} names no test")
            for name in named:
                self.assertTrue(os.path.exists(os.path.join(ROOT, *name.split("/"))), f"row {n}: {name}")


class TheLimitsAsTheStateFileListsThem(unittest.TestCase):
    def test_each_number_is_the_codes(self):
        s = src("docs", "security.md")
        para = s[s.index("The limits per address as they stand, 13 names:"):]
        para = para[:para.index("Two things noted")]
        code = {}
        for base, dirs, names in os.walk(os.path.join(ROOT, "site", "app")):
            dirs[:] = [d for d in dirs if d != "_retired"]
            if "route.ts" in names:
                for bucket, limit in re.findall(r'limited\(req, "(\w+)", (\d+),', open(os.path.join(base, "route.ts"), encoding="utf-8").read()):
                    code[bucket] = int(limit)
        self.assertGreaterEqual(len(code), 10)
        for bucket, limit in code.items():
            self.assertIn(f"`{bucket}`", para, bucket)
            if bucket in ("subscribe_day",):
                self.assertIn(f"`{bucket}`, {limit} a day", para)
            else:
                self.assertRegex(para, rf"`{bucket}` \({limit}\b", f"{bucket}: the state file does not say {limit}")
        for bucket in re.findall(r"`(\w+)`", para):
            self.assertTrue(bucket in code or bucket in ("ask_hour", "download"), f"the state file lists a limit the code does not have: {bucket}")


class NoDash(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5163.py"), LIST, ("docs", "security.md")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
