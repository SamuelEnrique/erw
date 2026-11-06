"""Session 2232 (chain 156): the deal tracker's schema and prompt, graded on a fixture of 40 stored stories.

The fixture (`tests/fixtures/deals/`): `stories_2232.json`, 40 stories of the audit's sample as `news_stories` holds them
(`docs/reviews/deals-audit-2026-11-06.md`), 30 of rows the audit found faulty and 6 clean; `answers_2232.json`, the
answers written from those stories' own words; `recorded_2232.json`, what the model answered to the new prompt on
6 November 2026 (3 calls, USD 0.1227). The test replays the recorded answers through the extractor (no model, no
network, a temporary folder) and grades the rows (`warehouse/deals/eval/fixture.py`).
"""

import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(ROOT, "warehouse", "deals"), os.path.join(ROOT, "warehouse", "deals", "eval")):
    if p not in sys.path:
        sys.path.insert(0, p)

import fields  # noqa: E402
import fixture  # noqa: E402


class TheFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answers = fixture.read("answers_2232.json")
        cls.rows, cls.log = fixture.replay("2232")
        cls.g = fixture.grade(cls.rows, cls.answers)
        cls.before = fixture.grade(None, cls.answers, view="stored")

    def test_the_fixture_is_forty_stored_stories(self):
        stories = fixture.read("stories_2232.json")
        self.assertEqual(len(stories), 40)
        self.assertEqual(len(self.answers), 36)
        self.assertTrue(all(a["why"] for a in self.answers))   # every answer says the words it rests on

    def test_no_deal_is_kept_where_the_story_reports_none(self):
        # before: 7 of the 9 (a plan, a pledge, a seeking, a permission, two governments, an unnamed raiser)
        self.assertEqual(len(self.before["deal_found_wrongly"]), 7)
        self.assertEqual(self.g["deal_found_wrongly"], [])

    def test_no_figure_is_invented_or_of_another_sum(self):
        self.assertEqual(len(self.before["figure_invented"]), 2)   # a valuation and a company-wide investment
        self.assertEqual(self.g["figure_invented"], [])
        self.assertEqual(self.g["price_not_energy"], [])
        for f in ("mw", "mwh", "usd", "term_years", "usd_per_mwh"):
            self.assertEqual(self.g["fields"][f], [], f)

    def test_the_ai_power_tag_follows_the_rule(self):
        self.assertEqual(len(self.before["fields"]["ai_power"]), 3)
        self.assertEqual(self.g["fields"]["ai_power"], [])
        # every tagged row says why
        tagged = self.rows[self.rows["ai_power"] == "true"]
        self.assertTrue(len(tagged) >= 10)
        self.assertTrue((tagged["ai_power_basis"] != "").all())

    def test_kind_and_stage_and_place(self):
        self.assertEqual(self.g["fields"]["kind"], [])
        self.assertEqual(self.g["fields"]["stage"], [])
        self.assertEqual(self.g["fields"]["state"], [])
        self.assertLessEqual(len(self.g["fields"]["country"]), 1)   # before: 4
        self.assertTrue(set(self.rows["kind"]) <= set(fields.KIND_IDS))
        self.assertTrue(set(self.rows["stage"]) <= set(fields.STAGE_IDS) | {""})
        self.assertIn("gas_buildout", set(self.rows["kind"]))        # BKV and Siemens Energy, before "ppa" and "other"
        self.assertIn("compute_capacity", set(self.rows["kind"]))    # the cloud and GPU contracts, before "offtake"

    def test_at_most_two_stated_deals_missed_and_one_role_swapped(self):
        self.assertLessEqual(len(self.g["deal_missed"]), 2)
        self.assertLessEqual(len(self.g["fields"]["buyer"]), 1)

    def test_every_row_carries_its_source_and_evidence(self):
        self.assertTrue((self.rows["source_url"] != "").all())
        self.assertTrue((self.rows["fields_version"] == fields.VERSION).all())
        self.assertIn("mw 500.0: no number in span 'Half-GW'", self.log)   # a figure without digits is not converted


class Fields(unittest.TestCase):
    def test_kind_power_kinds_first(self):
        self.assertEqual(fields.kind_of({"deal_type": "ppa", "asset": "Crane Clean Energy Center restart"})[0],
                         "nuclear_restart_uprate")
        self.assertEqual(fields.kind_of({"deal_type": "ppa", "technology": "solar plus storage"})[0], "storage")
        self.assertEqual(fields.kind_of({"deal_type": "other", "technology": "natural gas",
                                         "asset": "1.2 GW of gas-fired generation equipment"})[0], "gas_buildout")
        self.assertEqual(fields.kind_of({"deal_type": "m_and_a", "technology": "gas", "asset": "gas plant"})[0], "m_and_a")
        self.assertEqual(fields.kind_of({"deal_type": "offtake", "asset": "cloud computing capacity"})[0],
                         "compute_capacity")
        self.assertEqual(fields.kind_of({"deal_type": "debt", "asset": "company"})[0], "capital")

    def test_ai_power_rule(self):
        self.assertTrue(fields.ai_of({"buyer": "Amazon", "seller": "AEP"}, "aep signs 960-mw nuclear pact")[0])
        self.assertFalse(fields.ai_of({"buyer": "Vistra", "seller": "Lotus"},
                                      "vistra buying us gas-power fleet to deepen ai bet")[0])
        self.assertEqual(fields.ai_of({"buyer": "Black Hills"}, "power google's data center")[1],
                         "datacenter load: data center")

    def test_a_percentage_is_never_a_price(self):
        self.assertFalse(fields.energy_price("%"))
        self.assertFalse(fields.energy_price("CAD/share"))
        self.assertTrue(fields.energy_price("USD/MWh"))
        self.assertTrue(fields.energy_price("$/MWh"))

    def test_a_deal_needs_a_party_the_story_names(self):
        self.assertFalse(fields.named_party({"buyer": "", "seller": ""}, "fusion startup raises $450 million"))
        self.assertTrue(fields.named_party({"other_parties": ["Continental", "Mercuria"]}, "continental joins mercuria"))
        self.assertTrue(fields.named_party({"deal_type": "m_and_a", "asset": "Oryx Energies"},
                                           "oryx energies sold for about $1 billion"))

    def test_a_figure_above_a_bound_is_flagged_not_dropped(self):
        self.assertEqual(fields.flags_of({"mw": 50000}), ["mw 50000 above the bound 20000"])
        self.assertEqual(fields.flags_of({"mw": 960}), [])


class TheUpgrade(unittest.TestCase):
    """A table written before this session gets the new columns in place, every row and value kept."""

    def test_upgrade_keeps_every_row(self):
        ex = fixture.load_extract()
        d = tempfile.mkdtemp(prefix="erw_s2232_up_")
        path = os.path.join(d, "energy_deals.csv")
        row = {c: "" for c in ex.DEAL_COLS_V1}
        row.update(event_id="deal:1", event_date="2026-10-01T00:00:00Z", deal_type="ppa", buyer="Tesla",
                   seller="ContourGlobal", technology="solar-plus-storage", dollars="5", price="40", mw="509")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("# a header line\n")
            pd.DataFrame([row], columns=ex.DEAL_COLS_V1).to_csv(f, index=False, lineterminator="\n")
        n = ex.upgrade_file(path, ex.DEAL_COLS_V1, ex.DEAL_COLS, fields.upgrade, lambda m: None)
        self.assertEqual(n, 1)
        new = ex.ip.read_series(path, ex.DEAL_COLS)
        self.assertEqual(new.loc[0, "mw"], "509")
        self.assertEqual(new.loc[0, "usd"], "5")
        self.assertEqual(new.loc[0, "usd_per_mwh"], "40")
        self.assertEqual(new.loc[0, "kind"], "storage")
        self.assertEqual(new.loc[0, "fields_version"], "upgraded")
        with open(path, encoding="utf-8") as f:
            self.assertTrue(f.readline().startswith("# a header line"))
        self.assertEqual(ex.upgrade_file(path, ex.DEAL_COLS_V1, ex.DEAL_COLS, fields.upgrade, lambda m: None), 0)

    def test_the_schema_asks_for_the_new_fields(self):
        ex = fixture.load_extract()
        req = ex.SCHEMA["properties"]["results"]["items"]["properties"]["deals"]["items"]["required"]
        for f in ("kind", "stage", "stage_text", "confidence_basis"):
            self.assertIn(f, req)
        # the Roundup's fields keep their names
        for f in ("deal_type", "buyer", "seller", "asset", "mw", "dollars", "status", "event_date", "story_urls",
                  "confidence"):
            self.assertIn(f, ex.DEAL_COLS)
        self.assertNotIn("evidence", ex.DEAL_COLS)   # outlet text stays in the internal evidence table


if __name__ == "__main__":
    unittest.main()
