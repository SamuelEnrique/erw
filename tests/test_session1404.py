"""Session 1404 (chain 100): the Grid's source-text tests, sturdier.

Energy Research Warehouse (ERW).

Many tests/test_session*.py pin the Grid tool's source word for word. site/scripts/test-grid-render.mjs renders each
panel of /grid on the committed fixtures (site/scripts/grid-render-standin.mjs: the page called as Next calls it on the
server, its reads answered from committed real rows) and checks, a case a panel and a kind of grid, its name, its keys by
kind and count, its words as rendered, its held lines, its anchor, its method link and its files. A pinned python
assertion it covers keeps its assertion and carries, above it, the line

    # also covered by site/scripts/test-grid-render.mjs: <case name>

so a later session can retire the pin with the owner's leave. This test runs the node test and holds every such line to
a case of it, directly above an assertion.

    python -m unittest tests.test_session1404 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
TAG = "# also covered by site/scripts/test-grid-render.mjs: "
RENDER = ("site", "scripts", "test-grid-render.mjs")
STANDIN = ("site", "scripts", "grid-render-standin.mjs")
FILES = [RENDER, STANDIN, ("tests", "test_session1404.py"), ("archive", "sessions", "SESSION_1404_REPORT.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def cases():
    out = []
    for line in src(*RENDER).split("\n"):
        if line.startswith('  {"name": '):
            out.append(json.loads(line.strip().rstrip(",")))
    return out


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheCases(unittest.TestCase):
    def test_one_case_a_panel_and_a_kind_of_grid(self):
        cs = cases()
        self.assertGreaterEqual(len(cs), 60)
        names = [c["name"] for c in cs]
        self.assertEqual(len(names), len(set(names)))
        for c in cs:
            self.assertEqual(c["name"], f'{c["block"]} on /grid?{c["q"]}')
        kinds = {c["grid"] for c in cs}
        for k in ("an ISO with prices (ERCOT)", "CAISO", "a held grid (ISO-NE)", "the Lower 48"):
            self.assertIn(k, kinds)
        for fam in ("grid_network_", "balance_", "replay_", "grid_gravity_", "view_exchange", "gravityday", "grid_clean24_", "grid_cleanweek_",
                    "grid_mix_", "grid_hubprice_", "grid_scarcity_", "grid_caisoalert_", "grid_ercotnotice_", "held_", "mixview_stress", "grid_ask_"):
            self.assertTrue(any(c["block"].startswith(fam) for c in cs), fam)
        # a chain panel names its anchor and its method; a held grid's block says so
        for c in cs:
            if c["block"].startswith(("grid_network_", "balance_", "replay_", "grid_gravity_", "grid_clean24_", "grid_cleanweek_", "grid_mix_", "grid_scarcity_")):
                self.assertTrue(c["anchors"] and c["methods"], c["name"])
        self.assertTrue(any(c["held"] and c["grid"] == "a held grid (ISO-NE)" for c in cs))

    def test_the_render_reads_only_the_stand_in(self):
        s = src(*STANDIN)
        self.assertIn("throw new Error(`a request this test does not make: ${u.origin}`);", s)
        self.assertIn('const page = await import("../app/grid/page.tsx");', s)
        r = src(*RENDER)
        self.assertIn('const S = await import("./grid-render-standin.mjs");', r)
        self.assertIn("every panel family drawn on these pages has a case", r)


class TheComments(unittest.TestCase):
    def test_every_comment_names_a_case_and_sits_above_an_assertion(self):
        names = {c["name"] for c in cases()}
        seen, files = 0, set()
        tests = os.path.join(ROOT, "tests")
        for fn in sorted(os.listdir(tests)):
            if not fn.endswith(".py") or fn == "test_session1404.py":
                continue
            lines = src("tests", fn).split("\n")
            for i, line in enumerate(lines):
                if TAG not in line:
                    continue
                seen += 1
                files.add(fn)
                self.assertTrue(line.strip().startswith(TAG), f"{fn}:{i + 1} is not a comment line of its own")
                self.assertIn(line.strip()[len(TAG):], names, f"{fn}:{i + 1} names no case of test-grid-render.mjs")
                self.assertIn("self.assert", lines[i + 1], f"{fn}:{i + 1}: the line under it is not an assertion")
                self.assertNotIn(TAG, lines[i - 1], f"{fn}:{i + 1}: two such lines over one assertion")
        # session 1404 wrote 63 of them in 19 files; a pin retired with the owner's leave takes its line with it
        self.assertGreaterEqual(seen, 50)
        self.assertGreaterEqual(len(files), 15)

    def test_no_em_dash(self):
        for parts in FILES:
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE and MODULES, "node and site/node_modules (typescript, react) are needed")
class TheNodeTest(unittest.TestCase):
    def test_the_render_test_passes(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-render.mjs"],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", env=node_env(), timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertRegex(r.stdout, r"every case holds \(\d+ cases\)")
        ran = set(re.findall(r"^ok   (.+?) \(", r.stdout, re.M))
        for c in cases():
            self.assertIn(c["name"], ran)


if __name__ == "__main__":
    unittest.main()
