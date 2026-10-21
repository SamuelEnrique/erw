"""Session 419 (the chain of 21 October 2026, day, 021, run on portable-laptop): three faults of session 401's list
(docs/reviews/tooling-pass-2026-10-20.md) that need no ruling. The research rule's percentile is an ordinal ("1st",
"22nd", never "1th" or "22th"); the carbon note of the load tool names the year of the page's own twelve months, not
the reader's clock's; a "#financing" link opens the fold it lands on. Energy Research Warehouse (ERW)."""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
LOADER = ["--import", "./scripts/alias-register.mjs"]
DASHES = (chr(0x2014), chr(0x2013))
NEW = [("site", "lib", "ordinal.ts"), ("site", "lib", "foldhash.ts"), ("site", "components", "tool", "OpenFoldOnHash.tsx"),
       ("site", "scripts", "test-session419.mjs"), ("tests", "test_session419.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePureFunctions(unittest.TestCase):
    @unittest.skipUnless(NODE and os.path.isdir(os.path.join(SITE, "node_modules")), "node or the site's packages are not on this machine")
    def test_the_node_test_passes(self):
        r = subprocess.run([NODE, *LOADER, "scripts/test-session419.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertRegex(r.stdout, r"(\d+) of \1 passed")


class TheWiring(unittest.TestCase):
    def test_the_research_view_writes_the_ordinal(self):
        t = src("site", "app", "research", "view.tsx")
        self.assertIn('import { ordinal } from "@/lib/ordinal";', t)
        self.assertIn("({ordinal(c.percentile)} percentile)", t)
        self.assertNotRegex(t, r"\}th\b")

    def test_the_carbon_note_reads_no_clock(self):
        t = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        self.assertNotIn("new Date(", t)
        self.assertNotIn("getUTCFullYear", t)
        self.assertIn("const thisYear = yearOfThrough(c.through);", t)
        a = src("site", "lib", "datacenter", "answers.ts")
        self.assertIn("through?: string | null;", a)
        self.assertIn("through: l12.at(-1) ?? null };", a)

    def test_the_battery_page_opens_the_fold_its_links_name(self):
        t = src("site", "app", "cost-of-power", "battery", "Settings.tsx")
        self.assertIn('import { OpenFoldOnHash } from "@/components/tool/OpenFoldOnHash";', t)
        self.assertEqual(t.count("<OpenFoldOnHash />"), 1)
        self.assertLess(t.index("<OpenFoldOnHash />"), t.index('<div id="financing">'))
        self.assertIn('<SettingsFold id="financing" title="Financing" open={false}', t)  # default-neutral: the fold still starts closed
        c = src("site", "components", "tool", "OpenFoldOnHash.tsx")
        self.assertTrue(c.startswith('"use client";'))
        for ev in ('addEventListener("hashchange"', 'removeEventListener("hashchange"', 'addEventListener("click"'):
            self.assertIn(ev, c)

    def test_no_dash_in_what_this_session_wrote(self):
        for p in NEW:
            t = src(*p)
            for d in DASHES:
                self.assertNotIn(d, t, os.path.join(*p))


if __name__ == "__main__":
    unittest.main()
