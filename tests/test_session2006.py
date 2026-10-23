"""Session 2006: NOAA CPC's population-weighted degree days, a day.

Energy Research Warehouse (ERW). Tests warehouse/connectors/noaa_cpc_degree_days.py on files built here in CPC's form
(figures made up for the test, not CPC's): a state's and a division's rows, CONUS's geo, an empty cell left out; the first
lines not as read, a region twice, a negative or decimal value and a state not in the map stopping the run; the sector
rule and the holds. No network.

    python -m unittest tests.test_session2006 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import noaa_cpc_degree_days as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def states(body, product="Daily Heating Degree Days"):
    return f"Product: {product}\nRegions: CPC::Regions::StatesCONUS\nWeights: Population\nRegion|20260101|20260102|\n" + body


def divisions(body):
    return "Product: Daily Cooling Degree Days\nRegions: CPC::Regions::CensusDivisions\nWeights: Population\nRegion|20260101|20260102|\n" + body


class Parse(unittest.TestCase):
    def test_rows(self):
        r = C.parse(states("TX|18|19|\nCA|13||\n"), "StatesCONUS", "Heating", BASE)
        got = {(x["entity"], x["ts_utc"][:10]): x for x in r}
        self.assertEqual(len(r), 3)
        self.assertEqual(got[("cpc_dd:TX", "2026-01-02")]["value"], 19.0)
        self.assertEqual((got[("cpc_dd:TX", "2026-01-01")]["variable"], got[("cpc_dd:TX", "2026-01-01")]["unit"]), ("hdd", "degF-day"))
        self.assertEqual(got[("cpc_dd:CA", "2026-01-01")]["geo"], "US-CA")
        d = C.parse(divisions("1|0|1|\nCONUS|2|3|\n"), "Population", "Cooling", BASE)
        got = {x["entity"]: x for x in d}
        self.assertEqual((got["cpc_dd:division_1"]["geo"], got["cpc_dd:conus"]["geo"]), ("", "US"))
        self.assertEqual(got["cpc_dd:conus"]["variable"], "cdd")

    def test_stops(self):
        for text, rs, kind in ((states("TX|1|2|\n", "Daily Cooling Degree Days"), "StatesCONUS", "Heating"),
                               (states("TX|1|2|\nTX|1|2|\n"), "StatesCONUS", "Heating"),
                               (states("TX|-1|2|\n"), "StatesCONUS", "Heating"),
                               (states("TX|1.5|2|\n"), "StatesCONUS", "Heating"),
                               (states("PR|1|2|\n"), "StatesCONUS", "Heating"),
                               (divisions("CONUS|1|2|\n"), "StatesCONUS", "Cooling")):
            with self.assertRaises(RuntimeError):
                C.parse(text, rs, kind, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.TABLE), "power;gas")
        self.assertIn(C.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
