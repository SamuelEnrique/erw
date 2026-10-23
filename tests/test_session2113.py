"""Session 2113: the USGS's daily mean streamflow below large hydropower plants.

Energy Research Warehouse (ERW). Tests warehouse/connectors/usgs_streamflow.py on answers built here in the USGS's rdb
form (figures made up for the test, not the USGS's): the gauge named in the header, the day's mean as ft3/s, the
qualification codes kept, a coded day (Ice) left out and counted; another gauge named, a day given twice and columns not
as read each stopping the run; the unit; the sector rule and the holds. No network.

    python -m unittest tests.test_session2113 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))  # appended: warehouse/validate has a build_coverage.py of its own
import usgs_streamflow as U  # noqa: E402
import build_coverage as B  # noqa: E402
import erw_validate as V  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def answer(site="06342500", name="MISSOURI RIVER AT BISMARCK, ND", days=(("2024-01-01", "21000", "A"), ("2024-01-02", "Ice", "A")),
           col="113459_00060_00003"):
    head = ["# Data for the following 1 site(s) are contained in this file", f"#    USGS {site} {name}", "#"]
    body = [f"agency_cd\tsite_no\tdatetime\t{col}\t{col}_cd", "5s\t15s\t20d\t14n\t10s"]
    body += [f"USGS\t{site}\t{d}\t{v}\t{c}" for d, v, c in days]
    return "\n".join(head + body) + "\n"


class Parse(unittest.TestCase):
    def test_answer(self):
        codes = {}
        rows, name = U.parse(answer(days=(("2024-01-01", "21000", "A"), ("2024-01-02", "Ice", "A"), ("2024-01-03", "20500", "P:e"))),
                             "06342500", BASE, codes)
        self.assertEqual((name, len(rows), codes), ("MISSOURI RIVER AT BISMARCK, ND", 2, {"Ice": 1}))
        r = rows[1]
        self.assertEqual((r["entity"], r["ts_utc"], r["value"], r["unit"], r["geo"], r["x_plant"], r["x_qual"]),
                         ("usgs_gauge:06342500", "2024-01-03T00:00:00Z", 20500.0, "ft3/s", "US-ND", "Garrison", "P:e"))

    def test_stops(self):
        for text, words in [(answer(site="06340500"), "not the one gauge asked"),
                            (answer(days=(("2024-01-01", "1", "A"), ("2024-01-01", "2", "A"))), "given twice"),
                            (answer(col="113459_00065_00003"), "columns are not as read"),
                            (answer(days=(("2024-01-01", "Ice", "A"),)), "no day with a value")]:
            with self.assertRaises(RuntimeError) as c:
                U.parse(text, "06342500", BASE, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_unit(self):
        self.assertIn("ft3/s", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("(Decision 64) `ft3/s`", f.read())

    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(U.TABLE), "power")
        self.assertIn(U.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
