"""Session 431: the database gate. scripts/db_probe.py times one ordered read of the series table under a 5-second
statement timeout: exit 0 under 3 seconds, exit 1 when slower, empty, timed out or not connected; each probe a line of
runs/db_probe.log. It reads only."""

import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import db_probe  # noqa: E402


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows


class FakeConn:
    def __init__(self, rows=None, error=None):
        self.rows, self.error, self.sql = rows or [], error, []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.sql.append((sql, params))
        if self.error and sql.startswith("select"):
            raise self.error
        return FakeCursor(self.rows)


def clock(*times):
    it = iter(times)
    return lambda: next(it)


class Probe(unittest.TestCase):
    def test_a_fast_read_opens_the_gate(self):
        conn = FakeConn(rows=[("ERCOT", "lmp", "2026-10-21", 1.0)] * 1000)
        code, s, what = db_probe.probe("url", connect=lambda u: conn, clock=clock(0.0, 0.4))
        self.assertEqual((code, round(s, 2)), (0, 0.4))
        self.assertIn("1000 rows of iso_dam_hub_prices", what)
        self.assertEqual(conn.sql[0][0], "set statement_timeout = 5000")
        self.assertTrue(conn.sql[1][0].startswith("select entity, variable, ts_utc, value from series"))
        self.assertIn("order by entity, variable, ts_utc, event", conn.sql[1][0])
        self.assertEqual(conn.sql[1][1], ("iso_dam_hub_prices", 1000))
        self.assertFalse(any(q.split()[0] in ("insert", "update", "delete") for q, _ in conn.sql))

    def test_three_seconds_or_more_closes_it(self):
        conn = FakeConn(rows=[("x", "y", "z", 1.0)])
        self.assertEqual(db_probe.probe("url", connect=lambda u: conn, clock=clock(0.0, 3.0))[0], 1)

    def test_a_statement_timeout_closes_it_and_says_so(self):
        err = RuntimeError("canceling statement due to statement timeout\nCONTEXT: ...")
        code, s, what = db_probe.probe("url", connect=lambda u: FakeConn(error=err), clock=clock(0.0, 5.1))
        self.assertEqual(code, 1)
        self.assertEqual(what, "RuntimeError: canceling statement due to statement timeout")

    def test_no_rows_closes_it(self):
        # a table not in the live set reads in no time and proves nothing
        code, _, what = db_probe.probe("url", table="iso_hub_prices_history", connect=lambda u: FakeConn(rows=[]),
                                       clock=clock(0.0, 0.1))
        self.assertEqual((code, what), (1, "no rows of iso_hub_prices_history"))

    def test_a_refused_connection_closes_it(self):
        def refuse(u):
            raise OSError("connection refused")
        self.assertEqual(db_probe.probe("url", connect=refuse, clock=clock(0.0, 0.2))[0], 1)

    def test_main_logs_one_line_a_probe_and_returns_the_code(self):
        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "runs", "db_probe.log")
            with mock.patch.object(db_probe, "db_url", return_value="url"), \
                    mock.patch.object(db_probe, "probe", return_value=(0, 0.45, "1000 rows of iso_dam_hub_prices")):
                self.assertEqual(db_probe.main(["--log", log]), 0)
            with mock.patch.object(db_probe, "db_url", return_value=None):
                self.assertEqual(db_probe.main(["--log", log]), 1)
            lines = open(log, encoding="utf-8").read().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertRegex(lines[0], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ open 0\.45 s 1000 rows of iso_dam_hub_prices$")
        self.assertIn("CLOSED", lines[1])
        self.assertIn("SUPABASE_DB_URL is not set", lines[1])


if __name__ == "__main__":
    unittest.main()
