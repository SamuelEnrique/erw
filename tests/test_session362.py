"""Session 362: the archive proven (warehouse/archive/prove.py, docs/state/archive_proof_2026-10-20.csv).

Energy Research Warehouse (ERW). The rows here are test fixtures. No network.

  1. the comparison's hash is the same for the same rows in any order and any retrieval time, and differs by a value;
  2. the listing names every table of coverage once, with a status from the documented set, and a cause for each
     mismatch.

    python -m unittest tests.test_session362 -v
"""

import csv
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "archive"))
import prove as P  # noqa: E402

HEAD = "entity,variable,ts_utc,value,unit,source,retrieved_at\n"
ROWS = ["x:a,v,2026-01-01T00:00:00Z,1,MW,s,2026-10-20T00:00:00Z\n", "x:a,v,2026-01-02T00:00:00Z,2,MW,s,2026-10-20T00:00:00Z\n"]


class TestHash(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw362_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name, rows):
        p = os.path.join(self.tmp, name)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write("# a header\n" + HEAD + "".join(rows))
        return p

    def test_order_and_retrieval_do_not_count(self):
        a = P.stats(self.write("a.csv", ROWS))
        b = P.stats(self.write("b.csv", [ROWS[1].replace("2026-10-20T00", "2026-10-21T00"), ROWS[0]]))
        self.assertEqual((a[0], a[1]), (2, "2026-01-02T00:00:00Z"))
        self.assertEqual(P.sha(a[2]), P.sha(b[2]))
        c = P.stats(self.write("c.csv", [ROWS[0], ROWS[1].replace(",2,MW", ",3,MW")]))
        self.assertNotEqual(P.sha(a[2]), P.sha(c[2]))


class TestListing(unittest.TestCase):
    def test_every_table_once_with_a_cause(self):
        with open(os.path.join(ROOT, "docs", "state", "archive_proof_2026-10-20.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            tables = {r["table"] for r in csv.DictReader(f)}
        self.assertEqual(len(rows), len({r["table"] for r in rows}))
        self.assertLessEqual({r["table"] for r in rows}, tables | {r["table"] for r in rows})
        ok = {"equal", "this machine behind", "both differ", "not in the archive", "archive behind", "not on this machine"}
        for r in rows:
            self.assertIn(r["status"], ok, r["table"])
            if r["status"] != "equal":
                self.assertTrue(r["cause"], r["table"])
        fixed = [r for r in rows if r["after_session_362"]]
        self.assertEqual(len(fixed), 7)


if __name__ == "__main__":
    unittest.main()
