"""Session 951: ONRR's federal production and revenue.

Energy Research Warehouse (ERW). Tests warehouse/connectors/onrr.py on rows built here in the files' form (figures made
up for the test, not ONRR's): the three tables' entities, units and dates; a FIPS code carrying two county names kept
apart; the minerals left out of the annual table; a heading not as read and a commodity not in the map stopping the
run; the sector rules and the holds. No network.

    python -m unittest tests.test_session951 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import onrr as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def frame(name, rows):
    return pd.DataFrame(rows, columns=O.HEADS[name], dtype=str)


class Build(unittest.TestCase):
    def test_monthly(self):
        t = O.build(O.MONTHLY, frame(O.MONTHLY, [["03/01/2024", "Federal", "Offshore", "Oil Prod Vol (bbl)", "100"],
                                                 ["03/01/2024", "Native American", "Onshore", "Coal Prod Vol (tons)", "7"]]), BASE).set_index("entity")
        self.assertEqual((t.loc["onrr_production:federal:offshore:oil"].ts_utc, t.loc["onrr_production:native_american:onshore:coal"].unit),
                         ("2024-03-01T00:00:00Z", "short_ton"))

    def test_annual(self):
        rows = [["2024", "Federal", "Onshore", "Alaska", "Kenai (Post)", "02122", "", "Gas (mcf)", "5"],
                ["2024", "Federal", "Onshore", "Alaska", "Kenai (Pre)", "02122", "", "Gas (mcf)", "6"],
                ["2024", "Federal", "Offshore", "", "", "", "Gulf of America", "Oil (bbl)", "9"],
                ["2024", "Federal", "Onshore", "Nevada", "Churchill", "32001", "", "Geothermal - electrical generation (kilowatt hours)", "2000"],
                ["2024", "Federal", "Onshore", "Utah", "Emery", "49015", "", "Salt (ton)", "3"]]
        t = O.build(O.ANNUAL, frame(O.ANNUAL, rows), BASE).set_index("entity")
        self.assertEqual(len(t), 4)
        self.assertIn("onrr_production:federal:onshore:02122_kenai_post:gas_mcf", t.index)
        self.assertEqual(t.loc["onrr_production:federal:offshore:gulf_of_america:oil_bbl"].geo, "")
        g = t.loc["onrr_production:federal:onshore:32001_churchill:geothermal_electrical_generation_kilowatt_hours"]
        self.assertEqual((g.value, g.unit, g.geo), (2.0, "MWh", "US-NV"))

    def test_revenue(self):
        rows = [["01/01/2003", "Federal", "Not Tied to a Lease", "", "", "", "", "Other revenues", "", "Not tied to a commodity", "", "-0.01"],
                ["01/01/2003", "Federal", "Onshore", "Wyoming", "Campbell", "56005", "", "Royalties", "Coal", "Coal", "Coal", "10"]]
        t = O.build(O.REVENUE, frame(O.REVENUE, rows), BASE).set_index("entity")
        self.assertEqual(t.loc["onrr_revenue:federal:not_tied_to_a_lease:none:other_revenues:none:not_tied_to_a_commodity:none"].value, -0.01)
        self.assertEqual(t.loc["onrr_revenue:federal:onshore:56005_campbell:royalties:coal:coal:coal"].geo, "US-WY")

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            O.build(O.MONTHLY, pd.DataFrame([["03/01/2024", "Federal", "Offshore", "Oil", "1"]], columns=["Date", "Class", "Category", "Commodity", "Volume"]), BASE)
        with self.assertRaises(RuntimeError):
            O.build(O.MONTHLY, frame(O.MONTHLY, [["03/01/2024", "Federal", "Offshore", "Helium Prod Vol (mcf)", "1"]]), BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = f.read().replace("\r\n", "\n")
        for name in (O.MONTHLY, O.ANNUAL, O.REVENUE):
            self.assertEqual(B.sector_of(name), "oil;gas;coal")
            self.assertIn(name, R.STORAGE_HELD)
            self.assertIn(f"  - {name}\n", live)


if __name__ == "__main__":
    unittest.main()
