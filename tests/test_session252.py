"""Session 252: the waiting findings, verified (docs/reviews/findings-verified-2026-10-13.md).

Energy Research Warehouse (ERW). The 16 drafts of the review list (8 of the daily scanner, 8 of the weekly hunt) were
each reproduced from their own data, their tests run again, their license read, and given a verdict: strong, usable or
drop. The document is written by docs/reviews/findings-verified-2026-10-13/build_doc.py from the two result files
beside it.

What is held here: the document has one block a draft, each with its six parts; the blocks are the drafts of the two
result files and no other; the strongest come first; the counts the document says are the counts of its blocks; and
both result files say every draft reproduced. No request, no database, no table.
"""

import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOC = ("docs", "reviews", "findings-verified-2026-10-13.md")
FOLDER = ("docs", "reviews", "findings-verified-2026-10-13")
ORDER = {"strong": 0, "usable": 1, "drop": 2}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def blocks():
    text = src(*DOC)
    body = text[text.index("drafts from before session 251, strongest first"):text.index("## Session 251's new drafts")]
    return [b for b in re.split(r"\n### \d+\. ", body)[1:]]


class TheDocument(unittest.TestCase):
    def test_one_block_a_draft_each_with_its_six_parts(self):
        bs = blocks()
        self.assertEqual(len(bs), 16)
        for b in bs:
            for part in ("- **Draft:**", "- **Claim:**", "- **Number:**", "- **Reproduced:**", "- **Robust", "- **License:**", "- **Verdict: "):
                self.assertIn(part, b, b[:80])

    def test_the_blocks_are_the_drafts_of_the_two_result_files(self):
        ids = [re.search(r"`(scan-[a-z]+-[0-9a-f]{12})`", b).group(1) for b in blocks()]
        self.assertEqual(len(set(ids)), 16)
        held = [r["id"] for name in ("verify_hunt.json", "verify_scanner.json") for r in json.loads(src(*FOLDER, name))]
        self.assertEqual(sorted(ids), sorted(held))

    def test_every_draft_reproduced_in_both_result_files(self):
        hunt = json.loads(src(*FOLDER, "verify_hunt.json"))
        scan = json.loads(src(*FOLDER, "verify_scanner.json"))
        self.assertEqual((len(hunt), len(scan)), (8, 8))
        for r in hunt:
            self.assertEqual(r["problems"], [], r["id"])
            self.assertEqual(r["mirror_exit"], 0, r["id"])
            self.assertTrue(r["reproduced_from_own_csv"] and r["reproduced_from_tables_full_years"], r["id"])
            self.assertEqual(r["state"], "draft", r["id"])
        for r in scan:
            self.assertEqual(r["problems"], [], r["id"])
            self.assertTrue(r["reproduced"], r["id"])
            self.assertGreaterEqual(r["numbers_compared"], 29, r["id"])
            self.assertEqual(r["state"], "draft", r["id"])

    def test_the_strongest_come_first_and_every_verdict_has_a_reason(self):
        verdicts = []
        for b in blocks():
            m = re.search(r"- \*\*Verdict: (strong|usable|drop)\.\*\* (.+)", b)
            self.assertIsNotNone(m, b[:80])
            self.assertGreater(len(m.group(2)), 60, b[:80])
            verdicts.append(m.group(1))
        self.assertEqual(verdicts, sorted(verdicts, key=ORDER.get))

    def test_the_counts_it_says_are_the_counts_of_its_blocks(self):
        said = re.search(r"\*\*Verdicts: (\d+) strong, (\d+) usable, (\d+) drop\.\*\*", src(*DOC))
        verdicts = [re.search(r"- \*\*Verdict: (\w+)\.", b).group(1) for b in blocks()]
        self.assertEqual(tuple(int(x) for x in said.groups()), tuple(verdicts.count(v) for v in ("strong", "usable", "drop")))

    def test_a_dropped_hunt_draft_is_under_one_typical_yearly_move_or_leans_on_its_first_year(self):
        """The reason given for the four dropped hunt drafts is in the numbers: a strength under 1, and under a third
        of the change left without the first year."""
        hunt = {r["id"]: r for r in json.loads(src(*FOLDER, "verify_hunt.json"))}
        for b in blocks():
            did = re.search(r"`(scan-[a-z]+-[0-9a-f]{12})`", b).group(1)
            if did in hunt and "- **Verdict: drop." in b:
                self.assertLess(hunt[did]["claim"]["strength"], 1.0, did)
                self.assertLess(hunt[did]["more"]["share_of_claim_without_first_year"], 1 / 3, did)
            if did in hunt and "- **Verdict: strong." in b:
                self.assertGreaterEqual(hunt[did]["claim"]["strength"], 1.0, did)
                self.assertGreaterEqual(abs(hunt[did]["more"]["spearman_year"]), 0.8, did)

    def test_no_em_dash(self):
        for name in [os.path.join(*DOC)] + [os.path.join(*FOLDER, f) for f in sorted(os.listdir(os.path.join(ROOT, *FOLDER)))]:
            self.assertEqual(src(name).count(chr(0x2014)), 0, name)


if __name__ == "__main__":
    unittest.main()
