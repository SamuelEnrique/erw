"""Session 2123: Eurostat's electricity production capacities for renewables and wastes.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_res_capacity.py on an SDMX-CSV answer and a codelist
built here in Eurostat's form (made up for the test, not Eurostat's): the countries Eurostat's terms allow kept and the
others left out and named, Greece's EL written as GR, an EU aggregate with a blank geo, the plant technologies as three
variables, the SIEC names as node, zeros kept and blanks left out; a header not Eurostat's, a unit not MW, a value that is
not a number and a key given twice stopping the run; the verdict and the holds. No network.

    python -m unittest tests.test_session2123 -v
"""

import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eurostat_res_capacity as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = "DATAFLOW,LAST UPDATE,freq,siec,plant_tec,unit,geo,TIME_PERIOD,OBS_VALUE,OBS_FLAG,CONF_STATUS\n"


def line(siec="RA420", tec="CAP_NET_ELC", unit="MW", geo="DE", year="2024", value="91204.000", flag=""):
    return f"ESTAT:NRG_INF_EPCRW(1.0),09/10/26 23:00:00,A,{siec},{tec},{unit},{geo},{year},{value},{flag},\n"


CODES = (b'<?xml version="1.0"?><m:Structure xmlns:m="m" xmlns:s="s" xmlns:c="c"><s:Codelist id="SIEC">'
         b'<s:Code id="RA420"><c:Name xml:lang="de">Photovoltaik</c:Name><c:Name xml:lang="en">Solar photovoltaic</c:Name></s:Code>'
         b'<s:Code id="RA300"><c:Name xml:lang="en">Wind</c:Name></s:Code></s:Codelist></m:Structure>')


class Build(unittest.TestCase):
    def test_rows(self):
        text = HEAD + line() + line(tec="CAP_NET_ELC_DC", value="102063") + line(geo="EL", siec="RA300", value="0.000") \
            + line(geo="EU27_2020", value="307101.445") + line(geo="UK") + line(geo="XK") + line(geo="FR", value="")
        t, left = E.build(text, E.names(CODES), "u", "r", "")
        self.assertEqual(left, ["UK", "XK"])
        a = t[(t.entity == "eurostat_epcrw:DE:RA420") & (t.variable == "net_capacity")].iloc[0]
        self.assertEqual((a.value, a.unit, a.geo, a.ts_utc, a.freq, a.node), (91204.0, "MW", "DE", "2024-01-01T00:00:00Z", "P1Y", "Solar photovoltaic"))
        self.assertIn("net_capacity_dc", set(t[t.entity == "eurostat_epcrw:DE:RA420"].variable))
        g = t[t.entity == "eurostat_epcrw:EL:RA300"].iloc[0]
        self.assertEqual((g.geo, g.value, g.node, g.x_geo_code), ("GR", 0.0, "Wind", "EL"))
        self.assertEqual(t[t.entity == "eurostat_epcrw:EU27_2020:RA420"].iloc[0].geo, "")
        self.assertFalse((t.x_geo_code == "FR").any())
        self.assertEqual(len(t), 4)

    def test_stops(self):
        for bad in (HEAD.replace("OBS_VALUE", "VALUE") + line(), HEAD + line(unit="GWh"), HEAD + line(value="n/a"),
                    HEAD + line() + line(), HEAD + line(tec="CAP_GROSS")):
            with self.assertRaises(RuntimeError):
                E.build(bad, {}, "u", "r", "")
        with self.assertRaises(RuntimeError):
            E.names(b"<a/>")


class Registered(unittest.TestCase):
    def test_verdict_sector_and_holds(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8", newline="") as f:
            v = {r["key"]: r for r in csv.DictReader(f)}
        self.assertEqual(v["Eurostat (Statistical Office of the European Union)"]["verdict"], "may be public")
        self.assertEqual(B.sector_of(E.NAME), "power")
        self.assertIn(E.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
