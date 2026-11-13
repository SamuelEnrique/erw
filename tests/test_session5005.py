"""Session 5005 (chain 233): the Grid tool's replication runs with no argument after the daily run.

Energy Research Warehouse (ERW). The daily run rewrites site/data/grid_network.json; page_figures.json was written from
one snapshot and nothing rewrote it, so `python replication/grid/replicate.py` stopped (exit 2) the next day. What is
held to:

  replication/grid/snapshot.json is the snapshot page_figures.json is of (the same "built");
  replicate.py reads it by default, and still takes --snapshot;
  figures_of_the_page.py keeps the snapshot it read beside the figures;
  the network group, from the kept snapshot alone, meets every computed figure (exit 0);
  no em or en dash in what the session wrote.

    python -m unittest tests.test_session5005 -v
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
GRID = os.path.join(ROOT, "replication", "grid")
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheKeptSnapshot(unittest.TestCase):
    def test_it_is_the_snapshot_of_the_figures(self):
        with open(os.path.join(GRID, "snapshot.json"), encoding="utf-8") as f:
            snap = json.load(f)
        with open(os.path.join(GRID, "page_figures.json"), encoding="utf-8") as f:
            page = json.load(f)
        self.assertEqual(snap["built"], page["snapshot_built"])

    def test_the_scripts(self):
        rep = src("replication", "grid", "replicate.py")
        self.assertIn('KEPT = os.path.join(HERE, "snapshot.json")', rep)
        self.assertIn('SNAPSHOT = KEPT if os.path.exists(KEPT) else os.path.join(ROOT, "site", "data", "grid_network.json")', rep)
        fig = src("replication", "grid", "figures_of_the_page.py")
        self.assertIn('OUT_SNAPSHOT = os.path.join(HERE, "snapshot.json")', fig)
        self.assertIn("shutil.copyfile(a.snapshot, OUT_SNAPSHOT)", fig)
        for s in (rep, fig, src("tests", "test_session5005.py")):
            for d in DASHES:
                self.assertNotIn(d, s)

    def test_the_default_run_meets_the_network(self):
        with tempfile.TemporaryDirectory() as empty:          # no tables: the network group alone
            r = subprocess.run([sys.executable, os.path.join(GRID, "replicate.py"), "--only", "network", "--tables", empty],
                               cwd=ROOT, capture_output=True, text=True, timeout=600, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertRegex(r.stdout, r"(\d+) of \1 computed figures met")


if __name__ == "__main__":
    unittest.main()
