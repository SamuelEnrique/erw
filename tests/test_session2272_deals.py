"""Session 2272 (chain 174): a facility's US state from the story's words, where the model gave none.

The second read (session 2249) found 2 of 60 sampled facilities with the state missed: "Skybox & Prologis file for
fourth data center in Hutto, Texas" and the Paducah hub "in Western Kentucky". warehouse/datacenters/extract.py
(facility_state) now reads the one US state a cluster of one facility names by its full name, with a capital, for a
facility with no country or the United States. On the replayed answers: 2 to 0 on the 2249 fixture, and the 2236
fixture's Columbus, Georgia facility gains its written answer's state; nothing else changes.
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
    spec = importlib.util.spec_from_file_location("erw_dc_extract_2272", os.path.join(ROOT, "warehouse", "datacenters", "extract.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TheWords(unittest.TestCase):
    def test_one_state(self):
        fs = extract().facility_state
        self.assertEqual(fs("Skybox & Prologis file for fourth data center in Hutto, Texas")[0], "TX")
        self.assertEqual(fs("the former uranium enrichment site in Western Kentucky")[0], "KY")
        self.assertEqual(fs("a campus in West Virginia")[0], "WV")
        self.assertEqual(fs("a site in Washington state")[0], "WA")

    def test_none_or_several(self):
        fs = extract().facility_state
        self.assertEqual(fs("campuses in Texas and Ohio"), ("", ""))
        self.assertEqual(fs("Microsoft opens office in Washington"), ("", ""))
        self.assertEqual(fs("an indiana jones film set"), ("", ""))   # no capital
        self.assertEqual(fs("a data center in Mumbai"), ("", ""))


class TheSample(unittest.TestCase):
    def test_state_missed_two_to_none(self):
        _, log = dc_fixture.replay("2249")
        fills = [l for l in log.splitlines() if ": state " in l and "from the words" in l]
        self.assertEqual(sorted(l.split(": state ")[1][:2] for l in fills), ["KY", "TX"])
        _, log2236 = dc_fixture.replay("2236")
        fills = [l for l in log2236.splitlines() if ": state " in l and "from the words" in l]
        self.assertEqual([l.split(": state ")[1][:2] for l in fills], ["GA"])


if __name__ == "__main__":
    unittest.main()
