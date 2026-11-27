"""Audit of the home page, finding 1 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the home page's
Digest block reads the first five stories under "## Top of the industry" of docs/digest/latest.md. The newest issue
(12 November 2026) is in the new form, "ERW Daily Digest, <date>", with no such section, so the block prints "no data",
and its link, written for "ERW's Energy Digest, <date>", read "The full Digest of ERW Daily Digest, 2026-11-12".

1. The newest issue is of the new form and has no "Top of the industry". Passes on main.
2. The fix on this branch, words only: the title cleaner also takes "ERW Daily Digest, ", so the link names the date
   alone. No figure moves; which stories the block draws is for Samuel's ruling (wip/audit-home-15). Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def cleaner():
    """The home page's title cleaner, as a Python pattern (the two regular expressions are written alike)."""
    m = re.search(r"digestTitle\(DOCS\.latest\)\.replace\(/(.+?)/, \"\"\)", src("site", "app", "page.tsx"))
    return re.compile(m.group(1).replace("\\s", r"\s"))


class TheDigestBlock(unittest.TestCase):
    def test_the_newest_issue_is_of_the_new_form(self):
        latest = src("docs", "digest", "latest.md")
        title = re.search(r"^# (.+)$", latest, re.M).group(1)
        if not title.startswith("ERW Daily Digest, "):
            self.skipTest(f"the newest issue is titled {title!r}")
        self.assertNotIn("\n## Top of the industry", latest)

    def test_the_link_names_the_date_alone(self):
        rx = cleaner()
        for title, date in (("ERW Daily Digest, 2026-11-12", "2026-11-12"), ("ERW's Energy Digest, 2026-11-06", "2026-11-06"), ("Energy Digest, 2026-10-01", "2026-10-01")):
            self.assertEqual(rx.sub("", title, count=1), date)


if __name__ == "__main__":
    unittest.main()
