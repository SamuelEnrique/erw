"""Session 2742: DESNZ's DUKES 5.12, the UK's installed capacity by connection a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_connection.py on a sheet built here (made up for the test,
not DESNZ's): three tables read by their titles, a blank network label carrying the one above, the fuels made entities; each total
checked against its fuels, Great Britain and Northern Ireland against the UK, and the UK's transmission and distribution against
its all; a network not in the map and a row given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2742 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_connection as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def block(title, rows):
    return [(title,), ("Network type", "Generator type", "2011", "2012")] + rows + [()]


def sheet(uk_solar_t=3.0, gb_total=12.0, extra=None, all_net="All"):
    gb = [("Transmission", "Total [note 3]", gb_total, gb_total), ("Transmission", "Coal [note 4]", 10.0, 10.0),
          ("Transmission", "Solar", 2.0, 2.0), ("Distribution", "Total [note 3]", 5.0, 5.0), ("Distribution", "Solar", 5.0, 5.0)]
    ni = [("Transmission", "Total [note 3]", 1.0, 1.0), ("Transmission", "Solar", 1.0, 1.0), ("Distribution", "Total [note 3]", 1.0, 1.0),
          ("Distribution", "Solar", 1.0, 1.0)]
    uk = [("Transmission", "Total [note 3]", 13.0, 13.0), ("Transmission", "Coal [note 4]", 10.0, 10.0),
          ("Transmission", "Solar", uk_solar_t, uk_solar_t), ("Distribution", "Total [note 3]", 6.0, 6.0),
          ("Distribution", "Solar", 6.0, 6.0), (all_net, "Coal [note 4]", 10.0, 10.0), (None, "Solar", 9.0, 9.0),
          ("All", "Total [note 3]", 19.0, 19.0)]
    if extra:
        uk.append(extra)
    return ([("Tables 5.12",), ("notes",)] + block("Table 5.12.A  Electricity network of Great Britain, MW", gb)
            + block("Table 5.12.B  Electricity network of Northern Ireland, MW", ni)
            + block("Table 5.12.C  Electricity network UK total, MW", uk))


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, nodes = A.parse_sheet(sheet())
        self.assertEqual(vals[(2012, "uk:all:solar")], 9.0)               # the blank network label carries "All"
        self.assertEqual(vals[(2011, "ni:distribution:solar")], 1.0)
        self.assertEqual(nodes["gb:transmission:coal"], ("Transmission: Coal", "GB"))
        self.assertEqual(nodes["ni:transmission:total"][1], "GB-NIR")

    def test_stops(self):
        for rows in (sheet(uk_solar_t=4.0),                                # GB and NI make 3, the UK 4 (and the UK total misses)
                     sheet(gb_total=13.0),                                 # GB's fuels make 12, its total 13
                     sheet(all_net="Interconnector"),
                     sheet(extra=("Distribution", "Solar", 6.0, 6.0))):
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
