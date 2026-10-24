"""Session 2217: Energinet's hourly production, consumption and exchanges by Danish price area (ProductionConsumptionSettlement).

Energy Research Warehouse (ERW). Tests warehouse/connectors/energinet_production.py on an answer built here in Energinet's
form (made up for the test, not Energinet's): one row a measure, the hour in UTC with a Z, a null left out, the grid
losses not taken, the exchanges' sign kept; an answer not the dataset's, a record missing a field, an hour not in
Energinet's form, a value that is not a number and an hour given twice stopping the run; the sector rule and the holds.
No network.

    python -m unittest tests.test_session2217 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import energinet_production as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(hour="2025-06-01T10:00:00", area="DK1", **over):
    r = {"HourUTC": hour, "HourDK": "2025-06-01T12:00:00", "PriceArea": area, "GridLossTransmissionMWh": 9.5,
         "PowerToHeatMWh": 3.0}
    for i, k in enumerate(E.FIELDS):
        r[k] = float(i + 1)
    r["ExchangeGE_MWh"] = -250.5
    r.update(over)
    return r


def answer(*recs, dataset="ProductionConsumptionSettlement"):
    return json.dumps({"total": len(recs), "dataset": dataset, "records": list(recs)})


class Build(unittest.TestCase):
    def test_rows(self):
        t, total = E.build(answer(rec(), rec(area="DK2", LocalPowerSelfConMWh=None)), "u", "r", "v")
        self.assertEqual(total, 2)
        self.assertEqual(len(t), 2 * len(E.FIELDS) - 1)
        a = t[(t.entity == "energinet:DK1") & (t.variable == "exchange_ge")].iloc[0]
        self.assertEqual((a.value, a.unit, a.ts_utc, a.freq, a.geo, a.node, a.x_hour_dk),
                         (-250.5, "MWh", "2025-06-01T10:00:00Z", "PT1H", "DK", "DK1", "2025-06-01T12:00:00"))
        self.assertNotIn("grid_loss_transmission", set(t.variable))
        self.assertNotIn("local_power_self_con", set(t[t.entity == "energinet:DK2"].variable))

    def test_stops(self):
        short = rec()
        del short["GrossConsumptionMWh"]
        for bad in (answer(rec(), dataset="Elspotprices"), answer(short), answer(rec(hour="2025-06-01 10:00")),
                    answer(rec(CentralPowerMWh="12,5")), answer(rec(), rec())):
            with self.assertRaises(RuntimeError):
                E.build(bad, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
