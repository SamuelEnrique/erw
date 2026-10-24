"""Session 1168 (chain 078): how hard the system works, in the Mix tab, year by year.

The view "How hard the system works" (site/components/mix/views.tsx StressView, /grid?view=mix&mix=stress) draws the
four measures of docs/methods/grid_stress.md as charts with a point a year, the values picked from the committed file
by site/lib/gridStress.ts: the evening ramp (the chart that stood, its series as they were, a note and a line added to
its hover), the lowest net load, the tightest hours and the longest dark, calm stretch. Each chart's hover ends with
what the figure is not (the note's section "What each chart is not (session 1168)"), and a link under each opens it.
The large tables (the fuels in the tightest hours, the dark, calm stretches) are keyed whole, "The longest" in a new
form, span (site/scripts/check-format.mjs). The node tests: site/scripts/test-grid-stress.mjs (new) and
site/scripts/test-grid-file-keys.mjs (extended).
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
NEW = [("site", "lib", "gridStress.ts"), ("site", "scripts", "test-grid-stress.mjs"), ("tests", "test_session1168.py")]
CHANGED = [("site", "components", "mix", "views.tsx"), ("site", "components", "mix", "Charts.tsx"), ("site", "scripts", "check-format.mjs"),
           ("site", "scripts", "test-grid-file-keys.mjs"), ("docs", "methods", "grid_stress.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME")}


class TheStressCharts(unittest.TestCase):
    def test_the_charts_take_a_note_and_a_line_off_by_default(self):
        c = src("site", "components", "mix", "Charts.tsx")
        self.assertIn("notes?: (string | null)[]; tip?: string }) {", c)
        self.assertEqual(c.count("notes={notes}><Tip tip={tip} /></CategoryChart>"), 2)   # Lines and Bars
        self.assertIn('return tip ? <div className="mt-1 max-w-[260px] border-t border-rule pt-1 text-muted" data-chart-not="1">{tip}</div> : null;', c)
        # the four charts session 317 kept are still the file's exports
        for name in ("export function HourStack(", "export function Lines(", "export function Bars(", "export function Heat("):
            self.assertIn(name, c)

    def test_the_view_draws_the_four_measures(self):
        v = src("site", "components", "mix", "views.tsx")
        self.assertIn('import * as GS from "@/lib/gridStress";', v)
        for name in ('name="erw-mix-ramp"', 'name="erw-mix-netload"', "name={`erw-mix-tight-${g}`}", "name={`erw-mix-calm-${g}`}"):
            self.assertIn(name, v)
        for m in ("ramp", "netload", "tight", "calm"):
            self.assertIn('{not("%s")}' % m, v)
            self.assertIn("tip={GS.NOT.%s}" % m, v)
        self.assertEqual(v.count("check={"), 1)   # test_session473: the one K writes every key
        self.assertIn('ck("calm_longest_hours", "span")', v)
        self.assertIn('kv(k("calm_longest_hours"), "span", `stress/${g}.json`, `years.${year}.calm_longest_hours`)', v)

    def test_the_lines_and_the_link(self):
        g = src("site", "lib", "gridStress.ts")
        self.assertIn('export const STRESS_METHOD = "/data/methods/grid_stress#what-each-chart-is-not-session-1168";', g)
        self.assertIn('import { caisoJoinDay } from "@/lib/caisoJoin";', g)   # test_session78: no second copy of the join's date
        self.assertNotRegex(g, r"2025-12-16|16 December 2025")
        note = src("docs", "methods", "grid_stress.md")
        for words in ("### The four measures by year, on the Mix tab (session 1168)", "### What each chart is not (session 1168)",
                      "### The large tables, keyed whole (session 1168)", "Decisions (session 1168):", "612 added",
                      "tight_<natural_gas, coal, nuclear, wind, solar, hydro, storage, hydro_storage>_mw"):
            self.assertIn(words, note)
        # the note's own section stands as it was
        for words in ("- **Not what a plant could do.** A plant below its capacity in a tight hour may have been in reserve,",
                      "- **The definition of dark and calm is one line.** At night solar is zero whatever is installed, so the measure"):
            self.assertIn(words, note)

    def test_the_span_form(self):
        f = src("site", "scripts", "check-format.mjs")
        self.assertIn("  span: (x) => span(x),", f)
        s = src("site", "lib", "stress.ts")
        # the form is lib/stress.ts span as it stands there
        for line in ('const d = Math.floor(hours / 24), h = Math.round(hours - d * 24);',
                     'const days = d ? `${d} day${d === 1 ? "" : "s"}` : "", hs = h || !d ? `${h} hour${h === 1 ? "" : "s"}` : "";',
                     'return [days, hs].filter(Boolean).join(" ");'):
            self.assertIn(line, s)
            self.assertIn(line, f)

    def test_no_em_dash(self):
        for parts in NEW + CHANGED:
            self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTests(unittest.TestCase):
    def run_node(self, script, n):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", script],
                           cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIsNotNone(re.search(r"^\S* ?pass %d" % n, r.stdout, re.M), r.stdout[-1500:])

    def test_stress(self):
        self.run_node("scripts/test-grid-stress.mjs", 7)

    def test_file_keys(self):
        self.run_node("scripts/test-grid-file-keys.mjs", 14)


if __name__ == "__main__":
    unittest.main()
