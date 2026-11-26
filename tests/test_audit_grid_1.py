"""Audit of the Grid tool, finding 1 (session 10205, docs/reviews/grid-model-audit-2026-11-26.md): the Lower 48's
Gravity tab said "The Lower 48 is the sum of its grids, so its exchange is theirs" (site/components/grid/ExchangeView.tsx)
and its Now card "The Lower 48 is the sum of its grids" (site/components/grid/NowView.tsx). The seven grids carry about
two thirds of the Lower 48's demand, and the Lower 48's own exchange is with Canada and Mexico: the trade between its
balancing authorities cancels inside it.

1. Against the page's own file (passes on main): in the committed snapshot, at the hour the page opens on, the net
   exports of all its balancing authorities sum to zero (each tie counted once, from both ends), while the seven grids'
   sum does not; and some of the snapshot's ties run to Canadian or Mexican authorities.
2. Against the warehouse (passes on main, skipped where the table is not on the machine): the seven grids' demand is
   under 75 percent of the Lower 48's in every hour eia930_all_demand holds for all eight.
3. The fix on this branch (fails on main): neither component says the Lower 48 is the sum of its grids; both name its
   exchange with Canada and Mexico."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SNAP = os.path.join(ROOT, "site", "data", "grid_network.json")
OUT = os.environ.get("ERW_AUDIT_OUTPUT_DIR", os.path.join(ROOT, "warehouse", "output"))
SEVEN = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"]
ABROAD = {"AESO", "BCHA", "CEN", "HQT", "IESO", "MHEB", "NBSO", "SPC", "CFE"}


def complete_index(hours, links, quiet=48):
    """site/lib/networkV3.ts completeHour, restated: the newest hour every pair that reported in the last 48 holds."""
    n = len(hours)
    def last(link):
        return max((h for h in range(n) if link["mw"][h] is not None), default=-1)
    reporting = [link for link in links if last(link) >= n - quiet]
    for h in range(n - 1, -1, -1):
        if reporting and all(link["mw"][h] is not None for link in reporting):
            return h
    return n - 1


class LowerFortyEight(unittest.TestCase):
    def test_trade_inside_cancels_and_the_seven_do_not(self):
        with open(SNAP, encoding="utf-8") as f:
            s = json.load(f)
        h = complete_index(s["hours"], s["links"])
        net = {}
        for link in s["links"]:
            v = link["mw"][h]
            if v is None:
                continue
            net[link["a"]] = net.get(link["a"], 0) + v
            net[link["b"]] = net.get(link["b"], 0) - v
        self.assertAlmostEqual(sum(net.values()), 0.0, places=6)
        self.assertGreater(abs(sum(net.get(c, 0) for c in SEVEN)), 100)
        self.assertTrue(any(link["a"] in ABROAD or link["b"] in ABROAD for link in s["links"]))

    def test_the_seven_are_not_the_lower_48(self):
        path = os.path.join(OUT, "eia930_all_demand.csv")
        if not os.path.exists(path):
            self.skipTest("eia930_all_demand is not on this machine")
        import pandas as pd
        n = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
        d = pd.read_csv(path, skiprows=n, usecols=["entity", "variable", "ts_utc", "value"])
        d = d[d["variable"] == "demand_mw"]
        p = d.pivot_table(index="ts_utc", columns="entity", values="value", aggfunc="first").dropna()
        share = p[[f"eia930:{c}" for c in SEVEN]].sum(axis=1) / p["eia930:US48"]
        self.assertGreater(len(share), 24)
        self.assertLess(share.max(), 0.75)

    def test_the_page_does_not_say_the_sum(self):
        for name in ("ExchangeView.tsx", "NowView.tsx"):
            with open(os.path.join(ROOT, "site", "components", "grid", name), encoding="utf-8") as f:
                t = f.read()
            self.assertNotIn("is the sum of its grids", t, name)
            self.assertIn("Canada and Mexico", t, name)


if __name__ == "__main__":
    unittest.main()
