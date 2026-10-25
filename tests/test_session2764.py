"""Session 2764: Statistics Austria's energy balances, Austria's electricity balance a year from 1970.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statat_energy_balance.py on an .ods file built here (made up for the
test, not Statistics Austria's): the sheet read by streaming its content.xml, repeated cells and rows expanded; the MWh block's
hierarchy (balance item, plant type, owner, fuel, sub-fuel) made entities; a breakdown not yet split counted, not checked; a row
that is 0 in every year left out; the energy sector's branches from the year its block begins; the balance identities, a parent
against its parts and the sectors checked; a parent missing its parts, a label not in the structure and a broken identity
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2764 -v
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
import statat_energy_balance as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = len(A.YEARS)
NS = ('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
      'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"')


def cell(v):
    if v is None:
        return "<table:table-cell/>"
    if isinstance(v, str):
        return f"<table:table-cell office:value-type=\"string\"><text:p>{escape(v)}</text:p></table:table-cell>"
    return f"<table:table-cell office:value-type=\"float\" office:value=\"{v}\"/>"


def row(label, vals):
    return "<table:table-row>" + cell(label) + "".join(cell(v) for v in vals) + "</table:table-row>"


def same(label, v):
    """A row with one value in every year, written as one repeated cell (the sheet's own compression)."""
    return ("<table:table-row>" + cell(label) + f"<table:table-cell office:value-type=\"float\" office:value=\"{v}\" "
            f"table:number-columns-repeated=\"{N}\"/></table:table-row>")


def ods(hydro=60.0, extra=None, fe=90.0):
    years = [float(y) for y in A.YEARS]
    r = [row("in MWh", []), row(None, years)]
    bal = {"Indigenious primary production": 0, "Imports": 20, "Stock changes": 0, "Recycling/Prod. Trans.": 0, "Exports": 30,
           "Gross inland consumption": -10}
    r += [same(k, v) for k, v in bal.items()]
    r += [same("Transformation input", 0)] + [same(p, 0) for p in A.PLANT]
    r += [same("Transformation output", 110), same("Power plants", 110), same("Public plants", 110), same("from natural gas", 50),
          same("from hydropower", hydro), same("from hydropower <=1MW", 0), same("from hydropower 1 - 10 MW", 0),
          same("from hydropower >10MW", 0), same("Autoproducers", 0)]
    if extra:
        r.append(same(extra, 0))
    r += [same("Energy sector use", 6), same("Transport losses", 4), same("Non energy use", 0), same("Final energy use", fe)]
    r += ["<table:table-row table:number-rows-repeated=\"3\"><table:table-cell/></table:table-row>"]
    r += [row("Final energy use by sectors", []), row("in Terajoule", []), row(None, years), row("Iron and Steel", [1.0] * N),
          row("Final energy use by sectors", []), row("in MWh", []), row(None, years)]
    sectors = {s: 0 for s in A.SECTORS}
    sectors.update({"Iron and Steel": 50, "Railways": 10, "Residential": 30, "Industry": 50, "Transport": 10, "Other Sectors": 30})
    r += [same(s, v) for s, v in sectors.items()]
    by = [None] * 29 + [float(y) for y in A.YEARS[29:]]
    r += [row("Energy sector use", []), row("in MWh", by)]
    for b in A.BRANCHES:
        v = 6.0 if b in ("Electricity, CHP and heat plants", "Total") else 0.0
        r.append(row(b, [None] * 29 + [v] * (N - 29)))
    body = (f"<office:document-content {NS}><office:body><office:spreadsheet>"
            "<table:table table:name=\"Frontpage\">" + row("x", []) + "</table:table>"
            "<table:table table:name=\"Electricity\">" + "".join(r) + "</table:table>"
            "</office:spreadsheet></office:body></office:document-content>")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("content.xml", body)
    return buf.getvalue()


class Parse(unittest.TestCase):
    def frame(self, content):
        vals, sec, br = A.parse_sheet(A.sheet_rows(content, A.SHEET))
        unsplit = A.check(vals, sec, br)
        t, dropped = A.rows_of(vals, sec, br, dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        return t, unsplit, dropped

    def test_rows(self):
        t, unsplit, dropped = self.frame(ods())
        self.assertEqual(unsplit, N)                                         # hydropower's sizes not split in any year
        v = {(e, var): x for e, var, x in zip(t.entity, t.variable, t.value)}
        self.assertEqual(v[("statat_ele:at", "imports")], 20.0)
        self.assertEqual(v[("statat_ele:power_plants:public_plants:hydropower", "transformation_output")], 60.0)
        self.assertNotIn(("statat_ele:power_plants:autoproducers", "transformation_output"), v)  # 0 every year: left out
        self.assertNotIn("indigenous_primary_production", set(t.variable))
        b = t[t.entity == "statat_ele:branch:electricity_chp_and_heat_plants"]
        self.assertEqual((len(b), b.ts_utc.min()), (N - 29, "1999-01-01T00:00:00Z"))
        self.assertEqual(set(t.unit), {"MWh"})
        self.assertGreater(dropped, 0)

    def test_stops(self):
        for content in (ods(hydro=65.0),                                     # the public plants' fuels make 115, it 110
                        ods(fe=95.0),                                        # final energy use is not the remainder
                        ods(extra="from moonlight")):
            with self.assertRaises(RuntimeError):
                self.frame(content)
        with self.assertRaises(RuntimeError):
            A.sheet_rows(ods(), "Gas")

    def test_slug(self):
        self.assertEqual(A.slug("from hydropower <=1MW"), "hydropower_le1mw")
        self.assertEqual(A.slug("Electricity, CHP and heat plants"), "electricity_chp_and_heat_plants")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
