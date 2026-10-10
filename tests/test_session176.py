"""Session 176: the daily cap for all scheduled model steps together (DAILY_MODEL_USD, warehouse/health.py budget),
and the digest and the Roundup written without their model-written parts when it is reached.

No test here calls a model or reaches the network: the ledger is a file written by the test, Supabase's copy is a
stub, and the digest's client is replaced by one that fails the test if it is ever built.
"""

import os
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import health  # noqa: E402

HEAD = ("event_id,event_date,event_type,currency,source,source_url,run_id,session,step,model,input_tokens,"
        "cached_input_tokens,cache_write_tokens,output_tokens,web_searches,usd,ts_utc,prices_as_of,request_id")


def row(i, ts, session, step, usd):
    return (f"anthropic:req_{i},{ts},api_call,USD,anthropic:messages-usage,https://docs.anthropic.com/en/api/messages,"
            f"20261008T140000Z,{session},{step},claude-sonnet-5-5,10,0,0,10,0,{usd},{ts},2026-09-25T00:00:00Z,req_{i}")


def ledger(lines):
    d = tempfile.mkdtemp(prefix="erw176_")
    path = os.path.join(d, "api_cost_ledger.csv")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Energy Research Warehouse (ERW): a ledger written by tests/test_session176.py\n# second comment line\n")
        f.write(HEAD + "\n" + "\n".join(lines) + "\n")
    return path


class Resp:
    def __init__(self, rows, status=200):
        self.status_code, self._rows = status, rows

    def json(self):
        return self._rows


def no_remote(*a, **k):
    return Resp([])


DAY = "2026-10-08"
ROWS = [row(1, "2026-10-08T14:20:00Z", "daily", "news_score", "0.600000"),
        row(2, "2026-10-08T14:25:00Z", "daily", "news_score", "0.502000"),
        row(3, "2026-10-08T14:40:00Z", "daily", "deals_extract", "0.217000"),
        row(4, "2026-10-08T10:00:00Z", "157", "policy_recheck_reads", "3.000000"),   # a session's work: not scheduled
        row(5, "2026-10-08T15:00:00Z", "daily", "thesis", "0.900000"),               # the Thesis Builder: not scheduled
        row(6, "2026-10-07T14:20:00Z", "daily", "news_score", "1.100000"),           # the day before
        row(7, "2026-10-08T14:50:00Z", "daily", "digest", "")]                       # a call with no configured price


class TheSpend(unittest.TestCase):
    def setUp(self):
        self.env = mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "SUPABASE_URL": "https://x.supabase.co/rest/v1/",
                                                "SUPABASE_SERVICE_KEY": "k"}, clear=False)
        self.env.start()
        os.environ.pop("ERW_SESSION", None)
        os.environ.pop("DAILY_MODEL_USD", None)

    def tearDown(self):
        self.env.stop()

    def test_the_days_scheduled_steps_are_summed_and_nothing_else(self):
        usd, calls = health.model_spend(DAY, path=ledger(ROWS), get=no_remote)
        self.assertAlmostEqual(usd, 0.600 + 0.502 + 0.217)
        self.assertEqual(calls, 4)  # the unpriced digest call counts as a call of USD 0

    def test_a_row_another_runner_wrote_today_is_added_once(self):
        remote = [{"event_id": "anthropic:req_3", "extra": {"step": "deals_extract", "session": "daily", "usd": "0.217000"}},
                  {"event_id": "anthropic:req_90", "extra": {"step": "roundup", "session": "daily", "usd": "0.044000"}},
                  {"event_id": "anthropic:req_91", "extra": {"step": "thesis", "session": "daily", "usd": "0.900000"}}]
        asked = {}

        def get(url, **k):
            asked["url"], asked["params"] = url, k["params"]
            return Resp(remote)
        usd, _ = health.model_spend(DAY, path=ledger(ROWS), get=get)
        self.assertAlmostEqual(usd, 0.600 + 0.502 + 0.217 + 0.044)
        self.assertTrue(asked["url"].endswith("/rest/v1/events"))
        self.assertEqual(asked["params"]["table_name"], "eq.api_cost_ledger")
        self.assertIn("2026-10-08T00:00:00Z", asked["params"]["and"])
        self.assertIn("2026-10-09T00:00:00Z", asked["params"]["and"])

    def test_no_ledger_on_the_machine_and_no_answer_is_zero_not_an_error(self):
        usd, calls = health.model_spend(DAY, path=os.path.join(tempfile.mkdtemp(prefix="erw176_"), "none.csv"),
                                        get=lambda *a, **k: Resp([], 503))
        self.assertEqual((usd, calls), (0, 0))

    def test_a_local_run_counts_its_own_rows_only(self):
        os.environ.pop("GITHUB_ACTIONS", None)
        self.assertEqual(health.ledger_session(), "local")
        usd, _ = health.model_spend(DAY, path=ledger(ROWS + [row(8, "2026-10-08T16:00:00Z", "local", "news_score", "0.300000")]),
                                    get=no_remote)
        self.assertAlmostEqual(usd, 0.3)

    def test_the_cap_reads_the_environment_and_falls_back_to_one_dollar(self):
        with mock.patch.object(health, "env", lambda k: ""):
            self.assertEqual(health.model_cap(), 1.00)
        with mock.patch.object(health, "env", lambda k: "2.5" if k == "DAILY_MODEL_USD" else ""):
            self.assertEqual(health.model_cap(), 2.5)
        with mock.patch.object(health, "env", lambda k: "a lot" if k == "DAILY_MODEL_USD" else ""):
            self.assertEqual(health.model_cap(), 1.00)
        with mock.patch.object(health, "env", lambda k: "-1" if k == "DAILY_MODEL_USD" else ""):
            self.assertEqual(health.model_cap(), 1.00)
        with mock.patch.object(health, "env", lambda k: "0" if k == "DAILY_MODEL_USD" else ""):
            self.assertEqual(health.model_cap(), 0.0)  # zero is a cap: no scheduled model step runs


class TheGate(unittest.TestCase):
    def test_under_the_cap_the_step_runs_and_nothing_is_recorded(self):
        rows = []
        code, line = health.budget("policy_score", DAY, rec=lambda *a: rows.append(a), spend=lambda d: (0.62, 9), cap=1.0)
        self.assertEqual(code, 0)
        self.assertEqual(rows, [])
        self.assertIn("USD 0.62 of 1.00", line)

    def test_at_the_cap_the_step_is_skipped_loudly(self):
        rows = []
        for spent in (1.00, 1.32):
            code, line = health.budget("deals", DAY, rec=lambda *a: rows.append(a), spend=lambda d, s=spent: (s, 16), cap=1.0)
            self.assertEqual(code, health.SKIP)
            self.assertTrue(line.startswith(health.CAP_MARK))
            self.assertIn("DAILY_MODEL_USD", line)
            self.assertIn("deals not run", line)
        self.assertEqual([(r[0], r[1]) for r in rows], [("deals", "skipped")] * 2)
        self.assertTrue(all(r[2].startswith(health.CAP_MARK) for r in rows))

    def test_a_step_written_without_the_model_says_so_and_not_that_it_did_not_run(self):
        rows = []
        code, line = health.budget("news_brief", DAY, rec=lambda *a: rows.append(a), spend=lambda d: (1.07, 16), cap=1.0,
                                   instead="written without the model-written parts (--no-model)")
        self.assertEqual(code, health.SKIP)
        self.assertTrue(line.endswith("news_brief written without the model-written parts (--no-model)"))
        self.assertNotIn("not run", line)
        skipped = {"workflow": "daily prices", "run_id": "9", "step": "deals", "status": "skipped",
                   "reason": health.CAP_MARK + " reached: USD 1.07 spent today (x) of USD 1.00 (DAILY_MODEL_USD); deals not run"}
        written = dict(skipped, step="news_brief", reason=rows[0][2])
        _, mail = health.alert_line("2026-10-12", [skipped, written], run_id="9")
        self.assertIn("written without the model: news_brief", mail)
        self.assertLessEqual(len(mail), 300)

    def test_a_cap_of_zero_skips_every_step(self):
        code, _ = health.budget("news_score", DAY, rec=lambda *a: None, spend=lambda d: (0.0, 0), cap=0.0)
        self.assertEqual(code, health.SKIP)

    def test_a_budget_that_cannot_be_read_never_switches_a_step_off(self):
        rows = []

        def broken(day):
            raise OSError("the ledger is locked")
        code, line = health.budget("news_score", DAY, rec=lambda *a: rows.append(a), spend=broken, cap=1.0)
        self.assertEqual(code, 0)
        self.assertEqual((rows[0][0], rows[0][1]), ("model budget", "failed"))
        self.assertIn("could not be read", line)

    def test_the_command_exits_with_the_skip_code(self):
        with mock.patch.object(health, "budget", lambda step, day, instead="": (health.SKIP, "x")):
            self.assertEqual(health.main(["budget", "--step", "roundup"]), 75)
        with mock.patch.object(health, "budget", lambda step, day, instead="": (0, "x")):
            self.assertEqual(health.main(["budget", "--step", "roundup", "--day", DAY]), 0)


class TheSameDayEmail(unittest.TestCase):
    CAP = {"workflow": "daily prices", "run_id": "9", "step": "deals", "status": "skipped",
           "reason": health.CAP_MARK + " reached: USD 1.10 spent today (2026-10-12 UTC, 16 calls of the scheduled model steps) "
                                       "of USD 1.00 (DAILY_MODEL_USD); deals not run"}
    FAIL = {"workflow": "daily prices", "run_id": "9", "step": "supabase_load", "status": "failed", "reason": "timeout"}
    SKIP = {"workflow": "daily prices", "run_id": "9", "step": "supply", "status": "skipped", "reason": "not Saturday"}

    def test_a_capped_step_is_told_the_same_day(self):
        cap2 = dict(self.CAP, step="datacenters")
        subject, line = health.alert_line("2026-10-12", [self.CAP, cap2, self.SKIP], run_id="9")
        self.assertEqual(subject, "ERW: the daily model cap skipped 2 steps")
        self.assertIn("USD 1.10 spent today", line)
        self.assertIn("deals, datacenters", line)
        self.assertLessEqual(len(line), 300)

    def test_an_ordinary_skip_sends_nothing(self):
        self.assertIsNone(health.alert_line("2026-10-12", [self.SKIP], run_id="9"))

    def test_a_failure_and_a_capped_step_are_one_line(self):
        subject, line = health.alert_line("2026-10-12", [self.FAIL, self.CAP], run_id="9")
        self.assertIn("1 scheduled step failed", subject)
        self.assertIn("the model cap skipped 1", subject)
        self.assertIn("supabase_load: timeout", line)
        self.assertIn("1 model step not run (deals)", line)
        self.assertLessEqual(len(line), 300)

    def test_a_failure_alone_reads_as_it_did(self):
        subject, line = health.alert_line("2026-10-12", [self.FAIL, self.SKIP], run_id="9")
        self.assertEqual(subject, "ERW: 1 scheduled step failed")
        self.assertEqual(line, "1 step of daily prices failed on 2026-10-12 UTC (run 9): supabase_load: timeout")

    def test_the_alert_sends_the_capped_line(self):
        sent = []
        n = health.alert("2026-10-12", "9", rows=[self.CAP], send=lambda s, l, d: sent.append((s, l)))
        self.assertEqual(n, 1)
        self.assertEqual(sent[0][0], "ERW: the daily model cap skipped 1 step")


class TheSchedule(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_every_model_step_of_the_daily_run_asks_the_budget_first(self):
        sh = self.read("warehouse", "run_daily.sh")
        body = sh[sh.index("model_step() {"):sh.index("run_other() {")]
        self.assertIn('warehouse/health.py budget --step "$1"', body)
        self.assertIn('-ne 75', body)
        self.assertIn('run_other "$@" "$NO_MODEL_FLAG"', body)
        self.assertNotIn("| tee", body)
        # the digest publishes without its model-written parts; no other step is given the flag
        self.assertEqual(re.findall(r"^NO_MODEL_FLAG=(\S+) model_step (\S+)", sh, re.M), [("--no-model", "news_brief")])
        # no model script is started outside model_step
        for script in ("news/score.py", "policy/score.py", "policy/reads.py", "deals/extract.py", "datacenters/extract.py",
                       "news/funfact.py", "news/brief.py", "news/shadow.py"):
            for ln in sh.splitlines():
                if f"warehouse/{script}" in ln and not ln.lstrip().startswith("#"):
                    self.assertIn("model_step ", ln, ln)

    def test_the_roundup_asks_the_budget_and_writes_without_the_model_at_the_cap(self):
        y = self.read(".github", "workflows", "roundup.yml")
        self.assertIn("if python warehouse/health.py budget --step analysis_note --instead 'written without the model (--no-model)'; "
                      "then python warehouse/analysis/run.py; else python warehouse/analysis/run.py --no-model; fi;", y)
        self.assertIn("if python warehouse/health.py budget --step roundup --instead 'written without the model-written parts (--no-model)'; "
                      "then python warehouse/news/roundup.py; else python warehouse/news/roundup.py --no-model; fi;", y)
        for name in ("roundup.yml", "daily-prices.yml"):
            self.assertIn("DAILY_MODEL_USD: ${{ vars.DAILY_MODEL_USD }}", self.read(".github", "workflows", name))

    def test_the_workflows_are_still_yaml(self):
        import yaml
        for name in ("roundup.yml", "daily-prices.yml"):
            self.assertIn("jobs", yaml.safe_load(self.read(".github", "workflows", name)))

    def test_the_steps_counted_are_the_steps_the_schedule_runs(self):
        # each scheduled script names its ledger step in its own llm.client(...) call
        named = {"news/score.py": "news_score", "policy/score.py": "policy_score", "policy/reads.py": "policy_reads",
                 "deals/extract.py": "deals_extract", "datacenters/extract.py": "datacenters_extract",
                 "news/funfact.py": "funfact", "news/brief.py": "digest", "news/roundup.py": "roundup",
                 "analysis/run.py": "analysis_note", "news/shadow.py": "news_score_shadow"}
        for script, step in named.items():
            self.assertIn(f'"{step}"', self.read("warehouse", *script.split("/")), script)
            self.assertIn(step, health.SCHEDULED_MODEL_STEPS)
        self.assertNotIn("thesis", health.SCHEDULED_MODEL_STEPS)
        self.assertEqual(len(health.SCHEDULED_MODEL_STEPS), len(set(named.values())))

    def test_nothing_written_holds_an_em_dash(self):
        for p in (("warehouse", "health.py"), ("warehouse", "run_daily.sh"), ("warehouse", "news", "brief.py"),
                  ("warehouse", "news", "roundup.py"), ("docs", "methods", "api_cost_ledger.md"),
                  ("tests", "test_session176.py")):
            self.assertNotIn(chr(8212), self.read(*p), p)


class WithoutTheModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import brief
        except Exception as exc:  # a machine without the digest's own imports
            raise unittest.SkipTest(f"brief not importable here: {type(exc).__name__}")
        cls.brief = brief

    def test_a_headline_is_the_publishers_own_title(self):
        import pandas as pd
        dash = chr(8212)
        c = pd.DataFrame([{"cluster_id": "a", "titles": [f"Texas adds 2 GW of batteries {dash} ERCOT", "second"]},
                          {"cluster_id": "b", "titles": ["  FERC approves the rule  "]}])
        heads = self.brief.own_titles(c)
        self.assertEqual(heads["b"], "FERC approves the rule")
        self.assertTrue(heads["a"].startswith("Texas adds 2 GW of batteries"))
        self.assertNotIn(dash, heads["a"])

    def test_a_policy_action_that_repeats_a_story_above_is_dropped_not_fatal(self):
        said = []
        above = ["1. **Energy Department announces a nuclear investment** (nuclear)  ",
                 "   Why it matters. Sources: [DOE](https://www.energy.gov/articles/a)"]
        new = ["- Energy Department announces a nuclear investment (DOE news release, policy action): why [DOE](https://x.gov/1)",
               "- Another rule (FERC final rule, policy action): why [FERC](https://www.energy.gov/articles/a)",
               "- A third thing (NRC notice, policy action): why [NRC](https://www.nrc.gov/3)"]
        kept = self.brief.without_repeats(new, above, said.append)
        self.assertEqual(kept, new[2:])
        self.assertEqual(len(said), 2)
        self.assertEqual(self.brief.assert_unique(above + kept), 2)

    def test_the_digest_and_the_roundup_take_the_flag_and_build_no_client_with_it(self):
        b = open(os.path.join(ROOT, "warehouse", "news", "brief.py"), encoding="utf-8").read()
        r = open(os.path.join(ROOT, "warehouse", "news", "roundup.py"), encoding="utf-8").read()
        for src, call in ((b, 'llm.client("digest"'), (r, 'brief.llm.client("roundup"')):
            self.assertIn('"--no-model"', src)
            i = src.index("if args.no_model:")
            j = src.index(call)
            self.assertLess(i, j)
            self.assertIn("else:", src[i:j])  # the client is built only on the other branch
            self.assertIn("(None, []) if args.no_model else", src)
        self.assertIn("NO_MODEL_LINE", b)
        self.assertNotIn("recommend", self.brief.NO_MODEL_LINE)

    def test_a_whole_digest_is_written_with_no_model_call(self):
        ip = self.brief.ip
        stories = os.path.join(ip.OUT_DIR, "news_stories.csv")
        if not os.path.exists(stories):
            self.skipTest("news_stories.csv is not on this machine")
        d = tempfile.mkdtemp(prefix="erw176_")
        out = os.path.join(d, "digest.md")

        def never(*a, **k):
            raise AssertionError("a model client was built on the --no-model path")
        with mock.patch.object(self.brief.llm, "client", never), mock.patch.object(ip, "write_status", lambda *a, **k: None), \
                mock.patch.object(ip, "LOG_DIR", d), mock.patch.object(self.brief, "fun_fact_section", lambda *a: []):
            rc = self.brief.main(["--no-model", "--hours", "400", "--date", "2026-10-09", "--out", out])
        if rc != 0 and not os.path.exists(out):
            log = "".join(open(os.path.join(d, f), encoding="utf-8").read() for f in os.listdir(d) if f.endswith(".log"))
            if "no scored stories in the window" in log:
                self.skipTest("no scored story in the last 400 hours on this machine")
            if "ERWDataNotFound" in log:  # a clean copy or GitHub's test job: the news tables are in git, the prices are not
                self.skipTest("the price tables the digest's numbers read are not on this machine")
            self.fail(log[-1500:])
        text = open(out, encoding="utf-8").read()
        self.assertIn(self.brief.NO_MODEL_LINE, text)
        self.assertIn("## Top of the industry", text)
        self.assertIn("## ERW's Numbers Today", text)
        self.assertIn("model none (the daily model cap was reached)", text)
        self.assertNotIn(chr(8212), text)


if __name__ == "__main__":
    unittest.main()
