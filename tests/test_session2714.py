"""Session 2714: DESNZ's DUKES 5.11, the major power producers' power stations in the United Kingdom.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_power_stations.py on sheets built here (made up for the
test, not DESNZ's): one row a station keyed by DESNZ's site code, the country as an ISO 3166-2 code, the list's day read from the
title, wind split onshore and offshore against table 5.11.A, and the conversion of British National Grid coordinates (where
pyproj is installed); a header, country or fuel not in the map, a site code twice, a capacity not positive and a list that misses
the summary stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2714 -v
"""

import importlib.util
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_power_stations as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = dict(source="s", source_url="u", retrieved_at="r", vintage="v")
TITLE = ("Table 5.11 List of major power producer power stations in the United Kingdom operational at the end of May 2026 [note 1]",)


def station(code, fuel="Natural Gas", typ="CCGT", mw=500.0, country="England", x="447000.0", y="425000.0"):
    return ("Co", f"Site {code}", "Fossil Fuel", typ, "No", fuel, None, mw, "HV", country, "Region", "PC1", None, x, y, "2001", code)


def sheet(*stations):
    return [TITLE, ("notes",), tuple(A.HEADER)] + list(stations)


SUMMARY = {"Natural Gas": 500.0, "Onshore Wind": 20.0, "Offshore Wind": 300.0, "Total": 820.0}
GOOD = [station("GAS-1"), station("WON-1", "Wind", "Onshore", 20.0, "Scotland"), station("WOF-1", "Wind", "Offshore", 300.0, "Northern Ireland", "147232", "530243")]


class Build(unittest.TestCase):
    def test_rows(self):
        t, day = A.build(sheet(*GOOD), SUMMARY, BASE, convert=False)
        self.assertEqual(day, "2026-05-31")
        self.assertEqual(list(t.entity_id), ["dukes:GAS-1", "dukes:WOF-1", "dukes:WON-1"])
        r = t.set_index("entity_id").loc["dukes:WOF-1"]
        self.assertEqual((r["geo"], r["capacity_mw"], r["status"], r["status_date"], r["operator"]), ("GB-NIR", 300.0, "operating", "2026-05-31", "Co"))
        self.assertEqual(r["desnz_site_code"], "WOF-1")
        self.assertEqual(list(t.columns[:14]), A.BASE)

    @unittest.skipUnless(importlib.util.find_spec("pyproj"), "pyproj is not installed")
    def test_grid_to_wgs84(self):
        t, _ = A.build(sheet(*GOOD), SUMMARY, BASE)
        r = t.set_index("entity_id").loc["dukes:WOF-1"]  # Belfast's SSE Arena's coordinates
        self.assertAlmostEqual(r["lat"], 54.604, places=2)
        self.assertAlmostEqual(r["lon"], -5.915, places=2)

    def test_as_at(self):
        self.assertEqual(A.as_at("... operational at the end of December 2025 ..."), "2025-12-31")
        with self.assertRaises(RuntimeError):
            A.as_at("Power stations in the United Kingdom")

    def test_stops(self):
        bad_head = sheet(*GOOD)
        bad_head[2] = tuple(A.HEADER[:-1]) + ("Site ID",)
        cases = [bad_head,
                 sheet(*GOOD, station("GAS-1", mw=0.5)),                          # a code twice (and the totals miss)
                 sheet(station("GAS-1", mw=500.0, country="Isle of Man"), *GOOD[1:]),
                 sheet(station("GAS-1", fuel="Peat"), *GOOD[1:]),
                 sheet(station("GAS-1", mw=-500.0), *GOOD[1:]),
                 sheet(station("GAS-1", mw=490.0), *GOOD[1:])]                    # misses 5.11.A by 10 MW
        for rows in cases:
            with self.assertRaises(RuntimeError):
                A.build(rows, SUMMARY, BASE, convert=False)

    def test_summary(self):
        rows = [("Generator Type", "Fuel", "Installed Capacity (MW)"), ("Major power producer", "Coal", 0),
                ("Major power producer", "Total", 12.5), ("Other Generators [note 10]", "Total", 99)]
        self.assertEqual(A.summary_mpp(rows), {"Coal": 0.0, "Total": 12.5})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
