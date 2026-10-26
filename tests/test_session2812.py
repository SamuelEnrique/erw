"""Session 2812: Eurostat's nrg_inf_nuc, Europe's nuclear fuel cycle facilities and nuclear heat a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_nuclear_facilities.py on a file built here (made up for
the test, not Eurostat's): tSWU written as SWU, tonnes of heavy metal as t, ktoe as MWh (times 11,630), EL written GR, the
United Kingdom left out, the burnup not written, a blank given no row, a zero kept; production compared with capacity, a case
above counted; an item in another unit, an item not expected, a value not a number, a negative value and a key given twice
stopping the run; the codelist read; the sector rule and the holds. No network.

    python -m unittest tests.test_session2812 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_nuclear_facilities as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
NAMES = {"CAP_EN": "Enrichment capacity (tSWU)", "PRD_FF": "Production of fresh fuel elements (tHM)",
         "PRDCAP_FF": "Production capacity of fresh fuel elements (tHM)", "PRD_MOXF": "Production of MOX fuel elements (tHM)",
         "PRDCAP_MOXF": "Production capacity of MOX fuel fabrication plants (tHM)",
         "PRD_UP": "Production of uranium and plutonium in reprocessing plants (tHM)",
         "CAP_UP": "Capacity (uranium and plutonium) of reprocessing plants (tHM)", "PRD_NUCH": "Production of nuclear heat (ktoe)",
         "BAA_IRRADF": "Annual average burnup of definitively discharged irradiated fuel elements (GWd/tHM)"}


def line(item, unit, geo, value, flag=""):
    return f"ESTAT:NRG_INF_NUC(1.0),09/10/26 23:00:00,A,{item},{unit},{geo},2024,{value},{flag},"


def data(cap_unit="TSWU", item="PRD_MOXF", value="82", prd_ff="641", twice=False):
    lines = [HEAD, line("CAP_EN", cap_unit, "FR", "7500"), line("PRD_FF", "THM", "FR", prd_ff), line("PRDCAP_FF", "THM", "FR", "1400"),
             line(item, "THM", "FR", value), line("PRD_NUCH", "KTOE", "FR", "88138", "p"), line("BAA_IRRADF", "GWD_THM", "FR", "45.39"),
             line("PRD_NUCH", "KTOE", "EL", "0"), line("CAP_EN", "TSWU", "NO", "", "m"), line("PRD_NUCH", "KTOE", "UK", "10000")]
    if twice:
        lines.append(lines[1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        return A.build(content, NAMES, "u", "r", "v")

    def test_rows(self):
        t, counts = self.build(data())
        self.assertEqual(len(t), 6)                                          # FR's five, Greece's zero
        self.assertEqual((counts["left_out_geo"], counts["blank"], counts["zero"], counts["not_written"]), (["UK"], 1, 1, 1))
        v = {(r.x_geo_code, r.variable): (r.value, r.unit) for r in t.itertuples()}
        self.assertEqual(v[("FR", "enrichment_capacity")], (7500000.0, "SWU"))
        self.assertEqual(v[("FR", "nuclear_heat_production")], (88138 * 11630.0, "MWh"))
        self.assertEqual(v[("FR", "mox_fuel_production")], (82.0, "t"))
        self.assertEqual(set(t.geo), {"FR", "GR"})
        self.assertEqual(A.checks(t), (1, []))

    def test_counted(self):
        t, _ = self.build(data(prd_ff="1500"))                               # fresh fuel production above its capacity
        self.assertEqual(A.checks(t), (1, [("FR", "2024", "PRD_FF", 1500.0, 1400.0)]))

    def test_stops(self):
        for content in (data(cap_unit="SWU"), data(item="PRD_XX"), data(value="n.a."), data(value="-1"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                self.build(content)

    def test_codelist(self):
        tsv = (chr(10).join(f"{k}\t{v}" for k, v in NAMES.items())).encode("utf-8")
        self.assertEqual(A.item_names(tsv)["CAP_EN"], "Enrichment capacity (tSWU)")
        with self.assertRaises(RuntimeError):
            A.item_names(b"CAP_EN\tEnrichment capacity (tSWU)\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power;uranium")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}" + chr(10), f.read().replace(chr(13) + chr(10), chr(10)))


if __name__ == "__main__":
    unittest.main()
