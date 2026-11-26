"""Audit of the home page, finding 1's ruling (session 10236, docs/reviews/home-model-audit-2026-11-26.md), a test only:
the home page's Digest block reads the first five items under "## Top of the industry" (site/lib/markdown.ts, topItems),
and the newest issue (12 November 2026, "ERW Daily Digest") has no such section, so the block draws "no data". The new
form's day's stories are under "## What moved".

This test shows it and passes on main. The choice, default "left as it is": the block reads the new form's "What moved"
when "Top of the industry" is not there. The effect: 5 stories drawn instead of "no data". No fix is made.
Nothing here sets the environment, reads a table or makes a request."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheDigestStories(unittest.TestCase):
    def test_the_block_reads_one_section_only(self):
        md = src("site", "lib", "markdown.ts")
        self.assertIn('const start = md.indexOf("\\n## Top of the industry");', md)
        self.assertIn("const items = topItems(DOCS.latest, 5);", src("site", "app", "page.tsx"))

    def test_the_newest_issue_holds_its_stories_under_what_moved(self):
        latest = src("docs", "digest", "latest.md")
        if "\n## Top of the industry" in latest:
            self.skipTest("the newest issue is of the old form")
        sect = latest[latest.index("\n## What moved"):]
        sect = sect[:sect.index("\n## ", 3)]
        self.assertEqual(len(re.findall(r"^\d+\.\s", sect, re.M)), 5)


if __name__ == "__main__":
    unittest.main()
