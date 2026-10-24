"""Session 2224: the IESO's Ontario generation by fuel.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ieso_genfuel.py on a document built here in the IESO's form
(made up for the test, not the IESO's): each fuel's Output an hour, at the hour's start in UTC from the IESO's hour ending
in Eastern Standard Time; the quality kept; CONTROL ACTIONS as control_actions; a fuel without an Output not written; a
document of another kind, a year not the file's, an hour outside 1 to 24, a fuel given twice, a fuel not one of the eight
and a value not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2224 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ieso_genfuel as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r"}


def fuel(name, out="100", q="0"):
    v = f"<Output>{out}</Output>" if out is not None else ""
    return f"<FuelTotal><Fuel>{name}</Fuel><EnergyValue><OutputQuality>{q}</OutputQuality>{v}</EnergyValue></FuelTotal>"


def doc(fuels, year=2026, day="2026-01-01", hour=1, doc_id="GenOutputbyFuelHourly"):
    return (f'<?xml version="1.0" encoding="UTF-8"?><Document docID="{doc_id}" xmlns="http://www.ieso.ca/schema">'
            "<DocHeader><CreatedAt>2026-10-23T06:50:49</CreatedAt></DocHeader>"
            f"<DocBody><DeliveryYear>{year}</DeliveryYear><DailyData><Day>{day}</Day><HourlyData><Hour>{hour}</Hour>"
            + "".join(fuels) + "</HourlyData></DailyData></DocBody></Document>").encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = G.parse(doc([fuel("NUCLEAR", "9602"), fuel("GAS", "3246", "-1"), fuel("SOLAR", None), fuel("CONTROL ACTIONS", "0")]), 2026, BASE)
        by = {r["variable"]: r for r in rows}
        self.assertEqual(set(by), {"generation_nuclear", "generation_gas", "control_actions"})
        self.assertEqual(by["generation_nuclear"]["ts_utc"], "2026-01-01T05:00:00Z")
        self.assertEqual(by["generation_nuclear"]["value"], 9602.0)
        self.assertEqual(by["generation_gas"]["x_quality"], "-1")
        self.assertEqual(by["generation_gas"]["vintage"], "2026-10-23T11:50:49Z")
        self.assertEqual(by["control_actions"]["node"], "CONTROL ACTIONS")
        h24 = G.parse(doc([fuel("HYDRO")], hour=24), 2026, BASE)[0]
        self.assertEqual(h24["ts_utc"], "2026-01-02T04:00:00Z")
        self.assertEqual(h24["unit"], "MWh")

    def test_stops(self):
        for content in (doc([fuel("HYDRO")], doc_id="Demand"), doc([fuel("HYDRO")], year=2025), doc([fuel("HYDRO")], hour=25),
                        doc([fuel("HYDRO"), fuel("HYDRO")]), doc([fuel("COAL")]), doc([fuel("HYDRO", "n/a")]),
                        doc([fuel("HYDRO")], day="2025-12-31")):
            with self.assertRaises(RuntimeError):
                G.parse(content, 2026, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(G.TABLE), "power")
        self.assertIn(G.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
