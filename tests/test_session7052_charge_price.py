"""Session 7052 (chain 370, the data machine): done-line request 183.

The curtailment worth file's battery rule (2, 4 and 8 hours per MW) now carries what the battery paid for what it took
in: the hub's real-time and day-ahead price of each interval's hour, weighted by the MWh the rule takes in that
interval (`charge_price`, USD per MWh charged), by the note's rule taken interval by interval in time order.
"""

import importlib.util
import json
import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    for d in ("connectors", "derived"):
        p = os.path.join(ROOT, "warehouse", d)
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("curtailment_worth_7052", os.path.join(ROOT, "warehouse", "derived", "curtailment_worth.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def intervals():
    # test data written here by hand, never a reported figure: one Pacific day, hourly, 0.6 to 1.5 MWh curtailed
    ts = pd.date_range("2026-04-10T15:00Z", periods=6, freq="h")
    return pd.DataFrame({"ts": ts, "mwh": [0.6, 1.5, 1.0, 1.0, 1.0, 0.4], "dur": 1.0})


class TheRuleIntervalByInterval(unittest.TestCase):
    def test_the_day_stops_at_its_hours(self):
        m = builder()
        iv = intervals()
        t = m.taken(iv, 1.0, 2, "America/Los_Angeles")
        self.assertEqual([round(x, 6) for x in t.values], [0.6, 1.0, 0.4, 0.0, 0.0, 0.0])
        self.assertAlmostEqual(float(t.sum()), float(m.absorbed(iv, 1.0, 2, "America/Los_Angeles").sum()))
        t8 = m.taken(iv, 1.0, 8, "America/Los_Angeles")
        self.assertAlmostEqual(float(t8.sum()), float(m.absorbed(iv, 1.0, 8, "America/Los_Angeles").sum()))

    def test_the_price_is_weighted_by_what_is_taken(self):
        m = builder()
        iv = intervals()
        t = m.taken(iv, 1.0, 2, "America/Los_Angeles")
        p = pd.Series([10.0, -5.0, 20.0, 99.0, 99.0, 99.0], index=iv["ts"])
        usd, mp, mt = m.charge_price(iv, t, p)
        self.assertAlmostEqual(usd, 0.6 * 10 + 1.0 * -5 + 0.4 * 20)
        self.assertAlmostEqual(mp, 2.0)
        self.assertAlmostEqual(mt, 2.0)
        p2 = p.copy()
        p2.iloc[1] = np.nan  # an hour without a price leaves its MWh out of both
        usd2, mp2, _ = m.charge_price(iv, t, p2)
        self.assertAlmostEqual(usd2, 0.6 * 10 + 0.4 * 20)
        self.assertAlmostEqual(mp2, 1.0)


class TheFile(unittest.TestCase):
    def test_every_month_carries_its_charge_price(self):
        with open(os.path.join(ROOT, "site", "data", "curtailment", "worth.json"), encoding="utf-8") as f:
            d = json.load(f)
        bat = d["grids"]["caiso"]["battery"]
        for month, r in bat["months"].items():
            cp = r["charge_price"]["TH_SP15_GEN-APND"]
            for side in ("rt", "da"):
                for dur, v in cp[side].items():
                    self.assertAlmostEqual(v["mwh_taken"], r["absorb_mwh_per_mw"][dur], places=1, msg=(month, side, dur))
        w = d["grids"]["ercot"]["battery"]["window"]
        self.assertIn("usd_per_mwh_charged", w["charge_price"]["HB_HUBAVG"]["rt"]["4"])


if __name__ == "__main__":
    unittest.main()
