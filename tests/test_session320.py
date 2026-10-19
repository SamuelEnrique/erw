"""Session 320: Ask, round two: thirty hard questions on the three economics pages (the chain of 19 October, daytime),
asked through the real routes as an evaluation (the ledger step site_ask_eval of session 314). What is held to:

  the thirty questions (ten a page: battery, generator, datacenter) are in the fixtures with their expected numbers,
    each note naming its table, entity, variable, period and aggregation; two must refuse (MISO paused, PJM not held);
  the first battery question's key is the battery page's own figure (USD per kW over the last twelve months);
  every recorded answer is right by session 267's grader, and a question wrong at first carries its cause and fix;
  no em dash.

No request, no model call; the environment is read, never set."""
import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
YAML = os.path.join(EVAL, "questions_s320.yaml")
FIX = os.path.join(EVAL, "eval_s320_fixtures.json")
FILES = ["warehouse/chat/eval/questions_s320.yaml", "warehouse/chat/README.md", "docs/state/review_2026-10-19_code_pm.md", "tests/test_session320.py"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load_yaml(path):
    qs, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("- id: "):
            cur = {"id": line[6:].strip()}
            qs.append(cur)
        elif line.startswith("  ") and cur is not None and ": " in line:
            k, v = line[2:].split(": ", 1)
            if k in ("question", "expected", "text", "tables", "note"):
                cur[k] = json.loads(v)
            elif k == "tolerance":
                cur[k] = float(v)
            elif k == "refuse":
                cur[k] = v.strip() == "true"
            else:
                cur[k] = v.strip()
    return qs


def grader():
    spec = importlib.util.spec_from_file_location("eval_s267", os.path.join(EVAL, "eval_s267.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheThirtyQuestions(unittest.TestCase):
    def setUp(self):
        self.qs = load_yaml(YAML)

    def test_ten_a_page_keyed_from_the_three_tables_with_two_refusals(self):
        self.assertEqual(len(self.qs), 30)
        self.assertEqual([q["id"][0] for q in self.qs].count("b"), 10)
        self.assertEqual([q["id"][0] for q in self.qs].count("g"), 10)
        self.assertEqual([q["id"][0] for q in self.qs].count("d"), 10)
        tables = {"b": "battery_stack_monthly", "g": "merchant_revenue_monthly", "d": "cost_of_power_monthly"}
        for q in self.qs:
            self.assertEqual(q["tables"], [tables[q["id"][0]]], q["id"])
            self.assertIn(q["via"], ("grid", "general"), q["id"])
            self.assertTrue(q["note"].strip(), q["id"])
            if q["refuse"]:
                self.assertEqual(q["expected"], [], q["id"])
            else:
                self.assertTrue(q["expected"] and all(isinstance(v, (int, float)) for v in q["expected"]), q["id"])
                self.assertIn(q["tables"][0], q["note"], q["id"])
        self.assertEqual([q["id"] for q in self.qs if q["refuse"]], ["g10", "d10"])
        self.assertEqual({q["grid"] for q in self.qs if q["refuse"]}, {"MISO", "PJM"})

    def test_the_first_key_is_the_battery_pages_own_figure(self):
        b01 = self.qs[0]
        self.assertEqual(b01["id"], "b01")
        self.assertAlmostEqual(b01["expected"][0], 81.4022, places=3)   # the battery page's USD 81.40 per kW, the last twelve months (session 304's package)
        self.assertIn("foresight_4h_revenue_total_usd_per_mw", b01["note"])

    def test_the_questions_say_their_aggregation_in_the_readers_words(self):
        for q in self.qs:
            if q["refuse"]:
                continue
            n = q["note"]
            if "summed" in n or "the sum of" in n:
                self.assertTrue("summed" in q["question"] or "in total" in q["question"] or "total revenue" in q["question"] or "earn" in q["question"], q["id"])
            if "the mean of" in n:
                self.assertIn("average of the twelve monthly", q["question"], q["id"])


@unittest.skipUnless(os.path.exists(FIX), "the recorded answers are written by the run")
class TheRecordedAnswers(unittest.TestCase):
    def setUp(self):
        self.fx = json.load(open(FIX, encoding="utf-8"))
        self.qs = {q["id"]: q for q in load_yaml(YAML)}

    def test_every_recorded_answer_is_right_by_the_grader_and_through_the_evaluations_step(self):
        G = grader()
        self.assertTrue(self.fx["questions"])
        for a in self.fx["questions"]:
            q = self.qs[a["id"]]
            body = {k: a.get(k) for k in ("answer", "citations", "not_in_warehouse", "error", "status")}
            g = G.grade(q, body)
            self.assertTrue(g["ok"], (a["id"], g, (a.get("answer") or "")[:200]))
            self.assertEqual(a.get("step"), "site_ask_eval", a["id"])
            self.assertGreater(float(a.get("cost_usd") or 0), 0, a["id"]) if not q["refuse"] else None

    def test_a_question_wrong_at_first_carries_its_cause_and_fix(self):
        for a in self.fx["questions"]:
            if a.get("first_asking"):
                self.assertTrue(a["first_asking"].get("cause") and a["first_asking"].get("fix"), a["id"])


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            p = os.path.join(ROOT, *f.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
