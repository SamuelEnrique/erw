"""Session 3303 (chain 200): the company database's tracers (warehouse/derived/check_companies.py).

Energy Research Warehouse (ERW). Builds three tables from a few input rows written here (test fixtures, not the
warehouse's), runs the tracers on them, then breaks one figure, one name and one row and sees each caught. No network.

    python -m unittest tests.test_session3303_companies -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import companies as C  # noqa: E402
import check_companies as K  # noqa: E402


def frames():
    deals = pd.DataFrame([dict(event_id="deal:1", buyer="Beta Capital", seller="Alpha Power Co", other_parties="",
                               mw="200", dollars="1000", event_date="2026-01-02", technology="gas", state="TX",
                               deal_type="debt")])
    gens = pd.DataFrame([dict(entity_id="eia860:9:1", operator="Alpha Power Co", utility_id="1", nameplate_mw="100",
                              status_date="1990-05-01", energy_source="NG", state="TX", balancing_authority="ERCO",
                              plant_id="9")])
    ms = C.m_deals(deals) + C.m_860m(gens, "eia860m_operating_generators")
    ms, rk, rp = C.resolve(ms, [], [])
    d, a, l = C.build(ms, rk, rp, [], {"energy_deals": "internal", "eia860m_operating_generators": "public"})
    to_str = lambda df: df.astype(str).replace({"nan": ""})
    return to_str(d), to_str(a), to_str(l), {"energy_deals": deals, "eia860m_operating_generators": gens}


class Tracers(unittest.TestCase):
    def test_clean_tables_pass(self):
        d, a, l, inputs = frames()
        self.assertEqual(K.tracers(d, a, l, inputs), [])

    def test_a_changed_figure_is_caught(self):
        d, a, l, inputs = frames()
        d.loc[d["entity_id"] == "company:eia-1", "plants_mw"] = "150.0"
        fails = K.tracers(d, a, l, inputs)
        self.assertTrue(any(x.startswith("4 plants_mw") for x in fails), fails)

    def test_a_name_not_in_its_row_is_caught(self):
        d, a, l, inputs = frames()
        inputs["energy_deals"].loc[0, "buyer"] = "Gamma Partners"
        fails = K.tracers(d, a, l, inputs)
        self.assertTrue(any(x.startswith("2 energy_deals") for x in fails), fails)

    def test_a_row_not_in_its_table_is_caught(self):
        d, a, l, inputs = frames()
        inputs["eia860m_operating_generators"].loc[0, "entity_id"] = "eia860:9:2"
        fails = K.tracers(d, a, l, inputs)
        self.assertTrue(any(x.startswith("1 eia860m_operating_generators") for x in fails), fails)


if __name__ == "__main__":
    unittest.main()
