"""Session 10000 (chain 701, part C1): the daily load says "held", not "failed", when its guard is right to refuse.

From 21 November 2026 the daily load "failed" every day on datacenter_projects, energy_deals and news_index (the guard
of older_than_live refused them: Supabase holds rows loaded 13 November that no copy in the repository holds, and the
three are rebuilt only with a model call, closed while the key is at its limit) and on sources (one name in Supabase
that sources.csv no longer has, which only a person prunes). The guard stands; these tests hold the line between a
hold and a failure so that a real failure is never read as a hold.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))

import load  # noqa: E402

REFUSAL = RuntimeError("refused, older than the live copy: it has 583 rows here and 590 in Supabase (no retrieved_at "
                       "to compare); 1 rows differ in value, 7 only in Supabase.")


class TheGuardIsAHoldOnlyForAModelExtractedTable(unittest.TestCase):
    def test_a_model_extracted_table_refused_as_older_is_held(self):
        why = load.held_reason("energy_deals", REFUSAL, "model_extracted")
        self.assertIsNotNone(why)
        self.assertTrue(why.startswith("energy_deals: "))
        self.assertIn("guard stands", why)

    def test_a_table_built_from_a_source_refused_as_older_still_fails(self):
        self.assertIsNone(load.held_reason("ercot_rt_hub_prices", REFUSAL, "source"))
        self.assertIsNone(load.held_reason("price_years_by_window", REFUSAL, "derived"))
        self.assertIsNone(load.held_reason("anything", REFUSAL, None))

    def test_any_other_error_of_a_model_extracted_table_still_fails(self):
        self.assertIsNone(load.held_reason("news_index", RuntimeError("not in coverage.csv"), "model_extracted"))
        self.assertIsNone(load.held_reason("news_index", TimeoutError("canceling statement due to statement timeout"),
                                           "model_extracted"))


class TheSourcesCountIsAHoldOnlyWhenItDiffersByTheStaleNames(unittest.TestCase):
    STALE = ["IEA – International Energy Agency"]

    def test_one_stale_name_and_one_more_row_is_held(self):
        why = load.sources_held(767, 768, self.STALE, prune=False)
        self.assertIsNotNone(why)
        self.assertIn("only a person prunes", why)

    def test_a_count_that_differs_otherwise_still_fails(self):
        self.assertIsNone(load.sources_held(767, 770, self.STALE, prune=False))
        self.assertIsNone(load.sources_held(767, 766, [], prune=False))

    def test_a_prune_run_is_never_held(self):
        self.assertIsNone(load.sources_held(767, 768, self.STALE, prune=True))


class TheStepEndsAsASkipWhoseReasonSaysHeld(unittest.TestCase):
    def test_the_loader_ends_on_its_skip_line_with_the_skip_exit(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "load.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('print(f"supabase_load SKIPPED: held: ', src)
        self.assertEqual(load.GATE_SKIP, 75)
        # the daily script records a step whose output has "<name> SKIPPED" as skipped with its reason
        with open(os.path.join(ROOT, "warehouse", "run_daily.sh"), encoding="utf-8") as f:
            self.assertIn('grep -q "^${name} SKIPPED" "$out"', f.read())


if __name__ == "__main__":
    unittest.main()
