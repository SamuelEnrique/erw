"""Session 492: EPA's GHGRP, power plants' reported CO2. Subpart D facilities only; CO2 (non-biogenic and biogenic) in
metric tons, never the CO2e totals; the ORIS codes from EPA's crosswalk; a facility twice in a year stops the run."""

import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ghgrp_power as gp  # noqa: E402

COLS = ["Facility Id", "FRS Id", "Facility Name", "State", "Primary NAICS Code", "Industry Type (subparts)",
        "Total reported direct emissions", "CO2 emissions (non-biogenic) ", "Biogenic CO2 emissions (metric tons)"]


def book(*rows):
    head = [["Summary data collected by the Greenhouse Gas Reporting Program"] + [None] * 8, ["reported"] + [None] * 8,
            ["All emissions data is presented in units of metric tons of carbon dioxide equivalent"] + [None] * 8, COLS]
    buf = io.BytesIO()
    pd.DataFrame(head + [list(r) for r in rows]).to_excel(buf, sheet_name="Direct Point Emitters", header=False, index=False)
    return buf.getvalue()


PLANT = [1000001, 110000, "PSE Ferndale Generating Station", "WA", 221112, "C,D", 300000.0, 299000.0, None]
LANDFILL = [1000031, 110001, "Northwest Regional Landfill", "AZ", 562212, "HH", 50000.0, 1000.0, None]


class Rows(unittest.TestCase):
    def test_subpart_d_and_co2_only(self):
        t = gp.year_rows(book(PLANT, LANDFILL), 2023, "u", "r", {1000001: "54537"})
        self.assertEqual(list(zip(t["entity"], t["variable"], t["value"])), [("ghgrp:1000001", "co2_non_biogenic", 299000.0)])
        self.assertEqual((t["unit"].iloc[0], t["x_oris"].iloc[0], t["geo"].iloc[0]), ("tCO2", "54537", "US-WA"))

    def test_a_facility_twice_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "twice"):
            gp.year_rows(book(PLANT, PLANT), 2023, "u", "r", {})

    def test_the_crosswalk_joins_every_oris_code(self):
        frame = pd.DataFrame([["GHGRP Facility ID", "FACILITY NAME", "ORIS CODE", "ORIS CODE 2"], [1000001, "x", 54537, 54538], [1000019, "y", 57937, None]])
        self.assertEqual(gp.crosswalk(frame), {1000001: "54537;54538", 1000019: "57937"})

    def test_the_newest_zip_and_the_crosswalk(self):
        html = ('<a href="https://www.epa.gov/system/files/other-files/2023-10/2022_data_summary_spreadsheets.zip"></a>'
                '<a href="https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip"></a>'
                '<a href="/system/files/documents/2022-04/ghgrp_oris_power_plant_crosswalk_12_13_21.xlsx"></a>')
        self.assertEqual(gp.links(html), ("https://www.epa.gov/system/files/other-files/2024-10/2023_data_summary_spreadsheets.zip", 2023,
                                          "https://www.epa.gov/system/files/documents/2022-04/ghgrp_oris_power_plant_crosswalk_12_13_21.xlsx"))


if __name__ == "__main__":
    unittest.main()
