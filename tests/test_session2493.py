"""Session 2493: NSO Malawi's Statistical Year Book 2023, table 10.1 (ESCOM's units sold by type of user, 1992 to 2019).

Energy Research Warehouse (ERW). Tests warehouse/connectors/nso_malawi_electricity.py on a page built here as words with
their positions (made up for the test, not NSO's): a quantity's digit groups joined within its "Kwh" column, the value
columns between them not read, millions of kWh to MWh, a cell "..." with no row, the years whose classes do not sum to
the total listed; a page without the five Kwh headings and years out of order stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2493 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nso_malawi_electricity as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
KWH = [191, 266, 342, 414, 482]          # the Kwh headings' x0, as on the year book's page
VAL = [232, 308, 384, 452, 515]          # the value columns' x0


def w(text, x0, top):
    return {"text": text, "x0": float(x0), "x1": float(x0 + 3 * len(text)), "top": float(top)}


def row(year, qty, val, top):
    ws = [w(str(year), 62, top), w("543", 106, top)]
    for x, q in zip(KWH, qty):
        groups = q.split()
        for k, g in enumerate(groups):
            ws.append(w(g, x + 1 + 6 * k - 6 * (len(groups) - 1), top))
    for x, v in zip(VAL, val):
        ws.append(w(v, x, top))
    return ws


def page(years=S.YEARS, heading=True):
    ws = [w("Kwh", x, 120) for x in KWH] if heading else []
    for i, y in enumerate(years):
        qty = ["675.8", "437.7", "102.5", "134.9", "0.7"]
        if y == 1998:
            qty = ["1 598.4", "863.4", "236.5", "489.8", "8.7"]
        if y == 2019:
            qty = ["1633.0", "742.6", "300.0", "572.3", "…"]
        if y == 2010:
            qty = ["1 420.9", "1 420.9", "283.3", "581.5", "20.5"]
        ws += row(y, qty, ["105.1", "59.7", "20.3", "25.0", "0.1"], 140 + 12 * i)
    return ws


class Parse(unittest.TestCase):
    def test_rows(self):
        counts = {}
        t = S.parse_words(page(), BASE, counts)
        r = {(e, ts[:4]): v for e, ts, v in zip(t.entity, t.ts_utc, t.value)}
        self.assertEqual(r[("nso:mw:total", "1992")], 675800.0)
        self.assertEqual(r[("nso:mw:total", "1998")], 1598400.0)
        self.assertEqual(r[("nso:mw:total", "2019")], 1633000.0)
        self.assertEqual(r[("nso:mw:exports", "1992")], 700.0)
        self.assertNotIn(("nso:mw:exports", "2019"), r)
        self.assertEqual(len(t), 28 * 5 - 1)
        self.assertEqual(counts["years whose classes do not sum to the total"], "2010")
        self.assertEqual(set(t.variable), {"sales"})

    def test_stops(self):
        for bad in (page(heading=False), page(years=S.YEARS[:5] + S.YEARS[6:])):
            with self.assertRaises(RuntimeError):
                S.parse_words(bad, BASE, {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
