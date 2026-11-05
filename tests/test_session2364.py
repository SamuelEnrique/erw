"""Session 2364: Eurostat's monthly solid fuels supply (nrg_cb_sffm).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_solid_fuels_monthly.py on SDMX-CSV built here in
Eurostat's form (figures made up for the test, not Eurostat's): a row read in tonnes with its fuel and flow, Kosovo and the
United Kingdom left out and named, Greece's code, the EU's blank geo, a blank value no row; a unit, a fuel, a flow or a
value not expected stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2364 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_solid_fuels_monthly as E  # noqa: E402
import build_coverage as B  # noqa: E402

HEAD = ",".join(E.HEADER)


def row(bal="IPRD", siec="C0200", unit="THS_T", geo="DE", month="2024-03", value="7800.25"):
    return f"ESTAT:NRG_CB_SFFM(1.0),23/10/26 23:00:00,M,{bal},{siec},{unit},{geo},{month},{value},,"


def build(*rows):
    return E.build("\n".join([HEAD, *rows]) + "\n", "2026-10-24T08:59:00Z", "")


class Build(unittest.TestCase):
    def test_rows(self):
        t, left, updated = build(row(), row(geo="XK"), row(geo="UK"), row(geo="EL"), row(geo="EU27_2020"), row(geo="PL", value=""))
        got = {(r.entity, r.variable): r for r in t.itertuples()}
        r = got[("eurostat_sff:DE:C0200", "flow:IPRD")]
        self.assertEqual((r.value, r.unit, r.freq, r.ts_utc, r.geo, r.node),
                         (7800250.0, "t", "P1M", "2024-03-01T00:00:00Z", "DE", "Brown coal: Indigenous production"))
        self.assertEqual(got[("eurostat_sff:EL:C0200", "flow:IPRD")].geo, "GR")
        self.assertEqual(got[("eurostat_sff:EU27_2020:C0200", "flow:IPRD")].geo, "")
        self.assertNotIn("eurostat_sff:PL:C0200", {k[0] for k in got})
        self.assertEqual((left, updated), (["UK", "XK"], ["23/10/26 23:00:00"]))

    def test_stops(self):
        for rows, words in [((row(unit="TJ_GCV"),), "not expected"), ((row(siec="C0129"),), "not expected"),
                            ((row(bal="NEWFLOW"),), "not expected"), ((row(value="7.5x"),), "not a number"), ((row(), row()), "twice")]:
            with self.assertRaises(RuntimeError) as c:
                build(*rows)
            self.assertIn(words, str(c.exception))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "coal")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}",', f.read())


if __name__ == "__main__":
    unittest.main()
