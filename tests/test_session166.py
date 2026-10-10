"""Session 166 (9 October 2026): the live-set load fixed at the root and gated, the board on the runner.

- The loader's three whole-table reads (what Supabase holds for a table, its newest retrieved_at, its count) go
  through the direct Postgres connection when one is open, and through the API when none is: the API path ran under
  the authenticator role's 8-second statement timeout and failed on ercot_as_prices on 5, 6, 7 and 8 October 2026.
- The daily run loads the live set under warehouse/health.py --strict, so a failed load reaches erw_health and the
  same-day failure email.
- The board's builder skips an ancillary service table that is not on the machine (page_keep.py keeps the held rows),
  the board's validate step lists only the files present, and the board step runs after the ancillary service
  connectors.
- SPP's real-time market is checked per operating day.

Every test here runs without the tables and without the network: the connection and the client are stubs.
"""
import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import load  # noqa: E402


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)

    def fetchone(self):
        return self.rows[0]


class FakeConn:
    """Answers each SELECT from a script: {fragment of the SQL: rows}. Records every statement."""

    def __init__(self, script):
        self.script, self.sql, self.closed, self.broken = script, [], False, False

    def execute(self, q, params=None):
        self.sql.append((q, params))
        for frag, rows in self.script.items():
            if frag in q:
                return FakeCursor(rows)
        raise AssertionError(f"no scripted answer for {q}")

    def close(self):
        self.closed = True


class FailingClient:
    """The API client: any call is a failure (the tests prove the API is not asked when the connection is open)."""

    def table(self, name):
        raise AssertionError(f"the API was asked for {name}")


class DirectReads(unittest.TestCase):
    def test_existing_rows_is_one_select_without_order_or_offset(self):
        rows = [{"table_name": "t", "entity": "e", "variable": "v", "ts_utc": "2026-10-08T00:00:00+00:00", "value": 1.0}]
        conn = FakeConn({"from series where table_name": rows})
        got = load.existing_rows(FailingClient(), "series", "t", conn)
        self.assertEqual(got, rows)
        q, params = conn.sql[0]
        self.assertEqual(params, ("t",))
        self.assertNotIn("order", q.lower())
        self.assertNotIn("offset", q.lower())
        self.assertTrue(q.startswith("select table_name,"))

    def test_live_count_through_the_connection(self):
        conn = FakeConn({"select count(*)": [{"n": 336692}]})
        self.assertEqual(load.live_count(FailingClient(), "series", "ercot_as_prices", conn), 336692)

    def test_older_than_live_reads_max_retrieved_at_through_the_connection(self):
        df = pd.DataFrame({"retrieved_at": ["2026-10-07T14:49:00Z"]})
        conn = FakeConn({"select max(retrieved_at)": [{"t": pd.Timestamp("2026-10-08T15:08:54Z").to_pydatetime()}]})
        why = load.older_than_live(FailingClient(), "ercot_as_prices", df, "series", conn)
        self.assertIn("Supabase holds rows retrieved", why or "")
        self.assertIn("2026-10-07T14:49:00Z", why)
        newer = pd.DataFrame({"retrieved_at": ["2026-10-09T07:00:00Z"]})
        self.assertIsNone(load.older_than_live(FailingClient(), "ercot_as_prices", newer, "series", conn))

    def test_older_than_live_by_count_for_a_table_without_retrieved_at(self):
        df = pd.DataFrame({"event_id": ["a", "b"]})
        conn = FakeConn({"select count(*)": [{"n": 3}]})
        self.assertIn("3", load.older_than_live(FailingClient(), "api_cost_ledger", df, "events", conn))
        conn = FakeConn({"select count(*)": [{"n": 2}]})
        self.assertIsNone(load.older_than_live(FailingClient(), "api_cost_ledger", df, "events", conn))

    def test_without_a_url_the_reader_is_none_and_the_api_path_stands(self):
        old = os.environ.get("SUPABASE_DB_URL")
        os.environ["SUPABASE_DB_URL"] = ""
        try:
            self.assertTrue(hasattr(load, "db_reader"))
            src = open(os.path.join(ROOT, "warehouse", "supabase", "load.py"), encoding="utf-8").read()
            self.assertIn("statement_timeout = '600s'", src)
            # the API path is kept for a machine without the URL: the paged read is still there
            self.assertIn(".range(start, start + BATCH - 1)", src)
        finally:
            if old is None:
                del os.environ["SUPABASE_DB_URL"]
            else:
                os.environ["SUPABASE_DB_URL"] = old


class TheDailyRun(unittest.TestCase):
    def setUp(self):
        self.daily = open(os.path.join(ROOT, "warehouse", "run_daily.sh"), encoding="utf-8").read()

    def test_the_load_runs_under_health_strict(self):
        for line in self.daily.splitlines():
            if "warehouse/supabase/load.py" in line and not line.lstrip().startswith("#"):
                self.assertIn('warehouse/health.py run --strict --step "supabase_load"', line, line)

    def test_the_board_step_follows_the_ancillary_service_connectors(self):
        lines = [ln for ln in self.daily.splitlines() if not ln.lstrip().startswith("#")]
        i_board = next(i for i, ln in enumerate(lines) if "refresh_board.sh" in ln)
        i_ercot = next(i for i, ln in enumerate(lines) if "connectors/ercot_as_prices.py" in ln)
        i_caiso = next(i for i, ln in enumerate(lines) if "connectors/caiso_as_prices.py" in ln)
        self.assertGreater(i_board, max(i_ercot, i_caiso))

    def test_the_board_validates_only_the_files_present(self):
        src = open(os.path.join(ROOT, "warehouse", "refresh_board.sh"), encoding="utf-8").read()
        self.assertRegex(src, r'\[ -f "warehouse/output/\$t\.csv" \] && FILES=')


class TheBoardBuilder(unittest.TestCase):
    def test_an_ancillary_service_table_not_on_the_machine_is_skipped(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import board_page  # noqa: E402
        old = board_page.ip.OUT_DIR
        board_page.ip.OUT_DIR = os.path.join(ROOT, "runs", "no_such_folder_session166")
        try:
            b = board_page.Board()
            lines = []
            board_page.build_as(b, set(), lines.append)
            skipped = [ln for ln in lines if "not on this machine, skipped" in ln]
            self.assertEqual(len(skipped), 4, lines)
            self.assertEqual([r["status"] for r in b.rows], ["not_held", "paused", "licensed"])
        finally:
            board_page.ip.OUT_DIR = old


class SPP(unittest.TestCase):
    def test_the_real_time_market_is_checked_per_day(self):
        src = open(os.path.join(ROOT, "warehouse", "connectors", "iso_prices.py"), encoding="utf-8").read()
        spp = src[src.index("def pull_spp("):src.index("# ISO-NE")]
        rtm = spp[spp.index('dict(name="RTM"'):]
        self.assertIn("per_day=True", rtm[:rtm.index("file=")])

    def test_the_known_gap_and_the_gap_day_are_recorded(self):
        gaps = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "known_gaps.csv"), dtype=str)
        row = gaps[gaps["table"] == "carb_lcfs_credit_prices"]
        self.assertEqual(len(row), 1)
        self.assertIn("Samuel, 8 October 2026", row["decided"].iloc[0])
        status = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "run_status.csv"), dtype=str, keep_default_na=False)
        spp = status[(status["run_id"] == "20261008T141233Z") & (status["table"] == "spp_rtm_hub_prices") & (status["market"].str.startswith("RTM"))]
        self.assertEqual(list(spp["status"]), ["gap"])
        self.assertEqual(list(spp["market"]), ["RTM 2026-10-07"])


class NoPageLive(unittest.TestCase):
    def test_release_has_no_live_page(self):
        src = open(os.path.join(ROOT, "site", "lib", "release.ts"), encoding="utf-8").read()
        self.assertEqual(re.findall(r'^\s*"/[^"]*":\s*"live"', src, re.M), [])


if __name__ == "__main__":
    unittest.main()
