"""Session 1413 (chain 107): the energy mix views' computed figures, keyed.

Session 1166 left without a key the figures the views (site/components/mix/views.tsx) compute from the committed files'
arrays: the duck curve year after year, the peak hours of the average day, the history by state, the availability
means. A new key kind, filecalc|<function>|<data file>|<args> behind fmt|<form>|, whose recomputation in
site/scripts/check-values.mjs applies the page's own function to the committed file (site/scripts/check-filecalc.mjs:
lib/mix2.ts acrossYears, periodOf, highest; lib/mixViewCalc.ts, the arithmetic that stood inline in the views, moved as
it stood). Each keyed table offers its file, carries its anchor (lib/gridAnchors.ts MIX_VIEW_ANCHOR) and links its
method (METHOD_MIX_VIEWS). The node test (site/scripts/test-mix-view-calc.mjs) holds each moved function to the old
expression on every committed file and every key the views write to its recomputation.
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
NEW = [("site", "lib", "mixViewCalc.ts"), ("site", "scripts", "check-filecalc.mjs"), ("site", "components", "mix", "CalcKey.tsx"),
       ("site", "scripts", "test-mix-view-calc.mjs"), ("tests", "test_session1413.py")]
CHANGED = [("site", "components", "mix", "views.tsx"), ("site", "lib", "gridAnchors.ts"), ("site", "scripts", "check-values.mjs"),
           ("site", "scripts", "check-methods.mjs"), ("site", "scripts", "test-grid-file-keys.mjs"), ("site", "scripts", "test-grid-files.mjs"),
           ("site", "scripts", "test-grid-render.mjs"), ("docs", "methods", "generation_mix_hourly.md"), ("tests", "test_session473.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME")}


class TheKind(unittest.TestCase):
    def test_check_values_reads_the_kind_by_the_pages_own_functions(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('import * as FCALC from "./check-filecalc.mjs";', cv)
        self.assertIn('if (p[0] === "filecalc") {', cv)
        self.assertIn("return FCALC.filecalcValue(f, dataFile(f.file));", cv)
        self.assertIn('/^(netday|filecalc)\\|/.test(fp ? fp.inner : check) ? "the committed file" : "Supabase"', cv)
        fc = src("site", "scripts", "check-filecalc.mjs")
        self.assertIn('import("../lib/mix2.ts"), import("../lib/mixViewCalc.ts")', fc)
        self.assertIn("mix.acrossYears(json, cal)", fc)
        self.assertIn("mix.highest(mix.periodOf(json, period)?.avg[source] ?? [])?.value", fc)

    def test_check_methods_names_the_kind(self):
        self.assertIn("MEASURE_AT.filecalc = 1;", src("site", "scripts", "check-methods.mjs"))

    def test_the_moved_arithmetic_has_no_import(self):
        lib = src("site", "lib", "mixViewCalc.ts")
        self.assertIsNone(re.search(r"^import ", lib, re.M))
        self.assertIn("return { share: v === undefined ? null : (100 * v) / historyTotal(h, s, y), mwh: v === undefined ? null : v / 1e6 };", lib)
        self.assertIn("(v ? v.reduce((a, b) => a + b, 0) / v.length : null)", lib)


class TheViews(unittest.TestCase):
    def test_the_views_call_the_moved_functions_and_key_through_one_component(self):
        v = src("site", "components", "mix", "views.tsx")
        self.assertEqual(v.count("check="), 1)   # session 1166's one K; the computed figures are drawn by CalcKey
        self.assertIn("MV.historyCell(HISTORY, s, y, f)", v)
        self.assertIn('ak("avail_mean", i, MV.availMean(v))', v)
        self.assertIn('kc(sol && sol.value > 0 ? sol.value : null, "n0", "day_peak", file, [period, "solar"]', v)
        self.assertIn('yk("duck_ramp", y, y.ramp)', v)
        self.assertNotIn("Math.min(...v)", v)
        self.assertEqual(v.count("<ViewMethod />"), 6)
        k = src("site", "components", "mix", "CalcKey.tsx")
        self.assertEqual(k.count("check="), 1)
        self.assertIn("<Num check={`fmt|${form}|${filecalcKey(fn, file, args)}`} raw={v}>{text}</Num>", k)

    def test_each_table_has_its_anchor_and_the_method_its_section(self):
        a = src("site", "lib", "gridAnchors.ts")
        for w in ('dayShares: "day-shares"', 'duckYears: "duck-by-year"', 'historyShares: "history-shares"', 'supplyTight: "supply-tight"',
                  'export const METHOD_MIX_VIEWS = "/data/methods/generation_mix_hourly#the-computed-views-keyed-chain-107-24-october-2026";'):
            self.assertIn(w, a)
        n = src("docs", "methods", "generation_mix_hourly.md")
        self.assertIn("## The computed views, keyed (chain 107, 24 October 2026)", n)
        for w in ("filecalc|", "duck_solar_peak", "day_peak", "hist_share", "avail_mean", "Decisions (chain 107, session 1413):"):
            self.assertIn(w, n)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in NEW + CHANGED:
            self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_every_case_holds(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-mix-view-calc.mjs"],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIsNotNone(re.search(r"^\S* ?pass 11\b", r.stdout, re.M), r.stdout[-1500:])


if __name__ == "__main__":
    unittest.main()
