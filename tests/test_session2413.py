"""Session 2413: Eurostat's gross electricity production by fuel, a year (nrg_bal_peh, GEP).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_electricity_production.py on a small SDMX-CSV and
codelist built here in Eurostat's form (made up for the test, not its figures): GWh written as MWh, EL as GR, the EU
aggregate's blank geo, a blank (flag m) without a row, a zero kept, a country Eurostat's terms leave out; a unit,
product or balance item not expected stopping the run; TOTAL against its top groups plus pumped hydro; the sector rule,
the live-set hold and the release hold (public). No network.

    python -m unittest tests.test_session2413 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_electricity_production as E  # noqa: E402
import build_coverage as B  # noqa: E402

CODES = "TOTAL\tTotal\nG3000\tNatural gas\nN900H\tNuclear heat\nRA000\tRenewables and biofuels\nRA130\tPumped hydro power\n".encode()
HEAD = ",".join(E.HEADER)


def csv(lines, unit="GWH", siec=None):
    out = [HEAD] + [f"ESTAT:NRG_BAL_PEH(1.0),25/09/26 23:00:00,A,GEP,{s if siec is None else siec},{unit},{g},{y},{v},{f}," for g, s, y, v, f in lines]
    return ("\n".join(out) + "\n").encode()


ROWS = [("EL", "TOTAL", "2023", "100", ""), ("EL", "G3000", "2023", "60", ""), ("EL", "RA000", "2023", "35", ""), ("EL", "RA130", "2023", "5", ""),
        ("EL", "N900H", "2023", "0", ""), ("EU27_2020", "TOTAL", "2023", "50", ""), ("EU27_2020", "G3000", "2023", "40", ""),
        ("EU27_2020", "N900H", "2023", "", "m"), ("UK", "TOTAL", "2023", "300", "")]


class Build(unittest.TestCase):
    def test_build(self):
        t, counts = E.build(csv(ROWS), E.siec_names(CODES), "u", "r", "")
        self.assertEqual(len(t), 7)
        self.assertEqual(counts["blank"], 1)
        self.assertEqual(counts["zero"], 1)
        self.assertEqual(counts["left_out_geo"], ["UK"])
        gr = t[t.entity == "eurostat_electricity_production:EL:TOTAL"].iloc[0]
        self.assertEqual((gr.geo, gr.value, gr.unit, gr.ts_utc), ("GR", 100000.0, "MWh", "2023-01-01T00:00:00Z"))
        self.assertEqual(t[t.x_geo_code == "EU27_2020"].geo.unique().tolist(), [""])
        self.assertIn("Natural gas", t[t.x_siec == "G3000"].node.iloc[0])
        compared, off = E.total_check(t)
        self.assertEqual(compared, 2)
        self.assertEqual(list(off.index), [("EU27_2020", "2023-01-01T00:00:00Z")])   # 40 against 50

    def test_stops(self):
        names = E.siec_names(CODES)
        for content in (csv(ROWS[:1], unit="TJ"), csv(ROWS[:1], siec="XX99"), csv([("EL", "TOTAL", "2023", "1O", "")])):
            with self.assertRaises(RuntimeError):
                E.build(content, names, "u", "r", "")
        with self.assertRaises(RuntimeError):
            E.siec_names(b"FOO\tBar\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}"', f.read())


if __name__ == "__main__":
    unittest.main()
