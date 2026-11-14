"""Session 3938 (chain 267): request 1 of docs/state/data_requests_forecast.md, and the STEO table's second release.

The GDP implicit price deflator (GDPDIUS) is read annual from 2009 into eia_steo_forecasts, unit index, a year from the
release's own on marked forecast. The table keeps each release (vintage), and the validator keys it by vintage only
when the header says decision 77's words: without them the release of 10 November 2026 was refused as 10,176
duplicate keys. Made-up values; no network.
"""
import datetime as dt
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import eia_steo  # noqa: E402


class TheDeflator(unittest.TestCase):
    def test_annual_rows(self):
        data = [{"period": "2025", "seriesId": "GDPDIUS", "seriesDescription": "GDP Implicit Price Deflator", "value": "100.5", "unit": "Index, 2017 = 100"},
                {"period": "2026", "seriesId": "GDPDIUS", "seriesDescription": "GDP Implicit Price Deflator", "value": "102.0", "unit": "Index, 2017 = 100"}]
        t = eia_steo.rows_annual(data, dt.date(2026, 11, 10), "https://example.invalid/", "2026-11-14T00:00:00Z")
        self.assertEqual(list(t["ts_utc"]), ["2025-01-01T00:00:00Z", "2026-01-01T00:00:00Z"])
        self.assertEqual(set(t["unit"]), {"index"})
        self.assertEqual(set(t["freq"]), {"P1Y"})
        self.assertEqual(list(t["x_kind"]), ["history", "forecast"])
        self.assertEqual(eia_steo.ANNUAL, ["GDPDIUS"])

    def test_the_header_keeps_the_revisions(self):
        import erw_validate
        src = open(eia_steo.__file__, encoding="utf-8").read()
        self.assertIn(erw_validate.REVISIONS_KEPT, src)



class TheForecastParameters(unittest.TestCase):
    """Request 4: forecast_tool_parameters from the forecast tool's committed files, each value as the file holds it."""

    def test_the_rows(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import json
        import forecast_tool_parameters as fp
        d, capex, taxable, gas = fp.build()
        self.assertFalse(d.duplicated(["entity", "variable"]).any())
        wind = d[(d.entity == "forecast:eia_capex:land_based_wind:us") & (d.variable == "overnight_cost")].iloc[0]
        self.assertEqual(wind.value, float(capex["technologies"]["land_based_wind"]["base_usd_per_kw"]))
        self.assertEqual(wind.unit, "USD/kW")
        hr = d[(d.entity == "forecast:gas:natural_gas:us") & (d.variable == "heat_rate")].iloc[0]
        self.assertAlmostEqual(hr.value, gas["heat_rate_btu_per_kwh"] / 1000.0)
        self.assertNotIn("forecast:jedi_taxable:geothermal:us", set(d.entity))   # JEDI's geothermal model has no sales tax line
        self.assertEqual(set(d.unit) - {"USD/kW", "USD/MW", "month", "MW", "year", "MMBtu/MWh", "ratio", "USD/MMBtu", "Btu/ft3"}, set())
        # session 3948 (request 2): JEDI's construction cost per MW, as jedi_costs.json holds it
        costs = json.load(open(os.path.join(ROOT, "site", "data", "forecast", "jedi_costs.json"), encoding="utf-8"))
        al = d[(d.entity == "forecast:jedi_costs:land_based_wind:al") & (d.variable == "construction_cost")].iloc[0]
        self.assertEqual(al.value, costs["technologies"]["land_based_wind"]["states"]["al"]["cost_usd_per_mw"])
        self.assertEqual(al.unit, "USD/MW")


if __name__ == "__main__":
    unittest.main()
