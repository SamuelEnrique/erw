"""Session 308: the rulings of 14 October at the owner's defaults of 18 October.

Energy Research Warehouse (ERW). The hunt's two rules (ruling 8), the late-January 2026 cold window (ruling 6) and the
Batch Zero deck's two figures (ruling 4). The tables are read where this machine holds them; a test skips where it
does not. The rows of the hunt tests are fixtures, not data values.

    python -m unittest tests.test_session308 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
OUT = os.path.join(ROOT, "warehouse", "output")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheHuntsRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import hunt
        except Exception as exc:  # the hunt imports the findings' modules
            raise unittest.SkipTest(f"hunt.py does not import here: {exc}")
        cls.h = hunt

    def test_the_reserve_adder_has_ended(self):
        self.assertIn("scarcity_hours", self.h.ENDED)
        self.assertEqual(self.h.ENDED["scarcity_hours"][0], "2025-12-04")
        self.assertIn("4 December 2025", src("docs", "methods", "ercot_rt_price_adders.md"))

    def test_negative_hours_by_hub_and_by_zone_are_one_story_over_the_same_years(self):
        k = self.h.fold_key
        self.assertEqual(k("negative_prices", "ercot_south", 2015, 2025), k("negative_hours_zones", "ercot_LZ_HOUSTON", "2015", "2025"))
        self.assertNotEqual(k("negative_prices", "ercot_south", 2015, 2025), k("negative_prices", "ercot_south", 2016, 2025))
        self.assertNotEqual(k("negative_prices", "ercot_south", 2015, 2025), k("negative_prices", "caiso_sp15", 2015, 2025))

    def test_a_part_of_the_day_is_its_own_story(self):
        k = self.h.fold_key
        self.assertEqual(k("da_rt_spread", "ercot_HB_WEST_evening", 2015, 2025), k("da_rt_spread", "ercot_HB_NORTH_evening", 2015, 2025))
        self.assertNotEqual(k("da_rt_spread", "ercot_HB_WEST_late", 2015, 2025), k("da_rt_spread", "ercot_HB_NORTH_evening", 2015, 2025))

    def test_the_list_is_read_from_the_memory(self):
        state = {"negative_prices|ercot_south": {"first_year": "2015", "last_year": "2025", "change": 1.0}}
        got = self.h.listed_stories(state)
        self.assertEqual(got[self.h.fold_key("negative_hours_zones", "ercot_LZ_WEST", 2015, 2025)], "negative_prices|ercot_south")


class TheFoldInAHunt(unittest.TestCase):
    def test_two_regions_of_one_grid_over_one_span_are_one_draft(self):
        import datetime as dt
        import tempfile
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import test_session233 as t233   # session 233's fixture: its pattern template and series
        hunt = t233.hunt
        saved = (hunt.PATTERNS, hunt.run_pattern)
        try:
            with tempfile.TemporaryDirectory() as d:
                def run_pattern(Pn, in_dir, this_year, blocked, log=print, compute=None):
                    out = []
                    for region, values in (("ercot_a", [1.0, 2.0, 3.0, 4.0, 5.0, 9.0]), ("ercot_b", [1.0, 2.0, 3.0, 4.0, 5.0, 12.0])):
                        sr = t233.series(values)
                        out.append((region, region, sr, hunt.test_claim(sr, Pn, this_year), None, {}, ["ercot_all_hub_prices_history"]))
                    return out
                hunt.PATTERNS, hunt.run_pattern = [dict(t233.P, name="one")], run_pattern
                s = hunt.hunt(in_dir=d, log=lambda m: None, now=dt.datetime(2026, 10, 17, tzinfo=dt.timezone.utc),
                              state_path=os.path.join(d, "state.json"), out_root=d, load=lambda drafts, log: [x["id"] for x in drafts])
                by = {r["key"]: r for r in s["results"]}
                self.assertTrue(by["one|ercot_b"]["drafted"])
                self.assertEqual(by["one|ercot_a"].get("folded_into"), "one|ercot_b")
                self.assertIn("folded into one|ercot_b", by["one|ercot_a"]["reason"])
                self.assertEqual(s["drafts"], 1)
        finally:
            hunt.PATTERNS, hunt.run_pattern = saved


class TheColdWindow(unittest.TestCase):
    def test_the_window_is_the_same_in_every_list(self):
        import event_window as ew
        import event_study as es
        self.assertEqual((ew.COLD_2026["start"], ew.COLD_2026["end"]), es.WINDOWS["cold_2026"])
        self.assertEqual(ew.COLD_2026["offsets"], [364, 728])
        self.assertIn('cold_2026: ["2026-01-23", "2026-02-02"]', src("site", "lib", "eventstudy.ts"))
        self.assertIn("cold_2026", src("notebooks", "event_study.ipynb"))

    def test_the_table_holds_it(self):
        path = os.path.join(OUT, "event_window_daily.csv")
        if not os.path.exists(path):
            self.skipTest("event_window_daily is not on this machine")
        t = pd.read_csv(path, comment="#", dtype=str, keep_default_na=False, usecols=["event", "ts_utc"])
        c = t[t["event"] == "cold_2026"]
        self.assertGreater(len(c), 0)
        self.assertEqual(c["ts_utc"].str[:4].isin(["2024", "2025", "2026"]).all(), True)


class TheBatchZeroFigures(unittest.TestCase):
    def test_the_two_figures_with_their_sentences(self):
        path = os.path.join(OUT, "large_load_statements.csv")
        if not os.path.exists(path):
            self.skipTest("large_load_statements is not on this machine")
        t = pd.read_csv(path, comment="#", dtype=str, keep_default_na=False)
        z = t[t["collected_in"] == "pass S308"]
        self.assertEqual(sorted(z["sentence"]), ["17 large loads (6,608 MW total peak demand over 5 years)",
                                                 "April snapshot had 157 medium data center and crypto loads totaling approximately 8,766 MW"])
        self.assertEqual(set(z["source_url"]), {"https://www.ercot.com/files/docs/2026/08/25/10.-Large-Load-Issues.zip"})


class NoDashes(unittest.TestCase):
    def test_no_em_dash(self):
        for rel in ("tests/test_session308.py", "warehouse/analysis/findings/hunt.py", "warehouse/derived/event_window.py",
                    "docs/methods/events.md", "warehouse/connectors/large_load_statements.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
