"""Session 10238, the small pages' audit, finding 2 (docs/reviews/small-pages-audit-2026-11-26.md): /subscribe described
the email of the issues before the v2 form ("the top 5 headlines", "yesterday's day-ahead average at each ISO's main
hub ... Henry Hub, WTI and Brent closes", "Every number comes from the warehouse and names its table"). The sender
(warehouse/news/email_digest.py, render) sends, for an issue in the v2 form, the opening number, the issue's own
numbers block, the first three stories, the chart and the fun fact; the numbers block of 12 November holds two figures
that are an outlet's, not a table's."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheSender(unittest.TestCase):
    def test_a_v2_issue_sends_three_stories_and_its_own_numbers_block(self):
        e = src("warehouse", "news", "email_digest.py")
        self.assertIn("numbered(lines, (V2_MOVED,), 3) if v2 else (numbered(lines, (\"## What mattered\",), 3) if v2r else top_stories(lines))", e)
        self.assertIn('section(lines, ("## The numbers",))]) if v2 else', e)
        self.assertIn("keep = [x for x in items(lines, kind) if tp.topic_of(x[\"sector\"]) in chosen][:5]", e)

    def test_the_newest_issue_is_in_the_v2_form_with_an_outlets_figure(self):
        latest = src("docs", "digest", "latest.md")
        self.assertIn("\n## What moved\n", latest)
        self.assertIn("\n## The numbers\n", latest)
        self.assertIn("the outlet's figure, not a table's", latest)
        self.assertGreaterEqual(len(re.findall(r"^\d+\. \*\*", latest.split("## What moved", 1)[1].split("\n## ", 1)[0], re.M)), 4)


class ThePage(unittest.TestCase):
    def page(self):
        return re.sub(r"\s+", " ", src("site", "app", "subscribe", "page.tsx"))

    def test_the_old_email_is_not_described(self):
        p = self.page()
        self.assertNotIn("the top 5 headlines", p)
        self.assertNotIn("Every number comes from the warehouse and names its table", p)
        self.assertNotIn("the weekend&apos;s stories, the five stories of the week", p)

    def test_the_v2_email_is_described(self):
        p = self.page()
        self.assertIn("the first three stories of what moved", p)
        self.assertIn("or, for a figure a news story reported, its outlet", p)
        self.assertIn("with every topic chosen, the email&apos;s stories are the first three of the issue&apos;s own", p)


if __name__ == "__main__":
    unittest.main()
