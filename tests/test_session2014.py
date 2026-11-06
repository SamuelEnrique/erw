"""Session 2014: ICE's day-ahead on-peak electricity indices, as EIA republishes them.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_ice_electricity.py on a workbook built here in EIA's
form (figures made up for the test, not ICE's): a hub's rows and units, a weekend package kept at its start date, an empty
cell left out; a hub not in the map, a delivery end before its start, a price not a number and a header without a needed
column stopping the run; the sector rule, the hold (internal, so not in the release package) and the license mapping.
No network.

    python -m unittest tests.test_session2014 -v
"""

import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import eia_ice_electricity as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import licenses as L  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEAD = ["Price hub", "Trade date", "Delivery start date", "Delivery \nend date", "High price $/MWh", "Low price $/MWh",
        "Wtd avg price $/MWh", "Change", "Daily volume MWh", "Number of trades", "Number of counterparties"]


def book(rows, head=HEAD):
    b = io.BytesIO()
    pd.DataFrame(rows, columns=head).to_excel(b, sheet_name="2026", index=False)
    return b.getvalue()


ROW = ["Mid C Peak", "2026-01-02", "2026-01-03", "2026-01-05", 20.5, 17.0, 18.19, -1.25, 9600, 12, 9]


class Parse(unittest.TestCase):
    def test_rows(self):
        rows, read = C.parse(book([ROW, ["Palo Verde Peak", "2026-01-05", "2026-01-06", "2026-01-06", 30, 28, 29, None, 800, 1, 2]]), BASE)
        self.assertEqual(read, ["2026"])
        got = {(r["entity"], r["variable"]): r for r in rows}
        w = got[("ice:mid_c_peak", "price_wavg")]
        self.assertEqual((w["ts_utc"], w["x_trade_date"], w["x_delivery_end"]), ("2026-01-03T00:00:00Z", "2026-01-02", "2026-01-05"))
        self.assertEqual((w["value"], w["unit"], w["market"], w["geo"]), (18.19, "USD/MWh", "Northwest", ""))
        self.assertEqual((got[("ice:mid_c_peak", "volume")]["unit"], got[("ice:mid_c_peak", "trades")]["unit"]), ("MWh", "count"))
        self.assertEqual(got[("ice:palo_verde_peak", "price_high")]["geo"], "US-AZ")
        self.assertNotIn(("ice:palo_verde_peak", "price_change"), got)  # an empty cell has no row
        self.assertEqual(len(rows), 7 + 6)

    def test_stops(self):
        for rows in ([["Some New Hub Peak"] + ROW[1:]],
                     [ROW[:2] + ["2026-01-05", "2026-01-03"] + ROW[4:]],
                     [ROW[:6] + ["n/a"] + ROW[7:]],
                     [ROW[:1] + ["not a date"] + ROW[2:]]):
            with self.assertRaises(RuntimeError):
                C.parse(book(rows), BASE)
        with self.assertRaises(RuntimeError):
            C.parse(book([ROW[:6] + ROW[7:]], HEAD[:6] + HEAD[7:]), BASE)  # no weighted average column
        with self.assertRaises(RuntimeError):
            C.parse(book([[1, 2]], ["a", "b"]), BASE)  # no sheet with the header


class Registered(unittest.TestCase):
    def test_sector_holds_and_license(self):
        self.assertEqual(B.sector_of(C.TABLE), "power")
        self.assertNotIn(C.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))
        self.assertEqual(L.BY_HAND[C.TABLE][0], ["EIA", "ICE, whose prices EIA republishes"])


if __name__ == "__main__":
    unittest.main()
