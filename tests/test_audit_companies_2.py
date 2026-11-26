"""Audit of the company database, finding 2 (session 10228, docs/reviews/companies-model-audit-2026-11-26.md): the
default order of /companies is the footprint, "operating, owned, planned and queue MW summed, a sort key". A jointly
owned generator the company also operates is in its operating MW whole and in its owned MW for its share, so it counts
twice: in the page files of 16 November 2026, 360 generators at 106 companies, 62,735 MW (Florida Power & Light's St.
Lucie unit 2, 919.2 MW of its share, among them). The method note says so; the page and the download did not.

1. In the page files, a company's footprint is its operating, owned, planned and queue MW summed, and Florida Power &
   Light's owned rows name a generator its operating rows name too. Passes on main.
2. The fix on this branch, words only: the hover of each footprint cell and the download's header say a jointly owned
   generator the company also operates counts twice; the method note gives the size. The order does not change.
   Fails on main."""
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


class TheFootprintCountsTwice(unittest.TestCase):
    def test_an_operated_generator_is_also_owned(self):
        ix = json.loads(src("site", "data", "companies", "index.json"))
        cols = ix["columns"]
        row = dict(zip(cols, next(r for r in ix["rows"] if r[0] == "eia-6452")))
        self.assertAlmostEqual(row["footprint_mw"], row["plants_mw"] + row["owned_mw"] + row["planned_mw"] + row["queue_mw"], places=1)
        c = company("eia-6452")
        t = ix["tables"]
        operated = {tuple(l[2].split(":")[1:3]) for l in c["links"] if t[l[1]] == "eia860m_operating_generators"}
        owned_also_operated = [l for l in c["links"] if t[l[1]] == "eia860_generator_owners" and tuple(l[2].split(":")[1:3]) in operated and l[6]]
        self.assertGreaterEqual(len(owned_also_operated), 1)
        self.assertGreater(sum(float(l[6]) for l in owned_also_operated), 900)

    def test_the_page_and_the_download_say_so(self):
        self.assertIn("a jointly owned generator the company also operates counts twice, whole in operating MW and for its share in owned MW",
                      src("site", "app", "companies", "page.tsx"))
        self.assertIn("a jointly owned generator the company also operates counts twice, whole in plants_mw and for its share in owned_mw",
                      src("site", "lib", "companydb.ts"))
        self.assertIn("360 jointly owned generators at 106 companies, 62,735 MW counted twice", flat(src("docs", "methods", "companies.md")))


if __name__ == "__main__":
    unittest.main()
