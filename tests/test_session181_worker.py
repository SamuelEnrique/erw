"""Session 181, part 3: the findings worker as a service.

The worker (warehouse/analysis/findings/worker.py) is one instance only (a lock file with the process id, a stale lock
recovered), survives a failed turn, stops cleanly on a stop file with the request in hand finished, puts back a request
it left running, records its state for --status, and passes the scanner's daily request to findings_scanner. Its text
names no model and no data lock. The two PowerShell scripts that register and remove the scheduled task hold no secret
and leave one task; scripts/queue_analysis_request.py queues one request through the page's database function and never
prints the token. No test reaches the network and none registers anything.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
REGISTER = os.path.join(ROOT, "scripts", "register_findings_worker.ps1")
UNREGISTER = os.path.join(ROOT, "scripts", "unregister_findings_worker.ps1")
QUEUE_SCRIPT = os.path.join(ROOT, "scripts", "queue_analysis_request.py")
MAIN_VENV = "C:\\Users\\lossa\\Documents\\erw\\.venv\\Scripts\\python.exe"
OWN = [os.path.join(FIND, "worker.py"), REGISTER, UNREGISTER, QUEUE_SCRIPT, os.path.abspath(__file__)]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def src(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def row(rid, finding="queue_divorce", status="queued", **more):
    return {"id": rid, "kind": "run", "finding": finding, "params": {}, "status": status, "asked_at": "2026-10-10T17:00:00Z", "note": "", **more}


def fake_run(name, params, in_dir=None, card_dir=None, download_dir=None, log=print):
    return "nowhere.json", {"card_id": f"{name}__fake", "title": "A CARD", "numbers": {"n": 1.0}}


class WorkerCase(unittest.TestCase):
    def setUp(self):
        self.worker = load("findings_worker_181", os.path.join(FIND, "worker.py"))
        self.d = tempfile.mkdtemp(prefix="erw181w-")
        self.q = os.path.join(self.d, "queue")
        os.makedirs(self.q)
        self.sleeps = []
        self.worker._sleep = self.sleeps.append

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def put(self, r):
        with open(os.path.join(self.q, r["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(r, f)

    def get(self, rid):
        with open(os.path.join(self.q, rid + ".json"), encoding="utf-8") as f:
            return json.load(f)

    def args(self, *more):
        return [*more, "--local-dir", self.q, "--in-dir", self.d, "--card-dir", self.d, "--download-dir", self.d, "--machine", "test"]

    def lock_path(self):
        return os.path.join(self.q, "findings_worker.lock")

    def state(self):
        with open(os.path.join(self.q, "findings_worker.state.json"), encoding="utf-8") as f:
            return json.load(f)


class TestOneInstance(WorkerCase):
    def test_a_second_worker_is_refused_while_the_first_is_alive(self):
        w = self.worker
        self.put(row("r1"))
        with open(self.lock_path(), "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "started_at": "2026-10-10T17:00:00Z", "machine": "test", "proc_started": w.proc_started(os.getpid())}, f)
        lines = []
        with mock.patch.object(w, "log", lines.append), mock.patch.object(w.run_finding, "run", fake_run):
            self.assertEqual(w.main(self.args("--once")), 0)
        self.assertEqual(len(lines), 1)
        self.assertIn(f"another worker holds the lock, pid {os.getpid()}", lines[0])
        self.assertEqual(self.get("r1")["status"], "queued")          # the refused worker took nothing
        self.assertEqual(w.read_lock(self.lock_path())["pid"], os.getpid())   # and left the lock

    def test_a_stale_lock_is_recovered_and_released_at_the_end(self):
        w = self.worker
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        p.wait()
        self.assertFalse(w.pid_alive(p.pid))
        self.put(row("r1"))
        with open(self.lock_path(), "w", encoding="utf-8") as f:
            json.dump({"pid": p.pid, "started_at": "2026-10-09T01:00:00Z", "machine": "test"}, f)
        lines = []
        with mock.patch.object(w, "log", lines.append), mock.patch.object(w.run_finding, "run", fake_run):
            self.assertEqual(w.main(self.args("--once")), 0)
        self.assertTrue(any("a stale lock was recovered" in ln for ln in lines), lines)
        self.assertEqual(self.get("r1")["status"], "done")
        self.assertFalse(os.path.exists(self.lock_path()))

    def test_a_live_process_that_began_at_another_time_is_not_the_holder(self):
        w = self.worker
        began = w.proc_started(os.getpid())
        if began is None:
            raise unittest.SkipTest("a process's start time is read on Windows only")
        self.assertTrue(w.holder_alive({"pid": os.getpid(), "proc_started": began}))
        self.assertFalse(w.holder_alive({"pid": os.getpid(), "proc_started": began - 86400}))   # the id of a process before the restart
        self.assertTrue(w.pid_alive(os.getpid()))
        self.assertFalse(w.pid_alive(0))
        self.assertFalse(w.pid_alive("x"))

    def test_an_unreadable_lock_is_stale(self):
        w = self.worker
        with open(self.lock_path(), "w", encoding="utf-8") as f:
            f.write("not json")
        ok, note = w.take_lock(self.lock_path(), "test")
        self.assertTrue(ok)
        self.assertIn("stale lock", note)
        w.release_lock(self.lock_path())
        self.assertFalse(os.path.exists(self.lock_path()))


class TestRequests(WorkerCase):
    def test_once_takes_a_stubbed_request_end_to_end(self):
        w = self.worker
        self.put(row("r1", params={"first_year": "2010"}))
        seen = []

        def run(name, params, *a, **k):
            seen.append((name, params))
            return fake_run(name, params)
        with mock.patch.object(w, "log", lambda m: None), mock.patch.object(w.run_finding, "run", run):
            self.assertEqual(w.main(self.args("--once")), 0)
        got = self.get("r1")
        self.assertEqual(seen, [("queue_divorce", {"first_year": "2010"})])
        self.assertEqual((got["status"], got["card_id"], got["machine"]), ("done", "queue_divorce__fake", "test"))
        self.assertEqual(got["card"]["numbers"], {"n": 1.0})
        self.assertTrue(got["started_at"] <= got["done_at"])
        st = self.state()
        self.assertEqual((st["done"], st["failed"], st["turns"], st["pid"]), (1, 0, 1, os.getpid()))
        self.assertEqual((st["last_request"]["id"], st["last_request"]["finding"], st["last_request"]["status"]), ("r1", "queue_divorce", "done"))
        self.assertIsNotNone(st["heartbeat_at"])
        self.assertEqual(len(w.LocalDir(self.q).rows()), 1)            # the state file is not read as a request

    def test_the_scanners_daily_request_goes_to_the_scanner_and_ends_with_its_note(self):
        w = self.worker
        self.put(row("s1", finding="scanner_daily", params={"day": "2026-10-10"}))
        calls = []
        fake = types.ModuleType("findings_scanner")

        def daily_request(params, in_dir, log):
            calls.append((params, in_dir))
            log("scanning")
            return {"flags": 9, "drafts": 4, "loaded": 4, "note": "9 flags, 4 drafts loaded " + "x" * 300}
        fake.daily_request = daily_request
        ran = []
        with mock.patch.dict(sys.modules, {"findings_scanner": fake}), mock.patch.object(w, "log", lambda m: None), \
                mock.patch.object(w.run_finding, "run", lambda *a, **k: ran.append(a)):
            self.assertEqual(w.main(self.args("--once")), 0)
        got = self.get("s1")
        self.assertEqual(calls, [({"day": "2026-10-10"}, self.d)])
        self.assertEqual(ran, [])                                      # never passed to run_finding
        self.assertEqual(got["status"], "done")
        self.assertTrue(got["note"].startswith("9 flags, 4 drafts loaded"))
        self.assertEqual(len(got["note"]), 200)
        self.assertNotIn("card", got)

    def test_a_scanner_that_fails_marks_the_row_failed_with_the_plain_reason(self):
        w = self.worker
        self.put(row("s1", finding="scanner_daily"))
        fake = types.ModuleType("findings_scanner")

        def daily_request(params, in_dir, log):
            raise w.common.NoData("table coverage is not here")
        fake.daily_request = daily_request
        with mock.patch.dict(sys.modules, {"findings_scanner": fake}), mock.patch.object(w, "log", lambda m: None):
            self.assertEqual(w.main(self.args("--once")), 0)
        got = self.get("s1")
        self.assertEqual(got["status"], "failed")
        self.assertIn("not on the data machine", got["note"])
        self.assertEqual(self.state()["failed"], 1)

    def test_a_request_left_running_by_a_dead_worker_is_put_back_and_taken(self):
        w = self.worker
        self.put(row("old", status="running", machine="test", started_at="2026-10-09T01:00:00Z"))
        self.put(row("theirs", status="running", machine="another", started_at="2026-10-09T01:00:00Z"))
        lines = []
        with mock.patch.object(w, "log", lines.append), mock.patch.object(w.run_finding, "run", fake_run):
            self.assertEqual(w.main(self.args("--once")), 0)
        self.assertTrue(any("put back to queued" in ln for ln in lines), lines)
        self.assertEqual(self.get("old")["status"], "done")
        self.assertEqual(self.get("theirs")["status"], "running")      # another machine's request is not ours to move

    def test_a_request_running_for_a_minute_is_left_alone(self):
        w = self.worker
        self.put(row("fresh", status="running", machine="test", started_at=w.now()))
        with mock.patch.object(w, "log", lambda m: None), mock.patch.object(w.run_finding, "run", fake_run):
            self.assertEqual(w.main(self.args("--once")), 0)
        self.assertEqual(self.get("fresh")["status"], "running")


class TestItStaysUpAndStops(WorkerCase):
    def test_a_failed_turn_does_not_end_the_loop_and_the_wait_doubles_then_resets(self):
        w = self.worker
        self.put(row("r1"))
        stop_file = os.path.join(self.q, "findings_worker.stop")
        turns = []

        class Flaky(w.LocalDir):
            def queued(inner):
                turns.append(len(self.sleeps))
                if len(turns) == 1:
                    raise ConnectionError("no route to host")
                if len(turns) == 3:
                    open(stop_file, "w").close()
                return super().queued()
        lines = []
        with mock.patch.object(w, "LocalDir", Flaky), mock.patch.object(w, "log", lines.append), mock.patch.object(w.run_finding, "run", fake_run):
            self.assertEqual(w.main(self.args("--loop", "1")), 0)
        self.assertEqual(len(turns), 3)
        self.assertEqual(turns, [0, 2, 3])                             # 2 seconds after the failure, then 1 again
        self.assertTrue(any("turn failed: ConnectionError: no route to host; the next try in 2 seconds" in ln for ln in lines), lines)
        self.assertEqual(self.get("r1")["status"], "done")
        self.assertTrue(any(ln.startswith("stopped (the stop file") for ln in lines), lines)
        self.assertFalse(os.path.exists(stop_file))                    # the stop is consumed
        self.assertFalse(os.path.exists(self.lock_path()))             # and the lock released
        st = self.state()
        self.assertEqual(st["turns"], 3)
        self.assertIn("ConnectionError", st["last_error"]["error"])

    def test_the_wait_after_failures_is_never_longer_than_fifteen_minutes(self):
        w = self.worker
        stop_file = os.path.join(self.q, "findings_worker.stop")
        waits, n = [], [0]

        class Down(w.LocalDir):
            def queued(inner):
                n[0] += 1
                if n[0] == 14:
                    open(stop_file, "w").close()
                raise TimeoutError("Supabase did not answer")
        with mock.patch.object(w, "LocalDir", Down), mock.patch.object(w, "log", lambda m: None), \
                mock.patch.object(w, "wait", lambda seconds, should_stop: waits.append(seconds)):
            self.assertEqual(w.main(self.args("--loop", "60")), 0)
        self.assertEqual(waits[:5], [120, 240, 480, 900, 900])
        self.assertEqual(max(waits), w.MAX_WAIT)
        self.assertEqual(n[0], 14)

    def test_a_stop_finishes_the_request_in_hand_and_leaves_the_rest_queued(self):
        w = self.worker
        self.put(row("a1", asked_at="2026-10-10T17:00:00Z"))
        self.put(row("a2", asked_at="2026-10-10T17:01:00Z"))
        stop_file = os.path.join(self.q, "findings_worker.stop")

        def run(name, params, *a, **k):
            open(stop_file, "w").close()                               # the stop arrives while the first request runs
            return fake_run(name, params)
        with mock.patch.object(w, "log", lambda m: None), mock.patch.object(w.run_finding, "run", run):
            self.assertEqual(w.main(self.args("--loop", "60")), 0)
        self.assertEqual(self.get("a1")["status"], "done")
        self.assertEqual(self.get("a2")["status"], "queued")
        self.assertEqual(self.sleeps, [])                              # it did not wait a minute before stopping

    def test_a_stop_file_older_than_the_worker_is_removed_and_ignored(self):
        w = self.worker
        self.put(row("r1"))
        stop_file = os.path.join(self.q, "findings_worker.stop")
        open(stop_file, "w").close()
        lines = []
        with mock.patch.object(w, "log", lines.append), mock.patch.object(w.run_finding, "run", fake_run):
            self.assertEqual(w.main(self.args("--once")), 0)
        self.assertEqual(self.get("r1")["status"], "done")
        self.assertTrue(any("an old stop file was removed" in ln for ln in lines))

    def test_the_wait_is_in_one_second_steps(self):
        w = self.worker
        flag = []
        w.wait(5, lambda: len(self.sleeps) >= 2 or bool(flag))
        self.assertEqual(self.sleeps, [1.0, 1.0])

    def test_the_signal_handlers_are_put_back(self):
        import signal
        w = self.worker
        before = signal.getsignal(signal.SIGINT)
        with mock.patch.object(w, "log", lambda m: None):
            self.assertEqual(w.main(self.args("--once")), 0)
        self.assertIs(signal.getsignal(signal.SIGINT), before)


class TestStatus(WorkerCase):
    def run_status(self):
        w = self.worker
        lines = []
        a = types.SimpleNamespace(local_dir=self.q, lock_file=None, state_file=None, stop_file=None)
        with mock.patch.object(w, "task_state", lambda: "not registered"):
            self.assertEqual(w.status(a, lines.append), 0)
        return lines

    def test_status_before_any_worker_ran(self):
        self.put(row("r1"))
        self.put(row("r2"))
        lines = self.run_status()
        self.assertEqual(lines[0], 'scheduled task "ERW findings worker": not registered')
        self.assertTrue(lines[1].startswith("process: not running (no lock"), lines)
        self.assertIn("heartbeat: none recorded", lines[2])
        self.assertEqual(lines[-1], f"queued: 2 request(s) in the files of {self.q}")

    def test_status_after_a_worker_ran_and_while_one_is_alive(self):
        w = self.worker
        self.put(row("r1"))
        with mock.patch.object(w, "log", lambda m: None), mock.patch.object(w.run_finding, "run", fake_run):
            w.main(self.args("--once"))
        with open(self.lock_path(), "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "started_at": "2026-10-10T17:00:00Z", "machine": "test", "proc_started": w.proc_started(os.getpid())}, f)
        lines = self.run_status()
        self.assertIn(f"process: alive, pid {os.getpid()} on test", lines[1])
        self.assertIn("1 done, 0 failed", lines[2])
        self.assertTrue(lines[3].startswith("last request: r1 queue_divorce done at "), lines)
        self.assertEqual(lines[-1], f"queued: 0 request(s) in the files of {self.q}")

    def test_the_status_flag_answers_zero_and_takes_no_lock(self):
        w = self.worker
        self.put(row("r1"))
        with mock.patch.object(w, "task_state", lambda: "not registered"), mock.patch("builtins.print") as p:
            self.assertEqual(w.main(["--status", "--local-dir", self.q]), 0)
        self.assertTrue(any("queued: 1 request(s)" in str(c) for c in p.call_args_list))
        self.assertFalse(os.path.exists(self.lock_path()))
        self.assertEqual(self.get("r1")["status"], "queued")

    def test_a_queue_that_cannot_be_asked_is_one_line_not_a_failure(self):
        w = self.worker
        lines = []
        a = types.SimpleNamespace(local_dir=None, lock_file=os.path.join(self.d, "l"), state_file=os.path.join(self.d, "s"), stop_file=None)

        class NoKey:
            def __init__(inner):
                raise SystemExit("the worker needs SUPABASE_URL and SUPABASE_SERVICE_KEY (.env or the environment)")
        with mock.patch.object(w, "task_state", lambda: "not registered"), mock.patch.object(w, "Supabase", NoKey):
            self.assertEqual(w.status(a, lines.append), 0)
        self.assertTrue(lines[-1].startswith("queued: not asked ("), lines)


class TestTheText(unittest.TestCase):
    def test_the_worker_names_no_model_and_takes_no_data_lock(self):
        text = src(os.path.join(FIND, "worker.py"))
        low = text.lower()
        for word in ("anthropic", "api.anthropic.com", "openai", "claude"):
            self.assertNotIn(word, low)
        for call in ("lock.acquire", "lock.run(", "lock.require", "lock.renew", "lock.py run", "lock.py acquire"):
            self.assertNotIn(call, text)
        self.assertIn("is never taken", text)
        self.assertIn('SCANNER = "scanner_daily"', text)
        self.assertIn('importlib.import_module("findings_scanner")', text)
        self.assertIn("os.O_CREAT | os.O_EXCL", text)

    def test_the_register_script_holds_no_secret_and_leaves_one_task(self):
        text = src(REGISTER)
        for secret in ("SERVICE_KEY", "ANON_KEY", "_TOKEN", "API_KEY", "DB_URL", "-Password", "eyJ"):
            self.assertNotIn(secret, text)
        self.assertIn('$TaskName = "ERW findings worker"', text)
        self.assertIn("Register-ScheduledTask -TaskName $TaskName", text)
        self.assertIn("-Force", text)                                  # registering twice replaces: one task
        self.assertIn("-MultipleInstances IgnoreNew", text)
        self.assertIn("-RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)", text)
        self.assertIn("-ExecutionTimeLimit (New-TimeSpan -Seconds 0)", text)
        self.assertIn("-AtLogOn", text)
        self.assertIn("-AtStartup", text)
        self.assertIn("S4U", text)
        self.assertIn("IsInRole", text)                                # the startup trigger only from an elevated shell
        self.assertIn('[string]$Root = "C:\\Users\\lossa\\Documents\\erw"', text)
        self.assertIn('Join-Path $Root ".venv\\Scripts\\python.exe"', text)
        self.assertIn("warehouse\\analysis\\findings\\worker.py", text)
        self.assertIn("' --loop ' + $LoopSeconds", text)
        self.assertIn("[int]$LoopSeconds = 60", text)
        self.assertIn('Join-Path $Root "runs\\findings_worker.log"', text)
        self.assertIn("[switch]$DryRun", text)
        self.assertLess(text.index("if ($DryRun)"), text.index("Register-ScheduledTask -TaskName $TaskName"))
        self.assertEqual(text.count("Register-ScheduledTask -TaskName"), 1)

    def test_the_unregister_script_is_safe_when_the_task_is_absent(self):
        text = src(UNREGISTER)
        self.assertIn('$TaskName = "ERW findings worker"', text)
        self.assertIn("nothing to remove", text)
        self.assertLess(text.index("nothing to remove"), text.index("Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false"))
        self.assertNotIn("Remove-Item -Recurse", text)
        for secret in ("SERVICE_KEY", "_TOKEN", "API_KEY"):
            self.assertNotIn(secret, text)

    def test_the_dry_run_of_the_register_script_registers_nothing_and_names_the_main_copy(self):
        if os.name != "nt" or not shutil.which("powershell") or not os.path.exists(MAIN_VENV):
            raise unittest.SkipTest("Windows with the main copy's venv only")
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", REGISTER, "-DryRun"], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("DRY RUN: nothing was registered.", r.stdout)
        self.assertIn(MAIN_VENV, r.stdout)
        self.assertIn("warehouse\\analysis\\findings\\worker.py --loop 60 >>", r.stdout)
        self.assertIn("runs\\findings_worker.log", r.stdout)
        self.assertNotIn("REGISTERED:", r.stdout)

    def test_no_em_dash_in_this_parts_files(self):
        for p in OWN:
            self.assertNotIn(chr(0x2014), src(p), p)
            self.assertNotIn(chr(0x2013), src(p), p)


class TestQueueScript(unittest.TestCase):
    TOKEN = "test-token-not-a-real-one-0123456789abcdef"
    KEY = "test-anon-key-not-a-real-one"

    def setUp(self):
        self.script = load("queue_analysis_request_181", QUEUE_SCRIPT)
        self.env = mock.patch.dict(os.environ, {"SUPABASE_URL": "https://example.invalid/rest/v1/", "SUPABASE_ANON_KEY": self.KEY, "INTERNAL_COSTS_TOKEN": self.TOKEN})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_the_dry_run_sends_nothing_and_prints_no_secret(self):
        lines = []

        def post(*a, **k):
            raise AssertionError("a dry run sends nothing")
        self.assertEqual(self.script.main(["--dry-run"], lines.append, post), 0)
        text = "\n".join(lines)
        self.assertNotIn(self.TOKEN, text)
        self.assertNotIn(self.KEY, text)
        self.assertIn("POST https://example.invalid/rest/v1/rpc/analysis_request", text)
        self.assertIn('"p_finding": "queue_divorce"', text)
        self.assertIn('"p_kind": "run"', text)
        self.assertIn('first_year\\": \\"2010', text)                  # the proof request never rewrites the default card

    def test_it_calls_the_pages_function_and_watches_the_row(self):
        sent = []

        class Answer:
            status_code = 200
            text = ""

            def __init__(inner, body):
                inner.body = body

            def json(inner):
                return inner.body

        def post(url, json=None, headers=None, timeout=None):
            sent.append((url, json, headers))
            if url.endswith("/rpc/analysis_request"):
                return Answer({"ok": True, "id": "20261010T180000Z-abc123"})
            return Answer([{"id": "20261010T180000Z-abc123", "status": "done", "asked_at": "2026-10-10T18:00:00Z", "started_at": "2026-10-10T18:00:20Z",
                            "done_at": "2026-10-10T18:00:31Z", "machine": "SamuelOldLaptop", "card_id": "queue_divorce", "note": ""}])
        lines = []
        self.assertEqual(self.script.main(["--watch", "30"], lines.append, post), 0)
        url, body, headers = sent[0]
        self.assertEqual(url, "https://example.invalid/rest/v1/rpc/analysis_request")
        self.assertEqual(body["p_token"], self.TOKEN)                  # in the body, as the site's route sends it
        self.assertEqual((body["p_kind"], body["p_finding"]), ("run", "queue_divorce"))
        self.assertEqual(json.loads(body["p_params"]), {"first_year": "2010", "last_year": "2020"})
        self.assertEqual(headers["apikey"], self.KEY)
        self.assertTrue(sent[1][0].endswith("/rpc/analysis_requests_list"))
        text = "\n".join(lines)
        self.assertNotIn(self.TOKEN, text)
        self.assertNotIn(self.KEY, text)
        self.assertIn("queued: request 20261010T180000Z-abc123", text)
        self.assertIn("done: asked 2026-10-10T18:00:00Z, started 2026-10-10T18:00:20Z, ended 2026-10-10T18:00:31Z, by SamuelOldLaptop", text)
        self.assertIn("card: queue_divorce", text)

    def test_an_input_that_is_not_a_choice_is_refused_before_anything_is_sent(self):
        lines = []

        def post(*a, **k):
            raise AssertionError("nothing is sent")
        self.assertEqual(self.script.main(["--param", "first_year=1492"], lines.append, post), 2)
        self.assertEqual(self.script.main(["--finding", "no_such_finding"], lines.append, post), 2)
        self.assertEqual(self.script.main(["--param", "colour=blue"], lines.append, post), 2)

    def test_a_named_input_replaces_the_proof_request(self):
        lines = []
        self.assertEqual(self.script.main(["--dry-run", "--param", "last_year=2020"], lines.append, None), 0)
        self.assertIn('first_year\\": \\"2000', " ".join(lines))        # only what was named; the rest are the defaults

    def test_a_day_that_is_used_up_is_said_plainly(self):
        class Answer:
            status_code = 200
            text = ""

            def json(inner):
                return {"ok": False, "reason": "day", "requests_today": 24}
        lines = []
        self.assertEqual(self.script.main([], lines.append, lambda *a, **k: Answer()), 1)
        self.assertIn("the 24 requests of this UTC day are used", lines[-1])


if __name__ == "__main__":
    unittest.main()
