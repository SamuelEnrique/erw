"""Session 6111 (chain 280): the chat on the tables that landed in the week of 9 November 2026.

Energy Research Warehouse (ERW).

What is held here, with no model and no network:

  the set       warehouse/chat/eval/questions_newtables.yaml: at least 40 questions drawn from the new tables, each key
                computed from the table's own file by scripts/ask_eval/newtables_questions.py; questions the chat must
                refuse among them. Where the tables' files are on the machine, the keys on disk are what they give.
  the grade     a key of kind unstated (the cell says the documents read do not state the thing) is met by an answer
                that says so and gives no figure, as a refusal or as an answer (eval_s1113.py unstated_grade).
  the runner    eval_loop.py --data-dir asks over a folder of table files (the erw package's local backend): the live
                set does not hold these tables yet.
  the tools     describe_table names a column of prose and does not list it, in both loops (tools.py split_long_text,
                site/lib/chat/longtext.ts splitLongText): describing a large-load table returned 80 to 90 KB.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import tools  # noqa: E402


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def questions():
    import yaml
    with open(os.path.join(EVAL, "questions_newtables.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)["questions"]


def data_dir():
    """The folder that holds the new tables' files on this machine, or None (GitHub's runner holds no warehouse data)."""
    for d in (os.environ.get("ERW_DATA_DIR"), os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")):
        if d and all(os.path.exists(os.path.join(d, t + ".csv")) for t in ("utility_large_load_rules", "state_large_load_laws", "forecast_tool_parameters",
                                                                            "utility_large_load_rule_changes", "deal_counterparties", "iso_reserve_margin_reports")):
            return d
    return None


class TheSet(unittest.TestCase):
    def test_at_least_forty_with_refusals_among_them(self):
        qs = questions()
        self.assertGreaterEqual(len(qs), 40)
        kinds = {k: sum(1 for q in qs if q["kind"] == k) for k in ("figure", "outside", "unstated")}
        self.assertEqual(sum(kinds.values()), len(qs))
        self.assertGreaterEqual(kinds["outside"] + kinds["unstated"], 10, "questions the chat must refuse")
        self.assertEqual(len({q["id"] for q in qs}), len(qs))

    def test_every_named_table_is_asked_about(self):
        qs = questions()
        by = {s: sum(1 for q in qs if q["sector"] == s) for s in ("rules", "changes", "laws", "forecast")}
        for sector, n in by.items():
            self.assertGreaterEqual(n, 10, sector)

    def test_a_key_is_a_figure_a_word_or_a_refusal_never_both(self):
        for q in questions():
            if q["kind"] == "figure":
                self.assertTrue(q["expected"] or q["text"], q["id"])
                self.assertFalse(q["refuse"], q["id"])
                self.assertEqual(len(q["tables"]), 1, q["id"])
            elif q["kind"] == "outside":
                self.assertEqual((q["expected"], q["refuse"]), ([], True), q["id"])
                self.assertEqual(q["text"][0], "not in the warehouse", q["id"])
            else:
                self.assertEqual((q["expected"], q["refuse"]), ([], False), q["id"])
                self.assertIn("not published", q["text"][0], q["id"])

    def test_the_set_is_one_of_the_evaluations_sets(self):
        E = module("eval_s1113_for_6111", os.path.join(EVAL, "eval_s1113.py"))
        self.assertEqual(os.path.basename(E.SETS["newtables"]["questions"]), "questions_newtables.yaml")
        self.assertEqual(len(E.questions(E.SETS["newtables"]["questions"])), len(questions()))

    def test_no_dash_in_the_set(self):
        with open(os.path.join(EVAL, "questions_newtables.yaml"), encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn(chr(0x2014), text)
        self.assertNotIn(chr(0x2013), text)

    def test_the_keys_are_the_tables_where_the_tables_are(self):
        if not data_dir():
            raise unittest.SkipTest("the new tables' files are not on this machine (scripts/sync.py restores them)")
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(ROOT, "scripts", "ask_eval", "newtables_questions.py"), "--check"],
                           capture_output=True, text=True, timeout=600, env={**os.environ, "ERW_DATA_DIR": data_dir()})
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])


class AnUnstatedCell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.E = module("eval_s1113_for_6111_grade", os.path.join(EVAL, "eval_s1113.py"))
        cls.key = {"text": ["not published|not state|not stated|no figure|not in the warehouse"]}

    def grade(self, answer):
        return self.E.unstated_grade(self.key, {"answer": answer})

    def test_said_as_an_answer_or_as_a_refusal(self):
        self.assertTrue(self.grade("The table says the queue size is not published for Duke Energy Carolinas (utility_large_load_rules).")["ok"])
        self.assertTrue(self.grade("Not in the warehouse. The documents the table read do not state a queue size.")["ok"])

    def test_a_figure_beside_the_words_is_wrong(self):
        self.assertFalse(self.grade("Not published, though news reports put the pipeline at 15.4 GW.")["ok"])
        self.assertFalse(self.grade("The queue size is not published; the rule applies from 100 MW.")["ok"])
        self.assertFalse(self.grade("Not published. Other utilities list 12,500 in theirs.")["ok"])

    def test_without_the_words_it_is_wrong(self):
        self.assertFalse(self.grade("Duke Energy Carolinas has a large queue.")["ok"])

    def test_a_year_and_a_day_are_not_figures(self):
        self.assertTrue(self.grade("Not published: the settlement of 6 October 2026 states no queue size.")["ok"])


class AFolderOfTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.L = module("eval_loop_for_6111", os.path.join(EVAL, "eval_loop.py"))

    def test_the_live_set_is_the_default(self):
        env = {}
        self.assertEqual(self.L.set_backend(["--session", "1"], env), "supabase")
        self.assertEqual(env, {"ERW_BACKEND": "supabase"})
        self.assertEqual(self.L.backend_words(env), "the Supabase live set as the backend")

    def test_a_folder_is_read_through_the_local_backend(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            data, meta = os.path.join(d, "data"), os.path.join(d, "metadata")
            os.makedirs(data)
            os.makedirs(meta)
            cov = os.path.join(meta, "coverage.csv")
            open(cov, "w").close()
            env = {}
            self.assertEqual(self.L.set_backend(["--data-dir", data], env), "local")
            self.assertEqual(env, {"ERW_BACKEND": "local", "ERW_DATA_DIR": os.path.abspath(data), "ERW_COVERAGE_CSV": os.path.abspath(cov)})
            self.assertIn("the table files of", self.L.backend_words(env))
            self.assertNotIn("live set as the backend", self.L.backend_words(env))

    def test_a_folder_that_is_not_there_stops_the_asking(self):
        with self.assertRaises(SystemExit):
            self.L.set_backend(["--data-dir", os.path.join(ROOT, "no", "such", "folder")], {})


class AColumnOfProse(unittest.TestCase):
    def test_a_value_over_200_characters_makes_the_column_prose(self):
        clause = "The minimum initial contract term for ESAs below 100 MW will be the greater of (a) 10 years and (b) 5 years plus the load ramp period. " * 2
        short, long = tools.split_long_text({"status": {"approved": 21, "proposed": 25}, "x_state": {"NC": 2}, "x_contract_term": {clause: 1, "not published": 3}})
        self.assertEqual(short, {"status": {"approved": 21, "proposed": 25}, "x_state": {"NC": 2}})
        self.assertEqual(long, {"x_contract_term": {"distinct": 2, "longest_chars": len(clause)}})

    def test_exactly_200_is_listed(self):
        self.assertEqual(tools.split_long_text({"a": {"x" * 200: 1}}), ({"a": {"x" * 200: 1}}, {}))
        self.assertEqual(tools.split_long_text({"a": {"x" * 201: 1}}), ({}, {"a": {"distinct": 1, "longest_chars": 201}}))
        self.assertEqual(tools.split_long_text({}), ({}, {}))

    def test_the_site_holds_the_same_rule(self):
        with open(os.path.join(SITE, "lib", "chat", "longtext.ts"), encoding="utf-8") as f:
            ts = f.read()
        self.assertIn("export const LONG_TEXT = 200;", ts)
        self.assertEqual(tools.LONG_TEXT, 200)
        said = "".join(part.strip().strip('"') for part in ts.split("export const LONG_TEXT_NOTE = ")[1].split(";\n")[0].split(" +\n"))
        self.assertEqual(said, tools.LONG_TEXT_NOTE)

    def test_the_sites_own_tests(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "--test", "scripts/test-ask-longtext.test.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in (r.stdout + r.stderr):
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-800:])

    def test_a_large_load_table_is_described_in_a_few_kb(self):
        """The measure: the Python tool's own description of the two tables of prose, from the files on this machine."""
        d = data_dir()
        if not d:
            raise unittest.SkipTest("the new tables' files are not on this machine")
        cov = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
        code = ("import json, sys, warnings; warnings.simplefilter('ignore'); sys.path.insert(0, sys.argv[1]); import tools\n"
                "for t in ('utility_large_load_rules', 'state_large_load_laws'):\n"
                "    out = tools.describe_table(t)\n"
                "    print(json.dumps({'table': t, 'chars': len(json.dumps(out, default=str)), 'prose': sorted(out.get('long_text_columns') or {}),\n"
                "                      'listed': sorted(out['text_column_values']), 'note': out.get('long_text_columns_note')}))\n")
        r = subprocess.run([sys.executable, "-W", "ignore", "-c", code, os.path.join(ROOT, "warehouse", "chat")], capture_output=True, text=True, timeout=600,
                           env={**os.environ, "ERW_BACKEND": "local", "ERW_DATA_DIR": d, "ERW_COVERAGE_CSV": cov, "ASK_HOLD": "on"})
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        got = {x["table"]: x for x in (json.loads(line) for line in r.stdout.splitlines() if line.startswith("{"))}
        rules, laws = got["utility_large_load_rules"], got["state_large_load_laws"]
        self.assertLess(rules["chars"], 12000)   # 79,989 before
        self.assertLess(laws["chars"], 15000)    # 90,394 before
        self.assertIn("x_contract_term", rules["prose"])
        self.assertIn("x_requirements", laws["prose"])
        for t in (rules, laws):
            self.assertIn("status", t["listed"])
            self.assertIn("x_state", t["listed"])
            self.assertEqual(t["note"], tools.LONG_TEXT_NOTE)


if __name__ == "__main__":
    unittest.main()
