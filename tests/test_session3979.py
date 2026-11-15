"""Session 3979 (chain 279): datacenter_tracker_rollups' header names its source on a "Source:" line.

The daily run of 15 November 2026 committed (the first since 12 November), and its package tests failed on one table:
test_fetch_types_and_provenance[datacenter_tracker_rollups], `assert meta["sources"]`, an empty list. The builder wrote
"Sources: datacenter_projects (...)", which the package's provenance (package/src/erw/provenance.py parse_header) does
not read; every other derived builder writes "Source: <id> ERW derived table, ..., <method url>". Where
datacenter_projects is on this machine the builder is run into a temporary folder and its header parsed as the package
parses it.
"""
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))
from erw.provenance import parse_header  # noqa: E402

BUILDER = os.path.join(ROOT, "warehouse", "derived", "datacenter_tracker_rollups.py")


class TheRollupsNameTheirSource(unittest.TestCase):
    def test_the_builder_writes_a_source_line(self):
        src = open(BUILDER, encoding="utf-8").read()
        self.assertIn('f"Source: {SOURCE} ERW derived table,', src)
        self.assertNotIn('"Sources: datacenter_projects', src)
        self.assertIn('METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/datacenter_tracker_rollups.md"', src)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", "datacenter_tracker_rollups.md")))

    def test_the_package_reads_such_a_line(self):
        # the package's reader (backends.py) strips the "# " before parse_header sees a line
        line = ("Source: erw:datacenter_projects ERW derived table, the datacenter tracker's rollups of datacenter_projects, "
                "the news the ERW scores (docs/methods/datacenter_tracker_rollups.md), "
                "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/datacenter_tracker_rollups.md")
        info = parse_header([line])
        self.assertEqual([s["source"] for s in info["sources"]], ["erw:datacenter_projects"])
        self.assertTrue(info["sources"][0]["report_url"].endswith("datacenter_tracker_rollups.md"))

    def test_the_written_header_names_the_rows_source(self):
        if not os.path.exists(os.path.join(ROOT, "warehouse", "output", "datacenter_projects.csv")):
            raise unittest.SkipTest("datacenter_projects is not on this machine")
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run([sys.executable, BUILDER, "--out", d], capture_output=True, text=True, cwd=ROOT, timeout=300)
            self.assertEqual(p.returncode, 0, p.stderr[-500:])
            with open(os.path.join(d, "datacenter_tracker_rollups.csv"), encoding="utf-8") as f:
                lines = f.read().split("\n")
        header = [ln[1:].lstrip(" ") for ln in lines if ln.startswith("#")]   # as backends.py reads it
        info = parse_header(header)
        cols = next(ln for ln in lines if not ln.startswith("#")).split(",")
        first = next(ln for ln in lines if ln and not ln.startswith("#") and not ln.startswith("entity,")).split(",")
        row_source = first[cols.index("source")]
        self.assertTrue(info["sources"])
        self.assertTrue(all(s["source"] == row_source or s["report_url"] for s in info["sources"]))
        self.assertEqual(info["sources"][0]["source"], "erw:datacenter_projects")


if __name__ == "__main__":
    unittest.main()
