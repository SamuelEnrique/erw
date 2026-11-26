"""Audit of the data pages, finding 3 (session 10233, docs/reviews/data-model-audit-2026-11-26.md): /data's citation
line says "Redivis dataset energy_research_warehouse, version v1", and the packages' citation printed on the same page
(site/lib/packages.ts, PACKAGES_CITATION) says "Redivis dataset `datapages.erw`": two datasets, two table lists
(docs/redivis/release-v1/ and release-v1-stanford/), neither released (site/data/site.json, released false), and the
page did not say which a reader cites.

1. The page cites one name, the packages another, and the two lists differ. Passes on main.
2. The fix on this branch, words only: the citation line says the packages write datapages.erw, the copy prepared under
   the Stanford organization, with its own list; that this page links and cites energy_research_warehouse; and that,
   neither being released, a citation names the dataset the table was read from. Which dataset /data links and cites is
   for Samuel's ruling (default: left as it is). No figure moves. Fails on main."""
import csv
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def tables(folder):
    with open(os.path.join(ROOT, "docs", "redivis", folder, "tables.csv"), encoding="utf-8", newline="") as f:
        return {r["table"]: r["in_v1"] for r in csv.DictReader(f)}


class TwoDatasetsToCite(unittest.TestCase):
    def test_the_page_and_the_packages_name_two_datasets(self):
        page = flat(src("site", "app", "data", "page.tsx"))
        self.assertIn("Redivis dataset <code className=\"font-mono\">energy_research_warehouse</code>, version v1", page)
        self.assertIn("Redivis dataset `datapages.erw`", src("site", "lib", "packages.ts"))
        site = json.loads(src("site", "data", "site.json"))
        self.assertEqual(site["redivis"]["dataset"], "energy_research_warehouse")
        self.assertFalse(site["redivis"]["released"])
        self.assertNotEqual(tables("release-v1"), tables("release-v1-stanford"))

    def test_the_page_says_so(self):
        page = flat(src("site", "app", "data", "page.tsx"))
        self.assertIn("The packages below write another dataset&apos;s name, <code className=\"font-mono\">datapages.erw</code>, the copy prepared under the Stanford organization", page)
        self.assertIn("docs/redivis/release-v1-stanford/tables.csv", page)
        self.assertIn("Neither is released, so a citation names the dataset the table was read from.", page)


if __name__ == "__main__":
    unittest.main()
