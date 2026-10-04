"""Session 79: reserves that are called (warehouse/analysis/battery_called.py).

Energy Research Warehouse (ERW). The days here are toy days with made-up prices and made-up calls, used only to test
the solver's arithmetic, as tests/test_session67.py does for the page's program. The same tests as session 67 (the
optimum against an exhaustive search, a day by hand, no double counting, every constraint every hour, a longer battery
never earns less), and two more: with no call the program is the page's, and the state of charge never goes negative.
The last class reads the built files where a machine holds them.

    python -m unittest tests.test_session79 -v
"""

import itertools
import math
import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/derived", "warehouse/analysis"):
    sys.path.insert(0, os.path.join(ROOT, p))

import battery_called as bc  # noqa: E402
import battery_stack as bs  # noqa: E402

GRID = (0.0, 0.5, 1.0)
SPEC = ((True, 1.0), (False, 1.0), (True, 1.0), (True, 2.0), (True, 4.0))  # regup, regdn, rrs, ecrs, nspin: ERCOT, 2023 to 2025


def brute(energy, reserves, spec, duration, shares):
    """The best day with calls by exhaustive search at a round trip of 1, in steps of half the rated power. It reads the
    rules, not the constraint matrix: a called award delivers share x award MWh, paid the energy price; the battery
    needs award x max(hours, share) stored at the hour's start and award x max(hours - share, 0) at its end; it may not
    charge in the called part of an hour in which it holds a called award; one cycle, calls included."""
    layer = {(0.0, 0.0): 0.0}
    for t in range(len(energy)):
        nxt = {}
        for (soc, cyc), val in layer.items():
            for c, d in itertools.product(GRID, GRID):
                if c > 0 and d > 0:
                    continue
                for aw in itertools.product(GRID, repeat=len(spec)):
                    up = sum(a for a, (is_up, _) in zip(aw, spec) if is_up)
                    dn = sum(a for a, (is_up, _) in zip(aw, spec) if not is_up)
                    if d + up > 1 or c + dn > 1:
                        continue
                    called = sum(a * s[t] for a, (is_up, _), s in zip(aw, spec, shares) if is_up)
                    held = [s[t] for a, (is_up, _), s in zip(aw, spec, shares) if is_up and a > 0 and s[t] > 0]
                    if held and c > 1 - max(held) + 1e-9:
                        continue
                    s2, c2 = soc + c - d - called, cyc + d + called
                    if s2 < -1e-9 or s2 > duration + 1e-9 or c2 > duration + 1e-9:
                        continue
                    start = sum(a * max(h, s[t]) for a, (is_up, h), s in zip(aw, spec, shares) if is_up)
                    end = sum(a * max(h - s[t], 0.0) for a, (is_up, h), s in zip(aw, spec, shares) if is_up)
                    need_dn = sum(a * h for a, (is_up, h) in zip(aw, spec) if not is_up)
                    if start > soc + 1e-9 or end > s2 + 1e-9 or need_dn > duration - max(soc, s2) + 1e-9:
                        continue
                    v = val + energy[t] * (d - c + called) + sum(a * r[t] for a, r in zip(aw, reserves))
                    k = (round(s2, 6), round(c2, 6))
                    if v > nxt.get(k, -math.inf):
                        nxt[k] = v
        layer = nxt
    return max(layer.values())


def toy(seed, T=24, K=5):
    rng = np.random.default_rng(seed)
    energy = rng.normal(40, 60, T)
    reserves = [np.abs(rng.normal(8, 10, T)) for _ in range(K)]
    shares = [np.zeros(T) for _ in range(K)]
    for j in (2, 3, 4):  # rrs, ecrs, nspin: a few called hours each, some for part of the hour
        for t in rng.choice(T, size=3, replace=False):
            shares[j][t] = rng.choice([0.25, 0.5, 1.0])
    return energy, reserves, shares


class Solver(unittest.TestCase):
    def test_with_no_call_it_is_the_pages_program(self):
        for seed in range(10):
            energy, reserves, _ = toy(seed)
            for dur in bs.DURATIONS:
                a = bs.solve_day(energy, reserves, SPEC, dur)
                b = bc.solve_day_called(energy, reserves, SPEC, dur, [None] * len(SPEC))
                z = bc.solve_day_called(energy, reserves, SPEC, dur, [np.zeros(len(energy))] * len(SPEC))
                self.assertAlmostEqual(a["total"], b["total"], places=6)
                self.assertAlmostEqual(a["total"], z["total"], places=6)
                self.assertAlmostEqual(a["energy"] + sum(a["reserve"]), b["energy"] + sum(b["reserve"]), places=6)
                self.assertEqual(sum(b["called"]), 0.0)
                self.assertEqual(bs.check_day(b, SPEC, dur), [])  # and it passes the page's own check

    def test_the_matrix_with_no_call_is_the_pages_matrix(self):
        eta = math.sqrt(bs.RTE)
        for dur in bs.DURATIONS:
            A, b, n = bs.structure(24, dur, SPEC, eta)
            A2, b2, n2 = bc.structure_called(24, dur, SPEC, eta, [np.zeros(24)] * len(SPEC))
            self.assertEqual(n, n2)
            self.assertTrue(np.allclose(A.toarray(), A2.toarray()))
            self.assertTrue(np.allclose(b, b2))

    def test_equals_brute_force_on_toy_days(self):
        spec = ((True, 1.0), (True, 2.0))
        for seed in range(6):
            rng = np.random.default_rng(100 + seed)
            energy = [float(v) for v in rng.integers(-20, 120, 4)]
            reserves = [[float(v) for v in rng.integers(0, 60, 4)] for _ in spec]
            shares = [[float(rng.choice([0.0, 0.0, 0.5, 1.0])) for _ in range(4)] for _ in spec]
            for dur in (1, 2):
                sol = bc.solve_day_called(energy, reserves, spec, dur, shares, rte=1.0)
                self.assertEqual(bc.check_day_called(sol, spec, dur, rte=1.0), [])
                best = brute(energy, reserves, spec, dur, shares)
                self.assertGreaterEqual(sol["total"], best - 1e-6, (seed, dur))  # the program is never below a feasible plan
                self.assertLessEqual(sol["total"], best + 1e-6, (seed, dur, energy, reserves, shares))

    def test_two_days_by_hand(self):
        spec = ((True, 1.0),)
        # charge 1 MWh at 10; hold 1 MW of reserve in hour 1 (60), called for the whole hour and paid 100; empty after
        a = bc.solve_day_called([10, 100, 10], [[0, 60, 60]], spec, 1, [[0, 1, 0]], rte=1.0)
        self.assertAlmostEqual(a["total"], -10 + 60 + 100, places=6)
        self.assertAlmostEqual(a["called"][0], 100, places=6)
        self.assertAlmostEqual(a["soc"][1], 0, places=6)
        # here the call is at a price of 5: holding the reserve would spend the energy before the 100 hour. Best is to
        # hold nothing, charge at 5 and sell at 100: 95. Never called, the same day pays 150 (60 for the reserve too)
        b = bc.solve_day_called([10, 5, 100], [[0, 60, 60]], spec, 1, [[0, 1, 0]], rte=1.0)
        self.assertAlmostEqual(b["total"], 95, places=6)
        self.assertAlmostEqual(bs.solve_day([10, 5, 100], [[0, 60, 60]], spec, 1, rte=1.0)["total"], 150, places=6)

    def test_no_double_counting_and_no_charging_while_called(self):
        for seed in range(10):
            energy, reserves, shares = toy(seed)
            for dur in bs.DURATIONS:
                sol = bc.solve_day_called(energy, reserves, SPEC, dur, shares)
                for t in range(len(energy)):
                    up = sum(sol["awards"][j][t] for j, (is_up, _) in enumerate(SPEC) if is_up)
                    self.assertLessEqual(sol["discharge"][t] + up, 1 + 1e-6)
                    held = [shares[j][t] for j, (is_up, _) in enumerate(SPEC) if is_up and shares[j][t] > 0 and sol["awards"][j][t] > 1e-6]
                    if held:
                        self.assertLessEqual(sol["charge"][t], 1 - max(held) + 1e-6)

    def test_constraints_hold_every_hour_and_the_state_of_charge_never_goes_negative(self):
        for seed in range(20):
            energy, reserves, shares = toy(seed)
            for dur in bs.DURATIONS:
                sol = bc.solve_day_called(energy, reserves, SPEC, dur, shares)
                self.assertEqual(bc.check_day_called(sol, SPEC, dur), [], (seed, dur))
                self.assertGreaterEqual(sol["soc"].min(), -1e-6)
                self.assertLessEqual(sol["soc"].max(), dur + 1e-6)
                # the energy delivered on call leaves the battery: the state of charge is the charges less everything sent out
                eta = math.sqrt(bs.RTE)
                out = sol["discharge"] + sum(np.asarray(shares[j]) * sol["awards"][j] for j, (is_up, _) in enumerate(SPEC) if is_up)
                self.assertTrue(np.allclose(sol["soc"], np.cumsum(eta * sol["charge"] - out / eta), atol=1e-6))
                self.assertAlmostEqual(sol["total"], sol["energy"] + sum(sol["reserve"]) + sum(sol["called"]), places=6)

    def test_a_long_call_is_paid_only_for_what_the_battery_can_deliver(self):
        # a reserve called for six hours on end, with a high capacity price in each: a 2-hour battery cannot hold 1 MW
        # of it through all six, as the price-taker's program lets it
        T = 8
        energy = [20.0] * T
        spec = ((True, 1.0),)
        reserves = [[0.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 0.0]]
        shares = [[0, 1, 1, 1, 1, 1, 1, 0]]
        never = bs.solve_day(energy, reserves, spec, 2, rte=1.0)
        called = bc.solve_day_called(energy, reserves, spec, 2, shares, rte=1.0)
        self.assertEqual(bc.check_day_called(called, spec, 2, rte=1.0), [])
        self.assertLess(called["total"], never["total"])
        self.assertLessEqual(called["called_mwh"], 2 + 1e-6)  # one cycle of a 2-hour battery
        self.assertGreater(never["reserve"][0], called["reserve"][0])

    def test_longer_duration_never_earns_less(self):
        for seed in range(6):
            energy, reserves, shares = toy(seed)
            totals = [bc.solve_day_called(energy, reserves, SPEC, d, shares)["total"] for d in bs.DURATIONS]
            self.assertLessEqual(totals[0], totals[1] + 1e-6)
            self.assertLessEqual(totals[1], totals[2] + 1e-6)

    def test_a_downward_product_cannot_be_called(self):
        with self.assertRaises(RuntimeError):
            bc.solve_day_called([10.0, 20.0], [[1.0, 1.0]], ((False, 1.0),), 2, [[1, 0]])


class Events(unittest.TestCase):
    def test_hour_shares(self):
        ev = pd.DataFrame({"product": ["rrs", "rrs", "ecrs"],
                           "start": pd.to_datetime(["2021-02-15T09:43:00Z", "2021-02-15T12:10:00Z", "2021-02-15T09:00:00Z"]),
                           "end": pd.to_datetime(["2021-02-15T11:15:00Z", "2021-02-15T12:20:00Z", "2021-02-15T09:30:00Z"])})
        s = bc.hour_shares(ev, "rrs")
        h = lambda x: pd.Timestamp(x, tz="UTC")  # noqa: E731
        self.assertAlmostEqual(s[h("2021-02-15T09:00:00")], 17 / 60)
        self.assertAlmostEqual(s[h("2021-02-15T10:00:00")], 1.0)
        self.assertAlmostEqual(s[h("2021-02-15T11:00:00")], 15 / 60)
        self.assertAlmostEqual(s[h("2021-02-15T12:00:00")], 10 / 60)
        self.assertEqual(len(s), 4)
        self.assertEqual(list(bc.hour_shares(ev, "ecrs").values()), [0.5])

    @unittest.skipUnless(os.path.exists(bc.EVENTS), "the events file is not on this machine")
    def test_the_transcribed_events(self):
        ev = bc.read_events()
        self.assertEqual(ev["product"].value_counts().to_dict(), {"rrs": 184, "nspin": 93, "ecrs": 53})
        self.assertGreaterEqual(ev["start"].min(), pd.Timestamp("2018-01-01", tz="UTC"))
        self.assertLessEqual(ev["end"].max(), pd.Timestamp("2024-08-01T05:00:00Z"))
        self.assertGreaterEqual(ev.loc[ev["product"] == "ecrs", "start"].min(), pd.Timestamp("2023-06-10T05:00:00Z"))
        # Winter Storm Uri: RRS released from 03:43 to 11:56 Central on 15 February 2021
        uri = bc.hour_shares(ev, "rrs")
        self.assertAlmostEqual(uri[pd.Timestamp("2021-02-15T12:00:00Z")], 1.0)       # 06:00 Central
        self.assertAlmostEqual(uri[pd.Timestamp("2021-02-15T09:00:00Z")], 17 / 60)   # 03:43 to 04:00 Central
        with open(bc.EVENTS, encoding="utf-8") as f:
            head = "".join(ln for ln in f if ln.startswith("#"))
        self.assertIn("https://www.ercot.com/files/docs/2024/10/07/ERCOT-Ancillary-Services-Study-Final-White-Paper.pdf", head)
        self.assertIn("Retrieved:", head)


YEARLY = os.path.join(bc.OUT_DIR, "battery_called_ercot_yearly.csv")
DAILY = os.path.join(bc.OUT_DIR, "battery_called_ercot_daily.csv")


@unittest.skipUnless(os.path.exists(YEARLY) and os.path.exists(DAILY), "the built files are not on this machine")
class Built(unittest.TestCase):
    def test_the_same_days_under_every_strategy_and_called_never_above_the_price_taker_by_much(self):
        d = pd.read_csv(DAILY, comment="#")
        n = d.groupby(["duration_h", "strategy"])["day"].nunique()
        self.assertEqual(n.nunique(), 1)  # every strategy and duration on the same days
        self.assertLessEqual(d["day"].max(), bc.WINDOW[1])
        self.assertGreaterEqual(d["day"].min(), bc.WINDOW[0])
        w = d.pivot_table(index=["day", "duration_h"], columns="strategy", values="total")
        # a day with no event is the price-taker's day exactly
        quiet = d[(d["strategy"] == "called") & (d[[c for c in d.columns if c.startswith("hours_called_")]].fillna(0).sum(axis=1) == 0)]
        q = w.loc[list(zip(quiet["day"], quiet["duration_h"]))]
        self.assertTrue(np.allclose(q["called"], q["foresight"]))

    def test_the_yearly_file_is_the_daily_files_sum(self):
        d, y = pd.read_csv(DAILY, comment="#"), pd.read_csv(YEARLY, comment="#")
        s = d.assign(year=d["day"].str[:4].astype(int)).groupby(["year", "duration_h", "strategy"])["total"].sum()
        for _, r in y.iterrows():
            self.assertAlmostEqual(r["total"], s[(r["year"], r["duration_h"], r["strategy"])], delta=0.01)
            self.assertAlmostEqual(r["total"], r["energy"] + r["called_energy"] + r["ancillary"], delta=0.05)

    def test_no_em_dash_in_the_session_files(self):
        for rel in ("warehouse/analysis/battery_called.py", "tests/test_session79.py"):
            with open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), rel)


if __name__ == "__main__":
    unittest.main()
