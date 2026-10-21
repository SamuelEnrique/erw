"""Session 450: the two research reports of 21 October read into a roadmap v4 draft (docs/reviews/roadmap-v4-draft.md).

The draft is a document; these tests hold it to the session's rules: no em or en dash; twenty tool entries (the master
plan's tools 1 to 20), each with a recommendation line whose place agrees with the order table and at least one link;
the sections on where the reports disagree and what neither checked; every repository path linked exists on this
branch (or, for a github.com link, on the branch it names), and every heading anchor into a report exists; and
docs/roadmap.md unchanged against the commit this branch stands on.
"""

import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOC = os.path.join(ROOT, "docs", "reviews", "roadmap-v4-draft.md")
DOC_DIR = os.path.dirname(DOC)
ROADMAP = os.path.join(ROOT, "docs", "roadmap.md")
GITHUB = "https://github.com/SamuelEnrique/erw/blob/"
PLACES = ("first", "second", "third", "later")


def _doc():
    with open(DOC, encoding="utf-8") as f:
        return f.read()


def _section(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j]


def _links(text):
    return re.findall(r"\]\(([^)\s]+)\)", text)


def _slug(heading):
    """GitHub's anchor for a heading: lower case, punctuation but hyphens dropped, spaces to hyphens."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def _anchors(path):
    with open(path, encoding="utf-8") as f:
        return {_slug(m.group(1)) for m in re.finditer(r"^#+\s+(.*)$", f.read(), re.M)}


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def _tools(text):
    """{number: the entry's text} for every '### Tool N:' heading."""
    body = _section(text, "## 2. The twenty tools", "## 3. ")
    parts = re.split(r"^### Tool (\d+):", body, flags=re.M)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}


class TheDraft(unittest.TestCase):
    def test_no_dashes(self):
        text = _doc()
        self.assertNotIn(chr(0x2014), text)
        self.assertNotIn(chr(0x2013), text)

    def test_twenty_tools_each_with_a_recommendation_and_a_link(self):
        tools = _tools(_doc())
        self.assertEqual(sorted(tools), list(range(1, 21)))
        for n, entry in tools.items():
            self.assertRegex(entry, r"\*\*Recommendation: (%s)\b" % "|".join(PLACES), f"tool {n}")
            self.assertTrue(_links(entry), f"tool {n} has no link")
            self.assertIn("**The reports.**", entry, f"tool {n}")
            self.assertIn("**The ERW today.**", entry, f"tool {n}")

    def test_the_order_table_agrees_with_each_recommendation(self):
        text = _doc()
        table = _section(text, "## 1. The order in one table", "## 2. ")
        placed = {}
        for place, tools in re.findall(r"^\| (first|second|third|later) \| ([^|]+) \|", table, re.M):
            for n in re.findall(r"\b(\d+) [A-Za-z]", tools):
                placed[int(n)] = place
        self.assertEqual(sorted(placed), list(range(1, 21)), "every tool placed once in the table")
        for n, entry in _tools(text).items():
            got = re.search(r"\*\*Recommendation: (%s)\b" % "|".join(PLACES), entry).group(1)
            self.assertEqual(got, placed[n], f"tool {n}")

    def test_no_tool_is_cut(self):
        self.assertNotRegex(_doc().lower(), r"recommendation: cut|\bdrop tool")

    def test_the_two_closing_sections(self):
        text = _doc()
        self.assertIn("## 4. Where the two reports disagree", text)
        self.assertIn("## 5. What neither report checked", text)
        for name in ("## 4. Where the two reports disagree", "## 5. What neither report checked"):
            items = re.findall(r"^\d+\. ", _section(text, name, "\n## "), re.M)
            self.assertGreaterEqual(len(items), 3, name)

    def test_this_week_in_the_roadmaps_format(self):
        week = _section(_doc(), "## 3. This week", "### From v2")
        items = re.findall(r"^(\d+)\. \[ \] ", week, re.M)
        self.assertGreaterEqual(len(items), 3)
        for block in re.split(r"^\d+\. \[ \] ", week, flags=re.M)[1:]:
            for field in ("   - machine: ", "   - where: ", "   - done: "):
                self.assertIn(field, block)
            self.assertRegex(block, r"machine: (code|data)\n")

    def test_every_local_link_exists_and_every_anchor_too(self):
        for link in _links(_doc()):
            if link.startswith("http"):
                continue
            path, _, anchor = link.partition("#")
            full = os.path.normpath(os.path.join(DOC_DIR, path))
            self.assertTrue(os.path.exists(full), link)
            if anchor:
                self.assertIn(anchor, _anchors(full), link)

    def test_every_branch_link_exists_on_its_branch(self):
        links = [l for l in _links(_doc()) if l.startswith("http")]
        self.assertTrue(all(l.startswith(GITHUB) for l in links), "only the ERW's own repository is linked")
        for link in links:
            branch_path = link[len(GITHUB):].split("#")[0]
            # a branch named wip/<x> or task/<x>: two parts, then the path
            parts = branch_path.split("/")
            branch, path = "/".join(parts[:2]), "/".join(parts[2:])
            if _git("rev-parse", "--verify", "--quiet", f"origin/{branch}").returncode != 0:
                self.skipTest(f"origin/{branch} is not fetched here")
            self.assertEqual(_git("cat-file", "-e", f"origin/{branch}:{path}").returncode, 0, link)

    def test_the_roadmap_is_unchanged(self):
        shown = _git("show", "HEAD:docs/roadmap.md")
        if shown.returncode != 0:
            self.skipTest("git cannot show HEAD:docs/roadmap.md here")
        with open(ROADMAP, encoding="utf-8", newline="") as f:
            here = f.read()
        self.assertEqual(here.replace("\r\n", "\n"), shown.stdout.replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
