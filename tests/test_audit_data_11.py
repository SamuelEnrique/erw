"""Audit of the data pages, finding 9, a data fault (session 10233, docs/reviews/data-model-audit-2026-11-26.md).
A test only, not for landing: it shows the row, and changes nothing.

/data's Last cell for news_index is coverage's ts_max, 2026-12-01, five days after coverage was built: one row of the
news index, an industry event's listing page, is dated at the event rather than at its publication (the standard's
events shape asks the connector to say which; the news index dates a story by its publish time). The fix belongs to the
news pipeline (a data request), not to the page."""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class ANewsRowDatedAfterItsRun(unittest.TestCase):
    def test_a_row_is_dated_after_the_tables_last_run(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            cov = {r["table"]: r for r in csv.DictReader(f)}
        run = cov["news_index"]["last_run"]
        with open(os.path.join(ROOT, "warehouse", "output", "news_index.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(l for l in f if not l.startswith("#")))
        later = [r for r in rows if r["event_date"] > run]
        self.assertGreater(len(later), 0)
        self.assertGreater(cov["news_index"]["ts_max"], run)
        print(f"\nnews_index rows dated after its last run ({run}): {len(later)}; "
              + "; ".join(f"{r['event_date']} {r['source']}: {r['headline'][:80]}" for r in later))


if __name__ == "__main__":
    unittest.main()
