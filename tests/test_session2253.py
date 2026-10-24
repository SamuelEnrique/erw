"""Session 2253: Energy-Charts' Belgian public net production and load, an hour.

Energy Research Warehouse (ERW). Tests warehouse/connectors/energy_charts_belgium.py on answers built here in the API's
form (figures made up for the test, not Energy-Charts'): production types, load and trading keyed by the hour's UTC
start, a blank with no row, the shares not taken; hours not an hour apart, a type not in the map and a series shorter
than its hours each stopping the run; the year's address; the sector rule and the hold. No network.

    python -m unittest tests.test_session2253 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import energy_charts_belgium as E  # noqa: E402
import build_coverage as B  # noqa: E402

T0 = 1735686000  # 2024-12-31 23:00 UTC, Belgium's 1 January 2025 00:00


def answer(types, hours=2, step=3600):
    return json.dumps({"unix_seconds": [T0 + i * step for i in range(hours)],
                       "production_types": [{"name": n, "data": d} for n, d in types], "deprecated": False}).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        out = E.parse(answer([("Nuclear", [5000.0, None]), ("Load", [9000.0, 8800.5]), ("Cross border electricity trading", [-300.0, 120.0]),
                              ("Renewable share of load", [20.0, 21.0])]), 2025, {}, counts)
        got = {(r["entity"], r["ts_utc"]): r for r in out}
        n = got[("energy_charts:be:nuclear", "2024-12-31T23:00:00Z")]
        self.assertEqual((n["variable"], n["value"], n["unit"], n["freq"], n["geo"]), ("public_net_power", 5000.0, "MW", "PT1H", "BE"))
        self.assertEqual(got[("energy_charts:be:load", "2025-01-01T00:00:00Z")]["variable"], "load")
        self.assertEqual(got[("energy_charts:be:cross_border_electricity_trading", "2024-12-31T23:00:00Z")]["variable"], "cross_border_trading")
        self.assertEqual((counts["Nuclear blank"], counts["shares not taken"]), (1, 2))
        self.assertEqual(len(out), 5)

    def test_stops(self):
        for content, words in [(answer([("Load", [1.0, 2.0])], step=900), "not an hour apart"),
                               (answer([("Tidal", [1.0, 2.0])]), "not in the map"),
                               (answer([("Load", [1.0])]), "figures for 2 hours")]:
            with self.assertRaises(RuntimeError) as c:
                E.parse(content, 2025, {}, {})
            self.assertIn(words, str(c.exception))

    def test_url(self):
        self.assertEqual(E.url_of(2026, "2026-10-23"), "https://api.energy-charts.info/public_power?country=be&start=2026-01-01&end=2026-10-23")
        self.assertEqual(E.url_of(2020), "https://api.energy-charts.info/public_power?country=be&start=2020-01-01&end=2020-12-31")


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(E.TABLE), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
