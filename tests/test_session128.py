"""Session 128: Ask ERCOT, made safe to open.

Energy Research Warehouse (ERW). The ceilings of the question-answering tools (site/lib/chat/limits.ts, migration 023):
a daily and a monthly spending ceiling read from configuration, a number of questions per visitor per day, and each
question's cost in the ledger. These tests run the site's own guard in node with a database call that is made up for
the test (it answers what the test tells it), and read the route, the migration and the page. That the database's own
function refuses when a ceiling is crossed is proven against the database by runs/session128/prove_sql.py, and end to
end by the session's report; neither runs here, because a test never asks a model or the live database.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


PRE = "const L = await import('./lib/chat/limits.ts'); const lim = { daily_usd: 3, monthly_usd: 30, per_visitor_per_day: 15 }; const salt = 'a-secret-of-at-least-24-characters'; const now = Date.UTC(2026, 9, 6, 12);"


class TheCeilingsHold(unittest.TestCase):
    def test_each_reason_refuses_with_a_plain_message_and_no_model_is_reached(self):
        out = node(PRE + """
          const res = {};
          for (const reason of ['day', 'month', 'visitor', 'unpriced', 'busy', 'config', null]) {
            let calls = 0;
            const r = await L.admit('198.51.100.7', now, lim, salt, async () => { calls += 1; return { ok: false, reason }; });
            res[String(reason)] = { ok: r.ok, reason: r.reason, status: r.status, message: r.message, calls };
          }
          console.log(JSON.stringify(res));""")
        self.assertEqual({k: v["reason"] for k, v in out.items()}, {"day": "day", "month": "month", "visitor": "visitor", "unpriced": "closed", "busy": "closed", "config": "closed", "null": "closed"})
        for k, v in out.items():
            self.assertFalse(v["ok"], k)
            self.assertEqual(v["calls"], 1, k)                       # one question of the database, and nothing after it
            self.assertIn("Your question was not sent to the model.", v["message"], k)
        self.assertEqual((out["day"]["status"], out["month"]["status"], out["visitor"]["status"], out["unpriced"]["status"]), (503, 503, 429, 503))
        self.assertIn("until tomorrow", out["day"]["message"])
        self.assertIn("until next month", out["month"]["message"])
        self.assertIn("limit of 15 questions", out["visitor"]["message"])

    def test_only_a_plain_yes_admits(self):
        out = node(PRE + """
          const yes = await L.admit('198.51.100.7', now, lim, salt, async () => ({ ok: true, reason: null }));
          const odd = [];
          for (const a of [{}, { ok: 'true' }, { ok: 1 }, null, { ok: false }, { reason: null }]) odd.push((await L.admit('198.51.100.7', now, lim, salt, async () => a)).ok);
          console.log(JSON.stringify({ yes, odd }));""")
        self.assertEqual(out["yes"], {"ok": True})
        self.assertEqual(out["odd"], [False] * 6)

    def test_it_fails_closed_when_it_cannot_count(self):
        out = node(PRE + """
          let calls = 0;
          const call = async () => { calls += 1; return { ok: true }; };
          const thrown = await L.admit('198.51.100.7', now, lim, salt, async () => { throw new Error('HTTP 500'); });
          const r = { thrown: [thrown.ok, thrown.reason, thrown.status],
            no_limits: (await L.admit('198.51.100.7', now, null, salt, call)).reason, no_salt: (await L.admit('198.51.100.7', now, lim, null, call)).reason,
            no_address: (await L.admit('unknown', now, lim, salt, call)).reason, calls };
          console.log(JSON.stringify(r));""")
        self.assertEqual(out["thrown"], [False, "closed", 503])
        self.assertEqual((out["no_limits"], out["no_salt"], out["no_address"]), ("closed", "closed", "closed"))
        self.assertEqual(out["calls"], 0)                              # without ceilings, a secret or an address the database is not even asked

    def test_the_ceilings_are_passed_as_configured_and_the_database_gets_no_address(self):
        out = node(PRE + """
          let got = null;
          await L.admit('198.51.100.7', now, lim, salt, async (a) => { got = a; return { ok: true }; });
          console.log(JSON.stringify(got));""")
        self.assertEqual((out["p_per_visitor"], out["p_day_usd"], out["p_month_usd"]), (15, 3, 30))
        self.assertRegex(out["p_visitor"], r"^[0-9a-f]{32}$")
        self.assertNotIn("198.51.100.7", json.dumps(out))


class TheConfiguration(unittest.TestCase):
    def test_the_file_then_the_environment(self):
        out = node("""const L = await import('./lib/chat/limits.ts');
          console.log(JSON.stringify({ file: L.readLimits({}), env: L.readLimits({ ASK_DAILY_USD: '0.5', ASK_MONTHLY_USD: '4', ASK_PER_VISITOR_PER_DAY: '3' }),
            zero: L.readLimits({ ASK_DAILY_USD: '0' }), blank: L.readLimits({ ASK_DAILY_USD: '' }),
            bad: [L.readLimits({ ASK_DAILY_USD: 'lots' }), L.readLimits({ ASK_MONTHLY_USD: '-1' }), L.readLimits({ ASK_PER_VISITOR_PER_DAY: '2.5' }), L.readLimits({}, { daily_usd: 3 }), L.readLimits({}, {})] }));""")
        with open(os.path.join(ROOT, "site", "lib", "chat", "limits.json"), encoding="utf-8") as f:
            conf = json.load(f)
        self.assertEqual(out["file"], {"daily_usd": conf["daily_usd"], "monthly_usd": conf["monthly_usd"], "per_visitor_per_day": conf["per_visitor_per_day"]})
        self.assertEqual(out["env"], {"daily_usd": 0.5, "monthly_usd": 4, "per_visitor_per_day": 3})
        self.assertEqual(out["zero"]["daily_usd"], 0)                 # a ceiling of zero is a ceiling: it admits nothing
        self.assertEqual(out["blank"], out["file"])
        self.assertEqual(out["bad"], [None] * 5)                      # anything that is not a number closes the tool
        self.assertGreater(conf["monthly_usd"], conf["daily_usd"])

    def test_a_secret_must_be_long_enough(self):
        out = node("""const L = await import('./lib/chat/limits.ts');
          console.log(JSON.stringify([L.readSalt({}), L.readSalt({ ASK_VISITOR_SALT: 'short' }), L.readSalt({ ASK_VISITOR_SALT: ' ' + 'x'.repeat(24) + ' ' })]));""")
        self.assertEqual(out, [None, None, "x" * 24])


class TheVisitor(unittest.TestCase):
    def test_a_hash_that_holds_no_address_and_changes_with_the_day_and_the_secret(self):
        out = node("""const L = await import('./lib/chat/limits.ts');
          const k = (ip, day, s) => L.visitorKey(ip, day, s);
          console.log(JSON.stringify({ a: k('198.51.100.7', '2026-10-06', 's1'.repeat(12)), again: k('198.51.100.7', '2026-10-06', 's1'.repeat(12)), tomorrow: k('198.51.100.7', '2026-10-07', 's1'.repeat(12)),
            other: k('198.51.100.8', '2026-10-06', 's1'.repeat(12)), secret: k('198.51.100.7', '2026-10-06', 's2'.repeat(12)), day: L.utcDay(Date.UTC(2026, 9, 6, 23, 59, 59)), next: L.utcDay(Date.UTC(2026, 9, 7, 0, 0, 0)),
            ids: [L.questionId(), L.questionId()] }));""")
        self.assertRegex(out["a"], r"^[0-9a-f]{32}$")
        self.assertEqual(out["a"], out["again"])
        self.assertEqual(len({out["a"], out["tomorrow"], out["other"], out["secret"]}), 4)
        self.assertEqual((out["day"], out["next"]), ("2026-10-06", "2026-10-07"))
        self.assertRegex(out["ids"][0], r"^[0-9a-f]{32}$")
        self.assertNotEqual(out["ids"][0], out["ids"][1])


class TheRouteTheLedgerAndTheDatabase(unittest.TestCase):
    def test_the_route_asks_before_any_model_call_and_logs_nothing_about_the_visitor(self):
        r = src("site", "app", "api", "ask", "route.ts")
        gate, first = r.index("await admit("), r.index("await ask(")
        self.assertLess(gate, first)
        self.assertLess(r.index("if (!admitted.ok)"), first)
        refusal = r[r.index("if (!admitted.ok)"): r.index("const qid = questionId()")]
        self.assertIn("return NextResponse.json({ error: admitted.message", refusal)
        self.assertNotIn("clientIp", refusal)
        self.assertNotIn("question:", refusal)                       # a refusal's log line holds its reason, not the question
        self.assertEqual(r.count("questionId: qid"), 3)               # the stream, Ask ERCOT and the general chat
        self.assertNotIn("x-forwarded-for", src("site", "lib", "chat", "limits.ts"))

    def test_every_model_call_carries_the_questions_number_into_the_ledger(self):
        self.assertIn('recordCall(model, resp, raw.request_id, profile ? "site_ask_ercot" : "site_ask", opts.questionId)', src("site", "lib", "chat", "ask.ts"))
        self.assertIn("question_id: questionId", src("site", "lib", "chat", "ledger.ts"))

    def test_the_migration(self):
        m = src("warehouse", "supabase", "migrations", "023_ask_limits.sql")
        self.assertIn("check (step in ('site_ask', 'site_ask_ercot'))", m)      # Ask ERCOT's rows were refused until now
        counts = m[m.index("create table if not exists public.site_ask_counts"): m.index("alter table public.site_ask_counts enable")]
        self.assertEqual(re.findall(r"^\s+(\w+)\s+(?:date|text|integer)", counts, flags=re.M), ["day", "visitor", "n"])   # a day, a hash and a number: nothing else
        self.assertIn("delete from public.site_ask_counts where day < today", m)
        self.assertIn("revoke all on public.site_ask_counts from public, anon, authenticated", m)
        f = m[m.index("create or replace function public.site_ask_admit"): m.index("revoke all on function public.site_ask_admit")]
        order = [f.index("'reason', 'unpriced'"), f.index("'reason', 'month'"), f.index("'reason', 'day'"), f.index("'reason', 'visitor'"), f.index("insert into public.site_ask_counts")]
        self.assertEqual(order, sorted(order))                        # the spend is checked before the visitor is counted
        self.assertNotIn("usd", f[f.index("return jsonb_build_object('ok', true"):])   # a caller learns yes or no, never the spend
        self.assertIn("secret is null or length(secret) < 24 or p_token is null or p_token <> secret", m)

    def test_the_internal_view_is_behind_the_token_and_in_no_menu(self):
        p = src("site", "app", "internal", "ask", "page.tsx")
        # session 177: the internal view's cookie opens the page as well (so the token need not travel in an address);
        # without the token and without the cookie it is still 404, and the database is still asked with the server's token
        self.assertIn("if (want.length < 24 || (token !== want && !(await internalOk((await cookies()).get(COOKIE)?.value)))) notFound();", p)
        self.assertIn('rpc<Spend>("internal_ask_spend", { p_token: want })', p)
        self.assertIn("robots: { index: false, follow: false }", p)
        self.assertNotIn("/internal/ask", src("site", "lib", "audience.ts"))

    def test_ask_ercot_is_still_in_review(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/ask/ercot": "review"', rel)
        self.assertIn('"/ask": "review"', rel)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for p in (("site", "lib", "chat", "limits.ts"), ("site", "lib", "chat", "limits.json"), ("site", "app", "internal", "ask", "page.tsx"),
                  ("warehouse", "supabase", "migrations", "023_ask_limits.sql"), ("tests", "test_session128.py"), ("docs", "methods", "ask_limits.md")):
            if os.path.exists(os.path.join(ROOT, *p)):
                self.assertNotIn(chr(0x2014), src(*p), p)
                self.assertNotIn(chr(0x2013), src(*p), p)


if __name__ == "__main__":
    unittest.main()
