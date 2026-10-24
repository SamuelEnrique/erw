"""Session 1414 (chain 107): the Clean tab's large tables keyed whole.

Session 1166 keyed the Clean tab's headline tables ("Carbon-free share and hours", "The seven grids") and left the
large ones; session 1168 keyed the stress tables whole. The Clean tab's three large tables (site/components/mix/views.tsx
CleanView: the annual purchase against the hours, the cleanest hours by month, the flat load moved into the cleanest
hours by year) are now keyed whole: each figure a value of the committed file (file|clean/<grid>.json|..., session
1166's kind) or, the cleanest and the dirtiest hour of a month, the page's own function on its day (filecalc|clean_day_max
and clean_day_min, session 1413's kind; lib/mixViewCalc.ts cleanDayHeld, cleanDayMax, cleanDayMin, the expression that
stood in the view, moved as it stood). A held grid's cells stay "license needed" (lib/gridHeld.ts) and carry no key. Each
of the tab's five tables offers its file, carries its anchor (lib/gridAnchors.ts CLEAN_TABLE_ANCHOR) and links its method
(METHOD_CLEAN_TABLES, a section of docs/methods/generation_mix_hourly.md). The node tests hold every key to its file
(site/scripts/test-grid-file-keys.mjs), the moved expression to the old one (test-mix-view-calc.mjs), the files and
anchors (test-grid-files.mjs) and the page as the server draws it (test-grid-render.mjs, three mixview_clean cases).
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
NEW = [("tests", "test_session1414.py")]
CHANGED = [("site", "components", "mix", "views.tsx"), ("site", "lib", "gridAnchors.ts"), ("site", "lib", "mixViewCalc.ts"),
           ("site", "scripts", "check-filecalc.mjs"), ("site", "scripts", "test-grid-file-keys.mjs"), ("site", "scripts", "test-mix-view-calc.mjs"),
           ("site", "scripts", "test-grid-files.mjs"), ("site", "scripts", "test-grid-render.mjs"), ("site", "scripts", "test-clean-week.mjs"),
           ("docs", "methods", "generation_mix_hourly.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME")}


class TheTables(unittest.TestCase):
    def test_the_large_tables_are_keyed_through_the_views_own_helpers(self):
        v = src("site", "components", "mix", "views.tsx")
        self.assertEqual(v.count("check="), 1)   # session 1166's one K: every figure goes through K, kv or kc
        self.assertIn("pc(v.match[s]?.[p]?.energy, `${yy}.match_${s}_${p}_energy_pct`), pc(v.match[s]?.[p]?.hours, `${yy}.match_${s}_${p}_hours_pct`)", v)
        self.assertIn('kc(MV.cleanDayMax(f, m), "n1", "clean_day_max", cf, [m], "%")', v)
        self.assertIn('kc(MV.cleanDayMin(f, m), "n1", "clean_day_min", cf, [m], "%")', v)
        self.assertIn("pc(clean.get(f.months[m], \"carbon_free_share_pct\"), `months.${m}.carbon_free_share_pct`)", v)
        self.assertIn('kv(w.carbon.flat, "n1", cf, `${wy}.flat_kgco2_per_mwh`)', v)
        self.assertIn('<K key="c" v={w.cost.flat} form="n2" file={cf} at={`${wy}.flat_cost_usd_per_mwh`} />', v)
        self.assertIn('kv(w.cost.days, "n0", cf, `${wy}.cost_days`, "", noPrice)', v)
        self.assertNotIn("Math.max(...d)", v)
        self.assertNotIn("Math.min(...d)", v)
        # a held grid's blocks return before any key (session 1167's rule)
        self.assertIn("if (held(g)) return week ?", v)

    def test_each_table_has_its_file_anchor_and_method(self):
        v = src("site", "components", "mix", "views.tsx")
        self.assertEqual(v.count("<CleanMethod />"), 5)
        self.assertEqual(v.count("<ViewMethod />"), 6)   # session 1413's line, as it was
        self.assertIn("<SiteLink href={METHOD_CLEAN_TABLES}>Method: the Clean tab&apos;s tables, keyed</SiteLink>", v)
        for w in ('cleanFile(c.grids, "grid_clean_all", `shares_${year}`', 'cleanFile([g], `grid_clean_${g}`, `purchase_${year}`',
                  'cleanFile([g], `grid_clean_${g}`, `months_${year}`', 'cleanFile([g], `grid_clean_${g}`, "shift"', 'cleanFile(clean.GRIDS, "grid_clean_all", `grids_${year}`'):
            self.assertIn(w, v)
        a = src("site", "lib", "gridAnchors.ts")
        for w in ('shares: "clean",', 'purchase: "clean-purchase",', 'months: "clean-months",', 'shift: "clean-shift",', 'grids: "clean-grids",',
                  'export const METHOD_CLEAN_TABLES = "/data/methods/generation_mix_hourly#the-clean-tabs-tables-keyed-whole-session-1414";'):
            self.assertIn(w, a)

    def test_the_function_and_the_kind(self):
        lib = src("site", "lib", "mixViewCalc.ts")
        self.assertIn("return day.filter((x): x is number => x !== null);", lib)
        self.assertIn("{ const d = cleanDayHeld(f, m); return d.length ? Math.max(...d) : null; }", lib)
        self.assertIn("{ const d = cleanDayHeld(f, m); return d.length ? Math.min(...d) : null; }", lib)
        fc = src("site", "scripts", "check-filecalc.mjs")
        self.assertIn("clean_day_max: { file: CLEAN, args: [MONTH] },", fc)
        self.assertIn('v = fn === "clean_day_max" ? calc.cleanDayMax(json, args[0]) : calc.cleanDayMin(json, args[0]);', fc)

    def test_the_note(self):
        n = src("docs", "methods", "generation_mix_hourly.md")
        self.assertIn("### The Clean tab's tables, keyed whole (session 1414)", n)
        sec = n.split("### The Clean tab's tables, keyed whole (session 1414)")[1].split("\n## ")[0]
        for w in ("filecalc|clean_day_max", "clean_day_min", "clean_energy_summary", "year_match_mix_<p>_energy_pct", "year_flat_kgco2_per_mwh",
                  "year_shift<s>_carbon_change_pct", "year_cost_days", "392 more", "test-grid-file-keys.mjs", "Decisions (chain 107, session 1414):"):
            self.assertIn(w, sec)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in NEW + CHANGED:
            self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTests(unittest.TestCase):
    def run_node(self, script, done):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", script],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn(done, r.stdout)

    def test_the_files_and_anchors(self):
        self.run_node("scripts/test-grid-files.mjs", "ok   the Clean tab's tables: each carries its anchor")


if __name__ == "__main__":
    unittest.main()
