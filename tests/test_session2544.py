"""Session 2544: DfE's Electricity Consumption and Renewable Generation in Northern Ireland, figures 6 to 9 (a month).

Energy Research Warehouse (ERW). Tests warehouse/connectors/dfe_ni_electricity.py on a page built here (made up for the
test, not DfE's): the figures' CSV files written into the page as base64 UTF-16 text with one-byte line ends, each found
by its header, not its number; a rolling figure passed over; exports written positive; GWh to MWh; a figure missing, a
gap between months, a figure that is not a whole number, two figures of one header, types not summing to their total
and imports less exports not making net imports stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2544 -v
"""

import base64
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import dfe_ni_electricity as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
MONTHS = ["2026-01-01", "2026-02-01"]


def link(name, rows):
    """A figure's link as DfE writes it: UTF-16 little-endian characters, one-byte line ends."""
    lines = [",".join(f'"{c}"' if not c[:1].isdigit() and not c[:1] == "-" else c for c in r) for r in rows]
    body = b"\xff\xfe" + b"\n".join(ln.encode("utf-16-le") for ln in lines)
    return f'<a href="data:text/csv;base64,{base64.b64encode(body).decode()}" download="x.csv">{name}</a>'


def figure(head, values, months=MONTHS):
    return [["Date"] + list(head)] + [[m] + [str(v) for v in vs] for m, vs in zip(months, values)]


HEADS = list(D.FIGURES)
GOOD = {6: figure(HEADS[0], [(300, 3, 60, 4, 20), (250, 2, 61, 4, 30)]),
        7: figure(HEADS[1], [(400, 387), (380, 347)]),
        8: figure(HEADS[2], [(0, 390, 10), (0, 372, 8)]),
        9: figure(HEADS[3], [(200, -150, 50), (180, -175, 5)]),
        3: figure(("Total consumption (GWh)", "Renewable Generation (GWh)"), [(8800, 4200), (8810, 4210)])}


def page(figs=None, extra=""):
    figs = GOOD if figs is None else figs
    return "<html><body>" + "".join(link(f"Figure {n}.CSV (4kB)", rows) for n, rows in sorted(figs.items())) + extra + "</body></html>"


class Parse(unittest.TestCase):
    def test_rows(self):
        t, found = D.parse_figures(D.figures_of(page()), BASE)
        r = {(e, v, ts[:7]): x for e, v, ts, x in zip(t.entity, t.variable, t.ts_utc, t.value)}
        self.assertEqual(r[("dfe_ni:gb-nir:wind", "renewable_generation", "2026-01")], 300000.0)
        self.assertEqual(r[("dfe_ni:gb-nir:total", "renewable_generation", "2026-02")], 347000.0)
        self.assertEqual(r[("dfe_ni:gb-nir:gas", "non_renewable_generation", "2026-02")], 372000.0)
        self.assertEqual(r[("dfe_ni:gb-nir:total", "exports", "2026-01")], 150000.0)
        self.assertEqual(r[("dfe_ni:gb-nir:total", "net_imports", "2026-02")], 5000.0)
        self.assertEqual(len(t), 13 * 2)
        self.assertEqual(sorted(found.values()), ["Figure 6.CSV (4kB)", "Figure 7.CSV (4kB)", "Figure 8.CSV (4kB)", "Figure 9.CSV (4kB)"])
        self.assertEqual(set(t.unit), {"MWh"})

    def test_stops(self):
        bad = [{k: v for k, v in GOOD.items() if k != 8},
               {**GOOD, 9: figure(HEADS[3], [(200, -150, 50), (180, -175, 5)], months=["2026-01-01", "2026-03-01"])},
               {**GOOD, 8: figure(HEADS[2], [(0, "390.5", 10), (0, 372, 8)])},
               {**GOOD, 11: GOOD[9]},
               {**GOOD, 6: figure(HEADS[0], [(300, 3, 60, 4, 90), (250, 2, 61, 4, 30)])},
               {**GOOD, 9: figure(HEADS[3], [(200, -150, 90), (180, -175, 5)])}]
        for figs in bad:
            with self.assertRaises(RuntimeError):
                D.parse_figures(D.figures_of(page(figs)), BASE)
        with self.assertRaises(RuntimeError):
            D.figures_of("<html>no figure</html>")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.NAME), "power")
        self.assertIn(D.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
