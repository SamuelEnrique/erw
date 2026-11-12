"""Session 1878: the company database's and the capital view's faults of 12 November 2026
(docs/reviews/companies-faults-2026-11-11.md, rows 1 to 11 and 13 to 16), fixed in site/lib/companydb.ts,
site/lib/capitalview.ts, site/app/companies/page.tsx, site/app/companies/[id]/page.tsx, site/app/deals/capital/page.tsx
and site/components/tool/GroupedBars.tsx.

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written. The environment is
read, never set.

    PureFunctions  site/scripts/test-session1878.mjs (Node runs the two libraries with the site's alias loader): the
                   hover of a summed figure (row 2), one is one (3), the rules' words (4), the ids of a shared name (5),
                   the States cell and CN (6), the deals frame (7), the live series (8), the planned month (9), the
                   share's hover (10), the order (11), four colors (13), the absent type and the card (14), USD billion
                   under 50 million and the seller (15). Also site/scripts/test-companies.mjs, whose two lines this
                   session changed (the query's order, the plural in the index CSV).
    TheFiles       every rule of the committed index (site/data/companies/index.json) has its words (row 4).
    TheView        the pages, read from their source (this session does not build): each wrapped in <Brand> with no
                   colored header band (row 1), each fixed row drawn as the functions give it, every data-n key kept,
                   the total line with no sum across types (16).

    python -m pytest tests/test_session1878.py
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
LOADER = ["--import", "./scripts/alias-register.mjs"]
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
INDEX = ("site", "app", "companies", "page.tsx")
COMPANY = ("site", "app", "companies", "[id]", "page.tsx")
CAPITAL = ("site", "app", "deals", "capital", "page.tsx")
MINE = (
    INDEX, COMPANY, CAPITAL, ("site", "lib", "companydb.ts"), ("site", "lib", "capitalview.ts"),
    ("site", "components", "tool", "GroupedBars.tsx"), ("site", "scripts", "test-session1878.mjs"),
    ("site", "scripts", "test-companies.mjs"), ("tests", "test_session1878.py"),
)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class PureFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, *LOADER, "scripts/test-session1878.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_the_node_tests_pass(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1000:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2), self.out[-500:])

    def test_each_fixed_row_has_its_node_tests(self):
        for row in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15):
            self.assertRegex(self.out, rf"(?m)^ok   row {row}:", f"row {row} has a passing node test")

    def test_the_older_company_tests_still_pass(self):
        r = subprocess.run([NODE, *LOADER, "scripts/test-companies.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-1000:])
        self.assertIn("10 tests passed", r.stdout)


@unittest.skipUnless(os.path.exists(os.path.join(SITE, "data", "companies", "index.json")), "site/data/companies is not built")
class TheFiles(unittest.TestCase):
    def test_every_rule_of_the_index_has_its_words(self):
        with open(os.path.join(SITE, "data", "companies", "index.json"), encoding="utf-8") as f:
            rules = json.load(f)["rules"]
        lib = src("site", "lib", "companydb.ts")
        block = lib[lib.index("export const RULE_WORDS"):]
        block = block[:block.index("};")]
        for r in rules:
            self.assertRegex(block, rf"\b{re.escape(r)}: \"[^\"]+\"", r)


class TheView(unittest.TestCase):
    def test_row_1_every_page_in_the_brand_with_no_band(self):
        for page in (INDEX, COMPANY, CAPITAL):
            s = src(*page)
            self.assertIn('import { Brand } from "@/components/Brand";', s, page)
            self.assertEqual(s.count("<Brand>"), s.count("</Brand>"), page)
            self.assertGreaterEqual(s.count("<Brand>"), 2, page)   # the page and its other branch (unread file, or the hold)
            self.assertEqual(s.count("<ToolPage>"), s.count("<Brand>"), page)
            self.assertNotIn("bg-accent text-white", s, page)

    def test_rows_2_to_10_the_company_page(self):
        s = src(*COMPANY)
        self.assertIn("basisOf(col, t, links)", s)                               # 2
        self.assertIn("leadRows(links.length, byTable.size", s)                  # 3
        self.assertIn('`Show its ${plural(rows.length, "row", "rows")}`', s)
        self.assertNotIn("rows, {rule}", s)                                      # 4
        self.assertIn("ruleWords(rule)", s)
        self.assertIn("ruleWords(r.rule)", s)
        self.assertIn("showDeals(c, dealsHeld) ? <ChartFrame", s)                # 7
        self.assertNotIn("No row of <code", s)
        self.assertIn("series={live.map(", s)                                    # 8
        self.assertIn("legend={live.map(", s)
        self.assertIn("seenLast(c.last_seen, ix.built)", s)                      # 9
        self.assertIn("planned generator&apos;s planned month", s)
        self.assertIn("title={shareTitle(k, c.fuel[k], f.plants_mw)}", s)        # 10

    def test_rows_5_6_11_the_index(self):
        s = src(*INDEX)
        self.assertIn("sharedNames(all)", s)                                     # 5, over every listed row, not the page
        self.assertIn("idTag(r.id).text", s)
        self.assertIn("title={statesCell(r.states).title || undefined}", s)      # 6
        self.assertIn("stateLabel(k, ix.states[k])", s)
        self.assertIn('aria-sort={q.sort === sort ? (sort === "name" ? "ascending" : "descending") : undefined}', s)   # 11
        self.assertIn('<input type="hidden" name="sort" value={q.sort} />', s)
        for k in ("name", "operating", "planned", "queue", "policy", "footprint"):
            self.assertIn(f'<Head sort="{k}"', s)
        self.assertIn('hrefOf("/companies/rows", { ...q, page: 1 })', s)        # the download keeps the order

    def test_rows_13_to_16_the_capital_view(self):
        s = src(*CAPITAL)
        self.assertIn("tone: toneOf(types.indexOf(t))", s)                       # 13
        self.assertIn('blue: "var(--chart-blue)"', src("site", "components", "tool", "GroupedBars.tsx"))
        self.assertIn("--chart-blue:", src("site", "app", "tokens.css"))
        self.assertIn("...quarterBars(q, shown, words)", s)                      # 14
        self.assertIn("g.cards?.[k] !== undefined ? { text: g.cards[k] }", src("site", "components", "tool", "GroupedBars.tsx"))
        self.assertIn("{named(d.seller)}", s)                                    # 15
        self.assertNotIn("const bn =", s)
        self.assertNotIn("summing USD", s)                                       # 16
        self.assertNotIn('k="total|usd"', s)

    def test_every_key_kept(self):
        c = src(*COMPANY)
        for key in ("data-n={`company_directory|${c.entity_id}|${col}`}", "data-n={`company_links|${r.link}|mw`}", "data-n={`company_links|${r.link}|usd`}"):
            self.assertIn(key, c)
        self.assertIn("data-n={`company_directory|company:${id}|${col}`}", src(*INDEX))
        k = src(*CAPITAL)
        for key in ('data-n="capital|n_rows"', "data-n={`capital|${k}`}", 'k="total|rows"', 'k="total|usd_rows"', 'k="total|no_usd"', "k={`${id}|usd`}", "k={`deal|${d.event_id}|usd`}"):
            self.assertIn(key, k)

    def test_no_dash(self):
        for parts in MINE:
            s = src(*parts)
            self.assertNotIn(EM_DASH, s, parts)
            self.assertNotIn(EN_DASH, s, parts)


if __name__ == "__main__":
    unittest.main()
