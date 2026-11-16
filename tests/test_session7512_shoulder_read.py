"""Session 7512 (chain 304, part B): "The shoulder hours" (/shoulder) read as the reader it is for.

The read is docs/reviews/shoulder-read-2026-11-16.md. Its site faults are held fixed by a Node check that draws the page
with the site's own code on real rows of the table (tests/fixtures/session7512: the five cases' months, copied as the
table holds them): site/scripts/test-shoulder-read.mjs. This file runs it, and holds what the read wrote: the review's
form (the reader and the cases first, numbered rows with a kind and a state, five closing bullets), the fixture's rows
against what the review quotes, and no em or en dash in the session's files.
"""
import csv
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session7512", "shoulder_hours_monthly.csv")
REVIEW = os.path.join(ROOT, "docs", "reviews", "shoulder-read-2026-11-16.md")
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
MINE = (
    ("docs", "reviews", "shoulder-read-2026-11-16.md"), ("site", "scripts", "test-shoulder-read.mjs"), ("site", "app", "shoulder", "page.tsx"), ("site", "lib", "shoulder.ts"),
    ("tests", "test_session7512_shoulder_read.py"), ("tests", "fixtures", "session7512", "shoulder_hours_monthly.csv"), ("archive", "sessions", "SESSION_7512_REPORT.md"),
)
KINDS = ("site", "data machine", "browser", "license", "key", "ruling")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def fixture():
    with open(FIXTURE, encoding="utf-8") as f:
        return {(r["entity"], r["variable"], r["ts_utc"][:10]): float(r["value"]) for r in csv.DictReader(line for line in f if not line.startswith("#"))}


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageAsItsReaderMeetsIt(unittest.TestCase):
    def test_the_reads_faults_stay_fixed(self):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-shoulder-read.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900)
        failed = [line for line in r.stdout.splitlines() if line.startswith("FAIL")]
        self.assertEqual((r.returncode, failed), (0, []), r.stdout[-3000:] + r.stderr[-1500:])
        m = re.search(r"(\d+) of (\d+) passed", r.stdout)
        self.assertTrue(m, r.stdout[-400:])
        self.assertEqual(m.group(1), m.group(2))
        self.assertGreaterEqual(int(m.group(2)), 37)


class TheReview(unittest.TestCase):
    def test_its_form(self):
        t = src("docs", "reviews", "shoulder-read-2026-11-16.md")
        head = t.split("\n## ")[0]
        self.assertIn("**The reader:**", head)
        self.assertIn("**The five cases:**", head)
        self.assertIn("**How it was read.**", head)
        self.assertIn("No click was made, no chart was seen", head)
        rows = re.findall(r"(?m)^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", t)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, len(rows) + 1)))
        self.assertGreaterEqual(len(rows), 12)
        for r in rows:
            self.assertIn(r[4].strip(), KINDS, r[0])
            self.assertTrue(r[5].strip(), r[0])
        closing = t.split("## What this reader still cannot get from the tool, and why")[1]
        self.assertEqual(len(re.findall(r"(?m)^- \*\*", closing)), 5)
        # a gap part A wrote down is cited by its row, not written again
        self.assertIn("shoulder-faults-2026-11-16.md", t)
        self.assertNotIn("Work in progress", t)

    def test_the_figures_it_quotes_are_the_tables(self):
        t, T = src("docs", "reviews", "shoulder-read-2026-11-16.md"), fixture()
        two = lambda v: f"{v:,.2f}"   # noqa: E731
        for entity, variable, date in (("iso:ercot", "shoulder_hours_needed", "2025-08-01"), ("iso:ercot", "shoulder_hours_needed", "2023-08-01"),
                                       ("iso:caiso", "shoulder_hours_needed", "2024-04-01"), ("iso:caiso_own", "shoulder_hours_needed", "2026-04-01"),
                                       ("iso:caiso", "shoulder_hours_needed", "2025-08-01"), ("iso:caiso_own", "shoulder_hours_needed", "2025-08-01"),
                                       ("iso:ercot", "day_shoulder_hours_needed", "2025-01-31"), ("iso:ercot", "day_shoulder_mwh_above_mean", "2025-01-31")):
            self.assertIn(two(T[(entity, variable, date)]), t, f"{entity} {variable} {date}")
        self.assertEqual(T[("iso:ercot", "worst_rank", "2025-01-31")], 1)
        self.assertEqual((T[("iso:ercot", "shoulder_hours", "2025-08-01")], T[("iso:ercot", "shoulder_hours", "2023-08-01")]), (5, 4))
        self.assertLess(T[("iso:ercot", "midday_low_hour", "2023-08-01")], 8)

    def test_no_dash_in_the_sessions_files(self):
        for parts in MINE:
            if not os.path.exists(os.path.join(ROOT, *parts)):
                continue
            t = src(*parts)
            self.assertNotIn(EM_DASH, t, "/".join(parts))
            self.assertNotIn(EN_DASH, t, "/".join(parts))


if __name__ == "__main__":
    unittest.main()
