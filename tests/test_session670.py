"""Session 670: OpenEI's large-load tariffs, the parser (chain 043).

Energy Research Warehouse (ERW). No OPENEI_API_KEY was on the data machine, so nothing was pulled; these tests check
warehouse/connectors/openei_large_load_tariffs.py on rates built here in the URDB API's documented form (test fixtures,
not any utility's rates). No network.

    python -m unittest tests.test_session670 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import openei_large_load_tariffs as O  # noqa: E402

WD = [[0] * 12 + [1] * 8 + [0] * 4 for _ in range(12)]   # 8 peak hours a weekday
WE = [[0] * 24 for _ in range(12)]


def rate(**k):
    r = dict(label="abc123", name="Large Power Service", utility="Utility A", eiaid=11, sector="Industrial",
             approved=True, startdate=1735689600, peakkwcapacitymin=5000, uri="https://apps.openei.org/IURDB/rate/view/abc123",
             energyratestructure=[[{"rate": 0.05, "unit": "kWh"}], [{"rate": 0.08, "adj": 0.01, "unit": "kWh"}]],
             energyweekdayschedule=WD, energyweekendschedule=WE,
             flatdemandstructure=[[{"rate": 10.0}]], flatdemandmonths=[0] * 12,
             fixedchargefirstmeter=500.0, fixedchargeunits="$/month")
    r.update(k)
    return r


class Parser(unittest.TestCase):
    def test_energy_is_the_hour_weighted_mean(self):
        # weekdays: 16 hours at 0.05, 8 at 0.09; weekends all at 0.05
        want = ((16 * 0.05 + 8 * 0.09) * 5 + 24 * 0.05 * 2) / (24 * 7) * 1000
        self.assertAlmostEqual(O.energy_charge(rate()), round(want, 4))

    def test_demand_flat_plus_time_of_use(self):
        self.assertEqual(O.demand_charge(rate()), 10.0)
        r = rate(demandratestructure=[[{"rate": 2.0}], [{"rate": 6.0}]], demandweekdayschedule=WD)
        self.assertEqual(O.demand_charge(r), 18.0)   # a flat load meets both periods every month

    def test_all_in_at_300_mw(self):
        rows = {x["variable"]: x for x in O.rows_of(rate(), {"11": "TX"}, "u", "r")}
        e, d, f = rows["energy_charge"]["value"], rows["demand_charge"]["value"], rows["fixed_charge"]["value"]
        self.assertAlmostEqual(rows["all_in_300mw"]["value"], round(e + d * 1000 / 730 + f / (300 * 730), 4))
        self.assertEqual(rows["min_demand_mw"]["value"], 5.0)
        self.assertEqual(rows["energy_charge"]["ts_utc"], "2025-01-01T00:00:00Z")
        self.assertEqual(rows["energy_charge"]["geo"], "US-TX")
        self.assertEqual(rows["energy_charge"]["entity"], "openei_urdb:abc123")

    def test_small_unlisted_or_other_sector_rates_are_left_out(self):
        self.assertEqual(O.rows_of(rate(peakkwcapacitymin=500), {"11": "TX"}, "u", "r"), [])
        self.assertEqual(O.rows_of(rate(peakkwcapacitymin=None), {"11": "TX"}, "u", "r"), [])
        self.assertEqual(O.rows_of(rate(), {"12": "TX"}, "u", "r"), [])
        self.assertEqual(O.rows_of(rate(sector="Residential"), {"11": "TX"}, "u", "r"), [])

    def test_a_tier_not_in_kwh_gives_no_energy_figure(self):
        r = rate(energyratestructure=[[{"rate": 0.05, "unit": "kWh daily"}], [{"rate": 0.08, "unit": "kWh"}]])
        vs = {x["variable"] for x in O.rows_of(r, {"11": "TX"}, "u", "r")}
        self.assertNotIn("energy_charge", vs)
        self.assertNotIn("all_in_300mw", vs)

    def test_never_the_bulk_file_and_no_key_asks_nothing(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "openei_large_load_tariffs.py"), encoding="utf-8") as h:
            src = h.read()
        self.assertNotIn("usurdb.csv\"", src)
        self.assertNotIn(chr(0x2014), src)
        old = os.environ.pop("OPENEI_API_KEY", None)
        try:
            from unittest import mock
            with mock.patch("dotenv.dotenv_values", return_value={}), \
                    mock.patch.object(O.ip, "fetch_raw", side_effect=AssertionError("asked")):
                self.assertEqual(O.main([]), 1)
        finally:
            if old is not None:
                os.environ["OPENEI_API_KEY"] = old


if __name__ == "__main__":
    unittest.main()
