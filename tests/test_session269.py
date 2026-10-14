"""Session 269: the index of the review packs, and session 270's final pass (the chain of 14 October 2026).

Energy Research Warehouse (ERW). docs/reviews/packs/README.md lists the five packs in the owner's order (battery,
datacenter, generator, the Grid tool, Research), the screenshot to open beside each, the count of questions awaiting
the owner, and every Stata command in one block. docs/brand/review-final-2/ holds session 270's pictures and table.

What is held here: the order; that each screenshot named exists; that the count of questions is the sum of the packs'
part 9; that every do-file the block names exists; the final pass's folder and its table. No number of a page is held.
Nothing here sets the environment, reads a table or makes a request.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PACKS = os.path.join(ROOT, "docs", "reviews", "packs")
ORDER = ["battery", "datacenter", "generator", "grid", "research"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def owners_questions(tool):
    lines = src("docs", "reviews", "packs", tool + ".md").split("\n")
    start = lines.index("## 9. Questions only Samuel can answer")
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    return sum(1 for line in lines[start + 1:end] if re.match(r"^(?:### )?\d+\. ", line))


class TheIndex(unittest.TestCase):
    def setUp(self):
        self.index = src("docs", "reviews", "packs", "README.md")

    def test_the_five_packs_in_the_owners_order(self):
        rows = [line for line in self.index.split("\n") if re.match(r"^\| \d \| ", line)]
        self.assertEqual([re.search(r"\]\((\w+)\.md\)", r).group(1) for r in rows], ORDER)
        self.assertEqual([int(r.split("|")[1]) for r in rows], [1, 2, 3, 4, 5])

    def test_each_screenshot_named_exists(self):
        for target in re.findall(r"\]\(\.\./\.\./brand/([^)]+\.png)\)", self.index):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "brand", *target.split("/"))), target)

    def test_the_count_of_questions_is_the_packs_own(self):
        rows = [line for line in self.index.split("\n") if re.match(r"^\| \d \| ", line)]
        for tool, row in zip(ORDER, rows):
            self.assertEqual(int(row.rstrip(" |").rsplit("|", 1)[1]), owners_questions(tool), tool)
        total = sum(owners_questions(t) for t in ORDER)
        self.assertIn(f"**Questions awaiting Samuel: {total}**", self.index)

    def test_every_do_file_in_the_block_exists(self):
        block = self.index[self.index.index("```stata"):]
        block = block[:block.index("```", 3)]
        folder = None
        named = 0
        for line in block.split("\n"):
            m = re.match(r'^cd "<repository>/(.+)"$', line)
            if m:
                folder = m.group(1)
            m = re.match(r"^do (\S+\.do)$", line)
            if m:
                named += 1
                self.assertTrue(os.path.exists(os.path.join(ROOT, *folder.split("/"), m.group(1))), m.group(1))
        self.assertEqual(named, 10)

    def test_the_final_pass_folder(self):
        readme = src("docs", "brand", "review-final-2", "README.md")
        self.assertIn("session 270", readme)
        self.assertIn("## Fixed in this pass", readme)
        self.assertIn("| Page | On the brand | Sideways at 390 | Exceptions | What remains |", readme)
        for name in ("cost-of-power-battery_1280.png", "cost-of-power-battery_390.png"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "brand", "review-final-2", name)), name)

    def test_no_em_dash(self):
        for parts in (("docs", "reviews", "packs", "README.md"), ("docs", "brand", "review-final-2", "README.md"), ("tests", "test_session269.py")):
            self.assertEqual(src(*parts).count(chr(0x2014)), 0, parts)


if __name__ == "__main__":
    unittest.main()
