"""Session 2262 (chain 159): a facility's country from the story's own words, where the model gave none.

The second read (session 2249) found 3 of 60 sampled facilities with the country missed (counted under no class in
its tally): "Stargate Norway" and "Stargate UK" as site names with no country, and the Chiba row of "AI
infrastructure in Japan". warehouse/datacenters/extract.py now reads an empty country from a country word in the
site's name, then "in <country>", then the deals' rule (a country before what is built), each only where one country
is named, and never another country than the United States for a facility with a US state. On the replayed 2249
answers: 3 to 0, and no other facility of either fixture gains a country.
"""

import importlib.util
import json
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
    spec = importlib.util.spec_from_file_location("erw_dc_extract_2262", os.path.join(ROOT, "warehouse", "datacenters", "extract.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TheWords(unittest.TestCase):
    def test_the_facility_country(self):
        fc = extract().facility_country
        self.assertEqual(fc("Stargate Norway", "Microsoft Takes Over Stargate Norway Data Center From OpenAI")[0], "Norway")
        self.assertEqual(fc("Stargate UK", "OpenAI halts Stargate UK data centre project")[0], "United Kingdom")
        self.assertEqual(fc("", "Jera, Dell Technologies, and Rhaelm team up for behind-the-meter AI infrastructure in Japan")[0], "Japan")
        self.assertEqual(fc("", "Equinix builds a US data center")[0], "United States")

    def test_no_country_where_the_words_do_not_name_one(self):
        fc = extract().facility_country
        self.assertEqual(fc("", "OpenAI's First Stargate Site to Hold Up to 400,000 Nvidia Chips"), ("", ""))
        self.assertEqual(fc("", "a campus in Japan and a campus in India"), ("", ""))
        self.assertEqual(fc("American Tower campus in Spain", "x"), ("Spain", "Spain"))   # the adjective is not counted
        self.assertEqual(fc("", "help us build the future"), ("", ""))


class TheSample(unittest.TestCase):
    def test_country_missed_three_to_none(self):
        rows, log = dc_fixture.replay("2249")
        fills = [l for l in log.splitlines() if "from the words" in l and ": country " in l]
        self.assertEqual(len(fills), 4)   # session 2276 adds F017's "enter US market"
        for c in ("United Kingdom", "Norway", "Japan", "United States"):
            self.assertTrue(any(f"country {c} " in l for l in fills), c)
        _, log2236 = dc_fixture.replay("2236")
        self.assertEqual([l for l in log2236.splitlines() if "from the words" in l and ": country " in l][0].split("country ")[1][:14], "United Kingdom")


if __name__ == "__main__":
    unittest.main()
