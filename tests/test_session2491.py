"""Session 2491: ZIMSTAT's Index of Electricity Generation, Appendix A (Zimbabwe's generation a month, 2019 to 2026).

Energy Research Warehouse (ERW). Tests warehouse/connectors/zimstat_zimbabwe_generation.py on a text built here (made up
for the test, not ZIMSTAT's): the table of contents' line passed over, each month's figures in the years' order, GWh to
MWh, a row of seven figures (the newest year not yet published), a figure with a comma for its decimal point not written
and counted, the quarter rows compared and not written; a missing appendix, a header of other years and a month row of
too few figures stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2491 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import zimstat_zimbabwe_generation as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
NL = chr(10)
TOC = "Appendix A: Volume of Electricity Generation in GWh, 2019 to 3rd Quarter 2025 ....86" + NL + "Appendix B: Index ...86"


def text(years=" ".join(S.YEARS), jan="840.6 411.6 593.4 705.5 471.1 708.6 742.5 971,5", apr="808.8 411.8 697.9 737.0 664.4 774.7 900.0"):
    rows = [f"January {jan}", "February 814.2 446.4 569.0 733.5 426.2 791.8 787.5 916.3",
            "March 839.4 478.9 652.6 827.8 554.8 750.1 888.3 1,036.1", f"April {apr}",
            "Q1 2,494.2 1,337.0 1,815.0 2,267.1 1,452.1 2,250.6 2,418.2"]
    return NL.join([TOC, "6. Appendices", "Appendix A: Volume of Electricity Generation in GWh, 2019 to 1st Quarter 2026", years]
                   + rows + ["Appendix B: Index of Electricity Generation", " ".join(S.YEARS), "Q1 100.0 56.3"])


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        t = S.parse_text(text(), BASE, counts)
        r = dict(zip(t.ts_utc, t.value))
        self.assertEqual(r["2019-01-01T00:00:00Z"], 840600.0)
        self.assertEqual(r["2026-03-01T00:00:00Z"], 1036100.0)
        self.assertEqual(r["2026-02-01T00:00:00Z"], 916300.0)
        self.assertNotIn("2026-01-01T00:00:00Z", r)
        self.assertNotIn("2026-04-01T00:00:00Z", r)
        self.assertEqual(r["2025-04-01T00:00:00Z"], 900000.0)
        self.assertEqual(len(t), 8 * 3 - 1 + 7)
        self.assertEqual(counts["figures out of form"], 1)
        self.assertEqual((counts["quarters compared"], counts["quarters agreeing"]), (7, 6))   # 2022's Q1 differs by 0.3 GWh
        self.assertEqual(set(t.freq), {"P1M"})
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        for bad in (TOC, text(years="2018 2019 2020 2021 2022 2023 2024 2025"), text(apr="808.8 411.8 697.9")):
            with self.assertRaises(RuntimeError):
                S.parse_text(bad, BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
