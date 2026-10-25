"""Session 2087: the IRS's residential energy credits by state (SOI Historic Table 2).

Energy Research Warehouse (ERW). Tests warehouse/connectors/irs_soi_energy.py on files built here in SOI's form (made up
for the test, not the IRS's): the row of all incomes taken, commas read, amounts in thousands made USD, the US and OA rows
kept with their geo, 2023's split credits; a year's column missing, a state given twice and a figure not a number
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2087 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import irs_soi_energy as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def csv(head, rows):
    return (",".join(head) + "\n" + "\n".join(",".join(f'"{v}"' for v in r) for r in rows) + "\n").encode("latin-1")


H22 = ["STATEFIPS", "STATE", "AGI_STUB", "N07260", "A07260"]
H23 = ["STATEFIPS", "STATE", "AGI_STUB", "N07262", "A07262", "N07265", "A07265"]


class Read(unittest.TestCase):
    def test_2022(self):
        rows = S.read_year(csv(H22, [["00", "US", "0", "3,220,260", "7,983,695"], ["00", "US", "1", "0", "0"],
                                     ["06", "CA", "0", "500,000", "1,200,000"], ["99", "OA", "0", "10", "5"]]), 2022, BASE)
        r = {(x["entity"], x["variable"]): x for x in rows}
        self.assertEqual(len(rows), 6)
        self.assertEqual(r[("irs_soi:US", "residential_energy_credit_returns")]["value"], 3220260)
        self.assertEqual(r[("irs_soi:US", "residential_energy_credit_amount")]["value"], 7983695000)
        self.assertEqual((r[("irs_soi:CA", "residential_energy_credit_amount")]["geo"], r[("irs_soi:OA", "residential_energy_credit_returns")]["geo"]),
                         ("US-CA", ""))
        self.assertEqual(r[("irs_soi:US", "residential_energy_credit_amount")]["unit"], "USD")

    def test_2023(self):
        rows = S.read_year(csv(H23, [["00", "US", "0", "1,518,210", "7,791,024", "2,612,610", "2,324,249"]]), 2023, BASE)
        self.assertEqual(sorted(x["variable"] for x in rows), ["energy_efficient_home_improvement_credit_amount", "energy_efficient_home_improvement_credit_returns",
                                                               "residential_clean_energy_credit_amount", "residential_clean_energy_credit_returns"])

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            S.read_year(csv(H22, [["00", "US", "0", "1", "1"]]), 2023, BASE)
        with self.assertRaises(RuntimeError):
            S.read_year(csv(H22, [["06", "CA", "0", "1", "1"], ["06", "CA", "0", "2", "2"]]), 2022, BASE)
        with self.assertRaises(RuntimeError):
            S.read_year(csv(H22, [["06", "CA", "0", "many", "1"]]), 2022, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.TABLE), "power")
        self.assertIn(S.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
