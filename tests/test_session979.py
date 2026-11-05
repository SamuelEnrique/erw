"""Session 979: Berkeley Lab's operating hybrid power plants.

Energy Research Warehouse (ERW). Tests warehouse/connectors/lbnl_hybrid_plants.py on a sheet built here in the data
file's form (figures made up for the test, not LBNL's): the plant's id and fields, a "missing" id named by the plant, a
date written as a day and an empty date left empty; a heading not as read and an id given twice stopping the run; the
sector rule and the hold (internal, so not in the release package). No network.

    python -m unittest tests.test_session979 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import lbnl_hybrid_plants as H  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
COLS = H.NAMED[:4] + ["Region"] + H.NAMED[4:] + list(H.FIELDS)[1:]


def frame(rows):
    out = []
    for r in rows:
        d = {c: None for c in COLS}
        d.update(r)
        out.append(d)
    return pd.DataFrame(out, columns=COLS)


ROWS = [{"State": "WA", "EIA Plant name": "Wild Horse", "EIA Plant ID": 56322, "Total Capacity, Generators and Storage (MW)": 273.1,
         "Type": "Wind+PV", "Final Type": "Wind+PV", "Generator 1 Online Date": pd.Timestamp("2006-12-01"), "Battery Online Date": pd.NaT},
        {"State": "TX", "EIA Plant name": "Myrtle Solar + Storage (TX)", "EIA Plant ID": "missing", "Type": "PV+Storage", "Final Type": "PV+Storage"}]


class Plants(unittest.TestCase):
    def test_rows(self):
        t = H.plants(frame(ROWS), BASE).set_index("entity_id")
        a = t.loc["lbnl_hybrid:56322"]
        self.assertEqual((a["name"], a.geo, a.capacity_mw, a.x_generator1_online, a.x_battery_online), ("Wild Horse", "US-WA", 273.1, "2006-12-01", ""))
        self.assertIn("lbnl_hybrid:none-myrtle-solar-storage-tx", t.index)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            H.plants(frame(ROWS).rename(columns={"Region": "Area"}), BASE)
        with self.assertRaises(RuntimeError):
            H.plants(frame([ROWS[0], ROWS[0]]), BASE)


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(H.NAME), "power")
        self.assertNotIn(H.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {H.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
