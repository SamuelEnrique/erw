"""Session 2463: ANARE-CI's open data, Côte d'Ivoire's gross generation by kind, consumption by voltage and peak demand.

Energy Research Warehouse (ERW). Tests warehouse/connectors/anare_cotedivoire.py's reader on pages built here in the form
of ANARE-CI's wpDataTables (figures made up for the test, not ANARE-CI's): GWh written as MWh and MW kept, a blank cell
with no row, a year printed twice with the same figures taken once; a year twice with different figures, a header not
ANARE-CI's and a value that is not a number stopping the run; the sector rule and the live-set hold. No network.

    python -m unittest tests.test_session2463 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import anare_cotedivoire as A  # noqa: E402
import build_coverage as B  # noqa: E402


def page(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<html><body><table id='table_1'><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></body></html>"


def pages(gen_rows=None, peak_head=None, cons_2020="4325"):
    gen = gen_rows or [["2020", "3376", "7828", "6"], ["2019", "3481", "7125", "7"], ["2019", "3481", "7125", "7"], ["1990", "1322", "656", ""]]
    return {"generation": page(["Année", "Hydraulique", "Thermique", "Centrales Isolées"], gen),
            "consumption": page(["Année", "BT", "HT/MT"], [["2020", cons_2020, "3699"]]),
            "peak": page(peak_head or ["Année", "MW"], [["2020", "1545"]])}


class Rows(unittest.TestCase):
    def test_rows(self):
        rows = A.parse(pages())
        self.assertEqual(rows[("generation_hydro", 2020)][:2], (3376000.0, "MWh"))
        self.assertEqual(rows[("peak_demand", 2020)][:2], (1545.0, "MW"))
        self.assertEqual(rows[("consumption_low_voltage", 2020)][0], 4325000.0)
        self.assertNotIn(("generation_isolated", 1990), rows)
        t = A.finish(rows, {}, {})
        self.assertEqual(len(t[t.ts_utc == "2019-01-01T00:00:00Z"]), 3)

    def test_stops(self):
        twice = [["2019", "3481", "7125", "7"], ["2019", "3480", "7125", "7"]]
        for p in (pages(gen_rows=twice), pages(peak_head=["Year", "MW"]), pages(cons_2020="n/a")):
            with self.assertRaises(RuntimeError):
                A.parse(p)


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(A.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {A.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
