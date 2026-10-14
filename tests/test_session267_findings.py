"""Session 267 (Research): the review pack's content beyond its form, and the verdict beside each draft.

Energy Research Warehouse (ERW). tests/test_session262.py holds the form of every pack. This file holds what is
Research's own: the old how-it-works note is gone and its content is in the pack (its demo as the appendix, its
sources); the README row points at the pack; each cross-check row of the pack names a figure and a gap; and the review
list's verdicts (site/lib/findingverdicts.ts) are the 28 of docs/reviews/findings-verified-2026-10-13.md, id for id
and word for word, and the page prints one beside every draft, "no verdict" for a draft raised after that evening.
Nothing here sets the environment, reads a table or makes a request.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PACK = os.path.join(ROOT, "docs", "reviews", "packs", "research.md")
OLD = os.path.join(ROOT, "docs", "howitworks", "research.md")
README = os.path.join(ROOT, "docs", "howitworks", "README.md")
DOC = os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-13.md")
VERDICTS = os.path.join(ROOT, "site", "lib", "findingverdicts.ts")
PAGE = os.path.join(ROOT, "site", "app", "internal", "findings", "page.tsx")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def section(text, heading):
    lines = text.split("\n")
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1:end]


class ThePack(unittest.TestCase):
    def test_the_old_note_is_gone_and_the_readme_points_at_the_pack(self):
        self.assertFalse(os.path.exists(OLD))
        self.assertTrue(os.path.exists(PACK))
        row = [line for line in read(README).split("\n") if line.startswith("| Research |")]
        self.assertEqual(len(row), 1)
        self.assertIn("../reviews/packs/research.md", row[0])

    def test_the_old_notes_content_is_folded_in(self):
        text = read(PACK)
        # the demo, its recovery lines and the old note's figures (session 260)
        for words in ("### Minute 0 to 1: the page and one card", "### Minute 4 to 5: asking, and the review list",
                      "### If something goes wrong", "126.6x", "18,204 MW", "3,016.40", "1,081", "38.8", "52.8",
                      "02:55:07", "45,968", "USD 0.0040", "6,797", "105 pairs", "3,509 GW", "25.68", "311.80"):
            self.assertIn(words, text, words)

    def test_the_cross_checks_name_figures_and_gaps(self):
        rows = [r for r in section(read(PACK), "## 4. The cross-checks") if r.startswith("|") and not set(r) <= set("|-: ")]
        rows = rows[1:]                       # the header
        self.assertGreaterEqual(len(rows), 10)
        drafts = [r for r in rows if re.search(r"`scan-[a-z]+-[0-9a-f]{12}`", r)]
        self.assertGreaterEqual(len(drafts), 10)
        for r in rows:
            cells = [c.strip() for c in r.strip().strip("|").split(" | ")]
            self.assertEqual(len(cells), 5, r[:60])
            self.assertTrue(all(cells), r[:60])
            self.assertRegex(cells[1] + cells[2], r"\d", r[:60])

    def test_the_section_8_names_do_files_that_exist(self):
        body = "\n".join(section(read(PACK), "## 8. What Samuel's Stata run must reproduce"))
        named = set(re.findall(r"do (\w+\.do)", body))
        self.assertGreaterEqual(len(named), 5)
        for name in named:
            self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "public", "findings", name)), name)

    def test_no_em_dash(self):
        for path in (PACK, VERDICTS, PAGE, README):
            self.assertEqual(read(path).count(chr(0x2014)), 0, path)


class TheVerdicts(unittest.TestCase):
    def doc_verdicts(self):
        doc = read(DOC)
        out = {}
        for n, body in zip(*[iter(re.split(r"\n### (\d+)\. ", doc)[1:])] * 2):
            m = re.search(r"\*\*Draft:\*\* `(scan-[a-z]+-[0-9a-f]{12})`", body)
            v = re.search(r"\*\*Verdict: (strong|usable|drop)\.\*\* (.+)", body)
            if m and v:
                out[m.group(1)] = (int(n), v.group(1), v.group(2).strip())
        return out

    def test_the_28_verdicts_are_the_documents(self):
        want = self.doc_verdicts()
        self.assertEqual(len(want), 28)
        ts = read(VERDICTS)
        got = dict(
            (m.group(1), (int(m.group(2)), m.group(3)))
            for m in re.finditer(r'"(scan-[a-z]+-[0-9a-f]{12})": \{ block: (\d+), verdict: "(\w+)"', ts))
        self.assertEqual(set(got), set(want))
        for k, (n, verdict, reason) in want.items():
            self.assertEqual(got[k], (n, verdict), k)
            self.assertIn(reason.replace("\\", "\\\\").replace('"', '\\"'), ts, k)
        counts = {w: sum(1 for v in want.values() if v[1] == w) for w in ("strong", "usable", "drop")}
        self.assertEqual(counts, {"strong": 7, "usable": 14, "drop": 7})

    def test_the_page_prints_a_verdict_beside_every_draft(self):
        page = read(PAGE)
        self.assertIn('from "@/lib/findingverdicts"', page)
        self.assertIn("<VerdictLine id={d.id} />", page)
        self.assertIn("no verdict", page)
        # words and an attribute only: the review buttons and the sections are as they were
        for kept in ("<DraftReview id={d.id}", 'title="Waiting for a ruling"', 'title="Ruled"'):
            self.assertIn(kept, page)


if __name__ == "__main__":
    unittest.main()
