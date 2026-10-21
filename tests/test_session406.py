"""Session 406: the newsletter's first issue, drafted, nothing sent (master plan tool 9).

docs/reviews/newsletter/issue-001.md (the draft), issue-001-notes.md (every claim, its source, the sceptic's reply) and
issue-001/ (the three charts and shots-406.mjs, which cuts them from a local build). These tests hold the draft to the
chain's rules: no em dash, about 1,200 words, every figure footnoted with its page address and its check-values key,
every key of a form check-values.mjs resolves, every page a route of the site, and the charts either made or said
to wait.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DIR = os.path.join(ROOT, "docs", "reviews", "newsletter")
DRAFT = os.path.join(DIR, "issue-001.md")
NOTES = os.path.join(DIR, "issue-001-notes.md")
CHARTS = os.path.join(DIR, "issue-001")
CHECK_VALUES = os.path.join(ROOT, "site", "scripts", "check-values.mjs")
APP = os.path.join(ROOT, "site", "app")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def footnotes(text):
    """The footnote definitions: {label: text}."""
    return {m.group(1): m.group(2) for m in re.finditer(r"^\[\^(\d+)\]:\s*(.+)$", text, re.M)}


class TheFiles(unittest.TestCase):
    def test_both_files_exist_and_hold_no_dash(self):
        for p in (DRAFT, NOTES):
            t = read(p)
            self.assertNotIn(chr(0x2014), t, p)
            self.assertNotIn(chr(0x2013), t, p)

    def test_the_draft_is_about_1200_words(self):
        t = read(DRAFT)
        parts = t.split("\n---\n")
        self.assertGreaterEqual(len(parts), 3, "the draft's body sits between two rules, the footnotes after the second")
        n = len(re.findall(r"\S+", parts[1]))
        self.assertGreaterEqual(n, 1000, n)
        self.assertLessEqual(n, 1500, n)

    def test_nothing_is_sent(self):
        t = read(DRAFT)
        self.assertIn("not sent", t.splitlines()[0])


class EveryFigureHasItsKey(unittest.TestCase):
    def setUp(self):
        self.t = read(DRAFT)
        self.notes = footnotes(self.t)

    def test_every_reference_has_a_footnote_and_back(self):
        body = re.sub(r"^\[\^\d+\]:.*$", "", self.t, flags=re.M)   # the definitions out, the references left
        refs = set(re.findall(r"\[\^(\d+)\]", body))
        self.assertTrue(refs)
        self.assertEqual(refs, set(self.notes))

    def test_every_footnote_names_a_page_and_a_key(self):
        for label, text in self.notes.items():
            pages = re.findall(r"`(/[^`\s]*)`", text)
            keys = [k for k in re.findall(r"`([^`]+)`", text) if "|" in k]
            self.assertTrue(pages, f"footnote {label} names no page address")
            self.assertTrue(keys, f"footnote {label} names no check-values key")

    def test_every_key_is_a_form_check_values_resolves(self):
        cv = read(CHECK_VALUES)
        for label, text in self.notes.items():
            for k in re.findall(r"`([^`]+)`", text):
                if "|" not in k:
                    continue
                head = k.split("|")[0]
                if head == "...":
                    continue
                if head == "series":
                    self.assertTrue(k.startswith("series|storage_buildout_monthly|"), k)
                else:
                    self.assertIn(f'p[0] === "{head}"', cv, f"footnote {label}: check-values.mjs reads no {head}| key")

    def test_the_battery_keys_carry_the_page_defaults(self):
        # the page's default inputs of a 100 MW, 4-hour battery: the key the page writes for its default view
        for k in re.findall(r"`(bs\|[^`]+)`", self.t):
            self.assertIn("&mw=100&fom=22&ds=2261119|", k, k)

    def test_every_page_is_a_route(self):
        for label, text in self.notes.items():
            for p in re.findall(r"`(/[^`\s]*)`", text):
                route = p.split("?")[0].strip("/")
                self.assertTrue(os.path.exists(os.path.join(APP, *route.split("/"), "page.tsx")), f"footnote {label}: {p}")


class TheNotes(unittest.TestCase):
    def test_claims_are_numbered_without_a_gap(self):
        nums = [int(n) for n in re.findall(r"^\| (\d+) \|", read(NOTES), re.M)]
        self.assertEqual(nums, list(range(1, len(nums) + 1)))
        self.assertGreaterEqual(len(nums), 20)

    def test_a_key_in_a_table_cell_escapes_its_bars(self):
        # an unescaped bar inside a cell would split the cell on GitHub
        for line in read(NOTES).splitlines():
            if not line.startswith("| "):
                continue
            for code in re.findall(r"`[^`]*`", line):
                self.assertNotRegex(code, r"(?<!\\)\|", line[:80])


class TheCharts(unittest.TestCase):
    def test_three_charts_made_or_said_to_wait(self):
        t = read(DRAFT)
        imgs = re.findall(r"!\[[^\]]*\]\((issue-001/[^)]+\.png)\)", t)
        self.assertEqual(len(imgs), 3)
        waiting = "The three charts are not made yet" in t
        for rel in imgs:
            p = os.path.join(DIR, *rel.split("/"))
            if waiting:
                continue
            self.assertTrue(os.path.exists(p), rel)
            with open(p, "rb") as f:
                self.assertEqual(f.read(8), b"\x89PNG\r\n\x1a\n", rel)

    def test_the_shot_script_names_the_drafts_charts(self):
        s = read(os.path.join(CHARTS, "shots-406.mjs"))
        t = read(DRAFT)
        for rel in re.findall(r"\((issue-001/[^)]+\.png)\)", t):
            self.assertIn(rel.split("/")[1], s)
        self.assertIn("unlock(base)", s)
        self.assertNotIn("INTERNAL_COSTS_TOKEN=", s)


if __name__ == "__main__":
    unittest.main()
