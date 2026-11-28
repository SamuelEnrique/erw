"""Audit of /impact's datacenter, finding 4 (session 11404, chain 770, docs/reviews/impact-datacenter-model-audit-2026-11-28.md):
a document's own wage and spending split are not taken, and the page did not say so. The picker's hover says "Picking
one sets the MW, the investment (in 2025 dollars), the permanent jobs and the construction workers the document states;
a figure it does not state keeps its default", which reads as if a figure the document does state is taken. Five rows'
documents state a wage (Pima County on Beale's Project Blue, USD 64,000; Metrobloks in Clay County, USD 95,649; Google
in Storey County, USD 31.29 an hour; Vantage in Storey County, USD 64 an hour; and the Huntsville row's wage field,
USD 80,000), and Pima County's states the split (USD 2.4 billion of 3.6 billion for equipment); the earnings stay
Census County Business Patterns' (Arizona's NAICS 518210: USD 98,701 in 2025 dollars, 54 percent above Pima's figure)
and the split JLARC's.

1. Against the page's own files (passes on main): the five rows state a wage; the picker's projects carry no wage or
   split (site/lib/dcui.ts, dcProjects); Arizona's default wage is 98,701.
2. The fix on this branch, words only (fails on main): the picker's hover says a stated wage or split is not taken, with
   Pima County's example. Taking them would move figures (for Beale: operating earnings -35.2 percent, income tax -17.4
   percent over the life): Samuel's ruling."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "site", "data", "forecast")


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class StatedWages(unittest.TestCase):
    def test_documents_state_wages_the_pick_does_not_take(self):
        A = json.loads(read("site", "data", "forecast", "datacenter_announced.json"))
        rows = {r["id"]: r for r in A["rows"]}
        quotes = lambda r: " ".join((r.get(k) or {}).get("quote", "") for k in ("mw", "investment", "permanent_jobs", "construction_jobs"))  # noqa: E731
        self.assertIn("average salaries of $64,000", quotes(rows["az_beale_pima_2025"]))
        self.assertIn("$2.4 billion for equipment", quotes(rows["az_beale_pima_2025"]))
        self.assertIn("average annual wage of $95,649", quotes(rows["mo_metrobloks_clay_2026"]))
        self.assertIn("$31.29 per hour", quotes(rows["nv_google_storey_2020"]))
        self.assertIn("$64", quotes(rows["nv_vantage_storey_2024"]))
        self.assertTrue(any(r.get("wage") for r in A["rows"]))
        ui = read("site", "lib", "dcui.ts")
        proj = re.search(r"export type DcProject = \{(.*?)\};", ui, re.S).group(1)
        self.assertNotIn("wage", proj)
        W = json.loads(read("site", "data", "forecast", "datacenter_wages.json"))
        idx = json.loads(read("site", "data", "forecast", "deflator.json"))["index"]
        az = W["states"]["az"]["operations"]["per_job_usd"] * idx["2025"] / idx[str(W["year"])]
        self.assertEqual(round(az), 98701)
        self.assertGreater(az / 64000, 1.5)

    def test_the_hover_says_a_stated_wage_is_not_taken(self):
        d = read("site", "app", "impact", "Datacenter.tsx")
        self.assertIn("A wage or a split of the spending that a document states is not taken", d)
        self.assertIn("USD 64,000", d)


if __name__ == "__main__":
    unittest.main()
