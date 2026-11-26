"""Session 10000 (chain 701, part C): the week's broken daily steps, each held at its cause.

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
