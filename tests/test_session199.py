"""Session 199: a green main that stays green.

Energy Research Warehouse (ERW). The owner's ruling of 11 October 2026: a test that a landing must pass never compares
a committed figure with the day's data files. What is held here, beside the tests that were changed to the ruling
(tests/test_session149.py, test_session153.py, test_session183_replication.py, test_session190.py,
test_session190_replication.py):

  the frozen files   docs/methods/figures/<day>/: each is small, dated by the files it quotes, named by its document,
                     and listed in the folder's README with its writer and its reader;
  the tests          none of the five changed tests reads the day's file in the place where it failed on main;
  the documents      docs/machines.md and queue/CHAIN_TEMPLATE.md say that every python command names .venv's
                     interpreter.

No request, no model call, no table. The environment is read, never set."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIGURES = os.path.join(ROOT, "docs", "methods", "figures")
EM = chr(0x2014)
FROZEN = {"2026-10-07/generator_capture_months.json": 40000, "2026-10-09/ask_ercot_pages_inputs.json": 150000, "2026-10-10/datacenter_pays_inputs.json": 300000}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFrozenFiles(unittest.TestCase):
    def test_each_is_small_dated_and_listed_with_its_writer_and_its_reader(self):
        readme = src("docs", "methods", "figures", "README.md")
        found = sorted(f"{day}/{name}" for day in os.listdir(FIGURES) if os.path.isdir(os.path.join(FIGURES, day)) for name in os.listdir(os.path.join(FIGURES, day)))
        self.assertEqual(found, sorted(FROZEN))                                   # a new frozen file is added to this list and to the README
        for rel, ceiling in FROZEN.items():
            day, name = rel.split("/")
            self.assertRegex(day, r"^\d{4}-\d{2}-\d{2}$")
            text = src("docs", "methods", "figures", day, name)
            self.assertLess(len(text), ceiling, rel)                              # kilobytes, never the page files themselves
            self.assertNotIn(EM, text, rel)
            z = json.loads(text)
            self.assertIn("not edited by hand", z["_about"], rel)
            self.assertIn(f"| `{rel}` |", readme, rel)
        self.assertNotIn(EM, readme)
        for words in ("A test that a landing must pass never compares a committed figure with the day's data files.", "The pages go on showing the day's data.",
                      "warehouse/derived/generator_hourly_export.py", "warehouse/chat/eval/ercot_pages_expected.py --write", "site/scripts/freeze-datacenter-note.mjs",
                      "tests/test_session183_replication.py", "tests/test_session153.py", "tests/test_session190.py", "tests/test_session190_replication.py"):
            self.assertIn(words, readme, words)

    def test_each_is_dated_by_the_files_it_quotes_and_named_by_its_document(self):
        cap = json.loads(src("docs", "methods", "figures", "2026-10-07", "generator_capture_months.json"))
        self.assertEqual(cap["capture_built"][:10], "2026-10-07")
        with open(os.path.join(ROOT, "site", "public", "seller", "erw_2026_generator_hourly.csv"), encoding="utf-8") as f:
            head = f.read(8000)
        self.assertIn(f"site/data/seller/capture.json (built {cap['capture_built']}; sha256 {cap['capture_sha256']})", head)
        ask = json.loads(src("docs", "methods", "figures", "2026-10-09", "ask_ercot_pages_inputs.json"))
        self.assertEqual(max(ask["built"].values())[:10], "2026-10-09")
        self.assertEqual(json.loads(src("warehouse", "chat", "eval_ercot_pages.json"))["built_from"]["inputs"], "docs/methods/figures/2026-10-09/ask_ercot_pages_inputs.json")
        note = json.loads(src("docs", "methods", "figures", "2026-10-10", "datacenter_pays_inputs.json"))
        self.assertEqual(note["built"][:10], "2026-10-10")
        self.assertIn("`docs/methods/figures/2026-10-10/datacenter_pays_inputs.json`", src("docs", "methods", "datacenter_pays_algorithm.md"))

    def test_the_site_does_not_take_the_folder_for_a_method_note(self):
        # build-content.mjs lists docs/methods and takes the .md files of that folder alone; the README here is one folder down
        self.assertIn('for (const f of fs.readdirSync(path.join(docs, "methods")).sort()) {\n  if (f.endsWith(".md")', src("site", "scripts", "build-content.mjs"))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "docs", "methods", "figures.md")))


class TheTestsFollowTheRuling(unittest.TestCase):
    def test_the_five_no_longer_read_the_days_file_where_they_failed(self):
        t153 = src("tests", "test_session153.py")
        self.assertIn("exp.use_frozen(path)", t153)
        self.assertNotIn("exp.build(tables_dir(), kept)", t153)
        t183 = src("tests", "test_session183_replication.py")
        self.assertIn("cls.facts = cls.ex.page_facts(capture_of_the_csvs_build())", t183)
        self.assertNotIn("with open(CAPTURE, encoding=\"utf-8\") as f:\n        cap = json.load(f)", t183)
        self.assertNotIn('fs.readFileSync("./data/seller/capture.json"', t183)
        t190 = src("tests", "test_session190.py")
        self.assertIn('const Z = JSON.parse(fs.readFileSync("../" + FROZEN, "utf-8"));', t190)
        self.assertNotIn("./data/datacenter/index.json", t190)
        self.assertNotIn("ercot_${y}.json", t190)
        t190r = src("tests", "test_session190_replication.py")
        self.assertIn("def test_the_example_of_the_note_on_the_files_it_quotes(self):", t190r)
        self.assertNotIn("on_the_window", t190r)
        t149 = src("tests", "test_session149.py")
        self.assertIn('if not os.path.exists(os.path.join(ROOT, ".erw", "machine.json")):\n            self.skipTest("this copy holds no role file', t149)

    def test_the_role_file_is_not_in_git(self):
        self.assertRegex(src(".gitignore"), r"(?m)^\.erw/?$")


class TheDocuments(unittest.TestCase):
    def test_every_python_command_names_the_repositorys_interpreter(self):
        for rel in (("docs", "machines.md"), ("queue", "CHAIN_TEMPLATE.md")):
            text = src(*rel)
            self.assertIn("`.venv\\Scripts\\python.exe`", text, rel)
            self.assertIn("`.venv/bin/python`", text, rel)
            self.assertIn("may hold no package", text, rel)
            self.assertNotIn(EM, text, rel)
        # the template's first and last rules are as they were (tests/test_session188_precheck.py holds them too)
        rules = re.findall(r"^(\d+)\. (.*)$", src("queue", "CHAIN_TEMPLATE.md"), re.M)
        self.assertIn("python scripts/precheck.py", rules[0][1])
        self.assertIn("python scripts/chain_queue.py next", rules[-1][1])

    def test_no_em_dash_in_what_was_written(self):
        for rel in ("tests/test_session199.py", "site/scripts/freeze-datacenter-note.mjs", "warehouse/derived/generator_hourly_export.py",
                    "warehouse/chat/eval/ercot_pages_expected.py", "docs/methods/datacenter_pays_algorithm.md"):
            self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
