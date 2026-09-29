"""Session 28: the append-only archive (warehouse/archive/archive.py and restore.py).

Energy Research Warehouse (ERW). Local files only (no bucket), in temporary directories.
The rows are small test fixtures, not data values.

    python -m unittest discover -s tests -v
"""

import datetime as dt
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "archive"))

import archive as A  # noqa: E402
import restore as R  # noqa: E402

ENT = "test_things"                 # an entities table: rows can disappear
ROLL = "ercot_dam_hub_prices"       # a rolling-window series table (restore_before_run)
T1 = dt.datetime(2026, 9, 28, 12, 0, tzinfo=dt.timezone.utc)
T2 = dt.datetime(2026, 9, 29, 12, 0, tzinfo=dt.timezone.utc)
T3 = dt.datetime(2026, 9, 30, 12, 0, tzinfo=dt.timezone.utc)
T4 = dt.datetime(2026, 10, 1, 12, 0, tzinfo=dt.timezone.utc)


def slurp(path):
    with open(path, "rb") as f:
        return f.read()


def ents(rows, cols=("entity_id", "entity_type", "name", "capacity_mw")):
    return pd.DataFrame(rows, columns=list(cols))


def series(rows):
    return pd.DataFrame(rows, columns=["entity", "variable", "ts_utc", "value"])


class ArchiveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out, self.arch = os.path.join(self.tmp, "output"), os.path.join(self.tmp, "archive")
        os.makedirs(self.out)
        os.makedirs(self.arch)
        self.p = [mock.patch.object(A, "OUT", self.out), mock.patch.object(A, "ARCH", self.arch),
                  mock.patch.object(A, "MANIFEST", os.path.join(self.tmp, "archive_manifest.csv")),
                  mock.patch.object(A, "log", lambda m: None)]
        for p in self.p:
            p.start()

    def tearDown(self):
        for p in self.p:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def put(self, name, df, header="source: test fixture"):
        with open(os.path.join(self.out, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# {header}\n")
            df.to_csv(f, index=False, lineterminator="\n")

    def run_at(self, when):
        self.assertEqual(A.write(None, False, now=when), 0)

    def rebuilt(self, name, as_of=None):
        return R.rebuild(name, as_of)[1]

    def same(self, a, b):
        self.assertEqual(list(a.columns), list(b.columns))
        self.assertTrue(np.array_equal(np.sort(A.row_hashes(a)), np.sort(A.row_hashes(b))), (a, b))

    def test_changes_deletes_and_rebuild_as_of_each_run(self):
        v1 = ents([["t:1", "plant", "A", "10"], ["t:2", "plant", "B", "20"], ["t:3", "plant", "C", "30"]])
        v2 = ents([["t:1", "plant", "A", "11"], ["t:3", "plant", "C", "30"], ["t:4", "plant", "D", "40"]])
        self.put(ENT, v1)
        self.run_at(T1)
        self.put(ENT, v2)
        self.run_at(T2)
        month = A.read_month(os.path.join(self.arch, ENT, "2026-09.csv"))
        second = month[month["_run_id"].str.startswith("20260929")]
        self.assertEqual(sorted(second["_op"]), ["delete", "upsert", "upsert"])  # t:2 gone, t:1 changed, t:4 new
        self.same(self.rebuilt(ENT, "2026-09-28T23:59:59Z"), v1)
        self.same(self.rebuilt(ENT), v2)
        self.assertEqual(R.check(ENT, *R.rebuild(ENT)[1:]), [])

    def test_month_file_is_append_only(self):
        self.put(ENT, ents([["t:1", "plant", "A", "10"]]))
        self.run_at(T1)
        path = os.path.join(self.arch, ENT, "2026-09.csv")
        before = slurp(path)
        self.put(ENT, ents([["t:1", "plant", "A", "12"]]))
        self.run_at(T2)
        after = slurp(path)
        self.assertTrue(after.startswith(before) and len(after) > len(before))
        self.put(ENT, ents([["t:1", "plant", "A", "13"]]))
        self.run_at(T4)  # a new month starts a new file; September's is untouched
        self.assertEqual(slurp(path), after)
        self.assertTrue(os.path.exists(os.path.join(self.arch, ENT, "2026-10.csv")))
        self.same(self.rebuilt(ENT), ents([["t:1", "plant", "A", "13"]]))

    def test_unchanged_and_reformatted_rows_are_not_archived_again(self):
        self.put(ROLL, series([["HB_NORTH", "lmp", "2026-09-27T00:00:00Z", "12"]]))
        self.run_at(T1)
        self.put(ROLL, series([["HB_NORTH", "lmp", "2026-09-27T00:00:00Z", "12.0"]]))  # as a Redivis restore writes it
        self.run_at(T2)
        month = A.read_month(os.path.join(self.arch, ROLL, "2026-09.csv"))
        self.assertEqual(len(month), 1)

    def test_a_new_retrieval_time_alone_is_not_archived(self):
        cols = ("entity_id", "entity_type", "name", "retrieved_at")
        self.put(ENT, ents([["t:1", "plant", "A", "2026-09-28T12:00:00Z"]], cols=cols))
        self.run_at(T1)
        self.put(ENT, ents([["t:1", "plant", "A", "2026-09-29T12:00:00Z"]], cols=cols))  # re-pulled, same values
        self.run_at(T2)
        self.assertEqual(len(A.read_month(os.path.join(self.arch, ENT, "2026-09.csv"))), 1)
        self.put(ENT, ents([["t:1", "plant", "B", "2026-09-30T12:00:00Z"]], cols=cols))  # a real change
        self.run_at(T3)
        self.assertEqual(len(A.read_month(os.path.join(self.arch, ENT, "2026-09.csv"))), 2)
        self.assertEqual(R.check(ENT, *R.rebuild(ENT)[1:]), [])

    def test_rolling_table_never_deletes(self):
        full = series([["HB_NORTH", "lmp", "2026-09-26T00:00:00Z", "10"], ["HB_NORTH", "lmp", "2026-09-27T00:00:00Z", "11"]])
        self.put(ROLL, full)
        self.run_at(T1)
        self.put(ROLL, series([["HB_NORTH", "lmp", "2026-09-28T00:00:00Z", "12"]]))  # a short, stale copy
        self.run_at(T2)
        month = A.read_month(os.path.join(self.arch, ROLL, "2026-09.csv"))
        self.assertNotIn("delete", set(month["_op"]))
        self.assertEqual(len(self.rebuilt(ROLL)), 3)

    def test_a_row_that_comes_back_is_archived_again(self):
        row = ["t:1", "plant", "A", "10"]
        self.put(ENT, ents([row, ["t:2", "plant", "B", "20"]]))
        self.run_at(T1)
        self.put(ENT, ents([["t:2", "plant", "B", "20"]]))
        self.run_at(T2)
        self.put(ENT, ents([row, ["t:2", "plant", "B", "20"]]))
        self.run_at(T3)
        self.same(self.rebuilt(ENT), ents([row, ["t:2", "plant", "B", "20"]]))

    def test_a_new_column_goes_to_extra_and_comes_back(self):
        self.put(ENT, ents([["t:1", "plant", "A", "10"]]))
        self.run_at(T1)
        v2 = ents([["t:1", "plant", "A", "10", "TX"]], cols=("entity_id", "entity_type", "name", "capacity_mw", "state"))
        self.put(ENT, v2)
        self.run_at(T2)
        month = A.read_month(os.path.join(self.arch, ENT, "2026-09.csv"))
        self.assertIn('"state": "TX"', month["_extra"].iloc[-1])
        self.same(self.rebuilt(ENT), v2)

    def test_index_rebuilt_from_the_archive_equals_the_kept_one(self):
        self.put(ENT, ents([["t:1", "plant", "A", "10"], ["t:2", "plant", "B", "20"]]))
        self.run_at(T1)
        self.put(ENT, ents([["t:1", "plant", "A", "11"]]))
        self.run_at(T2)
        seen, keys, _ = A.unpack_state(slurp(A.state_path(ENT)))
        s2, k2, _ = R.state_from_archive(ENT)
        self.assertTrue(np.array_equal(seen, s2) and np.array_equal(keys, k2))

    def test_run_log_keeps_each_runs_provenance_header(self):
        self.put(ENT, ents([["t:1", "plant", "A", "10"]]), header="source: report one, retrieved 2026-09-28")
        self.run_at(T1)
        self.put(ENT, ents([["t:1", "plant", "A", "11"]]), header="source: report two, retrieved 2026-09-29")
        self.run_at(T2)
        h1 = R.rebuild(ENT, "2026-09-28T23:59:59Z")[0]
        h2 = R.rebuild(ENT)[0]
        self.assertIn("source: report one, retrieved 2026-09-28", h1)
        self.assertIn("source: report two, retrieved 2026-09-29", h2)


if __name__ == "__main__":
    unittest.main()
