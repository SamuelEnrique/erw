"""Session 2056: FEMA's disaster declarations (OpenFEMA, Disaster Declarations Summaries v2).

Energy Research Warehouse (ERW). Tests warehouse/connectors/fema_disasters.py on a file built here in OpenFEMA's form
(rows made up for the test, not FEMA's): a major disaster's county row and a statewide emergency, the programs
declared, a closed declaration, a row before the start date left out; a declaration type not in the map, a date that
does not read and a missing column stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2056 -v
"""

import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import fema_disasters as F  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def row(**k):
    r = dict(femaDeclarationString="DR-4834-FL", disasterNumber="4834", state="FL", declarationType="DR",
             declarationDate="2024-10-11T00:00:00.000Z", incidentType="Hurricane", declarationTitle="HURRICANE MILTON",
             ihProgramDeclared="1", iaProgramDeclared="0", paProgramDeclared="1", hmProgramDeclared="1",
             incidentBeginDate="2024-10-05T00:00:00.000Z", incidentEndDate="2024-11-01T00:00:00.000Z", disasterCloseoutDate="",
             tribalRequest="0", fipsStateCode="12", fipsCountyCode="57", placeCode="99057", designatedArea="Hillsborough (County)",
             region="4")
    r.update(k)
    return r


def csv_of(rows, drop=None):
    d = pd.DataFrame(rows)
    if drop:
        d = d.drop(columns=[drop])
    return d.to_csv(index=False).encode()


class Parse(unittest.TestCase):
    def test_rows(self):
        rows, n = F.parse(csv_of([row(), row(femaDeclarationString="EM-3600-TX", disasterNumber="3600", state="TX", declarationType="EM",
                                         fipsStateCode="48", fipsCountyCode="000", placeCode="0", designatedArea="Statewide",
                                         disasterCloseoutDate="2025-06-01T00:00:00.000Z"),
                                     row(declarationDate="2014-12-31T00:00:00.000Z", femaDeclarationString="DR-4200-FL")]), BASE, "2015-01-01")
        self.assertEqual(n, 3)
        self.assertEqual(len(rows), 2)
        got = {r["event_id"]: r for r in rows}
        d = got["fema:DR-4834-FL:12057:99057"]
        self.assertEqual((d["event_date"], d["event_type"], d["entity_ids"], d["status"], d["x_programs"], d["x_incident_end"]),
                         ("2024-10-11", "major_disaster", "US-FL;fips:12057", "open", "IH;PA;HM", "2024-11-01"))
        e = got["fema:EM-3600-TX:48000:0"]
        self.assertEqual((e["event_type"], e["entity_ids"], e["status"]), ("emergency", "US-TX", "closed"))

    def test_stops(self):
        for rows in ([row(declarationType="XX")], [row(declarationDate="not a date")]):
            with self.assertRaises(RuntimeError):
                F.parse(csv_of(rows), BASE, "2015-01-01")
        with self.assertRaises(RuntimeError):
            F.parse(csv_of([row()], drop="incidentType"), BASE, "2015-01-01")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(F.TABLE), "power;gas;oil")
        self.assertIn(F.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {F.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
