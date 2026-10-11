"""Session 188: the precheck every session runs first (scripts/precheck.py).

Energy Research Warehouse (ERW). docs/machines.md, "Continuous work". What is held to:

  each of the six checks passes and fails for the reason it gives, on stand-ins: no git command, no claude command,
    no request and no file of this machine is used;
  the claude check asks for the sign-in status only: it starts no session and sends no prompt;
  no value of a key is ever in a line, a reason or the report: names only;
  a pass puts the machine on duty, a dry run does not; a failure writes the report, sends one line of at most 300
    characters through the injected sender, exits 1, and never waits; a line that cannot be sent is said in the report;
  the scripts need only the standard library at import, and the documents and the chain template name the precheck.

No test here sends anything, pushes anything or reaches a network; the environment is read, never set.

    python -m unittest tests.test_session188_precheck -v
"""

import datetime as dt
import json
import os
import re
import sys
import tempfile
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import duty  # noqa: E402
import precheck  # noqa: E402

UTC = dt.timezone.utc
EM = chr(0x2014)
NOW = dt.datetime(2026, 10, 11, 7, 5, tzinfo=UTC)
SECRET = "s3cr3t-value-never-shown"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def envs(**kv):
    return lambda name: kv.get(name, "")


class Runner:
    """A stand-in for a command: answers by the command's second word, and keeps what it was asked."""

    def __init__(self, **answers):
        self.answers, self.calls = answers, []

    def __call__(self, cmd, cwd=None, timeout=60, env=None):
        self.calls.append((list(cmd), timeout, env))
        return self.answers.get(cmd[1], (1, ""))


class TheChecks(unittest.TestCase):
    def test_github_credentials_are_found_by_name_and_never_read_out(self):
        run = Runner(config=(0, "manager\n"), remote=(0, "https://github.com/SamuelEnrique/erw.git"))
        ok, why = precheck.check_github_credentials(env=envs(GH_TOKEN=SECRET), run=run)
        self.assertTrue(ok)
        self.assertIn("GH_TOKEN set", why)
        self.assertIn('credential helper is "manager"', why)
        self.assertNotIn(SECRET, why)
        ok, why = precheck.check_github_credentials(env=envs(), run=Runner(config=(1, ""), remote=(0, "git@github.com:SamuelEnrique/erw.git")))
        self.assertEqual((ok, why), (True, "origin is an ssh address"))
        ok, why = precheck.check_github_credentials(env=envs(), run=Runner(config=(1, ""), remote=(0, "https://github.com/SamuelEnrique/erw.git")))
        self.assertFalse(ok)
        self.assertIn("no GH_TOKEN or GITHUB_TOKEN", why)

    def test_the_push_is_a_dry_run_to_the_machines_own_ref_and_cannot_ask_at_the_keyboard(self):
        run = Runner(push=(0, "To https://github.com/SamuelEnrique/erw.git\n * [new branch]      HEAD -> wip/precheck-old-laptop"))
        ok, why = precheck.check_push_dry_run("Old Laptop", run=run)
        self.assertTrue(ok)
        cmd, timeout, env = run.calls[0]
        self.assertEqual(cmd, ["git", "push", "--dry-run", "origin", "HEAD:refs/heads/wip/precheck-old-laptop"])
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        self.assertLessEqual(timeout, 120, "the dry run must not wait for a person")
        self.assertIn("wip/precheck-old-laptop", why)
        self.assertIn("creates nothing", why)
        ok, why = precheck.check_push_dry_run("x", run=Runner(push=(128, "remote: Invalid username or token.\nfatal: Authentication failed for 'https://github.com/SamuelEnrique/erw.git/'")))
        self.assertFalse(ok)
        self.assertIn("exit 128", why)
        self.assertIn("Authentication failed", why)
        ok, why = precheck.check_push_dry_run("x", run=Runner(push=(124, "no answer in 90 seconds")))
        self.assertFalse(ok)
        self.assertIn("no answer in 90 seconds", why)

    def test_claude_is_asked_for_its_status_only_and_no_prompt_is_sent(self):
        run = Runner(auth=(0, json.dumps({"loggedIn": True, "authMethod": "claude.ai", "email": "someone@example.invalid", "orgName": "An Org"})))
        ok, why = precheck.check_claude_signed_in(run=run, env=envs(), which=lambda n: "/bin/claude")
        self.assertEqual((ok, why), (True, "claude auth status: signed in (claude.ai)"))
        self.assertEqual(run.calls[0][0], ["/bin/claude", "auth", "status", "--json"])
        self.assertEqual(len(run.calls), 1)
        for word in ("-p", "--print", "--continue", "--resume"):
            self.assertNotIn(word, run.calls[0][0], "the check must not start a session")
        self.assertNotIn("example.invalid", why, "the account is not read out")
        ok, why = precheck.check_claude_signed_in(run=Runner(auth=(1, '{"loggedIn": false}')), env=envs(), which=lambda n: "/bin/claude")
        self.assertFalse(ok)
        self.assertIn("not signed in", why)
        ok, why = precheck.check_claude_signed_in(run=run, env=envs(), which=lambda n: None)
        self.assertFalse(ok)
        self.assertIn("not on PATH", why)

    def test_an_older_claude_is_read_from_its_credentials_file_or_the_environment(self):
        old = Runner(auth=(1, "error: unknown command 'auth'"))
        with tempfile.TemporaryDirectory() as home:
            ok, why = precheck.check_claude_signed_in(run=old, env=envs(), home=home, which=lambda n: "claude")
            self.assertFalse(ok)
            ok, why = precheck.check_claude_signed_in(run=old, env=envs(ANTHROPIC_API_KEY=SECRET), home=home, which=lambda n: "claude")
            self.assertTrue(ok)
            self.assertIn("ANTHROPIC_API_KEY is set", why)
            self.assertNotIn(SECRET, why)
            os.makedirs(os.path.join(home, ".claude"))
            with open(os.path.join(home, ".claude", ".credentials.json"), "w", encoding="utf-8") as f:
                json.dump({"claudeAiOauth": {"accessToken": SECRET}}, f)
            ok, why = precheck.check_claude_signed_in(run=old, env=envs(), home=home, which=lambda n: "claude")
            self.assertTrue(ok)
            self.assertIn("credentials file is present", why)
            self.assertNotIn(SECRET, why)

    def test_the_role_file_must_be_there_and_name_a_machine_and_a_role(self):
        with tempfile.TemporaryDirectory() as state:
            ok, why = precheck.check_role_file(state)
            self.assertFalse(ok)
            self.assertIn("absent", why)
            p = os.path.join(state, "machine.json")
            for text, word in (("{not json", "cannot be read"), ('{"name": "x"}', "data or code"), ('{"name": "", "role": "code"}', "data or code"),
                               ('{"name": "x", "role": "admin"}', "data or code"), ("[1, 2]", "cannot be read")):
                with open(p, "w", encoding="utf-8") as f:
                    f.write(text)
                ok, why = precheck.check_role_file(state)
                self.assertFalse(ok, text)
                self.assertIn(word, why, text)
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"name": "samueloldlaptop", "role": "code"}, f)
            self.assertEqual(precheck.check_role_file(state), (True, "samueloldlaptop is a code machine"))

    def test_the_keys_are_the_setup_scripts_lists_and_the_alerts_two_and_only_names_are_said(self):
        setup = src("scripts", "setup.sh")
        for k in precheck.ROLE_KEYS["code"]:
            self.assertIn(k, setup.split("need=(", 1)[1].split(")", 1)[0])
        for k in set(precheck.ROLE_KEYS["data"]) - set(precheck.ROLE_KEYS["code"]):
            self.assertIn(k, setup.split('[ "$role" = data ] && need+=(', 1)[1].split(")", 1)[0])
        self.assertEqual(precheck.ALERT_KEYS, ("RESEND_API_KEY", "DIGEST_RECIPIENTS"))
        full = {k: SECRET for k in precheck.ROLE_KEYS["data"] + precheck.ALERT_KEYS}
        ok, why = precheck.check_env_keys("data", env=envs(**full))
        self.assertEqual((ok, why), (True, "10 keys a data machine needs are set (values not shown)"))
        ok, why = precheck.check_env_keys("code", env=envs(**full))
        self.assertEqual((ok, why), (True, "5 keys a code machine needs are set (values not shown)"))
        less = {k: v for k, v in full.items() if k not in ("SUPABASE_SERVICE_KEY", "DIGEST_RECIPIENTS")}
        ok, why = precheck.check_env_keys("code", env=envs(**less))
        self.assertFalse(ok)
        self.assertIn("SUPABASE_SERVICE_KEY, DIGEST_RECIPIENTS", why)
        self.assertNotIn(SECRET, why)
        ok, why = precheck.check_env_keys(None, env=envs(**full))
        self.assertFalse(ok)
        self.assertIn("role is not known", why)

    def test_the_daily_cap_is_read_as_the_budget_reads_it(self):
        asked = []

        def spend(day, path=None, get=None):  # warehouse/health.py's model_spend: the ledger here, then Supabase's copy
            asked.append((day, path))
            get("https://x.invalid/rest/v1/events")
            return 0.42, 7
        health = types.SimpleNamespace(MODEL_CAP_DEFAULT=1.00, LEDGER="api_cost_ledger", model_spend=spend)
        answer = lambda code: (lambda *a, **k: types.SimpleNamespace(status_code=code))  # noqa: E731
        with tempfile.TemporaryDirectory() as d:
            absent = os.path.join(d, "api_cost_ledger.csv")
            ok, why = precheck.check_daily_cap(env=envs(), day="2026-10-11", health=health, ledger=absent, get=answer(200))
            self.assertTrue(ok)
            self.assertIn("USD 1.00 a UTC day (the default: DAILY_MODEL_USD is not set)", why)
            self.assertIn("USD 0.42 spent today in 7 calls", why)
            self.assertIn("Supabase's copy of the ledger", why)
            self.assertEqual(asked[0], ("2026-10-11", absent))
            ok, why = precheck.check_daily_cap(env=envs(DAILY_MODEL_USD="2.5"), day="2026-10-11", health=health, ledger=absent, get=answer(200))
            self.assertTrue(ok)
            self.assertIn("USD 2.50 a UTC day (DAILY_MODEL_USD)", why)
            for bad in ("a dollar", "-1", "1,00"):
                ok, why = precheck.check_daily_cap(env=envs(DAILY_MODEL_USD=bad), day="2026-10-11", health=health, ledger=absent, get=answer(200))
                self.assertEqual((ok, why), (False, "DAILY_MODEL_USD is set but is not a number of dollars"), bad)
            # neither Supabase's copy nor a ledger file on the machine: nothing was read, so nothing is known
            ok, why = precheck.check_daily_cap(env=envs(), day="2026-10-11", health=health, ledger=absent, get=answer(503))
            self.assertFalse(ok)
            self.assertIn("could not be read", why)
            with open(absent, "w", encoding="utf-8") as f:
                f.write("event_id,ts_utc,step,session,usd\n")
            ok, why = precheck.check_daily_cap(env=envs(), day="2026-10-11", health=health, ledger=absent, get=answer(503))
            self.assertTrue(ok)
            self.assertIn("this machine's ledger file", why)
            self.assertNotIn("Supabase's copy", why)

            def broken(day, path=None, get=None):
                raise OSError("the ledger is locked")
            health.model_spend = broken
            ok, why = precheck.check_daily_cap(env=envs(), day="2026-10-11", health=health, ledger=absent, get=answer(200))
            self.assertFalse(ok)
            self.assertIn("the ledger is locked", why)

    def test_the_cap_check_reads_what_health_py_names(self):
        h = src("warehouse", "health.py")
        for name in ("MODEL_CAP_DEFAULT = 1.00", 'LEDGER = "api_cost_ledger"', "def model_spend(day, session=None, path=None, get=requests.get):", 'env("DAILY_MODEL_USD")'):
            self.assertIn(name, h)


def passing():
    return [(n, (lambda n=n: (True, f"{n} is fine"))) for n in precheck.CHECKS]


class ThePrecheck(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.state = os.path.join(self.dir.name, ".erw")
        os.makedirs(self.state)
        with open(os.path.join(self.state, "machine.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "Test Laptop", "role": "code"}, f)
        self.reports = os.path.join(self.dir.name, "runs", "precheck")
        self.sent, self.marked, self.printed = [], [], []

    def tearDown(self):
        self.dir.cleanup()

    def run_it(self, checks, **kw):
        def send(subject, line, dry_run=False):
            self.sent.append((subject, line, dry_run))
            return 2

        def on_duty(name, what, hours, state=None):
            self.marked.append((name, what, hours, state))
            return f"{name} is on duty"
        kw.setdefault("send", send)
        kw.setdefault("on_duty", on_duty)
        return precheck.precheck("session 900", checks=checks, state=self.state, report_dir=self.reports, now=NOW, out=self.printed.append, **kw)

    def test_a_pass_puts_the_machine_on_duty_and_sends_nothing(self):
        code, results, path = self.run_it(passing())
        self.assertEqual((code, path, self.sent), (0, None, []))
        self.assertEqual([r[0] for r in results], list(precheck.CHECKS))
        self.assertEqual(self.marked, [("test-laptop", "session 900", duty.HOURS, self.state)])
        self.assertEqual(len(self.printed), 7)
        self.assertTrue(all(ln.startswith("pass  ") for ln in self.printed[:6]))
        self.assertIn("precheck passed: test-laptop is on duty", self.printed[-1])
        self.assertFalse(os.path.exists(self.reports), "a pass writes no report")

    def test_a_dry_run_or_no_duty_marks_nothing(self):
        for kw in ({"dry_run": True}, {"no_duty": True}):
            code, _, _ = self.run_it(passing(), **kw)
            self.assertEqual((code, self.marked, self.sent), (0, [], []), kw)

    def test_a_mark_that_cannot_be_written_is_said_and_the_session_still_runs(self):
        def refused(name, what, hours, state=None):
            raise RuntimeError("erw_lock_acquire: HTTP 503")
        code, _, _ = self.run_it(passing(), on_duty=refused)
        self.assertEqual(code, 0)
        self.assertIn("could not be put on duty", self.printed[-1])
        self.assertIn("the idle alarm does not watch it", self.printed[-1])

    def failing(self):
        checks = passing()
        checks[1] = ("push_dry_run", lambda: (False, "git push --dry-run to wip/precheck-test-laptop: exit 128: fatal: Authentication failed"))
        checks[5] = ("daily_cap", lambda: (False, "DAILY_MODEL_USD is set but is not a number of dollars"))
        return checks

    def test_a_failure_writes_the_report_sends_one_line_and_exits_1(self):
        code, results, path = self.run_it(self.failing())
        self.assertEqual(code, 1)
        self.assertEqual(self.marked, [], "a machine that failed its precheck is not on duty")
        self.assertEqual(len(self.sent), 1)
        subject, line, dry = self.sent[0]
        self.assertEqual((subject, dry), ("ERW: precheck failed on test-laptop", False))
        self.assertLessEqual(len(line), 300)
        self.assertNotIn("\n", line)
        self.assertNotIn(EM, line)
        self.assertTrue(line.startswith("Precheck failed on test-laptop at 07:05 UTC (session 900): 2 of 6 checks. push_dry_run: "), line)
        self.assertIn("daily_cap: ", line)
        self.assertTrue(line.endswith("No work was started."), line)
        self.assertEqual(os.path.basename(path), "20261011T070500Z-test-laptop.md")
        report = read(path)
        self.assertIn("# Precheck on test-laptop, 2026-10-11 07:05 UTC: failed", report)
        self.assertIn("- Checks: 4 of 6 passed", report)
        self.assertIn("- The line by email: sent to 2 fixed recipients", report)
        for name in precheck.CHECKS:
            self.assertIn(f"| `{name}` |", report)
        self.assertEqual(report.count("**fail**"), 2)
        self.assertNotIn(EM, report)
        self.assertIn("precheck FAILED: 2 of 6 checks", self.printed[-1])
        self.assertTrue(self.printed[1].startswith("FAIL  push_dry_run"))

    def test_a_failed_dry_run_prints_the_line_and_sends_nothing(self):
        code, _, path = self.run_it(self.failing(), dry_run=True)
        self.assertEqual(code, 1)
        self.assertEqual([s[2] for s in self.sent], [True], "the sender is asked to print, not to send")
        self.assertIn("printed, not sent (dry run)", read(path))

    def test_a_line_that_cannot_be_sent_is_said_and_nothing_waits(self):
        def no_key(subject, line, dry_run=False):
            raise RuntimeError("not sent: RESEND_API_KEY not set")
        code, _, path = self.run_it(self.failing(), send=no_key)
        self.assertEqual(code, 1)
        self.assertIn("NOT sent (RuntimeError: not sent: RESEND_API_KEY not set)", read(path))
        self.assertIn("NOT sent", self.printed[-1])

    def test_a_check_that_raises_has_failed(self):
        checks = passing()
        checks[2] = ("claude_signed_in", lambda: 1 / 0)
        code, results, _ = self.run_it(checks)
        self.assertEqual(code, 1)
        self.assertEqual(results[2][:2], ("claude_signed_in", False))
        self.assertIn("ZeroDivisionError", results[2][2])

    def test_every_failure_at_once_still_fits_one_line(self):
        long = "a reason that goes on " * 30
        checks = [(n, (lambda: (False, long))) for n in precheck.CHECKS]
        self.run_it(checks)
        line = self.sent[0][1]
        self.assertLessEqual(len(line), 300)
        for n in precheck.CHECKS:
            self.assertIn(n + ":", line)

    def test_the_default_checks_are_the_six_in_order(self):
        self.assertEqual([n for n, _ in precheck.default_checks(self.state)], list(precheck.CHECKS))
        self.assertEqual(precheck.CHECKS, ("github_credentials", "push_dry_run", "claude_signed_in", "role_file", "env_keys", "daily_cap"))


class TheWiring(unittest.TestCase):
    NEW = ("scripts/precheck.py", "scripts/duty.py", "scripts/chain_queue.py")

    def test_the_scripts_import_only_the_standard_library_and_each_other(self):
        allowed = {"argparse", "datetime", "json", "os", "re", "shutil", "subprocess", "sys", "types", "urllib", "alert", "duty"}
        for rel in self.NEW:
            top = {ln.split()[1].split(".")[0] for ln in src(*rel.split("/")).splitlines() if ln.startswith(("import ", "from "))}
            self.assertEqual(top - allowed, set(), rel)

    def test_no_em_dash_and_no_address_in_what_was_written(self):
        for rel in self.NEW + ("queue/README.md", "queue/CHAIN_TEMPLATE.md", "scripts/githooks/post-commit", "scripts/githooks/pre-push",
                               ".github/workflows/chain-watch.yml", "tests/test_session188_precheck.py"):
            text = src(*rel.split("/"))
            self.assertNotIn(EM, text, rel)
            self.assertIsNone(re.search(r"[\w.+-]+@(?!example\.invalid|github\.com|users\.noreply)[\w-]+\.(com|edu|org|net)\b", text), f"{rel}: an address")

    def test_the_documents_and_the_template_name_the_precheck(self):
        doc = src("docs", "machines.md")
        self.assertIn("## Continuous work", doc)
        for word in ("python scripts/precheck.py", "github_credentials", "push_dry_run", "claude_signed_in", "role_file", "env_keys", "daily_cap",
                     "runs/precheck/", "does not wait"):
            self.assertIn(word, doc, word)
        template = src("queue", "CHAIN_TEMPLATE.md")
        rules = re.findall(r"^(\d+)\. (.*)$", template, re.M)
        self.assertGreaterEqual(len(rules), 3)
        self.assertEqual(rules[0][0], "1")
        self.assertIn("python scripts/precheck.py", rules[0][1], "the template's first rule names the precheck")
        self.assertIn("python scripts/chain_queue.py next", rules[-1][1], "the template's last rule names the queue step")


if __name__ == "__main__":
    unittest.main()
