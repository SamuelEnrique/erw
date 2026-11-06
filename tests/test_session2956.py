"""Session 2956 (chain 157): gas_balance_weekly. The weekly part runs on a small storage series written here: the
change needs the week exactly 7 days before, and the five-year figures need the same ISO week in all five years before.
No request, no model call."""
import importlib.util
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("gb_2956", os.path.join(ROOT, "warehouse", "derived", "gas_balance_weekly.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def storage():
    rows = []
    for k, y in enumerate(range(2019, 2025)):          # the same ISO week (41) in six years, 100 Bcf more each year
        t = pd.Timestamp.fromisocalendar(y, 41, 5).tz_localize("UTC")
        rows.append((t, 1000.0 + 100 * k))
    t = rows[-1][0]
    rows.append((t + pd.Timedelta(days=7), 1630.0))      # the next week
    rows.append((t + pd.Timedelta(days=21), 1700.0))     # a week missing before it
    return pd.DataFrame({"entity": "eia:NW2_EPG0_SWO_R48_BCF", "variable": "working_gas", "t": [r[0] for r in rows], "v": [r[1] for r in rows]})


class TheWeeks(unittest.TestCase):
    def test_the_five_years_and_the_change(self):
        m = load()
        t = pd.DataFrame(m.weekly(storage()))
        last = t[t["ts_utc"].str.startswith("2024")]
        get = lambda v: last[last["variable"] == v]["value"].tolist()
        self.assertEqual(get("five_year_avg_bcf")[0], 1200.0)          # 1,000 to 1,400, the five years before 2024
        self.assertEqual(get("five_year_position_pct")[0], 125.0)        # 1,500 above the range's 1,000 to 1,400
        changes = t[t["variable"] == "net_change_bcf"]["value"].tolist()
        self.assertEqual(changes, [130.0])                              # only the week 7 days after; not across the gap
        self.assertTrue(t[t["ts_utc"].str.startswith("2019") & (t["variable"] == "five_year_avg_bcf")].empty)


if __name__ == "__main__":
    unittest.main()
