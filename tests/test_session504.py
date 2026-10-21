"""Session 504: the build lock in the repository (scripts/buildlock.py). Chain files have named runs/build.lock since
19 October 2026 and no tool held it until chain 019's helper (runs/chain_019/buildlock.py, not in git). The lock is
one file holding "<who> <UTC time>", the helper's format, so a lock either tool holds is honoured by the other; it
lives in the main checkout's runs/, found from a worktree; only its holder releases it; a stale lock is taken."""

import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import buildlock as B  # noqa: E402

SCRIPT = os.path.join(ROOT, "scripts", "buildlock.py")


def quiet(*a, **k):
    pass


class Lock(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "runs", "build.lock")

    def tearDown(self):
        self.tmp.cleanup()

    def test_acquire_writes_the_helpers_format(self):
        self.assertEqual(B.acquire("s504", path=self.path, out=quiet), 0)
        who, since = open(self.path, encoding="utf-8").read().split()
        self.assertEqual(who, "s504")
        self.assertRegex(since, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_a_held_lock_is_waited_for_then_given_up(self):
        B.acquire("s1", path=self.path, out=quiet)
        t0 = time.time()
        self.assertEqual(B.acquire("s2", path=self.path, wait_min=0.001, poll_s=0.01, out=quiet), 1)
        self.assertLess(time.time() - t0, 5)
        self.assertEqual(B.holder(self.path)[0], "s1")

    def test_a_lock_the_helper_wrote_is_honoured(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("s474 2026-10-21T10:13:00Z")       # the helper's own line
        self.assertEqual(B.acquire("s504", path=self.path, wait_min=0.001, poll_s=0.01, out=quiet), 1)
        self.assertEqual(B.release("s504", path=self.path, out=quiet), 1)
        self.assertEqual(B.holder(self.path), ("s474", "2026-10-21T10:13:00Z"))
        self.assertEqual(B.release("s474", path=self.path, out=quiet), 0)
        self.assertIsNone(B.holder(self.path))

    def test_only_the_holder_releases(self):
        B.acquire("s1", path=self.path, out=quiet)
        self.assertEqual(B.release("s2", path=self.path, out=quiet), 1)
        self.assertTrue(os.path.exists(self.path))
        self.assertEqual(B.release("s1", path=self.path, out=quiet), 0)
        self.assertFalse(os.path.exists(self.path))
        self.assertEqual(B.release("s1", path=self.path, out=quiet), 0)   # not held: nothing to do

    def test_a_stale_lock_is_taken(self):
        B.acquire("old", path=self.path, out=quiet)
        past = time.time() - 4 * 3600
        os.utime(self.path, (past, past))
        self.assertEqual(B.acquire("new", path=self.path, wait_min=0.001, poll_s=0.01, out=quiet), 0)
        self.assertEqual(B.holder(self.path)[0], "new")

    def test_status_says_who_and_exits_1_when_held(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(B.status(path=self.path), 0)
            B.acquire("s9", path=self.path)
            self.assertEqual(B.status(path=self.path), 1)
        self.assertIn("free", buf.getvalue())
        self.assertIn("held by s9", buf.getvalue())


class Where(unittest.TestCase):
    def test_the_lock_lives_in_the_main_checkouts_runs(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ERW_BUILD_LOCK", None)
            main = B.main_checkout(ROOT)
            self.assertEqual(os.path.normcase(B.lock_path(ROOT)), os.path.normcase(os.path.join(main, "runs", "build.lock")))
            self.assertTrue(os.path.isdir(os.path.join(main, ".git")), main)   # a worktree's .git is a file; the main checkout's a folder

    def test_the_environment_names_another_file(self):
        with mock.patch.dict(os.environ, {"ERW_BUILD_LOCK": "x.lock"}):
            self.assertEqual(B.lock_path(ROOT), "x.lock")


class Command(unittest.TestCase):
    def run_cli(self, *args, env_extra=None):
        env = dict(os.environ, **(env_extra or {}))
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, timeout=60, env=env)

    def test_the_command_under_git_bashs_setting(self):
        with tempfile.TemporaryDirectory() as d:
            lock = os.path.join(d, "b.lock")
            extra = {"ERW_BUILD_LOCK": lock, "MSYS_NO_PATHCONV": "1"}
            self.assertEqual(self.run_cli("acquire", "s504", env_extra=extra).returncode, 0)
            self.assertEqual(self.run_cli("status", env_extra=extra).returncode, 1)
            self.assertEqual(self.run_cli("release", "s504", env_extra=extra).returncode, 0)
            self.assertEqual(self.run_cli("status", env_extra=extra).returncode, 0)

    def test_bad_input_exits_2(self):
        self.assertEqual(self.run_cli("acquire").returncode, 2)
        self.assertEqual(self.run_cli("release", "two words").returncode, 2)
        self.assertEqual(self.run_cli("take", "x").returncode, 2)


class Words(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for p in (SCRIPT, os.path.abspath(__file__)):
            text = open(p, encoding="utf-8").read()
            self.assertNotIn(chr(0x2014), text, p)
            self.assertNotIn(chr(0x2013), text, p)

    def test_machines_md_names_the_tool(self):
        text = open(os.path.join(ROOT, "docs", "machines.md"), encoding="utf-8").read()
        self.assertIn("scripts/buildlock.py", text)


if __name__ == "__main__":
    unittest.main()
