"""Session 1174 (chain 078): ERCOT's notices, tied into the Grid tool as CAISO's alerts are (session 1155).

  TheStateLine      the panel grid_ercotnotice_ercot opens the ERCOT Mix tab, after CAISO's line and before the Now
                    blocks, its figures keyed through its one F, the newest notice and the read day said, the notices
                    that are not calls named apart, the method linked
  TheStrip          ERCOT's scarcity strip marks its call days through HeatChart's colMarks and keys the counts through
                    the panel's one F; CAISO's line is as it was
  TheMonthlyMix     ERCOT's monthly view marks the months with a call day and keys their count; CAISO's marks stand
  TheRead           the rows are read once per render, with three fields of extra, from a file apart from lib/reliability.ts
  TheKeys           check-values recomputes ercotn| with lib/ercotNotices.ts (no import); the node test passes; the note names them
  NoDash            no em dash in anything the session wrote or changed
"""
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DASH = chr(0x2014)
WROTE = ["site/lib/ercotNotices.ts", "site/lib/gridErcotNotices.ts", "site/components/grid/ErcotNoticeState.tsx",
         "site/scripts/test-ercot-notices.mjs", "site/scripts/fixtures/ercot_notices.json", "tests/test_session1174.py"]
CHANGED = ["site/app/grid/page.tsx", "site/components/grid/ScarcityPanel.tsx", "site/components/grid/MixView.tsx",
           "site/components/grid/MixFigures.tsx", "site/scripts/check-values.mjs", "site/lib/gridtables.ts",
           "docs/methods/ercot_grid_notices.md", "docs/methods/scarcity_hours_by_grid.md", "tests/test_session473.py"]


def src(*parts):
    with open(os.path.join(SITE, *parts), encoding="utf-8") as f:
        return f.read()


class TheStateLine(unittest.TestCase):
    def test_the_panel_is_first_on_the_ercot_mix_tab(self):
        page = src("app", "grid", "page.tsx")
        self.assertIn('import { ErcotNoticeState } from "@/components/grid/ErcotNoticeState";', page)
        mix = page[page.index('<div data-grid-view="mix">'):]
        self.assertLess(mix.index('{grid.slug === "caiso" ? <CaisoAlertState /> : null}'), mix.index('{grid.slug === "ercot" ? <ErcotNoticeState /> : null}'))
        self.assertLess(mix.index('{grid.slug === "ercot" ? <ErcotNoticeState /> : null}'), mix.index("<NowView"))

    def test_the_panel_names_itself_and_keys_through_one_f(self):
        c = src("components", "grid", "ErcotNoticeState.tsx")
        self.assertIn('data-grid-panel="grid_ercotnotice_ercot"', c)
        self.assertIn('id="ercot-notices"', c)
        self.assertEqual(c.count("check="), 1)
        self.assertIn('<span title={f.tip} className="cursor-help border-b border-dotted border-muted">', c)
        self.assertIn("noticeState(read.data, renderTime())", c)
        self.assertIn("ercotNotices()", c)

    def test_it_never_says_none_past_the_table(self):
        c = src("components", "grid", "ErcotNoticeState.tsx")
        self.assertIn("is not held yet:</strong> the table holds ERCOT&apos;s notices to <F f={s.newest} />", c)
        self.assertIn("read from ERCOT&apos;s pages on <F f={s.read} /> (UTC)", c)
        self.assertIn('data-ercotnotice-state={s.covered ? (s.todayCalls.length ? "in-force" : "none") : "not-held"}', c)

    def test_the_kinds_the_others_and_the_links(self):
        c = src("components", "grid", "ErcotNoticeState.tsx")
        self.assertIn("The last day with {k.name}:", c)
        self.assertIn("Not calls, named apart:", c)
        self.assertIn("#scarcity`}>the scarcity strip</Link>", c)
        self.assertIn("#hourly`}>the monthly mix</Link>", c)
        self.assertIn('const MONTH = gridHref("ercot", "mix", { mixp: "month" });', c)
        self.assertIn('<Link href="/data/methods/ercot_grid_notices">Method: ERCOT&apos;s grid notices</Link>', c)
        self.assertIn("Electric Reliability Council of Texas, ERCOT", c)

    def test_a_call_is_the_methods_own_count(self):
        e = src("lib", "ercotNotices.ts")
        self.assertIn('const counted = (r: NoticeLike) => r.extra?.x_counts === "yes";', e)
        self.assertIn('eea: ["eea3", "rotating_outages", "eea2", "eea1"],', e)
        self.assertIn('export const GROUPS = ["any", "call", ...Object.keys(KINDS), "other"];', e)
        self.assertIn('export const NOTICE_TZ = "America/Chicago";', e)
        self.assertFalse(any(line.startswith("import ") for line in e.splitlines()))   # node runs it with its types stripped


class TheStrip(unittest.TestCase):
    def test_the_ercot_strip_marks_call_days(self):
        p = src("components", "grid", "ScarcityPanel.tsx")
        self.assertIn('g.slug === "ercot" ? attempt(() => ercotNotices()) : Promise.resolve(null),', p)
        self.assertIn("const calls = ercot && ercot.ok ? callDays(ercot.data, w.days) : null;", p)
        self.assertIn("const alerts = caiso ?? calls;", p)
        self.assertIn("colMarks={alerts?.cols}", p)
        self.assertIn("data-scarcity-notice-days=", p)
        self.assertIn("<F f={days(calls.call)} />", p)
        self.assertIn("<F f={days(calls.otherFig)} />", p)
        self.assertIn("#ercot-notices`}>ERCOT&apos;s notices today</SiteLink>", p)
        self.assertEqual(p.count("check="), 1)

    def test_caisos_line_reads_as_before(self):
        p = src("components", "grid", "ScarcityPanel.tsx")
        self.assertIn('g.slug === "caiso" ? attempt(() => gridNotices()) : Promise.resolve(null)', p)
        self.assertIn("alertDays(notices.data, w.days)", p)
        self.assertIn('data-scarcity-alert-days={caiso ? caiso.cols.length : "unread"}', p)
        self.assertIn("Restricted maintenance, not an alert and not marked: <F f={days(caiso.rmoFig)} /> days", p)


class TheMonthlyMix(unittest.TestCase):
    def test_ercot_months_with_a_call_are_marked_and_counted(self):
        f = src("components", "grid", "MixFigures.tsx")
        self.assertIn("const en = ercot && ercot.ok ? callMonths(ercot.data, m.months) : null;", f)
        self.assertIn(": en?.months.length ? en.months.map(", f)
        self.assertIn("data-mix-notice-months=", f)
        self.assertIn("marks={al?.months.length ?", f)   # CAISO's marks stand first
        self.assertEqual(f.count("check="), 1)
        v = src("components", "grid", "MixView.tsx")
        self.assertIn('month && bas.some((b) => b.code === "erco") ? attempt(() => ercotNotices()) : Promise.resolve(null),', v)
        self.assertIn('ercot={b.code === "erco" ? ercotN : undefined}', v)
        self.assertIn("notices={withheld ? notices : undefined}", v)


class TheRead(unittest.TestCase):
    def test_once_per_render_three_fields_apart_from_reliability(self):
        r = src("lib", "gridErcotNotices.ts")
        self.assertIn('import { cache } from "react";', r)
        self.assertIn("export const ercotNotices = cache(async (): Promise<ErcotNotice[]> => {", r)
        self.assertIn("x_counts:extra->>x_counts,x_region:extra->>x_region,retrieved_at:extra->>retrieved_at", r)
        self.assertNotIn("x_text", r.split("import { cache }")[1].split("export const ercotNotices")[1])
        for word in ("gridErcotNotices", "ercotNotices", "ercot_grid_notices"):
            self.assertNotIn(word, src("lib", "reliability.ts"))   # the Clean tab draws lib/reliability.ts

    def test_the_tabs_lines_name_the_table(self):
        t = src("lib", "gridtables.ts")
        self.assertEqual(t.count('"ercot_grid_notices"'), 2)   # the Mix tab and the Clean tab (MixView.tsx's imports)


class TheKeys(unittest.TestCase):
    def test_check_values_recomputes_them_with_the_page_rule(self):
        cv = src("scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "ercotn") {', cv)
        self.assertIn('const E = await import("../lib/ercotNotices.ts");', cv)
        self.assertIn("E.ercotnValue(", cv)
        self.assertIn("throw new Error(`unknown ercotn key ${check}`);", cv)
        self.assertLess(cv.index('if (p[0] === "ercotn") {'), cv.index('if (p[0] === "awe") {'))

    def test_the_method_note_names_them(self):
        with open(os.path.join(ROOT, "docs", "methods", "ercot_grid_notices.md"), encoding="utf-8") as f:
            note = f.read()
        for k in ("`ercotn|last|<group>|<day>`", "`ercotn|ndays|<group>|<from>|<to>`", "`ercotn|read`", "`call`", "`other`", "`any`",
                  "## 6. On the Grid tool: the notice state (session 1174, 24 October 2026)", "### Decisions (session 1174, chain 078)"):
            self.assertIn(k, note)
        with open(os.path.join(ROOT, "docs", "methods", "scarcity_hours_by_grid.md"), encoding="utf-8") as f:
            self.assertIn("**ERCOT's notice days** (session 1174)", f.read())

    def test_the_node_test_passes(self):
        r = subprocess.run(["node", "scripts/test-ercot-notices.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("14 of 14 passed", r.stdout)


class NoDash(unittest.TestCase):
    def test_no_em_dash(self):
        for rel in WROTE + CHANGED:
            with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                self.assertNotIn(DASH, f.read(), rel)


if __name__ == "__main__":
    unittest.main()
