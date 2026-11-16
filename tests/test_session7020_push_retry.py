"""Session 7020 (chain 301): the daily run's commit is pushed again when main moved during its guard. On 16 November
2026 a landing merged at 16:37 UTC while the guard's suite ran, the single push was refused ("fetch first"), and the
day's metadata, docs and digests never reached main. A refused push now rebases onto the new main and the guard runs
again on the rebased commit before it is pushed, up to three times. No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheRetry(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, ".github", "workflows", "daily-prices.yml"), encoding="utf-8") as f:
            self.wf = f.read()
        i = self.wf.index("pushed=0")
        self.block = self.wf[i:self.wf.index("Release the data lock", i)]

    def test_the_guard_runs_on_every_try_before_its_push(self):
        b = self.block
        self.assertIn("for try in 1 2 3; do", b)
        self.assertLess(b.index('python scripts/push_guard.py --who "daily prices" --step "commit"'), b.index("git push origin HEAD:main"))
        self.assertLess(b.index("git push origin HEAD:main"), b.index("git pull --rebase origin main"))
        self.assertIn("git rebase --abort", b)
        self.assertIn('[ "$pushed" = 1 ] || echo', b)

    def test_a_refused_guard_never_pushes(self):
        b = self.block
        guard = b.index('if ! python scripts/push_guard.py --who "daily prices" --step "commit"')
        self.assertIn("break", b[guard:b.index("git push origin HEAD:main")])


if __name__ == "__main__":
    unittest.main()
