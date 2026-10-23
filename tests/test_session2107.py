"""Session 2107: NOAA's U.S. Climate Reference Network, monthly solar radiation.

Energy Research Warehouse (ERW). Tests warehouse/connectors/noaa_uscrn.py on lines built here in USCRN's monthly01 form
(figures made up for the test, not NOAA's): a month written -9999.0 left out and counted, the month's first day as
ts_utc, the grid and the station kept; headers not as read, a short line, a place that changes, a month given twice and
a negative radiation each stopping the run; the unit; the sector rule and the holds. No network.

    python -m unittest tests.test_session2107 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))  # appended: warehouse/validate has a build_coverage.py of its own
import noaa_uscrn as N  # noqa: E402
import build_coverage as B  # noqa: E402
import erw_validate as V  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def line(yrmo, solrad, wban="23907", lon="-102.8134", lat="31.6214"):
    return (f"{wban} {yrmo}  2.623 {lon}   {lat}    30.1    15.2    22.6    22.0    10.4 {solrad:7.1f} C    45.0    12.0    25.0")


HEADS = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 \n" + " ".join(N.HEADS) + " \nThe station WBAN number.\n"


class Parse(unittest.TestCase):
    def test_months(self):
        counts = {}
        rows = N.parse("\n".join([line("202406", 27.4), line("202407", -9999.0), line("202408", 24.1)]), "TX_Monahans_6_ENE", BASE, counts)
        self.assertEqual([r["ts_utc"] for r in rows], ["2024-06-01T00:00:00Z", "2024-08-01T00:00:00Z"])
        self.assertEqual(counts, {"TX_Monahans_6_ENE": 1})
        r = rows[0]
        self.assertEqual((r["entity"], r["value"], r["unit"], r["geo"], r["ba"], r["node"]),
                         ("uscrn:23907", 27.4, "MJ/m2-day", "US-TX", "erco", "TX Monahans 6 ENE"))
        self.assertEqual((r["x_lat"], r["x_lon"], r["x_logger"]), ("31.6214", "-102.8134", "2.623"))
        N.check_heads(HEADS)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            N.check_heads(HEADS.replace("SOLRAD_MONTHLY_AVG", "SOLARAD"))
        for text, words in [(line("202406", 27.4)[:60], "fields"),
                            (line("202406", 27.4) + "\n" + line("202407", 20.0, lat="31.7000"), "place changed"),
                            (line("202406", 27.4) + "\n" + line("202406", 20.0), "given twice"),
                            (line("202406", -3.0), "negative"), (line("202413", 3.0), "not a year and month"),
                            (line("202406", -9999.0), "no month with a value")]:
            with self.assertRaises(RuntimeError) as c:
                N.parse(text, "CA_Merced_23_WSW", BASE, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_unit(self):
        self.assertIn("MJ/m2-day", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("(Decision 63) `MJ/m2-day`", f.read())

    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.TABLE), "power")
        self.assertIn(N.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
