"""Session 2169: the Canada Energy Regulator's pipeline throughput and capacity, the cross-border lines.

Energy Research Warehouse (ERW). Tests warehouse/connectors/cer_throughput.py on files built here in the CER's oil and
gas forms (made up for the test, not the CER's): thousand cubic metres a day written as m3/d, an oil key point's
capacity written once for all its products, one product as export and intracanada kept apart, a gas key point's two
directions kept apart, the shorter oil header (no contracted volumes) accepted, blanks left out; a header not the CER's,
a value that is not a number, an oil capacity that differs between products and a key given twice stopping the run; the
unit m3/d (Decision 69), the verdict, the sector rule and the holds. No network.

    python -m unittest tests.test_session2169 -v
"""

import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import cer_throughput as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402


def line(cols):
    return ",".join(f'"{c}"' if "," in c else c for c in cols) + "\n"


OIL_HEAD = line(C.OIL)
OIL_ROW = ["2026-06-01", "6", "2026", "South Bow", "Keystone pipeline", "International boundary at or near Haskett, Manitoba",
           "48.99", "-97.95", "south", "export", "domestic light", "1.54", "", "", "", "93.56", "Capacity may vary"]


def oil(**kw):
    r = list(OIL_ROW)
    for k, v in kw.items():
        r[C.OIL.index(k)] = v
    return line(r)


GAS_HEAD = line(C.GAS)


def gas(direction="south", cap="51717.2", thr="48884.2"):
    return line(["2026-06-30", "30", "6", "2026", "Westcoast", "Westcoast pipeline", "Kingsvale", "49.9", "-120.9", direction,
                 "intracanada", cap, thr, "1973513.8"])


class Build(unittest.TestCase):
    def test_oil(self):
        rows = C.finish(C.file_rows(OIL_HEAD + oil() + oil(**{"Product": "domestic heavy", "Throughput (1000 m3/d)": "15.07"})
                                    + oil(**{"Trade Type": "intracanada"}), "oil", "u", "r", ""))
        cap = rows[rows.variable == "available_capacity"]
        self.assertEqual(len(cap), 1)
        self.assertEqual((cap.iloc[0].value, cap.iloc[0].unit, cap.iloc[0].freq), (93560.0, "m3/d", "P1M"))
        t = rows[rows.variable == "throughput"]
        self.assertEqual(len(t), 3)
        light = t[t.entity.str.endswith(":domestic_light:export")].iloc[0]
        self.assertEqual((light.value, light.ts_utc, light.geo), (1540.0, "2026-06-01T00:00:00Z", "CA"))
        self.assertTrue(any(e.endswith(":domestic_light:intracanada") for e in t.entity))

    def test_short_oil_header(self):
        short = [c for c in C.OIL if not c.startswith(("Committed", "Uncommitted"))]
        r = [v for c, v in zip(C.OIL, OIL_ROW) if c in short]
        t = C.finish(C.file_rows(line(short) + line(r), "oil", "u", "r", ""))
        self.assertEqual(sorted(set(t.variable)), ["available_capacity", "throughput"])

    def test_gas(self):
        t = C.finish(C.file_rows(GAS_HEAD + gas() + gas(direction="north", thr=""), "gas", "u", "r", ""))
        self.assertEqual(sorted(set(t.entity)), ["cer_pipe:westcoast_pipeline:kingsvale:north", "cer_pipe:westcoast_pipeline:kingsvale:south"])
        s = t[(t.entity.str.endswith(":south")) & (t.variable == "throughput")].iloc[0]
        self.assertEqual((s.value, s.freq), (48884200.0, "P1D"))
        self.assertEqual(len(t), 3)

    def test_stops(self):
        for bad, kind in ((GAS_HEAD + gas(), "oil"), (OIL_HEAD + oil(**{"Throughput (1000 m3/d)": "lots"}), "oil"),
                          (OIL_HEAD + oil() + oil(**{"Product": "domestic heavy", "Available Capacity (1000 m3/d)": "90"}), "oil")):
            with self.assertRaises(RuntimeError):
                C.file_rows(bad, kind, "u", "r", "")
        with self.assertRaises(RuntimeError):
            C.finish(C.file_rows(GAS_HEAD + gas() + gas(), "gas", "u", "r", ""))


class Registered(unittest.TestCase):
    def test_unit_verdict_sector_and_holds(self):
        self.assertIn("m3/d", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("69. **Session 2169: m3/d.**", f.read())
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8", newline="") as f:
            v = {r["key"]: r for r in csv.DictReader(f)}
        self.assertEqual(v["Canada Energy Regulator (CER), Open Government Licence - Canada"]["verdict"], "may be public")
        self.assertEqual(B.sector_of(C.NAME), "oil;gas")
        self.assertIn(C.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
