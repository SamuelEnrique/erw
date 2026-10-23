"""Session 958: EIA's Domestic Uranium Production Report (quarterly).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_uranium_production.py on workbooks built here in EIA's
form (figures made up for the test, not EIA's): a facility's quarters, EIA's marks left out, the total row; the counts by
kind at a year's end and a quarter's; a plant's owner, state, capacity and statuses; a heading not as read stopping the
run; the sector rule and the holds. No network.

    python -m unittest tests.test_session958 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_uranium_production as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def sheet(rows, width):
    return pd.DataFrame([r + [None] * (width - len(r)) for r in rows])


def t1():
    pad = [[None]] * 5
    return sheet(pad + [["pounds U3O8"], [None], ["Facility", "Location", "Q1 2026", "Q2 2026"],
                        ["Lost Creek Project", "Sweetwater, Wyoming", 95599, 129444],
                        ["Ross CPP", "Crook, Wyoming", "-", "."],
                        ["Total production", None, 95599, 129444], ["Data source: EIA"]], 4)


def t2():
    pad = [[None]] * 7
    head = ["End of"] + [k + " x" if k != "Total" else k for k in U.KINDS]
    head = ["End of", "Mills - conventional milling a", "Mills - other operations b", "In-situ recovery plants c", "Byproduct recovery plants d", "Total"]
    return sheet(pad + [head, [2025, 0, 1, 6, 0, 7], ["Second quarter of 2026", 1, 0, 5, 0, 6], ["Data source: EIA"]], 6)


def t4():
    pad = [[None]] * 6
    return sheet(pad + [["In-situ recovery plant owner", "In-situ recovery plant name", "County, state", "Production capacity (pounds U3O8 per year)", "Operating status at end of"],
                        [None, None, None, None, "2025", "First-quarter 2026"],
                        ["Lost Creek Isr Llc", "Lost Creek Project", "Sweetwater,\nWyoming", 2000000, "operating", "operating"],
                        ["Total production capacity", None, None, 2000000]], 6)


class Tables(unittest.TestCase):
    def test_production(self):
        marks = {}
        t = pd.DataFrame(U.table1(t1(), BASE, marks))
        self.assertEqual(len(t), 4)
        self.assertEqual(marks, {"-": 1, ".": 1})
        a = t[(t.entity == "eia_u3o8:lost_creek_project") & (t.ts_utc == "2026-04-01T00:00:00Z")].iloc[0]
        self.assertEqual((a.value, a.unit, a.geo, a.freq), (129444.0, "lb", "US-WY", "P3M"))
        self.assertEqual(t[t.entity == "eia_u3o8:total"].geo.unique().tolist(), ["US"])

    def test_counts(self):
        t = pd.DataFrame(U.table2(t2(), BASE)).set_index(["entity", "ts_utc"])
        self.assertEqual(t.loc[("eia_uranium_facilities:isr_plants", "2025-01-01T00:00:00Z")].value, 6.0)
        self.assertEqual(t.loc[("eia_uranium_facilities:total", "2026-04-01T00:00:00Z")].freq, "P3M")

    def test_plants(self):
        p = U.plants(t4(), BASE, "isr")
        self.assertEqual(len(p), 1)
        self.assertEqual((p[0]["entity_id"], p[0]["geo"], p[0]["operator"], p[0]["x_capacity_unit"], p[0]["x_status_first_quarter_2026"]),
                         ("eia_uranium_facility:lost_creek_project", "US-WY", "Lost Creek Isr Llc", "pounds U3O8 per year", "operating"))

    def test_stops(self):
        bad = t1()
        bad.iloc[7, 0] = "Plant"
        with self.assertRaises(RuntimeError):
            U.table1(bad, BASE, {})
        with self.assertRaises(RuntimeError):
            U.plants(t4(), BASE, "mill")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = f.read().replace("\r\n", "\n")
        for name in (U.SERIES, U.ENTITIES):
            self.assertEqual(B.sector_of(name), "uranium")
            self.assertIn(name, R.STORAGE_HELD)
            self.assertIn(f"  - {name}\n", live)


if __name__ == "__main__":
    unittest.main()
