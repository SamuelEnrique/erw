"""Session 7052 (chain 370, the data machine): done-line request 262.

/research's weekly chart of the Lower 48's battery discharge read "Source: Energy Research Warehouse (ERW), derived,
Energy Research Warehouse (ERW), derived from California ISO via ..., table storage_daily_cycle": the ERW twice and
California ISO for EIA-930's series. A watch line's stored source now takes session 1896's rule (the publisher of the
series charted, the ERW once), and the stored records were rewritten by it.
"""

import glob
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BAD = "derived, Energy Research Warehouse (ERW), derived from"


class TheSourceLine(unittest.TestCase):
    def test_result_takes_the_roundups_rule_for_a_watch_line(self):
        with open(os.path.join(ROOT, "warehouse", "analysis", "templates", "common.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("def watch_source_line(template, src):", s)
        self.assertIn("roundup.chart_source_line(", s)
        self.assertIn('if template.startswith("watch_"):', s)

    def test_no_stored_chart_names_the_erw_twice(self):
        files = glob.glob(os.path.join(ROOT, "docs", "analysis", "2026-W*", "*.json")) + glob.glob(os.path.join(ROOT, "docs", "analysis", "gallery", "*", "*.json"))
        bad = [f for f in files if BAD in open(f, encoding="utf-8").read()]
        self.assertEqual(bad, [])

    def test_w45s_line_names_eia_930(self):
        with open(os.path.join(ROOT, "docs", "analysis", "2026-W45", "chart_of_the_week.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.assertTrue(d["source_line"].startswith("Source: EIA-930, Hourly Electric Grid Monitor"), d["source_line"])
        self.assertNotIn("California ISO", d["source_line"])


if __name__ == "__main__":
    unittest.main()
