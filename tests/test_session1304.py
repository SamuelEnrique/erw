"""Session 1304 (chain 093): Ask's stored refusals classed from their tool records (warehouse/chat/eval/refusals.py).

Held here: docs/reviews/ask-refusals.md is what the stored runs give; each class is read from the record as its rule
says (a tool's MISO pause, a hold, the call limit of the run's day, rows read or not); and on the runs as they stand no
refusal read rows and still refused, none stopped at the call limit, and the two graded wrong are PJM's d10, a right
refusal graded on a cited table (session 320's ruling 3), not a fault of the loop.
No network, no model. Nothing here sets the environment at import.
"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def mod():
    if EVAL not in sys.path:
        sys.path.insert(0, EVAL)
    import refusals as F  # noqa: E402
    return F


class TheRefusals(unittest.TestCase):
    def test_the_file_is_what_the_runs_give(self):
        r = subprocess.run([sys.executable, os.path.join(EVAL, "refusals.py"), "--check"], capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])

    def test_the_classes_on_the_runs(self):
        rows = mod().refusals()
        by = {}
        for r in rows:
            by.setdefault(r["class"], []).append(r)
        self.assertEqual(sorted(by), ["lacks", "pause"])
        self.assertEqual(len(by["pause"]), 3)
        self.assertEqual(sorted((r["run"], r["id"]) for r in rows if r["right"] is False),
                         [("session 1113", "d10"), ("session 1149, first set", "d10")])

    def test_each_rule(self):
        F = mod()
        t = lambda tool, inp, out, err=False: {"tool": tool, "input": inp, "out": out, "isError": err}
        base = {"status": "not_in_warehouse", "answer": "Not in the warehouse.", "tool_calls": 2}
        self.assertEqual(F.classify(dict(base, trace=[t("query", {"table": "x"}, {"error": "MISO is paused while its terms are reviewed"}, True)]), "session 1113"), "pause")
        self.assertEqual(F.classify(dict(base, trace=[t("query", {"table": "x"}, {"held": True})]), "session 1113"), "held")
        self.assertEqual(F.classify(dict(base, tool_calls=12, trace=[t("list_tables", {}, {"tables": []})]), "session 1113"), "limit")
        self.assertEqual(F.classify(dict(base, tool_calls=8, trace=[t("list_tables", {}, {"tables": []})]), "session 302"), "limit")
        self.assertEqual(F.classify(dict(base, tool_calls=8, trace=[t("list_tables", {}, {"tables": []})]), "session 1113"), "lacks")
        self.assertEqual(F.classify(dict(base, trace=[t("query", {"table": "x", "aggregation": "mean"}, {"rows_matched": 30})]), "session 1113"), "read")
        self.assertEqual(F.classify(dict(base, trace=[t("query", {"table": "x", "aggregation": "count"}, {"rows_matched": 30})]), "session 1113"), "lacks")


if __name__ == "__main__":
    unittest.main()
