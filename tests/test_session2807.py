"""Session 2807: Destatis's monthly report on electricity and heat generation by energy source (general supply plants).

Energy Research Warehouse (ERW). Tests warehouse/connectors/destatis_electricity_monthly.py on a page built here (made up for
the test, not Destatis's): the month read from the caption, "." given no row and "-" (or "- -") read as zero, digits read
whatever their grouping and an irregular grouping counted, the labels' slugs; the parts compared with the total and gross with
net, a case counted; no caption month, a header not the report's, a cell neither number, "." nor "-", and no total row
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2807 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import destatis_electricity_monthly as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

NB = chr(0xa0)
HEAD = ("<thead><tr><th>Energietr" + chr(0xe4) + "ger</th><th>brutto</th><th>netto</th></tr><tr><th>insgesamt</th><th>darunter</th>"
        "<th>KWK</th></tr><tr><th>MWh</th></tr></thead>")


def row(label, *cells):
    return "<tr><td class=\"Vorspalte\">" + label + "</td>" + "".join(f"<td class=\"right\">{c}</td>" for c in cells) + "</tr>"


def page(caption="Elektrizit" + chr(0xe4) + "ts- und W" + chr(0xe4) + "rmeerzeugung nach Energietr" + chr(0xe4) + "gern, Juli 2026",
         head=HEAD, cell="2" + NB + "000", total=True, net="1" + NB + "900"):
    rows = [row("Braunkohlen" + NB + "insgesamt", cell, net, ".", "10" + NB + "420" + NB + "92", "-" + NB + "-" + NB),
            row("Erdgas," + NB + "Erd" + chr(0xf6) + "lgas", "1" + NB + "000", "950", "500", "600", "400"),
            row("Kernenergie", "-" + NB, "-" + NB, "-" + NB, "-" + NB, "-" + NB)]
    if total:
        rows.append(row("Insgesamt", "3" + NB + "100", "2" + NB + "900", "600", "1" + NB + "700" + NB + "000", "500"))
    s = (f"<html><body><table class=\"wide\"><caption>{caption}</caption>{head}<tbody>" + "".join(rows) + "</tbody></table>"
         "<p>Stand&nbsp;7. Oktober 2026</p></body></html>")
    return s.encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        month, rows, irregular, stand = A.parse(page())
        self.assertEqual((month, stand), ((2026, 7), "7. Oktober 2026"))
        self.assertEqual(len(irregular), 1)                                  # "10 420 92"
        v = {(lab, k): x for lab, k, x, _ in rows}
        self.assertEqual(v[("Braunkohlen insgesamt", "net_heat_generation")], 1042092.0)
        self.assertIsNone(v[("Braunkohlen insgesamt", "net_generation_chp")])
        self.assertEqual(v[("Braunkohlen insgesamt", "net_heat_generation_chp")], 0.0)  # "- -"
        t = A.frame(month, rows, "r", "v")
        self.assertEqual(len(t), 4 * 5 - 1)
        self.assertIn("destatis:de:erdgas_erdoelgas", set(t.entity))
        x = t[(t.entity == "destatis:de") & (t.variable == "gross_generation")]
        self.assertEqual((x.value.iloc[0], x.ts_utc.iloc[0], x.unit.iloc[0]), (3100.0, "2026-07-01T00:00:00Z", "MWh"))

    def test_checks(self):
        parts, off = A.checks(A.parse(page())[1])
        self.assertEqual(parts["gross_generation"][:2], (3000.0, 3100.0))
        self.assertEqual(off, [])
        _, off = A.checks(A.parse(page(net="2" + NB + "100"))[1])           # net above gross
        self.assertEqual(off, [("Braunkohlen insgesamt", "gross_generation", "net_generation")])

    def test_stops(self):
        for content in (page(caption="Elektrizit" + chr(0xe4) + "tserzeugung"), page(head="<thead><tr><th>x</th></tr></thead>"),
                        page(cell="n.a."), page(total=False)):
            with self.assertRaises(RuntimeError):
                A.parse(content)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
