"""Audit of the Grid tool, finding 2 (session 10205, docs/reviews/grid-model-audit-2026-11-26.md): a grid's net export on
the Now card, the Gravity tab and the Network tab's panel is "the sum of a grid's reporting ties, signed from its side".
Each tie in the snapshot is one side's report: the balancing authority whose code sorts first, else the other's with the
sign turned (warehouse/derived/grid_network.py RULE). For PJM six of its seven ties are read from the neighbour, and the
sum differs from PJM's own reports by about 1,000 MW in the median hour, in sign in about a third of hours.

1. Against the page's own file (passes on main): in the committed snapshot, PJM is the second code of six of its seven
   ties, so the rule reads them from CPLE, CPLW, DUK, LGEE, MISO and NYIS.
2. Against the warehouse (passes on main, skipped where eia930_all_interchange is not on the machine): over the hours
   it holds, PJM's sum by the page's rule and by its own reports first differ by more than 500 MW in the median hour,
   and in sign in more than a tenth of hours. Changing the rule moves the figure: the owner's ruling, not made here.
3. The fix on this branch (fails on main): the figures' words say which side each tie is read from."""
import json
import os
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SNAP = os.path.join(ROOT, "site", "data", "grid_network.json")
OUT = os.environ.get("ERW_AUDIT_OUTPUT_DIR", os.path.join(ROOT, "warehouse", "output"))
REGIONS = {"CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NY", "NW", "SE", "SW", "TEN", "TEX", "US48", "CAN", "MEX"}


class WhichSide(unittest.TestCase):
    def test_pjm_ties_are_read_from_the_neighbour(self):
        with open(SNAP, encoding="utf-8") as f:
            s = json.load(f)
        mine = [link for link in s["links"] if "PJM" in (link["a"], link["b"])]
        from_neighbour = sorted(link["a"] for link in mine if link["b"] == "PJM")
        self.assertGreaterEqual(len(mine), 7)
        self.assertTrue({"CPLE", "DUK", "MISO", "NYIS"} <= set(from_neighbour))
        self.assertGreater(len(from_neighbour), len(mine) / 2)

    def test_the_rule_moves_pjm(self):
        path = os.path.join(OUT, "eia930_all_interchange.csv")
        if not os.path.exists(path):
            self.skipTest("eia930_all_interchange is not on this machine")
        import pandas as pd
        n = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
        parts = []
        for c in pd.read_csv(path, skiprows=n, usecols=["ts_utc", "value", "ba", "x_to_ba"], chunksize=400_000):
            c = c[(c["ba"] == "pjm") | (c["x_to_ba"] == "pjm")]
            parts.append(c[c["value"].notna()])
        x = pd.concat(parts)
        x = x[~x["ba"].str.upper().isin(REGIONS) & ~x["x_to_ba"].str.upper().isin(REGIONS)]
        x["other"] = np.where(x["ba"] == "pjm", x["x_to_ba"].str.upper(), x["ba"].str.upper())
        x["exp"] = np.where(x["ba"] == "pjm", x["value"], -x["value"])
        x["own"] = x["ba"] == "pjm"
        p = x.pivot_table(index=["other", "ts_utc"], columns="own", values="exp", aggfunc="first")
        p.columns = ["nbr" if not k else "own" for k in p.columns]
        p = p.reset_index()
        first_is_pjm = "PJM" < p["other"]
        p["page"] = np.where(first_is_pjm, p["own"].fillna(p["nbr"]), p["nbr"].fillna(p["own"]))
        p["ownfirst"] = p["own"].fillna(p["nbr"])
        h = p.groupby("ts_utc").agg(page=("page", "sum"), ownfirst=("ownfirst", "sum"), n=("other", "nunique"))
        h = h[h["n"] == p["other"].nunique()]
        self.assertGreater(len(h), 24)
        d = (h["page"] - h["ownfirst"]).abs()
        self.assertGreater(d.median(), 500)
        self.assertGreater(((h["page"] * h["ownfirst"]) < 0).mean(), 0.1)

    def test_the_words_say_which_side(self):
        with open(os.path.join(ROOT, "site", "lib", "network.ts"), encoding="utf-8") as f:
            self.assertIn("each tie as the balancing authority first in the alphabet reported it", f.read())
        for name, n in (("ExchangeView.tsx", 3), ("NowView.tsx", 1), ("NetworkFigures.tsx", 1)):
            with open(os.path.join(ROOT, "site", "components", "grid", name), encoding="utf-8") as f:
                t = f.read()
            self.assertGreaterEqual(t.count("${TIE_SIDE_WORDS}") + t.count("{TIE_SIDE_WORDS}"), n, name)
        with open(os.path.join(ROOT, "site", "components", "grid", "ExchangeView.tsx"), encoding="utf-8") as f:
            self.assertNotIn('note="Net export, MW: the sum of a grid\'s reporting ties, signed from its side. A negative', f.read())


if __name__ == "__main__":
    unittest.main()
