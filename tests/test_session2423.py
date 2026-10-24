"""Session 2423: the Electricity Market Operator of Georgia's (ESCO) actual electricity balance a month, in place of
Cambodia's regulator, whose robots file disallows every path.

Energy Research Warehouse (ERW). Tests warehouse/connectors/esco_georgia.py's reader on a page built here in ESCO's form
(figures made up for the test, not ESCO's): the two tables read, million kWh as MWh in the table, months not yet
published left out, the 2021 form's "Total Consumption" placed as supplied_and_export by its arithmetic, a check that
fails kept as published and named, a blank cell with no row; a line not in the map, a value that is not a number and a
line's months not adding to its printed total stopping the run; the sector rule and the live-set hold. No network.

    python -m unittest tests.test_session2423 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import esco_georgia as E  # noqa: E402
import build_coverage as B  # noqa: E402


def tr(label, jan, feb, total=None):
    def f(v):
        try:
            return float(v or 0)
        except ValueError:
            return 0.0
    cells = [label, jan, feb] + [""] * 10 + [total if total is not None else f"{f(jan) + f(feb):g}"]
    return "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"


HEAD = "<tr><th></th>" + "".join(f"<th>{m}</th>" for m in E.MONTHS) + "</tr>"


def page(form2021=False, dist_jan="60", wind="Kartli Wind Power Plant", transit_feb="0", gen_total=None):
    supply = [tr("Generation", "100", "100", gen_total), tr("Thermal plants", "20", "20"), tr(wind, "5", "5"),
              tr("Hydro Plants", "75", "75"), tr("Including the Regulatory", "25", "25"), tr("Including the Seasonal", "40", "40"),
              tr("Including the Small power", "10", "10"), tr("Import", "10", "10"), tr("Transit", "0", transit_feb),
              tr("Total Resource", "110", "110"), tr("Plant Losses and Self-consumption", "4", "4"), tr("Delivery to the Network", "106", "106")]
    demand = [tr("Supplied to the Consumers", "100", "100"), tr("Including the Distributiuon Comp.", dist_jan, "60"),
              tr("Including the Direct Customers", "39", "39"), tr("Self-consumption of Stopped Plants", "1", "1"),
              tr("Export", "2", "2"), tr("Transit", "0", "0")]
    if form2021:
        demand += [tr("Total Consumption", "102", "102"), tr("Transportation Expences", "4", "4"), tr("Total Demand Including the Losses", "106", "106")]
    else:
        demand += [tr("Supplied to the Consumers and Export", "102", "102"), tr("Transportation Expences", "4", "4"),
                   tr("Total Demand Including the Losses", "106", "106"), tr("Total Consumption", "108", "108")]
    return f"<table>{HEAD}{''.join(supply)}</table><p>x</p><table>{HEAD}{''.join(demand)}</table>"


class Rows(unittest.TestCase):
    def test_rows(self):
        out, gaps = E.parse_year(page(), 2025)
        self.assertEqual(out[("generation_wind", 1)], 5.0)
        self.assertEqual(out[("total_consumption", 2)], 108.0)
        self.assertNotIn(("generation", 3), out)
        self.assertEqual(gaps, [])
        t = E.finish({(2025, v, m): (x, "u") for (v, m), x in out.items()}, {}, {})
        self.assertEqual(t[(t.variable == "generation") & (t.ts_utc == "2025-01-01T00:00:00Z")].value.item(), 100000.0)

    def test_2021_form(self):
        out, gaps = E.parse_year(page(form2021=True), 2021)
        self.assertEqual((out[("supplied_and_export", 2)], gaps), (102.0, []))
        self.assertNotIn(("total_consumption", 1), out)

    def test_kept_and_named(self):
        out, gaps = E.parse_year(page(dist_jan="50"), 2023)
        self.assertEqual(out[("supplied_distribution", 1)], 50.0)
        self.assertEqual(gaps, [(2023, 1, "the supply to consumers", 90.0, 100.0)])
        out, gaps = E.parse_year(page(transit_feb=""), 2021)
        self.assertNotIn(("transit_in", 2), out)
        self.assertIn((2021, 2, "transit_in is blank", None, None), gaps)

    def test_stops(self):
        for p in (page(wind="Wind farms"), page(dist_jan="x"), page(gen_total="250")):
            with self.assertRaises(RuntimeError):
                E.parse_year(p, 2025)


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(E.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
