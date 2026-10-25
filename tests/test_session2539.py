"""Session 2539: NSI Bulgaria's workbook "Production and deliveries of electricity" (Energy-1.4.Electricity_en.xlsx).

Energy Research Warehouse (ERW). Tests warehouse/connectors/nsi_bulgaria_electricity.py on sheets built here (made up for
the test, not NSI's): both of NSI's month headers ("months of 2019" over I to XII, and "I.2026"), figures held as text,
a label's trailing space, "-" not written, the legend rows passed over, GWh to MWh; a row not in the map, a mark other
than "-", a month header of another form and sources not summing to net production stopping the run; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2539 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nsi_bulgaria_electricity as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
TITLE = ("PRODUCTION AND DELIVERIES OF ELECTRICITY", None, None)
LEGEND = [("- no case registered", None, None), ("x not applicable", None, None)]


def old_year():
    return [TITLE, (None, None, "GWh"), (None, "months of 2019", None), (None, "I", "II"),
            ("Gross production", "40", "30"), ("Net production", "37", "27"), ("Import", "2", "3"), ("Export", "7", "8"),
            ("Total net consumption", "31", "22")]


def new_year(nuclear="13", other="-", head=("I.2026", "II.2026")):
    return [TITLE, (None, None, "(GWh)"), (None,) + head, ("Electricity", None, None),
            ("Gross production", "41", "35"), ("Net production", "37", "32"), ("of which Nuclear", nuclear, "12"),
            ("of which Coal ", "11", "6"), ("of which Petroleum products", "0", "0"), ("of which Natural gas", "2", "2"),
            ("of which Combustible renewables", "1", "1"), ("of which Hydro", "4", "5"), ("of which Wind", "2", "1"),
            ("of which Solar photovoltaic", "3", "3"), ("of which Other sources", other, "2"), ("Import", "8", "8"),
            ("Export", "5", "5"), ("Total net consumption", "40", "34")] + LEGEND


class Parse(unittest.TestCase):
    def test_rows(self):
        t, read = N.parse_sheets({"2019": old_year(), "2026": new_year()}, BASE)
        r = {(e, v, p): x for e, v, p, x in zip(t.entity, t.variable, t.x_period, t.value)}
        self.assertEqual(r[("nsi:bg:total", "gross_production", "2019-02")], 30000.0)
        self.assertEqual(r[("nsi:bg:total", "imports", "2019-01")], 2000.0)
        self.assertEqual(r[("nsi:bg:coal", "net_production", "2026-01")], 11000.0)
        self.assertEqual(r[("nsi:bg:other", "net_production", "2026-02")], 2000.0)
        self.assertNotIn(("nsi:bg:other", "net_production", "2026-01"), r)
        self.assertEqual(len(t), 5 * 2 + 14 * 2 - 1)
        self.assertEqual(read, ["2019 (2019-01 to 2019-02)", "2026 (2026-01 to 2026-02)"])
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [{"2026": new_year() + [("of which Nuclear fusion", "1", "1")]},
               {"2026": new_year(other=".")},
               {"2026": new_year(head=("Jan 2026", "Feb 2026"))},
               {"2026": new_year(nuclear="30")},
               {"2019": old_year()[:3] + [(None, "I", "III")] + old_year()[4:]}]
        for sheets in bad:
            with self.assertRaises(RuntimeError):
                N.parse_sheets(sheets, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.NAME), "power")
        self.assertIn(N.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
