"""Session 2496: the Central Statistical Office of Grenada's electricity by category, 2000 to 2023.

Energy Research Warehouse (ERW). Tests warehouse/connectors/grenada_cso_electricity.py on an HTML table built here (made
up for the test, not the CSO's): the production row and the consumption volume rows written, figures with and without
thousands separators, an empty cell with no row, the value section (EC$) not taken, the gap of the total from its
categories counted; a header of other years, a row of another width and a row not in the map stopping the run; the
sector rule and the holds. No network.

    python -m unittest tests.test_session2496 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import grenada_cso_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
N = len(S.YEARS)


def tr(cells, tag="td"):
    return "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"


def page(years=S.YEARS, extra=None, short=False):
    rows = [tr(["Category"] + list(years), "th"),
            tr(["Electricity Production Volume (thousands of KWH)", "133,543.7"] + ["1,000.0"] * (N - 2) + ["261209.648"]),
            tr(["Electricity Consumption", "Volume (thousands of KWH)"] + [""] * (N - 1)),
            tr(["Domestic", "45,935.3"] + ["400.0"] * (N - 1)),
            tr(["Commercial", "60,907.9"] + ["500.0"] * (N - 2) + [""]),
            tr(["Industrial", "4,975.6"] + ["50.0"] * (N - 1)),
            tr(["Street Lights", "1,528.9"] + ["5.0"] * (N - 1)),
            tr(["Total", "113,347.7"] + ["955.0"] * (N - 1)),
            tr(["Electricity Consumption", "Value (EC$ thousands)"] + [""] * (N - 1)),
            tr(["Domestic", "25,264.4"] + ["1.0"] * (N - 1))]
    if extra:
        rows.append(extra)
    if short:
        rows.append(tr(["Total", "1"]))
    return "<p>x</p><table id='t'><thead>" + rows[0] + "</thead><tbody>" + "".join(rows[1:]) + "</tbody></table>"


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        t = S.parse_rows(S.table_rows(page()), BASE, counts)
        r = {(e, v, ts[:4]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("grenada_cso:gd:total", "generation", "2000")], 133543.7)
        self.assertEqual(r[("grenada_cso:gd:total", "generation", "2023")], 261209.648)
        self.assertEqual(r[("grenada_cso:gd:domestic", "consumption", "2000")], 45935.3)
        self.assertEqual(r[("grenada_cso:gd:total", "consumption", "2000")], 113347.7)
        self.assertNotIn(("grenada_cso:gd:commercial", "consumption", "2023"), r)
        self.assertEqual(len(t), N + 5 * N - 1)
        self.assertEqual(set(t.unit), {"MWh"})
        self.assertGreater(counts["largest gap between the total and its categories, MWh"], 0)

    def test_stops(self):
        for bad in (page(years=[str(y) for y in range(1999, 2023)]), page(short=True), page(extra=tr(["Hotels"] + ["1"] * N)),
                    "<p>no table</p>"):
            with self.assertRaises(RuntimeError):
                S.parse_rows(S.table_rows(bad), BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
