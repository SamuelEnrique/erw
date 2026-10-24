"""Session 1184 (chain 091): the method from each panel.

Energy Research Warehouse (ERW).

Each panel chains 077, 078 and 091 added to the Grid tool links the section of its method note that defines it
(site/lib/gridAnchors.ts GRID_METHOD, /data/methods/<note>#<heading id>), as the older blocks' source lines end with
"Method". site/scripts/test-grid-methods.mjs renders each committed note with the site's own renderer
(site/lib/markdown.ts) and holds each fragment to an id of it, by check-links.mjs's own logic; site/scripts/test-grid-files.mjs
holds each drawn panel to its link; site/scripts/check-methods.mjs reads each METHOD_<PANEL> as a note of /grid.

    python -m unittest tests.test_session1184 -v
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

KEYS = ["network", "replay", "balance", "gravity", "exchangeGrids", "exchangeTies", "exchangeMonths", "clean24", "mix", "scarcity",
        "caisoAlerts", "ercotNotices", "ask", "stressRamp", "stressTight", "stressCalm", "stressGrids"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def const_of(key):
    """A panel's constant in site/lib/gridAnchors.ts: METHOD_ and its key in capitals (exchangeGrids: METHOD_EXCHANGE_GRIDS)."""
    return "METHOD_" + re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key).upper()


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheList(unittest.TestCase):
    def test_one_method_a_panel(self):
        a = src("site", "lib", "gridAnchors.ts")
        self.assertIn("export const GRID_METHOD: Record<GridAnchorKey, string> = {", a)
        body = a[a.index("export const GRID_METHOD"):]
        body = body[:body.index("};")]
        for k in KEYS:
            c = const_of(k)
            self.assertIn(f"\n  {k}: {c},", body, k)
            self.assertRegex(a, r"\nexport const " + c + r' = "/data/methods/[a-z0-9_]+#[a-z0-9_-]+";', c)

    def test_each_panel_links_it(self):
        uses = {
            ("components", "grid", "NetworkFigures.tsx"): ["<Link href={METHOD_NETWORK}>Method: ", "<Link href={METHOD_BALANCE}>Method: ", "<Link href={METHOD_GRAVITY}>Method: "],
            ("components", "grid", "ReplayDay.tsx"): ["<Link href={METHOD_REPLAY}>Method: "],
            ("components", "grid", "ExchangeView.tsx"): ["<Link href={METHOD_EXCHANGE_GRIDS}>Method: ", "<Link href={METHOD_EXCHANGE_TIES}>Method: ", "<Link href={METHOD_EXCHANGE_MONTHS}>Method: "],
            ("components", "grid", "Emissions.tsx"): ["<Link href={METHOD_CLEAN24}>Method: "],
            ("components", "grid", "MixView.tsx"): ["<SiteLink href={METHOD_MIX}>Method: "],
            ("components", "grid", "ScarcityPanel.tsx"): ["<SiteLink href={METHOD_SCARCITY}>Method: each grid&apos;s own scarcity signal</SiteLink>"],
            ("components", "grid", "CaisoAlertState.tsx"): ["<Link href={METHOD_CAISO_ALERTS}>Method: California reliability</Link>"],
            ("components", "grid", "ErcotNoticeState.tsx"): ['<Link href="/data/methods/ercot_grid_notices">Method: ERCOT&apos;s grid notices</Link>; <Link href={METHOD_ERCOT_NOTICES}>Method: '],
            ("components", "grid", "AskExamples.tsx"): ["<Link href={METHOD_ASK}>Method: "],
            ("components", "mix", "views.tsx"): ["<SiteLink href={METHOD_STRESS_RAMP}>Method: ", "<SiteLink href={METHOD_STRESS_TIGHT}>Method: ",
                                                 "<SiteLink href={METHOD_STRESS_CALM}>Method: ", "<SiteLink href={METHOD_STRESS_GRIDS}>Method: "],
        }
        for parts, words in uses.items():
            s = src("site", *parts)
            for w in words:
                self.assertIn(w, s, f"{'/'.join(parts)}: {w}")
        self.assertEqual(src("site", "components", "grid", "Emissions.tsx").count("<Link href={METHOD_CLEAN24}>"), 2)
        p = src("site", "components", "grid", "PanelMethod.tsx")
        self.assertIn('return <p className="mt-1 text-xs text-muted" data-grid-method={at}>{children}.</p>;', p)
        # the scarcity strip's own source line links the section; the whole note is no longer its only link
        self.assertNotIn('const METHOD = "/data/methods/scarcity_hours_by_grid";', src("site", "components", "grid", "ScarcityPanel.tsx"))

    def test_no_component_links_the_whole_list(self):
        # scripts/page_tables.py reads the constants a component imports: the whole list would name ercot_grid_notices and
        # scarcity_hours_by_grid, notes named like tables, as reads of the network's panels (tests/test_session502.py)
        for d in (("components", "grid"), ("components", "mix")):
            for f in os.listdir(os.path.join(SITE, *d)):
                if f.endswith(".tsx") and f != "PanelMethod.tsx":
                    self.assertNotIn("GRID_METHOD", src("site", *d, f), f)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react, marked) is not on this machine")
class TheNodeTests(unittest.TestCase):
    def run_node(self, script, tsx=True):
        args = [NODE, "--import", "./scripts/alias-register.mjs"] + (["--import", "./scripts/tsx-register.mjs"] if tsx else []) + [script]
        return subprocess.run(args, cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())

    def test_the_fragments_on_the_rendered_notes(self):
        r = self.run_node("scripts/test-grid-methods.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertRegex(r.stdout, r"pass 5\b")
        self.assertRegex(r.stdout, r"fail 0\b")

    def test_the_drawn_pages(self):
        r = self.run_node("scripts/test-grid-files.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(len(re.findall(r"each panel links its method's own section", r.stdout)), 18)
        self.assertIn("ok   every panel's method link is drawn on a page above (session 1184)", r.stdout)

    def test_check_methods(self):
        r = subprocess.run([NODE, "scripts/check-methods.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        line = next(x for x in r.stdout.splitlines() if x.startswith("notes | /grid |"))
        for slug in ("grid_network", "grid_network_v3", "generation_mix_hourly", "grid_stress", "scarcity_hours_by_grid", "california_reliability", "ercot_grid_notices"):
            self.assertIn(f"{slug} (", line, slug)


class TheNote(unittest.TestCase):
    def test_the_method_note_says_it(self):
        n = src("docs", "methods", "grid_network.md")
        at = n.index("## The method from each panel (chain 091, 24 October 2026)")
        part = n[at:n.index("## Not here", at)]
        for w in ("Decisions (session 1184):", "`GRID_METHOD`", "`headingSlugs`", "`site/scripts/test-grid-methods.mjs`", "\"Who supplies a grid (session 68)\"",
                  "\"The large tables, keyed whole (session 1168)\"", "needed no change"):
            self.assertIn(w, part, w)

    def test_no_em_dash(self):
        for parts in (("site", "lib", "gridAnchors.ts"), ("docs", "methods", "grid_network.md"), ("site", "scripts", "check-methods.mjs"),
                      ("site", "scripts", "test-grid-methods.mjs"), ("site", "scripts", "test-grid-files.mjs"), ("site", "components", "grid", "PanelMethod.tsx"),
                      ("tests", "test_session1184.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
