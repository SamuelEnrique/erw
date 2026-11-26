"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 6. Shows the
finding; not for landing (a rebuild moves figures: Samuel's ruling, default left as it is).

ai_power_regions was built on 2 October 2026 and is not in the daily run. Its "largest studied event" for each region
(event_largest_effect_pct) is read from event_study_estimates as that table stood then. On 19 October the event table
gained cold_2026 (January 2026), whose effect is the largest in every region but California: rebuilt today, ERCOT's
figure would read 31.15 percent of normal demand, not 8.78 (summer 2023 heat), PJM's 28.97 not 7.34, SPP's 26.29 not
6.14. The measure also ranks a temperature-controlled effect against effects controlled for day of week and year
alone (cold_2026 has no temperature-controlled estimate).

The data test reads both tables from ERW_AUDIT_OUTPUT (or warehouse/output) and is skipped where they are not held.
"""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUILDER = os.path.join(ROOT, "warehouse", "derived", "ai_power_regions.py")
OUT = os.environ.get("ERW_AUDIT_OUTPUT") or os.path.join(ROOT, "warehouse", "output")
HELD = all(os.path.exists(os.path.join(OUT, f"{t}.csv")) for t in ("ai_power_regions", "event_study_estimates"))


def rows(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


class TheLargestEventIsAsBuilt(unittest.TestCase):
    def test_the_builder_mixes_two_kinds_of_estimate(self):
        with open(BUILDER, encoding="utf-8") as f:
            s = f.read()
        self.assertIn('("demand_mwh_effect_pooled_temp", "demand_mwh_counterfactual_mean_temp") if "demand_mwh_effect_pooled_temp" in v else', s)
        self.assertIn('("demand_mwh_effect_pooled", "demand_mwh_counterfactual_mean")', s)

    def test_the_table_is_not_rebuilt_daily(self):
        with open(os.path.join(ROOT, "warehouse", "run_daily.sh"), encoding="utf-8") as f:
            self.assertNotIn("ai_power_regions", f.read())

    @unittest.skipUnless(HELD, "ai_power_regions or event_study_estimates not held here")
    def test_the_event_table_has_moved_since_the_build(self):
        table = {}
        for r in rows("ai_power_regions"):
            if r["variable"] == "event_largest_effect_pct":
                table[r["entity"].split(":")[1]] = float(r["value"])
        ev = {}
        for r in rows("event_study_estimates"):
            if r["event"] != "covid_2020":
                ev.setdefault((r["entity"], r["event"]), {})[r["variable"]] = float(r["value"])
        ba = {"caiso": "CISO", "ercot": "ERCO", "isone": "ISNE", "miso": "MISO", "nyiso": "NYIS", "pjm": "PJM", "spp": "SWPP"}
        moved = {}
        for reg, b in ba.items():
            best = None
            for (e, name), v in ev.items():
                if e != f"eia930:{b}":
                    continue
                eff, cf = ("demand_mwh_effect_pooled_temp", "demand_mwh_counterfactual_mean_temp") if "demand_mwh_effect_pooled_temp" in v else ("demand_mwh_effect_pooled", "demand_mwh_counterfactual_mean")
                if eff in v and cf in v:
                    pct = v[eff] / v[cf] * 100
                    if best is None or abs(pct) > abs(best):
                        best = pct
            if best is not None and reg in table and abs(best - table[reg]) > 0.01:
                moved[reg] = (table[reg], round(best, 2))
        if not any(name == "cold_2026" for (_, name) in ev):
            self.skipTest("the held event table has no cold_2026")
        self.assertIn("ercot", moved)
        self.assertGreater(moved["ercot"][1], 30)


if __name__ == "__main__":
    unittest.main()
