"""Session 578: the suite's own output is not read as GitHub workflow commands.

On GitHub's runner (GITHUB_ACTIONS=true) a line any process prints that begins with "::warning::" or "::notice::" becomes
an annotation on the run. The code under test prints such lines (warehouse/health.py, warehouse/connectors/ercot_dam_esr.py,
the derived tables), and the tests' fixtures put 20 to 29 false annotations on every run that ran the suite (the daily
run's "merge tests" step, code-branch's "Tests (tests/)"), beside the real ones: "network_hourly FAILED: RuntimeError:
boom", "daily model cap reached: USD 1.32 spent today (2026-10-08 UTC, 16 calls ...)", "x FAILED: RuntimeError: HTTP 500"
(docs/reviews/scheduled-jobs-2026-10-22.md, which read every run of 15 to 21 October).

`python -m unittest discover -s tests` imports the test modules in sorted order before it runs any, so this one first
("test_000" sorts before every other name). On the runner it prints GitHub's `::stop-commands::<token>` with a random
token, and the token again (`::<token>::`) when the process exits, so the lines printed between are plain text in the log
and nothing else. Off the runner it does nothing. No workflow is changed: what the step prints after the suite (health.py's
own line on a failed suite) is read as before.
"""
import atexit
import os
import secrets
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def quiet(env=None, out=None, at_exit=atexit.register):
    """On GitHub's runner, stop the reading of workflow commands until this process exits; returns the token, or None
    off the runner (nothing printed)."""
    env = os.environ if env is None else env
    if env.get("GITHUB_ACTIONS") != "true":
        return None
    out = out or sys.stdout
    token = "erw-suite-" + secrets.token_hex(12)
    out.write(f"::stop-commands::{token}\n")
    out.flush()

    def resume():
        try:
            out.write(f"::{token}::\n")
            out.flush()
        except (OSError, ValueError):
            pass

    at_exit(resume)
    return token


TOKEN = quiet()


class QuietAnnotations(unittest.TestCase):
    def test_off_the_runner_nothing_is_printed(self):
        import io
        buf, later = io.StringIO(), []
        self.assertIsNone(quiet(env={}, out=buf, at_exit=later.append))
        self.assertIsNone(quiet(env={"GITHUB_ACTIONS": "false"}, out=buf, at_exit=later.append))
        self.assertEqual(buf.getvalue(), "")
        self.assertEqual(later, [])

    def test_on_the_runner_the_commands_stop_and_resume_with_one_random_token(self):
        import io
        buf, later = io.StringIO(), []
        token = quiet(env={"GITHUB_ACTIONS": "true"}, out=buf, at_exit=later.append)
        self.assertEqual(buf.getvalue(), f"::stop-commands::{token}\n")
        self.assertEqual(len(later), 1)
        later[0]()
        self.assertEqual(buf.getvalue(), f"::stop-commands::{token}\n::{token}::\n")
        other = quiet(env={"GITHUB_ACTIONS": "true"}, out=io.StringIO(), at_exit=[].append)
        self.assertNotEqual(token, other)
        # never a name GitHub reads as a command of its own
        for name in ("warning", "notice", "error", "debug", "group", "endgroup", "add-mask", "stop-commands"):
            self.assertNotEqual(token, name)

    def test_a_fixtures_annotation_is_between_the_stop_and_the_resume(self):
        """The module in a process of its own, as the suite imports it on the runner."""
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import test_000_quiet_annotations; "
                "print('::warning::network_hourly FAILED: RuntimeError: boom')")
        p = subprocess.run([sys.executable, "-c", code, HERE], capture_output=True, text=True, timeout=120,
                           env={**os.environ, "GITHUB_ACTIONS": "true"})
        self.assertEqual(p.returncode, 0, p.stderr)
        lines = p.stdout.splitlines()
        self.assertEqual(len(lines), 3, lines)
        self.assertTrue(lines[0].startswith("::stop-commands::erw-suite-"), lines)
        token = lines[0].split("::stop-commands::", 1)[1]
        self.assertEqual(lines[1], "::warning::network_hourly FAILED: RuntimeError: boom")
        self.assertEqual(lines[2], f"::{token}::")

    def test_off_the_runner_the_module_prints_nothing(self):
        code = "import sys; sys.path.insert(0, sys.argv[1]); import test_000_quiet_annotations"
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_ACTIONS"}
        p = subprocess.run([sys.executable, "-c", code, HERE], capture_output=True, text=True, timeout=120, env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout, "")

    def test_discover_imports_this_module_first(self):
        names = sorted(n for n in os.listdir(HERE) if n.startswith("test") and n.endswith(".py"))
        self.assertEqual(names[0], os.path.basename(__file__))


if __name__ == "__main__":
    unittest.main()
