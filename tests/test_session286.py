"""Session 286: the hunt's drafts of 14 October 2026, verified, and the motion proofs of the strong ones.

Energy Research Warehouse (ERW). Held here, with no request, no model call and no read of the review list: the
appended section of docs/reviews/findings-verified-2026-10-13.md agrees with its result file (twelve blocks, the same
ids, strongest first, every draft reproduced); the earlier sections are kept; and every number of the two motion specs
is the draft's own value for that year.
"""

import glob
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOC = os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-13.md")
KIT = os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-14-session286")
MOTION = os.path.join(ROOT, "docs", "research", "motion", "hunt-2026-10-14")
HEADING = "## Session 286's twelve drafts, verified (the hunt of 14 October 2026)"
EM = chr(0x2014)


def results():
    with open(os.path.join(KIT, "verify_286.json"), encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)}


class TheDocument(unittest.TestCase):
    def setUp(self):
        with open(DOC, encoding="utf-8") as f:
            self.doc = f.read()
        self.section = self.doc.split(HEADING, 1)[1]

    def test_the_earlier_sections_are_kept_and_this_one_is_last(self):
        self.assertIn("## The 16 drafts from before session 251, strongest first", self.doc)
        self.assertIn("## Session 251's twelve drafts, verified", self.doc)
        self.assertLess(self.doc.index("## Session 251's twelve drafts, verified"), self.doc.index(HEADING))
        self.assertNotIn("\n## ", self.section)

    def test_twelve_blocks_numbered_on_strongest_first(self):
        nums = [int(n) for n in re.findall(r"^### (\d+)\. ", self.section, re.M)]
        self.assertEqual(nums, list(range(29, 41)))
        verdicts = re.findall(r"^- \*\*Verdict: (strong|usable|drop)\.\*\*", self.section, re.M)
        self.assertEqual(verdicts, ["strong"] * 2 + ["usable"] * 6 + ["drop"] * 4)

    def test_the_blocks_are_the_result_files_drafts_and_each_reproduced(self):
        res = results()
        ids = re.findall(r"^- \*\*Draft:\*\* `(scan-hunt-[0-9a-f]+)`", self.section, re.M)
        self.assertEqual(sorted(ids), sorted(res))
        for r in res.values():
            self.assertEqual(r["problems"], [], r["id"])
            self.assertTrue(r["reproduced_from_own_csv"] and r["reproduced_from_tables_full_years"], r["id"])
        self.assertEqual(self.section.count("- **Reproduced:** yes, exactly."), 12)

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.section)
        for p in glob.glob(os.path.join(KIT, "*.py")) + [os.path.join(MOTION, "README.md")]:
            with open(p, encoding="utf-8") as f:
                self.assertNotIn(EM, f.read(), p)


class TheMotionProofs(unittest.TestCase):
    def test_every_number_is_the_drafts(self):
        res = results()
        specs = sorted(glob.glob(os.path.join(MOTION, "specs", "*.json")))
        self.assertEqual([os.path.basename(p)[:-5] for p in specs], ["scan-hunt-4aa7db84eaa1", "scan-hunt-7a9b1b9695e1"])
        for p in specs:
            with open(p, encoding="utf-8") as f:
                s = json.load(f)
            r = res[s["id"]]
            self.assertEqual(s["type"], "draw-on")
            self.assertEqual(len(s["series"]), 1)
            self.assertEqual(s["series"][0]["values"], [r["series"][x][0] for x in s["x"]], s["id"])
            self.assertEqual(s["x"][-1], str(r["claim"]["last_year"]))
            for year in (r["claim"]["first_year"], r["claim"]["last_year"]):   # the subtitle's two figures are the claim's
                self.assertIn(str(year), s["subtitle"])

    def test_both_sizes_with_their_stills(self):
        for sid in ("scan-hunt-4aa7db84eaa1", "scan-hunt-7a9b1b9695e1"):
            for size in ("1080x1350", "1080x1080"):
                for ext in (".mp4", "_last.png"):
                    p = os.path.join(MOTION, f"{sid}_{size}{ext}")
                    self.assertTrue(os.path.exists(p) and os.path.getsize(p) > 10_000, p)

    def test_session_274s_seven_specs_are_left_as_they_were(self):
        self.assertEqual(len(glob.glob(os.path.join(ROOT, "motion", "specs", "*.json"))), 7)


if __name__ == "__main__":
    unittest.main()
