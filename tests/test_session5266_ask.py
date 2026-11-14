"""Session 5266 (chain 256): the measure of the calls made after the figure is in hand.

Energy Research Warehouse (ERW). warehouse/chat/eval/calls_after.py reads the stored runs of the platform set and puts
each tool call made after the first result that held the key's figure in one class (a count of the same window, the
same rows grouped another way, another query of the same table, another table, compare, describe, list, a refused call,
a call the loop counted and did not make). No model, no network.

Held here: the classes on made records; and on the stored runs, what must be true whatever the keys of the day are
(every call after the figure is in one class, the figure is in hand no later than the loop's count, the session filter
reads only the runs named). The counts of 14 November 2026 are written in docs/reviews/ask-eval-2026-11-13.md with
their date, not pinned here: a key that moves with the live set moves them.
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def module(name):
    spec = importlib.util.spec_from_file_location(f"{name}_for_test_5266", os.path.join(EVAL, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def call(tool, out=None, error=False, **args):
    return {"tool": tool, "input": args, "out": out or {}, "isError": error}


FIGURE = call("query", table="iso_dam_hub_prices", aggregation="mean", entity="ercot:HB_HUBAVG", start="2026-11-10", end="2026-11-11")


class TheClasses(unittest.TestCase):
    def setUp(self):
        self.C = module("calls_after")

    def of(self, c):
        return self.C.class_of(c, FIGURE)

    def test_each_class(self):
        same = dict(table="iso_dam_hub_prices", entity="ercot:HB_HUBAVG", start="2026-11-10", end="2026-11-11")
        self.assertEqual(self.of(call("query", aggregation="count", **same)), "count_window")
        self.assertEqual(self.of(call("query", aggregation="mean", group_by="hour", **same)), "regroup")
        self.assertEqual(self.of(call("query", aggregation="max", **same)), "same_table")
        self.assertEqual(self.of(call("query", aggregation="mean", **{**same, "tz": "America/Chicago"})), "same_table")
        self.assertEqual(self.of(call("query", table="iso_rtm_hub_prices", aggregation="mean")), "other_table")
        self.assertEqual(self.of(call("compare", a={}, b={})), "compare")
        self.assertEqual(self.of(call("describe_table", table="iso_dam_hub_prices")), "describe")
        self.assertEqual(self.of(call("list_tables")), "list")
        self.assertEqual(self.of(call("grid_notes", grid="ercot")), "other")

    def test_a_refused_call_is_refused_whatever_it_asked(self):
        self.assertEqual(self.of(call("query", error=True, table="iso_dam_hub_prices", aggregation="count")), "refused")
        self.assertEqual(self.of({"tool": "query", "input": {"table": "x"}, "is_error": True}), "refused")

    def test_a_count_after_a_count_is_not_a_check_of_the_window(self):
        counted = call("query", table="large_load_public", aggregation="count", group_by="status")
        self.assertEqual(self.C.class_of(call("query", table="large_load_public", aggregation="count", group_by="stage_class"), counted), "regroup")
        self.assertEqual(self.C.class_of(call("query", table="large_load_public", aggregation="count", where={"status": "x"}, group_by="status"), counted), "same_table")

    def test_a_figure_first_held_by_a_compare_makes_every_later_query_another_table(self):
        self.assertEqual(self.C.class_of(call("query", table="iso_dam_hub_prices", aggregation="count"), call("compare", a={}, b={})), "other_table")

    def test_the_calls_the_loop_counted_and_did_not_make(self):
        q = {"id": "x01", "kind": "figure", "expected": [1.0], "tolerance": 0.01}
        rec = {"id": "x01", "status": "answered", "tool_calls": 5, "trace": [call("list_tables"), FIGURE, call("query", table="iso_dam_hub_prices", aggregation="count")]}
        m = self.C.after(q, rec, lambda q, rec: 2)
        self.assertEqual(m, {"at": 2, "calls": 5, "after": ["count_window", "not_made", "not_made"]})
        self.assertIsNone(self.C.after(q, rec, lambda q, rec: None))        # the figure in no result: not measured

    def test_the_measure_adds_up_and_reads_only_the_sessions_named(self):
        qs = [{"id": "a", "kind": "figure"}, {"id": "b", "kind": "figure"}, {"id": "c", "kind": "outside"}]
        old = {"id": "a", "status": "answered", "tool_calls": 3, "cost_usd": 0.1, "trace": [call("list_tables"), FIGURE, call("list_tables")]}
        new = {"id": "a", "status": "answered", "tool_calls": 2, "cost_usd": 0.05, "trace": [call("list_tables"), FIGURE]}
        b = {"id": "b", "status": "not_in_warehouse", "tool_calls": 1, "trace": [call("list_tables")]}
        c = {"id": "c", "status": "answered", "tool_calls": 4, "trace": [FIGURE]}
        runs = [("5251", [old, b, c], {}, []), ("5270", [new], {}, [])]
        at2 = lambda q, rec: 2  # noqa: E731
        m = self.C.measure(qs, runs, at2)
        self.assertEqual((m["questions"], m["calls"], m["calls_after"]), (1, 2, 0))          # a's newest answer; b refused; c not a figure key
        first = self.C.measure(qs, runs, at2, sessions={"5251"})
        self.assertEqual((first["questions"], first["calls"], first["calls_after"], first["by_class"]["list"]), (1, 3, 1, 1))
        self.assertEqual(sum(first["by_class"].values()), first["calls_after"])
        self.assertEqual(self.C.measure(qs, runs, at2, ids={"b"})["questions"], 0)
        self.assertIn("| list | 1 | 1 |", "\n".join(self.C.lines(first)))


class TheStoredRuns(unittest.TestCase):
    def test_every_call_after_the_figure_is_in_one_class_and_the_figure_comes_no_later_than_the_count(self):
        C, S, E, P = module("calls_after"), module("eval_site"), module("eval_s1113"), module("platform_scores")
        qs, runs = P.load(S, E)
        m = C.measure(qs, runs, lambda q, rec: P.in_hand(q, rec, E.G), sessions={str(n) for n in range(5251, 5263)})
        self.assertGreater(m["questions"], 0)
        self.assertEqual(sum(m["by_class"].values()), m["calls_after"])
        for r in m["rows"]:
            self.assertLessEqual(r["at"], r["calls"], r["id"])
            self.assertEqual(len(r["after"]), r["calls"] - r["at"], r["id"])       # recorded later calls and the ones not made
            self.assertTrue(set(r["after"]) <= set(C.CLASSES), r["id"])
        self.assertEqual({r["session"] for r in m["rows"]} - {str(n) for n in range(5251, 5263)}, set())


if __name__ == "__main__":
    unittest.main()
