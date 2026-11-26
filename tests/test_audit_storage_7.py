"""Session 10212 (storage audit, finding 7): "MWh of batteries per MW of solar" is not hours the batteries "could carry" solar.

The build-out's chart "Storage against solar" said: "The ratio is the hours the grid's batteries could carry its whole
solar fleet at nameplate output". Battery MWh over solar MW is a ratio of energy; to carry the solar fleet's output the
batteries would need its power too. Measured on EIA-860M's September 2026 inventory
(docs/reviews/storage-model-audit-2026-11-26/measures.json, "battery_vs_solar"): battery MW over solar MW is 0.663 in
CAISO, 0.568 in ERCOT, 0.272 in ISO-NE, 0.047 in MISO, 0.089 in NYISO, 0.034 in PJM, 0.181 in SPP, 0.274 outside the
seven and 0.326 in the United States, so on no grid could the batteries take in or give back the solar fleet's
nameplate output; the chart's own US figure is 0.896 MWh per MW of solar.

Words only (site/app/storage/buildout/view.tsx, the chart's note; docs/methods/storage_buildout.md, the variable's row):
no figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class EnergyNotPower(unittest.TestCase):
    def test_battery_power_is_below_solar_power_on_the_grids_held(self):
        # the owners' snapshot (EIA-860M, September 2026) gives each grid's operating battery MW; places.json the US
        o = json.loads(read("site", "data", "storage_owners.json"))
        self.assertEqual(o["counts"]["vintage"], "2026-09")
        self.assertLess(o["grids"]["caiso"]["operating_mw"], 26034.5)   # CAISO's operating solar MW, same inventory
        self.assertLess(o["grids"]["ercot"]["operating_mw"], 33779.7)   # ERCOT's

    def test_the_note_says_energy_only(self):
        v = read("site", "app", "storage", "buildout", "view.tsx")
        self.assertNotIn("could carry its whole solar fleet", v)
        self.assertIn("The ratio is the batteries' energy counted in hours of the solar fleet's nameplate output", v)
        self.assertIn("It compares energy only: in EIA's newest inventory the batteries' power is below the solar fleet's on every grid", v)
        m = read("docs", "methods", "storage_buildout.md")
        self.assertNotIn("the hours the batteries could carry the solar fleet's nameplate |", m)
        for s in (v, m):
            self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
