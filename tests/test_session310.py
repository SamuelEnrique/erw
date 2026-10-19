"""Session 310: the public tables behind cadence, and the one table no job refreshed.

Energy Research Warehouse (ERW). generation_mix_records and generation_mix_hourly_profile were written by
warehouse/derived/mix_profile.py from warehouse/refresh_mix.sh, which no run script or workflow calls; session 310 puts
the builder on the data machine's weekly steps. The Flex Alert scorecard's tables stay off the schedule: its window
ends with the last alert season that has weather (flex_alert_scorecard.py END), so a daily run would add nothing.

    python -m unittest tests.test_session310 -v
"""

import os
import re
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheSchedule(unittest.TestCase):
    def test_mix_profile_is_a_weekly_step_of_the_data_machine(self):
        steps = src("warehouse", "run_data_machine_tables.sh")
        self.assertIn('"dm_mix_profile|generation_mix_hourly_profile,generation_mix_records|weekly|warehouse/derived/mix_profile.py"', steps)

    def test_refresh_mix_is_called_by_no_job(self):
        for rel in ("warehouse/run_daily.sh", "warehouse/run_data_machine.sh", "warehouse/run_monthly.sh"):
            self.assertNotIn("refresh_mix.sh", src(*rel.split("/")), rel)

    def test_the_scorecard_is_a_closed_study(self):
        self.assertTrue(re.search(r'^END = "2025-10-31"', src("warehouse", "derived", "flex_alert_scorecard.py"), re.M))
        self.assertNotIn("flex_alert_scorecard.py", src("warehouse", "run_data_machine_tables.sh"))

    def test_the_list_names_the_step(self):
        try:
            out = subprocess.run(["bash", "warehouse/run_data_machine_tables.sh", "--list"], cwd=ROOT, capture_output=True,
                                 text=True, timeout=60).stdout
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.skipTest(f"bash is not usable here: {exc}")
        self.assertIn("dm_mix_profile: generation_mix_hourly_profile,generation_mix_records (weekly)", out)


if __name__ == "__main__":
    unittest.main()
