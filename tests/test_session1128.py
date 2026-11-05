"""Session 1128 (chain 076): an evaluation of Ask as one command (warehouse/chat/eval/run_eval.py).

Held here, with nothing started: the plan's steps are chain 075's, in its order (probe, memory, lock, build, serve, keys,
ask, grade, stop, release); --no-build leaves the build out and nothing else; each set's keys step is its own script;
--only and --cap reach the asking; --dry-run prints every step and exits 0. No network, no server, no model. Nothing
here sets the environment at import.
"""
import contextlib
import io
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def run_eval():
    if EVAL not in sys.path:
        sys.path.insert(0, EVAL)
    import run_eval as m  # noqa: E402
    return m


class ThePlan(unittest.TestCase):
    def test_the_steps_in_order(self):
        m = run_eval()
        self.assertEqual([s[0] for s in m.plan("s320", 6, 3713)], ["probe", "memory", "lock", "build", "serve", "keys", "ask", "grade", "stop", "release"])
        self.assertEqual([s[0] for s in m.plan("s320", 6, 3713, build=False)], ["probe", "memory", "lock", "serve", "keys", "ask", "grade", "stop", "release"])

    def test_each_sets_keys_and_the_asking(self):
        m = run_eval()
        s320, s1114 = dict((n, c) for n, c, _ in m.plan("s320", 6, 3713)), dict((n, c) for n, c, _ in m.plan("s1114", 4.5, 3800, only={"t02", "t01"}))
        self.assertTrue(s320["keys"][1].endswith("eval_s1113.py") and s320["keys"][2] == "--keys")
        self.assertTrue(s1114["keys"][1].endswith("expected_s1114.py"))
        self.assertEqual(s1114["ask"][2:], ["--ask", "--set", "s1114", "--base", "http://localhost:3800", "--cap", "4.5", "--only", "t01,t02"])
        self.assertEqual(s1114["serve"], ["npx", "next", "start", "-p", "3800"])
        self.assertEqual(s1114["lock"][2:], ["acquire", "eval-s1114", "--wait-min", "20"])

    def test_a_dry_run_starts_nothing(self):
        m = run_eval()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = m.main(["--set", "s320", "--cap", "6", "--dry-run"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        for name in ("probe", "memory", "lock", "build", "serve", "keys", "ask", "grade", "stop", "release"):
            self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
