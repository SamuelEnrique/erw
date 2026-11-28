"""wip/ready-reports-events (session 11406, chain 770, part C): the other choice of the reports audit of 26 November,
finding 6 (docs/reviews/reports-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main ai_power_regions' largest studied event (event_largest_effect_pct, the AI gigawatts draft's table) was built
on 2 October, before cold_2026 joined event_study_estimates, and mixes two kinds of estimate (temperature-controlled
where held, else day-of-week and year). On this branch the builder takes the day-of-week and year estimate for every
event, the one kind every event holds, and the table is rebuilt at landing by the desk. This test runs the builder's
events() on the event studies held here (ERW_AUDIT_OUTPUT, this worktree's warehouse/output, or the main copy's, read
only) and prints each region's largest event before (main's rule) and after; the audit measured, with main's mixed rule
on a rebuild, ERCOT 8.78 to 31.15, PJM 7.34 to 28.97, SPP 6.14 to 26.29, MISO 7.28 to 22.96, ISO-NE 1.15 to 19.36,
NYISO 1.38 to 17.31, CAISO 3.15 unchanged."""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def held_dir():
    for d in (os.environ.get("ERW_AUDIT_OUTPUT"), os.path.join(ROOT, "warehouse", "output"), os.path.join(ROOT, "..", "erw", "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, "event_study_estimates.csv")):
            return d
    return None


def main_rule(es, regions):
    out = {}
    for r, (ba, *_rest) in regions.items():
        g = es[(es["entity"] == f"eia930:{ba}") & (es["event"] != "covid_2020")]
        best = None
        for ev, e in g.groupby("event"):
            v = e.set_index("variable")["value"]
            eff, cf = ("demand_mwh_effect_pooled_temp", "demand_mwh_counterfactual_mean_temp") if "demand_mwh_effect_pooled_temp" in v else \
                ("demand_mwh_effect_pooled", "demand_mwh_counterfactual_mean")
            if eff in v and cf in v:
                pct = float(v[eff]) / float(v[cf]) * 100
                if best is None or abs(pct) > abs(best[0]):
                    best = (pct, ev)
        if best:
            out[r] = best
    return out


class OneKindOfEstimate(unittest.TestCase):
    def test_the_builder_takes_one_kind(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "ai_power_regions.py"), encoding="utf-8") as f:
            s = f.read()
        body = s[s.index("def events():"):s.index("return out", s.index("def events():"))]
        self.assertIn('eff, cf = ("demand_mwh_effect_pooled", "demand_mwh_counterfactual_mean")', body)
        self.assertNotIn('"demand_mwh_effect_pooled_temp" in v else', body)

    def test_before_and_after_on_the_held_event_studies(self):
        d = held_dir()
        if not d:
            self.skipTest("event_study_estimates is not held here")
        try:
            import ai_power_regions as apr
        except Exception as exc:
            self.skipTest(f"ai_power_regions does not import here: {exc}")
        path = os.path.join(d, "event_study_estimates.csv")
        saved = apr.read

        def read(name, usecols=None):
            with open(path, encoding="utf-8") as f:
                n = sum(1 for ln in f if ln.startswith("#"))
            return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, usecols=usecols)
        apr.read = read
        try:
            after = apr.events()
            es = read("event_study_estimates", ["entity", "variable", "ts_utc", "value", "event"])
        finally:
            apr.read = saved
        before = main_rule(es, apr.REGIONS)
        lines = [f"{r}: {before[r][0]:.2f} ({before[r][1]}) to {after[r]['event_largest_effect_pct']:.2f} ({after[r]['_event_id']})" for r in sorted(after) if r in before]
        print("largest studied event, before to after: " + "; ".join(lines))
        self.assertTrue(lines)
        self.assertTrue(all("day-of-week and year" in a["_note_event"] for a in after.values()))


if __name__ == "__main__":
    unittest.main()
