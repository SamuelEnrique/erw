"""Session 2239: Red Electrica's REData, Spain's electrical energy balance a month (balance-electrico).

Energy Research Warehouse (ERW). Tests warehouse/connectors/ree_balance.py on an answer built here in REE's form (made
up for the test, not REE's): every series in snake case with its group, the month's first day, negative pumping kept,
a month not ended at retrieval left out and counted; an answer not the balance, a series without values, a value that
is not a number and a month given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2239 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ree_balance as R  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def series(name, sid, values):
    return {"type": name, "id": sid, "attributes": {"title": name, "type": "distinct",
            "values": [{"value": v, "percentage": 0.1, "datetime": d} for d, v in values]}}


def answer(groups, title="Electrical energy balance"):
    return json.dumps({"data": {"type": "Balance", "id": "bal1", "attributes": {"title": title, "last-update": "2026-05-11T21:41:15.000+02:00"}},
                       "included": [{"type": g, "id": g, "attributes": {"title": g, "content": c}} for g, c in groups]})


SEPT = "2026-09-01T00:00:00.000+02:00"
OCT = "2026-10-01T00:00:00.000+02:00"


class Rows(unittest.TestCase):
    def test_rows(self):
        c = {"open_month": 0}
        body = answer([("Renewable", [series("Solar photovoltaic", "1458", [(SEPT, 3000000.5), (OCT, 1000.0)])]),
                       ("Almacenamiento", [series("Pumping consumption", "1472", [(SEPT, -700000.0)])])])
        rows, updated = R.file_rows(body, "u", "2026-10-24T03:00:00Z", "v", c)
        t = R.finish(rows)
        self.assertEqual(c["open_month"], 1)
        self.assertEqual(updated, "2026-05-11T21:41:15.000+02:00")
        s = t[t.variable == "solar_photovoltaic"].iloc[0]
        self.assertEqual((s.ts_utc, s.value, s.unit, s.freq, s.geo, s.x_group, s.x_series_id),
                         ("2026-09-01T00:00:00Z", 3000000.5, "MWh", "P1M", "ES", "Renewable", "1458"))
        self.assertEqual(t[t.variable == "pumping_consumption"].value.iloc[0], -700000.0)

    def test_month_ended(self):
        self.assertTrue(R.month_ended("2026-09", "2026-10-01T00:00:00+02:00"))
        self.assertFalse(R.month_ended("2026-10", "2026-10-24T03:00:00Z"))
        self.assertTrue(R.month_ended("2025-12", "2026-01-01T00:00:00+01:00"))

    def test_stops(self):
        r = "2026-10-24T03:00:00Z"
        for bad in (json.dumps({"errors": [{"status": "400"}]}), answer([], title="Generation structure"),
                    answer([("Renewable", [series("Wind", "10291", [])])]),
                    answer([("Renewable", [series("Wind", "10291", [(SEPT, "lots")])])])):
            with self.assertRaises(RuntimeError):
                R.file_rows(bad, "u", r, "v", {"open_month": 0})
        rows, _ = R.file_rows(answer([("Renewable", [series("Wind", "10291", [(SEPT, 1.0), (SEPT, 2.0)])])]), "u", r, "v", {"open_month": 0})
        with self.assertRaises(RuntimeError):
            R.finish(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(R.NAME), "power")
        self.assertIn(R.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {R.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
