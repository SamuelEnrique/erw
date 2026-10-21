"""Session 449: the reports of sessions 365 to 440 read as a reviewer (docs/reviews/review-of-20-21-october.md). The
review gives one line a session found with a report, each with a verdict word, the numbers with none, and exactly five
items for Samuel's eyes; every commit it cites must exist."""

import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REVIEW = os.path.join(ROOT, "docs", "reviews", "review-of-20-21-october.md")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_449_REPORT.md")

# the 36 numbers with a report on a remote branch at 07:30 UTC on 21 October (runs/chain_oct21_third/s449/reports_latest.txt)
FOUND = list(range(365, 390)) + [402, 403, 404, 405, 406, 407, 409, 410, 413, 414, 420]
VERDICTS = ("met", "partly", "not met")


def text():
    with open(REVIEW, encoding="utf-8") as f:
        return f.read()


def section(s, heading):
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", s, re.M | re.S)
    return m.group(1) if m else ""


class TheReview(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for p in (REVIEW, REPORT, __file__):
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as f:
                body = f.read()
            self.assertNotIn(chr(0x2014), body, p)
            self.assertNotIn(chr(0x2013), body, p)

    def test_one_line_a_session_found_each_with_a_verdict(self):
        lines = section(text(), "One line a session")
        got = {}
        for m in re.finditer(r"^- \*\*(\d{3})\*\* (not met|partly|met)[:,]", lines, re.M):
            n = int(m.group(1))
            self.assertNotIn(n, got, f"session {n} listed twice")
            got[n] = m.group(2)
        self.assertEqual(sorted(got), sorted(FOUND))
        for v in got.values():
            self.assertIn(v, VERDICTS)

    def test_every_number_365_to_440_is_a_line_or_in_the_missing_table(self):
        s = text()
        missing = section(s, "Session numbers with no report found anywhere")
        named = set()
        for a, b in re.findall(r"(\d{3}) to (\d{3})", missing):
            named.update(range(int(a), int(b) + 1))
        named.update(int(n) for n in re.findall(r"\b(3[6-9]\d|4[0-4]\d)\b", missing))
        for n in range(365, 441):
            if n in FOUND:
                continue
            self.assertIn(n, named, f"session {n} neither reviewed nor listed as missing")
        self.assertIn("40 of the 76", missing)

    def test_exactly_five_items_for_samuel(self):
        five = section(text(), "The five items that most need Samuel's eyes before the landings pile up")
        items = re.findall(r"^(\d+)\. \*\*", five, re.M)
        self.assertEqual(items, ["1", "2", "3", "4", "5"])

    def test_every_cited_commit_exists(self):
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("git is not available")
        hashes = set(re.findall(r"`([0-9a-f]{8})`", text()))
        self.assertGreater(len(hashes), 20)
        for h in sorted(hashes):
            r = subprocess.run(["git", "cat-file", "-e", h + "^{commit}"], cwd=ROOT, capture_output=True)
            self.assertEqual(r.returncode, 0, f"commit {h} not found")


if __name__ == "__main__":
    unittest.main()
