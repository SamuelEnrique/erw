"""Session 3127 (chain 169): the place rule's four widenings (warehouse/connectors/policy_sources.py), each with the
words of the audit's sample document that needed it (docs/reviews/policy-audit-2026-11-06.md, class 6). Session 157's
87-document test (tests/test_session157.py, 85 right) holds them too.

    .venv/Scripts/python.exe -m pytest -q tests/test_policy_places.py
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import policy_sources as ps  # noqa: E402


class Places(unittest.TestCase):
    def test_a_public_body_named_with_its_postal_code(self):
        # r8
        self.assertEqual(ps.place_states("City of Pelican, AK; Notice of Authorization for Continued Project Operation", "", ""), "AK")
        self.assertEqual(ps.place_states("Acme Power, AK Inc.; Notice of Application", "", ""), "", "a company is not a public body")

    def test_an_alaska_census_area(self):
        # r39
        s = ps.county_sentence("f. Location: On Solomon Lake and Solomon Gulch Creek, in the Chugach Census Area, in Valdez, Alaska.")
        self.assertEqual(ps.place_states("Copper Valley Electric Association, Inc.; Notice", "", "", s), "AK")

    def test_a_plant_located_at_a_place(self):
        # r66
        s = ps.county_sentence("for a dual-unit SMR-300 plant located at the Palisades Energy Center (PEC) in Covert, Michigan. The units")
        self.assertEqual(ps.place_states("SMR, LLC; Pioneer Units 1 and 2; Exemption", "", "", s), "MI")

    def test_a_part_of_a_state_and_a_venue_passed_over(self):
        # r60: the first sentence is a meeting's address, the second the action's place
        t = ("The scoping meeting will be held at the Sky Ute Casino Resort, located on the Southern Ute Indian Reservation, "
             "at 14324 US Highway 172 North, Ignacio, Colorado 81301. Federal approval of operations on lands held in trust "
             "for the Tribe within an area on the Southern Ute Indian Reservation in southwestern Colorado is proposed.")
        self.assertEqual(ps.place_states("Intent To Prepare a Programmatic Environmental Impact Statement", "", "", ps.county_sentence(t)), "CO")


if __name__ == "__main__":
    unittest.main()
