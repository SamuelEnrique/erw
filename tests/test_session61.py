"""Session 61: scheduled-job reliability. warehouse/health.py's outcomes (ok, skipped, retried, failed; never a failed
job), its duplicate-start rule, the daily summary; the lock's and the network job's skip exits; and the workflows
themselves: no scheduled job opens an issue, cancels a run in progress, or runs its work outside health.py."""

import os
import sys
import unittest
from unittest import mock

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import health  # noqa: E402

WF = os.path.join(ROOT, ".github", "workflows")
SCHEDULED = ("daily-prices.yml", "latest-prices.yml", "hourly-network.yml", "roundup.yml", "weekly-vacuum.yml")


class Run(unittest.TestCase):
    def go(self, codes, retries=1, strict=False):
        seq = iter(codes)
        rows = []

        def attempt(cmd):
            c = next(seq)
            return c, ["working", "network_hourly FAILED: RuntimeError: boom" if c not in (0, 75) else
                       ("skipped: the data lock is held by home-laptop" if c == 75 else "done")], 1.0
        with mock.patch.dict(os.environ, {"GITHUB_OUTPUT": ""}):
            code, status = health.run("step", ["x"], retries=retries, wait=0, strict=strict, attempt=attempt,
                                      sleep=lambda s: None, rec=lambda *a: rows.append(a))
        return code, status, rows

    def test_outcomes(self):
        self.assertEqual(self.go([0])[:2], (0, "ok"))
        code, status, rows = self.go([75])
        self.assertEqual((code, status), (0, "skipped"))
        self.assertIn("data lock is held", rows[0][2])
        code, status, rows = self.go([1, 0])
        self.assertEqual((code, status), (0, "retried"))
        self.assertIn("boom", rows[0][2])
        code, status, rows = self.go([1, 1])
        self.assertEqual((code, status), (0, "failed"))  # recorded, and the job stays green
        self.assertIn("FAILED: RuntimeError: boom", rows[0][2])
        self.assertEqual(self.go([1], retries=0)[1], "failed")
        self.assertEqual(self.go([1, 1], strict=True)[0], 1)

    def test_reason(self):
        self.assertEqual(health.reason_of(["a", "Traceback", "ValueError: x", "exit"], True), "ValueError: x")
        self.assertEqual(health.reason_of(["a", "", "nothing new"], False), "nothing new")


class Dedupe(unittest.TestCase):
    def go(self, event, runs):
        class R:
            status_code = 200

            def json(self):
                return {"workflow_runs": runs}
        rows = []
        env = {"GITHUB_RUN_ID": "200", "GITHUB_REPOSITORY": "o/r", "GITHUB_TOKEN": "t", "GITHUB_EVENT_NAME": event, "GITHUB_OUTPUT": ""}
        with mock.patch.dict(os.environ, env):
            return health.dedupe("latest-prices.yml", 15, rec=lambda *a: rows.append(a), get=lambda *a, **k: R()), rows

    def test_schedule_yields_to_the_database(self):
        disp = {"id": 199, "event": "workflow_dispatch", "status": "completed", "conclusion": "success", "created_at": "t"}
        skipped, rows = self.go("schedule", [disp])
        self.assertTrue(skipped)
        self.assertIn("duplicate", rows[0][2])
        self.assertFalse(self.go("schedule", [dict(disp, conclusion="failure")])[0])  # a failed run does not count
        self.assertFalse(self.go("schedule", [dict(disp, event="schedule")])[0])
        self.assertTrue(self.go("workflow_dispatch", [disp])[0])
        self.assertFalse(self.go("workflow_dispatch", [dict(disp, id=201)])[0])  # a later run never makes an earlier one skip


class Summary(unittest.TestCase):
    def test_render(self):
        rows = [{"at": "2026-10-02T08:05:00+00:00", "workflow": "hourly network", "run_id": "1", "step": "network snapshot",
                 "status": "skipped", "reason": "EIA's newest hour is not complete yet"},
                {"at": "2026-10-02T09:05:00+00:00", "workflow": "hourly network", "run_id": "2", "step": "network snapshot",
                 "status": "failed", "reason": "RuntimeError: x"},
                {"at": "2026-10-02T09:15:00+00:00", "workflow": "latest prices", "run_id": "3", "step": "latest prices",
                 "status": "retried", "reason": "failed once, then passed: y"}]
        md = health.render("2026-10-02", rows)
        self.assertIn("**1 failure**", md)
        self.assertIn("| hourly network | 2 | 23 | 0 | 1 | 0 | 1 |", md)
        self.assertIn("latest prices**: 1 runs against 96 expected", md)
        self.assertIn("09:05 UTC, hourly network, network snapshot (run 2): RuntimeError: x", md)
        self.assertIn("1 x EIA's newest hour is not complete yet", md)
        self.assertNotIn("energy roundup", md.split("## Fewer")[0])  # a Friday: the weekly jobs are not expected
        self.assertIn("| energy roundup | 0 | 1 |", health.render("2026-10-04", []))  # a Sunday


class SkipExits(unittest.TestCase):
    def test_lock_held_is_a_skip_under_health(self):
        import lock
        err = SystemExit("the data lock is held by home-laptop for 'x' until 2026-10-02 12:00; not taken")
        with mock.patch.object(lock, "acquire", side_effect=err), mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}):
            with self.assertRaises(SystemExit) as c:
                lock.main(["acquire", "--task", "t"])
            self.assertEqual(c.exception.code, 75)
        with mock.patch.object(lock, "acquire", side_effect=err), mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": ""}):
            with self.assertRaises(SystemExit) as c:
                lock.main(["acquire", "--task", "t"])
            self.assertIn("held", str(c.exception.code))  # by hand: the message, a failure

    def test_network_skip_code(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import network_hourly as nh
        with mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}):
            self.assertEqual(nh.skip("x"), 75)
        with mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": ""}):
            self.assertEqual(nh.skip("x"), 0)


class Workflows(unittest.TestCase):
    def load(self, f):
        with open(os.path.join(WF, f), encoding="utf-8") as fh:
            text = fh.read()
        return text, yaml.safe_load(text)

    def test_no_issue_no_cancel_work_under_health(self):
        for f in SCHEDULED:
            text, d = self.load(f)
            self.assertNotIn("gh issue create", text, f)
            self.assertNotIn("cancel-in-progress: true", text, f)
            self.assertIn("warehouse/health.py", text, f)
        _, d = self.load("daily-prices.yml")
        steps = {s.get("name"): s for s in d["jobs"]["refresh"]["steps"]}
        self.assertIn("--retries 0", steps["Pull, validate, rebuild coverage"]["run"])  # never a second digest
        self.assertIn("always()", steps["Write yesterday's health summary"]["if"])
        self.assertIn("note-skip", d["jobs"])


if __name__ == "__main__":
    unittest.main()
