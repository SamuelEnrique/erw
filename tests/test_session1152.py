"""Session 1152 (chain 077): the Grid tool's energy mix panel, grid_mix_<grid>, at the top of the Mix tab's hourly block.

The figures are lib/mixHourly.ts's (tested on a committed fixture of real rows by site/scripts/test-mix-hourly.mjs, run
here when node is present); the panel is components/grid/MixFigures.tsx, drawn by components/grid/MixView.tsx; the
monthly view is in the address (mixp=month, lib/mixpage.ts); scripts/check-values.mjs sums a list of variables in one
series_sum key and reads the two monthly addresses. California's hourly mix stays withheld (the session 118 ruling).
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
DASHES = (chr(0x2014), "\\u2014", "&mdash;")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePanel(unittest.TestCase):
    def test_the_panel_is_named_and_placed_at_the_top_of_the_hourly_block(self):
        v = src("site", "components", "grid", "MixView.tsx")
        # also covered by site/scripts/test-grid-render.mjs: grid_mix_ercot on /grid?grid=ercot&view=mix
        self.assertIn("<div data-grid-panel={`grid_mix_${grid}`}>", v)
        top = v.index('<section id={i ? `hourly-${b.code}` : "hourly"} className="mb-8">')
        self.assertLess(top, v.index("data-grid-panel={`grid_mix_${grid}`}"))
        self.assertLess(v.index("data-grid-panel={`grid_mix_${grid}`}"), v.index("<Legend items={HOURLY_FUELS.map("))
        # also covered by site/scripts/test-grid-render.mjs: mixview_now on /grid?grid=ercot&view=mix
        self.assertIn("hourly mix, last 7 days", v)

    def test_california_stays_withheld_as_the_ruling_says(self):
        v = src("site", "components", "grid", "MixView.tsx")
        self.assertEqual(v.count("withheld ? <Missing why={caiso}"), 2)
        self.assertIn("!month && !withheld && hourly.ok ? mixHourly(", v)
        self.assertNotIn("license needed", v)

    def test_the_figures_are_keys_with_a_source_in_the_tip(self):
        f = src("site", "components", "grid", "MixFigures.tsx")
        self.assertIn('<span title={f.tip} className="cursor-help border-b border-dotted border-muted">', f)
        self.assertIn("<Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>", f)
        lib = src("site", "lib", "mixHourly.ts")
        for kind in ("series_sum|${GEN}|", "calc|pct|", "series_max|${DEMAND}|demand_mw|", "series|${GEN}|${entity}|${NET}|", "series|${PROFILE}|", "series_esum|${PROFILE}|"):
            self.assertIn(kind, lib, kind)
        self.assertIsNone(re.search(r"^import ", lib, re.M))   # no import: a node test loads it with type stripping

    def test_the_chart_hovers_with_share_and_names_the_peak(self):
        v = src("site", "components", "grid", "MixView.tsx")
        self.assertIn("<Hourly rows={hourly.data} table={table} label={b.label} share through={figures?.newest.t}", v)
        self.assertIn("name: `Peak demand, ", v)
        t = src("site", "components", "TimeChart.tsx")
        self.assertIn("share = false, marks }: Props) {", t)
        self.assertIn("{share ? shareOf(v, hover.t) : \"\"}", t)
        self.assertIn("data-chart-mark={m.name}", t)

    def test_a_mixed_sign_stack_draws_each_band_from_its_own_side(self):
        t = src("site", "components", "TimeChart.tsx")
        self.assertIn("if (v >= 0) { bases![k][i] = up[i]; up[i] += v; return up[i]; }", t)
        self.assertIn("bases![k][i] = down[i]; down[i] += v; return down[i];", t)
        self.assertIn("const base = (i: number) => `${px(xs[i]).toFixed(1)},${py(bases[k][i], b).toFixed(1)}`;", t)
        self.assertNotIn("const below = k === 0 ? null : stacked[k - 1];", t)

    def test_the_monthly_view_is_in_the_address(self):
        lib = src("site", "lib", "mixpage.ts")
        self.assertIn('...(view === "now" && one(q.mixp) === "month" ? { mixp: "month" as const } : {}),', lib)
        self.assertIn('if (n.mixp === "month") q.set("mixp", "month");', lib)
        v = src("site", "components", "grid", "MixView.tsx")
        self.assertIn('{month ? <input type="hidden" name="mixp" value="month" /> : null}', v)

    def test_check_values_knows_the_keys(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('variable: variable.includes(",") ? `in.(${variable})` : `eq.${variable}`', cv)
        self.assertIn('"/grid?grid=ercot&mixp=month", "/grid?grid=caiso&mixp=month"', cv)

    def test_no_dash(self):
        for p in (("site", "lib", "mixHourly.ts"), ("site", "components", "grid", "MixFigures.tsx"), ("site", "scripts", "test-mix-hourly.mjs"),
                  ("site", "components", "grid", "MixView.tsx"), ("site", "components", "TimeChart.tsx"), ("tests", "fixtures", "session1152", "mix_hourly_erco.json")):
            text = src(*p)
            for d in DASHES:
                self.assertNotIn(d, text, "/".join(p))


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_the_figures_recompute_on_the_fixture(self):
        r = subprocess.run([NODE, "scripts/test-mix-hourly.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertRegex(r.stdout, r"\d+ tests passed")


if __name__ == "__main__":
    unittest.main()
