"""Session 249: how it works, five tools.

Energy Research Warehouse (ERW). docs/howitworks/ holds one document a tool: What a battery earns, What a generator
earns, What a datacenter pays, the Grid tool and Research. Each has the same seven parts, in the same order: what it is
for and for whom; the model in numbered steps; every assumption with its default and its source; the cross-checks; what
it cannot see, ranked; the ten hardest questions; a five-minute demo, click by click. A last part says where each number
was read.

What is held here: the five files, their parts and the order of the parts, the ten questions, that each says what it
was written from, and the repository's rule on dashes. No number is held here: the documents' numbers are the methods'
and the pages', which move, and a pin here would fail the next session that moves one.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "docs", "howitworks")

ALL_TOOLS = {
    "battery": ("What a battery earns", "/cost-of-power/battery"),
    "generator": ("What a generator earns", "/cost-of-power/seller"),
    "datacenter": ("What a datacenter pays", "/cost-of-power"),
    "grid": ("the Grid tool", "/grid"),
    "research": ("Research", "/research"),
}
# session 262: a tool whose review pack is written (docs/reviews/packs/<tool>.md, tests/test_session262.py) no longer
# has its note here; the parts below are held for the notes that remain
PACKS = os.path.join(ROOT, "docs", "reviews", "packs")
TOOLS = {k: v for k, v in ALL_TOOLS.items() if not os.path.exists(os.path.join(PACKS, k + ".md"))}

PARTS = [
    "## 1. What it is for, and for whom",
    "## 2. The model, in numbered steps",
    "## 3. Every assumption, its default and its source",
    "## 4. The cross-checks",
    "## 5. What it cannot see, ranked by how much it moves the answer",
    "## 6. The ten hardest questions",
    "## 7. A five-minute demo, click by click",
    "## Where the numbers in this document come from",
]


def doc(tool):
    with open(os.path.join(DIR, tool + ".md"), encoding="utf-8") as f:
        return f.read()


def part(text, heading):
    """The lines under one heading, to the next heading of the same level."""
    lines = text.split("\n")
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1:end]


class TheFiveDocuments(unittest.TestCase):
    def test_each_tool_has_its_note_or_its_review_pack(self):
        for tool in ALL_TOOLS:
            note, pack = os.path.join(DIR, tool + ".md"), os.path.join(PACKS, tool + ".md")
            self.assertTrue(os.path.exists(note) != os.path.exists(pack), f"{tool}: the note or the pack, one of them")

    def test_each_tool_has_its_document_and_the_index_lists_them(self):
        index = doc("README")
        for tool, (name, address) in TOOLS.items():
            self.assertTrue(os.path.exists(os.path.join(DIR, tool + ".md")), tool)
            self.assertIn(f"({tool}.md)", index)
            self.assertIn(f"`{address}`", index)

    def test_the_title_names_the_tool_and_the_opening_names_its_address(self):
        for tool, (name, address) in TOOLS.items():
            lines = doc(tool).split("\n")
            self.assertEqual(lines[0], f"# How it works: {name}", tool)
            opening = "\n".join(lines[1:lines.index(PARTS[0])])
            self.assertIn(f"`{address}`", opening, tool)
            self.assertIn("in review", opening, tool)
            self.assertIn("2026-10-13", opening, tool)

    def test_the_parts_are_the_same_seven_and_the_sources_in_order(self):
        for tool in TOOLS:
            headings = [line for line in doc(tool).split("\n") if line.startswith("## ")]
            self.assertEqual(headings, PARTS, tool)

    def test_no_part_is_empty(self):
        for tool in TOOLS:
            text = doc(tool)
            for heading in PARTS:
                body = [line for line in part(text, heading) if line.strip()]
                self.assertGreaterEqual(len(body), 3, f"{tool}: {heading}")

    def test_the_model_is_numbered_from_one(self):
        for tool in TOOLS:
            steps = [int(m.group(1)) for line in part(doc(tool), PARTS[1]) if (m := re.match(r"^(\d+)\. ", line))]
            self.assertGreaterEqual(len(steps), 5, tool)
            self.assertEqual(steps, list(range(1, len(steps) + 1)), tool)

    def test_the_assumptions_and_the_cross_checks_are_tables(self):
        for tool in TOOLS:
            text = doc(tool)
            for heading in (PARTS[2], PARTS[3], PARTS[7]):
                rows = [line for line in part(text, heading) if line.startswith("|")]
                self.assertGreaterEqual(len(rows), 4, f"{tool}: {heading}")

    def test_there_are_ten_questions_numbered_one_to_ten(self):
        for tool in TOOLS:
            # a question is a numbered line at the margin; its answer is indented under it
            asked = [int(m.group(1)) for line in part(doc(tool), PARTS[5]) if (m := re.match(r"^(?:### )?(\d+)\. ", line))]
            self.assertEqual(asked, list(range(1, 11)), tool)

    def test_the_demo_says_it_needs_the_internal_view_and_was_not_clicked_through(self):
        for tool in TOOLS:
            demo = "\n".join(part(doc(tool), PARTS[6]))
            self.assertIn("/internal/", demo, tool)
            self.assertIn("internal view", demo, tool)
            self.assertIn("not clicked through", demo, tool)
            self.assertRegex(demo, r"Minute \d", tool)

    def test_no_em_dash_in_any_of_them(self):
        for name in sorted(os.listdir(DIR)):
            if name.endswith(".md"):
                with open(os.path.join(DIR, name), encoding="utf-8") as f:
                    self.assertEqual(f.read().count(chr(0x2014)), 0, name)


if __name__ == "__main__":
    unittest.main()
