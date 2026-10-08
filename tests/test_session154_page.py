"""Session 154, the page half: "Rules in motion" in the section "How soon" of /cost-of-power (in review).

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written anywhere.

    PureFunctions  site/scripts/test-rules.mjs: the grid an address names, the rows shown, their order, the fold, the
                   words of every hover (Node runs site/lib/rules.ts as it is). Its rows are made up and marked so;
                   where site/data/datacenter/rules.json is on the machine it also reads the real file.
    ThePage        the page's rules, read from its source: in review; the block stands in "How soon" after its table;
                   it reads one site file and nothing from the database, and calls no model; MISO's words are the
                   page's own and its hover is the site's; the shared tool components and the pages open to visitors
                   import nothing of it; no em dash; the checks name it.
    TheFile        where site/data/datacenter/rules.json is on the machine: it is a rules file of the contract's shape;
                   MISO shows no row; every row the block shows has a day or none, a source address, and a read that is
                   a model's or absent; no municipal word; no made-up row.
On the built site: node site/scripts/check-datacenter.mjs <base>.

    python -m unittest tests.test_session154_page
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
RULES = os.path.join(SITE, "data", "datacenter", "rules.json")
MINE = (
    ("site", "app", "cost-of-power", "RulesInMotion.tsx"), ("site", "lib", "rules.ts"), ("site", "lib", "rulesdata.ts"),
    ("site", "scripts", "test-rules.mjs"), ("site", "scripts", "check-datacenter.mjs"), ("tests", "test_session154_page.py"),
)
GRIDS = ["ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"]
EM_DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def sources_under(*parts):
    out = []
    top = os.path.join(ROOT, *parts)
    for folder, _, names in os.walk(top):
        for n in names:
            if n.endswith((".ts", ".tsx")):
                out.append(os.path.join(folder, n))
    return out


@unittest.skipUnless(NODE, "node is not installed")
class PureFunctions(unittest.TestCase):
    def test_the_node_tests_pass(self):
        r = subprocess.run([NODE, "scripts/test-rules.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"all \d+ passed")
        self.assertNotIn("FAIL", r.stdout)

    def test_its_rows_are_marked_made_up(self):
        t = src("site", "scripts", "test-rules.mjs")
        self.assertIn("THE ROWS BELOW ARE MADE UP FOR THIS TEST", t)
        self.assertIn("example.invalid", t)            # no address of a real regulator stands in a made-up row


class ThePage(unittest.TestCase):
    def test_in_review(self):
        self.assertRegex(src("site", "lib", "release.ts"), r'"/cost-of-power": "review"')

    def test_the_block_stands_in_how_soon_after_its_table(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        start = page.index('<ToolSection title="How soon" id="soon">')
        end = page.index("</ToolSection>", start)
        section = page[start:end]
        self.assertEqual(page.count("<RulesInMotion "), 1)
        self.assertIn("<RulesInMotion ", section)
        self.assertLess(section.index("<ToolTable "), section.index("<RulesInMotion "))
        self.assertLess(section.rindex('key: "waitload"'), section.index("<RulesInMotion "))   # the table's last row is still its last
        for key in ("q", "wait", "done", "ll", "line", "waitload"):                               # nothing the section showed is dropped
            self.assertIn('{ key: "%s", cells:' % key, section)

    def test_one_site_file_and_nothing_else(self):
        comp, data, lib = src("site", "app", "cost-of-power", "RulesInMotion.tsx"), src("site", "lib", "rulesdata.ts"), src("site", "lib", "rules.ts")
        self.assertEqual(re.findall(r'"([a-z_]+\.json)"', data), ["rules.json"])
        self.assertIn('path.join(process.cwd(), "data", "datacenter", "rules.json")', data)
        self.assertNotRegex(lib, r"^\s*import\s", "lib/rules.ts imports nothing: Node runs it as it is")
        for name, t in (("RulesInMotion.tsx", comp), ("rulesdata.ts", data), ("rules.ts", lib)):
            self.assertNotRegex(t, r"supabase|fetch\(|anthropic|/api/", name)           # no table read, no request, no model
            self.assertNotIn('"use client"', t, name)
        # the folder is already in the page's server trace
        self.assertIn('"/cost-of-power": ["./data/datacenter/*.json"]', src("site", "next.config.ts"))

    def test_miso_is_the_pages_own_words_with_the_sites_hover(self):
        lib = src("site", "lib", "rules.ts")
        words = json.loads(src("site", "data", "datacenter", "index.json"))["blank"]["miso"]["words"]
        self.assertEqual(words, "paused while terms are reviewed")
        self.assertIn('export const PAUSED_WORDS = "%s";' % words, lib)
        said = "MISO's terms forbid automated access to its site; its pulls are paused."
        self.assertIn(said, src("site", "components", "mix", "views.tsx"))
        self.assertIn('export const PAUSE_WHY = "%s' % said, lib)

    def test_no_live_page_and_no_shared_component_takes_anything_of_it(self):
        took = re.compile(r"RulesInMotion|@/lib/rules|lib/rulesdata|Rules in motion")
        for parts in (("site", "app", "cost-of-power", "battery"), ("site", "app", "network"), ("site", "app", "storage"), ("site", "components", "tool")):
            for f in sources_under(*parts):
                with open(f, encoding="utf-8") as fh:
                    self.assertIsNone(took.search(fh.read()), f)
        for parts in (("site", "app", "cost-of-power", "Tabs.tsx"), ("site", "lib", "pages.ts"), ("site", "lib", "supabase.ts")):
            self.assertIsNone(took.search(src(*parts)), parts[-1])

    def test_no_em_dash(self):
        for parts in MINE + (("site", "app", "cost-of-power", "page.tsx"), ("site", "scripts", "check-routes.mjs")):
            self.assertNotIn(EM_DASH, src(*parts), parts[-1])

    def test_the_checks_name_it(self):
        check = src("site", "scripts", "check-datacenter.mjs")
        for said in ("Rules in motion", "data-rules-paused", "MUNICIPAL", "docs/methods/datacenter_cost.md", "Input.dispatchKeyEvent"):
            self.assertIn(said, check)
        routes = src("site", "scripts", "check-routes.mjs")
        self.assertIn('"/cost-of-power?grid=pjm"', routes)
        self.assertIn('"/cost-of-power?grid=miso"', routes)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_words_the_owner_fixed(self):
        got = node("import * as R from './lib/rules.ts';"
                   "console.log(JSON.stringify({ grids: R.RULE_GRIDS, shown: R.SHOWN, paused: R.blockOf(null, 'miso'), none: R.NO_READ, municipal: R.MUNICIPAL, pjm: R.rulesGrid('pjm', 'ercot') }));")
        self.assertEqual(got["grids"], GRIDS)
        self.assertEqual(got["shown"], 8)
        self.assertEqual(got["none"], "no read yet")
        self.assertEqual(got["pjm"], "pjm")
        self.assertEqual(got["municipal"], ["zoning", "permit", "city council", "county board"])
        self.assertEqual((got["paused"]["state"], got["paused"]["words"], got["paused"]["rows"], got["paused"]["federal"]), ("paused", "paused while terms are reviewed", [], []))


@unittest.skipUnless(os.path.exists(RULES), "site/data/datacenter/rules.json is not on this machine")
class TheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RULES, encoding="utf-8") as f:
            cls.text = f.read()
        cls.file = json.loads(cls.text)

    def test_the_contract(self):
        f = self.file
        for key in ("built_at_utc", "window_months", "sources", "grids", "federal_all_grids"):
            self.assertIn(key, f)
        self.assertIsInstance(f["grids"], dict)
        self.assertIsInstance(f["federal_all_grids"], list)
        self.assertEqual(f["grids"].get("miso", {}).get("state"), "paused")
        self.assertEqual(f["grids"]["miso"].get("rows", []), [])
        for g, entry in f["grids"].items():
            self.assertIn(g, GRIDS)
            self.assertIn(entry.get("state"), ("shown", "none", "paused"), g)

    def test_no_made_up_row(self):
        self.assertNotRegex(self.text, r"(?i)made[- ]up|example\.invalid|example\.com|lorem ipsum")

    @unittest.skipUnless(NODE, "node is not installed")
    def test_what_the_block_shows(self):
        got = node("import fs from 'node:fs'; import * as R from './lib/rules.ts';"
                   "const f = R.fileOf(JSON.parse(fs.readFileSync('data/datacenter/rules.json', 'utf8')));"
                   "const out = {};"
                   "for (const g of R.RULE_GRIDS) { const b = R.blockOf(f, g); const rows = [...b.rows, ...b.federal];"
                   "  out[g] = { state: b.state, own: b.rows.length, federal: b.federal.length, dropped: b.dropped.length,"
                   "    days: [b.rows, b.federal].map((l) => l.map((r) => (R.dayWords(r.date) ? r.date : ''))),"
                   "    links: rows.every((r) => R.linkOf(r) === r.url), municipal: rows.map((r) => R.municipalWord(R.wordsOf(r))).filter(Boolean),"
                   "    reads: rows.every((r) => { const x = R.readOf(r); return x.line === null || (r.read_by === 'model' && x.line === r.read.trim()); }),"
                   "    status: rows.every((r) => R.statusOf(r).words.length > 0), tips: rows.every((r) => !r.sentence || R.docketTip(r).includes('\"' + r.sentence.trim() + '\"')) }; }"
                   "console.log(JSON.stringify(out));")
        self.assertEqual(sorted(got), sorted(GRIDS))
        self.assertEqual((got["miso"]["state"], got["miso"]["own"], got["miso"]["federal"]), ("paused", 0, 0))
        for g, b in got.items():
            self.assertTrue(b["links"] and b["reads"] and b["status"] and b["tips"], g)
            self.assertEqual(b["municipal"], [], g)
            for days in b["days"]:                         # newest first, a row with no day last
                dated = [d for d in days if d]
                self.assertEqual(dated, sorted(dated, reverse=True), g)
                self.assertEqual(days[:len(dated)], dated, g)


if __name__ == "__main__":
    unittest.main()
