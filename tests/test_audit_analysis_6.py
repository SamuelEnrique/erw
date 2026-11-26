"""Audit of Automated Analysis, finding 6 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): the deep
hunt's drafts carry no step-or-trend flag and no round.

Session 361 gave the weekly hunt's drafts a statistics block (the trend's p, a Benjamini-Hochberg q over the round,
findings_common.step_or_trend), and the page prints "A step, not a trend" when a step fits better. The deep hunt's
builder (all forty of the sheet) calls none of them. The engine's own step_or_trend finds draft 33 (cooling degree days
in Texas, 2019 to 2024) a step: 12 of the forty's 37 yearly claims are (the audit's a8). Passes on main; carrying the
block would add a flag a reader sees: the owner's ruling.

No table, no request, no model call; the environment is read, never set."""
import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


def full_years(slug):
    with open(os.path.join(ROOT, "docs", "findings", slug + ".csv"), encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    rows = [r for r in csv.DictReader(lines) if str(r.get("full_year")) == "1"]
    return [int(float(r["year"])) for r in rows], [float(r["value"]) for r in rows]


class DeepDraftsWithoutTheirShape(unittest.TestCase):
    def test_builder_never_computes_the_block(self):
        with open(os.path.join(ROOT, "warehouse", "analysis", "findings", "deep", "builder.py"), encoding="utf-8") as f:
            t = f.read()
        for name in ("step_or_trend", "trend_p", "q_bh", '"statistics"'):
            self.assertNotIn(name, t)

    def test_draft_33_is_a_step_by_the_engines_own_rule(self):
        import findings_common as common
        ys, vs = full_years("weather/cdd-wd-tex")
        self.assertEqual(ys, [2019, 2020, 2021, 2022, 2023, 2024])
        sh = common.step_or_trend(ys, vs)
        self.assertTrue(sh["step_better"])
        self.assertEqual(int(sh["break_year"]), 2022)


if __name__ == "__main__":
    unittest.main()
