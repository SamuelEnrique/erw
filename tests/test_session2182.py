"""Session 2182: the FTA's National Transit Database fuel and energy.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ntd_transit_energy.py on a CSV built here with the FTA's 67
columns (figures made up for the test, not the FTA's): kWh written as MWh and kg of hydrogen as t, a blank with no row
and a zero kept, a Questionable mark carried; a key given twice, a negative quantity, a Questionable column holding a
number and a changed column count each stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2182 -v
"""

import csv
import io
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ntd_transit_energy as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

TAKEN_COLS = [c for _, c, q, _, _ in N.TAKEN] + [q for _, c, q, _, _ in N.TAKEN]
PAD = [f"Extra {i}" for i in range(N.N_COLUMNS - len(N.IDENT) - len(TAKEN_COLS))]
COLS = N.IDENT + TAKEN_COLS + PAD


def row(year="2024", mode="MB", **vals):
    r = dict.fromkeys(COLS, "")
    r.update({"Agency": "Metro Transit", "City": "Town", "State": "MN", "NTD ID": "50027", "Reporter Type": "Full Reporter",
              "Report Year": year, "UZA Name": "Town, MN", "Mode": mode, "Mode Name": "Bus", "TOS": "DO", "Mode VOMS": "12"})
    r.update(vals)
    return r


def file(rows, cols=COLS):
    b = io.StringIO()
    w = csv.DictWriter(b, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    return b.getvalue().encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = N.parse(file([row(**{"Electric Battery (kWh)": "1,500", "Hydrogen (kg)": "2000", "Diesel (gal)": "0",
                                    "Diesel (gal) Questionable": "Questionable"})]), {})
        got = {r["variable"]: r for r in rows}
        self.assertEqual(set(got), {"electric_battery", "hydrogen", "diesel"})
        self.assertEqual((got["electric_battery"]["value"], got["electric_battery"]["unit"]), (1.5, "MWh"))
        self.assertEqual((got["hydrogen"]["value"], got["hydrogen"]["unit"]), (2.0, "t"))
        self.assertEqual((got["diesel"]["value"], got["diesel"]["x_questionable"]), (0.0, "yes"))
        r = got["diesel"]
        self.assertEqual((r["entity"], r["ts_utc"], r["geo"], r["freq"]), ("ntd_mode:50027:MB:DO", "2024-01-01T00:00:00Z", "US-MN", "P1Y"))

    def test_stops(self):
        for content, words in [(file([row(**{"Diesel (gal)": "5"})] * 2), "given twice"),
                               (file([row(**{"Diesel (gal)": "-5"})]), "negative"),
                               (file([row(**{"Diesel (gal)": "5", "Diesel (gal) Questionable": "3.4"})]), "holds"),
                               (file([row(**{"Diesel (gal)": "5"})], COLS[:-1]), "the columns")]:
            with self.assertRaises(RuntimeError) as c:
                N.parse(content, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.TABLE), "power;products")
        self.assertIn(N.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
