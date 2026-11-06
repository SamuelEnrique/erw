"""Session 2785: STATEC's LUSTAT DF_A4209, the mix of electricity provided to Luxembourg's end users a year, in per cent.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statec_supplier_mix.py on a CSV built here (made up for the test,
not STATEC's): the shares written in pct, a missing observation given no row, the groups compared with 100 and fossil and
renewable with their sources, a difference counted, not a stop; a code not expected, a value not a number, a share above 100
and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2785 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statec_supplier_mix as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ("STRUCTURE,STRUCTURE_ID,STRUCTURE_NAME,ACTION,FREQ,Frequency,SPECIFICATION,Specification,TIME_PERIOD,Time period,"
        "OBS_VALUE,Observation value,OBS_STATUS,Observation status")
VALS = {"L01": 20.0, "L02": 10.0, "L03": 68.0, "L04": 2.0, "SL01": 5.0, "SL02": 5.0, "SL03": 8.0, "SL04": 2.0,
        "SL05": 4.0, "SL06": 10.0, "SL07": 50.0, "SL08": 4.0}


def csv(l03=68.0, code=None, value=None, twice=False):
    lines = [HEAD]
    for c, v in VALS.items():
        v = l03 if c == "L03" else v
        s = value if (value is not None and c == "SL08") else f"{v}"
        lines.append(f"DATAFLOW,LU1:DF_A4209(1.0),x,I,A,Annual,{c},label {c},2024,,{s},,,")
    lines.append("DATAFLOW,LU1:DF_A4209(1.0),x,I,A,Annual,SL09,Other renewables,2024,,,,-,Nil")
    if code:
        lines.append(f"DATAFLOW,LU1:DF_A4209(1.0),x,I,A,Annual,{code},x,2024,,1,,,")
    if twice:
        lines.append(lines[-1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, names, missing, counted = A.parse(csv())
        self.assertEqual((missing, counted), (1, []))
        t = A.frame(vals, names, dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        self.assertEqual(len(t), len(VALS))
        x = t[t.entity == "statec_mix:lu:l03"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0]), (68.0, "pct"))

    def test_counted(self):
        _, _, _, counted = A.parse(csv(l03=70.0))                               # the groups make 102 and renewables' sources 68
        self.assertEqual(sorted(c[1] for c in counted), ["L03", "groups"])

    def test_stops(self):
        for content in (csv(code="SL99"), csv(value="x"), csv(value="101"), csv(twice=True)):
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
