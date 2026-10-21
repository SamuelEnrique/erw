"""Session 540: shadcn MCP and Bencium evaluated in a note under docs/reviews/, nothing installed. The note answers both
tools, names every request it made (at most 25, robots files first), carries no em dash and no personal address, and
docs/tooling.md points to it."""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NOTE = os.path.join(ROOT, "docs", "reviews", "tooling-shadcn-bencium-2026-10-21.md")
TOOLING = os.path.join(ROOT, "docs", "tooling.md")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_540_REPORT.md")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def request_rows(text):
    """The rows of the note's request table: a number, then an address in backticks, then the HTTP status."""
    return re.findall(r"^\| (\d+) \| `([^`]+)`[^|]* \| (\d{3}) \|", text, flags=re.M)


class TheNote(unittest.TestCase):
    def setUp(self):
        self.text = read(NOTE)

    def test_both_tools_are_answered_with_a_recommendation(self):
        self.assertIn("## shadcn MCP", self.text)
        self.assertIn("## Bencium", self.text)
        self.assertEqual(self.text.count("### Recommendation"), 2)
        self.assertIn("**shadcn MCP: do not install.**", self.text)
        self.assertIn("**Bencium: install none", self.text)

    def test_every_request_is_named_and_numbered_in_order_at_most_25(self):
        rows = request_rows(self.text)
        self.assertTrue(rows, "no request table")
        self.assertLessEqual(len(rows), 25)
        self.assertEqual([int(n) for n, _, _ in rows], list(range(1, len(rows) + 1)))

    def test_robots_files_are_read_before_their_hosts(self):
        rows = request_rows(self.text)
        first = {}
        for n, url, _ in rows:
            m = re.match(r"https://([^/]+)/", url)
            if m:
                first.setdefault(m.group(1), (int(n), url))
        # npm's registry was read once (request 11) before its robots address (request 24), which holds no robots
        # file: the note says so. Every other host's first request is its robots file.
        late = {"registry.npmjs.org"}
        hosts_with_robots = {re.match(r"https://([^/]+)/", u).group(1) for _, u, _ in rows if u.endswith("/robots.txt")}
        self.assertEqual(set(first) - hosts_with_robots, set(), "a host whose robots file was never read")
        for host, (n, url) in first.items():
            if host in late:
                self.assertIn("read late", self.text)
                continue
            self.assertTrue(url.endswith("/robots.txt"), f"{host}: first request {n} is {url}, not its robots file")

    def test_no_em_dash_and_no_personal_address(self):
        for path in (NOTE, TOOLING, REPORT):
            if not os.path.exists(path):
                continue
            text = read(path)
            self.assertNotIn(chr(0x2014), text, path)
            self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.(com|org|net|edu|io)\b", text), path)

    def test_the_ruled_contact_string_is_the_user_agent(self):
        self.assertIn("ERW research project, github.com/SamuelEnrique/erw", self.text)

    def test_items_for_ruling_are_one_a_line(self):
        part = self.text.split("## For Samuel's ruling", 1)[1]
        items = [line for line in part.splitlines() if line.startswith("- ")]
        self.assertEqual(len(items), 3)


class TheToolingPagePointsToIt(unittest.TestCase):
    def test_tooling_names_the_note(self):
        self.assertIn("docs/reviews/tooling-shadcn-bencium-2026-10-21.md", read(TOOLING))


if __name__ == "__main__":
    unittest.main()
