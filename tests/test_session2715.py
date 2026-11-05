"""Session 2715: DESNZ's DUKES 5.13, the UK's interconnector flows a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/desnz_dukes_interconnectors.py on a sheet built here (made up for the
test, not DESNZ's): every heading matched to its pair and variable, GWh stated as MWh and utilisation as a ratio, "[x]" and blank
cells without a row; a heading not in the map, a net that misses its parts, interconnectors that miss the UK's total and a
utilisation above 1 stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2715 -v
"""

import io
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import desnz_dukes_interconnectors as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = list(A.COLUMNS)


def year_row(y, france=(10.0, 2.0, 8.0, 0.5), norway=None, total=None, moyle=(3.0, 1.0, 2.0)):
    v = {"Year": y}
    imp, exp, net, use = france
    v.update({"Imports (France to UK)": imp, "Exports (UK to France)": exp, "Net imports (France to UK)": net,
              "Utilisation (France and UK)": use})
    ti, te, tn = imp, exp, net
    if norway:
        i, e, n, u = norway
        v.update({"Imports (Norway to UK)": i, "Exports (UK to Norway)": e, "Net imports (Norway to UK)": n,
                  "Utilisation (Norway and UK)": u})
        ti, te, tn = ti + i, te + e, tn + n
    ti, te, tn = total or (ti, te, tn)
    v.update({"Total Imports (to UK)": ti, "Total Exports (from UK)": te, "Net imports (to UK)": tn,
              "Transfers to NI (from Scotland)": moyle[0], "Transfers to Scotland (from NI)": moyle[1],
              "Net transfers (to NI from Scotland)": moyle[2], "Transfers to England (from Scotland)": "[x]"})
    return tuple(v.get(h) for h in HEAD)


def sheet(*years, head=None):
    h = list(head or HEAD)
    h[4] = h[4] + " [note 3]"   # the sheet's note marks are read off
    return [("Table 5.13 Net imports and utilisation of interconnectors, (GWh) [note 1]",), ("notes",), tuple(h)] + list(years)


class Parse(unittest.TestCase):
    def test_rows(self):
        v = A.parse_sheet(sheet(year_row(2020), year_row(2021, norway=(5.0, 1.0, 4.0, 0.9))))
        self.assertEqual(v[(2021, "uk_total", "imports")][0], 15.0)
        self.assertEqual(v[(2020, "scotland_northern_ireland", "net_transfers")][0], 2.0)
        self.assertNotIn((2020, "scotland_england", "transfers_to_england"), v)
        self.assertNotIn((2020, "norway", "imports"), v)

    def test_frame_units(self):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "5.13"
        for r in sheet(year_row(2020)):
            ws.append(list(r))
        f = io.BytesIO()
        wb.save(f)
        t = A.parse(f.getvalue(), {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": ""})
        r = dict(zip(t.entity + "|" + t.variable, zip(t.value, t.unit)))
        self.assertEqual(r["desnz_ic:france|imports"], (10000.0, "MWh"))
        self.assertEqual(r["desnz_ic:france|utilisation"], (0.5, "ratio"))

    def test_stops(self):
        bad_head = list(HEAD)
        bad_head[1] = "Imports (Spain to UK)"
        for rows in (sheet(year_row(2020), head=bad_head),
                     sheet(year_row(2020, france=(10.0, 2.0, 9.0, 0.5))),                # net misses its parts by 1 GWh
                     sheet(year_row(2020, total=(12.0, 2.0, 8.0))),                      # total misses the parts by 2 GWh
                     sheet(year_row(2020, france=(10.0, 2.0, 8.0, 1.5))),
                     sheet(year_row(2020, moyle=(3.0, 1.0, 5.0)))):
            with self.assertRaises(RuntimeError):
                A.parse_sheet(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
