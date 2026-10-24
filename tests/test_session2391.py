"""Session 2391: E-Control's monthly electricity statistics (el_dataset_mn.csv), Austria.

Energy Research Warehouse (ERW). Tests warehouse/connectors/econtrol_austria_electricity.py on a file built here in the
download's form (made up for the test, not E-Control's): metadata rows, then one row a month, semicolon-separated with
decimal commas, in Windows-1252; each cell a row in its series' unit, a series in another unit not taken and counted, a
series given twice kept once, a blank not written; a metadata row missing, a value that is not a number and a series
given twice with different values stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2391 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import econtrol_austria_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
COLS = [  # TS_ID, KOMP, Gliederung1, N, UNIT
    ("#999033", "Importe", "_", "Ges", "MWh"), ("#999034", "Importe", "CH", "Ges", "MWh"), ("#999023", "Erzeugungskoeffizient", "Hydr", "Oef", "[1]"),
    ("#999033", "Importe", "_", "Ges", "MWh"), ("#89110m", "Inlandstromverbrauch", "_", "Ges", "MWh"),
]


def build(months=(("2026-07", ["1234,5", "100", "0,7", "1234,5", "6000"]), ("2026-08", ["1300", "", "0,6", "1300", "6100,25"])), drop=None, cols=COLS):
    meta = {"TS_ID": [c[0] for c in cols], "ZA": ["mn"] * len(cols), "KOMP": [c[1] for c in cols], "Gliederung1": [c[2] for c in cols],
            "Gliederung2": ["_"] * len(cols), "Gliederung3": ["_"] * len(cols), "VO": ["Betr"] * len(cols), "REG": ["AT"] * len(cols),
            "N": [c[3] for c in cols], "EHB": ["M"] * len(cols), "KAT": ["A"] * len(cols), "UNIT": [c[4] for c in cols]}
    lines = ['"Header & Timestamp";' + ";".join(f'"{i + 1}"' for i in range(len(cols))), '"aktualisiert";' + ";".join('"2026-09-28"' for _ in cols)]
    for k in S.META:
        if k != drop:
            lines.append(f'"{k}";' + ";".join(f'"{v}"' for v in meta[k]))
    for m, vals in months:
        lines.append(f'"{m}";' + ";".join(f'"{v}"' if v else "" for v in vals))
    return ("\r\n".join(lines) + "\r\n").encode("cp1252")


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        t = S.parse(build(), BASE, counts).set_index(["entity", "ts_utc"])
        self.assertEqual(len(t), 5)
        r = t.loc[("econtrol:at:999033", "2026-07-01T00:00:00Z")]
        self.assertEqual((r.variable, r.value, r.unit, r.geo, r.node, r.x_scope), ("importe", 1234.5, "MWh", "AT", "Importe | Ges", "Ges"))
        self.assertEqual(t.loc[("econtrol:at:999034", "2026-07-01T00:00:00Z")].node, "Importe | CH | Ges")
        self.assertNotIn(("econtrol:at:999034", "2026-08-01T00:00:00Z"), t.index)
        self.assertEqual(counts, {"series in [1] not taken": 1, "series given twice, kept once": 1})

    def test_stops(self):
        bad = [build(drop="UNIT"),
               build(months=(("2026-07", ["about", "100", "0,7", "about", "6000"]),)),
               build(months=(("2026-07", ["1234,5", "100", "0,7", "999", "6000"]),))]
        for content in bad:
            with self.assertRaises(RuntimeError):
                S.parse(content, BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
