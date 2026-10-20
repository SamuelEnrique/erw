"""Session 239: the merges, the menu and the old addresses.

The owner's instruction of 12 October 2026 (docs/reviews/erw-review-2026-10-12.md, sections B and C): six pages hold
what thirteen held, each as tabs of one address; every old address redirects to the tab it became; the menu follows;
nothing a page showed is dropped.

  TheTabs        lib/tabs.ts: the six pages, their tabs and their addresses; one tabs component, one brand rule
  ThePages       each surviving page takes the brand, draws the shared tabs and one view; each folded page file is a view
  TheAddresses   next.config.ts redirects every old address to its tab; no page file answers at an old address
  TheMenu        lib/pages.ts: the pages that became tabs left the menu; their tables are on the surviving page's line
  ThePromise     the lease tab: nothing is sent, said on the page, and no link prefetches on /severance
  TheChecks      the checks' lists name the new addresses and still name every old one
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = chr(0x2014)
APP = ("site", "app")


def path(*parts):
    return os.path.join(ROOT, *parts)


def src(*parts):
    with open(path(*parts), encoding="utf-8") as f:
        return f.read()


def code(text):
    """A source file without its comments, for a search of what is drawn."""
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", text)


# the surviving page, its parameter, its tabs in order, and the view file and component of each folded page
PAGES = {
    "/storage": ("tab", ["fleet", "buildout", "owners"], {"buildout": ("storage/buildout/view.tsx", "BuildoutView"), "owners": ("storage/owners/view.tsx", "OwnersView")}),
    "/severance": ("tab", ["calculator", "lease"], {"lease": ("severance/lease/view.tsx", "LeaseView")}),
    "/prices": ("tab", ["now", "ercot"], {"ercot": ("explorer/ercot-peak-premium/view.tsx", "PeakPremiumView")}),
    "/demand": ("view", ["metered", "weather", "consumption"], {"consumption": ("consumption/view.tsx", "ConsumptionView")}),
    "/deals": ("tab", ["deals", "tracker", "companies"], {"tracker": ("deals/v2/view.tsx", "TrackerView"), "companies": ("companies/view.tsx", "CompaniesView")}),
    "/map": ("tab", ["projects", "resources", "queues"], {"resources": ("resources/view.tsx", "ResourcesView"), "queues": ("map/QueuesView.tsx", "QueuesView")}),  # session 349: Queues
}
# every old address and the tab it became
MERGED = {
    "/storage/buildout": "/storage?tab=buildout", "/storage/owners": "/storage?tab=owners", "/severance/lease": "/severance?tab=lease",
    "/explorer/ercot-peak-premium": "/prices?tab=ercot", "/consumption": "/demand?view=consumption", "/deals/v2": "/deals?tab=tracker",
    "/companies": "/deals?tab=companies", "/resources": "/map?tab=resources",
}
# the versioned addresses of the owner's list, each with its one page (session 241: "/datacenters/v2" redirects too, now that /datacenters draws its blocks)
VERSIONED = {
    "/board/v3": "/board", "/board/v4": "/board", "/deals/v2": "/deals?tab=tracker", "/map/v2": "/map", "/network/v3": "/grid?view=network",
    "/curtailment/v2": "/curtailment", "/cost-of-power/seller/v2": "/cost-of-power/seller", "/seller/v2": "/cost-of-power/seller",
    "/datacenters/v2": "/datacenters",
}


def page_file(href):
    return src(*APP, href.strip("/"), "page.tsx")


class TheTabs(unittest.TestCase):
    def test_the_six_pages_and_their_tabs(self):
        t = src("site", "lib", "tabs.ts")
        for href, (param, tabs, _) in PAGES.items():
            line = next(l for l in t.splitlines() if l.strip().startswith(f'"{href}": {{ param:'))
            self.assertIn(f'param: "{param}"', line, href)
            self.assertEqual(re.findall(r'\["([a-z]+)", "', line), tabs, href)

    def test_the_old_addresses_are_named_with_their_tabs(self):
        t = src("site", "lib", "tabs.ts")
        for old, new in MERGED.items():
            self.assertIn(f'"{old}": "{new}"', t)

    def test_one_component_draws_the_tabs_of_all_six(self):
        c = src("site", "components", "tool", "Tabs.tsx")
        self.assertIn('aria-current={k === active ? "page" : undefined}', c)   # the tab in view is marked
        self.assertIn("data-tabs={page}", c)
        self.assertIn("href={tabHref(page, k)}", c)
        self.assertNotIn("SiteLink", code(c))   # plain anchors: never prefetched
        for href in PAGES:
            self.assertRegex(page_file(href), r'<Tabs page="%s" active=\{\w+\} />' % href, href)

    def test_the_brand_styles_the_tabs_by_one_rule(self):
        css = src("site", "app", "tokens.css")
        self.assertIn('.brand-a nav[aria-label="Cost of power"] a,\n.brand-a nav[data-tabs] a {', css.replace("\r\n", "\n"))
        self.assertIn('.brand-a nav[data-tabs] a[aria-current="page"] {', css)
        # no page writes a color, a font or a rule for its tabs
        for href in PAGES:
            self.assertNotRegex(code(page_file(href)), r"#[0-9A-Fa-f]{6}\b", href)


class ThePages(unittest.TestCase):
    def test_each_surviving_page_takes_the_brand_and_reads_its_tab_from_the_address(self):
        for href, (param, tabs, views) in PAGES.items():
            p = page_file(href)
            self.assertIn('import { Brand } from "@/components/Brand";', p, href)
            self.assertRegex(p, r"<Brand( noUsage)?>", href)
            self.assertIn("searchParams", p, href)
            for key, (_, component) in views.items():
                self.assertIn(f"<{component}", p, f"{href}: the {key} tab")

    def test_each_folded_page_is_a_view_and_no_page_file_answers_at_its_address(self):
        for href, (_, _, views) in PAGES.items():
            for key, (file, component) in views.items():
                self.assertTrue(os.path.exists(path(*APP, *file.split("/"))), file)
                self.assertFalse(os.path.exists(path(*APP, *file.replace("view.tsx", "page.tsx").split("/"))), f"{file}: the page file still answers")
                v = src(*APP, *file.split("/"))
                self.assertRegex(v, r"export (async )?function %s\(" % component, file)
                self.assertNotIn("export default", v, file)
                self.assertNotIn("<ToolPage>", code(v), f"{file}: the sheet is the surviving page's")

    def test_the_blocks_of_the_folded_pages_are_still_drawn(self):
        # one mark of each block the inventory lists (the session's report), in the file that draws it now
        blocks = {
            "storage/buildout/view.tsx": ["How much storage has been built", "Operating storage by year, by duration", "Storage against solar", "By grid", "How generators are assigned to a grid, and how many were not",
                                          "What EIA-860M covers and misses", "The newest month held", "data-summary", "<SourceLine tables={[TABLE]}"],
            "storage/owners/view.tsx": ["Who owns the batteries", "The largest owners, operating MW", "Operating: the largest owners", "Planned: the largest owners", "What an owner is here", "What is counted", "<SourceLine tables={[TABLE]}"],
            "severance/lease/view.tsx": ["Severance tax for a lease: every well, every month", "Your file stays on your computer.", "An estimate for education and planning, not tax advice.", "<LeaseTool rules={rules} prices={prices} />", "<Cite tables={[T]}"],
            "explorer/ercot-peak-premium/view.tsx": ["ERCOT peak premium", "<Explorer", "citeAnnual", "citeMonthly", "lastInput", "<AskErcotLink"],
            "consumption/view.tsx": ["Consumption by sector", '<Section title="United States"', '<Section title="Sector shares and growth, by state"', '<Section title="Where industrial and commercial load is growing fastest"',
                                     '<Section title="Industrial and commercial energy, all fuels (US)"', "series_esum|"],
            "deals/v2/view.tsx": ["The deals tracker", "data-deals-summary", "data-deals-stated", "Deals by month", "How a deal gets here", "Rows that were one deal", "What this does not tell you", '<SourceLine tables={["energy_deals"]}'],
            "companies/view.tsx": ["<h1 className=\"mb-1 text-3xl\">Companies</h1>", "<CompaniesTable", '<Cite tables={["energy_companies"]}', "a seed, not a census"],
            "resources/view.tsx": ["Where the resources are", "<ResourceMap layers={layers} groups={groups} manifestReason={reason} />", "data-method-note", "How the map is drawn", "data-method-missing", "data-method-overlays", "data-method-doc"],
        }
        for file, marks in blocks.items():
            v = src(*APP, *file.split("/"))
            for m in marks:
                self.assertIn(m, v, f"{file}: {m}")

    def test_a_company_is_a_filter_of_the_tracker(self):
        self.assertIn("`/deals?tab=tracker&party=${encodeURIComponent(r.name)}`", src(*APP, "companies", "CompaniesTable.tsx"))
        self.assertIn("`/deals?tab=companies#${companyAnchor(n)}`", src(*APP, "deals", "DealsTable.tsx"))
        self.assertIn('"/deals?tab=tracker"', src("site", "lib", "deals2.ts"))
        v = src(*APP, "deals", "v2", "view.tsx")
        self.assertIn('<form method="get" action="/deals"', v)
        self.assertIn('<input type="hidden" name="tab" value="tracker" />', v)

    def test_the_resource_map_keeps_its_tab_in_the_address_it_writes(self):
        m = src(*APP, "resources", "ResourceMap.tsx")
        self.assertIn('const TAB = "?tab=resources&";', m)
        self.assertIn('.replace("?", TAB)', m)
        self.assertIn('.some((k) => k !== "tab")', m)   # the tab alone is not a choice of the reader


class TheAddresses(unittest.TestCase):
    def setUp(self):
        self.config = src("site", "next.config.ts")

    def test_every_old_address_redirects_to_its_tab_for_good(self):
        for old, new in {**MERGED, **VERSIONED}.items():
            self.assertIn(f'{{ source: "{old}", destination: "{new}", permanent: true }}', self.config, old)

    def test_only_the_address_itself_is_redirected(self):
        # the resource map's files, the internal lease loader and the finder answer as before
        for sub in ("/resources/:", "/resources/layer", "/severance/lease/:", "/severance/finder", "/storage/:", "/deals/:"):
            self.assertNotIn(f'source: "{sub}', self.config, sub)
        for file in (("resources", "layer", "[name]", "route.ts"), ("resources", "overlay", "plants", "route.ts"), ("severance", "lease", "real", "page.tsx"), ("severance", "finder", "page.tsx")):
            self.assertTrue(os.path.exists(path(*APP, *file)), "/".join(file))

    def test_every_page_is_still_in_review(self):
        r = src("site", "lib", "release.ts")
        self.assertNotRegex(code(r).split("export function exempt")[0], r'"\s*:\s*"live"')
        for old in MERGED:
            self.assertRegex(r, r'"%s":\s*"review"' % re.escape(old), f"{old}: an address typed by hand still has a status")


class TheMenu(unittest.TestCase):
    def setUp(self):
        self.pages = src("site", "lib", "pages.ts")
        self.entries = dict(re.findall(r'\{ href: "([^"]+)", label: "[^"]+", line: "[^"]*", tables: "([^"]*)"', self.pages))

    def test_the_pages_that_became_tabs_left_the_menu(self):
        for old in MERGED:
            self.assertNotIn(old, self.entries, old)
            self.assertNotIn(f'"{old}"', code(self.pages), f"{old}: a related line still names it")
        for href in PAGES:
            self.assertIn(href, self.entries, href)

    def test_the_surviving_line_lists_the_tables_of_all_its_tabs(self):
        want = {
            "/storage": ["storage_capacity", "storage_daily_cycle", "eia930_all_storage", "storage_buildout_monthly", "storage_owners_monthly"],
            "/prices": ["latest_prices", "ercot_peak_premium_annual", "ercot_peak_premium_monthly"],
            "/demand": ["eia930_demand_growth", "eia930_demand_weather", "eia_retail_sales_monthly", "eia_sector_energy_consumption_monthly"],
            "/deals": ["energy_deals", "energy_companies"],
            "/map": ["energy_projects", "datacenter_facilities", "docs/methods/resources.md", "eia860m_operating_generators", "eia860m_planned_generators"],
            "/severance": ["site/data/severance_rules.json", "eia_fuel_spot_prices"],
        }
        for href, tables in want.items():
            for t in tables:
                self.assertIn(t, self.entries[href], f"{href}: {t}")

    def test_the_groups_of_the_merged_site(self):
        group = lambda label: re.search(r'label: "%s",\s*pages: \[(.*?)\n    \],' % label, self.pages, flags=re.S).group(1)
        hrefs = lambda label: re.findall(r'\{ href: "([^"]+)"', code(group(label)))
        self.assertEqual(hrefs("Infrastructure"), ["/map", "/datacenters", "/storage", "/deals"])
        self.assertEqual(hrefs("Economics"), ["/board", "/prices", "/supply", "/contracts", "/severance", "/impact"])   # Power contracts stays (the owner's ruling); session 288: the bill moved to Games; session 347: the economic impact tool
        self.assertIn("/thesis", hrefs("Analysis"))   # Thesis Builder stays (the owner's ruling)
        # session 288 (Samuel's ruling 14 of 14 October 2026): the battery game, the tour, the bill and the problem sets' index
        self.assertEqual(hrefs("Games"), ["/play/battery", "/tour", "/learn/bill", "/learn/problems", "/play/ev"])   # session 294: the EV game


class ThePromise(unittest.TestCase):
    def test_the_lease_tab_says_nothing_is_sent_and_the_page_is_never_counted(self):
        v = src(*APP, "severance", "lease", "view.tsx")
        self.assertIn("<strong>Your file stays on your computer.</strong>", v)
        self.assertIn("Nothing in it is sent to this site&apos;s server", v)
        self.assertIn("<Brand noUsage>", src(*APP, "severance", "page.tsx"))
        self.assertIn('"/severance"', re.search(r"export const QUIET = \[(.*?)\];", src("site", "lib", "usage.ts")).group(1))

    def test_no_link_prefetches_on_the_page_of_the_lease_tab(self):
        s = src("site", "components", "SiteLink.tsx")
        listed = re.search(r"export const NO_PREFETCH = \[(.*?)\];", s).group(1)
        self.assertIn('"/severance"', listed)        # the tab's address is /severance?tab=lease: the path is /severance
        self.assertIn('"/severance/lease"', listed)  # the old address and /severance/lease/real
        self.assertNotIn("next/link", src("site", "components", "tool", "Tabs.tsx"))
        self.assertIn('<Link href="/severance?tab=lease" prefetch={false}>', src(*APP, "severance", "page.tsx"))


class TheChecks(unittest.TestCase):
    def test_check_values_reads_the_tabs_and_drops_no_page(self):
        s = src("site", "scripts", "check-values.mjs")
        for new in ("/prices?tab=ercot", "/demand?view=consumption", "/storage?tab=buildout", "/storage?tab=buildout&grid=ercot&measure=mwh", "/storage?tab=buildout&grid=caiso",
                    "/storage?tab=owners", "/deals?tab=tracker", "/deals?tab=companies", "/severance?tab=lease", "/map?tab=resources"):
            self.assertIn(f'"{new}"', s, new)
        for kept in ('"/storage"', '"/prices"', '"/deals"', '"/map"'):
            self.assertIn(kept, s)

    def test_check_routes_asks_the_tabs_and_still_asks_every_old_address(self):
        s = src("site", "scripts", "check-routes.mjs")
        for old, new in MERGED.items():
            self.assertIn(f'"{old}"', s, old)
            if old != "/consumption":   # asked through its redirect until the baseline holds the view (the note in the list)
                self.assertIn(f'"{new}"', s, new)

    def test_the_browser_checks_open_the_new_addresses(self):
        self.assertIn("/storage?tab=buildout&grid=${grid.slug}&measure=${measure}", src("site", "scripts", "check-buildout.mjs"))
        self.assertIn("${base}/deals?tab=tracker", src("site", "scripts", "check-deals-v2.mjs"))
        r = src("site", "scripts", "check-resources.mjs")
        self.assertIn('get("/map?tab=resources")', r)
        self.assertNotIn("${base}/resources", r)
        self.assertIn("/resources/layer/", r)   # the files keep their addresses

    def test_no_em_dash_in_what_the_session_wrote(self):
        files = [("site", "lib", "tabs.ts"), ("site", "components", "tool", "Tabs.tsx"), ("site", "lib", "pages.ts"), ("site", "next.config.ts"), ("tests", "test_session239.py")]
        files += [(*APP, href.strip("/"), "page.tsx") for href in PAGES]
        files += [(*APP, *file.split("/")) for _, _, views in PAGES.values() for file, _ in views.values()]
        for f in files:
            self.assertNotIn(DASH, src(*f), "/".join(f))


if __name__ == "__main__":
    unittest.main()
