"""Audit of Automated Analysis, finding 9 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): "the week
before" when the week before was not held.

warehouse/analysis/run.py: change() pairs each held week with the previous HELD week, and a watch line drops a week
with too few rows, so the week compared with can be two weeks back. finding() wrote "the week before" whatever it was.
Since this session it names the week compared with when it is not the one just before; the adjacent case keeps "the
week before", and no figure or score changes. Fails on main, passes on the branch.

No table, no request, no model call; the environment is read, never set."""
import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


def wk(i):
    a = dt.date(2026, 1, 5) + dt.timedelta(weeks=i)
    return f"{a} to {a + dt.timedelta(days=6)}"


def headline(skip):
    hist = [(wk(i), 10.0 + (i % 3)) for i in range(20) if i != skip]
    return {"label": "a weekly mean", "unit": "u", "period": wk(20), "value": 20.0, "history": hist}


class WeekBefore(unittest.TestCase):
    def test_gap_names_the_week(self):
        import run
        h = headline(19)
        ch = run.change(h, "previous")
        self.assertEqual(ch["prev_period"], wk(18))
        one, _ = run.finding(h, ch, "previous")
        self.assertNotIn("the week before", one)
        self.assertIn(f"in the week of {wk(18)}", one)

    def test_adjacent_keeps_the_week_before(self):
        import run
        h = headline(5)
        ch = run.change(h, "previous")
        one, two = run.finding(h, ch, "previous")
        self.assertTrue(one.endswith("the week before."), one)
        self.assertTrue(two)

    def test_no_figure_moves(self):
        import run
        h = headline(19)
        ch = run.change(h, "previous")
        one, _ = run.finding(h, ch, "previous")
        self.assertIn("up 10 from 10", one)
        self.assertEqual(ch["score"], run.change(headline(19), "previous")["score"])

    def test_no_em_dash(self):
        for p in ("warehouse/analysis/run.py", "tests/test_audit_analysis_9.py"):
            with open(os.path.join(ROOT, p), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
