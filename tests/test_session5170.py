"""Session 5170: each database function the anon key may execute checks its credential before anything else
(docs/reviews/security-faults-2026-11-13.md, row 7; warehouse/supabase/verify_rls.py, ANON_FUNCTIONS).

Energy Research Warehouse (ERW). No network, no database, no model: the migrations are read.

Session 5156 listed the 23 functions the anon key may execute and said each asks for a credential; it did not prove
that each CHECKS it first. This reads the newest definition of each in warehouse/supabase/migrations/ (the last file,
in order, that creates it) and holds its opening:

    a function listed as "p_token": the token is checked, and "not authorized" raised, before any other statement
    the two subscription functions: the address's signed token is compared first, and a wrong one changes nothing
    the one-time key of a thesis run: its form is checked first, then the run is read and the key compared

A migration that redefines one of them without its check, or with a statement before it, fails here.

    python -m unittest tests.test_session5170 -v
"""

import importlib.util
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MIG = os.path.join(ROOT, "warehouse", "supabase", "migrations")


def anon_functions():
    spec = importlib.util.spec_from_file_location("verify_rls_5170", os.path.join(ROOT, "warehouse", "supabase", "verify_rls.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v.ANON_FUNCTIONS


def newest_definitions():
    """{function: (migration file, the text of its newest definition)} for the functions of schema public."""
    out = {}
    for name in sorted(os.listdir(MIG)):
        if not name.endswith(".sql"):
            continue
        t = open(os.path.join(MIG, name), encoding="utf-8").read()
        for m in re.finditer(r"create (?:or replace )?function public\.(\w+)\s*\(", t, flags=re.I):
            end = t.find("$$;", m.end())
            out[m.group(1)] = (name, t[m.start():end if end > 0 else len(t)])
    return out


def statements(text):
    """The statements of a function's body, in order, comments and the declarations before `begin` left out."""
    body = text[text.find("$$") + 2:]
    parts = re.split(r"(?im)^\s*begin\b", body, maxsplit=1)
    body = parts[1] if len(parts) == 2 else body
    return [re.sub(r"\s+", " ", s.strip()) for s in re.sub(r"--[^\n]*", "", body).split(";") if s.strip()]


# The two ways the token is checked first. A: the shared check. B: the secret read, then compared (migrations 010 to 027).
SHARED = re.compile(r"^if not (?:erw_private\.site_token_ok|public\.thesis_token_ok)\(p_token\) then raise exception 'not authorized' using errcode = '42501'$")
READ_SECRET = "select value into secret from erw_private.settings where key = 'internal_costs_token'"
COMPARE = "if secret is null or length(secret) < 24 or p_token is null or p_token <> secret then raise exception 'not authorized' using errcode = '42501'"


class TheTokenIsCheckedFirst(unittest.TestCase):
    def setUp(self):
        self.listed = anon_functions()
        self.defs = newest_definitions()

    def test_every_listed_function_is_defined_by_a_migration_or_is_the_hosts_own(self):
        for fn in self.listed:
            if fn == "rls_auto_enable":          # Supabase's own event trigger function: no migration of the ERW creates it
                self.assertNotIn(fn, self.defs)
                continue
            self.assertIn(fn, self.defs, f"{fn} is listed as open to the anon key and no migration defines it")

    def test_a_p_token_function_checks_the_token_before_anything_else(self):
        tokens = [fn for fn, want in self.listed.items() if want == "p_token"]
        self.assertEqual(len(tokens), 19)
        for fn in tokens:
            name, text = self.defs[fn]
            self.assertRegex(text, r"(?i)language plpgsql", fn)
            self.assertRegex(text, r"(?i)security definer", fn)
            self.assertRegex(text, r"(?i)set search_path\s*(?:=|to)\s*''", f"{fn} ({name}): a definer's function with a search path a caller could lean on")
            st = statements(text)
            if SHARED.match(st[0]):
                self.assertEqual(st[1], "end if", f"{fn} ({name})")
            else:
                self.assertEqual(st[0], READ_SECRET, f"{fn} ({name}): the first statement is neither the shared check nor the read of the secret")
                self.assertEqual(st[1], COMPARE, f"{fn} ({name})")
                self.assertEqual(st[2], "end if", f"{fn} ({name})")

    def test_the_shared_checks_themselves(self):
        t = open(os.path.join(MIG, "028_security_usage.sql"), encoding="utf-8").read()
        body = re.sub(r"\s+", " ", t[t.index("function erw_private.site_token_ok"):][:700])
        self.assertIn("return secret is not null and length(secret) >= 24 and p_token is not null and p_token = secret;", body)
        self.assertIn("revoke all on function erw_private.site_token_ok(text) from public, anon, authenticated;", body)
        # the thesis tool's check is not itself open to the anon key (the verifier's catalog read says so of the database)
        self.assertNotIn("thesis_token_ok", self.listed)

    def test_the_subscription_functions_compare_the_signed_token_first(self):
        for fn, purpose in (("subscribe_confirm", "confirm"), ("subscribe_unsubscribe", "unsubscribe")):
            name, text = self.defs[fn]
            st = statements(text)
            self.assertEqual(st[0], f"if p_token is null or p_token <> erw_private.email_token(p_email, '{purpose}') then return false", f"{fn} ({name})")
            self.assertEqual(st[1], "end if", fn)
            self.assertRegex(text, r"(?i)set search_path\s*(?:=|to)\s*''", fn)

    def test_the_one_time_key_is_checked_before_a_run_is_changed(self):
        name, text = self.defs["thesis_pitchbook_accept"]
        st = statements(text)
        self.assertEqual(st[0], "if p_key is null or length(p_key) < 32 or p_run_id is null then return jsonb_build_object('ok', false, 'reason', 'key')", name)
        # the run is read under a lock, the key compared, and only then is anything written
        self.assertEqual(st[2], "select * into r from public.thesis_runs where run_id = p_run_id for update", name)
        self.assertEqual(st[3], "if not found or r.pitchbook_key is null or r.pitchbook_key <> p_key then return jsonb_build_object('ok', false, 'reason', 'key')", name)
        writes = [i for i, s in enumerate(st) if re.match(r"(?i)^(update|insert|delete)\b", s)]
        self.assertTrue(writes and min(writes) > 3, f"{name}: something is written before the key is compared")
        # the key opens the run once: accepting it clears it
        self.assertIn("pitchbook_key = null", st[min(writes)])


class TheRecords(unittest.TestCase):
    def test_the_list_says_it(self):
        t = open(os.path.join(ROOT, "docs", "reviews", "security-faults-2026-11-13.md"), encoding="utf-8").read()
        self.assertIn("**Session 5170 (chain 247), the functions open to the anon key.**", t)

    def test_no_em_or_en_dash(self):
        t = open(os.path.join(ROOT, "tests", "test_session5170.py"), encoding="utf-8").read()
        self.assertNotIn(chr(0x2014), t)
        self.assertNotIn(chr(0x2013), t)


if __name__ == "__main__":
    unittest.main()
