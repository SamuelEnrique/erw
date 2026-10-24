"""Session 2213: Eurostat's monthly imports of natural gas and LNG by partner (nrg_ti_gasm).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_gas_imports.py on an SDMX-CSV result built here in
Eurostat's form (made up for the test, not Eurostat's): the energy unit kept and the volume unit left, TJ written as MWh,
zeros and blanks left out and counted, the countries Eurostat's terms allow kept (EL written as GR, an aggregate's geo
blank, the UK left out and named); a header not Eurostat's, a unit not expected, a value that is not a number and a key
given twice stopping the run; the queued job's id read from Eurostat's answer; --offline needing --job; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2213 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_gas_imports as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ",".join(E.HEADER) + "\n"


def line(siec="G3200", partner="US", unit="TJ_GCV", geo="DE", period="2025-03", value="3600"):
    return f"ESTAT:NRG_TI_GASM(1.0),01/10/26 23:00:00,M,{siec},{partner},{unit},{geo},{period},{value},,\n"


class Build(unittest.TestCase):
    def test_rows(self):
        text = (HEAD + line() + line(unit="MIO_M3", value="100") + line(geo="EL", partner="QA", value="0")
                + line(geo="EU27_2020", siec="G3000", partner="TOTAL", value="36000") + line(geo="UK") + line(geo="FR", value=""))
        t, counts = E.build(text.encode("utf-8"), "u", "r", "")
        self.assertEqual(len(t), 2)
        a = t[t.entity == "eurostat_gas_imports:DE:G3200:US"].iloc[0]
        self.assertEqual((a.value, a.unit, a.ts_utc, a.geo, a.freq), (1000000.0, "MWh", "2025-03-01T00:00:00Z", "DE", "P1M"))
        self.assertEqual(t[t.x_geo_code == "EU27_2020"].iloc[0].geo, "")
        self.assertEqual((counts["zero"], counts["blank"], sorted(counts["left_out_geo"])), (1, 1, ["UK"]))

    def test_greece(self):
        t, _ = E.build((HEAD + line(geo="EL", value="36")).encode("utf-8"), "u", "r", "")
        self.assertEqual(t.iloc[0].geo, "GR")

    def test_stops(self):
        for bad in (HEAD.replace("OBS_VALUE", "VALUE") + line(), HEAD + line(unit="GWH"), HEAD + line(value="lots"), HEAD + line() + line()):
            with self.assertRaises(RuntimeError):
                E.build(bad.encode("utf-8"), "u", "r", "")
        with self.assertRaises(SystemExit):
            E.main(["--offline"])

    def test_job_id(self):
        answer = "<ns0:syncResponse><processingTime>93</processingTime><queued><id>7330e3ef-4d8a-41e6-af23-bdfd15c46fd7</id><status>SUBMITTED</status></queued></ns0:syncResponse>"
        self.assertEqual(E.JOB.search(answer).group(1), "7330e3ef-4d8a-41e6-af23-bdfd15c46fd7")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "gas;lng")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
