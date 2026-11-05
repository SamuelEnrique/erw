"""Session 1110 (chain 075): the number check lets nothing invented through, and stops nothing true for a name.

Held here: on six answers to session 320's b01 (tests/fixtures/session1110/answers.json: three clean, three with a
figure no tool returned in the unit stated) against two tool results of the site's tool on session 1109's saved rows
(sources.json), warehouse/chat/ask.py unverified and unit_mismatches return what each answer names, and
site/lib/chat/ask.ts returns the same on the same strings (site/scripts/test-ask-1110.mjs); a form name (EIA-930) is
not a figure, which sent four right first drafts back in session 320's run; the refusal begins "The warehouse does not
hold that figure"; the spec the site reads is the one ask.py exports.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CHAT = os.path.join(ROOT, "warehouse", "chat")
FIX = os.path.join(ROOT, "tests", "fixtures", "session1110")


def load(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return json.load(f)


def chat_ask():
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    import ask  # noqa: E402
    return ask


class TheCheck(unittest.TestCase):
    def setUp(self):
        self.ask = chat_ask()
        src = load("sources.json")
        self.sources = [src["question"]] + src["sources"]

    def test_the_six_answers(self):
        answers = load("answers.json")["answers"]
        self.assertEqual(len(answers), 6)
        for a in answers:
            self.assertEqual(self.ask.unverified(a["answer"], self.sources), a["untraced"], a["id"])
            self.assertEqual(self.ask.unit_mismatches(a["answer"], self.sources), a["units"], a["id"])
        self.assertEqual(sum(1 for a in answers if not a["untraced"] and not a["units"]), 3)

    def test_a_form_name_is_not_a_figure(self):
        n = self.ask.numbers
        self.assertEqual(n("the EIA-930 balance, EIA-860M and EIA-923"), [])
        self.assertEqual(n("fell -3.2 to (-1.5)"), [(-3.2, 1), (-1.5, 1)])
        self.assertEqual(n("2026-09-22"), [(2026.0, 0), (9.0, 0), (22.0, 0)])
        # session 320's four first drafts were sent back for 930 alone: the same words now pass
        self.assertEqual(self.ask.unverified("hourly demand from EIA-930 (eia930_balance)", ["{}"]), [])

    def test_a_unit_with_no_money_or_a_compound_unit_is_not_judged(self):
        s = [json.dumps({"units": ["MWh/MW"], "result": [{"value": 150.5}]}),
             json.dumps({"units": ["USD/MW-month"], "result": [{"value": 7.25}]})]
        self.assertEqual(self.ask.unit_mismatches("It discharged 150.5 MWh per MW, at USD 7.25 per MW-month.", s), [])

    def test_a_number_no_result_places_in_a_unit_is_not_judged(self):
        self.assertEqual(self.ask.unit_mismatches("USD 40 per MWh", ["the question says 40", json.dumps({"rows_matched": 40})]), [])
        mixed = json.dumps({"units": ["USD/MW", "USD/MWh"], "result": [{"value": 40}]})
        self.assertEqual(self.ask.unit_mismatches("USD 40 per kW", [mixed]), [])

    def test_the_refusal_and_the_spec(self):
        self.assertTrue(self.ask.REFUSAL.startswith("The warehouse does not hold that figure: "))
        with open(os.path.join(SITE, "lib", "chat", "spec.json"), encoding="utf-8") as f:
            committed = f.read()
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "spec.json")
            self.ask.export_spec(out)
            with open(out, encoding="utf-8") as f:
                self.assertEqual(f.read(), committed)


class BothLanguages(unittest.TestCase):
    def test_the_site_check_returns_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-1110.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        site = json.loads(r.stdout.splitlines()[0])["results"]
        ask = chat_ask()
        src = load("sources.json")
        sources = [src["question"]] + src["sources"]
        for a in load("answers.json")["answers"]:
            self.assertEqual(site[a["id"]], {"untraced": ask.unverified(a["answer"], sources),
                                             "units": ask.unit_mismatches(a["answer"], sources)}, a["id"])


if __name__ == "__main__":
    unittest.main()
