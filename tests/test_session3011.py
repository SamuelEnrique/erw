"""Session 3011 (chain 164): the queue's wait, withdrawals and request size by type (deep/queues.py).

Energy Research Warehouse (ERW). The table of session 3009's test; no warehouse file, no network, no database.
"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
sys.path.insert(0, os.path.dirname(__file__))
import hunt_measures as hm  # noqa: E402
import queues  # noqa: E402
from test_session3009 import lbnl_table  # noqa: E402


class ByType(unittest.TestCase):
    def test_the_type_candidates_reproduce_from_the_table(self):
        with tempfile.TemporaryDirectory() as d:
            lbnl_table(d)
            hm.clear_cache()
            for name in ("months_by_type", "withdrawn_by_type", "request_size"):
                P = next(p for p in queues.CANDIDATES if p["name"] == name)
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, name)
                for region in regions:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{name}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, "lbnl_interconnection_queue.csv")], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (name, r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (name, region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(name, region, y))
                    do = P["reproduce"](region)["do"]
                    self.assertIn("keep if type_clean ==", do)
                    self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), name)
            hm.clear_cache()


if __name__ == "__main__":
    unittest.main()
