"""Session 2276 (chain 174): a facility's country from the market its company enters with it.

The second read (session 2249) found two stated facilities with no row. F017, "UK-based AI infrastructure firm
Gorilla Technology Group to enter US market with proposed 6MW data center acquisition", was answered by the model and
refused for no place; its words name the country as the market the facility enters (facility_country now reads "enter
<country> market"). F028, "Axe Compute acquires full ownership of AI cluster in Columbus, Georgia", got no answer from
the model: the prompt's human ruling of session 23 makes a purchase of chips or servers no facility, and an AI
cluster bought outright reads as one; left by that ruling.
"""

import importlib.util
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters", "eval"))
import dc_fixture  # noqa: E402


def extract():
    for p in (os.path.join(ROOT, "warehouse", "datacenters"), os.path.join(ROOT, "warehouse", "connectors"),
              os.path.join(ROOT, "warehouse")):
        sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("erw_dc_extract_2276", os.path.join(ROOT, "warehouse", "datacenters", "extract.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TheWords(unittest.TestCase):
    def test_the_market_entered(self):
        fc = extract().facility_country
        self.assertEqual(fc("", "Gorilla Technology Group to enter US market with proposed 6MW data center acquisition")[0], "United States")
        self.assertEqual(fc("", "a firm entering the UK market with a data centre")[0], "United Kingdom")
        self.assertEqual(fc("", "US market share of data centers grew"), ("", ""))   # no entry


class TheSample(unittest.TestCase):
    def test_f017_is_kept(self):
        rows, log = dc_fixture.replay("2249")
        self.assertEqual(len(rows), 61)
        self.assertNotIn("news:89042444b5a57d83: facility 0 not kept", log)
        got = [r for r in rows.to_dict("records") if "news:89042444b5a57d83" in str(r["story_ids"])]
        self.assertEqual([(r["operator"], r["country"], r["mw"]) for r in got], [("Gorilla Technology Group", "United States", "6")])


if __name__ == "__main__":
    unittest.main()
