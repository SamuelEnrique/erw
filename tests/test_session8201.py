"""Session 8201 (chain 502): the findings hunt of 19 November, its shared EIA-930 readers and the trade family.

Energy Research Warehouse (ERW). No warehouse file, no network, no database: small tables written to a temporary folder.
"""

import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
import builder  # noqa: E402
import check_do  # noqa: E402
import hourly930  # noqa: E402
import hunt_measures as hm  # noqa: E402
import trade  # noqa: E402

PY = "# Expected: 2019 1.0, 2025 2.0, change 1.0 (MW); tolerance 0.5 percent of the change.\nprint(1)\n"
LOOP = ('* Expected: 2019 1.0, 2025 2.0, change 1.0 (MW); tolerance 0.5 percent of the change.\n\nclear all\n\ntempfile all\n\nsave `all\', emptyok\n\n'
        'foreach y of numlist 2018/2026 {\nimport delimited "t_`y\'.csv", varnames(1) stringcols(_all) clear\nappend using `all\'\nsave `all\', replace\n}\n\n'
        "use `all', clear\n\ndestring value, replace force\n\nlist year measure n, noobs\n")


def write(folder, name, header, rows):
    with open(os.path.join(folder, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# test table\n" + header + "\n" + "\n".join(rows) + "\n")


class Rules(unittest.TestCase):
    def test_a_loop_is_one_block_and_its_braces_are_allowed(self):
        self.assertEqual(check_do.problems(LOOP, PY), [])
        self.assertIn("a block holds two lines", check_do.problems(LOOP.replace("clear all\n\n", "clear all\n"), PY))

    def test_the_chain_number_and_plan_are_this_hunts(self):
        self.assertEqual(builder.CHAIN, 502)
        self.assertTrue(builder.METHOD.endswith("findings-hunt-plan-2026-11-19.md"))

    def test_two_sides_agree_only_within_half_to_twice(self):
        self.assertTrue(trade._side_ok(100.0, None))
        self.assertTrue(trade._side_ok(100.0, 60.0))
        self.assertFalse(trade._side_ok(6410.0, 97.0))
        self.assertFalse(trade._side_ok(100.0, -100.0))

    def test_a_flow_fault_is_dropped_by_its_years_99th_percentile(self):
        d = pd.DataFrame({"year": [2020] * 200, "v": [100.0] * 199 + [-5378863.0]})
        kept = hourly930.drop_flow_faults(d, "v", ["year"])
        self.assertEqual(len(kept), 199)


class RegionDemand(unittest.TestCase):
    def test_an_hour_is_held_only_when_every_authority_of_the_month_files(self):
        hm.clear_cache()
        with tempfile.TemporaryDirectory() as d:
            rows = []
            for h in range(3):
                ts = f"2021-09-01T0{h}:00:00Z"
                rows.append(f"eia930:SOCO,demand_mw,{ts},1000,SE")
                if h != 2:
                    rows.append(f"eia930:AEC,demand_mw,{ts},500,SE")
            rows.append("eia930:SOCO,demand_mw,2021-10-01T00:00:00Z,1600,SE")   # October: AEC no longer files
            write(d, "eia930_ba_demand_hourly", "entity,variable,ts_utc,value,x_region", rows)
            w = hourly930.region_demand(d)
            got = dict(zip(w["ts_utc"], w["demand_mw"]))
            self.assertEqual(got["2021-09-01T00:00:00Z"], 1500.0)
            self.assertNotIn("2021-09-01T02:00:00Z", got)
            self.assertEqual(got["2021-10-01T00:00:00Z"], 1600.0)
        hm.clear_cache()


class Reproduce(unittest.TestCase):
    def test_a_pair_script_names_its_table_and_its_sign(self):
        py = trade.reproduce_py("pair_flow", "rp_ny_ne")
        self.assertIn("python {this file} <eia930_region_pair_hourly.csv>", py)
        self.assertIn("eia930:NE-NY", py)
        self.assertIn("* -1", py)
        do = trade.reproduce_do("pair_against_winter", "rp_can_ny")
        self.assertEqual([p for p in check_do.problems("* Expected: x\n\n" + do, "# Expected: x\n") if "expected" not in p], [])
        self.assertIn("month == 1 | month == 2 | month == 12", do)


if __name__ == "__main__":
    unittest.main()
