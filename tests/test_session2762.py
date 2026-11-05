"""Session 2762: Eurostat's nrg_ind_ren, European renewable energy shares a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_renewable_shares.py on a file built here (made up for the
test, not Eurostat's): the six shares written in pct, EL written GR and EU27_2020 given no geo, Kosovo left out, a share above 100
kept and counted, the provisional flag counted; a unit not PC, a share not expected, a value not a number, a negative and a key
given twice stopping the run; the codelist read; the sector rule and the holds. No network.

    python -m unittest tests.test_session2762 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_renewable_shares as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(A.HEADER)
NAMES = {k: k.lower() for k in A.ITEMS} | {"REN": "Renewable energy - overall"}


def data(unit="PC", item="REN_TRA", value="9.5", twice=False):
    lines = [HEAD]
    for g in ("NO", "EL", "EU27_2020", "XK"):
        for k in ("REN", "REN_ELC", "REN_HEAT_CL"):
            v = "115.063" if (g, k) == ("NO", "REN_ELC") else "30.25"
            lines.append(f"ESTAT:NRG_IND_REN(1.0),15/09/26 23:00:00,A,{k},{unit},{g},2024,{v},{'p' if g == 'EL' else ''},")
        lines.append(f"ESTAT:NRG_IND_REN(1.0),15/09/26 23:00:00,A,{item},{unit},{g},2024,{value},,")
    if twice:
        lines.append(lines[1])
    return ("\n".join(lines) + "\n").encode("utf-8")


class Parse(unittest.TestCase):
    def build(self, content):
        return A.build(content, NAMES, "u", "r", "v")

    def test_rows(self):
        t, counts = self.build(data())
        self.assertEqual(len(t), 3 * 4)                                      # three areas kept, four shares; Kosovo left
        self.assertEqual(counts["left_out_geo"], ["XK"])
        self.assertEqual(set(t.geo), {"NO", "GR", ""})
        self.assertEqual(set(t.unit), {"pct"})
        self.assertEqual((counts["over_100"], counts["provisional"]), (1, 3))
        x = t[(t.x_geo_code == "NO") & (t.variable == "renewable_share_electricity")]
        self.assertEqual(x.value.iloc[0], 115.063)                           # above 100 kept
        self.assertEqual(x.node.iloc[0], "NO share, ren_elc")

    def test_stops(self):
        for content in (data(unit="KTOE"), data(item="REN_XYZ"), data(value="n.a."), data(value="-1"), data(twice=True)):
            with self.assertRaises(RuntimeError):
                self.build(content)

    def test_codelist(self):
        tsv = "\n".join(f"{k}\t{v}" for k, v in NAMES.items()).encode("utf-8")
        self.assertEqual(A.item_names(tsv)["REN"], "Renewable energy - overall")
        with self.assertRaises(RuntimeError):
            A.item_names(b"REN\tRenewable energy - overall\n")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
