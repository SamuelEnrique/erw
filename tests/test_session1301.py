"""Session 1301 (chain 093): the stored answers replayed through today's checks (warehouse/chat/eval/replay.py).

Held here: docs/reviews/ask-replay.md is what the stored runs give, and no answer graded right would now be sent back by
the number check, the unit check or the citations as they stand; the replay reads every run that carries a tool record
(more than 150 answers); and it is not blind: a stored answer with one figure changed, one with a table cited that no
tool read, and one that cites nothing are each caught.
No network, no model. Nothing here sets the environment at import.
"""
import copy
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def replay():
    if EVAL not in sys.path:
        sys.path.insert(0, EVAL)
    import replay as R  # noqa: E402
    return R


class TheReplay(unittest.TestCase):
    def test_the_file_is_what_the_runs_give_and_no_right_answer_is_sent_back(self):
        r = subprocess.run([sys.executable, os.path.join(EVAL, "replay.py"), "--check"], capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])

    def test_every_run_with_a_record_is_read(self):
        R = replay()
        rows = R.replay()
        self.assertGreater(len(rows), 150)
        self.assertEqual({r["run"] for r in rows}, {label for _, _, label in R.RUNS})
        self.assertEqual([r for r in rows if R.sent_back(r) and r["right"]], [])

    def test_it_is_not_blind(self):
        R = replay()
        q = next(x for x in R.load("eval_s1113_run.json")["questions"] if x["status"] == "answered" and re.search(r"\d+\.\d+", x["answer"]) and R.trace_of(x))
        sources = [q["question"], "Today is 2026-10-23 (UTC)."] + [str(t.get("out")) for t in R.trace_of(q)]
        m = re.search(r"\d+\.\d+", q["answer"])
        changed = q["answer"][:m.start()] + f"{float(m.group()) + 7.13:.{len(m.group().split('.')[1])}f}" + q["answer"][m.end():]
        self.assertEqual(R.ask.unverified(q["answer"], sources), [])
        self.assertTrue(R.ask.unverified(changed, sources))
        self.assertFalse(R.sent_back(R.check(q)))
        moved = dict(copy.deepcopy(q), answer=changed)
        self.assertTrue(R.check(moved)["numbers"])
        unread = copy.deepcopy(q)
        unread["citations"] = [{"table": "a_table_never_read", "source_report": "x", "data_version": "x", "tier": "derived"}]
        self.assertEqual(R.check(unread)["uncited"], ["a_table_never_read"])
        empty = dict(copy.deepcopy(q), citations=[])
        self.assertTrue(R.check(empty)["no_cite"])


if __name__ == "__main__":
    unittest.main()
