"""Audit of the tour, finding 10 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the tour's first page and
its last stop said "After the tour: the home page lists every tool by who it is for". Since session 300 (the owner's
ruling of 18 October 2026) the home page shows the five groups of the menu by subject; the list by audience is the draft
at /home/v2.

1. The home page draws the five groups and reads no audience. Passes on main.
2. The fix on this branch, words only: both say the home page shows the five groups of tools. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AfterTheTour(unittest.TestCase):
    def test_the_home_page_shows_five_groups(self):
        home = src("site", "app", "page.tsx")
        self.assertIn('const HOME_GROUPS = ["Economics", "Grid", "Infrastructure", "Analysis", "Games"];', home)
        self.assertNotIn("lib/audience", home)
        self.assertIn("lib/audience", src("site", "app", "home", "v2", "page.tsx"))

    def test_the_words_say_so(self):
        for parts in (("site", "app", "tour", "page.tsx"), ("site", "app", "tour", "[stop]", "page.tsx")):
            t = src(*parts)
            self.assertNotIn("lists every tool by who it is for", t)
            self.assertIn('the <Link href="/">home page</Link> shows the five groups of tools, and', t)


if __name__ == "__main__":
    unittest.main()
