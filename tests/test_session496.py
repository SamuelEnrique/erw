"""Session 496: USGS's U.S. Wind Turbine Database. One row a turbine; capacity_mw from the turbine's kW; the image date
in the standard's form; a repeated case_id, a missing field or an image date that is not M/D/YYYY stops the run."""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import uswtdb as uw  # noqa: E402

TURBINE = {"case_id": 3123493, "faa_ors": "40-097555", "faa_asn": "2021-WTW-7877-OE", "usgs_pr_id": None, "t_state": "OK",
           "t_county": "Ellis County", "t_fips": "40045", "p_name": "25 Mile Creek", "p_year": 2022, "p_tnum": 60, "p_cap": 250.0,
           "t_manu": "Vestas", "t_model": "V150-4.2", "t_cap": 4200, "t_hh": 105.0, "t_rd": 150.0, "t_rsa": 17671.46, "t_ttlh": 180.1,
           "t_conf_atr": 3, "t_conf_loc": 3, "t_img_date": "1/4/2023", "t_img_src": "Vantor", "xlong": -99.75696, "ylat": 36.49125,
           "eia_id": 65511, "t_retrofit": 0, "t_retro_yr": None, "t_offshore": 0}


class Turbines(unittest.TestCase):
    def test_a_turbine(self):
        r = uw.turbines([TURBINE], "u", "r").iloc[0]
        self.assertEqual((r["entity_id"], r["entity_type"], r["geo"], r["capacity_mw"]), ("uswtdb:3123493", "generator", "US-OK", 4.2))
        self.assertEqual((r["image_date"], r["eia_plant_id"], r["retrofit_year"], r["status"]), ("2023-01-04", "65511", "", ""))
        self.assertEqual((r["lat"], r["lon"]), (36.49125, -99.75696))

    def test_a_repeated_case_id_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "given twice"):
            uw.turbines([TURBINE, TURBINE], "u", "r")

    def test_a_missing_field_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "lack"):
            uw.turbines([{k: v for k, v in TURBINE.items() if k != "t_cap"}], "u", "r")

    def test_an_image_date_in_another_form_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "not M/D/YYYY"):
            uw.turbines([dict(TURBINE, t_img_date="2023-01-04")], "u", "r")


if __name__ == "__main__":
    unittest.main()
