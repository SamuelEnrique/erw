"""Session 321: the daily run finishes.

Energy Research Warehouse (ERW). The daily job was cancelled at GitHub's 180-minute limit on 14, 15 and 19 October 2026,
waiting on CAISO's and SPP's hosts and on EIA's API. These tests hold the fix (no network, no keys; the rows are test
fixtures, not data values):

  1. warehouse/pull_budget.py: a command still running at its budget is stopped and settled as a skip (exit 75) with gap
     rows; a connector that left the budget's mark has its failed tables turned into gap rows; otherwise the exit passes.
  2. warehouse/connectors/iso_prices.py: under ERW_PULL_DEADLINE a publisher's request is cut to the time left and refused
     after it, and with_retries does not retry past it; the warehouse's own stores are never cut.
  3. The wiring: every publisher pull of run_daily.sh under the budget, the job's 300 minutes and the lock's 320, the
     gate reading the daily step's row of erw_health, a stopped run recorded as failed, and a failed step recorded.
  4. eia930_emissions: a window with no complete CO2 day yet is "stale at source", a skip.

    python -m unittest tests.test_session321 -v
"""

import json
import os
import re
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import pull_budget as pb  # noqa: E402
import iso_prices as ip  # noqa: E402


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Budget(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.status = os.path.join(self.tmp, "status")
        os.makedirs(self.status)
        self.marks = mock.patch.object(pb, "MARK_DIR", os.path.join(self.tmp, "budget"))
        self.marks.start()
        self.rs = os.path.join(self.tmp, "run_status.csv")
        with open(self.rs, "w", encoding="utf-8") as f:
            f.write("run_id,runner,connector,table,market,status,detail\n"
                    "20261018T140000Z,github,caiso,caiso_dam_hub_prices,DAM,ok,\n"
                    "20261018T140000Z,github,caiso,caiso_rtm_hub_prices,RTM,ok,\n"
                    "20261017T140000Z,github,caiso,caiso_old_table,DAM,ok,\n")

    def tearDown(self):
        self.marks.stop()

    def test_no_budget_spent_passes_the_exit(self):
        self.assertEqual(pb.settle("caiso", 1, time.time(), 15, False, self.status, self.rs), (1, None))
        self.assertEqual(pb.settle("caiso", 0, time.time(), 15, False, self.status, self.rs), (0, None))

    def test_a_stopped_pull_is_a_skip_with_gap_rows(self):
        code, line = pb.settle("caiso", 124, time.time(), 15, True, self.status, self.rs)
        self.assertEqual(code, 75)
        self.assertEqual(line, "caiso SKIPPED: publisher did not answer within the budget (15 minutes of wall clock); "
                               "asked again by the next run")
        doc = load(os.path.join(self.status, "caiso.json"))
        self.assertEqual(sorted(r["table"] for r in doc["results"]), ["caiso_dam_hub_prices", "caiso_rtm_hub_prices"])
        for r in doc["results"]:
            self.assertEqual(r["status"], "gap")
            self.assertTrue(r["detail"].startswith(pb.REASON))
            self.assertRegex(r["market"], r"^all \d{4}-\d{2}-\d{2}$")  # build_status reads the day from the market

    def test_the_mark_turns_failed_tables_into_gaps(self):
        since = time.time()
        os.makedirs(pb.MARK_DIR, exist_ok=True)
        open(pb.mark_path("spp"), "w").write("x\n")
        with open(os.path.join(self.status, "spp.json"), "w", encoding="utf-8") as f:
            json.dump({"connector": "spp", "run_id": "r", "runner": "github", "results": [
                {"table": "spp_dam_hub_prices", "market": "DAM", "status": "failed", "detail": "RuntimeError: x"},
                {"table": "spp_rtm_hub_prices", "market": "RTM", "status": "ok", "detail": ""}]}, f)
        code, line = pb.settle("spp", 1, since, 15, False, self.status, self.rs)
        self.assertEqual(code, 75)
        rows = load(os.path.join(self.status, "spp.json"))["results"]
        self.assertEqual([r["status"] for r in rows], ["gap", "ok"])
        self.assertTrue(rows[0]["market"].startswith("DAM 20"))
        self.assertIn("RuntimeError: x", rows[0]["detail"])

    def test_the_wrapper_stops_a_command_at_its_budget(self):
        rs = mock.patch.object(pb, "RUN_STATUS", self.rs)
        st = mock.patch.object(pb, "STATUS_DIR", self.status)
        with rs, st:
            t0 = time.time()
            code = pb.main(["--step", "slow_test_step", "--minutes", "0.03", "--", sys.executable, "-c",
                            "import time; time.sleep(60)"])
        self.assertEqual(code, 75)
        self.assertLess(time.time() - t0, 40)
        doc = load(os.path.join(self.status, "slow_test_step.json"))
        self.assertEqual(doc["results"][0]["table"], "slow_test_step")  # no run recorded: the step's own name

    def test_the_wrapper_passes_the_deadline_and_the_exit(self):
        code = pb.main(["--step", "quick_test_step", "--minutes", "15", "--", sys.executable, "-c",
                        "import os, sys, time; d = float(os.environ['ERW_PULL_DEADLINE']); "
                        "sys.exit(3 if 800 < d - time.time() < 901 and os.environ['ERW_PULL_STEP'] == 'quick_test_step' else 9)"])
        self.assertEqual(code, 3)


class Deadline(unittest.TestCase):
    def test_no_deadline_changes_nothing(self):
        with mock.patch.dict(os.environ, {"ERW_PULL_DEADLINE": ""}):
            self.assertEqual(ip.budget_timeout("https://oasis.caiso.com/x", 180), 180)
            self.assertIsNone(ip.budget_timeout("https://oasis.caiso.com/x", None))

    def test_a_publisher_request_is_cut_to_the_time_left(self):
        with mock.patch.dict(os.environ, {"ERW_PULL_DEADLINE": str(time.time() + 100), "ERW_PULL_STEP": ""}):
            self.assertLessEqual(ip.budget_timeout("https://oasis.caiso.com/x", 180), 100)
            self.assertEqual(ip.budget_timeout("https://oasis.caiso.com/x", 30), 30)
            c, r = ip.budget_timeout("https://portal.spp.org/x", (180, 600))
            self.assertLessEqual(max(c, r), 100)
            self.assertLessEqual(ip.budget_timeout("https://api.eia.gov/x", None), 100)
            # the warehouse's own stores are not publishers
            self.assertEqual(ip.budget_timeout("https://abc.supabase.co/rest/v1/t", 180), 180)

    def test_no_request_after_the_deadline(self):
        with mock.patch.dict(os.environ, {"ERW_PULL_DEADLINE": str(time.time() - 5), "ERW_PULL_STEP": ""}):
            with self.assertRaises(ip.BudgetExhausted) as cm:
                ip.budget_timeout("https://oasis.caiso.com/x", 180)
            self.assertIn(ip.BUDGET_REASON, str(cm.exception))

    def test_no_retry_past_the_deadline(self):
        calls = []

        def fn():
            calls.append(1)
            raise TimeoutError("timed out")
        with mock.patch.dict(os.environ, {"ERW_PULL_DEADLINE": str(time.time() + 2), "ERW_PULL_STEP": ""}):
            with self.assertRaises(ip.BudgetExhausted):
                ip.with_retries("CAISO DAM 2026-10-15", fn, lambda m: None)
        self.assertEqual(len(calls), 1)

    def test_the_step_name_and_pb_agree_on_the_mark(self):
        self.assertEqual(ip.BUDGET_REASON, pb.REASON)


class Wiring(unittest.TestCase):
    def setUp(self):
        self.daily = src("warehouse", "run_daily.sh")
        self.wf = src(".github", "workflows", "daily-prices.yml")

    def test_every_publisher_pull_is_under_the_budget(self):
        for name in ("eia930", "eia930_storage", "eia930_emissions", "caiso_fuel_supply", "eia930_interchange",
                     "weather_nws", "eia_fuels", "eia_series", "capacity_prices", "carbon_auctions", "portwatch",
                     "curtailment", "ercot_wind_solar_history", "caiso_outlook", "eia860", "iso_queues",
                     "nyiso_load_queue", "ercot_large_load", "datacenter_operators", "news_ingest", "policy_sources"):
            self.assertRegex(self.daily, rf"\n\s*pull {name} ")
        for name in ("ercot_as_prices", "caiso_as_prices", "iso_capacity_prices", "eia930_daily_interchange",
                     "eia930_daily_demand", "ercot_storage_dam", "policy_monitor_refresh"):
            self.assertIn(f'"${{BUDGET[@]}}" {name} -- ', self.daily)
        self.assertIn('"${BUDGET[@]}" "$iso" -- "$PYTHON" warehouse/connectors/iso_prices.py', self.daily)
        for f, names in (("refresh_board.sh", ("eia_board", "frb_treasury", "imf_pcps", "carb_lcfs")),
                         ("refresh_supply.sh", ("eia_supply", "cftc_cot", '"${iso}_dam_cleared"', '"${t}_load"',
                                                "zone_price_history_pull", "release_schedule"))):
            for n in names:
                self.assertIn(f"pull_budget.py --minutes \"${{PULL_BUDGET_MIN:-15}}\" --step {n} -- ", src("warehouse", f))

    def test_the_job_and_the_lock(self):
        self.assertIn("timeout-minutes: 300", self.wf)
        self.assertNotIn("timeout-minutes: 180", self.wf)
        self.assertIn("--minutes 320 --wait 60", self.wf)

    def test_the_gate_reads_the_daily_step(self):
        gate = self.wf.split("  gate:", 1)[1].split("  note-skip:", 1)[0]
        self.assertIn("erw_health?select=run_id&workflow=eq.daily%20prices&step=eq.daily%20run&status=in.(ok,retried)", gate)
        self.assertNotIn("runs?status=success", gate)
        self.assertIn('startswith(\\"Daily prices ${today}\\")', gate)

    def test_a_stopped_run_is_a_failed_row(self):
        step = self.wf.split("- name: Record a daily run stopped at the time limit", 1)[1].split("- name:", 1)[0]
        self.assertIn("if: always() && steps.daily.outcome == 'cancelled'", step)
        self.assertIn('--step "daily run" --status failed', step)

    def test_a_failed_step_is_a_failed_row(self):
        body = self.daily.split("run_other() {", 1)[1].split("\n}\n", 1)[0]
        self.assertIn('health_row "$name" failed', body)
        self.assertIn('*"warehouse/health.py run"*) ;;', body)  # a step under health.py run recorded itself
        self.assertIn('health_row "$iso" failed', self.daily)
        self.assertIn('[ "${DRY_STORES:-0}" = "1" ] && return 0', self.daily)


class Downstream(unittest.TestCase):
    def test_generation_mix_skips_when_eia_series_did_not_write(self):
        # session 327: the manual run of 20 October 2026 stopped eia_series at its budget and generation_mix then failed
        sh = src("warehouse", "run_daily.sh")
        self.assertIn("if [ -f warehouse/output/eia_state_generation_monthly.csv ]; then\n  run_other generation_mix", sh)
        self.assertIn("generation_mix skipped: its input eia_state_generation_monthly is not on this machine", sh)


class Status(unittest.TestCase):
    def test_a_budget_gap_closes_with_the_next_good_run(self):
        s = src("warehouse", "metadata", "build_status.py")
        self.assertIn(f'BUDGET_REASON = "{pb.REASON}"', s)
        self.assertIn('if str(g.detail).startswith(BUDGET_REASON) and str(oks.get(g.table, "")) > str(g.run_id):', s)


class Emissions(unittest.TestCase):
    def test_no_complete_day_is_stale_at_source(self):
        s = src("warehouse", "connectors", "eia930_emissions.py")
        self.assertIn('raise RuntimeError("stale at source: no complete day of CO2 values in the window', s)
        self.assertIn("ip.gap_skip(NAME, last)", s)
        why = ip.stale_skip("RuntimeError: stale at source: no complete day of CO2 values in the window; EIA's newest "
                            "workbooks hold none yet (CISO: x)")
        self.assertTrue(why and why.startswith("stale at source"))
        self.assertIn('eia930_emissions.py --days "${EMISSIONS_DAYS:-10}"', src("warehouse", "run_daily.sh"))


if __name__ == "__main__":
    unittest.main()
