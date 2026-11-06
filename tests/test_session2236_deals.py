"""Session 2236 (chain 156): the datacenter facilities made precise, and their rollups.

The fixture (`tests/fixtures/datacenters/`): 35 stored stories in 28 clusters from the audit's sample of facilities,
answers written from their words, and the model's answers to the new prompt, recorded once (3 calls). The test replays
them through `warehouse/datacenters/extract.py` (no model, no network, no gazetteer) and grades the rows
(`warehouse/datacenters/eval/dc_fixture.py`); the rollups are built from a small frame.
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(ROOT, "warehouse", "datacenters"), os.path.join(ROOT, "warehouse", "datacenters", "eval"),
          os.path.join(ROOT, "warehouse", "derived")):
    if p not in sys.path:
        sys.path.insert(0, p)

import dc_fixture  # noqa: E402
import facility_fields as ff  # noqa: E402
import datacenter_tracker_rollups as rollups  # noqa: E402


class TheFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answers = dc_fixture.read("answers_2236.json")
        cls.rows, cls.log = dc_fixture.replay("2236")
        cls.g = dc_fixture.grade(cls.rows, cls.answers)
        cls.before = dc_fixture.grade(None, cls.answers, view="stored")

    def test_two_places_are_two_facilities(self):
        self.assertEqual(len(self.before["two_places_one_row"]), 6)   # xAI TN and MS, AWS Mexico and UAE, each way
        self.assertEqual(self.g["two_places_one_row"], [])

    def test_no_facility_without_a_place(self):
        # session 2276: F017 ("to enter US market with proposed 6MW data center acquisition") is either, two reads disagreeing
        self.assertEqual(sorted(self.before["found_wrongly"]), ["F057"])
        self.assertEqual(self.g["found_wrongly"], [])
        self.assertIn("no site, city, county, state or country stated", self.log)

    def test_the_mw_basis(self):
        self.assertEqual(self.g["fields"]["mw_basis"], [])
        r = self.rows.set_index("operator")
        self.assertEqual(r.loc["Nebius", "mw_basis"], "tenant")
        self.assertTrue(((self.rows["mw"] == "") == (self.rows["mw_basis"] == "")).all())

    def test_a_year_of_another_event_is_not_the_facilitys(self):
        self.assertEqual(self.before["fields"]["planned_year"], ["F010: '2028', answer ''"])
        self.assertEqual(self.g["fields"]["planned_year"], [])
        self.assertEqual(self.g["fields"]["energized_year"], [])

    def test_status_and_operator(self):
        self.assertEqual(len(self.before["fields"]["project_status"]), 3)
        self.assertLessEqual(len(self.g["fields"]["project_status"]), 1)
        self.assertEqual(self.g["fields"]["operator"], [])   # "TikTok owner" is a description

    def test_at_most_one_facility_missed(self):
        self.assertLessEqual(len(self.g["missed"]), 1)   # DataOne's NJ facility: the model gave no state

    def test_the_grid_says_its_basis(self):
        tx = self.rows[self.rows["state"] == "TX"]
        self.assertTrue(len(tx) >= 1)
        self.assertTrue((tx["grid"] == "ERCOT").all() and (tx["grid_basis"] == "state").all())
        self.assertTrue((self.rows.loc[self.rows["grid"] == "", "grid_basis"] == "").all())


class Fields(unittest.TestCase):
    def test_power_kind(self):
        self.assertEqual(ff.power_kind("off-grid"), "behind_the_meter")
        self.assertEqual(ff.power_kind("gas turbines"), "behind_the_meter_gas")
        self.assertEqual(ff.power_kind("unpermitted generator fleet"), "behind_the_meter_gas")
        self.assertEqual(ff.power_kind("20-year power deal"), "grid")
        self.assertEqual(ff.power_kind("solar and storage"), "renewables_storage")
        self.assertEqual(ff.power_kind(""), "")

    def test_the_countys_utility(self):
        table = {("PA", "luzerne"): [("PPL Electric Utilities Corp", "14715"), ("UGI Utilities, Inc", "19390")],
                 ("TX", "potter"): [("Southwestern Public Service Co", "17718")]}
        self.assertEqual(ff.utility_of("TX", "Potter County", table), ("Southwestern Public Service Co", "17718", "1"))
        self.assertEqual(ff.utility_of("PA", "Luzerne County", table), ("", "", "2"))
        self.assertEqual(ff.utility_of("PA", "", table), ("", "", ""))

    def test_place_conflict(self):
        self.assertTrue(ff.place_conflict({"state": "TN"}, {"state": "MS"}))
        self.assertTrue(ff.place_conflict({"country": "Mexico"}, {"country": "UAE"}))
        self.assertTrue(ff.place_conflict({"state": "TX", "city": "Abilene"}, {"state": "TX", "city": "Amarillo"}))
        self.assertFalse(ff.place_conflict({"state": "TN", "city": "Memphis"}, {"state": "", "city": "Memphis"}))

    def test_a_description_is_not_an_operator(self):
        self.assertTrue(ff.description("TikTok owner"))
        self.assertTrue(ff.description("US hyperscaler"))
        self.assertFalse(ff.description("Microsoft"))


class Rollups(unittest.TestCase):
    def test_sums_of_stated_mw_with_the_rest_counted(self):
        fac = pd.DataFrame([
            {"operator": "Google", "developer": "", "state": "TX", "mw": "200", "status": "planned", "grid": "ERCOT"},
            {"operator": "Google", "developer": "", "state": "TX", "mw": "", "status": "operating", "grid": "ERCOT"},
            {"operator": "", "developer": "Fermi", "state": "TX", "mw": "222", "status": "", "grid": "ERCOT"},
            {"operator": "Meta", "developer": "", "state": "LA", "mw": "", "status": "planned", "grid": "MISO"},
        ])
        r = pd.DataFrame(rollups.rollups(fac, "2026-11-06"))
        v = r.set_index(["entity", "variable"])["value"]
        self.assertEqual(v[("grid:ERCOT", "facilities")], 3)
        self.assertEqual(v[("grid:ERCOT", "mw_stated")], 422)
        self.assertEqual(v[("grid:ERCOT", "facilities_without_mw")], 1)
        self.assertEqual(v[("grid:ERCOT", "mw_stated_planned")], 200)
        self.assertEqual(v[("operator:Fermi", "mw_stated")], 222)        # the developer where no operator is named
        self.assertNotIn(("grid:MISO", "mw_stated"), v.index)            # no stated MW: no sum, never a zero
        self.assertEqual(v[("grid:MISO", "facilities_without_mw")], 1)
        self.assertEqual(v[("tracker:all", "facilities")], 4)


if __name__ == "__main__":
    unittest.main()
