"""Session 2231: Statistics Netherlands' table 84575NED, the Netherlands' electricity balance.

Energy Research Warehouse (ERW). Tests warehouse/connectors/cbs_electricity.py on a zip built here in CBS's form (made up
for the test, not CBS's): the monthly periods only, each measure under its English name, million kWh written as MWh on
the month's first day, the period's status kept, an empty cell not written; a measure not in the map, a unit other than
million kWh, a missing file and a value not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2231 -v
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
import cbs_electricity as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
MEAS = "Identifier;MeasureGroupId;Index;Title;Description;DataType;Unit;Decimals;PresentationType\nE006590;M002417_1;14;Zonnestroom;;Long;mln kWh;0;\nL008592_1;M001250_1;19;Duitsland;;Long;mln kWh;0;\n"
PER = "Identifier;DimensionGroupId;DimensionId;Index;Title;Description;Status\n2026MM07;1;Perioden;1;2026 juli;;Voorlopig\n2026JJ00;0;Perioden;2;2026;;Voorlopig\n"
OBS = ("Id;Measure;Perioden;Value;StringValue;ValueAttribute\n0;E006590;2026MM07;2500;;None\n1;L008592_1;2026MM07;1200;;None\n"
       "2;E006590;2026JJ00;9999;;None\n3;L008592_1;2026MM06;;;Impossible\n")


def zipped(meas=MEAS, per=PER, obs=OBS, drop=None):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n, t in (("MeasureCodes.csv", meas), ("PeriodenCodes.csv", per), ("Observations.csv", obs)):
            if n != drop:
                z.writestr(n, t)
        z.writestr("Properties.csv", "Identifier;License\n84575NED;https://creativecommons.org/licenses/by/4.0/\n")
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        t, lic = C.parse(zipped(), BASE)
        self.assertEqual(lic, "https://creativecommons.org/licenses/by/4.0/")
        s = t.set_index(["variable", "ts_utc"])
        self.assertEqual(len(t), 2)
        r = s.loc[("net_solar", "2026-07-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.node, r.x_status, r.geo), (2500000.0, "MWh", "Zonnestroom", "Voorlopig", "NL"))
        self.assertEqual(s.loc[("import_germany", "2026-07-01T00:00:00Z")].x_measure, "L008592_1")

    def test_stops(self):
        for z in (zipped(meas=MEAS.replace("E006590;", "X999999;")), zipped(meas=MEAS.replace("mln kWh", "TJ", 1)),
                  zipped(drop="PeriodenCodes.csv"), zipped(obs=OBS.replace(";2500;", ";many;"))):
            with self.assertRaises(RuntimeError):
                C.parse(z, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.NAME), "power")
        self.assertIn(C.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
