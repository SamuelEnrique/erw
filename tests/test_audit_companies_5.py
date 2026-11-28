"""Audit of the company database, finding 5 (session 10228, docs/reviews/companies-model-audit-2026-11-26.md): since
session 7001 a company whose EIA-861 ownership is a retail or wholesale power marketer is of the kind "power marketer"
(439 listed companies in the page files of 16 November 2026). The kind's hovers on /companies and on a company's page
list the kinds without it, and the Kind choices (KIND_ORDER in site/lib/companydb.ts) do not offer it.

1. The index counts 439 power marketers and KIND_ORDER leaves the kind out. Passes on main.
2. The fix on this branch, words only: both hovers list power marketer and say "other" is where no rule applies; the
   index's hover says which kinds the choices do not offer, computed from KIND_ORDER, so it stays right whatever the
   choices become. Adding the choice would add a count to the page and is for the owner's ruling
   (wip/audit-companies-9). Fails on main."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class PowerMarketers(unittest.TestCase):
    def test_the_kind_is_counted_and_not_offered(self):
        ix = json.loads(src("site", "data", "companies", "index.json"))
        self.assertEqual(ix["kinds"].get("power marketer"), 439)
        order = re.findall(r'"([^"]+)"', re.search(r"KIND_ORDER = \[(.*?)\]", src("site", "lib", "companydb.ts")).group(1))
        # session 11407 (wip/ready-companies-marketer, the owner's other choice): the kind is offered on this branch;
        # until then this line asserted that KIND_ORDER left it out (tests/test_ready_companies_marketer.py)
        self.assertIn("power marketer", order)

    def test_the_hovers_name_it(self):
        page = flat(src("site", "app", "companies", "page.tsx"))
        self.assertIn("developer, operator, power marketer, other that the company&apos;s rows show", page)
        self.assertIn("const kindsUnoffered = Object.keys(ix.kinds).filter((k) => !KIND_ORDER.includes(k));", page)
        self.assertIn("The choices here do not offer ${kindsUnoffered.join(\", \")}: such a company shows its kind in the table.", page)
        one = flat(src("site", "app", "companies", "[id]", "page.tsx"))
        self.assertIn("developer, operator, power marketer, other that its rows show; other where no rule applies.", one)
        self.assertIn("power marketer included after operator (439 listed companies on 16 November 2026", flat(src("docs", "methods", "companies.md")))


if __name__ == "__main__":
    unittest.main()
