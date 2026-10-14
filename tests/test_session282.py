"""Session 282: the finish pass of the Infrastructure and Analysis pages.

Energy Research Warehouse (ERW), the daytime chain of 14 October 2026. What is held here, each a fix that needed no
ruling:
- /api/download refuses a table held for a license on the day, as /data already hides its link;
- the severance calculator: an empty price gives no result (not a price of 0), and a Reset puts every input back;
- a "Reset the filters" button on /datacenters, /deals, the companies tab and /policy's list of every action;
- two stale sentences of /deals made true; the method links of /contracts;
- two method notes say what the code does (the lease tab's address, the thesis table's name).
Nothing here sets the environment, reads a table or makes a request.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheDownloadHoldsWhatDataHolds(unittest.TestCase):
    def test_a_held_table_is_refused(self):
        route = src("site", "app", "api", "download", "route.ts")
        self.assertIn('import { licenseNeeded, licensePublishers } from "@/lib/license";', route)
        guard = "if (licenseNeeded(table)) return text("
        self.assertIn(guard, route)
        self.assertLess(route.index(guard), route.index("const lim = await limited("))    # before any read
        self.assertIn("licenseNeeded(r.table_name) ? (", src("site", "app", "data", "page.tsx"))  # the same rule


class Resets(unittest.TestCase):
    def test_each_filter_bar_has_one(self):
        for parts, words in ((("site", "app", "datacenters", "DatacentersTable.tsx"), 'setCountry(""); setState(""); setStatus(""); setOperator(""); setKind(""); setMinMw("");'),
                             (("site", "app", "deals", "DealsTable.tsx"), 'setType(""); setTech(""); setState(""); setAi(""); setStatus(""); setFrom(""); setTo("");'),
                             (("site", "app", "companies", "CompaniesTable.tsx"), 'setSector(""); setNiche(""); setStage(""); setState(""); setMinConf("0");'),
                             (("site", "app", "policy", "PolicyTable.tsx"), 'setTag(""); setMinSig("5"); setFrom("");')):
            s = src(*parts)
            self.assertIn(words, s, parts)
            self.assertIn(">Reset the filters</button>", s, parts)

    def test_the_calculator(self):
        calc = src("site", "app", "severance", "Calculator.tsx")
        self.assertIn('if (price === "") return null;', calc)
        self.assertIn('setState("TX"); setProduct("oil"); setVolume(1000);', calc)
        self.assertIn(">Reset to the defaults</button>", calc)


class WordsAndLinks(unittest.TestCase):
    def test_deals(self):
        page = src("site", "app", "deals", "page.tsx")
        self.assertNotIn("2026-09-23, so the table starts there", page)
        self.assertIn("{ca.withPrice ? <>Only {whole(ca.withPrice)} of the deals held state a price per MWh", src("site", "app", "deals", "v2", "view.tsx"))

    def test_method_links_and_notes(self):
        contracts = src("site", "app", "contracts", "page.tsx")
        for slug in ("ferc_eqr_contracts", "eqr_buyers", "eqr_terms"):
            self.assertIn(f'<Link href="/data/methods/{slug}">', contracts)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", f"{slug}.md")), slug)
        self.assertIn("`/severance?tab=lease`", src("docs", "methods", "severance.md"))
        self.assertIn("`thesis_runs`", src("docs", "methods", "thesis.md"))


if __name__ == "__main__":
    unittest.main()
