"""Session 2272: Energy-Charts' public net production and load for Austria, Switzerland and Czechia.

Energy Research Warehouse (ERW). Tests warehouse/connectors/energy_charts_central.py on answers built here in the form
of the API's public_power (made up for the test, not Energy-Charts'): an hourly answer kept as given, a quarter-hour
answer averaged to the hour, an hour with a blank or a missing quarter not written and counted, the shares not taken,
load and the others named, uneven timestamps and a series of the wrong length stopping the run; the address; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2272 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import energy_charts_central as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
T0 = 1704063600  # 2023-12-31T23:00:00Z, midnight in Central European time


def answer(step, n, types):
    return json.dumps({"unix_seconds": [T0 + step * i for i in range(n)],
                       "production_types": [{"name": k, "data": v} for k, v in types.items()]}).encode()


class Parse(unittest.TestCase):
    def test_hourly(self):
        c = {}
        rows = E.parse(answer(3600, 3, {"Nuclear": [3000, 3010, None], "Load": [7000, 7100, 7200],
                                        "Renewable share of load": [50, 51, 52]}), "ch", 2024, BASE, c)
        self.assertEqual(len(rows), 5)
        r = rows[0]
        self.assertEqual((r["entity"], r["variable"], r["ts_utc"], r["value"], r["freq"], r["geo"], r["x_resolution"]),
                         ("energy_charts:ch:nuclear", "public_net_power", "2023-12-31T23:00:00Z", 3000.0, "PT1H", "CH", "PT1H"))
        self.assertEqual([x["variable"] for x in rows if x["x_type"] == "Load"], ["load"] * 3)
        self.assertEqual(c, {"ch Nuclear hours not whole": 1, "shares not taken": 3})

    def test_quarter_hours(self):
        c = {}
        rows = E.parse(answer(900, 9, {"Solar": [0, 4, 8, 12, 10, 10, 10, None, 5]}), "cz", 2024, BASE, c)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["ts_utc"], rows[0]["value"], rows[0]["freq"], rows[0]["x_resolution"]),
                         ("2023-12-31T23:00:00Z", 6.0, "PT1H", "PT15M"))
        self.assertEqual(c, {"cz Solar hours not whole": 2})

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            E.parse(json.dumps({"unix_seconds": [T0, T0 + 3600, T0 + 5400], "production_types": []}).encode(), "at", 2024, BASE, {})
        with self.assertRaises(RuntimeError):
            E.parse(answer(3600, 3, {"Solar": [1, 2]}), "at", 2024, BASE, {})
        with self.assertRaises(RuntimeError):
            E.parse(json.dumps({"production_types": []}).encode(), "at", 2024, BASE, {})

    def test_address(self):
        self.assertEqual(E.url_of("at", 2025), "https://api.energy-charts.info/public_power?country=at&start=2025-01-01&end=2025-12-31")
        self.assertEqual(E.url_of("cz", 2026, "2026-10-23"), "https://api.energy-charts.info/public_power?country=cz&start=2026-01-01&end=2026-10-23")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.TABLE), "power")
        self.assertIn(E.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
