"""Session 2420: the Energy Regulation Board's Statistical Bulletin, Zambia's generation by station, consumption by sector,
trade and installed capacity.

Energy Research Warehouse (ERW). Tests warehouse/connectors/erb_zambia.py's reader on text and a Table 16 built here in
the form pdfplumber gives the bulletin (figures made up for the test, not ERB's): the list of tables passed over, "-" with
no row and 0 kept, GWh written as MWh, a sector's 2019 column left out when it equals 2021's, the one known gap in the
traders' total allowed; a header not ERB's, a value that is not a number and parts not adding to their total stopping
the run; the sector rule and the live-set hold (internal, so not in the release). No network, no PDF.

    python -m unittest tests.test_session2420 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import erb_zambia as Z  # noqa: E402
import build_coverage as B  # noqa: E402


def text(kafue_2014="6.00", cons_2019="1.00 2.00", greenco="1.00", trader_total="4.00"):
    return "\n".join([
        "Table 13: Electricity generation from ZESCO's large hydro power plants (GWh), 2013-2014 ........ 15",
        "Table 12: National Electricity Generation 2014",
        "ZESCO's Major-Hydro 16.00",
        "ZESCO's Mini-Hydro 3.00",
        "ZESCO's Diesel 1.00",
        "IPPs 4.00",
        "Total 24.00",
        "Table 13: Electricity generation from ZESCO's large hydro power plants (GWh), 2013-2014",
        Z.LINE_TABLES["13"][1],
        "2013 7.00 4.00 1.00 12.00",
        f"2014 {kafue_2014} 8.00 2.00 16.00",
        "Table 14: Electricity generation from ZESCO's mini- hydro power plants (GWh), 2013-2014",
        Z.LINE_TABLES["14"][1],
        "2013 1.00 - 1.00 - 1.00 0.50 3.50",
        "2014 1.00 1.00 - - 1.00 0 3.00",
        "Table 15: Electricity generation from ZESCO's Diesel power plants (GWh), 2013-2014",
        Z.LINE_TABLES["15"][1],
        "2013 - - 1.00 - - - - 1.00",
        "2014 - - - 1.00 - - - 1.00",
        "Table 16: Electricity generation from independent power producers (GWh), 2013-2014",
        "Table 17: Electricity Exports, 2024|2025",
        "Exporter Trader Name 2024 2025 % Change",
        "Enterprise Power 1.00 - -100.00%",
        "Kanona Power Company Limited 2.00 3.00 50.00%",
        f"Africa GreenCo - {greenco} 100.00%",
        "Petrodex 1.00 1.00 0.00%",
        f"Power Trader Total Exports (GWh) 4.00 {trader_total} 0.00%",
        "ZESCO ZESCO 5.00 6.00 20.00%",
        "ZESCO Total Exports (GWh) 5.00 6.00 20.00%",
        "Grand Total Exports (GWh) 9.00 10.00 11.11%",
        "Table 18: Electricity Imports, 2024|2025",
        "Importer 2024 2025 % Change",
        "ZESCO 2,467.02 2119.70 -14.08%",
        "Table 19: Comparison of national electricity consumption by economic sector, 2019-2021",
        "Electricity Consumption (GWh) 2019 2020 2021",
    ] + [f"{label} {cons_2019.split()[0] if label != 'Grand Total' else '11.00'} 2.00 {'1.00' if label != 'Grand Total' else '11.00'}"
         for label in Z.SECTORS if label not in ("Grand Total",)] + [
        "Grand Total 11.00 22.00 11.00",
        "Table 26: Summary of National Installed Electricity Capacity by Technology - 2025",
        "Technology 2025 Installed Capacity (MW) % Share",
        "Hydro 3,000.00 75.00%",
        "Coal 400 10.00%",
        "Diesel 200 5.00%",
        "Solar 300.5 7.50%",
        "Heavy Fuel Oil 99.5 2.50%",
        "Total 4,000.00 100.00%",
    ])


def ipp(total_2014="4.00"):
    head = ["Year"] + [n.replace(" ", "\n", 1) for n in Z.IPPS] + ["Total\nGWh"]
    row13 = ["", "2013", ""] + ["0"] * 13 + ["0", "0"]
    row14 = ["2014", None] + ["1.00", "3.00"] + ["0"] * 12 + [total_2014]
    return [[head, row13, row14]]


class Rows(unittest.TestCase):
    def test_rows(self):
        out, drop, nat, short = Z.parse(text(), ipp())
        got = {(e, y): (v, u, g) for e, var, y, v, u, node, g, n in out}
        self.assertEqual(got[("erb_zm:station:kafue_gorge", 2014)], (6000.0, "MWh", "zesco_major_hydro"))
        self.assertNotIn(("erb_zm:station:lunzua", 2013), got)                          # "-": no row
        self.assertEqual(got[("erb_zm:station:shiwangandu", 2014)][0], 0.0)              # a 0 is kept
        self.assertEqual(got[("erb_zm:station:itezhi_tezhi_power_corporation", 2014)][0], 3000.0)
        self.assertEqual(got[("erb_zm:group:ipp", 2014)][0], 4000.0)
        self.assertEqual(got[("erb_zm:importer:zesco", 2025)][0], 2119700.0)
        self.assertEqual(got[("erb_zm:technology:total", 2025)], (4000.0, "MW", "capacity"))
        self.assertEqual((drop, short, nat["Total"]), ({2019}, {2025: 1.0}, 24.0))
        self.assertNotIn(("erb_zm:sector:mining", 2019), got)
        self.assertEqual(got[("erb_zm:sector:mining", 2021)][0], 1000.0)

    def test_2019_kept_when_it_differs(self):
        t = text().replace("Grand Total 11.00 22.00 11.00", "Grand Total 11.00 22.00 11.00").splitlines()
        t = [l.replace("Mining 1.00 2.00 1.00", "Mining 1.50 2.00 1.00").replace("Others 1.00 2.00 1.00", "Others 0.50 2.00 1.00") for l in t]
        out, drop, nat, short = Z.parse("\n".join(t), ipp())
        self.assertEqual(drop, set())
        self.assertIn(("erb_zm:sector:mining", 2019), {(e, y) for e, var, y, *_ in out})

    def test_stops(self):
        for args in (dict(t=text(kafue_2014="7.00")), dict(t=text(kafue_2014="x")), dict(t=text(trader_total="3.50")),
                     dict(t=text().replace("Year Kafue Gorge", "Year Kafue")), dict(t=text(), i=ipp(total_2014="5.00"))):
            with self.assertRaises(RuntimeError):
                Z.parse(args["t"], args.get("i", ipp()))


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(Z.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {Z.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
