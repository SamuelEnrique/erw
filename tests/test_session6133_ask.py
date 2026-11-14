"""Session 6133 (chain 281): the loop names a table of the record the chat cannot read.

Energy Research Warehouse (ERW).

The week's new tables are in no copy a visitor's chat reads. Three questions about them were asked three times through
the site's loop as the tools' words were mended (sessions 6113, 6132, 6133): USD 0.67, 0.49, 0.38, every refusal right,
and two of three still read "I found no table of forecast-tool parameters" or leaned on a neighbour table, where the
ERW's record holds the table by that very name. When a question's own words hold every word of the name of a table of
the record that the list did not show, and the refusal does not name that table, both loops now say what it is, before
the model's own sentence.

No model, no network.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import ask  # noqa: E402
import tools  # noqa: E402

with open(os.path.join(ROOT, "tests", "fixtures", "session6133", "unlisted.json"), encoding="utf-8") as _f:
    FX = json.load(_f)


def python_side():
    return {"named": {q["id"]: ask.unlisted_named(q["question"], FX["names"]) for q in FX["questions"]},
            "said": {a["id"]: ask.with_unlisted_words(a["answer"], a["tables"], FX["verdicts"].get) for a in FX["answers"]},
            "lists": {r["id"]: ask.unlisted_tables(r["records"], FX["names"]) for r in FX["records"]}}


class TheTableTheQuestionNames(unittest.TestCase):
    def test_each_case_of_the_fixture(self):
        got = python_side()
        for q in FX["questions"]:
            self.assertEqual(got["named"][q["id"]], q["named"], q["id"])
        for a in FX["answers"]:
            self.assertEqual(got["said"][a["id"]], a["said"], a["id"])
        for r in FX["records"]:
            self.assertEqual(got["lists"][r["id"]], r["unlisted"], r["id"])

    def test_the_site_returns_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "scripts/test-ask-6133.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
        self.assertEqual(json.loads(next(x for x in r.stdout.splitlines() if x.startswith("{"))), python_side())

    def test_only_a_refusal_of_the_general_chat_and_only_over_the_live_set(self):
        py = open(os.path.join(ROOT, "warehouse", "chat", "ask.py"), encoding="utf-8").read()
        self.assertIn("if tools.live_only():\n                        # session 6133", py)
        # session 6166: against what the catalogue lists (known at the first list, whatever its filter), else what a whole list showed
        self.assertIn("named = unlisted_named(question, unlisted if unlisted is not None else unlisted_tables(results, tools.verdicts()))", py)
        ts = open(os.path.join(SITE, "lib", "chat", "ask.ts"), encoding="utf-8").read().replace("\r\n", "\n")
        self.assertIn("if (!profile && draft.not_in_warehouse) {\n      const verdicts = verdictFile as unknown as Record<string, [string, string]>;", ts)
        self.assertIn("const named = unlistedNamed(question, unlisted ?? unlistedTables(lists, Object.keys(verdicts)));", ts)

    def test_the_record_names_the_weeks_tables(self):
        v = tools.verdicts()
        for t in ("utility_large_load_rules", "utility_large_load_rule_changes", "state_large_load_laws", "forecast_tool_parameters"):
            self.assertIn(t, v)
        self.assertGreater(len(v), 400)

    def test_the_three_askings_of_the_three(self):
        """What the mends bought, from the stored runs: the same three questions, sessions 6113, 6132 and 6133."""
        eval_dir = os.path.join(ROOT, "warehouse", "chat", "eval")
        calls, cost = [], []
        for s in ("6113", "6132", "6133"):
            with open(os.path.join(eval_dir, f"eval_s{s}_site_newtables_live_run.json"), encoding="utf-8") as f:
                qs = {q["id"]: q for q in json.load(f)["questions"]}
            self.assertTrue(all(qs[i]["status"] == "not_in_warehouse" for i in ("ru07", "ru09", "fc06")), s)
            calls.append(sum(qs[i]["tool_calls"] for i in ("ru07", "ru09", "fc06")))
            cost.append(round(sum(qs[i]["cost_usd"] for i in ("ru07", "ru09", "fc06")), 2))
        self.assertEqual(calls, [36, 23, 15])
        self.assertEqual(cost, [0.67, 0.49, 0.38])


if __name__ == "__main__":
    unittest.main()
