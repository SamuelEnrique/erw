"""Session 2799: Eurostat's isoc_env_ict_nrg, European data centres' electricity consumption a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_data_centres.py on a file built here (made up for the test,
not Eurostat's): GWh written as MWh, EL written GR, the United Kingdom left out; a confidential observation given no row and
counted; a zero kept and counted; a unit not GWH, an activity not DATAC, a value not a number, a negative value and a key given
twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2799 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_data_centres as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)


def line(geo, year, value, unit="GWH", nace="DATAC", conf=""):
    return f"ESTAT:ISOC_ENV_ICT_NRG(1.0),27/07/26 11:00:00,A,{unit},E7000,{nace},{geo},{year},{value},,{conf}"


def data(unit="GWH", nace="DATAC", value="6969.000", twice=False):
    lines = [HEAD, line("IE", 2024, value, unit, nace), line("EL", 2024, "39.8"), line("DK", 2022, "0.000"),
             line("IT", 2024, "", conf="C"), line("UK", 2024, "100.0")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t, counts = A.build(data(), "u", "r", "v")
        self.assertEqual(len(t), 3)
        self.assertEqual(counts["left_out_geo"], ["UK"])
        self.assertEqual((counts["confidential"], counts["zero"]), (1, [("DK", "2022")]))
        self.assertEqual(set(t.geo), {"IE", "GR", "DK"})
        x = t[t.entity == "eurostat_data_centres:IE"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.ts_utc.iloc[0], x.variable.iloc[0]),
                         (6969000.0, "MWh", "2024-01-01T00:00:00Z", "electricity_consumption"))

    def test_stops(self):
        for content in (data(unit="TJ"), data(nace="J63"), data(value="n.a."), data(value="-5.0"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                A.build(content, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        self.assertLessEqual(len(A.NAME), 40)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
