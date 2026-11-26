"""Audit of the tour, finding 8 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the Digest's stop said
"Read \"Top of the industry\", then \"ERW's Numbers Today\"." /digest draws today's issue only (session 402), and none
has been written since 12 November 2026; the newest issue, of the new form, has no "Top of the industry" and carries
"ERW's Numbers Today" only as a sub-heading of "More". Session 9601 left the stop as it was for the owner's ruling.

1. The newest issue's headings, and the page's "Archive" drawn every day. Passes on main.
2. The fix on this branch, words only: the stop says to read today's issue or the newest the page names, its opening
   number and its numbers; the one heading it quotes, for check-tour, is "Archive". Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def digest_stop():
    t = src("site", "lib", "tour.ts")
    i = t.index('href: "/digest"')
    return t[i:t.index("},", i)]


class TheDigestStop(unittest.TestCase):
    def test_the_newest_issue_and_the_archive(self):
        latest = src("docs", "digest", "latest.md")
        h2 = re.findall(r"^## (.+)$", latest, re.M)
        if "Top of the industry" in h2:
            self.skipTest("the newest issue is of the old form")
        self.assertIn("The opening number", h2)
        self.assertIn("The numbers", h2)
        page = src("site", "app", "digest", "page.tsx")
        self.assertIn('<h2 className="mb-2 text-lg">Archive</h2>', page)
        self.assertIn("The newest is <Link href={`/digest/${newest}`}>", page)

    def test_the_stop_quotes_what_is_there(self):
        s = digest_stop()
        self.assertNotIn('"Top of the industry"', s)
        self.assertIn('headings: ["Archive"]', s)
        self.assertIn("Read today's issue; when there is none yet, open the newest the page names, or the newest under \\\"Archive\\\", and read its opening number, then its numbers.", s)


if __name__ == "__main__":
    unittest.main()
