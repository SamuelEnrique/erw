"""Session 10214 (chain 710, part D: the demand page audited, docs/reviews/demand-model-audit-2026-11-26.md, finding 1).

/demand reads EIA's Adjusted demand for each balancing authority and says "Nothing is filled". EIA's Adjusted demand
already holds EIA's own estimates for hours an authority reported nothing for, and the page uses them as reported
hours: MISO's highest hour of 2025, printed on the default view's ranking, is one. The data test runs where EIA's
workbook extract is held (the data machine's warehouse/raw, or a folder named by ERW_AUDIT_RAW); the words tests run
everywhere.
"""
import glob
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def extract(name):
    roots = [os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")]
    if os.environ.get("ERW_AUDIT_RAW"):
        roots.insert(0, os.environ["ERW_AUDIT_RAW"])
    for r in roots:
        hits = sorted(glob.glob(os.path.join(r, "*", name)))
        if hits:
            return hits[-1]
    return None


class EiasEstimatesInsideAdjustedDemand(unittest.TestCase):
    def test_miso_reported_nothing_in_the_hour_of_its_2025_peak(self):
        path = extract("miso_hours.csv")
        if not path:
            self.skipTest("EIA's workbook extract is not held on this machine")
        site = json.loads(src("site", "data", "demand_growth.json"))
        at = site["areas"]["MISO"]["at"]["2025"]["peak_demand_mw"]
        self.assertEqual(at, "2025-07-24T20:00:00Z")
        self.assertEqual(site["areas"]["MISO"]["years"]["2025"]["peak_demand_mw"], 120343.0)
        with open(path, encoding="utf-8") as f:
            rows = [line.rstrip("\n").split(",") for line in f if line.startswith("2025-07-24T")]
        self.assertEqual(len(rows), 24)
        peak = [r for r in rows if r[0] == at]
        self.assertEqual(peak[0][1], "", "MISO's own Demand is blank in the hour of its 2025 peak")
        self.assertGreaterEqual(sum(r[1] == "" for r in rows), 18, "and in most of that UTC day (the local day, Central)")

    def test_the_page_says_eias_estimates_are_used_as_reported_hours(self):
        page = src("site", "app", "demand", "page.tsx")
        self.assertIn("Nothing is filled here. A grid operator's hours are EIA's Adjusted demand, which already holds EIA's own estimate", page)
        self.assertIn("MISO's highest hour of 2025 (24 July 2025, a day MISO reported nothing) is EIA's estimate.", page)

    def test_the_decision_and_the_note_say_it_word_for_word(self):
        words = "Adjusted demand holds EIA's own estimate where an authority reported nothing or an implausible value, and the page uses such an hour as a reported one: 351 hours of the seven authorities from 2019 to 2025"
        self.assertIn(words, src("site", "lib", "decisions.ts"))
        note = src("docs", "methods", "demand_growth.md")
        self.assertIn(words, note)
        self.assertIn("**EIA's estimates inside Adjusted demand (session 10214).**", note)


if __name__ == "__main__":
    unittest.main()
