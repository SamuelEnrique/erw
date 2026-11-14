"""Session 5173: what else the database could offer the anon key (docs/reviews/security-faults-2026-11-13.md, "The
fresh pass", session 5173; warehouse/supabase/verify_rls.py, step 8).

Energy Research Warehouse (ERW). No network, no database, no model: the verifier's new step is run against stand-ins.

    the REST API serves schema public alone: a read of a table of net, cron, vault, erw_private, storage or extensions
    with the anon key is refused (the anon role holds usage on `net` by the host's default; the API's list of schemas
    keeps it out of reach)
    the anon role holds no usage on cron, vault or erw_private, and cannot execute the dispatcher
    each scheduled job is one call of the dispatcher and holds no text shaped like a key

    python -m unittest tests.test_session5173 -v
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
    spec = importlib.util.spec_from_file_location("verify_rls_5173", os.path.join(ROOT, "warehouse", "supabase", "verify_rls.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Catalog:
    def __init__(self, jobs, closed):
        self.answers, self.said = [jobs, [closed]], []

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


JOBS = [("erw-chain-watch", "select public.erw_dispatch('chain-watch.yml')"),
        ("erw-daily", "select public.erw_dispatch('daily-prices.yml', '{\"ref\":\"main\",\"inputs\":{\"queues\":\"0\",\"once\":\"1\"}}'::jsonb)"),   # as the database holds it
        ("erw-roundup", "select public.erw_dispatch('roundup.yml', '{\"ref\":\"main\",\"inputs\":{\"once\":\"1\"}}')"),
        ("erw-latest-prices", "select public.erw_dispatch('latest-prices.yml');")]
REFUSED = (406, "PGRST106")


def run(v, jobs=JOBS, closed=(False, False, False, False), answers=None):
    lines, cat, asked = [], Catalog(list(jobs), closed), []

    def reader(origin, key, schema, table):
        asked.append((schema, table))
        return (answers or {}).get(schema, REFUSED)

    with mock.patch("psycopg.connect", return_value=cat):
        bad = v.check_surface("postgresql://stand-in", "https://stand-in.example", "the-anon-key", out=lines.append, reader=reader)
    return bad, lines, cat, asked


class TheSurface(unittest.TestCase):
    def setUp(self):
        self.v = verifier()

    def test_as_it_stands_it_passes(self):
        bad, lines, cat, asked = run(self.v)
        self.assertEqual(bad, 0, lines)
        self.assertEqual(lines[0], "8. what else the database could offer the anon key")
        self.assertEqual(cat.said[0], "set transaction read only")
        self.assertEqual(cat.said[-1], "rollback")
        self.assertEqual([s for s, _ in asked], ["net", "cron", "vault", "erw_private", "storage", "extensions"])

    def test_a_schema_the_api_serves_fails(self):
        bad, lines, _, _ = run(self.v, answers={"net": (200, "")})
        self.assertEqual(bad, 1)
        self.assertTrue(any("schema net" in line and "MISMATCH: the API serves this schema to the anon key" in line for line in lines), lines)
        # any refusal passes: a wrong key, a forbidden read, an unknown schema
        for status in (401, 403, 404, 406):
            self.assertEqual(run(self.v, answers={"net": (status, "")})[0], 0, status)

    def test_a_privilege_the_anon_role_should_not_hold_fails(self):
        for i, label in enumerate(("usage on schema cron", "usage on schema vault", "usage on schema erw_private", "execute on erw_dispatch")):
            closed = [False, False, False, False]
            closed[i] = True
            bad, lines, _, _ = run(self.v, closed=tuple(closed))
            self.assertEqual(bad, 1, label)
            self.assertTrue(any(label in line and "HELD  MISMATCH" in line for line in lines), lines)

    def test_a_job_that_does_more_than_call_the_dispatcher_fails(self):
        for command in ("select public.erw_dispatch('daily-prices.yml'); delete from public.series",
                        "select net.http_post('https://example.com', '{}')",
                        "select public.erw_dispatch('daily-prices.yml' || (select value from erw_private.settings limit 1))",
                        "call something()"):
            bad, lines, _, _ = run(self.v, jobs=[("a-job", command)])
            self.assertEqual(bad, 1, command)
            self.assertTrue(any("its command is not one call of public.erw_dispatch" in line for line in lines), lines)

    def test_a_job_whose_command_holds_a_key_fails(self):
        token = "gh" + "p_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4"                     # the shape of a token, made here; not a token
        bad, lines, _, _ = run(self.v, jobs=[("a-job", "select public.erw_dispatch('daily-prices.yml', '{\"token\":\"" + token + "\"}')")])
        self.assertEqual(bad, 1)
        self.assertTrue(any("its command holds text shaped like a key" in line for line in lines), lines)
        self.assertFalse(any(token in line for line in lines), "the step printed the text it matched")

    def test_the_shapes_of_a_key(self):
        k = self.v.KEY_SHAPED
        for text in ("eyJ" + "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" + "." + "eyJyb2xlIjoic2VydmljZV9yb2xlIn0", "github_" + "pat_" + "11ABCDEFG0abcdefghijkl_mnopq",
                     "sk-" + "ant-" + "api03-abcdefghij", "Bearer " + "abcdefghijklmnopqrstuvwxyz012345", "postgresql://user:" + "s3cretpassw0rd" + "@db.example.com:5432/postgres"):
            self.assertIsNotNone(k.search(text), text[:12])
        for text in ("select public.erw_dispatch('daily-prices.yml')", '{"ref":"main","inputs":{"once":"1"}}', "https://example.com/a/b"):
            self.assertIsNone(k.search(text), text)

    def test_the_step_runs_with_the_catalog_and_only_reads(self):
        t = src("warehouse", "supabase", "verify_rls.py")
        self.assertLess(t.index('bad += check_storage(db_url, f"{u.scheme}://{u.netloc}", key)'), t.index('bad += check_surface(db_url, f"{u.scheme}://{u.netloc}", key)'))
        body = t[t.index("def schema_read("):t.index("def main(")]
        self.assertNotIn("/rpc/", body)                                           # no function is called: a read of a table by name
        self.assertNotIn('method="POST"', body)
        for word in ("insert into", "update ", "delete from", "cron.schedule", "cron.unschedule", "vault.decrypted"):
            self.assertNotIn(word, body.lower(), word)


class TheRecords(unittest.TestCase):
    def test_the_list(self):
        self.assertIn("**Session 5173 (chain 247), the scheduler and the API's reach.**", src("docs", "reviews", "security-faults-2026-11-13.md"))

    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5173.py"), ("warehouse", "supabase", "verify_rls.py")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
