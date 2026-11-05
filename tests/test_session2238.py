"""Session 2238: RTE's eco2mix, France every half hour (national definitive and consolidated files).

Energy Research Warehouse (ERW). Tests warehouse/connectors/rte_eco2mix.py on a zip built here in RTE's form (made up for
the test, not RTE's): French local time placed in UTC, the spring change's nonexistent and the autumn change's twice-
occurring half hours left out and counted, the quarter-hour lines without measures skipped, "ND" and blanks without a
row, the zero wind split beside a total left out; a header not RTE's, a perimeter not France, a value not a number and
a half hour given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2238 -v
"""

import io
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import rte_eco2mix as R  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

HEAD = ["Périmètre", "Nature", "Date", "Heures", "Consommation", "Prévision J-1", "Prévision J"] + \
       [k for k in R.FIELDS if k != "Consommation"]


def line(day, hour, cons="65000", wind="1000", on="900", off="100", perim="France", nature="Données définitives"):
    v = {k: "10" for k in R.FIELDS}
    v.update({"Consommation": cons, "Eolien": wind, "Eolien terrestre": on, "Eolien offshore": off})
    return "\t".join([perim, nature, day, hour, v["Consommation"], "64000", "64100"] + [v[k] for k in R.FIELDS if k != "Consommation"])


def zipped(*lines, head=HEAD):
    text = "\t".join(head) + "\n" + "\n".join(lines) + "\nRTE ne pourra être tenu responsable\n"
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("eCO2mix_RTE_Annuel-Definitif_2025.xls", text.encode("cp1252"))
    return b.getvalue()


def counts():
    return {"ambiguous": 0, "nonexistent": 0, "zero_split": 0}


class Rows(unittest.TestCase):
    def test_time_and_values(self):
        c = counts()
        rows = R.file_rows(zipped(line("2025-07-01", "12:00"), "\t".join(["France", "x", "2025-07-01", "12:15", "", "1", "1"] + [""] * 14),
                                  line("2025-07-01", "12:30", cons="ND")), "u", "r", "v", c)
        t = R.finish(rows)
        cons = t[t.variable == "consumption"]
        self.assertEqual(list(cons.ts_utc), ["2025-07-01T10:00:00Z"])
        self.assertEqual((cons.value.iloc[0], cons.unit.iloc[0], cons.freq.iloc[0], cons.geo.iloc[0]), (65000.0, "MW", "PT30M", "FR"))
        self.assertEqual(len(t[t.ts_utc == "2025-07-01T10:30:00Z"]), len(R.FIELDS) - 1)

    def test_daylight_saving(self):
        c = counts()
        R.file_rows(zipped(line("2025-03-30", "02:00"), line("2025-03-30", "02:30"), line("2025-10-26", "02:00"),
                           line("2025-10-26", "03:00")), "u", "r", "v", c)
        self.assertEqual((c["nonexistent"], c["ambiguous"]), (2, 1))
        self.assertEqual(R.local_to_utc("2025-03-30", "03:00"), ("2025-03-30T01:00:00Z", ""))
        self.assertEqual(R.local_to_utc("2025-10-26", "03:00"), ("2025-10-26T02:00:00Z", ""))

    def test_zero_wind_split(self):
        c = counts()
        t = R.finish(R.file_rows(zipped(line("2021-06-01", "12:00", on="0", off="0")), "u", "r", "v", c))
        self.assertEqual(c["zero_split"], 1)
        self.assertNotIn("wind_onshore", set(t.variable))
        self.assertIn("wind", set(t.variable))

    def test_stops(self):
        for z in (zipped(line("2025-07-01", "12:00"), head=["Zone"] + HEAD[1:]), zipped(line("2025-07-01", "12:00", perim="Bretagne")),
                  zipped(line("2025-07-01", "12:00", cons="lots")), zipped(line("01/07/2025", "12:00"))):
            with self.assertRaises(RuntimeError):
                R.file_rows(z, "u", "r", "v", counts())
        rows = R.file_rows(zipped(line("2025-07-01", "12:00"), line("2025-07-01", "12:00")), "u", "r", "v", counts())
        with self.assertRaises(RuntimeError):
            R.finish(rows)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(R.NAME), "power")
        self.assertIn(R.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {R.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
