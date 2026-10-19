"""Session 301: the security review's build items (docs/reviews/2026-10-10-security.md; the chain prompt of 19 October
2026). What is held to:

  H1: no check script writes the internal token into an address: every one opens the internal view by the form's door
    (scripts/browser.mjs: unlockPost for a script that fetches, unlockForm for one that drives a browser), and only
    check-security.mjs still names the old link, to prove it answers as it did until it is retired;
  H3 and M1: the site's writes go with the service key when the server holds it and with the anon key otherwise
    (lib/supabase.ts writeConfig: insertRow, and rpc with `privileged`, which the question counter uses); the service
    key is read by that helper alone; migration 034 and its rollback drop and restore the four insert policies, the
    sequences' use and the execute right, and the migration is not applied by the session;
  M4: the full content security policy is enforced, the report-only header beside it with the same value, and the
    CSP check expects its probe to be blocked;
  the review marks the four items with their session 301 lines; no em dash in any file the session wrote."""
import glob
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
FILES = ["site/scripts/browser.mjs", "site/scripts/check-csp.mjs", "site/lib/supabase.ts", "site/app/api/ask/route.ts", "site/next.config.ts", "site/README.md",
         "warehouse/supabase/migrations/034_server_writes.sql", "warehouse/supabase/rollbacks/034_server_writes.sql",
         "docs/reviews/2026-10-10-security.md", "tests/test_session301.py"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class H1(unittest.TestCase):
    def test_no_script_puts_the_token_in_an_address(self):
        names = sorted(os.path.basename(f) for f in glob.glob(os.path.join(SITE, "scripts", "*.mjs")) if "internal/unlock?token" in src("site", "scripts", os.path.basename(f)))
        self.assertEqual(names, ["check-security.mjs"])       # the three requests that prove the old link still answers
        sec = src("site", "scripts", "check-security.mjs")
        self.assertIn("the old link", sec)
        wf = src(".github", "workflows", "code-branch.yml")
        self.assertNotIn("internal/unlock?token", wf)

    def test_the_two_doors_in_the_browser_helper(self):
        b = src("site", "scripts", "browser.mjs")
        self.assertIn("export async function unlockPost(base, token) {", b)
        self.assertIn('if (!token) return new Response("Not found", { status: 404 });', b)   # no request, no wrong try counted
        self.assertIn("return fetch(`${origin}/internal/unlock`, {", b)
        self.assertIn('method: "POST", redirect: "manual",', b)
        self.assertIn('headers: { "Content-Type": "application/x-www-form-urlencoded", Origin: origin,', b)
        self.assertIn("body: new URLSearchParams({ token }).toString(),", b)
        self.assertIn("export async function unlockForm(h, base, token) {", b)
        self.assertIn("await h.go(`${base}/internal/open`);", b)
        self.assertIn("""document.querySelector('form[action="/internal/unlock"] input[name="token"]')""", b)
        self.assertIn("await unlockForm({ go, evaluate, sleep }, base, token);", b)      # withBrowser's own unlock
        self.assertNotIn("/internal/unlock?token", b)

    def test_every_moved_script_names_a_door(self):
        for f in sorted(glob.glob(os.path.join(SITE, "scripts", "*.mjs"))):
            name = os.path.basename(f)
            text = src("site", "scripts", name)
            if "unlockPost(" in text and name != "browser.mjs":
                self.assertRegex(text, r'import \{[^}]*\bunlockPost\b[^}]*\} from "\./browser\.mjs"', name)
            if "unlockForm(" in text and name != "browser.mjs":
                self.assertRegex(text, r'import \{[^}]*\bunlockForm\b[^}]*\} from "\./browser\.mjs"', name)
        for name in ("check-routes.mjs", "check-values.mjs", "check-no-request.mjs", "check-battery-face.mjs", "frametime-resources.mjs"):
            text = src("site", "scripts", name)
            self.assertTrue("unlockPost(" in text or "unlockForm(" in text or "/internal/open" in text, name)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_unlock_post_sends_the_token_in_the_body_and_nothing_without_one(self):
        code = ("import { unlockPost } from './scripts/browser.mjs'; const calls = []; globalThis.fetch = async (u, o) => { calls.push({ u, o }); return new Response('', { status: 303 }); }; "
                "const none = await unlockPost('http://localhost:3000', ''); const r = await unlockPost('http://localhost:3000/', 'abc def'); "
                "console.log(JSON.stringify({ none: none.status, status: r.status, calls }));")
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(d["none"], 404)
        self.assertEqual(len(d["calls"]), 1)                                     # no request without a token
        self.assertEqual(d["calls"][0]["u"], "http://localhost:3000/internal/unlock")
        self.assertEqual(d["calls"][0]["o"]["body"], "token=abc+def")
        self.assertEqual(d["calls"][0]["o"]["headers"]["Origin"], "http://localhost:3000")
        self.assertEqual(d["calls"][0]["o"]["redirect"], "manual")


class H3AndM1(unittest.TestCase):
    def test_the_writes_go_with_the_service_key_when_held(self):
        s = src("site", "lib", "supabase.ts")
        self.assertIn('import "server-only";', s)
        self.assertIn("function writeConfig(): { base: string; key: string; role: \"service\" | \"anon\" } {", s)
        self.assertIn("const service = process.env.SUPABASE_SERVICE_KEY;", s)
        self.assertIn('return service ? { ...c, key: service, role: "service" } : { ...c, role: "anon" };', s)
        self.assertIn("const { base, key } = writeConfig();   // session 301", s)                 # insertRow
        self.assertIn("const { base, key } = opts.privileged ? writeConfig() : config();", s)    # rpc
        self.assertEqual(s.count("SUPABASE_SERVICE_KEY"), s.count("process.env.SUPABASE_SERVICE_KEY") + s.count("SUPABASE_SERVICE_KEY when") + s.count("SUPABASE_SERVICE_KEY,") , "the key is named in the helper and its comments only")
        self.assertNotIn("NEXT_PUBLIC_SUPABASE_SERVICE_KEY", s)
        ask = src("site", "app", "api", "ask", "route.ts")
        self.assertIn('rpc("site_ask_admit", a as unknown as Record<string, string>, { privileged: true })', ask)
        for f in ("site/app/api/subscribe/route.ts", "site/app/api/play/score/route.ts", "site/lib/chat/ledger.ts"):
            self.assertIn("insertRow(", src(*f.split("/")), f)
        readme = src("site", "README.md")
        self.assertIn("`SUPABASE_SERVICE_KEY`, when set, is read by its write helper alone", readme)

    def test_the_migration_and_its_rollback(self):
        m = src("warehouse", "supabase", "migrations", "034_server_writes.sql")
        for t in ("site_api_calls", "game_scores", "game_plays", "subscribers"):
            self.assertIn(f"drop policy if exists anon_insert on public.{t};", m)
            self.assertIn(f"revoke insert on public.{t} from anon, authenticated;", m)
        self.assertIn("revoke execute on function public.site_ask_admit(text, integer, numeric, numeric) from public, anon, authenticated;", m)
        self.assertIn("grant execute on function public.site_ask_admit(text, integer, numeric, numeric) to service_role;", m)
        self.assertIn("NOT applied by it", m)
        self.assertNotIn("drop table", m.lower())
        self.assertNotIn("delete from", m.lower())
        r = src("warehouse", "supabase", "rollbacks", "034_server_writes.sql")
        for t in ("site_api_calls", "game_scores", "game_plays", "subscribers"):
            self.assertIn(f"create policy anon_insert on public.{t} for insert to anon with check", r)
        self.assertIn("grant execute on function public.site_ask_admit(text, integer, numeric, numeric) to anon, authenticated;", r)
        # the rollback's grants are the ones the earlier migrations made
        self.assertIn('grant insert (level_date, nickname, score, optimal_score, "check", preset, difficulty) on public.game_scores to anon;', r)
        self.assertIn("grant insert (email, source, daily, weekly, topics) on public.subscribers to anon;", r)
        self.assertIn("grant insert (step, model, input_tokens, cached_input_tokens, cache_write_tokens, output_tokens, usd, request_id, question_id) on public.site_api_calls to anon;", r)


class M4(unittest.TestCase):
    def test_the_full_policy_is_enforced_with_the_report_only_header_beside_it(self):
        c = src("site", "next.config.ts")
        self.assertIn("const CSP_ENFORCED = CSP_FULL;", c)
        self.assertIn("const CSP_REPORT_ONLY = CSP_FULL;", c)
        self.assertIn('const CSP_MINIMAL = "base-uri \'self\'; object-src \'none\'; frame-ancestors \'none\'; form-action \'self\'";', c)
        self.assertIn('{ key: "Content-Security-Policy", value: CSP_ENFORCED },', c)
        self.assertIn('{ key: "Content-Security-Policy-Report-Only", value: CSP_REPORT_ONLY },', c)
        full = c[c.index("const CSP_FULL = ["):c.index("].join(\"; \");")]
        for d in ("default-src 'self'", "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com", "connect-src 'self' https://*.supabase.co", "worker-src 'self' blob:", "frame-ancestors 'none'"):
            self.assertIn(d, full)
        csp = src("site", "scripts", "check-csp.mjs")
        self.assertIn('const blocked = probe.seen.some((v) => v.disposition === "enforce" && /script-src/.test(v.directive));', csp)
        self.assertIn("const caught = blocked ? !probe.ran : reportedOnly && probe.ran;", csp)
        self.assertIn("if (!caught) failed += 1;", csp)


class TheReview(unittest.TestCase):
    def test_the_four_items_carry_their_session_301_lines(self):
        doc = src("docs", "reviews", "2026-10-10-security.md")
        self.assertIn("### H1. The internal token travels in addresses. `FIXED` (session 301: every check script on the form; the old link kept), rotation `FOR SAMUEL`", doc)
        self.assertIn("### H3. The anon key can write the cost ledger directly. `FIXED IN THE SITE` (session 301), migration 034 `FOR SAMUEL`", doc)
        self.assertIn("### M1. The same class, three more places: the game's tables, the subscribers and the ask counter. `FIXED IN THE SITE` (session 301), migration 034 `FOR SAMUEL`", doc)
        self.assertIn("### M4. No security headers beyond the host's. `FIXED` (session 301: the full policy enforced)", doc)
        self.assertEqual(doc.count("**Session 301 (19 October 2026).**"), 4)

    def test_no_em_dash_in_any_file_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
