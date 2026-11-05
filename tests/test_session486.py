"""Session 486: EPA eGRID's plant sheet as an entities table. The workbook in short tons, not the metric one; the plant
code as entity_id; eGRID's own fields under named columns; a repeated plant code stops the run; nothing is filled."""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import egrid as eg  # noqa: E402

CODES = ["SEQPLT23", "PNAME", "LAT", "LON", "NAMEPCAP", "UTLSRVNM"] + list(eg.FIELDS)


def sheet(*plants):
    """eGRID's plant sheet: a row of long names, a row of codes, then plants (a dict of code -> value each)."""
    rows = [[f"long name of {c}" for c in CODES], CODES]
    for p in plants:
        rows.append([p.get(c) for c in CODES])
    return pd.DataFrame(rows)


ALAKANUK = {"SEQPLT23": 1, "YEAR": 2023, "PSTATABB": "AK", "PNAME": "Alakanuk", "ORISPL": 57053, "LAT": 62.6833, "LON": -164.6544,
            "NAMEPCAP": 0.8, "UTLSRVNM": "Alaska Village Elec Coop, Inc", "FIPSST": 2, "FIPSCNTY": None, "PLNGENAN": 0.0, "PLCO2AN": None}


class Plants(unittest.TestCase):
    def test_a_plant_row(self):
        t = eg.plants(sheet(ALAKANUK), 2023, "u", "r")
        r = t.iloc[0]
        self.assertEqual((r["entity_id"], r["entity_type"], r["name"], r["geo"]), ("egrid:57053", "plant", "Alakanuk", "US-AK"))
        self.assertEqual((r["capacity_mw"], r["status"], r["vintage"]), (0.8, "", "eGRID2023"))
        self.assertEqual((r["plant_id"], r["fips_state"], r["fips_county"]), ("57053", "02", ""))
        self.assertTrue(r["co2_tons"] == "" or pd.isna(r["co2_tons"]))   # a blank cell stays blank (an empty cell in the CSV)

    def test_a_repeated_plant_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "given twice"):
            eg.plants(sheet(ALAKANUK, ALAKANUK), 2023, "u", "r")

    def test_a_missing_field_stops_the_run(self):
        frame = sheet(ALAKANUK).drop(columns=[CODES.index("PLCO2AN")])
        with self.assertRaisesRegex(RuntimeError, "lacks"):
            eg.plants(frame, 2023, "u", "r")

    def test_the_newest_workbook_in_short_tons(self):
        html = ('<a href="https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_metric_rev2.xlsx"></a>'
                '<a href="https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_rev2.xlsx"></a>'
                '<a href="/system/files/documents/2024-01/egrid2022_data.xlsx"></a>')
        self.assertEqual(eg.workbook_url(html), ("https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_rev2.xlsx", 2023))


if __name__ == "__main__":
    unittest.main()
