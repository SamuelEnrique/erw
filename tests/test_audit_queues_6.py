"""Audit of the interconnection queue, finding 5 (session 10213, docs/reviews/queues-model-audit-2026-11-26.md): the page
reads every grid as of "the end of 2025". In the 2026 edition each grid's newest dates differ: no CAISO request after
17 April 2023, one ISO-NE request of 2025, NYISO's newest operation date 31 December 2023 and MISO's 19 December 2024
(so the chart of waits has no later point there because the file dates none); and 53 requests (13,275 MW) carry a
withdrawal date in January 2026 and count as withdrawn, not active. No figure moves.

1. In Berkeley Lab's rows (skipped where the warehouse does not hold them): those dates and counts. Passes on main.
2. The fix on this branch, words only: a line of the fold "What the file does not hold" and the method note say so.
   Fails on main."""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LBNL = os.environ.get("ERW_LBNL_CSV") or os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(LBNL), "lbnl_interconnection_queue.csv is not on this machine")
class EachGridsNewestDates(unittest.TestCase):
    def test_the_dates(self):
        with open(LBNL, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
        newest = lambda g, col: max(r[col] for r in rows if r["region"] == g and r[col])
        self.assertEqual(newest("CAISO", "q_date"), "2023-04-17")
        self.assertEqual(newest("NYISO", "on_date"), "2023-12-31")
        self.assertEqual(newest("MISO", "on_date"), "2024-12-19")
        self.assertEqual(sum(1 for r in rows if r["region"] == "ISO-NE" and r["q_date"][:4] == "2025"), 1)
        late = [r for r in rows if r["q_status"] == "withdrawn" and r["wd_date"] > "2025-12-31"]
        self.assertEqual(len(late), 53)
        self.assertEqual(round(sum(max(float(r["capacity_mw"]), 0) for r in late)), 13275)
        self.assertEqual((min(r["wd_date"] for r in late), max(r["wd_date"] for r in late)), ("2026-01-02", "2026-01-16"))


class TheFoldSaysSo(unittest.TestCase):
    def test_the_words(self):
        page = src("site", "app", "queues", "page.tsx")
        self.assertIn('<li data-grid-dates="1">One date for every grid.', page)
        self.assertIn("NYISO&apos;s newest operation date is 31 December 2023 and MISO&apos;s 19 December 2024, so a later year has no point for "
                      "them because the file dates none, not because none was built.", page)
        self.assertIn("53 requests (13,275 MW) carry a withdrawal date of 2 to 16 January 2026 and count as withdrawn, not active.", page)
        note = src("docs", "methods", "interconnection_queue_summary.md")
        self.assertIn("- One date for every grid (session 10213", note)
        self.assertIn("it would be up to 8,566 at that date (1,864,963 MW, up to 1,878,238)", note)
        for t in (page, note):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
