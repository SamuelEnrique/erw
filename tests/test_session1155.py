"""Session 1155 (chain 077): CAISO's alerts, tied into the Grid tool.

  TheStateLine      the panel grid_caisoalert_caiso opens the CAISO Mix tab, its figures keyed through its one F, the
                    newest notice said, rmo and transmission emergencies named apart, the scorecard linked
  TheStrip          the scarcity strip marks CAISO's alert days on its day axis (HeatChart's optional colMarks, off by
                    default) and keys the counts through its one F
  TheMonthlyMix     CAISO's monthly view marks the months with an alert day and keys their count; the hourly mix stays withheld
  TheAlertsPage     /grid/caiso/alerts links back to the state line and the strip, and nothing else on it moved
  TheKeys           check-values recomputes awe|last and awe|ndays with lib/caisoAlerts.ts; the node test passes
  NoDash            no em dash in anything the session wrote
"""
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DASH = chr(0x2014)
WROTE = ["site/lib/caisoAlerts.ts", "site/components/grid/CaisoAlertState.tsx", "site/scripts/test-caiso-alerts.mjs",
         "site/scripts/fixtures/caiso_alerts.json", "tests/test_session1155.py"]


def src(*parts):
    with open(os.path.join(SITE, *parts), encoding="utf-8") as f:
        return f.read()


class TheStateLine(unittest.TestCase):
    def test_the_panel_is_first_on_the_caiso_mix_tab(self):
        page = src("app", "grid", "page.tsx")
        self.assertIn('import { CaisoAlertState } from "@/components/grid/CaisoAlertState";', page)
        mix = page[page.index('<div data-grid-view="mix">'):]
        self.assertLess(mix.index('{grid.slug === "caiso" ? <CaisoAlertState /> : null}'), mix.index("<NowView"))

    def test_the_panel_names_itself_and_keys_through_one_f(self):
        c = src("components", "grid", "CaisoAlertState.tsx")
        # also covered by site/scripts/test-grid-render.mjs: grid_caisoalert_caiso on /grid?grid=caiso&view=mix
        self.assertIn('data-grid-panel="grid_caisoalert_caiso"', c)
        self.assertIn('id="caiso-alerts"', c)
        self.assertEqual(c.count("check="), 1)
        self.assertIn("alertState(read.data, renderTime())", c)
        self.assertIn("gridNotices()", c)   # the Reliability section's own read

    def test_it_never_says_no_alert_past_the_table(self):
        c = src("components", "grid", "CaisoAlertState.tsx")
        # also covered by site/scripts/test-grid-render.mjs: grid_caisoalert_caiso on /grid?grid=caiso&view=mix
        self.assertIn("is not held yet:</strong> the table holds CAISO&apos;s notices to <F f={s.newest} />", c)
        self.assertIn('data-caisoalert-state={s.covered ? (s.todayAlerts.length ? "in-force" : "none") : "not-held"}', c)

    def test_rmo_and_transmission_are_named_apart_and_the_scorecard_linked(self):
        c = src("components", "grid", "CaisoAlertState.tsx")
        # also covered by site/scripts/test-grid-render.mjs: grid_caisoalert_caiso on /grid?grid=caiso&view=mix
        self.assertIn("Not alerts, named apart:", c)
        # also covered by site/scripts/test-grid-render.mjs: grid_caisoalert_caiso on /grid?grid=caiso&view=mix
        self.assertIn("restricted maintenance operations", c)
        # also covered by site/scripts/test-grid-render.mjs: grid_caisoalert_caiso on /grid?grid=caiso&view=mix
        self.assertIn("a transmission emergency (local)", c)
        # also covered by site/scripts/test-grid-render.mjs: grid_caisoalert_caiso on /grid?grid=caiso&view=mix
        self.assertIn('<Link href="/grid/caiso/alerts">The Flex Alert scorecard</Link>', c)
        self.assertIn("#scarcity`}>the scarcity strip</Link>", c)

    def test_the_alert_set_is_the_own_signal(self):
        a = src("lib", "caisoAlerts.ts")
        self.assertIn('export const EEA_TYPES = ["eea_watch", "eea1", "eea2", "eea3"];', a)
        self.assertIn('export const OLD_ALERT_TYPES = ["alert", "warning", "stage1", "stage2", "stage3"];', a)
        self.assertNotIn('"rmo", "eea', a)
        self.assertFalse(any(line.startswith("import ") for line in a.splitlines()))   # node runs it with its types stripped


class TheStrip(unittest.TestCase):
    def test_heatchart_takes_column_marks_off_by_default(self):
        s = src("components", "svgchart.tsx")
        self.assertIn("export function HeatChart({ id, rows, cols, cells, unit, label, tips, marks, colMarks, lo: loGiven, hi: hiGiven, legend, table: tableFirst = false }: {", s)
        self.assertIn("colMarks?: number[];", s)
        self.assertIn("{colMarks?.map((c) =>", s)
        self.assertEqual(s.count("colMarks={"), 0)   # no chart of the shared file sets it

    def test_the_caiso_strip_marks_alert_days(self):
        p = src("components", "grid", "ScarcityPanel.tsx")
        self.assertIn("colMarks={alerts?.cols}", p)
        self.assertIn('g.slug === "caiso" ? attempt(() => gridNotices()) : Promise.resolve(null)', p)
        self.assertIn("alertDays(notices.data, w.days)", p)
        self.assertIn("data-scarcity-alert-days=", p)
        # also covered by site/scripts/test-grid-render.mjs: grid_scarcity_caiso on /grid?grid=caiso&view=mix
        self.assertIn("Restricted maintenance, not an alert and not marked", p)
        self.assertEqual(p.count("check="), 1)


class TheMonthlyMix(unittest.TestCase):
    def test_caiso_months_with_an_alert_are_marked_and_counted(self):
        f = src("components", "grid", "MixFigures.tsx")
        self.assertIn("alertMonths(notices.data, m.months)", f)
        self.assertIn("marks={al?.months.length ?", f)
        self.assertIn("data-mix-alert-months=", f)
        self.assertEqual(f.count("check="), 1)
        v = src("components", "grid", "MixView.tsx")
        self.assertIn('month && bas.some((b) => b.code === "ciso") ? attempt(() => gridNotices()) : Promise.resolve(null)', v)
        self.assertIn("notices={withheld ? notices : undefined}", v)

    def test_the_hourly_mix_stays_withheld(self):
        v = src("components", "grid", "MixView.tsx")
        self.assertIn('{withheld ? <Missing why={caiso} /> : hourly.ok ? <Hourly', v)


class TheAlertsPage(unittest.TestCase):
    def test_it_links_back(self):
        a = src("app", "grid", "caiso", "alerts", "page.tsx")
        # also covered by site/scripts/test-grid-render.mjs: grid_caisoalert_caiso on /grid?grid=caiso&view=mix
        self.assertIn('<Link href="/grid?grid=caiso#caiso-alerts">whether an alert is in force today</Link>', a)
        self.assertIn('<Link href="/grid?grid=caiso#scarcity">the alert days on the scarcity strip</Link>', a)

    def test_nothing_else_moved(self):
        a = src("app", "grid", "caiso", "alerts", "page.tsx")
        self.assertEqual(a.count("data-alerts-back="), 1)
        self.assertIn('<h1 className="mb-2 text-3xl">The Flex Alert scorecard: CAISO, 2018 to 2024</h1>', a)
        self.assertNotIn("caisoAlerts", a)


class TheKeys(unittest.TestCase):
    def test_check_values_recomputes_them_with_the_page_rule(self):
        cv = src("scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "awe" && (p[1] === "last" || p[1] === "ndays")) {', cv)
        self.assertIn('const A = await import("../lib/caisoAlerts.ts");', cv)
        self.assertLess(cv.index('p[1] === "ndays"'), cv.index('if (p[0] === "awe") {'))

    def test_the_method_note_names_them(self):
        with open(os.path.join(ROOT, "docs", "methods", "california_reliability.md"), encoding="utf-8") as f:
            note = f.read()
        for k in ("`awe|last|<group>|<day>`", "`awe|ndays|<group>|<from>|<to>`", "`signal`", "`any`", "`rmo`", "`transmission_emergency`"):
            self.assertIn(k, note)

    def test_the_node_test_passes(self):
        r = subprocess.run(["node", "scripts/test-caiso-alerts.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("12 of 12 passed", r.stdout)


class NoDash(unittest.TestCase):
    def test_no_em_dash(self):
        for rel in WROTE + ["site/components/grid/ScarcityPanel.tsx", "site/components/grid/MixFigures.tsx", "site/components/grid/MixView.tsx",
                            "site/app/grid/caiso/alerts/page.tsx", "docs/methods/california_reliability.md", "docs/methods/scarcity_hours_by_grid.md"]:
            with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                self.assertNotIn(DASH, f.read(), rel)


if __name__ == "__main__":
    unittest.main()
