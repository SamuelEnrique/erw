"""Session 5156: rows 7 and 12 of the security list (docs/reviews/security-faults-2026-11-13.md), read again.

Energy Research Warehouse (ERW). No network, no database, no model: the verifier's new step is run against a stand-in
for the catalog.

    row 7    the default privileges give every new table AND every new function of schema public to the anon key. A
             table is covered by the ensure_rls trigger and by verify_rls.py's step 5. A function was covered by
             nothing: step 6 (check_functions) now fails on a function the anon key may execute that is not listed
             with the credential it asks for.
    row 12   sign-ups in Supabase Auth: a dashboard setting, read again and still on; the ruling stands.

    python -m unittest tests.test_session5156 -v
"""

import importlib.util
import os
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def verifier():
    spec = importlib.util.spec_from_file_location("verify_rls_5156", os.path.join(ROOT, "warehouse", "supabase", "verify_rls.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Catalog:
    """A stand-in for the connection: it answers the one query with the rows it was given."""

    def __init__(self, rows):
        self.rows, self.said = rows, []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, *a):
        self.said.append(sql)
        return self

    def fetchall(self):
        return self.rows

    def rollback(self):
        self.said.append("rollback")


def run(v, rows):
    lines, cat = [], Catalog(rows)
    with mock.patch("psycopg.connect", return_value=cat):
        bad = v.check_functions("postgresql://stand-in", out=lines.append)
    return bad, lines, cat


class TheFunctionsTheAnonKeyMayExecute(unittest.TestCase):
    def setUp(self):
        self.v = verifier()
        self.listed = [(name, "p_token text, p_x text" if want == "p_token" else "p_email text, p_token text") for name, want in sorted(self.v.ANON_FUNCTIONS.items())]

    def test_the_list_as_it_stands_passes(self):
        bad, lines, cat = run(self.v, self.listed)
        self.assertEqual(bad, 0, lines)
        self.assertEqual(lines[0], "6. the catalog: every function of schema public the anon key may execute")
        # it only reads: a read-only transaction, rolled back
        self.assertEqual(cat.said[0], "set transaction read only")
        self.assertEqual(cat.said[-1], "rollback")
        self.assertIn("has_function_privilege('anon', p.oid, 'execute')", cat.said[1])

    def test_a_new_function_open_to_the_anon_key_fails(self):
        bad, lines, _ = run(self.v, self.listed + [("a_new_function", "p_anything text")])
        self.assertEqual(bad, 1)
        self.assertTrue(any("a_new_function" in line and "MISMATCH: not in ANON_FUNCTIONS" in line for line in lines), lines)

    def test_a_listed_function_that_no_longer_takes_the_token_first_fails(self):
        rows = [(n, "p_id text, p_token text") if n == "internal_costs" else (n, a) for n, a in self.listed]
        bad, lines, _ = run(self.v, rows)
        self.assertEqual(bad, 1)
        self.assertTrue(any("internal_costs" in line and "p_token is not its first argument" in line for line in lines), lines)

    def test_a_listed_function_the_anon_key_lost_is_said_and_is_no_failure(self):
        bad, lines, _ = run(self.v, [r for r in self.listed if r[0] != "thesis_get"])
        self.assertEqual(bad, 0)
        self.assertTrue(any(line.strip().startswith("thesis_get") and "the list can lose it" in line for line in lines), lines)

    def test_every_listed_function_names_a_credential(self):
        for name, want in self.v.ANON_FUNCTIONS.items():
            self.assertTrue(want == "p_token" or len(want) > 15, name)
        # the functions that must never be open are not in the list
        for name in ("site_ask_admit", "erw_lock_acquire", "erw_lock_release", "erw_dispatch", "erw_db_size", "thesis_token_ok", "eqr_summary_store"):
            self.assertNotIn(name, self.v.ANON_FUNCTIONS)

    def test_the_step_runs_with_the_catalog_and_changes_nothing_else(self):
        t = src("warehouse", "supabase", "verify_rls.py")
        self.assertLess(t.index("bad += check_catalog(db_url, args.before_028)"), t.index("bad += check_functions(db_url)"))
        self.assertIn("It only reads.", t)
        for word in ("insert into", "update public", "delete from", "grant ", "revoke execute on"):
            self.assertNotIn(word, t[t.index("def check_functions("):t.index("def main(")].lower(), word)


class TheRecords(unittest.TestCase):
    def test_the_list_and_the_state_file(self):
        rows = {line.split("|")[1].strip(): line for line in src("docs", "reviews", "security-faults-2026-11-13.md").splitlines() if line.startswith("| ") and line.split("|")[1].strip().isdigit()}
        self.assertIn("ANON_FUNCTIONS", rows["7"])
        self.assertIn("**ruling**", rows["7"])
        self.assertIn("**ruling**", rows["12"])
        self.assertIn("13 November", rows["12"])
        self.assertIn("## The guards on new tables and functions, and sign-ups, read on 13 November 2026", src("docs", "security.md"))

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5156.py"), ("warehouse", "supabase", "verify_rls.py")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
