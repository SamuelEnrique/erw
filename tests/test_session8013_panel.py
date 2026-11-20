"""Session 8013 (chain 505, part C): the authority's own facts in the Grid tool's panel.

The panel of app/network/Network.tsx shows components/grid/AuthorityFacts.tsx only where the whole country's index is
held (baRegions), so /network's panel is as it was; the facts are read from /grid/authority/<code>, a static route made
for each file of data/regions/authority/ (the data machine's, contract section 10).
"""

import json
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, "site")


def src(*p):
    with open(os.path.join(SITE, *p), encoding="utf-8") as f:
        return f.read()


class ThePanel(unittest.TestCase):
    def test_the_facts_sit_under_the_panel_only_where_the_index_is_held(self):
        s = src("app", "network", "Network.tsx")
        self.assertIn('import { AuthorityFacts } from "@/components/grid/AuthorityFacts";', s)
        self.assertRegex(s, r"\{baRegions\?\.\[pick\.id\] \? <AuthorityFacts code=\{pick\.id\} region=\{baRegions\[pick\.id\]\.code\} /> : null\}\s*</aside>")

    def test_the_route_is_static_and_reads_only_listed_files(self):
        r = src("app", "grid", "authority", "[code]", "route.ts")
        self.assertIn('export const dynamic = "force-static";', r)
        self.assertIn("export const dynamicParams = false;", r)
        lib = src("lib", "regionsdata.ts")
        self.assertIn("authorityStems().includes(stem)", lib)

    def test_every_file_name_the_folder_holds_passes_the_route_rule(self):
        folder = os.path.join(SITE, "data", "regions", "authority")
        if not os.path.isdir(folder):
            self.skipTest("the authority files are not on this branch")
        rule = re.compile(r"^(region-)?[a-z0-9_]{2,12}$")
        names = [f[:-5] for f in os.listdir(folder) if f.endswith(".json")]
        self.assertTrue(names)
        self.assertEqual([n for n in names if not rule.match(n)], [])

    def test_each_block_the_component_reads_is_in_every_file(self):
        folder = os.path.join(SITE, "data", "regions", "authority")
        if not os.path.isdir(folder):
            self.skipTest("the authority files are not on this branch")
        for f in os.listdir(folder):
            with open(os.path.join(folder, f), encoding="utf-8") as h:
                d = json.load(h)
            for k in ("code", "name", "owns", "coming", "burns", "trades", "size", "large_loads"):
                self.assertIn(k, d, f)

    def test_a_missing_figure_says_its_reason(self):
        c = src("components", "grid", "AuthorityFacts.tsx")
        self.assertIn("Not held: {b.why", c)
        self.assertNotIn("?? 0)}", c.replace("(f.owns.generators ?? 0)", ""))


if __name__ == "__main__":
    unittest.main()
