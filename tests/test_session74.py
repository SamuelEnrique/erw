"""Session 74 tests: the fleet-limited cap in battery_stack.solve_day, and the ERCOT AS Plan parser.

Energy Research Warehouse (ERW). A cap of 1 everywhere (or none) is the page's program exactly; a cap below what the
price-taker would hold binds in exactly those hours; no award passes its cap; every constraint still holds.
"""

import io
import os
import sys
import unittest
import zipfile

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402

SPEC = ((True, 1.0), (False, 1.0), (True, 1.0))  # an upward product, Regulation Down, another upward product


def day(seed, T=24):
    rng = np.random.default_rng(seed)
    energy = rng.normal(40, 25, T)
    reserves = [rng.uniform(0, 30, T), rng.uniform(0, 15, T), rng.uniform(0, 60, T)]
    return energy, reserves


class TestCap(unittest.TestCase):
    def test_cap_of_one_reproduces_the_program(self):
        for seed in range(6):
            e, r = day(seed)
            for dur in bs.DURATIONS:
                free = bs.solve_day(e, r, SPEC, dur)
                one = bs.solve_day(e, r, SPEC, dur, caps=[np.ones(24)] * 3)
                self.assertAlmostEqual(free["total"], one["total"], places=6)
                self.assertAlmostEqual(free["energy"], one["energy"], places=6)

    def test_cap_binds_where_it_should(self):
        for seed in range(6):
            e, r = day(seed)
            free = bs.solve_day(e, r, SPEC, 4)
            caps = [np.full(24, 0.2), np.full(24, 0.1), np.full(24, 0.15)]
            lim = bs.solve_day(e, r, SPEC, 4, caps=caps)
            self.assertEqual(bs.check_day(lim, SPEC, 4), [])
            for j in range(3):
                self.assertTrue((lim["awards"][j] <= caps[j] + 1e-9).all(), "no award passes its cap")
            # the price-taker's revenue is an upper bound of the capped program's
            self.assertLessEqual(lim["total"], free["total"] + 1e-6)
            # where the price-taker held more than the cap of the dearest product, the capped battery holds the cap
            j = 2
            over = free["awards"][j] > caps[j][0] + 1e-6
            if over.any():
                self.assertTrue(np.allclose(lim["awards"][j][over], caps[j][0], atol=1e-6) | (np.asarray(r[j])[over] <= 0).any())

    def test_zero_cap_holds_nothing(self):
        e, r = day(9)
        lim = bs.solve_day(e, r, SPEC, 2, caps=[np.zeros(24)] * 3)
        self.assertTrue(all(np.allclose(a, 0) for a in lim["awards"]))
        energy_only = bs.solve_day(e, [np.zeros(24)] * 3, SPEC, 2)
        self.assertAlmostEqual(lim["total"], energy_only["total"], places=6)


class TestASPlanParser(unittest.TestCase):
    def test_parse(self):
        import ercot_as_quantities as q
        rows = "DeliveryDate,HourEnding,AncillaryType,Quantity,DSTFlag\n" + "".join(
            f"10/03/2026,{h:02d}:00,{s},{100 + h},N\n" for h in range(1, 25) for s in ("REGUP", "RRS"))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("x.ASPLANNP433.csv", rows)
        p = q.parse(buf.getvalue())
        self.assertEqual(len(p), 48)
        self.assertEqual(str(p["ts"].min()), "2026-10-03 05:00:00+00:00")  # hour ending 01:00 CDT starts 05:00 UTC
        self.assertEqual(p.loc[p["service"] == "RRS", "value"].max(), 124)


if __name__ == "__main__":
    unittest.main()
