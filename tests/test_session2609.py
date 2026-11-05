"""Session 2609: the Observatoire Polynesien de l'Energie's energy balance, edition 2024, French Polynesia's electricity a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ope_pf_electricity.py on text lines built here (made up for the
test, not the balance's): the main table's years and its two rows read, the ligature restored, Figure 17's renewable row and the
losses' GWh line taken, French decimals stated in MWh; Figure 17's total off the main table's, a printed EnR rate that misses
and a row of years out of order stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2609 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ope_pf_electricity as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
E = chr(0xE9)
YM = " ".join(str(y) for y in range(2010, 2025))
Y14 = " ".join(str(y) for y in range(2014, 2025))
TOTAL = ["100,0"] * 4 + ["200,0"] * 11
CONS = ["90,0"] * 15


def lines(t17="200,0", rate="25,0%", years14=Y14):
    return ["Sous th" + chr(0xE8) + "mes Indicateurs Unit" + E + "s " + YM + " 2 V 0 a",
            "Produc(cid:31)on totale d'" + E + "lectricit" + E + " GWh " + " ".join(TOTAL) + " ▲ 3,4%",
            "Consomma(cid:31)o ( n C ) Consomma(cid:31)on finale d'" + E + "lectricit" + E + " GWh " + " ".join(CONS) + " ▲ 4,2%",
            years14, "Produc(cid:31)on d'EnR " + E + "lectrique (GWh) " + " ".join(["50,0"] * 11),
            "Produc(cid:31)on totale d'" + E + "lectricit" + E + " (GWh) " + " ".join([t17] + ["200,0"] * 10), "Taux d'EnR dans la",
            " ".join([rate] + ["25,0%"] * 10), "Pertes " + Y14, "en ktep " + " ".join(["1,0"] * 11), "Transport et",
            "en GWh " + " ".join(["7,5"] * 11), "Consommation finale", Y14, "d'" + E + "lectricit" + E, "GWh " + " ".join(["90,0"] * 11)]


class Parse(unittest.TestCase):
    def test_rows(self):
        t = O.parse_lines(lines(), BASE)
        r = {(e.split(":")[-1], ts[:4]): v for e, ts, v in zip(t.entity, t.ts_utc, t.value)}
        self.assertEqual(r[("total", "2010")], 100000.0)
        self.assertEqual(r[("final_consumption", "2024")], 90000.0)
        self.assertEqual(r[("renewable", "2014")], 50000.0)
        self.assertEqual(r[("losses", "2024")], 7500.0)
        self.assertNotIn(("renewable", "2013"), r)
        self.assertEqual(len(t), 15 + 15 + 11 + 11)

    def test_stops(self):
        for bad in (lines(t17="201,0"), lines(rate="30,0%"), lines(years14="2014 2016 2015")):
            with self.assertRaises(RuntimeError):
                O.parse_lines(bad, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(O.NAME), "power")
        self.assertIn(O.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {O.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
