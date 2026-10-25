"""Session 2698: DESNZ's Subnational gas consumption statistics, Great Britain's countries and regions, 2005 to 2024.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_subnational_gas_consumption.py on sheets built here (made up
for the test, not DESNZ's): only the countries' and regions' rows read, the Notes column and the means not taken, the
non-consuming meters read as their own item, consumption stated in MWh and meters as a count; a sheet with Inner and Outer London
and no London checked against England; a heading or area not in the map, a note on a region's row, parts that miss their total,
regions that miss England and an Inner and Outer London that miss London stopping the run; the sector rule and the holds. No
network.

    python -m unittest tests.test_session2698 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_subnational_gas_consumption as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

OTHERS = ["North East", "North West", "Yorkshire and The Humber", "East Midlands", "West Midlands", "East", "South East",
          "South West"]
HEAD = ("Code", "Country or region", "Local authority", "Notes", "Number of meters (thousands): Domestic",
        "Number of meters (thousands): Non-Domestic", "Number of meters (thousands): All meters", "Total consumption (GWh): Domestic",
        "Total consumption (GWh): Non-Domestic", "Total consumption (GWh): All meters", "Mean consumption (kWh per meter): Domestic",
        "Median consumption (kWh per meter): Domestic", "Number of  non-consuming meters  (thousands)")


def sheet(london=("London",), total=10.0, england=90.0, note=None, extra_area=None, inner=4.0):
    rows = [("Subnational gas consumption, Great Britain, 2015",), ("notes",), HEAD,
            ("K03000001", "Great Britain (inc unallocated)", "All local authorities", None, 30.0, 3.0, 33.0, 40.0, 60.0, 100.0, 4000.0,
             3000.0, 0.5),
            ("E92000001", "England", "All local authorities", None, 27.0, 2.7, 29.7, 36.0, 54.0, england, 4000.0, 3000.0, 0.4)]
    for r in OTHERS:
        rows.append(("E12", r, "All local authorities", note if r == "East" else None, 3.0, 0.3, 3.3, 4.0, 6.0, total, 4000.0,
                     3000.0, 0.05))
    if "London" in london:
        rows.append(("E12", "London", "All local authorities", None, 3.0, 0.3, 3.3, 4.0, 6.0, 10.0, 4000.0, 3000.0, 0.05))
    if "Inner London" in london:
        rows.append(("E13", "Inner London", "All local authorities", None, 1.0, 0.1, 1.1, 2.0, inner - 2.0, inner, 4000.0, 3000.0,
                     0.02))
        rows.append(("E13", "Outer London", "All local authorities", None, 2.0, 0.2, 2.2, 2.0, 4.0, 6.0, 4000.0, 3000.0, 0.03))
    rows.append(("E06000001", "North East", "Hartlepool", "[Note 1]", 1.0, 0.1, 1.1, 1.0, 1.0, 2.0, 4000.0, 3000.0, 0.01))
    rows.append(("W99", "England and Wales (unallocated)", "Unallocated", None, 1.0, 0.1, 1.1, 1.0, 1.0, 2.0, 4000.0, 3000.0, 0.01))
    if extra_area:
        rows.append(("", extra_area, "All local authorities", None, 1.0, 0.1, 1.1, 1.0, 1.0, 2.0, 4000.0, 3000.0, 0.01))
    return rows


class Parse(unittest.TestCase):
    def test_rows_read(self):
        v = A.parse_sheet(sheet(london=("London", "Inner London")), 2015)
        self.assertEqual(v[("great_britain_inc_unallocated", "consumption_total")][0], 100.0)
        self.assertEqual(v[("east_of_england", "meters_domestic")][0], 3.0)
        self.assertEqual(v[("england", "meters_non_consuming")][0], 0.4)
        self.assertFalse([k for k in v if "mean" in k[1] or "median" in k[1]])
        self.assertEqual(len({a for a, _ in v}), 13)

    def test_london_split_only(self):
        v = A.parse_sheet(sheet(london=("Inner London",)), 2014)
        self.assertNotIn(("london", "consumption_total"), v)
        self.assertEqual(v[("outer_london", "consumption_total")][0], 6.0)

    def test_frame_units(self):
        import io
        import openpyxl
        wb = openpyxl.Workbook()
        wb.active.title = "Cover sheet"
        wb.create_sheet("Notes")
        for y in (2015, 2016):
            ws = wb.create_sheet(str(y))
            for r in sheet():
                ws.append(list(r))
        f = io.BytesIO()
        wb.save(f)
        t = A.parse(f.getvalue(), {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""})
        r = dict(zip(t.entity + "|" + t.ts_utc.str[:4], zip(t.variable, t.value, t.unit, t.geo)))
        self.assertEqual(r["desnz_subgas:great_britain_inc_unallocated:consumption_total|2015"], ("consumption", 100000.0, "MWh", "GB"))
        self.assertEqual(r["desnz_subgas:england:meters_total|2016"], ("meters", 29700.0, "count", "GB-ENG"))
        self.assertEqual(r["desnz_subgas:england:meters_non_consuming|2016"], ("meters", 400.0, "count", "GB-ENG"))

    def test_stops(self):
        bad_head = sheet()
        bad_head[2] = bad_head[2][:4] + ("Number of meters (thousands): Prepayment",) + bad_head[2][5:]
        for fn in (lambda: A.parse_sheet(sheet(extra_area="Isle of Man"), 2015),
                   lambda: A.parse_sheet(sheet(total=12.0), 2015),
                   lambda: A.parse_sheet(sheet(england=95.0), 2015),
                   lambda: A.parse_sheet(sheet(note="[Note 1]"), 2015),
                   lambda: A.parse_sheet(sheet(london=("London", "Inner London"), inner=7.0), 2015),
                   lambda: A.parse_sheet(sheet(london=()), 2015),
                   lambda: A.parse_sheet(bad_head, 2015)):
            with self.assertRaises(RuntimeError):
                fn()


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "gas")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
