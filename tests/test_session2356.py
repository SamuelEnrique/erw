"""Session 2356 (chain 105's 2306): Eurostat's electricity production capacities by main fuel groups and operator.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_capacity.py on SDMX-CSV built here in Eurostat's
form (figures made up for the test, not Eurostat's): a row read with its variable from the plant technology and the
operator, Greece's code, an aggregate's blank geo, Kosovo left out, a blank value no row; a unit, an operator, a header
or a value not expected stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2356 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_capacity as E  # noqa: E402
import build_coverage as B  # noqa: E402

HEAD = ",".join(E.HEADER)


def row(siec="RA300", tec="CAP_NET_ELC", op="TOTAL", unit="MW", geo="DE", year="2024", value="63000.5"):
    return f"ESTAT:NRG_INF_EPC(1.0),22/10/26 23:00:00,A,{siec},{tec},{op},{unit},{geo},{year},{value},,"


def build(*rows):
    return E.build("\n".join([HEAD, *rows]) + "\n", {"RA300": "Wind"}, "u", "2026-10-24T07:17:00Z", "")


class Build(unittest.TestCase):
    def test_rows(self):
        t, left = build(row(), row(tec="CAP_NET_ELC_C", op="PRR_AUTO", value="12"), row(geo="EL"), row(geo="EU27_2020"),
                        row(geo="XK"), row(geo="FR", value=""))
        got = {(r.entity, r.variable): r for r in t.itertuples()}
        r = got[("eurostat_epc:DE:RA300", "net_capacity_total")]
        self.assertEqual((r.value, r.unit, r.freq, r.ts_utc, r.geo, r.node), (63000.5, "MW", "P1Y", "2024-01-01T00:00:00Z", "DE", "Wind"))
        self.assertIn(("eurostat_epc:DE:RA300", "net_capacity_commissioned_autoproducers"), got)
        self.assertEqual(got[("eurostat_epc:EL:RA300", "net_capacity_total")].geo, "GR")
        self.assertEqual(got[("eurostat_epc:EU27_2020:RA300", "net_capacity_total")].geo, "")
        self.assertEqual(left, ["XK"])
        self.assertNotIn("eurostat_epc:FR:RA300", {k[0] for k in got})  # a blank value: no row

    def test_stops(self):
        for rows, words in [((row(unit="GW"),), "not expected"), ((row(op="PRR_OTHER"),), "not expected"),
                            ((row(value="1.5:"),), "not a number"), ((row(), row()), "twice")]:
            with self.assertRaises(RuntimeError) as c:
                build(*rows)
            self.assertIn(words, str(c.exception))
        with self.assertRaises(RuntimeError):
            E.build("a,b\n1,2\n", {}, "u", "", "")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}",', f.read())


if __name__ == "__main__":
    unittest.main()
