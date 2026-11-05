"""Session 2748: DESNZ's DUKES 5.3, the fuel used in UK electricity generation a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_fuel_used.py on a sheet built here (made up for the test,
not DESNZ's): tables 5.3.B and 5.3.C read by their titles, million tonnes of oil equivalent stated as MWh at 11,630,000 a MTOE,
the "All" rows read as totals; each group's fuels, the other generators and all companies checked; a group not in the map and a
total missed by more than the tolerance stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2748 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_fuel_used as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

M, T, I = "Major power producers [note 2]", "Other generators undertakings in transport ", "Other generators undertakings in industrial and commercial sectors"


def sheet(mpp_total=3.0, group=M, all_total=4.5):
    b = [("Table 5.3.B  Fuel used in generation, million tonnes of oil equivalent (MTOE)",), ("Generator type", "Fuel", 1996, 1997),
         (group, "Gas", 2.0, 2.0), (M, "Nuclear", 1.0, 1.0), ("Total major power producers [note 2]", "All [note 9]", mpp_total, 3.0),
         (T, "Gas [note 6]", 0.5, 0.5), (I, "Gas", 1.0, 1.0), ("Total other generators", "All", 1.5, 1.5),
         ("All generating companies", "Gas [note 6]", 3.5, 3.5), ("All generating companies", "Nuclear", 1.0, 1.0),
         ("Total all generating companies", "All", all_total, 4.5)]
    c = [("Table 5.3.C  Fuel used in generation in Combined Cycle Gas Turbines (CCGT) and conventional steam plants (MTOE)",),
         ("Generator type", "Fuel", 1996, 1997), (M, "Combined cycle gas turbine stations", 2.0, 2.0)]
    return [("Table 5.3",), ("notes",)] + b + c


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, nodes = A.parse_sheet(sheet())
        self.assertEqual(vals[(1996, "mpp:total", "fuel_used")], 3.0)
        self.assertEqual(vals[(1997, "mpp:combined_cycle_gas_turbine_stations", "fuel_used_by_plant")], 2.0)
        self.assertEqual(nodes[("other_transport:gas", "fuel_used")], "Other generators undertakings in transport: Gas")

    def test_frame_units(self):
        import io
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "5.3"
        for r in sheet():
            ws.append(list(r))
        f = io.BytesIO()
        wb.save(f)
        t, _ = A.parse(f.getvalue(), {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""})
        r = dict(zip(t.entity + "|" + t.ts_utc.str[:4], zip(t.value, t.unit)))
        self.assertEqual(r["desnz_fuel:all:total|1996"], (4.5 * 11_630_000, "MWh"))

    def test_stops(self):
        for rows in (sheet(mpp_total=3.1),            # the fuels make 3.0, the total 3.1
                     sheet(all_total=4.6),            # the producers and others make 4.5
                     sheet(group="Independent generators")):
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
