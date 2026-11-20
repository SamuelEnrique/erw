"""Sessions 8202 to 8206 (chain 502): the regions, weather, events, authorities and large-load families of the findings hunt.

Energy Research Warehouse (ERW). No warehouse file, no network, no database.
"""

import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
import authorities  # noqa: E402
import check  # noqa: E402
import check_do  # noqa: E402
import events  # noqa: E402
import large_load  # noqa: E402
import regions  # noqa: E402
import weather  # noqa: E402


class Pieces(unittest.TestCase):
    def test_an_event_window_counts_its_hours(self):
        self.assertEqual(events.window_hours(2022, "12-19", "12-29"), 11 * 24)
        self.assertEqual(events.window_hours(2020, "03-01", "05-31"), 92 * 24)
        self.assertEqual(events.day_words(2025, "01-17"), "17 January 2025")

    def test_a_lone_spike_is_dropped_and_a_peak_kept(self):
        ts = [f"2025-02-13T{h:02d}:00:00Z" for h in range(5)]
        d = pd.DataFrame({"ba": ["AZPS"] * 5, "ts_utc": ts, "demand": [5000.0, 5100.0, 10529.0, 5050.0, 5000.0]})
        self.assertNotIn(10529.0, authorities.despike(d, "demand")["demand"].tolist())
        d2 = d.copy()
        d2["demand"] = [5000.0, 5400.0, 5600.0, 5500.0, 5000.0]
        self.assertEqual(len(authorities.despike(d2, "demand")), 5)

    def test_a_utility_name_is_shortened_and_years_counted(self):
        self.assertEqual(large_load.short("Georgia Power Company"), "Georgia Power")
        self.assertEqual(large_load.short("Evergy Metro, Inc. d/b/a Evergy Missouri Metro"), "Evergy Metro")
        self.assertEqual(large_load.qty(1.0, "years", 0), "1 year")
        self.assertEqual(large_load.qty(10.0, "years", 0), "10 years")

    def test_a_claim_with_named_figures_is_checked(self):
        text = "# Expected figures: median 10.0; lowest 1.0; highest 15.0; filings 13.0; tolerance 0.5 percent of each.\nprint(1)\n"
        self.assertEqual(check.figures_of(text), {"median": 10.0, "lowest": 1.0, "highest": 15.0, "filings": 13.0})
        do = ('* Expected figures: median 10.0; tolerance 0.5 percent of each.\n\nclear all\n\nimport delimited "t.csv", varnames(1) stringcols(_all) clear\n\n'
              'destring value, replace force\n\nsummarize value, detail\n\ndisplay "median " r(p50)\n')
        self.assertEqual(check_do.problems(do, "# Expected figures: median 10.0; tolerance 0.5 percent of each.\n"), [])

    def test_every_generator_writes_a_do_file_that_holds(self):
        files = [regions.reproduce("winter_summer")("rd_car")["do"], regions.reproduce("coal_share")("st_se_cow")["do"], weather.reproduce("cold_ratio")("wx_tex")["do"],
                 weather.reproduce("winter_temp")("wt_ten")["do"], authorities.reproduce("ba_peak_mw")("ba_azps")["do"], authorities.reproduce("ba_coal_co2_share")("ba_erco")["do"]]
        for do in files:
            self.assertEqual([p for p in check_do.problems("* Expected: x\n\n" + do, "# Expected: x\n") if "expected" not in p], [])
        c = {"event": "elliott_2022", "code": "TEN", "a": "12-19", "b": "12-29", "how": "max"}
        self.assertEqual([p for p in check_do.problems("* Expected: x\n\n" + events.reproduce_do(c), "# Expected: x\n") if "expected" not in p], [])

    def test_the_state_groups_name_their_states(self):
        for code, (sts, words) in regions.STATES.items():
            self.assertTrue(sts)
            self.assertIn("EIA", words) if code in ("SE", "CAR", "NW", "SW") else None


if __name__ == "__main__":
    unittest.main()
