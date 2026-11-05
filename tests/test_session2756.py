"""Session 2756: Statistics Denmark's ENE1HT, Denmark's electricity supply a year from 1966.

Energy Research Warehouse (ERW). Tests warehouse/connectors/dst_energy_account.py on an extract built here (made up for the test,
not Statistics Denmark's): the codes read from StatBank's code-and-text cells, GWh stated as MWh, the six kept cells written and
the zero cells left; the total supply checked against production plus imports, each renewable's total supply against its
renewable supply and the zero cells against 0; a missing year, a cell given twice and a value not a whole number stopping the run;
the sector rule and the holds. No network.

    python -m unittest tests.test_session2756 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import dst_energy_account as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

S = {"ETIL": "ETIL Total supply", "EIMPORT": "EIMPORT Imports", "ETILVE": "ETILVE Supply of renewable energy",
     "EPRODI": "EPRODI Total production"}
E = {"EMEL": "EMEL Electricity (GWh)", "EMVIND": "EMVIND Wind power (GWh)", "EMVAND": "EMVAND Hydro power (GWh)",
     "EMSOLK": "EMSOLK Solar power (GWh)"}


def extract(total=30, drop=None, twice=False, value=None):
    out = ["﻿TILGANG;ENERGI1;TID;INDHOLD"]
    for y in A.YEARS:
        cells = {("ETIL", "EMEL"): total, ("EPRODI", "EMEL"): 20, ("EIMPORT", "EMEL"): 10, ("ETILVE", "EMEL"): 0}
        for e, v in (("EMVIND", 5), ("EMVAND", 1), ("EMSOLK", 2)):
            cells.update({("ETIL", e): v, ("ETILVE", e): v, ("EIMPORT", e): 0, ("EPRODI", e): 0})
        for (s, e), v in cells.items():
            if drop == (s, e, y):
                continue
            if value is not None and (s, e, y) == ("ETIL", "EMEL", 2000):
                v = value
            out.append(f"{S[s]};{E[e]};{y} {y};{v}")
    if twice:
        out.append(out[1])
    return ("\n".join(out) + "\n").encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        t = A.parse(extract(), dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        self.assertEqual(len(t), 6 * 60)                                     # six kept cells, sixty years; the zero cells left
        self.assertEqual(set(t.unit), {"MWh"})
        x = t[(t.variable == "electricity_imports") & (t.ts_utc == "1966-01-01T00:00:00Z")]
        self.assertEqual(x.value.iloc[0], 10000.0)                           # 10 GWh stated as MWh
        self.assertEqual(x.node.iloc[0], "EIMPORT Imports; EMEL Electricity (GWh)")
        self.assertEqual(t.ts_utc.max(), "2025-01-01T00:00:00Z")

    def test_stops(self):
        for content in (extract(total=31),                                 # production 20 and imports 10 make 30, not 31
                        extract(drop=("ETIL", "EMVIND", 1990)),
                        extract(twice=True),
                        extract(value="30.5")):
            with self.assertRaises(RuntimeError):
                A.parse_csv(content)

    def test_zero_cells(self):
        bad = extract().replace(b"EIMPORT Imports;EMVIND Wind power (GWh);2001 2001;0", b"EIMPORT Imports;EMVIND Wind power (GWh);2001 2001;3")
        with self.assertRaises(RuntimeError):
            A.parse_csv(bad)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
