"""Session 5151: row 6 of the security list (docs/reviews/security-faults-2026-11-13.md), the site's writes and the
service key on the host.

Energy Research Warehouse (ERW). No network, no model, no build: the source is read.

What the row's proof rests on, pinned here so the proof stays a proof:

    1. Since migration 034 the anon key cannot execute site_ask_admit, and the site calls it with the write key.
    2. The write key is the service key when the server holds it, else the anon key.
    3. The question counter fails closed: when the database refuses the call, no question is answered.

So a server without SUPABASE_SERVICE_KEY answers no question, and one answered question on production says the key is
there. The three lines above are what a later change must not undo unseen.

    python -m unittest tests.test_session5151 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheProofOfTheWriteKey(unittest.TestCase):
    def test_the_anon_key_cannot_count_a_question(self):
        m = src("warehouse", "supabase", "migrations", "034_server_writes.sql")
        self.assertRegex(m, r"revoke execute on function public\.site_ask_admit\([^)]*\) from public, anon, authenticated;")
        self.assertRegex(m, r"grant execute on function public\.site_ask_admit\([^)]*\) to service_role;")

    def test_the_site_counts_a_question_with_the_write_key(self):
        r = src("site", "app", "api", "ask", "route.ts")
        self.assertRegex(r, r'rpc\("site_ask_admit",[^\n]*\{ privileged: true \}')
        s = src("site", "lib", "supabase.ts")
        self.assertIn("const { base, key } = opts.privileged ? writeConfig() : config();", s)
        self.assertIn('return service ? { ...c, key: service, role: "service" } : { ...c, role: "anon" };', s)
        self.assertIn("const service = process.env.SUPABASE_SERVICE_KEY;", s)

    def test_the_counter_fails_closed(self):
        t = src("site", "lib", "chat", "limits.ts")
        admit = t[t.index("export async function admit("):]
        admit = admit[:admit.index("\n}\n")]
        # the call is inside a try, and its failure refuses the question
        self.assertRegex(admit, r"try \{\s*r = await call\(")
        self.assertRegex(admit, r'catch \(e\) \{\s*return refuse\("closed"')
        # nothing but the database's own yes admits a question
        self.assertEqual(len(re.findall(r"return \{ ok: true \}", admit)), 1)
        self.assertIn("if (r && r.ok === true) return { ok: true };", admit)

    def test_the_list_and_the_state_file_say_how_the_look_is_made(self):
        row = [line for line in src("docs", "reviews", "security-faults-2026-11-13.md").splitlines() if line.startswith("| 6 |")]
        self.assertEqual(len(row), 1)
        self.assertIn("one question", row[0])
        self.assertIn("tests/test_session5151.py", row[0])
        self.assertIn("one question asked on production", src("docs", "security.md"))


class NoDash(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for parts in (("tests", "test_session5151.py"), ("docs", "security.md"), ("docs", "reviews", "security-faults-2026-11-13.md")):
            t = src(*parts)
            self.assertNotIn(chr(0x2014), t, parts)
            self.assertNotIn(chr(0x2013), t, parts)


if __name__ == "__main__":
    unittest.main()
