"""Session 6136 (chain 281): the fresh read for three audiences; a date in words; rule 12; the list names the table a
question asks about and the site cannot read.

Energy Research Warehouse (ERW).

The read. Sixty stored replies read as a trader, a project developer and an AI lab's energy team would read them, 20
each (the trader's twenty of session 5275; twenty of the platform set's projects, transmission, storage and renewables
questions as asked on 14 November; the lab's twenty of the same day). Every one right. The faults are of form: 16 gave a
date as the tool writes it (2026-11-05); 6 spoke of a row's label ("the row labelled 2026-09-01", "keyed to"); 4 of the
tools ("the compare tool's result", "every query returns"); 3 wrote a price past the cent.

The mends. The date is the loop's to write (plain_dates, plainDates), after every check has run. The other three are
rule 12 of the prompt, "Write for the reader, not about how you worked". And the cost of a question about a table the
site cannot read: the list's own result now names that table first, in the tools' words (with_asked_about).

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

with open(os.path.join(ROOT, "tests", "fixtures", "session6136", "cases.json"), encoding="utf-8") as _f:
    FX = json.load(_f)


def python_side():
    dates = {c["id"]: ask.plain_dates(c["text"]) for c in FX["dates"]}
    lists = {}
    for c in FX["lists"]:
        out, told = ask.with_asked_about(c["out"], c["question"], c["input"], FX["verdicts"], tools.not_listed_words)
        lists[c["id"]] = {"keys": list(out), "told": list(told), "words": list(told.values())}
    return {"dates": dates, "lists": lists}


class ADateInWords(unittest.TestCase):
    def test_each_case(self):
        got = python_side()["dates"]
        for c in FX["dates"]:
            self.assertEqual(got[c["id"]], c["plain"], c["id"])

    def test_it_is_written_after_the_checks_and_for_the_general_chat(self):
        py = open(os.path.join(ROOT, "warehouse", "chat", "ask.py"), encoding="utf-8").read()
        self.assertIn('if type(self) is Asker and isinstance(record.get("answer"), str):\n            record["answer"] = plain_dates(record["answer"])', py)
        ts = open(os.path.join(SITE, "lib", "chat", "ask.ts"), encoding="utf-8").read()
        self.assertIn("if (!profile) draft = { ...draft, answer: plainDates(draft.answer) };\n    const answer = plain(nodash(draft.answer));", ts.replace("\r\n", "\n"))


class RuleTwelve(unittest.TestCase):
    def test_the_rule_is_in_the_prompt_of_both_loops(self):
        self.assertIn('\n12. Write for the reader, not about how you worked. Say the thing itself: "the week is complete"', ask.RULES)
        self.assertIn("Do not mention tools, calls, queries or checks.", ask.RULES)
        self.assertIn("Write a price to the cent (49.84 USD/MWh, not 49.835) unless the question asks for more decimals.", ask.RULES)
        with open(os.path.join(SITE, "lib", "chat", "spec.json"), encoding="utf-8") as f:
            spec = json.load(f)
        self.assertEqual(spec["system"], ask.SYSTEM)
        self.assertEqual(len([line for line in ask.RULES.split("\n") if line[:3].rstrip(". ").isdigit()]), 12)

    def test_the_earlier_rules_are_as_they_were(self):
        self.assertIn("\n11. Stop when you have the answer.", ask.RULES)
        self.assertIn("\n3. If the warehouse does not hold what the question asks", ask.RULES)
        self.assertIn("\n1. Answer only from tool results.", ask.RULES)


class TheListNamesTheTable(unittest.TestCase):
    def test_each_case(self):
        got = python_side()["lists"]
        for c in FX["lists"]:
            self.assertEqual(got[c["id"]]["told"], c["told"], c["id"])
            self.assertEqual(got[c["id"]]["keys"], c["keys"], c["id"])
        words = got["the_question_names_one"]["words"][0]
        self.assertEqual(words, tools.not_listed_words("forecast_tool_parameters", "public"))

    def test_the_table_counts_as_refused_whole(self):
        py = open(os.path.join(ROOT, "warehouse", "chat", "ask.py"), encoding="utf-8").read()
        self.assertIn("refused_whole_words.setdefault(t, words)\n                                refused_tables.add(t)", py)
        ts = open(os.path.join(SITE, "lib", "chat", "ask.ts"), encoding="utf-8").read()
        self.assertIn("for (const [t, words] of Object.entries(told.told)) { if (!refusedWholeWords.has(t)) refusedWholeWords.set(t, words); refusedTables.add(t); }", ts)


class BothLanguages(unittest.TestCase):
    def test_the_site_returns_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, "scripts/test-ask-6136.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
        self.assertEqual(json.loads(next(x for x in r.stdout.splitlines() if x.startswith("{"))), python_side())


if __name__ == "__main__":
    unittest.main()
