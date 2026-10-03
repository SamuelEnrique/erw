"""Session 72 tests: apply.py applies one named migration (--only), and nothing else; sync.py compares each table
with Redivis's own copy (rows and newest timestamp), not with coverage.csv.

Energy Research Warehouse (ERW). Session 71 found that a full run of warehouse/supabase/apply.py stops on
014_game_v2.sql, which re-adds the version 2 preset check that version 3 plays break. --only applies one migration.
No database is touched: the Postgres connection is replaced by a recorder.
"""

import contextlib
import io
import os
import sys
import types
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import apply  # noqa: E402

MIGRATIONS = sorted(f for f in os.listdir(os.path.join(ROOT, "warehouse", "supabase", "migrations")) if f.endswith(".sql"))


class Recorder:
    def __init__(self):
        self.sql = []

    def execute(self, sql, params=None):
        self.sql.append(sql)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def run(argv, env):
    rec = Recorder()
    fake = types.SimpleNamespace(connect=lambda url, autocommit=True: rec)
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.dict(sys.modules, {"psycopg": fake}), mock.patch.object(apply, "env", lambda n: env.get(n, "")), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = apply.main(argv)
    return code, rec.sql, out.getvalue(), err.getvalue()


class TestOnly(unittest.TestCase):
    ENV = {"SUPABASE_DB_URL": "postgresql://example.invalid/db", "EMAIL_TOKEN_SECRET": "x" * 32, "INTERNAL_COSTS_TOKEN": "y" * 32}

    def test_select_by_name_and_by_number(self):
        files = [f"/m/{f}" for f in ["013_game.sql", "014_game_v2.sql", "019_game_v4.sql"]]
        self.assertEqual(apply.select(files, "019_game_v4.sql"), ["/m/019_game_v4.sql"])
        self.assertEqual(apply.select(files, "019"), ["/m/019_game_v4.sql"])
        self.assertEqual(apply.select(files, None), files)
        with self.assertRaises(ValueError):
            apply.select(files, "020")
        with self.assertRaises(ValueError):
            apply.select(files, "01")  # a prefix that is not a whole number names nothing

    def test_only_applies_that_migration_and_nothing_else(self):
        self.assertIn("019_game_v4.sql", MIGRATIONS)
        code, sql, out, _ = run(["--only", "019"], self.ENV)
        self.assertEqual(code, 0)
        with open(os.path.join(ROOT, "warehouse", "supabase", "migrations", "019_game_v4.sql"), encoding="utf-8") as f:
            self.assertEqual(sql, [f.read()])
        self.assertIn("applied 019_game_v4.sql", out)
        self.assertNotIn("014", out)
        self.assertFalse(any(s.startswith("insert into erw_private.settings") for s in sql), "the settings belong to the full run")

    def test_unknown_name_applies_nothing(self):
        code, sql, _, err = run(["--only", "099_nothing.sql"], self.ENV)
        self.assertEqual(code, 2)
        self.assertEqual(sql, [])
        self.assertIn("nothing applied", err)

    def test_full_run_unchanged(self):
        code, sql, out, _ = run([], self.ENV)
        self.assertEqual(code, 0)
        self.assertEqual(len([s for s in sql if not s.startswith("insert into erw_private.settings")]), len(MIGRATIONS))
        self.assertTrue(any("email_token_secret" in s for s in sql))


sys.path.insert(0, os.path.join(ROOT, "scripts"))
import sync  # noqa: E402
import tempfile  # noqa: E402


class TestSync(unittest.TestCase):
    def test_classify(self):
        c = sync.classify
        self.assertEqual(c(None, (5, "2026-09-30 00:00:00")), "missing")
        self.assertEqual(c((5, "2026-09-30 00:00:00"), (5, "2026-09-30 00:00:00")), "current")
        self.assertEqual(c((5, "2026-09-28 23:00:00"), (9, "2026-10-01 23:00:00")), "behind")   # the stale laptop
        self.assertEqual(c((9, "2026-09-30 00:00:00"), (9, "2026-10-01 00:00:00")), "behind")   # same rows, older
        self.assertEqual(c((9, "2026-10-02 00:00:00"), (5, "2026-10-01 00:00:00")), "ahead")    # a run not uploaded
        self.assertEqual(c((9, "2026-10-01 00:00:00"), (5, "2026-10-01 00:00:00")), "ahead")
        self.assertEqual(c((3, "2026-10-02 00:00:00"), (9, "2026-10-01 00:00:00")), "diverged")
        self.assertEqual(c((3, None), (9, None)), "behind")  # no time column: rows alone
        self.assertEqual(c((9, "2026-10-01"), (9, "2026-10-01 00:00:00")), "current")  # a date against a timestamp
        self.assertEqual(c((9, "2026-10-01"), (9, None)), "current")  # Redivis gives no newest for a string column
        self.assertIsNone(sync.stat_newest({"max": 20, "variable": {"type": "string"}}))
        self.assertEqual(sync.stat_newest({"max": 1790722800000, "variable": {"type": "dateTime"}}), "2026-09-29 23:00:00")

    def test_norm_ts_and_local_state(self):
        self.assertEqual(sync.norm_ts("2026-09-28T23:00:00Z"), "2026-09-28 23:00:00")
        self.assertEqual(sync.norm_ts("2026-09-28 23:00:00+00:00"), "2026-09-28 23:00:00")
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write('# header\nentity,variable,ts_utc,value,note\na,x,2026-01-02T00:00:00Z,1,"two\nlines"\n'
                        'a,x,2026-03-01T00:00:00Z,2,\na,x,2026-02-01T00:00:00Z,3,\n')
            self.assertEqual(sync.local_state(p), (3, "ts_utc", "2026-03-01 00:00:00"))

    def test_behind_restored_ahead_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "output")
            os.makedirs(out)
            rows = lambda ts: "".join(f"e,v,{t},1\n" for t in ts)  # noqa: E731
            for name, ts in {"behind_t": ["2026-09-01T00:00:00Z"], "ahead_t": ["2026-09-01T00:00:00Z", "2026-10-01T00:00:00Z"],
                             "same_t": ["2026-09-01T00:00:00Z"]}.items():
                with open(os.path.join(out, name + ".csv"), "w", encoding="utf-8") as f:
                    f.write("# h\nentity,variable,ts_utc,value\n" + rows(ts))
            cov = os.path.join(d, "coverage.csv")
            with open(cov, "w", encoding="utf-8") as f:
                # coverage's own counts agree with every local file: the old check would have called them all current
                f.write("table,n_rows,license\nbehind_t,1,public\nahead_t,2,public\nsame_t,1,public\nmissing_t,4,public\n")
            cloud = {"behind_t": (2, "2026-10-01 00:00:00"), "ahead_t": (1, "2026-09-01 00:00:00"),
                     "same_t": (1, "2026-09-01 00:00:00"), "missing_t": (4, "2026-10-01 00:00:00")}
            restored = []
            def restorer(names, lic, log):
                restored.extend(names)
                return {n: (cloud[n][0], None) for n in names}
            buf = io.StringIO()
            with mock.patch.object(sync, "OUT", out), mock.patch.object(sync, "COVERAGE", cov), contextlib.redirect_stdout(buf):
                code = sync.main(["--no-git"], cloud_reader=lambda names, lic, cols, log: dict(cloud), restorer=restorer)
                self.assertEqual(code, 0)
                self.assertEqual(sorted(restored), ["behind_t", "missing_t"])
                self.assertIn("AHEAD, not overwritten: ahead_t", buf.getvalue())
                restored.clear()
                self.assertEqual(sync.main(["--no-git", "--check"], cloud_reader=lambda *a: dict(cloud), restorer=restorer), 0)
                self.assertEqual(restored, [], "--check writes nothing")
                # a table whose Redivis question goes unanswered is not read as absent, and fails the run
                part = {k: v for k, v in cloud.items() if k != "same_t"}
                self.assertEqual(sync.main(["--no-git", "--check"], cloud_reader=lambda *a: dict(part), restorer=restorer), 1)


if __name__ == "__main__":
    unittest.main()


class TestSyncTyped(unittest.TestCase):
    def test_csv_export_written_as_before(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
        import pandas as pd
        import upload as up
        df = pd.DataFrame({"ts_utc": ["2026-09-28 00:00:00", ""], "value": ["1.5", ""], "event_date": ["2026-10-01", ""],
                           "flag": ["true", "false"], "n": ["3", ""]})
        types = {"ts_utc": "dateTime", "value": "float", "event_date": "date", "flag": "boolean", "n": "integer"}
        out = up.as_erw_text(sync.typed(df, types))
        self.assertEqual(out.iloc[0].tolist(), ["2026-09-28T00:00:00Z", "1.5", "2026-10-01", "True", "3"])
        self.assertEqual(out.iloc[1].tolist(), ["", "", "", "False", ""])


class TestHeadersNeverClobbered(unittest.TestCase):
    """Session 72: upload.merge_headers took any error reading erw_headers for "none in the draft" and would have
    replaced every table's header lines with the uploaded table's alone. Only a table Redivis says is absent starts
    afresh; a read error fails the step and writes nothing."""

    def run_merge(self, meta, read):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
        import upload as up
        pushed, results = [], []
        draft = types.SimpleNamespace(table=lambda name: object())
        with mock.patch.object(up, "table_meta", lambda ds, name: meta), mock.patch.object(up, "read_frame", read), \
                mock.patch.object(up, "push", lambda *a, **k: pushed.append(a) or (1, 1)), \
                mock.patch.object(up, "split_header", lambda path: (["a header line"], "")), mock.patch.object(up, "log", lambda m: None):
            up.merge_headers(lambda target: draft, ["new_table"], {"new_table": "public"}, "now", results)
        return pushed, results

    def test_read_error_writes_nothing(self):
        def boom(table):
            raise ImportError("blocked")
        pushed, results = self.run_merge({"numRows": 1741}, boom)
        self.assertEqual(pushed, [])
        self.assertTrue(results and results[0][3].startswith("ImportError"))

    def test_absent_table_starts_afresh(self):
        pushed, results = self.run_merge(None, lambda t: self.fail("an absent table is not read"))
        self.assertEqual(len(pushed), 1)
        self.assertEqual(results[0][3], "")
