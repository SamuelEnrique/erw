"""Session 2757: Eurostat's nrg_cb_e, European electricity consumption by sector a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_electricity_consumption.py on files built here (made up for
the test, not Eurostat's): the twelve balance items kept and the others left, GWh stated as MWh, EL written GR and EU27_2020 given
no geo, the United Kingdom left out; AFC checked against FC plus STATDIFF (a stop) and FC against NRG_E plus the seven sectors
(counted); a unit not GWh, a value not a number and a key given twice stopping the run; the codelist read; the sector rule and
the holds. No network.

    python -m unittest tests.test_session2757 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_electricity_consumption as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
NAMES = {k: k.lower() for k in A.ITEMS} | {"FC": "Final consumption", "GEP": "Gross electricity production"}
VALS = {"FC_IND_E": 10, "FC_TRA_E": 1, "FC_OTH_CP_E": 6, "FC_OTH_HH_E": 7, "FC_OTH_AF_E": 1, "FC_OTH_FISH_E": 0,
        "FC_OTH_NSP_E": 0, "NRG_E": 2, "FC": 27, "STATDIFF": 1, "AFC": 28, "LOSS": 3, "GEP": 40}


def data(geo=("DK", "EL", "EU27_2020", "UK"), fc=27, unit="GWH", value=None, twice=False):
    lines = [HEAD]
    for g in geo:
        for k, v in VALS.items():
            v = fc if k == "FC" else v
            if value is not None and (g, k) == ("DK", "LOSS"):
                v = value
            lines.append(f"ESTAT:NRG_CB_E(1.0),22/10/26 23:00:00,A,{k},E7000,{unit},{g},2024,{v},,")
    if twice:
        lines.append(lines[1])
    return ("\n".join(lines) + "\n").encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        return A.build(content, NAMES, "u", "r", "v")

    def test_rows(self):
        t, counts = self.build(data())
        self.assertEqual(len(t), 3 * 12)                                     # three areas kept, twelve items; GEP left
        self.assertEqual(counts["left_out_geo"], ["UK"])
        self.assertEqual(set(t.geo), {"DK", "GR", ""})
        x = t[(t.x_geo_code == "DK") & (t.variable == "households")]
        self.assertEqual(x.value.iloc[0], 7000.0)
        self.assertEqual(x.node.iloc[0], "DK electricity, fc_oth_hh_e")
        n_afc, compared, off = A.checks(t)
        self.assertEqual((n_afc, compared, len(off)), (3, 3, 0))

    def test_fc_off_is_counted(self):
        content = data(fc=27)
        t, _ = self.build(content.replace(b"A,FC,E7000,GWH,DK,2024,27", b"A,FC,E7000,GWH,DK,2024,29")
                          .replace(b"A,AFC,E7000,GWH,DK,2024,28", b"A,AFC,E7000,GWH,DK,2024,30"))
        n_afc, compared, off = A.checks(t)
        self.assertEqual(len(off), 1)                                        # counted, not a stop

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            A.checks(self.build(data(fc=30))[0])                            # AFC 28 is not FC 30 plus STATDIFF 1
        for content in (data(unit="KTOE"), data(value="n.a."), data(twice=True)):
            with self.assertRaises(RuntimeError):
                self.build(content)

    def test_codelist(self):
        tsv = "\n".join(f"{k}\t{v}" for k, v in NAMES.items()).encode("utf-8")
        self.assertEqual(A.item_names(tsv)["FC"], "Final consumption")
        with self.assertRaises(RuntimeError):
            A.item_names(b"FC\tFinal consumption\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
