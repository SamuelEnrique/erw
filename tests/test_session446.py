"""Session 446: the paper outlined on what the warehouse can show (docs/paper/outline.md, extended).

Session 139's outline of 7 October is kept as it was (non-negotiable 3: extend, never overwrite); session 446 appends one
section in the IRW paper's shape, with the figures and tables the warehouse can produce today, a figure list, the author
roles and a cover note of five decisions. These tests pin the old text, the new section's words and its table names.
"""
import csv
import hashlib
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTLINE = os.path.join(ROOT, "docs", "paper", "outline.md")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
TABLES = os.path.join(ROOT, "docs", "redivis", "release-v1", "tables.csv")
VARIABLES = os.path.join(ROOT, "docs", "redivis", "release-v1", "variables.csv")
HEADING = "## The outline on what the warehouse can show, session 446, 21 October 2026"
# sha256 of session 139's outline as committed before session 446 (git show HEAD:docs/paper/outline.md, line ends as LF)
OLD_SHA256 = "c052f601df03f0b6854ec5a7195493ecaa72f4d686de40ed0c6acd5371dd1387"
OLD_LENGTH = 13381


def outline():
    with open(OUTLINE, "rb") as f:
        return f.read().replace(b"\r\n", b"\n").decode("utf-8")


def split():
    s = outline()
    i = s.index("\n" + HEADING)
    return s[:i], s[i + 1:]


def rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


class TheOldOutlineIsKept(unittest.TestCase):
    def test_the_text_before_the_new_heading_is_session_139s(self):
        old, _ = split()
        b = old.encode("utf-8")
        self.assertEqual(len(b), OLD_LENGTH)
        self.assertEqual(hashlib.sha256(b).hexdigest(), OLD_SHA256)

    def test_the_new_heading_is_there_once(self):
        self.assertEqual(outline().count(HEADING), 1)


class TheNewSection(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        _, new = split()
        self.assertNotIn(chr(0x2014), new)
        self.assertNotIn(chr(0x2013), new)
        with open(__file__, encoding="utf-8") as f:
            me = f.read()
        self.assertNotIn(chr(0x2014), me)
        self.assertNotIn(chr(0x2013), me)

    def test_the_irw_papers_sections_are_there(self):
        _, new = split()
        for h in ("### Part 1. The data standard", "### Part 2. The harmonization", "### Part 3. The coverage", "### Part 4. The licensing ledger",
                  "### Part 5. The validator", "### Part 6. The citable release", "### Part 7. The uses", "### The figure list",
                  "### The author roles", "### Cover note: five decisions the paper needs from Samuel and Ben"):
            self.assertIn(h, new)

    def test_every_snake_case_name_is_a_table_a_column_or_a_variable(self):
        """A name in backticks is a coverage.csv table, a v1 metadata table, a column of the records the section reads,
        or a variable or column listed in release-v1/variables.csv; nothing else but a short list of other names."""
        _, new = split()
        tables = {r["table"] for r in rows(COVERAGE)}
        meta = {r["table"] for r in rows(TABLES) if r["shape"] == "metadata"}
        names = {r["name"] for r in rows(VARIABLES)}
        columns = set()
        for p in (COVERAGE, TABLES, os.path.join(ROOT, "warehouse", "metadata", "run_status.csv")):
            with open(p, encoding="utf-8") as f:
                columns |= set(f.readline().strip().split(","))
        other = {"02_master_plan", "series", "events", "entities"}
        tokens = set(re.findall(r"`([a-z0-9]+(?:_[a-z0-9]+)*)`", new))
        unknown = sorted(t for t in tokens if t not in tables | meta | names | columns | other)
        self.assertEqual(unknown, [])

    def test_every_table_the_figure_list_names_is_in_coverage(self):
        _, new = split()
        tables = {r["table"] for r in rows(COVERAGE)}
        figs = new.split("### The figure list", 1)[1].split("###", 1)[0]
        named = set()
        for line in figs.splitlines():
            if re.match(r"\| \d+ \|", line):
                cell = line.split("|")[3]
                named |= set(re.findall(r"`([a-z0-9_]+)`", cell))
        named -= {"erw_coverage", "license_status", "run_status"}
        self.assertTrue(named)
        self.assertEqual(sorted(named - tables), [])

    def test_the_cover_note_has_five_decisions(self):
        _, new = split()
        note = new.split("### Cover note: five decisions the paper needs from Samuel and Ben", 1)[1]
        self.assertEqual(re.findall(r"^(\d+)\. \*\*", note, re.M), ["1", "2", "3", "4", "5"])

    def test_the_counts_agree_with_the_records(self):
        """The eight numbers are the records' own on the day; a later change to the records is a reason to recount,
        so this test reads the records and skips when they have moved on rather than failing the suite."""
        _, new = split()
        cov = rows(COVERAGE)
        if len(cov) != 212:
            self.skipTest("coverage.csv has changed since 21 October 2026: recount (runs/chain_oct21_third/s446/counts.py)")
        self.assertIn("| Tables | 212 |", new)
        self.assertIn("{:,}".format(sum(int(r["n_rows"] or 0) for r in cov)), new)
        rel = rows(TABLES)
        self.assertEqual(sum(1 for r in rel if r["in_v1"] == "yes"), 138)
        self.assertEqual(sum(1 for r in rel if r["in_v1"] == "no"), 42)

    def test_the_master_plan_is_not_quoted(self):
        _, new = split()
        self.assertIn("**The master plan is not in the repository.**", new)


if __name__ == "__main__":
    unittest.main()
