"""Session 2282: Energy-Charts (Fraunhofer ISE), Portugal's public net production by type and load (public_power, pt).

Energy Research Warehouse (ERW). Tests warehouse/connectors/energy_charts_portugal.py on an answer built here in the API's
form (made up for the test, not Energy-Charts'): one row a type and interval, the interval's start from unix seconds,
the freq from the spacing, the derived series left out, a null without a row; an answer not public_power's, uneven
intervals, a value that is not a number, a list of the wrong length and an interval given twice stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2282 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import energy_charts_portugal as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

T0 = 1735686000  # 2024-12-31T23:00:00Z


def answer(step=3600, types=None, secs=None):
    secs = secs or [T0, T0 + step, T0 + 2 * step]
    types = types or [{"name": "Solar", "data": [0.0, None, 5.5]}, {"name": "Load", "data": [30000.0, 29000.0, 28000.0]},
                      {"name": "Residual load", "data": [1.0, 1.0, 1.0]}]
    return json.dumps({"unix_seconds": secs, "production_types": types, "deprecated": False})


class Rows(unittest.TestCase):
    def test_rows(self):
        t = E.finish(E.file_rows(answer(), "u", "r", "v"))
        self.assertEqual(len(t), 5)
        self.assertNotIn("residual_load", set(t.variable))
        first = t[t.variable == "load"].iloc[0]
        self.assertEqual((first.ts_utc, first.freq, first.unit, first.geo, first.value), ("2024-12-31T23:00:00Z", "PT1H", "MW", "PT", 30000.0))
        self.assertEqual(E.finish(E.file_rows(answer(step=900), "u", "r", "v")).freq.iloc[0], "PT15M")

    def test_stops(self):
        for bad in (json.dumps({"data": []}), answer(secs=[T0, T0 + 3600, T0 + 9000]),
                    answer(types=[{"name": "Solar", "data": [1, "x", 2]}]), answer(types=[{"name": "Solar", "data": [1, 2]}])):
            with self.assertRaises(RuntimeError):
                E.file_rows(bad, "u", "r", "v")
        with self.assertRaises(RuntimeError):
            E.finish(E.file_rows(answer(), "u", "r", "v") * 2)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
