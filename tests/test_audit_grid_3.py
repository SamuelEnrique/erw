"""Audit of the Grid tool, finding 3 (session 10205, docs/reviews/grid-model-audit-2026-11-26.md): one tool, two rules
for the same tie. The grid's tabs (Now, Network, Gravity) read each tie from one side, the code first in the alphabet
(warehouse/derived/grid_network.py RULE); a region's Gravity tab and the trade tables read both sides and take their mean
where both reported (warehouse/derived/interchange_pairs.py, x_basis "mean"). A reader moving between a grid and its
region meets two net exchanges for the same ties. Choosing one rule moves figures: the owner's ruling. This branch only
shows it; nothing is changed and it is not for landing.

1. In the code (passes on main): the two rules are as stated.
2. In the warehouse (passes on main, skipped without eia930_all_interchange): MISO's net export, summed over its ties
   hour by hour, differs between the two rules by more than 200 MW in the median hour, once reports above 20,000 MW
   (none a tie can carry) are set aside."""
import os
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.environ.get("ERW_AUDIT_OUTPUT_DIR", os.path.join(ROOT, "warehouse", "output"))
REGIONS = {"CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NY", "NW", "SE", "SW", "TEN", "TEX", "US48", "CAN", "MEX"}


class TwoRules(unittest.TestCase):
    def test_the_two_rules_in_the_code(self):
        with open(os.path.join(ROOT, "warehouse", "derived", "grid_network.py"), encoding="utf-8") as f:
            g = f.read()
        self.assertIn("read from the BA whose code sorts first", g)
        with open(os.path.join(ROOT, "warehouse", "derived", "interchange_pairs.py"), encoding="utf-8") as f:
            p = f.read()
        self.assertIn('"mean_both": ((w["a"] + w["b"]) / 2)', p)
        self.assertIn('np.where(a["n_both"] > 0, "mean"', p)

    def test_the_rules_disagree_for_miso(self):
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
            c = c[((c["ba"] == "miso") | (c["x_to_ba"] == "miso")) & c["value"].notna() & (c["value"].abs() <= 20000)]
            parts.append(c)
        x = pd.concat(parts)
        x = x[~x["ba"].str.upper().isin(REGIONS) & ~x["x_to_ba"].str.upper().isin(REGIONS)]
        x["other"] = np.where(x["ba"] == "miso", x["x_to_ba"].str.upper(), x["ba"].str.upper())
        x["exp"] = np.where(x["ba"] == "miso", x["value"], -x["value"])
        x["own"] = x["ba"] == "miso"
        p = x.pivot_table(index=["other", "ts_utc"], columns="own", values="exp", aggfunc="first")
        p.columns = ["nbr" if not k else "own" for k in p.columns]
        p = p.reset_index()
        first_is_miso = "MISO" < p["other"]
        p["page"] = np.where(first_is_miso, p["own"].fillna(p["nbr"]), p["nbr"].fillna(p["own"]))
        p["mean2"] = p[["own", "nbr"]].mean(axis=1)
        h = p.groupby("ts_utc").agg(page=("page", "sum"), mean2=("mean2", "sum"), n=("other", "nunique"))
        h = h[h["n"] == p["other"].nunique()]
        self.assertGreater(len(h), 24)
        self.assertGreater((h["page"] - h["mean2"]).abs().median(), 200)


if __name__ == "__main__":
    unittest.main()
