"""Session 2387: CENCE's web service EnergiaMensualOficial, Costa Rica's official monthly generation by plant.

Energy Research Warehouse (ERW). Tests warehouse/connectors/cence_costarica_electricity.py on an answer built here in the
service's form (made up for the test, not CENCE's): each record a row in MWh on the month's first day, the plant as a slug,
its source and company kept, the source Intercambio written as interchange, a record without a number not written; an
answer without data, a record of another year, a month outside 1 to 12 and a record without its plant stopping the run;
the sector rule and the holds. No network.

    python -m unittest tests.test_session2387 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import cence_costarica_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""}


def rec(**kw):
    r = {"Empresa": "ICE", "Planta": "Cachí", "Trimestre": "1", "NMes": 1, "Mes": "Enero", "Fuente": "Hidro", "Año": 2025, "MWh": 40646.543}
    r.update(kw)
    return r


def enc(data):
    return json.dumps({"descripcion": "d", "data": data}).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        out = S.parse(enc([rec(), rec(Planta="Intercambio Norte", Fuente="Intercambio", MWh=-1200.5), rec(Planta="Arenal", MWh=None)]), 2025, BASE)
        self.assertEqual(len(out), 2)
        a = out[0]
        self.assertEqual((a["entity"], a["variable"], a["ts_utc"], a["value"], a["unit"], a["geo"], a["x_source"], a["x_company"], a["node"]),
                         ("cence:cachi", "generation", "2025-01-01T00:00:00Z", 40646.543, "MWh", "CR", "Hidro", "ICE", "Cachí"))
        self.assertEqual((out[1]["variable"], out[1]["value"]), ("interchange", -1200.5))

    def test_stops(self):
        for content in (json.dumps({"descripcion": "d"}).encode(), enc([rec(Año=2024)]), enc([rec(NMes=13)]), enc([rec(Planta="")])):
            with self.assertRaises(RuntimeError):
                S.parse(content, 2025, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
