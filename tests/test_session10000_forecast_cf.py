"""Session 10000 (chain 701, row 10 of docs/state/data_requests_forecast.md): forecast_tool_parameters carries the coal
and biopower plants' capacity factors from site/data/forecast/coal.json and biopower.json (JEDI's saved projects, as
chain 740 read them), each with its cells, beside the other parameters. Reads only the site's forecast files."""
import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("ftp_cf", os.path.join(ROOT, "warehouse", "derived", "forecast_tool_parameters.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ThePlantsCapacityFactors(unittest.TestCase):
    def test_coal_and_biopower(self):
        folder = os.path.join(ROOT, "site", "data", "forecast")
        for plant in ("coal", "biopower"):
            if not os.path.exists(os.path.join(folder, plant + ".json")):
                self.skipTest(f"{plant}.json is not on this checkout")
        d = load().build()[0]
        cf = d[d["variable"] == "capacity_factor"]
        got = {e: (float(v), s, det) for e, v, s, det in zip(cf["entity"], cf["value"], cf["source"], cf["x_detail"])}
        self.assertEqual(got["forecast:coal:coal:us"][:2], (0.85, "nlr:jedi_models"))
        self.assertEqual(got["forecast:biopower:biopower:us"][:2], (0.8, "nlr:jedi_models"))
        self.assertIn("ProjectData!B17", got["forecast:coal:coal:us"][2])
        self.assertIn("forecast:gas:natural_gas:us", got)
        self.assertFalse(d.duplicated(["entity", "variable"]).any())


if __name__ == "__main__":
    unittest.main()
