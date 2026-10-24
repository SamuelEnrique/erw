"""Session 1173 (chain 078): the Grid pack brought current against main after chains 077 and 078.

Energy Research Warehouse (ERW). docs/reviews/packs/grid.md was rewritten in place: its production figures read through
the internal view at 2026-10-24 00:58 UTC (docs/brand/review-1173/walk-1173.mjs, its record walk-1173-prod.json), the
branch's figures marked as from the code, the demo corrected to the four tabs with each step marked walked on production
or to be walked on landing B's build. What is held here: the two states said in the opening, the record exists and holds
the figures the pack quotes from it, every demo step is marked, the six owner's questions stand, no em dash.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def part(text, heading):
    lines = text.split("\n")
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1:end]


class ThePack(unittest.TestCase):
    def setUp(self):
        self.pack = src("docs", "reviews", "packs", "grid.md")

    def test_the_opening_says_both_states(self):
        opening = self.pack[:self.pack.index("## Against roadmap item 2")]
        self.assertIn("Brought current by session 1173 (chain 078, 24 October 2026)", opening)
        self.assertIn("**On production**", opening)
        self.assertIn("2026-10-24 00:58 UTC", opening)
        self.assertIn('"from the code, to be read on landing B\'s build"', opening)
        self.assertIn("docs/brand/review-1173/walk-1173.mjs", opening)

    def test_four_tabs_and_the_panel(self):
        body = "\n".join(part(self.pack, "## 1. What it is for, and for whom"))
        self.assertIn("four tabs and the Ask panel beside every tab", body)
        self.assertIn("(chain 078: was \"six views\"", body)
        for tab in ("| Mix (the tab the page opens on) |", "| Network |", "| Clean |", "| Gravity |", "| Ask (a panel beside every tab) |"):
            self.assertIn(tab, body)

    def test_the_blind_spots_keep_their_numbers(self):
        body = "\n".join(part(self.pack, "## 6. What the model cannot see, ranked"))
        for n, words in ((3, "Since session 1165 (chain 078)"), (4, "Session 1169 (chain 078)"), (6, "Landing B (session 1167)"),
                         (9, "Since session 1171 (chain 078)"), (11, "Since session 1170 (chain 078)")):
            item = re.search(rf"^{n}\. .*$", body, re.M).group(0)
            self.assertIn(words, item, n)
        nums = [int(m.group(1)) for m in re.finditer(r"^(\d+)\. ", body, re.M)]
        self.assertEqual(nums, list(range(1, 18)))

    def test_every_demo_step_is_marked(self):
        demo = part(self.pack, "## Appendix: the five-minute demo")
        steps = [line for line in demo if re.match(r"^\d+\. ", line)]
        self.assertGreaterEqual(len(steps), 12)
        for line in steps:
            self.assertTrue("**Walked on production.**" in line or "To be walked on landing B's build" in line
                            or "the clicks not made by session 1173" in line or line.startswith("5. Click **Map**"), line[:80])
        self.assertNotIn("The page opens on **ERCOT**, tab **Now**", "\n".join(demo))

    def test_the_owners_questions_stand_at_six(self):
        body = part(self.pack, "## 9. Questions only Samuel can answer")
        self.assertEqual([int(m.group(1)) for line in body if (m := re.match(r"^(\d+)\. ", line))], [1, 2, 3, 4, 5, 6])
        self.assertIn("docs/reviews/grid-rulings-2026-10-23.md", "\n".join(body))


class TheRecord(unittest.TestCase):
    def test_the_record_holds_the_quoted_figures(self):
        rec = json.loads(src("docs", "brand", "review-1173", "walk-1173-prod.json"))
        self.assertTrue(rec["at"][0].startswith("2026-10-24T00:58"))
        by = {r["address"]: r for r in rec["record"]}
        self.assertTrue(all(r["status"] == 200 for r in rec["record"]))
        self.assertIn("492,641 MW", by["/grid"]["sentences"]["now"])
        self.assertIn("45 hours before the latest hourly refresh", by["/grid?grid=ercot"]["sentences"]["now"])
        net = next(p for p in by["/grid?grid=ercot&view=network"]["panels"] if p["panel"] == "grid_network_ercot")
        self.assertEqual({f["key"]: f["shown"] for f in net["figures"]}["net|import|ERCO|2026-10-22T03:00:00Z"], "350")
        self.assertIn("Net imports were 16.84 percent of CAISO's demand", by["/grid?grid=caiso&view=gravity&shape=gravity"]["sentences"]["twelve"])
        self.assertIn("ISO-NE 12 of 12 37.3%", by["/grid?grid=ercot&view=clean"]["sentences"]["seven2024"])
        self.assertNotIn("INTERNAL_COSTS_TOKEN=", src("docs", "brand", "review-1173", "walk-1173-prod.json"))

    def test_no_em_dash(self):
        for parts in (("docs", "reviews", "packs", "grid.md"), ("docs", "brand", "review-1173", "walk-1173.mjs"),
                      ("docs", "brand", "review-1173", "walk-1173-prod.json"), ("tests", "test_session1173.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
