"""Session 2259: Energy-Charts' Hungary, Romania, Greece and Bulgaria, a day.

Energy Research Warehouse (ERW). Tests warehouse/connectors/energy_charts_southeast.py on answers built here in the
API's form (figures made up for the test, not Energy-Charts'): quarter hours and hours summed over a complete UTC day to
MWh, a part day and a day with a blank not summed and counted, the shares not taken; a period of another length and a
type not in the map each stopping the run; the address; the sector rule and the holds. No network.

    python -m unittest tests.test_session2259 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import energy_charts_southeast as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

DAY = 1735689600  # 2025-01-01 00:00 UTC


def answer(times, types):
    return json.dumps({"unix_seconds": times, "production_types": [{"name": n, "data": d} for n, d in types]}).encode("utf-8")


class Parse(unittest.TestCase):
    def test_quarter_hours(self):
        t = [DAY - 900 + i * 900 for i in range(1 + 96 + 2)]  # the last quarter of 31 December, a whole day, two quarters of 2 January
        counts = {}
        out = E.parse(answer(t, [("Nuclear", [100.0] * len(t)), ("Load", [400.0] * len(t)), ("Renewable share of load", [1.0] * len(t))]),
                      "hu", {}, counts)
        got = {(r["entity"], r["ts_utc"]): r for r in out}
        n = got[("energy_charts:hu:nuclear", "2025-01-01T00:00:00Z")]
        self.assertEqual((n["value"], n["unit"], n["freq"], n["geo"], n["x_periods"], n["variable"]), (2400.0, "MWh", "P1D", "HU", 96, "public_net_energy"))
        self.assertEqual(got[("energy_charts:hu:load", "2025-01-01T00:00:00Z")]["value"], 9600.0)
        self.assertEqual(len(out), 2)
        self.assertEqual(counts["hu part day"], 4)

    def test_hours_and_blank(self):
        t = [DAY + i * 3600 for i in range(48)]
        counts = {}
        out = E.parse(answer(t, [("Solar", [10.0] * 30 + [None] + [10.0] * 17)]), "gr", {}, counts)
        self.assertEqual([(r["ts_utc"], r["value"]) for r in out], [("2025-01-01T00:00:00Z", 240.0)])
        self.assertEqual(counts["gr day with a blank"], 1)

    def test_stops(self):
        for content, words in [(answer([DAY, DAY + 1800], [("Solar", [1.0, 1.0])]), "not 15 or 60"),
                               (answer([DAY, DAY + 3600], [("Tidal", [1.0, 1.0])]), "not in the map")]:
            with self.assertRaises(RuntimeError) as c:
                E.parse(content, "bg", {}, {})
            self.assertIn(words, str(c.exception))

    def test_url(self):
        self.assertEqual(E.url_of("ro", "2026-10-23"), "https://api.energy-charts.info/public_power?country=ro&start=2020-01-01&end=2026-10-23")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.TABLE), "power")
        self.assertIn(E.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
