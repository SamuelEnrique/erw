"""Audit of the company database, finding 6 (session 10228, docs/reviews/companies-model-audit-2026-11-26.md): a company
page's "Owned share" hover counts every jointly owned generator, but 651 of the 5,680 owner rows in the page files of 16
November 2026 (at 337 companies) carry no MW, their generator not in EIA-860M's operating list; Florida Power & Light's
5 counted generators sum from 3. "Headquarters state" is the state of the owner's address in EIA-860's owner schedule,
an address on a form: for 1,015 of the 2,031 listed companies that have one it is none of the states their rows name.

1. Florida Power & Light's owner rows: 5, of which 2 carry no MW. Passes on main.
2. The fix on this branch, words only: the owned share's hover and its figure's hover say a generator EIA-860M does not
   hold adds no MW and that the share is of jointly owned generators only; the fact is called the owner's address state,
   its hover says it is an address on a form. No figure moves. Fails on main."""
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


class OwnedShareAndAddress(unittest.TestCase):
    def test_owner_rows_without_mw(self):
        ix = json.loads(src("site", "data", "companies", "index.json"))
        c = company("eia-6452")
        owners = [l for l in c["links"] if ix["tables"][l[1]] == "eia860_generator_owners"]
        self.assertEqual((len(owners), sum(1 for l in owners if l[6] == "")), (5, 2))
        self.assertEqual(c["figures"]["n_owned_generators"], 5)

    def test_the_hovers_say_so(self):
        one = flat(src("site", "app", "companies", "[id]", "page.tsx"))
        self.assertIn("A generator EIA-860M's operating list does not hold (retired, or not matched) is counted here and adds no MW.", one)
        self.assertIn('<Fact label="Owner&apos;s address state"', one)
        self.assertIn("an address on a form, not a stated headquarters", one)
        self.assertNotIn('label="Headquarters state"', one)
        self.assertIn("(a row whose generator EIA-860M's operating list does not hold adds no MW)", src("site", "lib", "companydb.ts"))
        self.assertIn("for 1,015 of the 2,031 listed companies that have one", flat(src("docs", "methods", "companies.md")))


if __name__ == "__main__":
    unittest.main()
