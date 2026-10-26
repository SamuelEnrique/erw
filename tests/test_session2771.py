"""Session 2771: STATEC's LUSTAT DF_A4203, Luxembourg's electricity generation a year from 1928.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statec_electricity_generation.py on a CSV built here (made up for the
test, not STATEC's): the GWh rows taken and the TJ and ktep rows left, GWh stated as MWh, a missing observation given no row;
sl01 and sl02 checked against their parts (a stop), l01 and l02 counted where they differ; a code not expected, a value not a
number and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2771 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statec_electricity_generation as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = "STRUCTURE,STRUCTURE_ID,STRUCTURE_NAME,ACTION,FREQ,Frequency,UNIT,Unit,SPECIFICATION,Specification,TIME_PERIOD,Time period,OBS_VALUE,Observation value,OBS_STATUS,Observation status"
VALS = {"L01": 10.0, "L02": 9.0, "SL01": 6.0, "SL02": 4.0, "SL03": 5.0, "SL04": 1.0, "SL05": 0.5, "SL06": 0.5, "SL07": 2.0,
        "SSL01": 4.0, "SSL02": 1.0, "SSL03": 1.0, "SSL04": 3.0, "SSL05": 1.0}


def csv(sl01=6.0, l02=9.0, code=None, value=None, twice=False):
    lines = [HEAD]
    for unit, name, k in (("A01", "TJ", 3.6), ("A03", "GWh", 1.0)):
        for c, v in VALS.items():
            v = sl01 if c == "SL01" else l02 if c == "L02" else v
            s = value if (value is not None and unit == "A03" and c == "SSL05") else f"{v * k}"
            lines.append(f"DATAFLOW,LU1:DF_A4203(1.0),Electricity generation,I,A,Annual,{unit},{name},{c},label {c},2024,,{s},,,")
        lines.append(f"DATAFLOW,LU1:DF_A4203(1.0),Electricity generation,I,A,Annual,{unit},{name},SSSL02,Siderurgy,2024,,,,l,Not available")
    if code:
        lines.append(f"DATAFLOW,LU1:DF_A4203(1.0),Electricity generation,I,A,Annual,A03,GWh,{code},x,2024,,1,,,")
    if twice:
        lines.append(lines[-1])
    return ("\n".join(lines) + "\n").encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, names, missing, counted = A.parse(csv())
        self.assertEqual((missing, counted), (1, []))
        t = A.frame(vals, names, dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        self.assertEqual(len(t), len(VALS))                                   # the GWh rows only; the missing one has none
        x = t[t.entity == "statec_elec:lu:l01"]
        self.assertEqual((x.value.iloc[0], x.unit.iloc[0], x.node.iloc[0]), (10000.0, "MWh", "L01 label L01"))

    def test_counted(self):
        _, _, _, counted = A.parse(csv(l02=10.0))                              # the plant types make 9, l02 10: counted
        self.assertEqual(counted, [("2024", "L02", -1.0)])

    def test_stops(self):
        for content in (csv(sl01=7.0), csv(code="SL99"), csv(value="x"), csv(twice=True)):
            with self.assertRaises(RuntimeError):
                A.parse(content)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        self.assertIn(A.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
