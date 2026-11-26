"""Session 10000 (chain 701, part C): the week's broken daily steps, each held at its cause.

- C2: the battery page's two downloads failed from 24 November: the runner builds battery_stack_monthly without ERCOT's
  price history, so 15 October 2026 (absent from the rolling table) was left out there and October held 29 days, while
  the downloads, solved here from the history, held 30. The data machine now builds and stores the stack before them.
- C4: from 21 November the data machine's live-set load failed every day with "coverage.csv is older than the tables it
  describes" (ercot_rtm_price_adders): this machine's commit was refused, so each morning's sync brought back main's
  older coverage row. Each live-set load of warehouse/run_data_machine_tables.sh now follows the coverage build of the
  same tables.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def text(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheStackIsBuiltHereBeforeTheBatteryDownloads(unittest.TestCase):
    def test_the_stack_and_its_stores_come_before_both_downloads(self):
        s = text("warehouse", "run_data_machine.sh")
        stack = s.index('soft_step dm_battery_stack "$PYTHON" warehouse/derived/battery_stack.py')
        stores = s.index('table_stores dm_battery_stack_stores battery_stack_monthly "$was_bs"')
        self.assertLess(s.index('was_bs="$(sha_of battery_stack_monthly)"'), stack)
        self.assertLess(stack, stores)
        self.assertLess(stores, s.index("soft_step dm_battery_dispatch_export"))
        self.assertLess(stores, s.index("soft_step dm_battery_scenario_steps"))

    def test_the_runner_keeps_a_month_whose_earlier_rows_held_more_days(self):
        s = text("warehouse", "derived", "battery_stack.py")
        self.assertIn("keep = [k for k in ho.index if k not in hn.index or ho[k] > hn[k]]", s)


class ACarriedLineTakesItsCountsFromItsRow(unittest.TestCase):
    """C5: the package's test of erw.info() failed every day from 23 November: coverage.csv held the carried
    ercot_all_hub_prices_history at 3,124,224 rows and docs/coverage.md at 3,125,376, each carried over apart."""

    LINE = ("| `ercot_all_hub_prices_history` | ERCOT | ercot_dam;ercot_rtm | spp_dam, spp_rtm | 6: HB_BUSAVG | PT15M;PT1H | "
            "2015-01-01 06:00:00 | 2026-11-21 05:00:00 | 3,125,376 | ercot:NP4-180-ER; ercot:NP4-190-CD | 2026-09-26 00:09:58 | "
            "pass | public | power | no | source | [iso_dam_hub_prices](methods/iso_dam_hub_prices.md) |")
    ROW = {"table": "ercot_all_hub_prices_history", "ts_min": "2015-01-01T06:00:00Z", "ts_max": "2026-11-19T05:45:00Z",
           "n_rows": "3124224", "last_run": "2026-09-26T00:09:58Z"}

    def test_the_rows_and_dates_follow_the_csv_row_and_nothing_else_moves(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_coverage", os.path.join(ROOT, "warehouse", "metadata", "build_coverage.py"))
        bc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bc)
        out = bc.align_carried(self.LINE, self.ROW)
        self.assertIn("| 3,124,224 |", out)
        self.assertIn("| 2026-11-19 05:45:00 |", out)
        self.assertNotIn("3,125,376", out)
        self.assertEqual(out.replace("3,124,224", "3,125,376").replace("2026-11-19 05:45:00", "2026-11-21 05:00:00"), self.LINE)

    def test_the_package_test_compares_info_with_coverage_csv(self):
        s = text("package", "tests", "test_erw.py")
        self.assertIn('assert d["n_rows"] == int(erw.coverage()["n_rows"].astype("int64").sum())', s)


class EveryLiveSetLoadFollowsItsCoverage(unittest.TestCase):
    def test_each_load_has_the_coverage_build_of_its_own_tables_just_before_it(self):
        lines = [ln.strip() for ln in text("warehouse", "run_data_machine_tables.sh").splitlines()]
        loads = [i for i, ln in enumerate(lines) if ln.startswith("soft_step dm_live_set") and "supabase/load.py" in ln]
        self.assertEqual(len(loads), 2)
        for i in loads:
            only = re.search(r'--only "(\$[A-Z_]+)"', lines[i]).group(1)
            before = lines[i - 1]
            self.assertTrue(before.startswith("soft_step dm_live_set"), before)
            self.assertIn("warehouse/metadata/build_coverage.py", before)
            self.assertIn(f'--only "{only}"', before)


if __name__ == "__main__":
    unittest.main()
