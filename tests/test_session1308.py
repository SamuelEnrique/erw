"""Session 1308 (chain 095): Ask's stored answers replayed as a step of the landing gate (scripts/land_check.py,
ask_replay, after the suite and before npm ci).

Held here, with session 579's scripted operations (no git, no build, no network): the step runs
warehouse/chat/eval/replay.py --check in the gate's clean copy; its failure fails the gate and every step after it is
skipped (no npm ci, no build, no server); a commit with no replay.py passes the step and says so; and the step's place
in the order.
Nothing here sets the environment at import.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_session579 as T  # noqa: E402

LC = T.LC


class Ops(T.FakeOps):
    """As session 579's, with the commit's replay.py present unless told otherwise."""

    def __init__(self, replay=True, **kw):
        super().__init__(**kw)
        self.replay = replay

    def exists(self, path):
        if path.replace("\\", "/").endswith("warehouse/chat/eval/replay.py"):
            return self.replay
        return super().exists(path)


class TheStep(unittest.TestCase):
    # session 579's gate helpers, borrowed (inheriting would run its tests a second time)
    setUp, tearDown, gate, steps, states, record = (T.Gate579.setUp, T.Gate579.tearDown, T.Gate579.gate, T.Gate579.steps,
                                                    T.Gate579.states, T.Gate579.record)

    def test_its_place(self):
        self.assertEqual(LC.STEPS[LC.STEPS.index("suite") + 1], "ask_replay")
        self.assertEqual(LC.STEPS[LC.STEPS.index("ask_replay") + 1], "npm_ci")

    def test_it_runs_the_replay_with_check_in_the_clean_copy(self):
        ops = Ops()
        self.assertEqual(self.gate(ops), 0)
        calls = self.steps(ops, "ask_replay")
        self.assertEqual(len(calls), 1)
        argv, cwd = calls[0][1], calls[0][2]
        self.assertTrue(argv[1].replace("\\", "/").endswith("warehouse/chat/eval/replay.py"))
        self.assertEqual(argv[2:], ["--check"])
        self.assertTrue(argv[1].startswith(cwd))
        self.assertEqual(self.states()["ask_replay"], "pass")

    def test_a_failure_stops_the_gate_before_the_build(self):
        ops = Ops(codes={"ask_replay": [1]})
        self.assertEqual(self.gate(ops), 1)
        st = self.states()
        self.assertEqual(st["suite"], "pass")
        self.assertEqual(st["ask_replay"], "fail")
        for step in LC.STEPS[LC.STEPS.index("npm_ci"):]:
            self.assertEqual(st[step], "skip", step)
        self.assertEqual(self.steps(ops, "npm_ci"), [])
        self.assertEqual(ops.started, 0)
        self.assertIn("NOT READY", "\n".join(self.printed))

    def test_a_commit_without_the_replay_passes_the_step(self):
        ops = Ops(replay=False)
        self.assertEqual(self.gate(ops), 0)
        self.assertEqual(self.steps(ops, "ask_replay"), [])
        self.assertIn("no replay.py in this commit", self.record())


if __name__ == "__main__":
    unittest.main()
