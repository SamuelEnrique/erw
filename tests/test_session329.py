"""Session 329 (the chain of 20 October 2026, night): /datacenters (the tracker) and /deals (its tabs) finished to the
five tools' standard, lighter. The companies tab's confidence is a checked number (a key of its own in check-values),
each page offers its public tables (session 328's shared line), the deals have their method note and the tracker's
note says what the page draws today. Energy Research Warehouse (ERW)."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCompaniesNumbers(unittest.TestCase):
    def test_the_confidence_is_read_again_by_its_key(self):
        t = src("site", "app", "companies", "CompaniesTable.tsx")
        self.assertIn('<Num check={`entity|energy_companies|${r.entity_id}|confidence`} raw={Number(r.confidence)}>{r.confidence}</Num>', t)
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "entity") {', cv)
        self.assertIn('const r = (await q("entities", { select: col, table_name: `eq.${table}`, entity_id: `eq.${id}` }))[0];', cv)
        num = src("site", "components", "Num.tsx")
        self.assertIn('else if (head === "event" || head === "entity") table = p[1] ?? "";', num)   # a held table is held by this key too


class TheDownloadsAndNotes(unittest.TestCase):
    def test_each_page_offers_its_tables(self):
        deals = src("site", "app", "deals", "page.tsx")
        self.assertIn('<TableDownloads tables={tab === "companies" ? ["energy_companies", "energy_deals"] : ["energy_deals", "news_stories"]} />', deals)
        dc = src("site", "app", "datacenters", "page.tsx")
        self.assertIn('<TableDownloads tables={["datacenter_facilities", "datacenter_operator_sites", "datacenter_projects", "ercot_large_load_status"]} />', dc)

    def test_the_method_links_reach_notes_that_exist(self):
        for page, slug in ((("site", "app", "deals", "page.tsx"), "energy_deals"), (("site", "app", "deals", "v2", "view.tsx"), "energy_deals"),
                           (("site", "app", "companies", "view.tsx"), "energy_deals"), (("site", "app", "companies", "view.tsx"), "thesis"),
                           (("site", "app", "datacenters", "page.tsx"), "datacenter_facilities")):
            self.assertIn(f'href="/data/methods/{slug}"', src(*page), (page, slug))
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", f"{slug}.md")), slug)

    def test_the_deals_note_says_what_the_builders_do(self):
        note = src("docs", "methods", "energy_deals.md")
        ex = src("warehouse", "deals", "extract.py")
        self.assertIn('SECTORS_IN = ["deal", "ppa", "capital", "nuclear", "generation", "datacenter_power", "lng", "oil", "gas"]', ex)
        self.assertIn("deal, ppa, capital, nuclear, generation, datacenter_power, lng, oil or gas", note)
        self.assertIn("significance 5 or more", ex)
        self.assertIn("significance of 5 or more", note)
        self.assertIn("20 per independent source, up to 3", src("warehouse", "companies", "seed_from_deals.py"))
        self.assertIn("20 a\n  source, up to three", note)
        self.assertIn("## The tracker as it stands (session 329, 20 October 2026)", src("docs", "methods", "datacenter_facilities.md"))


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "app", "companies", "CompaniesTable.tsx"), ("site", "app", "companies", "view.tsx"), ("site", "app", "deals", "page.tsx"),
                      ("site", "app", "deals", "v2", "view.tsx"), ("site", "app", "datacenters", "page.tsx"), ("site", "scripts", "check-values.mjs"),
                      ("site", "components", "Num.tsx"), ("docs", "methods", "energy_deals.md"), ("docs", "methods", "datacenter_facilities.md"),
                      ("tests", "test_session329.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
