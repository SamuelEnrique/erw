"""Session 333 (the chain of 20 October 2026, night): /supply and /contracts finished to the five tools' standard,
lighter. /supply offers the tables its file's sources name; a page none of whose tables is in the site's live catalogue
says so and names Redivis; /contracts, whose table is internal, offers none and its note says why. Energy Research
Warehouse (ERW)."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheSupplyDownloads(unittest.TestCase):
    def test_the_list_is_read_from_the_files_sources(self):
        page = src("site", "app", "supply", "page.tsx")
        self.assertIn("const TABLES = [...new Set((file.sources as string[]).flatMap((s) => [...s.matchAll(/\\(([a-z0-9]+(?:_[a-z0-9]+)+)\\)/g)].map((m) => m[1])))];", page)
        self.assertIn("<TableDownloads tables={TABLES} />", page)
        sources = json.loads(src("site", "data", "supply.json"))["sources"]
        found = sorted({m for s in sources for m in re.findall(r"\(([a-z0-9]+(?:_[a-z0-9]+)+)\)", s)})
        self.assertEqual(found, ["cftc_cot_positions", "eia_basin_production_monthly", "eia_gas_storage_weekly", "eia_gas_trade_monthly", "eia_petroleum_supply_weekly"])


class TheLineWithNoTable(unittest.TestCase):
    def test_a_page_with_no_catalogued_table_names_redivis_and_a_failed_read_names_data(self):
        c = src("site", "components", "tool", "TableDownloads.tsx")
        self.assertIn('<span data-not-held="catalogue">this page&apos;s tables are not in the site&apos;s live set; every table is on <a href={site.redivis.url}>Redivis</a> (version 1 pending release)</span>', c)
        self.assertIn('{!cat.ok ? (\n        <>every public table is on <Link href="/data">Data and methods</Link></>', c)


class TheContracts(unittest.TestCase):
    def test_the_note_says_why_the_page_offers_no_download(self):
        note = src("docs", "methods", "ferc_eqr_contracts.md")
        self.assertIn("## The page as it stands (session 333, 20 October 2026)", note)
        self.assertIn("| `ferc_eqr_contracts` | source | internal |", note)
        self.assertNotIn("TableDownloads", src("site", "app", "contracts", "page.tsx"))
        self.assertIn("## The page as it stands (session 333, 20 October 2026)", src("docs", "methods", "supply_and_trade.md"))


class TheContractsResets(unittest.TestCase):
    def test_each_panel_resets_to_the_defaults_the_library_sets(self):
        page = src("site", "app", "contracts", "page.tsx")
        self.assertEqual(page.count('<InputPanel title="Choose" reset={{'), 3)
        lib = src("site", "lib", "contracts.ts")
        self.assertIn("const quarter = q.q && held.includes(q.q) ? q.q : held[0] ?? null;", lib)
        self.assertIn("const product = PRODUCTS.find((p) => p.slug === q.product) ?? PRODUCTS[0];", lib)
        self.assertIn(".sort((a, b) => b.quarter.localeCompare(a.quarter));", lib)    # newest first: held[0] is the newest


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "app", "supply", "page.tsx"), ("site", "components", "tool", "TableDownloads.tsx"), ("site", "scripts", "check-table-downloads.mjs"),
                      ("docs", "methods", "supply_and_trade.md"), ("docs", "methods", "ferc_eqr_contracts.md"), ("tests", "test_session333.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
