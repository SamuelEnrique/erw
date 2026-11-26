"""Audit of Automated Analysis, finding 12 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): a watch
line called the battery model "a model's upper bound".

warehouse/analysis/watch.py, watch_battery_model_ercot. The battery audit (docs/reviews/battery-model-audit-2026-11-20.md,
finding 6) shows the model's figure is not an upper bound: its empty start each day and its hourly energy hold it
8.3 percent under a foreseeing battery's. The title now says what the model is: perfect foresight, not an upper bound.
Words only: the line's table, variable, period and comparison are unchanged. Land with or after wip/audit-battery-6.
Fails on main, passes on the branch.

No table, no request, no model call; the environment is read, never set."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


class BatteryLineWords(unittest.TestCase):
    def line(self):
        import watch
        return next(L for L in watch.WATCH if L["name"] == "watch_battery_model_ercot")

    def test_title_does_not_claim_an_upper_bound(self):
        t = self.line()["title"]
        self.assertNotIn("upper bound)", t.replace("not an upper bound", ""))
        self.assertIn("perfect foresight", t)

    def test_the_measure_is_unchanged(self):
        L = self.line()
        self.assertEqual((L["table"], L["entity"], L["variable"], L["by"], L["how"], L["compare"], L["unit"]),
                         ("battery_stack_monthly", "ercot:HB_HUBAVG", "foresight_2h_revenue_total_usd_per_mw", "month", "last", "year", "USD/MW"))

    def test_no_em_dash(self):
        for p in ("warehouse/analysis/watch.py", "tests/test_audit_analysis_12.py"):
            with open(os.path.join(ROOT, p), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
