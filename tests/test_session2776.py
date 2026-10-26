"""Session 2776: STATEC's LUSTAT DF_A4208, Luxembourg's electricity imports and exports by country a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statec_electricity_trade.py on a CSV built here (made up for the test,
not STATEC's): the GWh rows taken and the TJ rows left, GWh stated as MWh, imports and exports made variables; imports and
exports checked against their countries (a stop), Germany's split counted where it differs; a code not expected, a value not a
number and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2776 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import statec_electricity_trade as A  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = "STRUCTURE,STRUCTURE_ID,STRUCTURE_NAME,ACTION,FREQ,Frequency,UNIT,Unit,SPECIFICATION,Specification,TIME_PERIOD,Time period,OBS_VALUE,Observation value,OBS_STATUS,Observation status"
VALS = {"L01": 10.0, "SL01": 2.0, "SL02": 3.0, "SL03": 5.0, "SSL01": 1.0, "SSL02": 4.0, "L02": 4.0, "SL04": 1.0, "SL06": 3.0}


def csv(l01=10.0, ssl02=4.0, code=None, value=None, twice=False):
    lines = [HEAD]
    for unit, name, k in (("A01", "TJ", 3.6), ("A03", "GWh", 1.0)):
        for c, v in VALS.items():
            v = l01 if c == "L01" else ssl02 if c == "SSL02" else v
            s = value if (value is not None and unit == "A03" and c == "SL06") else f"{v * k}"
            lines.append(f"DATAFLOW,LU1:DF_A4208(1.0),Electricity imports and exports by country,I,A,Annual,{unit},{name},{c},label {c},2024,,{s},,,")
        lines.append(f"DATAFLOW,LU1:DF_A4208(1.0),Electricity imports and exports by country,I,A,Annual,{unit},{name},SL05,To France,2024,,,,l,Not available")
    if code:
        lines.append(f"DATAFLOW,LU1:DF_A4208(1.0),Electricity imports and exports by country,I,A,Annual,A03,GWh,{code},x,2024,,1,,,")
    if twice:
        lines.append(lines[-1])
    return (chr(10).join(lines) + chr(10)).encode("utf-8")


class Parse(unittest.TestCase):
    def test_rows(self):
        vals, names, missing, counted = A.parse(csv())
        self.assertEqual((missing, counted), (1, []))
        t = A.frame(vals, names, dict(source="s", source_url="u", retrieved_at="r", vintage="v"))
        self.assertEqual(len(t), len(VALS))
        x = t[t.entity == "statec_trade:lu:sl03"]
        self.assertEqual((x.value.iloc[0], x.variable.iloc[0]), (5000.0, "electricity_imports"))
        self.assertEqual(t[t.entity == "statec_trade:lu:l02"].variable.iloc[0], "electricity_exports")

    def test_counted(self):
        _, _, _, counted = A.parse(csv(ssl02=6.0))                              # SEO 1 and others 6 make 7, Germany 5: counted
        self.assertEqual(counted, [("2024", "SL03", 2.0)])

    def test_stops(self):
        for content in (csv(l01=12.0), csv(code="SL99"), csv(value="x"), csv(twice=True)):
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
