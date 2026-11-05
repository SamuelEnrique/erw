"""Session 2497: the Central Statistical Office of Saint Lucia's electricity output and consumption, 2010 to 2023 (LUCELEC's figures).

Energy Research Warehouse (ERW). Tests warehouse/connectors/slu_cso_electricity.py on an HTML table built here (made up
for the test, not the CSO's): thousands of kWh as MWh, kW to MW, the commercial row split by its "*" (hotels included or
not), a cell ".." with no row, a cell out of form counted, the average section's commercial row and the rows not
taken passed over; a header of other years and a row of another width stopping the run; the two publishers in the
registry; the sector rule and the holds. No network.

    python -m unittest tests.test_session2497 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import slu_cso_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
N = len(S.YEARS)


def tr(cells, tag="td"):
    return "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"


def page(years=S.YEARS, short=False):
    rows = [tr(["Category"] + list(years), "th"),
            tr(["Available Capacity", "76,000"] + ["88,400"] * (N - 1)),
            tr(["Average No. of Hotels", "64"] + [".."] * (N - 1)),
            tr(["Sales (kWh x 1000)"] + [""] * N),
            tr(["Commercial Use (including Hotels)", "106,525", "122,098", "122,840", "193,199*", "194,66*"] + ["200,000*"] * (N - 5)),
            tr(["Domestic Use", "104,209"] + ["10342"] * (N - 1)),
            tr(["Hotel Use"] + ["61,304"] * N),
            tr(["Total Sales", "310,091"] + [".."] * (N - 1)),
            tr(["Loss of transmission"] + ["36,033"] * N),
            tr(["Total Generated (Units generated/purchases (kWhx1000))", "360,251"] + ["400,000"] * (N - 1)),
            tr(["Growth in units generated"] + ["4.9%"] * N),
            tr(["Average Annual Consumption"] + [""] * N),
            tr(["Commercial Use (including Hotels)"] + ["28,769"] * N),
            tr(["", "Source: St. Lucia Electricity Services Limited (LUCELEC)"] + [""] * (N - 1))]
    if short:
        rows.append(tr(["Internal Use", "1"]))
    return "<table>" + "".join(rows) + "</table>"


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        t = S.parse_rows(S.table_rows(page()), BASE, counts)
        r = {(e, v, ts[:4]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("slu_cso:lc:total", "available_capacity", "2010")], 76.0)
        self.assertEqual(r[("slu_cso:lc:commercial_excl_hotels", "sales", "2012")], 122840.0)
        self.assertEqual(r[("slu_cso:lc:commercial_incl_hotels", "sales", "2013")], 193199.0)
        self.assertNotIn(("slu_cso:lc:commercial_incl_hotels", "sales", "2014"), r)
        self.assertEqual(r[("slu_cso:lc:domestic", "sales", "2023")], 10342.0)
        self.assertEqual(r[("slu_cso:lc:total", "generation", "2010")], 360251.0)
        self.assertNotIn(("slu_cso:lc:total", "sales", "2011"), r)
        self.assertEqual(counts, {"cells out of form": 1})
        self.assertEqual(len(t), N + (N - 1) + N + N + 1 + N + N)
        self.assertEqual(set(t.unit[t.variable == "available_capacity"]), {"MW"})

    def test_stops(self):
        for bad in (page(years=[str(y) for y in range(2009, 2023)]), page(short=True), "<p>none</p>"):
            with self.assertRaises(RuntimeError):
                S.parse_rows(S.table_rows(bad), BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))
        self.assertNotEqual(S.SOURCE, S.SOURCE_LUCELEC)


if __name__ == "__main__":
    unittest.main()
