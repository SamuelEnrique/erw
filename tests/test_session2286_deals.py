"""Session 2286 (chain 179): a facility's country from "<place>, <country>", a UK nation counted as the UK.

The third read (session 2284) found U009, "Era4 reveals details of hyperscale data center planned for former
steelworks in Newport, Wales", with no country. warehouse/datacenters/extract.py (facility_country) reads "in <place>,
<country>" as well as "in <country>", and for facilities counts England, Scotland, Wales and Northern Ireland as the
United Kingdom. On the three facility fixtures, only U009 changes.
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
    spec = importlib.util.spec_from_file_location("erw_dc_extract_2286", os.path.join(ROOT, "warehouse", "datacenters", "extract.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TheWords(unittest.TestCase):
    def test_a_place_and_its_country(self):
        fc = extract().facility_country
        self.assertEqual(fc("", "data center planned for former steelworks in Newport, Wales")[0], "United Kingdom")
        self.assertEqual(fc("", "a campus in San Mateo, Zaragoza, Spain")[0], "Spain")
        self.assertEqual(fc("", "a campus in Edinburgh, Scotland")[0], "United Kingdom")

    def test_none(self):
        fc = extract().facility_country
        self.assertEqual(fc("", "Wales Energy signs a deal"), ("", ""))   # no place before it


class TheSample(unittest.TestCase):
    def test_u009(self):
        rows, log = dc_fixture.replay("2284")
        self.assertIn("country United Kingdom from the words 'in Newport, Wales'", log)
        self.assertEqual(sorted(r["country"] for r in rows.to_dict("records") if r["city"] == "Newport"), ["United Kingdom"])


if __name__ == "__main__":
    unittest.main()
