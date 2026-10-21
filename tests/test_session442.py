"""Session 442: the daily Digest audited (docs/reviews/digest-audit-2026-10-21.md).

The audit is a document; these tests hold it to the session's rules: no em or en dash, every Digest issue it names is a
file of docs/digest/, the issue table names every issue the repository holds, every fix of the ranked list names a file
that exists and a test, the trace's total is the one its table states, and the request count is within the ceiling.
"""

import glob
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOC = os.path.join(ROOT, "docs", "reviews", "digest-audit-2026-10-21.md")
CEILING = 250
AUDITED = "2026-10-21"   # the audit's own day (its first line)


def _doc():
    with open(DOC, encoding="utf-8") as f:
        return f.read()


def _section(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j]


class TestSession442(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        text = _doc()
        self.assertNotIn(chr(0x2014), text)
        self.assertNotIn(chr(0x2013), text)

    def test_every_issue_named_exists(self):
        named = set(re.findall(r"docs/digest/(2026-\d\d-\d\d)\.md", _doc()))
        self.assertTrue(named)
        for d in named:
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "digest", f"{d}.md")), d)

    def test_issue_table_names_every_issue_held(self):
        # the issues the repository held when the audit was read (21 October, 07:16 to 07:50 UTC, before that day's Digest
        # was written): an issue written after the audit is not one it could name
        held = {os.path.basename(p)[:10] for p in glob.glob(os.path.join(ROOT, "docs", "digest", "2026-*.md"))}
        held = {d for d in held if d < AUDITED}
        table = _section(_doc(), "## 1. What was read", "## 2.")
        rows = set(re.findall(r"\| `docs/digest/(2026-\d\d-\d\d)\.md` \|", table))
        self.assertEqual(rows, held)
        self.assertIn(f"**{len(held)} issues, not 14.**", table)

    def test_every_fix_names_a_file_and_a_test(self):
        fixes = _section(_doc(), "## 12. The fixes", "## 13.")
        rows = [r for r in fixes.splitlines() if re.match(r"\| \d+ \|", r)]
        self.assertGreaterEqual(len(rows), 10)
        for i, r in enumerate(rows, 1):
            cells = [c.strip() for c in r.strip("|").split("|")]
            self.assertEqual(cells[0], str(i), "ranks run 1, 2, 3 ...")
            paths = re.findall(r"`([^`]+)`", cells[2])
            self.assertEqual(len(paths), 1, r)
            self.assertTrue(os.path.exists(os.path.join(ROOT, paths[0])), paths[0])
            self.assertTrue(len(cells[3]) > 20, f"fix {i} names no test")

    def test_trace_total(self):
        text = _section(_doc(), "## 3. Every number, traced", "## 4.")
        self.assertIn("**118 of 118 equal**", text)
        # the parts the table's rows give add to the total
        table = "\n".join(line for line in text.splitlines() if line.startswith("| ") and "issues) |" in line)
        parts = [int(a) for a, b in re.findall(r"(\d+) of (\d+)", table) if a == b]
        self.assertEqual(sum(parts), 118, parts)

    def test_requests_within_ceiling(self):
        text = _section(_doc(), "## 14. Requests")
        n = int(re.search(r"(\d+) requests, all logged", text).group(1))
        self.assertLessEqual(n, CEILING)
        links = _section(_doc(), "## 4. Every link", "## 5.")
        self.assertIn(f"{n} of {CEILING}", links)


if __name__ == "__main__":
    unittest.main()
