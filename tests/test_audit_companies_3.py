"""Audit of the company database, finding 3 (session 10228, docs/reviews/companies-model-audit-2026-11-26.md): the
hold's sentence on /companies gives each held table's count as its rows ("energy_deals (958 rows)"), but the count is of
links, a company named in one row: energy_deals held 583 rows (extracted 12 November 2026) and policy_actions 2,127
(coverage, 25 November) against 958 and 3,249 links. The source line said "Built 2026-11-16 from 13 tables held",
where "held" meant read, beside "held for a license" (5 of the 13, which add nothing), and gave no input's date.

1. The page files' held counts are larger than the rows of the tables they count (energy_deals' 958 against at most
   600 rows; policy_actions' 3,249 against coverage's count). Passes on main.
2. The fix on this branch, words only: the sentence says links and what a link is; the source line says the public rows
   of 8 of the 13 tables, the 5 held adding nothing, each input as held that day with its own date; the lead's hover
   says "the warehouse's own tables". No figure moves. Fails on main."""
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


class HeldCountsAreLinks(unittest.TestCase):
    def test_the_counts_are_more_than_the_rows(self):
        ix = json.loads(src("site", "data", "companies", "index.json"))
        self.assertEqual(ix["held_links"]["energy_deals"], 958)
        self.assertGreater(ix["held_links"]["energy_deals"], 600)
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            cov = {r["table"]: int(r["n_rows"]) for r in csv.DictReader(f)}
        self.assertGreater(ix["held_links"]["policy_actions"], cov["policy_actions"])
        self.assertEqual((len(ix["tables"]), len(ix["held_tables"])), (13, 5))

    def test_the_page_says_links(self):
        page = flat(src("site", "app", "companies", "page.tsx"))
        self.assertIn('plural(ix.held_links[t] ?? 0, "link", "links")', page)
        self.assertIn("a link being a company named in one of a table&apos;s rows (a row that names two companies is two links)".replace("&apos;", "'"), page.replace("&apos;", "'"))
        self.assertIn("from the public rows of {ix.tables.length - held.length} of the {ix.tables.length} tables it reads ({held.length} held for a license add nothing)", page)
        self.assertIn("so a figure is as of its input&apos;s own date and the dates differ", page)
        self.assertIn("Built from the warehouse&apos;s own tables and nothing else", page)
        self.assertNotIn("tables held;", page)
        self.assertIn("energy_deals' 958 links against its 583 rows", flat(src("docs", "methods", "companies.md")))


if __name__ == "__main__":
    unittest.main()
