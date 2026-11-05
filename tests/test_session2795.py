"""Session 2795: Statistics Austria's monthly electricity statistics, Austria's net production and balance a month from 2023.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statat_electricity_monthly.py on .ods files built here (made up for
the test, not Statistics Austria's): both sheets read by streaming, "of which" dropped from the labels, "." given no row and "-"
read as zero, GWh stated as MWh; the parts compared with their totals and the two sheets' totals with each other, a difference
counted; the total not compared in a year whose file lists no solar; a row not in the structure and a value not a number
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2795 -v
"""

import io
import os
import sys
import unittest
import zipfile
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statat_electricity_monthly as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

NS = ('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
      'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"')


def cell(v):
    if v is None:
        return "<table:table-cell/>"
    if isinstance(v, str):
        return f"<table:table-cell office:value-type=\"string\"><text:p>{escape(v)}</text:p></table:table-cell>"
    return f"<table:table-cell office:value-type=\"float\" office:value=\"{v}\"/>"


def row(*cells):
    return "<table:table-row>" + "".join(cell(c) for c in cells) + "</table:table-row>"


def ods(total=10.0, solar=True, extra=None, bad=None, summary_total=None):
    months = A.MONTHS
    p = [row("Monthly electricity statistics: net electricity production"), row(None, *months),
         row("Total net production", total, *["."] * 11), row("Conventional thermal", 4.0, *["."] * 11),
         row("of which coal", 1.0, *["."] * 11), row("of which oil", "-", *["."] * 11),
         row("of which natural gas", bad if bad is not None else 3.0, *["."] * 11),
         row("of which combustible renewables", 0.0, *["."] * 11),
         row("of which other combustible fuels (non-renewable)", 0.0, *["."] * 11),
         row("Hydro", 4.0, *["."] * 11), row("of which pure hydro", 3.0, *["."] * 11), row("of which mixed hydro", 1.0, *["."] * 11),
         row("Wind", 1.0 if solar else 2.0, *["."] * 11)]
    if solar:
        p.append(row("Solar", 1.0, *["."] * 11))
    if extra:
        p.append(row(extra, 1.0, *["."] * 11))
    p.append(row("S: STATISTICS AUSTRIA, a note"))
    s = [row("Monthly electricity statistics: summary"), row(None, *months),
         row("Total net production", summary_total if summary_total is not None else total, *["."] * 11),
         row("Total imports", 2.0, *["."] * 11), row("out of which from EU", 1.5, *["."] * 11), row("Total exports", 1.0, *["."] * 11),
         row("out of which to EU", 0.5, *["."] * 11), row("Used for pumped storage", 0.5, *["."] * 11),
         row("Transmission and distribution losses", 0.5, *["."] * 11), row("Total consumption (calculated)", 10.0, *["."] * 11),
         row("S: STATISTICS AUSTRIA, a note")]
    body = (f"<office:document-content {NS}><office:body><office:spreadsheet>"
            "<table:table table:name=\"NetElectricityProduction\">" + "".join(p) + "</table:table>"
            "<table:table table:name=\"SummaryProductionAndSupply\">" + "".join(s) + "</table:table>"
            "</office:spreadsheet></office:body></office:document-content>")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("content.xml", body)
    return buf.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, counted = A.parse({2026: ods()})
        self.assertEqual(counted, [])
        self.assertEqual(vals[(2026, 1, "net_production", "coal")][0], 1.0)
        self.assertEqual(vals[(2026, 1, "net_production", "oil")][0], 0.0)                     # "-" is zero
        self.assertNotIn((2026, 2, "net_production", "coal"), vals)                            # "." has no row
        self.assertEqual(vals[(2026, 1, "imports_from_eu", "total")][0], 1.5)
        t = A.frame(vals, {2026: dict(source="s", source_url="u", retrieved_at="r", vintage="v")})
        x = t[(t.entity == "statat_mele:at") & (t.variable == "net_production")]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.ts_utc.iloc[0]), (10000.0, "MWh", "2026-01-01T00:00:00Z"))

    def test_counted(self):
        _, counted = A.parse({2026: ods(total=12.0)})                                          # the parts make 10, the total 12
        self.assertIn(("2026-01", "total", -2.0), counted)
        _, counted = A.parse({2026: ods(summary_total=10.5)})
        self.assertEqual(counted, [("2026-01", "summary total", 0.5)])
        _, counted = A.parse({2023: ods(total=12.0, solar=False)})                             # no solar row: the total not compared
        self.assertEqual(counted, [])

    def test_stops(self):
        for content in (ods(extra="Moonlight"), ods(bad="n.a.")):
            with self.assertRaises(RuntimeError):
                A.parse({2026: content})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
