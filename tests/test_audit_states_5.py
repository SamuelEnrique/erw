"""Session 10223 (the states audit, finding 5): "Nothing is filled, scaled or estimated" was true of the ERW, silent on EIA.

Form EIA-861M's monthly state sales hold EIA's estimates for the utilities it does not survey each month; the annual
Form EIA-861 behind the state profile replaces them with reported sales. Texas's 2024 months, summed, are 2.07 percent
above the profile's full-service and energy-only sales (the method note's cross-check). The decision now says so.
Words only: no figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "tx.json")), "the states' page files are not on this machine")
class TheFile(unittest.TestCase):
    def test_texas_monthly_sales_are_above_the_annual_form(self):
        with open(os.path.join(DIR, "tx.json"), encoding="utf-8") as f:
            t = json.load(f)
        r, d = t["retail"], t["disposition"]
        monthly = r["annual_sales_mwh"]["all"][r["years"].index("2024")]
        i = d["years"].index("2024")
        annual = d["values"]["full_service_providers"][i] + d["values"]["energy_only_providers"][i]
        self.assertAlmostEqual(100 * (monthly - annual) / annual, 2.07, places=2)


class TheWords(unittest.TestCase):
    def test_the_decision_names_eia_estimates(self):
        dec = src("site", "app", "states", "Decisions.tsx")
        self.assertNotIn("Nothing is filled, scaled or estimated.", dec)
        self.assertIn("The ERW fills, scales and estimates nothing. EIA's monthly figures hold EIA's own estimates", dec)
        self.assertIn("2.07 percent", dec)
        self.assertIn("EIA revises its newest months", dec)
        self.assertIn("EIA's monthly figures hold EIA's own estimates", src("docs", "methods", "states_page.md"))


if __name__ == "__main__":
    unittest.main()
