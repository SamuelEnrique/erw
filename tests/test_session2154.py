"""Session 2154: the Census Bureau's Building Permits Survey by state, a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/census_bps.py on files built here in the Bureau's form
(figures made up for the test, not the Bureau's): the estimates taken and the reported-only columns not, the value in
dollars, a territory under an older code matched by its name, the regions, divisions and nation not kept; a sum that
differs in a count, a value past the rounding, an area not in the map and a header not as read each stopping the run;
the sector rule and the holds. No network.

    python -m unittest tests.test_session2154 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import census_bps as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
H1 = ("Survey,FIPS,Region,Division,State,,1-unit,,,2-units,,,3-4 units,,,5+ units,,,1-unit rep,,,2-units rep,,,"
      "3-4 units rep       ,,,5+ units rep")
H2 = "Date,State,Code,Code,Name," + ",".join(["Bldgs,Units,Value"] * 8)


def line(year, code, name, nums):
    return f"{year}99,{code},0,0,{name}," + ",".join(str(x) for x in nums + nums)


def text(year=2015, us_delta=(0,) * 12, extra=None, pr_code="43"):
    states = {name: fips for name, fips in C.NAMES.items() if fips not in C.TERRITORIES}
    rows, total = [], [0] * 12
    for k, name in enumerate(states):
        nums = [10 + k, 10 + k, 2000 + k, 1, 2, 300, 0, 0, 0, 1, 20, 4000]
        rows.append(line(year, states[name], name, nums))
        total = [a + b for a, b in zip(total, nums)]
    rows.append(line(year, pr_code, "Puerto Rico", [5] * 12))
    rows.append(line(year, "R1", "Northeast Region", [1] * 12))
    rows.append(line(year, "US", "United States", [a + d for a, d in zip(total, us_delta)]))
    if extra:
        rows.append(extra)
    return "\n".join([H1, H2, " "] + rows) + "\n"


class Parse(unittest.TestCase):
    def test_file(self):
        rounding = {}
        rows = C.parse(text(us_delta=(0, 0, 3) + (0,) * 9), 2015, BASE, rounding)
        self.assertEqual(rounding[2015], 3)
        geos = {r["geo"] for r in rows}
        self.assertEqual(len(geos), 52)  # 50 states, DC and Puerto Rico; the region and the nation not kept
        pr = [r for r in rows if r["geo"] == "US-PR" and r["variable"] == "units_1_unit"][0]
        self.assertEqual((pr["x_fips"], pr["x_code"], pr["value"]), ("72", "43", 5.0))
        al = {r["variable"]: r for r in rows if r["geo"] == "US-AL"}
        self.assertEqual((al["value_1_unit"]["value"], al["value_1_unit"]["unit"]), (2000 * 1000.0, "USD"))
        self.assertEqual((al["units_5_plus_units"]["value"], al["units_5_plus_units"]["unit"]), (20.0, "count"))
        self.assertEqual(len(al), 12)

    def test_stops(self):
        for t, words in [(text(us_delta=(1,) + (0,) * 11), "sum to"), (text(us_delta=(0, 0, 11) + (0,) * 9), "sum to"),
                         (text(extra=line(2015, "66", "Guam", [1] * 12)), "not in the map"),
                         (text().replace("Bldgs,Units,Value", "Bldgs,Units,Cost", 1), "header rows")]:
            with self.assertRaises(RuntimeError) as c:
                C.parse(t, 2015, BASE, {})
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.TABLE), "power")
        self.assertIn(C.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
