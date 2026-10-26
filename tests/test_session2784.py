"""Session 2784: STATEC's LUSTAT DF_A4201, Luxembourg's power stations' net maximum power and number a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statec_power_capacity.py on a CSV built here (made up for the test,
not STATEC's): the two variables written in MW and as a count, a missing observation given no row, the first two levels compared
with their parts and a difference counted, not a stop; a code not expected, a value not a number and a key given twice stopping
the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2784 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statec_power_capacity as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ("STRUCTURE,STRUCTURE_ID,STRUCTURE_NAME,ACTION,FREQ,Frequency,VARIABLES,Variables,SPECIFICATION,Specification,"
        "TIME_PERIOD,Time period,OBS_VALUE,Observation value,OBS_STATUS,Observation status")
VALS = {"L01": 10.0, "SL01": 8.0, "SL02": 2.0, "SSL01": 5.0, "SSL02": 1.0, "SSL03": 2.0, "SSL04": 1.0, "SSL05": 1.0}


def csv(l01=10.0, code=None, value=None, twice=False):
    lines = [HEAD]
    for var in ("C001", "C002"):
        for c, v in VALS.items():
            v = l01 if (c == "L01" and var == "C001") else v
            s = value if (value is not None and var == "C001" and c == "SSL05") else f"{v}"
            lines.append(f"DATAFLOW,LU1:DF_A4201(1.0),x,I,A,Annual,{var},v,{c},label {c},2024,,{s},,,")
        lines.append(f"DATAFLOW,LU1:DF_A4201(1.0),x,I,A,Annual,{var},v,SSSL06,woodpellets,2024,,,,l,Not available")
    if code:
        lines.append(f"DATAFLOW,LU1:DF_A4201(1.0),x,I,A,Annual,C001,v,{code},x,2024,,1,,,")
    if twice:
        lines.append(lines[-1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, names, missing, counted = A.parse(csv())
        self.assertEqual((missing, counted), (2, []))
        t = A.frame(vals, names, dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        self.assertEqual(len(t), 2 * len(VALS))
        mw = t[(t.entity == "statec_cap:lu:l01") & (t.variable == "net_maximum_power")]
        n = t[(t.entity == "statec_cap:lu:l01") & (t.variable == "power_stations")]
        self.assertEqual((mw.value.iloc[0], mw.unit.iloc[0], n.unit.iloc[0]), (10.0, "MW", "count"))

    def test_counted(self):
        _, _, _, counted = A.parse(csv(l01=12.0))                               # primary 8 and secondary 2 make 10, the total 12
        self.assertEqual(counted, [("2024", "C001", "L01", -2.0)])

    def test_stops(self):
        for content in (csv(code="SL99"), csv(value="x"), csv(twice=True)):
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
