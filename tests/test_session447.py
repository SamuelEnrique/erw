"""Session 447: every open ruling of sessions 351 to 440, with a recommended answer (docs/reviews/rulings-2026-10-21-draft.md).

The agenda is a document; these tests hold it to the session's rules: no em or en dash, the ledger's groups present in
order, every item citing at least one session of the run, every item with its evidence, its meanwhile, what each
answer changes and one recommended ruling, the items numbered 1 to N with N the count the document states, and the
three highest-value items first.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOC = os.path.join(ROOT, "docs", "reviews", "rulings-2026-10-21-draft.md")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_447_REPORT.md")
GROUPS = ["## The three highest value first", "## Money", "## A data pull", "## A ruling on a figure",
          "## A public page", "## None of the four"]
FIELDS = ["**Raised by:**", "**Evidence:**", "**Meanwhile:**", "**What each answer changes:**", "**Recommended ruling:**"]


def _doc():
    with open(DOC, encoding="utf-8") as f:
        return f.read()


def _items(text):
    """[(number, title, body)] for every "### N. title" heading, the body running to the next heading."""
    parts = re.split(r"^(### \d+\. .*)$", text, flags=re.M)
    out = []
    for i in range(1, len(parts), 2):
        m = re.match(r"### (\d+)\. (.*)", parts[i])
        body = re.split(r"^## ", parts[i + 1], flags=re.M)[0]
        out.append((int(m.group(1)), m.group(2), body))
    return out


class TestSession447(unittest.TestCase):
    def test_no_dashes(self):
        for path in (DOC, REPORT, __file__):
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn(chr(0x2014), text, path)
            self.assertNotIn(chr(0x2013), text, path)

    def test_groups_in_order(self):
        text = _doc()
        at = [text.find(g + "\n") for g in GROUPS]
        self.assertTrue(all(a >= 0 for a in at), dict(zip(GROUPS, at)))
        self.assertEqual(at, sorted(at))

    def test_items_numbered_and_counted(self):
        text = _doc()
        nums = [n for n, _, _ in _items(text)]
        self.assertEqual(nums, list(range(1, len(nums) + 1)))
        m = re.search(r"make \*\*(\d+) items\*\* below", text)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)), len(nums))

    def test_every_item_has_its_fields(self):
        for n, title, body in _items(_doc()):
            for field in FIELDS:
                self.assertEqual(body.count(field), 1, f"item {n} ({title}): {field}")
            rec = body.split("**Recommended ruling:**", 1)[1].strip().splitlines()[0]
            self.assertIn("Reason:", rec, f"item {n}: the ruling line gives its reason")

    def test_every_item_cites_a_session_of_the_run(self):
        for n, title, body in _items(_doc()):
            raised = body.split("**Raised by:**", 1)[1].splitlines()[0]
            sessions = [int(x) for x in re.findall(r"\b(3[5-9]\d|4[0-4]\d)\b", raised)]
            self.assertTrue(any(351 <= s <= 440 for s in sessions), f"item {n} ({title}): {raised}")

    def test_first_three_follow_the_ranked_note(self):
        text = _doc()
        top = text.split("## The three highest value first", 1)[1].split("## Money", 1)[0]
        self.assertEqual([n for n, _, _ in _items(top)], [1, 2, 3])
        self.assertIn("note_2026-10-21_day_data.md", text)

    def test_nothing_decided(self):
        text = _doc()
        self.assertIn("Nothing is decided here", text)
        self.assertNotRegex(text, r"(?i)\bSamuel (?:ruled|decided) (?!.*21 October)")


if __name__ == "__main__":
    unittest.main()
