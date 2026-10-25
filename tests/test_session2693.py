"""Session 2693: DESNZ's Subnational electricity consumption statistics, Great Britain's countries and regions, 2005 to 2024.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_subnational_consumption.py on sheets built here (made up for
the test, not DESNZ's): only the countries' and regions' rows read, "Domestic" and "All Domestic" read as one item, consumption
stated in MWh and meters as a count, the means not taken; a heading or area not in the map, parts that miss their total, standard
and E7 that miss the domestic, and regions that miss England stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2693 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_subnational_consumption as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

REGIONS = ["North East", "North West", "Yorkshire and The Humber", "East Midlands", "West Midlands", "East", "London", "South East",
           "South West"]


def old_sheet(extra_area=None, total=10.0, england=90.0):
    head = ("Code", "Country or region", "Local authority", "Number of meters (thousands): Domestic",
            "Number of meters (thousands): Non-Domestic", "Number of meters (thousands): All meters", "Total consumption (GWh): Domestic",
            "Total consumption (GWh): Non-Domestic", "Total consumption (GWh): All meters", "Mean consumption (kWh per meter): Domestic")
    rows = [("Subnational electricity consumption",), ("notes",), head,
            ("", "Great Britain", "All local authorities", 30.0, 3.0, 33.0, 40.0, 60.0, 100.0, 4000.0),
            ("", "England", "All local authorities", 27.0, 2.7, 29.7, 36.0, 54.0, england, 4000.0)]
    for r in REGIONS:
        rows.append(("UKX", r, "All local authorities", 3.0, 0.3, 3.3, 4.0, 6.0, total, 4000.0))
    rows.append(("E06000001", "North East", "Hartlepool", 1.0, 0.1, 1.1, 1.0, 1.0, 2.0, 4000.0))
    if extra_area:
        rows.append(("", extra_area, "All local authorities", 1.0, 0.1, 1.1, 1.0, 1.0, 2.0, 4000.0))
    return rows


def new_sheet(e7=1.0):
    head = ("Code", "Country or region", "Local authority", "Number of meters (thousands): Domestic Standard",
            "Number of meters (thousands): Domestic E7", "Number of meters (thousands): All Domestic",
            "Number of meters (thousands): All Non-Domestic", "Number of meters (thousands): All meters",
            "Total consumption (GWh): Domestic Standard", "Total consumption (GWh): Domestic E7", "Total consumption (GWh): All Domestic",
            "Total consumption (GWh): All Non-Domestic", "Total consumption (GWh): All meters", "Median consumption (kWh per meter): All meters")
    rows = [("Subnational electricity consumption",), head,
            ("K03000001", "Great Britain (inc unallocated)", "All local authorities", 2.0, 1.0, 3.0, 1.0, 4.0, 3.0, e7, 4.0, 6.0, 10.0, 3000.0),
            ("E92000001", "England", "All local authorities", 18.0, 9.0, 27.0, 9.0, 36.0, 27.0, 9.0, 36.0, 54.0, 90.0, 3000.0)]
    for r in REGIONS:
        rows.append(("E12", r, "All local authorities", 2.0, 1.0, 3.0, 1.0, 4.0, 3.0, 1.0, 4.0, 6.0, 10.0, 3000.0))
    return rows


class Parse(unittest.TestCase):
    def test_old_layout(self):
        v = A.parse_sheet(old_sheet(), 2005)
        self.assertEqual(v[("great_britain", "consumption_total")][0], 100.0)
        self.assertEqual(v[("east_of_england", "meters_domestic")][0], 3.0)
        self.assertNotIn(("north_east", "consumption_domestic_e7"), v)
        self.assertFalse([k for k in v if "mean" in k[1]])
        self.assertEqual(len({a for a, _ in v}), 11)

    def test_new_layout(self):
        v = A.parse_sheet(new_sheet(), 2024)
        self.assertEqual(v[("great_britain_inc_unallocated", "consumption_domestic")][0], 4.0)
        self.assertEqual(v[("london", "consumption_domestic_e7")][0], 1.0)

    def test_frame_units(self):
        import io
        import openpyxl
        wb = openpyxl.Workbook()
        wb.active.title = "Cover sheet"
        for y, rows in ((2011, old_sheet()), (2012, new_sheet())):
            ws = wb.create_sheet(str(y))
            for r in rows:
                ws.append(list(r))
        f = io.BytesIO()
        wb.save(f)
        t = A.parse(f.getvalue(), {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""})
        r = dict(zip(t.entity + "|" + t.ts_utc.str[:4], zip(t.variable, t.value, t.unit, t.geo)))
        self.assertEqual(r["desnz_sub:great_britain:consumption_total|2011"], ("consumption", 100000.0, "MWh", "GB"))
        self.assertEqual(r["desnz_sub:england:meters_total|2012"], ("meters", 36000.0, "count", "GB-ENG"))

    def test_stops(self):
        bad_head = old_sheet()
        bad_head[2] = bad_head[2][:3] + ("Number of meters (thousands): Prepayment",) + bad_head[2][4:]
        for fn in (lambda: A.parse_sheet(old_sheet(extra_area="Isle of Man"), 2005), lambda: A.parse_sheet(old_sheet(total=12.0), 2005),
                   lambda: A.parse_sheet(old_sheet(england=95.0), 2005), lambda: A.parse_sheet(new_sheet(e7=2.0), 2024),
                   lambda: A.parse_sheet(bad_head, 2005)):
            with self.assertRaises(RuntimeError):
                fn()


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
