"""Session 2150: the World Bank's electricity indicators.

Energy Research Warehouse (ERW). Tests warehouse/connectors/wb_wdi_electricity.py on answers built here in the
Indicators API's form (figures made up for the test, not the World Bank's): an aggregate and an empty value left out,
the economy's codes and groups kept, each indicator's table and unit; a page that is not whole, a row of another
indicator and an economy given twice each stopping the run; the unit; the sector rules and the holds (the IEA's table
internal). No network.

    python -m unittest tests.test_session2150 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))  # appended: warehouse/validate has a build_coverage.py of its own
import wb_wdi_electricity as W  # noqa: E402
import build_coverage as B  # noqa: E402
import erw_validate as V  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
ECON = [{"id": "KEN", "iso2Code": "KE", "name": "Kenya", "region": {"id": "SSF", "value": "Sub-Saharan Africa "},
         "incomeLevel": {"value": "Lower middle income"}},
        {"id": "WLD", "iso2Code": "1W", "name": "World", "region": {"id": "NA", "value": "Aggregates"}, "incomeLevel": {"value": "Aggregates"}}]


def answer(ind, rows, total=None):
    return [{"page": 1, "pages": 1, "total": len(rows) if total is None else total, "lastupdated": "2026-10-08"}, rows]


def row(ind, iso3, year, value):
    return {"indicator": {"id": ind}, "countryiso3code": iso3, "date": str(year), "value": value}


class Parse(unittest.TestCase):
    def test_rows(self):
        econ = W.economies(answer(None, ECON))
        self.assertEqual(sorted(econ), ["KEN"])
        ind = "EG.USE.ELEC.KH.PC"
        rows, last = W.parse(answer(ind, [row(ind, "KEN", 2022, 170.5), row(ind, "KEN", 2023, None), row(ind, "WLD", 2022, 3500.0)]),
                             ind, econ, BASE)
        self.assertEqual((len(rows), last), (1, "2026-10-08"))
        r = rows[0]
        self.assertEqual((r["entity"], r["variable"], r["unit"], r["geo"], r["ts_utc"], r["x_region"], r["x_income"]),
                         ("wb:KEN", "electricity_consumption_per_person", "kWh/person", "KE", "2022-01-01T00:00:00Z",
                          "Sub-Saharan Africa", "Lower middle income"))
        self.assertEqual(W.INDICATORS["EG.ELC.ACCS.ZS"][0], "wb_electricity_access_annual")

    def test_stops(self):
        econ = W.economies(answer(None, ECON))
        ind = "EG.ELC.ACCS.ZS"
        for a, words in [(answer(ind, [row(ind, "KEN", 2022, 70.0)], total=5), "not one whole page"),
                         (answer(ind, [row("EG.ELC.RNEW.ZS", "KEN", 2022, 70.0)]), "a row of"),
                         (answer(ind, [row(ind, "KEN", 2022, 70.0), row(ind, "KEN", 2022, 71.0)]), "given twice")]:
            with self.assertRaises(RuntimeError) as c:
                W.parse(a, ind, econ, BASE)
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_unit(self):
        self.assertIn("kWh/person", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("(Decision 68) `kWh/person`", f.read())

    def test_sector_and_holds(self):
        for t in W.TABLES:
            self.assertEqual(B.sector_of(t), "power")
        self.assertIn("wb_electricity_access_annual", R.STORAGE_HELD)
        self.assertNotIn("wb_iea_electricity_annual", R.STORAGE_HELD)  # internal until the IEA's terms are read
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            text = f.read().replace("\r\n", "\n")
        for t in W.TABLES:
            self.assertIn(f"  - {t}\n", text)


if __name__ == "__main__":
    unittest.main()
