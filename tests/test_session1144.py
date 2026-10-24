"""Session 1144 (chain 085): the unit check, measured on the stored transcripts, extended to percent and MW.

Held here: on every stored answer with its tool record (sessions 267, 302, 1113 and 1114: 119 answers), the check
(warehouse/chat/ask.py unit_mismatches) sends back no answer that was graded right, now that it judges percent and MW;
it still judges no MWh (four right answers wrote "MWh" before "per MW"); a figure stated in the wrong one of the two is
sent back; session 1110's six answers still give what they gave. No network, no model. Nothing here sets the
environment at import.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT = os.path.join(ROOT, "warehouse", "chat")
EVAL = os.path.join(CHAT, "eval")


def chat_ask():
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    import ask  # noqa: E402
    return ask


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


class TheStoredAnswers(unittest.TestCase):
    def test_no_right_answer_is_sent_back(self):
        ask = chat_ask()
        g13 = {q["id"]: q["held_ok"] for q in load("eval_s1113_grades.json")["questions"]}
        g14 = {q["id"]: q["ok"] for q in load("eval_s1114_grades.json")["questions"]}
        judged, sent_back = 0, []
        for name in ("eval_s267_fixtures.json", "eval_s302_fixtures.json", "eval_s1113_run.json", "eval_s1114_run.json"):
            for q in load(name)["questions"]:
                if not q.get("trace") or not q.get("answer"):
                    continue
                right = g13.get(q["id"]) if name == "eval_s1113_run.json" else g14.get(q["id"]) if name == "eval_s1114_run.json" else q.get("verdict") == "right"
                if not right:
                    continue
                judged += 1
                sources = [q.get("question", "")] + [json.dumps(t.get("out")) for t in q["trace"]] + [json.dumps(t.get("input")) for t in q["trace"]]
                bad = ask.unit_mismatches(q["answer"], sources)
                if bad:
                    sent_back.append((name, q["id"], bad))
        self.assertGreater(judged, 60)
        self.assertEqual(sent_back, [])

    def test_percent_and_mw_are_judged_mwh_is_not(self):
        ask = chat_ask()
        src = [json.dumps({"units": ["pct"], "result": [{"value": 90.79}]}), json.dumps({"units": ["MW"], "result": [{"value": 18204.5}]}),
               json.dumps({"units": ["MWh/MW"], "result": [{"value": 200.34}]})]
        self.assertEqual(ask.unit_mismatches("a capture rate of 90.79 percent; 18,204.5 MW operating", src), [])
        self.assertEqual(ask.unit_mismatches("18,204.5 percent", src), ["18204.5 pct (the tools gave it in MW)"])
        self.assertEqual(ask.unit_mismatches("90.79 MW", src), ["90.79 MW (the tools gave it in pct)"])
        self.assertEqual(ask.unit_mismatches("it discharged 200.34 MWh per MW", src), [])
        self.assertEqual(ask.unit_mismatches("USD 18,204.5 per MW", src), ["18204.5 USD/MW (the tools gave it in MW)"])

    def test_session_1110s_six_answers(self):
        ask = chat_ask()
        with open(os.path.join(ROOT, "tests", "fixtures", "session1110", "sources.json"), encoding="utf-8") as f:
            s = json.load(f)
        with open(os.path.join(ROOT, "tests", "fixtures", "session1110", "answers.json"), encoding="utf-8") as f:
            answers = json.load(f)["answers"]
        for a in answers:
            self.assertEqual(ask.unit_mismatches(a["answer"], [s["question"]] + s["sources"]), a["units"], a["id"])


class BothLanguages(unittest.TestCase):
    def test_the_site_check_says_the_same(self):
        site = os.path.join(ROOT, "site")
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(site, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        src = [json.dumps({"units": ["pct"], "result": [{"value": 90.79}]}), json.dumps({"units": ["MW"], "result": [{"value": 18204.5}]}),
               json.dumps({"units": ["MWh/MW"], "result": [{"value": 200.34}]})]
        texts = ["a capture rate of 90.79 percent; 18,204.5 MW operating", "18,204.5 percent", "90.79 MW", "it discharged 200.34 MWh per MW", "USD 18,204.5 per MW", "90.79% of the flat price"]
        script = ("const { unitMismatches } = await import('./lib/chat/ask.ts');"
                  f"process.stdout.write(JSON.stringify({json.dumps(texts)}.map((t) => unitMismatches(t, {json.dumps(src)}))));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=site,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), [chat_ask().unit_mismatches(t, src) for t in texts])


if __name__ == "__main__":
    unittest.main()
