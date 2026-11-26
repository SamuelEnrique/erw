"""Audit of the company database, finding 4 (session 10228, docs/reviews/companies-model-audit-2026-11-26.md): /companies
ranks companies as EIA, ERCOT and the NRC name them (operating utilities, plant operators, project companies), not
groups, and said so nowhere on the page. In the page files of 16 November 2026: the 12 rows whose name begins "Duke"
hold 60,830 operating MW (more than any listed company; the largest of them is sixth by footprint); the 13
"Constellation" rows 32,154 MW, the reactors on one row and their MW on another; NextEra Energy, Inc. lists 0 MW though
Florida Power & Light names it as parent; 18 listed companies carry a parent.

1. In the page files, Florida Power & Light names NextEra Energy, Inc. as parent and NextEra's own row has no MW; the
   Duke rows summed exceed the first row's operating MW. Passes on main.
2. The fix on this branch, words only: a hover on the index's count line, and the parent and EIA id hovers of a
   company's page, say a row is a company, not its group, and a parent's figures are not summed; the method note gives
   the sizes. No figure moves. Fails on main."""
import hashlib
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def company(cid):
    key = hashlib.sha1(f"company:{cid}".encode()).hexdigest()[:2]
    return json.loads(src("site", "data", "companies", "c", f"{key}.json"))[cid]


class ACompanyNotItsGroup(unittest.TestCase):
    def test_the_files_list_operating_companies(self):
        ix = json.loads(src("site", "data", "companies", "index.json"))
        rows = [dict(zip(ix["columns"], r)) for r in ix["rows"]]
        self.assertEqual(company("eia-6452")["parent"], "NextEra Energy, Inc.")
        nextera = next(r for r in rows if r["name"] == "NextEra Energy, Inc.")
        self.assertEqual(nextera["plants_mw"], 0)
        duke = sum(r["plants_mw"] for r in rows if r["name"].split()[0].lower() == "duke")
        self.assertGreater(duke, rows[0]["plants_mw"])

    def test_the_pages_say_so(self):
        page = flat(src("site", "app", "companies", "page.tsx"))
        self.assertIn("A parent&apos;s figures are not summed and a group&apos;s companies are rows of their own", page)
        self.assertIn("the footprint ranks those companies, not groups.", page)
        one = flat(src("site", "app", "companies", "[id]", "page.tsx"))
        self.assertIn("its figures are not summed with this company's, and its other companies are rows of their own.", one)
        self.assertIn("Another id is another company, even of the same group", one)
        self.assertIn('the 12 rows whose name begins "Duke" hold 60,830 operating MW', flat(src("docs", "methods", "companies.md")))


if __name__ == "__main__":
    unittest.main()
