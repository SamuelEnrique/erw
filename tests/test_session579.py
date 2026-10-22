"""Session 579: the landing gate in one script, without the push (scripts/land_check.py).

Every step is stubbed: no build, no suite, no server, no git command and no request is made here. One test runs a
tiny Python process through the real runner to prove an exit code is read and a timeout stops the process.
"""

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHA = "0123456789abcdef0123456789abcdef01234567"


def load():
    spec = importlib.util.spec_from_file_location("land_check_579", os.path.join(ROOT, "scripts", "land_check.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LC = load()


class FakeOps:
    """Scripted exit codes a step (a list, used in turn; 0 when it runs out) and the text each call writes to its log."""

    def __init__(self, codes=None, logs=None, ls_remote="", lock_status=(0, "build.lock is free"), held=None,
                 branch="wip/579-s", exists=()):
        self.codes = {k: list(v) for k, v in (codes or {}).items()}
        self.logs = {k: list(v) for k, v in (logs or {}).items()}
        self.ls_remote, self.lock_status, self.held_map, self.branch = ls_remote, lock_status, held or {}, branch
        self.files = {}
        self.present = set(exists)
        self.calls = []
        self.started = self.stopped = 0
        self.held_asked = None

    def run(self, step, argv, cwd, log, env=None, timeout=None):
        self.calls.append((step, list(argv), cwd, env, timeout))
        texts = self.logs.get(step)
        if texts:
            self.files[log] = self.files.get(log, "") + texts.pop(0)
        q = self.codes.get(step)
        return q.pop(0) if q else 0

    def output(self, argv, cwd):
        self.calls.append(("output", list(argv), cwd, None, None))
        if argv[:3] == ["git", "rev-parse", "--verify"]:
            return (0, SHA + "\n") if not argv[3].startswith("nope") else (128, "")
        if argv[:2] == ["git", "ls-remote"]:
            return 0, self.ls_remote
        if argv[:3] == ["git", "rev-parse", "--abbrev-ref"]:
            return 0, self.branch + "\n"
        if argv[-1] == "status":
            return self.lock_status
        raise AssertionError(f"unexpected output call {argv}")

    def read(self, path):
        return self.files.get(path, "")

    def exists(self, path):
        return path in self.present or path.replace("\\", "/").endswith("site/.env.local")

    def copy(self, src, dst):
        self.calls.append(("copy", [src, dst], None, None, None))

    def port_busy(self, port):
        return False

    def start_server(self, site_dir, port, log):
        self.started += 1
        return "server"

    def wait_ready(self, base, seconds=180):
        return True

    def stop_server(self, handle, port):
        self.stopped += 1
        return "server 1 stopped"

    def held_pages(self, base, token, pages):
        self.held_asked = list(pages)
        return {p: self.held_map.get(p, True) for p in pages}


class Gate579(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw579_")
        self.main = os.path.join(self.tmp, "erw")
        self.printed = []

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def gate(self, ops, *argv):
        code = LC.main(["--ref", "wip/579-s", *argv], ops=ops, root=self.tmp, main=self.main, out=self.printed.append)
        return code

    def record(self):
        with open(os.path.join(self.tmp, "runs", "land_check", f"{SHA}.txt"), encoding="utf-8") as f:
            return f.read()

    def steps(self, ops, step):
        return [c for c in ops.calls if c[0] == step]

    def states(self):
        out = {}
        for ln in self.record().splitlines():
            if ln.startswith("#"):
                continue
            parts = [p.strip() for p in ln.split("|")]
            out.setdefault(parts[1], parts[2])
        return out

    def assert_never_deploys(self, ops):
        for step, argv, *_ in ops.calls:
            joined = " ".join(argv)
            self.assertNotIn("push", argv, joined)
            self.assertNotIn("snapshot-live", joined)
            self.assertFalse(argv[:2] == ["git", "branch"], joined)
            self.assertNotIn("--delete", argv, joined)

    def test_all_pass_prints_but_never_runs_the_push(self):
        ops = FakeOps()
        self.assertEqual(self.gate(ops), 0)
        st = self.states()
        for step in LC.STEPS:
            self.assertEqual(st.get(step), "pass", step)
        self.assertEqual(st.get("cleanup"), "pass")
        self.assertEqual(st.get("release"), "pass")
        text = "\n".join(self.printed)
        self.assertIn(f"git push origin {SHA}:refs/heads/task/579-s", text)
        self.assertIn("snapshot-live.mjs take before-01234567", text)
        self.assertIn("compare before-01234567 after-01234567", text)
        self.assertIn("This script does not push", text)
        self.assert_never_deploys(ops)
        self.assertEqual((ops.started, ops.stopped), (1, 1))
        # each gate is its own process, in the order of the part
        order = [c[0] for c in ops.calls if c[0] in LC.STEPS]
        firsts = sorted(set(order), key=order.index)
        self.assertEqual(firsts, [s for s in LC.STEPS if s in firsts])
        self.assertNotIn(chr(0x2014), self.record() + text)

    def test_check_values_exit_3_resumed_until_0(self):
        ops = FakeOps(codes={"check_values": [3, 3, 0]})
        self.assertEqual(self.gate(ops), 0)
        cv = self.steps(ops, "check_values")
        self.assertEqual(len(cv), 3)
        self.assertNotIn("CHECK_VALUES_RESUME", cv[0][3])
        self.assertEqual(cv[1][3].get("CHECK_VALUES_RESUME"), "1")
        self.assertEqual(cv[2][3].get("CHECK_VALUES_RESUME"), "1")
        self.assertTrue(all(c[3]["CHECK_VALUES_STATE"].endswith("check-values-state.json") for c in cv))
        self.assertIn("3 tries", self.record())

    def test_check_values_three_exit_3_is_a_fail_and_stops(self):
        ops = FakeOps(codes={"check_values": [3, 3, 3, 0]})
        self.assertEqual(self.gate(ops), 1)
        self.assertEqual(len(self.steps(ops, "check_values")), 3)
        st = self.states()
        self.assertEqual(st["check_values"], "fail")
        self.assertEqual(st["check_routes"], "skip")
        self.assertEqual(st["stop"], "skip")
        self.assertEqual(ops.stopped, 1)            # the server is stopped all the same
        self.assertEqual(st.get("release"), "pass")  # and the lock released
        self.assertNotIn("git push", "\n".join(self.printed))
        self.assertIn("NOT READY", "\n".join(self.printed))

    def test_check_values_exit_1_stops_at_once(self):
        ops = FakeOps(codes={"check_values": [1]}, logs={"check_values": ["FAIL | /prices | key | page shows 1 | Supabase 2\n"]})
        self.assertEqual(self.gate(ops), 1)
        self.assertEqual(len(self.steps(ops, "check_values")), 1)
        self.assertIsNone(ops.held_asked)

    def held_log(self, pages=("/deals", "/map")):
        return "".join(f"FAIL | {p} | the floor | the page carries 0 checked numbers; its floor is 10\n" for p in pages) + \
            "ok   | /prices | k | page shows 1 | page read 1 | Supabase 1\n6456 of 6466 values match Supabase; 10 FAILED\n"

    def test_license_held_floors_showing_license_needed_pass(self):
        ops = FakeOps(codes={"check_values": [1]}, logs={"check_values": [self.held_log()]})
        self.assertEqual(self.gate(ops), 0)
        self.assertEqual(ops.held_asked, ["/deals", "/map"])
        self.assertIn("license needed", self.record())
        self.assertIn("git push origin", "\n".join(self.printed))

    def test_license_held_floor_not_showing_it_fails(self):
        ops = FakeOps(codes={"check_values": [1]}, logs={"check_values": [self.held_log()]}, held={"/map": False})
        self.assertEqual(self.gate(ops), 1)
        self.assertIn("/map", self.record())

    def test_held_floor_failures_reads_only_the_held_floors(self):
        f = LC.held_floor_failures
        self.assertEqual(f(self.held_log()), ["/deals", "/map"])
        self.assertIsNone(f(self.held_log() + "FAIL | /prices | the floor | x\n"))          # a floor not on the list
        self.assertIsNone(f(self.held_log() + "FAIL | /deals | lic|held | x\n"))           # not a floor
        self.assertIsNone(f(self.held_log() + "check-values FAILED: 3 values checked\n"))
        self.assertIsNone(f(self.held_log() + "not read | /grid | slow | not judged\n"))
        self.assertIsNone(f("ok | / | k\n"))
        self.assertEqual(len(LC.HELD_FLOOR_PAGES), 10)

    def test_db_probe_fail_stops_before_the_lock(self):
        ops = FakeOps(codes={"db_probe": [1]})
        self.assertEqual(self.gate(ops), 1)
        st = self.states()
        self.assertEqual(st["db_probe"], "fail")
        for step in LC.STEPS[LC.STEPS.index("build_lock"):]:
            self.assertEqual(st[step], "skip", step)
        self.assertEqual(self.steps(ops, "build_lock"), [])
        self.assertEqual(self.steps(ops, "worktree"), [])
        self.assertEqual(ops.started, 0)

    def test_frozen_runs_the_rest_but_prints_no_push(self):
        ops = FakeOps(codes={"freeze": [1]})
        self.assertEqual(self.gate(ops), 1)
        st = self.states()
        self.assertEqual(st["freeze"], "fail")
        self.assertEqual(st["check_csp"], "pass")
        text = "\n".join(self.printed)
        self.assertNotIn("git push", text)
        self.assertIn("wip/", text)

    def test_statement_timeout_rebuilt_once(self):
        ops = FakeOps(logs={"build": ["Supabase series: HTTP 500 canceling statement due to statement timeout\n", "ok\n"]})
        self.assertEqual(self.gate(ops), 0)
        self.assertEqual(len(self.steps(ops, "build")), 2)
        self.assertIn("statement timeout", self.record())

    def test_statement_timeout_twice_fails(self):
        t = "canceling statement due to statement timeout\n"
        ops = FakeOps(logs={"build": [t, t]})
        self.assertEqual(self.gate(ops), 1)
        self.assertEqual(self.states()["build"], "fail")

    def test_build_stopped_at_its_limit(self):
        ops = FakeOps(codes={"build": [None]})
        self.assertEqual(self.gate(ops, "--build-min", "30"), 1)
        b = self.steps(ops, "build")
        self.assertEqual(b[0][4], 1800)
        self.assertIn("stopped after 30", self.record())

    def test_suite_runs_in_the_clean_copy_without_keys(self):
        old = {k: os.environ.get(k) for k in ("SUPABASE_SERVICE_KEY", "ANTHROPIC_API_KEY", "GH_TOKEN")}
        try:
            for k in old:
                os.environ[k] = "x"
            ops = FakeOps()
            self.assertEqual(self.gate(ops), 0)
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        step, argv, cwd, env, timeout = self.steps(ops, "suite")[0]
        self.assertEqual(argv[1:], ["-m", "unittest", "discover", "-s", "tests"])
        self.assertTrue(cwd.endswith("erw-land-01234567"))
        self.assertEqual(env["ERW_LOCK_EXEMPT"], "1")
        for k in ("SUPABASE_SERVICE_KEY", "ANTHROPIC_API_KEY", "GH_TOKEN"):
            self.assertNotIn(k, env)
        wt = self.steps(ops, "worktree")[0][1]
        self.assertEqual(wt[:4], ["git", "worktree", "add", "--detach"])
        self.assertEqual(wt[-1], SHA)
        # .env.local copied into the clean copy only for the build, after the suite
        names = [c[0] for c in ops.calls]
        self.assertLess(names.index("suite"), names.index("copy"))

    def test_task_branch_in_flight_with_a_conflict_fails(self):
        ls = f"{'a' * 40}\trefs/heads/task/1-on-main\n{'b' * 40}\trefs/heads/task/2-in-flight\n"
        # fetch, is-ancestor (0: on main); fetch, is-ancestor (1: in flight), merge-tree (1: conflict)
        ops = FakeOps(ls_remote=ls, codes={"task_branches": [0, 0, 0, 1, 1]})
        self.assertEqual(self.gate(ops), 1)
        self.assertIn("conflicts with task/2-in-flight", self.record())
        self.assertEqual(self.states()["db_probe"], "skip")

    def test_task_branch_in_flight_merging_cleanly_is_named(self):
        ls = f"{'b' * 40}\trefs/heads/task/2-in-flight\n"
        ops = FakeOps(ls_remote=ls, codes={"task_branches": [0, 1, 0]})
        self.assertEqual(self.gate(ops), 0)
        self.assertIn("in flight, merging cleanly: task/2-in-flight", self.record())

    def test_main_not_merged_fails(self):
        ops = FakeOps(codes={"main_merged": [0, 1]})
        self.assertEqual(self.gate(ops), 1)
        self.assertIn("merge it first", self.record())

    def test_lock_already_held_by_the_caller_is_left_held(self):
        ops = FakeOps(lock_status=(1, "build.lock held by s589 since 2026-10-22T03:00:00Z (x)"))
        self.assertEqual(self.gate(ops, "--lock-as", "s589"), 0)
        self.assertEqual(self.steps(ops, "build_lock"), [])
        self.assertNotIn("release", self.states())

    def test_lock_not_taken_stops(self):
        ops = FakeOps(codes={"build_lock": [1]})
        self.assertEqual(self.gate(ops), 1)
        self.assertEqual(self.states()["worktree"], "skip")
        self.assertNotIn("release", self.states())

    def test_existing_worktree_is_not_removed(self):
        wt = os.path.join(self.tmp, "erw-land-01234567")
        ops = FakeOps(exists=[wt])
        self.assertEqual(self.gate(ops), 1)
        self.assertEqual(self.steps(ops, "cleanup"), [])
        self.assertEqual(self.states().get("release"), "pass")

    def test_keep_worktree(self):
        ops = FakeOps()
        self.assertEqual(self.gate(ops, "--keep-worktree"), 0)
        self.assertEqual(self.steps(ops, "cleanup"), [])

    def test_task_name_from_head_and_option(self):
        ops = FakeOps(branch="wip/579-s")
        self.assertEqual(LC.main(["--task", "579-gate"], ops=ops, root=self.tmp, main=self.main, out=self.printed.append), 0)
        self.assertIn(f"{SHA}:refs/heads/task/579-gate", "\n".join(self.printed))
        self.assertEqual(LC.task_name("HEAD", FakeOps(branch="wip/580-s"), self.tmp), "580-s")

    def test_bad_ref_is_exit_2(self):
        ops = FakeOps()
        self.assertEqual(LC.main(["--ref", "nope"], ops=ops, root=self.tmp, main=self.main, out=self.printed.append), 2)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "runs")))

    def test_record_appends_runs(self):
        self.gate(FakeOps())
        self.gate(FakeOps(codes={"freeze": [1]}))
        self.assertEqual(self.record().count("# "), 2)


class RealRunner579(unittest.TestCase):
    def test_exit_code_read_and_timeout_stops(self):
        tmp = tempfile.mkdtemp(prefix="erw579r_")
        try:
            ops = LC.Ops()
            log = os.path.join(tmp, "x", "a.out")
            self.assertEqual(ops.run("a", [sys.executable, "-c", "print('hi'); raise SystemExit(3)"], tmp, log), 3)
            self.assertIn("hi", ops.read(log))
            self.assertIsNone(ops.run("b", [sys.executable, "-c", "import time; time.sleep(30)"], tmp, log, timeout=2))
            self.assertIn("stopped after 2 s", ops.read(log))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_source_never_runs_a_push_or_a_snapshot(self):
        with open(os.path.join(ROOT, "scripts", "land_check.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn('"push"', src)
        self.assertNotIn('"snapshot-live.mjs"', src)
        self.assertNotIn("check=True", src)
        self.assertNotIn("shell=True", src)
        self.assertNotIn(chr(0x2014), src)


if __name__ == "__main__":
    unittest.main()
