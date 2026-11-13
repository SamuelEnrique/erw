"""Session 5174: a signed-in user may do no more than the anon key (docs/reviews/security-faults-2026-11-13.md, row 12
and "The fresh pass", session 5174; warehouse/supabase/verify_rls.py, step 9).

Energy Research Warehouse (ERW). No network, no database, no model: the verifier's new step is run against a stand-in
for the catalog.

Sign-ups are on in Supabase Auth (the review's L8, a dashboard setting that waits for the owner), so anyone may mint a
token of the role `authenticated`. docs/security.md has said since session 371 that such a token "reads nothing the
anon key cannot"; every check proved the anon key's reach and none the signed-in user's. Step 9 proves it from the
catalog: no privilege on a relation, no policy, no function for authenticated that anon lacks.

    python -m unittest tests.test_session5174 -v
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
    spec = importlib.util.spec_from_file_location("verify_rls_5174", os.path.join(ROOT, "warehouse", "supabase", "verify_rls.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Catalog:
    def __init__(self, relations, policies, functions):
        self.answers, self.said = [relations, policies, functions], []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, *a):
        self.said.append(sql)
        self.now = None if sql.startswith("set ") else self.answers.pop(0)
        return self

    def fetchall(self):
        return self.now

    def rollback(self):
        self.said.append("rollback")


RELATIONS = [("series", []), ("entities", []), ("subscribers", []), ("site_api_calls", []), ("game_scores_id_seq", [])]


def run(v, relations=RELATIONS, policies=(), functions=()):
    lines, cat = [], Catalog(list(relations), list(policies), list(functions))
    with mock.patch("psycopg.connect", return_value=cat):
        bad = v.check_signed_in("postgresql://stand-in", out=lines.append)
    return bad, lines, cat


class ASignedInUserHoldsNoMore(unittest.TestCase):
    def setUp(self):
        self.v = verifier()

    def test_as_it_stands_it_passes(self):
        bad, lines, cat = run(self.v)
        self.assertEqual(bad, 0, lines)
        self.assertEqual(lines[0], "9. a signed-in user (sign-ups are on) against the anon key")
        self.assertIn("5 relations of schema public: authenticated holds more than anon on 0", lines[-1])
        self.assertEqual(cat.said[0], "set transaction read only")
        self.assertEqual(cat.said[-1], "rollback")

    def test_a_privilege_only_a_signed_in_user_holds_fails(self):
        bad, lines, _ = run(self.v, relations=[("series", []), ("subscribers", ["select", "insert"])])
        self.assertEqual(bad, 1)
        self.assertTrue(any("subscribers" in line and "authenticated holds select, insert and anon does not" in line for line in lines), lines)

    def test_a_policy_for_signed_in_users_alone_fails(self):
        bad, lines, _ = run(self.v, policies=[("public.subscribers", "members read", "SELECT", "{authenticated}")])
        self.assertEqual(bad, 1)
        self.assertTrue(any("the policy members read (SELECT) names {authenticated} and not anon" in line for line in lines), lines)

    def test_a_function_for_signed_in_users_alone_fails(self):
        bad, lines, _ = run(self.v, functions=[("site_ask_admit",)])
        self.assertEqual(bad, 1)
        self.assertTrue(any("site_ask_admit" in line and "authenticated may execute it and anon may not" in line for line in lines), lines)

    def test_the_three_reads_ask_what_the_step_says(self):
        _, _, cat = run(self.v)
        reads = [s for s in cat.said if s.startswith("select")]
        self.assertEqual(len(reads), 3)
        self.assertIn("has_table_privilege('authenticated', c.oid, p) and not has_table_privilege('anon', c.oid, p)", reads[0])
        self.assertIn("has_sequence_privilege('authenticated', c.oid, p) and not has_sequence_privilege('anon', c.oid, p)", reads[0])
        self.assertIn("(roles && array['authenticated', 'public']::name[]) and not (roles && array['anon']::name[])", reads[1])
        self.assertIn("has_function_privilege('authenticated', p.oid, 'execute') and not has_function_privilege('anon', p.oid, 'execute')", reads[2])
        for r in reads:
            for word in ("insert into", "update public", "delete from", "grant ", "revoke "):
                self.assertNotIn(word, r.lower())

    def test_the_step_runs_with_the_catalog(self):
        t = src("warehouse", "supabase", "verify_rls.py")
        self.assertLess(t.index('bad += check_surface(db_url, f"{u.scheme}://{u.netloc}", key)'), t.index("bad += check_signed_in(db_url)"))


class TheRecords(unittest.TestCase):
    def test_the_list_and_the_row(self):
        t = src("docs", "reviews", "security-faults-2026-11-13.md")
        self.assertIn("**Session 5174 (chain 247), a signed-in user.**", t)
        row = [line for line in t.splitlines() if line.startswith("| 12 |")]
        self.assertIn("step 9", row[0])

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5174.py"), ("warehouse", "supabase", "verify_rls.py")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
