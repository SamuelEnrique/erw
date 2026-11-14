"""Session 5172: the storage buckets are in the verifier (docs/reviews/security-faults-2026-11-13.md, "The fresh
pass", session 5172; warehouse/supabase/verify_rls.py, step 7).

Energy Research Warehouse (ERW). No network, no database, no model: the verifier's new step is run against stand-ins
for the catalog and for the storage service.

The archive of every table's rows (erw-archive, 26 GB on 13 November 2026) and the thesis tool's files are private
buckets. Until this session nothing checked that they are: verify_rls.py read the tables and, since session 5156, the
functions. Step 7 fails when a private bucket is public, when a bucket is not listed, when storage.objects has
row-level security off or a policy for the anon key, and when the anon key lists an entry of a private bucket.

    python -m unittest tests.test_session5172 -v
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
    spec = importlib.util.spec_from_file_location("verify_rls_5172", os.path.join(ROOT, "warehouse", "supabase", "verify_rls.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Catalog:
    """A stand-in for the connection: three reads, answered in order (the buckets, the policies, row-level security)."""

    def __init__(self, buckets, policies, rls):
        self.answers, self.said = [buckets, policies, [(rls,)]], []

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


GOOD = [("erw-archive", False), ("erw-public", True), ("erw-thesis", False)]


def run(v, buckets=GOOD, policies=(), rls=True, listed=None):
    lines, cat, asked = [], Catalog(list(buckets), list(policies), rls), []

    def lister(origin, key, bucket):
        asked.append((origin, bucket))
        return (listed or {}).get(bucket, (200, 0))

    with mock.patch("psycopg.connect", return_value=cat):
        bad = v.check_storage("postgresql://stand-in", "https://stand-in.example", "the-anon-key", out=lines.append, lister=lister)
    return bad, lines, cat, asked


class TheBuckets(unittest.TestCase):
    def setUp(self):
        self.v = verifier()

    def test_as_they_stand_they_pass(self):
        bad, lines, cat, asked = run(self.v)
        self.assertEqual(bad, 0, lines)
        self.assertEqual(lines[0], "7. storage: the buckets, and what the anon key lists of each")
        self.assertEqual(cat.said[0], "set transaction read only")
        self.assertEqual(cat.said[-1], "rollback")
        self.assertEqual([b for _, b in asked], ["erw-archive", "erw-public", "erw-thesis"])
        self.assertEqual(self.v.EXPECTED_BUCKETS, {"erw-archive": "private", "erw-public": "public", "erw-thesis": "private"})

    def test_the_archive_made_public_fails(self):
        bad, lines, _, _ = run(self.v, buckets=[("erw-archive", True), ("erw-public", True), ("erw-thesis", False)])
        self.assertEqual(bad, 1)
        self.assertTrue(any("erw-archive" in line and "PUBLIC in the database" in line for line in lines), lines)

    def test_a_bucket_that_is_not_listed_fails(self):
        bad, lines, _, _ = run(self.v, buckets=GOOD + [("a-new-bucket", True)])
        self.assertEqual(bad, 1)
        self.assertTrue(any("a-new-bucket" in line and "not in EXPECTED_BUCKETS" in line for line in lines), lines)

    def test_a_listed_bucket_that_is_gone_fails(self):
        bad, lines, _, _ = run(self.v, buckets=GOOD[:2])
        self.assertEqual(bad, 1)
        self.assertTrue(any("erw-thesis" in line and "absent from the database" in line for line in lines), lines)

    def test_a_policy_for_the_anon_key_fails(self):
        bad, lines, _, _ = run(self.v, policies=[("read all", "SELECT", "{anon}")])
        self.assertEqual(bad, 1)
        self.assertTrue(any("the policy read all (SELECT) names {anon}" in line for line in lines), lines)

    def test_row_level_security_off_fails(self):
        bad, lines, _, _ = run(self.v, rls=False)
        self.assertEqual(bad, 1)
        self.assertTrue(any("row-level security is OFF" in line for line in lines), lines)

    def test_the_anon_key_listing_a_private_bucket_fails_and_a_refusal_does_not(self):
        bad, lines, _, _ = run(self.v, listed={"erw-archive": (200, 1)})
        self.assertEqual(bad, 1)
        self.assertTrue(any("erw-archive" in line and "the anon key lists it" in line for line in lines), lines)
        bad, _, _, _ = run(self.v, listed={"erw-archive": (400, None), "erw-thesis": (403, None)})
        self.assertEqual(bad, 0)
        # the public bucket may list: it is public
        bad, _, _, _ = run(self.v, listed={"erw-public": (200, 3)})
        self.assertEqual(bad, 0)

    def test_the_step_runs_with_the_catalog_and_only_reads(self):
        t = src("warehouse", "supabase", "verify_rls.py")
        self.assertLess(t.index("bad += check_functions(db_url)"), t.index('bad += check_storage(db_url, f"{u.scheme}://{u.netloc}", key)'))
        body = t[t.index("def storage_list("):t.index("def main(")].lower()
        for word in ("insert into", "update ", "delete from", "/object/upload", "method=\"put\"", "method=\"delete\"", "create policy", "alter "):
            self.assertNotIn(word, body, word)
        # the one request is a list of at most one entry
        self.assertIn('json.dumps({"prefix": "", "limit": 1})', t)


class TheRecords(unittest.TestCase):
    def test_the_list_and_the_state_file(self):
        self.assertIn("**Session 5172 (chain 247), the storage buckets.**", src("docs", "reviews", "security-faults-2026-11-13.md"))
        self.assertIn("EXPECTED_BUCKETS", src("docs", "security.md"))

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5172.py"), ("warehouse", "supabase", "verify_rls.py")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
