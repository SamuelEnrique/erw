"""Session 7202 (chain 302, goal 3): the scheduled model steps fail soft when the key refuses.

On 15 November 2026 the API answered every scheduled call with "You have reached your specified API usage limits. You
will regain access on 2026-12-01 at 00:00 UTC". The news and the policy scoring were recorded as failed and the
Roundup's job skipped its commit and its email after a failed step. These tests hold the rule that replaces that:

- the shared client (warehouse/llm.py) knows the refusal once, sends no further call, and never retries;
- a scheduled model step ends as skipped: its status says "the key's limit" with the date access returns, one line is
  printed last, the exit is 75 (one skipped row of erw_health, by the daily sequence or by health.py run);
- no Digest and no Roundup is written on a day the scoring was refused.

Every client here is a stub that raises the API's error: no request is made, nothing is sent, no issue is written
outside a temporary folder.
"""
import contextlib
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for sub in ("", "connectors", "news", "policy"):
    sys.path.insert(0, os.path.join(ROOT, "warehouse", sub))
import iso_prices as ip  # noqa: E402
import llm  # noqa: E402

WORDS = "You have reached your specified API usage limits. You will regain access on 2026-12-01 at 00:00 UTC."
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
STEPS = {  # each scheduled model step's script and the name its status is written under
    ("warehouse", "news", "score.py"): 'llm.finish("news_score", main())',
    ("warehouse", "policy", "score.py"): 'llm.finish("policy_score", _rc)',
    ("warehouse", "policy", "reads.py"): 'llm.finish("policy_reads", main())',
    ("warehouse", "deals", "extract.py"): 'llm.finish("deals", main())',
    ("warehouse", "datacenters", "extract.py"): 'llm.finish("datacenters", main())',
    ("warehouse", "news", "funfact.py"): 'llm.finish("news_funfact", _rc)',
    ("warehouse", "news", "brief.py"): 'llm.finish("news_brief", main())',
    ("warehouse", "news", "roundup.py"): 'brief.llm.finish("news_roundup", main())',
    ("warehouse", "analysis", "run.py"): 'llm.finish("analysis", _rc)',
    ("warehouse", "news", "shadow.py"): 'llm.finish(f"news_shadow_{args.cmd}", 0 if res["status"] in ("ok", "skipped") else 1)',
}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Refusal(Exception):
    """The SDK's BadRequestError as the scripts meet it: HTTP 400 with the API's sentence in its body."""
    status_code = 400

    def __init__(self, words=WORDS):
        super().__init__(f"Error code: 400 - {{'type': 'error', 'error': {{'type': 'invalid_request_error', 'message': '{words}'}}}}")
        self.body = {"type": "error", "error": {"type": "invalid_request_error", "message": words}}


class Stub:
    """A client whose every request is refused; it counts the requests that reached it."""

    def __init__(self, exc=None):
        self.sent = 0
        outer = self

        class Messages:
            def create(self, **kwargs):
                outer.sent += 1
                raise exc or Refusal()

            def stream(self, **kwargs):
                class Manager:
                    def __enter__(self_inner):
                        outer.sent += 1
                        raise exc or Refusal()

                    def __exit__(self_inner, *a):
                        return False
                return Manager()

        class Models:
            def list(self, *a, **k):
                outer.sent += 1
                raise exc or Refusal()

        self.messages, self.models = Messages(), Models()


class Base(unittest.TestCase):
    def setUp(self):
        llm.reset_key_limit()
        self.tmp = tempfile.mkdtemp(prefix="erw7202_")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.addCleanup(llm.reset_key_limit)
        # Every client of these tests is a stub: a session's own spend cap (ERW_SPEND_CAP_USD=0 refuses before the stub is
        # asked) and the cost ledger are set aside, and a real client can never be built here.
        env = mock.patch.dict(os.environ, {"ERW_SPEND_CAP_USD": "", "ERW_LEDGER": "0"})
        env.start()
        self.addCleanup(env.stop)
        real = mock.patch.object(llm, "client", side_effect=AssertionError("a test asked for a real client"))
        real.start()
        self.addCleanup(real.stop)

    def refuse(self):
        with self.assertRaises(llm.KeyLimitReached):
            llm.guarded(Stub().messages.create)


class TheClient(Base):
    def test_the_refusal_is_read_with_its_date(self):
        self.assertEqual(llm.key_limit_of(Refusal()), {"returns": "2026-12-01 at 00:00 UTC", "words": WORDS})
        self.assertEqual(llm.key_limit_of(Exception("You have reached your specified API usage limits. You will regain access on 2026-12-01."))["returns"], "2026-12-01")
        self.assertEqual(llm.key_limit_of(Exception("You have reached your specified API usage limits."))["returns"], "")
        for other in ("temperature is not supported by this model", "Overloaded", "rate limit exceeded", "credit balance is too low"):
            self.assertIsNone(llm.key_limit_of(Exception(other)), other)

    def test_one_request_then_none(self):
        stub = Stub()
        c = llm.wrap(stub, "news_score")
        with self.assertRaises(llm.KeyLimitReached) as e:
            c.messages.create(model="m", max_tokens=1, messages=[])
        self.assertIn("the key's limit", str(e.exception))
        self.assertIn("access returns 2026-12-01 at 00:00 UTC", str(e.exception))
        self.assertIn("usage limits", str(e.exception), "the API's own words are kept, so the extractors' sorter reads it as the limit")
        self.assertEqual(stub.sent, 1)
        for again in (lambda: c.messages.create(model="m", max_tokens=1, messages=[]), lambda: c.models.list(),
                      lambda: c.messages.stream(model="m", max_tokens=1, messages=[]).__enter__()):
            with self.assertRaises(llm.KeyLimitReached):
                again()
        self.assertEqual(stub.sent, 1, "after the refusal no request is sent: no retry, by this client or another of the process")
        other = Stub()
        with self.assertRaises(llm.KeyLimitReached):
            llm.wrap(other, "policy_score").messages.create(model="m", max_tokens=1, messages=[])
        self.assertEqual(other.sent, 0)
        self.assertEqual(c.calls, [], "a refused call writes no row of the cost ledger")

    def test_the_model_list_and_a_stream_meet_it_too(self):
        for ask in (lambda c: c.models.list(), lambda c: c.messages.stream(model="m", max_tokens=1, messages=[]).__enter__()):
            llm.reset_key_limit()
            stub = Stub()
            with self.assertRaises(llm.KeyLimitReached):
                ask(llm.wrap(stub, "digest"))
            self.assertEqual((stub.sent, llm.key_limit()["returns"]), (1, "2026-12-01 at 00:00 UTC"))

    def test_another_error_is_the_sdks_own(self):
        stub = Stub(exc=ValueError("temperature: Extra inputs are not permitted"))
        c = llm.wrap(stub, "news_score")
        for _ in range(2):
            with self.assertRaises(ValueError):
                c.messages.create(model="m", max_tokens=1, messages=[])
        self.assertEqual(stub.sent, 2)
        self.assertIsNone(llm.key_limit())

    def test_the_extractors_sorter_reads_it_as_the_limit(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
        import calls
        stub = Stub()
        with self.assertRaises(calls.Stop):
            calls.call(llm.wrap(stub, "deals_extract"), dict(model="m", max_tokens=1, messages=[]), [], lambda m: None, "call 1", sleep=lambda s: None)
        self.assertEqual(stub.sent, 1)


class TheStepEnds(Base):
    def status(self, name, rows, run_id=None):
        with mock.patch.object(ip, "STATUS_DIR", self.tmp):
            ip.write_status(name, run_id or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), rows)
        return os.path.join(self.tmp, f"{name}.json")

    def test_with_no_refusal_nothing_changes(self):
        path = self.status("news_score", [dict(table="news_stories", market="scoring", status="failed", detail="calls 0 (16 failed)")])
        before = open(path, encoding="utf-8").read()
        out = io.StringIO()
        with mock.patch.object(ip, "STATUS_DIR", self.tmp), contextlib.redirect_stdout(out):
            self.assertEqual((llm.finish("news_score", 1), llm.finish("news_score", 0)), (1, 0))
        self.assertEqual((open(path, encoding="utf-8").read(), out.getvalue()), (before, ""))

    def test_a_refused_step_is_skipped_with_the_keys_line(self):
        path = self.status("policy_score", [dict(table="policy_actions", market="score", status="failed", detail="0 newly scored, 2049 of 2063 scored"),
                                             dict(table="policy_reads", market="reads", status="ok", detail=""),
                                             dict(table="x", market="y", status="gap", detail="a known gap")])
        self.refuse()
        out = io.StringIO()
        with mock.patch.object(ip, "STATUS_DIR", self.tmp), contextlib.redirect_stdout(out):
            rc = llm.finish("policy_score", 1)
        self.assertEqual(rc, 75)
        self.assertEqual(rc, llm.SKIP_EXIT)
        line = "the key's limit: the Anthropic API key has reached its usage limit; access returns 2026-12-01 at 00:00 UTC; no model call is sent until then"
        self.assertEqual(out.getvalue().strip().splitlines()[-1], f"policy_score SKIPPED: {line}")
        rows = json.load(open(path, encoding="utf-8"))["results"]
        self.assertEqual([r["status"] for r in rows], ["skipped", "skipped", "gap"])
        self.assertEqual(rows[0]["detail"], f"{line}; before the refusal: 0 newly scored, 2049 of 2063 scored")
        self.assertEqual((rows[1]["detail"], rows[2]["detail"]), (line, "a known gap"))

    def test_an_earlier_runs_status_is_not_rewritten(self):
        path = self.status("deals", [dict(table="energy_deals", market="extract", status="ok", detail="")])
        old = time.time() - 3600 * 30
        os.utime(path, (old, old))
        self.refuse()
        with mock.patch.object(ip, "STATUS_DIR", self.tmp), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(llm.finish("deals", 0), 75)
        self.assertEqual(json.load(open(path, encoding="utf-8"))["results"][0]["status"], "ok")

    def test_every_scheduled_model_step_exits_through_it(self):
        for parts, call in STEPS.items():
            self.assertIn(call, src(*parts), parts)
        sh = src("warehouse", "run_daily.sh")
        scripts = {tuple(m.split("/")) for m in __import__("re").findall(r'^(?:NO_MODEL_FLAG=--no-model )?model_step \w+ "\$PYTHON" (warehouse/[\w/]+\.py)', sh, flags=8)}
        self.assertEqual(scripts - set(STEPS), set(), "a model step of the daily sequence that does not exit through llm.finish")
        self.assertGreaterEqual(len(scripts), 7)

    def test_health_records_one_skipped_row_and_does_not_retry(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import health
        line = "news_roundup SKIPPED: " + llm.key_line({"returns": "2026-12-01 at 00:00 UTC", "words": WORDS})
        tried, rows = [], []
        attempt = lambda cmd: (tried.append(cmd) or (75, ["news_roundup FAILED: KeyLimitReached", line], 2.0))  # noqa: E731
        with contextlib.redirect_stdout(io.StringIO()):
            rc, status = health.run("write the Roundup", ["x"], retries=1, attempt=attempt, sleep=lambda s: self.fail("a refused step waited to retry"),
                                    rec=lambda *a: rows.append(a))
        self.assertEqual((rc, status, len(tried), len(rows)), (0, "skipped", 1, 1))
        self.assertEqual(rows[0][:2], ("write the Roundup", "skipped"))
        self.assertIn("the key's limit", rows[0][2])
        self.assertIn("access returns 2026-12-01 at 00:00 UTC", rows[0][2])
        self.assertEqual(health.SKIP, llm.SKIP_EXIT)


class TheScorer(Base):
    """The news scorer on a copy of the stories with 60 or more unscored: one request, no further batch, the table untouched."""

    def test_one_call_no_table_write_and_a_skipped_status(self):
        try:
            import pandas as pd
            import score
        except Exception as exc:
            self.skipTest(f"the scorer is not importable here: {type(exc).__name__}")
        real = os.path.join(ROOT, "warehouse", "output", "news_stories.csv")
        if not os.path.exists(real):
            self.skipTest("news_stories.csv is not on this copy")
        with open(real, encoding="utf-8") as f:
            head = [next(f) for _ in range(40)]
        comments = [ln for ln in head if ln.startswith("#")]
        df = ip.read_series(real, score.NEWS_COLS).head(200).copy()
        now = pd.Timestamp.now(tz="UTC")
        fresh = df.index[:60]
        df.loc[fresh, "event_date"] = [ip.utc_iso(now - pd.Timedelta(minutes=5 * (i + 1))) for i in range(60)]
        df.loc[fresh, ["scored_at", "significance", "ai_power_relevance", "cluster_id"]] = ""
        table = os.path.join(self.tmp, "news_stories.csv")
        with open(table, "w", encoding="utf-8", newline="") as f:
            f.writelines(comments)
            df.to_csv(f, index=False, lineterminator="\n")
        before = open(table, "rb").read()
        stub = Stub()
        saved = (ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR)
        out = io.StringIO()
        try:
            with mock.patch.object(score.llm, "client", lambda step, log=None, api_key=None, **k: llm.wrap(stub, step, log)), \
                    mock.patch.object(ip, "load_key", lambda *a, **k: "not-a-key"), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = score.main(["--out-dir", self.tmp, "--days", "2"])
                status = json.load(open(os.path.join(ip.STATUS_DIR, "news_score.json"), encoding="utf-8"))["results"][0]
                end = llm.finish("news_score", rc)
        finally:
            ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR = saved
        self.assertEqual(stub.sent, 1, "60 and more stories are three batches: the first is refused and the others are never sent")
        self.assertEqual(open(table, "rb").read(), before, "nothing was scored, so the table and its header are as they were")
        self.assertEqual(status["status"], "skipped")
        self.assertTrue(status["detail"].startswith("the key's limit: "), status["detail"])
        self.assertRegex(status["detail"], r"; 0 of \d+ stories scored, the table is left as it was$")
        self.assertEqual(end, 75)
        self.assertRegex(out.getvalue().strip().splitlines()[-1], r"^news_score SKIPPED: the key's limit: .*access returns 2026-12-01 at 00:00 UTC")
        self.assertNotIn("FAILED", out.getvalue())


class NoIssueOnARefusedDay(Base):
    DAY = "2026-11-16"   # a Monday

    def refused_status(self, run_id="20261116T152052Z", status="skipped", detail=None):
        detail = detail if detail is not None else llm.key_line({"returns": "2026-12-01 at 00:00 UTC", "words": WORDS}) + "; 0 of 400 stories scored, the table is left as it was"
        with open(os.path.join(self.tmp, "news_score.json"), "w", encoding="utf-8") as f:
            json.dump({"connector": "news_score", "run_id": run_id, "runner": "github", "results": [dict(table="news_stories", market="scoring", status=status, detail=detail)]}, f)

    def test_the_day_is_read_from_the_status_or_the_history(self):
        none = os.path.join(self.tmp, "none.csv")
        self.assertIsNone(llm.refused_today("news_score", self.DAY, status_dir=self.tmp, csv_path=none))
        self.refused_status()
        self.assertTrue(llm.refused_today("news_score", self.DAY, status_dir=self.tmp, csv_path=none).startswith("the key's limit: "))
        self.assertIsNone(llm.refused_today("news_score", "2026-11-17", status_dir=self.tmp, csv_path=none), "another day's refusal is not today's")
        self.refused_status(status="failed", detail="calls 0 (16 failed)")
        self.assertIsNone(llm.refused_today("news_score", self.DAY, status_dir=self.tmp, csv_path=none), "a failure of another kind is not the key's limit")
        self.refused_status(status="skipped", detail="MODEL_STEPS=0 (no model calls in this run)")
        self.assertIsNone(llm.refused_today("news_score", self.DAY, status_dir=self.tmp, csv_path=none))
        hist = os.path.join(self.tmp, "run_status.csv")
        line = llm.key_line({"returns": "2026-12-01 at 00:00 UTC", "words": WORDS})
        with open(hist, "w", encoding="utf-8", newline="") as f:
            f.write("run_id,runner,connector,table,market,status,detail\n")
            f.write(f'20261116T140500Z,github,news_score,news_stories,scoring,skipped,"{line}"\n')
            f.write('20261116T140700Z,github,policy_score,policy_actions,score,ok,"3 newly scored"\n')
        os.remove(os.path.join(self.tmp, "news_score.json"))
        self.assertEqual(llm.refused_today("news_score", self.DAY, status_dir=self.tmp, csv_path=hist), line)
        with open(hist, "a", encoding="utf-8", newline="") as f:
            f.write('20261116T190000Z,local,news_score,news_stories,scoring,ok,"stories scored 400 of 400"\n')
        self.assertIsNone(llm.refused_today("news_score", self.DAY, status_dir=self.tmp, csv_path=hist), "a later run of the day that scored: not a refused day")

    def brief(self):
        try:
            import brief
        except Exception as exc:
            self.skipTest(f"brief not importable here: {type(exc).__name__}")
        return brief

    def test_the_digest_writes_nothing_and_ends_skipped(self):
        brief = self.brief()
        self.refused_status()
        digests = os.path.join(self.tmp, "digest")
        out = io.StringIO()

        def never(*a, **k):
            raise AssertionError("the Digest read the stories or built a client on a day the scoring was refused")
        with mock.patch.object(ip, "STATUS_DIR", self.tmp), mock.patch.object(ip, "LOG_DIR", self.tmp), mock.patch.object(brief, "DIGEST_DIR", digests), \
                mock.patch.object(brief.llm, "client", never), mock.patch.object(ip, "read_series", never), contextlib.redirect_stdout(out):
            rc = brief.main(["--date", self.DAY])
            status = json.load(open(os.path.join(self.tmp, "news_brief.json"), encoding="utf-8"))["results"][0]
            end = llm.finish("news_brief", rc)
        self.assertEqual((rc, end), (75, 75))
        self.assertFalse(os.path.exists(digests), "no issue, and no latest.md")
        self.assertEqual(status["status"], "skipped")
        self.assertRegex(status["detail"], r"^the key's limit: .*access returns 2026-12-01 at 00:00 UTC.*the day's stories were not scored, so no issue is written$")
        self.assertRegex(out.getvalue().strip().splitlines()[-1], r"^news_brief SKIPPED: the key's limit: ")
        self.assertNotIn("before the refusal", status["detail"])

    def test_a_dry_run_to_a_path_is_a_persons_own(self):
        brief = self.brief()
        self.refused_status()

        class Reached(Exception):
            pass

        def reached(*a, **k):
            raise Reached()
        with mock.patch.object(ip, "STATUS_DIR", self.tmp), mock.patch.object(ip, "LOG_DIR", self.tmp), mock.patch.object(ip, "read_series", reached), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = brief.main(["--date", self.DAY, "--out", os.path.join(self.tmp, "dry.md")])
        self.assertEqual(rc, 1, "the run went on to read the stories (and failed on this test's stand-in)")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "dry.md")))

    def test_the_digests_own_refused_call_writes_no_issue(self):
        brief = self.brief()
        stories = os.path.join(ip.OUT_DIR, "news_stories.csv")
        if not os.path.exists(stories):
            self.skipTest("news_stories.csv is not on this copy")
        stub, out_path = Stub(), os.path.join(self.tmp, "digest.md")
        with mock.patch.object(brief.llm, "client", lambda step, log=None, api_key=None, **k: llm.wrap(stub, step, log)), \
                mock.patch.object(ip, "load_key", lambda *a, **k: "not-a-key"), mock.patch.object(ip, "STATUS_DIR", self.tmp), \
                mock.patch.object(ip, "LOG_DIR", self.tmp), contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            rc = brief.main(["--hours", "8000", "--date", "2026-10-09", "--out", out_path])
            log = "".join(open(os.path.join(self.tmp, f), encoding="utf-8").read() for f in os.listdir(self.tmp) if f.endswith(".log"))
            if "no scored stories in the window" in log:
                self.skipTest("no scored story in the window on this copy")
            status = json.load(open(os.path.join(self.tmp, "news_brief.json"), encoding="utf-8"))["results"][0]
            before = status["status"]
            end = llm.finish("news_brief", rc)
            status = json.load(open(os.path.join(self.tmp, "news_brief.json"), encoding="utf-8"))["results"][0]
        self.assertIsNotNone(llm.key_limit(), log[-1500:])
        self.assertEqual(stub.sent, 1, "one refused request, then none")
        self.assertFalse(os.path.exists(out_path), "no issue is written when the Digest's own call is refused")
        self.assertEqual((rc, before, end, status["status"]), (1, "failed", 75, "skipped"))
        self.assertTrue(status["detail"].startswith("the key's limit: "))
        self.assertRegex(out.getvalue().strip().splitlines()[-1], r"^news_brief SKIPPED: the key's limit: ")

    def test_the_roundup_writes_nothing_and_ends_skipped(self):
        self.brief()
        try:
            import roundup
        except Exception as exc:
            self.skipTest(f"roundup not importable here: {type(exc).__name__}")
        today = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
        self.refused_status(run_id=f"{today}T140500Z")
        weeks = os.path.join(self.tmp, "roundup")
        out = io.StringIO()

        def never(*a, **k):
            raise AssertionError("the Roundup read the stories or built a client on a day the scoring was refused")
        with mock.patch.object(ip, "STATUS_DIR", self.tmp), mock.patch.object(ip, "LOG_DIR", self.tmp), mock.patch.object(roundup, "ROUNDUP_DIR", weeks), \
                mock.patch.object(roundup.brief.llm, "client", never), mock.patch.object(ip, "read_series", never), contextlib.redirect_stdout(out):
            rc = roundup.main([])
            status = json.load(open(os.path.join(self.tmp, "news_roundup.json"), encoding="utf-8"))["results"][0]
        self.assertEqual(rc, 75)
        self.assertFalse(os.path.exists(weeks))
        self.assertEqual(status["status"], "skipped")
        self.assertRegex(status["detail"], r"^the key's limit: .*so no Roundup is written$")
        self.assertRegex(out.getvalue().strip().splitlines()[-1], r"^news_roundup SKIPPED: the key's limit: ")


class TheJobs(unittest.TestCase):
    def test_the_daily_sequence_records_the_skip(self):
        sh = src("warehouse", "run_daily.sh")
        self.assertIn('KEY_MARK="the key\'s limit"', sh)
        self.assertEqual(llm.KEY_MARK, "the key's limit")
        fn = sh[sh.index("run_other() {"):sh.index("pull() {")]
        self.assertIn('grep -m1 "SKIPPED: ${KEY_MARK}" "$out"', fn)
        self.assertIn('case "$why" in "$BUDGET_MARK"*|"$KEY_MARK"*)', fn)

    @unittest.skipUnless(shutil.which("bash"), "bash is not installed")
    def test_run_other_writes_one_skipped_row_for_a_refused_step(self):
        sh = src("warehouse", "run_daily.sh")
        fn = sh[sh.index("run_other() {"):sh.index("pull() {")]
        d = tempfile.mkdtemp(prefix="erw7202_sh_")
        self.addCleanup(shutil.rmtree, d, True)
        line = llm.key_line({"returns": "2026-12-01 at 00:00 UTC", "words": WORDS})
        with open(os.path.join(d, "step.sh"), "w", encoding="utf-8", newline="\n") as f:
            f.write("echo 'news_score news_stories FAILED: an earlier line'\n")
            f.write(f'echo "news_score SKIPPED: {line}"\nexit 75\n')
        with open(os.path.join(d, "run.sh"), "w", encoding="utf-8", newline="\n") as f:
            f.write('cd "$(dirname "$0")"\nmkdir -p runs\nstatus=status.txt\n: > "$status"\n')
            f.write('BUDGET_MARK="publisher did not answer within the budget"\nKEY_MARK="the key\'s limit"\n')
            f.write('health_row() { echo "$1|$2|$3" >> health.txt; }\n')
            f.write(fn)
            f.write('\nrun_other news_score bash step.sh\n')
        r = subprocess.run([shutil.which("bash"), os.path.join(d, "run.sh").replace("\\", "/")], capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        self.assertEqual(open(os.path.join(d, "status.txt"), encoding="utf-8").read().strip(), f"news_score skipped: {line}")
        self.assertEqual(open(os.path.join(d, "health.txt"), encoding="utf-8").read().strip(), f"news_score|skipped|{line}")

    def test_the_roundups_job_commits_and_sends_only_after_a_written_issue(self):
        y = src(".github", "workflows", "roundup.yml")
        main = y[y.index("id: main"):y.index("- name: Keep the log")]
        self.assertIn('python warehouse/health.py run --step "write the Roundup" --retries 0 -- bash -c "set -o pipefail;', main)
        self.assertIn("python warehouse/news/roundup.py; else python warehouse/news/roundup.py --no-model; fi; }; } 2>&1 | tee roundup.log", main)
        commit = y[y.index("- name: Commit the Roundup and the analysis"):y.index("- name: Send the Roundup by email")]
        self.assertIn("if: steps.main.outputs.status == 'ok' || steps.main.outputs.status == 'retried'", commit)
        send = y[y.index("- name: Send the Roundup by email"):y.index("- name: Keep the cost ledger")]
        self.assertIn("if: steps.commit.outcome == 'success'", send)

    def test_the_email_is_not_sent_without_todays_issue(self):
        e = src("warehouse", "news", "email_digest.py")
        self.assertIn("if args.auto and not_todays_issue():", e)

    def test_no_em_or_en_dash(self):
        for parts in (("warehouse", "llm.py"), ("tests", "test_session7202_key_refusal.py")):
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
            self.assertNotIn(EN_DASH, text, parts)


if __name__ == "__main__":
    unittest.main()
