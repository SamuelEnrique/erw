"""Session 2225: Eurostat's monthly electricity (nrg_cb_pem and nrg_cb_em).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_electricity_monthly.py on files built here in
Eurostat's SDMX-CSV form (made up for the test, not Eurostat's): GWh written as MWh on the month's first day; the percent
shares not taken; the United Kingdom left out and EU27_2020 kept with a blank geo; EL written GR; a unit, frequency or
balance not expected, a value not a number and a key given twice stopping the run; the sector rule and the holds. No
network.

    python -m unittest tests.test_session2225 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_electricity_monthly as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

B1 = {"source": "s", "source_url": "u1", "retrieved_at": "r", "vintage": "v"}
B2 = {"source": "s", "source_url": "u2", "retrieved_at": "r", "vintage": "v"}
PEM = ("DATAFLOW,LAST UPDATE,freq,siec,unit,geo,TIME_PERIOD,OBS_VALUE,OBS_FLAG,CONF_STATUS\n"
       "ESTAT:NRG_CB_PEM(1.0),23/10/26 23:00:00,M,TOTAL,GWH,EL,2026-01,4000.5,,\n"
       "ESTAT:NRG_CB_PEM(1.0),23/10/26 23:00:00,M,TOTAL,PC,EL,2026-01,100,,\n"
       "ESTAT:NRG_CB_PEM(1.0),23/10/26 23:00:00,M,N9000,GWH,EU27_2020,2026-01,50000,e,\n"
       "ESTAT:NRG_CB_PEM(1.0),23/10/26 23:00:00,M,TOTAL,GWH,UK,2026-01,25000,,\n"
       "ESTAT:NRG_CB_PEM(1.0),23/10/26 23:00:00,M,RA300,GWH,FR,2026-02,,,C\n")
EM = ("DATAFLOW,LAST UPDATE,freq,nrg_bal,siec,unit,geo,TIME_PERIOD,OBS_VALUE,OBS_FLAG,CONF_STATUS\n"
      "ESTAT:NRG_CB_EM(1.0),23/10/26 23:00:00,M,IMP,E7000,GWH,FR,2026-01,1200,,\n")
NAMES = {"TOTAL": "Total", "N9000": "Nuclear heat"}
BAL = {"IMP": "Imports"}


class Build(unittest.TestCase):
    def test_rows(self):
        t, left = E.build(PEM, EM, NAMES, BAL, B1, B2)
        self.assertEqual(left, ["UK"])
        s = t.set_index(["entity", "variable", "ts_utc"])
        r = s.loc[("eurostat_elec:EL", "net_production:TOTAL", "2026-01-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.geo, r.node, r.x_dataset), (4000500.0, "MWh", "GR", "Total", "nrg_cb_pem"))
        eu = s.loc[("eurostat_elec:EU27_2020", "net_production:N9000", "2026-01-01T00:00:00Z")]
        self.assertEqual((eu.geo, eu.x_flag), ("", "e"))
        imp = s.loc[("eurostat_elec:FR", "flow:IMP", "2026-01-01T00:00:00Z")]
        self.assertEqual((imp.value, imp.node, imp.source_url), (1200000.0, "Imports", "u2"))
        self.assertEqual(len(t), 3)

    def test_stops(self):
        for pem, em in ((PEM.replace(",GWH,FR,", ",TJ,FR,"), EM), (PEM, EM.replace(",M,IMP,", ",A,IMP,")), (PEM, EM.replace("E7000", "G3000")),
                        (PEM.replace("4000.5", "n/a"), EM), (PEM + PEM.splitlines()[1] + "\n", EM), (PEM.replace("OBS_FLAG", "FLAG"), EM)):
            with self.assertRaises(RuntimeError):
                E.build(pem, em, NAMES, BAL, B1, B2)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
