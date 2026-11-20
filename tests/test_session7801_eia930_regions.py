"""Session 7801 (chain 401 part C, tables 1 to 3): the region sums of warehouse/connectors/eia930_region_hourly.py and the
region pair sums of warehouse/connectors/eia930_ba_interchange_hourly.py, on real rows of EIA's six-month files of July to
December 2025 (the hour starting 2025-07-01T00:00:00Z), as the tables of 18 November 2026 hold them.

Energy Research Warehouse (ERW). docs/methods/eia930_region_hourly.md.

    python -m unittest tests.test_session7801_eia930_regions -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia930_ba_interchange_hourly as ix  # noqa: E402
import eia930_region_hourly as rh  # noqa: E402

TS = pd.Timestamp("2025-07-01T00:00:00Z")
# CAL's five balancing authorities, demand (MW) reported and adjusted, as the July to December 2025 file prints them
CAL = {"BANC": 3695, "CISO": 33243, "IID": 1012, "LDWP": 4148, "TIDC": 586}
# the six reports between FLA and SE in that hour (reporting BA, neighbour, MW, region, neighbour's region)
FLA_SE = [("FPC", "SOCO", 39, "FLA", "SE"), ("FPL", "SOCO", -344, "FLA", "SE"), ("SOCO", "FPC", -39, "SE", "FLA"),
          ("SOCO", "FPL", 355, "SE", "FLA"), ("SOCO", "TAL", 108, "SE", "FLA"), ("TAL", "SOCO", -108, "FLA", "SE")]


def balance(values):
    rows = []
    for ba, v in values.items():
        r = {"Balancing Authority": ba, "Region": "CAL", "ts": TS}
        for rep, adj in rh.VARS.values():
            r[rep] = float(v) if rep == "Demand (MW)" else float("nan")
            if adj:
                r[adj] = float(v) if adj == "Demand (MW) (Adjusted)" else float("nan")
        rows.append(r)
    return pd.DataFrame(rows)


class RegionSums(unittest.TestCase):
    def test_cal_is_the_sum_of_its_five(self):
        out, short = rh.region_rows(balance(CAL), "2025_Jul_Dec", None)
        d = out[(out["entity"] == "eia930:CAL") & (out["variable"] == "demand_mw")]
        self.assertEqual(len(d), 1)
        self.assertEqual(d["value"].iloc[0], 42684)  # the table's figure
        self.assertEqual(int(d["x_bas"].iloc[0]), 5)
        self.assertEqual(d["x_basis"].iloc[0], "adjusted")
        self.assertEqual(short["demand_mw"], 0)

    def test_a_missing_member_leaves_the_hour_out(self):
        b = balance(CAL)
        b.loc[b["Balancing Authority"] == "IID", ["Demand (MW)", "Demand (MW) (Adjusted)"]] = float("nan")
        out, short = rh.region_rows(b, "2025_Jul_Dec", None)
        self.assertTrue(out[(out["entity"] == "eia930:CAL") & (out["variable"] == "demand_mw")].empty)
        self.assertEqual(short["demand_mw"], 1)

    def test_a_reported_value_stands_in_where_no_adjusted_is_printed(self):
        b = balance({"CISO": 33243})
        b["Demand (MW) (Adjusted)"] = float("nan")
        rows = rh.ba_rows(b, "2025_Jul_Dec")
        d = rows[rows["variable"] == "demand_mw"]
        self.assertEqual((d["value"].iloc[0], d["x_basis"].iloc[0]), (33243, "reported"))


class RegionPairs(unittest.TestCase):
    def frame(self, reports):
        return pd.DataFrame([{"ba": b, "diba": n, "v": float(v), "region": r, "diba_region": nr, "ts": TS} for b, n, v, r, nr in reports])

    def test_fla_se_both_sides_and_the_gap(self):
        out = ix.pair_rows(self.frame(FLA_SE), "2025_Jul_Dec", None)
        self.assertEqual(len(out), 1)
        r = out.iloc[0]
        self.assertEqual((r["entity"], r["value"], r["x_first_report"], r["x_second_report"], r["x_gap"], int(r["x_ties"])),
                         ("eia930:FLA-SE", "-413", "-413", "-424", "11", 3))

    def test_a_side_with_a_missing_report_is_empty(self):
        reports = [x for x in FLA_SE if not (x[0] == "TAL")]
        reports.append(("TAL", "SOCO", float("nan"), "FLA", "SE"))
        r = ix.pair_rows(self.frame(reports), "2025_Jul_Dec", None).iloc[0]
        self.assertEqual((r["x_basis"], r["value"], r["x_first_report"], r["x_gap"]), ("second", "-424", "", ""))

    def test_the_ba_table_keeps_each_report_unnetted(self):
        rows = ix.ba_rows(self.frame(FLA_SE), "2025_Jul_Dec")
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows.set_index("entity").loc["eia930:SOCO-FPL", "value"], "355")


class Files(unittest.TestCase):
    def test_the_file_list_runs_from_2018_july(self):
        import datetime as dt
        names = rh.files_between(today=dt.date(2026, 11, 18))
        self.assertEqual((names[0], names[-1], len(names)), ("EIA930_BALANCE_2018_Jul_Dec.csv", "EIA930_BALANCE_2026_Jul_Dec.csv", 17))
        self.assertEqual(ix.files_between(today=dt.date(2026, 11, 18))[0], "EIA930_INTERCHANGE_2018_Jul_Dec.csv")


if __name__ == "__main__":
    unittest.main()
