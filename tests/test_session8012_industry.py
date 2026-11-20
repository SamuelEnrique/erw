"""Session 8012, chain 505 (part B1): the page "Energy use by industry" (/industry)."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


class ThePage(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "industry", "page.tsx")

    def test_it_reads_the_one_file(self):
        self.assertIn('import raw from "@/data/industry.json";', self.page)
        self.assertNotIn("supabase", self.page)

    def test_it_is_in_no_menu_and_in_review(self):
        self.assertNotIn('"/industry"', src("site", "lib", "pages.ts"))
        self.assertNotIn('"/industry"', src("site", "lib", "release.ts"))   # a path with no line is in review

    def test_two_of_each_side_by_side(self):
        for name in ('name="a"', 'name="b"', 'name="sa"', 'name="sb"', 'name="ca"', 'name="cb"'):
            self.assertIn(name, self.page)

    def test_no_em_dash(self):
        for p in (("site", "app", "industry", "page.tsx"), ("site", "app", "industry", "Decisions.tsx"), ("site", "lib", "industry.ts")):
            self.assertNotIn(chr(0x2014), src(*p))


class TheDecisions(unittest.TestCase):
    def test_the_fold_and_the_note_are_one_list(self):
        keys = re.findall(r'\{ key: "([a-z0-9-]+)", session: "', src("site", "app", "industry", "Decisions.tsx"))
        note = src("docs", "methods", "industry_page.md").split("### Decisions (session 8012)")[1]
        self.assertEqual(re.findall(r"^\| `([a-z0-9-]+)` \|", note, re.M), keys)
        self.assertEqual(len(keys), 8)


@unittest.skipUnless(NODE, "node is not on this machine")
class TheArithmetic(unittest.TestCase):
    def test_years_and_sums(self):
        d = node("import fs from 'node:fs'; import * as I from './lib/industry.ts';"
                 "const f = I.readIndustry(JSON.parse(fs.readFileSync('./data/industry.json', 'utf8')));"
                 "const y = I.lastWholeYear(f);"
                 "let s = 0; for (let m = 1; m <= 12; m++) s += I.monthValue(f, 'total', `${y}-${String(m).padStart(2, '0')}`);"
                 "console.log(JSON.stringify({ num: typeof f.states_annual.years[0], same: Math.abs(I.yearSum(f, 'total', y) - s) < 1e-6,"
                 " top: I.rankedIndustries(f, 'us')[0].naics, firstState: I.rankedStates(f, I.lastStateYear(f), 'total')[0].st,"
                 " noFuture: I.yearSum(f, 'total', 2100) }));")
        self.assertEqual(d["num"], "number")
        self.assertTrue(d["same"])
        self.assertEqual(d["top"], "325")
        self.assertEqual(d["firstState"], "TX")
        self.assertIsNone(d["noFuture"])

    def test_a_withheld_cell_stays_null(self):
        d = node("import fs from 'node:fs'; import * as I from './lib/industry.ts';"
                 "const f = I.readIndustry(JSON.parse(fs.readFileSync('./data/industry.json', 'utf8')));"
                 "const r = I.rankedIndustries(f, 'us').find((x) => x.naics === '325');"
                 "console.log(JSON.stringify({ resid: r.fuels.residual_fuel_oil ?? null }));")
        self.assertIsNone(d["resid"])


if __name__ == "__main__":
    unittest.main()
