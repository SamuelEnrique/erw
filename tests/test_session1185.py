"""Session 1185 (chain 091): the Lower 48 in each new panel.

Energy Research Warehouse (ERW).

The energy mix panel's view by month (grid_mix_us48, mixp=month) said "not built for the Lower 48": it now draws the
Lower 48 as the sum of the 48 contiguous states and DC in state_generation_mix_monthly (EIA-923, not EIA-930's US48),
site/lib/lower48.ts and site/components/grid/Lower48Mix.tsx, keyed by a new kind, states_sum, that
site/scripts/check-values.mjs recomputes with the page's own function. The scarcity strip's line for the Lower 48 stays
and says why: the method defines no national scarcity measure. The method is docs/methods/generation_mix.md, section
"The Lower 48 by month, the sum of the states (chain 091, 24 October 2026)".

    python -m unittest tests.test_session1185 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react", "marked"))
EM = chr(0x2014)
HEADING = "## The Lower 48 by month, the sum of the states (chain 091, 24 October 2026)"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheLower48ByMonth(unittest.TestCase):
    def test_the_view_is_drawn_not_said_not_built(self):
        v = src("site", "components", "grid", "MixView.tsx")
        self.assertNotIn('words="not built for the Lower 48"', v)
        self.assertIn('grid === "us48" ? (more && more.ok ? <Lower48Monthly rows={more.data} /> : failed(more && !more.ok ? more.reason : "no read"))', v)
        self.assertIn("series(STATE_MIX, { entities: LOWER48_ENTITIES, since: `${daysAgo(800).slice(0, 7)}-01T00:00:00Z` })", v)

    def test_the_group_and_the_rule(self):
        lib = src("site", "lib", "lower48.ts")
        states = re.search(r"export const LOWER48_STATES = \[([^\]]+)\]", lib).group(1)
        codes = re.findall(r'"([A-Z]{2})"', states)
        self.assertEqual(len(codes), 49)
        self.assertIn("DC", codes)
        for x in ("AK", "HI", "PR", "US"):
            self.assertNotIn(x, codes)
        self.assertIn("export function statesSum(", lib)
        # also covered by site/scripts/test-grid-render.mjs: grid_mix_us48 on /grid?grid=us48&view=mix&mixp=month
        self.assertIn("`states_sum|${STATE_MIX}|${variables.join(\",\")}|${start}|${end}|${group}`", lib)
        self.assertNotIn("import ", lib.split("export const STATE_MIX")[0].replace("no import", ""))

    def test_the_face_says_what_it_is(self):
        c = src("site", "components", "grid", "Lower48Mix.tsx")
        self.assertIn("monthly net generation by state ({STATE_MIX}), not EIA-930&apos;s US48 total, which adds up the balancing authorities hour by hour", c)
        # also covered by site/scripts/test-grid-render.mjs: grid_mix_us48 on /grid?grid=us48&view=mix&mixp=month
        self.assertIn("A month is drawn only\n        when every one of the 49 holds it.", c)
        # also covered by site/scripts/test-grid-render.mjs: grid_mix_us48 on /grid?grid=us48&view=mix&mixp=month
        self.assertIn("<SiteLink href={METHOD_MIX_US48}>Method: the Lower 48 by month, the sum of the states</SiteLink>", c)
        self.assertEqual(c.count("<PanelFile "), 1)
        self.assertEqual(c.count("check="), 1)
        self.assertNotIn('from "@/components/mix/Now"', c)

    def test_the_checkers_know_the_kind(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "states_sum") {', cv)
        self.assertIn("return L.statesSum(statesRows.get(k), entities, variable.split(\",\"), start, end);", cv)
        self.assertIn('"/grid?grid=ercot&mixp=month", "/grid?grid=caiso&mixp=month",\n  // session 1185', cv)
        self.assertIn('  "/grid?grid=us48&mixp=month",', cv)
        self.assertIn("states_sum: [1, 2],", src("site", "scripts", "check-methods.mjs"))
        self.assertIn('else if (head === "states_sum") table = p[1] ?? "";', src("site", "components", "Num.tsx"))
        self.assertIn('["/grid?grid=us48&mixp=month", ["grid_mix_us48_monthly"]]', src("site", "scripts", "grid-files.mjs"))

    def test_the_method_link(self):
        a = src("site", "lib", "gridAnchors.ts")
        self.assertIn('export const METHOD_MIX_US48 = "/data/methods/generation_mix#the-lower-48-by-month-the-sum-of-the-states-chain-091-24-october-2026";', a)
        body = a[a.index("export const GRID_METHOD"):]
        self.assertNotIn("METHOD_MIX_US48", body[:body.index("};")])


class TheScarcityLine(unittest.TestCase):
    def test_the_lower_48_line_stays_and_says_why(self):
        s = src("site", "components", "grid", "ScarcityPanel.tsx")
        self.assertIn('<p className="max-w-3xl text-sm" data-scarcity-us48="1">', s)
        # also covered by site/scripts/test-grid-render.mjs: grid_scarcity_us48 on /grid?grid=us48&view=mix
        self.assertIn("is by grid, and it holds two:", s)
        # also covered by site/scripts/test-grid-render.mjs: grid_scarcity_us48 on /grid?grid=us48&view=mix
        self.assertIn('<span data-scarcity-us48-why="1">The Lower 48 has no strip of its own:', s)
        # also covered by site/scripts/test-grid-render.mjs: grid_scarcity_us48 on /grid?grid=us48&view=mix
        self.assertIn("so the method defines no national scarcity measure, and none is summed from the grids.", s)
        n = src("docs", "methods", "scarcity_hours_by_grid.md")
        self.assertIn("- **The Lower 48 has no strip of its own** (session 1185, chain 091, 24 October 2026)", n)


class TheNotes(unittest.TestCase):
    def test_the_section_and_its_decisions(self):
        n = src("docs", "methods", "generation_mix.md")
        self.assertIn(HEADING, n)
        part = n[n.index(HEADING):]
        for w in ("**Which locations.**", "**Which months.**", "**A missing state month.**", "is not drawn and not summed",
                  "`states_sum|state_generation_mix_monthly|<variables, comma separated>|<start>|<end>|lower48`",
                  "`net_generation_<natural_gas, coal, nuclear, wind, solar, hydro, other_renewables, oil_and_other, not_itemized>_mwh`",
                  "not EIA-930's US48", "Decisions (chain 091):"):
            self.assertIn(w, part, w)
        self.assertIn("Since session 1185 (chain 091) the view is drawn", src("docs", "methods", "generation_mix_hourly.md"))

    def test_the_fixture_is_real_rows_of_the_49(self):
        import json
        with open(os.path.join(SITE, "scripts", "fixtures", "lower48_mix.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.assertIn("anon key", d["source"])
        self.assertEqual(sorted(d["months"]), [f"2025-{m:02d}" for m in range(8, 13)] + [f"2026-{m:02d}" for m in range(1, 9)])
        for m, states in d["months"].items():
            self.assertEqual(len(states), 49, m)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "lower48.ts"), ("site", "components", "grid", "Lower48Mix.tsx"), ("site", "scripts", "test-lower48.mjs"),
                      ("docs", "methods", "generation_mix.md"), ("docs", "methods", "scarcity_hours_by_grid.md"), ("site", "components", "grid", "ScarcityPanel.tsx"),
                      ("site", "components", "grid", "MixView.tsx"), ("tests", "test_session1185.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


@unittest.skipUnless(NODE, "node is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_every_key_recomputes(self):
        r = subprocess.run([NODE, "scripts/test-lower48.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("9 tests passed", r.stdout)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react, marked) is not on this machine")
class TheDrawnPages(unittest.TestCase):
    def run_node(self, script):
        args = [NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", script]
        return subprocess.run(args, cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())

    def test_the_view_drawn_with_its_file_and_links(self):
        r = self.run_node("scripts/test-grid-files.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("ok   /grid?grid=us48&view=mix&mixp=month: grid_mix_us48", r.stdout)
        self.assertIn("ok   /grid?grid=us48&view=mix&mixp=month: the Lower 48 by month, the sum of the states, keyed, its file and both method links", r.stdout)

    def test_a_failed_read(self):
        r = self.run_node("scripts/test-grid-failed-reads.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertEqual(len(re.findall(r"^ok   grid_mix_us48 \(1185, by month\), state_generation_mix_monthly, ", r.stdout, re.M)), 3)

    def test_the_method_link_resolves_and_check_methods_reads_the_note(self):
        r = self.run_node("scripts/test-grid-methods.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        r = subprocess.run([NODE, "scripts/check-methods.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        line = next(x for x in r.stdout.splitlines() if x.startswith("notes | /grid |"))
        self.assertIn("generation_mix (", line)


if __name__ == "__main__":
    unittest.main()
