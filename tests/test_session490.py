"""Session 490: EIA's Annual Energy Outlook, electricity Tables 8 and 9, every case. Units mapped into the standard's
vocabulary (GW as MW, billion kWh as MWh, cents per kWh as USD/kWh with the dollar year kept); short tons not taken;
an unknown unit stops the run; a missing value has no row."""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_aeo as ea  # noqa: E402


def api(unit, value, series="elec_NA_sal_NA_tot_NA_usa_bkwh", period="2030", case="cb2026"):
    return dict(period=period, history="PROJECTION", scenario=case, scenarioDescription="Counterfactual Baseline case", tableId="8",
                seriesId=series, seriesName="Electricity : Electricity Sales by Sector : Total", regionId="0-0", value=value, unit=unit)


class Rows(unittest.TestCase):
    def test_units_into_the_vocabulary(self):
        t, skipped = ea.rows([api("BkWh", "4069.278"), api("GW", "1.5", series="cap_x"), api("2025 cents/kWh", "13.5", series="prc_r"),
                              api("nom cents/kWh", "14.0", series="prc_n")], "2026", "u", "r")
        by = {r["entity"].split(":")[1]: r for _, r in t.iterrows()}
        self.assertAlmostEqual(by["elec_NA_sal_NA_tot_NA_usa_bkwh"]["value"], 4069278000.0, places=0)
        self.assertEqual(by["elec_NA_sal_NA_tot_NA_usa_bkwh"]["unit"], "MWh")
        self.assertEqual((by["cap_x"]["value"], by["cap_x"]["unit"]), (1500.0, "MW"))
        self.assertEqual((by["prc_r"]["value"], by["prc_r"]["unit"], by["prc_r"]["x_dollar_year"]), (0.135, "USD/kWh", "2025"))
        self.assertEqual(by["prc_n"]["x_dollar_year"], "nominal")
        self.assertEqual(skipped, {})

    def test_short_tons_are_not_taken(self):
        t, skipped = ea.rows([api("MMst", "1.2", series="emi_nox"), api("st", "3.0", series="emi_hg")], "2026", "u", "r")
        self.assertEqual((len(t), skipped), (0, {"MMst": 1, "st": 1}))

    def test_an_unknown_unit_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "not in the map"):
            ea.rows([api("quads", "1.0")], "2026", "u", "r")

    def test_a_missing_value_has_no_row_and_the_case_is_in_the_entity(self):
        t, _ = ea.rows([api("BkWh", None), api("BkWh", "1.0", case="higheldmd")], "2026", "u", "r")
        self.assertEqual(list(t["entity"]), ["eia_aeo_2026:elec_NA_sal_NA_tot_NA_usa_bkwh:higheldmd"])
        self.assertEqual(list(t["ts_utc"]), ["2030-01-01T00:00:00Z"])


if __name__ == "__main__":
    unittest.main()
