"""Session 206: the daily-run rulings of 12 October 2026 (docs/state/scheduled_failures_2026-10-12.md, the owner's
chain prompt of that day).

1. News scoring on the fixed model claude-haiku-4-5 (warehouse/news/score.py NEWS_SCORE_MODEL); SHADOW_MODEL out of
   the workflows.
2. The daily model cap 1.50 (warehouse/health.py MODEL_CAP_DEFAULT, DAILY_MODEL_USD in the workflows).
3. The cost ledger loaded as a union by event_id (warehouse/supabase/load.py, live_set.yaml union_by_key).
4. price_board_spreads judged by its newest timestamp, not its row count (warehouse/redivis/upload.py, config.yaml
   judge_by_newest, the manifest's newest_ts_utc).
5. Known gaps recorded as skipped, not failed, on the GitHub runner (iso_prices.gap_skip, exit 75; the connectors;
   run_other's 75 branch); nyiso_load_queue and Oregon's docket host in known_gaps.csv.
6. The three pulls in warehouse/run_data_machine.sh.
7. The digest's --auto sends only today's issue (email_digest.not_todays_issue).
8. Session 202's connectors patch applied (tests/test_session202.py holds that).
"""
import datetime as dt
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/news", "warehouse/supabase", "warehouse/redivis"):
    sys.path.insert(0, os.path.join(ROOT, p))
import email_digest as em  # noqa: E402
import health  # noqa: E402
import iso_prices as ip  # noqa: E402
import load  # noqa: E402
import upload  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheModel(unittest.TestCase):
    def test_news_scoring_uses_the_fixed_haiku_model_and_the_others_keep_pick_model(self):
        import score
        self.assertEqual(score.NEWS_SCORE_MODEL, "claude-haiku-4-5")
        s = src("warehouse", "news", "score.py")
        main = s[s.index("def main("):]
        self.assertIn("model = NEWS_SCORE_MODEL", main)
        self.assertNotIn("model = pick_model(client, log)", main)
        self.assertIn("def pick_model(client, log):", s)  # the other steps still import it
        self.assertIn("claude-haiku-4-5", score.PRICES)  # priced, so the cost is never "unknown"
        for f in ("warehouse/news/brief.py", "warehouse/news/roundup.py", "warehouse/policy/score.py"):
            self.assertIn("pick_model", src(*f.split("/")), f)

    def test_the_effort_parameter_is_not_sent_to_haiku(self):
        # the trial of 12 October 2026: Haiku answers HTTP 400 "This model does not support the effort parameter"
        s = src("warehouse", "news", "score.py")
        self.assertIn('if use_effort and "haiku" not in model.lower():', s)
        self.assertIn('"effort" in str(exc).lower()', s)

    def test_the_shadow_is_out_of_the_workflows(self):
        for name in ("daily-prices.yml", "roundup.yml"):
            wf = src(".github", "workflows", name)
            self.assertNotIn("SHADOW_MODEL: claude-haiku-4-5", wf, name)
        self.assertNotIn("run: python warehouse/news/shadow.py roundup", src(".github", "workflows", "roundup.yml"))


class TheCap(unittest.TestCase):
    def test_the_default_is_one_dollar_fifty(self):
        self.assertEqual(health.MODEL_CAP_DEFAULT, 1.50)
        with mock.patch.object(health, "env", lambda k: ""):
            self.assertEqual(health.model_cap(), 1.50)

    def test_the_workflows_set_the_same_figure(self):
        for name in ("daily-prices.yml", "roundup.yml"):
            wf = src(".github", "workflows", name)
            self.assertIn('DAILY_MODEL_USD: "1.50"', wf, name)
            self.assertNotIn("vars.DAILY_MODEL_USD", wf, name)


class TheLedgerUnion(unittest.TestCase):
    def test_the_ledger_is_a_union_table_and_nothing_else_is(self):
        self.assertTrue(load.union_table("api_cost_ledger"))
        for other in ("news_index", "price_board_spreads", "policy_reads", "api_cost_ledger_x"):
            self.assertFalse(load.union_table(other), other)

    def rows(self, ids):
        return pd.DataFrame([{"event_id": i, "event_date": "2026-10-10T10:00:00Z", "event_type": "model_call",
                              "parties": "", "entity_ids": "", "mw": "", "price": "", "currency": "USD", "status": "",
                              "source": "ledger", "source_url": ""} for i in ids])

    def sync(self, union, mine, theirs):
        calls = {"upsert": [], "delete": 0}

        class Q:
            def __init__(s):
                pass

            def upsert(s, recs, on_conflict=""):
                calls["upsert"] += recs
                return s

            def delete(s):
                calls["delete"] += 1
                return s

            def eq(s, *a):
                return s

            def lt(s, *a):
                return s

            def in_(s, *a):
                return s

            def execute(s):
                return s

        client = mock.Mock()
        client.table = lambda shape: Q()
        have = load.records("api_cost_ledger", self.rows(theirs), "events", "internal", "2026-10-09T00:00:00Z")
        with mock.patch.object(load, "existing_rows", lambda *a, **k: have):
            written, deleted = load.sync_table(client, "api_cost_ledger", self.rows(mine), "events", "internal",
                                               "2026-10-12T00:00:00Z", None, pd.Timestamp("2026-10-12", tz="UTC"), union=union)
        return written, deleted, calls

    def test_a_union_load_adds_the_rows_the_live_copy_lacks_and_removes_none(self):
        written, deleted, calls = self.sync(True, mine=["a", "b", "c"], theirs=["a", "x"])
        self.assertEqual((written, deleted), (2, 0))
        self.assertEqual(sorted(r["event_id"] for r in calls["upsert"]), ["b", "c"])
        self.assertEqual(calls["delete"], 0)  # "x", which the file lacks, stays

    def test_a_replacement_load_still_removes_what_the_file_lacks(self):
        written, deleted, calls = self.sync(False, mine=["a", "b"], theirs=["a", "x"])
        self.assertEqual((written, deleted), (1, 1))
        self.assertGreaterEqual(calls["delete"], 1)

    def test_main_skips_the_older_than_live_guard_for_a_union_table_and_matches_on_at_least(self):
        s = src("warehouse", "supabase", "load.py")
        self.assertIn("stale = None if unchanged or union or name in args.allow_older else older_than_live(", s)
        self.assertIn("ok = n >= len(df) if union else n == len(df)", s)
        y = src("warehouse", "supabase", "live_set.yaml")
        self.assertIn("union_by_key:", y)
        self.assertIn("  - '^api_cost_ledger$'", y[y.index("union_by_key:"):])


class JudgedByNewest(unittest.TestCase):
    def manifest(self, newest, rows="2285"):
        return pd.DataFrame([["price_board_spreads", "x", rows, "2026-10-10T15:46:26Z", "price_board_spreads",
                              upload.PUBLIC, "", newest]], columns=upload.MANIFEST_COLS).set_index("table")

    def test_the_spreads_table_is_judged_by_its_newest_timestamp(self):
        self.assertTrue(upload.judged_by_newest("price_board_spreads"))
        self.assertFalse(upload.judged_by_newest("price_board_carbon"))
        self.assertTrue(upload.rolling("price_board_spreads"))  # still a rolling-window table for the restore

    def test_fewer_rows_with_a_newer_or_equal_newest_pass(self):
        man = self.manifest("2026-10-06T00:00:00Z")
        self.assertIsNone(upload.shrink_refusal("price_board_spreads", 2283, man, set(), newest="2026-10-06T00:00:00Z"))
        self.assertIsNone(upload.shrink_refusal("price_board_spreads", 2283, man, set(), newest="2026-10-13T00:00:00Z"))
        self.assertIsNone(upload.shrink_refusal("price_board_spreads", 2283, self.manifest(""), set(), newest="2026-10-06T00:00:00Z"))

    def test_an_older_newest_is_refused_with_the_reason(self):
        man = self.manifest("2026-10-06T00:00:00Z")
        why = upload.shrink_refusal("price_board_spreads", 2300, man, set(), newest="2026-10-05T00:00:00Z")
        self.assertIn("newest ts_utc here, 2026-10-05T00:00:00Z, is older than the newest last uploaded, 2026-10-06T00:00:00Z", why)
        self.assertIn("--allow-shrink price_board_spreads", why)
        self.assertIsNone(upload.shrink_refusal("price_board_spreads", 2300, man, {"price_board_spreads"}, newest="2026-10-05T00:00:00Z"))

    def test_other_rolling_tables_are_still_judged_by_their_row_count(self):
        man = pd.DataFrame([["api_cost_ledger", "x", "3519", "t", "api_cost_ledger", upload.INTERNAL, "", ""]],
                           columns=upload.MANIFEST_COLS).set_index("table")
        self.assertIn("would shrink the rolling-window table", upload.shrink_refusal("api_cost_ledger", 3000, man, set()))
        self.assertIsNone(upload.shrink_refusal("api_cost_ledger", 3519, man, set()))

    def test_newest_ts_reads_past_the_header_lines(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("# Energy Research Warehouse (ERW): t\n# source: x\nentity,variable,ts_utc,value\n"
                        "a,v,2026-10-01T00:00:00Z,1\na,v,2026-10-09T00:00:00Z,2\na,v,2026-10-03T00:00:00Z,3\n")
            self.assertEqual(upload.newest_ts(p), "2026-10-09T00:00:00Z")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("entity_id,name\na,b\n")
            self.assertEqual(upload.newest_ts(p), "")

    def test_an_old_manifest_gains_the_column(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "redivis_uploads.csv")
            pd.DataFrame([["t", "x", "3", "u", "t", upload.PUBLIC, ""]], columns=upload.MANIFEST_COLS[:7]).to_csv(p, index=False)
            with mock.patch.object(upload, "MANIFEST", p):
                m = upload.read_manifest()
            self.assertEqual(list(m.columns), upload.MANIFEST_COLS)
            self.assertEqual(m["newest_ts_utc"].iloc[0], "")

    def test_the_real_manifest_carries_the_column(self):
        m = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "redivis_uploads.csv"), dtype=str, keep_default_na=False)
        self.assertIn("newest_ts_utc", m.columns)


class KnownGapsOnTheRunner(unittest.TestCase):
    def setUp(self):
        self.saved = {k: os.environ.get(k) for k in ("GITHUB_ACTIONS", "ERW_SKIP_EXIT")}

    def tearDown(self):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_the_file_names_the_four_and_the_queue_sheet(self):
        gaps = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "known_gaps.csv"), dtype=str, keep_default_na=False)
        for t in ("carb_auction_allowance_prices", "carb_lcfs_credit_prices", "nyiso_load_queue", "policy_monitor_refresh:orpuc",
                  "nyiso_interconnection_queue"):
            self.assertEqual((gaps["table"] == t).sum(), 1, t)
        for t in ("nyiso_load_queue", "policy_monitor_refresh:orpuc"):
            self.assertIn("Samuel, 12 October 2026", gaps.set_index("table").loc[t, "decided"])

    def test_off_the_runner_a_failure_stands(self):
        os.environ.pop("GITHUB_ACTIONS", None)
        self.assertIsNone(ip.gap_skip("carb_auction_allowance_prices", "HTTP 202"))
        self.assertIsNotNone(ip.known_gap("carb_auction_allowance_prices"))
        self.assertIsNone(ip.known_gap("ercot_rtm_node_prices"))

    def test_on_the_runner_a_known_gap_is_a_skip_and_any_other_table_a_failure(self):
        os.environ["GITHUB_ACTIONS"] = "true"
        why = ip.gap_skip("carb_lcfs_credit_prices", RuntimeError("HTTP 202 for https://ww2.arb.ca.gov/x"))
        self.assertTrue(why.startswith("a known gap on the GitHub runner since 2026-10-06"))
        self.assertIn("HTTP 202", why)
        self.assertIn("run_data_machine.sh", why)
        self.assertIsNone(ip.gap_skip("eia930_all_demand", "HTTP 500"))
        self.assertIsNotNone(ip.gap_skip("policy_monitor_refresh:orpuc", "ReadTimeout"))
        self.assertIsNotNone(ip.gap_skip("policy_monitor_refresh:orpuc", "ConnectionError(MaxRetryError('HTTPSConnectionPool(host=...)'))"))
        self.assertIsNotNone(ip.gap_skip("nyiso_load_queue", "RuntimeError: the answer is not the workbook (HTTP 202, first bytes b'')"))
        self.assertIsNone(ip.gap_skip("policy_monitor_refresh:txpuc", "HTTP 403"))

    def test_a_connectors_own_refusal_is_a_failure_even_on_the_runner(self):
        # the gap is the publisher's answer: a ceiling, a parse or a validator of a document that did arrive is ours
        os.environ["GITHUB_ACTIONS"] = "true"
        for own in ("RuntimeError: 20 rows would pass this run's ceiling of 19; nothing is written",
                    "KeyError: 'Load Projects'", "ValueError: no auction table in the PDF",
                    "RuntimeError: carb_auction_allowance_prices: newest auction 2026-05-01 is 160 days old; not writing"):
            self.assertIsNone(ip.gap_skip("nyiso_load_queue", own), own)
            self.assertIsNone(ip.gap_skip("carb_auction_allowance_prices", own), own)
        self.assertIsNotNone(ip.gap_skip("carb_auction_allowance_prices",
                                         "RuntimeError: CARB auction summary PDF failed after 4 attempts: RuntimeError('CARB auction summary PDF HTTP 202')"))

    def test_the_skip_exit_is_75_or_the_environment(self):
        os.environ.pop("ERW_SKIP_EXIT", None)
        self.assertEqual(ip.skip_exit(), 75)
        os.environ["ERW_SKIP_EXIT"] = "75"
        self.assertEqual(ip.skip_exit(), 75)

    def test_each_connector_asks_before_it_records_a_failure(self):
        for f, table in (("carbon_auctions.py", "name"), ("carb_lcfs.py", "NAME"), ("nyiso_load_queue.py", "NAME"),
                         ("iso_queues.py", "name")):
            s = src("warehouse", "connectors", f)
            self.assertIn(f"ip.gap_skip({table}, last)", s, f)
            self.assertIn("ip.skip_exit()", s, f)
            self.assertIn('status="skipped"', s, f)
        p = src("warehouse", "connectors", "policy_monitor_refresh.py")
        self.assertIn('ip.gap_skip(f"{NAME}:{key}"', p)
        self.assertIn('"skipped" if gap else "failed"', p)
        self.assertIn("SKIPPED for", p)
        self.assertIn('status=v["status"] if v["status"] in ("failed", "skipped") else "ok"', p)

    def test_run_other_reads_the_skip_exit(self):
        sh = src("warehouse", "run_daily.sh")
        fn = sh[sh.index("run_other() {"):sh.index("# Derived (session 9)")]
        self.assertIn('elif [ "$rc" -eq 75 ]; then', fn)
        self.assertIn("skipped:", fn[fn.index('-eq 75'):])

    def test_the_connectors_still_exit_1_on_a_real_failure(self):
        for f in ("carbon_auctions.py", "carb_lcfs.py", "nyiso_load_queue.py", "iso_queues.py"):
            s = src("warehouse", "connectors", f)
            self.assertRegex(s, r"if (failures|any\(r\[\"status\"\] == \"failed\" for r in results\)):\s*\n\s*return 1", f)


class TheDataMachine(unittest.TestCase):
    def test_the_three_pulls_are_in_the_daily_run_with_their_stores(self):
        sh = src("warehouse", "run_data_machine.sh")
        for step, cmd in (("dm_carb_auction", "warehouse/connectors/carbon_auctions.py --table carb"),
                          ("dm_carb_lcfs", "warehouse/connectors/carb_lcfs.py"),
                          ("dm_orpuc_dockets", "warehouse/connectors/policy_monitor_refresh.py --only orpuc")):
            self.assertIn(f'soft_step {step} "$PYTHON" {cmd}', sh)
        for stores, table in (("dm_carb_auction_stores", '"$CARB"'), ("dm_carb_lcfs_stores", '"$LCFS"'),
                              ("dm_orpuc_rules_stores", '"$RULES"'), ("dm_orpuc_held_stores", '"$RULES_HELD"')):
            self.assertIn(f"table_stores {stores} {table}", sh)
        # after the node prices, before the load zones: the order the header describes
        self.assertLess(sh.index("table_stores dm_node_stores"), sh.index("soft_step dm_carb_auction"))
        self.assertLess(sh.index("soft_step dm_orpuc_dockets"), sh.index("# ---- 2. ERCOT's load zones"))
        self.assertIn("(session 206) then the runner's known gaps", sh)

    def test_the_machines_document_names_the_steps(self):
        d = src("docs", "machines.md")
        for step in ("dm_carb_auction", "dm_carb_lcfs", "dm_orpuc_dockets"):
            self.assertIn(step, d)


class TheDigestsDate(unittest.TestCase):
    def write(self, d, title):
        p = os.path.join(d, "latest.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\nbody\n")
        return p

    def test_todays_issue_is_sent(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.write(d, "ERW's Energy Digest, 2026-10-12")
            now = dt.datetime(2026, 10, 12, 15, 40, tzinfo=dt.timezone.utc)
            self.assertEqual(em.issue_of(p), "2026-10-12")
            self.assertIsNone(em.not_todays_issue(p, now))

    def test_an_earlier_issue_is_not_sent_again(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.write(d, "ERW's Energy Digest, 2026-10-02")
            why = em.not_todays_issue(p, dt.datetime(2026, 10, 5, 15, 40, tzinfo=dt.timezone.utc))  # Monday 5 October
            self.assertIn("the issue of 2026-10-02, not today's (2026-10-05 UTC)", why)
            self.assertIn("nothing is sent", why)

    def test_no_file_is_no_send(self):
        with tempfile.TemporaryDirectory() as d:
            why = em.not_todays_issue(os.path.join(d, "none.md"), dt.datetime(2026, 10, 5, tzinfo=dt.timezone.utc))
            self.assertIn("no date", why)

    def test_main_with_auto_skips_and_records_before_any_send(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.write(d, "ERW's Energy Digest, 2026-10-02")
            statuses = []
            monday = dt.datetime(2026, 10, 5, 15, 40, tzinfo=dt.timezone.utc)

            class Clock(dt.datetime):
                @classmethod
                def now(cls, tz=None):
                    return monday if tz else monday.replace(tzinfo=None)

            with mock.patch.object(em, "DIGEST", p), mock.patch.object(em.dt, "datetime", Clock), \
                    mock.patch.object(em.ip, "write_status", lambda *a: statuses.append(a)), \
                    mock.patch.object(em.ip, "LOG_DIR", d), \
                    mock.patch.object(em, "send", lambda *a, **k: self.fail("send was called")):
                self.assertEqual(em.main(["--auto"]), 0)
            self.assertEqual(len(statuses), 1)
            rows = statuses[0][2]
            self.assertEqual((rows[0]["status"], rows[0]["market"]), ("skipped", "daily"))
            self.assertIn("the issue of 2026-10-02", rows[0]["detail"])

    def test_the_roundup_is_not_held_to_the_daily_date(self):
        s = src("warehouse", "news", "email_digest.py")
        self.assertIn("if args.auto and not_todays_issue():", s)
        self.assertNotIn("if args.roundup and not_todays_issue", s)


class NoDashes(unittest.TestCase):
    def test_no_em_dash_in_what_this_session_wrote(self):
        for f in ("warehouse/news/score.py", "warehouse/health.py", "warehouse/supabase/load.py", "warehouse/supabase/live_set.yaml",
                  "warehouse/redivis/upload.py", "warehouse/redivis/config.yaml", "warehouse/connectors/carbon_auctions.py",
                  "warehouse/connectors/carb_lcfs.py", "warehouse/connectors/nyiso_load_queue.py", "warehouse/connectors/iso_queues.py",
                  "warehouse/connectors/policy_monitor_refresh.py", "warehouse/news/email_digest.py", "warehouse/run_daily.sh",
                  "warehouse/run_data_machine.sh", "warehouse/metadata/known_gaps.csv", ".github/workflows/daily-prices.yml",
                  ".github/workflows/roundup.yml", "docs/methods/api_cost_ledger.md", "docs/runbook.md", "tests/test_session206.py"):
            s = src(*f.split("/"))
            if f == "warehouse/news/score.py":  # nodash() names the character it removes; nothing else may
                s = s.replace('replace("' + chr(0x2014) + '", " - ")', "")
            self.assertNotIn(chr(0x2014), s, f)


if __name__ == "__main__":
    unittest.main()
