"""Session 262: the review packs, one a tool, for the owner's technical review (the chain of 14 October 2026).

Energy Research Warehouse (ERW). Each deep session of the chain (263 to 267) writes docs/reviews/packs/<tool>.md for
its tool and deletes docs/howitworks/<tool>.md, whose content it folds in. A pack has nine numbered parts, in this
order: what the tool is for and for whom; the model step by step, each step naming its function and file; every
assumption with its default, its source and the ruling of 12 October where one applies; the cross-check table, at
least ten rows; the edge cases tested and what the page does in each; what the model cannot see, ranked; the ten
hardest questions; what the owner's Stata run must reproduce, with the command; the questions only the owner can
answer. A last part names where every number was read; an appendix may keep the old note's demo.

What is held here, for every pack that exists: the title, the opening's address and status, the parts and their order,
the numbered steps each citing code, the ten rows of cross-checks, the ten questions, a command block for Stata, at
least one numbered question for the owner, no em dash; and that the old note is gone and no live document still links
it. No number is held: a pack's numbers are the methods' and the pages', which move.
Nothing here sets the environment, reads a table or makes a request.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PACKS = os.path.join(ROOT, "docs", "reviews", "packs")
OLD = os.path.join(ROOT, "docs", "howitworks")

TOOLS = {
    "battery": ("What a battery earns", "/cost-of-power/battery"),
    "generator": ("What a generator earns", "/cost-of-power/seller"),
    "datacenter": ("What a datacenter pays", "/cost-of-power"),
    "grid": ("the Grid tool", "/grid"),
    "research": ("Research", "/research"),
    "impact": ("What a project does for a state", "/impact"),  # session 347, the economic impact tool
}

PARTS = [
    "## 1. What it is for, and for whom",
    "## 2. The model, step by step",
    "## 3. Every assumption",
    "## 4. The cross-checks",
    "## 5. The edge cases tested",
    "## 6. What the model cannot see, ranked",
    "## 7. The ten hardest questions",
    "## 8. What Samuel's Stata run must reproduce",
    "## 9. Questions only Samuel can answer",
]
APPENDIX = "## Appendix: the five-minute demo"
SOURCES = "## Where every number comes from"
# session 381: a pack of the five sellable tools may open with its table against roadmap item 2, before part 1
ROADMAP = "## Against roadmap item 2 (session 381)"

# the documents a reader follows today: a link to an old note here would lead nowhere
LIVE_DOCS = [os.path.join(ROOT, "docs", "methods"), os.path.join(ROOT, "docs", "howitworks"), PACKS,
             os.path.join(ROOT, "site", "app"), os.path.join(ROOT, "site", "lib"), os.path.join(ROOT, "site", "content"),
             os.path.join(ROOT, "package")]


def written():
    return [t for t in TOOLS if os.path.exists(os.path.join(PACKS, t + ".md"))]


def pack(tool):
    with open(os.path.join(PACKS, tool + ".md"), encoding="utf-8") as f:
        return f.read()


def part(text, heading):
    """The lines under one heading, to the next heading of the same level."""
    lines = text.split("\n")
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1:end]


def table_rows(lines):
    """The data rows of the markdown tables in a stretch: not the header, not the rule under it."""
    rows = [line for line in lines if line.startswith("|")]
    out, after_rule = [], set()
    for i, r in enumerate(rows):
        if set(r.replace(" ", "")) <= set("|-:"):
            after_rule.add(i)
    for i, r in enumerate(rows):
        if i in after_rule or (i + 1) in after_rule:
            continue
        out.append(r)
    return out


class ThePacks(unittest.TestCase):
    def test_the_title_and_the_opening(self):
        for tool in written():
            name, address = TOOLS[tool]
            lines = pack(tool).split("\n")
            self.assertEqual(lines[0], f"# Review pack: {name}", tool)
            opening = "\n".join(lines[1:lines.index(PARTS[0])])
            self.assertIn(f"`{address}`", opening, tool)
            self.assertIn("in review", opening, tool)

    def test_the_nine_parts_in_order_then_the_sources(self):
        for tool in written():
            headings = [line for line in pack(tool).split("\n") if line.startswith("## ")]
            want = ([ROADMAP] if ROADMAP in headings else []) + PARTS + ([APPENDIX] if APPENDIX in headings else []) + [SOURCES]
            self.assertEqual(headings, want, tool)

    def test_no_part_is_thin(self):
        for tool in written():
            text = pack(tool)
            for heading in PARTS + [SOURCES]:
                body = [line for line in part(text, heading) if line.strip()]
                self.assertGreaterEqual(len(body), 3, f"{tool}: {heading}")

    def test_each_step_names_its_code(self):
        for tool in written():
            steps = [(int(m.group(1)), line) for line in part(pack(tool), PARTS[1]) if (m := re.match(r"^(\d+)\. ", line))]
            self.assertGreaterEqual(len(steps), 5, tool)
            self.assertEqual([n for n, _ in steps], list(range(1, len(steps) + 1)), tool)
            for n, line in steps:
                self.assertIn("`", line, f"{tool}: step {n} names no function or file")

    def test_every_assumption_has_a_source(self):
        for tool in written():
            rows = table_rows(part(pack(tool), PARTS[2]))
            self.assertGreaterEqual(len(rows), 10, tool)
            for r in rows:
                cells = [c.strip() for c in r.strip().strip("|").split(" | ")]
                self.assertGreaterEqual(len(cells), 3, f"{tool}: {r[:60]}")
                self.assertTrue(cells[-1], f"{tool}: no source: {r[:60]}")

    def test_at_least_ten_cross_checks(self):
        for tool in written():
            rows = table_rows(part(pack(tool), PARTS[3]))
            self.assertGreaterEqual(len(rows), 10, tool)

    def test_edge_cases_are_listed(self):
        for tool in written():
            lines = part(pack(tool), PARTS[4])
            cases = table_rows(lines) or [line for line in lines if re.match(r"^(\d+\.|-) ", line)]
            self.assertGreaterEqual(len(cases), 3, tool)

    def test_ten_hardest_questions(self):
        for tool in written():
            asked = [int(m.group(1)) for line in part(pack(tool), PARTS[6]) if (m := re.match(r"^(?:### )?(\d+)\. ", line))]
            self.assertEqual(asked, list(range(1, 11)), tool)

    def test_the_stata_run_has_its_command(self):
        for tool in written():
            body = "\n".join(part(pack(tool), PARTS[7]))
            self.assertIn("```", body, tool)

    def test_the_owners_questions_are_numbered(self):
        for tool in written():
            asked = [int(m.group(1)) for line in part(pack(tool), PARTS[8]) if (m := re.match(r"^(?:### )?(\d+)\. ", line))]
            self.assertGreaterEqual(len(asked), 1, tool)
            self.assertEqual(asked, list(range(1, len(asked) + 1)), tool)

    def test_the_old_note_is_gone_and_nothing_live_links_it(self):
        for tool in written():
            self.assertFalse(os.path.exists(os.path.join(OLD, tool + ".md")), f"{tool}: the old note is still there")
            old = f"howitworks/{tool}.md"
            for top in LIVE_DOCS:
                for d, _, files in os.walk(top):
                    if "node_modules" in d or os.sep + ".next" in d:
                        continue
                    for f in files:
                        if f.endswith((".md", ".ts", ".tsx", ".mjs", ".py", ".txt")):
                            with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
                                self.assertNotIn(old, fh.read(), os.path.join(d, f))

    def test_no_em_dash(self):
        if not os.path.isdir(PACKS):
            return
        for name in sorted(os.listdir(PACKS)):
            if name.endswith(".md"):
                with open(os.path.join(PACKS, name), encoding="utf-8") as f:
                    self.assertEqual(f.read().count(chr(0x2014)), 0, name)


if __name__ == "__main__":
    unittest.main()
