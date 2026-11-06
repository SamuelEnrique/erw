"""Session 2297: the Korea Power Exchange's EPSIS, South Korea's generation by source a year and its peak and base demand a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/kpx_korea.py on page scripts built here in EPSIS's form
(figures made up for the test, not KPX's): a year's columns read in MWh, an empty cell no row, the year in progress left
out, a subtotal off by more than KPX's rounding named and one off by more than 5% stopping the run; the demand page's two
views, a month not ended and a month shown as 0 no row, an ended year published in part left out and named; the sector
rule and the holds. No network.

    python -m unittest tests.test_session2297 -v
"""

import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import kpx_korea as K  # noqa: E402
import build_coverage as B  # noqa: E402

NOW = dt.datetime(2026, 10, 24, 14, 0, tzinfo=K.KST)


def gen_year(year, cells):
    body = "".join(f'                    {c} = textFormmat("{v}",count);\n' for c, v in cells.items())
    return (f'                if("{year}" >= beginDate && "{year}" <= endDate){{\n\n{body}\n'
            f'                    gridData.push({{"Year":"{year}",\n "c1":c1}});\n                }}\n')


def gen_page(*years):
    return '<span class="unit">(Unit : MWh)</span>\n' + "".join(gen_year(y, c) for y, c in years)


def full(c1="10", c2="20", c3="", c4="30"):
    cells = {k: "0" for k in K.GEN_COLS}
    cells.update(c1=c1, c2=c2, c3=c3, c4=c4, c17=c4, c21=c4, c22=c4, c10="", c11="")
    return cells


def dem_page(peak, base):
    def view(kind, years):
        out = f'            if(dataType == "{kind}") {{\n' if kind == "0" else f'            }} else if(dataType == "{kind}") {{\n'
        for y, vals in years.items():
            if kind == "0":
                body = "".join(f'c{i} = textFormmat("{v}",count);\n' for i, v in enumerate(vals, 1))
            else:
                body = "".join(f'c{i} = ("{v}" == 0) ? "-" : Math.round("{v}").toString() + point;\n' for i, v in enumerate(vals, 1))
            out += f'\n                if("{y}" >= beginDate && "{y}" <= endDate){{\n{body}gridData.push({{"Year":"{y}",\n"c1":c1}});\n}}\n'
        return out
    return '<span class="unit">(Unit : MW)</span>\n' + view("0", peak) + view("1", base) + "            }\n"


class Generation(unittest.TestCase):
    def test_rows(self):
        rows, diffs = K.parse_generation(gen_page((2026, full("1", "1", "", "2")), (2025, full())), {}, NOW)
        got = {(r["variable"], r["ts_utc"]): r for r in rows}
        r = got[("generation_hydro_general", "2025-01-01T00:00:00Z")]
        self.assertEqual((r["value"], r["unit"], r["freq"], r["x_group"], r["x_label"]), (10.0, "MWh", "P1Y", "Hydro", "General"))
        self.assertNotIn(("generation_hydro_small", "2025-01-01T00:00:00Z"), got)  # empty: no row
        self.assertNotIn(("generation_combined_cycle_general", "2025-01-01T00:00:00Z"), got)
        self.assertEqual(got[("generation_nuclear", "2025-01-01T00:00:00Z")]["value"], 0.0)  # a 0 is KPX's figure
        self.assertFalse([k for k in got if k[1].startswith("2026")])  # the year in progress
        self.assertEqual(diffs, [])

    def test_subtotals(self):
        _, diffs = K.parse_generation(gen_page((2016, full("1000", "1000", "", "2010"))), {}, NOW)
        self.assertEqual(diffs, ["2016 generation_hydro_total +10.0"])  # off by more than 1 MWh a part: named
        with self.assertRaises(RuntimeError) as c:
            K.parse_generation(gen_page((2016, full("10", "20", "", "40"))), {}, NOW)
        self.assertIn("its parts sum to", str(c.exception))


class Demand(unittest.TestCase):
    def test_views(self):
        peak = {"2026": ["80230.0"] * 9 + ["68469.0", "0", "0"], "2025": ["75680.0"] * 12, "2001": ["0"] * 6 + ["43125.0"] + ["0"] * 5}
        base = {"2026": ["60392.0"] * 9 + ["49704.0", "0", "0"], "2025": ["0"] * 10 + ["12277.0", "57565.0"]}
        rows, short = K.parse_demand(dem_page(peak, base), {}, NOW)
        got = {(r["variable"], r["ts_utc"]): r for r in rows}
        r = got[("peak_demand_daily_mean", "2026-09-01T00:00:00Z")]
        self.assertEqual((r["value"], r["unit"], r["freq"], r["x_kpx_view"]), (80230.0, "MW", "P1M", "peak"))
        self.assertNotIn(("peak_demand_daily_mean", "2026-10-01T00:00:00Z"), got)  # October not ended
        self.assertEqual(len([k for k in got if k[0] == "peak_demand_daily_mean" and k[1][:4] == "2025"]), 12)
        self.assertEqual(got[("base_demand_daily_mean", "2026-01-01T00:00:00Z")]["value"], 60392.0)
        self.assertFalse([k for k in got if k[1][:4] in ("2001",) or (k[0].startswith("base") and k[1][:4] == "2025")])
        self.assertEqual(short, ["peak 2001 (1 month)", "base 2025 (2 months)"])

    def test_views_named(self):
        with self.assertRaises(RuntimeError):
            K.parse_demand('<span class="unit">(Unit : MW)</span>\n', {}, NOW)


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            held = f.read().replace("\r\n", "\n")
        for t in (K.TABLE_GEN, K.TABLE_DEM):
            self.assertEqual(B.sector_of(t), "power")
            self.assertIn(f"  - {t}\n", held)


if __name__ == "__main__":
    unittest.main()
