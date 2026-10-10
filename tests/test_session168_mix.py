"""Session 168, part B: "Select grids" on every view of /mix.

The owner's instruction of 8 October 2026: show the control on every view; where a view can use the choice, use it;
where it cannot, show it greyed with a hover saying why; nothing else on /mix changes. The address and its helpers are
tested by site/scripts/test-mix.mjs (run here when node is present); the page by site/scripts/check-mix.mjs against a
served build. Asserts on file contents and behaviour, never on a branch.
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class SelectGridsOnEveryView(unittest.TestCase):
    def test_the_control_stands_on_every_view(self):
        page = src("site", "app", "mix", "page.tsx")
        self.assertIn("      <Controls c={c} />", page)                       # the opening view too
        self.assertNotIn('c.view === "now" ? null : <Controls', page)
        self.assertEqual(page.count('<Chips label="Select grids"'), 3)            # compare, filter, greyed
        self.assertIn("title: NO_GRID_CHOICE", page)

    def test_each_view_says_what_it_does_with_the_choice(self):
        lib = src("site", "lib", "mixpage.ts")
        self.assertIn('export const gridUse = (view: View): "compare" | "filter" | "none" => (view === "now" || view === "forecast" ? "filter" : view === "history" ? "none" : "compare");', lib)
        self.assertIn("This view is by state: EIA's record since 2001 is not kept by grid.", lib)

    def test_the_address_tests(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(SITE, "node_modules")):
            self.skipTest("node or the site's modules are absent: node --import ./scripts/alias-register.mjs scripts/test-mix.mjs")
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-mix.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-2000:])

    def test_no_em_dash(self):
        for parts in (("site", "app", "mix", "page.tsx"), ("site", "lib", "mixpage.ts"), ("site", "components", "mix", "views.tsx"), ("site", "scripts", "test-mix.mjs"),
                      ("tests", "test_session168_mix.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
