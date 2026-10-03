"""Session 72 tests: apply.py applies one named migration (--only), and nothing else.

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


if __name__ == "__main__":
    unittest.main()
