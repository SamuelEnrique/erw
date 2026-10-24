"""Session 1403 (chain 100): the cleanest hours, live.

Energy Research Warehouse (ERW).

Beside the Clean tab's committed "the cleanest hours of the average day" (site/components/mix/views.tsx CleanView, from
site/data/clean/<grid>.json), the panel grid_cleanweek_<grid> draws the newest 7 whole local days of
carbon_intensity_hourly (intensity_generation, the committed view's own generation) in the same shape, the hour of day
across and the day down, in the committed file's clock time; the week's cleanest and dirtiest hours and its mean keyed
(series_min and series_mean, new kinds that site/scripts/check-values.mjs recomputes with site/lib/cleanWeek.ts weekStat;
series_max and series_n as before), and a line setting the week against the committed average day of its month in
words. The method is docs/methods/generation_mix_hourly.md, section "The cleanest hours, live (chain 100, 24 October 2026)".

    python -m unittest tests.test_session1403 -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react", "marked"))
EM = chr(0x2014)
HEADING = "## The cleanest hours, live (chain 100, 24 October 2026)"
FILES = [("site", "lib", "cleanWeek.ts"), ("site", "components", "grid", "CleanWeekPanel.tsx"),
         ("site", "scripts", "test-clean-week.mjs"), ("site", "scripts", "fixtures", "clean_week.json"),
         ("tests", "test_session1403.py"), ("archive", "sessions", "SESSION_1403_REPORT.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheCleanWeek(unittest.TestCase):
    def test_the_table_the_variable_and_the_kinds(self):
        lib = src("site", "lib", "cleanWeek.ts")
        for w in ('export const CARBON_TABLE = "carbon_intensity_hourly";', 'export const CLEAN_VARIABLE = "intensity_generation";',
                  "export const READ_DAYS = 12;", "export function weekStat(", "export function weekWindow(", "export function compareWords("):
            self.assertIn(w, lib)
        self.assertNotRegex(lib, r"(?m)^import ")  # no import: check-values loads the file as it is
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "series_min" || p[0] === "series_mean") {', cv)
        self.assertIn('return W.weekStat(rows, p[0].slice("series_".length), start, end);', cv)
        self.assertIn("series_min: [1, 2], series_mean: [1, 2],", src("site", "scripts", "check-methods.mjs"))

    def test_the_view_and_the_read(self):
        v = src("site", "components", "grid", "MixView.tsx")
        self.assertIn("export async function MixClean({ c }: { c: Choice }) {", v)
        self.assertIn("since: daysAgo(READ_DAYS)", v)
        self.assertIn("<CleanView c={c} live={live} />", v)
        views = src("site", "components", "mix", "views.tsx")
        self.assertIn("live?: (g: Slug, year: string) => ReactNode }) {", views)
        # the view is drawn as before where no caller passes `live`
        self.assertIn(": <Block key={g} title={`${nameOf(g)}, ${year}`}><LW /></Block>;", views)
        a = src("site", "lib", "gridAnchors.ts")
        self.assertIn('export const CLEAN_WEEK_ANCHOR = "clean-week";', a)
        self.assertIn('export const METHOD_CLEAN_WEEK = "/data/methods/generation_mix_hourly#the-cleanest-hours-live-chain-100-24-october-2026";', a)
        self.assertIn("export function heldCarbon(", src("site", "lib", "gridHeld.ts"))

    def test_the_method_section_and_its_decisions(self):
        n = src("docs", "methods", "generation_mix_hourly.md")
        self.assertIn(HEADING, n)
        sec = n.split(HEADING)[1].split("\n## ")[0]
        for w in ("Decisions (chain 100, session 1403):", "`intensity_generation`, not `intensity_demand`", "series_min|", "series_mean|",
                  "grid_cleanweek_<grid>", "`CLEAN_WEEK_ANCHOR`", "`METHOD_CLEAN_WEEK`", "caisoJoinDay()", "Etc/GMT+5", "license needed"):
            self.assertIn(w, sec)
        self.assertLess(n.index("## The hub's price beside the hourly mix (chain 100, 24 October 2026)"), n.index(HEADING))
        self.assertLess(n.index(HEADING), n.index("## The figures on the page and their keys"))

    def test_the_older_tests_are_extended(self):
        t = src("tests", "test_session473.py")
        self.assertIn('"components/grid/CleanWeekPanel.tsx": 1,', t)
        self.assertIn('"grid_clean24_ercot", "grid_cleanweek_ercot"', src("site", "scripts", "test-grid-files.mjs"))
        f = src("site", "scripts", "test-grid-failed-reads.mjs")
        self.assertIn("grid_cleanweek_ercot (1403), carbon_intensity_hourly", f)
        self.assertIn("|ask|hubprice)_|", f)
        self.assertIn("const NAMED_1403 = /^grid_cleanweek_/;", f)

    def test_no_em_dash(self):
        for parts in FILES + [("docs", "methods", "generation_mix_hourly.md")]:
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertNotIn(EM, src(*parts), parts)

    @unittest.skipUnless(NODE and MODULES, "node and site/node_modules are needed")
    def test_the_node_test_passes(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-clean-week.mjs"],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", env=node_env(), timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("pass 9", r.stdout)


if __name__ == "__main__":
    unittest.main()
