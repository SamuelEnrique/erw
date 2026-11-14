"""Session 3967 (chain 278): the shadow scores' stored outlet names are folded as the stories' are.

The daily run of 14 November 2026 stopped at its coverage step: news_scores_shadow named 'IEA <en dash> International
Energy Agency', which session 3940 had folded out of the registry, and the shadow scorer (expired 6 October) never writes
its table again. warehouse/news/ingest.py now folds those stored names every day, before coverage. No network, no lock:
the output folder is a temporary one and the lock check is stubbed.
"""
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS = os.path.join(ROOT, "warehouse", "news")
if NEWS not in sys.path:
    sys.path.insert(0, NEWS)
import ingest  # noqa: E402

COLS = ["event_id", "event_date", "event_type", "parties", "mw", "source", "source_url", "story_id", "model_id",
        "significance", "ai_power_relevance", "sector", "region", "price_mentioned", "headline", "why",
        "is_duplicate_of", "cluster_id", "scored_at", "run_id"]
DASHED = "IEA " + chr(0x2013) + " International Energy Agency"


def row(i, source):
    r = {c: "" for c in COLS}
    r.update(event_id=f"shadow:news:{i}:claude-haiku-4-5", event_date=f"2026-10-0{i}T00:00:00Z", event_type="shadow_score",
             source=source, source_url=f"https://example.org/{i}", story_id=f"news:{i}", model_id="claude-haiku-4-5",
             significance=str(i), ai_power_relevance="1", why="a reason, with a comma")
    return r


class TheFold(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "news_scores_shadow.csv")
        with open(self.path, "w", encoding="utf-8", newline="") as f:
            f.write("# Energy Research Warehouse (ERW): shadow news scores.\n")
            f.write("# Retrieved: 20261004T143649Z (shadow scoring run).\n")
            f.write("# File holds 3 rows, 2026-10-01T00:00:00Z to 2026-10-03T00:00:00Z.\n")
            pd.DataFrame([row(1, DASHED), row(2, "Bloomberg"), row(3, DASHED)], columns=COLS).to_csv(
                f, index=False, lineterminator="\n")
        self.patches = [mock.patch.object(ingest.ip, "OUT_DIR", self.tmp.name),
                        mock.patch.object(ingest.ip, "_require_lock", lambda *a: None)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_the_dashed_names_are_folded_and_nothing_else_moves(self):
        before = ingest.ip.read_series(self.path, COLS)
        n = ingest.fold_shadow_sources(lambda *a: None, "20261114T160000Z")
        self.assertEqual(n, 2)
        after = ingest.ip.read_series(self.path, COLS).set_index("event_id")
        self.assertEqual(len(after), 3)
        self.assertEqual(sorted(after["source"].unique()), ["Bloomberg", "IEA - International Energy Agency"])
        b = before.set_index("event_id")
        self.assertTrue((after.drop(columns="source") == b.loc[after.index].drop(columns="source")).all().all())

    def test_the_header_keeps_its_retrieved_line_and_says_what_was_done(self):
        ingest.fold_shadow_sources(lambda *a: None, "20261114T160000Z")
        head = [l for l in open(self.path, encoding="utf-8") if l.startswith("#")]
        self.assertTrue(any("Retrieved: 20261004T143649Z" in l for l in head))
        self.assertTrue(any("Session 3967: 2 stored rows' outlet names folded" in l for l in head))
        self.assertEqual(sum(l.startswith("# File holds ") for l in head), 1)
        self.assertFalse(any(chr(0x2013) in l or chr(0x2014) in l for l in open(self.path, encoding="utf-8")))

    def test_a_second_run_writes_nothing(self):
        ingest.fold_shadow_sources(lambda *a: None, "20261114T160000Z")
        mtime = os.path.getmtime(self.path)
        self.assertEqual(ingest.fold_shadow_sources(lambda *a: None, "20261115T160000Z"), 0)
        self.assertEqual(os.path.getmtime(self.path), mtime)

    def test_no_table_no_write(self):
        os.remove(self.path)
        self.assertEqual(ingest.fold_shadow_sources(lambda *a: None, "20261114T160000Z"), 0)
        self.assertFalse(os.path.exists(self.path))

    def test_main_calls_it_before_the_registry(self):
        src = open(os.path.join(NEWS, "ingest.py"), encoding="utf-8").read()
        main = src[src.index("def main("):]
        self.assertLess(main.index("fold_shadow_sources(log, run_id)"), main.index("ip.update_sources("))


if __name__ == "__main__":
    unittest.main()
