"""Session 2007: BOEM's offshore platforms.

Energy Research Warehouse (ERW). Tests warehouse/connectors/boem_platforms.py on a layout page and fixed-width lines
built here in BOEM's form (made up for the test, not BOEM's): the layout read from its table, the structures joined to
their locations and their complex's masters row, removed and active structures, BOEM's dates; a column not in the
layout, a structure twice and a date not as BOEM writes it stopping the run; the entity type platform in the validator;
the sector rule and the holds. No network.

    python -m unittest tests.test_session2007 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import boem_platforms as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def page(fields):
    rows = "".join(f"<tr><td>{s}</td><td>{n}</td><td>{a}</td><td>def</td></tr>" for s, n, a in fields)
    return f"<html><table><tr><th>Start Position</th><th>Item Length</th><th>Column Alias</th><th>Definition</th></tr>{rows}</table></html>"


def fixed(fields, values):
    width = max(s + n - 1 for s, n, _ in fields)
    line = [" "] * width
    for (s, n, _), v in zip(fields, values):
        line[s - 1:s - 1 + n] = list(str(v).ljust(n)[:n])
    return "".join(line)


def lay(names):
    out, pos = [], 1
    for a in names:
        out.append((pos, 12, a))
        pos += 12
    return out


ST = lay(P.NEED["structures"])
LO = lay(P.NEED["locations"])
MA = lay(P.NEED["masters"])


def frames(st_rows, lo_rows, ma_rows):
    st = P.read_fixed("\n".join(fixed(ST, r) for r in st_rows), P.layout(page(ST)), P.NEED["structures"], "structures")
    lo = P.read_fixed("\n".join(fixed(LO, r) for r in lo_rows), P.layout(page(LO)), P.NEED["locations"], "locations")
    ma = P.read_fixed("\n".join(fixed(MA, r) for r in ma_rows), P.layout(page(MA)), P.NEED["masters"], "masters")
    return st, lo, ma


S1 = ["SS", "32", "00000010", "1", "E-1", "WP", "30-AUG-1977", "01-NOV-2016", "1", "1", "N", "TERMIN"]
S2 = ["EI", "100", "00000011", "2", "A", "FIXED", "07-AUG-2001", "", "4", "2", "Y", "APPROVED"]
L1 = ["00000010", "1", "-91.297066", "29.062099", "2"]
M1 = ["00000010", "01284", "15", "7", "00335", "SS032", "N", "N", "N", "N", "Y"]
M2 = ["00000011", "02266", "95", "67", "G02846", "EI100", "Y", "Y", "N", "Y", "N"]


class Build(unittest.TestCase):
    def test_rows(self):
        e, no_loc, no_mas = P.build(*frames([S1, S2], [L1], [M1, M2]), BASE)
        e = e.set_index("entity_id")
        a, b = e.loc["boem_platform:10-1"], e.loc["boem_platform:11-2"]
        self.assertEqual((a.status, a.status_date, a.x_install_date), ("retired", "2016-11-01", "1977-08-30"))
        self.assertEqual((a.lat, a.lon, a.x_water_depth_ft), ("29.062099", "-91.297066", "15"))
        self.assertEqual((b.status, b.status_date, b.lat, b.x_lease_number), ("active", "2001-08-07", "", "G02846"))
        self.assertEqual((no_loc, no_mas), (1, 0))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            P.build(*frames([S1, S1], [L1], [M1]), BASE)
        with self.assertRaises(RuntimeError):
            P.build(*frames([S1[:6] + ["1977-08-30"] + S1[7:]], [L1], [M1]), BASE)
        with self.assertRaises(RuntimeError):
            P.read_fixed("x", P.layout(page(ST[:-1])), P.NEED["structures"], "structures")
        with self.assertRaises(RuntimeError):
            P.layout("<html><table><tr><td>none</td></tr></table></html>")

    def test_dates(self):
        self.assertEqual(P.day("02-JUN-79"), "1979-06-02")
        self.assertEqual(P.day("06/20/2009"), "2009-06-20")
        self.assertEqual(P.day(""), "")


class Registered(unittest.TestCase):
    def test_type_sector_and_holds(self):
        self.assertIn("platform", V.ENTITY_TYPES)
        self.assertEqual(B.sector_of(P.TABLE), "oil;gas")
        self.assertIn(P.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {P.TABLE}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("58. **Session 2007: platform.**", f.read())


if __name__ == "__main__":
    unittest.main()
