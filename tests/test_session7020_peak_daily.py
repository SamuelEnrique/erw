"""Session 7020 (chain 301): the ERCOT peak premium is rebuilt each day on the data machine, after the day's hub rows.
Only the GitHub run called its builder, and there it always skipped for want of the hub history, so the two tables
stood at 21 October until 16 November. The builder's --split splits the two consolidated families, builds, and builds
them back. No request, no model call."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheDailyStep(unittest.TestCase):
    def test_after_the_hub_rows_and_loaded_daily(self):
        t = src("warehouse", "run_data_machine_tables.sh")
        step = '"dm_peak_premium|ercot_peak_premium_annual,ercot_peak_premium_monthly|daily|warehouse/derived/ercot_peak_premium.py --split"'
        self.assertIn(step, t)
        self.assertLess(t.index('"dm_ercot_hub_append|'), t.index(step))
        live = [ln for ln in t.splitlines() if ln.startswith("LIVE_ONLY=")][0]
        self.assertIn("ercot_peak_premium_annual|ercot_peak_premium_monthly", live)

    def test_split_builds_the_families_back_whatever_the_metrics_did(self):
        s = src("warehouse", "derived", "ercot_peak_premium.py")
        self.assertIn('FAMILIES = ("ercot_all_hub_prices_history", "iso_rtm_hub_prices")', s)
        body = s[s.index("def main_split():"):s.index("def main():")]
        self.assertLess(body.index('cons + ["split"] + fam'), body.index("rc = main()"))
        self.assertIn("finally:", body)
        self.assertIn('back = subprocess.run(cons + ["build"] + fam', body)
        self.assertIn('main_split() if "--split" in sys.argv[1:] else main()', s)


if __name__ == "__main__":
    unittest.main()
