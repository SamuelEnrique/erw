"""Session 455: the loader compares values, not stamps. A row whose values have not moved is not written again when only
its retrieved_at has (session 438 wrote 30,232 rows for 8 changed values); a copy older by its stamps but equal in value
is no rollback (session 374's 31 refusals); and series is vacuumed after a load only when the load changed more than 1%
of it, else analysed (a VACUUM of 2.1 GB after 474 rows, session 432)."""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import load  # noqa: E402


def frame(rows):
    """A series table as the loader reads it: every column a string."""
    out = []
    for ts, value, stamp in rows:
        r = {c: "" for c in load.SERIES_COLS}
        r.update(entity="ercot:HB_HUBAVG", variable="spp_rtm", ts_utc=ts, value=str(value), unit="USD/MWh", freq="PT15M",
                 source="ercot:NP6-905-CD", retrieved_at=stamp)
        out.append(r)
    return pd.DataFrame(out, columns=load.SERIES_COLS)


def live(df, name="t_table", license_="public"):
    """What Supabase would hold after a load of df: the loader's own records."""
    return load.records(name, df, "series", license_, "2026-10-20T00:00:00Z")


class FakeConn:
    def __init__(self, rows):
        self.rows = rows

    def execute(self, sql, params=None):
        return list(self.rows)


class Query:
    def __init__(self, log, op, rows=None):
        self.log, self.op, self.rows = log, op, rows

    def __getattr__(self, _):
        return lambda *a, **k: self

    def execute(self):
        self.log.append((self.op, len(self.rows or [])))
        return self


class FakeClient:
    def __init__(self):
        self.log = []

    def table(self, _):
        client = self

        class T:
            def upsert(self, rows, on_conflict=None):
                return Query(client.log, "upsert", rows)

            def delete(self):
                return Query(client.log, "delete")
        return T()


OLD = frame([("2026-10-19T05:00:00Z", 30.5, "2026-10-19T06:00:00Z"), ("2026-10-19T05:15:00Z", 31.0, "2026-10-19T06:00:00Z")])


class ValuesNotStamps(unittest.TestCase):
    def test_new_stamps_on_the_same_values_write_nothing(self):
        new = frame([("2026-10-19T05:00:00Z", 30.5, "2026-10-21T08:00:00Z"), ("2026-10-19T05:15:00Z", 31.0, "2026-10-21T08:00:00Z")])
        write, gone = load.value_diff(None, "t_table", new, "series", "public", "x", FakeConn(live(OLD)))
        self.assertEqual((write, gone), ([], []))

    def test_a_moved_value_is_written_with_its_new_stamp(self):
        new = frame([("2026-10-19T05:00:00Z", 30.5, "2026-10-21T08:00:00Z"), ("2026-10-19T05:15:00Z", 31.2, "2026-10-21T08:00:00Z")])
        write, gone = load.value_diff(None, "t_table", new, "series", "public", "x", FakeConn(live(OLD)))
        self.assertEqual([(r["ts_utc"], r["value"], r["retrieved_at"]) for r in write],
                         [("2026-10-19T05:15:00Z", 31.2, "2026-10-21T08:00:00Z")])
        self.assertEqual(gone, [])

    def test_an_older_copy_equal_in_value_has_nothing_to_write(self):
        # session 374: a copy restored from the archive, its stamps older than the live rows', its values the same
        newer_live = live(frame([("2026-10-19T05:00:00Z", 30.5, "2026-10-20T06:33:59Z"), ("2026-10-19T05:15:00Z", 31.0, "2026-10-20T06:33:59Z")]))
        write, gone = load.value_diff(None, "t_table", OLD, "series", "public", "x", FakeConn(newer_live))
        self.assertEqual((write, gone), ([], []))

    def test_a_key_gone_from_the_file_is_still_seen(self):
        new = frame([("2026-10-19T05:00:00Z", 30.5, "2026-10-21T08:00:00Z")])
        write, gone = load.value_diff(None, "t_table", new, "series", "public", "x", FakeConn(live(OLD)))
        self.assertEqual(write, [])
        self.assertEqual([k[3] for k in gone], ["2026-10-19T05:15:00Z"])

    def test_a_licence_change_is_still_a_write(self):
        new = frame([("2026-10-19T05:00:00Z", 30.5, "2026-10-19T06:00:00Z"), ("2026-10-19T05:15:00Z", 31.0, "2026-10-19T06:00:00Z")])
        write, _ = load.value_diff(None, "t_table", new, "series", "internal", "x", FakeConn(live(OLD)))
        self.assertEqual(len(write), 2)

    def test_sync_table_upserts_only_the_moved_rows(self):
        new = frame([("2026-10-19T05:00:00Z", 30.5, "2026-10-21T08:00:00Z"), ("2026-10-19T05:15:00Z", 31.2, "2026-10-21T08:00:00Z")])
        client = FakeClient()
        written, deleted = load.sync_table(client, "t_table", new, "series", "public", "x", None, pd.Timestamp.now(tz="UTC"),
                                           FakeConn(live(OLD)))
        self.assertEqual((written, deleted), (1, 0))
        self.assertEqual(client.log, [("upsert", 1)])

    def test_the_stamps_still_count_where_asked(self):
        r = live(OLD)[0]
        later = dict(r, retrieved_at="2026-10-21T08:00:00Z")
        self.assertNotEqual(load.canon(r, "series")[1], load.canon(later, "series")[1])
        self.assertEqual(load.canon(r, "series", stamps=False), load.canon(later, "series", stamps=False))


class VacuumConn:
    def __init__(self, reltuples):
        self.reltuples, self.sql = reltuples, []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.sql.append(sql)

        class R:
            def __init__(self, v):
                self.v = v

            def fetchone(self):
                return (self.v,)
        if "reltuples" in sql:
            return R(self.reltuples)
        return R(1048576)


class Vacuum(unittest.TestCase):
    def run_vacuum(self, changed, reltuples=3_606_639):
        conn = VacuumConn(reltuples)
        load.vacuum("url", changed=changed, connect=lambda *a, **k: conn)
        return conn.sql

    def test_a_small_load_analyses_series_and_vacuums_the_small_tables(self):
        sql = self.run_vacuum({"series": 474})
        self.assertIn("ANALYZE public.series", sql)
        self.assertNotIn("VACUUM (ANALYZE) public.series", sql)
        for t in ("headers", "catalogue", "sources"):
            self.assertIn(f"VACUUM (ANALYZE) public.{t}", sql)

    def test_a_large_load_vacuums_series(self):
        sql = self.run_vacuum({"series": 957_969})  # session 374's node_basis_daily
        self.assertIn("VACUUM (ANALYZE) public.series", sql)

    def test_without_counts_every_table_is_vacuumed_as_before(self):
        sql = self.run_vacuum(None)
        for t in ("series", "entities", "events", "headers", "catalogue", "sources"):
            self.assertIn(f"VACUUM (ANALYZE) public.{t}", sql)


if __name__ == "__main__":
    unittest.main()
