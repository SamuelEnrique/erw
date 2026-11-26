"""Session 10238, the small pages' audit, finding 8 (docs/reviews/small-pages-audit-2026-11-26.md): /about said "The digest
covers the 24 hours before it is written" and that the Roundup "opens with the weekend's top stories". Since session
2701 the Digest's window opens where the previous issue's ended, at most 96 hours back (the issue of 12 November 2026
covers 96 hours); the Roundup in the v2 form (session 2704) opens with its opening number and the week in five
numbers, its weekend's stories under More."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheIssues(unittest.TestCase):
    def test_the_window_opens_at_the_previous_issue_up_to_96_hours(self):
        b = src("warehouse", "news", "brief.py")
        self.assertIn("WINDOW_CAP_HOURS = 96", b)
        self.assertIn("return max(prev_end, now - pd.Timedelta(hours=cap))", b)
        self.assertIn("for the 96 hours to 2026-11-12 22:56 UTC", src("docs", "digest", "2026-11-12.md"))

    def test_the_v2_roundup_opens_with_its_numbers(self):
        heads = re.findall(r"^#{2,3} (.+)$", src("docs", "roundup", "2026-W45.md"), re.M)
        self.assertEqual(heads[:4], ["The opening number", "The week in five numbers", "What mattered", "More"])
        self.assertEqual(heads[4], "Weekend")


class ThePage(unittest.TestCase):
    def test_the_schedule_says_what_the_issues_cover(self):
        p = re.sub(r"\s+", " ", src("site", "app", "about", "page.tsx"))
        self.assertNotIn("The digest covers the 24 hours before it is written", p)
        self.assertNotIn("opens with the weekend&apos;s top stories", p)
        self.assertIn("The digest covers the news since the previous issue was written, at most 96 hours back", p)
        self.assertIn("opens with its opening number and the week in five numbers (the weekend&apos;s stories are under More)", p)


if __name__ == "__main__":
    unittest.main()
