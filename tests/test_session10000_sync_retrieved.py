"""Session 10000 (chain 701): scripts/sync.py compares a table with no ts_utc, event_date or date by retrieved_at. By rows
alone, GitHub's October EIA-860M planned table (2,328 rows) read as older than this machine's September one (2,361 rows),
so it was never restored and the project map stopped on the two 860M tables' different months. Made-up files; no
request is made."""
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import sync  # noqa: E402


class ASnapshotIsComparedByItsRetrieval(unittest.TestCase):
    def test_an_entities_table_reads_its_retrieved_at(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "eia860m_planned_generators.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("# a header\nentity_id,capacity_mw,vintage,retrieved_at\n"
                        "eia860:1:1,10,2026-09,2026-10-24T14:49:59Z\neia860:1:2,20,2026-09,2026-10-24T14:49:59Z\n")
            self.assertEqual(sync.local_state(p), (2, "retrieved_at", "2026-10-24 14:49:59"))

    def test_a_newer_vintage_with_fewer_rows_is_not_ahead(self):
        here, redivis = (2361, "2026-10-24 14:49:59"), (2328, "2026-11-26 15:08:16")
        self.assertEqual(sync.classify(here, redivis, by_retrieval=True), "behind")   # the later retrieval decides
        self.assertEqual(sync.classify(here, redivis), "diverged")   # a real time column keeps its rule
        self.assertEqual(sync.classify((2400, "2026-11-27 01:00:00"), redivis, by_retrieval=True), "ahead")
        self.assertEqual(sync.classify((2361, "2026-11-26 15:08:16"), redivis, by_retrieval=True), "ahead")   # a tie: rows

    def test_a_time_column_still_comes_first(self):
        self.assertEqual(sync.TIME_COLUMNS[:3], ("ts_utc", "event_date", "date"))
        self.assertEqual(sync.TIME_COLUMNS[-1], "retrieved_at")


if __name__ == "__main__":
    unittest.main()
