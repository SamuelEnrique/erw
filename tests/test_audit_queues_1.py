"""Audit of the interconnection queue, finding 1 (session 10213, docs/reviews/queues-model-audit-2026-11-26.md): the page
said a solar-with-storage request's capacity is "both parts" in every grid. The builder sums mw_1 + mw_2 + mw_3, but
Berkeley Lab's file gives a hybrid's second part its own MW only in CAISO (730 of 733 requests with a type_2) and for
some of the West's (360 of 1,862); in ERCOT, ISO-NE, MISO, NYISO, PJM, SPP and the Southeast none of the 2,462 does.
So CAISO's hybrids count both parts and ERCOT's one figure, and the grids' MW of hybrids are not alike.

1. In Berkeley Lab's rows (read where the warehouse holds them; skipped where it does not): CAISO's second parts carry
   MW, ERCOT's and PJM's none. Passes on main.
2. In the page's file: the builder's sum is what the file gives, so ERCOT's solar-with-storage active MW are the first
   parts alone (no figure is moved by this branch). Passes on main.
3. The fix on this branch, words only: the chart's note, the technology table's note, decision 4 and the method note say
   where both parts are counted. Fails on main."""
import csv
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LBNL = os.environ.get("ERW_LBNL_CSV") or os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def rows():
    with open(LBNL, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(ln for ln in f if not ln.startswith("#")))


def mw(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


@unittest.skipUnless(os.path.exists(LBNL), "lbnl_interconnection_queue.csv is not on this machine")
class TheFileGivesTheSecondPartMwInTwoRegions(unittest.TestCase):
    def test_caiso_gives_the_second_part_mw_and_seven_regions_never_do(self):
        by = {}
        for r in rows():
            if r["type_2"]:
                n, m = by.get(r["region"], (0, 0))
                by[r["region"]] = (n + 1, m + (mw(r["mw_2"]) > 0))
        self.assertGreater(by["CAISO"][1], 0.9 * by["CAISO"][0])
        self.assertTrue(0 < by["West"][1] < by["West"][0])
        for g in ("ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP", "Southeast"):
            self.assertGreater(by[g][0], 100, g)
            self.assertEqual(by[g][1], 0, g)


class ThePageSaysWhereBothPartsAreCounted(unittest.TestCase):
    def test_the_figures_do_not_move(self):
        q = json.loads(src("site", "data", "queues.json"))
        if q.get("hybrid") == "largest part":   # session 11408 (wip/ready-queues-hybrid-largest): rebuilt at landing
            self.assertEqual(round(q["views"]["caiso|all"]["whole"]["total_active_mw"]), 129435)
        else:
            self.assertEqual(round(q["views"]["caiso|all"]["whole"]["total_active_mw"]), 190717)
        self.assertEqual(round(q["views"]["ercot|solar_battery"]["whole"]["total_active_mw"]), 112068)

    def test_the_words_say_both_parts_only_where_the_file_gives_them(self):
        page = src("site", "app", "queues", "page.tsx")
        self.assertNotIn("for solar with storage, both parts.", page)
        self.assertNotIn("and its capacity is both parts together.", page)
        # session 11408 (wip/ready-queues-hybrid-largest): the words of the other choice, each hybrid at its largest part
        self.assertIn("a hybrid counts at its largest part, since the file gives a second part its own MW in CAISO and for some of the "
                      "West&apos;s requests and in no other grid, so every grid&apos;s hybrids count alike.", page)
        self.assertIn("so a hybrid at its largest part counts alike in every grid.", page)
        dec = src("site", "lib", "decisions.ts")
        words = ("a hybrid's is its largest part (the file gives a second part its own MW in CAISO and for some of the West's requests "
                 "only, so the largest part counts every grid's hybrids alike)")
        self.assertIn(words, dec)
        note = src("docs", "methods", "interconnection_queue_summary.md")
        self.assertIn(words, note)
        self.assertIn("**A hybrid's parts carry MW in two regions only**", note)
        self.assertIn("1,507 active requests have a battery part that carries no MW in the file", note)
        for t in (page, dec, note):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
