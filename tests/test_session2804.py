"""Session 2804: Eurostat's road_if_rchev, European electric vehicle recharging pools, stations and points and their power output.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_ev_recharging.py on files built here (made up for the test,
not Eurostat's): counts kept as counts and kW written as MW, EL written GR, the United Kingdom left out, a zero kept, the flag i
kept, the codelist's names in the node; a type in a unit it is not read in, a value not a number, a negative value and a key
given twice stopping the run; the codelist read; the sector rule and the holds. No network.

    python -m unittest tests.test_session2804 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_ev_recharging as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
NAMES = {"RCHRG_POOL": "Recharging pool", "RCHRG_POOL_HVY": "Recharging pool dedicated to heavy-duty vehicles",
         "RCHRG_STN": "Recharging station", "RCHRG_PNT": "Recharging point"}


def line(infr, geo, unit, year, value, flag=""):
    return f"ESTAT:ROAD_IF_RCHEV(1.0),13/10/26 23:00:00,A,{infr},{geo},{unit},{year},{value},{flag},"


def data(unit="KW", value="6211711", twice=False):
    lines = [HEAD, line("RCHRG_PNT", "DE", "NR", 2024, "163410"), line("RCHRG_POOL", "DE", unit, 2024, value),
             line("RCHRG_POOL_HVY", "EL", "NR", 2024, "0"), line("RCHRG_STN", "PL", "NR", 2024, "5016", "i"),
             line("RCHRG_PNT", "UK", "NR", 2020, "100")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        return A.build(content, NAMES, "u", "r", "v")

    def test_rows(self):
        t, counts = self.build(data())
        self.assertEqual(len(t), 4)
        self.assertEqual((counts["left_out_geo"], counts["zero"]), (["UK"], 1))
        self.assertEqual(set(t.geo), {"DE", "GR", "PL"})
        x = t.set_index("variable")
        self.assertEqual((x.loc["recharging_pools_power", "value"], x.loc["recharging_pools_power", "unit"]), (6211.711, "MW"))
        self.assertEqual((x.loc["recharging_points", "value"], x.loc["recharging_points", "unit"]), (163410.0, "count"))
        self.assertEqual(x.loc["recharging_stations", "x_flag"], "i")
        self.assertEqual(x.loc["recharging_pools_power", "node"], "DE Recharging pool, power output")

    def test_stops(self):
        for content in (data(unit="MW"), data(value="n.a."), data(value="-1"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                self.build(content)

    def test_codelist(self):
        tsv = (chr(10).join(f"{k}\t{v}" for k, v in NAMES.items())).encode("utf-8")
        self.assertEqual(A.type_names(tsv)["RCHRG_STN"], "Recharging station")
        with self.assertRaises(RuntimeError):
            A.type_names(b"RCHRG_PNT\tRecharging point\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
