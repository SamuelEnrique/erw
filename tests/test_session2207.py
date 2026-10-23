"""Session 2207 (23 October 2026): Samuel's ruling on item 7 of docs/reviews/deals-rulings-2026-10-23.md, finished. A
stored Digest issue is a record and keeps the figure it printed; when the warehouse later holds another value, the page
says so in one line under the numbers (site/lib/digestLive.ts reads the live set, site/lib/digest.ts draws the note),
and every check treats the revision as a note: scripts/check_digest.py (session 2206's fix 5), scripts/check-values.mjs
(a figure whose page carries its revision at the live value passes as "note") and scripts/land_check.py (the step's line
counts them). No model call, no network, no warehouse write."""
import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DASH = chr(0x2014)
FILES = [("site", "lib", "digest.ts"), ("site", "lib", "digestLive.ts"), ("site", "lib", "markdown.ts"), ("site", "app", "digest", "page.tsx"),
         ("site", "app", "digest", "[date]", "page.tsx"), ("site", "scripts", "check-values.mjs"), ("scripts", "land_check.py"), ("tests", "test_session2207.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePage(unittest.TestCase):
    def test_both_digest_pages_read_the_live_values_and_pass_them_to_the_renderer(self):
        for parts in (("site", "app", "digest", "page.tsx"), ("site", "app", "digest", "[date]", "page.tsx")):
            p = src(*parts)
            self.assertIn('import { digestRevisions } from "@/lib/digestLive";', p, "/".join(parts))
            self.assertIn("await digestRevisions(DOCS.digests[", p)
            self.assertIn(", new Date(), revisions) }}", p)
        self.assertIn("export default async function DigestIndex()", src("site", "app", "digest", "page.tsx"))

    def test_the_live_reader_reads_the_fuel_closes_only_and_never_fails_the_page(self):
        s = src("site", "lib", "digestLive.ts")
        self.assertIn('.filter((f) => f.part === "fuel" && !f.held)', s)
        self.assertIn("attempt(() => rest<Row>(", s)
        self.assertIn("if (!r.ok || !r.data.length) continue;", s)
        self.assertIn('v.toFixed(2) === Number(f.raw).toFixed(2)) continue;', s)

    def test_the_renderer_draws_the_note_with_the_values_and_keeps_the_figure(self):
        d = src("site", "lib", "digest.ts")
        self.assertIn("export type Revision = { key: string; value: number; retrieved: string | null };", d)
        self.assertIn('data-revised="${esc(f.key)}" data-revised-value="${r.value}" data-revised-printed="${esc(f.raw)}"', d)
        self.assertIn("after this issue was written: ", d)
        self.assertIn("and keeps it as its record.", d)
        self.assertIn("out.splice(num.end, 0,", d)
        m = src("site", "lib", "markdown.ts")
        self.assertIn("revisions: Record<string, Revision> = {}): string {", m)
        self.assertIn("digestMarkdown(md, date, chart ? { table: chart.table, numbers: chart.numbers } : null, now, revisions);", m)


class TheChecks(unittest.TestCase):
    def test_check_values_reads_the_note_as_a_pass(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (!pass && /^digest_(dam|rt|fuel)\\|/.test(check) && t !== undefined && t !== null) {', cv)
        self.assertIn('data-revised-value="([^"]+)"', cv)
        self.assertIn('out.lines.push(`note | ${page} | ${check} | revised: page shows "${text}" as the issue printed it, its note says ${rv[1]} | page read ${raw} | Supabase ${t}`);', cv)
        body = cv[cv.index("if (!pass && /^digest_"):cv.index("pass ? out.ok++ : out.bad++;")]
        self.assertIn("out.ok++;", body)
        self.assertNotIn("out.bad++", body)

    def test_the_gate_counts_the_revised_notes_and_passes(self):
        spec = importlib.util.spec_from_file_location("land_check", os.path.join(ROOT, "scripts", "land_check.py"))
        lc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lc)
        lines = ['ok   | /digest/2026-10-21 | digest_fuel|eia_fuel_spot_prices|eia:brent|2026-10-14 | page shows "65.00" | page read 65 | Supabase 65',
                 'note | /digest/2026-10-21 | digest_fuel|eia_fuel_spot_prices|eia:wti_cushing|2026-10-14 | revised: page shows "101.91" as the issue printed it, its note says 96.34 | page read 101.91 | Supabase 96.34',
                 'note | /digest/2026-10-21 | the floor | the page carries 9 checked numbers and has no floor',
                 'FAIL | /x | the floor | the page carries 3 checked numbers; its floor is 5']
        self.assertEqual(lc.revised_notes(lines), ["/digest/2026-10-21 digest_fuel|eia_fuel_spot_prices|eia:wti_cushing|2026-10-14"])
        s = src("scripts", "land_check.py")
        self.assertIn("revised = revised_notes(self.ops.read(log)[before:])", s)
        self.assertIn("read as notes", s)
        self.assertLess(s.index("revised = revised_notes("), s.index('if code == 0:\n            return "pass", 0, note'))

    def test_check_digest_marks_a_revision_as_revised(self):
        self.assertIn('return "revised", f"{got} (row retrieved {when}, after the issue was written {written}', src("scripts", "check_digest.py"))

    def test_no_em_dash_in_the_files(self):
        for parts in FILES:
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
