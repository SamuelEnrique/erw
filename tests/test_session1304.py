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
        # session 5251 (chain 238): the platform set's runs through the site's loop come one a session, with refusals of their own
        # (tests/test_session5251_ask.py holds them); the counts below are the other sets'
        rows = [r for r in mod().refusals() if "the platform set" not in r["run"]]
        by = {}
        for r in rows:
            by.setdefault(r["class"], []).append(r)
        # session 3282: the call limit's first refusal, iv14 asked again (twelve calls, the durations table never listed)
        # sessions 6108 to 6113 (chain 280): the investor's and the lab's twenty through the site's loop and the new tables' set bring
        # three classes more: checked (iv14, the fixed refusal over a percentile's name, since mended), not_live (iv18) and read
        # (five refusals of the new tables' set that had read a figure of something else on the way)
        self.assertEqual(sorted(by), ["checked", "held", "lacks", "limit", "not_live", "pause", "read"])   # session 2224 (chain 152): the twenty's four questions of tables held whole
        self.assertEqual(len(by["held"]), 56)   # session 6167: the investor's six held questions again, 50 before. Sessions 6165 and 6166 (chain 282): NYISO's load queue twice and a refusal that touched a held table, 47 before. Sessions 6132 to 6141 (chain 281): 13 more (the visitor's set and the two twenties asked again), 34 before. Sessions 6108 to 6113: 20 more (the two sets' held tables, asked and asked again; ru07 and ru09 of the visitor's slice), 14 before. Session 2968 (chain 157): the weekly twenty's l01 to l04 again; session 3281: iv01 to iv05
        self.assertEqual(len(by["pause"]), 15)   # sessions 6137 and 6138: tr20 and l10 asked again under rule 12, 13 before. Session 6109: the lab's l10 through the site's loop, 12 before. Session 5275 (chain 256): the trader's tr20 through the site's loop, 11 before. Session 3769 (chain 211): the thirty's g10 again; session 2221 (chain 152): the Python loop's g10; session 2968: its g10 and l10; session 3280: tr20
        # sessions 6134 and 6135 (chain 281): five more refusals of the visitor's set at twelve calls, before the list named the
        # table (9 in all; none since session 6136). not_live: the refusals of a table of the record the site cannot read are of
        # this class once the tools name it so (6, of which 5 this chain's). read: two more that had read a neighbour table (7)
        self.assertEqual(len(by["limit"]), 11)   # sessions 6168 and 6169: two refusals of the new tables' set at twelve calls through the Python loop, 9 before. Sessions 6111 to 6113: fc19, ru12 and the visitor's fc06 at twelve calls, 4 then; 1 before
        self.assertEqual((len(by["checked"]), len(by["not_live"]), len(by["read"])), (1, 9, 14))   # sessions 6167 to 6170: (1, 8, 8) before; sessions 6165 and 6166: (1, 6, 7) before
        inv, again = "session 3281, Python loop, the investor's twenty", "session 3282, Python loop, the investor's iv13 to iv15 again"
        self.assertEqual(sorted((r["run"], r["id"]) for r in rows if r["right"] is False),
                         [("session 1113", "d10"), ("session 1149, first set", "d10"), ("session 2221, Python loop", "d10"), ("session 2222, Python loop", "d10"),
                          (inv, "iv13"), (inv, "iv14"), (inv, "iv15"), (again, "iv14"),
                          # session 6108: iv14 through the site's loop (the percentile's name); session 6109: l02 (cut in mid-sentence); both mended and right when asked again
                          ("session 6108, the site's loop, the investor set", "iv14"), ("session 6109, the site's loop, the s2224 set", "l02")])   # session 3281: the months to operation refused, the durations table unlisted

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
