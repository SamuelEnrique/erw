"""Session 3940 (chain 267): request 28 of docs/state/data_requests_licenses.md.

A grid in license_status.held_grids() builds no row data and no series file in any group of the price board. On
14 November 2026 a scratch build of board_page.py on the data machine wrote, of the held grids, only the spark, heat
and dark rows of NYISO's N.Y.C. and ISO-NE's Internal Hub (six series files): build_spreads drew every operator's main
hub without asking the hold. Held here on the real rows of tests/fixtures/board_1606/ with an empty spark input set,
and with held_grids() answering as the license file did on that day. No network, no model.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheHeldGridsSpreads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bp = cls.bp = builder()
        saved = bp.ls.held_grids
        bp.ls.held_grids = lambda today=None, path=None: {"ISO-NE", "MISO", "NYISO"}
        try:
            b = cls.b = bp.Board()
            day = {"2026-08-20": 30.0, "2026-08-21": 31.0}
            import pandas as pd
            frame = pd.DataFrame({"mean": day}).rename_axis("date")
            frame.index = pd.to_datetime(frame.index).date
            daily = {(f"{iso}:{bp.MAIN[iso]}", "da"): frame for iso in bp.ISO}
            gas = {d: 3.0 for d in frame.index}
            bp.build_spreads(b, daily, {"eia:henry_hub": gas}, {})
        finally:
            bp.ls.held_grids = saved
        cls.rows = {r["id"]: r for r in b.rows}

    def test_no_held_grid_row_has_values(self):
        for r in self.rows.values():
            if r.get("group") == "spark" and r.get("tags", {}).get("grid") in ("ISO-NE", "NYISO", "MISO", "PJM"):
                self.assertNotIn("last", r, r["id"])
                self.assertIn(r["status"], ("licensed", "paused"), r["id"])

    def test_one_licensed_row_a_held_grid(self):
        for iso, grid in (("nyiso", "NYISO"), ("isone", "ISO-NE")):
            r = self.rows[f"{iso}-spark"]
            self.assertEqual((r["group"], r["status"]), ("spark", "licensed"))
            self.assertIn("written permission", r["note"])
            main = self.bp.slug(f"{iso}:{self.bp.MAIN[iso]}")
            for kind in ("spark", "heat", "dark"):
                self.assertNotIn(f"{main}-{kind}", self.rows)

    def test_no_series_file_for_a_held_grid(self):
        held = ("nyiso", "isone")
        files = [k for k in getattr(self.b, "series", {}) if k.startswith(held)]
        self.assertEqual(files, [])

    def test_a_public_grid_keeps_its_rows(self):
        main = self.bp.slug(f"ercot:{self.bp.MAIN['ercot']}")
        self.assertEqual(self.rows[f"{main}-spark"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
