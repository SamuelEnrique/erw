"""Session 713: the gaps of the All grids tab, complete (docs/reviews/siting-gaps.md). Every row has its six cells;
every connector it names exists; the site's copy (site/data/siting/gaps.json) is the table as written, and
/internal/siting-gaps reads it at build time, behind the internal cookie. No request, no model call."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import siting_page as sp  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Gaps(unittest.TestCase):
    def test_the_site_copy_is_the_table(self):
        self.assertEqual(json.loads(src("site", "data", "siting", "gaps.json")), sp.gaps_file())

    def test_every_row_whole_and_every_connector_real(self):
        g = sp.gaps_file()
        self.assertEqual(g["columns"], ["Grid", "Column", "What is not held", "The source that would fill it", "Its license, as recorded", "The connector it resembles"])
        self.assertGreaterEqual(len(g["rows"]), 25)
        for r in g["rows"]:
            self.assertTrue(all(r[c] for c in g["columns"]), r)
            for c in re.findall(r"`([a-z0-9_]+\.py)`", r["The connector it resembles"]):
                self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "connectors", c)), c)

    def test_each_column_of_the_tab_with_a_gap_is_listed(self):
        cols = {r["Column"].split(",")[0].strip() for r in sp.gaps_file()["rows"]}
        for c in ("Transmission and 4CP", "Capacity", "Time to connect", "Headroom", "Utility", "Energy"):
            self.assertIn(c, cols)

    def test_the_page_is_internal_and_reads_the_copy(self):
        p = src("site", "app", "internal", "siting-gaps", "page.tsx")
        self.assertIn('import gapsJson from "@/data/siting/gaps.json";', p)
        self.assertIn("if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();", p)
        self.assertNotIn(chr(0x2014), p + src("docs", "reviews", "siting-gaps.md"))


if __name__ == "__main__":
    unittest.main()
